-- Phase 2, Step 2.2: Compare Questionnaire Mission vs IRS Mission
-- Purpose: Get IRS mission to compare with questionnaire mission
-- Usage: Replace :client_ein with actual EIN

-- Get IRS mission from nonprofit_returns
SELECT
    ein,
    organization_name,
    mission_description,
    tax_year,
    total_revenue,
    total_assets
FROM f990_2025.nonprofit_returns
WHERE ein = :client_ein
ORDER BY tax_year DESC
LIMIT 3;

-- Get questionnaire mission from dim_clients
SELECT
    name,
    ein,
    mission_text as questionnaire_mission
FROM f990_2025.dim_clients
WHERE ein = :client_ein;

-- Side-by-side comparison (combine results manually or use this)
SELECT
    dc.name,
    dc.ein,
    dc.mission_text as questionnaire_mission,
    nr.mission_description as irs_mission,
    nr.tax_year as irs_year,
    LENGTH(dc.mission_text) as questionnaire_length,
    LENGTH(nr.mission_description) as irs_length
FROM f990_2025.dim_clients dc
LEFT JOIN (
    SELECT DISTINCT ON (ein) *
    FROM f990_2025.nonprofit_returns
    WHERE ein = :client_ein
    ORDER BY ein, tax_year DESC
) nr ON dc.ein = nr.ein
WHERE dc.ein = :client_ein;

-- Update dim_clients with IRS mission if better
-- UPDATE f990_2025.dim_clients
-- SET mission_text = (
--     SELECT mission_description
--     FROM f990_2025.nonprofit_returns
--     WHERE ein = :client_ein
--     ORDER BY tax_year DESC
--     LIMIT 1
-- ),
-- updated_at = NOW()
-- WHERE ein = :client_ein;
