-- Annual Giving Query
-- Returns total giving for most recent year with data

SELECT
    foundation_ein,
    SUM(amount) as total_giving,
    COUNT(*) as grant_count,
    tax_year
FROM f990_2025.fact_grants
WHERE foundation_ein = %(foundation_ein)s
  AND tax_year = (
      SELECT MAX(tax_year)
      FROM f990_2025.fact_grants
      WHERE foundation_ein = %(foundation_ein)s
  )
GROUP BY foundation_ein, tax_year;
