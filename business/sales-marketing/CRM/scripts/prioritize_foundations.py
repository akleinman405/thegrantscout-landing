#!/usr/bin/env python3
"""
Prioritize foundations in CRM based on:
1. Capacity/general support grants (more flexible funding)
2. Likelihood to answer phone (has dedicated contact, email, etc.)
"""

import psycopg2
import requests

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


def get_foundation_scores():
    """Get foundations with capacity grant scores and phone responsiveness indicators"""
    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    query = """
    WITH foundation_grant_profile AS (
        SELECT
            fg.foundation_ein,
            COUNT(*) as total_grants,
            COUNT(CASE WHEN fg.purpose_text ILIKE '%capacity%' THEN 1 END) as capacity_grants,
            COUNT(CASE WHEN fg.purpose_text ILIKE '%general%support%' OR fg.purpose_text ILIKE '%general%operating%' THEN 1 END) as general_support,
            COUNT(CASE WHEN fg.purpose_text ILIKE '%unrestricted%' THEN 1 END) as unrestricted
        FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein IN (
            SELECT DISTINCT ein
            FROM f990_2025.pf_returns
            WHERE grants_to_organizations_ind = true
              AND only_contri_to_preselected_ind = false
        )
        GROUP BY fg.foundation_ein
    ),
    latest_returns AS (
        SELECT ein, MAX(tax_year) as max_year
        FROM f990_2025.pf_returns
        WHERE grants_to_organizations_ind = true
          AND only_contri_to_preselected_ind = false
        GROUP BY ein
    )
    SELECT
        pr.ein,
        pr.business_name,
        fgp.capacity_grants,
        fgp.general_support,
        fgp.unrestricted,
        pr.app_contact_name,
        pr.app_contact_email,
        pr.app_contact_phone,
        -- Score components
        CASE
            WHEN pr.app_contact_name IS NOT NULL
                 AND pr.app_contact_name NOT ILIKE '%' || pr.business_name || '%'
                 AND pr.app_contact_name NOT ILIKE '%FOUNDATION%'
                 AND LENGTH(pr.app_contact_name) < 50
            THEN 2 ELSE 0
        END as named_contact_score,
        CASE
            WHEN pr.app_contact_email IS NOT NULL
                 AND pr.app_contact_email LIKE '%@%'
            THEN 2 ELSE 0
        END as email_score,
        CASE
            WHEN pr.app_contact_phone IS NOT NULL AND pr.app_contact_phone != ''
            THEN 1 ELSE 0
        END as app_phone_score
    FROM f990_2025.pf_returns pr
    JOIN latest_returns lr ON pr.ein = lr.ein AND pr.tax_year = lr.max_year
    LEFT JOIN foundation_grant_profile fgp ON pr.ein = fgp.foundation_ein
    WHERE pr.grants_to_organizations_ind = true
      AND pr.only_contri_to_preselected_ind = false
      AND (pr.phone_num IS NOT NULL OR pr.app_contact_phone IS NOT NULL)
    """

    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    foundations = []
    for row in rows:
        data = dict(zip(columns, row))

        # Calculate priority score (higher = better)
        capacity_score = min((data.get('capacity_grants') or 0), 100)  # Cap at 100
        general_score = min((data.get('general_support') or 0) + (data.get('unrestricted') or 0), 100) // 2
        phone_responsiveness = (data.get('named_contact_score') or 0) + (data.get('email_score') or 0) + (data.get('app_phone_score') or 0)

        # Combined score: capacity grants most important, then general support, then responsiveness
        priority_score = capacity_score * 3 + general_score * 2 + phone_responsiveness * 10

        foundations.append({
            'ein': data['ein'],
            'name': data['business_name'],
            'capacity_grants': data.get('capacity_grants') or 0,
            'general_support': (data.get('general_support') or 0) + (data.get('unrestricted') or 0),
            'phone_responsiveness': phone_responsiveness,
            'priority_score': priority_score
        })

    # Sort by priority score
    foundations.sort(key=lambda x: x['priority_score'], reverse=True)
    return foundations


def update_foundation_tiers(foundations):
    """Update foundation tiers in CRM based on priority scores"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

    # First, get all foundations in CRM
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/prospects?segment=eq.foundation&select=id,ein',
        headers={'apikey': SUPABASE_KEY}
    )
    crm_foundations = {f['ein']: f['id'] for f in r.json() if f.get('ein')}

    # Create EIN to priority rank mapping
    ein_to_rank = {}
    for i, f in enumerate(foundations):
        ein_to_rank[f['ein']] = i + 1

    # Update tiers based on ranking
    # Top 100 = Tier 2 (highest foundation tier)
    # 101-500 = Tier 3
    # 501+ = Tier 4

    tier_2_updated = 0
    tier_3_updated = 0
    tier_4_updated = 0

    for ein, prospect_id in crm_foundations.items():
        rank = ein_to_rank.get(ein)
        if rank:
            if rank <= 100:
                new_tier = 2
                tier_2_updated += 1
            elif rank <= 500:
                new_tier = 3
                tier_3_updated += 1
            else:
                new_tier = 4
                tier_4_updated += 1

            # Also update ICP score based on capacity grants
            fdn = next((f for f in foundations if f['ein'] == ein), None)
            icp_score = 0
            if fdn:
                icp_score = min(fdn['capacity_grants'] + fdn['general_support'] // 10, 100)

            requests.patch(
                f'{SUPABASE_URL}/rest/v1/prospects?id=eq.{prospect_id}',
                headers=headers,
                json={'tier': new_tier, 'icp_score': icp_score}
            )

    return tier_2_updated, tier_3_updated, tier_4_updated


def main():
    print("=== PRIORITIZING FOUNDATIONS ===\n")

    print("Calculating priority scores...")
    foundations = get_foundation_scores()
    print(f"Scored {len(foundations)} foundations\n")

    print("Top 20 foundations by priority:")
    print("-" * 80)
    print(f"{'Rank':<5} {'Foundation':<40} {'Capacity':<10} {'Gen/Unrestr':<12} {'Phone Score':<12}")
    print("-" * 80)
    for i, f in enumerate(foundations[:20], 1):
        print(f"{i:<5} {f['name'][:39]:<40} {f['capacity_grants']:<10} {f['general_support']:<12} {f['phone_responsiveness']:<12}")

    print("\nUpdating CRM tiers...")
    t2, t3, t4 = update_foundation_tiers(foundations)
    print(f"  Tier 2 (Top 100): {t2}")
    print(f"  Tier 3 (101-500): {t3}")
    print(f"  Tier 4 (500+): {t4}")

    print("\n=== DONE ===")


if __name__ == '__main__':
    main()
