#!/usr/bin/env python3
"""
Cold Call Analysis Script
Analyzes call data to identify patterns predicting successful connections
"""

import pandas as pd
import numpy as np
import os

# File paths
CALLS_CSV = r"/mnt/c/TheGrantScout/4. Sales & Marketing/Cold Calls/Beta Test Group Calls(Phone Outreach Prospects).csv"
OUTPUT_DIR = r"/mnt/c/TheGrantScout/4. Sales & Marketing/Launch Strategy/3. Nonprofit"

# Load data
print("=" * 60)
print("STEP 1: LOAD AND EXPLORE DATA")
print("=" * 60)

# Skip the first empty row (header row issue)
calls = pd.read_csv(CALLS_CSV, skiprows=1)

print(f"Total rows: {len(calls)}")
print(f"\nColumn names:\n{list(calls.columns)}")
print(f"\n--- Outcome Column Distributions ---")
print(f"Talked to Someone:\n{calls['Talked to Someone'].value_counts(dropna=False)}")
print(f"\nReached Decision Maker:\n{calls['Reached Decision Maker'].value_counts(dropna=False)}")
print(f"\nYes/No/Maybe/Uncertain:\n{calls['Yes/No/Maybe/Uncertain'].value_counts(dropna=False)}")
print(f"\nVM/Message:\n{calls['VM/Message'].value_counts(dropna=False)}")

# STEP 2: Create Binary Outcome Flags
print("\n" + "=" * 60)
print("STEP 2: CREATE BINARY OUTCOME FLAGS")
print("=" * 60)

def to_binary(col):
    """Convert outcome columns to binary (handle various formats: text and numeric)"""
    # Convert to string first, handle NaN
    str_col = col.astype(str).str.lower().str.strip()
    # Check for text values OR numeric 1.0
    return (str_col.isin(['yes', 'y', '1', 'true', 'x', '1.0']) | (pd.to_numeric(col, errors='coerce') == 1)).astype(int)

calls['connected'] = to_binary(calls['Talked to Someone'])
calls['reached_dm'] = to_binary(calls['Reached Decision Maker'])
calls['left_vm'] = to_binary(calls['VM/Message'])
calls['email_requested'] = to_binary(calls['Send us an Email'])

# Interest level
calls['interested'] = calls['Yes/No/Maybe/Uncertain'].astype(str).str.lower().str.strip().isin(['yes', 'maybe']).astype(int)

print(f"\n--- Connection Rates ---")
print(f"Connected with anyone: {calls['connected'].mean():.1%}")
print(f"Reached decision maker: {calls['reached_dm'].mean():.1%}")
print(f"Left voicemail: {calls['left_vm'].mean():.1%}")
print(f"Interest (Yes/Maybe): {calls['interested'].mean():.1%}")

# STEP 3: Create Analysis Segments
print("\n" + "=" * 60)
print("STEP 3: CREATE ANALYSIS SEGMENTS")
print("=" * 60)

# Revenue bands
calls['revenue_band'] = pd.cut(
    calls['Total_Revenue'],
    bins=[0, 250000, 500000, 1000000, 2000000, 3000000, 5000000, float('inf')],
    labels=['<$250K', '$250K-$500K', '$500K-$1M', '$1M-$2M', '$2M-$3M', '$3M-$5M', '>$5M']
)

# Grant dependency bands
calls['grant_dep_band'] = pd.cut(
    calls['Grant_Dependency_Pct'],
    bins=[0, 25, 50, 75, 90, 100, float('inf')],
    labels=['0-25%', '25-50%', '50-75%', '75-90%', '90-100%', '>100%']
)

# NTEE sector (first letter)
calls['sector'] = calls['NTEE_Codes'].astype(str).str[0]

# Clean EIN
calls['ein_clean'] = calls['EIN'].astype(str).str.replace('-', '').str.replace('.0', '').str.zfill(9)

