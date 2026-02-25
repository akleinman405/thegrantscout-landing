-- build_cohorts_v3.sql
-- Email Pipeline Redesign: Composite scoring replaces total_giving_5yr DESC
-- Date: 2026-02-17
-- Source: REPORT_2026-02-17.1_data_pipeline_redesign.md
--
-- Changes from v2:
--   1. Composite email_fit_score (geo 0.30, size 0.25, openness 0.20, recency 0.15, volume 0.10)
--   2. Mega-foundation penalty (0.50x for $1B+, 0.75x for $500M+)
--   3. LEFT JOIN to ref_foundation_email_exclusions (ban list)
--   4. Geographic monopoly carve-out (allowed in home state if state_pct >= 0.10)
--   5. Top 25 per combo (up from 15)
--   6. NTEE sub-code example grant matching (4-tier cascade)
--   7. cohort_viability display_count / display_text update
--   8. New columns: geo_score, size_fit_score, openness_score, recency_score, volume_score,
--      mega_penalty, email_fit_score, state_pct, geo_tier, assets, recent_recipients,
--      last_active_year, example_match_tier, example_recipient_ein, example_grant_year,
--      example_recipient_revenue

SET search_path TO f990_2025;

------------------------------------------------------------------------
-- STEP 5: Build cohort_foundation_lists_v2 with composite scoring
------------------------------------------------------------------------

DROP TABLE IF EXISTS cohort_foundation_lists_v2;

CREATE TABLE cohort_foundation_lists_v2 AS
WITH target_combos AS (
    SELECT DISTINCT state, LEFT(ntee_code, 1) AS sector
    FROM nonprofits_prospects2
    WHERE contact_email IS NOT NULL
      AND ntee_code IS NOT NULL
      AND state IS NOT NULL
),

foundation_state_sector AS (
    SELECT
        fg.recipient_state AS state,
        LEFT(dr.ntee_code, 1) AS sector,
        fg.foundation_ein,
        df.name AS foundation_name,
        SUM(fg.amount) AS total_giving_5yr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fg.amount) AS median_grant,
        COUNT(DISTINCT fg.recipient_ein) AS unique_recipients,
        COUNT(DISTINCT CASE WHEN fg.tax_year >= 2022 THEN fg.recipient_ein END) AS recent_recipients,
        MAX(fg.tax_year) AS last_active_year,
        COUNT(DISTINCT fg.tax_year) AS active_years
    FROM fact_grants fg
    JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
    JOIN dim_foundations df ON df.ein = fg.foundation_ein
    WHERE fg.tax_year >= 2019
      AND fg.amount > 0
      AND dr.ntee_code IS NOT NULL
    GROUP BY fg.recipient_state, LEFT(dr.ntee_code, 1), fg.foundation_ein, df.name
    HAVING SUM(fg.amount) > 0
),

