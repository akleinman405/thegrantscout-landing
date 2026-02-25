#!/usr/bin/env python3
"""
VetsBoats Public Charity Funder Discovery
Identifies public charity grantmakers from schedule_i_grants who fund VetsBoats peers
or make thematically relevant grants (adaptive sailing, veteran recreation, etc.).

Outputs:
  - DATA_2026-02-21_vetsboats_pc_candidates_ranked.md  (ranked candidate list)
  - DATA_2026-02-21_vetsboats_pc_query_results.json     (structured data for reuse)
  - DATA_2026-02-21_vetsboats_daf_signals.md             (DAF platform activity)
  - REPORT_2026-02-21_P1_vetsboats_pc_discovery.md       (session report)
"""

import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from collections import defaultdict

# =====================================================
# CONSTANTS
# =====================================================
OUTPUT_DIR = '/Users/aleckleinman/Documents/TheGrantScout/Enhancements/2026-02-21'

# Peer organizations — confirmed in schedule_i_grants
PEER_EINS = {
    '680024920': 'Achieve Tahoe',
    '311732524': 'Disabled Sports Eastern Sierra',
    '311625735': 'Treasure Island Sailing Center',
    '050399703': 'Sail to Prevail',
    '943067409': 'BAADS',
    '363832321': 'Judd Goldman Adaptive Sailing',
    '331859385': 'Warrior Sailing',
}

# Name fallback patterns for ILIKE (when EIN not matched)
PEER_NAME_PATTERNS = [
    '%achieve tahoe%',
    '%disabled sports eastern%',
    '%treasure island sail%',
    '%bay area%disabled sail%',
    '%baads%',
    '%judd goldman%',
    '%sail to prevail%',
    '%warrior sail%',
]

# VetsBoats itself — must exclude from results
VETSBOATS_EINS = {'464194065'}
# TRAP: EIN 911061721 = "Center for Wooden Boats" (WA) — different org, do NOT conflate

# Known funders from dim_clients
DIM_CLIENTS_FUNDERS = {
    '943073894', '946073084', '956495222', '946077619', '133556721',
}

# Known funders from PF deep crawl work
PF_WORK_FUNDERS = {
    '680400024',  # Tahoe Maritime Museum Foundation
    '953059828',  # Henry Mayo Newhall Foundation
    '956054953',  # Sidney Stern Memorial Trust
    '841849498',  # Charis Fund
    '843805975',  # Bonnell Cove Foundation
}

# VetsBoats existing schedule_i funders
SCHEDULE_I_EXISTING = {
    '205205488',  # Silicon Valley Community Foundation ($30K, 2023)
    '810739440',  # American Online Giving Foundation ($126K, 2022)
}

# Union of all known funders
ALL_KNOWN_FUNDERS = DIM_CLIENTS_FUNDERS | PF_WORK_FUNDERS | SCHEDULE_I_EXISTING | VETSBOATS_EINS

# DAF platforms (verified EINs) — separate from main candidates
DAF_EINS = {
    '110303001': 'Fidelity Charitable',
    '311640316': 'Schwab Charitable',
    '237825575': 'National Philanthropic Trust',
    '232888152': 'Vanguard Charitable',
    '527082731': 'Morgan Stanley Gift Fund',
    '680480736': 'Network for Good',
    '272499903': 'Mightycause',
    '208630809': 'TisBest Philanthropy',
}

# PF leads already researched (from deep crawl batches)
PF_LEADS = [
    {'ein': '680400024', 'name': 'Tahoe Maritime Museum Foundation', 'fit': 'HIGH',
     'notes': 'Maritime education focus; Tahoe region. Already known funder.'},
    {'ein': '941567169', 'name': 'Koret Foundation', 'fit': 'MEDIUM',
     'notes': 'Bay Area focus, broad human services. $250M+ assets.'},
    {'ein': '946062657', 'name': 'Walter & Elise Haas Fund', 'fit': 'MEDIUM',
     'notes': 'Bay Area community focus. Strong arts/equity mission.'},
    {'ein': '943136000', 'name': 'S.H. Cowell Foundation', 'fit': 'MEDIUM',
     'notes': 'Northern CA community development. Smaller grants ($25-75K).'},
    {'ein': '237047543', 'name': 'Bob Woodruff Foundation', 'fit': 'HIGH',
     'notes': 'National veteran services. Known funder of vet adaptive programs.'},
    {'ein': '953178302', 'name': 'California Wellness Foundation', 'fit': 'LOW',
     'notes': 'Health focus, CA only. Vet programs tangential.'},
]


