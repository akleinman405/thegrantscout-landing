#!/usr/bin/env python3
"""
scrape_events_large.py - Large-scale fundraising event aggregation

Scrapes nonprofit fundraising events from multiple sources and loads them into
the f990_2025.fundraising_events table with fuzzy matching to prospects.

Usage:
    python scrape_events_large.py --source eventbrite
    python scrape_events_large.py --source all
    python scrape_events_large.py --resume
    python scrape_events_large.py --source eventbrite --states CA,NY,TX
    python scrape_events_large.py --match-only

Requirements:
    pip install psycopg2 requests beautifulsoup4
"""

import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import csv

# Database connection
DB_CONFIG = {
    'host': '172.26.16.1',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'kmalec21'
}

# Checkpoint file
CHECKPOINT_FILE = Path('/tmp/eventbrite_scrape_checkpoint.json')
EVENTS_FILE = Path('/tmp/scraped_events_large.csv')

# State slugs for Eventbrite URLs
STATE_SLUGS = {
    'AL': 'al--alabama', 'AK': 'ak--alaska', 'AZ': 'az--arizona',
    'AR': 'ar--arkansas', 'CA': 'ca--california', 'CO': 'co--colorado',
    'CT': 'ct--connecticut', 'DE': 'de--delaware', 'FL': 'fl--florida',
    'GA': 'ga--georgia', 'HI': 'hi--hawaii', 'ID': 'id--idaho',
    'IL': 'il--illinois', 'IN': 'in--indiana', 'IA': 'ia--iowa',
    'KS': 'ks--kansas', 'KY': 'ky--kentucky', 'LA': 'la--louisiana',
    'ME': 'me--maine', 'MD': 'md--maryland', 'MA': 'ma--massachusetts',
    'MI': 'mi--michigan', 'MN': 'mn--minnesota', 'MS': 'ms--mississippi',
    'MO': 'mo--missouri', 'MT': 'mt--montana', 'NE': 'ne--nebraska',
    'NV': 'nv--nevada', 'NH': 'nh--new-hampshire', 'NJ': 'nj--new-jersey',
    'NM': 'nm--new-mexico', 'NY': 'ny--new-york', 'NC': 'nc--north-carolina',
    'ND': 'nd--north-dakota', 'OH': 'oh--ohio', 'OK': 'ok--oklahoma',
    'OR': 'or--oregon', 'PA': 'pa--pennsylvania', 'RI': 'ri--rhode-island',
    'SC': 'sc--south-carolina', 'SD': 'sd--south-dakota', 'TN': 'tn--tennessee',
    'TX': 'tx--texas', 'UT': 'ut--utah', 'VT': 'vt--vermont',
    'VA': 'va--virginia', 'WA': 'wa--washington', 'WV': 'wv--west-virginia',
    'WI': 'wi--wisconsin', 'WY': 'wy--wyoming', 'DC': 'dc--washington-dc'
}

# Search terms for Eventbrite
SEARCH_TERMS = [
    'nonprofit gala',
    'charity auction',
    'charity fundraiser',
    'benefit dinner',
    'charity ball',
    'charity walk',
    'charity run',
    'nonprofit benefit',
    'foundation gala',
    'annual fundraiser',
    '5k charity',
    'charity golf',
    'silent auction'
]

# Rate limiting
REQUEST_DELAY = 2.5  # seconds between requests

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]


def normalize_org_name(name):
    """Normalize organization name for matching."""
    if not name:
        return ""
    name = name.upper().strip()
    suffixes = [
        ' INC', ' INCORPORATED', ' LLC', ' CORP', ' CORPORATION',
        ' FOUNDATION', ' FUND', ' TRUST', ' ASSOC', ' ASSOCIATION',
        ' NFP', ' NPO', ' 501C3', ' 501(C)(3)', ' CO', ' COMPANY'
    ]
    for suffix in suffixes:
        name = name.replace(suffix, '')
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name.strip()


def generate_source_event_id(url, source='eventbrite'):
    """Generate a unique ID from the event URL."""
    if not url:
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:20]
    if source == 'eventbrite':
        match = re.search(r'tickets-(\d+)', url)
        if match:
            return match.group(1)
    return hashlib.md5(url.encode()).hexdigest()[:20]


def parse_date(date_str):
    """Parse various date formats."""
    if not date_str:
        return None

    # Clean up the string
    date_str = date_str.strip()

    formats = [
        '%Y-%m-%d',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m/%d/%Y',
        '%d %B %Y',
        '%A, %B %d, %Y',
        '%a, %b %d, %Y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Try to extract date from text like "Sat, Dec 14, 2025"
    match = re.search(r'(\w+),?\s*(\w+)\s+(\d+),?\s*(\d{4})', date_str)
    if match:
        try:
            month_day_year = f"{match.group(2)} {match.group(3)}, {match.group(4)}"
            return datetime.strptime(month_day_year, '%b %d, %Y').date()
        except:
            pass

    return None


def save_checkpoint(completed_states, event_count):
    """Save progress checkpoint."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'completed_states': completed_states,
            'event_count': event_count,
            'timestamp': datetime.now().isoformat()
        }, f)


def load_checkpoint():
    """Load progress checkpoint."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'completed_states': [], 'event_count': 0}


def save_events_csv(events, append=True):
    """Save events to CSV file."""
    mode = 'a' if append and EVENTS_FILE.exists() else 'w'
    with open(EVENTS_FILE, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'source', 'source_event_id', 'org_name', 'event_name',
            'event_date', 'event_city', 'event_state', 'event_url'
        ])
        if mode == 'w':
            writer.writeheader()
        for event in events:
            writer.writerow(event)


