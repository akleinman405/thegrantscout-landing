# PROMPT: Prospect Call List v2

**Date:** 2025-12-12

---

## Task

Generate prospect call list CSV (two-step process)

**Step 1:** Report count of prospects matching filters. STOP and wait for approval.

**Step 2:** After approval, build full CSV.

---

## Filters (prospects table)

- `sector IN ('E', 'P')`
- `employee_count BETWEEN 0 AND 3`
- `total_revenue BETWEEN 1000000 AND 2000000`
- `grant_dependency_pct >= 75`
- `num_foundation_grants <= 3`

---

## Phone Enrichment

JOIN to `nonprofit_returns` on EIN to get phone number field.

---

## Output Columns

All from `f990_2025.prospects` unless noted:

```
ein, org_name, state, city, zip, ntee_code, sector, form_type, tax_year,
total_revenue, total_expenses, total_assets, contributions_grants,
program_service_revenue, grant_dependency_pct, employee_count, volunteer_count,
num_foundation_grants, num_unique_funders, total_foundation_grant_amount,
most_recent_grant_year, revenue_band, grant_dep_band, yoy_revenue_growth,
icp_score, priority_tier, website, mission_statement,
reach_employees_1_10, reach_revenue_1m_2m, reach_form_990, reach_sector_e_p,
reach_grant_dep_75, reach_more_employees_than_volunteers, reach_all_flags,
capacity_grant_date, capacity_grant_amount, capacity_grant_funder_ein,
capacity_grant_funder_name, capacity_grant_pct_of_revenue, received_capacity_grant,
has_concrete_mission, fundraising_likelihood_score, likely_active_fundraiser,
fiscal_year_end_soon, has_biz_dev_staff, new_to_foundations, shares_funder_with_beta,
phone (from nonprofit_returns)
```

---

## Output

`DATA_2025-12-12_prospect_call_list_v2.csv`

---

## DB Connection

Per CLAUDE.md
