-- SQL_2025-01-03_v6_training_data_fixed.sql
-- V6 Training Data: Fixed based on statistical review
--
-- FIXES from review:
-- 1. REMOVED: f_funded_new_recently (temporal leakage)
-- 2. REMOVED: f_first_time_rate (99.8% correlated with openness_score)
-- 3. REMOVED: f_one_time_rate (86% correlated with openness_score)
-- 4. CHANGED: Random 80/10/10 split instead of temporal (fixes missing negatives)
--
-- Original V6 changes (kept):
-- - REMOVED: r_total_grants, r_total_funders, r_total_funding (leakage)
-- - REMOVED: r_assets, r_employee_count (multicollinear with revenue)
-- - ADDED: r_org_age, f_is_accessible, f_is_growing, match_same_region
--
-- Prerequisites:
--   - Run PY_2025-01-02_v6_foundation_embeddings.py first (DONE)
--   - stg_v5_training_pairs must exist
--
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- ============================================================================
-- STEP 1: Verify prerequisites
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stg_v5_training_pairs') THEN
        RAISE EXCEPTION 'stg_v5_training_pairs not found. Run SQL_2025-01-02_v5_training_data_fast.sql first.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'calc_foundation_avg_embedding') THEN
        RAISE EXCEPTION 'calc_foundation_avg_embedding not found. Run PY_2025-01-02_v6_foundation_embeddings.py first.';
    END IF;
END $$;

SELECT 'Prerequisites verified' as status;

-- ============================================================================
-- STEP 2: Create region mapping for geographic proximity
-- ============================================================================

DROP TABLE IF EXISTS ref_state_regions;

CREATE TABLE ref_state_regions (
    state_code VARCHAR(2) PRIMARY KEY,
    region VARCHAR(20),
    division VARCHAR(30)
);

INSERT INTO ref_state_regions (state_code, region, division) VALUES
-- Northeast
('CT', 'Northeast', 'New England'),
('ME', 'Northeast', 'New England'),
('MA', 'Northeast', 'New England'),
('NH', 'Northeast', 'New England'),
('RI', 'Northeast', 'New England'),
('VT', 'Northeast', 'New England'),
('NJ', 'Northeast', 'Middle Atlantic'),
('NY', 'Northeast', 'Middle Atlantic'),
('PA', 'Northeast', 'Middle Atlantic'),
-- Midwest
('IL', 'Midwest', 'East North Central'),
('IN', 'Midwest', 'East North Central'),
('MI', 'Midwest', 'East North Central'),
('OH', 'Midwest', 'East North Central'),
('WI', 'Midwest', 'East North Central'),
('IA', 'Midwest', 'West North Central'),
('KS', 'Midwest', 'West North Central'),
('MN', 'Midwest', 'West North Central'),
('MO', 'Midwest', 'West North Central'),
('NE', 'Midwest', 'West North Central'),
('ND', 'Midwest', 'West North Central'),
('SD', 'Midwest', 'West North Central'),
-- South
('DE', 'South', 'South Atlantic'),
('FL', 'South', 'South Atlantic'),
('GA', 'South', 'South Atlantic'),
('MD', 'South', 'South Atlantic'),
('NC', 'South', 'South Atlantic'),
('SC', 'South', 'South Atlantic'),
('VA', 'South', 'South Atlantic'),
('DC', 'South', 'South Atlantic'),
('WV', 'South', 'South Atlantic'),
('AL', 'South', 'East South Central'),
('KY', 'South', 'East South Central'),
('MS', 'South', 'East South Central'),
('TN', 'South', 'East South Central'),
('AR', 'South', 'West South Central'),
('LA', 'South', 'West South Central'),
('OK', 'South', 'West South Central'),
('TX', 'South', 'West South Central'),
-- West
('AZ', 'West', 'Mountain'),
('CO', 'West', 'Mountain'),
('ID', 'West', 'Mountain'),
('MT', 'West', 'Mountain'),
('NV', 'West', 'Mountain'),
('NM', 'West', 'Mountain'),
('UT', 'West', 'Mountain'),
('WY', 'West', 'Mountain'),
('AK', 'West', 'Pacific'),
('CA', 'West', 'Pacific'),
('HI', 'West', 'Pacific'),
('OR', 'West', 'Pacific'),
('WA', 'West', 'Pacific');

SELECT 'Region mapping created' as status;

-- ============================================================================
-- STEP 3: Create V6 training data with cleaned features
-- NOTE: Using RANDOM split assignment instead of temporal
-- ============================================================================

DROP TABLE IF EXISTS training_data_v6;

