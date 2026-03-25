-- Migration: Add locations column to organizations
-- Matches subscribers.locations format (JSONB array of {type, state, detail})
-- Date: 2026-03-25

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS locations JSONB DEFAULT '[]';
