-- SQL_2025-01-02_v5_training_data.sql
-- Create V5 training dataset: first-time grants + stratified negative samples
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- ============================================================================
-- STEP 1: Create positive examples (first-time grants from accessible foundations)
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_positives;

CREATE TABLE stg_v5_positives AS
SELECT
    ftg.grant_id,
    ftg.foundation_ein,
    ftg.recipient_ein,
    ftg.tax_year,
    ftg.amount,
    1 as label,
    'positive' as sample_type
FROM stg_first_time_grants ftg
JOIN stg_accessible_foundations af ON ftg.foundation_ein = af.ein
WHERE ftg.tax_year >= 2017;  -- Exclude 2016 (sparse data)

CREATE INDEX idx_v5pos_fein ON stg_v5_positives(foundation_ein);
CREATE INDEX idx_v5pos_rein ON stg_v5_positives(recipient_ein);

-- Check count
SELECT 'Positive examples' as type, COUNT(*) as count FROM stg_v5_positives;

-- ============================================================================
-- STEP 2: Create negative examples with stratified hard mining
-- Strategy:
--   30% same-state, different sector (geographic fit, sector mismatch)
--   30% same-sector, different state (sector fit, geographic mismatch)
--   40% random accessible foundation-recipient pairs
-- ============================================================================

-- Get unique recipients from positives
DROP TABLE IF EXISTS stg_v5_recipients;
CREATE TABLE stg_v5_recipients AS
SELECT DISTINCT recipient_ein
FROM stg_v5_positives;

CREATE INDEX idx_v5rec ON stg_v5_recipients(recipient_ein);

-- Get recipient features for sampling
DROP TABLE IF EXISTS stg_v5_recipient_features;
CREATE TABLE stg_v5_recipient_features AS
SELECT
    r.recipient_ein,
    COALESCE(rf.state, fg.recipient_state) as state,
    COALESCE(rf.ntee_broad, LEFT(rf.ntee_code, 1)) as ntee_broad
FROM stg_v5_recipients r
LEFT JOIN calc_recipient_features rf ON r.recipient_ein = rf.ein
LEFT JOIN (
    SELECT DISTINCT ON (recipient_ein) recipient_ein, recipient_state
    FROM fact_grants
    WHERE recipient_ein IS NOT NULL
    ORDER BY recipient_ein, tax_year DESC
) fg ON r.recipient_ein = fg.recipient_ein;

CREATE INDEX idx_v5rf_ein ON stg_v5_recipient_features(recipient_ein);
CREATE INDEX idx_v5rf_state ON stg_v5_recipient_features(state);
CREATE INDEX idx_v5rf_ntee ON stg_v5_recipient_features(ntee_broad);

-- ============================================================================
-- STEP 2a: Same-state negatives (30%)
-- Foundations in same state as recipient, but never funded them
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_neg_same_state;

CREATE TABLE stg_v5_neg_same_state AS
WITH target_count AS (
    SELECT ROUND(COUNT(*) * 0.30) as n FROM stg_v5_positives
),
candidate_pairs AS (
    SELECT
        af.ein as foundation_ein,
        rf.recipient_ein,
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
    FROM stg_accessible_foundations af
    JOIN stg_v5_recipient_features rf ON af.state = rf.state
    WHERE NOT EXISTS (
        SELECT 1 FROM fact_grants fg
        WHERE fg.foundation_ein = af.ein
          AND fg.recipient_ein = rf.recipient_ein
    )
    -- Limit candidates for performance
    LIMIT 5000000
)
SELECT
    foundation_ein,
    recipient_ein,
    0 as label,
    'neg_same_state' as sample_type
FROM candidate_pairs
WHERE rn <= (SELECT n FROM target_count);

-- ============================================================================
-- STEP 2b: Same-sector negatives (30%)
-- Foundations funding same NTEE sector, but different state
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_neg_same_sector;

