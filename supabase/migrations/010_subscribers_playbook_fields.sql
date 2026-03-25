-- Migration: Update subscribers table for playbook model
-- Replaces state/city with locations JSON, removes ntee_code/timeframe, adds report fields
-- Date: 2026-03-18

-- Add new columns
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS locations JSONB DEFAULT '[]';
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS report_count INTEGER DEFAULT 1;
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS report_recipients JSONB DEFAULT '[]';

-- Migrate existing state/city data into locations
UPDATE subscribers
SET locations = CASE
  WHEN state IS NOT NULL AND city IS NOT NULL THEN
    jsonb_build_array(jsonb_build_object('type', 'city', 'state', state, 'detail', city))
  WHEN state IS NOT NULL THEN
    jsonb_build_array(jsonb_build_object('type', 'state', 'state', state, 'detail', ''))
  ELSE '[]'::jsonb
END
WHERE locations = '[]'::jsonb OR locations IS NULL;

-- Drop old columns (after migration)
ALTER TABLE subscribers DROP COLUMN IF EXISTS state;
ALTER TABLE subscribers DROP COLUMN IF EXISTS city;
ALTER TABLE subscribers DROP COLUMN IF EXISTS ntee_code;
ALTER TABLE subscribers DROP COLUMN IF EXISTS timeframe;
