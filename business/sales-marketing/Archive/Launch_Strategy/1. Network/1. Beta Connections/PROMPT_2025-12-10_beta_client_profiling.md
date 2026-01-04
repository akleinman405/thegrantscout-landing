# Claude Code CLI Prompt
## Beta Client + VetsBoats Profile Analysis

**Goal:** Pull F990 data for all beta clients + VetsBoats to understand the size/profile of orgs that converted. Use this to define targeting criteria for prospect list.

---

## Target EINs

| Organization | EIN | Source |
|--------------|-----|--------|
| Patient Safety Movement Foundation | 462730379 | Beta Group 1 |
| Retirement Housing Foundation | 952249495 | Beta Group 1 |
| Senior Network Services | 942259716 | Beta Group 1 |
| Ka Ulukoa | 260542078 | Beta Group 1 |
| Arborbrook Christian Academy | 202707577 | Beta Group 1 |
| Horizons National | 061468129 | Beta Group 2 |
| Friendship Circle SD | 203472700 | Beta Group 2 |
| VetsBoats Foundation | 464194065 | First Paying Client |

---

## Step 1: Connect to Database

```python
import pandas as pd
import psycopg2

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="thegrantscout",
    # Add credentials as needed
)

# Beta client EINs (include both with and without leading zeros)
beta_eins = [
    '462730379',  # PSMF
    '952249495',  # RHF
    '942259716',  # SNS
    '260542078',  # Ka Ulukoa
    '202707577',  # Arborbrook
    '061468129',  # Horizons National
    '61468129',   # Horizons (no leading zero)
    '203472700',  # Friendship Circle SD
    '464194065',  # VetsBoats
    '46-4194065', # VetsBoats (with dash)
]

ein_list = "', '".join(beta_eins)
```

---

## Step 2: Pull Org Size Metrics

```python
# Query 1: Size metrics from most recent filing
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
    nr.total_assets,
    nr.net_assets,
    nr.grants_revenue,
    nr.program_service_revenue,
    nr.contributions,
    nr.investment_income,
    ROUND(100.0 * nr.grants_revenue / NULLIF(nr.total_revenue, 0), 1) as grant_dependency_pct,
    ROUND(100.0 * nr.program_expenses / NULLIF(nr.total_expenses, 0), 1) as program_expense_ratio,
    nr.employee_count,
    nr.volunteer_count,
    nr.form_type
FROM f990_2025.nonprofit_returns nr
JOIN latest l ON nr.ein = l.ein AND nr.tax_year = l.max_year
ORDER BY nr.total_revenue DESC;
"""

size_df = pd.read_sql(size_query, conn)
print("=== ORG SIZE METRICS ===")
print(size_df.to_string())
```

---

## Step 3: Pull Foundation Grants Received

```python
# Query 2: Grant history
grants_query = f"""
SELECT 
    fg.recipient_ein as ein,
    fg.recipient_name_raw as org_name,
    COUNT(*) as num_grants,
    COUNT(DISTINCT fg.foundation_ein) as num_unique_funders,
    SUM(fg.amount) as total_grant_amount,
    ROUND(AVG(fg.amount), 0) as avg_grant_size,
    MIN(fg.amount) as min_grant,
    MAX(fg.amount) as max_grant,
    MIN(fg.tax_year) as earliest_grant_year,
    MAX(fg.tax_year) as latest_grant_year,
    COUNT(DISTINCT fg.tax_year) as years_with_grants
FROM f990_2025.fact_grants fg
WHERE fg.recipient_ein IN ('{ein_list}')
GROUP BY fg.recipient_ein, fg.recipient_name_raw
ORDER BY num_grants DESC;
"""

grants_df = pd.read_sql(grants_query, conn)
print("\n=== FOUNDATION GRANTS RECEIVED ===")
print(grants_df.to_string())
```

---

## Step 4: Pull Revenue Trend

```python
# Query 3: Revenue over multiple years
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

trend_df = pd.read_sql(trend_query, conn)

# Pivot to show years as columns
trend_pivot = trend_df.pivot(index='ein', columns='tax_year', values='total_revenue')
print("\n=== REVENUE BY YEAR ===")
print(trend_pivot.to_string())

# Calculate YoY growth
trend_df['prev_revenue'] = trend_df.groupby('ein')['total_revenue'].shift(1)
trend_df['yoy_growth'] = (trend_df['total_revenue'] - trend_df['prev_revenue']) / trend_df['prev_revenue'] * 100
print("\n=== YEAR-OVER-YEAR GROWTH ===")
print(trend_df[trend_df['yoy_growth'].notna()][['ein', 'organization_name', 'tax_year', 'total_revenue', 'yoy_growth']].to_string())
```

---

## Step 5: Summary Statistics

