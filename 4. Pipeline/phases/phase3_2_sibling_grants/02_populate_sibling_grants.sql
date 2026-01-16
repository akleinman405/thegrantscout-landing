-- V3 Pipeline: Populate Sibling Grants
-- Purpose: Insert all grants to sibling nonprofits
-- Usage: Run after siblings are identified in calc_client_siblings
-- Date: 2026-01-13

-- ============================================================
-- Step 4.1: Populate calc_client_sibling_grants
-- ============================================================

-- Replace :client_ein with actual client EIN (e.g., '462730379' for PSMF)

INSERT INTO f990_2025.calc_client_sibling_grants
    (client_ein, foundation_ein, sibling_ein, grant_id, amount, tax_year,
     recipient_state, purpose_text, is_first_grant, purpose_quality)
SELECT
    :client_ein as client_ein,
    fg.foundation_ein,
    fg.recipient_ein as sibling_ein,
    fg.id as grant_id,
    fg.amount,
    fg.tax_year,
    fg.recipient_state,
    fg.purpose_text,
    -- is_first_grant: TRUE if this is the earliest grant year from foundation->recipient
    (fg.tax_year = (
        SELECT MIN(fg2.tax_year)
        FROM f990_2025.fact_grants fg2
        WHERE fg2.foundation_ein = fg.foundation_ein
        AND fg2.recipient_ein = fg.recipient_ein
    )) as is_first_grant,
    -- purpose_quality: assess text quality for semantic matching
    CASE
        WHEN fg.purpose_text IS NULL THEN 'NULL'
        WHEN TRIM(fg.purpose_text) = '' THEN 'EMPTY'
        WHEN LENGTH(TRIM(fg.purpose_text)) < 10 THEN 'SHORT'
        ELSE 'VALID'
    END as purpose_quality
FROM f990_2025.fact_grants fg
WHERE fg.recipient_ein IN (
    SELECT sibling_ein FROM f990_2025.calc_client_siblings
    WHERE client_ein = :client_ein
);


-- ============================================================
-- Verification Query
-- ============================================================

-- Run this to verify the insert:
/*
SELECT
    COUNT(*) as total_grants,
    COUNT(DISTINCT foundation_ein) as unique_foundations,
    COUNT(DISTINCT sibling_ein) as unique_siblings,
    COUNT(*) FILTER (WHERE is_first_grant = TRUE) as first_grants,
    COUNT(*) FILTER (WHERE purpose_quality = 'VALID') as valid_purpose,
    COUNT(*) FILTER (WHERE purpose_quality = 'NULL') as null_purpose,
    COUNT(*) FILTER (WHERE purpose_quality = 'EMPTY') as empty_purpose,
    COUNT(*) FILTER (WHERE purpose_quality = 'SHORT') as short_purpose
FROM f990_2025.calc_client_sibling_grants
WHERE client_ein = :client_ein;
*/
