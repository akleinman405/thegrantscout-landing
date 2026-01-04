-- Fix dashboard stats view to include scheduled_calls_today
-- Date: 2026-01-02

-- Drop existing view
DROP VIEW IF EXISTS v_dashboard_stats;

-- Recreate with scheduled_calls_today
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

-- Grant access
GRANT SELECT ON v_dashboard_stats TO anon, authenticated;
