#!/usr/bin/env python3
"""
Deep Crawl Foundation Websites for VetsBoats Eligibility Intelligence

Phase 1 of the deep-crawl pipeline. Priority BFS crawler with:
- Playwright for JS-rendered pages, aiohttp fast fallback
- Priority link queue (grant/eligibility pages first)
- No text cap per page (original capped at 3K chars)
- PDF download + text extraction via PyPDF2
- Depth 3 crawling, 30-75 page limit per site
- Link categorization with anchor text

Output: DATA_2026-02-20_deep_crawl_batch3_raw.json
"""

import asyncio
import json
import io
import random
import re
import time
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse, urljoin, urldefrag

import aiohttp
from bs4 import BeautifulSoup

# Playwright import — used for JS-heavy sites
try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("WARNING: playwright not available, using aiohttp only")

# PDF extraction
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("WARNING: PyPDF2 not available, PDFs will be skipped")

# ─── Config ───────────────────────────────────────────────────────────────────

OUTPUT_DIR = '/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-20'
BROWSER_CONCURRENCY = 3          # concurrent Playwright contexts
AIOHTTP_CONCURRENCY = 5          # concurrent aiohttp fetches
PER_DOMAIN_DELAY = 1.0           # seconds between requests to same domain
JITTER = 0.5                     # random jitter added to delay
PAGE_TIMEOUT = 20                # seconds per page
MAX_PAGES_PER_SITE = 50          # hard cap on pages per foundation
PDF_MAX_SIZE = 10 * 1024 * 1024  # 10MB max PDF size

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
]

# ─── Link Priority Tiers ──────────────────────────────────────────────────────

PRIORITY_1_PATTERNS = [
    r'grant', r'apply', r'eligib', r'guideline', r'fund(?:ing)?',
    r'how.?to', r'rfp', r'requirement', r'criteria', r'limitation',
    r'preference', r'letter.?of.?inquiry', r'loi', r'request.?for',
    r'submission', r'deadline', r'grantseek', r'grant.?seek',
]

PRIORITY_2_PATTERNS = [
    r'program', r'focus', r'area', r'our.?work', r'what.?we',
    r'initiative', r'about', r'mission', r'faq', r'strateg',
    r'priorities', r'impact', r'grantmak',
]

PRIORITY_3_PATTERNS = [
    r'contact', r'staff', r'team', r'leadership', r'grantee',
    r'recipient', r'annual.?report', r'financ', r'990',
]

SKIP_PATTERNS = [
    r'news', r'blog', r'press', r'event', r'donat(?:e|ion)',
    r'career', r'login', r'sign.?in', r'privac', r'terms',
    r'cookie', r'subscribe', r'newsletter', r'calendar',
    r'webinar', r'video', r'podcast', r'gallery', r'photo',
    r'twitter\.com', r'facebook\.com', r'linkedin\.com',
    r'instagram\.com', r'youtube\.com', r'mailto:',
    r'\.jpg$', r'\.png$', r'\.gif$', r'\.svg$', r'\.mp4$',
    r'\.zip$', r'\.doc$', r'\.xlsx$', r'\.pptx$',
]

# Direct paths to always attempt (appended to base URL)
DIRECT_GRANT_PATHS = [
    '/grants', '/grants/', '/apply', '/apply/', '/funding', '/funding/',
    '/eligibility', '/eligibility/', '/guidelines', '/guidelines/',
    '/how-to-apply', '/how-to-apply/', '/grantmaking', '/grantmaking/',
    '/for-grantseekers', '/grant-seekers', '/grantees',
    '/what-we-fund', '/areas-of-focus', '/focus-areas',
    '/programs', '/our-work', '/about', '/about-us', '/faq',
    '/contact', '/contact-us', '/staff', '/team',
    '/funding-guidelines', '/funding-guidelines/',
    '/support-guidelines', '/giving',
]

# ─── Target Foundations ───────────────────────────────────────────────────────

