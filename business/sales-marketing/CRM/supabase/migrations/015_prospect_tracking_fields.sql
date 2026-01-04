-- Migration: 015_prospect_tracking_fields.sql
-- Date: 2026-01-03
-- Purpose: Add tracking fields for email/call activity, do-not-contact, and 990 enrichment

-- =====================================================
-- OUTREACH TRACKING
-- =====================================================

-- Email count (how many emails sent to this prospect)
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS email_count INTEGER DEFAULT 0;

-- Last email date
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS last_email_date TIMESTAMPTZ;

-- Last call date (call_count already exists)
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS last_call_date TIMESTAMPTZ;

-- =====================================================
-- DO NOT CONTACT
-- =====================================================

-- Master do-not-contact flag
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS do_not_contact BOOLEAN DEFAULT FALSE;

-- Reason: 'unsubscribed', 'bounced', 'requested', 'invalid_email', 'wrong_number'
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS do_not_contact_reason TEXT;

-- When they were added to do-not-contact list
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS do_not_contact_date TIMESTAMPTZ;

-- =====================================================
-- ENRICHMENT FROM 990 DATA
-- =====================================================

-- Mission statement from nonprofit_returns
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS mission_statement TEXT;

-- Sector description (e.g., "Education", "Human Services")
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS sector TEXT;

-- NTEE code description
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS ntee_description TEXT;

-- =====================================================
-- NEXT ACTION DECISIONING
-- =====================================================

-- Recommended next action: 'call', 'email', 'wait', 'none'
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS next_action TEXT;

-- When to take next action
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS next_action_date DATE;

-- Why this action (e.g., "Follow-up after voicemail", "Initial outreach")
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS next_action_reason TEXT;

-- =====================================================
-- EMAIL ENRICHMENT TRACKING
-- =====================================================

-- Where email came from: 'scraped', '990', 'manual', 'enrichment_api'
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS email_source TEXT;

-- When email was scraped/added
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS email_enriched_at TIMESTAMPTZ;

-- =====================================================
-- NEW ICP SCORING FIELDS
-- =====================================================

-- New ICP score (0-100) based on updated model
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_score_v2 INTEGER;

-- Component scores for transparency
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_base_score INTEGER;      -- 0-40: Organization fit
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_channel_score INTEGER;   -- 0-30: Reachability
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_readiness_score INTEGER; -- 0-30: Conversion likelihood

-- Scoring model version
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_model_version TEXT DEFAULT 'v2';

-- When score was last calculated
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS icp_scored_at TIMESTAMPTZ;

-- =====================================================
-- INDEXES
-- =====================================================

-- Index for do-not-contact filtering
CREATE INDEX IF NOT EXISTS idx_prospects_do_not_contact ON prospects(do_not_contact) WHERE do_not_contact = TRUE;

-- Index for next action queue
CREATE INDEX IF NOT EXISTS idx_prospects_next_action ON prospects(next_action, next_action_date) WHERE next_action IS NOT NULL;

-- Index for new ICP score
CREATE INDEX IF NOT EXISTS idx_prospects_icp_v2 ON prospects(icp_score_v2 DESC NULLS LAST);

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Do Not Contact List
CREATE OR REPLACE VIEW v_do_not_contact AS
SELECT
    id,
    org_name,
    email,
    phone,
    do_not_contact_reason,
    do_not_contact_date
FROM prospects
WHERE do_not_contact = TRUE;

-- View: Next Actions Queue
CREATE OR REPLACE VIEW v_next_actions AS
SELECT
    p.*,
    CASE
        WHEN p.do_not_contact THEN 'DO NOT CONTACT'
        WHEN p.email IS NOT NULL AND COALESCE(p.email_count, 0) = 0 THEN 'First Email'
        WHEN p.email IS NOT NULL AND COALESCE(p.email_count, 0) = 1 THEN 'Follow-up Email'
        WHEN p.phone IS NOT NULL AND COALESCE(p.call_count, 0) = 0 THEN 'First Call'
        WHEN p.phone IS NOT NULL AND COALESCE(p.call_count, 0) > 0 THEN 'Follow-up Call'
        ELSE 'Need Enrichment'
    END as recommended_action
FROM prospects p
WHERE p.status NOT IN ('converted', 'not_interested')
  AND COALESCE(p.do_not_contact, FALSE) = FALSE;

-- View: High Priority Prospects (new ICP v2)
CREATE OR REPLACE VIEW v_high_priority AS
SELECT *
FROM prospects
WHERE icp_score_v2 >= 65
  AND COALESCE(do_not_contact, FALSE) = FALSE
  AND status NOT IN ('converted', 'not_interested')
ORDER BY icp_score_v2 DESC;

COMMENT ON VIEW v_do_not_contact IS 'Prospects who should not be contacted';
COMMENT ON VIEW v_next_actions IS 'Prospects with recommended next actions';
COMMENT ON VIEW v_high_priority IS 'High-scoring prospects ready for outreach';