# Flag beta clients (these converted AND have been 100% responsive)
beta_client_eins = [
    '462730379',   # Patient Safety Movement Foundation
    '952249495',   # Retirement Housing Foundation (not in data but maybe related orgs)
    '942259716',   # Senior Network Services
    '260542078',   # Ka Ulukoa (not in this data - Hawaii)
    '202707577',   # Arborbrook Christian Academy (not in this data - NC)
    '061468129',   # Horizons National (note: may need leading zero)
    '61468129',    # Horizons National (without leading zero)
    '203472700',   # Friendship Circle SD
    # Also look for RHF-related orgs
    '311042917',   # Villa Greentree (RHF)
    '953815145',   # Diakonia Housing (RHF)
    '310956562',   # Friendship House III (RHF)
    '300105351',   # Independence Square RHF
    '953618525',   # Anaheim Memorial Manor (RHF) - this one said YES!
]

calls['is_beta_client'] = calls['ein_clean'].isin(beta_client_eins)
calls['converted'] = calls['is_beta_client'].astype(int)

print(f"\n--- Beta Client Check ---")
print(f"Beta clients found in call data: {calls['is_beta_client'].sum()}")
if calls['is_beta_client'].sum() > 0:
    print(calls[calls['is_beta_client']][['Organization_Name', 'EIN', 'Total_Revenue', 'NTEE_Codes', 'Yes/No/Maybe/Uncertain']])

# Look for actual "Yes" responses
yes_responses = calls[calls['Yes/No/Maybe/Uncertain'].astype(str).str.lower().str.strip() == 'yes']
print(f"\n--- Organizations that said YES ---")
print(f"Count: {len(yes_responses)}")
if len(yes_responses) > 0:
    print(yes_responses[['Organization_Name', 'EIN', 'Total_Revenue', 'Grant_Dependency_Pct', 'NTEE_Codes', 'State']])

# Look for "Maybe" responses
maybe_responses = calls[calls['Yes/No/Maybe/Uncertain'].astype(str).str.lower().str.strip() == 'maybe']
print(f"\n--- Organizations that said MAYBE ---")
print(f"Count: {len(maybe_responses)}")
if len(maybe_responses) > 0:
    print(maybe_responses[['Organization_Name', 'EIN', 'Total_Revenue', 'Grant_Dependency_Pct', 'NTEE_Codes', 'State']])

# STEP 3b: Analyze Beta Client Conversion / Interested Orgs
print("\n" + "=" * 60)
print("STEP 3b: INTERESTED ORG PROFILE (Yes/Maybe)")
print("=" * 60)

interested_orgs = calls[calls['interested'] == 1]
non_interested = calls[calls['interested'] == 0]

if len(interested_orgs) > 0:
    print(f"\nInterested Org Attributes (n={len(interested_orgs)}):")
    print(f"  Average Revenue: ${interested_orgs['Total_Revenue'].mean():,.0f}")
    print(f"  Revenue Range: ${interested_orgs['Total_Revenue'].min():,.0f} - ${interested_orgs['Total_Revenue'].max():,.0f}")
    print(f"  Median Revenue: ${interested_orgs['Total_Revenue'].median():,.0f}")
    print(f"  Average Grant Dependency: {interested_orgs['Grant_Dependency_Pct'].mean():.1f}%")
    print(f"  Sectors: {interested_orgs['sector'].value_counts().to_dict()}")
    print(f"  States: {interested_orgs['State'].value_counts().to_dict()}")

    print("\n--- Interested vs Non-Interested Comparison ---")
    comparison = pd.DataFrame({
        'Metric': ['Avg Revenue', 'Median Revenue', 'Avg Grant Dependency %', 'Avg Grants Revenue'],
        'Interested': [
            f"${interested_orgs['Total_Revenue'].mean():,.0f}",
            f"${interested_orgs['Total_Revenue'].median():,.0f}",
            f"{interested_orgs['Grant_Dependency_Pct'].mean():.1f}%",
            f"${interested_orgs['Grants_Revenue'].mean():,.0f}"
        ],
        'Non-Interested': [
            f"${non_interested['Total_Revenue'].mean():,.0f}",
            f"${non_interested['Total_Revenue'].median():,.0f}",
            f"{non_interested['Grant_Dependency_Pct'].mean():.1f}%",
            f"${non_interested['Grants_Revenue'].mean():,.0f}"
        ]
    })
    print(comparison.to_string(index=False))

    # What revenue bands did interested orgs come from?
    print("\n--- Interested Orgs by Revenue Band ---")
    print(interested_orgs['revenue_band'].value_counts())

    # What sectors?
    print("\n--- Interested Orgs by Sector ---")
    print(interested_orgs['sector'].value_counts())

