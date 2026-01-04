-- SQL_2025-01-03_v6.1_training_data_bucket.sql
-- V6.1 Training Data: BUCKET-BASED Size-Matched Negative Sampling
--
-- APPROACH: Use 4 size buckets instead of percentiles to reduce memory
-- This samples negatives within the same size bucket as each positive
-- Much more memory-efficient than percentile cross-join
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
-- STEP 2: Create nonprofit size buckets
-- ============================================================================

\echo 'Step 2: Creating nonprofit size buckets...'

DROP TABLE IF EXISTS stg_v61_nonprofit_buckets;

CREATE TABLE stg_v61_nonprofit_buckets AS
SELECT
    ein,
    total_revenue,
    state,
    LEFT(COALESCE(ntee_code, 'Z'), 1) as ntee_broad,
    CASE
        WHEN total_revenue < 100000 THEN 'tiny'
        WHEN total_revenue < 1000000 THEN 'small'
        WHEN total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    -- Random sort within bucket for sampling
    HASHTEXT(ein) as hash_val
FROM nonprofit_returns
WHERE total_revenue IS NOT NULL
  AND total_revenue > 0
  AND ein IS NOT NULL;

CREATE INDEX idx_v61nb_bucket ON stg_v61_nonprofit_buckets(size_bucket);
CREATE INDEX idx_v61nb_ein ON stg_v61_nonprofit_buckets(ein);

\echo 'Step 2 complete'
SELECT size_bucket, COUNT(*) as count FROM stg_v61_nonprofit_buckets GROUP BY size_bucket ORDER BY 1;

-- ============================================================================
-- STEP 3: Extract positives with bucket
-- ============================================================================

\echo 'Step 3: Extracting positives with size buckets...'

DROP TABLE IF EXISTS stg_v61_positives;

CREATE TABLE stg_v61_positives AS
SELECT
    td.foundation_ein,
    td.recipient_ein,
    td.tax_year,
    td.r_total_revenue,
    CASE
        WHEN td.r_total_revenue < 100000 THEN 'tiny'
        WHEN td.r_total_revenue < 1000000 THEN 'small'
        WHEN td.r_total_revenue < 10000000 THEN 'medium'
        ELSE 'large'
    END as size_bucket,
    ROW_NUMBER() OVER (ORDER BY HASHTEXT(td.foundation_ein || td.recipient_ein)) as pos_id
FROM training_data_v6 td
WHERE td.label = 1
  AND td.r_total_revenue IS NOT NULL
  AND td.r_total_revenue > 0;

CREATE INDEX idx_v61pos_bucket ON stg_v61_positives(size_bucket);
CREATE INDEX idx_v61pos_id ON stg_v61_positives(pos_id);

\echo 'Step 3 complete'
SELECT size_bucket, COUNT(*) as positive_count FROM stg_v61_positives GROUP BY size_bucket ORDER BY 1;

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

\echo 'Step 4 complete'
SELECT COUNT(*) as funded_pairs FROM stg_v61_funded_pairs;

-- ============================================================================
-- STEP 5: Sample negatives per bucket (memory efficient - one bucket at a time)
-- ============================================================================

\echo 'Step 5: Creating size-matched negatives (bucket by bucket)...'

DROP TABLE IF EXISTS stg_v61_matched_negatives;

CREATE TABLE stg_v61_matched_negatives (
    foundation_ein VARCHAR(20),
    recipient_ein VARCHAR(20),
    r_total_revenue NUMERIC,
    r_state VARCHAR(10),
    r_ntee_broad VARCHAR(10),
    size_bucket VARCHAR(10),
    label INTEGER DEFAULT 0
);

-- Process TINY bucket
\echo '  Processing TINY bucket...'
INSERT INTO stg_v61_matched_negatives
WITH pos_tiny AS (
    SELECT foundation_ein, recipient_ein, pos_id
    FROM stg_v61_positives
    WHERE size_bucket = 'tiny'
),
neg_pool_tiny AS (
    SELECT ein, total_revenue, state, ntee_broad, hash_val
    FROM stg_v61_nonprofit_buckets
    WHERE size_bucket = 'tiny'
),
matched AS (
    SELECT
        p.foundation_ein,
        p.recipient_ein as positive_recipient,
        p.pos_id,
        n.ein as negative_recipient,
        n.total_revenue,
        n.state,
        n.ntee_broad,
        ROW_NUMBER() OVER (PARTITION BY p.pos_id ORDER BY ABS(HASHTEXT(p.foundation_ein || n.ein) - p.pos_id)) as rn
    FROM pos_tiny p
    CROSS JOIN LATERAL (
        SELECT ein, total_revenue, state, ntee_broad
        FROM neg_pool_tiny
        WHERE ein != p.recipient_ein
          AND NOT EXISTS (
              SELECT 1 FROM stg_v61_funded_pairs fp
              WHERE fp.foundation_ein = p.foundation_ein AND fp.recipient_ein = neg_pool_tiny.ein
          )
        ORDER BY ABS(HASHTEXT(p.foundation_ein || ein) - p.pos_id)
        LIMIT 10  -- Sample pool
    ) n
)
SELECT foundation_ein, negative_recipient, total_revenue, state, ntee_broad, 'tiny', 0
FROM matched WHERE rn = 1;

SELECT 'TINY done', COUNT(*) FROM stg_v61_matched_negatives WHERE size_bucket = 'tiny';

