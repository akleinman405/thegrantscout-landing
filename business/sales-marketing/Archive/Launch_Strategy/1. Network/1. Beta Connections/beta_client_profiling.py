#!/usr/bin/env python3
"""
Beta Client Profile Analysis
Pull F990 data for beta clients + VetsBoats to understand converted org profiles
"""

import pandas as pd
import psycopg2
import os

# Output directory (same folder as prompt)
OUTPUT_DIR = r"/mnt/c/TheGrantScout/4. Sales & Marketing/Launch Strategy/1. Network/1. Beta Connections"

# Database connection
conn = psycopg2.connect(
    host="172.26.16.1",
    port=5432,
    database="postgres",
    user="postgres",
    password="kmalec21"
)

print("=" * 60)
print("STEP 0: CHECK AVAILABLE TABLES")
print("=" * 60)

# Check what tables exist
tables_query = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'f990_2025'
ORDER BY table_name;
"""
tables_df = pd.read_sql(tables_query, conn)
print("Tables in f990_2025 schema:")
print(tables_df.to_string())

# Check columns in key tables
print("\n--- Checking nonprofit_returns columns ---")
columns_query = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'f990_2025' AND table_name = 'nonprofit_returns'
ORDER BY ordinal_position;
"""
try:
    cols_df = pd.read_sql(columns_query, conn)
    print(cols_df.to_string())
except Exception as e:
    print(f"Table nonprofit_returns not found: {e}")

# Check for pf_grants table
print("\n--- Checking pf_grants columns ---")
pf_grants_query = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'f990_2025' AND table_name = 'pf_grants'
ORDER BY ordinal_position;
"""
try:
    pf_cols_df = pd.read_sql(pf_grants_query, conn)
    print(pf_cols_df.to_string())
except Exception as e:
    print(f"Table pf_grants: {e}")

print("\n" + "=" * 60)
print("STEP 1: DEFINE BETA CLIENT EINS")
print("=" * 60)

# Beta client EINs (with organization names for reference)
beta_clients = {
    '462730379': {'name': 'Patient Safety Movement Foundation', 'group': 'Beta Group 1'},
    '952249495': {'name': 'Retirement Housing Foundation', 'group': 'Beta Group 1'},
    '942259716': {'name': 'Senior Network Services', 'group': 'Beta Group 1'},
    '260542078': {'name': 'Ka Ulukoa', 'group': 'Beta Group 1'},
    '202707577': {'name': 'Arborbrook Christian Academy', 'group': 'Beta Group 1'},
    '061468129': {'name': 'Horizons National', 'group': 'Beta Group 2'},
    '61468129': {'name': 'Horizons National (no leading zero)', 'group': 'Beta Group 2'},
    '203472700': {'name': 'Friendship Circle SD', 'group': 'Beta Group 2'},
    '464194065': {'name': 'VetsBoats Foundation', 'group': 'First Paying Client'},
}

# Create list for SQL IN clause
beta_eins = list(beta_clients.keys())
ein_list = "', '".join(beta_eins)

print(f"Searching for {len(beta_clients)} EINs:")
for ein, info in beta_clients.items():
    print(f"  {ein}: {info['name']} ({info['group']})")

print("\n" + "=" * 60)
print("STEP 2: PULL ORG SIZE METRICS")
print("=" * 60)

# Query: Try to get nonprofit data
# First check if table exists and has data
# Note: column names from schema: total_assets_eoy, net_assets_eoy, contributions_grants, etc.
size_query = f"""
WITH latest AS (
    SELECT ein, MAX(tax_year) as max_year
    FROM f990_2025.nonprofit_returns
    WHERE ein IN ('{ein_list}')
    GROUP BY ein
)
SELECT
    nr.ein,
    nr.organization_name,
    nr.state,
    nr.city,
    nr.ntee_code,
    nr.tax_year,
    nr.total_revenue,
    nr.total_expenses,
    nr.total_assets_eoy as total_assets,
    nr.net_assets_eoy as net_assets,
    nr.contributions_grants as grants_revenue,
    nr.program_service_revenue,
    nr.investment_income,
    ROUND(100.0 * COALESCE(nr.contributions_grants, 0) / NULLIF(nr.total_revenue, 0), 1) as grant_dependency_pct,
    nr.total_employees_cnt as employee_count,
    nr.total_volunteers_cnt as volunteer_count,
    nr.form_type
