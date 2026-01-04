-- SQL_2025-01-02_v5_training_data_fast.sql
-- FAST version: simplified negative sampling (no expensive NOT EXISTS)
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- ============================================================================
-- STEP 1: Create positive examples (reuse if exists)
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_positives CASCADE;

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
WHERE ftg.tax_year >= 2017;

CREATE INDEX idx_v5pos_fein ON stg_v5_positives(foundation_ein);
CREATE INDEX idx_v5pos_rein ON stg_v5_positives(recipient_ein);

SELECT 'Positive examples' as step, COUNT(*) as count FROM stg_v5_positives;

-- ============================================================================
-- STEP 2: Create existing pairs lookup (for fast exclusion)
-- ============================================================================

DROP TABLE IF EXISTS stg_existing_pairs;

CREATE TABLE stg_existing_pairs AS
SELECT DISTINCT foundation_ein, recipient_ein
FROM fact_grants
WHERE foundation_ein IS NOT NULL AND recipient_ein IS NOT NULL;

CREATE INDEX idx_ep_pair ON stg_existing_pairs(foundation_ein, recipient_ein);

SELECT 'Existing pairs' as step, COUNT(*) as count FROM stg_existing_pairs;

-- ============================================================================
-- STEP 3: Get recipient info for sampling
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_recipients;

CREATE TABLE stg_v5_recipients AS
SELECT DISTINCT
    p.recipient_ein,
    COALESCE(rf.state, 'XX') as state,
    COALESCE(rf.ntee_broad, 'X') as ntee_broad
FROM stg_v5_positives p
LEFT JOIN calc_recipient_features rf ON p.recipient_ein = rf.ein;

CREATE INDEX idx_v5r_ein ON stg_v5_recipients(recipient_ein);
CREATE INDEX idx_v5r_state ON stg_v5_recipients(state);
CREATE INDEX idx_v5r_ntee ON stg_v5_recipients(ntee_broad);

SELECT 'Recipients' as step, COUNT(*) as count FROM stg_v5_recipients;

-- ============================================================================
-- STEP 4: Simple negative sampling (random pairs, exclude existing)
-- Strategy: Generate 3x negatives, filter out existing pairs
-- Much faster than NOT EXISTS subquery
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_negatives;

-- Generate random foundation-recipient pairs
CREATE TABLE stg_v5_negatives AS
WITH
-- Random sample of foundations (repeated for volume)
foundations AS (
    SELECT ein, state, ROW_NUMBER() OVER (ORDER BY RANDOM()) as f_rn
    FROM stg_accessible_foundations
),
-- Random sample of recipients
recipients AS (
    SELECT recipient_ein, state, ntee_broad, ROW_NUMBER() OVER (ORDER BY RANDOM()) as r_rn
    FROM stg_v5_recipients
),
-- Create random pairs by matching on row numbers (modulo for cycling)
random_pairs AS (
    SELECT
        f.ein as foundation_ein,
        r.recipient_ein,
        f.state as f_state,
        r.state as r_state,
        r.ntee_broad
    FROM foundations f
    CROSS JOIN LATERAL (
        -- Pick 40 random recipients per foundation
        SELECT * FROM recipients ORDER BY RANDOM() LIMIT 40
    ) r
    LIMIT 3000000  -- Generate 3M candidates
),
-- Exclude existing pairs
filtered AS (
    SELECT rp.*
    FROM random_pairs rp
    LEFT JOIN stg_existing_pairs ep
        ON rp.foundation_ein = ep.foundation_ein
        AND rp.recipient_ein = ep.recipient_ein
    WHERE ep.foundation_ein IS NULL  -- Not an existing pair
)
-- Take 750K negatives (1:1 with positives)
SELECT
    foundation_ein,
    recipient_ein,
    0 as label,
    CASE
        WHEN f_state = r_state THEN 'neg_same_state'
        ELSE 'neg_random'
    END as sample_type
