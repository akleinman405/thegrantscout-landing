"""
Nonprofit Website Email Scraper.

Scrapes nonprofit websites to extract email addresses using async HTTP requests.
Adapted from Filtered project's therapist scraper with nonprofit-specific patterns.

Features:
- Concurrent scraping with configurable semaphore
- Per-domain rate limiting
- Email confidence scoring (domain match, prefix priority, generic penalties)
- Contact page discovery (link-based + direct URL construction)
- SSL fallback to HTTP
- Returns ALL valid emails per site (not just best)
"""

import re
import asyncio
import hashlib
import random
import time
from urllib.parse import urlparse, urljoin, unquote
from typing import Optional
from dataclasses import dataclass, field

import aiohttp
from bs4 import BeautifulSoup


@dataclass
class EmailResult:
    """A single extracted email with metadata."""
    email: str
    confidence: float
    source_page: str       # homepage, contact_page, about_page
    source_url: str        # actual URL it was found on
    domain_matches: bool   # does email domain match website domain?


@dataclass
class PageResult:
    """Result of fetching a single page."""
    url: str
    page_type: str         # homepage, contact, about, donate, team, staff
    http_status: Optional[int]
    html_hash: Optional[str]
    html_size: Optional[int]
    error: Optional[str]   # None if successful


@dataclass
class ScrapeResult:
    """Complete scrape result for one nonprofit website."""
    ein: str
    status: str            # completed, failed, not_found, timeout, blocked, connection_error, ssl_error
    emails: list[EmailResult] = field(default_factory=list)
    pages: list[PageResult] = field(default_factory=list)


# --- Email type classification constants ---

ROLE_PREFIXES = {
    'info', 'contact', 'hello', 'office', 'admin', 'support',
    'grants', 'development', 'giving', 'donate', 'donations',
    'membership', 'members', 'volunteer', 'volunteers',
    'events', 'programs', 'services', 'outreach',
    'communications', 'media', 'press', 'pr', 'marketing',
    'hr', 'humanresources', 'finance', 'accounting', 'billing',
    'general', 'main', 'inquiries', 'help', 'feedback', 'reception',
    'fundraising', 'foundation', 'advancement', 'scholarship', 'alumni',
    'intake', 'enrollment', 'housing', 'training', 'facilities',
    'maintenance', 'transportation', 'nutrition', 'wellness',
    'safety', 'staffing', 'compliance',
    'treasurer', 'secretary', 'registrar', 'board',
    'newsletter', 'webmaster', 'postmaster',
    'director', 'president', 'ceo', 'cfo', 'coo', 'ed',
    'executive', 'executivedirector',
    'pastor', 'chaplain', 'counselor', 'referee',
}

GENERIC_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'comcast.net', 'att.net',
    'msn.com', 'live.com', 'sbcglobal.net', 'verizon.net',
    'me.com', 'mac.com', 'mail.com', 'protonmail.com',
    'proton.me', 'fastmail.com', 'zoho.com',
    'ymail.com', 'rocketmail.com', 'cox.net', 'earthlink.net',
    'charter.net', 'optonline.net',
}

JUNK_PATTERNS = [
    r'@latofonts\.com', r'@broofa\.com', r'@indiantypefoundry\.com',
    r'@rfuenzalida\.com', r'@eyebytes\.com', r'@micahrich\.com',
    r'@pixelspread\.com', r'@astigmatic\.com', r'@sansoxygen\.com',
    r'@ndiscovered\.com', r'@daltonmaag\.com', r'@prototypo\.io',
    r'@type-together\.com', r'@latinotype\.com',
    r'^john@doe\.com$', r'^name@email\.com$', r'^your@email\.com$',
    r'^email@email\.com$', r'^someone@website\.com$',
    r'^email@address\.com$', r'^name@domain\.com$',
    r'^you@email\.com$', r'^info@domain\.com$',
    r'\.calendar\.google\.com',
    r'prober', r'@example\.', r'@test\.', r'@localhost',
    r'@automattic\.com',
]


def classify_email_type(email: str) -> str:
    """Classify an email into: junk, role, generic, or personal.

    Args:
        email: Lowercase email address.

    Returns:
        One of 'junk', 'role', 'generic', 'personal'.
    """
    email = email.lower().strip()

    # Check junk patterns first
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return 'junk'

    local, domain = email.split('@', 1)

    # Generic free-mail providers
    if domain in GENERIC_DOMAINS:
        return 'generic'

    # Role-based prefixes (strip dots/hyphens for matching)
    local_clean = local.replace('.', '').replace('-', '').replace('_', '')
    if local_clean in ROLE_PREFIXES or local in ROLE_PREFIXES:
        return 'role'

    # Personal: has a dot or hyphen separator typical of name patterns (john.smith)
    # or is a simple first-name-like local part on an org domain
    return 'personal'