FOUNDATIONS = [
    # Batch 3: Pre-filtered candidates from multi-peer, niche sailing, high-affinity CA sources
    # Tier A: Must-Crawl
    {"ein": "330247161", "name": "Crail-Johnson Foundation", "url": "https://www.crail-johnson.org", "tier": 1},
    {"ein": "946079493", "name": "William G Gilmore Foundation", "url": "https://www.williamggilmorefoundation.org", "tier": 1},
    {"ein": "870757807", "name": "Kim & Harold Louie Family", "url": "https://www.louiefamilyfoundation.org", "tier": 1},
    {"ein": "911722000", "name": "Lucky Seven Foundation", "url": "https://www.fsrequests.com/luckyseven", "tier": 1},
    {"ein": "650171539", "name": "Lennar Foundation", "url": "https://www.lennar.com/about/community", "tier": 1},
    # Tier B: Worth Crawling (corporate foundations)
    {"ein": "236261726", "name": "Cigna Foundation", "url": "https://www.cigna.com/about-us/community/giving", "tier": 2},
    {"ein": "756038519", "name": "Texas Instruments Foundation", "url": "https://www.ti.com/giving", "tier": 2},
    {"ein": "810465899", "name": "First Interstate BancSystem", "url": "https://www.firstinterstatebank.com", "tier": 2},
    # SOFT_FAIL foundations crawled for relationship intel
    {"ein": "474305984", "name": "Hutton Family Foundation", "url": "https://www.huttonfamilyfoundation.org", "tier": 3},
]


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class CrawledPage:
    url: str
    final_url: str              # after redirects
    page_type: str              # homepage, grants, application, about, etc.
    priority: int               # 1-4 (1=highest)
    depth: int                  # 0=homepage, 1=first level, etc.
    text: str                   # full extracted text (no cap)
    title: str = ""
    anchor_text: str = ""       # text of link that led here
    status: Optional[int] = None
    content_type: str = "html"  # html or pdf
    error: Optional[str] = None
    char_count: int = 0
    fetch_method: str = "aiohttp"  # aiohttp or playwright


@dataclass
class DiscoveredLink:
    url: str
    anchor_text: str
    priority: int
    depth: int
    source_url: str


@dataclass
class FoundationCrawl:
    ein: str
    name: str
    base_url: str
    tier: int
    pages: list = field(default_factory=list)
    discovered_links: list = field(default_factory=list)
    pdfs_found: list = field(default_factory=list)
    crawl_status: str = "pending"
    error: Optional[str] = None
    total_chars: int = 0
    pages_crawled: int = 0
    pages_with_content: int = 0
    grant_pages_found: int = 0
    crawl_time_seconds: float = 0


# ─── Utility Functions ────────────────────────────────────────────────────────

def normalize_url(url, base_url=None):
    """Normalize a URL: resolve relative, strip fragment, lowercase domain."""
    if not url:
        return None

    # Strip whitespace
    url = url.strip()

    # Skip non-http links
    if url.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
        return None

    # Resolve relative URLs
    if base_url and not url.startswith('http'):
        url = urljoin(base_url, url)

    # Add scheme if missing
    if not url.startswith('http'):
        url = 'https://' + url

    # Strip fragment
    url, _ = urldefrag(url)

    # Parse and normalize
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        # Lowercase scheme and domain
        normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
        if parsed.path:
            # Remove trailing slash for consistency (except root)
            path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
            normalized += path
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized
    except Exception:
        return None


def get_domain(url):
    """Extract domain without www prefix."""
    try:
        parsed = urlparse(url)
        d = parsed.netloc.lower()
        if d.startswith('www.'):
            d = d[4:]
        return d
    except Exception:
        return ''


def same_domain(url1, url2):
    """Check if two URLs share the same base domain."""
    return get_domain(url1) == get_domain(url2)


def classify_link(url, anchor_text=""):
    """Classify a link into priority tier (1-4) based on URL and anchor text."""
    combined = (url + ' ' + anchor_text).lower()

    # Check skip patterns first
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, combined):
            return 4  # skip tier

    # Priority 1: grant/eligibility/application
    for pattern in PRIORITY_1_PATTERNS:
        if re.search(pattern, combined):
            return 1

    # Priority 2: programs/focus/about
    for pattern in PRIORITY_2_PATTERNS:
        if re.search(pattern, combined):
            return 2

    # Priority 3: contact/staff/grantees
    for pattern in PRIORITY_3_PATTERNS:
        if re.search(pattern, combined):
            return 3

    return 4  # default: low priority


