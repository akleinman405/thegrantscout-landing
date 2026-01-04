# Claude Code CLI Prompt
## Add Capacity Building Grant Fields to Prospects Table

**Goal:** Identify prospects who received capacity building grants and add relevant fields.

---

## Step 1: Check Available Data

```sql
-- What columns exist in pf_grants?
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'f990_2025' 
  AND table_name = 'pf_grants';

-- Sample grant purposes
SELECT purpose, COUNT(*) as cnt
FROM f990_2025.pf_grants 
WHERE purpose IS NOT NULL
GROUP BY purpose 
ORDER BY cnt DESC
LIMIT 50;

-- Check for capacity-related keywords
SELECT purpose, amount, tax_year
FROM f990_2025.pf_grants 
WHERE purpose ILIKE '%capacity%' 
   OR purpose ILIKE '%operating%'
   OR purpose ILIKE '%general support%'
   OR purpose ILIKE '%general operating%'
   OR purpose ILIKE '%organizational development%'
   OR purpose ILIKE '%infrastructure%'
LIMIT 50;
```

---

## Step 2: Add Columns to Prospects Table

```sql
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS capacity_grant_date DATE;
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS capacity_grant_amount NUMERIC;
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS capacity_grant_funder_ein VARCHAR(9);
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS capacity_grant_funder_name TEXT;
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS capacity_grant_pct_of_revenue NUMERIC;
ALTER TABLE f990_2025.prospects ADD COLUMN IF NOT EXISTS received_capacity_grant SMALLINT DEFAULT 0;
```

---

## Step 3: Identify Capacity Building Grants

Define capacity building grants as grants where purpose contains:
- "capacity"
- "general operating"
- "general support"
- "operating support"
- "organizational development"
- "infrastructure"
- "unrestricted"

```sql
-- Create temp table of capacity grants to prospects
CREATE TEMP TABLE capacity_grants AS
SELECT 
    recipient_ein,
    MAX(tax_year) as most_recent_year,
    -- Get most recent grant details
    (ARRAY_AGG(amount ORDER BY tax_year DESC))[1] as most_recent_amount,
    (ARRAY_AGG(foundation_ein ORDER BY tax_year DESC))[1] as funder_ein,
    (ARRAY_AGG(foundation_name ORDER BY tax_year DESC))[1] as funder_name,
    COUNT(*) as total_capacity_grants,
    SUM(amount) as total_capacity_amount
FROM f990_2025.pf_grants
WHERE (
    purpose ILIKE '%capacity%'
    OR purpose ILIKE '%general operating%'
    OR purpose ILIKE '%general support%'
    OR purpose ILIKE '%operating support%'
    OR purpose ILIKE '%organizational development%'
    OR purpose ILIKE '%infrastructure%'
    OR purpose ILIKE '%unrestricted%'
)
GROUP BY recipient_ein;
```

---

## Step 4: Update Prospects Table

```sql
UPDATE f990_2025.prospects p
SET 
    received_capacity_grant = 1,
    capacity_grant_date = MAKE_DATE(cg.most_recent_year, 12, 31),
    capacity_grant_amount = cg.most_recent_amount,
    capacity_grant_funder_ein = cg.funder_ein,
    capacity_grant_funder_name = cg.funder_name,
    capacity_grant_pct_of_revenue = ROUND(100.0 * cg.most_recent_amount / NULLIF(p.total_revenue, 0), 1)
FROM capacity_grants cg
WHERE p.ein = cg.recipient_ein;
```

---

## Step 5: Output Summary

```sql
-- How many prospects received capacity grants?
SELECT 
    received_capacity_grant,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM f990_2025.prospects
GROUP BY received_capacity_grant;

-- Distribution of capacity grant amounts
SELECT 
    CASE 
        WHEN capacity_grant_amount < 10000 THEN '<$10K'
        WHEN capacity_grant_amount < 25000 THEN '$10K-$25K'
        WHEN capacity_grant_amount < 50000 THEN '$25K-$50K'
        WHEN capacity_grant_amount < 100000 THEN '$50K-$100K'
        ELSE '>$100K'
    END as amount_band,
    COUNT(*) as count
FROM f990_2025.prospects
WHERE received_capacity_grant = 1
GROUP BY 1
ORDER BY 1;

-- Distribution of capacity grant as % of revenue
SELECT 
    CASE 
        WHEN capacity_grant_pct_of_revenue < 1 THEN '<1%'
        WHEN capacity_grant_pct_of_revenue < 5 THEN '1-5%'
        WHEN capacity_grant_pct_of_revenue < 10 THEN '5-10%'
        WHEN capacity_grant_pct_of_revenue < 25 THEN '10-25%'
        ELSE '>25%'
    END as pct_band,
    COUNT(*) as count
FROM f990_2025.prospects
WHERE received_capacity_grant = 1
GROUP BY 1
ORDER BY 1;

-- Top 20 prospects with recent capacity grants
SELECT 
    ein, 
    org_name, 
    state, 
    sector,
    total_revenue,
    capacity_grant_date,
    capacity_grant_amount,
    capacity_grant_pct_of_revenue,
    capacity_grant_funder_name,
    icp_score,
    reach_all_flags
FROM f990_2025.prospects
WHERE received_capacity_grant = 1
ORDER BY capacity_grant_date DESC, icp_score DESC
LIMIT 20;

-- Overlap: High ICP + reachable + capacity grant
SELECT COUNT(*) as prime_prospects
FROM f990_2025.prospects
WHERE icp_score >= 10
  AND reach_all_flags = 1
  AND received_capacity_grant = 1;
```

---

## Deliverables

- [ ] Document which keywords matched capacity grants
- [ ] Add 6 new columns to prospects table
- [ ] Update with capacity grant data
- [ ] Output summary statistics
- [ ] List top prospects with recent capacity grants

---

*Prompt: PROMPT_2025-12-10_capacity_grant_fields.md*
