-- Migration 003: Daily Call Queue System
-- Date: 2026-01-02
-- Purpose: Add views for daily call scheduling workflow

-- v_daily_call_queue: Prospects with scheduled call tasks
-- Used to show "Scheduled for Today/Date" section
CREATE OR REPLACE VIEW v_daily_call_queue AS
SELECT
    t.id as task_id,
    t.due_date as scheduled_date,
    t.description as task_description,
    t.completed as task_completed,
    p.id,
    p.org_name,
    p.ein,
    p.phone,
    p.email,
    p.website,
    p.contact_name,
    p.contact_title,
    p.linkedin_url,
    p.tier,
    p.segment,
    p.status,
    p.source_list_id,
    p.city,
    p.state,
    p.ntee_code,
    p.annual_budget,
    p.icp_score,
    p.notes,
    p.description,
    p.last_contacted_at,
    p.call_count,
    p.timezone,
    p.created_at,
    p.updated_at,
    sl.name as source_list_name,
    sl.criteria as source_criteria
FROM tasks t
JOIN prospects p ON t.prospect_id = p.id
LEFT JOIN source_lists sl ON p.source_list_id = sl.id
WHERE t.type = 'call'
  AND t.completed = FALSE
  AND p.phone IS NOT NULL
  AND p.phone != ''
ORDER BY t.due_date, p.tier NULLS LAST, p.icp_score DESC NULLS LAST;

-- v_called_today: Prospects called today (for "Called Today" section)
CREATE OR REPLACE VIEW v_called_today AS
SELECT
    p.id,
    p.org_name,
    p.ein,
    p.phone,
    p.email,
    p.website,
    p.contact_name,
    p.contact_title,
    p.tier,
    p.segment,
    p.status,
    p.city,
    p.state,
    p.description,
    p.timezone,
    c.id as call_id,
    c.outcome,
    c.interest,
    c.notes as call_notes,
    c.call_date,
    c.follow_up_date,
    c.duration_minutes
FROM prospects p
JOIN calls c ON c.prospect_id = p.id
WHERE c.call_date::date = CURRENT_DATE
ORDER BY c.call_date DESC;

-- Update dashboard stats to include scheduled calls for today
DROP VIEW IF EXISTS v_dashboard_stats;
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
    (SELECT COUNT(*) FROM tasks WHERE due_date <= CURRENT_DATE AND completed = FALSE) as overdue_tasks,
    (SELECT COUNT(*) FROM tasks WHERE due_date = CURRENT_DATE AND type = 'call' AND completed = FALSE) as scheduled_calls_today;

-- Grant permissions for Supabase anonymous access
GRANT SELECT ON v_daily_call_queue TO anon, authenticated;
GRANT SELECT ON v_called_today TO anon, authenticated;
GRANT SELECT ON v_dashboard_stats TO anon, authenticated;
