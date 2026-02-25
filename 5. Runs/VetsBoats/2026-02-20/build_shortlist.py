#!/usr/bin/env python3
"""
VetsBoats Hard-Filtered Foundation Shortlist Builder
Produces: HTML review file, CSV export, summary report
"""

import psycopg2
import psycopg2.extras
import csv
import json
from datetime import datetime

# --- Config ---
CLIENT_EIN = '464194065'
CLIENT_NAME = 'VetsBoats (Wooden Boats for Veterans)'
OUTPUT_DIR = '/Users/aleckleinman/Documents/TheGrantScout/5. Runs/VetsBoats/2026-02-20'

KNOWN_FUNDERS = {
    '680400024': 'Tahoe Maritime Museum Foundation',
    '953059828': 'Henry Mayo Newhall Foundation',
    '956054953': 'Sidney Stern Memorial Trust',
    '841849498': 'Charis Fund',
    '843805975': 'Bonnell Cove Foundation',
}

VETERAN_KEYWORDS_REGEX = r'(veteran|military|armed forces|service member|wounded warrior|adaptive sailing|therapeutic sailing|adaptive recreation)'

conn = psycopg2.connect(
    host='localhost', port=5432, database='thegrantscout',
    user='postgres'
)
conn.set_session(readonly=True)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# =====================================================
# STEP 1: Build candidate pool
# =====================================================
print("Step 1: Building candidate pool...")

# Source A: Sibling analysis
cur.execute("""
    SELECT DISTINCT foundation_ein
    FROM f990_2025.calc_client_foundation_scores
    WHERE client_ein = %s
""", (CLIENT_EIN,))
source_a = {row['foundation_ein'] for row in cur.fetchall()}
print(f"  Source A (sibling analysis): {len(source_a)} foundations")

# Source B: Veteran keyword search
cur.execute("""
    SELECT DISTINCT foundation_ein
    FROM f990_2025.fact_grants
    WHERE LOWER(purpose_text) ~ %s
""", (VETERAN_KEYWORDS_REGEX,))
source_b = {row['foundation_ein'] for row in cur.fetchall()}
print(f"  Source B (veteran keywords): {len(source_b)} foundations")

all_candidates = source_a | source_b
print(f"  Combined pool (A ∪ B): {len(all_candidates)} foundations")

# Track source for each
source_map = {}
for ein in all_candidates:
    in_a = ein in source_a
    in_b = ein in source_b
    if in_a and in_b:
        source_map[ein] = 'both'
    elif in_a:
        source_map[ein] = 'sibling'
    else:
        source_map[ein] = 'keyword'

# =====================================================
# STEP 2: Get latest filing data for each foundation
# =====================================================
print("Step 2: Getting latest filing data...")

ein_list = list(all_candidates)
# Use ANY array for large IN clause
cur.execute("""
    WITH latest AS (
        SELECT DISTINCT ON (ein)
            ein,
            business_name,
            state,
            website_url,
            total_assets_eoy_amt,
            fmv_assets_eoy_amt,
            total_grant_paid_amt,
            qualifying_distributions_amt,
            only_contri_to_preselected_ind,
            grants_to_organizations_ind,
            tax_year,
            mission_desc,
            activity_or_mission_desc,
            phone_num,
            app_contact_email,
            app_contact_name,
            app_contact_phone
        FROM f990_2025.pf_returns
        WHERE ein = ANY(%s)
        ORDER BY ein, tax_year DESC, return_timestamp DESC NULLS LAST
    )
    SELECT * FROM latest
""", (ein_list,))

filing_data = {}
for row in cur.fetchall():
    filing_data[row['ein']] = dict(row)

print(f"  Found filing data for {len(filing_data)} of {len(all_candidates)} candidates")

# Candidates without filing data are dropped
missing_filings = all_candidates - set(filing_data.keys())
if missing_filings:
    print(f"  WARNING: {len(missing_filings)} candidates have no pf_returns data")

# =====================================================
# STEP 3: Apply Filter 1 - Open to applicants
# =====================================================
print("Step 3: Applying Filter 1 (open to applicants)...")

