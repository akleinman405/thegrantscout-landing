# PROMPT_03a: Phase 3a - Funder Snapshot SQL Queries

**Date:** 2025-12-27
**Phase:** 3a
**Agent:** Dev Team
**Estimated Time:** 3-4 hours
**Depends On:** PROMPT_01 (Infrastructure) complete
**Can Parallel With:** PROMPT_02 (Scoring Function)

---

## Objective

Create SQL query templates for all 8 Funder Snapshot metrics. These queries extract foundation intelligence from the database for report generation.

---

## Context

The Funder Snapshot appears in each opportunity section of the report. It provides data-driven intelligence about foundation giving behavior.

**Reference:** See `SPEC_2025-12-01_report_section_definitions.md` for detailed metric definitions.

---

## Database Schema

**Schema:** `f990_2025`

**Key Tables:**
| Table | Description |
|-------|-------------|
| `dim_foundations` | Foundation dimension (EIN, name, state, assets) |
| `fact_grants` | Grant records (foundation_ein, recipient_ein, amount, year, purpose) |
| `dim_recipients` | Recipient dimension (EIN, name, state, NTEE) |
| `pf_returns` | 990-PF return data |

**Key Columns in `fact_grants`:**
- `foundation_ein` - Funder EIN
- `recipient_ein` - Recipient EIN (may be NULL)
- `recipient_name` - Recipient name
- `recipient_state` - Recipient state
- `grant_amount` - Grant amount
- `grant_year` - Tax year
- `grant_purpose` - Purpose text (often short)

---

## Tasks

### Task 1: Annual Giving Query

**Metric:** Total giving in most recent year

**Output Columns:**
- `total_giving` - Sum of grant amounts
- `grant_count` - Number of grants
- `tax_year` - Most recent year with data

**Query Requirements:**
- Use most recent tax year with grant data
- Sum all grants for that year
- Handle foundations with no recent grants

```sql
-- Template
SELECT 
    foundation_ein,
    SUM(grant_amount) as total_giving,
    COUNT(*) as grant_count,
    grant_year as tax_year
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
  AND grant_year = (
      SELECT MAX(grant_year) 
      FROM f990_2025.fact_grants 
      WHERE foundation_ein = %(foundation_ein)s
  )
GROUP BY foundation_ein, grant_year;
```

### Task 2: Typical Grant Query

**Metric:** Median, min, max grant amounts

**Output Columns:**
- `median_grant` - Median grant amount
- `min_grant` - Minimum grant amount
- `max_grant` - Maximum grant amount
- `avg_grant` - Average grant amount

**Query Requirements:**
- Calculate across all years (not just most recent)
- Use PERCENTILE_CONT for median
- Exclude $0 grants

```sql
-- Template
SELECT 
    foundation_ein,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY grant_amount) as median_grant,
    MIN(grant_amount) as min_grant,
    MAX(grant_amount) as max_grant,
    AVG(grant_amount) as avg_grant
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
  AND grant_amount > 0
GROUP BY foundation_ein;
```

### Task 3: Geographic Focus Query

**Metric:** Top state and in-state percentage

**Output Columns:**
- `top_state` - State with most grants
- `top_state_count` - Grants to top state
- `top_state_pct` - Percentage to top state
- `in_state_count` - Grants to foundation's home state
- `in_state_pct` - Percentage to home state
- `total_grants` - Total grants with state data

**Query Requirements:**
- Join to get foundation's home state
- Handle NULL recipient_state
- Calculate percentages

```sql
-- Template (multi-step)
-- Step 1: Get foundation state
-- Step 2: Count by recipient state
-- Step 3: Calculate top state and in-state metrics
```

### Task 4: Repeat Funding Rate Query

**Metric:** Percentage of recipients funded 2+ times

**Output Columns:**
- `unique_recipients` - Count of unique recipients
- `repeat_recipients` - Recipients with 2+ grants
- `repeat_rate` - Percentage repeat (0-1)

**Query Requirements:**
- Count unique recipient_ein (or recipient_name if EIN null)
- Count those with 2+ grants
- Handle NULL recipient identifiers

```sql
-- Template
WITH recipient_counts AS (
    SELECT 
        COALESCE(recipient_ein, recipient_name) as recipient_id,
        COUNT(*) as grant_count
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
      AND (recipient_ein IS NOT NULL OR recipient_name IS NOT NULL)
    GROUP BY COALESCE(recipient_ein, recipient_name)
)
SELECT 
    COUNT(*) as unique_recipients,
    SUM(CASE WHEN grant_count >= 2 THEN 1 ELSE 0 END) as repeat_recipients,
    SUM(CASE WHEN grant_count >= 2 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as repeat_rate
FROM recipient_counts;
```

### Task 5: Giving Style Query

**Metric:** General support vs program-specific percentage

**Output Columns:**
- `general_support_count` - Grants with general/operating keywords
- `program_specific_count` - Grants with program/project keywords
- `general_support_pct` - Percentage general support
- `classified_grants` - Total grants with purpose text

**Classification Keywords:**
- **General support:** 'general', 'operating', 'unrestricted', 'charitable', 'support'
- **Program-specific:** 'program', 'project', specific named initiatives

**Query Requirements:**
- Case-insensitive keyword matching
- Handle NULL/empty grant_purpose
- Note: 91.9% of purposes are <50 chars, so keep simple