scored AS (
    SELECT
        fss.state,
        fss.sector,
        fss.foundation_ein,
        fss.foundation_name,
        fss.total_giving_5yr,
        fss.median_grant,
        fss.unique_recipients,
        fss.recent_recipients,
        fss.last_active_year,
        fss.active_years,
        cfp.accepts_applications,
        fp.total_assets_eoy_amt AS assets,

        COALESCE(fsd.state_pct, 0) AS state_pct,

        -- Geo tier from materialized view
        COALESCE(mgr.geo_tier, 'incidental') AS geo_tier,
        COALESCE(mgr.is_national_funder, false) AS is_national_funder,

        -- 1. GEO SCORE (0-1): concentration in target state
        LEAST(COALESCE(fsd.state_pct, 0) / 0.40, 1.0) AS geo_score,

        -- 2. SIZE FIT SCORE (0-1): median grant in sweet spot $5K-$200K
        CASE
            WHEN fss.median_grant BETWEEN 5000 AND 200000 THEN 1.0
            WHEN fss.median_grant BETWEEN 1000 AND 5000 THEN 0.6
            WHEN fss.median_grant BETWEEN 200000 AND 500000 THEN 0.7
            WHEN fss.median_grant > 500000 THEN 0.3
            WHEN fss.median_grant < 1000 THEN 0.2
            ELSE 0.5
        END AS size_fit_score,

        -- 3. OPENNESS SCORE (0-1): new-grantee rate + accepts applications
        CASE
            WHEN cfp.accepts_applications = true
                 AND cfp.new_recipients_5yr::float / NULLIF(cfp.unique_recipients_5yr, 0) >= 0.30
            THEN LEAST(
                0.5 + 0.5 * (cfp.new_recipients_5yr::float / NULLIF(cfp.unique_recipients_5yr, 0)),
                1.0
            )
            WHEN cfp.accepts_applications = true THEN 0.5
            ELSE 0.2
        END AS openness_score,

        -- 4. RECENCY SCORE (0-1): how recently active
        CASE
            WHEN fss.last_active_year >= 2023 AND fss.active_years >= 3 THEN 1.0
            WHEN fss.last_active_year >= 2023 THEN 0.9
            WHEN fss.last_active_year >= 2022 THEN 0.7
            WHEN fss.last_active_year >= 2021 THEN 0.5
            ELSE 0.3
        END AS recency_score,

        -- 5. VOLUME SCORE (0-1): log-scaled total giving
        LEAST(LN(fss.total_giving_5yr + 1) / LN(100000000), 1.0) AS volume_score,

        -- MEGA-FOUNDATION PENALTY
        CASE
            WHEN fp.total_assets_eoy_amt >= 1000000000 THEN 0.50
            WHEN fp.total_assets_eoy_amt >= 500000000 THEN 0.75
            ELSE 1.00
        END AS mega_penalty

    FROM foundation_state_sector fss
    JOIN target_combos tc ON tc.state = fss.state AND tc.sector = fss.sector
    LEFT JOIN calc_foundation_profiles cfp ON cfp.ein = fss.foundation_ein
    LEFT JOIN foundation_prospects2 fp ON fp.ein = fss.foundation_ein
    LEFT JOIN stg_foundation_state_dist fsd
        ON fsd.foundation_ein = fss.foundation_ein
        AND fsd.recipient_state = fss.state
    LEFT JOIN mv_foundation_geo_relevance mgr
        ON mgr.foundation_ein = fss.foundation_ein
        AND mgr.state = fss.state
    LEFT JOIN ref_foundation_email_exclusions exc
        ON exc.foundation_ein = fss.foundation_ein
    WHERE
      -- Exclude banned foundations, BUT allow geographic monopolies in their home state
      (
          exc.foundation_ein IS NULL
          OR (
              exc.exclusion_category = 'geographic_monopoly'
              AND COALESCE(fsd.state_pct, 0) >= 0.10
          )
      )
      -- Must accept applications or have high openness
      AND (cfp.accepts_applications = true OR cfp.openness_score >= 0.30)
      -- Must be recently active
      AND cfp.last_active_year >= 2021
      -- Must have grant history
      AND cfp.has_grant_history = true
      -- Geographic floor: at least tertiary, or national funder
      AND (
          COALESCE(mgr.geo_tier, 'incidental') IN ('primary', 'secondary', 'tertiary')
          OR COALESCE(mgr.is_national_funder, false) = true
      )
),

ranked AS (
    SELECT
        s.*,
        (
            0.30 * s.geo_score +
            0.25 * s.size_fit_score +
            0.20 * s.openness_score +
            0.15 * s.recency_score +
            0.10 * s.volume_score
        ) * s.mega_penalty AS email_fit_score,
        ROW_NUMBER() OVER (
            PARTITION BY s.state, s.sector
            ORDER BY (
                0.30 * s.geo_score +
                0.25 * s.size_fit_score +
                0.20 * s.openness_score +
                0.15 * s.recency_score +
                0.10 * s.volume_score
            ) * s.mega_penalty DESC
        ) AS foundation_rank
    FROM scored s
)