FROM filtered
ORDER BY RANDOM()
LIMIT 750000;

CREATE INDEX idx_v5neg_fein ON stg_v5_negatives(foundation_ein);
CREATE INDEX idx_v5neg_rein ON stg_v5_negatives(recipient_ein);

SELECT 'Negatives' as step, COUNT(*) as count FROM stg_v5_negatives;
SELECT sample_type, COUNT(*) FROM stg_v5_negatives GROUP BY sample_type;

-- ============================================================================
-- STEP 5: Combine positives and negatives
-- ============================================================================

DROP TABLE IF EXISTS stg_v5_training_pairs;

CREATE TABLE stg_v5_training_pairs AS
-- Positives (with their actual tax year)
SELECT foundation_ein, recipient_ein, tax_year, label, sample_type
FROM stg_v5_positives
UNION ALL
-- Negatives (assign random tax year)
SELECT
    foundation_ein,
    recipient_ein,
    2017 + (RANDOM() * 5)::int as tax_year,
    label,
    sample_type
FROM stg_v5_negatives;

CREATE INDEX idx_v5tp_fein ON stg_v5_training_pairs(foundation_ein);
CREATE INDEX idx_v5tp_rein ON stg_v5_training_pairs(recipient_ein);
CREATE INDEX idx_v5tp_year ON stg_v5_training_pairs(tax_year);

SELECT 'Training pairs' as step, sample_type, label, COUNT(*) as count
FROM stg_v5_training_pairs
GROUP BY sample_type, label
ORDER BY label DESC, sample_type;

-- ============================================================================
-- STEP 6: Join with features
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
    COALESCE(sd.sector_pct / 100.0, 0) as match_sector_pct,
    COALESCE(std.state_pct / 100.0, 0) as match_state_pct,
    COALESCE(gt.pct_capital, 0) as match_capital_pct

FROM stg_v5_training_pairs tp
LEFT JOIN calc_foundation_features cf ON tp.foundation_ein = cf.ein
LEFT JOIN calc_foundation_grant_type_dist gt ON tp.foundation_ein = gt.foundation_ein
LEFT JOIN stg_foundation_sector_hhi hhi ON tp.foundation_ein = hhi.foundation_ein
LEFT JOIN calc_recipient_features rf ON tp.recipient_ein = rf.ein
LEFT JOIN stg_foundation_sector_dist sd
    ON tp.foundation_ein = sd.foundation_ein AND rf.ntee_broad = sd.ntee_broad
LEFT JOIN stg_foundation_state_dist std
    ON tp.foundation_ein = std.foundation_ein AND rf.state = std.recipient_state
WHERE cf.ein IS NOT NULL;

CREATE INDEX idx_v5td_year ON training_data_v5(tax_year);
CREATE INDEX idx_v5td_label ON training_data_v5(label);

-- ============================================================================
-- FINAL SUMMARY
-- ============================================================================

SELECT 'FINAL SUMMARY' as info;
SELECT 'Total rows' as metric, COUNT(*)::text as value FROM training_data_v5
UNION ALL SELECT 'Positives', COUNT(*)::text FROM training_data_v5 WHERE label = 1
UNION ALL SELECT 'Negatives', COUNT(*)::text FROM training_data_v5 WHERE label = 0
UNION ALL SELECT 'Train (<=2022)', COUNT(*)::text FROM training_data_v5 WHERE tax_year <= 2022
UNION ALL SELECT 'Val (2023)', COUNT(*)::text FROM training_data_v5 WHERE tax_year = 2023
UNION ALL SELECT 'Test (2024)', COUNT(*)::text FROM training_data_v5 WHERE tax_year = 2024;

-- ============================================================================
-- CLEANUP staging tables
-- ============================================================================
DROP TABLE IF EXISTS stg_existing_pairs;
DROP TABLE IF EXISTS stg_v5_recipients;
DROP TABLE IF EXISTS stg_v5_negatives;

SELECT 'Done!' as status;
