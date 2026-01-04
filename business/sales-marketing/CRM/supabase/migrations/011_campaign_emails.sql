-- Campaign Emails Integration
-- Stores email campaign activity synced from sent_tracker.csv
-- Date: 2026-01-02

-- ============================================
-- CAMPAIGN EMAILS TABLE
-- Stores all campaign email sends with status
-- ============================================
CREATE TABLE campaign_emails (
    id SERIAL PRIMARY KEY,
    email_address TEXT NOT NULL,
    prospect_id INTEGER REFERENCES prospects(id) ON DELETE SET NULL,
    vertical TEXT NOT NULL,                 -- grant_alerts, debarment, food_recall
    message_type TEXT NOT NULL,             -- initial, followup
    subject_line TEXT,
    status TEXT NOT NULL,                   -- SUCCESS, BOUNCED, FAILED
    error_message TEXT,
    sender_email TEXT,
    sent_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(email_address, sent_at)          -- Prevent duplicate syncs
);

COMMENT ON TABLE campaign_emails IS 'Email campaign sends synced from sent_tracker.csv';

-- Indexes
CREATE INDEX idx_campaign_emails_email ON campaign_emails(email_address);
CREATE INDEX idx_campaign_emails_prospect ON campaign_emails(prospect_id);
CREATE INDEX idx_campaign_emails_status ON campaign_emails(status);
CREATE INDEX idx_campaign_emails_vertical ON campaign_emails(vertical);
CREATE INDEX idx_campaign_emails_sent ON campaign_emails(sent_at);

-- ============================================
-- CAMPAIGN STATS VIEW
-- Aggregate stats for dashboard
-- ============================================
CREATE VIEW v_campaign_stats AS
SELECT
    -- Overall stats
    COUNT(*) as total_emails,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as sent_success,
    COUNT(CASE WHEN status = 'BOUNCED' THEN 1 END) as bounced,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,

    -- By message type
    COUNT(CASE WHEN message_type = 'initial' AND status = 'SUCCESS' THEN 1 END) as initial_sent,
    COUNT(CASE WHEN message_type = 'followup' AND status = 'SUCCESS' THEN 1 END) as followup_sent,

    -- Recent activity
    COUNT(CASE WHEN sent_at >= CURRENT_DATE - INTERVAL '7 days' AND status = 'SUCCESS' THEN 1 END) as sent_last_7_days,
    COUNT(CASE WHEN sent_at >= CURRENT_DATE - INTERVAL '30 days' AND status = 'SUCCESS' THEN 1 END) as sent_last_30_days,

    -- Unique recipients
    COUNT(DISTINCT email_address) as unique_recipients,
    COUNT(DISTINCT CASE WHEN prospect_id IS NOT NULL THEN prospect_id END) as linked_prospects,

    -- Reply stats (from emails table - inbound)
    (SELECT COUNT(*) FROM emails WHERE direction = 'inbound') as total_replies,

    -- Calculated rates
    ROUND(100.0 * COUNT(CASE WHEN status = 'BOUNCED' THEN 1 END) / NULLIF(COUNT(*), 0), 1) as bounce_rate
FROM campaign_emails;

-- ============================================
-- CAMPAIGN STATS BY VERTICAL VIEW
-- Stats broken down by vertical (grant_alerts, etc.)
-- ============================================
CREATE VIEW v_campaign_stats_by_vertical AS
SELECT
    vertical,
    COUNT(*) as total_emails,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as sent_success,
    COUNT(CASE WHEN status = 'BOUNCED' THEN 1 END) as bounced,
    COUNT(CASE WHEN message_type = 'initial' AND status = 'SUCCESS' THEN 1 END) as initial_sent,
    COUNT(CASE WHEN message_type = 'followup' AND status = 'SUCCESS' THEN 1 END) as followup_sent,
    COUNT(DISTINCT email_address) as unique_recipients,
    ROUND(100.0 * COUNT(CASE WHEN status = 'BOUNCED' THEN 1 END) / NULLIF(COUNT(*), 0), 1) as bounce_rate
FROM campaign_emails
GROUP BY vertical
ORDER BY sent_success DESC;

-- ============================================
-- RECENT CAMPAIGN ACTIVITY VIEW
-- Recent email sends for activity feed
-- ============================================
CREATE VIEW v_campaign_recent AS
SELECT
    ce.id,
    ce.email_address,
    ce.vertical,
    ce.message_type,
    ce.subject_line,
    ce.status,
    ce.sent_at,
    p.id as prospect_id,
    p.org_name as prospect_org_name,
    p.contact_name as prospect_contact_name
FROM campaign_emails ce
LEFT JOIN prospects p ON ce.prospect_id = p.id
ORDER BY ce.sent_at DESC
LIMIT 50;

-- ============================================
-- PROSPECT CAMPAIGN HISTORY VIEW
-- Show campaign emails for each prospect
-- ============================================
CREATE VIEW v_prospect_campaign_emails AS
SELECT
    p.id as prospect_id,
    p.org_name,
    p.email,
    ce.vertical,
    ce.message_type,
    ce.status,
    ce.sent_at,
    ce.subject_line
FROM prospects p
LEFT JOIN campaign_emails ce ON p.id = ce.prospect_id OR LOWER(p.email) = LOWER(ce.email_address)
WHERE ce.id IS NOT NULL
ORDER BY p.id, ce.sent_at DESC;

-- ============================================
-- RLS & PERMISSIONS
-- ============================================
ALTER TABLE campaign_emails ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access to campaign_emails" ON campaign_emails FOR ALL USING (true) WITH CHECK (true);

GRANT SELECT ON v_campaign_stats TO anon, authenticated;
GRANT SELECT ON v_campaign_stats_by_vertical TO anon, authenticated;
GRANT SELECT ON v_campaign_recent TO anon, authenticated;
GRANT SELECT ON v_prospect_campaign_emails TO anon, authenticated;
GRANT ALL ON campaign_emails TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE campaign_emails_id_seq TO anon, authenticated;