# STEP 3c: Conversion Funnel
print("\n" + "=" * 60)
print("STEP 3c: FULL CONVERSION FUNNEL")
print("=" * 60)

# Count rows that have been called (have a contact date or any outcome data)
called_mask = calls['Contact Date'].notna() | (calls['VM/Message'].notna() & (calls['VM/Message'] != ''))
calls_made = calls[called_mask]
total_called = len(calls_made)

total = len(calls)
connected = calls['connected'].sum()
reached_dm = calls['reached_dm'].sum()
interested = calls['interested'].sum()

print(f"Total prospects in file: {total}")
print(f"Prospects called (have contact date/outcome): {total_called}")
print(f"  → Connected with someone: {connected} ({connected/total_called:.1%} of called)" if total_called > 0 else f"  → Connected: {connected}")
if connected > 0:
    print(f"  → Reached DM: {reached_dm} ({reached_dm/total_called:.1%} of called, {reached_dm/connected:.1%} of connected)")
if reached_dm > 0:
    print(f"  → Interested (Yes/Maybe): {interested} ({interested/total_called:.1%} of called, {interested/reached_dm:.1%} of reached DM)")

# STEP 4: Analyze Connection Rate by Factor
print("\n" + "=" * 60)
print("STEP 4: CONNECTION RATE BY FACTOR")
print("=" * 60)

# Only analyze rows that were actually called
calls_analyzed = calls[called_mask].copy()

print(f"\nAnalyzing {len(calls_analyzed)} calls with contact data")

# By Revenue Band
print("\n=== CONNECTION RATE BY REVENUE ===")
if len(calls_analyzed) > 0:
    revenue_analysis = calls_analyzed.groupby('revenue_band', observed=True).agg({
        'connected': ['mean', 'sum', 'count'],
        'reached_dm': 'mean',
        'interested': 'mean'
    }).round(3)
    print(revenue_analysis)

# By Grant Dependency
print("\n=== CONNECTION RATE BY GRANT DEPENDENCY ===")
if len(calls_analyzed) > 0:
    grant_dep_analysis = calls_analyzed.groupby('grant_dep_band', observed=True).agg({
        'connected': ['mean', 'sum', 'count'],
        'reached_dm': 'mean',
        'interested': 'mean'
    }).round(3)
    print(grant_dep_analysis)

# By State
print("\n=== CONNECTION RATE BY STATE ===")
if len(calls_analyzed) > 0:
    state_analysis = calls_analyzed.groupby('State').agg({
        'connected': ['mean', 'sum', 'count'],
        'reached_dm': 'mean'
    }).round(3)
    # Only show states with 3+ calls
    state_analysis = state_analysis[state_analysis[('connected', 'count')] >= 3]
    print(state_analysis.sort_values(('connected', 'mean'), ascending=False))

# By NTEE Sector
print("\n=== CONNECTION RATE BY SECTOR ===")
if len(calls_analyzed) > 0:
    sector_analysis = calls_analyzed.groupby('sector').agg({
        'connected': ['mean', 'sum', 'count'],
        'reached_dm': 'mean',
        'interested': 'mean'
    }).round(3)
    print(sector_analysis.sort_values(('connected', 'mean'), ascending=False))

# STEP 5: Time Patterns (if available)
print("\n" + "=" * 60)
print("STEP 5: TIME PATTERNS")
print("=" * 60)

calls['Contact Date'] = pd.to_datetime(calls['Contact Date'], errors='coerce')

if calls['Contact Date'].notna().sum() > 0:
    calls['day_of_week'] = calls['Contact Date'].dt.day_name()
    calls['call_date'] = calls['Contact Date'].dt.date

    # By day of week
    if calls['day_of_week'].notna().sum() > 0:
        print("By Day of Week:")
        dow_analysis = calls.groupby('day_of_week')['connected'].agg(['mean', 'sum', 'count'])
        print(dow_analysis)

    # By date
    print("\nBy Date:")
    date_analysis = calls.groupby('call_date')['connected'].agg(['mean', 'sum', 'count'])
    print(date_analysis)