def fmt_money(val):
    """Format dollar amount for display."""
    if val is None or val == 0:
        return '$0'
    val = int(val)
    if val >= 1_000_000_000:
        return f'${val / 1_000_000_000:.1f}B'
    if val >= 1_000_000:
        return f'${val / 1_000_000:.1f}M'
    if val >= 1_000:
        return f'${val / 1_000:.0f}K'
    return f'${val:,}'


def fmt_number(val):
    """Format integer with commas."""
    if val is None:
        return '0'
    return f'{val:,}'


# =====================================================
# DATABASE CONNECTION
# =====================================================
print("Connecting to database...")
conn = psycopg2.connect(
    host='localhost', port=5432, database='thegrantscout',
    user='postgres'
)
conn.set_session(readonly=True)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# =====================================================
# STEP 1: PEER FUNDER DISCOVERY
# =====================================================
print("\nStep 1: Peer Funder Discovery...")

peer_ein_list = list(PEER_EINS.keys())

# Build ILIKE conditions for name fallback
ilike_clauses = " OR ".join(f"recipient_name ILIKE %s" for _ in PEER_NAME_PATTERNS)

query_peer = f"""
    SELECT filer_ein, recipient_ein, recipient_name, amount, purpose, tax_year
    FROM f990_2025.schedule_i_grants
    WHERE (
        recipient_ein = ANY(%s)
        OR {ilike_clauses}
    )
    ORDER BY filer_ein, tax_year DESC, amount DESC
"""

params = [peer_ein_list] + PEER_NAME_PATTERNS
cur.execute(query_peer, params)
peer_grants = cur.fetchall()
print(f"  Found {len(peer_grants)} grants to peer organizations")

# Group by filer_ein
peer_funder_data = defaultdict(lambda: {'grants': [], 'peers_funded': set(), 'peer_grant_details': []})
for g in peer_grants:
    filer = g['filer_ein']
    # Determine which peer was funded
    peer_name = None
    if g['recipient_ein'] in PEER_EINS:
        peer_name = PEER_EINS[g['recipient_ein']]
    else:
        rname = (g['recipient_name'] or '').lower()
        for pattern in PEER_NAME_PATTERNS:
            clean = pattern.replace('%', '').lower()
            if clean in rname:
                peer_name = g['recipient_name']
                break
        if not peer_name:
            peer_name = g['recipient_name'] or 'Unknown'

    peer_funder_data[filer]['grants'].append(dict(g))
    peer_funder_data[filer]['peers_funded'].add(peer_name)
    peer_funder_data[filer]['peer_grant_details'].append({
        'peer': peer_name,
        'amount': float(g['amount']) if g['amount'] else 0,
        'purpose': g['purpose'],
        'year': g['tax_year'],
    })

print(f"  {len(peer_funder_data)} distinct filers fund peer orgs")

# =====================================================
# STEP 2: KEYWORD DISCOVERY
# =====================================================
print("\nStep 2: Keyword Discovery...")

cur.execute("""
    SELECT filer_ein, recipient_ein, recipient_name, amount, purpose, tax_year
    FROM f990_2025.schedule_i_grants
    WHERE amount >= 5000
      AND tax_year >= 2022
      AND (
        LOWER(purpose) LIKE '%%adaptive sail%%'
        OR LOWER(purpose) LIKE '%%therapeutic sail%%'
        OR (LOWER(purpose) LIKE '%%veteran%%' AND (
            LOWER(purpose) LIKE '%%sail%%' OR LOWER(purpose) LIKE '%%boat%%'
            OR LOWER(purpose) LIKE '%%maritime%%' OR LOWER(purpose) LIKE '%%adaptive%%'
            OR LOWER(purpose) LIKE '%%recreation%%'))
        OR (LOWER(purpose) LIKE '%%disabled%%' AND (
            LOWER(purpose) LIKE '%%sail%%' OR LOWER(purpose) LIKE '%%adaptive sport%%'
            OR LOWER(purpose) LIKE '%%recreation%%'))
        OR LOWER(purpose) LIKE '%%therapeutic%%recreation%%'
      )
    ORDER BY filer_ein, amount DESC
""")
keyword_grants = cur.fetchall()
print(f"  Found {len(keyword_grants)} keyword-matching grants")