FROM f990_2025.nonprofit_returns nr
JOIN latest l ON nr.ein = l.ein AND nr.tax_year = l.max_year
ORDER BY nr.total_revenue DESC;
"""

try:
    size_df = pd.read_sql(size_query, conn)
    print(f"\n=== ORG SIZE METRICS (n={len(size_df)}) ===")
    print(size_df.to_string())
except Exception as e:
    print(f"Error querying nonprofit_returns: {e}")
    # Try alternative approach - check what we can find
    alt_query = f"""
    SELECT DISTINCT ein
    FROM f990_2025.nonprofit_returns
    WHERE ein IN ('{ein_list}')
    """
    try:
        alt_df = pd.read_sql(alt_query, conn)
        print(f"Found {len(alt_df)} EINs in nonprofit_returns")
        print(alt_df)
    except Exception as e2:
        print(f"Alternative query also failed: {e2}")
    size_df = pd.DataFrame()

# If nonprofit_returns didn't work, try querying all rows to find matches
if len(size_df) == 0:
    print("\nNo exact EIN matches. Trying broader search...")

    broad_query = """
    SELECT ein, organization_name, tax_year, total_revenue
    FROM f990_2025.nonprofit_returns
    WHERE organization_name ILIKE '%patient safety%'
       OR organization_name ILIKE '%retirement housing%'
       OR organization_name ILIKE '%senior network%'
       OR organization_name ILIKE '%ka ulukoa%'
       OR organization_name ILIKE '%arborbrook%'
       OR organization_name ILIKE '%horizons national%'
       OR organization_name ILIKE '%friendship circle%'
       OR organization_name ILIKE '%vetsboats%'
    ORDER BY organization_name, tax_year DESC;
    """
    try:
        broad_df = pd.read_sql(broad_query, conn)
        print(f"\n=== BROAD NAME SEARCH (n={len(broad_df)}) ===")
        print(broad_df.to_string())
    except Exception as e:
        print(f"Broad search error: {e}")

print("\n" + "=" * 60)
print("STEP 3: PULL FOUNDATION GRANTS RECEIVED")
print("=" * 60)

# Try pf_grants table (foundation grants made TO these orgs)
grants_query = f"""
SELECT
    pg.recipient_ein as ein,
    pg.recipient_name as org_name,
    COUNT(*) as num_grants,
    COUNT(DISTINCT pg.filer_ein) as num_unique_funders,
    SUM(pg.amount) as total_grant_amount,
    ROUND(AVG(pg.amount), 0) as avg_grant_size,
    MIN(pg.amount) as min_grant,
    MAX(pg.amount) as max_grant,
    MIN(pg.tax_year) as earliest_grant_year,
    MAX(pg.tax_year) as latest_grant_year,
    COUNT(DISTINCT pg.tax_year) as years_with_grants
FROM f990_2025.pf_grants pg
WHERE pg.recipient_ein IN ('{ein_list}')
   OR pg.recipient_ein IN ('46-2730379', '95-2249495', '94-2259716', '26-0542078', '20-2707577', '06-1468129', '20-3472700', '46-4194065')