CREATE TABLE stg_v5_neg_same_sector AS
WITH target_count AS (
    SELECT ROUND(COUNT(*) * 0.30) as n FROM stg_v5_positives
),
foundation_sectors AS (
    SELECT DISTINCT foundation_ein, ntee_broad
    FROM stg_foundation_sector_dist
    WHERE sector_pct >= 10  -- At least 10% in this sector
),
candidate_pairs AS (
    SELECT
        fs.foundation_ein,
        rf.recipient_ein,
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
    FROM foundation_sectors fs
    JOIN stg_accessible_foundations af ON fs.foundation_ein = af.ein
    JOIN stg_v5_recipient_features rf ON fs.ntee_broad = rf.ntee_broad
    WHERE af.state != rf.state  -- Different state
      AND NOT EXISTS (
        SELECT 1 FROM fact_grants fg
        WHERE fg.foundation_ein = fs.foundation_ein
          AND fg.recipient_ein = rf.recipient_ein
    )
    LIMIT 5000000
)
SELECT
    foundation_ein,
    recipient_ein,
    0 as label,
    'neg_same_sector' as sample_type
FROM candidate_pairs
WHERE rn <= (SELECT n FROM target_count);

-- ============================================================================
-- STEP 2c: Random negatives (40%)
-- Random accessible foundation-recipient pairs
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_neg_random;

CREATE TABLE stg_v5_neg_random AS
WITH target_count AS (
    SELECT ROUND(COUNT(*) * 0.40) as n FROM stg_v5_positives
),
candidate_pairs AS (
    SELECT
        af.ein as foundation_ein,
        r.recipient_ein,
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
    FROM stg_accessible_foundations af
    CROSS JOIN (SELECT recipient_ein FROM stg_v5_recipients ORDER BY RANDOM() LIMIT 10000) r
    WHERE NOT EXISTS (
        SELECT 1 FROM fact_grants fg
        WHERE fg.foundation_ein = af.ein
          AND fg.recipient_ein = r.recipient_ein
    )
    LIMIT 5000000
)
SELECT
    foundation_ein,
    recipient_ein,
    0 as label,
    'neg_random' as sample_type
FROM candidate_pairs
WHERE rn <= (SELECT n FROM target_count);

-- ============================================================================
-- STEP 3: Combine positives and negatives
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_training_pairs;

CREATE TABLE stg_v5_training_pairs AS
-- Positives
SELECT foundation_ein, recipient_ein, tax_year, label, sample_type
FROM stg_v5_positives
UNION ALL
-- Same-state negatives (assign random year from training range)
SELECT foundation_ein, recipient_ein,
       2017 + FLOOR(RANDOM() * 6)::int as tax_year,  -- 2017-2022
       label, sample_type
FROM stg_v5_neg_same_state
UNION ALL
-- Same-sector negatives
SELECT foundation_ein, recipient_ein,
       2017 + FLOOR(RANDOM() * 6)::int as tax_year,
       label, sample_type
FROM stg_v5_neg_same_sector
UNION ALL
-- Random negatives
SELECT foundation_ein, recipient_ein,
       2017 + FLOOR(RANDOM() * 6)::int as tax_year,
       label, sample_type
FROM stg_v5_neg_random;

CREATE INDEX idx_v5tp_fein ON stg_v5_training_pairs(foundation_ein);
CREATE INDEX idx_v5tp_rein ON stg_v5_training_pairs(recipient_ein);
CREATE INDEX idx_v5tp_year ON stg_v5_training_pairs(tax_year);

-- Check balance
SELECT sample_type, label, COUNT(*) as count
FROM stg_v5_training_pairs
GROUP BY sample_type, label
ORDER BY label DESC, sample_type;

-- ============================================================================
-- STEP 4: Join with features to create final training data
-- ============================================================================

DROP TABLE IF EXISTS training_data_v5;

