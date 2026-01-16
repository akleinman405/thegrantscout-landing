-- Phase 2, Step 2.4: Check Data Quality
-- Purpose: Identify data quality issues that may affect matching
-- Usage: Replace :client_ein with actual EIN

-- Full data quality check
SELECT
    dc.name,
    dc.ein,

    -- Required field checks
    CASE WHEN dc.ein IS NULL OR dc.ein = '' THEN 'MISSING' ELSE 'OK' END as ein_status,
    CASE WHEN dc.mission_text IS NULL OR dc.mission_text = '' THEN 'MISSING' ELSE 'OK' END as mission_status,
    CASE WHEN dc.state IS NULL OR dc.state = '' THEN 'MISSING' ELSE 'OK' END as state_status,

    -- Budget variance check
    dc.budget_tier as questionnaire_budget,
    dc.database_revenue as irs_revenue,
    CASE
        WHEN dc.database_revenue IS NULL THEN 'NO_IRS_DATA'
        WHEN dc.budget_tier LIKE '%Over $1,000,000%' AND dc.database_revenue < 333000 THEN 'RED (>3x)'
        WHEN dc.budget_tier LIKE '%Over $1,000,000%' AND dc.database_revenue < 500000 THEN 'YELLOW (2-3x)'
        WHEN dc.budget_tier LIKE '%$500,000%' AND dc.database_revenue < 166000 THEN 'RED (>3x)'
        WHEN dc.budget_tier LIKE '%$500,000%' AND dc.database_revenue < 250000 THEN 'YELLOW (2-3x)'
        ELSE 'GREEN'
    END as budget_variance,

    -- IRS record check
    CASE WHEN nr.ein IS NULL THEN 'NO_IRS_RECORD' ELSE 'FOUND' END as irs_record_status,
    nr.tax_year as irs_latest_year,

    -- Mission length check
    LENGTH(dc.mission_text) as mission_length,
    CASE
        WHEN LENGTH(dc.mission_text) < 50 THEN 'TOO_SHORT'
        WHEN LENGTH(dc.mission_text) > 2000 THEN 'VERY_LONG'
        ELSE 'OK'
    END as mission_length_status

FROM f990_2025.dim_clients dc
LEFT JOIN (
    SELECT DISTINCT ON (ein) ein, tax_year
    FROM f990_2025.nonprofit_returns
    ORDER BY ein, tax_year DESC
) nr ON dc.ein = nr.ein
WHERE dc.ein = :client_ein;

-- Update quality flags
-- UPDATE f990_2025.dim_clients
-- SET
--     quality_flags = ARRAY['budget_variance_red'],  -- adjust based on findings
--     budget_variance_flag = 'RED',
--     updated_at = NOW()
-- WHERE ein = :client_ein;
