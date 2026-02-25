#!/usr/bin/env python3
"""
Pre-Filter Script for VetsBoats Deep Crawl Batch 3

Implements audit recommendations from REPORT_2026-02-20.9:
- Rec #1: Parse app_restrictions for PF exclusion keywords
- Rec #2: Parse app_restrictions for hard geographic restrictions outside CA/SF Bay
- Rec #3: Cross-reference "has funded PFs" claims against actual 990-PF filers
- Check against dim_clients.known_funders for VetsBoats
- Flag corporate foundations by name pattern

Inputs: 23 candidate EINs from 3 sources (multi-peer, niche sailing, high-affinity CA)
Outputs: PASS / SOFT_FAIL / HARD_FAIL classification for each foundation
"""

import json
import os
import sys

import psycopg2
import psycopg2.extras

# ─── Config ──────────────────────────────────────────────────────────────────

OUTPUT_DIR = '/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-20'

# DB connection — read creds from env or use defaults
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'thegrantscout',
    'user': 'postgres',
    'password': os.environ.get('PGPASSWORD', 'postgres'),
}

# VetsBoats client
VETSBOATS_EIN = '464194065'
VETSBOATS_CLIENT_ID = 8

# ─── Full Candidate Pool (23 foundations) ────────────────────────────────────

CANDIDATES = [
    # Tier A: Must-Crawl (8)
    {"ein": "366152744", "name": "Kovler Family Foundation", "source": "multi-peer", "tier": "A"},
    {"ein": "237376427", "name": "Helen V Brach Foundation", "source": "high-affinity-CA", "tier": "A"},
    {"ein": "330247161", "name": "Crail-Johnson Foundation", "source": "high-affinity-CA", "tier": "A"},
    {"ein": "946079493", "name": "William G Gilmore Foundation", "source": "high-affinity-CA", "tier": "A"},
    {"ein": "870757807", "name": "Kim & Harold Louie Family", "source": "high-affinity-CA", "tier": "A"},
    {"ein": "911722000", "name": "Lucky Seven Foundation", "source": "high-affinity-CA", "tier": "A"},
    {"ein": "367041179", "name": "Howard Family Foundation", "source": "multi-peer", "tier": "A"},
    {"ein": "650171539", "name": "Lennar Foundation", "source": "high-affinity-CA", "tier": "A"},
    # Tier B: Worth Crawling (7)
    {"ein": "236261726", "name": "Cigna Foundation", "source": "multi-peer", "tier": "B"},
    {"ein": "756038519", "name": "Texas Instruments Foundation", "source": "multi-peer", "tier": "B"},
    {"ein": "810465899", "name": "First Interstate BancSystem", "source": "multi-peer", "tier": "B"},
    {"ein": "364267581", "name": "The Kellcie Fund", "source": "multi-peer", "tier": "B"},
    {"ein": "474305984", "name": "Hutton Family Foundation", "source": "niche-sailing", "tier": "B"},
    {"ein": "911913330", "name": "Enersen Foundation", "source": "niche-sailing", "tier": "B"},
    {"ein": "371392755", "name": "Jerome Mirza Foundation", "source": "multi-peer", "tier": "B"},
    # Expected Eliminations (8) — included for validation
    {"ein": "320341358", "name": "Wood-Claeyssens Foundation", "source": "high-affinity-CA", "tier": "X"},
    {"ein": "330399736", "name": "McBeth Foundation", "source": "high-affinity-CA", "tier": "X"},
    {"ein": "936021333", "name": "Autzen Foundation", "source": "multi-peer", "tier": "X"},
    {"ein": "953924667", "name": "Honda USA Foundation", "source": "high-affinity-CA", "tier": "X"},
    {"ein": "931283076", "name": "Phileo Foundation", "source": "niche-sailing", "tier": "X"},
    {"ein": "770494059", "name": "Coastal Barrier Island Foundation", "source": "niche-sailing", "tier": "X"},
    {"ein": "946104634", "name": "McGuire & Hester Foundation", "source": "multi-peer", "tier": "X"},
    {"ein": "352671842", "name": "Hutton Family Foundation (9.7M)", "source": "niche-sailing", "tier": "X"},
]

# ─── PF Exclusion Keywords ───────────────────────────────────────────────────