else:
    print("Contact Date not populated or not parseable")

# STEP 6: Attribute Comparisons
print("\n" + "=" * 60)
print("STEP 6: ATTRIBUTE COMPARISONS")
print("=" * 60)

calls_analyzed = calls[called_mask].copy()

# Has grants vs no grants
has_grants = calls_analyzed['Grants_Revenue'] > 0
print(f"Has grant revenue: {calls_analyzed[has_grants]['connected'].mean():.1%} connected (n={has_grants.sum()})")
print(f"No grant revenue: {calls_analyzed[~has_grants]['connected'].mean():.1%} connected (n=(~has_grants).sum())")

# High grant dependency vs low
high_grant_dep = calls_analyzed['Grant_Dependency_Pct'] > 75
print(f"\nHigh grant dependency (>75%): {calls_analyzed[high_grant_dep]['connected'].mean():.1%} connected (n={high_grant_dep.sum()})")
print(f"Lower grant dependency (<=75%): {calls_analyzed[~high_grant_dep]['connected'].mean():.1%} connected (n={(~high_grant_dep).sum()})")

# STEP 7: Best-Performing Segments
print("\n" + "=" * 60)
print("STEP 7: BEST-PERFORMING SEGMENTS")
print("=" * 60)

results = []

for rev in calls_analyzed['revenue_band'].dropna().unique():
    for sec in calls_analyzed['sector'].dropna().unique():
        subset = calls_analyzed[(calls_analyzed['revenue_band'] == rev) & (calls_analyzed['sector'] == sec)]
        if len(subset) >= 3:  # Min 3 calls for segment
            results.append({
                'revenue_band': rev,
                'sector': sec,
                'n': len(subset),
                'connect_rate': subset['connected'].mean(),
                'dm_rate': subset['reached_dm'].mean(),
                'interest_rate': subset['interested'].mean()
            })

if results:
    results_df = pd.DataFrame(results).sort_values('connect_rate', ascending=False)
    print("Top segments by connection rate (min 3 calls):")
    print(results_df.head(15).to_string(index=False))

# STEP 8: Build ICP from Interested Orgs
print("\n" + "=" * 60)
print("STEP 8: IDEAL CUSTOMER PROFILE")
print("=" * 60)

interested_orgs = calls[calls['interested'] == 1]

if len(interested_orgs) >= 2:
    icp = {
        'revenue_min': interested_orgs['Total_Revenue'].min(),
        'revenue_max': interested_orgs['Total_Revenue'].max(),
        'revenue_median': interested_orgs['Total_Revenue'].median(),
        'grant_dep_min': interested_orgs['Grant_Dependency_Pct'].min(),
        'grant_dep_max': interested_orgs['Grant_Dependency_Pct'].max(),
        'sectors': interested_orgs['sector'].unique().tolist(),
        'states': interested_orgs['State'].unique().tolist(),
    }

    print(f"""
IDEAL CUSTOMER PROFILE (Based on {len(interested_orgs)} Interested Orgs):

Revenue:        ${icp['revenue_min']:,.0f} - ${icp['revenue_max']:,.0f}
                (Median: ${icp['revenue_median']:,.0f})

Grant Dependency: {icp['grant_dep_min']:.0f}% - {icp['grant_dep_max']:.0f}%

Sectors (NTEE):  {', '.join(str(s) for s in icp['sectors'])}

States:          {', '.join(str(s) for s in icp['states'])}
""")

    # Score all prospects based on similarity to ICP
    calls['icp_score'] = 0

    # Revenue in range: +2 points
    calls.loc[
        (calls['Total_Revenue'] >= icp['revenue_min']) &
        (calls['Total_Revenue'] <= icp['revenue_max']),
        'icp_score'
    ] += 2

    # Sector match: +2 points
    calls.loc[calls['sector'].isin(icp['sectors']), 'icp_score'] += 2

    # Grant dependency in range: +1 point
    calls.loc[
        (calls['Grant_Dependency_Pct'] >= icp['grant_dep_min']) &
        (calls['Grant_Dependency_Pct'] <= icp['grant_dep_max']),
        'icp_score'
    ] += 1

    print("\n--- ICP Score Distribution ---")
    icp_dist = calls.groupby('icp_score').agg({
        'connected': ['mean', 'count'],
        'interested': 'mean'
    }).round(3)
    print(icp_dist)

    print("\n--- Top Non-Interested Prospects (Highest ICP Score, Not Yet Called or Not Interested) ---")
    not_contacted = calls[(calls['interested'] == 0)].copy()
    top_prospects = not_contacted.nlargest(20, 'icp_score')[
        ['Organization_Name', 'State', 'Total_Revenue', 'sector', 'Grant_Dependency_Pct', 'icp_score', 'connected', 'interested', 'Contact Date']
    ]
    print(top_prospects.to_string(index=False))