def load_events_csv():
    """Load events from CSV file."""
    events = []
    if EVENTS_FILE.exists():
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            events = list(reader)
    return events


def insert_events_to_db(events):
    """Insert events into database with deduplication."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    inserted = 0
    duplicates = 0

    for event in events:
        try:
            event_date = parse_date(event.get('event_date'))
            expires_at = event_date + timedelta(days=1) if event_date else None

            cur.execute('''
                INSERT INTO f990_2025.fundraising_events (
                    source, source_event_id, org_name_raw, org_name_normalized,
                    event_name, event_date, event_city, event_state, event_url,
                    expires_at, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (source, source_event_id) DO NOTHING
                RETURNING event_id;
            ''', (
                event.get('source', 'eventbrite'),
                generate_source_event_id(event.get('event_url'), event.get('source', 'eventbrite')),
                event.get('org_name'),
                normalize_org_name(event.get('org_name')),
                event.get('event_name'),
                event_date,
                event.get('event_city'),
                event.get('event_state'),
                event.get('event_url'),
                expires_at,
                True
            ))

            result = cur.fetchone()
            if result:
                inserted += 1
            else:
                duplicates += 1

        except Exception as e:
            print(f"  Error inserting event: {e}")

    conn.close()
    return inserted, duplicates


def run_fuzzy_matching():
    """Run fuzzy matching to populate EINs from prospects table."""
    print("\nRunning fuzzy matching against prospects...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute('''
        WITH event_matches AS (
            SELECT
                e.event_id,
                e.org_name_normalized,
                p.ein,
                p.org_name,
                similarity(e.org_name_normalized, UPPER(p.org_name)) AS sim_score
            FROM f990_2025.fundraising_events e
            CROSS JOIN LATERAL (
                SELECT ein, org_name
                FROM f990_2025.prospects
                WHERE similarity(e.org_name_normalized, UPPER(org_name)) > 0.4
                ORDER BY similarity(e.org_name_normalized, UPPER(org_name)) DESC
                LIMIT 1
            ) p
            WHERE e.matched_ein IS NULL
        )
        UPDATE f990_2025.fundraising_events e
        SET
            matched_ein = m.ein,
            matched_org_name = m.org_name,
            match_confidence = ROUND(m.sim_score * 100)::SMALLINT,
            match_method = CASE
                WHEN m.sim_score >= 0.95 THEN 'exact'
                ELSE 'fuzzy'
            END
        FROM event_matches m
        WHERE e.event_id = m.event_id;
    ''')

    matched_count = cur.rowcount
    conn.close()
    print(f"Matched {matched_count} events to prospects.")
    return matched_count


def get_stats():
    """Get current table statistics."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    stats = {}

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events;')
    stats['total'] = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE matched_ein IS NOT NULL;')
    stats['matched'] = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE is_active = TRUE AND event_date >= CURRENT_DATE;')
    stats['active'] = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE match_confidence >= 80;')
    stats['high_confidence'] = cur.fetchone()[0]

    cur.execute('''
        SELECT source, COUNT(*) FROM f990_2025.fundraising_events
        GROUP BY source ORDER BY COUNT(*) DESC;
    ''')
    stats['by_source'] = cur.fetchall()

    cur.execute('''
        SELECT event_state, COUNT(*) FROM f990_2025.fundraising_events
        WHERE event_state IS NOT NULL
        GROUP BY event_state ORDER BY COUNT(*) DESC LIMIT 10;
    ''')
    stats['by_state'] = cur.fetchall()

    conn.close()
    return stats


def print_stats():
    """Print current statistics."""
    stats = get_stats()
    print("\n" + "=" * 60)
    print("CURRENT STATISTICS")
    print("=" * 60)
    print(f"Total events:           {stats['total']:,}")
    print(f"Matched to EIN:         {stats['matched']:,}")
    print(f"Active (upcoming):      {stats['active']:,}")
    print(f"High confidence (≥80%): {stats['high_confidence']:,}")

    print("\nBy Source:")
    for source, count in stats['by_source']:
        print(f"  {source}: {count:,}")

    print("\nTop 10 States:")
    for state, count in stats['by_state']:
        print(f"  {state}: {count:,}")


def main():
    parser = argparse.ArgumentParser(description='Large-scale event scraping')
    parser.add_argument('--source', choices=['eventbrite', 'facebook', 'google', 'givesmart', 'all'],
                        default='eventbrite', help='Source to scrape')
    parser.add_argument('--states', type=str, help='Comma-separated list of states (e.g., CA,NY,TX)')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--match-only', action='store_true', help='Only run matching, no scraping')
    parser.add_argument('--stats-only', action='store_true', help='Only print statistics')
    args = parser.parse_args()

    print("=" * 60)
    print("Large-Scale Fundraising Events Scraper")
    print("=" * 60)

    if args.stats_only:
        print_stats()
        return

    if args.match_only:
        run_fuzzy_matching()
        print_stats()
        return

    # Load events from CSV if exists
    events = load_events_csv()
    print(f"Loaded {len(events)} existing events from CSV")

    # Insert to database
    if events:
        print(f"\nInserting {len(events)} events to database...")
        inserted, dupes = insert_events_to_db(events)
        print(f"Inserted: {inserted}, Duplicates skipped: {dupes}")

    # Run matching
    run_fuzzy_matching()

    # Print final stats
    print_stats()

    print("\nDone!")


if __name__ == '__main__':
    main()