PF_EXCLUSION_PATTERNS = [
    'public charit',          # "public charities only"
    '501(c)(3)/509(a)',       # explicit public charity code
    '509(a)',                 # public charity subsection
    'not private foundation', # explicit exclusion
    'no private foundation',
    'no grants to private',
    'grantmaking organization',  # sometimes used to exclude PFs
]

# ─── Geographic Restriction Keywords ─────────────────────────────────────────
# These indicate grants restricted to areas OUTSIDE CA/SF Bay Area

GEO_HARD_FAIL_PATTERNS = [
    ('southern california',),           # SoCal only
    ('oregon',),                        # Oregon only
    ('southwest washington',),          # SW WA only
    ('texas',),                         # TX only
    ('montana',),                       # MT only
]

# Sub-California county restrictions that exclude SF Bay Area
# These are HARD_FAIL even though they mention "California"
CA_SUB_REGION_FAIL = [
    ('santa barbara', 'ventura'),       # SB/Ventura counties only
    ('orange', 'riverside'),            # OC/Riverside only
    ('los angeles',),                   # LA only
    ('san diego',),                     # SD only (when "only" or "restricted to")
]

# CA / Bay Area terms that would indicate NOT a geographic exclusion
CA_SAFE_TERMS = [
    'california', 'san francisco', 'bay area', 'northern california',
    'norcal', 'alameda', 'marin', 'contra costa', 'san mateo',
]

# ─── Mission Mismatch Keywords ───────────────────────────────────────────────

MISSION_HARD_FAIL = [
    'youth programs focused on the environment, mobility, and traffic safety',  # Honda
    'youth or scientific education programs',  # Honda alt year
]

# ─── Corporate Foundation Name Patterns ──────────────────────────────────────

CORPORATE_PATTERNS = [
    'bank of america', 'wells fargo', 'jpmorgan', 'goldman sachs',
    'cigna', 'texas instruments', 'honda', 'lennar', 'enterprise holdings',
    'first interstate', 'liberty mutual', 'dick\'s sporting',
]


def connect_db():
    return psycopg2.connect(**DB_CONFIG)


def get_foundation_data(conn, eins):
    """Fetch latest 990-PF filing data for each candidate EIN."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    placeholders = ','.join(['%s'] * len(eins))
    cur.execute(f"""
        SELECT DISTINCT ON (ein)
            ein, business_name, state,
            only_contri_to_preselected_ind AS preselected,
            total_assets_eoy_amt AS assets,
            app_restrictions,
            app_form_requirements,
            website_url,
            app_contact_email,
            tax_year
        FROM f990_2025.pf_returns
        WHERE ein IN ({placeholders})
        ORDER BY ein, tax_year DESC
    """, eins)
    rows = cur.fetchall()
    return {row['ein']: dict(row) for row in rows}


def get_known_funders(conn, client_id):
    """Get VetsBoats known funders to exclude."""
    cur = conn.cursor()
    cur.execute("SELECT known_funders FROM f990_2025.dim_clients WHERE id = %s", (client_id,))
    row = cur.fetchone()
    return set(row[0]) if row and row[0] else set()


def get_pf_grant_recipients(conn, eins):
    """Get grant recipients for each foundation and check which are actual 990-PF filers."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    placeholders = ','.join(['%s'] * len(eins))

    # Get all grants with recipient EINs, then cross-reference against pf_returns
    cur.execute(f"""
        WITH foundation_grants AS (
            SELECT
                fg.foundation_ein,
                fg.recipient_ein,
                fg.recipient_name_raw AS recipient_name,
                fg.amount,
                fg.tax_year
            FROM f990_2025.fact_grants fg
            WHERE fg.foundation_ein IN ({placeholders})
            AND fg.recipient_ein IS NOT NULL
            AND fg.recipient_ein != ''
        ),
        pf_filers AS (
            SELECT DISTINCT ein
            FROM f990_2025.pf_returns
        )
        SELECT
            fg.foundation_ein,
            fg.recipient_ein,
            fg.recipient_name,
            fg.amount,
            fg.tax_year,
            CASE WHEN pf.ein IS NOT NULL THEN TRUE ELSE FALSE END AS recipient_is_pf
        FROM foundation_grants fg
        LEFT JOIN pf_filers pf ON fg.recipient_ein = pf.ein
        ORDER BY fg.foundation_ein, fg.tax_year DESC, fg.amount DESC
    """, eins)
    rows = cur.fetchall()

    # Group by foundation
    result = {}
    for row in rows:
        fein = row['foundation_ein']
        if fein not in result:
            result[fein] = {'all_grants': [], 'pf_recipients': [], 'non_pf_recipients': []}
        result[fein]['all_grants'].append(dict(row))
        if row['recipient_is_pf']:
            result[fein]['pf_recipients'].append(dict(row))
        else:
            result[fein]['non_pf_recipients'].append(dict(row))

    return result


