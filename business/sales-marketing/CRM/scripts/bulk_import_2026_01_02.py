#!/usr/bin/env python3
"""
Bulk import prospects to CRM - 2026-01-02

Imports:
1. All foundation management companies (53)
2. All grant_alerts emailed prospects
3. Top 1000 foundations by capacity building score
4. Top 1000 nonprofits by ICP score

Usage:
    python3 bulk_import_2026_01_02.py
"""

import csv
import json
import urllib.request
import urllib.error
import psycopg2
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

SUPABASE_URL = "https://qisbqmwtfzeiffgtlzpk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo"

LOCAL_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': 'SHiNYL!ght105'
}

# File paths
FDN_MGMT_CSV = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Archive/Prospect_Lists/DATA_2025-12-17_non_bank_foundation_mgmt_companies.csv"
SENT_TRACKER_CSV = "/Users/aleckleinman/Documents/TheGrantScout/4. Sales & Marketing/Email_Campaign/sent_tracker.csv"

# Foundation Management Company enrichment data (researched)
FDN_MGMT_ENRICHMENT = {
    "Foundation Source": {
        "phone": "(800) 839-0054",
        "contact_name": "Jeffrey D. Haskell",
        "contact_title": "Chief Legal Officer",
        "managed_foundations": "2,288 foundations, $59B combined assets",
        "pitch_angle": "Largest dedicated manager. Clients ask 'where should we give?' constantly - we answer that with 8.3M grants data."
    },
    "Sterling Foundation Management": {
        "phone": "(703) 865-6000",
        "contact_name": "John Carter",
        "contact_title": "President",
        "managed_foundations": "Charitable remainder trusts, private foundations",
        "pitch_angle": "Oldest national firm (since 1998). CRT specialists - help their charitable trust clients identify aligned nonprofits."
    },
    "Rockefeller Philanthropy Advisors": {
        "phone": "(212) 812-4330",
        "contact_name": "Lisa Philp",
        "contact_title": "President & CEO",
        "managed_foundations": "100+ fiscal sponsor projects, $500M annual giving",
        "pitch_angle": "Premier philanthropic advisory - data-driven approach aligns with their brand. $4B+ granted historically."
    },
    "The Philanthropic Initiative (TPI)": {
        "phone": "(617) 338-2590",
        "contact_name": "Leslie Pine",
        "contact_title": "Managing Partner",
        "managed_foundations": "Clients include families and foundations",
        "pitch_angle": "Pioneered strategic philanthropy. Now part of Boston Foundation. Help their clients increase impact."
    },
    "Third Plateau": {
        "phone": "(415) 321-3000",
        "contact_name": "Alyse Eberle",
        "contact_title": "Partner",
        "managed_foundations": "Family foundations, political philanthropy",
        "pitch_angle": "Merged with Hirsch (first US philanthropy firm). Program design + grantmaking expertise."
    },
    "Bridgespan Group": {
        "phone": "(617) 572-2833",
        "contact_name": "Thomas Tierney",
        "contact_title": "Co-Founder & Chairman",
        "managed_foundations": "Advises Gates, Ford, Bloomberg, Rockefeller",
        "pitch_angle": "Elite consulting - TheGrantScout data could power their research. Spun from Bain."
    },
    "Bessemer Trust": {
        "phone": "(212) 708-9100",
        "contact_name": "Caroline Woodruff Hodkinson",
        "contact_title": "Head of Philanthropic Advisory",
        "managed_foundations": "500+ foundations, $200B+ AUM, $220M granted annually",
        "pitch_angle": "UHNW families with $10M+ minimum. Data-driven approach for sophisticated donors."
    },
    "Whittier Trust": {
        "phone": "(626) 441-5111",
        "contact_name": "David Dahl",
        "contact_title": "CEO",
        "managed_foundations": "140+ foundations, DAFs, endowments. $20B+ AUM",
        "pitch_angle": "Oldest/largest multi-family office in the West. 140 foundations under management."
    },
    "Glenmede Trust": {
        "phone": "(215) 419-6000",
        "contact_name": "Andrew K. Slade, CAP",
        "contact_title": "VP, E&F Advisory Team Lead",
        "managed_foundations": "Family philanthropy, private foundations. $42B AUM",
        "pitch_angle": "Founded 1956 for Pew Trusts. Andrew leads E&F Advisory - perfect for partnership."
    },
    "Fiduciary Trust Company": {
        "phone": "(617) 292-6799",
        "contact_name": "Michael Perrin",
        "contact_title": "CEO",
        "managed_foundations": "Foundation advisory, DAFs. $34B AUM",
        "pitch_angle": "Being acquired by GTCR (leadership transition). DAF deployment challenge - we accelerate decisions."
    },
    "Arden Trust Company": {
        "phone": "(302) 594-3130",
        "contact_name": "Doug Sherry",
        "contact_title": "Philanthropic Services",
        "managed_foundations": "60+ foundations, $5.4B AUA",
        "pitch_angle": "Part of Kestra Financial. Help advisors become philanthropic advisors."
    },
    "BlueStone Services": {
        "phone": "(410) 561-3100",
        "contact_name": "Trey Gailey, CPA",
        "contact_title": "Managing Partner",
        "managed_foundations": "Private foundation accounting and administration",
        "pitch_angle": "Small boutique firm. Foundation clients need grant strategy, not just compliance."
    },
    "Armanino": {
        "phone": "(925) 790-2600",
        "contact_name": "Matt Armanino",
        "contact_title": "CEO",
        "managed_foundations": "600+ nonprofit clients, benchmarking platform",
        "pitch_angle": "Their benchmarking platform (300K+ nonprofits) + TheGrantScout (8.3M grants) = comprehensive intelligence."
    },
    "GHJ Advisors": {
        "phone": "(310) 873-1600",
        "contact_name": "Anant Patel",
        "contact_title": "Advisory Practice Leader",
        "managed_foundations": "Serves 10 of SoCal's top 25 foundations",
        "pitch_angle": "Strategic Grantmaking Service would be competitive moat for their advisory practice."
    },
    "Plante Moran": {
        "phone": "(248) 223-3000",
        "contact_name": "Kellie Ray",
        "contact_title": "Not-for-Profit Practice Leader",
        "managed_foundations": "100s of nonprofit clients",
        "pitch_angle": "34% report declining federal funding - they need foundation diversification fast."
    },
    "National Philanthropic Trust": {
        "phone": "(888) 878-7900",
        "contact_name": "Eileen Heisman",
        "contact_title": "President & CEO",
        "managed_foundations": "Largest independent DAF sponsor. $5.87B granted in 2024",
        "pitch_angle": "Help DAF donors make faster, smarter grant decisions. 146,449 grants in 2024."
    },
    "Tides Foundation": {
        "phone": "(415) 561-6400",
        "contact_name": "Janiece Evans-Page",
        "contact_title": "CEO",
        "managed_foundations": "80+ fiscal sponsor projects, $1B+ assets",
        "pitch_angle": "Model C fiscal sponsorship. Help donors and projects identify aligned charities."
    },
    "New Venture Fund": {
        "phone": "(202) 596-3470",
        "contact_name": "Lee Bodner",
        "contact_title": "President",
        "managed_foundations": "243+ projects, $1B+ annual revenue (network)",
        "pitch_angle": "Premier fiscal sponsor - acquired Sunflower Services. Help projects find grantees."
    },
    "CCS Fundraising": {
        "phone": "(212) 695-1175",
        "contact_name": "Jon Kane",
        "contact_title": "President & CEO",
        "managed_foundations": "Since 1947, 25K+ campaigns. $26B annual campaign goals",
        "pitch_angle": "Different angle: help their nonprofit clients find aligned foundations."
    },
    "Convergent Nonprofit Solutions": {
        "phone": "(888) 986-6672",
        "contact_name": "Michael Tobin",
        "contact_title": "CEO",
        "managed_foundations": "Capital campaigns, nonprofit consulting",
        "pitch_angle": "Merger of five national firms (2009). Help their nonprofit clients identify foundation prospects."
    },
    "Silicon Valley Community Foundation": {
        "phone": "(650) 450-5400",
        "contact_name": "Nicole Taylor",
        "contact_title": "CEO",
        "managed_foundations": "$15B+ assets, major tech philanthropy hub",
        "pitch_angle": "Donors ask 'where should we give?' constantly. Data-driven grantmaking for Silicon Valley tech donors."
    },
    "California Community Foundation": {
        "phone": "(213) 413-4130",
        "contact_name": "Miguel A. Santana",
        "contact_title": "President & CEO",
        "managed_foundations": "$2.3B AUM, 1,900 funds",
        "pitch_angle": "Equity layer that helps smaller nonprofits get discovered, not just well-connected ones."
    },
    "The Cleveland Foundation": {
        "phone": "(216) 861-3810",
        "contact_name": "Lillian Kuri",
        "contact_title": "President & CEO",
        "managed_foundations": "$3B AUM, world's first community foundation",
        "pitch_angle": "Help their grantees diversify funding sources beyond Cleveland Foundation."
    },
    "Marin Community Foundation": {
        "phone": "(415) 464-2500",
        "contact_name": "Rhea Suh",
        "contact_title": "President & CEO",
        "managed_foundations": "850+ funds with different donor priorities",
        "pitch_angle": "AI matching helps donors make most impactful grants based on 8.3M real grants."
    },
    "The Chicago Community Trust": {
        "phone": "(312) 616-8000",
        "contact_name": "Andrea Sáenz",
        "contact_title": "President & CEO",
        "managed_foundations": "$4.5B AUM, $1.6B granted in 2023",
        "pitch_angle": "Alt contact: Sheila Cawley (Chief Philanthropy Officer). Help donors find highest-impact nonprofits."
    },
    "Schwab Charitable": {
        "phone": "(800) 746-6216",
        "contact_name": "Julia Reed",
        "contact_title": "Managing Director, Relationship Management",
        "managed_foundations": "Nation's 2nd largest DAF. 4,700+ advisors use DAFgiving360",
        "pitch_angle": "Donors need help answering 'where should I give?' - we solve that with 8.3M grants data."
    },
    "Fidelity Charitable": {
        "phone": "(800) 262-6039",
        "contact_name": "Tony Harris",
        "contact_title": "President",
        "managed_foundations": "Nation's top grantmaker - $14.9B distributed in 2024. 350K+ donors",
        "pitch_angle": "Their Philanthropic Strategists could use TheGrantScout to accelerate donor recommendations."
    },
    "Vanguard Charitable": {
        "phone": "(888) 383-4483",
        "contact_name": "Bryan Kelley",
        "contact_title": "Head of Client Services & Operations",
        "managed_foundations": "50K+ donors, $2.6B granted in 2023",
        "pitch_angle": "Premier Services for $1M+ accounts - data-driven giving recommendations would differentiate."
    }
}

