#!/usr/bin/env python3
"""
Import prospects from local PostgreSQL to Supabase CRM
"""

import psycopg2
import requests
import json
from datetime import datetime

# Local PostgreSQL
LOCAL_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'kmalec21'
}

# Supabase
SUPABASE_URL = 'https://qisbqmwtfzeiffgtlzpk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo'

BATCH_SIZE = 500  # Supabase batch limit

def get_local_prospects():
    """Fetch prospects from local PostgreSQL"""
    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    query = """
    SELECT
        ein,
        org_name,
        contact_name,
        contact_title,
        contact_phone as phone,
        contact_email as email,
        COALESCE(places_website, f990_website, website) as website,
        city,
        state,
        ntee_code,
        total_revenue::bigint as annual_budget,
        icp_score,
        priority_tier as tier,
        notes,
        CASE
            WHEN form_type = '990PF' THEN 'foundation'
            ELSE 'nonprofit'
        END as segment
    FROM f990_2025.prospects
    WHERE contact_phone IS NOT NULL
      AND contact_phone != ''
    ORDER BY priority_tier NULLS LAST, icp_score DESC NULLS LAST
    """

    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert to list of dicts
    prospects = []
    for row in rows:
        prospect = dict(zip(columns, row))
        # Clean up None values and convert types
        for key, val in prospect.items():
            if val is None:
                prospect[key] = None
            elif isinstance(val, (int, float)) and key == 'annual_budget':
                prospect[key] = int(val) if val else None
        prospects.append(prospect)

    return prospects


def create_source_list():
    """Create a source list for this import"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    source_list = {
        'name': 'Initial Import - Nonprofits',
        'criteria': 'All nonprofits from ICP scoring model with phone numbers',
        'file_origin': 'f990_2025.prospects table',
        'segment': 'nonprofit',
        'notes': f'Imported on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    }

    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/source_lists',
        headers=headers,
        json=source_list
    )

    if response.status_code in (200, 201):
        result = response.json()
        source_id = result[0]['id'] if isinstance(result, list) else result['id']
        print(f"Created source list with ID: {source_id}")
        return source_id
    else:
        print(f"Failed to create source list: {response.status_code}")
        print(response.text)
        return None


def import_batch(prospects, source_list_id):
    """Import a batch of prospects to Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    # Add source_list_id to each prospect
    for p in prospects:
        p['source_list_id'] = source_list_id
        p['status'] = 'not_contacted'

    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/prospects',
        headers=headers,
        json=prospects
    )

    return response.status_code in (200, 201)


def main():
    print("Fetching prospects from local database...")
    prospects = get_local_prospects()
    print(f"Found {len(prospects):,} prospects with phone numbers")

    # Show tier breakdown
    tiers = {}
    for p in prospects:
        tier = p.get('tier') or 'None'
        tiers[tier] = tiers.get(tier, 0) + 1
    print("\nTier breakdown:")
    for tier in sorted(tiers.keys(), key=lambda x: (x is None, x)):
        print(f"  Tier {tier}: {tiers[tier]:,}")

    print("\nCreating source list...")
    source_list_id = create_source_list()
    if not source_list_id:
        print("Failed to create source list. Aborting.")
        return

    print(f"\nImporting {len(prospects):,} prospects in batches of {BATCH_SIZE}...")

    success_count = 0
    fail_count = 0

    for i in range(0, len(prospects), BATCH_SIZE):
        batch = prospects[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(prospects) + BATCH_SIZE - 1) // BATCH_SIZE

        if import_batch(batch, source_list_id):
            success_count += len(batch)
            print(f"  Batch {batch_num}/{total_batches}: {len(batch)} imported ({success_count:,} total)")
        else:
            fail_count += len(batch)
            print(f"  Batch {batch_num}/{total_batches}: FAILED")

    print(f"\nImport complete!")
    print(f"  Success: {success_count:,}")
    print(f"  Failed: {fail_count:,}")

    # Update source list record count
    if success_count > 0:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        requests.patch(
            f'{SUPABASE_URL}/rest/v1/source_lists?id=eq.{source_list_id}',
            headers=headers,
            json={'record_count': success_count}
        )
        print(f"\nUpdated source list record count to {success_count:,}")


if __name__ == '__main__':
    main()