def get_peer_org_grants(conn, eins):
    """Check which foundations have funded VetsBoats peer organizations."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    placeholders = ','.join(['%s'] * len(eins))

    # VetsBoats peer orgs (adaptive sailing / veteran sailing)
    # Use %% to escape ILIKE wildcards from psycopg2 parameter substitution
    cur.execute(f"""
        SELECT
            fg.foundation_ein,
            fg.recipient_name_raw AS recipient_name,
            fg.recipient_ein,
            fg.amount,
            fg.tax_year
        FROM f990_2025.fact_grants fg
        WHERE fg.foundation_ein IN ({placeholders})
        AND (
            fg.recipient_name_raw ILIKE ANY(ARRAY[
                '%%sail to prevail%%', '%%achieve tahoe%%', '%%judd goldman%%',
                '%%warrior sailing%%', '%%st francis sailing%%', '%%saint francis sailing%%',
                '%%baads%%', '%%bay area association of disabled sailors%%',
                '%%california inclusive sailing%%', '%%tisc%%',
                '%%shake-a-leg%%', '%%courageous sailing%%', '%%community boating%%',
                '%%adaptive sailing%%', '%%disabled sailing%%'
            ])
        )
        ORDER BY fg.foundation_ein, fg.tax_year DESC
    """, eins)
    rows = cur.fetchall()

    result = {}
    for row in rows:
        fein = row['foundation_ein']
        if fein not in result:
            result[fein] = []
        result[fein].append(dict(row))

    return result


def check_pf_exclusion(app_restrictions):
    """Check if app_restrictions contains PF exclusion language. Returns (bool, evidence)."""
    if not app_restrictions:
        return False, None
    text = app_restrictions.lower()
    for pattern in PF_EXCLUSION_PATTERNS:
        if pattern in text:
            return True, f"Found '{pattern}' in app_restrictions: {app_restrictions[:200]}"
    return False, None


def check_geo_restriction(app_restrictions, foundation_state):
    """Check for hard geographic restrictions outside CA/SF Bay Area.
    Returns (bool, restriction_description)."""
    if not app_restrictions:
        return False, None

    text = app_restrictions.lower()

    # Check sub-California county restrictions first (e.g. "Santa Barbara and Ventura Counties")
    # These are HARD_FAIL even though they're in California, because they exclude SF Bay
    for pattern_group in CA_SUB_REGION_FAIL:
        if all(p in text for p in pattern_group):
            return True, f"Geographic restriction (CA sub-region): {', '.join(pattern_group)} — {app_restrictions[:200]}"

    # Check each non-CA geo hard-fail pattern
    for pattern_group in GEO_HARD_FAIL_PATTERNS:
        if all(p in text for p in pattern_group):
            # Check if CA/Bay Area is ALSO mentioned (would make it not a hard fail)
            if any(safe in text for safe in CA_SAFE_TERMS):
                # "Southern California" is still restrictive for SF Bay
                if 'southern california' in text:
                    return True, f"Geographic restriction: Southern California only — {app_restrictions[:200]}"
                continue
            return True, f"Geographic restriction: {', '.join(pattern_group)} — {app_restrictions[:200]}"

    return False, None


def check_mission_mismatch(app_restrictions):
    """Check for hard mission mismatch keywords. Returns (bool, evidence)."""
    if not app_restrictions:
        return False, None
    text = app_restrictions.lower()
    for pattern in MISSION_HARD_FAIL:
        if pattern in text:
            return True, f"Mission mismatch: '{pattern}' — {app_restrictions[:200]}"
    return False, None


def is_corporate_foundation(name):
    """Flag corporate foundations by name pattern."""
    name_lower = name.lower()
    for pattern in CORPORATE_PATTERNS:
        if pattern in name_lower:
            return True, pattern
    return False, None


def run_prefilter():
    """Run all pre-filter checks and produce PASS/SOFT_FAIL/HARD_FAIL lists."""
    conn = connect_db()

    eins = [c['ein'] for c in CANDIDATES]

    print("=" * 70)
    print("  PRE-FILTER: VetsBoats Deep Crawl Batch 3")
    print("=" * 70)
    print(f"\nCandidates: {len(CANDIDATES)}")

    # Fetch data
    print("\n1. Fetching foundation filing data...")
    filing_data = get_foundation_data(conn, eins)
    print(f"   Found filings for {len(filing_data)}/{len(eins)} foundations")

    print("2. Fetching known funders...")
    known_funders = get_known_funders(conn, VETSBOATS_CLIENT_ID)
    print(f"   VetsBoats has {len(known_funders)} known funders")

    print("3. Cross-referencing PF grant recipients...")
    pf_grants = get_pf_grant_recipients(conn, eins)
    print(f"   Found grant data for {len(pf_grants)} foundations")

    print("4. Checking peer org grants...")
    peer_grants = get_peer_org_grants(conn, eins)
    print(f"   Found peer org grants for {len(peer_grants)} foundations")

    conn.close()

    # ─── Run Filters ─────────────────────────────────────────────────────────

    results = []

    for candidate in CANDIDATES:
        ein = candidate['ein']
        name = candidate['name']
        filing = filing_data.get(ein, {})
        app_restrictions = filing.get('app_restrictions', '')
        preselected = filing.get('preselected', None)
        state = filing.get('state', '')
        assets = filing.get('assets', 0)

        flags = []
        verdict = 'PASS'
        category = None

        # Check 1: Known funder
        if ein in known_funders:
            flags.append("KNOWN_FUNDER: Already in VetsBoats known funders list")
            verdict = 'HARD_FAIL'
            category = 'known_funder'

        # Check 2: PF exclusion in app_restrictions
        has_pf_excl, pf_evidence = check_pf_exclusion(app_restrictions)
        if has_pf_excl:
            flags.append(f"PF_EXCLUSION: {pf_evidence}")
            verdict = 'HARD_FAIL'
            category = category or 'pf_exclusion'

        # Check 3: Geographic restriction
        has_geo, geo_evidence = check_geo_restriction(app_restrictions, state)
        if has_geo:
            flags.append(f"GEO_RESTRICTION: {geo_evidence}")
            verdict = 'HARD_FAIL'
            category = category or 'geo_restriction'

        # Check 4: Mission mismatch
        has_mission, mission_evidence = check_mission_mismatch(app_restrictions)
        if has_mission:
            flags.append(f"MISSION_MISMATCH: {mission_evidence}")
            verdict = 'HARD_FAIL'
            category = category or 'mission_mismatch'

        # Check 5: Duplicate EIN check (Hutton 9.7M is a different EIN from Hutton 16M)
        if ein == '352671842':
            # Check if this is a duplicate of 474305984
            flags.append("DUPLICATE: Second Hutton Family Foundation EIN (9.7M) — primary is 474305984 (16.3M)")
            verdict = 'HARD_FAIL'
            category = category or 'duplicate'

        # Check 6: Preselected = TRUE (board-directed, no application)
        if preselected is True and verdict == 'PASS':
            peer = peer_grants.get(ein, [])
            pf_data = pf_grants.get(ein, {})
            pf_recipients = pf_data.get('pf_recipients', [])

            if peer:
                peer_names = list(set(g['recipient_name'] for g in peer))
                flags.append(f"PRESELECTED: preselected=TRUE but has peer org grants: {', '.join(peer_names[:3])}")
                verdict = 'SOFT_FAIL'
                category = 'preselected_with_peers'
            else:
                total_grants = len(pf_data.get('all_grants', []))
                flags.append(f"PRESELECTED: preselected=TRUE, no peer org grants, {total_grants} total grants")
                if total_grants <= 5 or (assets and float(assets) < 2000000):
                    verdict = 'HARD_FAIL'
                    category = category or 'preselected_tiny'
                else:
                    verdict = 'SOFT_FAIL'
                    category = 'preselected_no_peers'

        # Check 7: Corporate foundation flag (informational, not disqualifying)
        is_corp, corp_match = is_corporate_foundation(name)
        if is_corp:
            flags.append(f"CORPORATE: Matches corporate pattern '{corp_match}' — likely has formal CSR process")

        # Check 8: PF cross-reference validation
        pf_data = pf_grants.get(ein, {})
        confirmed_pf = pf_data.get('pf_recipients', [])
        if confirmed_pf:
            unique_pf_recipients = len(set(g['recipient_ein'] for g in confirmed_pf))
            total_pf_amount = sum(float(g['amount'] or 0) for g in confirmed_pf)
            flags.append(f"PF_CROSS_REF: {unique_pf_recipients} confirmed PF recipients, ${total_pf_amount:,.0f} total")
        else:
            flags.append("PF_CROSS_REF: No confirmed PF-to-PF grants found")

        # Compile result
        website = filing.get('website_url', '')
        if website and website.upper() in ('N/A', 'NONE', '0', 'NA', ''):
            website = None
        email = filing.get('app_contact_email', '')
        if email and email.upper() in ('N/A', 'NONE', '0', 'NA', ''):
            email = None

        results.append({
            'ein': ein,
            'name': name,
            'source': candidate['source'],
            'tier': candidate['tier'],
            'verdict': verdict,
            'category': category,
            'flags': flags,
            'preselected': preselected,
            'state': state,
            'assets': str(assets) if assets else None,
            'website_url': website,
            'app_contact_email': email,
            'app_restrictions': app_restrictions[:300] if app_restrictions else None,
            'confirmed_pf_recipients': len(set(g['recipient_ein'] for g in pf_data.get('pf_recipients', []))) if pf_data else 0,
            'peer_org_grants': len(peer_grants.get(ein, [])),
        })

    # ─── Output Results ──────────────────────────────────────────────────────

    pass_list = [r for r in results if r['verdict'] == 'PASS']
    soft_fail = [r for r in results if r['verdict'] == 'SOFT_FAIL']
    hard_fail = [r for r in results if r['verdict'] == 'HARD_FAIL']

    print("\n" + "=" * 70)
    print("  PRE-FILTER RESULTS")
    print("=" * 70)

    print(f"\n  PASS:      {len(pass_list)} foundations (crawl these)")
    print(f"  SOFT_FAIL: {len(soft_fail)} foundations (relationship-only targets)")
    print(f"  HARD_FAIL: {len(hard_fail)} foundations (eliminated)")

    print(f"\n{'─' * 70}")
    print(f"  PASS — Crawl These ({len(pass_list)})")
    print(f"{'─' * 70}")
    for r in pass_list:
        pf_str = f", {r['confirmed_pf_recipients']} PF recipients" if r['confirmed_pf_recipients'] else ""
        peer_str = f", {r['peer_org_grants']} peer grants" if r['peer_org_grants'] else ""
        url_str = f" | URL: {r['website_url']}" if r['website_url'] else " | NO URL"
        print(f"  [{r['tier']}] {r['name']:<35} {r['ein']} | {r['state']}{pf_str}{peer_str}{url_str}")
        for flag in r['flags']:
            if not flag.startswith('PF_CROSS_REF: No'):
                print(f"      {flag}")

    print(f"\n{'─' * 70}")
    print(f"  SOFT_FAIL — Relationship Only ({len(soft_fail)})")
    print(f"{'─' * 70}")
    for r in soft_fail:
        print(f"  [{r['tier']}] {r['name']:<35} {r['ein']} | {r['state']} | {r['category']}")
        for flag in r['flags']:
            if not flag.startswith('PF_CROSS_REF: No'):
                print(f"      {flag}")

    print(f"\n{'─' * 70}")
    print(f"  HARD_FAIL — Eliminated ({len(hard_fail)})")
    print(f"{'─' * 70}")
    for r in hard_fail:
        print(f"  [{r['tier']}] {r['name']:<35} {r['ein']} | {r['category']}")
        for flag in r['flags']:
            if 'PF_CROSS_REF: No' not in flag:
                print(f"      {flag}")

    # Save to JSON
    output = {
        'metadata': {
            'script': 'pre_filter_batch3.py',
            'date': '2026-02-20',
            'client': 'VetsBoats',
            'client_ein': VETSBOATS_EIN,
            'total_candidates': len(CANDIDATES),
            'pass_count': len(pass_list),
            'soft_fail_count': len(soft_fail),
            'hard_fail_count': len(hard_fail),
        },
        'pass': pass_list,
        'soft_fail': soft_fail,
        'hard_fail': hard_fail,
    }

    output_path = f"{OUTPUT_DIR}/DATA_2026-02-20_prefilter_batch3.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    run_prefilter()