CREATE TABLE training_data_v5 AS
SELECT
    tp.foundation_ein,
    tp.recipient_ein,
    tp.tax_year,
    tp.label,
    tp.sample_type,

    -- Foundation features
    cf.assets as f_assets,
    cf.total_grants_all_time as f_total_grants,
    cf.avg_grant_amount as f_avg_grant,
    cf.median_grant as f_median_grant,
    cf.repeat_rate as f_repeat_rate,
    cf.openness_score as f_openness_score,
    cf.in_state_grant_pct as f_in_state_pct,
    cf.states_funded as f_states_funded,
    cf.sectors_funded as f_sectors_funded,
    cf.years_active as f_years_active,
    cf.foundation_age as f_foundation_age,
    cf.payout_rate as f_payout_rate,
    cf.officer_count as f_officer_count,
    CASE WHEN cf.has_paid_staff THEN 1 ELSE 0 END as f_has_paid_staff,
    cf.grant_amount_cv as f_grant_cv,
    cf.primary_sector_pct as f_primary_sector_pct,
    cf.state as f_state,

    -- Foundation grant type features
    COALESCE(gt.pct_capital, 0) as f_pct_capital,
    COALESCE(gt.pct_operating, 0) as f_pct_operating,
    COALESCE(gt.pct_program, 0) as f_pct_program,

    -- Foundation sector HHI
    COALESCE(hhi.sector_hhi, 0.05) as f_sector_hhi,

    -- Recipient features
    rf.total_revenue as r_total_revenue,
    rf.assets as r_assets,
    rf.employee_count as r_employee_count,
    rf.state as r_state,
    rf.ntee_broad as r_ntee_broad,
    rf.size_bucket as r_size_bucket,
    COALESCE(rf.total_grants, 0) as r_total_grants,
    COALESCE(rf.total_funders, 0) as r_total_funders,
    COALESCE(rf.total_funding_received, 0) as r_total_funding,

    -- Match features
    CASE WHEN cf.state = rf.state THEN 1 ELSE 0 END as match_same_state,

    -- Sector match: foundation's % in recipient's sector
    COALESCE(sd.sector_pct / 100.0, 0) as match_sector_pct,

    -- State match: foundation's % in recipient's state
    COALESCE(std.state_pct / 100.0, 0) as match_state_pct,

    -- Grant type alignment (for capital-seeking: how much capital does foundation give?)
    COALESCE(gt.pct_capital, 0) as match_capital_pct

FROM stg_v5_training_pairs tp

-- Foundation features
LEFT JOIN calc_foundation_features cf ON tp.foundation_ein = cf.ein

-- Foundation grant type
LEFT JOIN calc_foundation_grant_type_dist gt ON tp.foundation_ein = gt.foundation_ein

-- Foundation sector HHI
LEFT JOIN stg_foundation_sector_hhi hhi ON tp.foundation_ein = hhi.foundation_ein

-- Recipient features
LEFT JOIN calc_recipient_features rf ON tp.recipient_ein = rf.ein

-- Sector match
LEFT JOIN stg_foundation_sector_dist sd
    ON tp.foundation_ein = sd.foundation_ein
    AND rf.ntee_broad = sd.ntee_broad

-- State match
LEFT JOIN stg_foundation_state_dist std
    ON tp.foundation_ein = std.foundation_ein
    AND rf.state = std.recipient_state

WHERE cf.ein IS NOT NULL;  -- Must have foundation features

-- Add indexes for export
CREATE INDEX idx_v5td_year ON training_data_v5(tax_year);
CREATE INDEX idx_v5td_label ON training_data_v5(label);

-- Final summary
SELECT
    'Total training pairs' as metric,
    COUNT(*)::text as value
FROM training_data_v5
UNION ALL
SELECT 'Positives', COUNT(*)::text FROM training_data_v5 WHERE label = 1
UNION ALL
SELECT 'Negatives', COUNT(*)::text FROM training_data_v5 WHERE label = 0
UNION ALL
SELECT 'Train (2017-2022)', COUNT(*)::text FROM training_data_v5 WHERE tax_year <= 2022
UNION ALL
SELECT 'Validation (2023)', COUNT(*)::text FROM training_data_v5 WHERE tax_year = 2023
UNION ALL
SELECT 'Test (2024)', COUNT(*)::text FROM training_data_v5 WHERE tax_year = 2024;

-- ============================================================================
-- CLEANUP (optional - run after export)
-- ============================================================================
-- DROP TABLE IF EXISTS stg_v5_positives;
-- DROP TABLE IF EXISTS stg_v5_recipients;
-- DROP TABLE IF EXISTS stg_v5_recipient_features;
-- DROP TABLE IF EXISTS stg_v5_neg_same_state;
-- DROP TABLE IF EXISTS stg_v5_neg_same_sector;
-- DROP TABLE IF EXISTS stg_v5_neg_random;
-- DROP TABLE IF EXISTS stg_v5_training_pairs;
