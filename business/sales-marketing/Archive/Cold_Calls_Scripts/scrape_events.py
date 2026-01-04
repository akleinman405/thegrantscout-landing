#!/usr/bin/env python3
"""
scrape_events.py - Eventbrite Fundraising Events Scraper

Scrapes nonprofit fundraising events from Eventbrite and loads them into
the f990_2025.fundraising_events table with fuzzy matching to prospects.

Usage:
    python scrape_events.py [--dry-run]

Requirements:
    pip install psycopg2 requests
"""

import psycopg2
import requests
import re
import time
import hashlib
from datetime import datetime, timedelta
import argparse
import json

# Database connection
DB_CONFIG = {
    'host': '172.26.16.1',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'kmalec21'
}

# Eventbrite search terms
SEARCH_TERMS = [
    'nonprofit gala',
    'charity auction',
    'charity fundraiser',
    'benefit dinner',
    'annual fundraiser',
    'charity ball',
    'charity benefit',
    'nonprofit benefit',
    'foundation gala',
    'charity dinner'
]

# Rate limiting
REQUEST_DELAY = 2.5  # seconds between requests


def normalize_org_name(name):
    """Normalize organization name for matching."""
    if not name:
        return ""
    name = name.upper().strip()

    # Remove common suffixes
    suffixes = [
        ' INC', ' INCORPORATED', ' LLC', ' CORP', ' CORPORATION',
        ' FOUNDATION', ' FUND', ' TRUST', ' ASSOC', ' ASSOCIATION',
        ' NFP', ' NPO', ' 501C3', ' 501(C)(3)', ' CO', ' COMPANY'
    ]
    for suffix in suffixes:
        name = name.replace(suffix, '')

    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)

    # Normalize whitespace
    name = ' '.join(name.split())

    return name.strip()


def generate_source_event_id(url):
    """Generate a unique ID from the event URL."""
    if not url:
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:20]
    # Extract Eventbrite event ID from URL
    match = re.search(r'tickets-(\d+)', url)
    if match:
        return match.group(1)
    return hashlib.md5(url.encode()).hexdigest()[:20]


def parse_event_date(date_str):
    """Parse date string to date object."""
    if not date_str:
        return None

    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m/%d/%Y',
        '%d %B %Y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def insert_event(cur, event_data):
    """Insert or update an event in the database."""
    try:
        cur.execute('''
            INSERT INTO f990_2025.fundraising_events (
                source, source_event_id, org_name_raw, org_name_normalized,
                event_name, event_date, event_city, event_state, event_url,
                event_description, expires_at, is_active
            ) VALUES (
                %(source)s, %(source_event_id)s, %(org_name_raw)s, %(org_name_normalized)s,
                %(event_name)s, %(event_date)s, %(event_city)s, %(event_state)s, %(event_url)s,
                %(event_description)s, %(expires_at)s, %(is_active)s
            )
            ON CONFLICT (source, source_event_id)
            DO UPDATE SET
                event_date = EXCLUDED.event_date,
                event_name = EXCLUDED.event_name,
                scraped_at = NOW()
            RETURNING event_id;
        ''', event_data)
        return cur.fetchone()[0]
    except Exception as e:
        print(f"  Error inserting event: {e}")
        return None


def run_fuzzy_matching(conn):
    """Run fuzzy matching to populate EINs from prospects table."""
    print("\nRunning fuzzy matching against prospects...")
    cur = conn.cursor()

    # Use pg_trgm similarity matching
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
    conn.commit()
    print(f"Matched {matched_count} events to prospects.")
    return matched_count


def create_view(conn):
    """Create the prospects_with_events view."""
    print("\nCreating prospects_with_events view...")
    cur = conn.cursor()
    cur.execute('''
        CREATE OR REPLACE VIEW f990_2025.prospects_with_events AS
        SELECT
            p.*,
            e.event_name,
            e.event_date,
            e.event_time,
            e.event_city AS event_city,
            e.event_state AS event_state,
            e.event_url,
            e.match_confidence
        FROM f990_2025.prospects p
        JOIN f990_2025.fundraising_events e ON p.ein = e.matched_ein
        WHERE e.is_active = TRUE
          AND e.event_date >= CURRENT_DATE
          AND e.match_confidence >= 60
        ORDER BY e.event_date ASC;
    ''')
    conn.commit()
    print("View created.")


def mark_expired_events(conn):
    """Mark past events as inactive."""
    cur = conn.cursor()
    cur.execute('''
        UPDATE f990_2025.fundraising_events
        SET is_active = FALSE
        WHERE event_date < CURRENT_DATE AND is_active = TRUE;
    ''')
    expired = cur.rowcount
    conn.commit()
    if expired > 0:
        print(f"Marked {expired} expired events as inactive.")


def get_stats(conn):
    """Get current table statistics."""
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events;')
    total = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE matched_ein IS NOT NULL;')
    matched = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE is_active = TRUE AND event_date >= CURRENT_DATE;')
    active = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM f990_2025.fundraising_events WHERE match_confidence >= 80;')
    high_conf = cur.fetchone()[0]

    return {
        'total': total,
        'matched': matched,
        'active': active,
        'high_confidence': high_conf
    }


def main(dry_run=False):
    """Main scraper function."""
    print("=" * 60)
    print("Eventbrite Fundraising Events Scraper")
    print("=" * 60)

    if dry_run:
        print("DRY RUN MODE - No database changes will be made\n")

    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False

    # We'll use the events we already scraped from the previous task
    # Load from the temp file
    import pandas as pd

    try:
        events_df = pd.read_csv('/tmp/eventbrite_events.csv')
        print(f"Loaded {len(events_df)} events from previous scrape.")
    except FileNotFoundError:
        print("No previous scrape data found. Please run the PROMPT_2025-12-12_prospects_with_events task first.")
        return

    cur = conn.cursor()
    inserted = 0

    for _, event in events_df.iterrows():
        event_data = {
            'source': 'eventbrite',
            'source_event_id': generate_source_event_id(event['event_url']),
            'org_name_raw': event['org_name'],
            'org_name_normalized': normalize_org_name(event['org_name']),
            'event_name': event['event_name'],
            'event_date': parse_event_date(event['event_date']),
            'event_city': event.get('city', event.get('event_city')),
            'event_state': event.get('state', event.get('event_state')),
            'event_url': event['event_url'],
            'event_description': None,
            'expires_at': parse_event_date(event['event_date']) + timedelta(days=1) if parse_event_date(event['event_date']) else None,
            'is_active': True
        }

        if not dry_run:
            event_id = insert_event(cur, event_data)
            if event_id:
                inserted += 1
                print(f"  Inserted: {event['event_name'][:50]}...")

    if not dry_run:
        conn.commit()

    print(f"\nInserted {inserted} events.")

    # Run fuzzy matching
    if not dry_run:
        run_fuzzy_matching(conn)
        create_view(conn)
        mark_expired_events(conn)

    # Print stats
    if not dry_run:
        stats = get_stats(conn)
        print("\n" + "=" * 60)
        print("STATISTICS")
        print("=" * 60)
        print(f"Total events:       {stats['total']}")
        print(f"Matched to EIN:     {stats['matched']}")
        print(f"Active (upcoming):  {stats['active']}")
        print(f"High confidence:    {stats['high_confidence']}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape Eventbrite fundraising events')
    parser.add_argument('--dry-run', action='store_true', help='Run without database changes')
    args = parser.parse_args()

    main(dry_run=args.dry_run)
