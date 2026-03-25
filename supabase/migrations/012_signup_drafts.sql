-- Migration: Create signup_drafts table for auto-saving questionnaire progress
-- Allows partial entries to be visible in admin, and account-based resume
-- Date: 2026-03-25

CREATE TABLE signup_drafts (
    id              BIGSERIAL PRIMARY KEY,
    draft_token     UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Progress tracking
    current_step    SMALLINT NOT NULL DEFAULT 1,
    status          VARCHAR(20) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'converted', 'abandoned')),

    -- Full form data as JSONB for flexibility
    form_data       JSONB NOT NULL DEFAULT '{}',

    -- Denormalized fields for admin dashboard queries
    org_name        TEXT,
    contact_name    TEXT,
    contact_email   TEXT,
    ein             VARCHAR(10),

    -- Link to subscriber after checkout
    subscriber_id   BIGINT REFERENCES subscribers(id) ON DELETE SET NULL,

    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ DEFAULT NOW() + INTERVAL '90 days'
);

CREATE INDEX idx_drafts_user_id ON signup_drafts(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_drafts_status ON signup_drafts(status);
CREATE INDEX idx_drafts_contact_email ON signup_drafts(contact_email);
CREATE INDEX idx_drafts_expires ON signup_drafts(expires_at) WHERE status = 'in_progress';

-- RLS (matching existing pattern — single-tenant, auth at app layer)
ALTER TABLE signup_drafts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access" ON signup_drafts FOR ALL USING (true) WITH CHECK (true);

-- Auto-update updated_at (reuse existing function from 001)
CREATE TRIGGER trg_signup_drafts_updated_at
  BEFORE UPDATE ON signup_drafts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
