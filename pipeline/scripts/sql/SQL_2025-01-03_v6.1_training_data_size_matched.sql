-- SQL_2025-01-03_v6.1_training_data_size_matched.sql
-- V6.1 Training Data: Size-Matched Negative Sampling
--
-- KEY CHANGES FROM V6:
-- 1. Size-matched negatives: 0.67x-1.5x of positive's recipient revenue
-- 2. Uses actual recipient embeddings (68% coverage) instead of sector averages
-- 3. Maintains random 80/10/10 split
-- 4. Removes size as a confounding signal
--
-- AGENT REVIEW CONDITIONS ADDRESSED:
-- - Statistician: 0.67x-1.5x range (not 0.5x-2.0x)
-- - ML Engineer: Uses actual recipient embeddings
-- - Pipeline: Includes foundation embeddings for semantic similarity
--
-- Prerequisites:
--   - training_data_v6 must exist
--   - emb_nonprofit_missions must exist (68% coverage)
--   - calc_foundation_avg_embedding must exist
--
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- ============================================================================
-- STEP 1: Verify prerequisites
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'training_data_v6') THEN
        RAISE EXCEPTION 'training_data_v6 not found. Run SQL_2025-01-03_v6_training_data_fixed.sql first.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emb_nonprofit_missions') THEN
        RAISE EXCEPTION 'emb_nonprofit_missions not found.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'calc_foundation_avg_embedding') THEN
        RAISE EXCEPTION 'calc_foundation_avg_embedding not found.';
    END IF;
END $$;

SELECT 'Prerequisites verified' as status;

-- ============================================================================
-- STEP 2: Extract positives with revenue for matching
-- ============================================================================

DROP TABLE IF EXISTS stg_v61_positives;

CREATE TABLE stg_v61_positives AS
SELECT
    foundation_ein,
    recipient_ein,
    tax_year,
    r_total_revenue,
    -- Size bucket for stratified analysis
    CASE
        WHEN r_total_revenue < 100000 THEN 'tiny'
        WHEN r_total_revenue < 1000000 THEN 'small'
        WHEN r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket
FROM training_data_v6
WHERE label = 1
  AND r_total_revenue IS NOT NULL
  AND r_total_revenue > 0;

CREATE INDEX idx_v61pos_fein ON stg_v61_positives(foundation_ein);
CREATE INDEX idx_v61pos_bucket ON stg_v61_positives(size_bucket);

SELECT 'Positives extracted' as status, COUNT(*) as count FROM stg_v61_positives;

-- ============================================================================
-- STEP 3: Get all potential negative recipients with revenue
-- ============================================================================

DROP TABLE IF EXISTS stg_v61_potential_negatives;

CREATE TABLE stg_v61_potential_negatives AS
SELECT DISTINCT
    np.ein as recipient_ein,
    COALESCE(np.total_revenue, 0) as r_total_revenue,
    np.state as r_state,
    LEFT(COALESCE(np.ntee_code, 'Z'), 1) as r_ntee_broad
FROM nonprofit_returns np
WHERE np.total_revenue IS NOT NULL
  AND np.total_revenue > 0
  AND np.ein IS NOT NULL;

CREATE INDEX idx_v61neg_ein ON stg_v61_potential_negatives(recipient_ein);
CREATE INDEX idx_v61neg_rev ON stg_v61_potential_negatives(r_total_revenue);

SELECT 'Potential negatives pool' as status, COUNT(*) as count FROM stg_v61_potential_negatives;

-- ============================================================================
-- STEP 4: Create funded pairs lookup (to exclude from negatives)
-- ============================================================================

DROP TABLE IF EXISTS stg_v61_funded_pairs;

CREATE TABLE stg_v61_funded_pairs AS
SELECT DISTINCT foundation_ein, recipient_ein
FROM fact_grants
WHERE foundation_ein IS NOT NULL AND recipient_ein IS NOT NULL;

CREATE INDEX idx_v61fp ON stg_v61_funded_pairs(foundation_ein, recipient_ein);

SELECT 'Funded pairs' as status, COUNT(*) as count FROM stg_v61_funded_pairs;

-- ============================================================================
-- STEP 5: Create size-matched negatives (0.67x to 1.5x range)
-- This is the key fix - forces model to learn affinity, not size
-- ============================================================================