```python
print("\n" + "="*60)
print("SUMMARY STATISTICS (Beta Clients + VetsBoats)")
print("="*60)

# Exclude RHF from some stats if it's a major outlier
size_df_no_rhf = size_df[size_df['ein'] != '952249495']

print(f"\n--- ALL ORGS (n={len(size_df)}) ---")
print(f"Revenue:     Min ${size_df['total_revenue'].min():,.0f} | Max ${size_df['total_revenue'].max():,.0f} | Median ${size_df['total_revenue'].median():,.0f} | Mean ${size_df['total_revenue'].mean():,.0f}")
print(f"Employees:   Min {size_df['employee_count'].min()} | Max {size_df['employee_count'].max()} | Median {size_df['employee_count'].median()}")
print(f"Volunteers:  Min {size_df['volunteer_count'].min()} | Max {size_df['volunteer_count'].max()} | Median {size_df['volunteer_count'].median()}")
print(f"Grant Dep:   Min {size_df['grant_dependency_pct'].min()}% | Max {size_df['grant_dependency_pct'].max()}% | Median {size_df['grant_dependency_pct'].median()}%")

print(f"\n--- EXCLUDING RHF (n={len(size_df_no_rhf)}) ---")
print(f"Revenue:     Min ${size_df_no_rhf['total_revenue'].min():,.0f} | Max ${size_df_no_rhf['total_revenue'].max():,.0f} | Median ${size_df_no_rhf['total_revenue'].median():,.0f}")
print(f"Employees:   Min {size_df_no_rhf['employee_count'].min()} | Max {size_df_no_rhf['employee_count'].max()} | Median {size_df_no_rhf['employee_count'].median()}")

# Grant history summary
if len(grants_df) > 0:
    print(f"\n--- GRANT HISTORY ---")
    print(f"Grants received: Min {grants_df['num_grants'].min()} | Max {grants_df['num_grants'].max()} | Median {grants_df['num_grants'].median()}")
    print(f"Unique funders:  Min {grants_df['num_unique_funders'].min()} | Max {grants_df['num_unique_funders'].max()}")
    print(f"Orgs with NO foundation grants in F990: {len(size_df) - len(grants_df)}")
```

---

## Step 6: Create Comparison Table

```python
# Merge size and grants data
comparison = size_df.merge(grants_df[['ein', 'num_grants', 'num_unique_funders', 'total_grant_amount']], 
                           on='ein', how='left')
comparison['num_grants'] = comparison['num_grants'].fillna(0).astype(int)
comparison['num_unique_funders'] = comparison['num_unique_funders'].fillna(0).astype(int)

# Add labels
comparison['client_type'] = comparison['ein'].apply(lambda x: 
    'VetsBoats (Paying)' if x in ['464194065', '46-4194065'] else
    'Beta Group 2' if x in ['061468129', '61468129', '203472700'] else
    'Beta Group 1'
)

# Display key columns
display_cols = [
    'organization_name', 'client_type', 'state', 'ntee_code',
    'total_revenue', 'total_expenses', 'total_assets',
    'grant_dependency_pct', 'employee_count', 'volunteer_count',
    'num_grants', 'num_unique_funders'
]

print("\n=== COMPARISON TABLE ===")
print(comparison[display_cols].sort_values('total_revenue', ascending=False).to_string())
```

---

## Step 7: Define ICP Range

```python
print("\n" + "="*60)
print("RECOMMENDED ICP RANGE (Based on Beta + VetsBoats)")
print("="*60)

# Exclude outliers (RHF is very large)
icp_df = size_df[size_df['ein'] != '952249495']

print(f"""
REVENUE:
  Range: ${icp_df['total_revenue'].min():,.0f} - ${icp_df['total_revenue'].max():,.0f}
  Recommended target: ${icp_df['total_revenue'].quantile(0.25):,.0f} - ${icp_df['total_revenue'].quantile(0.75):,.0f}

EMPLOYEES:
  Range: {icp_df['employee_count'].min()} - {icp_df['employee_count'].max()}
  
GRANT DEPENDENCY:
  Range: {icp_df['grant_dependency_pct'].min()}% - {icp_df['grant_dependency_pct'].max()}%

SECTORS (NTEE):
  {icp_df['ntee_code'].value_counts().to_dict()}

STATES:
  {icp_df['state'].value_counts().to_dict()}

FOUNDATION GRANTS RECEIVED:
  Range: {comparison[comparison['ein'] != '952249495']['num_grants'].min()} - {comparison[comparison['ein'] != '952249495']['num_grants'].max()}
""")
```

---

## Step 8: Save Outputs

```python
# Save comparison table
comparison.to_csv('DATA_2025-12-10_beta_client_profiles.csv', index=False)

# Save summary
with open('REPORT_2025-12-10_beta_client_profile_summary.md', 'w') as f:
    f.write("# Beta Client Profile Summary\n\n")
    f.write(f"**Date:** 2025-12-10\n")
    f.write(f"**Orgs Analyzed:** {len(size_df)}\n\n")
    f.write("## Size Metrics\n\n")
    f.write(comparison[display_cols].to_markdown())
    f.write("\n\n## Recommended ICP Range\n\n")
    f.write(f"- Revenue: ${icp_df['total_revenue'].min():,.0f} - ${icp_df['total_revenue'].max():,.0f}\n")
    f.write(f"- Employees: {icp_df['employee_count'].min()} - {icp_df['employee_count'].max()}\n")
    f.write(f"- Grant Dependency: {icp_df['grant_dependency_pct'].min()}% - {icp_df['grant_dependency_pct'].max()}%\n")

print("\n=== FILES SAVED ===")
print("- DATA_2025-12-10_beta_client_profiles.csv")
print("- REPORT_2025-12-10_beta_client_profile_summary.md")
```

---

## Deliverables

- [ ] `DATA_2025-12-10_beta_client_profiles.csv` — Full comparison table
- [ ] `REPORT_2025-12-10_beta_client_profile_summary.md` — Summary with ICP recommendations
- [ ] Console output with summary stats

---

## Key Questions to Answer

1. What's the revenue range of converted orgs?
2. How many employees/volunteers do they have?
3. How grant-dependent are they?
4. How many foundation grants have they received (if any)?
5. Are they growing or shrinking?
6. What sectors (NTEE) are represented?
7. Is RHF an outlier we should exclude from ICP?

---

*Prompt: PROMPT_2025-12-10_beta_client_profiling.md*
