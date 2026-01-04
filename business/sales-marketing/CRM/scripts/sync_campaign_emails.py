#!/usr/bin/env python3
"""
Sync Campaign Emails to CRM

Reads sent_tracker.csv and syncs to Supabase campaign_emails table.
Links emails to prospects by email address.

Usage:
    python sync_campaign_emails.py           # Full sync
    python sync_campaign_emails.py --recent  # Only last 7 days
    python sync_campaign_emails.py --dry-run # Preview without syncing
"""

import os
import sys
import argparse
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Supabase credentials
SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

# File paths
EMAIL_CAMPAIGN_DIR = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Email_Campaign"
SENT_TRACKER = os.path.join(EMAIL_CAMPAIGN_DIR, "sent_tracker.csv")

# API headers
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ============================================================================
# API FUNCTIONS
# ============================================================================

def api_request(endpoint: str, method: str = 'GET', data: dict = None) -> Optional[dict]:
    """Make a request to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"

    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=HEADERS, json=data, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=HEADERS, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json() if response.text else None

    except requests.exceptions.RequestException as e:
        print(f"  API error: {e}")
        return None


def get_existing_campaign_emails() -> set:
    """Get set of (email, sent_at) tuples already in database."""
    existing = api_request('campaign_emails?select=email_address,sent_at')
    if not existing:
        return set()

    return {(e['email_address'].lower(), e['sent_at'][:19]) for e in existing}


def get_prospect_email_map() -> Dict[str, int]:
    """Get mapping of email address -> prospect_id."""
    prospects = api_request('prospects?select=id,email&email=neq.null')
    if not prospects:
        return {}

    return {p['email'].lower(): p['id'] for p in prospects if p.get('email')}


def insert_campaign_emails(emails: List[dict]) -> int:
    """Insert campaign emails in batches."""
    if not emails:
        return 0

    # Insert in batches of 100
    batch_size = 100
    inserted = 0

    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        result = api_request('campaign_emails', method='POST', data=batch)
        if result:
            inserted += len(result)
            print(f"  Inserted batch {i//batch_size + 1}: {len(result)} records")
        else:
            print(f"  Failed batch {i//batch_size + 1}")

    return inserted


# ============================================================================
# SYNC LOGIC
# ============================================================================

def sync_sent_tracker(recent_only: bool = False, dry_run: bool = False) -> Dict:
    """
    Sync sent_tracker.csv to Supabase campaign_emails table.

    Args:
        recent_only: If True, only sync last 7 days
        dry_run: If True, preview without inserting

    Returns:
        Dict with sync statistics
    """
    print("\n" + "=" * 60)
    print("CAMPAIGN EMAIL SYNC")
    print("=" * 60)

    # Load sent tracker
    if not os.path.exists(SENT_TRACKER):
        return {'error': f'File not found: {SENT_TRACKER}'}

    print(f"\nReading: {SENT_TRACKER}")
    df = pd.read_csv(SENT_TRACKER)
    print(f"  Total records in file: {len(df)}")

    # Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Filter to recent if requested
    if recent_only:
        cutoff = datetime.now() - timedelta(days=7)
        df = df[df['timestamp'] >= cutoff]
        print(f"  Filtered to last 7 days: {len(df)} records")

    # Get existing records to avoid duplicates
    print("\nChecking for existing records...")
    existing = get_existing_campaign_emails()
    print(f"  Found {len(existing)} existing records in database")

    # Get prospect email map
    print("\nLoading prospect email map...")
    prospect_map = get_prospect_email_map()
    print(f"  Found {len(prospect_map)} prospects with emails")

    # Prepare records for insert
    print("\nPreparing records...")
    to_insert = []
    skipped_existing = 0
    skipped_no_timestamp = 0

    for _, row in df.iterrows():
        # Skip if no valid timestamp
        if pd.isna(row['timestamp']):
            skipped_no_timestamp += 1
            continue

        # Create unique key
        email = str(row['email']).lower()
        sent_at = row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')

        # Skip if already exists
        if (email, sent_at) in existing:
            skipped_existing += 1
            continue

        # Look up prospect ID
        prospect_id = prospect_map.get(email)

        # Build record
        record = {
            'email_address': email,
            'prospect_id': prospect_id,
            'vertical': row.get('vertical', 'unknown'),
            'message_type': row.get('message_type', 'initial'),
            'subject_line': row.get('subject_line'),
            'status': row.get('status', 'UNKNOWN'),
            'error_message': row.get('error_message') if pd.notna(row.get('error_message')) else None,
            'sender_email': row.get('sender_email') if pd.notna(row.get('sender_email')) else None,
            'sent_at': row['timestamp'].isoformat()
        }
        to_insert.append(record)

    print(f"\nRecords to insert: {len(to_insert)}")
    print(f"Skipped (already exists): {skipped_existing}")
    print(f"Skipped (no timestamp): {skipped_no_timestamp}")

    # Count how many have prospect links
    linked = sum(1 for r in to_insert if r['prospect_id'] is not None)
    print(f"Linked to prospects: {linked}/{len(to_insert)}")

    # Dry run preview
    if dry_run:
        print("\n[DRY RUN] Would insert:")
        for r in to_insert[:5]:
            print(f"  {r['email_address']} | {r['vertical']} | {r['status']} | {r['sent_at'][:10]}")
        if len(to_insert) > 5:
            print(f"  ... and {len(to_insert) - 5} more")
        return {
            'dry_run': True,
            'would_insert': len(to_insert),
            'linked_to_prospects': linked
        }

    # Insert records
    if to_insert:
        print("\nInserting records...")
        inserted = insert_campaign_emails(to_insert)
        print(f"\nInserted: {inserted} records")
    else:
        inserted = 0
        print("\nNo new records to insert")

    return {
        'total_in_file': len(df),
        'already_exists': skipped_existing,
        'inserted': inserted,
        'linked_to_prospects': linked
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Sync campaign emails to CRM')
    parser.add_argument('--recent', action='store_true', help='Only sync last 7 days')
    parser.add_argument('--dry-run', action='store_true', help='Preview without inserting')
    args = parser.parse_args()

    stats = sync_sent_tracker(recent_only=args.recent, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()


if __name__ == '__main__':
    main()
