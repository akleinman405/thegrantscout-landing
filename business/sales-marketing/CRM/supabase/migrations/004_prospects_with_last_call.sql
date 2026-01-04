-- Migration 004: Prospects with Last Call View
-- Date: 2026-01-02
-- Purpose: Add view showing prospects with their most recent call info

-- v_prospects_with_last_call: All prospects with last call details
CREATE OR REPLACE VIEW v_prospects_with_last_call AS
SELECT
    p.*,
    lc.call_date as last_call_date,
    lc.outcome as last_call_outcome,
    lc.notes as last_call_notes,
    lc.interest as last_call_interest
FROM prospects p
LEFT JOIN LATERAL (
    SELECT c.call_date, c.outcome, c.notes, c.interest
    FROM calls c
    WHERE c.prospect_id = p.id
    ORDER BY c.call_date DESC
    LIMIT 1
) lc ON true
ORDER BY p.org_name;

-- Grant permissions
GRANT SELECT ON v_prospects_with_last_call TO anon, authenticated;
