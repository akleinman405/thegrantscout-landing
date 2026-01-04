#!/usr/bin/env python3
"""
Enrich CRM prospects with descriptions from f990 data.
Also adds last_contacted_at column if missing.
"""

import psycopg2
import requests
import time

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


def get_nonprofit_descriptions():
    """Get mission descriptions for nonprofits from f990 data"""
    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    query = """
    SELECT ein, mission_description
    FROM f990_2025.nonprofit_returns
    WHERE mission_description IS NOT NULL
      AND length(mission_description) > 20
    """

    cur.execute(query)
    descriptions = {row[0]: row[1][:500] for row in cur.fetchall()}  # Truncate to 500 chars
    cur.close()
    conn.close()

    return descriptions


def get_foundation_descriptions():
    """Get descriptions for foundations from pf_returns"""
    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    # Get the best available description for each foundation
    query = """
    SELECT ein,
           COALESCE(
               NULLIF(activity_or_mission_desc, ''),
               NULLIF(primary_exempt_purpose, ''),
               NULLIF(mission_desc, '')
           ) as description
    FROM f990_2025.pf_returns
    WHERE activity_or_mission_desc IS NOT NULL
       OR primary_exempt_purpose IS NOT NULL
       OR mission_desc IS NOT NULL
    """

    cur.execute(query)
    # Filter out junk descriptions (less than 20 chars or clearly not mission statements)
    descriptions = {}
    junk_terms = ['n/a', 'none', 'see', 'attached', 'schedule', 'cash', 'fees', 'furniture']
    for row in cur.fetchall():
        ein, desc = row
        if desc and len(desc) > 20:
            desc_lower = desc.lower()
            if not any(term in desc_lower for term in junk_terms):
                descriptions[ein] = desc[:500]

    cur.close()
    conn.close()

    return descriptions


def get_crm_prospects():
    """Get all prospects from CRM"""
    headers = {'apikey': SUPABASE_KEY}
    prospects = []
    offset = 0
    limit = 1000

    while True:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/prospects?select=id,ein,segment&offset={offset}&limit={limit}',
            headers=headers
        )
        batch = r.json()
        if not batch:
            break
        prospects.extend(batch)
        offset += limit
        if len(batch) < limit:
            break

    return prospects


def batch_update_descriptions(updates, batch_size=100):
    """Batch update prospect descriptions in CRM"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

    total_updated = 0
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]

        # Use upsert with id as the conflict key
        for item in batch:
            try:
                r = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/prospects?id=eq.{item["id"]}',
                    headers=headers,
                    json={'description': item['description']},
                    timeout=30
                )
                if r.status_code in (200, 204):
                    total_updated += 1
            except Exception as e:
                print(f"    Error updating {item['id']}: {e}")
                continue

        print(f"  Batch {i // batch_size + 1}: updated {total_updated} so far...")
        time.sleep(0.5)  # Small delay between batches

    return total_updated


def main():
    print("=== ENRICHING CRM WITH DESCRIPTIONS ===\n")

    # Get descriptions from f990 data
    print("Loading nonprofit descriptions...")
    nonprofit_descs = get_nonprofit_descriptions()
    print(f"  Found {len(nonprofit_descs):,} nonprofit descriptions")

    print("Loading foundation descriptions...")
    foundation_descs = get_foundation_descriptions()
    print(f"  Found {len(foundation_descs):,} foundation descriptions")

    # Get CRM prospects
    print("\nLoading CRM prospects...")
    prospects = get_crm_prospects()
    print(f"  Found {len(prospects):,} prospects in CRM")

    # Match and prepare updates
    print("\nPreparing updates...")
    updates = []
    no_match = 0

    for p in prospects:
        ein = p.get('ein')
        if not ein:
            continue

        # Try to find description
        desc = None
        if p.get('segment') == 'nonprofit':
            desc = nonprofit_descs.get(ein)
        elif p.get('segment') in ('foundation', 'foundation_mgmt'):
            desc = foundation_descs.get(ein)

        if desc:
            updates.append({'id': p['id'], 'description': desc})
        else:
            no_match += 1

    print(f"  Found descriptions for {len(updates):,} prospects")
    print(f"  No description for {no_match:,} prospects")

    # Batch update
    print("\nUpdating CRM (this may take a few minutes)...")
    updated = batch_update_descriptions(updates)

    print(f"\n=== COMPLETE ===")
    print(f"  Updated: {updated:,}")
    print(f"  No description found: {no_match:,}")


if __name__ == '__main__':
    main()
