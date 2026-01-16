-- V3 Pipeline: Quality Verification Queries
-- Purpose: Verify data quality at each step
-- Usage: Run after each step to confirm results
-- Date: 2026-01-13

-- ============================================================
-- After Step 4.1: Verify Sibling Grants Population
-- ============================================================

-- Basic counts
SELECT
    'Sibling Grants' as check_name,
    COUNT(*) as total_grants,
    COUNT(DISTINCT foundation_ein) as unique_foundations,
    COUNT(DISTINCT sibling_ein) as unique_siblings
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;

-- Purpose quality distribution
SELECT
    purpose_quality,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein
GROUP BY purpose_quality
ORDER BY count DESC;

-- Year distribution
SELECT
    tax_year,
    COUNT(*) as grants
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein
GROUP BY tax_year
ORDER BY tax_year DESC;


-- ============================================================
-- After Step 4.2: Verify Semantic Similarity
-- ============================================================

-- Distribution of semantic similarity scores
SELECT
    CASE
        WHEN semantic_similarity >= 0.55 THEN 'High (>=0.55)'
        WHEN semantic_similarity >= 0.40 THEN 'Medium (0.40-0.55)'
        WHEN semantic_similarity IS NOT NULL THEN 'Low (<0.40)'
        ELSE 'NULL'
    END as similarity_bucket,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein
GROUP BY 1
ORDER BY count DESC;

-- Statistics
SELECT
    ROUND(AVG(semantic_similarity)::NUMERIC, 3) as avg_similarity,
    ROUND(MIN(semantic_similarity)::NUMERIC, 3) as min_similarity,
    ROUND(MAX(semantic_similarity)::NUMERIC, 3) as max_similarity,
    COUNT(*) FILTER (WHERE semantic_similarity IS NOT NULL) as scored_count,
    COUNT(*) FILTER (WHERE semantic_similarity IS NULL) as null_count
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;


-- ============================================================
-- After Step 4.3: Verify Keyword Matches
-- ============================================================

SELECT
    'Keyword Match' as check_name,
    COUNT(*) FILTER (WHERE keyword_match = TRUE) as matches,
    COUNT(*) FILTER (WHERE keyword_match = FALSE) as non_matches,
    ROUND(100.0 * COUNT(*) FILTER (WHERE keyword_match = TRUE) / COUNT(*), 1) as match_pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;

-- Sample keyword matches
SELECT
    LEFT(purpose_text, 80) as purpose_snippet,
    keyword_match,
    semantic_similarity
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein
AND keyword_match = TRUE
LIMIT 10;


-- ============================================================
-- After Step 4.4: Verify Target Grants
-- ============================================================

SELECT
    'Target Grant Status' as check_name,
    COUNT(*) FILTER (WHERE is_target_grant = TRUE) as target_grants,
    COUNT(*) FILTER (WHERE is_target_grant = FALSE) as non_target,
    COUNT(*) FILTER (WHERE is_target_grant IS NULL) as unknown
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;

-- Breakdown by reason
SELECT
    target_grant_reason,
    COUNT(*) as count
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein
AND is_target_grant = TRUE
GROUP BY target_grant_reason;


-- ============================================================
-- After Step 4.5: Verify Foundation Scores
-- ============================================================

-- Top foundations by target grants
SELECT
    foundation_name,
    foundation_state,
    target_grants_to_siblings,
    gold_standard_grants,
    most_recent_target_year,
    median_grant_size_to_siblings,
    lasso_score
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = :client_ein
ORDER BY target_grants_to_siblings DESC NULLS LAST
LIMIT 20;

-- Summary statistics
SELECT
    COUNT(*) as total_foundations,
    COUNT(*) FILTER (WHERE target_grants_to_siblings > 0) as with_target_grants,
    COUNT(*) FILTER (WHERE gold_standard_grants > 0) as with_gold_standard,
    SUM(target_grants_to_siblings) as total_target_grants
FROM f990_2025.calc_client_foundation_scores
WHERE client_ein = :client_ein;