# ============================================
# SUPABASE HELPERS
# ============================================

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

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error {e.code}: {error_body}")
        return None

def get_existing_eins():
    """Get set of EINs already in CRM"""
    prospects = supabase_request("prospects?select=ein")
    if prospects:
        return set(p['ein'] for p in prospects if p.get('ein'))
    return set()

def get_existing_emails():
    """Get set of email addresses already in CRM"""
    prospects = supabase_request("prospects?select=email")
    if prospects:
        return set(p['email'].lower() for p in prospects if p.get('email'))
    return set()

def get_existing_org_names():
    """Get set of org names already in CRM (for foundation mgmt)"""
    prospects = supabase_request("prospects?segment=eq.foundation_mgmt&select=org_name")
    if prospects:
        return set(p['org_name'].lower() for p in prospects if p.get('org_name'))
    return set()

def create_source_list(name, segment, criteria, count):
    """Create a source list entry"""
    result = supabase_request("source_lists", method='POST', data={
        'name': name,
        'segment': segment,
        'criteria': criteria,
        'record_count': count
    })
    if result:
        return result[0]['id']
    return None

def batch_insert_prospects(prospects, batch_size=100):
    """Insert prospects in batches"""
    inserted = 0
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i + batch_size]
        result = supabase_request("prospects", method='POST', data=batch)
        if result:
            inserted += len(result)
            print(f"  Inserted {inserted}/{len(prospects)}...")
        else:
            print(f"  Error inserting batch starting at {i}")
    return inserted

