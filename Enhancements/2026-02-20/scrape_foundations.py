#!/usr/bin/env python3
"""
Foundation Website Scraper for VetsBoats Eligibility Verification

Reads the 340 hard-filtered prospects, scrapes foundation websites for
grant eligibility info, and saves structured text for classification.

Output: DATA_2026-02-20_scraped_foundations.json
"""

import asyncio
import csv
import json
import hashlib
import random
import re
import time
import sys
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field, asdict
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras

# --- Config ---
OUTPUT_DIR = '/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-20'
CSV_PATH = '/Users/aleckleinman/Documents/TheGrantScout/5. Runs/VetsBoats/2026-02-20/DATA_2026-02-20_vetsboats_hardfiltered_prospects.csv'
CONCURRENCY = 10
PER_DOMAIN_DELAY = 0.5
TIMEOUT = 15
MAX_PAGES_PER_SITE = 6
MAX_CHARS_PER_PAGE = 3000

# 15 foundations already manually reviewed
ALREADY_REVIEWED = {
    '381359217',  # Kresge
    '943100217',  # Hilton
    '941655673',  # Hewlett
    '770348912',  # Sobrato
    '954560243',  # GSD
    '650464177',  # Knight
    '131628151',  # Carnegie
    '381359264',  # Kellogg
    '410754835',  # McKnight
    '954292101',  # CA Wellness
    '251721100',  # Heinz
    '472746460',  # Dominion Energy
    '956054814',  # Weingart
    '237093598',  # MacArthur
    '131684331',  # Ford
}

VETERAN_KEYWORDS_REGEX = r'(veteran|military|armed forces|service member|wounded warrior|adaptive sailing|therapeutic sailing|adaptive recreation)'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
]

# Pages to look for related to grants/eligibility
GRANT_PAGE_PATTERNS = [
    r'/grant', r'/apply', r'/eligib', r'/fund', r'/program',
    r'/guidelines', r'/rfp', r'/rfa', r'/application',
    r'/how-to-apply', r'/grantee', r'/giving', r'/philanthropic',
    r'/for-grantseekers', r'/grant-seekers', r'/nonprofit',
    r'/faq', r'/about', r'/mission', r'/focus', r'/criteria',
    r'/what-we-fund', r'/areas-of-focus', r'/our-work',
]

DIRECT_GRANT_PATHS = [
    '/grants', '/apply', '/funding', '/programs',
    '/eligibility', '/guidelines', '/how-to-apply',
    '/for-grantseekers', '/grant-seekers', '/grantmaking',
    '/about', '/about-us', '/faq', '/our-work',
    '/what-we-fund', '/areas-of-focus', '/focus-areas',
]


@dataclass
class PageContent:
    url: str
    page_type: str
    text: str
    status: Optional[int] = None
    error: Optional[str] = None


@dataclass
class FoundationScrape:
    ein: str
    name: str
    website: str
    state: str
    assets: Optional[float] = None
    annual_giving: Optional[float] = None
    vet_grant_count: int = 0
    vet_grant_amount: float = 0
    sample_grants: list = field(default_factory=list)
    pages: list = field(default_factory=list)
    scrape_status: str = 'pending'
    error: Optional[str] = None


def clean_url(url):
    if not url or url.strip().upper() in ('', 'N/A', 'NONE', '0', 'NULL'):
        return None
    url = url.strip()
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"
    except Exception:
        return None


def extract_text(html, max_chars=MAX_CHARS_PER_PAGE):
    """Extract clean text from HTML, stripping scripts/styles."""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    return text[:max_chars]


def get_domain(url):
    try:
        parsed = urlparse(url)
        d = parsed.netloc.lower()
        if d.startswith('www.'):
            d = d[4:]
        return d
    except Exception:
        return ''


def load_prospects():
    """Load foundations from CSV that passed all 3 filters and have valid URLs."""
    prospects = []
    skipped_no_url = 0
    skipped_reviewed = 0
    skipped_filters = 0

    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ein = row['foundation_ein']
            filter_passes = int(row.get('filter_passes', 0))

            if filter_passes < 3:
                skipped_filters += 1
                continue

            if ein in ALREADY_REVIEWED:
                skipped_reviewed += 1
                continue

            url = clean_url(row.get('website_url', ''))
            if not url:
                skipped_no_url += 1
                continue

            prospects.append({
                'ein': ein,
                'name': row.get('foundation_name', ''),
                'website': url,
                'state': row.get('state', ''),
                'assets': float(row['total_assets']) if row.get('total_assets') else None,
                'annual_giving': float(row['annual_giving']) if row.get('annual_giving') else None,
                'vet_grant_count': int(row.get('veteran_grant_count', 0) or 0),
                'vet_grant_amount': float(row.get('veteran_grant_amount', 0) or 0),
            })

    print(f"Loaded {len(prospects)} foundations to scrape")
    print(f"  Skipped: {skipped_filters} didn't pass all 3 filters")
    print(f"  Skipped: {skipped_reviewed} already reviewed")
    print(f"  Skipped: {skipped_no_url} no valid URL")
    return prospects