# Group by filer_ein
keyword_funder_data = defaultdict(lambda: {'grants': [], 'keyword_grant_details': []})
for g in keyword_grants:
    filer = g['filer_ein']
    keyword_funder_data[filer]['grants'].append(dict(g))
    keyword_funder_data[filer]['keyword_grant_details'].append({
        'recipient': g['recipient_name'],
        'amount': float(g['amount']) if g['amount'] else 0,
        'purpose': g['purpose'],
        'year': g['tax_year'],
    })

print(f"  {len(keyword_funder_data)} distinct filers via keyword")

# =====================================================
# COMBINE FILER EINS
# =====================================================
all_filer_eins = set(peer_funder_data.keys()) | set(keyword_funder_data.keys())
print(f"\nCombined pool: {len(all_filer_eins)} distinct filers")
print(f"  Peer-only: {len(set(peer_funder_data.keys()) - set(keyword_funder_data.keys()))}")
print(f"  Keyword-only: {len(set(keyword_funder_data.keys()) - set(peer_funder_data.keys()))}")
print(f"  Both: {len(set(peer_funder_data.keys()) & set(keyword_funder_data.keys()))}")

# =====================================================
# STEP 3: ENRICHMENT FROM NONPROFIT_RETURNS
# =====================================================
print("\nStep 3: Enrichment from nonprofit_returns...")

filer_list = list(all_filer_eins)
cur.execute("""
    SELECT DISTINCT ON (ein)
        ein, organization_name, state, city,
        total_revenue, total_assets_eoy, website, mission_description, tax_year
    FROM f990_2025.nonprofit_returns
    WHERE ein = ANY(%s)
    ORDER BY ein, tax_year DESC
""", (filer_list,))

enrichment = {}
for row in cur.fetchall():
    enrichment[row['ein']] = dict(row)

print(f"  Found enrichment for {len(enrichment)} of {len(all_filer_eins)} filers")

# =====================================================
# STEP 4: GRANTMAKING VOLUME + CA GEOGRAPHY
# =====================================================
print("\nStep 4: Grantmaking volume + CA geography...")

cur.execute("""
    SELECT filer_ein,
        COUNT(*) as total_grants,
        COUNT(DISTINCT recipient_ein) FILTER (WHERE recipient_ein IS NOT NULL) as distinct_recipients,
        COALESCE(SUM(amount), 0) as total_amount,
        MAX(tax_year) as latest_year,
        COUNT(CASE WHEN recipient_state = 'CA' THEN 1 END) as ca_grants,
        COALESCE(SUM(CASE WHEN recipient_state = 'CA' THEN amount ELSE 0 END), 0) as ca_total,
        COUNT(DISTINCT recipient_state) FILTER (WHERE recipient_state IS NOT NULL) as state_count
    FROM f990_2025.schedule_i_grants
    WHERE filer_ein = ANY(%s)
    GROUP BY filer_ein
""", (filer_list,))

volume = {}
for row in cur.fetchall():
    volume[row['filer_ein']] = dict(row)

print(f"  Got volume data for {len(volume)} filers")

# =====================================================
# STEP 5: FILTER, CLASSIFY, RANK
# =====================================================
print("\nStep 5: Filter, classify, rank...")

# Filter pipeline
candidates = []
excluded = []
daf_signals = []

