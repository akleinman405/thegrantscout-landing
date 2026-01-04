-- Recipient Profile Query
-- Returns typical recipient budget range and sector focus

WITH recipient_budgets AS (
    SELECT DISTINCT ON (fg.recipient_ein)
        fg.recipient_ein,
        nr.total_revenue as budget,
        dr.ntee_broad as sector
    FROM f990_2025.fact_grants fg
    LEFT JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
    LEFT JOIN f990_2025.nonprofit_returns nr ON fg.recipient_ein = nr.ein
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND fg.recipient_ein IS NOT NULL
      AND nr.total_revenue IS NOT NULL
      AND nr.total_revenue > 0
    ORDER BY fg.recipient_ein, nr.tax_year DESC
),
sector_counts AS (
    SELECT
        sector,
        COUNT(*) as sector_count
    FROM recipient_budgets
    WHERE sector IS NOT NULL AND sector != ''
    GROUP BY sector
    ORDER BY sector_count DESC
    LIMIT 1
)
SELECT
    COALESCE(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY budget), 0)::bigint as typical_budget_min,
    COALESCE(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY budget), 0)::bigint as typical_budget_max,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY budget), 0)::bigint as median_budget,
    (SELECT sector FROM sector_counts) as primary_sector,
    (SELECT sector_count::float / NULLIF((SELECT COUNT(*) FROM recipient_budgets WHERE sector IS NOT NULL), 0)
     FROM sector_counts) as primary_sector_pct,
    COUNT(*) as recipients_with_budget
FROM recipient_budgets;
