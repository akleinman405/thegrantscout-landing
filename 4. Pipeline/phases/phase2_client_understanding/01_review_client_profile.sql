-- Phase 2, Step 2.1: Review Client Profile
-- Purpose: Pull full client profile for review
-- Usage: Replace :client_ein or :client_name with actual values

-- By EIN
SELECT
    id,
    name,
    ein,
    state,
    city,
    org_type,
    sector_broad,
    sector_ntee,
    budget_tier,
    database_revenue,
    database_assets,
    grant_size_seeking,
    grant_capacity,
    geographic_scope,
    mission_text,
    matching_grant_keywords,
    target_grant_purpose,
    timeframe,
    budget_variance_flag,
    quality_flags,
    created_at,
    updated_at
FROM f990_2025.dim_clients
WHERE ein = :client_ein;

-- Or by name (fuzzy match)
-- SELECT * FROM f990_2025.dim_clients
-- WHERE LOWER(name) LIKE LOWER('%:client_name%');
