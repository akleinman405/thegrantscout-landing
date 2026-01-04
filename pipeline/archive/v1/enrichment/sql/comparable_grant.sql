-- Comparable Grant Query
-- Finds a grant to a similar organization for positioning

-- Priority 1: Same state AND similar NTEE
WITH same_state_same_sector AS (
    SELECT
        fg.recipient_name_raw as recipient_name,
        fg.amount as grant_amount,
        fg.purpose_text as grant_purpose,
        fg.tax_year as grant_year,
        1 as priority
    FROM f990_2025.fact_grants fg
    LEFT JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND fg.recipient_state = %(client_state)s
      AND dr.ntee_broad = %(client_ntee)s
      AND fg.amount > 0
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
),
-- Priority 2: Same state only
same_state AS (
    SELECT
        fg.recipient_name_raw as recipient_name,
        fg.amount as grant_amount,
        fg.purpose_text as grant_purpose,
        fg.tax_year as grant_year,
        2 as priority
    FROM f990_2025.fact_grants fg
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND fg.recipient_state = %(client_state)s
      AND fg.amount > 0
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
),
-- Priority 3: Similar NTEE only
same_sector AS (
    SELECT
        fg.recipient_name_raw as recipient_name,
        fg.amount as grant_amount,
        fg.purpose_text as grant_purpose,
        fg.tax_year as grant_year,
        3 as priority
    FROM f990_2025.fact_grants fg
    LEFT JOIN f990_2025.dim_recipients dr ON fg.recipient_ein = dr.ein
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND dr.ntee_broad = %(client_ntee)s
      AND fg.amount > 0
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
),
-- Priority 4: Any recent grant
any_grant AS (
    SELECT
        fg.recipient_name_raw as recipient_name,
        fg.amount as grant_amount,
        fg.purpose_text as grant_purpose,
        fg.tax_year as grant_year,
        4 as priority
    FROM f990_2025.fact_grants fg
    WHERE fg.foundation_ein = %(foundation_ein)s
      AND fg.amount > 0
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
),
-- Combine all priorities
all_options AS (
    SELECT * FROM same_state_same_sector
    UNION ALL
    SELECT * FROM same_state
    UNION ALL
    SELECT * FROM same_sector
    UNION ALL
    SELECT * FROM any_grant
)
SELECT recipient_name, grant_amount, grant_purpose, grant_year
FROM all_options
ORDER BY priority
LIMIT 1;
