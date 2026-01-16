-- V3 Pipeline: Update Keyword Matches
-- Purpose: Flag grants where purpose_text matches client keywords
-- Usage: Run after Step 4.2 (semantic similarity) completes
-- Date: 2026-01-13

-- ============================================================
-- Step 4.3: Update keyword_match using word boundaries
-- ============================================================

-- PSMF Keywords (customize per client):
-- patient safety, healthcare education, clinical education, medical education,
-- fellowship, preventable harm, healthcare quality, hospital safety, medical training

-- Using PostgreSQL word boundary regex (\y) to prevent false positives
-- e.g., prevents "reeducation" from matching "education"

-- For grants with VALID purpose text:
UPDATE f990_2025.calc_client_sibling_grants
SET keyword_match = (
    purpose_text ~* '\ypatient\s+safety\y' OR
    purpose_text ~* '\yhealthcare\s+education\y' OR
    purpose_text ~* '\yclinical\s+education\y' OR
    purpose_text ~* '\ymedical\s+education\y' OR
    purpose_text ~* '\yfellowship\y' OR
    purpose_text ~* '\ypreventable\s+harm\y' OR
    purpose_text ~* '\yhealthcare\s+quality\y' OR
    purpose_text ~* '\yhospital\s+safety\y' OR
    purpose_text ~* '\ymedical\s+training\y'
)
WHERE client_ein = :client_ein
AND purpose_quality = 'VALID';

-- For grants with non-VALID purpose text, set to FALSE:
UPDATE f990_2025.calc_client_sibling_grants
SET keyword_match = FALSE
WHERE client_ein = :client_ein
AND purpose_quality != 'VALID';


-- ============================================================
-- Verification Query
-- ============================================================

/*
SELECT
    COUNT(*) as total_grants,
    COUNT(*) FILTER (WHERE keyword_match = TRUE) as keyword_matches,
    COUNT(*) FILTER (WHERE keyword_match = FALSE) as non_matches,
    ROUND(100.0 * COUNT(*) FILTER (WHERE keyword_match = TRUE) / COUNT(*), 1) as match_pct
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;
*/