GROUP BY pg.recipient_ein, pg.recipient_name
ORDER BY num_grants DESC;
"""

try:
    grants_df = pd.read_sql(grants_query, conn)
    print(f"\n=== FOUNDATION GRANTS RECEIVED (n={len(grants_df)}) ===")
    if len(grants_df) > 0:
        print(grants_df.to_string())
    else:
        print("No grants found with these EINs")
except Exception as e:
    print(f"Error querying pf_grants: {e}")
    grants_df = pd.DataFrame()

# Try searching by name in grants
if len(grants_df) == 0:
    print("\nTrying name-based grant search...")
    name_grants_query = """
    SELECT
        pg.recipient_ein as ein,
        pg.recipient_name as org_name,
        COUNT(*) as num_grants,
        COUNT(DISTINCT pg.filer_ein) as num_unique_funders,
        SUM(pg.amount) as total_grant_amount,
        MIN(pg.tax_year) as earliest_year,
        MAX(pg.tax_year) as latest_year
    FROM f990_2025.pf_grants pg
    WHERE pg.recipient_name ILIKE '%patient safety%'
       OR pg.recipient_name ILIKE '%retirement housing%'
       OR pg.recipient_name ILIKE '%senior network%'
       OR pg.recipient_name ILIKE '%ka ulukoa%'
       OR pg.recipient_name ILIKE '%arborbrook%'
       OR pg.recipient_name ILIKE '%horizons national%'
       OR pg.recipient_name ILIKE '%friendship circle%'
       OR pg.recipient_name ILIKE '%vetsboats%'
    GROUP BY pg.recipient_ein, pg.recipient_name
    ORDER BY num_grants DESC;
    """
    try:
        grants_df = pd.read_sql(name_grants_query, conn)
        print(f"\n=== GRANTS BY NAME SEARCH (n={len(grants_df)}) ===")
        print(grants_df.to_string())
    except Exception as e:
        print(f"Name-based grant search error: {e}")

print("\n" + "=" * 60)
print("STEP 4: PULL REVENUE TREND")
print("=" * 60)

trend_query = f"""
SELECT
    ein,
    organization_name,
    tax_year,
    total_revenue,
    total_expenses
