-- Phase 2: Add target_grant_purpose column to dim_clients
-- Purpose: Store the synthesized grant purpose for semantic matching
-- Usage: Run once to add the column

-- Add column if it doesn't exist
ALTER TABLE f990_2025.dim_clients
ADD COLUMN IF NOT EXISTS target_grant_purpose TEXT;

-- Add comment explaining the column
COMMENT ON COLUMN f990_2025.dim_clients.target_grant_purpose IS
'Synthesized grant purpose text for semantic matching. Written to sound like how a funder would describe a grant to this client. Used in Step 3.2.2 for semantic similarity against actual grant purposes.';

-- Verify column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'f990_2025'
AND table_name = 'dim_clients'
AND column_name = 'target_grant_purpose';
