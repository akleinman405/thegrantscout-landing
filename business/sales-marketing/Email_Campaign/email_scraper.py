#!/usr/bin/env python3
"""
Email Scraper for TheGrantScout
Scrapes contact emails from nonprofit websites.
Connects directly to Supabase for input/output.

Usage:
    python3 email_scraper.py --limit 100              # Scrape 100 prospects
    python3 email_scraper.py --limit 50 --test        # Test mode (no DB updates)
    python3 email_scraper.py --limit 500 --offset 100 # Skip first 100
"""

import asyncio
import aiohttp
import re
import argparse
import urllib.request
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Supabase config
SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

# Email extraction patterns
EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

# Emails to exclude (patterns and domains that are not the org's real email)
EXCLUDE_PATTERNS = [
    r'noreply@', r'no-reply@', r'donotreply@', r'do-not-reply@',
    r'privacy@', r'unsubscribe@', r'careers@', r'jobs@', r'hr@',
    r'webmaster@', r'postmaster@', r'mailer-daemon@', r'bounce@',
    r'@example\.', r'@test\.', r'@localhost', r'@domain\.',
    r'\.png$', r'\.jpg$', r'\.gif$', r'\.svg$', r'\.pdf$',
    r'@sentry\.', r'@wix\.', r'@squarespace\.', r'@wordpress\.',
    r'@godaddy\.', r'@google\.', r'@facebook\.', r'@twitter\.',
    r'user@domain', r'email@domain', r'name@domain', r'your@',
    r'sample@', r'placeholder@', r'test@test',
    # False positives - third-party grant/application portals
    r'@grantstation\.', r'@foundant\.', r'@fluxx\.', r'@submittable\.',
    r'@instrumentl\.', r'@smartsimple\.', r'@blackbaud\.',
]

# URLs to skip (not real nonprofit websites)
SKIP_URL_PATTERNS = [
    r'icims\.com', r'workday\.com', r'greenhouse\.io', r'lever\.co',  # Job sites
    r'linkedin\.com', r'facebook\.com', r'twitter\.com', r'instagram\.com',  # Social
    r'grantstation\.com', r'foundant\.com', r'fluxx\.io',  # Grant portals
    r'youtube\.com', r'vimeo\.com',  # Video
]

# Priority email prefixes (order matters)
PRIORITY_PREFIXES = [
    'contact', 'info', 'hello', 'inquiries', 'general',
    'admin', 'office', 'support', 'mail', 'email',
    'giving', 'development', 'donate', 'grants', 'partnership'
]

# Contact page patterns
CONTACT_PATTERNS = [
    '/contact', '/contact-us', '/contactus', '/get-in-touch',
    '/about/contact', '/about-us/contact', '/reach-us',
    '/connect', '/about', '/about-us', '/who-we-are',
    '/support', '/donate', '/get-involved'
]


