-- Phase 2, Step 2.5: Find Similar Grant Purposes
-- Purpose: See how funders phrase grants for similar work (to inform target_grant_purpose)
-- Usage: Adjust keywords based on client's sector

-- Find grants with relevant keywords to see phrasing patterns
SELECT
    fg.foundation_ein,
    df.name as foundation_name,
    fg.recipient_name_raw,
    fg.amount,
    fg.purpose_text,
    fg.tax_year
FROM f990_2025.fact_grants fg
LEFT JOIN f990_2025.dim_foundations df ON fg.foundation_ein = df.ein
WHERE (
    LOWER(fg.purpose_text) ~ '\ypatient safety\y'
    OR LOWER(fg.purpose_text) ~ '\yhealthcare education\y'
    OR LOWER(fg.purpose_text) ~ '\yclinical education\y'
    OR LOWER(fg.purpose_text) ~ '\yfellowship\y'
)
AND fg.amount >= 25000
AND fg.tax_year >= 2020
ORDER BY fg.tax_year DESC, fg.amount DESC
LIMIT 30;

-- Analyze common phrasing patterns
-- Look for:
-- - How amount is described (if at all)
-- - Action verbs used (support, fund, provide, establish)
-- - Outcome language (to improve, to reduce, to train)
-- - Beneficiary language (for students, for healthcare professionals)

-- Example target_grant_purpose patterns from real grants:
-- "To support fellowship program for clinical education"
-- "For healthcare professional training in patient safety"
-- "To reduce preventable harm through clinical education"
-- "Fellowship program to train healthcare professionals"

-- Update dim_clients with target_grant_purpose
-- UPDATE f990_2025.dim_clients
-- SET
--     target_grant_purpose = 'Fellowship program for clinical education to train healthcare professionals in patient safety and reduce preventable harm',
--     updated_at = NOW()
-- WHERE ein = :client_ein;