FROM f990_2025.nonprofit_returns
WHERE ein IN ('{ein_list}')
ORDER BY ein, tax_year;
"""

try:
    trend_df = pd.read_sql(trend_query, conn)
    print(f"\n=== REVENUE TREND (n={len(trend_df)}) ===")
    if len(trend_df) > 0:
        # Pivot to show years as columns
        trend_pivot = trend_df.pivot_table(index='ein', columns='tax_year', values='total_revenue', aggfunc='first')
        print(trend_pivot.to_string())

        # Calculate YoY growth
        trend_df['prev_revenue'] = trend_df.groupby('ein')['total_revenue'].shift(1)
        trend_df['yoy_growth'] = (trend_df['total_revenue'] - trend_df['prev_revenue']) / trend_df['prev_revenue'] * 100
        print("\n=== YEAR-OVER-YEAR GROWTH ===")
        growth_df = trend_df[trend_df['yoy_growth'].notna()][['ein', 'organization_name', 'tax_year', 'total_revenue', 'yoy_growth']]
        if len(growth_df) > 0:
            print(growth_df.to_string())
    else:
        print("No trend data found")
except Exception as e:
    print(f"Error querying trend: {e}")
    trend_df = pd.DataFrame()

print("\n" + "=" * 60)
print("STEP 5: SUMMARY STATISTICS")
print("=" * 60)

if len(size_df) > 0:
    # Exclude RHF from some stats if it's a major outlier
    size_df_no_rhf = size_df[size_df['ein'] != '952249495']

    print(f"\n--- ALL ORGS (n={len(size_df)}) ---")
    print(f"Revenue:     Min ${size_df['total_revenue'].min():,.0f} | Max ${size_df['total_revenue'].max():,.0f} | Median ${size_df['total_revenue'].median():,.0f} | Mean ${size_df['total_revenue'].mean():,.0f}")

    if 'employee_count' in size_df.columns and size_df['employee_count'].notna().sum() > 0:
        print(f"Employees:   Min {size_df['employee_count'].min()} | Max {size_df['employee_count'].max()} | Median {size_df['employee_count'].median()}")

    if 'volunteer_count' in size_df.columns and size_df['volunteer_count'].notna().sum() > 0:
        print(f"Volunteers:  Min {size_df['volunteer_count'].min()} | Max {size_df['volunteer_count'].max()} | Median {size_df['volunteer_count'].median()}")

    if 'grant_dependency_pct' in size_df.columns and size_df['grant_dependency_pct'].notna().sum() > 0:
        print(f"Grant Dep:   Min {size_df['grant_dependency_pct'].min()}% | Max {size_df['grant_dependency_pct'].max()}% | Median {size_df['grant_dependency_pct'].median()}%")

    if len(size_df_no_rhf) > 0:
        print(f"\n--- EXCLUDING RHF (n={len(size_df_no_rhf)}) ---")
        print(f"Revenue:     Min ${size_df_no_rhf['total_revenue'].min():,.0f} | Max ${size_df_no_rhf['total_revenue'].max():,.0f} | Median ${size_df_no_rhf['total_revenue'].median():,.0f}")

    # Grant history summary
    if len(grants_df) > 0:
        print(f"\n--- GRANT HISTORY ---")
        print(f"Grants received: Min {grants_df['num_grants'].min()} | Max {grants_df['num_grants'].max()} | Median {grants_df['num_grants'].median()}")
        print(f"Unique funders:  Min {grants_df['num_unique_funders'].min()} | Max {grants_df['num_unique_funders'].max()}")
        print(f"Orgs with NO foundation grants in F990: {len(size_df) - len(grants_df)}")
else:
    print("No size data available for summary statistics")

print("\n" + "=" * 60)
print("STEP 6: CREATE COMPARISON TABLE")
print("=" * 60)

if len(size_df) > 0:
    # Merge size and grants data
    if len(grants_df) > 0:
        comparison = size_df.merge(
            grants_df[['ein', 'num_grants', 'num_unique_funders', 'total_grant_amount']],
            on='ein', how='left'
        )
        comparison['num_grants'] = comparison['num_grants'].fillna(0).astype(int)
        comparison['num_unique_funders'] = comparison['num_unique_funders'].fillna(0).astype(int)
    else:
        comparison = size_df.copy()
        comparison['num_grants'] = 0
        comparison['num_unique_funders'] = 0
        comparison['total_grant_amount'] = 0

    # Add labels
    def get_client_type(ein):
        if ein in ['464194065', '46-4194065']:
            return 'VetsBoats (Paying)'
        elif ein in ['061468129', '61468129', '203472700']:
            return 'Beta Group 2'
        else:
            return 'Beta Group 1'

    comparison['client_type'] = comparison['ein'].apply(get_client_type)

    # Display key columns
    display_cols = [
        'organization_name', 'client_type', 'state', 'ntee_code',
        'total_revenue', 'total_expenses', 'total_assets',
        'grant_dependency_pct', 'employee_count', 'volunteer_count',
        'num_grants', 'num_unique_funders'
    ]

    # Only use columns that exist
    available_cols = [c for c in display_cols if c in comparison.columns]

    print("\n=== COMPARISON TABLE ===")
    print(comparison[available_cols].sort_values('total_revenue', ascending=False).to_string())
else:
    comparison = pd.DataFrame()
    print("No comparison data available")

print("\n" + "=" * 60)
print("STEP 7: RECOMMENDED ICP RANGE")
print("=" * 60)

if len(size_df) > 0:
    # Exclude outliers (RHF is very large)
    icp_df = size_df[size_df['ein'] != '952249495']

    if len(icp_df) > 0:
        print(f"""
IDEAL CUSTOMER PROFILE (Based on Beta + VetsBoats, excl. RHF)
=============================================================

