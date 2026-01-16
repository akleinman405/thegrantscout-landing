-- SQL_2025-01-03.1_fix_v6_validation_negatives.sql
--
-- Fix V6 critical issue: Add hard negatives for 2023-2024 validation/test sets
--
-- Problem: training_data_v6 has 0 negatives for tax_year >= 2023
-- Solution: Generate hard negatives by sampling foundation-recipient pairs
--           that could have happened but didn't (no grant recorded)
--
-- Run: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- ============================================================================
-- STEP 1: Identify active foundations in 2023-2024
-- ============================================================================

DROP TABLE IF EXISTS stg_active_foundations_2023_2024;

CREATE TABLE stg_active_foundations_2023_2024 AS
SELECT DISTINCT
    foundation_ein,
    tax_year
FROM fact_grants
WHERE tax_year IN (2023, 2024)
  AND foundation_ein IN (
    SELECT ein FROM stg_accessible_foundations
  );

CREATE INDEX idx_af_2324_ein ON stg_active_foundations_2023_2024(foundation_ein);
CREATE INDEX idx_af_2324_year ON stg_active_foundations_2023_2024(tax_year);

SELECT 'Active foundations in 2023-2024' as step,
       COUNT(DISTINCT foundation_ein) as foundations,
       COUNT(*) as foundation_years
FROM stg_active_foundations_2023_2024;

-- ============================================================================
-- STEP 2: Identify eligible recipients (existed in 2017-2022, filed 990s)
-- ============================================================================

DROP TABLE IF EXISTS stg_eligible_recipients_2023_2024;

CREATE TABLE stg_eligible_recipients_2023_2024 AS
SELECT DISTINCT
    recipient_ein
FROM fact_grants
WHERE tax_year BETWEEN 2017 AND 2022  -- Recipients that existed in training period
  AND recipient_ein IS NOT NULL;

CREATE INDEX idx_er_2324_ein ON stg_eligible_recipients_2023_2024(recipient_ein);

SELECT 'Eligible recipients' as step,
       COUNT(*) as count
FROM stg_eligible_recipients_2023_2024;

-- ============================================================================
-- STEP 3: Create lookup of actual grants (to exclude from negatives)
-- ============================================================================

DROP TABLE IF EXISTS stg_actual_grants_2023_2024;

CREATE TABLE stg_actual_grants_2023_2024 AS
SELECT DISTINCT
    foundation_ein,
    recipient_ein,
    tax_year
FROM fact_grants
WHERE tax_year IN (2023, 2024);

CREATE INDEX idx_ag_2324_pair ON stg_actual_grants_2023_2024(foundation_ein, recipient_ein, tax_year);

SELECT 'Actual grants in 2023-2024' as step,
       COUNT(*) as count
FROM stg_actual_grants_2023_2024;

-- ============================================================================
-- STEP 4: Sample hard negatives for 2023 (validation set)
-- ============================================================================

-- Strategy: For each foundation active in 2023, sample 5-10 recipients they didn't fund
-- Prioritize same-state and same-sector matches (hard negatives)

DROP TABLE IF EXISTS stg_hard_negatives_2023;

CREATE TABLE stg_hard_negatives_2023 AS
WITH foundation_profiles AS (
    -- Get foundation state and primary sector
    SELECT
        cf.ein,
        cf.state as f_state,
        sd.ntee_broad as primary_sector
    FROM calc_foundation_features cf
    LEFT JOIN LATERAL (
        SELECT ntee_broad
        FROM stg_foundation_sector_dist
        WHERE foundation_ein = cf.ein
        ORDER BY sector_pct DESC
        LIMIT 1
    ) sd ON true
),
recipient_profiles AS (
    -- Get recipient state and sector
    SELECT
        rf.ein,
        rf.state as r_state,
        rf.ntee_broad
    FROM calc_recipient_features rf
    WHERE rf.ein IN (SELECT recipient_ein FROM stg_eligible_recipients_2023_2024)
),
candidate_pairs AS (
    -- Generate candidates: prioritize same state or same sector
    SELECT
        af.foundation_ein,
        rp.ein as recipient_ein,
        2023 as tax_year,
        0 as label,
        'hard_negative_2023' as sample_type,
        CASE
            WHEN fp.f_state = rp.r_state AND fp.primary_sector = rp.ntee_broad THEN 1  -- Hardest
            WHEN fp.f_state = rp.r_state THEN 2  -- Same state
            WHEN fp.primary_sector = rp.ntee_broad THEN 3  -- Same sector
            ELSE 4  -- Random
        END as difficulty_tier,
        ROW_NUMBER() OVER (PARTITION BY af.foundation_ein ORDER BY RANDOM()) as rn
    FROM stg_active_foundations_2023_2024 af
    JOIN foundation_profiles fp ON af.foundation_ein = fp.ein
    CROSS JOIN recipient_profiles rp
    WHERE af.tax_year = 2023
      -- Exclude actual grants
      AND NOT EXISTS (
        SELECT 1 FROM stg_actual_grants_2023_2024 ag
        WHERE ag.foundation_ein = af.foundation_ein
          AND ag.recipient_ein = rp.ein
          AND ag.tax_year = 2023
      )
      -- Prioritize hardest negatives (same state + sector), then same state, then same sector
      AND (
        fp.f_state = rp.r_state OR
        fp.primary_sector = rp.ntee_broad OR
        RANDOM() < 0.1  -- 10% random negatives
      )
)
SELECT
    foundation_ein,
    recipient_ein,
    tax_year,
    label,
    sample_type
FROM candidate_pairs
WHERE rn <= 10  -- 10 negatives per foundation
  AND difficulty_tier <= 3  -- Only hard and medium negatives
