-- SQL_2025-01-03_v6.1_training_data_optimized.sql
-- V6.1 Training Data: OPTIMIZED Size-Matched Negative Sampling
--
-- OPTIMIZATION: Uses revenue deciles instead of BETWEEN join
-- This reduces query time from hours to minutes
--
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

\echo 'Step 1: Verifying prerequisites...'

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'training_data_v6') THEN
        RAISE EXCEPTION 'training_data_v6 not found.';
    END IF;
END $$;

-- ============================================================================
-- STEP 2: Create revenue decile buckets for efficient matching
-- ============================================================================

\echo 'Step 2: Creating revenue decile buckets...'

DROP TABLE IF EXISTS stg_v61_revenue_deciles;

CREATE TABLE stg_v61_revenue_deciles AS
SELECT
    ein,
    total_revenue,
    state,
    LEFT(COALESCE(ntee_code, 'Z'), 1) as ntee_broad,
    NTILE(100) OVER (ORDER BY total_revenue) as revenue_percentile
FROM nonprofit_returns
WHERE total_revenue IS NOT NULL
  AND total_revenue > 0
  AND ein IS NOT NULL;

CREATE INDEX idx_v61rd_pct ON stg_v61_revenue_deciles(revenue_percentile);
CREATE INDEX idx_v61rd_ein ON stg_v61_revenue_deciles(ein);

\echo 'Step 2 complete: Revenue deciles created'
SELECT COUNT(*) as nonprofit_count FROM stg_v61_revenue_deciles;

-- ============================================================================
-- STEP 3: Add percentile to positives
-- ============================================================================

\echo 'Step 3: Extracting positives with percentiles...'

DROP TABLE IF EXISTS stg_v61_positives;

CREATE TABLE stg_v61_positives AS
SELECT
    td.foundation_ein,
    td.recipient_ein,
    td.tax_year,
    td.r_total_revenue,
    rd.revenue_percentile,
    CASE
        WHEN td.r_total_revenue < 100000 THEN 'tiny'
        WHEN td.r_total_revenue < 1000000 THEN 'small'
        WHEN td.r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket
FROM training_data_v6 td
JOIN stg_v61_revenue_deciles rd ON td.recipient_ein = rd.ein
WHERE td.label = 1
  AND td.r_total_revenue IS NOT NULL
  AND td.r_total_revenue > 0;

CREATE INDEX idx_v61pos_pct ON stg_v61_positives(revenue_percentile);
CREATE INDEX idx_v61pos_fein ON stg_v61_positives(foundation_ein);

\echo 'Step 3 complete: Positives extracted'
SELECT COUNT(*) as positive_count FROM stg_v61_positives;

-- ============================================================================
-- STEP 4: Create funded pairs lookup
-- ============================================================================

\echo 'Step 4: Creating funded pairs lookup...'

DROP TABLE IF EXISTS stg_v61_funded_pairs;

CREATE TABLE stg_v61_funded_pairs AS
SELECT DISTINCT foundation_ein, recipient_ein
FROM fact_grants
WHERE foundation_ein IS NOT NULL AND recipient_ein IS NOT NULL;

CREATE INDEX idx_v61fp ON stg_v61_funded_pairs(foundation_ein, recipient_ein);

\echo 'Step 4 complete: Funded pairs indexed'

-- ============================================================================
-- STEP 5: OPTIMIZED size-matched negatives using percentile matching
-- Match within ±10 percentile points (roughly 0.5x-2x revenue range)
-- ============================================================================

\echo 'Step 5: Creating size-matched negatives (OPTIMIZED - ~5-10 min)...'

DROP TABLE IF EXISTS stg_v61_matched_negatives;

-- Sample one negative per positive from same percentile range
CREATE TABLE stg_v61_matched_negatives AS
WITH numbered_positives AS (
    SELECT
        foundation_ein,
        recipient_ein as positive_recipient,
        revenue_percentile,
        size_bucket,
        ROW_NUMBER() OVER (ORDER BY foundation_ein, recipient_ein) as pos_id
    FROM stg_v61_positives
),
-- For each percentile, get pool of potential negatives
percentile_pools AS (
    SELECT
        revenue_percentile,
        ein as recipient_ein,
        total_revenue,
        state,
        ntee_broad
    FROM stg_v61_revenue_deciles
),
-- Match positives to negatives in same percentile (±5 points for tighter matching)
matched AS (
    SELECT
        np.foundation_ein,
        np.positive_recipient,
        np.size_bucket,
        np.pos_id,
        pp.recipient_ein as negative_recipient,
        pp.total_revenue as neg_revenue,
        pp.state as r_state,
        pp.ntee_broad as r_ntee_broad,
        -- Deterministic random selection using hash
        ROW_NUMBER() OVER (
            PARTITION BY np.pos_id
            ORDER BY ABS(HASHTEXT(np.foundation_ein || pp.recipient_ein))
        ) as neg_rank
    FROM numbered_positives np
    JOIN percentile_pools pp
        ON pp.revenue_percentile BETWEEN np.revenue_percentile - 5 AND np.revenue_percentile + 5
    WHERE pp.recipient_ein != np.positive_recipient
    -- Exclude already funded pairs
    AND NOT EXISTS (
        SELECT 1 FROM stg_v61_funded_pairs fp
        WHERE fp.foundation_ein = np.foundation_ein
          AND fp.recipient_ein = pp.recipient_ein
    )
)
SELECT
    foundation_ein,
    negative_recipient as recipient_ein,
    neg_revenue as r_total_revenue,
    r_state,
    r_ntee_broad,
    size_bucket,
    0 as label