def load_grant_samples(eins):
    """Query DB for top 5 veteran-related grants per foundation."""
    conn = psycopg2.connect(host='localhost', port=5432, database='thegrantscout', user='postgres')
    conn.set_session(readonly=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT foundation_ein, recipient_name_raw, recipient_state, amount, purpose_text, tax_year
        FROM f990_2025.fact_grants
        WHERE foundation_ein = ANY(%s)
          AND LOWER(purpose_text) ~ %s
        ORDER BY foundation_ein, amount DESC NULLS LAST
    """, (eins, VETERAN_KEYWORDS_REGEX))

    grants_by_ein = {}
    for row in cur.fetchall():
        ein = row['foundation_ein']
        if ein not in grants_by_ein:
            grants_by_ein[ein] = []
        if len(grants_by_ein[ein]) < 5:
            grants_by_ein[ein].append({
                'recipient': row['recipient_name_raw'],
                'state': row['recipient_state'],
                'amount': float(row['amount']) if row['amount'] else None,
                'purpose': row['purpose_text'][:200] if row['purpose_text'] else None,
                'year': row['tax_year'],
            })

    cur.close()
    conn.close()
    return grants_by_ein


class FoundationScraper:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(CONCURRENCY)
        self._domain_last_request = {}
        self.stats = {'completed': 0, 'failed': 0, 'blocked': 0, 'timeout': 0}

    async def scrape_all(self, prospects, grant_samples):
        connector = aiohttp.TCPConnector(
            limit=CONCURRENCY * 2,
            limit_per_host=2,
            ssl=False,
            enable_cleanup_closed=True,
        )
        timeout = aiohttp.ClientTimeout(total=TIMEOUT * 4, connect=5, sock_read=TIMEOUT)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        results = []
        async with aiohttp.ClientSession(connector=connector, headers=headers, timeout=timeout) as session:
            tasks = []
            for p in prospects:
                task = self._scrape_with_sem(session, p, grant_samples.get(p['ein'], []))
                tasks.append(task)

            total = len(tasks)
            for i, coro in enumerate(asyncio.as_completed(tasks)):
                result = await coro
                results.append(result)
                status = result.scrape_status
                if status == 'completed':
                    self.stats['completed'] += 1
                elif status in ('blocked', 'rate_limited'):
                    self.stats['blocked'] += 1
                elif status == 'timeout':
                    self.stats['timeout'] += 1
                else:
                    self.stats['failed'] += 1

                done = i + 1
                if done % 20 == 0 or done == total:
                    print(f"  [{done}/{total}] OK={self.stats['completed']} FAIL={self.stats['failed']} "
                          f"BLOCK={self.stats['blocked']} TIMEOUT={self.stats['timeout']}")

        return results

    async def _scrape_with_sem(self, session, prospect, grants):
        async with self.semaphore:
            return await self._scrape_site(session, prospect, grants)

    async def _scrape_site(self, session, prospect, grants):
        result = FoundationScrape(
            ein=prospect['ein'],
            name=prospect['name'],
            website=prospect['website'],
            state=prospect['state'],
            assets=prospect.get('assets'),
            annual_giving=prospect.get('annual_giving'),
            vet_grant_count=prospect.get('vet_grant_count', 0),
            vet_grant_amount=prospect.get('vet_grant_amount', 0),
            sample_grants=grants,
        )

        url = prospect['website']
        domain = get_domain(url)

        # 1. Fetch homepage
        await self._rate_limit(domain)
        html, page = await self._fetch(session, url, 'homepage')
        result.pages.append(asdict(page))

        if page.error:
            result.scrape_status = page.error
            result.error = page.error
            return result

        # 2. Find grant-related subpages
        subpage_urls = self._find_grant_pages(html, url)
        pages_fetched = 0

        for sub_url in subpage_urls:
            if pages_fetched >= MAX_PAGES_PER_SITE - 1:
                break

            page_type = self._classify_page(sub_url)
            await self._rate_limit(domain)
            sub_html, sub_page = await self._fetch(session, sub_url, page_type)
            result.pages.append(asdict(sub_page))
            pages_fetched += 1

        result.scrape_status = 'completed'
        return result

    async def _rate_limit(self, domain):
        now = time.time()
        last = self._domain_last_request.get(domain, 0)
        wait = PER_DOMAIN_DELAY - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self._domain_last_request[domain] = time.time()

    async def _fetch(self, session, url, page_type):
        req_headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            async with session.get(url, headers=req_headers, allow_redirects=True) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    text = extract_text(html)
                    return html, PageContent(url=url, page_type=page_type, text=text, status=200)
                else:
                    err = {403: 'blocked', 404: 'not_found', 429: 'rate_limited'}.get(resp.status, f'http_{resp.status}')
                    return None, PageContent(url=url, page_type=page_type, text='', status=resp.status, error=err)
        except asyncio.TimeoutError:
            return None, PageContent(url=url, page_type=page_type, text='', error='timeout')
        except aiohttp.ClientSSLError:
            if url.startswith('https://'):
                http_url = url.replace('https://', 'http://')
                try:
                    async with session.get(http_url, headers=req_headers, allow_redirects=True) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            text = extract_text(html)
                            return html, PageContent(url=http_url, page_type=page_type, text=text, status=200)
                except Exception:
                    pass
            return None, PageContent(url=url, page_type=page_type, text='', error='ssl_error')
        except aiohttp.ClientConnectorError:
            return None, PageContent(url=url, page_type=page_type, text='', error='connection_error')
        except Exception as e:
            return None, PageContent(url=url, page_type=page_type, text='', error=str(type(e).__name__))

    def _find_grant_pages(self, html, base_url):
        """Find grant/apply/about pages from links + direct URL construction."""
        found = []
        seen = {base_url}

        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    for pattern in GRANT_PAGE_PATTERNS:
                        if re.search(pattern, href):
                            full_url = urljoin(base_url, link['href'])
                            if full_url not in seen and get_domain(full_url) == get_domain(base_url):
                                found.append(full_url)
                                seen.add(full_url)
                            break
            except Exception:
                pass

        # Add direct paths not already found
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        for path in DIRECT_GRANT_PATHS:
            direct_url = base + path
            if direct_url not in seen:
                found.append(direct_url)
                seen.add(direct_url)

        return found[:MAX_PAGES_PER_SITE * 2]  # return more than needed, we'll cap during fetch

    def _classify_page(self, url):
        lower = url.lower()
        if any(p in lower for p in ['/grant', '/fund', '/giving', '/grantmak']):
            return 'grants'
        if any(p in lower for p in ['/apply', '/eligib', '/guideline', '/how-to', '/rfp']):
            return 'application'
        if any(p in lower for p in ['/about', '/mission', '/focus', '/our-work', '/what-we']):
            return 'about'
        if any(p in lower for p in ['/faq', '/criteria']):
            return 'faq'
        if any(p in lower for p in ['/program']):
            return 'programs'
        return 'other'


async def main():
    print("=== Foundation Website Scraper for VetsBoats ===\n")

    # Step 1: Load prospects
    print("Step 1: Loading prospects from CSV...")
    prospects = load_prospects()
    if not prospects:
        print("No prospects to scrape!")
        return

    # Step 2: Load grant samples
    print(f"\nStep 2: Loading veteran grant samples for {len(prospects)} foundations...")
    eins = [p['ein'] for p in prospects]
    grant_samples = load_grant_samples(eins)
    with_grants = sum(1 for e in eins if e in grant_samples)
    print(f"  {with_grants} foundations have veteran-related grants in DB")

    # Step 3: Scrape websites
    print(f"\nStep 3: Scraping {len(prospects)} foundation websites...")
    print(f"  Concurrency: {CONCURRENCY}, Delay: {PER_DOMAIN_DELAY}s, Timeout: {TIMEOUT}s")
    start = time.time()

    scraper = FoundationScraper()
    results = await scraper.scrape_all(prospects, grant_samples)

    elapsed = time.time() - start
    print(f"\nScraping complete in {elapsed:.1f}s")
    print(f"  Completed: {scraper.stats['completed']}")
    print(f"  Failed: {scraper.stats['failed']}")
    print(f"  Blocked: {scraper.stats['blocked']}")
    print(f"  Timeout: {scraper.stats['timeout']}")

    # Step 4: Save results
    output_path = f"{OUTPUT_DIR}/DATA_2026-02-20_scraped_foundations.json"
    output_data = []
    for r in results:
        d = asdict(r)
        output_data.append(d)

    # Sort by name for easier review
    output_data.sort(key=lambda x: x['name'])

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    # Stats
    total_pages = sum(len(r.pages) for r in results)
    pages_with_text = sum(1 for r in results for p in r.pages
                          if (p.get('text', '') if isinstance(p, dict) else getattr(p, 'text', '')))
    print(f"\nSaved {len(output_data)} foundations to {output_path}")
    print(f"  Total pages fetched: {total_pages}")
    print(f"  Pages with text: {pages_with_text}")

    # Quick check: how many have meaningful content?
    meaningful = 0
    for r in results:
        if r.scrape_status != 'completed':
            continue
        for p in r.pages:
            txt = p.get('text', '') if isinstance(p, dict) else getattr(p, 'text', '')
            if len(txt) > 200:
                meaningful += 1
                break
    print(f"  Foundations with meaningful content (>200 chars): {meaningful}")


if __name__ == '__main__':
    asyncio.run(main())
