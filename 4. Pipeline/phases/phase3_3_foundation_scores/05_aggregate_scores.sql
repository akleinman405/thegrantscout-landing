-- V3 Pipeline: Aggregate Foundation Scores
-- Purpose: Roll up grant-level data to foundation-level scores
-- Usage: Run after is_target_grant is updated
-- Date: 2026-01-13

-- ============================================================
-- Step 4.5: Aggregate to calc_client_foundation_scores
-- ============================================================

-- Replace :client_ein and :client_name with actual values
-- Replace :client_state with client's state (e.g., 'CA' for PSMF)

INSERT INTO f990_2025.calc_client_foundation_scores
    (client_ein, client_name, foundation_ein, foundation_name, foundation_state,
     foundation_total_assets, siblings_funded, grants_to_siblings,
     total_amount_to_siblings, median_grant_size_to_siblings,
     target_grants_to_siblings, target_first_grants, unknown_target_count,
     client_state, geo_grants_to_siblings, target_geo_grants, gold_standard_grants,
     most_recent_grant_year, most_recent_target_year, lasso_score)
SELECT
    :client_ein as client_ein,
    :client_name as client_name,
    csg.foundation_ein,
    df.name as foundation_name,
    df.state as foundation_state,
    pr.total_assets_eoy_amt as foundation_total_assets,
    COUNT(DISTINCT csg.sibling_ein) as siblings_funded,
    COUNT(*) as grants_to_siblings,
    SUM(csg.amount) as total_amount_to_siblings,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY csg.amount) as median_grant_size_to_siblings,

    -- Target metrics
    COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE) as target_grants_to_siblings,
    COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE AND csg.is_first_grant = TRUE) as target_first_grants,
    COUNT(*) FILTER (WHERE csg.is_target_grant IS NULL) as unknown_target_count,

    -- Geographic (use client_state parameter)
    :client_state as client_state,
    COUNT(*) FILTER (WHERE csg.recipient_state = :client_state) as geo_grants_to_siblings,
    COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE AND csg.recipient_state = :client_state) as target_geo_grants,

    -- GOLD STANDARD: Target + First + Client State
    COUNT(*) FILTER (WHERE csg.is_target_grant = TRUE
                     AND csg.is_first_grant = TRUE
                     AND csg.recipient_state = :client_state) as gold_standard_grants,

    -- Recency
    MAX(csg.tax_year) as most_recent_grant_year,
    MAX(csg.tax_year) FILTER (WHERE csg.is_target_grant = TRUE) as most_recent_target_year,

    fcs.lasso_score
FROM f990_2025.calc_client_sibling_grants csg
JOIN f990_2025.dim_foundations df ON csg.foundation_ein = df.ein
LEFT JOIN f990_2025.pf_returns pr ON df.ein = pr.ein
    AND pr.tax_year = (SELECT MAX(tax_year) FROM f990_2025.pf_returns WHERE ein = df.ein)
LEFT JOIN f990_2025.fact_foundation_client_scores fcs
    ON csg.foundation_ein = fcs.foundation_ein AND fcs.client_ein = :client_ein
WHERE csg.client_ein = :client_ein
GROUP BY csg.foundation_ein, df.name, df.state, pr.total_assets_eoy_amt, fcs.lasso_score;


-- ============================================================
-- Verification Query
-- ============================================================

/*
SELECT
    COUNT(*) as total_foundations,
    COUNT(*) FILTER (WHERE target_grants_to_siblings > 0) as with_target_grants,
    COUNT(*) FILTER (WHERE gold_standard_grants > 0) as with_gold_standard,
    SUM(target_grants_to_siblings) as total_target_grants,
    SUM(gold_standard_grants) as total_gold_standard
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = :client_ein;
*/
