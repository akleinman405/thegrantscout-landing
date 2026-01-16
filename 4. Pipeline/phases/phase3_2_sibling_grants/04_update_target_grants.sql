-- V3 Pipeline: Update Target Grant Flags
-- Purpose: Mark grants as target based on keywords OR semantic similarity
-- Usage: Run after keyword_match is updated
-- Date: 2026-01-13

-- ============================================================
-- Step 4.4: Update is_target_grant with NULL handling
-- ============================================================

-- Key insight: NULL means "unknown", not "false"
-- A grant with NULL semantic_similarity and no keyword match = unknown target status
-- This preserves uncertainty for manual review

UPDATE f990_2025.calc_client_sibling_grants
SET
    is_target_grant = CASE
        WHEN keyword_match = TRUE THEN TRUE
        WHEN semantic_similarity IS NULL THEN NULL  -- Preserve uncertainty
        WHEN semantic_similarity >= 0.55 THEN TRUE
        ELSE FALSE
    END,
    target_grant_reason = CASE
        WHEN keyword_match = TRUE AND COALESCE(semantic_similarity, 0) >= 0.55 THEN 'BOTH'
        WHEN keyword_match = TRUE THEN 'KEYWORD'
        WHEN semantic_similarity >= 0.55 THEN 'SEMANTIC'
        ELSE NULL
    END
WHERE client_ein = :client_ein;


-- ============================================================
-- Verification Query
-- ============================================================

/*
SELECT
    COUNT(*) as total_grants,
    COUNT(*) FILTER (WHERE is_target_grant = TRUE) as target_grants,
    COUNT(*) FILTER (WHERE is_target_grant = FALSE) as non_target_grants,
    COUNT(*) FILTER (WHERE is_target_grant IS NULL) as unknown_grants,
    COUNT(*) FILTER (WHERE target_grant_reason = 'KEYWORD') as keyword_only,
    COUNT(*) FILTER (WHERE target_grant_reason = 'SEMANTIC') as semantic_only,
    COUNT(*) FILTER (WHERE target_grant_reason = 'BOTH') as both_signals
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;
*/