```sql
-- Template
SELECT 
    foundation_ein,
    SUM(CASE 
        WHEN LOWER(grant_purpose) ~ '(general|operating|unrestricted)' THEN 1 
        ELSE 0 
    END) as general_support_count,
    SUM(CASE 
        WHEN LOWER(grant_purpose) ~ '(program|project|initiative)' THEN 1 
        ELSE 0 
    END) as program_specific_count,
    COUNT(CASE WHEN grant_purpose IS NOT NULL AND grant_purpose != '' THEN 1 END) as classified_grants
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
GROUP BY foundation_ein;
```

### Task 6: Recipient Profile Query

**Metric:** Typical recipient budget range and sector focus

**Output Columns:**
- `typical_budget_min` - 25th percentile recipient budget
- `typical_budget_max` - 75th percentile recipient budget
- `primary_sector` - Most common NTEE category
- `primary_sector_pct` - Percentage in primary sector

**Query Requirements:**
- Join to recipient data to get budgets
- Handle missing budget data
- Use NTEE broad category for sector

```sql
-- Template
-- This requires joining fact_grants to recipient budget data
-- May need to use nonprofit_returns table
```

### Task 7: Funding Trend Query

**Metric:** 3-year trend (growing, stable, declining)

**Output Columns:**
- `year_1_total` - Oldest year total
- `year_3_total` - Most recent year total
- `change_pct` - Percentage change
- `trend` - 'Growing' (>10%), 'Stable' (-10% to +10%), 'Declining' (<-10%)

**Query Requirements:**
- Get 3 most recent years with data
- Calculate year-over-year change
- Classify trend

```sql
-- Template
WITH yearly_totals AS (
    SELECT 
        grant_year,
        SUM(grant_amount) as year_total
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
    GROUP BY grant_year
    ORDER BY grant_year DESC
    LIMIT 3
)
-- Calculate trend from oldest to newest
```

### Task 8: Comparable Grant Query

**Metric:** Find a grant to a similar organization

**Input Parameters:**
- `foundation_ein` - The foundation
- `recipient_state` - Client's state
- `recipient_ntee` - Client's NTEE code
- `recipient_budget` - Client's budget

**Output Columns:**
- `recipient_name` - Similar org name
- `grant_amount` - Grant amount
- `grant_purpose` - Purpose text
- `grant_year` - Year

**Query Requirements:**
- Prioritize: same state > same NTEE > similar budget
- Return most recent matching grant
- Fallback to any recent grant if no good match

```sql
-- Template
-- Priority 1: Same state AND similar NTEE
-- Priority 2: Same state
-- Priority 3: Similar NTEE
-- Priority 4: Any recent grant
```

---

## Output Files

| File | Description |
|------|-------------|
| `enrichment/sql/annual_giving.sql` | Query template |
| `enrichment/sql/typical_grant.sql` | Query template |
| `enrichment/sql/geographic_focus.sql` | Query template |
| `enrichment/sql/repeat_funding.sql` | Query template |
| `enrichment/sql/giving_style.sql` | Query template |
| `enrichment/sql/recipient_profile.sql` | Query template |
| `enrichment/sql/funding_trend.sql` | Query template |
| `enrichment/sql/comparable_grant.sql` | Query template |

Create folder: `enrichment/sql/`

---

## Done Criteria

- [ ] All 8 SQL query templates created
- [ ] Each query is parameterized (uses `%(param)s` syntax)
- [ ] Each query tested against a sample foundation
- [ ] Each query returns expected columns
- [ ] No SQL syntax errors
- [ ] Queries handle NULL/missing data gracefully

---

## Verification Tests

For each query, test with a known foundation EIN:

```sql
-- Pick a foundation with lots of grants
SELECT foundation_ein, COUNT(*) 
FROM f990_2025.fact_grants 
GROUP BY foundation_ein 
ORDER BY COUNT(*) DESC 
LIMIT 5;
```

Then run each query with that EIN and verify:
1. Query executes without error
2. Returns expected columns
3. Values are reasonable (not NULL, not obviously wrong)

### Sample Verification

```python
import psycopg2

# Test annual_giving query
with open('enrichment/sql/annual_giving.sql') as f:
    query = f.read()

conn = psycopg2.connect(...)
cur = conn.cursor()
cur.execute(query, {'foundation_ein': 'TEST_EIN'})
result = cur.fetchone()
print(f"Annual giving: ${result[1]:,.0f} across {result[2]} grants in {result[3]}")
```

---

## Notes

### Parameter Style

Use psycopg2 named parameters: `%(param_name)s`

Example:
```sql
WHERE foundation_ein = %(foundation_ein)s
```

### NULL Handling

All queries should handle:
- NULL recipient_ein (common)
- NULL recipient_state (40% missing)
- NULL grant_purpose (rare but possible)
- Missing years of data

### Performance

For frequently queried foundations, consider:
- Creating indexes on `foundation_ein`
- Pre-computing metrics in a materialized view

---

## Handoff

After completion:
1. Run all queries against 3 sample foundations
2. Document any edge cases or data quality issues
3. PM reviews before proceeding to PROMPT_03b

---

*Next: PROMPT_03b (Enrichment Python Wrappers)*
