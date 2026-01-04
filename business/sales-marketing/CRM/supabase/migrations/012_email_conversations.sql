-- Migration: 012_email_conversations.sql
-- Phase 2: Email Conversation Visibility
-- Stores full email threads synced from Gmail

-- Email conversations table
CREATE TABLE IF NOT EXISTS email_conversations (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER REFERENCES prospects(id) ON DELETE CASCADE,
    email_address TEXT NOT NULL,
    gmail_message_id TEXT UNIQUE,  -- Gmail message ID for deduplication
    gmail_thread_id TEXT,          -- Gmail thread ID for grouping
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    subject TEXT,
    body_preview TEXT,             -- First 500 chars of body
    sent_at TIMESTAMPTZ NOT NULL,
    synced_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    from_email TEXT,
    to_email TEXT,
    is_reply BOOLEAN DEFAULT FALSE,
    is_bounce BOOLEAN DEFAULT FALSE
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_email_conversations_prospect
    ON email_conversations(prospect_id);
CREATE INDEX IF NOT EXISTS idx_email_conversations_email
    ON email_conversations(email_address);
CREATE INDEX IF NOT EXISTS idx_email_conversations_thread
    ON email_conversations(gmail_thread_id);
CREATE INDEX IF NOT EXISTS idx_email_conversations_sent
    ON email_conversations(sent_at DESC);

-- View: Get conversation threads for a prospect
CREATE OR REPLACE VIEW v_prospect_conversations AS
SELECT
    ec.id,
    ec.prospect_id,
    p.org_name,
    p.contact_name,
    ec.email_address,
    ec.gmail_thread_id,
    ec.direction,
    ec.subject,
    ec.body_preview,
    ec.sent_at,
    ec.from_email,
    ec.to_email,
    ec.is_reply,
    ec.is_bounce
FROM email_conversations ec
LEFT JOIN prospects p ON ec.prospect_id = p.id
ORDER BY ec.sent_at DESC;

-- View: Conversation summary per prospect
CREATE OR REPLACE VIEW v_prospect_conversation_summary AS
SELECT
    prospect_id,
    COUNT(*) as total_emails,
    COUNT(*) FILTER (WHERE direction = 'outbound') as emails_sent,
    COUNT(*) FILTER (WHERE direction = 'inbound') as emails_received,
    COUNT(DISTINCT gmail_thread_id) as thread_count,
    MAX(sent_at) FILTER (WHERE direction = 'outbound') as last_sent,
    MAX(sent_at) FILTER (WHERE direction = 'inbound') as last_received,
    BOOL_OR(is_reply) as has_replied
FROM email_conversations
WHERE prospect_id IS NOT NULL
GROUP BY prospect_id;

-- View: Recent conversations across all prospects
CREATE OR REPLACE VIEW v_recent_conversations AS
SELECT
    ec.id,
    ec.prospect_id,
    p.org_name,
    ec.email_address,
    ec.direction,
    ec.subject,
    ec.body_preview,
    ec.sent_at,
    ec.is_reply
FROM email_conversations ec
LEFT JOIN prospects p ON ec.prospect_id = p.id
ORDER BY ec.sent_at DESC
LIMIT 50;

-- Enable RLS
ALTER TABLE email_conversations ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (single user)
CREATE POLICY "Allow all access to email_conversations"
    ON email_conversations FOR ALL
    USING (true)
    WITH CHECK (true);

-- Comment
COMMENT ON TABLE email_conversations IS 'Email conversation history synced from Gmail - Phase 2 of CRM integration';
