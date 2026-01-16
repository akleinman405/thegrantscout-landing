-- Phase 2, Step 2.3: Check Keyword Frequency
-- Purpose: Verify keywords appear in grant purposes before using them
-- Usage: Replace keyword values as needed

-- Check individual keyword frequency
SELECT
    'patient safety' as keyword,
    COUNT(*) as grant_count,
    COUNT(DISTINCT foundation_ein) as foundation_count
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\ypatient safety\y'
UNION ALL
SELECT
    'healthcare education',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\yhealthcare education\y'
UNION ALL
SELECT
    'clinical education',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\yclinical education\y'
UNION ALL
SELECT
    'medical education',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\ymedical education\y'
UNION ALL
SELECT
    'fellowship',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\yfellowship\y'
UNION ALL
SELECT
    'preventable harm',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\ypreventable harm\y'
UNION ALL
SELECT
    'healthcare quality',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\yhealthcare quality\y'
UNION ALL
SELECT
    'hospital safety',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\yhospital safety\y'
UNION ALL
SELECT
    'medical training',
    COUNT(*),
    COUNT(DISTINCT foundation_ein)
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\ymedical training\y'
ORDER BY grant_count DESC;

-- Sample grants with keyword matches
SELECT
    foundation_ein,
    recipient_name_raw,
    amount,
    purpose_text,
    tax_year
FROM f990_2025.fact_grants
WHERE LOWER(purpose_text) ~ '\ypatient safety\y'
ORDER BY tax_year DESC, amount DESC
LIMIT 10;

-- Update dim_clients with keywords (PostgreSQL array)
-- UPDATE f990_2025.dim_clients
-- SET matching_grant_keywords = ARRAY[
--     'patient safety',
--     'healthcare education',
--     'clinical education',
--     'medical education',
--     'fellowship',
--     'preventable harm',
--     'healthcare quality',
--     'hospital safety',
--     'medical training'
-- ],
-- updated_at = NOW()
-- WHERE ein = :client_ein;