for ein in all_filer_eins:
    # 1. Remove known funders
    if ein in ALL_KNOWN_FUNDERS:
        excluded.append({'ein': ein, 'reason': 'known_funder',
                         'name': enrichment.get(ein, {}).get('organization_name', 'Unknown')})
        continue

    # 2. Separate DAF platforms
    if ein in DAF_EINS:
        daf_signals.append({
            'ein': ein,
            'name': DAF_EINS[ein],
            'peer_grants': peer_funder_data.get(ein, {}).get('peer_grant_details', []),
            'keyword_grants': keyword_funder_data.get(ein, {}).get('keyword_grant_details', []),
            'volume': volume.get(ein, {}),
        })
        continue

    # 3. Geographic filter
    enr = enrichment.get(ein, {})
    vol = volume.get(ein, {})
    hq_state = enr.get('state', '')
    ca_grants = vol.get('ca_grants', 0)
    state_count = vol.get('state_count', 0)
    pacific_states = {'CA', 'OR', 'NV', 'WA', 'HI'}

    geo_pass = (
        hq_state in pacific_states
        or ca_grants > 0
        or state_count >= 10
    )

    if not geo_pass:
        excluded.append({'ein': ein, 'reason': 'geography',
                         'name': enr.get('organization_name', 'Unknown'),
                         'state': hq_state, 'ca_grants': ca_grants,
                         'state_count': state_count})
        continue

    # Passed all filters — classify
    in_peer = ein in peer_funder_data
    in_keyword = ein in keyword_funder_data
    peer_count = len(peer_funder_data.get(ein, {}).get('peers_funded', set()))

    if peer_count >= 2:
        category = 'MULTI_PEER_FUNDER'
    elif peer_count == 1 and in_keyword:
        category = 'PEER_PLUS_KEYWORD'
    elif peer_count == 1:
        category = 'SINGLE_PEER_FUNDER'
    elif in_keyword:
        # Check purpose text for strong thematic fit
        kw_details = keyword_funder_data.get(ein, {}).get('keyword_grant_details', [])
        strong_keywords = ['adaptive sail', 'therapeutic sail', 'veteran']
        has_strong = any(
            any(sk in (d.get('purpose', '') or '').lower() for sk in strong_keywords)
            for d in kw_details
        )
        category = 'STRONG_KEYWORD' if has_strong else 'KEYWORD_MATCH'
    else:
        category = 'UNKNOWN'

    # Ranking score
    latest_year = vol.get('latest_year', 0) or 0
    score = (
        (peer_count * 10)
        + (3 if in_keyword else 0)
        + (5 if ca_grants > 0 else 0)
        + (2 if latest_year == 2023 else 0)
    )

    candidates.append({
        'ein': ein,
        'name': enr.get('organization_name', 'Unknown'),
        'state': hq_state,
        'city': enr.get('city', ''),
        'website': enr.get('website', ''),
        'total_revenue': float(enr.get('total_revenue', 0) or 0),
        'total_assets': float(enr.get('total_assets_eoy', 0) or 0),
        'mission': enr.get('mission_description', ''),
        'enr_tax_year': enr.get('tax_year'),
        'total_grants': vol.get('total_grants', 0),
        'distinct_recipients': vol.get('distinct_recipients', 0),
        'total_amount': float(vol.get('total_amount', 0) or 0),
        'latest_year': latest_year,
        'ca_grants': ca_grants,
        'ca_total': float(vol.get('ca_total', 0) or 0),
        'state_count': state_count,
        'peer_count': peer_count,
        'peers_funded': list(peer_funder_data.get(ein, {}).get('peers_funded', set())),
        'peer_grant_details': peer_funder_data.get(ein, {}).get('peer_grant_details', []),
        'keyword_grant_details': keyword_funder_data.get(ein, {}).get('keyword_grant_details', []),
        'has_keyword': in_keyword,
        'category': category,
        'score': score,
        'source': 'SCHEDULE_I',
        'status': 'NEW',
    })

# Sort by score descending, then by peer count, then CA grants
candidates.sort(key=lambda c: (-c['score'], -c['peer_count'], -c['ca_grants'], -c['total_amount']))

# Category order for output sections
cat_order = {
    'MULTI_PEER_FUNDER': 0,
    'PEER_PLUS_KEYWORD': 1,
    'SINGLE_PEER_FUNDER': 2,
    'STRONG_KEYWORD': 3,
    'KEYWORD_MATCH': 4,
}

print(f"\n=== FUNNEL SUMMARY ===")
print(f"  Total filers discovered: {len(all_filer_eins)}")
print(f"  Excluded (known funders): {len([e for e in excluded if e['reason'] == 'known_funder'])}")
print(f"  Excluded (geography):     {len([e for e in excluded if e['reason'] == 'geography'])}")
print(f"  Separated (DAF):          {len(daf_signals)}")
print(f"  Candidates after filters: {len(candidates)}")
print(f"\n  By category:")
for cat in ['MULTI_PEER_FUNDER', 'PEER_PLUS_KEYWORD', 'SINGLE_PEER_FUNDER', 'STRONG_KEYWORD', 'KEYWORD_MATCH']:
    count = len([c for c in candidates if c['category'] == cat])
    if count:
        print(f"    {cat}: {count}")