ORDER BY difficulty_tier, RANDOM()
LIMIT 500000;  -- Cap at 500K negatives

CREATE INDEX idx_hn2023_pair ON stg_hard_negatives_2023(foundation_ein, recipient_ein);

SELECT 'Hard negatives for 2023' as step,
       COUNT(*) as count
FROM stg_hard_negatives_2023;

-- ============================================================================
-- STEP 5: Sample hard negatives for 2024 (test set)
-- ============================================================================

DROP TABLE IF EXISTS stg_hard_negatives_2024;

CREATE TABLE stg_hard_negatives_2024 AS
WITH foundation_profiles AS (
    SELECT
        cf.ein,
        cf.state as f_state,
        sd.ntee_broad as primary_sector
    FROM calc_foundation_features cf
    LEFT JOIN LATERAL (
        SELECT ntee_broad
        FROM stg_foundation_sector_dist
        WHERE foundation_ein = cf.ein
        ORDER BY sector_pct DESC
        LIMIT 1
    ) sd ON true
),
recipient_profiles AS (
    SELECT
        rf.ein,
        rf.state as r_state,
        rf.ntee_broad
    FROM calc_recipient_features rf
    WHERE rf.ein IN (SELECT recipient_ein FROM stg_eligible_recipients_2023_2024)
),
candidate_pairs AS (
    SELECT
        af.foundation_ein,
        rp.ein as recipient_ein,
        2024 as tax_year,
        0 as label,
        'hard_negative_2024' as sample_type,
        CASE
            WHEN fp.f_state = rp.r_state AND fp.primary_sector = rp.ntee_broad THEN 1
            WHEN fp.f_state = rp.r_state THEN 2
            WHEN fp.primary_sector = rp.ntee_broad THEN 3
            ELSE 4
        END as difficulty_tier,
        ROW_NUMBER() OVER (PARTITION BY af.foundation_ein ORDER BY RANDOM()) as rn
    FROM stg_active_foundations_2023_2024 af
    JOIN foundation_profiles fp ON af.foundation_ein = fp.ein
    CROSS JOIN recipient_profiles rp
    WHERE af.tax_year = 2024
      AND NOT EXISTS (
        SELECT 1 FROM stg_actual_grants_2023_2024 ag
        WHERE ag.foundation_ein = af.foundation_ein
          AND ag.recipient_ein = rp.ein
          AND ag.tax_year = 2024
      )
      AND (
        fp.f_state = rp.r_state OR
        fp.primary_sector = rp.ntee_broad OR
        RANDOM() < 0.1
      )
)
SELECT
    foundation_ein,
    recipient_ein,
    tax_year,
    label,
    sample_type
FROM candidate_pairs
WHERE rn <= 10
  AND difficulty_tier <= 3
ORDER BY difficulty_tier, RANDOM()
LIMIT 100000;  -- Smaller test set

CREATE INDEX idx_hn2024_pair ON stg_hard_negatives_2024(foundation_ein, recipient_ein);

SELECT 'Hard negatives for 2024' as step,
       COUNT(*) as count
FROM stg_hard_negatives_2024;

-- ============================================================================
-- STEP 6: Insert negatives into stg_v5_training_pairs
-- ============================================================================

INSERT INTO stg_v5_training_pairs (foundation_ein, recipient_ein, tax_year, label, sample_type)
SELECT foundation_ein, recipient_ein, tax_year, label, sample_type
FROM stg_hard_negatives_2023;

INSERT INTO stg_v5_training_pairs (foundation_ein, recipient_ein, tax_year, label, sample_type)
SELECT foundation_ein, recipient_ein, tax_year, label, sample_type
FROM stg_hard_negatives_2024;

-- ============================================================================
-- STEP 7: Verify class balance in splits
-- ============================================================================

SELECT 'Final training pair distribution' as info;

SELECT
    tax_year,
    label,
    sample_type,
    COUNT(*) as count
FROM stg_v5_training_pairs
GROUP BY tax_year, label, sample_type
ORDER BY tax_year, label, sample_type;

SELECT 'Split summary' as info;

SELECT
    CASE
        WHEN tax_year <= 2022 THEN 'Train (2017-2022)'
        WHEN tax_year = 2023 THEN 'Validation (2023)'
        WHEN tax_year = 2024 THEN 'Test (2024)'
    END as split,
    label,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY CASE
        WHEN tax_year <= 2022 THEN 'Train'
        WHEN tax_year = 2023 THEN 'Val'
        ELSE 'Test'
    END), 1) as pct
FROM stg_v5_training_pairs
GROUP BY CASE
    WHEN tax_year <= 2022 THEN 'Train (2017-2022)'
    WHEN tax_year = 2023 THEN 'Validation (2023)'
    WHEN tax_year = 2024 THEN 'Test (2024)'
END, label
ORDER BY split, label;

-- ============================================================================
-- STEP 8: Cleanup temporary tables
-- ============================================================================

-- Keep these for debugging:
-- DROP TABLE IF EXISTS stg_active_foundations_2023_2024;
-- DROP TABLE IF EXISTS stg_eligible_recipients_2023_2024;
-- DROP TABLE IF EXISTS stg_actual_grants_2023_2024;
-- DROP TABLE IF EXISTS stg_hard_negatives_2023;
-- DROP TABLE IF EXISTS stg_hard_negatives_2024;

SELECT 'Done! Negatives added to stg_v5_training_pairs' as status;
SELECT 'Now re-run SQL_2025-01-02_v6_training_data.sql to rebuild training_data_v6' as next_step;