DROP TABLE IF EXISTS stg_v61_matched_negatives;

-- For each positive, sample ONE size-matched negative
-- Using deterministic hash for reproducibility
CREATE TABLE stg_v61_matched_negatives AS
WITH positive_with_bounds AS (
    SELECT
        p.foundation_ein,
        p.recipient_ein as positive_recipient,
        p.r_total_revenue,
        p.size_bucket,
        -- 0.67x to 1.5x range (per statistician recommendation)
        p.r_total_revenue / 1.5 as min_revenue,
        p.r_total_revenue * 1.5 as max_revenue,
        -- For sampling randomness
        ROW_NUMBER() OVER (PARTITION BY p.foundation_ein ORDER BY RANDOM()) as pos_rank
    FROM stg_v61_positives p
),
candidate_negatives AS (
    SELECT
        pb.foundation_ein,
        pb.positive_recipient,
        pb.size_bucket,
        pb.pos_rank,
        pn.recipient_ein as negative_recipient,
        pn.r_total_revenue as neg_revenue,
        pn.r_state,
        pn.r_ntee_broad,
        -- Rank candidates by hash for deterministic random selection
        ROW_NUMBER() OVER (
            PARTITION BY pb.foundation_ein, pb.positive_recipient
            ORDER BY ABS(HASHTEXT(pb.foundation_ein || pn.recipient_ein || pb.positive_recipient))
        ) as neg_rank
    FROM positive_with_bounds pb
    JOIN stg_v61_potential_negatives pn
        ON pn.r_total_revenue BETWEEN pb.min_revenue AND pb.max_revenue
    -- Exclude the positive recipient itself
    WHERE pn.recipient_ein != pb.positive_recipient
    -- Exclude already funded pairs
    AND NOT EXISTS (
        SELECT 1 FROM stg_v61_funded_pairs fp
        WHERE fp.foundation_ein = pb.foundation_ein
          AND fp.recipient_ein = pn.recipient_ein
    )
)
SELECT
    foundation_ein,
    negative_recipient as recipient_ein,
    neg_revenue as r_total_revenue,
    r_state,
    r_ntee_broad,
    size_bucket,
    0 as label  -- These are negatives
FROM candidate_negatives
WHERE neg_rank = 1;  -- Take one negative per positive

CREATE INDEX idx_v61mn_fein ON stg_v61_matched_negatives(foundation_ein);

SELECT 'Size-matched negatives created' as status, COUNT(*) as count FROM stg_v61_matched_negatives;

-- ============================================================================
-- STEP 6: Check size balance (should be ~50% positive in each bucket now)
-- ============================================================================

SELECT 'Size Balance Check (Target: ~50% each)' as info;