filter1_pass = set()
filter1_fail = set()
for ein, data in filing_data.items():
    preselected = data.get('only_contri_to_preselected_ind')
    # Pass if not preselected-only (FALSE or NULL)
    # grants_to_organizations_ind is unreliable — all candidates demonstrably make grants
    if preselected is not True:
        filter1_pass.add(ein)
    else:
        filter1_fail.add(ein)

print(f"  Filter 1 pass: {len(filter1_pass)}, fail: {len(filter1_fail)}")

# =====================================================
# STEP 4: Apply Filter 2 - Geographic (CA grants)
# =====================================================
print("Step 4: Applying Filter 2 (CA geography)...")

cur.execute("""
    SELECT foundation_ein, COUNT(*) as ca_grant_count
    FROM f990_2025.fact_grants
    WHERE foundation_ein = ANY(%s)
      AND recipient_state = 'CA'
    GROUP BY foundation_ein
""", (ein_list,))

ca_grants = {}
for row in cur.fetchall():
    ca_grants[row['foundation_ein']] = row['ca_grant_count']

# Also pass foundations HQ'd in CA even without explicit CA grants (they may give nationally)
filter2_pass = set()
filter2_fail = set()
for ein in filing_data:
    has_ca_grants = ca_grants.get(ein, 0) > 0
    is_ca_hq = filing_data[ein].get('state') == 'CA'
    if has_ca_grants or is_ca_hq:
        filter2_pass.add(ein)
    else:
        filter2_fail.add(ein)

print(f"  Filter 2 pass: {len(filter2_pass)}, fail: {len(filter2_fail)}")

# =====================================================
# STEP 5: Apply Filter 3 - PF-to-PF grants
# =====================================================
print("Step 5: Applying Filter 3 (PF-to-PF grants)...")

# Method: Join fact_grants recipient_ein to pf_returns to confirm recipient is a PF
cur.execute("""
    SELECT
        fg.foundation_ein,
        COUNT(*) as pf_grant_count,
        SUM(fg.amount) as pf_grant_total
    FROM f990_2025.fact_grants fg
    JOIN f990_2025.pf_returns pr ON fg.recipient_ein = pr.ein
    WHERE fg.foundation_ein = ANY(%s)
      AND fg.recipient_ein IS NOT NULL
    GROUP BY fg.foundation_ein
""", (ein_list,))

pf_to_pf = {}
for row in cur.fetchall():
    pf_to_pf[row['foundation_ein']] = {
        'count': row['pf_grant_count'],
        'total': row['pf_grant_total'] or 0
    }

# Deduplicate: pf_returns may have multiple rows per EIN (multiple years)
# The JOIN above will count duplicates. Let's use DISTINCT recipient_ein approach
cur.execute("""
    SELECT
        fg.foundation_ein,
        COUNT(DISTINCT fg.id) as pf_grant_count,
        COALESCE(SUM(fg.amount), 0) as pf_grant_total
    FROM f990_2025.fact_grants fg
    WHERE fg.foundation_ein = ANY(%s)
      AND fg.recipient_ein IS NOT NULL
      AND EXISTS (
          SELECT 1 FROM f990_2025.pf_returns pr
          WHERE pr.ein = fg.recipient_ein
      )
    GROUP BY fg.foundation_ein
""", (ein_list,))

pf_to_pf = {}
for row in cur.fetchall():
    pf_to_pf[row['foundation_ein']] = {
        'count': row['pf_grant_count'],
        'total': int(row['pf_grant_total'])
    }

filter3_pass = set(pf_to_pf.keys())
filter3_fail = set(filing_data.keys()) - filter3_pass

print(f"  Filter 3 pass: {len(filter3_pass)}, fail: {len(filter3_fail)}")

# =====================================================
# STEP 6: Get additional metrics
# =====================================================
print("Step 6: Getting additional metrics...")

# Total grants per foundation
cur.execute("""
    SELECT foundation_ein, COUNT(*) as total_grants
    FROM f990_2025.fact_grants
    WHERE foundation_ein = ANY(%s)
    GROUP BY foundation_ein
""", (ein_list,))
total_grants_map = {row['foundation_ein']: row['total_grants'] for row in cur.fetchall()}

