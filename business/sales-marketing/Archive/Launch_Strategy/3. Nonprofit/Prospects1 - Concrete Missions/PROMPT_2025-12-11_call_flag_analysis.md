# Claude Code CLI Prompt
## Analyze Call Outcomes vs Prospect Flags

---

## Context & Goal

**Situation:** We made ~50 cold calls to nonprofits. We want to see if our prospect flags (ICP score, concrete mission, fiscal year timing, biz dev staff, etc.) correlate with connection rates and interest.

**Goal:** Match call list to database, pull all flags, analyze which flags predict success.

**Database:** PostgreSQL, schema `f990_2025`, Windows machine, Python/psycopg2.

---

## Output Requirements

1. **All outputs in same folder as this prompt**
2. **Use naming convention:** DOCTYPE_YYYY-MM-DD_description.ext
3. **Required deliverables:**
   - REPORT_2025-12-11_call_flag_analysis.md
   - DATA_2025-12-11_call_flag_enriched.csv

---

## Input Data

The user will provide a call list with:
- Organization name (and/or EIN if available)
- Outcome: connected (yes/no), reached_decision_maker (yes/no), interested (yes/no)

If only org names provided, fuzzy match to `f990_2025.prospects.org_name`.

---

## Step 1: Match Calls to Database

```sql
-- If EIN provided, direct match
SELECT * FROM f990_2025.prospects WHERE ein = '[EIN]';

-- If name only, fuzzy match
SELECT ein, org_name, state, 
       similarity(org_name, '[ORG_NAME]') as match_score
FROM f990_2025.prospects
WHERE similarity(org_name, '[ORG_NAME]') > 0.3
ORDER BY match_score DESC
LIMIT 5;
```

Note: May need to enable pg_trgm extension for fuzzy matching:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## Step 2: Pull All Flags for Matched Orgs

```sql
SELECT 
    ein,
    org_name,
    state,
    -- ICP/Scoring
    icp_score,
    priority_tier,
    -- Size
    employee_count,
    total_revenue,
    -- Mission
    has_concrete_mission,
    -- Capacity/Intent
    received_capacity_grant,
    -- Fundraising
    fundraising_likelihood_score,
    likely_active_fundraiser,
    fiscal_year_end_soon,
    -- Staffing
    has_biz_dev_staff,
    -- Funding
    new_to_foundations,
    num_foundation_grants,
    -- Connections
    shares_funder_with_beta,
    -- Trends
    yoy_revenue_growth,
    grant_dependency_pct,
    -- Reachability
    reach_employees_1_10,
    reach_revenue_1m_2m,
    reach_sector_e_p,
    reach_grant_dep_75
FROM f990_2025.prospects
WHERE ein IN ([LIST_OF_EINS]);
```

---

## Step 3: Merge with Call Outcomes

Create combined dataset:

| ein | org_name | connected | reached_dm | interested | icp_score | has_concrete_mission | fiscal_year_end_soon | has_biz_dev_staff | ... |

---

## Step 4: Analyze Correlations

For each flag, calculate:

```python
# Connection rate by flag value
connected_rate_flag_1 = calls[calls['flag'] == 1]['connected'].mean()
connected_rate_flag_0 = calls[calls['flag'] == 0]['connected'].mean()
lift = connected_rate_flag_1 / connected_rate_flag_0

# Interest rate by flag value (for those who connected)
interest_rate_flag_1 = connected_calls[connected_calls['flag'] == 1]['interested'].mean()
```

**Metrics to calculate for each flag:**
1. Connection rate (answered phone)
2. Decision maker rate (got to right person)
3. Interest rate (showed interest)
4. Lift vs baseline (how much better is flag=1 vs flag=0?)

---

## Step 5: Output Analysis

### Table 1: Flag Impact on Connection Rate

| Flag | Flag=1 Connect% | Flag=0 Connect% | Lift | Significant? |
|------|-----------------|-----------------|------|--------------|
| fiscal_year_end_soon | X% | Y% | Z | Yes/No |
| has_biz_dev_staff=no | X% | Y% | Z | Yes/No |
| ... | | | | |

### Table 2: Flag Impact on Interest Rate (among connected)

| Flag | Flag=1 Interest% | Flag=0 Interest% | Lift |
|------|------------------|------------------|------|
| ... | | | |

### Table 3: Best Flag Combinations

| Combination | Calls | Connected | Interest | Rate |
|-------------|-------|-----------|----------|------|
| FY soon + no biz dev + small | X | Y | Z | W% |
| ... | | | | |

---

## Deliverables

### REPORT_2025-12-11_call_flag_analysis.md

1. **Match Summary** — How many calls matched to database?
2. **Overall Metrics** — Baseline connection/interest rates
3. **Flag Analysis** — Table showing each flag's impact
4. **Best Predictors** — Which flags most predict success?
5. **Recommendations** — Which flags to prioritize for future calls?
6. **Surprising Findings** — Anything unexpected?

### DATA_2025-12-11_call_flag_enriched.csv

All calls with:
- Original outcome data
- All prospect flags from database
- Match confidence score

---

## Success Criteria

- [ ] All calls matched to database (or flagged as not found)
- [ ] All flags pulled for matched orgs
- [ ] Connection rate calculated by flag
- [ ] Interest rate calculated by flag
- [ ] Top predictive flags identified
- [ ] Report and data file created

---

*Prompt: PROMPT_2025-12-11_call_flag_analysis.md*
