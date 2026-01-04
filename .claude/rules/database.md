# Database Rules - TheGrantScout

**Schema:** f990_2025
**Host:** localhost:5432

---

## Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| pf_returns | Private foundation 990-PF filings | ein, business_name, state, total_assets_eoy_amt, grants_to_organizations_ind, only_contri_to_preselected_ind |
| pf_grants | Individual grant records (raw) | filer_ein, recipient_name, recipient_state, amount, purpose, tax_year |
| fact_grants | Cleaned grant records | foundation_ein, recipient_ein, amount, purpose_text, tax_year |
| dim_foundations | Foundation dimension table | ein, name, state, ntee_code |
| dim_recipients | Recipient dimension table | ein, name, state, ntee_code |
| nonprofit_returns | 990/990-EZ filings | ein, organization_name, state, total_revenue, mission_description |
| officers | Board/officers from all forms | ein, person_nm, title_txt, compensation_amt |
| prospects | Sales prospects | ein, org_name, mission_statement, icp_score |

### Embedding Tables

| Table | Records | Purpose |
|-------|---------|---------|
| grant_embeddings | 8.3M | Semantic embeddings of grant purposes |
| prospect_embeddings | 74K | Prospect mission embeddings |
| nonprofit_mission_embeddings | 529K | Nonprofit mission embeddings |
| program_embeddings | 317K | Program description embeddings |
| client_embeddings | 7 | Client mission/project embeddings |

---

## Key Relationships

- `fact_grants.foundation_ein` → `dim_foundations.ein`
- `fact_grants.recipient_ein` → `dim_recipients.ein`
- `pf_grants.return_id` → `pf_returns.id` (CASCADE delete)
- `grant_embeddings.grant_id` → `fact_grants.id`

---

## Data Conventions

| Field Type | Format | Notes |
|------------|--------|-------|
| Amounts | NUMERIC(15,2) | Dollars with cents, NULL = not reported |
| Dates | YYYY-MM-DD | ISO 8601 |
| EINs | VARCHAR(20) | Preserve leading zeros, no dashes |
| Booleans | TRUE/FALSE/NULL | NULL = not applicable |
| Embeddings | float[384] | all-MiniLM-L6-v2 model |

---

## Critical Filter Fields

```sql
-- Foundation makes grants to organizations
grants_to_organizations_ind = TRUE

-- Foundation is open to applications (KEY!)
only_contri_to_preselected_ind = FALSE
-- Note: NULL often means open, so use:
(only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)
```

---

## Common Queries

### Find foundations accepting applications
```sql
SELECT ein, business_name, state, total_assets_eoy_amt
FROM f990_2025.pf_returns
WHERE grants_to_organizations_ind = TRUE
  AND (only_contri_to_preselected_ind = FALSE OR only_contri_to_preselected_ind IS NULL)
ORDER BY total_assets_eoy_amt DESC NULLS LAST;
```

### Get grant history for a foundation
```sql
SELECT recipient_name, recipient_state, amount, purpose_text, tax_year
FROM f990_2025.fact_grants
WHERE foundation_ein = '123456789'
ORDER BY tax_year DESC, amount DESC;
```

### Check field population rates
```sql
SELECT
    'purpose_text' as field,
    COUNT(*) as total,
    COUNT(purpose_text) as populated,
    ROUND(100.0 * COUNT(purpose_text) / COUNT(*), 1) as pct
FROM f990_2025.fact_grants;
```

### Find similar grants (with embeddings)
```sql
-- Requires pgvector extension for production use
-- Current: float[] arrays, use Python cosine similarity
SELECT ge.grant_id, fg.purpose_text, fg.amount
FROM f990_2025.grant_embeddings ge
JOIN f990_2025.fact_grants fg ON ge.grant_id = fg.id
WHERE fg.foundation_ein = '123456789'
LIMIT 100;
```

### Foundation profile with calculated metrics
```sql
SELECT *
FROM f990_2025.calc_foundation_profiles
WHERE ein = '123456789';
-- Includes: openness_score, repeat_rate, geographic_focus, sector_focus
```

---

## Table Counts (as of 2025-12-16)

| Table | Records |
|-------|---------|
| dim_foundations | 143,184 |
| fact_grants | 8,310,650 |
| grant_embeddings | 8,310,431 |
| nonprofit_returns | 2,953,274 |
| prospects | 73,836 |
| dim_recipients | 263,895 |

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Column not found: filer_ein | Wrong table | Use `foundation_ein` in fact_grants |
| UNIQUE constraint on filename | Duplicate XML | Check processed_xml_files first |
| NULL purpose text (0%) | Wrong XPath | Use `GrantOrContributionPurposeTxt` |
| Connection refused | PostgreSQL not running | Run `brew services start postgresql` |

---

*See CLAUDE.md for quick reference. See SCHEMA_SUMMARY.md for full schema documentation.*