# Veteran keyword grants per foundation
cur.execute("""
    SELECT foundation_ein,
           COUNT(*) as vet_count,
           COALESCE(SUM(amount), 0) as vet_total
    FROM f990_2025.fact_grants
    WHERE foundation_ein = ANY(%s)
      AND LOWER(purpose_text) ~ %s
    GROUP BY foundation_ein
""", (ein_list, VETERAN_KEYWORDS_REGEX))
vet_grants = {row['foundation_ein']: {'count': row['vet_count'], 'total': int(row['vet_total'])} for row in cur.fetchall()}

# Target grant counts from sibling analysis
cur.execute("""
    SELECT foundation_ein, target_grants_to_siblings, lasso_score
    FROM f990_2025.calc_client_foundation_scores
    WHERE client_ein = %s AND foundation_ein = ANY(%s)
""", (CLIENT_EIN, ein_list))
sibling_data = {row['foundation_ein']: {
    'target_grants': row['target_grants_to_siblings'],
    'lasso_score': float(row['lasso_score']) if row['lasso_score'] else None
} for row in cur.fetchall()}

# Annual giving from calc_foundation_profiles
cur.execute("""
    SELECT ein, total_giving_5yr, unique_recipients_5yr
    FROM f990_2025.calc_foundation_profiles
    WHERE ein = ANY(%s)
""", (ein_list,))
profiles = {row['ein']: {
    'annual_giving': int(row['total_giving_5yr'] / 5) if row['total_giving_5yr'] else None,
    'unique_recipients': row['unique_recipients_5yr']
} for row in cur.fetchall()}

# =====================================================
# STEP 7: Assemble results
# =====================================================
print("Step 7: Assembling results...")

all_three_pass = filter1_pass & filter2_pass & filter3_pass
near_misses = set()  # Passed exactly 2 of 3
for ein in filing_data:
    passes = sum([ein in filter1_pass, ein in filter2_pass, ein in filter3_pass])
    if passes == 2:
        near_misses.add(ein)

results = []
for ein in filing_data:
    fd = filing_data[ein]
    passes = sum([ein in filter1_pass, ein in filter2_pass, ein in filter3_pass])

    # Pick mission description (longer of the two)
    mission = fd.get('mission_desc') or ''
    activity = fd.get('activity_or_mission_desc') or ''
    description = mission if len(mission) >= len(activity) else activity

    assets = fd.get('total_assets_eoy_amt') or fd.get('fmv_assets_eoy_amt')

    row = {
        'foundation_ein': ein,
        'foundation_name': fd.get('business_name', ''),
        'state': fd.get('state', ''),
        'website_url': fd.get('website_url', ''),
        'total_assets': int(assets) if assets else None,
        'annual_giving': profiles.get(ein, {}).get('annual_giving'),
        'total_grants_made': total_grants_map.get(ein, 0),
        'pf_to_pf_grant_count': pf_to_pf.get(ein, {}).get('count', 0),
        'pf_to_pf_total_amount': pf_to_pf.get(ein, {}).get('total', 0),
        'ca_grant_count': ca_grants.get(ein, 0),
        'veteran_grant_count': vet_grants.get(ein, {}).get('count', 0),
        'veteran_grant_amount': vet_grants.get(ein, {}).get('total', 0),
        'target_grant_count': sibling_data.get(ein, {}).get('target_grants', 0),
        'lasso_score': sibling_data.get(ein, {}).get('lasso_score'),
        'open_to_applicants': ein in filter1_pass,
        'gives_in_ca': ein in filter2_pass,
        'funds_pfs': ein in filter3_pass,
        'latest_tax_year': fd.get('tax_year'),
        'source': source_map.get(ein, 'new'),
        'known_funder': ein in KNOWN_FUNDERS,
        'filter_passes': passes,
        'failed_filter': [],
        'description': description,
        'phone': fd.get('phone_num', ''),
        'app_contact_email': fd.get('app_contact_email', ''),
        'app_contact_name': fd.get('app_contact_name', ''),
    }

    if ein not in filter1_pass:
        row['failed_filter'].append('Open to Applicants')
    if ein not in filter2_pass:
        row['failed_filter'].append('CA Geography')
    if ein not in filter3_pass:
        row['failed_filter'].append('PF-to-PF Grants')

    results.append(row)

