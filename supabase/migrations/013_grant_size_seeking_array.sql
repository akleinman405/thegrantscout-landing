-- Migration: Change grant_size_seeking from VARCHAR(50) to TEXT[]
-- Allows users to select multiple grant size ranges
-- Date: 2026-03-27

-- Convert existing single values to single-element arrays
ALTER TABLE subscribers
  ALTER COLUMN grant_size_seeking TYPE TEXT[]
  USING CASE
    WHEN grant_size_seeking IS NULL THEN NULL
    ELSE ARRAY[grant_size_seeking]
  END;