else:
    calls['icp_score'] = 0
    print("Not enough interested orgs to build ICP")

# STEP 9: Generate Targeting Recommendations
print("\n" + "=" * 60)
print("STEP 9: TARGETING RECOMMENDATIONS")
print("=" * 60)

if len(calls_analyzed) > 0:
    avg_connect = calls_analyzed['connected'].mean()

    recommendations = []

    # Revenue recommendation
    rev_rates = calls_analyzed.groupby('revenue_band', observed=True)['connected'].mean()
    best_rev = rev_rates[rev_rates > avg_connect].index.tolist()
    if best_rev:
        recommendations.append(f"Revenue: Prioritize {', '.join(str(x) for x in best_rev)}")

    # Sector recommendation
    sec_rates = calls_analyzed.groupby('sector')['connected'].mean()
    best_sec = sec_rates[sec_rates > avg_connect].index.tolist()
    if best_sec:
        recommendations.append(f"Sectors: Prioritize NTEE codes starting with {', '.join(str(x) for x in best_sec)}")

    # Grant dependency recommendation
    grant_rates = calls_analyzed.groupby('grant_dep_band', observed=True)['connected'].mean()
    best_grant = grant_rates[grant_rates > avg_connect].index.tolist()
    if best_grant:
        recommendations.append(f"Grant dependency: Prioritize {', '.join(str(x) for x in best_grant)}")

    print(f"\nAverage connection rate: {avg_connect:.1%}")
    print("\nBased on CONNECTION rates (above average):")
    for rec in recommendations:
        print(f"  - {rec}")

# STEP 10: Save Enriched Data
print("\n" + "=" * 60)
print("STEP 10: SAVE ENRICHED DATA")
print("=" * 60)

output_csv = os.path.join(OUTPUT_DIR, "DATA_2025-12-10_call_analysis.csv")
calls.to_csv(output_csv, index=False)
print(f"Saved enriched data to: {output_csv}")

# STEP 11: Generate Summary Stats for Report
print("\n" + "=" * 60)
print("SUMMARY STATS FOR REPORT")
print("=" * 60)

summary = {
    'total_prospects': len(calls),
    'total_called': total_called,
    'connected': connected,
    'connected_pct': connected/total_called*100 if total_called > 0 else 0,
    'reached_dm': reached_dm,
    'reached_dm_pct': reached_dm/total_called*100 if total_called > 0 else 0,
    'interested': interested,
    'interested_pct': interested/total_called*100 if total_called > 0 else 0,
    'left_vm': calls['left_vm'].sum(),
    'left_vm_pct': calls['left_vm'].mean()*100,
}

print(f"""
SUMMARY STATISTICS:
-------------------
Total prospects in file: {summary['total_prospects']}
Total called: {summary['total_called']}
Connected with someone: {summary['connected']} ({summary['connected_pct']:.1f}%)
Reached decision maker: {summary['reached_dm']} ({summary['reached_dm_pct']:.1f}%)
Interested (Yes/Maybe): {summary['interested']} ({summary['interested_pct']:.1f}%)
Left voicemail: {summary['left_vm']} ({summary['left_vm_pct']:.1f}%)
""")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