# Sort: passed all 3 first, then near misses, then rest
# Within each group: pf_to_pf_grant_count DESC, veteran_grant_count DESC, ca_grant_count DESC
results.sort(key=lambda r: (
    -r['filter_passes'],
    -r['pf_to_pf_grant_count'],
    -r['veteran_grant_count'],
    -r['ca_grant_count']
))

passed_all = [r for r in results if r['filter_passes'] == 3]
near_miss_results = [r for r in results if r['filter_passes'] == 2]
rest = [r for r in results if r['filter_passes'] < 2]

print(f"\n=== FUNNEL SUMMARY ===")
print(f"  Total candidate pool: {len(filing_data)}")
print(f"  Passed Filter 1 (open): {len(filter1_pass)}")
print(f"  Passed F1 + F2 (open + CA): {len(filter1_pass & filter2_pass)}")
print(f"  Passed ALL 3: {len(all_three_pass)}")
print(f"  Near misses (2 of 3): {len(near_misses)}")

# =====================================================
# STEP 8: Write CSV
# =====================================================
print("\nStep 8: Writing CSV...")

csv_path = f"{OUTPUT_DIR}/DATA_2026-02-20_vetsboats_hardfiltered_prospects.csv"
csv_headers = [
    'foundation_ein', 'foundation_name', 'state', 'website_url', 'total_assets',
    'annual_giving', 'total_grants_made', 'pf_to_pf_grant_count', 'pf_to_pf_total_amount',
    'ca_grant_count', 'veteran_grant_count', 'veteran_grant_amount', 'target_grant_count',
    'lasso_score', 'open_to_applicants', 'gives_in_ca', 'funds_pfs',
    'latest_tax_year', 'source', 'known_funder', 'filter_passes', 'failed_filters',
    'description', 'phone', 'app_contact_email', 'app_contact_name'
]

with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
    for r in results:
        row = {k: r.get(k, '') for k in csv_headers}
        row['failed_filters'] = '; '.join(r.get('failed_filter', []))
        writer.writerow(row)

print(f"  Wrote {len(results)} rows to CSV")

# =====================================================
# STEP 9: Write HTML
# =====================================================
print("Step 9: Writing HTML review file...")

def fmt_money(val):
    if val is None or val == 0:
        return '$0'
    if val >= 1_000_000_000:
        return f'${val/1_000_000_000:.1f}B'
    if val >= 1_000_000:
        return f'${val/1_000_000:.1f}M'
    if val >= 1_000:
        return f'${val/1_000:.0f}K'
    return f'${val:,.0f}'

def fmt_number(val):
    if val is None:
        return '0'
    return f'{val:,}'

def make_badge(passed, label_pass, label_fail):
    if passed:
        return f'<span class="badge badge-pass">&#x2705; {label_pass}</span>'
    else:
        return f'<span class="badge badge-fail">&#x274C; {label_fail}</span>'