CREATE TABLE training_data_v6 AS
SELECT
    tp.foundation_ein,
    tp.recipient_ein,
    tp.tax_year,
    tp.label,
    tp.sample_type,

    -- RANDOM SPLIT: 80% train, 10% validation, 10% test
    -- Using deterministic hash for reproducibility
    CASE
        WHEN MOD(ABS(HASHTEXT(tp.foundation_ein || tp.recipient_ein)), 100) < 80 THEN 'train'
        WHEN MOD(ABS(HASHTEXT(tp.foundation_ein || tp.recipient_ein)), 100) < 90 THEN 'validation'
        ELSE 'test'
    END as split,

    -- =======================================================================
    -- FOUNDATION FEATURES (kept from V5)
    -- =======================================================================
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

    -- Foundation accessibility (gettability)
    CASE WHEN cf.accepts_applications = TRUE
         AND COALESCE(cf.preselected_only, FALSE) = FALSE
         THEN 1 ELSE 0 END as f_is_accessible,

    -- Foundation size category (for gettability)
    CASE WHEN cf.assets < 10000000 THEN 1 ELSE 0 END as f_is_small,

    -- REMOVED: f_funded_new_recently (temporal leakage)
    -- REMOVED: f_first_time_rate (99.8% correlated with openness_score)
    -- REMOVED: f_one_time_rate (86% correlated with openness_score)

    -- Foundation giving trend (growing foundations fund new orgs 92% vs declining 81%)
    CASE WHEN cf.giving_trend = 'growing' THEN 1 ELSE 0 END as f_is_growing,
    CASE WHEN cf.giving_trend = 'declining' THEN 1 ELSE 0 END as f_is_declining,

    -- Recently active (gave grants in last 2 years of data)
    CASE WHEN cf.last_grant_year >= 2022 THEN 1 ELSE 0 END as f_is_recently_active,

    -- =======================================================================
    -- RECIPIENT FEATURES (V6: removed leaky/multicollinear features)
    -- =======================================================================

    -- KEPT: Revenue as primary size signal
    COALESCE(rf.total_revenue, 0) as r_total_revenue,

    -- REMOVED: r_assets (multicollinear with revenue, coefficient was -1.0)
    -- REMOVED: r_employee_count (multicollinear with revenue, coefficient was -0.54)
    -- REMOVED: r_total_grants (leakage, coefficient was +4.18)
    -- REMOVED: r_total_funders (leakage, coefficient was +2.90)
    -- REMOVED: r_total_funding (leakage, coefficient was +1.84)

    -- KEPT: Categorical features
    rf.state as r_state,
    rf.ntee_broad as r_ntee_broad,

    -- Organization age (years since ruling date or first return)
    COALESCE(rf.org_age_years, 10) as r_org_age,

    -- Is emerging org (less than 5 years old)
    CASE WHEN COALESCE(rf.org_age_years, 10) < 5 THEN 1 ELSE 0 END as r_is_emerging,

    -- =======================================================================
    -- MATCH FEATURES
    -- =======================================================================

    -- Geographic match
    CASE WHEN cf.state = rf.state THEN 1 ELSE 0 END as match_same_state,

    -- Sector match: foundation's % in recipient's sector
    COALESCE(sd.sector_pct / 100.0, 0) as match_sector_pct,

    -- State match: foundation's % in recipient's state
    COALESCE(std.state_pct / 100.0, 0) as match_state_pct,

    -- Grant type alignment (for capital-seeking)
    COALESCE(gt.pct_capital, 0) as match_capital_pct,

    -- Same region match
    CASE WHEN fr.region = rr.region THEN 1 ELSE 0 END as match_same_region,

    -- Same division match (more granular)
    CASE WHEN fr.division = rr.division THEN 1 ELSE 0 END as match_same_division,

    -- Has foundation embedding (for semantic similarity)
    CASE WHEN fae.foundation_ein IS NOT NULL THEN 1 ELSE 0 END as f_has_embedding

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
    ON tp.foundation_ein = sd.foundation_ein AND rf.ntee_broad = sd.ntee_broad

-- State match
LEFT JOIN stg_foundation_state_dist std
    ON tp.foundation_ein = std.foundation_ein AND rf.state = std.recipient_state

-- Region mapping for foundation
LEFT JOIN ref_state_regions fr ON cf.state = fr.state_code

-- Region mapping for recipient
LEFT JOIN ref_state_regions rr ON rf.state = rr.state_code

-- Foundation embedding (to flag if available)
LEFT JOIN calc_foundation_avg_embedding fae ON tp.foundation_ein = fae.foundation_ein

WHERE cf.ein IS NOT NULL  -- Must have foundation features
  -- V6: Filter out negative revenue (data quality)
  AND (rf.total_revenue IS NULL OR rf.total_revenue >= 0);

-- Add indexes
CREATE INDEX idx_v6td_split ON training_data_v6(split);
CREATE INDEX idx_v6td_label ON training_data_v6(label);
CREATE INDEX idx_v6td_fein ON training_data_v6(foundation_ein);
CREATE INDEX idx_v6td_rein ON training_data_v6(recipient_ein);

-- ============================================================================
-- SUMMARY: Random Split Distribution
-- ============================================================================

SELECT 'V6 Training Data Summary (Random Split)' as info;

SELECT
    split,
    label,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY split), 1) as pct_in_split
FROM training_data_v6
GROUP BY split, label
ORDER BY split, label;

SELECT 'Split Totals' as info;

SELECT
    split,
    COUNT(*) as total,
    SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) as positives,
    SUM(CASE WHEN label = 0 THEN 1 ELSE 0 END) as negatives
FROM training_data_v6
GROUP BY split
ORDER BY split;

-- Verify both classes exist in all splits
SELECT 'Class Balance Check' as info;

SELECT
    split,
    MIN(label) as min_label,
    MAX(label) as max_label,
    CASE WHEN MIN(label) = 0 AND MAX(label) = 1 THEN 'OK - both classes'
         ELSE 'ERROR - missing class!' END as status
FROM training_data_v6
GROUP BY split;

-- Data quality
SELECT 'Data Quality Checks' as info;

SELECT
    'Total rows' as metric,
    COUNT(*)::text as value
FROM training_data_v6
UNION ALL
SELECT 'With embedding', COUNT(*)::text FROM training_data_v6 WHERE f_has_embedding = 1
UNION ALL
SELECT 'NULL revenue rate',
    ROUND(100.0 * SUM(CASE WHEN r_total_revenue = 0 THEN 1 ELSE 0 END) / COUNT(*), 1)::text || '%'
FROM training_data_v6;

SELECT 'Done!' as status;