WITH combined AS (
    SELECT size_bucket, 1 as label FROM stg_v61_positives
    UNION ALL
    SELECT size_bucket, 0 as label FROM stg_v61_matched_negatives
)
SELECT
    size_bucket,
    SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) as positives,
    SUM(CASE WHEN label = 0 THEN 1 ELSE 0 END) as negatives,
    COUNT(*) as total,
    ROUND(100.0 * SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_positive
FROM combined
GROUP BY size_bucket
ORDER BY
    CASE size_bucket WHEN 'tiny' THEN 1 WHEN 'small' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END;

-- ============================================================================
-- STEP 7: Create V6.1 training data with all features
-- ============================================================================

DROP TABLE IF EXISTS training_data_v6_1;

CREATE TABLE training_data_v6_1 AS

-- POSITIVES (from V6, keep all features)
SELECT
    td.foundation_ein,
    td.recipient_ein,
    td.tax_year,
    td.label,
    td.sample_type,

    -- Random split (same as V6)
    CASE
        WHEN MOD(ABS(HASHTEXT(td.foundation_ein || td.recipient_ein)), 100) < 80 THEN 'train'
        WHEN MOD(ABS(HASHTEXT(td.foundation_ein || td.recipient_ein)), 100) < 90 THEN 'validation'
        ELSE 'test'
    END as split,

    -- Size bucket for stratified analysis
    CASE
        WHEN td.r_total_revenue < 100000 THEN 'tiny'
        WHEN td.r_total_revenue < 1000000 THEN 'small'
        WHEN td.r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,

    -- Foundation features (from V6)
    td.f_assets,
    td.f_total_grants,
    td.f_avg_grant,
    td.f_median_grant,
    td.f_repeat_rate,
    td.f_openness_score,
    td.f_in_state_pct,
    td.f_states_funded,
    td.f_sectors_funded,
    td.f_years_active,
    td.f_foundation_age,
    td.f_payout_rate,
    td.f_officer_count,
    td.f_has_paid_staff,
    td.f_grant_cv,
    td.f_primary_sector_pct,
    td.f_state,
    td.f_pct_capital,
    td.f_pct_operating,
    td.f_pct_program,
    td.f_sector_hhi,
    td.f_is_accessible,
    td.f_is_small,
    td.f_is_growing,
    td.f_is_declining,
    td.f_is_recently_active,

    -- Recipient features
    td.r_total_revenue,
    td.r_state,
    td.r_ntee_broad,
    td.r_org_age,
    td.r_is_emerging,

    -- Match features
    td.match_same_state,
    td.match_sector_pct,
    td.match_state_pct,
    td.match_capital_pct,
    td.match_same_region,
    td.match_same_division,
    td.f_has_embedding,

    -- NEW: Flag for recipient embedding availability
    CASE WHEN enm.ein IS NOT NULL THEN 1 ELSE 0 END as r_has_embedding

FROM training_data_v6 td
LEFT JOIN emb_nonprofit_missions enm ON td.recipient_ein = enm.ein
WHERE td.label = 1
  AND td.r_total_revenue IS NOT NULL
  AND td.r_total_revenue > 0

UNION ALL

-- NEGATIVES (size-matched)
SELECT
    mn.foundation_ein,
    mn.recipient_ein,
    NULL as tax_year,
    mn.label,
    'size_matched_negative' as sample_type,

    -- Random split
    CASE
        WHEN MOD(ABS(HASHTEXT(mn.foundation_ein || mn.recipient_ein)), 100) < 80 THEN 'train'
        WHEN MOD(ABS(HASHTEXT(mn.foundation_ein || mn.recipient_ein)), 100) < 90 THEN 'validation'
        ELSE 'test'
    END as split,

    mn.size_bucket,

    -- Foundation features (join to calc_foundation_features)
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
    COALESCE(gt.pct_capital, 0) as f_pct_capital,
    COALESCE(gt.pct_operating, 0) as f_pct_operating,
    COALESCE(gt.pct_program, 0) as f_pct_program,
    COALESCE(hhi.sector_hhi, 0.05) as f_sector_hhi,
    CASE WHEN cf.accepts_applications = TRUE AND COALESCE(cf.preselected_only, FALSE) = FALSE THEN 1 ELSE 0 END as f_is_accessible,
    CASE WHEN cf.assets < 10000000 THEN 1 ELSE 0 END as f_is_small,
    CASE WHEN cf.giving_trend = 'growing' THEN 1 ELSE 0 END as f_is_growing,
    CASE WHEN cf.giving_trend = 'declining' THEN 1 ELSE 0 END as f_is_declining,
    CASE WHEN cf.last_grant_year >= 2022 THEN 1 ELSE 0 END as f_is_recently_active,

    -- Recipient features (from potential negatives + nonprofit_returns)
    mn.r_total_revenue,
    mn.r_state,
    mn.r_ntee_broad,
    COALESCE(rf.org_age_years, 10) as r_org_age,
    CASE WHEN COALESCE(rf.org_age_years, 10) < 5 THEN 1 ELSE 0 END as r_is_emerging,

    -- Match features
    CASE WHEN cf.state = mn.r_state THEN 1 ELSE 0 END as match_same_state,
    COALESCE(sd.sector_pct / 100.0, 0) as match_sector_pct,
    COALESCE(std.state_pct / 100.0, 0) as match_state_pct,
    COALESCE(gt.pct_capital, 0) as match_capital_pct,
    CASE WHEN fr.region = rr.region THEN 1 ELSE 0 END as match_same_region,
    CASE WHEN fr.division = rr.division THEN 1 ELSE 0 END as match_same_division,
    CASE WHEN fae.foundation_ein IS NOT NULL THEN 1 ELSE 0 END as f_has_embedding,

    -- Recipient embedding flag
    CASE WHEN enm.ein IS NOT NULL THEN 1 ELSE 0 END as r_has_embedding

FROM stg_v61_matched_negatives mn
LEFT JOIN calc_foundation_features cf ON mn.foundation_ein = cf.ein
LEFT JOIN calc_foundation_grant_type_dist gt ON mn.foundation_ein = gt.foundation_ein
LEFT JOIN stg_foundation_sector_hhi hhi ON mn.foundation_ein = hhi.foundation_ein
LEFT JOIN calc_recipient_features rf ON mn.recipient_ein = rf.ein
LEFT JOIN stg_foundation_sector_dist sd ON mn.foundation_ein = sd.foundation_ein AND mn.r_ntee_broad = sd.ntee_broad
LEFT JOIN stg_foundation_state_dist std ON mn.foundation_ein = std.foundation_ein AND mn.r_state = std.recipient_state
LEFT JOIN ref_state_regions fr ON cf.state = fr.state_code
LEFT JOIN ref_state_regions rr ON mn.r_state = rr.state_code
LEFT JOIN calc_foundation_avg_embedding fae ON mn.foundation_ein = fae.foundation_ein
LEFT JOIN emb_nonprofit_missions enm ON mn.recipient_ein = enm.ein
WHERE cf.ein IS NOT NULL;  -- Must have foundation features

-- Add indexes
CREATE INDEX idx_v61td_split ON training_data_v6_1(split);
CREATE INDEX idx_v61td_label ON training_data_v6_1(label);
CREATE INDEX idx_v61td_bucket ON training_data_v6_1(size_bucket);
CREATE INDEX idx_v61td_fein ON training_data_v6_1(foundation_ein);
CREATE INDEX idx_v61td_rein ON training_data_v6_1(recipient_ein);

-- ============================================================================
-- STEP 8: Summary Statistics
-- ============================================================================

SELECT 'V6.1 Training Data Summary' as info;

SELECT
    split,
    label,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY split), 1) as pct_in_split