def extract_text_full(html):
    """Extract all text from HTML with no character cap. Preserves structure."""
    if not html:
        return "", ""

    soup = BeautifulSoup(html, 'html.parser')

    # Get title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Remove non-content elements
    for tag in soup.find_all(['script', 'style', 'noscript', 'svg', 'iframe']):
        tag.decompose()

    # Extract text preserving some structure
    text_parts = []
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'th',
                                   'div', 'span', 'article', 'section', 'blockquote', 'dd', 'dt']):
        txt = element.get_text(separator=' ', strip=True)
        if txt and len(txt) > 3:
            # Add heading markers
            if element.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                text_parts.append(f"\n## {txt}\n")
            elif element.name == 'li':
                text_parts.append(f"- {txt}")
            else:
                text_parts.append(txt)

    text = '\n'.join(text_parts)

    # Deduplicate repeated lines (common in scraped sites)
    seen = set()
    deduped = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            deduped.append(line)

    return '\n'.join(deduped), title


def extract_links(html, base_url):
    """Extract all links from HTML with anchor text and priority classification."""
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    links = []
    seen_urls = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        anchor = a_tag.get_text(strip=True)[:200]  # cap anchor text

        normalized = normalize_url(href, base_url)
        if not normalized or normalized in seen_urls:
            continue

        # Only follow same-domain links
        if not same_domain(normalized, base_url):
            continue

        seen_urls.add(normalized)
        priority = classify_link(normalized, anchor)
        links.append({
            'url': normalized,
            'anchor_text': anchor,
            'priority': priority,
        })

    # Sort by priority (1 first)
    links.sort(key=lambda x: x['priority'])
    return links


def extract_pdf_text(pdf_bytes):
    """Extract text from PDF bytes using PyPDF2."""
    if not HAS_PYPDF2:
        return ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text_parts = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
        return '\n\n'.join(text_parts)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


# ─── Foundation Crawler ───────────────────────────────────────────────────────

