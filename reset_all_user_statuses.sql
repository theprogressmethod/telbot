-- Reset All User Statuses for First Impression Experience
-- This ensures everyone gets the new 100x onboarding experience

-- Reset all users to trigger first impression flow
UPDATE users 
SET 
    status = NULL,
    total_commitments = 0,
    first_impression_started_at = NULL,
    first_commitment_at = NULL,
    first_celebration_at = NULL,
    bigger_goal_collected_at = NULL,
    onboarding_started_at = NULL
WHERE status IS NOT NULL OR total_commitments > 0;

-- Clear first commitment markers so everyone gets the celebration
UPDATE commitments 
SET is_first_commitment = FALSE 
WHERE is_first_commitment = TRUE;

-- Clear any FSM states that might be stuck
-- Note: FSM states are handled in memory/Redis, not database

-- Optional: Reset goal fields to allow re-collection
UPDATE users 
SET goal_90_days = NULL 
WHERE goal_90_days IS NOT NULL;

-- Show summary of changes
SELECT 
    'Users reset' as action,
    COUNT(*) as count
FROM users 
WHERE status IS NULL;

SELECT 
    'Commitments unmarked' as action, 
    COUNT(*) as count
FROM commitments 
WHERE is_first_commitment = FALSE;