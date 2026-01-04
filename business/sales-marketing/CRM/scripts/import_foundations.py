#!/usr/bin/env python3
"""
Import foundation mgmt companies and open foundations to Supabase CRM
Priority: foundation_mgmt (tier 1) > foundations (tier 2) > nonprofits (tier 3+)
"""

import psycopg2
import requests
import csv
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

BATCH_SIZE = 100

def create_source_list(name, criteria, segment, file_origin=None):
    """Create a source list for this import"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    source_list = {
        'name': name,
        'criteria': criteria,
        'file_origin': file_origin,
        'segment': segment,
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
        print(f"  Created source list '{name}' with ID: {source_id}")
        return source_id
    else:
        print(f"  Failed to create source list: {response.status_code}")
        print(response.text)
        return None


def import_batch(prospects):
    """Import a batch of prospects to Supabase"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/prospects',
        headers=headers,
        json=prospects
    )

    return response.status_code in (200, 201)


def update_source_list_count(source_list_id, count):
    """Update record count on source list"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    requests.patch(
        f'{SUPABASE_URL}/rest/v1/source_lists?id=eq.{source_list_id}',
        headers=headers,
        json={'record_count': count}
    )


def import_foundation_mgmt_companies():
    """Import foundation management companies from CSV"""
    print("\n=== FOUNDATION MANAGEMENT COMPANIES ===")

    csv_path = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/2. Foundations/DATA_2025-12-17_non_bank_foundation_mgmt_companies.csv'

    # Create source list
    source_list_id = create_source_list(
        name='Foundation Management Companies',
        criteria='Non-bank foundation managers, advisors, and fiscal sponsors',
        segment='foundation_mgmt',
        file_origin='DATA_2025-12-17_non_bank_foundation_mgmt_companies.csv'
    )

    if not source_list_id:
        return 0

    prospects = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            # Skip membership associations and directories (can't really cold call them)
            if row.get('type') in ('Membership Association', 'Membership Network', 'Directory'):
                continue

            prospect = {
                'org_name': row['company_name'],
                'website': row.get('website') or None,
                'city': row.get('hq_city') or None,
                'state': row.get('hq_state') or None,
                'segment': 'foundation_mgmt',
                'tier': 1,  # Highest priority
                'status': 'not_contacted',
                'source_list_id': source_list_id,
                'notes': f"Type: {row.get('type', 'Unknown')}. Services: {row.get('services', 'N/A')}"
            }
            prospects.append(prospect)

    print(f"  Found {len(prospects)} callable foundation mgmt companies")

    if prospects and import_batch(prospects):
        update_source_list_count(source_list_id, len(prospects))
        print(f"  Imported {len(prospects)} foundation mgmt companies (Tier 1)")
        return len(prospects)
    else:
        print("  Failed to import foundation mgmt companies")
        return 0


def import_open_foundations():
    """Import open-to-applications foundations from PostgreSQL"""
    print("\n=== OPEN FOUNDATIONS ===")

    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    query = """
    WITH latest AS (
        SELECT ein, MAX(tax_year) as max_year
        FROM f990_2025.pf_returns
        WHERE grants_to_organizations_ind = true
          AND only_contri_to_preselected_ind = false
        GROUP BY ein
    )
    SELECT
        pr.ein,
        pr.business_name as org_name,
        pr.app_contact_name as contact_name,
        COALESCE(pr.app_contact_phone, pr.phone_num) as phone,
        COALESCE(pr.app_contact_email, pr.email_address_txt) as email,
        pr.website_url as website,
        pr.city,
        pr.state,
        pr.total_assets_eoy_amt as total_assets
    FROM f990_2025.pf_returns pr
    JOIN latest l ON pr.ein = l.ein AND pr.tax_year = l.max_year
    WHERE pr.grants_to_organizations_ind = true
      AND pr.only_contri_to_preselected_ind = false
      AND (pr.phone_num IS NOT NULL AND pr.phone_num != ''
           OR pr.app_contact_phone IS NOT NULL AND pr.app_contact_phone != '')
    ORDER BY pr.total_assets_eoy_amt DESC NULLS LAST
    """

    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"  Found {len(rows)} open foundations with phone numbers")

    # Create source list
    source_list_id = create_source_list(
        name='Open Foundations',
        criteria='Foundations accepting applications (only_contri_to_preselected_ind = false) with phone numbers',
        segment='foundation',
        file_origin='f990_2025.pf_returns table'
    )

    if not source_list_id:
        return 0

    # Convert to prospect format
    prospects = []
    for row in rows:
        data = dict(zip(columns, row))

        # Clean phone number
        phone = data.get('phone')
        if phone:
            phone = ''.join(c for c in str(phone) if c.isdigit())
            if len(phone) == 10:
                phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            elif len(phone) == 11 and phone[0] == '1':
                phone = f"({phone[1:4]}) {phone[4:7]}-{phone[7:]}"

        prospect = {
            'ein': data['ein'],
            'org_name': data['org_name'],
            'contact_name': data.get('contact_name'),
            'phone': phone,
            'email': data.get('email'),
            'website': data.get('website'),
            'city': data.get('city'),
            'state': data.get('state'),
            'annual_budget': int(data['total_assets']) if data.get('total_assets') else None,
            'segment': 'foundation',
            'tier': 2,  # Second priority (after foundation mgmt)
            'status': 'not_contacted',
            'source_list_id': source_list_id
        }
        prospects.append(prospect)

    # Import in batches
    success_count = 0
    for i in range(0, len(prospects), BATCH_SIZE):
        batch = prospects[i:i+BATCH_SIZE]
        if import_batch(batch):
            success_count += len(batch)
            print(f"  Batch {(i // BATCH_SIZE) + 1}: {success_count} imported")
        else:
            print(f"  Batch {(i // BATCH_SIZE) + 1}: FAILED")

    update_source_list_count(source_list_id, success_count)
    print(f"  Imported {success_count} foundations (Tier 2)")
    return success_count


def update_nonprofit_tiers():
    """Update existing nonprofit prospects to have tier 3+ (lower priority than foundations)"""
    print("\n=== UPDATING NONPROFIT TIERS ===")

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

    # Update tier 1 nonprofits to tier 3
    response = requests.patch(
        f'{SUPABASE_URL}/rest/v1/prospects?segment=eq.nonprofit&tier=eq.1',
        headers=headers,
        json={'tier': 3}
    )

    # Update tier 2 nonprofits to tier 4
    response = requests.patch(
        f'{SUPABASE_URL}/rest/v1/prospects?segment=eq.nonprofit&tier=eq.2',
        headers=headers,
        json={'tier': 4}
    )

    # Update tier 3 nonprofits to tier 5
    response = requests.patch(
        f'{SUPABASE_URL}/rest/v1/prospects?segment=eq.nonprofit&tier=eq.3',
        headers=headers,
        json={'tier': 5}
    )

    print("  Updated nonprofit tiers: 1→3, 2→4, 3→5")
    print("  New priority order: Fdn Mgmt (1) > Foundations (2) > Nonprofits (3-5)")


def main():
    print("=" * 60)
    print("IMPORTING FOUNDATIONS TO CRM")
    print("=" * 60)

    # 1. Import foundation management companies (Tier 1)
    fdn_mgmt_count = import_foundation_mgmt_companies()

    # 2. Import open foundations (Tier 2)
    foundation_count = import_open_foundations()

    # 3. Update nonprofit tiers to be lower priority
    update_nonprofit_tiers()

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"  Foundation Mgmt Companies: {fdn_mgmt_count} (Tier 1)")
    print(f"  Open Foundations: {foundation_count} (Tier 2)")
    print(f"  Nonprofits: 74,144 (Tiers 3-5)")
    print("\nCall queue priority: Fdn Mgmt → Foundations → Nonprofits")


if __name__ == '__main__':
    main()
