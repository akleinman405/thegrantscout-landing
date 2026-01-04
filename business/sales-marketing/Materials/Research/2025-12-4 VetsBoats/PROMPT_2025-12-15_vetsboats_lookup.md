# PROMPT: VetsBoats Foundation Grant History

**Date:** 2025-12-15  
**For:** Claude Code CLI  
**Schema:** f990_2025

---

## Task

Pull grant history for VetsBoats Foundation to prep for sales call with Matt Gettleman.

**VetsBoats EIN:** 463069841

## Queries Needed

```sql
-- 1. Grant summary
SELECT 
    COUNT(*) as total_grants,
    COUNT(DISTINCT foundation_ein) as unique_funders,
    SUM(amount) as total_dollars,
    ROUND(AVG(amount), 0) as avg_grant,
    MIN(tax_year) as earliest_year,
    MAX(tax_year) as latest_year
FROM f990_2025.fact_grants
WHERE recipient_ein = '463069841';

-- 2. All grants with funder names
SELECT 
    fg.tax_year,
    df.name as foundation_name,
    fg.amount,
    fg.purpose_text
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE fg.recipient_ein = '463069841'
ORDER BY fg.tax_year DESC, fg.amount DESC;

-- 3. Repeat funders
SELECT 
    df.name as foundation_name,
    COUNT(*) as grant_count,
    SUM(fg.amount) as total_given,
    MAX(fg.tax_year) as last_gift
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE fg.recipient_ein = '463069841'
GROUP BY df.name
HAVING COUNT(*) > 1
ORDER BY total_given DESC;

-- 4. Largest single grant
SELECT 
    fg.tax_year,
    df.name as foundation_name,
    fg.amount,
    fg.purpose_text
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE fg.recipient_ein = '463069841'
ORDER BY fg.amount DESC
LIMIT 1;
```

## Output

Brief summary I can reference on the call:
- Total grants / funders / dollars
- Top 5 funders by amount
- Any repeat funders
- Largest single grant details