class DeepCrawler:
    def __init__(self):
        self._domain_last_request = {}
        self._browser = None
        self._browser_sem = asyncio.Semaphore(BROWSER_CONCURRENCY)
        self._aiohttp_sem = asyncio.Semaphore(AIOHTTP_CONCURRENCY)
        self.stats = defaultdict(int)

    async def start_browser(self):
        """Launch Playwright browser."""
        if not HAS_PLAYWRIGHT:
            return
        try:
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled'],
            )
            print("  Playwright browser launched")
        except Exception as e:
            print(f"  WARNING: Failed to launch Playwright: {e}")
            self._browser = None

    async def stop_browser(self):
        """Close Playwright browser."""
        if self._browser:
            await self._browser.close()
            await self._pw.stop()

    async def _rate_limit(self, domain):
        """Enforce per-domain rate limiting with jitter."""
        now = time.time()
        last = self._domain_last_request.get(domain, 0)
        delay = PER_DOMAIN_DELAY + random.uniform(0, JITTER)
        wait = delay - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self._domain_last_request[domain] = time.time()

    async def fetch_aiohttp(self, session, url):
        """Fetch a page using aiohttp (fast, no JS)."""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            async with self._aiohttp_sem:
                async with session.get(url, headers=headers, allow_redirects=True,
                                       timeout=aiohttp.ClientTimeout(total=PAGE_TIMEOUT)) as resp:
                    final_url = str(resp.url)
                    ct = resp.headers.get('Content-Type', '').lower()

                    # Handle PDFs
                    if 'pdf' in ct or url.lower().endswith('.pdf'):
                        if resp.content_length and resp.content_length > PDF_MAX_SIZE:
                            return None, final_url, resp.status, "pdf_too_large", "pdf"
                        pdf_bytes = await resp.read()
                        if len(pdf_bytes) > PDF_MAX_SIZE:
                            return None, final_url, resp.status, "pdf_too_large", "pdf"
                        text = extract_pdf_text(pdf_bytes)
                        return text, final_url, resp.status, None, "pdf"

                    if resp.status == 200:
                        html = await resp.text()
                        return html, final_url, resp.status, None, "html"
                    else:
                        err = {403: 'blocked', 404: 'not_found', 429: 'rate_limited',
                               503: 'service_unavailable'}.get(resp.status, f'http_{resp.status}')
                        return None, final_url, resp.status, err, "html"

        except asyncio.TimeoutError:
            return None, url, None, "timeout", "html"
        except aiohttp.ClientSSLError:
            # Try HTTP fallback
            if url.startswith('https://'):
                try:
                    http_url = url.replace('https://', 'http://')
                    async with session.get(http_url, headers=headers, allow_redirects=True,
                                           timeout=aiohttp.ClientTimeout(total=PAGE_TIMEOUT)) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            return html, str(resp.url), resp.status, None, "html"
                except Exception:
                    pass
            return None, url, None, "ssl_error", "html"
        except Exception as e:
            return None, url, None, str(type(e).__name__), "html"

    async def fetch_playwright(self, url):
        """Fetch a page using Playwright (JS rendering)."""
        if not self._browser:
            return None, url, None, "no_browser", "html"

        try:
            async with self._browser_sem:
                context = await self._browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080},
                )
                page = await context.new_page()
                try:
                    response = await page.goto(url, wait_until='networkidle', timeout=PAGE_TIMEOUT * 1000)
                    final_url = page.url
                    status = response.status if response else None

                    if status == 200 or (status and 200 <= status < 400):
                        html = await page.content()
                        return html, final_url, status, None, "html"
                    else:
                        err = {403: 'blocked', 404: 'not_found'}.get(status, f'http_{status}')
                        return None, final_url, status, err, "html"
                finally:
                    await page.close()
                    await context.close()

        except Exception as e:
            err_name = type(e).__name__
            if 'timeout' in str(e).lower() or 'Timeout' in err_name:
                return None, url, None, "timeout", "html"
            return None, url, None, err_name, "html"

    async def crawl_foundation(self, session, foundation):
        """Deep-crawl a single foundation website using priority BFS."""
        start_time = time.time()
        result = FoundationCrawl(
            ein=foundation['ein'],
            name=foundation['name'],
            base_url=foundation['url'],
            tier=foundation['tier'],
        )

        base_url = foundation['url']
        domain = get_domain(base_url)
        visited = set()
        # Priority queue: list of (priority, depth, url, anchor_text)
        queue = [(0, 0, base_url, "homepage")]

        # Add direct grant paths as priority 1, depth 1
        parsed = urlparse(base_url)
        base_origin = f"{parsed.scheme}://{parsed.netloc}"
        for path in DIRECT_GRANT_PATHS:
            direct_url = normalize_url(base_origin + path)
            if direct_url and direct_url not in visited:
                queue.append((1, 1, direct_url, f"direct:{path}"))

        pages_fetched = 0
        use_playwright = False  # Start with aiohttp, upgrade if needed

        while queue and pages_fetched < MAX_PAGES_PER_SITE:
            # Sort by (priority, depth) — fetch most important pages first
            queue.sort(key=lambda x: (x[0], x[1]))

            priority, depth, url, anchor = queue.pop(0)
            normalized = normalize_url(url)
            if not normalized or normalized in visited:
                continue

            # Skip low-priority links at depth > 1
            if priority >= 4 and depth > 0:
                continue

            # Don't go deeper than depth 3
            if depth > 3:
                continue

            visited.add(normalized)
            await self._rate_limit(domain)

            # Decide fetch method
            fetch_method = "aiohttp"
            content = None
            final_url = url
            status = None
            error = None
            content_type = "html"

            # Try aiohttp first
            content, final_url, status, error, content_type = await self.fetch_aiohttp(session, normalized)

            # If aiohttp got blocked/empty and we have Playwright, retry with JS rendering
            if content_type == "html" and self._browser:
                needs_playwright = False
                if error in ('blocked', 'timeout', 'service_unavailable'):
                    needs_playwright = True
                elif content and len(content.strip()) < 500:
                    needs_playwright = True
                elif content:
                    # Check if page is mostly JS-rendered (thin HTML shell)
                    text, _ = extract_text_full(content)
                    if len(text.strip()) < 100 and '<script' in content.lower():
                        needs_playwright = True

                if needs_playwright and pages_fetched < MAX_PAGES_PER_SITE:
                    await self._rate_limit(domain)
                    pw_content, pw_final, pw_status, pw_error, pw_ct = await self.fetch_playwright(normalized)
                    if pw_content and (not error or pw_error is None):
                        content, final_url, status, error, content_type = pw_content, pw_final, pw_status, pw_error, pw_ct
                        fetch_method = "playwright"
                        use_playwright = True

            # Process the fetched content
            text = ""
            title = ""
            if content and content_type == "html":
                text, title = extract_text_full(content)
            elif content and content_type == "pdf":
                text = content  # Already extracted
                title = f"PDF: {url.split('/')[-1]}"

            page_type = self._classify_url(normalized, anchor)
            char_count = len(text)

            page = CrawledPage(
                url=normalized,
                final_url=final_url,
                page_type=page_type,
                priority=priority,
                depth=depth,
                text=text,
                title=title,
                anchor_text=anchor,
                status=status,
                content_type=content_type,
                error=error,
                char_count=char_count,
                fetch_method=fetch_method,
            )
            result.pages.append(asdict(page))
            pages_fetched += 1

            if char_count > 0:
                result.pages_with_content += 1
                result.total_chars += char_count
            if page_type in ('grants', 'application', 'eligibility', 'guidelines'):
                result.grant_pages_found += 1

            # Extract links from HTML and add to queue
            if content and content_type == "html" and depth < 3:
                links = extract_links(content, normalized)
                for link in links:
                    link_url = link['url']
                    link_norm = normalize_url(link_url)
                    if link_norm and link_norm not in visited:
                        new_priority = link['priority']
                        # Boost priority for PDF links (likely guidelines docs)
                        if link_url.lower().endswith('.pdf'):
                            new_priority = min(new_priority, 1)
                            result.pdfs_found.append({
                                'url': link_url,
                                'anchor': link['anchor_text'],
                                'source': normalized,
                            })
                        queue.append((new_priority, depth + 1, link_url, link['anchor_text']))
                        result.discovered_links.append({
                            'url': link_url,
                            'anchor': link['anchor_text'],
                            'priority': new_priority,
                            'source': normalized,
                        })

            # Progress indicator
            if pages_fetched % 10 == 0:
                print(f"    [{foundation['name'][:30]}] {pages_fetched} pages, {result.total_chars:,} chars")

        result.pages_crawled = pages_fetched
        result.crawl_time_seconds = round(time.time() - start_time, 1)
        result.crawl_status = "completed" if pages_fetched > 0 else "failed"

        return result

    def _classify_url(self, url, anchor=""):
        """Classify a page type based on its URL and anchor text."""
        combined = (url + ' ' + anchor).lower()

        if any(p in combined for p in ['eligib', 'requirement', 'criteria', 'limitation', 'who-can', 'who-we-fund']):
            return 'eligibility'
        if any(p in combined for p in ['guideline', 'support-guideline', 'funding-guideline']):
            return 'guidelines'
        if any(p in combined for p in ['apply', 'application', 'how-to', 'loi', 'letter-of-inquiry', 'submission']):
            return 'application'
        if any(p in combined for p in ['grant', 'fund', 'giving', 'grantmak']):
            return 'grants'
        if any(p in combined for p in ['program', 'initiative', 'what-we', 'our-work', 'focus', 'area', 'strateg']):
            return 'programs'
        if any(p in combined for p in ['about', 'mission', 'histor', 'who-we-are']):
            return 'about'
        if any(p in combined for p in ['contact', 'staff', 'team', 'leadership']):
            return 'contact'
        if any(p in combined for p in ['grantee', 'recipient', 'partner']):
            return 'grantees'
        if any(p in combined for p in ['faq', 'frequently']):
            return 'faq'
        if any(p in combined for p in ['annual.?report', 'financ', 'impact']):
            return 'reports'
        if anchor == 'homepage' or url.rstrip('/') == normalize_url(url).rstrip('/').rsplit('/', 1)[0] if '/' in url else True:
            return 'homepage'
        return 'other'


