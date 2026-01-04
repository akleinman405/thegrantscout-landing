-- Migration 005: Dashboard Metrics Functions
-- Date: 2026-01-02
-- Purpose: Add functions for conversion metrics with time and segment filtering

-- Function to get dashboard metrics with filters
CREATE OR REPLACE FUNCTION get_dashboard_metrics(
    p_days INTEGER DEFAULT 30,
    p_segment TEXT DEFAULT NULL
)
RETURNS TABLE (
    total_calls BIGINT,
    calls_no_answer BIGINT,
    calls_vm_left BIGINT,
    calls_talked BIGINT,
    calls_reached_dm BIGINT,
    calls_email_request BIGINT,
    calls_wrong_disconnected BIGINT,
    prospects_contacted BIGINT,
    prospects_interested BIGINT,
    prospects_converted BIGINT,
    avg_calls_to_talk NUMERIC,
    avg_calls_to_interest NUMERIC,
    avg_calls_to_convert NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH call_stats AS (
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE c.outcome = 'no_answer') as no_answer,
            COUNT(*) FILTER (WHERE c.outcome = 'vm_left') as vm_left,
            COUNT(*) FILTER (WHERE c.outcome IN ('talked_to_someone', 'reached_decision_maker')) as talked,
            COUNT(*) FILTER (WHERE c.outcome = 'reached_decision_maker') as dm,
            COUNT(*) FILTER (WHERE c.outcome = 'sent_email_request') as email_req,
            COUNT(*) FILTER (WHERE c.outcome IN ('wrong_number', 'disconnected')) as wrong_disc
        FROM calls c
        JOIN prospects p ON c.prospect_id = p.id
        WHERE c.call_date >= CURRENT_DATE - (p_days || ' days')::INTERVAL
          AND (p_segment IS NULL OR p.segment = p_segment)
    ),
    prospect_stats AS (
        SELECT
            COUNT(DISTINCT c.prospect_id) FILTER (WHERE c.outcome IN ('talked_to_someone', 'reached_decision_maker')) as contacted,
            COUNT(DISTINCT p.id) FILTER (WHERE p.status = 'interested') as interested,
            COUNT(DISTINCT p.id) FILTER (WHERE p.status = 'converted') as converted
        FROM calls c
        JOIN prospects p ON c.prospect_id = p.id
        WHERE c.call_date >= CURRENT_DATE - (p_days || ' days')::INTERVAL
          AND (p_segment IS NULL OR p.segment = p_segment)
    ),
    conversion_metrics AS (
        SELECT
            -- Avg calls to get someone on the phone
            CASE WHEN ps.contacted > 0
                THEN ROUND(cs.total::NUMERIC / ps.contacted, 1)
                ELSE 0 END as calls_per_talk,
            -- Avg calls to get interest
            CASE WHEN ps.interested > 0
                THEN ROUND(cs.total::NUMERIC / ps.interested, 1)
                ELSE 0 END as calls_per_interest,
            -- Avg calls to convert
            CASE WHEN ps.converted > 0
                THEN ROUND(cs.total::NUMERIC / ps.converted, 1)
                ELSE 0 END as calls_per_convert
        FROM call_stats cs, prospect_stats ps
    )
    SELECT
        cs.total,
        cs.no_answer,
        cs.vm_left,
        cs.talked,
        cs.dm,
        cs.email_req,
        cs.wrong_disc,
        ps.contacted,
        ps.interested,
        ps.converted,
        cm.calls_per_talk,
        cm.calls_per_interest,
        cm.calls_per_convert
    FROM call_stats cs, prospect_stats ps, conversion_metrics cm;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION get_dashboard_metrics(INTEGER, TEXT) TO anon, authenticated;

-- Also create a simpler view for quick stats by segment
CREATE OR REPLACE VIEW v_call_outcomes_by_segment AS
SELECT
    p.segment,
    DATE(c.call_date) as call_day,
    c.outcome,
    COUNT(*) as call_count
FROM calls c
JOIN prospects p ON c.prospect_id = p.id
WHERE c.call_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.segment, DATE(c.call_date), c.outcome
ORDER BY call_day DESC, p.segment, c.outcome;

GRANT SELECT ON v_call_outcomes_by_segment TO anon, authenticated;
