#!/usr/bin/env python3
"""
Enrich phone numbers for foundation management companies by scraping websites
"""

import requests
import re
import time
from urllib.parse import urljoin

SUPABASE_URL = 'https://qisbqmwtfzeiffgtlzpk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo'

# Phone number patterns
PHONE_PATTERNS = [
    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
    r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 123-456-7890
    r'1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 1-123-456-7890
]

# Common contact page paths to check
CONTACT_PATHS = ['', '/contact', '/contact-us', '/about', '/about-us', '/connect']

def extract_phone(text):
    """Extract first valid US phone number from text"""
    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean and validate
            digits = re.sub(r'\D', '', match)
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return None


def fetch_website(url, timeout=10):
    """Fetch website content"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        if not url.startswith('http'):
            url = f'https://{url}'
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.text
    except Exception as e:
        return None


def get_companies():
    """Get foundation mgmt companies from CRM"""
    headers = {'apikey': SUPABASE_KEY}
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/prospects?segment=eq.foundation_mgmt&phone=is.null&select=id,org_name,website',
        headers=headers
    )
    return r.json()


def update_phone(prospect_id, phone):
    """Update phone number in CRM"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.patch(
        f'{SUPABASE_URL}/rest/v1/prospects?id=eq.{prospect_id}',
        headers=headers,
        json={'phone': phone}
    )
    return response.status_code in (200, 204)


def main():
    companies = get_companies()
    print(f"Found {len(companies)} companies without phone numbers\n")

    found = 0
    failed = 0

    for company in companies:
        name = company['org_name']
        website = company['website']
        prospect_id = company['id']

        if not website or website == 'N/A':
            print(f"  {name}: No website")
            failed += 1
            continue

        print(f"  {name} ({website})...", end=" ", flush=True)

        phone = None

        # Try main page and contact pages
        for path in CONTACT_PATHS:
            if phone:
                break

            if path:
                url = f"https://{website.rstrip('/')}{path}"
            else:
                url = f"https://{website}"

            content = fetch_website(url)
            if content:
                phone = extract_phone(content)

            time.sleep(0.3)  # Be polite

        if phone:
            if update_phone(prospect_id, phone):
                print(f"Found: {phone}")
                found += 1
            else:
                print(f"Found {phone} but update failed")
                failed += 1
        else:
            print("No phone found")
            failed += 1

    print(f"\n=== RESULTS ===")
    print(f"  Found phones: {found}")
    print(f"  Not found: {failed}")
    print(f"  Total: {len(companies)}")


if __name__ == '__main__':
    main()