class NonprofitEmailScraper:
    """Async email scraper optimized for nonprofit websites."""

    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )

    # Emails to always exclude
    EXCLUDE_PATTERNS = [
        # System / transactional
        r'noreply@', r'no-reply@', r'donotreply@', r'do-not-reply@',
        r'privacy@', r'unsubscribe@', r'careers@', r'jobs@', r'recruitment@',
        r'webmaster@', r'postmaster@', r'mailer-daemon@', r'bounce@',
        # Website builders & their error tracking
        r'support@wix\.', r'support@squarespace\.', r'support@wordpress\.',
        r'@wix\.com', r'@squarespace\.com', r'@wordpress\.com',
        r'@godaddy\.com', r'@weebly\.com', r'@sitebuilder\.com',
        r'wixpress\.com',  # catches @sentry.wixpress.com and @sentry-next.wixpress.com
        # Social media platforms
        r'@google\.com', r'@facebook\.com', r'@twitter\.com', r'@instagram\.com',
        # Error tracking (general + self-hosted sentry)
        r'sentry\.io', r'@sentry\.', r'bugsnag\.com', r'rollbar\.com',
        # Test / example / placeholder (common CMS defaults)
        r'@example\.', r'@test\.', r'@localhost', r'@sample\.',
        r'^user@domain\.com$', r'^info@mysite\.com$', r'^example@',
        r'^email@domain\.com$', r'^hello@mydomain\.com$',
        r'^youremail@domain\.com$',
        r'@webdev\.com', r'@mydomain\.com',
        # Nonprofit directories (not the org's own email)
        r'@guidestar\.org', r'@charitynavigator\.org', r'@candid\.org',
        r'@irs\.gov', r'@idealist\.org', r'@greatnonprofits\.org',
        r'@networkforgood\.', r'@donorbox\.org', r'@classy\.org',
        r'@givebutter\.', r'@bloomerang\.', r'@neoncrm\.',
        # Donation / fundraising platforms
        r'@zeffy\.com', r'@actblue\.com', r'@gofundme\.com',
        r'@fundrazr\.com', r'@mightycause\.com',
        # Payment / CRM platforms
        r'@paypal\.com', r'@stripe\.com', r'@salesforce\.com',
        r'@constantcontact\.com', r'@mailchimp\.com',
        # Health insurance / student services (scraped from embedded widgets)
        r'@uhcsr\.com',
        # Font designer / foundry metadata (embedded in CSS/JS bundles)
        r'@latofonts\.com', r'@broofa\.com', r'@indiantypefoundry\.com',
        r'@rfuenzalida\.com', r'@eyebytes\.com', r'@micahrich\.com',
        r'@pixelspread\.com', r'@astigmatic\.com', r'@sansoxygen\.com',
        r'@ndiscovered\.com', r'@daltonmaag\.com', r'@prototypo\.io',
        r'@type-together\.com', r'@latinotype\.com',
        # Placeholder / form-default emails (exact match - real domains)
        r'^john@doe\.com$', r'^name@email\.com$', r'^your@email\.com$',
        r'^email@email\.com$', r'^someone@website\.com$',
        r'^email@address\.com$', r'^name@domain\.com$',
        r'^you@email\.com$', r'^info@domain\.com$',
        # Platform vendor emails (not the org's own)
        r'@givelively\.org', r'@automattic\.com',
        r'^program\.intake@usda\.gov$',
        # Google Calendar hash addresses (includes group.v.calendar variant)
        r'\.calendar\.google\.com',
    ]

    # Regex for image filenames that look like emails (retina @2x etc.)
    IMAGE_FILENAME_PATTERN = re.compile(
        r'@\d+x[\.-]|\.(?:jpg|jpeg|png|gif|svg|webp|bmp|ico)$',
        re.IGNORECASE,
    )

    # Legitimate long TLDs that start with a base TLD prefix (com/org/net/edu/gov)
    VALID_LONG_TLDS = {
        'community', 'company', 'computer', 'consulting', 'construction',
        'cooking', 'compare', 'cool', 'organic', 'network',
        'education', 'foundation', 'services', 'solutions',
        'frontend', 'commercial',
    }

    # Malformed TLDs: known base TLD (org/com/edu/gov/net) fused with trailing text
    # e.g., voa.orgvolunteering, clemson.edumailing, hotmail.comtimothy
    MALFORMED_TLD_PATTERN = re.compile(
        r'\.(com|org|net|edu|gov)[a-z]{2,}$',
        re.IGNORECASE,
    )

    # Hash-based tracking emails: 20+ hex chars in local part
    HASH_LOCAL_PATTERN = re.compile(
        r'^[a-f0-9]{20,}@',
        re.IGNORECASE,
    )

    # Priority prefixes for nonprofit emails (in order of preference)
    PRIORITY_PREFIXES = [
        'contact', 'info', 'hello', 'office', 'admin',
        'grants', 'development', 'giving', 'donate', 'executive',
        'director', 'president', 'ceo', 'ed',
        'general', 'main', 'inquiries', 'support',
    ]

    # Patterns to identify contact-like pages from links
    CONTACT_PAGE_PATTERNS = [
        r'/contact', r'/about', r'/team', r'/staff', r'/meet',
        r'/reach-us', r'/get-in-touch', r'/connect',
        r'/donate', r'/support', r'/get-involved', r'/join',
        r'/leadership', r'/board', r'/who-we-are',
    ]

    # Direct paths to try if not found via links
    DIRECT_PAGE_PATHS = [
        '/contact', '/contact-us', '/about', '/about-us',
        '/team', '/our-team', '/staff', '/leadership',
        '/donate', '/support', '/get-involved',
    ]

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
    ]

    def __init__(self, concurrency: int = 10, timeout: int = 15,
                 per_domain_delay: float = 0.3):
        self.concurrency = concurrency
        self.timeout = timeout
        self.per_domain_delay = per_domain_delay
        self.semaphore = asyncio.Semaphore(concurrency)
        self._domain_last_request: dict[str, float] = {}

    async def scrape_batch(self, prospects: list[dict],
                           progress_callback=None) -> list[ScrapeResult]:
        """
        Scrape emails for a batch of prospects.

        Args:
            prospects: List of dicts with 'ein' and 'url' keys
            progress_callback: Optional callback(processed, total, result)

        Returns:
            List of ScrapeResult objects
        """
        connector = aiohttp.TCPConnector(
            limit=self.concurrency * 2,
            limit_per_host=2,
            ssl=False,
            enable_cleanup_closed=True,
        )
        headers = self._get_headers()
        timeout = aiohttp.ClientTimeout(
            total=self.timeout * 3,  # total across all pages
            connect=5,
            sock_read=self.timeout,
        )

        results = []
        async with aiohttp.ClientSession(
            connector=connector, headers=headers, timeout=timeout
        ) as session:
            tasks = []
            for prospect in prospects:
                task = self._scrape_with_semaphore(
                    session, prospect['ein'], prospect['url']
                )
                tasks.append(task)

            for i, coro in enumerate(asyncio.as_completed(tasks)):
                result = await coro
                results.append(result)
                if progress_callback:
                    progress_callback(i + 1, len(prospects), result)

        return results

    async def _scrape_with_semaphore(self, session, ein: str, url: str) -> ScrapeResult:
        """Scrape with concurrency control."""
        async with self.semaphore:
            return await self._scrape_website(session, ein, url)

    async def _scrape_website(self, session, ein: str, url: str) -> ScrapeResult:
        """Scrape a single nonprofit website for all emails."""
        result = ScrapeResult(ein=ein, status='completed')

        if not url:
            result.status = 'failed'
            return result

        url = self._normalize_url(url)
        if not url:
            result.status = 'failed'
            return result

        domain = self._get_domain(url)

        # 1. Fetch homepage
        await self._rate_limit_domain(domain)
        html, page_result = await self._fetch_page(session, url, 'homepage')
        result.pages.append(page_result)

        if page_result.error:
            result.status = page_result.error
            return result

        # Extract emails from homepage
        homepage_emails = self._find_all_emails(html, domain, 'homepage', url)
        seen_emails = set()
        for e in homepage_emails:
            if e.email not in seen_emails:
                result.emails.append(e)
                seen_emails.add(e.email)

        # 2. Find and fetch contact/about pages (max 2 additional)
        contact_urls = self._find_contact_pages(html, url)
        pages_fetched = 0
        for contact_url in contact_urls:
            if pages_fetched >= 2:
                break

            # Determine page type from URL
            page_type = self._classify_page_type(contact_url)

            await self._rate_limit_domain(domain)
            contact_html, contact_page = await self._fetch_page(session, contact_url, page_type)
            result.pages.append(contact_page)
            pages_fetched += 1

            if contact_html:
                page_emails = self._find_all_emails(contact_html, domain, page_type, contact_url)
                for e in page_emails:
                    if e.email not in seen_emails:
                        # Boost confidence for contact page emails
                        e.confidence = min(1.0, e.confidence + 0.1)
                        result.emails.append(e)
                        seen_emails.add(e.email)

        if not result.emails:
            result.status = 'not_found'
        elif len(result.emails) > 5:
            # Cap at 5 best emails per org to avoid team page over-extraction
            result.emails.sort(key=lambda e: e.confidence, reverse=True)
            result.emails = result.emails[:5]

        return result

    # Unicode escape sequences found in JSON-embedded HTML (e.g., Wix sites)
    UNICODE_ESCAPES = re.compile(r'\\u003[ce]', re.IGNORECASE)

    @staticmethod
    def _clean_html(html: str) -> str:
        """Remove script, style, and noscript tags to avoid extracting junk emails
        from CSS font metadata, JS library authors, and embedded tracking code."""
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        return str(soup)

    def _find_all_emails(self, html: str, domain: str,
                         source_page: str, source_url: str) -> list[EmailResult]:
        """Extract ALL valid emails from HTML content."""
        if not html:
            return []

        # Decode JSON Unicode escapes before extracting emails
        # \u003c = <, \u003e = > (common in Wix JSON-embedded HTML)
        if '\\u003' in html:
            html = self.UNICODE_ESCAPES.sub('', html)

        # Strip script/style/noscript tags to avoid font metadata and JS library emails
        html = self._clean_html(html)

        found_emails = self.EMAIL_PATTERN.findall(html)
        if not found_emails:
            return []

        results = []
        seen = set()
        for email in found_emails:
            email = email.lower().strip()
            # Strip any remaining u003e/u003c prefixes
            email = re.sub(r'^u003[ce]', '', email)
            # Decode URL-encoded characters (%20 spaces from mailto: links)
            if '%' in email:
                email = unquote(email).strip()
            # Reject if still contains invalid chars after decode
            if '%' in email or ' ' in email:
                continue
            if email in seen:
                continue
            seen.add(email)

            if self._is_excluded(email):
                continue

            # Reject malformed TLDs (run-together text like voa.orgvolunteering)
            tld_match = self.MALFORMED_TLD_PATTERN.search(email)
            if tld_match:
                actual_tld = email.rsplit('.', 1)[-1]
                if actual_tld.lower() not in self.VALID_LONG_TLDS:
                    continue

            # Reject hash-based tracking emails (20+ hex chars in local part)
            if self.HASH_LOCAL_PATTERN.match(email):
                continue

            confidence = self._calculate_confidence(email, domain)
            if confidence > 0:
                email_domain = email.split('@')[1]
                results.append(EmailResult(
                    email=email,
                    confidence=confidence,
                    source_page=source_page,
                    source_url=source_url,
                    domain_matches=(email_domain == domain),
                ))

        # Sort by confidence descending
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    def _calculate_confidence(self, email: str, website_domain: str) -> float:
        """Calculate confidence score for an email (0.0 - 1.0)."""
        score = 0.5
        local, domain = email.split('@')

        # Domain matching
        if domain == website_domain:
            score += 0.3
        elif website_domain in domain or domain in website_domain:
            score += 0.15

        # Priority prefix scoring
        for i, prefix in enumerate(self.PRIORITY_PREFIXES):
            if local.startswith(prefix):
                score += 0.1 * (1 - i * 0.03)
                break

        # Personal name pattern bonus
        if re.match(r'^[a-z]+(\.[a-z]+)?$', local):
            score += 0.05

        # Generic domain penalty
        if domain in ('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                       'aol.com', 'icloud.com', 'comcast.net', 'att.net'):
            score -= 0.1

        # Short local part penalty
        if len(local) < 3:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _is_excluded(self, email: str) -> bool:
        """Check if email matches exclusion patterns."""
        # Image filenames with @ (retina @2x, srcset variants)
        if self.IMAGE_FILENAME_PATTERN.search(email):
            return True
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, email, re.IGNORECASE):
                return True
        return False

    def _normalize_url(self, url: str) -> Optional[str]:
        """Normalize URL to include scheme."""
        url = url.strip().rstrip('/')
        if not url:
            return None
        if not url.startswith('http'):
            url = 'https://' + url
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
            if parsed.path:
                normalized += parsed.path
            if parsed.query:
                normalized += '?' + parsed.query
            return normalized
        except Exception:
            return None

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL (without www.)."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ''

    async def _rate_limit_domain(self, domain: str):
        """Enforce per-domain rate limiting."""
        now = time.time()
        last = self._domain_last_request.get(domain, 0)
        wait = self.per_domain_delay - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self._domain_last_request[domain] = time.time()

    async def _fetch_page(self, session, url: str,
                          page_type: str) -> tuple[Optional[str], PageResult]:
        """Fetch a page. Returns (html_or_None, PageResult)."""
        try:
            async with session.get(url, allow_redirects=True) as response:
                status = response.status
                if status == 200:
                    html = await response.text()
                    html_hash = hashlib.md5(html.encode('utf-8', errors='replace')).hexdigest()
                    page = PageResult(
                        url=url, page_type=page_type, http_status=status,
                        html_hash=html_hash, html_size=len(html), error=None,
                    )
                    return (html, page)
                else:
                    error = {403: 'blocked', 404: 'not_found', 429: 'rate_limited'}.get(
                        status, f'http_{status}'
                    )
                    page = PageResult(
                        url=url, page_type=page_type, http_status=status,
                        html_hash=None, html_size=None, error=error,
                    )
                    return (None, page)

        except asyncio.TimeoutError:
            page = PageResult(url=url, page_type=page_type, http_status=None,
                              html_hash=None, html_size=None, error='timeout')
            return (None, page)

        except aiohttp.ClientSSLError:
            # Try HTTP fallback
            if url.startswith('https://'):
                http_url = url.replace('https://', 'http://')
                try:
                    async with session.get(http_url, allow_redirects=True) as response:
                        if response.status == 200:
                            html = await response.text()
                            html_hash = hashlib.md5(html.encode('utf-8', errors='replace')).hexdigest()
                            page = PageResult(
                                url=http_url, page_type=page_type,
                                http_status=response.status,
                                html_hash=html_hash, html_size=len(html), error=None,
                            )
                            return (html, page)
                except Exception:
                    pass
            page = PageResult(url=url, page_type=page_type, http_status=None,
                              html_hash=None, html_size=None, error='ssl_error')
            return (None, page)

        except aiohttp.ClientConnectorError:
            page = PageResult(url=url, page_type=page_type, http_status=None,
                              html_hash=None, html_size=None, error='connection_error')
            return (None, page)

        except Exception:
            page = PageResult(url=url, page_type=page_type, http_status=None,
                              html_hash=None, html_size=None, error='error')
            return (None, page)

    def _find_contact_pages(self, html: str, base_url: str) -> list[str]:
        """Find contact page URLs from homepage links + direct URL construction."""
        contact_urls = []

        # 1. Parse links from homepage
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    for pattern in self.CONTACT_PAGE_PATTERNS:
                        if re.search(pattern, href):
                            full_url = urljoin(base_url, link['href'])
                            if full_url not in contact_urls and full_url != base_url:
                                contact_urls.append(full_url)
                            break
            except Exception:
                pass

        # 2. Construct direct URLs for common paths not already covered
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        for path in self.DIRECT_PAGE_PATHS:
            direct_url = base + path
            if direct_url not in contact_urls:
                path_stem = path.split('-')[0]
                already_covered = any(path_stem in u for u in contact_urls)
                if not already_covered:
                    contact_urls.append(direct_url)

        return contact_urls

    def _classify_page_type(self, url: str) -> str:
        """Classify a URL into a page type."""
        lower = url.lower()
        if any(p in lower for p in ['/contact', '/reach', '/connect', '/get-in-touch']):
            return 'contact'
        if any(p in lower for p in ['/about', '/who-we-are', '/mission']):
            return 'about'
        if any(p in lower for p in ['/team', '/staff', '/leadership', '/board', '/people']):
            return 'team'
        if any(p in lower for p in ['/donate', '/support', '/give', '/get-involved']):
            return 'donate'
        return 'other'

    def _get_headers(self) -> dict:
        """Get randomized request headers."""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