# ============================================
# IMPORT FUNCTIONS
# ============================================

def import_foundation_mgmt():
    """Import all foundation management companies with enrichment data"""
    print("\n" + "="*60)
    print("IMPORTING FOUNDATION MANAGEMENT COMPANIES")
    print("="*60)

    existing_names = get_existing_org_names()
    print(f"Found {len(existing_names)} existing foundation mgmt companies")

    prospects = []
    with open(FDN_MGMT_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('company_name', '').strip()
            if not name or name.lower() in existing_names:
                continue

            # Skip membership associations and directories (not sales targets)
            company_type = row.get('type', '').lower()
            if any(x in company_type for x in ['membership', 'directory', 'association', 'network']):
                continue

            prospect = {
                'org_name': name,
                'website': row.get('website', '').strip() or None,
                'city': row.get('hq_city', '').strip() or None,
                'state': row.get('hq_state', '').strip() or None,
                'segment': 'foundation_mgmt',
                'tier': 1,
                'icp_score': 100,
                'status': 'not_contacted',
            }

            # Try to get enrichment data
            enrichment = None
            for key in FDN_MGMT_ENRICHMENT:
                if key.lower() in name.lower() or name.lower() in key.lower():
                    enrichment = FDN_MGMT_ENRICHMENT[key]
                    break

            if enrichment:
                prospect['phone'] = enrichment.get('phone')
                prospect['contact_name'] = enrichment.get('contact_name')
                prospect['contact_title'] = enrichment.get('contact_title')
                prospect['pitch_angle'] = enrichment.get('pitch_angle')
                notes = f"Managed: {enrichment.get('managed_foundations', 'Unknown')}. Type: {row.get('type', '')}. {row.get('notes', '')}"
                prospect['notes'] = notes[:500]
            else:
                # Use CSV data if no enrichment
                if row.get('key_contact_name'):
                    prospect['contact_name'] = row.get('key_contact_name')
                if row.get('key_contact_title'):
                    prospect['contact_title'] = row.get('key_contact_title')
                if row.get('key_contact_linkedin'):
                    prospect['linkedin_url'] = row.get('key_contact_linkedin')
                prospect['notes'] = f"Type: {row.get('type', '')}. Services: {row.get('services', '')}. {row.get('notes', '')}"[:500]

            prospects.append(prospect)

    print(f"Found {len(prospects)} new foundation mgmt companies to import")

    if prospects:
        source_id = create_source_list(
            "Foundation Mgmt Companies - Jan 2026",
            "foundation_mgmt",
            "Non-bank foundation management companies from research",
            len(prospects)
        )
        for p in prospects:
            p['source_list_id'] = source_id

        inserted = batch_insert_prospects(prospects)
        print(f"Imported {inserted} foundation mgmt companies")
        return inserted
    return 0

def import_emailed_prospects():
    """Import prospects that were emailed (grant_alerts vertical)

    Matches emails to local PostgreSQL prospects by website domain.
    """
    print("\n" + "="*60)
    print("IMPORTING EMAILED PROSPECTS (grant_alerts)")
    print("="*60)

    # Get existing emails in CRM
    existing_emails = get_existing_emails()
    print(f"Found {len(existing_emails)} existing email addresses in CRM")

    # Read sent_tracker.csv for grant_alerts
    emailed = {}  # domain -> (email, sent_date)
    with open(SENT_TRACKER_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('vertical') == 'grant_alerts' and row.get('status') == 'SUCCESS':
                email = row.get('email', '').lower().strip()
                if email and '@' in email and email not in existing_emails:
                    domain = email.split('@')[1].lower()
                    if domain not in emailed:
                        emailed[domain] = (email, row.get('timestamp'))

    print(f"Found {len(emailed)} unique domains from grant_alerts emails")

    if not emailed:
        return 0

    # Match by website domain in local PostgreSQL
    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    # Get prospects with matching websites
    domain_list = list(emailed.keys())

    cur.execute("""
        SELECT ein, org_name, contact_name, contact_title, contact_phone,
               website, city, state, ntee_code, total_revenue, icp_score, priority_tier,
               personalization_hook
        FROM f990_2025.prospects
        WHERE contact_phone IS NOT NULL
        ORDER BY icp_score DESC NULLS LAST
    """)

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Match by domain
    prospects = []
    matched_domains = set()

    for row in rows:
        data = dict(zip(columns, row))
        website = (data.get('website') or '').lower()

        # Extract domain from website
        for domain in emailed.keys():
            if domain in website and domain not in matched_domains:
                email, sent_date = emailed[domain]
                matched_domains.add(domain)

                prospect = {
                    'org_name': data.get('org_name'),
                    'ein': data.get('ein'),
                    'phone': data.get('contact_phone'),
                    'email': email,
                    'website': data.get('website'),
                    'contact_name': data.get('contact_name'),
                    'contact_title': data.get('contact_title'),
                    'city': data.get('city'),
                    'state': data.get('state'),
                    'ntee_code': data.get('ntee_code'),
                    'annual_budget': int(data['total_revenue']) if data.get('total_revenue') else None,
                    'icp_score': data.get('icp_score') or 50,
                    'tier': data.get('priority_tier') or 4,
                    'segment': 'nonprofit',
                    'status': 'contacted',
                    'notes': f"Emailed grant_alerts {sent_date[:10] if sent_date else ''}. {data.get('personalization_hook') or ''}"[:500]
                }
                prospects.append(prospect)
                break

    print(f"Matched {len(prospects)} prospects by website domain")

    # For unmatched, create minimal records
    unmatched = 0
    for domain, (email, sent_date) in emailed.items():
        if domain not in matched_domains:
            org_name = domain.replace('.org', '').replace('.com', '').replace('.net', '').replace('-', ' ').title()
            prospect = {
                'org_name': f"{org_name} (from email)",
                'email': email,
                'website': f"https://{domain}",
                'segment': 'nonprofit',
                'status': 'contacted',
                'tier': 5,
                'icp_score': 30,
                'notes': f"Emailed grant_alerts {sent_date[:10] if sent_date else ''}. Needs enrichment."
            }
            prospects.append(prospect)
            unmatched += 1

    print(f"Created {unmatched} minimal records for unmatched emails")

    if prospects:
        source_id = create_source_list(
            "Grant Alerts Email Campaign - Jan 2026",
            "nonprofit",
            f"Nonprofits emailed grant_alerts. {len(prospects)-unmatched} matched, {unmatched} unmatched.",
            len(prospects)
        )
        for p in prospects:
            p['source_list_id'] = source_id

        inserted = batch_insert_prospects(prospects)
        print(f"Imported {inserted} emailed prospects")
        return inserted
    return 0

def import_top_foundations(limit=1000):
    """Import top foundations by capacity building score"""
    print("\n" + "="*60)
    print(f"IMPORTING TOP {limit} FOUNDATIONS")
    print("="*60)

    existing_eins = get_existing_eins()
    print(f"Found {len(existing_eins)} existing EINs in CRM")

    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    # Get foundations with capacity building scores
    cur.execute("""
        WITH capacity_scores AS (
            SELECT
                foundation_ein,
                COUNT(*) as total_grants,
                COUNT(CASE WHEN purpose_text ILIKE '%%capacity%%'
                           OR purpose_text ILIKE '%%general support%%'
                           OR purpose_text ILIKE '%%operating support%%'
                           OR purpose_text ILIKE '%%unrestricted%%' THEN 1 END) as capacity_grants
            FROM f990_2025.fact_grants
            GROUP BY foundation_ein
        ),
        latest_returns AS (
            SELECT ein, MAX(tax_year) as max_year
            FROM f990_2025.pf_returns
            WHERE grants_to_organizations_ind = true
              AND (only_contri_to_preselected_ind = false OR only_contri_to_preselected_ind IS NULL)
            GROUP BY ein
        )
        SELECT
            pr.ein,
            pr.business_name,
            pr.phone_num,
            pr.app_contact_name,
            pr.app_contact_email,
            pr.app_contact_phone,
            pr.city,
            pr.state,
            pr.total_assets_eoy_amt,
            COALESCE(cs.capacity_grants, 0) as capacity_grants,
            COALESCE(cs.total_grants, 0) as total_grants
        FROM f990_2025.pf_returns pr
        JOIN latest_returns lr ON pr.ein = lr.ein AND pr.tax_year = lr.max_year
        LEFT JOIN capacity_scores cs ON pr.ein = cs.foundation_ein
        WHERE pr.grants_to_organizations_ind = true
          AND (pr.only_contri_to_preselected_ind = false OR pr.only_contri_to_preselected_ind IS NULL)
          AND (pr.phone_num IS NOT NULL OR pr.app_contact_phone IS NOT NULL)
        ORDER BY COALESCE(cs.capacity_grants, 0) DESC, COALESCE(cs.total_grants, 0) DESC
        LIMIT %s
    """, (limit * 2,))  # Get extra to account for existing

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    prospects = []
    for row in rows:
        if len(prospects) >= limit:
            break

        data = dict(zip(columns, row))
        ein = data.get('ein')

        if ein in existing_eins:
            continue

        # Calculate tier based on capacity grants
        capacity = data.get('capacity_grants', 0)
        if capacity >= 10:
            tier = 2
            icp_score = 90
        elif capacity >= 1:
            tier = 3
            icp_score = 70
        else:
            tier = 4
            icp_score = 40

        phone = data.get('app_contact_phone') or data.get('phone_num')

        prospect = {
            'org_name': data.get('business_name'),
            'ein': ein,
            'phone': phone,
            'email': data.get('app_contact_email'),
            'contact_name': data.get('app_contact_name'),
            'city': data.get('mailing_addr_city'),
            'state': data.get('mailing_addr_state'),
            'annual_budget': int(data['total_assets_eoy_amt']) if data.get('total_assets_eoy_amt') else None,
            'icp_score': icp_score,
            'tier': tier,
            'segment': 'foundation',
            'status': 'not_contacted',
            'notes': f"Capacity grants: {capacity}. Total grants: {data.get('total_grants', 0)}"
        }
        prospects.append(prospect)

    print(f"Found {len(prospects)} new foundations to import")

    if prospects:
        source_id = create_source_list(
            f"Top {len(prospects)} Open Foundations - Jan 2026",
            "foundation",
            "Foundations accepting applications, sorted by capacity building grant history",
            len(prospects)
        )
        for p in prospects:
            p['source_list_id'] = source_id

        inserted = batch_insert_prospects(prospects)
        print(f"Imported {inserted} foundations")
        return inserted
    return 0

def import_top_nonprofits(limit=1000):
    """Import top nonprofits by ICP score"""
    print("\n" + "="*60)
    print(f"IMPORTING TOP {limit} NONPROFITS")
    print("="*60)

    existing_eins = get_existing_eins()
    existing_emails = get_existing_emails()
    print(f"Found {len(existing_eins)} existing EINs, {len(existing_emails)} existing emails")

    conn = psycopg2.connect(**LOCAL_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ein, org_name, contact_name, contact_title, contact_phone, contact_email,
            website, city, state, ntee_code, total_revenue, icp_score, priority_tier,
            mission_statement, personalization_hook
        FROM f990_2025.prospects
        WHERE icp_score IS NOT NULL
          AND contact_phone IS NOT NULL
        ORDER BY icp_score DESC
        LIMIT %s
    """, (limit * 2,))  # Extra for filtering

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    prospects = []
    for row in rows:
        if len(prospects) >= limit:
            break

        data = dict(zip(columns, row))
        ein = data.get('ein')
        email = (data.get('contact_email') or '').lower()

        # Skip if already exists
        if ein in existing_eins:
            continue
        if email and email in existing_emails:
            continue

        prospect = {
            'org_name': data.get('org_name'),
            'ein': ein,
            'phone': data.get('contact_phone'),
            'email': data.get('contact_email'),
            'website': data.get('website'),
            'contact_name': data.get('contact_name'),
            'contact_title': data.get('contact_title'),
            'city': data.get('city'),
            'state': data.get('state'),
            'ntee_code': data.get('ntee_code'),
            'annual_budget': int(data['total_revenue']) if data.get('total_revenue') else None,
            'icp_score': data.get('icp_score') or 50,
            'tier': data.get('priority_tier') or 4,
            'segment': 'nonprofit',
            'status': 'not_contacted',
            'notes': data.get('personalization_hook', '')[:500] if data.get('personalization_hook') else None
        }
        prospects.append(prospect)

    print(f"Found {len(prospects)} new nonprofits to import")

    if prospects:
        source_id = create_source_list(
            f"Top {len(prospects)} Nonprofits by ICP - Jan 2026",
            "nonprofit",
            "Top nonprofits by ICP score (underfunded, grant-dependent)",
            len(prospects)
        )
        for p in prospects:
            p['source_list_id'] = source_id

        inserted = batch_insert_prospects(prospects)
        print(f"Imported {inserted} nonprofits")
        return inserted
    return 0

# ============================================
# MAIN
# ============================================

def main():
    print("="*60)
    print("CRM BULK IMPORT - 2026-01-02")
    print("="*60)
    print(f"Started at: {datetime.now().isoformat()}")

    results = {}

    # 1. Foundation Management Companies
    results['foundation_mgmt'] = import_foundation_mgmt()

    # 2. Emailed Prospects
    results['emailed'] = import_emailed_prospects()

    # 3. Top Foundations
    results['foundations'] = import_top_foundations(1000)

    # 4. Top Nonprofits
    results['nonprofits'] = import_top_nonprofits(1000)

    # Summary
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    for key, count in results.items():
        print(f"  {key}: {count} imported")
    print(f"\nTotal: {sum(results.values())} prospects imported")
    print(f"Finished at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
