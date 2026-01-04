-- TheGrantScout CRM - Initial Schema
-- Version: 1.0
-- Date: 2025-12-31

-- ============================================
-- SOURCE LISTS
-- Track why prospects were pulled
-- ============================================
CREATE TABLE source_lists (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    criteria TEXT,                -- Why these prospects were pulled
    file_origin TEXT,             -- Original CSV filename
    record_count INTEGER,
    segment TEXT CHECK(segment IN ('nonprofit', 'foundation', 'foundation_mgmt')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

COMMENT ON TABLE source_lists IS 'Tracks prospect sources - which list, criteria, and origin file';
COMMENT ON COLUMN source_lists.segment IS 'Default segment for prospects imported from this list';

-- ============================================
-- PROSPECTS
-- Master list of all contacts
-- ============================================
CREATE TABLE prospects (
    id SERIAL PRIMARY KEY,
    org_name TEXT NOT NULL,
    ein VARCHAR(20),              -- Preserve leading zeros
    phone TEXT,
    email TEXT,
    website TEXT,
    contact_name TEXT,
    contact_title TEXT,
    linkedin_url TEXT,            -- Useful for research
    tier INTEGER,                 -- Foundation mgmt tier ranking (1-7)
    segment TEXT CHECK(segment IN ('nonprofit', 'foundation', 'foundation_mgmt')),
    status TEXT DEFAULT 'not_contacted' CHECK(status IN (
        'not_contacted', 'contacted', 'interested', 'not_interested', 'converted'
    )),
    source_list_id INTEGER REFERENCES source_lists(id),
    city TEXT,
    state VARCHAR(2),
    ntee_code VARCHAR(10),
    annual_budget BIGINT,
    icp_score INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE prospects IS 'Master prospect list - nonprofits, foundations, and foundation mgmt contacts';
COMMENT ON COLUMN prospects.tier IS 'Foundation mgmt tier ranking (1=highest, 7=lowest)';
COMMENT ON COLUMN prospects.status IS 'Pipeline status: not_contacted → contacted → interested → converted/not_interested';

-- ============================================
-- CALLS
-- Call activity log
-- ============================================
CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    call_date TIMESTAMPTZ DEFAULT NOW(),
    outcome TEXT CHECK(outcome IN (
        'vm_left',
        'talked_to_someone',
        'reached_decision_maker',
        'sent_email_request',
        'no_answer',
        'wrong_number',
        'disconnected'
    )),
    interest TEXT CHECK(interest IN ('yes', 'no', 'maybe', 'uncertain')),
    duration_minutes INTEGER,     -- Optional call length
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE calls IS 'Call activity log with outcomes and follow-up tracking';

-- ============================================
-- EMAILS
-- Email outreach tracking
-- ============================================
CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    sent_date TIMESTAMPTZ DEFAULT NOW(),
    direction TEXT DEFAULT 'outbound' CHECK(direction IN ('outbound', 'inbound')),
    subject TEXT,
    body_preview TEXT,            -- First 500 chars
    response_date TIMESTAMPTZ,    -- When they replied
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE emails IS 'Email outreach tracking - sent and received';

-- ============================================
-- TASKS
-- Unified follow-up tracking
-- ============================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    due_date DATE NOT NULL,
    type TEXT DEFAULT 'call' CHECK(type IN ('call', 'email', 'meeting', 'other')),
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tasks IS 'Unified follow-up tasks across calls, emails, and other activities';

-- ============================================
-- PIPELINE
-- Deal/opportunity tracking (optional)
-- ============================================
CREATE TABLE pipeline (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER UNIQUE NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    stage TEXT CHECK(stage IN ('lead', 'beta', 'negotiating', 'paying', 'churned')),
    value INTEGER,                -- Expected revenue
    expected_close DATE,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE pipeline IS 'Sales pipeline stages and deal values';

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_prospects_status ON prospects(status);
CREATE INDEX idx_prospects_segment ON prospects(segment);
CREATE INDEX idx_prospects_source ON prospects(source_list_id);
CREATE INDEX idx_prospects_state ON prospects(state);
CREATE INDEX idx_prospects_ein ON prospects(ein) WHERE ein IS NOT NULL;

CREATE INDEX idx_calls_prospect ON calls(prospect_id);
CREATE INDEX idx_calls_date ON calls(call_date);
CREATE INDEX idx_calls_followup ON calls(follow_up_date) WHERE follow_up_date IS NOT NULL;

CREATE INDEX idx_emails_prospect ON emails(prospect_id);
CREATE INDEX idx_emails_date ON emails(sent_date);

CREATE INDEX idx_tasks_due ON tasks(due_date) WHERE completed = FALSE;
CREATE INDEX idx_tasks_prospect ON tasks(prospect_id);
CREATE INDEX idx_tasks_incomplete ON tasks(completed) WHERE completed = FALSE;

CREATE INDEX idx_pipeline_stage ON pipeline(stage);

-- ============================================
-- TRIGGERS
-- ============================================

-- Auto-update updated_at on prospects
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prospects_updated_at
    BEFORE UPDATE ON prospects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER pipeline_updated_at
    BEFORE UPDATE ON pipeline
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Auto-update prospect status when call is logged
CREATE OR REPLACE FUNCTION update_prospect_status_on_call()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if prospect is still 'not_contacted'
    UPDATE prospects
    SET status = 'contacted',
        updated_at = NOW()
    WHERE id = NEW.prospect_id
      AND status = 'not_contacted';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calls_update_prospect_status
    AFTER INSERT ON calls
    FOR EACH ROW
    EXECUTE FUNCTION update_prospect_status_on_call();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Permissive for single-user personal CRM
-- ============================================

-- Enable RLS on all tables
ALTER TABLE source_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline ENABLE ROW LEVEL SECURITY;

-- Permissive policies (allow all operations for anon role)
CREATE POLICY "Allow all access to source_lists" ON source_lists FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to prospects" ON prospects FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to calls" ON calls FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to emails" ON emails FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to tasks" ON tasks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access to pipeline" ON pipeline FOR ALL USING (true) WITH CHECK (true);

-- ============================================
-- VIEWS
-- Convenience views for common queries
-- ============================================

-- Prospects with their latest call info
CREATE VIEW v_prospect_summary AS
SELECT
    p.*,
    sl.name as source_list_name,
    c.call_date as last_call_date,
    c.outcome as last_call_outcome,
    c.notes as last_call_notes,
    (SELECT COUNT(*) FROM calls WHERE prospect_id = p.id) as call_count,
    (SELECT COUNT(*) FROM emails WHERE prospect_id = p.id) as email_count
FROM prospects p
LEFT JOIN source_lists sl ON p.source_list_id = sl.id
LEFT JOIN LATERAL (
    SELECT call_date, outcome, notes
    FROM calls
    WHERE prospect_id = p.id
    ORDER BY call_date DESC
    LIMIT 1
) c ON true;

-- Today's follow-ups
CREATE VIEW v_todays_followups AS
SELECT
    t.*,
    p.org_name,
    p.contact_name,
    p.phone,
    p.email,
    p.segment
FROM tasks t
JOIN prospects p ON t.prospect_id = p.id
WHERE t.due_date <= CURRENT_DATE
  AND t.completed = FALSE
ORDER BY t.due_date, t.type;

-- Call queue: not_contacted prospects ordered by priority
CREATE VIEW v_call_queue AS
SELECT
    p.*,
    sl.name as source_list_name,
    sl.criteria as source_criteria
FROM prospects p
LEFT JOIN source_lists sl ON p.source_list_id = sl.id
WHERE p.status = 'not_contacted'
  AND p.phone IS NOT NULL
  AND p.phone != ''
ORDER BY
    p.tier NULLS LAST,
    p.icp_score DESC NULLS LAST,
    p.created_at;

-- Dashboard stats
CREATE VIEW v_dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM prospects) as total_prospects,
    (SELECT COUNT(*) FROM prospects WHERE status = 'not_contacted') as not_contacted,
    (SELECT COUNT(*) FROM prospects WHERE status = 'contacted') as contacted,
    (SELECT COUNT(*) FROM prospects WHERE status = 'interested') as interested,
    (SELECT COUNT(*) FROM prospects WHERE status = 'converted') as converted,
    (SELECT COUNT(*) FROM prospects WHERE status = 'not_interested') as not_interested,
    (SELECT COUNT(*) FROM calls WHERE call_date >= CURRENT_DATE) as calls_today,
    (SELECT COUNT(*) FROM calls WHERE call_date >= CURRENT_DATE - INTERVAL '7 days') as calls_this_week,
    (SELECT COUNT(*) FROM tasks WHERE due_date <= CURRENT_DATE AND completed = FALSE) as overdue_tasks;

-- Grant access to views
GRANT SELECT ON v_prospect_summary TO anon, authenticated;
GRANT SELECT ON v_todays_followups TO anon, authenticated;
GRANT SELECT ON v_call_queue TO anon, authenticated;
GRANT SELECT ON v_dashboard_stats TO anon, authenticated;