REVENUE:
  Range: ${icp_df['total_revenue'].min():,.0f} - ${icp_df['total_revenue'].max():,.0f}
  25th percentile: ${icp_df['total_revenue'].quantile(0.25):,.0f}
  75th percentile: ${icp_df['total_revenue'].quantile(0.75):,.0f}
  Recommended target: ${icp_df['total_revenue'].quantile(0.25):,.0f} - ${icp_df['total_revenue'].quantile(0.75):,.0f}
""")

        if 'employee_count' in icp_df.columns and icp_df['employee_count'].notna().sum() > 0:
            print(f"""EMPLOYEES:
  Range: {icp_df['employee_count'].min()} - {icp_df['employee_count'].max()}
  Median: {icp_df['employee_count'].median()}
""")

        if 'grant_dependency_pct' in icp_df.columns and icp_df['grant_dependency_pct'].notna().sum() > 0:
            print(f"""GRANT DEPENDENCY:
  Range: {icp_df['grant_dependency_pct'].min()}% - {icp_df['grant_dependency_pct'].max()}%
  Median: {icp_df['grant_dependency_pct'].median()}%
""")

        if 'ntee_code' in icp_df.columns:
            print(f"""SECTORS (NTEE):
  {icp_df['ntee_code'].value_counts().to_dict()}
""")

        if 'state' in icp_df.columns:
            print(f"""STATES:
  {icp_df['state'].value_counts().to_dict()}
""")

        if len(comparison) > 0 and 'num_grants' in comparison.columns:
            comp_no_rhf = comparison[comparison['ein'] != '952249495']
            if len(comp_no_rhf) > 0:
                print(f"""FOUNDATION GRANTS RECEIVED:
  Range: {comp_no_rhf['num_grants'].min()} - {comp_no_rhf['num_grants'].max()}
  Median: {comp_no_rhf['num_grants'].median()}
