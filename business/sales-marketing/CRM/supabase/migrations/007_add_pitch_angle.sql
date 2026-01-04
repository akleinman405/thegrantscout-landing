-- Migration: Add pitch_angle column for personalized sales approach
-- Date: 2026-01-02

-- Add pitch_angle column for storing personalized approach/why interested
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS pitch_angle TEXT;

COMMENT ON COLUMN prospects.pitch_angle IS 'Personalized pitch angle - why this prospect would be especially interested in our services';

-- Index for prospects with pitch angles (useful for prioritizing researched leads)
CREATE INDEX IF NOT EXISTS idx_prospects_has_pitch ON prospects((pitch_angle IS NOT NULL));
