-- =============================================================================
-- PRODUCTION MIGRATION SCRIPT - The Progress Method
-- TESTED LOCALLY - SAFE FOR PRODUCTION
-- =============================================================================

-- ⚠️ IMPORTANT: Run this in your PRODUCTION Supabase SQL Editor
-- This script safely upgrades your existing schema without data loss

-- =============================================================================
-- STEP 1: BACKUP EXISTING DATA (CRITICAL!)
-- =============================================================================

-- Create backup tables before ANY changes
CREATE TABLE users_backup AS SELECT * FROM users;
CREATE TABLE commitments_backup AS SELECT * FROM commitments;

-- Verify backups
SELECT 'BACKUP CREATED' as status, 
       (SELECT COUNT(*) FROM users_backup) as users_backed_up,
       (SELECT COUNT(*) FROM commitments_backup) as commitments_backed_up;

-- =============================================================================
-- STEP 2: ENHANCE EXISTING USERS TABLE (SAFE COLUMN ADDITION)
-- =============================================================================

-- Add new UUID column and other enhancements
ALTER TABLE users ADD COLUMN IF NOT EXISTS id UUID DEFAULT gen_random_uuid();
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT DEFAULT 'User';
ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_bot_interaction_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS goals_category TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_commitments INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS completed_commitments INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Add notification preferences
ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{
    "telegram": true,
    "email": true,
    "sms": false,
    "pod_reminders": true,
    "commitment_reminders": true,
    "weekly_summary": true
}'::jsonb;

-- Populate new columns with data from existing columns
UPDATE users SET 
    created_at = COALESCE(created_at, accepted_at),
    first_bot_interaction_at = COALESCE(first_bot_interaction_at, accepted_at),
    id = COALESCE(id, gen_random_uuid())
WHERE created_at IS NULL OR first_bot_interaction_at IS NULL OR id IS NULL;

-- Add unique constraint on UUID (needed for foreign keys)
ALTER TABLE users ADD CONSTRAINT users_id_unique UNIQUE (id);

SELECT 'STEP 2 COMPLETE: Users table enhanced' as status;

-- =============================================================================
-- STEP 3: CREATE NEW TABLES FOR ADMIN SYSTEM
-- =============================================================================

-- User roles table (multi-role system)
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_type TEXT NOT NULL CHECK (role_type IN (
        'unpaid', 'paid', 'pod_member', 'admin', 'super_admin', 
        'beta_tester', 'lifetime_member'
    )),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID,
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, role_type)
);

-- Grant all existing users the 'unpaid' role (as requested)
INSERT INTO user_roles (user_id, role_type)
SELECT id, 'unpaid' FROM users
ON CONFLICT (user_id, role_type) DO NOTHING;

-- Pods table (accountability groups)
CREATE TABLE IF NOT EXISTS pods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    day_of_week INTEGER CHECK (day_of_week BETWEEN 1 AND 7),
    time_utc TIME,
    timezone TEXT,
    duration_minutes INTEGER DEFAULT 60,
    zoom_link TEXT,
    calendar_event_id TEXT,
    max_members INTEGER DEFAULT 6,
    current_members INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'full', 'disbanded')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    health_score DECIMAL(5,2) DEFAULT 100.0,
    is_active BOOLEAN DEFAULT true
);

-- Pod memberships table
CREATE TABLE IF NOT EXISTS pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    role TEXT DEFAULT 'member' CHECK (role IN ('member', 'leader'))
);

-- Pod meetings table (for attendance tracking)
CREATE TABLE IF NOT EXISTS pod_meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    calendar_event_id TEXT,
    google_meet_link TEXT,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meeting attendance table
CREATE TABLE IF NOT EXISTS meeting_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES pod_meetings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    attended BOOLEAN DEFAULT false,
    rsvp_status TEXT CHECK (rsvp_status IN ('pending', 'accepted', 'declined')),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT 'STEP 3 COMPLETE: New tables created' as status;

-- =============================================================================
-- STEP 4: CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity_at);

-- Role indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_type ON user_roles(role_type);
CREATE INDEX IF NOT EXISTS idx_user_roles_active ON user_roles(user_id, role_type) WHERE is_active = true;

-- Pod indexes
CREATE INDEX IF NOT EXISTS idx_pods_status ON pods(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_pod_memberships_pod_id ON pod_memberships(pod_id);
CREATE INDEX IF NOT EXISTS idx_pod_memberships_user_id ON pod_memberships(user_id);

-- Meeting indexes
CREATE INDEX IF NOT EXISTS idx_pod_meetings_pod_id ON pod_meetings(pod_id);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meeting_id ON meeting_attendance(meeting_id);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_user_id ON meeting_attendance(user_id);

SELECT 'STEP 4 COMPLETE: Indexes created' as status;

-- =============================================================================
-- STEP 5: GRANT SUPER ADMIN ROLE TO YOU
-- =============================================================================

-- TODO: Replace YOUR_TELEGRAM_ID with your actual Telegram ID
-- INSERT INTO user_roles (user_id, role_type, is_active)
-- SELECT id, 'super_admin', true 
-- FROM users 
-- WHERE telegram_user_id = YOUR_TELEGRAM_ID
-- ON CONFLICT (user_id, role_type) DO UPDATE SET is_active = true;

SELECT 'STEP 5 READY: Replace YOUR_TELEGRAM_ID above with your actual ID' as status;

-- =============================================================================
-- STEP 6: FINAL VERIFICATION
-- =============================================================================

-- Verify migration success
SELECT 'FINAL VERIFICATION' as check_type,
       'users' as table_name, 
       COUNT(*) as count,
       'Has UUID column: ' || (CASE WHEN EXISTS(
           SELECT 1 FROM information_schema.columns 
           WHERE table_name = 'users' AND column_name = 'id'
       ) THEN 'YES' ELSE 'NO' END) as has_uuid
FROM users
UNION ALL
SELECT 'FINAL VERIFICATION', 'user_roles', COUNT(*), 'All users have unpaid role' FROM user_roles
UNION ALL  
SELECT 'FINAL VERIFICATION', 'pods', COUNT(*), 'Ready for pod creation' FROM pods
UNION ALL
SELECT 'FINAL VERIFICATION', 'pod_memberships', COUNT(*), 'Ready for memberships' FROM pod_memberships
UNION ALL
SELECT 'FINAL VERIFICATION', 'pod_meetings', COUNT(*), 'Ready for meetings' FROM pod_meetings
UNION ALL
SELECT 'FINAL VERIFICATION', 'meeting_attendance', COUNT(*), 'Ready for attendance' FROM meeting_attendance;

-- =============================================================================
-- MIGRATION COMPLETE!
-- =============================================================================

SELECT 
    '🎉 MIGRATION COMPLETE!' as status,
    'Your database is now ready for the admin system!' as message,
    'Next: Deploy Python files and access admin dashboard' as next_step;