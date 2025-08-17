-- First Impression Experience Schema Migration
-- Adds columns to track the detailed first impression user journey

-- Add new columns to users table for first impression tracking
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS onboarding_started_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS first_impression_started_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS first_commitment_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS first_celebration_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS bigger_goal_collected_at TIMESTAMPTZ;

-- Add index for performance on first impression tracking
CREATE INDEX IF NOT EXISTS idx_users_first_impression_started_at ON users(first_impression_started_at);
CREATE INDEX IF NOT EXISTS idx_users_first_commitment_at ON users(first_commitment_at);

-- Add column to commitments table to track first commitments
ALTER TABLE commitments 
ADD COLUMN IF NOT EXISTS is_first_commitment BOOLEAN DEFAULT FALSE;

-- Create index for first commitment queries
CREATE INDEX IF NOT EXISTS idx_commitments_is_first_commitment ON commitments(is_first_commitment) WHERE is_first_commitment = TRUE;

-- Update existing first commitments (optional - for historical data)
-- This identifies users' first commitments based on creation order
WITH first_commitments AS (
  SELECT DISTINCT ON (telegram_user_id) 
    id,
    telegram_user_id
  FROM commitments 
  ORDER BY telegram_user_id, created_at ASC
)
UPDATE commitments 
SET is_first_commitment = TRUE 
WHERE id IN (SELECT id FROM first_commitments)
AND is_first_commitment IS NOT TRUE; -- Only update if not already marked

-- Add comment for documentation
COMMENT ON COLUMN users.onboarding_started_at IS 'When user first started any onboarding process';
COMMENT ON COLUMN users.first_impression_started_at IS 'When user started the 100x first impression experience';
COMMENT ON COLUMN users.first_commitment_at IS 'When user created their very first commitment';
COMMENT ON COLUMN users.first_celebration_at IS 'When user completed their first commitment and got celebration';
COMMENT ON COLUMN users.bigger_goal_collected_at IS 'When user provided their bigger goal during progressive onboarding';
COMMENT ON COLUMN commitments.is_first_commitment IS 'Marks if this was the users first ever commitment';