# =====================================================
# STEP 6: GENERATE RANKED MARKDOWN
# =====================================================
print("\nStep 6: Generating ranked markdown...")

md_lines = [
    "# VetsBoats Public Charity Funder Candidates",
    "",
    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    f"**Source:** f990_2025.schedule_i_grants (997K grants, 48K public charity grantmakers, 2019-2023)",
    f"**Method:** Peer funder analysis + thematic keyword search",
    "",
    "## Funnel Summary",
    "",
    f"- Total filers discovered: {len(all_filer_eins)}",
    f"- Excluded (known funders): {len([e for e in excluded if e['reason'] == 'known_funder'])}",
    f"- Excluded (geography): {len([e for e in excluded if e['reason'] == 'geography'])}",
    f"- Separated (DAF platforms): {len(daf_signals)}",
    f"- **Candidates after filters: {len(candidates)}**",
    "",
    "---",
    "",
]

# Group by category
sections = [
    ('MULTI_PEER_FUNDER', 'Multi-Peer Funders', 'Fund 2+ VetsBoats peer organizations'),
    ('PEER_PLUS_KEYWORD', 'Peer + Keyword Funders', 'Fund 1 peer org AND make thematically relevant grants'),
    ('SINGLE_PEER_FUNDER', 'Single Peer Funders', 'Fund exactly 1 peer organization'),
    ('STRONG_KEYWORD', 'Strong Keyword Matches', 'Thematically strong grants (adaptive sailing, veteran recreation)'),
    ('KEYWORD_MATCH', 'Keyword Matches', 'Thematically relevant grants'),
]

for cat_key, cat_title, cat_desc in sections:
    cat_candidates = [c for c in candidates if c['category'] == cat_key]
    if not cat_candidates:
        continue

    md_lines.append(f"## {cat_title} ({len(cat_candidates)})")
    md_lines.append("")
    md_lines.append(f"*{cat_desc}*")
    md_lines.append("")

    for i, c in enumerate(cat_candidates, 1):
        md_lines.append(f"### {i}. {c['name']}")
        md_lines.append("")
        md_lines.append(f"**EIN:** {c['ein']}")
        md_lines.append("")

        md_lines.append(f"**Location:** {c['city']}, {c['state']}" if c['city'] else f"**Location:** {c['state']}")
        md_lines.append("")

        if c['website'] and c['website'].lower() not in ('n/a', 'none', '0', ''):
            url = c['website'] if c['website'].startswith('http') else 'http://' + c['website']
            md_lines.append(f"**Website:** [{c['website']}]({url})")
        else:
            md_lines.append("**Website:** None on file")
        md_lines.append("")

        md_lines.append(f"**Category:** {c['category']} | **Score:** {c['score']}")
        md_lines.append("")

        md_lines.append(f"**Revenue:** {fmt_money(c['total_revenue'])} | **Assets:** {fmt_money(c['total_assets'])}")
        md_lines.append("")

        md_lines.append(f"**Grantmaking:** {fmt_number(c['total_grants'])} grants | {fmt_number(c['distinct_recipients'])} recipients | {fmt_money(c['total_amount'])} total | Latest: {c['latest_year']}")
        md_lines.append("")

        md_lines.append(f"**CA Activity:** {fmt_number(c['ca_grants'])} grants ({fmt_money(c['ca_total'])}) | Grants in {c['state_count']} states")
        md_lines.append("")

        if c['peer_grant_details']:
            md_lines.append(f"**Peer Grants ({c['peer_count']} peers: {', '.join(c['peers_funded'])}):**")
            md_lines.append("")
            for pg in c['peer_grant_details']:
                purpose_snip = (pg['purpose'] or '')[:100]
                if len(pg['purpose'] or '') > 100:
                    purpose_snip += '...'
                md_lines.append(f"- {pg['peer']}: {fmt_money(pg['amount'])} ({pg['year']}) {purpose_snip}")
            md_lines.append("")

        if c['keyword_grant_details']:
            md_lines.append("**Keyword Grants:**")
            md_lines.append("")
            for kg in c['keyword_grant_details']:
                purpose_snip = (kg['purpose'] or '')[:120]
                if len(kg['purpose'] or '') > 120:
                    purpose_snip += '...'
                md_lines.append(f"- To {kg['recipient']}: {fmt_money(kg['amount'])} ({kg['year']}) \"{purpose_snip}\"")
            md_lines.append("")

        if c['mission']:
            mission_snip = c['mission'][:300]
            if len(c['mission']) > 300:
                mission_snip += '...'
            md_lines.append(f"**Mission:** {mission_snip}")
            md_lines.append("")

        md_lines.append("**Status:** NEW - Needs review")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