def supabase_request(endpoint, method='GET', data=None):
    """Make request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def get_prospects_to_scrape(limit=100, offset=0):
    """Get prospects with website but no email from Supabase"""
    # Filter: has real website (not empty, not N/A), no email
    endpoint = (
        f"prospects?select=id,ein,org_name,website"
        f"&website=neq."
        f"&website=neq.N/A"
        f"&website=neq.NONE"
        f"&website=neq.0"
        f"&email=is.null"
        f"&limit={limit}"
        f"&offset={offset}"
    )
    return supabase_request(endpoint)


def update_prospect_email(prospect_id, email, confidence, source_page=None):
    """Update prospect with scraped email"""
    data = {
        'email': email,
        'email_source': 'scraped',
        'email_enriched_at': datetime.now().isoformat()
    }

    endpoint = f"prospects?id=eq.{prospect_id}"
    return supabase_request(endpoint, method='PATCH', data=data)


def should_skip_url(url):
    """Check if URL should be skipped (not a real nonprofit website)"""
    if not url:
        return True
    url_lower = url.lower()
    for pattern in SKIP_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True
    return False


def normalize_url(url):
    """Normalize URL for scraping"""
    if not url:
        return None

    url = url.strip()

    # Handle ALL CAPS URLs
    url = url.lower()

    # Skip if it's not a real nonprofit website
    if should_skip_url(url):
        return None

    # Remove common prefixes that might be wrong
    url = url.replace('www.www.', 'www.')

    # Add protocol if missing
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    # Ensure starts with www if no subdomain
    parsed = urlparse(url)
    domain_parts = parsed.netloc.split('.')

    # Skip if already has subdomain or is www
    if len(domain_parts) == 2:
        # Add www
        url = url.replace('://', '://www.')

    return url


def is_valid_email(email, domain=None):
    """Check if email should be included"""
    if not email:
        return False

    email_lower = email.lower().strip()

    # Must not be empty
    if not email_lower:
        return False

    # Length check
    if len(email_lower) < 6 or len(email_lower) > 100:
        return False

    # Exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, email_lower):
            return False

    # Must have valid format
    if not EMAIL_PATTERN.match(email_lower):
        return False

    # Check for valid TLD
    parts = email_lower.split('.')
    if len(parts) < 2:
        return False

    tld = parts[-1]
    if len(tld) < 2 or len(tld) > 10:
        return False

    # Check for obviously fake emails
    if email_lower.count('@') != 1:
        return False

    local_part = email_lower.split('@')[0]
    if len(local_part) < 2:
        return False

    # Prefer emails from same domain as website
    if domain:
        email_domain = email_lower.split('@')[1]
        # Remove www. prefix for comparison
        clean_domain = domain.replace('www.', '').lower()
        if email_domain == clean_domain:
            return True
        # Still valid if different domain, just less priority

    return True


def score_email(email, website_domain=None):
    """Score email by priority (higher is better)"""
    email_lower = email.lower()
    prefix = email_lower.split('@')[0]
    email_domain = email_lower.split('@')[1]

    score = 0

    # Matching domain is critical
    if website_domain:
        clean_domain = website_domain.replace('www.', '').replace('https://', '').replace('http://', '').lower()
        if email_domain == clean_domain:
            score += 100
        else:
            # Email from different domain - likely wrong
            score -= 50

    # Name-based emails (firstname@) get priority
    if '.' not in prefix and prefix.isalpha() and 3 <= len(prefix) <= 15:
        score += 50

    # First.last@ format
    if '.' in prefix and all(p.isalpha() for p in prefix.split('.')):
        score += 45

    # Priority prefixes
    for i, pref in enumerate(PRIORITY_PREFIXES):
        if prefix.startswith(pref):
            score += 40 - i
            break

    return score


def extract_emails_from_html(html, base_url):
    """Extract emails from HTML content"""
    emails = set()

    # Get domain for validation
    parsed = urlparse(base_url)
    domain = parsed.netloc

    # Find all email-like strings
    found = EMAIL_PATTERN.findall(html)

    for email in found:
        email = email.lower().strip()
        if is_valid_email(email, domain):
            emails.add(email)

    # Also check mailto: links
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0].strip().lower()
                if is_valid_email(email, domain):
                    emails.add(email)
    except Exception:
        pass

    return emails, domain


def find_contact_links(html, base_url):
    """Find links to contact pages"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        return []

    contact_urls = []

    for link in soup.find_all('a', href=True):
        try:
            href = link['href'].lower()
            text = link.get_text().lower()

            # Check if link text or href suggests contact page
            is_contact = any(p in href for p in CONTACT_PATTERNS) or \
                         'contact' in text or 'reach us' in text or \
                         'get in touch' in text or 'email us' in text

            if is_contact:
                full_url = urljoin(base_url, link['href'])
                if full_url not in contact_urls and len(contact_urls) < 5:
                    contact_urls.append(full_url)
        except Exception:
            continue

    return contact_urls


async def fetch_url(session, url, timeout=12):
    """Fetch URL with error handling"""
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
            allow_redirects=True,
            ssl=False
        ) as response:
            if response.status == 200:
                return await response.text()
    except asyncio.TimeoutError:
        pass
    except aiohttp.ClientError:
        pass
    except Exception:
        pass

    return None


async def scrape_website(session, prospect):
    """Scrape a single website for emails"""
    website = prospect.get('website', '')
    prospect_id = prospect.get('id')
    org_name = prospect.get('org_name', '')

    result = {
        'id': prospect_id,
        'org_name': org_name,
        'website': website,
        'email': None,
        'all_emails': [],
        'source_page': None,
        'confidence': 'none',
        'error': None
    }

    url = normalize_url(website)
    if not url:
        if should_skip_url(website):
            result['error'] = 'Skipped (not nonprofit site)'
        else:
            result['error'] = 'Invalid URL'
        return result

    # Try with https first
    html = await fetch_url(session, url)

    # If failed, try http
    if not html and url.startswith('https://'):
        http_url = url.replace('https://', 'http://')
        html = await fetch_url(session, http_url)
        if html:
            url = http_url

    # If still failed, try without www
    if not html:
        alt_url = url.replace('://www.', '://')
        html = await fetch_url(session, alt_url)
        if html:
            url = alt_url

    if not html:
        result['error'] = 'Failed to fetch'
        return result

    # Extract emails from homepage
    emails, domain = extract_emails_from_html(html, url)

    # If no emails on homepage, try contact pages
    if not emails:
        contact_links = find_contact_links(html, url)
        for contact_url in contact_links:
            contact_html = await fetch_url(session, contact_url)
            if contact_html:
                contact_emails, _ = extract_emails_from_html(contact_html, contact_url)
                if contact_emails:
                    emails.update(contact_emails)
                    if emails:
                        result['source_page'] = contact_url
                        break
    else:
        result['source_page'] = url

    if emails:
        # Score and sort emails
        scored = [(e, score_email(e, domain)) for e in emails]
        scored.sort(key=lambda x: -x[1])

        # Only use emails with positive score (matching domain)
        valid_emails = [(e, s) for e, s in scored if s > 0]

        if valid_emails:
            result['all_emails'] = [e[0] for e in valid_emails]
            result['email'] = valid_emails[0][0]

            # Set confidence
            top_score = valid_emails[0][1]
            if top_score >= 140:
                result['confidence'] = 'high'  # Matching domain + name-based
            elif top_score >= 100:
                result['confidence'] = 'high'  # Matching domain
            elif top_score >= 50:
                result['confidence'] = 'medium'
            else:
                result['confidence'] = 'low'

    return result