FROM training_data_v6_1
GROUP BY split, label
ORDER BY split, label;

SELECT 'Size Bucket Balance (Target: ~50% positive each)' as info;

SELECT
    size_bucket,
    label,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY size_bucket), 1) as pct_in_bucket
FROM training_data_v6_1
GROUP BY size_bucket, label
ORDER BY
    CASE size_bucket WHEN 'tiny' THEN 1 WHEN 'small' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
    label;

SELECT 'Embedding Coverage' as info;

SELECT
    'Foundation embeddings' as embedding_type,
    SUM(f_has_embedding) as with_embedding,
    COUNT(*) as total,
    ROUND(100.0 * SUM(f_has_embedding) / COUNT(*), 1) as pct
FROM training_data_v6_1
UNION ALL
SELECT
    'Recipient embeddings',
    SUM(r_has_embedding),
    COUNT(*),
    ROUND(100.0 * SUM(r_has_embedding) / COUNT(*), 1)
FROM training_data_v6_1;

SELECT 'Class Balance Check' as info;

SELECT
    split,
    MIN(label) as min_label,
    MAX(label) as max_label,
    CASE WHEN MIN(label) = 0 AND MAX(label) = 1 THEN 'OK - both classes'
         ELSE 'ERROR - missing class!' END as status
FROM training_data_v6_1
GROUP BY split;

-- ============================================================================
-- STEP 9: Revenue distribution comparison (should be similar now)
-- ============================================================================

SELECT 'Revenue Distribution by Label (should be similar now)' as info;

SELECT
    label,
    COUNT(*) as n,
    ROUND(AVG(r_total_revenue)::numeric, 0) as avg_revenue,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r_total_revenue)::numeric, 0) as median_revenue
FROM training_data_v6_1
GROUP BY label
ORDER BY label;

-- Cleanup staging tables
DROP TABLE IF EXISTS stg_v61_positives;
DROP TABLE IF EXISTS stg_v61_potential_negatives;
DROP TABLE IF EXISTS stg_v61_funded_pairs;
DROP TABLE IF EXISTS stg_v61_matched_negatives;

SELECT 'V6.1 Training Data Creation Complete!' as status;
