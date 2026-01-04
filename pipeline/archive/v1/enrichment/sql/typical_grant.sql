-- Typical Grant Query
-- Returns median, min, max, avg grant amounts across all years

SELECT
    foundation_ein,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_grant,
    MIN(amount) as min_grant,
    MAX(amount) as max_grant,
    AVG(amount)::numeric as avg_grant,
    COUNT(*) as total_grants
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
  AND amount > 0
GROUP BY foundation_ein;