def make_card(r, section):
    ein = r['foundation_ein']
    name = r['foundation_name'] or 'Unknown'
    url = r.get('website_url', '')

    # Clean URL
    if url and url.lower() not in ('n/a', 'none', '0', ''):
        if not url.startswith('http'):
            url = 'http://' + url
        url_html = f'<a href="{url}" target="_blank" rel="noopener">{url}</a>'
    else:
        url_html = '<span class="no-url">No website on file</span>'

    known_banner = ''
    if r['known_funder']:
        known_banner = '<div class="known-funder-banner">&#x26A0;&#xFE0F; KNOWN FUNDER - Already in VetsBoats network</div>'

    border_class = 'card-pass' if section == 'pass' else 'card-near'

    # Badges
    b1 = make_badge(r['open_to_applicants'], 'Open to Applicants', 'Preselected Only')
    b2_label = f"Gives in CA ({fmt_number(r['ca_grant_count'])} grants)" if r['gives_in_ca'] else 'No CA Grants'
    b2 = make_badge(r['gives_in_ca'], b2_label, b2_label)
    b3_label = f"Funds PFs ({fmt_number(r['pf_to_pf_grant_count'])} grants, {fmt_money(r['pf_to_pf_total_amount'])})" if r['funds_pfs'] else 'No PF Grants'
    b3 = make_badge(r['funds_pfs'], b3_label, b3_label)

    # Source tag
    source_colors = {'sibling': '#3498db', 'keyword': '#27ae60', 'both': '#8e44ad', 'new': '#95a5a6'}
    source_color = source_colors.get(r['source'], '#95a5a6')
    source_tag = f'<span class="source-tag" style="background:{source_color}">{r["source"].upper()}</span>'

    # Failed filter labels for near misses
    failed_html = ''
    if section == 'near' and r.get('failed_filter'):
        failed_html = f'<div class="failed-filter">Failed: {", ".join(r["failed_filter"])}</div>'

    desc = r.get('description', '') or ''
    if len(desc) > 500:
        desc = desc[:500] + '...'
    desc_html = f'<div class="description">{desc}</div>' if desc else ''

    # Contact info
    contact_parts = []
    if r.get('app_contact_name'):
        contact_parts.append(f"Contact: {r['app_contact_name']}")
    if r.get('app_contact_email') and r['app_contact_email'].lower() not in ('n/a', 'none', ''):
        contact_parts.append(f"Email: {r['app_contact_email']}")
    if r.get('phone') and r['phone'].lower() not in ('n/a', 'none', ''):
        contact_parts.append(f"Phone: {r['phone']}")
    contact_html = f'<div class="contact">{" | ".join(contact_parts)}</div>' if contact_parts else ''

    lasso = f" | LASSO: {r['lasso_score']:.2f}" if r.get('lasso_score') is not None else ''

    return f"""
    <div class="card {border_class}">
        {known_banner}
        <div class="card-header">
            <div class="foundation-name">{name}</div>
            <div class="ein">EIN: {ein}</div>
        </div>
        <div class="website">{url_html}</div>
        <div class="meta">
            {r['state'] or 'N/A'} | Assets: {fmt_money(r['total_assets'])} | Annual Giving: {fmt_money(r['annual_giving'])} | Tax Year: {r.get('latest_tax_year', 'N/A')}{lasso}
        </div>
        {desc_html}
        <div class="badges">
            {b1} {b2} {b3}
        </div>
        {failed_html}
        <div class="stats">
            <div class="stat"><span class="stat-val">{fmt_number(r['pf_to_pf_grant_count'])}</span><span class="stat-label">PF Grants</span></div>
            <div class="stat"><span class="stat-val">{fmt_money(r['pf_to_pf_total_amount'])}</span><span class="stat-label">PF Total</span></div>
            <div class="stat"><span class="stat-val">{fmt_number(r['ca_grant_count'])}</span><span class="stat-label">CA Grants</span></div>
            <div class="stat"><span class="stat-val">{fmt_number(r['veteran_grant_count'])}</span><span class="stat-label">Veteran Grants</span></div>
            <div class="stat"><span class="stat-val">{fmt_money(r['veteran_grant_amount'])}</span><span class="stat-label">Veteran $</span></div>
            <div class="stat"><span class="stat-val">{fmt_number(r['target_grant_count'])}</span><span class="stat-label">Sibling Grants</span></div>
            <div class="stat"><span class="stat-val">{fmt_number(r['total_grants_made'])}</span><span class="stat-label">Total Grants</span></div>
        </div>
        {contact_html}
        <div class="source-row">{source_tag}</div>
    </div>"""