""")
else:
    icp_df = pd.DataFrame()
    print("Insufficient data to define ICP range")

print("\n" + "=" * 60)
print("STEP 8: SAVE OUTPUTS")
print("=" * 60)

# Save comparison table
if len(comparison) > 0:
    comparison_file = os.path.join(OUTPUT_DIR, 'DATA_2025-12-10_beta_client_profiles.csv')
    comparison.to_csv(comparison_file, index=False)
    print(f"Saved: {comparison_file}")

# Save summary report
report_file = os.path.join(OUTPUT_DIR, 'REPORT_2025-12-10_beta_client_profile_summary.md')
with open(report_file, 'w') as f:
    f.write("# Beta Client Profile Summary\n\n")
    f.write(f"**Date:** 2025-12-10\n")
    f.write(f"**Orgs Analyzed:** {len(size_df)}\n\n")

    f.write("## Target Organizations\n\n")
    f.write("| Organization | EIN | Group |\n")
    f.write("|--------------|-----|-------|\n")
    for ein, info in beta_clients.items():
        if ein != '61468129':  # Skip duplicate
            f.write(f"| {info['name']} | {ein} | {info['group']} |\n")

    if len(size_df) > 0:
        f.write("\n## Size Metrics\n\n")
        available_cols = [c for c in display_cols if c in comparison.columns]
        comp_sorted = comparison[available_cols].sort_values('total_revenue', ascending=False)
        f.write("| " + " | ".join(available_cols) + " |\n")
        f.write("| " + " | ".join(["---"] * len(available_cols)) + " |\n")
        for _, row in comp_sorted.iterrows():
            vals = []
            for col in available_cols:
                val = row[col]
                if pd.isna(val):
                    vals.append("")
                elif isinstance(val, float):
                    if col in ['total_revenue', 'total_expenses', 'total_assets', 'total_grant_amount']:
                        vals.append(f"${val:,.0f}")
                    else:
                        vals.append(f"{val:.1f}")
                else:
                    vals.append(str(val))
            f.write("| " + " | ".join(vals) + " |\n")

        f.write("\n\n## Summary Statistics\n\n")
        f.write(f"### All Orgs (n={len(size_df)})\n\n")
        f.write(f"- **Revenue:** Min ${size_df['total_revenue'].min():,.0f} | Max ${size_df['total_revenue'].max():,.0f} | Median ${size_df['total_revenue'].median():,.0f}\n")

        if 'grant_dependency_pct' in size_df.columns and size_df['grant_dependency_pct'].notna().sum() > 0:
            f.write(f"- **Grant Dependency:** Min {size_df['grant_dependency_pct'].min()}% | Max {size_df['grant_dependency_pct'].max()}% | Median {size_df['grant_dependency_pct'].median()}%\n")

        if len(icp_df) > 0:
            f.write(f"\n### Excluding RHF (n={len(icp_df)})\n\n")
            f.write(f"- **Revenue:** Min ${icp_df['total_revenue'].min():,.0f} | Max ${icp_df['total_revenue'].max():,.0f} | Median ${icp_df['total_revenue'].median():,.0f}\n")

        f.write("\n## Recommended ICP Range\n\n")
        if len(icp_df) > 0:
            f.write(f"- **Revenue:** ${icp_df['total_revenue'].min():,.0f} - ${icp_df['total_revenue'].max():,.0f}\n")
            f.write(f"- **Recommended Target (25th-75th pct):** ${icp_df['total_revenue'].quantile(0.25):,.0f} - ${icp_df['total_revenue'].quantile(0.75):,.0f}\n")

            if 'employee_count' in icp_df.columns and icp_df['employee_count'].notna().sum() > 0:
                f.write(f"- **Employees:** {icp_df['employee_count'].min():.0f} - {icp_df['employee_count'].max():.0f}\n")

            if 'grant_dependency_pct' in icp_df.columns and icp_df['grant_dependency_pct'].notna().sum() > 0:
                f.write(f"- **Grant Dependency:** {icp_df['grant_dependency_pct'].min():.0f}% - {icp_df['grant_dependency_pct'].max():.0f}%\n")

            if 'ntee_code' in icp_df.columns:
                f.write(f"- **Sectors:** {', '.join(str(x) for x in icp_df['ntee_code'].dropna().unique())}\n")

            if 'state' in icp_df.columns:
                f.write(f"- **States:** {', '.join(str(x) for x in icp_df['state'].dropna().unique())}\n")
    else:
        f.write("\n## Data Status\n\n")
        f.write("No F990 data found for the target EINs in the database.\n")
        f.write("This may indicate:\n")
        f.write("1. EINs don't match format in database (try with/without dashes)\n")
        f.write("2. Organizations file different form types not in nonprofit_returns\n")
        f.write("3. Data has not been imported for these organizations\n")

    if len(grants_df) > 0:
        f.write("\n## Foundation Grants Received\n\n")
        # Write as markdown table without tabulate
        grant_cols = grants_df.columns.tolist()
        f.write("| " + " | ".join(grant_cols) + " |\n")
        f.write("| " + " | ".join(["---"] * len(grant_cols)) + " |\n")
        for _, row in grants_df.iterrows():
            vals = []
            for col in grant_cols:
                val = row[col]
                if pd.isna(val):
                    vals.append("")
                elif isinstance(val, float):
                    if 'amount' in col.lower() or 'grant' in col.lower():
                        vals.append(f"${val:,.0f}")
                    else:
                        vals.append(f"{val:.0f}")
                else:
                    vals.append(str(val))
            f.write("| " + " | ".join(vals) + " |\n")

    f.write("\n\n---\n")
    f.write("*Generated: 2025-12-10*\n")
    f.write("*Prompt: PROMPT_2025-12-10_beta_client_profiling.md*\n")

print(f"Saved: {report_file}")

print("\n=== FILES SAVED ===")
print(f"- {os.path.basename(comparison_file) if len(comparison) > 0 else 'No data file created'}")
print(f"- {os.path.basename(report_file)}")

conn.close()
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