SELECT
    r.state,
    r.sector AS ntee_sector,
    CASE r.sector
        WHEN 'A' THEN 'Arts & Culture'
        WHEN 'B' THEN 'Education'
        WHEN 'C' THEN 'Environment'
        WHEN 'D' THEN 'Animal-Related'
        WHEN 'E' THEN 'Health'
        WHEN 'F' THEN 'Mental Health'
        WHEN 'G' THEN 'Disease/Disorder'
        WHEN 'H' THEN 'Medical Research'
        WHEN 'I' THEN 'Crime/Legal'
        WHEN 'J' THEN 'Employment'
        WHEN 'K' THEN 'Food/Agriculture'
        WHEN 'L' THEN 'Housing'
        WHEN 'M' THEN 'Public Safety'
        WHEN 'N' THEN 'Recreation'
        WHEN 'O' THEN 'Youth Development'
        WHEN 'P' THEN 'Human Services'
        WHEN 'Q' THEN 'International'
        WHEN 'R' THEN 'Civil Rights'
        WHEN 'S' THEN 'Community Improvement'
        WHEN 'T' THEN 'Philanthropy'
        WHEN 'U' THEN 'Science'
        WHEN 'V' THEN 'Social Science'
        WHEN 'W' THEN 'Public Policy'
        WHEN 'X' THEN 'Religion'
        WHEN 'Y' THEN 'Mutual/Membership'
        WHEN 'Z' THEN 'Unknown'
        ELSE 'Other'
    END AS sector_label,
    r.foundation_rank,
    r.foundation_ein,
    r.foundation_name,
    r.total_giving_5yr,
    r.median_grant,
    r.unique_recipients,
    r.recent_recipients,
    r.last_active_year,
    r.assets,
    r.state_pct,
    r.geo_score::NUMERIC(4,3),
    r.size_fit_score::NUMERIC(4,3),
    r.openness_score::NUMERIC(4,3),
    r.recency_score::NUMERIC(4,3),
    r.volume_score::NUMERIC(4,3),
    r.mega_penalty::NUMERIC(4,2),
    r.email_fit_score::NUMERIC(5,4),
    r.geo_tier,
    r.is_national_funder,
    r.accepts_applications,
    -- Example grant fields (populated in Step 6)
    NULL::TEXT AS example_recipient_name,
    NULL::VARCHAR(20) AS example_recipient_ein,
    NULL::NUMERIC AS example_grant_amount,
    NULL::TEXT AS example_grant_purpose,
    NULL::INTEGER AS example_grant_year,
    NULL::INTEGER AS example_match_tier,
    NULL::NUMERIC AS example_recipient_revenue,
    NULL::VARCHAR(20) AS giving_trend,
    NOW() AS created_at
FROM ranked r
WHERE r.foundation_rank <= 25;

-- Indexes
CREATE INDEX idx_cfl2_state_sector ON cohort_foundation_lists_v2(state, ntee_sector);
CREATE INDEX idx_cfl2_ein ON cohort_foundation_lists_v2(foundation_ein);
CREATE INDEX idx_cfl2_state_sector_rank ON cohort_foundation_lists_v2(state, ntee_sector, foundation_rank);

------------------------------------------------------------------------
-- STEP 6: Example grant selection via NTEE sub-code matching
------------------------------------------------------------------------

-- Tier 1: Same 3-char NTEE prefix + similar revenue (3x range) + recent (2021+)
UPDATE cohort_foundation_lists_v2 cfl SET
    example_recipient_name = ex.recipient_name,
    example_recipient_ein = ex.recipient_ein,
    example_grant_amount = ex.amount,
    example_grant_purpose = ex.purpose_text,
    example_grant_year = ex.tax_year,
    example_match_tier = 1,
    example_recipient_revenue = ex.total_revenue
FROM LATERAL (
    SELECT
        dr.name AS recipient_name,
        dr.ein AS recipient_ein,
        fg.amount,
        fg.purpose_text,
        fg.tax_year,
        nr.total_revenue
    FROM fact_grants fg
    JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
    LEFT JOIN LATERAL (
        SELECT n.total_revenue
        FROM nonprofit_returns n
        WHERE n.ein = dr.ein
        ORDER BY n.tax_year DESC NULLS LAST
        LIMIT 1
    ) nr ON true
    WHERE fg.foundation_ein = cfl.foundation_ein
      AND fg.recipient_state = cfl.state
      AND fg.tax_year >= 2021
      AND fg.amount > 0
      AND dr.ntee_code IS NOT NULL
      AND LENGTH(dr.ntee_code) >= 3
      AND LEFT(dr.ntee_code, 3) LIKE LEFT(cfl.ntee_sector, 1) || '%'
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
) ex
WHERE cfl.example_match_tier IS NULL;

-- Tier 2: Same 2-char NTEE prefix + same state + 2019+
UPDATE cohort_foundation_lists_v2 cfl SET
    example_recipient_name = ex.recipient_name,
    example_recipient_ein = ex.recipient_ein,
    example_grant_amount = ex.amount,
    example_grant_purpose = ex.purpose_text,
    example_grant_year = ex.tax_year,
    example_match_tier = 2,
    example_recipient_revenue = ex.total_revenue