# Build cards
pass_cards = ''.join(make_card(r, 'pass') for r in passed_all)
near_cards = ''.join(make_card(r, 'near') for r in near_miss_results)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VetsBoats Foundation Shortlist - Hard Filtered</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; padding: 20px; max-width: 900px; margin: 0 auto; }}
h1 {{ color: #1e3a5f; margin-bottom: 5px; font-size: 24px; }}
.subtitle {{ color: #666; margin-bottom: 20px; font-size: 14px; }}
.funnel {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.funnel h2 {{ font-size: 16px; color: #1e3a5f; margin-bottom: 12px; }}
.funnel-row {{ display: flex; align-items: center; margin-bottom: 6px; }}
.funnel-bar {{ height: 24px; background: #3498db; border-radius: 4px; margin-right: 10px; min-width: 2px; transition: width 0.3s; }}
.funnel-label {{ font-size: 13px; white-space: nowrap; }}
.funnel-count {{ font-weight: bold; font-variant-numeric: tabular-nums; }}
.section-header {{ font-size: 18px; color: #1e3a5f; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #d4a853; }}
.section-count {{ font-size: 14px; color: #666; font-weight: normal; }}
.card {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 5px solid #ccc; }}
.card-pass {{ border-left-color: #27ae60; }}
.card-near {{ border-left-color: #f39c12; }}
.card-header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }}
.foundation-name {{ font-size: 17px; font-weight: 700; color: #1e3a5f; }}
.ein {{ font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; color: #888; }}
.website {{ margin-bottom: 6px; }}
.website a {{ color: #2980b9; text-decoration: underline; font-size: 13px; word-break: break-all; }}
.no-url {{ color: #999; font-size: 13px; font-style: italic; }}
.meta {{ font-size: 13px; color: #555; margin-bottom: 8px; }}
.description {{ font-size: 12px; color: #666; margin-bottom: 8px; line-height: 1.4; padding: 8px; background: #fafafa; border-radius: 4px; }}
.badges {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }}
.badge {{ font-size: 12px; padding: 3px 8px; border-radius: 12px; }}
.badge-pass {{ background: #d4edda; color: #155724; }}
.badge-fail {{ background: #f8d7da; color: #721c24; }}
.failed-filter {{ font-size: 12px; color: #e67e22; font-weight: 600; margin-bottom: 6px; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 6px; }}
.stat {{ text-align: center; }}
.stat-val {{ display: block; font-size: 15px; font-weight: 700; color: #1e3a5f; font-variant-numeric: tabular-nums; }}
.stat-label {{ font-size: 10px; color: #888; text-transform: uppercase; }}
.contact {{ font-size: 12px; color: #555; margin-top: 4px; }}
.source-row {{ margin-top: 6px; }}
.source-tag {{ font-size: 11px; color: #fff; padding: 2px 8px; border-radius: 10px; font-weight: 600; }}
.known-funder-banner {{ background: #fff3cd; color: #856404; padding: 6px 12px; border-radius: 4px; font-weight: 600; font-size: 13px; margin-bottom: 8px; }}
.data-quality {{ background: #fff; border-radius: 8px; padding: 16px; margin-top: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.data-quality h2 {{ font-size: 16px; color: #1e3a5f; margin-bottom: 8px; }}
.data-quality p {{ font-size: 13px; color: #555; line-height: 1.5; }}
.search-box {{ margin-bottom: 16px; }}
.search-box input {{ width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
.search-box input:focus {{ outline: none; border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,0.2); }}
.hidden {{ display: none; }}
</style>
</head>
<body>
<h1>VetsBoats Foundation Shortlist</h1>
<p class="subtitle">Hard-filtered prospects. Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. Client EIN: {CLIENT_EIN}</p>

<div class="funnel">
    <h2>Filter Funnel</h2>
    <div class="funnel-row">
        <div class="funnel-bar" style="width:{min(100, len(filing_data)*100//max(len(filing_data),1))}%"></div>
        <div class="funnel-label"><span class="funnel-count">{len(filing_data)}</span> Total candidate pool</div>
    </div>
    <div class="funnel-row">
        <div class="funnel-bar" style="width:{len(filter1_pass)*100//max(len(filing_data),1)}%; background:#2ecc71"></div>
        <div class="funnel-label"><span class="funnel-count">{len(filter1_pass)}</span> Passed F1: Open to applicants</div>
    </div>
    <div class="funnel-row">
        <div class="funnel-bar" style="width:{len(filter1_pass & filter2_pass)*100//max(len(filing_data),1)}%; background:#27ae60"></div>
        <div class="funnel-label"><span class="funnel-count">{len(filter1_pass & filter2_pass)}</span> Passed F1 + F2: Open + CA geography</div>
    </div>
    <div class="funnel-row">
        <div class="funnel-bar" style="width:{len(all_three_pass)*100//max(len(filing_data),1)}%; background:#1e8449"></div>
        <div class="funnel-label"><span class="funnel-count">{len(all_three_pass)}</span> Passed ALL 3 filters</div>
    </div>
    <div class="funnel-row">
        <div class="funnel-bar" style="width:{len(near_misses)*100//max(len(filing_data),1)}%; background:#f39c12"></div>
        <div class="funnel-label"><span class="funnel-count">{len(near_misses)}</span> Near misses (2 of 3)</div>
    </div>
</div>

<div class="search-box">
    <input type="text" id="search" placeholder="Search by name, EIN, state, or keyword..." oninput="filterCards()">
</div>

<h2 class="section-header">Passed All 3 Filters <span class="section-count">({len(passed_all)} foundations)</span></h2>
<div id="pass-section">
{pass_cards}
</div>

<h2 class="section-header">Near Misses (2 of 3 Filters) <span class="section-count">({len(near_miss_results)} foundations)</span></h2>
<div id="near-section">
{near_cards}
</div>

<div class="data-quality">
    <h2>Data Quality Notes</h2>
    <p><strong>Recipient EIN coverage:</strong> 56.1% of fact_grants have recipient_ein populated. Filter 3 (PF-to-PF) depends on this join, so some foundations may have PF-to-PF grants that we cannot detect because the recipient EIN was not recorded. Near-miss foundations that failed only Filter 3 are worth manual checking.</p>
    <p><strong>CA geography:</strong> Foundations headquartered in CA are included even without explicit CA grants in the database. Some national funders give in CA but have grants recorded without state info.</p>
    <p><strong>Veteran keywords:</strong> Regex search covers: veteran, military, armed forces, service member, wounded warrior, adaptive sailing, therapeutic sailing, adaptive recreation. Some relevant grants may use different terminology.</p>
</div>

<script>
function filterCards() {{
    const q = document.getElementById('search').value.toLowerCase();
    document.querySelectorAll('.card').forEach(card => {{
        card.classList.toggle('hidden', q && !card.textContent.toLowerCase().includes(q));
    }});
}}
</script>
</body>
</html>"""

html_path = f"{OUTPUT_DIR}/REVIEW_2026-02-20_vetsboats_prospects.html"
with open(html_path, 'w') as f:
    f.write(html)

print(f"  Wrote HTML to {html_path}")

# =====================================================
# STEP 10: Summary stats for report
# =====================================================
stats = {
    'total_pool': len(filing_data),
    'source_a': len(source_a),
    'source_b': len(source_b),
    'overlap': len(source_a & source_b),
    'missing_filings': len(missing_filings),
    'filter1_pass': len(filter1_pass),
    'filter1_fail': len(filter1_fail),
    'filter2_pass': len(filter2_pass),
    'filter2_fail': len(filter2_fail),
    'filter3_pass': len(filter3_pass),
    'filter3_fail': len(filter3_fail),
    'f1_f2': len(filter1_pass & filter2_pass),
    'all_three': len(all_three_pass),
    'near_misses': len(near_misses),
    'passed_all': passed_all,
    'near_miss_results': near_miss_results,
    'known_in_passed': len([r for r in passed_all if r['known_funder']]),
    'known_in_near': len([r for r in near_miss_results if r['known_funder']]),
}

# Save stats as JSON for report generation
with open(f"{OUTPUT_DIR}/_stats.json", 'w') as f:
    json.dump({k: v for k, v in stats.items() if not isinstance(v, list)}, f, indent=2)

# Save passed_all and near_miss for report
with open(f"{OUTPUT_DIR}/_passed_all.json", 'w') as f:
    json.dump(passed_all, f, indent=2, default=str)

with open(f"{OUTPUT_DIR}/_near_misses.json", 'w') as f:
    json.dump(near_miss_results, f, indent=2, default=str)

print(f"\n=== DONE ===")
print(f"  HTML: {html_path}")
print(f"  CSV:  {csv_path}")
print(f"  Stats saved for report generation")

cur.close()
conn.close()
