-- Migration: Add columns required by CRM mockups + Stripe integration
-- Date: 2026-03-14

-- ============================================================
-- ORGANIZATIONS: Stripe subscription fields
-- ============================================================

ALTER TABLE organizations ADD COLUMN stripe_customer_id TEXT;
ALTER TABLE organizations ADD COLUMN stripe_subscription_id TEXT UNIQUE;
ALTER TABLE organizations ADD COLUMN subscription_type VARCHAR(20)
  CHECK (subscription_type IN ('monthly', 'quarterly', 'annual'));
ALTER TABLE organizations ADD COLUMN subscription_status VARCHAR(20)
  CHECK (subscription_status IN ('active', 'past_due', 'canceled', 'pending_payment'));
ALTER TABLE organizations ADD COLUMN start_date DATE;
ALTER TABLE organizations ADD COLUMN next_payment_date DATE;

-- ============================================================
-- ORGANIZATIONS: Contact + follow-up fields
-- ============================================================

ALTER TABLE organizations ADD COLUMN contact_name TEXT;
ALTER TABLE organizations ADD COLUMN contact_email TEXT;
ALTER TABLE organizations ADD COLUMN last_contact_date DATE;
ALTER TABLE organizations ADD COLUMN next_followup_date DATE;
ALTER TABLE organizations ADD COLUMN next_followup_note TEXT;

-- ============================================================
-- ORGANIZATIONS: Financial + report tracking
-- ============================================================

ALTER TABLE organizations ADD COLUMN revenue BIGINT;
ALTER TABLE organizations ADD COLUMN reports_sent_count INT DEFAULT 0;

-- ============================================================
-- REPORTS: Additional metadata
-- ============================================================

ALTER TABLE reports ADD COLUMN report_name TEXT;
ALTER TABLE reports ADD COLUMN report_type VARCHAR(30)
  CHECK (report_type IN ('grant_report', 'viability_brief', 'contacts', 'additional_funders', 'legacy'));
ALTER TABLE reports ADD COLUMN file_url_html TEXT;
ALTER TABLE reports ADD COLUMN file_url_pdf TEXT;
ALTER TABLE reports ADD COLUMN is_draft BOOLEAN DEFAULT true;
ALTER TABLE reports ADD COLUMN delivered_at TIMESTAMPTZ;

-- ============================================================
-- MEETINGS: Additional metadata
-- ============================================================

ALTER TABLE meetings ADD COLUMN meeting_type VARCHAR(20)
  CHECK (meeting_type IN ('zoom', 'phone', 'google_meet', 'teams'));
ALTER TABLE meetings ADD COLUMN outcome VARCHAR(30)
  CHECK (outcome IN ('interested', 'reviewing', 'gave_referral', 'needs_info'));
ALTER TABLE meetings ADD COLUMN notes_markdown TEXT;
ALTER TABLE meetings ADD COLUMN next_followup_date DATE;

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_organizations_stripe_sub ON organizations(stripe_subscription_id) WHERE stripe_subscription_id IS NOT NULL;
CREATE INDEX idx_organizations_contact_email ON organizations(contact_email) WHERE contact_email IS NOT NULL;
CREATE INDEX idx_reports_type ON reports(report_type);