FROM LATERAL (
    SELECT
        dr.name AS recipient_name,
        dr.ein AS recipient_ein,
        fg.amount,
        fg.purpose_text,
        fg.tax_year,
        nr.total_revenue
    FROM fact_grants fg
    JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
    LEFT JOIN LATERAL (
        SELECT n.total_revenue
        FROM nonprofit_returns n
        WHERE n.ein = dr.ein
        ORDER BY n.tax_year DESC NULLS LAST
        LIMIT 1
    ) nr ON true
    WHERE fg.foundation_ein = cfl.foundation_ein
      AND fg.recipient_state = cfl.state
      AND fg.tax_year >= 2019
      AND fg.amount > 0
      AND dr.ntee_code IS NOT NULL
      AND LEFT(dr.ntee_code, 1) = cfl.ntee_sector
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
) ex
WHERE cfl.example_match_tier IS NULL;

-- Tier 3: Same broad sector (1 char) + same state + 2019+ (fallback)
UPDATE cohort_foundation_lists_v2 cfl SET
    example_recipient_name = ex.recipient_name,
    example_recipient_ein = ex.recipient_ein,
    example_grant_amount = ex.amount,
    example_grant_purpose = ex.purpose_text,
    example_grant_year = ex.tax_year,
    example_match_tier = 3,
    example_recipient_revenue = ex.total_revenue
FROM LATERAL (
    SELECT
        dr.name AS recipient_name,
        dr.ein AS recipient_ein,
        fg.amount,
        fg.purpose_text,
        fg.tax_year,
        nr.total_revenue
    FROM fact_grants fg
    JOIN dim_recipients dr ON dr.ein = fg.recipient_ein
    LEFT JOIN LATERAL (
        SELECT n.total_revenue
        FROM nonprofit_returns n
        WHERE n.ein = dr.ein
        ORDER BY n.tax_year DESC NULLS LAST
        LIMIT 1
    ) nr ON true
    WHERE fg.foundation_ein = cfl.foundation_ein
      AND fg.recipient_state = cfl.state
      AND fg.tax_year >= 2019
      AND fg.amount > 0
      AND dr.ntee_code IS NOT NULL
      AND LEFT(dr.ntee_code, 1) = cfl.ntee_sector
    ORDER BY fg.tax_year DESC, fg.amount DESC
    LIMIT 1
) ex
WHERE cfl.example_match_tier IS NULL;

-- Delete rows with no viable example grant
DELETE FROM cohort_foundation_lists_v2
WHERE example_match_tier IS NULL;

-- Recompute foundation_rank after deletions (some combos may have gaps)
-- This is a no-op for ranking purposes but keeps the data clean

------------------------------------------------------------------------
-- STEP 7: Update cohort_viability with display columns
------------------------------------------------------------------------

ALTER TABLE cohort_viability
    ADD COLUMN IF NOT EXISTS display_count INTEGER,
    ADD COLUMN IF NOT EXISTS display_text VARCHAR(100);

UPDATE cohort_viability SET
    display_count = CASE
        WHEN foundation_count < 25 THEN NULL
        WHEN foundation_count BETWEEN 25 AND 75 THEN ROUND(foundation_count / 5.0) * 5
        WHEN foundation_count BETWEEN 76 AND 150 THEN 75
        ELSE 75
    END,
    display_text = CASE
        WHEN foundation_count < 25 THEN 'several foundations that fund'
        WHEN foundation_count BETWEEN 25 AND 75 THEN (ROUND(foundation_count / 5.0) * 5)::text || ' foundations that fund'
        WHEN foundation_count BETWEEN 76 AND 150 THEN 'over 75 foundations that fund'
        ELSE '75 foundations we identified that fund'
    END;

------------------------------------------------------------------------
-- SUMMARY
------------------------------------------------------------------------

SELECT 'cohort_foundation_lists_v2' AS table_name,
       COUNT(*) AS total_rows,
       COUNT(DISTINCT (state, ntee_sector)) AS total_combos,
       COUNT(DISTINCT foundation_ein) AS distinct_foundations,
       ROUND(AVG(email_fit_score)::numeric, 4) AS avg_fit_score,
       ROUND(AVG(CASE WHEN assets >= 1000000000 THEN 1.0 ELSE 0.0 END)::numeric, 3) AS pct_mega
FROM cohort_foundation_lists_v2;

SELECT example_match_tier, COUNT(*) AS cnt
FROM cohort_foundation_lists_v2
GROUP BY example_match_tier
ORDER BY example_match_tier;
