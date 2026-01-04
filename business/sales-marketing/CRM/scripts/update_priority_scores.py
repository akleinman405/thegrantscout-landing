#!/usr/bin/env python3
"""
Update CRM prospect priority scores based on:
1. Foundation mgmt companies with capacity building grant track record
2. Foundations with capacity building grant track record
3. Underfunded nonprofits (few funders, low revenue)

Priority scoring:
- Tier 1 (highest): Foundation mgmt with capacity building track record
- Tier 2: Foundations with 10+ capacity building grants
- Tier 3: Foundations with any capacity building grants
- Tier 4: Underfunded nonprofits (<=3 funders)
- Tier 5: Other nonprofits
"""

import psycopg2
import urllib.request
import json
from collections import defaultdict

# Supabase config
SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

# Main DB config (read from file)
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='thegrantscout',
        user='postgres',
        password='SHiNYL!ght105'
    )

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

def get_capacity_building_foundations(conn):
    """Get foundations that give capacity building grants"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            foundation_ein,
            COUNT(*) as capacity_grant_count
        FROM f990_2025.fact_grants
        WHERE (
            purpose_text ILIKE '%general support%'
            OR purpose_text ILIKE '%operating support%'
            OR purpose_text ILIKE '%capacity%'
            OR purpose_text ILIKE '%unrestricted%'
        )
        AND foundation_ein IS NOT NULL
        GROUP BY foundation_ein
    """)

    result = {}
    for row in cursor.fetchall():
        result[row[0]] = row[1]
    cursor.close()
    return result

def get_nonprofit_funders(conn):
    """Get unique funder count for each nonprofit"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            recipient_ein,
            COUNT(DISTINCT foundation_ein) as unique_funders,
            SUM(amount) as total_received
        FROM f990_2025.fact_grants
        WHERE recipient_ein IS NOT NULL
        GROUP BY recipient_ein
    """)

    result = {}
    for row in cursor.fetchall():
        result[row[0]] = {
            'unique_funders': row[1],
            'total_received': row[2] or 0
        }
    cursor.close()
    return result

def calculate_priority(prospect, capacity_foundations, nonprofit_funders):
    """Calculate priority tier and ICP score for a prospect"""
    segment = prospect.get('segment')
    ein = prospect.get('ein')

    if not ein:
        return 5, 10  # Default tier 5, score 10

    # Foundation management companies - highest priority
    if segment == 'foundation_mgmt':
        # Check if they manage foundations that give capacity building grants
        # For now, give them tier 1 by default (highest priority)
        return 1, 100

    # Foundations
    elif segment == 'foundation':
        capacity_count = capacity_foundations.get(ein, 0)
        if capacity_count >= 10:
            return 2, 90  # Tier 2: Strong capacity building track record
        elif capacity_count >= 1:
            return 3, 70  # Tier 3: Some capacity building grants
        else:
            return 4, 40  # Tier 4: No capacity building history

    # Nonprofits
    else:
        funder_data = nonprofit_funders.get(ein, {})
        unique_funders = funder_data.get('unique_funders', 0)
        total_received = funder_data.get('total_received', 0)

        # Underfunded: few funders or low total funding
        if unique_funders <= 3:
            if total_received < 100000:
                return 3, 80  # High priority - underfunded
            else:
                return 4, 60  # Medium priority
        elif unique_funders <= 10:
            return 4, 50
        else:
            return 5, 30  # Well-funded, lower priority

def main():
    print("Starting priority score update...")

    # Connect to main DB
    print("Connecting to thegrantscout database...")
    conn = get_db_connection()

    # Get capacity building foundations
    print("Querying capacity building foundations...")
    capacity_foundations = get_capacity_building_foundations(conn)
    print(f"  Found {len(capacity_foundations)} foundations with capacity building grants")

    # Get nonprofit funder data
    print("Querying nonprofit funder data...")
    nonprofit_funders = get_nonprofit_funders(conn)
    print(f"  Found funder data for {len(nonprofit_funders)} nonprofits")

    conn.close()

    # Get CRM prospects
    print("Fetching CRM prospects from Supabase...")
    prospects = supabase_request("prospects?select=id,ein,segment,tier,icp_score&limit=10000")
    print(f"  Found {len(prospects)} prospects")

    # Calculate new scores
    print("Calculating priority scores...")
    updates = defaultdict(list)

    for prospect in prospects:
        new_tier, new_score = calculate_priority(prospect, capacity_foundations, nonprofit_funders)

        # Only update if changed
        if prospect.get('tier') != new_tier or prospect.get('icp_score') != new_score:
            updates[(new_tier, new_score)].append(prospect['id'])

    # Summary before update
    print("\nPriority distribution:")
    tier_counts = defaultdict(int)
    for prospect in prospects:
        new_tier, _ = calculate_priority(prospect, capacity_foundations, nonprofit_funders)
        tier_counts[new_tier] += 1

    for tier in sorted(tier_counts.keys()):
        print(f"  Tier {tier}: {tier_counts[tier]} prospects")

    # Update in batches
    print("\nUpdating prospects...")
    updated_count = 0
    for (tier, score), ids in updates.items():
        # Update in chunks of 100
        for i in range(0, len(ids), 100):
            chunk = ids[i:i+100]
            id_list = ','.join(f'"{id}"' for id in chunk)

            url = f"prospects?id=in.({','.join(str(id) for id in chunk)})"
            try:
                result = supabase_request(url, method='PATCH', data={
                    'tier': tier,
                    'icp_score': score
                })
                updated_count += len(chunk)
                print(f"  Updated {len(chunk)} prospects to Tier {tier}, Score {score}")
            except Exception as e:
                print(f"  Error updating batch: {e}")

    print(f"\nDone! Updated {updated_count} prospects.")

if __name__ == '__main__':
    main()
