-- Migration 014: Queue Redesign - Day-by-day cold calling queue
-- Date: 2026-01-02
-- Purpose: Support day-by-day queue with First Contact vs Follow-up filtering

-- Add call_type column to tasks table to distinguish first contact vs follow-up
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS call_type TEXT CHECK (call_type IN ('first_contact', 'follow_up'));

-- Update existing call tasks based on prospect call history
UPDATE tasks t
SET call_type = CASE
    WHEN EXISTS (SELECT 1 FROM calls c WHERE c.prospect_id = t.prospect_id) THEN 'follow_up'
    ELSE 'first_contact'
END
WHERE t.type = 'call' AND t.call_type IS NULL;

-- Set default for new tasks
ALTER TABLE tasks ALTER COLUMN call_type SET DEFAULT 'first_contact';

-- Create enhanced daily queue view with call_type
DROP VIEW IF EXISTS v_daily_call_queue CASCADE;
CREATE VIEW v_daily_call_queue AS
SELECT
    t.id as task_id,
    t.due_date as scheduled_date,
    t.description as task_description,
    t.completed as task_completed,
    COALESCE(t.call_type,
        CASE WHEN p.call_count > 0 THEN 'follow_up' ELSE 'first_contact' END
    ) as call_type,
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
    p.pitch_angle,
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

-- Grant permissions
GRANT SELECT ON v_daily_call_queue TO anon, authenticated;

-- Create a function to reschedule a task
CREATE OR REPLACE FUNCTION reschedule_task(task_id_param UUID, new_date DATE)
RETURNS VOID AS $$
BEGIN
    UPDATE tasks
    SET due_date = new_date, updated_at = NOW()
    WHERE id = task_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION reschedule_task TO anon, authenticated;