async def scrape_batch(prospects, concurrency=15):
    """Scrape a batch of websites concurrently"""
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [scrape_website(session, p) for p in prospects]
        results = await asyncio.gather(*tasks)

    return results


def main():
    import sys

    parser = argparse.ArgumentParser(description='Scrape emails from nonprofit websites')
    parser.add_argument('--limit', type=int, default=20, help='Max websites to scrape')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrent requests')
    parser.add_argument('--offset', type=int, default=0, help='Skip first N rows')
    parser.add_argument('--test', action='store_true', help='Test mode (no DB updates)')
    args = parser.parse_args()

    print(f"Email Scraper for TheGrantScout", flush=True)
    print(f"================================", flush=True)
    print(f"Mode: {'TEST (no DB updates)' if args.test else 'LIVE'}", flush=True)
    print(f"Limit: {args.limit}, Offset: {args.offset}, Concurrency: {args.concurrency}", flush=True)
    print(flush=True)

    # Get prospects from Supabase
    print("Fetching prospects from Supabase...", flush=True)
    try:
        prospects = get_prospects_to_scrape(args.limit, args.offset)
        print(f"  Found {len(prospects)} prospects to scrape", flush=True)
    except Exception as e:
        print(f"  Error fetching prospects: {e}", flush=True)
        return

    if not prospects:
        print("  No prospects need scraping (all have emails or no websites)", flush=True)
        return

    # Show what we're scraping
    print(f"\nProspects to scrape:", flush=True)
    for p in prospects[:5]:
        print(f"  {p.get('org_name', 'N/A')[:35]} | {p.get('website', 'N/A')[:35]}", flush=True)
    if len(prospects) > 5:
        print(f"  ... and {len(prospects) - 5} more", flush=True)

    # Run scraper
    print(f"\nScraping with {args.concurrency} concurrent requests...", flush=True)
    start_time = datetime.now()

    results = asyncio.run(scrape_batch(prospects, args.concurrency))

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"Completed in {elapsed:.1f} seconds ({len(results)/elapsed:.1f} sites/sec)", flush=True)

    # Analyze results
    success = [r for r in results if r['email']]
    failed = [r for r in results if r['error']]
    no_email = [r for r in results if not r['email'] and not r['error']]

    print(f"\nResults:")
    print(f"  Emails found: {len(success)} ({100*len(success)/len(results):.1f}%)")
    print(f"  No email found: {len(no_email)}")
    print(f"  Failed to fetch: {len(failed)}")

    # Confidence breakdown
    high = sum(1 for r in results if r['confidence'] == 'high')
    medium = sum(1 for r in results if r['confidence'] == 'medium')
    low = sum(1 for r in results if r['confidence'] == 'low')
    print(f"\nConfidence:")
    print(f"  High: {high}")
    print(f"  Medium: {medium}")
    print(f"  Low: {low}")

    # Show sample results
    print(f"\nEmails found:")
    for r in success[:15]:
        print(f"  {r['org_name'][:35]:35} | {r['email']:35} | {r['confidence']}")

    if len(success) > 15:
        print(f"  ... and {len(success) - 15} more")

    # Update Supabase (unless test mode)
    if not args.test and success:
        print(f"\nUpdating Supabase...")
        updated = 0
        for r in success:
            try:
                update_prospect_email(r['id'], r['email'], r['confidence'], r['source_page'])
                updated += 1
            except Exception as e:
                print(f"  Error updating {r['org_name']}: {e}")
        print(f"  Updated {updated} records in Supabase")
    elif args.test:
        print(f"\nTEST MODE - No database updates made")

    # Show failures for debugging
    if failed and len(failed) <= 10:
        print(f"\nFailed URLs:")
        for r in failed:
            print(f"  {r['website']}")


if __name__ == '__main__':
    main()
