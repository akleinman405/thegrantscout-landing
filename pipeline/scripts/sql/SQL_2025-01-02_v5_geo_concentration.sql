-- SQL_2025-01-02_v5_geo_concentration.sql
-- Create geographic concentration table for V5 model
-- Run manually: psql -h localhost -U postgres -d thegrantscout -f this_file.sql

SET search_path TO f990_2025;

-- Drop if exists
DROP TABLE IF EXISTS calc_foundation_geo_concentration;

-- Create from existing features (fast approach)
CREATE TABLE calc_foundation_geo_concentration AS
SELECT
    ein as foundation_ein,
    states_funded::integer,
    in_state_grant_pct as primary_state_pct,
    -- Approximate HHI based on in-state concentration
    CASE
        WHEN states_funded IS NULL OR states_funded = 0 THEN NULL
        WHEN states_funded = 1 THEN 1.0
        ELSE ROUND((in_state_grant_pct * in_state_grant_pct +
                   (1.0 - in_state_grant_pct) * (1.0 - in_state_grant_pct) / NULLIF(states_funded - 1, 0))::numeric, 4)
    END as geo_hhi,
    CASE WHEN in_state_grant_pct >= 0.80 THEN TRUE ELSE FALSE END as is_geo_concentrated
FROM calc_foundation_features
WHERE has_grant_history = TRUE;

-- Add index
CREATE INDEX idx_fgc_ein ON calc_foundation_geo_concentration(foundation_ein);
CREATE INDEX idx_fgc_concentrated ON calc_foundation_geo_concentration(is_geo_concentrated);

-- Verify
SELECT
    COUNT(*) as total_foundations,
    SUM(CASE WHEN is_geo_concentrated THEN 1 ELSE 0 END) as concentrated,
    ROUND(AVG(geo_hhi)::numeric, 3) as avg_hhi
FROM calc_foundation_geo_concentration;