FROM matched
WHERE neg_rank = 1;

CREATE INDEX idx_v61mn_fein ON stg_v61_matched_negatives(foundation_ein);
CREATE INDEX idx_v61mn_bucket ON stg_v61_matched_negatives(size_bucket);

\echo 'Step 5 complete: Size-matched negatives created'
SELECT COUNT(*) as negative_count FROM stg_v61_matched_negatives;

-- ============================================================================
-- STEP 6: Check size balance
-- ============================================================================

\echo 'Step 6: Checking size balance...'

SELECT
    size_bucket,
    SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) as positives,
    SUM(CASE WHEN label = 0 THEN 1 ELSE 0 END) as negatives,
    ROUND(100.0 * SUM(CASE WHEN label = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_positive
FROM (
    SELECT size_bucket, 1 as label FROM stg_v61_positives
    UNION ALL
    SELECT size_bucket, 0 as label FROM stg_v61_matched_negatives
) combined
GROUP BY size_bucket
ORDER BY
    CASE size_bucket WHEN 'tiny' THEN 1 WHEN 'small' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END;

-- ============================================================================
-- STEP 7: Create final V6.1 training data
-- ============================================================================

\echo 'Step 7: Creating final training_data_v6_1 table (~5 min)...'

DROP TABLE IF EXISTS training_data_v6_1;

CREATE TABLE training_data_v6_1 AS

-- POSITIVES
SELECT
    td.foundation_ein,
    td.recipient_ein,
    td.tax_year,
    td.label,
    td.sample_type,
    CASE
        WHEN MOD(ABS(HASHTEXT(td.foundation_ein || td.recipient_ein)), 100) < 80 THEN 'train'
        WHEN MOD(ABS(HASHTEXT(td.foundation_ein || td.recipient_ein)), 100) < 90 THEN 'validation'
        ELSE 'test'
    END as split,
    CASE
        WHEN td.r_total_revenue < 100000 THEN 'tiny'
        WHEN td.r_total_revenue < 1000000 THEN 'small'
        WHEN td.r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    td.f_assets, td.f_total_grants, td.f_avg_grant, td.f_median_grant,
    td.f_repeat_rate, td.f_openness_score, td.f_in_state_pct, td.f_states_funded,
    td.f_sectors_funded, td.f_years_active, td.f_foundation_age, td.f_payout_rate,
    td.f_officer_count, td.f_has_paid_staff, td.f_grant_cv, td.f_primary_sector_pct,
    td.f_state, td.f_pct_capital, td.f_pct_operating, td.f_pct_program,
    td.f_sector_hhi, td.f_is_accessible, td.f_is_small, td.f_is_growing,
    td.f_is_declining, td.f_is_recently_active,
    td.r_total_revenue, td.r_state, td.r_ntee_broad, td.r_org_age, td.r_is_emerging,
    td.match_same_state, td.match_sector_pct, td.match_state_pct, td.match_capital_pct,
    td.match_same_region, td.match_same_division, td.f_has_embedding,
    CASE WHEN enm.ein IS NOT NULL THEN 1 ELSE 0 END as r_has_embedding
FROM training_data_v6 td
LEFT JOIN emb_nonprofit_missions enm ON td.recipient_ein = enm.ein
WHERE td.label = 1
  AND td.r_total_revenue IS NOT NULL AND td.r_total_revenue > 0

UNION ALL

-- NEGATIVES
SELECT
    mn.foundation_ein,
    mn.recipient_ein,
    NULL as tax_year,
    mn.label,
    'size_matched_negative' as sample_type,
    CASE
        WHEN MOD(ABS(HASHTEXT(mn.foundation_ein || mn.recipient_ein)), 100) < 80 THEN 'train'
        WHEN MOD(ABS(HASHTEXT(mn.foundation_ein || mn.recipient_ein)), 100) < 90 THEN 'validation'
        ELSE 'test'
    END as split,
    mn.size_bucket,
    cf.assets, cf.total_grants_all_time, cf.avg_grant_amount, cf.median_grant,
    cf.repeat_rate, cf.openness_score, cf.in_state_grant_pct, cf.states_funded,
    cf.sectors_funded, cf.years_active, cf.foundation_age, cf.payout_rate,
    cf.officer_count, CASE WHEN cf.has_paid_staff THEN 1 ELSE 0 END, cf.grant_amount_cv, cf.primary_sector_pct,
    cf.state, COALESCE(gt.pct_capital, 0), COALESCE(gt.pct_operating, 0), COALESCE(gt.pct_program, 0),
    COALESCE(hhi.sector_hhi, 0.05),
    CASE WHEN cf.accepts_applications = TRUE AND COALESCE(cf.preselected_only, FALSE) = FALSE THEN 1 ELSE 0 END,
    CASE WHEN cf.assets < 10000000 THEN 1 ELSE 0 END,
    CASE WHEN cf.giving_trend = 'growing' THEN 1 ELSE 0 END,
    CASE WHEN cf.giving_trend = 'declining' THEN 1 ELSE 0 END,
    CASE WHEN cf.last_grant_year >= 2022 THEN 1 ELSE 0 END,
    mn.r_total_revenue, mn.r_state, mn.r_ntee_broad,
    COALESCE(rf.org_age_years, 10),
    CASE WHEN COALESCE(rf.org_age_years, 10) < 5 THEN 1 ELSE 0 END,
    CASE WHEN cf.state = mn.r_state THEN 1 ELSE 0 END,
    COALESCE(sd.sector_pct / 100.0, 0),
    COALESCE(std.state_pct / 100.0, 0),
    COALESCE(gt.pct_capital, 0),
    CASE WHEN fr.region = rr.region THEN 1 ELSE 0 END,
    CASE WHEN fr.division = rr.division THEN 1 ELSE 0 END,
    CASE WHEN fae.foundation_ein IS NOT NULL THEN 1 ELSE 0 END,
    CASE WHEN enm.ein IS NOT NULL THEN 1 ELSE 0 END
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
WHERE cf.ein IS NOT NULL;

CREATE INDEX idx_v61td_split ON training_data_v6_1(split);
CREATE INDEX idx_v61td_label ON training_data_v6_1(label);
CREATE INDEX idx_v61td_bucket ON training_data_v6_1(size_bucket);

\echo 'Step 7 complete: Final table created'

-- ============================================================================
-- STEP 8: Summary
-- ============================================================================

\echo '============================================================'
\echo 'V6.1 TRAINING DATA SUMMARY'
\echo '============================================================'

SELECT 'Total Rows' as metric, COUNT(*)::text as value FROM training_data_v6_1
UNION ALL
SELECT 'Positives', COUNT(*)::text FROM training_data_v6_1 WHERE label = 1
UNION ALL
SELECT 'Negatives', COUNT(*)::text FROM training_data_v6_1 WHERE label = 0;

\echo ''
\echo 'Split Distribution:'
SELECT split, label, COUNT(*) as count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY split), 1) as pct
FROM training_data_v6_1
GROUP BY split, label
ORDER BY split, label;

