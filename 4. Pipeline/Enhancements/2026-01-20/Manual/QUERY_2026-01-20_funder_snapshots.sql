-- FUNDER SNAPSHOT QUERIES
-- Generated: 2026-01-20
-- Purpose: Gather funder metrics for top 5 foundation profiles

-- ============================================================================
-- QUERY 1: Basic Metrics from calc_foundation_features
-- ============================================================================

SELECT
    ein,
    name,
    total_grants_5yr,
    unique_recipients_5yr,
    total_giving_5yr,
    median_grant,
    cfp_avg_grant,
    grant_range_min,
    grant_range_max,
    in_state_grant_pct,
    repeat_rate,
    most_common_recipient_state,
    primary_sector,
    primary_sector_pct,
    giving_trend,
    trend_pct_change,
    assets
FROM f990_2025.calc_foundation_features
WHERE ein IN (
    '251721100',  -- Heinz Endowments
    '251127705',  -- Richard King Mellon
    '042768239',  -- Yawkey Foundation II
    '562305694',  -- Gilbert Foundation
    '846002373'   -- El Pomar Foundation
);

-- ============================================================================
-- QUERY 2: Annual Giving Trend (Last 5 Years)
-- ============================================================================

SELECT
    foundation_ein,
    tax_year,
    COUNT(*) as grant_count,
    SUM(amount) as total_given,
    ROUND(AVG(amount), 0) as avg_grant
FROM f990_2025.fact_grants
WHERE foundation_ein IN (
    '251721100', '251127705', '042768239', '562305694', '846002373'
)
AND tax_year >= 2020
GROUP BY foundation_ein, tax_year
ORDER BY foundation_ein, tax_year;

-- ============================================================================
-- QUERY 3: Top Sectors Funded
-- ============================================================================

SELECT
    fg.foundation_ein,
    COALESCE(LEFT(r.ntee_code, 1), 'X') as sector,
    COUNT(*) as grant_count,
    SUM(fg.amount) as total_given,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY fg.foundation_ein), 1) as pct_of_grants
FROM f990_2025.fact_grants fg
LEFT JOIN f990_2025.dim_recipients r ON fg.recipient_ein = r.ein
WHERE fg.foundation_ein IN (
    '251721100', '251127705', '042768239', '562305694', '846002373'
)
AND fg.tax_year >= 2020
GROUP BY fg.foundation_ein, COALESCE(LEFT(r.ntee_code, 1), 'X')
ORDER BY fg.foundation_ein, grant_count DESC;

-- ============================================================================
-- QUERY 4: Proof-of-Fit Grants (Youth Education Focus)
-- Keywords: youth, summer, education, student, after-school, tutoring,
--           enrichment, elementary, middle school, learning, children, academic
-- ============================================================================

SELECT
    fg.foundation_ein,
    r.name as recipient_name,
    r.state as recipient_state,
    r.ntee_code,
    fg.amount,
    fg.purpose_text,
    fg.tax_year
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_recipients r ON fg.recipient_ein = r.ein
WHERE fg.foundation_ein IN (
    '251721100', '251127705', '042768239', '562305694', '846002373'
)
AND fg.tax_year >= 2020
AND fg.amount >= 10000
AND (
    -- NTEE B (Education) or O (Youth Development) or P (Human Services)
    LEFT(r.ntee_code, 1) IN ('B', 'O', 'P')
    OR LOWER(fg.purpose_text) LIKE '%youth%'
    OR LOWER(fg.purpose_text) LIKE '%summer%'
    OR LOWER(fg.purpose_text) LIKE '%education%'
    OR LOWER(fg.purpose_text) LIKE '%student%'
    OR LOWER(fg.purpose_text) LIKE '%after-school%'
    OR LOWER(fg.purpose_text) LIKE '%afterschool%'
    OR LOWER(fg.purpose_text) LIKE '%tutoring%'
    OR LOWER(fg.purpose_text) LIKE '%enrichment%'
    OR LOWER(fg.purpose_text) LIKE '%elementary%'
    OR LOWER(fg.purpose_text) LIKE '%middle school%'
    OR LOWER(fg.purpose_text) LIKE '%learning%'
    OR LOWER(fg.purpose_text) LIKE '%children%'
    OR LOWER(fg.purpose_text) LIKE '%academic%'
)
ORDER BY fg.foundation_ein, fg.amount DESC;

-- ============================================================================
-- QUERY 5: Grants to Organizations with "Horizons" in Name
-- ============================================================================

SELECT
    fg.foundation_ein,
    r.name as recipient_name,
    r.state as recipient_state,
    fg.amount,
    fg.purpose_text,
    fg.tax_year
FROM f990_2025.fact_grants fg
JOIN f990_2025.dim_recipients r ON fg.recipient_ein = r.ein
WHERE fg.foundation_ein IN (
    '251721100', '251127705', '042768239', '562305694', '846002373'
)
AND LOWER(r.name) LIKE '%horizons%'
ORDER BY fg.foundation_ein, fg.tax_year DESC, fg.amount DESC;