# PF Leads section
md_lines.append("## Previously Researched PF Leads (6)")
md_lines.append("")
md_lines.append("*These foundations were identified in prior deep crawl batches. Included for completeness.*")
md_lines.append("")

for pf in PF_LEADS:
    md_lines.append(f"### {pf['name']}")
    md_lines.append("")
    md_lines.append(f"**EIN:** {pf['ein']}")
    md_lines.append("")
    md_lines.append(f"**Fit Rating:** {pf['fit']}")
    md_lines.append("")
    md_lines.append(f"**Notes:** {pf['notes']}")
    md_lines.append("")
    md_lines.append("**Status:** ALREADY_RESEARCHED (PF deep crawl)")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

# Excluded summary
md_lines.append("## Excluded Filers")
md_lines.append("")
geo_excluded = [e for e in excluded if e['reason'] == 'geography']
known_excluded = [e for e in excluded if e['reason'] == 'known_funder']
if known_excluded:
    md_lines.append(f"**Known funders ({len(known_excluded)}):** {', '.join(e['name'] for e in known_excluded)}")
    md_lines.append("")
if geo_excluded:
    md_lines.append(f"**Geographic filter ({len(geo_excluded)}):**")
    md_lines.append("")
    for e in geo_excluded:
        md_lines.append(f"- {e['name']} (EIN {e['ein']}, HQ: {e.get('state', '?')}, CA grants: {e.get('ca_grants', 0)}, states: {e.get('state_count', 0)})")
    md_lines.append("")

md_text = "\n".join(md_lines)
md_path = f"{OUTPUT_DIR}/DATA_2026-02-21_vetsboats_pc_candidates_ranked.md"
with open(md_path, 'w') as f:
    f.write(md_text)
print(f"  Wrote {md_path}")

# =====================================================
# STEP 7: GENERATE JSON
# =====================================================
print("\nStep 7: Generating JSON...")

json_data = {
    'metadata': {
        'generated': datetime.now().isoformat(),
        'source_table': 'f990_2025.schedule_i_grants',
        'method': 'Peer funder analysis + thematic keyword search',
        'peer_eins': PEER_EINS,
        'known_funders_excluded': list(ALL_KNOWN_FUNDERS),
        'daf_eins': DAF_EINS,
        'funnel': {
            'total_filers': len(all_filer_eins),
            'excluded_known': len(known_excluded),
            'excluded_geography': len(geo_excluded),
            'separated_daf': len(daf_signals),
            'final_candidates': len(candidates),
        },
    },
    'candidates': candidates,
    'pf_leads': PF_LEADS,
    'excluded': excluded,
    'daf_signals': [{
        'ein': d['ein'],
        'name': d['name'],
        'peer_grants': d['peer_grants'],
        'keyword_grants': d['keyword_grants'],
        'total_grants': d['volume'].get('total_grants', 0),
    } for d in daf_signals],
}

json_path = f"{OUTPUT_DIR}/DATA_2026-02-21_vetsboats_pc_query_results.json"
with open(json_path, 'w') as f:
    json.dump(json_data, f, indent=2, default=str)
print(f"  Wrote {json_path}")

# =====================================================
# STEP 8: GENERATE DAF SIGNALS MARKDOWN
# =====================================================
print("\nStep 8: Generating DAF signals markdown...")

daf_lines = [
    "# VetsBoats DAF Platform Activity on Peer Organizations",
    "",
    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "DAF (Donor-Advised Fund) platforms are intermediaries, not direct decision-makers.",
    "These signals show which peers receive DAF-channeled funding but are not directly actionable for outreach.",
    "",
    "---",
    "",
]

