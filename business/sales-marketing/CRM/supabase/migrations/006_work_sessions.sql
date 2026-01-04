-- Migration 006: Work Sessions (Time Tracking)
-- Date: 2026-01-02
-- Purpose: Track clock in/out, hours worked, calls made per session

-- Work sessions table
CREATE TABLE work_sessions (
    id SERIAL PRIMARY KEY,
    clock_in TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    clock_out TIMESTAMPTZ,
    planned_hours NUMERIC(4,2),
    planned_calls INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add work_session_id to calls table to link calls to sessions
ALTER TABLE calls ADD COLUMN work_session_id INTEGER REFERENCES work_sessions(id);

-- View to get session stats
CREATE OR REPLACE VIEW v_work_session_stats AS
SELECT
    ws.id,
    ws.clock_in,
    ws.clock_out,
    ws.planned_hours,
    ws.planned_calls,
    ws.notes,
    EXTRACT(EPOCH FROM (COALESCE(ws.clock_out, NOW()) - ws.clock_in)) / 3600 as actual_hours,
    COUNT(c.id) as calls_made,
    CASE
        WHEN EXTRACT(EPOCH FROM (COALESCE(ws.clock_out, NOW()) - ws.clock_in)) > 0
        THEN COUNT(c.id) / (EXTRACT(EPOCH FROM (COALESCE(ws.clock_out, NOW()) - ws.clock_in)) / 3600)
        ELSE 0
    END as calls_per_hour
FROM work_sessions ws
LEFT JOIN calls c ON c.work_session_id = ws.id
GROUP BY ws.id, ws.clock_in, ws.clock_out, ws.planned_hours, ws.planned_calls, ws.notes
ORDER BY ws.clock_in DESC;

-- Get active session (not clocked out)
CREATE OR REPLACE VIEW v_active_session AS
SELECT
    ws.*,
    EXTRACT(EPOCH FROM (NOW() - ws.clock_in)) as elapsed_seconds,
    COUNT(c.id) as calls_made
FROM work_sessions ws
LEFT JOIN calls c ON c.work_session_id = ws.id
WHERE ws.clock_out IS NULL
GROUP BY ws.id
ORDER BY ws.clock_in DESC
LIMIT 1;

-- Grant permissions
GRANT ALL ON work_sessions TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE work_sessions_id_seq TO anon, authenticated;
GRANT SELECT ON v_work_session_stats TO anon, authenticated;
GRANT SELECT ON v_active_session TO anon, authenticated;