-- Process SMALL bucket
\echo '  Processing SMALL bucket...'
INSERT INTO stg_v61_matched_negatives
WITH pos_small AS (
    SELECT foundation_ein, recipient_ein, pos_id
    FROM stg_v61_positives
    WHERE size_bucket = 'small'
),
neg_pool_small AS (
    SELECT ein, total_revenue, state, ntee_broad, hash_val
    FROM stg_v61_nonprofit_buckets
    WHERE size_bucket = 'small'
),
matched AS (
    SELECT
        p.foundation_ein,
        p.pos_id,
        n.ein as negative_recipient,
        n.total_revenue,
        n.state,
        n.ntee_broad,
        ROW_NUMBER() OVER (PARTITION BY p.pos_id ORDER BY ABS(HASHTEXT(p.foundation_ein || n.ein) - p.pos_id)) as rn
    FROM pos_small p
    CROSS JOIN LATERAL (
        SELECT ein, total_revenue, state, ntee_broad
        FROM neg_pool_small
        WHERE ein != p.recipient_ein
          AND NOT EXISTS (
              SELECT 1 FROM stg_v61_funded_pairs fp
              WHERE fp.foundation_ein = p.foundation_ein AND fp.recipient_ein = neg_pool_small.ein
          )
        ORDER BY ABS(HASHTEXT(p.foundation_ein || ein) - p.pos_id)
        LIMIT 10
    ) n
)
SELECT foundation_ein, negative_recipient, total_revenue, state, ntee_broad, 'small', 0
FROM matched WHERE rn = 1;

SELECT 'SMALL done', COUNT(*) FROM stg_v61_matched_negatives WHERE size_bucket = 'small';

-- Process MEDIUM bucket
\echo '  Processing MEDIUM bucket...'
INSERT INTO stg_v61_matched_negatives
WITH pos_medium AS (
    SELECT foundation_ein, recipient_ein, pos_id
    FROM stg_v61_positives
    WHERE size_bucket = 'medium'
),
neg_pool_medium AS (
    SELECT ein, total_revenue, state, ntee_broad, hash_val
    FROM stg_v61_nonprofit_buckets
    WHERE size_bucket = 'medium'
),
matched AS (
    SELECT
        p.foundation_ein,
        p.pos_id,
        n.ein as negative_recipient,
        n.total_revenue,
        n.state,
        n.ntee_broad,
        ROW_NUMBER() OVER (PARTITION BY p.pos_id ORDER BY ABS(HASHTEXT(p.foundation_ein || n.ein) - p.pos_id)) as rn
    FROM pos_medium p
    CROSS JOIN LATERAL (
        SELECT ein, total_revenue, state, ntee_broad
        FROM neg_pool_medium
        WHERE ein != p.recipient_ein
          AND NOT EXISTS (
              SELECT 1 FROM stg_v61_funded_pairs fp
              WHERE fp.foundation_ein = p.foundation_ein AND fp.recipient_ein = neg_pool_medium.ein
          )
        ORDER BY ABS(HASHTEXT(p.foundation_ein || ein) - p.pos_id)
        LIMIT 10
    ) n
)
SELECT foundation_ein, negative_recipient, total_revenue, state, ntee_broad, 'medium', 0
FROM matched WHERE rn = 1;

SELECT 'MEDIUM done', COUNT(*) FROM stg_v61_matched_negatives WHERE size_bucket = 'medium';

-- Process LARGE bucket
\echo '  Processing LARGE bucket...'
INSERT INTO stg_v61_matched_negatives
WITH pos_large AS (
    SELECT foundation_ein, recipient_ein, pos_id
    FROM stg_v61_positives
    WHERE size_bucket = 'large'
),
neg_pool_large AS (
    SELECT ein, total_revenue, state, ntee_broad, hash_val
    FROM stg_v61_nonprofit_buckets
    WHERE size_bucket = 'large'
),
matched AS (
    SELECT
        p.foundation_ein,
        p.pos_id,
        n.ein as negative_recipient,
        n.total_revenue,
        n.state,
        n.ntee_broad,
        ROW_NUMBER() OVER (PARTITION BY p.pos_id ORDER BY ABS(HASHTEXT(p.foundation_ein || n.ein) - p.pos_id)) as rn
    FROM pos_large p
    CROSS JOIN LATERAL (
        SELECT ein, total_revenue, state, ntee_broad
        FROM neg_pool_large
        WHERE ein != p.recipient_ein
          AND NOT EXISTS (
              SELECT 1 FROM stg_v61_funded_pairs fp
              WHERE fp.foundation_ein = p.foundation_ein AND fp.recipient_ein = neg_pool_large.ein
          )
        ORDER BY ABS(HASHTEXT(p.foundation_ein || ein) - p.pos_id)
        LIMIT 10
    ) n
)
SELECT foundation_ein, negative_recipient, total_revenue, state, ntee_broad, 'large', 0
FROM matched WHERE rn = 1;

SELECT 'LARGE done', COUNT(*) FROM stg_v61_matched_negatives WHERE size_bucket = 'large';

\echo 'Step 5 complete'
SELECT size_bucket, COUNT(*) as negative_count FROM stg_v61_matched_negatives GROUP BY size_bucket ORDER BY 1;

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

\echo 'Step 7: Creating final training_data_v6_1 table...'

DROP TABLE IF EXISTS training_data_v6_1;

CREATE TABLE training_data_v6_1 AS

-- POSITIVES (from V6)
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

-- NEGATIVES (size-matched)
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

\echo 'Step 7 complete'

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

-- Cleanup staging tables
DROP TABLE IF EXISTS stg_v61_nonprofit_buckets;
DROP TABLE IF EXISTS stg_v61_positives;
DROP TABLE IF EXISTS stg_v61_funded_pairs;
DROP TABLE IF EXISTS stg_v61_matched_negatives;

\echo ''
\echo 'V6.1 Training Data Creation Complete!'
\echo 'Next: Run PY_2025-01-03_v6.1_export_training.py'
