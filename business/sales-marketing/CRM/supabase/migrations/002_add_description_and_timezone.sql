-- Migration: Add description, timezone, and last_contacted_at columns
-- Date: 2026-01-02

-- Add description column for f990 mission/activity descriptions
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS description TEXT;

-- Add last_contacted_at for tracking contact history
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMPTZ;

-- Add call_count for quick reference
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS call_count INTEGER DEFAULT 0;

-- Create function to derive timezone from state
CREATE OR REPLACE FUNCTION get_timezone_from_state(state_code VARCHAR(2))
RETURNS TEXT AS $$
BEGIN
    RETURN CASE state_code
        -- Pacific
        WHEN 'CA' THEN 'Pacific'
        WHEN 'WA' THEN 'Pacific'
        WHEN 'OR' THEN 'Pacific'
        WHEN 'NV' THEN 'Pacific'
        -- Mountain
        WHEN 'AZ' THEN 'Mountain'
        WHEN 'CO' THEN 'Mountain'
        WHEN 'NM' THEN 'Mountain'
        WHEN 'UT' THEN 'Mountain'
        WHEN 'WY' THEN 'Mountain'
        WHEN 'MT' THEN 'Mountain'
        WHEN 'ID' THEN 'Mountain'
        -- Central
        WHEN 'TX' THEN 'Central'
        WHEN 'IL' THEN 'Central'
        WHEN 'MN' THEN 'Central'
        WHEN 'WI' THEN 'Central'
        WHEN 'IA' THEN 'Central'
        WHEN 'MO' THEN 'Central'
        WHEN 'AR' THEN 'Central'
        WHEN 'LA' THEN 'Central'
        WHEN 'MS' THEN 'Central'
        WHEN 'AL' THEN 'Central'
        WHEN 'TN' THEN 'Central'
        WHEN 'KY' THEN 'Central'
        WHEN 'KS' THEN 'Central'
        WHEN 'NE' THEN 'Central'
        WHEN 'SD' THEN 'Central'
        WHEN 'ND' THEN 'Central'
        WHEN 'OK' THEN 'Central'
        -- Eastern
        WHEN 'NY' THEN 'Eastern'
        WHEN 'PA' THEN 'Eastern'
        WHEN 'NJ' THEN 'Eastern'
        WHEN 'CT' THEN 'Eastern'
        WHEN 'MA' THEN 'Eastern'
        WHEN 'RI' THEN 'Eastern'
        WHEN 'NH' THEN 'Eastern'
        WHEN 'VT' THEN 'Eastern'
        WHEN 'ME' THEN 'Eastern'
        WHEN 'OH' THEN 'Eastern'
        WHEN 'MI' THEN 'Eastern'
        WHEN 'IN' THEN 'Eastern'
        WHEN 'WV' THEN 'Eastern'
        WHEN 'VA' THEN 'Eastern'
        WHEN 'NC' THEN 'Eastern'
        WHEN 'SC' THEN 'Eastern'
        WHEN 'GA' THEN 'Eastern'
        WHEN 'FL' THEN 'Eastern'
        WHEN 'MD' THEN 'Eastern'
        WHEN 'DE' THEN 'Eastern'
        WHEN 'DC' THEN 'Eastern'
        -- Alaska/Hawaii
        WHEN 'AK' THEN 'Alaska'
        WHEN 'HI' THEN 'Hawaii'
        ELSE NULL
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add computed timezone column (or use function in queries)
-- For simplicity, we'll add a trigger to set timezone on insert/update

ALTER TABLE prospects ADD COLUMN IF NOT EXISTS timezone TEXT;

-- Update existing prospects with timezone
UPDATE prospects SET timezone = get_timezone_from_state(state) WHERE state IS NOT NULL;

-- Create trigger to auto-set timezone
CREATE OR REPLACE FUNCTION set_prospect_timezone()
RETURNS TRIGGER AS $$
BEGIN
    NEW.timezone := get_timezone_from_state(NEW.state);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prospects_set_timezone ON prospects;
CREATE TRIGGER prospects_set_timezone
    BEFORE INSERT OR UPDATE OF state ON prospects
    FOR EACH ROW
    EXECUTE FUNCTION set_prospect_timezone();

-- Update last_contacted_at from calls
UPDATE prospects p
SET last_contacted_at = (
    SELECT MAX(call_date) FROM calls WHERE prospect_id = p.id
)
WHERE EXISTS (SELECT 1 FROM calls WHERE prospect_id = p.id);

-- Update call_count from calls
UPDATE prospects p
SET call_count = (
    SELECT COUNT(*) FROM calls WHERE prospect_id = p.id
);

-- Create trigger to update last_contacted_at and call_count on new call
CREATE OR REPLACE FUNCTION update_prospect_contact_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE prospects
    SET last_contacted_at = NEW.call_date,
        call_count = COALESCE(call_count, 0) + 1
    WHERE id = NEW.prospect_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS calls_update_contact_stats ON calls;
CREATE TRIGGER calls_update_contact_stats
    AFTER INSERT ON calls
    FOR EACH ROW
    EXECUTE FUNCTION update_prospect_contact_stats();

-- Index for efficient timezone queries
CREATE INDEX IF NOT EXISTS idx_prospects_timezone ON prospects(timezone);
CREATE INDEX IF NOT EXISTS idx_prospects_last_contacted ON prospects(last_contacted_at);
