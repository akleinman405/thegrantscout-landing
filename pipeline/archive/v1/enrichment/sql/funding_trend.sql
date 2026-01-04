-- Funding Trend Query
-- Returns 3-year trend (growing, stable, declining)

WITH yearly_totals AS (
    SELECT
        tax_year,
        SUM(amount) as year_total,
        COUNT(*) as year_count
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
    GROUP BY tax_year
    ORDER BY tax_year DESC
    LIMIT 3
),
trend_calc AS (
    SELECT
        MIN(tax_year) as oldest_year,
        MAX(tax_year) as newest_year,
        (SELECT year_total FROM yearly_totals ORDER BY tax_year ASC LIMIT 1) as year_1_total,
        (SELECT year_total FROM yearly_totals ORDER BY tax_year DESC LIMIT 1) as year_3_total
    FROM yearly_totals
)
SELECT
    oldest_year,
    newest_year,
    year_1_total,
    year_3_total,
    CASE
        WHEN year_1_total > 0
        THEN ((year_3_total - year_1_total)::float / year_1_total)
        ELSE 0
    END as change_pct,
    CASE
        WHEN year_1_total = 0 THEN 'Stable'
        WHEN ((year_3_total - year_1_total)::float / year_1_total) > 0.10 THEN 'Growing'
        WHEN ((year_3_total - year_1_total)::float / year_1_total) < -0.10 THEN 'Declining'
        ELSE 'Stable'
    END as trend
FROM trend_calc;
