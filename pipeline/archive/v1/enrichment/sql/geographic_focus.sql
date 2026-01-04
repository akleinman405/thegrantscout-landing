-- Geographic Focus Query
-- Returns top recipient state and in-state percentage

WITH foundation_info AS (
    SELECT ein, state as home_state
    FROM f990_2025.dim_foundations
    WHERE ein = %(foundation_ein)s
),
state_counts AS (
    SELECT
        recipient_state,
        COUNT(*) as state_grants,
        SUM(amount) as state_total
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
      AND recipient_state IS NOT NULL
      AND recipient_state != ''
    GROUP BY recipient_state
),
totals AS (
    SELECT
        COUNT(*) as total_grants,
        SUM(amount) as total_amount
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
      AND recipient_state IS NOT NULL
      AND recipient_state != ''
)
SELECT
    f.home_state as foundation_state,
    (SELECT recipient_state FROM state_counts ORDER BY state_grants DESC LIMIT 1) as top_state,
    (SELECT state_grants FROM state_counts ORDER BY state_grants DESC LIMIT 1) as top_state_count,
    (SELECT state_grants::float / NULLIF(t.total_grants, 0) FROM state_counts ORDER BY state_grants DESC LIMIT 1) as top_state_pct,
    COALESCE((SELECT state_grants FROM state_counts WHERE recipient_state = f.home_state), 0) as in_state_count,
    COALESCE((SELECT state_grants::float FROM state_counts WHERE recipient_state = f.home_state) / NULLIF(t.total_grants, 0), 0) as in_state_pct,
    t.total_grants
FROM foundation_info f, totals t;
