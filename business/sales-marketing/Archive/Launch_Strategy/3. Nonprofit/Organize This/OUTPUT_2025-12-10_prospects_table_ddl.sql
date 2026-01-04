-- =============================================================================
-- f990_2025.prospects Table DDL
-- Created: 2025-12-10
-- Purpose: Store and score nonprofits for outreach
-- =============================================================================

-- Drop existing table if needed
-- DROP TABLE IF EXISTS f990_2025.prospects CASCADE;

CREATE TABLE f990_2025.prospects (
    -- Primary Key
    ein VARCHAR(9) PRIMARY KEY,

    -- Base Info (from F990 import tables)
    org_name TEXT,
    state VARCHAR(2),
    city TEXT,
    zip VARCHAR(10),
    ntee_code VARCHAR(10),
    sector CHAR(1),  -- First letter of NTEE
    form_type VARCHAR(10),  -- 990, 990-EZ, etc.
    tax_year INT,

    -- Size Metrics
    total_revenue NUMERIC,
    total_expenses NUMERIC,
    total_assets NUMERIC,
    contributions_grants NUMERIC,
    program_service_revenue NUMERIC,
    grant_dependency_pct NUMERIC,
    employee_count INT,
    volunteer_count INT,

    -- Foundation Grants Received (from 990-PF grant data)
    num_foundation_grants INT DEFAULT 0,
    num_unique_funders INT DEFAULT 0,
    total_foundation_grant_amount NUMERIC DEFAULT 0,
    most_recent_grant_year INT,

    -- Calculated/Derived
    revenue_band VARCHAR(20),
    grant_dep_band VARCHAR(20),
    yoy_revenue_growth NUMERIC,

    -- Scoring
    icp_score INT DEFAULT 0,
    priority_tier INT,  -- 1, 2, or 3

    -- Enrichment (to be added later)
    website TEXT,
    mission_statement TEXT,
    contact_name TEXT,
    contact_title TEXT,
    contact_email TEXT,
    contact_phone TEXT,

    -- Personalization (for email generation)
    personalization_tier INT,
    personalization_hook TEXT,
    email_template_id TEXT,
    custom_sentence TEXT,
    email_draft TEXT,
    beta_client_connection TEXT,  -- "Same funder as Horizons", "Same sector as SNS"

    -- Outreach Tracking
    outreach_status VARCHAR(20) DEFAULT 'not_contacted',
    last_contact_date DATE,
    email_sent_date DATE,
    email_opened BOOLEAN,
    email_replied BOOLEAN,
    reply_sentiment VARCHAR(20),
    next_followup_date DATE,
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Indexes for common queries
-- =============================================================================

CREATE INDEX idx_prospects_score ON f990_2025.prospects(icp_score DESC);
CREATE INDEX idx_prospects_tier ON f990_2025.prospects(priority_tier);
CREATE INDEX idx_prospects_status ON f990_2025.prospects(outreach_status);
CREATE INDEX idx_prospects_state ON f990_2025.prospects(state);
CREATE INDEX idx_prospects_sector ON f990_2025.prospects(sector);

-- =============================================================================
-- Population Query (insert qualifying nonprofits)
-- =============================================================================

-- INSERT INTO f990_2025.prospects (...)
-- WITH latest_filing AS (
--     SELECT ein, MAX(tax_year) as max_year
--     FROM f990_2025.nonprofit_returns
--     WHERE tax_year >= 2022
--     GROUP BY ein
-- )
-- SELECT DISTINCT ON (nr.ein)
--     nr.ein,
--     nr.organization_name,
--     nr.state,
--     nr.city,
--     nr.zip,
--     bmf.ntee_cd,
--     LEFT(bmf.ntee_cd, 1),
--     nr.form_type,
--     nr.tax_year,
--     nr.total_revenue,
--     nr.total_expenses,
--     nr.total_assets_eoy,
--     nr.contributions_grants,
--     nr.program_service_revenue,
--     ROUND(100.0 * nr.contributions_grants / NULLIF(nr.total_revenue, 0), 2),
--     nr.total_employees_cnt,
--     nr.total_volunteers_cnt,
--     nr.website,
--     COALESCE(nr.mission_description, nr.primary_exempt_purpose, nr.activity_description)
-- FROM f990_2025.nonprofit_returns nr
-- JOIN latest_filing lf ON nr.ein = lf.ein AND nr.tax_year = lf.max_year
-- LEFT JOIN f990_2025.irs_bmf bmf ON nr.ein = bmf.ein
-- WHERE nr.total_revenue BETWEEN 500000 AND 5000000
--   AND nr.total_revenue > 0
--   AND nr.contributions_grants > 0
--   AND (nr.contributions_grants::numeric / nr.total_revenue::numeric) > 0.25
--   AND nr.form_type IN ('990', '990EZ')
--   AND (bmf.ntee_cd IS NULL
--        OR NOT (
--            bmf.ntee_cd ~ '^B4[0-3]'  -- Universities
--            OR bmf.ntee_cd ~ '^E2[0-4]'  -- Hospitals
--            OR bmf.ntee_cd ~ '^X'  -- Churches
--            OR bmf.ntee_cd ~ '^T'  -- Federated giving
--        ))
-- ORDER BY nr.ein, nr.tax_year DESC;

-- =============================================================================
-- ICP Score Calculation
-- =============================================================================

-- UPDATE f990_2025.prospects
-- SET icp_score =
--     -- Revenue sweet spot
--     CASE
--         WHEN total_revenue BETWEEN 1000000 AND 3500000 THEN 3
--         WHEN total_revenue BETWEEN 500000 AND 1000000 THEN 1
--         WHEN total_revenue BETWEEN 3500000 AND 5000000 THEN 1
--         ELSE 0
--     END
--     -- High grant dependency
--     + CASE WHEN grant_dependency_pct >= 50 THEN 2 ELSE 0 END
--     -- Underserved by foundations
--     + CASE
--         WHEN COALESCE(num_foundation_grants, 0) <= 3 THEN 3
--         WHEN COALESCE(num_foundation_grants, 0) <= 5 THEN 1
--         ELSE 0
--     END
--     -- Proven sector
--     + CASE WHEN sector IN ('E', 'P', 'B', 'N') THEN 2 ELSE 0 END
--     -- California bonus
--     + CASE WHEN state = 'CA' THEN 1 ELSE 0 END
--     -- Has employees
--     + CASE WHEN employee_count BETWEEN 5 AND 50 THEN 1 ELSE 0 END;

-- =============================================================================
-- Priority Tier Assignment
-- =============================================================================

-- UPDATE f990_2025.prospects
-- SET priority_tier = CASE
--     WHEN icp_score >= 10 THEN 1  -- High touch
--     WHEN icp_score >= 6 THEN 2   -- Template
--     ELSE 3                        -- Mail merge
-- END;

-- =============================================================================
-- Useful Queries
-- =============================================================================

-- Top prospects by score
-- SELECT ein, org_name, state, sector, total_revenue, icp_score, priority_tier
-- FROM f990_2025.prospects
-- ORDER BY icp_score DESC, total_revenue DESC
-- LIMIT 100;

-- Tier 1 prospects in California
-- SELECT * FROM f990_2025.prospects
-- WHERE priority_tier = 1 AND state = 'CA'
-- ORDER BY icp_score DESC;

-- Prospects with beta client connections
-- SELECT * FROM f990_2025.prospects
-- WHERE beta_client_connection IS NOT NULL
-- ORDER BY icp_score DESC;