for d in daf_signals:
    daf_lines.append(f"## {d['name']} (EIN: {d['ein']})")
    daf_lines.append("")
    daf_lines.append(f"**Total grantmaking in DB:** {fmt_number(d['volume'].get('total_grants', 0))} grants")
    daf_lines.append("")

    if d['peer_grants']:
        daf_lines.append("**Peer org grants:**")
        daf_lines.append("")
        for pg in d['peer_grants']:
            daf_lines.append(f"- {pg['peer']}: {fmt_money(pg['amount'])} ({pg['year']})")
        daf_lines.append("")
    else:
        daf_lines.append("*No peer org grants found.*")
        daf_lines.append("")

    if d['keyword_grants']:
        daf_lines.append("**Keyword grants:**")
        daf_lines.append("")
        for kg in d['keyword_grants']:
            purpose_snip = (kg['purpose'] or '')[:120]
            daf_lines.append(f"- To {kg['recipient']}: {fmt_money(kg['amount'])} ({kg['year']}) \"{purpose_snip}\"")
        daf_lines.append("")

    daf_lines.append("---")
    daf_lines.append("")

daf_text = "\n".join(daf_lines)
daf_path = f"{OUTPUT_DIR}/DATA_2026-02-21_vetsboats_daf_signals.md"
with open(daf_path, 'w') as f:
    f.write(daf_text)
print(f"  Wrote {daf_path}")

# =====================================================
# STEP 9: GENERATE REPORT
# =====================================================
print("\nStep 9: Generating session report...")

cat_counts = {}
for cat_key, _, _ in sections:
    cat_counts[cat_key] = len([c for c in candidates if c['category'] == cat_key])

report_lines = [
    "# VetsBoats Public Charity Funder Discovery",
    "",
    "**Date:** 2026-02-21",
    "**Prompt:** Identify and rank public charity grantmakers from schedule_i_grants who fund VetsBoats peers or make thematically relevant grants",
    "**Status:** Complete",
    "**Owner:** Claude Code",
    "",
    "---",
    "",
    "## Revision History",
    "",
    "| Version | Date | Author | Changes |",
    "|---------|------|--------|---------|",
    "| 1.0 | 2026-02-21 | Claude Code | Initial version |",
    "",
    "---",
    "",
    "## Table of Contents",
    "",
    "1. [Executive Summary](#executive-summary)",
    "2. [Methodology](#methodology)",
    "3. [Funnel Metrics](#funnel-metrics)",
    "4. [Candidate Breakdown](#candidate-breakdown)",
    "5. [Key Findings](#key-findings)",
    "6. [Files Created](#files-createdmodified)",
    "7. [Notes](#notes)",
    "",
    "---",
    "",
    "## Executive Summary",
    "",
    f"Searched schedule_i_grants (997K grants from 48K public charity grantmakers, 2019-2023) for funders of VetsBoats peer organizations and thematically relevant grants. Discovered **{len(all_filer_eins)}** distinct filers, filtered to **{len(candidates)}** actionable candidates after removing known funders, DAF platforms, and geographically irrelevant organizations.",
    "",
    "## Methodology",
    "",
    "**Two discovery channels:**",
    "",
    "1. **Peer Funder Analysis:** Identified all public charities that have funded any of 7 VetsBoats peer organizations (Achieve Tahoe, DSES, TISC, Sail to Prevail, BAADS, Judd Goldman, Warrior Sailing) using both EIN matching and name ILIKE fallbacks.",
    "",
    "2. **Keyword Discovery:** Searched grant purpose text for thematic keywords (adaptive sailing, therapeutic sailing, veteran+sailing/boating/maritime/adaptive/recreation, disabled+sailing/adaptive sport/recreation, therapeutic recreation). Limited to grants >= $5K since 2022.",
    "",
    "**Filter pipeline:**",
    "",
    "1. Remove known funders (dim_clients + PF work + existing schedule_i funders)",
    "2. Separate DAF platforms (Fidelity, Schwab, NPT, Vanguard, Morgan Stanley, Network for Good, Mightycause, TisBest)",
    "3. Geographic filter: keep if HQ in CA/OR/NV/WA/HI, OR has CA grants, OR grants to 10+ states",
    "",
    "**Classification hierarchy:**",
    "",
    "- MULTI_PEER_FUNDER: funds 2+ peer orgs (strongest signal)",
    "- PEER_PLUS_KEYWORD: 1 peer + keyword match",
    "- SINGLE_PEER_FUNDER: 1 peer only",
    "- STRONG_KEYWORD: keyword match with veteran/adaptive sailing terms",
    "- KEYWORD_MATCH: general thematic match",
    "",
    "## Funnel Metrics",
    "",
    "| Stage | Count |",
    "|-------|-------|",
    f"| Peer filer discovery | {len(peer_funder_data)} |",
    f"| Keyword filer discovery | {len(keyword_funder_data)} |",
    f"| Combined (deduplicated) | {len(all_filer_eins)} |",
    f"| Excluded: known funders | {len(known_excluded)} |",
    f"| Excluded: geography | {len(geo_excluded)} |",
    f"| Separated: DAF platforms | {len(daf_signals)} |",
    f"| **Final candidates** | **{len(candidates)}** |",
    "",
    "## Candidate Breakdown",
    "",
    "| Category | Count | Description |",
    "|----------|-------|-------------|",
]

