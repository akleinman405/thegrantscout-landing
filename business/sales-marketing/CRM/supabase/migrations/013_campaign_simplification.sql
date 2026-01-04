-- Migration: 013_campaign_simplification.sql
-- Simplify campaigns view: Grant Scout only, add reply sentiment tracking
-- Date: 2026-01-02

-- ============================================
-- ADD REPLY SENTIMENT TO EMAIL_CONVERSATIONS
-- ============================================
ALTER TABLE email_conversations
ADD COLUMN IF NOT EXISTS reply_sentiment TEXT CHECK (
    reply_sentiment IN (
        'interested',       -- Expressed interest in learning more
        'not_interested',   -- Declined or unsubscribed
        'question',         -- Asked a question
        'meeting',          -- Scheduled or requested meeting
        'forwarded',        -- Forwarded to someone else
        'out_of_office',    -- Auto-reply
        'unclassified'      -- Not yet classified
    )
);

COMMENT ON COLUMN email_conversations.reply_sentiment IS 'Sentiment classification of inbound replies';

-- ============================================
-- UPDATE CAMPAIGN STATS VIEW
-- Grant Scout only (vertical = grant_alerts)
-- ============================================
DROP VIEW IF EXISTS v_campaign_stats CASCADE;
CREATE VIEW v_campaign_stats AS
SELECT
    -- Overall stats (Grant Scout only)
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

    -- Reply stats from email_conversations (inbound only)
    (SELECT COUNT(*) FROM email_conversations WHERE direction = 'inbound') as total_replies,
    (SELECT COUNT(*) FROM email_conversations WHERE direction = 'inbound' AND reply_sentiment = 'interested') as replies_interested,
    (SELECT COUNT(*) FROM email_conversations WHERE direction = 'inbound' AND reply_sentiment = 'not_interested') as replies_not_interested,
    (SELECT COUNT(*) FROM email_conversations WHERE direction = 'inbound' AND reply_sentiment = 'question') as replies_questions,
    (SELECT COUNT(*) FROM email_conversations WHERE direction = 'inbound' AND reply_sentiment = 'meeting') as replies_meeting,

    -- Calculated rates
    ROUND(100.0 * COUNT(CASE WHEN status = 'BOUNCED' THEN 1 END) / NULLIF(COUNT(*), 0), 1) as bounce_rate
FROM campaign_emails
WHERE vertical = 'grant_alerts';

-- ============================================
-- UPDATE RECENT ACTIVITY VIEW
-- Grant Scout only
-- ============================================
CREATE OR REPLACE VIEW v_campaign_recent AS
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
WHERE ce.vertical = 'grant_alerts'
ORDER BY ce.sent_at DESC
LIMIT 50;

-- ============================================
-- REPLY SENTIMENT SUMMARY VIEW
-- Shows breakdown of reply sentiments
-- ============================================
CREATE OR REPLACE VIEW v_reply_sentiment_summary AS
SELECT
    reply_sentiment,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days') as last_7_days,
    COUNT(*) FILTER (WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days') as last_30_days
FROM email_conversations
WHERE direction = 'inbound'
  AND reply_sentiment IS NOT NULL
GROUP BY reply_sentiment
ORDER BY count DESC;

-- Grant permissions
GRANT SELECT ON v_campaign_stats TO anon, authenticated;
GRANT SELECT ON v_campaign_recent TO anon, authenticated;
GRANT SELECT ON v_reply_sentiment_summary TO anon, authenticated;
