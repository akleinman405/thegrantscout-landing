#!/usr/bin/env python3
"""
Add description and last_contacted_at columns to CRM prospects table.
Run this before enrich_descriptions.py
"""

import requests

SUPABASE_URL = 'https://qisbqmwtfzeiffgtlzpk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo'

# Note: Supabase REST API doesn't support DDL operations with anon key
# You'll need to run this SQL in Supabase SQL Editor:

SQL_MIGRATION = """
-- Add description column for org mission/purpose
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS description TEXT;

-- Add last_contacted_at to track when prospect was last contacted
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMPTZ;

-- Add call_count for quick reference
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS call_count INTEGER DEFAULT 0;

-- Create index for status filtering
CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status);

-- Update the call queue view to include new fields
CREATE OR REPLACE VIEW v_call_queue AS
SELECT
    p.*,
    (SELECT COUNT(*) FROM calls c WHERE c.prospect_id = p.id) as call_count
FROM prospects p
WHERE p.phone IS NOT NULL
  AND p.status IN ('not_contacted', 'contacted')
ORDER BY
    p.tier NULLS LAST,
    p.icp_score DESC NULLS LAST;
"""

print("=== CRM SCHEMA UPDATE ===\n")
print("Run this SQL in Supabase SQL Editor (https://supabase.com/dashboard):\n")
print("-" * 60)
print(SQL_MIGRATION)
print("-" * 60)
print("\nAfter running the SQL, execute enrich_descriptions.py to populate descriptions.")