for cat_key, cat_title, cat_desc in sections:
    count = cat_counts.get(cat_key, 0)
    if count:
        report_lines.append(f"| {cat_title} | {count} | {cat_desc} |")

report_lines.extend([
    f"| **Total** | **{len(candidates)}** | |",
    "",
    "## Key Findings",
    "",
])

# Top candidates summary
multi_peer = [c for c in candidates if c['category'] == 'MULTI_PEER_FUNDER']
if multi_peer:
    report_lines.append(f"**Highest-priority candidates ({len(multi_peer)} multi-peer funders):**")
    report_lines.append("")
    for c in multi_peer:
        report_lines.append(f"- **{c['name']}** (EIN {c['ein']}): Funds {c['peer_count']} peers ({', '.join(c['peers_funded'])}). {fmt_number(c['total_grants'])} total grants, {fmt_money(c['total_amount'])}. {fmt_number(c['ca_grants'])} CA grants.")
    report_lines.append("")

report_lines.extend([
    f"**DAF activity:** {len(daf_signals)} DAF platforms found in results, separated into intel file. Not directly actionable but shows peer orgs receive DAF-channeled funding.",
    "",
    f"**PF leads carried forward:** 6 previously researched private foundation leads included for completeness.",
    "",
    "## Files Created/Modified",
    "",
    "| File | Path | Description |",
    "|------|------|-------------|",
    f"| discover_pc_funders.py | Enhancements/2026-02-21/ | Main discovery script |",
    f"| DATA_...pc_candidates_ranked.md | Enhancements/2026-02-21/ | Ranked candidate list ({len(candidates)} candidates) |",
    f"| DATA_...pc_query_results.json | Enhancements/2026-02-21/ | Full structured data for Prompt 2 reuse |",
    f"| DATA_...daf_signals.md | Enhancements/2026-02-21/ | DAF platform activity ({len(daf_signals)} platforms) |",
    f"| REPORT_...pc_discovery.md | Enhancements/2026-02-21/ | This report |",
    "",
    "## Notes",
    "",
    "- **Next step:** Alec reviews ranked candidates, marks GO/NO-GO, then targeted deep crawls on approved candidates (Prompt 2).",
    "- **Keyword search is intentionally narrow** to avoid false positives. Broader veteran keyword search would return hundreds of community foundations with general veteran grants.",
    "- **Geographic filter is permissive** (Pacific states + national funders). Some single-peer funders may be geographically irrelevant for VetsBoats specifically.",
    "- **schedule_i_grants covers 2019-2023** tax years. Some funders may have changed focus since their last filing.",
    "",
    "---",
    "",
    "*Generated by Claude Code on 2026-02-21*",
])

report_text = "\n".join(report_lines)
report_path = f"{OUTPUT_DIR}/REPORT_2026-02-21_P1_vetsboats_pc_discovery.md"
with open(report_path, 'w') as f:
    f.write(report_text)
print(f"  Wrote {report_path}")

# =====================================================
# DONE
# =====================================================
print(f"\n=== DONE ===")
print(f"  Candidates: {len(candidates)}")
print(f"  DAF signals: {len(daf_signals)}")
print(f"  PF leads: {len(PF_LEADS)}")
print(f"  Excluded: {len(excluded)}")
print(f"\nOutput files:")
print(f"  {md_path}")
print(f"  {json_path}")
print(f"  {daf_path}")
print(f"  {report_path}")

cur.close()
conn.close()