\echo ''
\echo 'Size Bucket Balance (Target: ~50% each):'
SELECT size_bucket, label, COUNT(*) as count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY size_bucket), 1) as pct
FROM training_data_v6_1
GROUP BY size_bucket, label
ORDER BY CASE size_bucket WHEN 'tiny' THEN 1 WHEN 'small' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, label;

\echo ''
\echo 'Revenue Distribution (should be similar for pos/neg now):'
SELECT label,
       ROUND(AVG(r_total_revenue)::numeric, 0) as avg_revenue,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r_total_revenue)::numeric, 0) as median_revenue
FROM training_data_v6_1
GROUP BY label;

\echo ''
\echo 'Embedding Coverage:'
SELECT
    ROUND(100.0 * SUM(f_has_embedding) / COUNT(*), 1) as foundation_emb_pct,
    ROUND(100.0 * SUM(r_has_embedding) / COUNT(*), 1) as recipient_emb_pct
FROM training_data_v6_1;

-- Cleanup
DROP TABLE IF EXISTS stg_v61_revenue_deciles;
DROP TABLE IF EXISTS stg_v61_positives;
DROP TABLE IF EXISTS stg_v61_funded_pairs;
DROP TABLE IF EXISTS stg_v61_matched_negatives;

\echo ''
\echo 'V6.1 Training Data Creation Complete!'
\echo 'Next: Run PY_2025-01-03_v6.1_export_training.py'
