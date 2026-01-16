-- Repeat Funding Rate Query
-- Returns percentage of recipients funded 2+ times

WITH recipient_counts AS (
    SELECT
        COALESCE(recipient_ein, recipient_name_raw) as recipient_id,
        COUNT(*) as grant_count
    FROM f990_2025.fact_grants
    WHERE foundation_ein = %(foundation_ein)s
      AND (recipient_ein IS NOT NULL OR recipient_name_raw IS NOT NULL)
    GROUP BY COALESCE(recipient_ein, recipient_name_raw)
)
SELECT
    COUNT(*) as unique_recipients,
    SUM(CASE WHEN grant_count >= 2 THEN 1 ELSE 0 END) as repeat_recipients,
    CASE
        WHEN COUNT(*) > 0
        THEN SUM(CASE WHEN grant_count >= 2 THEN 1 ELSE 0 END)::float / COUNT(*)
        ELSE 0
    END as repeat_rate
FROM recipient_counts;
