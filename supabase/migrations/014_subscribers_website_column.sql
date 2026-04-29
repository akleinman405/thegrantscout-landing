-- Migration: Document website column on subscribers
-- The column was added directly in Supabase Studio in late April 2026 with no
-- corresponding migration. This file backfills the migration history so a fresh
-- rebuild matches production. No-op if the column already exists.
-- Date: 2026-04-28

ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS website TEXT;