async def main():
    print("=" * 70)
    print("  DEEP CRAWL: Foundation Websites for VetsBoats Eligibility")
    print("=" * 70)
    print(f"\nTargets: {len(FOUNDATIONS)} foundations")
    print(f"Config: max {MAX_PAGES_PER_SITE} pages/site, depth 3, {PER_DOMAIN_DELAY}s delay")
    print(f"Playwright: {'available' if HAS_PLAYWRIGHT else 'NOT available'}")
    print(f"PyPDF2: {'available' if HAS_PYPDF2 else 'NOT available'}")
    print()

    crawler = DeepCrawler()

    # Start Playwright browser
    if HAS_PLAYWRIGHT:
        print("Starting Playwright browser...")
        await crawler.start_browser()

    # Create aiohttp session
    connector = aiohttp.TCPConnector(
        limit=AIOHTTP_CONCURRENCY * 2,
        limit_per_host=2,
        ssl=False,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=PAGE_TIMEOUT * 5, connect=10, sock_read=PAGE_TIMEOUT)
    session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    results = []
    total_start = time.time()

    # Crawl foundations sequentially (they have internal concurrency via priority queue)
    # But we can do 2-3 at a time since they're different domains
    batch_size = 3
    for i in range(0, len(FOUNDATIONS), batch_size):
        batch = FOUNDATIONS[i:i + batch_size]
        print(f"\n--- Batch {i // batch_size + 1}: {', '.join(f['name'][:25] for f in batch)} ---")

        tasks = [crawler.crawl_foundation(session, f) for f in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                foundation = batch[j]
                print(f"  ERROR [{foundation['name']}]: {result}")
                results.append(FoundationCrawl(
                    ein=foundation['ein'],
                    name=foundation['name'],
                    base_url=foundation['url'],
                    tier=foundation['tier'],
                    crawl_status="error",
                    error=str(result),
                ))
            else:
                print(f"  [{result.name[:30]}] {result.pages_crawled} pages, "
                      f"{result.total_chars:,} chars, {result.grant_pages_found} grant pages, "
                      f"{result.crawl_time_seconds}s")
                results.append(result)

    total_time = time.time() - total_start
    await session.close()
    if HAS_PLAYWRIGHT:
        await crawler.stop_browser()

    # ─── Save Results ─────────────────────────────────────────────────────────
    output_path = f"{OUTPUT_DIR}/DATA_2026-02-20_deep_crawl_batch3_raw.json"
    output_data = [asdict(r) for r in results]

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    # ─── Summary Statistics ───────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  CRAWL SUMMARY")
    print("=" * 70)
    print(f"\nTotal time: {total_time:.0f}s ({total_time / 60:.1f} min)")
    print(f"Foundations crawled: {len(results)}")

    total_pages = sum(r.pages_crawled for r in results if isinstance(r, FoundationCrawl))
    total_chars = sum(r.total_chars for r in results if isinstance(r, FoundationCrawl))
    total_grant_pages = sum(r.grant_pages_found for r in results if isinstance(r, FoundationCrawl))
    with_content = sum(1 for r in results if isinstance(r, FoundationCrawl) and r.pages_with_content > 0)

    print(f"Total pages fetched: {total_pages}")
    print(f"Total characters: {total_chars:,}")
    print(f"Grant-relevant pages: {total_grant_pages}")
    print(f"Foundations with content: {with_content}/{len(results)}")

    # Per-foundation summary
    print(f"\n{'Foundation':<35} {'Pages':>5} {'Chars':>10} {'Grant':>5} {'Time':>6}")
    print("-" * 65)
    for r in results:
        if isinstance(r, FoundationCrawl):
            print(f"{r.name[:34]:<35} {r.pages_crawled:>5} {r.total_chars:>10,} "
                  f"{r.grant_pages_found:>5} {r.crawl_time_seconds:>5.0f}s")

    print(f"\nOutput saved to: {output_path}")


if __name__ == '__main__':
    asyncio.run(main())
