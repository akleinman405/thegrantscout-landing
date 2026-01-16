-- V3 Pipeline: Create Tables
-- Purpose: Create tables for sibling-based foundation matching
-- Usage: Run once to set up V3 infrastructure
-- Date: 2026-01-13

-- ============================================================
-- Table 1: calc_client_sibling_grants
-- Stores all grants to sibling nonprofits with target flags
-- ============================================================

CREATE TABLE IF NOT EXISTS f990_2025.calc_client_sibling_grants (
    -- Keys
    client_ein          VARCHAR(9) NOT NULL,
    foundation_ein      VARCHAR(9) NOT NULL,
    sibling_ein         VARCHAR(9) NOT NULL,
    grant_id            BIGINT NOT NULL,

    -- Grant details
    amount              BIGINT,
    tax_year            INT,
    recipient_state     VARCHAR(2),
    purpose_text        TEXT,

    -- Computed flags
    is_first_grant      BOOLEAN,           -- First grant from this fdn to this recipient
    purpose_quality     VARCHAR(20),       -- 'VALID', 'NULL', 'EMPTY', 'SHORT'
    keyword_match       BOOLEAN,           -- Purpose matches client keywords
    semantic_similarity NUMERIC(4,3),      -- 0.000 - 1.000
    is_target_grant     BOOLEAN,           -- keyword OR semantic >= 0.55 (NULL = unknown)
    target_grant_reason VARCHAR(20),       -- 'KEYWORD', 'SEMANTIC', 'BOTH'

    computed_at         TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (client_ein, grant_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sibling_grants_foundation
    ON f990_2025.calc_client_sibling_grants(client_ein, foundation_ein);
CREATE INDEX IF NOT EXISTS idx_sibling_grants_target
    ON f990_2025.calc_client_sibling_grants(client_ein, is_target_grant)
    WHERE is_target_grant = TRUE;
CREATE INDEX IF NOT EXISTS idx_sibling_grants_sibling
    ON f990_2025.calc_client_sibling_grants(client_ein, sibling_ein);


-- ============================================================
-- Table 2: calc_client_foundation_scores
-- Aggregated scores per foundation for ranking
-- ============================================================

CREATE TABLE IF NOT EXISTS f990_2025.calc_client_foundation_scores (
    -- Keys
    client_ein                  VARCHAR(9) NOT NULL,
    client_name                 VARCHAR(255),
    foundation_ein              VARCHAR(9) NOT NULL,

    -- Foundation context (denormalized)
    foundation_name             VARCHAR(255),
    foundation_state            VARCHAR(2),
    foundation_total_assets     BIGINT,

    -- Volume metrics
    siblings_funded             INT,
    grants_to_siblings          INT,

    -- Amount metrics
    total_amount_to_siblings    BIGINT,
    median_grant_size_to_siblings BIGINT,

    -- TARGET METRICS (core)
    target_grants_to_siblings   INT,           -- KEY METRIC
    target_first_grants         INT,           -- Target + first-time combo
    unknown_target_count        INT,           -- NULL is_target_grant count

    -- Geographic metrics
    client_state                VARCHAR(2),    -- For geo matching
    geo_grants_to_siblings      INT,           -- Grants to siblings in client_state
    target_geo_grants           INT,           -- Target grants in client_state

    -- GOLD STANDARD
    gold_standard_grants        INT,           -- Target + First + Geo (THE KEY METRIC)

    -- Recency
    most_recent_grant_year      INT,
    most_recent_target_year     INT,

    -- LASSO reference
    lasso_score                 NUMERIC(10,3),

    -- MANUAL RESEARCH FIELDS
    geo_eligible                BOOLEAN,       -- Do they fund CA or nationally?
    open_to_applicants          BOOLEAN,       -- Accept unsolicited applications?
    client_eligible             BOOLEAN,       -- Does client meet requirements?
    eligibility_notes           TEXT,          -- Budget limits, org type, geography
    has_active_opportunities    BOOLEAN,       -- Current RFP or open cycle?
    opportunity_notes           TEXT,          -- Deadlines, program names
    reviewed_at                 TIMESTAMP,

    computed_at                 TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (client_ein, foundation_ein)
);

-- Indexes for ranking
CREATE INDEX IF NOT EXISTS idx_scores_target_grants
    ON f990_2025.calc_client_foundation_scores(client_ein, target_grants_to_siblings DESC);
CREATE INDEX IF NOT EXISTS idx_scores_gold
    ON f990_2025.calc_client_foundation_scores(client_ein, gold_standard_grants DESC);
