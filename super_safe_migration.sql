-- The Progress Method - Super Safe Migration with Dependency Handling
-- Run this in Supabase SQL Editor

-- =============================================================================
-- STEP 1: Discover all dependencies and table structure
-- =============================================================================

-- First, let's see what tables we have and their dependencies
SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND (ccu.table_name = 'users' OR tc.table_name = 'users')
ORDER BY tc.table_name;

-- Check what columns exist in users table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Check what columns exist in commitments table  
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'commitments' 
ORDER BY ordinal_position;

-- =============================================================================
-- STEP 2: Create backups of ALL existing tables
-- =============================================================================

-- Backup users and related tables
CREATE TABLE users_backup AS SELECT * FROM users;

-- Backup commitments
CREATE TABLE commitments_backup AS SELECT * FROM commitments;

-- Backup other dependent tables if they exist
DO $$
BEGIN
    -- Backup user_preferences if it exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_preferences') THEN
        EXECUTE 'CREATE TABLE user_preferences_backup AS SELECT * FROM user_preferences';
        RAISE NOTICE 'Backed up user_preferences table';
    END IF;
    
    -- Backup pod_matching_queue if it exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pod_matching_queue') THEN
        EXECUTE 'CREATE TABLE pod_matching_queue_backup AS SELECT * FROM pod_matching_queue';
        RAISE NOTICE 'Backed up pod_matching_queue table';
    END IF;
    
    -- Check for feedback table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'feedback') THEN
        EXECUTE 'CREATE TABLE feedback_backup AS SELECT * FROM feedback';
        RAISE NOTICE 'Backed up feedback table';
    END IF;
END $$;

-- =============================================================================
-- STEP 3: Add new columns to existing users table instead of replacing
-- =============================================================================

-- Add new columns to existing users table (safer approach)
DO $$
BEGIN
    -- Journey tracking columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_bot_interaction_at') THEN
        ALTER TABLE users ADD COLUMN first_bot_interaction_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added first_bot_interaction_at column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_commitment_at') THEN
        ALTER TABLE users ADD COLUMN first_commitment_at TIMESTAMPTZ;
        RAISE NOTICE 'Added first_commitment_at column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_pod_call_at') THEN
        ALTER TABLE users ADD COLUMN first_pod_call_at TIMESTAMPTZ;
        RAISE NOTICE 'Added first_pod_call_at column';
    END IF;
    
    -- Profile columns for pod matching
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'timezone') THEN
        ALTER TABLE users ADD COLUMN timezone TEXT;
        RAISE NOTICE 'Added timezone column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'goals_category') THEN
        ALTER TABLE users ADD COLUMN goals_category TEXT CHECK (goals_category IN ('health', 'business', 'personal', 'learning', 'relationships', 'finance'));
        RAISE NOTICE 'Added goals_category column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'experience_level') THEN
        ALTER TABLE users ADD COLUMN experience_level TEXT CHECK (experience_level IN ('beginner', 'intermediate', 'advanced'));
        RAISE NOTICE 'Added experience_level column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'preferred_meeting_style') THEN
        ALTER TABLE users ADD COLUMN preferred_meeting_style TEXT CHECK (preferred_meeting_style IN ('supportive', 'direct', 'mixed'));
        RAISE NOTICE 'Added preferred_meeting_style column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'strengths') THEN
        ALTER TABLE users ADD COLUMN strengths JSONB DEFAULT '[]'::jsonb;
        RAISE NOTICE 'Added strengths column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'help_needed') THEN
        ALTER TABLE users ADD COLUMN help_needed JSONB DEFAULT '[]'::jsonb;
        RAISE NOTICE 'Added help_needed column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'bio') THEN
        ALTER TABLE users ADD COLUMN bio TEXT;
        RAISE NOTICE 'Added bio column';
    END IF;
    
    -- Engagement metrics
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_commitments') THEN
        ALTER TABLE users ADD COLUMN total_commitments INTEGER DEFAULT 0;
        RAISE NOTICE 'Added total_commitments column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'completed_commitments') THEN
        ALTER TABLE users ADD COLUMN completed_commitments INTEGER DEFAULT 0;
        RAISE NOTICE 'Added completed_commitments column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'current_streak') THEN
        ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added current_streak column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'longest_streak') THEN
        ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added longest_streak column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_activity_at') THEN
        ALTER TABLE users ADD COLUMN last_activity_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added last_activity_at column';
    END IF;
    
    -- Settings
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'notification_preferences') THEN
        ALTER TABLE users ADD COLUMN notification_preferences JSONB DEFAULT '{
            "telegram": true,
            "email": true,
            "sms": false,
            "pod_reminders": true,
            "commitment_reminders": true,
            "weekly_summary": true
        }'::jsonb;
        RAISE NOTICE 'Added notification_preferences column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_active') THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
        RAISE NOTICE 'Added is_active column';
    END IF;
    
    -- Ensure id column is UUID (might already be)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'id') THEN
        ALTER TABLE users ADD COLUMN id UUID DEFAULT gen_random_uuid();
        RAISE NOTICE 'Added id column';
    END IF;
END $$;

-- Update existing user metrics based on actual commitment data
UPDATE users SET 
    total_commitments = COALESCE((
        SELECT COUNT(*) 
        FROM commitments 
        WHERE commitments.telegram_user_id = users.telegram_user_id
    ), 0),
    completed_commitments = COALESCE((
        SELECT COUNT(*) 
        FROM commitments 
        WHERE commitments.telegram_user_id = users.telegram_user_id 
        AND status = 'completed'
    ), 0),
    first_commitment_at = (
        SELECT MIN(created_at) 
        FROM commitments 
        WHERE commitments.telegram_user_id = users.telegram_user_id
    )
WHERE EXISTS (SELECT 1 FROM commitments WHERE commitments.telegram_user_id = users.telegram_user_id);

-- =============================================================================
-- STEP 4: Create new tables that don't conflict with existing ones
-- =============================================================================

-- User Roles Table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID, -- We'll add the foreign key constraint later
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

-- Add foreign key constraint for user_roles if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'user_roles' AND constraint_name = 'user_roles_user_id_fkey'
    ) THEN
        -- First ensure users have id column populated
        UPDATE users SET id = gen_random_uuid() WHERE id IS NULL;
        
        -- Add foreign key
        ALTER TABLE user_roles ADD CONSTRAINT user_roles_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        
        RAISE NOTICE 'Added foreign key constraint for user_roles';
    END IF;
END $$;

-- Give all existing users the 'unpaid' role
INSERT INTO user_roles (user_id, role_type)
SELECT id, 'unpaid' 
FROM users 
WHERE id IS NOT NULL
ON CONFLICT (user_id, role_type) DO NOTHING;

-- Pods Table
CREATE TABLE IF NOT EXISTS pods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    
    -- Schedule
    day_of_week INTEGER CHECK (day_of_week BETWEEN 1 AND 7),
    time_utc TIME,
    timezone TEXT,
    duration_minutes INTEGER DEFAULT 60,
    
    -- Meeting details
    zoom_link TEXT,
    zoom_meeting_id TEXT,
    zoom_password TEXT,
    calendar_event_id TEXT,
    
    -- Capacity
    max_members INTEGER DEFAULT 6,
    current_members INTEGER DEFAULT 0,
    
    -- Health metrics
    avg_attendance_rate DECIMAL(5,2) DEFAULT 0,
    avg_completion_rate DECIMAL(5,2) DEFAULT 0,
    member_satisfaction_score DECIMAL(3,2) DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'full', 'disbanded')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    next_meeting_at TIMESTAMPTZ,
    last_meeting_at TIMESTAMPTZ,
    
    -- Smart matching criteria
    target_goals_category TEXT,
    target_experience_level TEXT,
    target_timezone_range TEXT[] DEFAULT '{}',
    
    CONSTRAINT valid_members CHECK (current_members <= max_members),
    CONSTRAINT valid_satisfaction CHECK (member_satisfaction_score BETWEEN 0 AND 5)
);

-- Pod Memberships Table
CREATE TABLE IF NOT EXISTS pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    pod_id UUID,
    
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'left')),
    
    -- Individual metrics
    meetings_attended INTEGER DEFAULT 0,
    meetings_missed INTEGER DEFAULT 0,
    contribution_score DECIMAL(3,2) DEFAULT 0,
    peer_ratings JSONB DEFAULT '[]'::jsonb,
    
    -- Payment tracking
    monthly_payment_active BOOLEAN DEFAULT false,
    last_payment_at TIMESTAMPTZ,
    payment_amount DECIMAL(10,2),
    
    -- Notes
    admin_notes TEXT,
    member_notes TEXT,
    
    UNIQUE(user_id, pod_id),
    CONSTRAINT valid_contribution CHECK (contribution_score BETWEEN 0 AND 5)
);

-- Add foreign keys for pod_memberships
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'pod_memberships' AND constraint_name = 'pod_memberships_user_id_fkey'
    ) THEN
        ALTER TABLE pod_memberships ADD CONSTRAINT pod_memberships_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added user foreign key for pod_memberships';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'pod_memberships' AND constraint_name = 'pod_memberships_pod_id_fkey'
    ) THEN
        ALTER TABLE pod_memberships ADD CONSTRAINT pod_memberships_pod_id_fkey 
        FOREIGN KEY (pod_id) REFERENCES pods(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added pod foreign key for pod_memberships';
    END IF;
END $$;

-- Long Term Goals Table
CREATE TABLE IF NOT EXISTS long_term_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    
    title TEXT NOT NULL,
    description TEXT,
    target_completion_date DATE,
    category TEXT CHECK (category IN ('health', 'business', 'personal', 'learning', 'relationships', 'finance')),
    
    -- Progress tracking
    progress_percentage DECIMAL(5,2) DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    
    -- AI Context Building (ZEP-style)
    context_summary JSONB DEFAULT '{}'::jsonb,
    success_patterns JSONB DEFAULT '[]'::jsonb,
    struggle_patterns JSONB DEFAULT '[]'::jsonb,
    ai_recommendations JSONB DEFAULT '[]'::jsonb,
    
    -- Milestones
    milestones JSONB DEFAULT '[]'::jsonb,
    next_milestone TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_review_at TIMESTAMPTZ
);

-- Add foreign key for long_term_goals
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'long_term_goals' AND constraint_name = 'long_term_goals_user_id_fkey'
    ) THEN
        ALTER TABLE long_term_goals ADD CONSTRAINT long_term_goals_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added foreign key for long_term_goals';
    END IF;
END $$;

-- =============================================================================
-- STEP 5: Enhance existing commitments table instead of replacing
-- =============================================================================

-- Add new columns to existing commitments table
DO $$
BEGIN
    -- Add user_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'user_id') THEN
        ALTER TABLE commitments ADD COLUMN user_id UUID;
        
        -- Populate user_id from telegram_user_id
        UPDATE commitments SET user_id = (
            SELECT users.id 
            FROM users 
            WHERE users.telegram_user_id = commitments.telegram_user_id
        ) WHERE telegram_user_id IS NOT NULL;
        
        RAISE NOTICE 'Added and populated user_id column in commitments';
    END IF;
    
    -- Add other enhancement columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'category') THEN
        ALTER TABLE commitments ADD COLUMN category TEXT CHECK (category IN ('health', 'work', 'personal', 'learning', 'relationships', 'finance'));
        RAISE NOTICE 'Added category column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'difficulty_level') THEN
        ALTER TABLE commitments ADD COLUMN difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5);
        RAISE NOTICE 'Added difficulty_level column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'estimated_time_minutes') THEN
        ALTER TABLE commitments ADD COLUMN estimated_time_minutes INTEGER;
        RAISE NOTICE 'Added estimated_time_minutes column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'priority_level') THEN
        ALTER TABLE commitments ADD COLUMN priority_level TEXT DEFAULT 'medium' CHECK (priority_level IN ('low', 'medium', 'high'));
        RAISE NOTICE 'Added priority_level column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'due_date') THEN
        ALTER TABLE commitments ADD COLUMN due_date DATE;
        RAISE NOTICE 'Added due_date column to commitments';
    END IF;
    
    -- Context & Memory columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'related_long_term_goal_id') THEN
        ALTER TABLE commitments ADD COLUMN related_long_term_goal_id UUID;
        RAISE NOTICE 'Added related_long_term_goal_id column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'context_from_previous') THEN
        ALTER TABLE commitments ADD COLUMN context_from_previous JSONB DEFAULT '{}'::jsonb;
        RAISE NOTICE 'Added context_from_previous column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'ai_insights') THEN
        ALTER TABLE commitments ADD COLUMN ai_insights JSONB DEFAULT '{}'::jsonb;
        RAISE NOTICE 'Added ai_insights column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'success_factors') THEN
        ALTER TABLE commitments ADD COLUMN success_factors JSONB DEFAULT '[]'::jsonb;
        RAISE NOTICE 'Added success_factors column to commitments';
    END IF;
    
    -- Pod integration columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'shared_with_pod') THEN
        ALTER TABLE commitments ADD COLUMN shared_with_pod BOOLEAN DEFAULT false;
        RAISE NOTICE 'Added shared_with_pod column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'pod_id') THEN
        ALTER TABLE commitments ADD COLUMN pod_id UUID;
        RAISE NOTICE 'Added pod_id column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'pod_feedback') THEN
        ALTER TABLE commitments ADD COLUMN pod_feedback JSONB DEFAULT '[]'::jsonb;
        RAISE NOTICE 'Added pod_feedback column to commitments';
    END IF;
    
    -- Analytics columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'completion_time_minutes') THEN
        ALTER TABLE commitments ADD COLUMN completion_time_minutes INTEGER;
        RAISE NOTICE 'Added completion_time_minutes column to commitments';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commitments' AND column_name = 'reflection_notes') THEN
        ALTER TABLE commitments ADD COLUMN reflection_notes TEXT;
        RAISE NOTICE 'Added reflection_notes column to commitments';
    END IF;
END $$;

-- Add foreign key constraints for commitments
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'commitments' AND constraint_name = 'commitments_user_id_fkey'
    ) THEN
        ALTER TABLE commitments ADD CONSTRAINT commitments_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added user foreign key for commitments';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'commitments' AND constraint_name = 'commitments_pod_id_fkey'
    ) THEN
        ALTER TABLE commitments ADD CONSTRAINT commitments_pod_id_fkey 
        FOREIGN KEY (pod_id) REFERENCES pods(id);
        RAISE NOTICE 'Added pod foreign key for commitments';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'commitments' AND constraint_name = 'commitments_related_long_term_goal_id_fkey'
    ) THEN
        ALTER TABLE commitments ADD CONSTRAINT commitments_related_long_term_goal_id_fkey 
        FOREIGN KEY (related_long_term_goal_id) REFERENCES long_term_goals(id);
        RAISE NOTICE 'Added long term goal foreign key for commitments';
    END IF;
END $$;

-- =============================================================================
-- STEP 6: Create remaining new tables
-- =============================================================================

-- Meetings Table
CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID,
    
    scheduled_at TIMESTAMPTZ NOT NULL,
    actual_start_at TIMESTAMPTZ,
    actual_end_at TIMESTAMPTZ,
    duration_minutes INTEGER DEFAULT 60,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'in_progress')),
    
    -- Attendance
    attendees JSONB DEFAULT '[]'::jsonb,
    absent_members JSONB DEFAULT '[]'::jsonb,
    attendance_count INTEGER DEFAULT 0,
    expected_attendance INTEGER DEFAULT 0,
    
    -- Content
    agenda JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    action_items JSONB DEFAULT '[]'::jsonb,
    commitments_shared JSONB DEFAULT '[]'::jsonb,
    
    -- Engagement metrics
    member_ratings JSONB DEFAULT '{}'::jsonb,
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    overall_satisfaction DECIMAL(3,2),
    
    -- Meeting artifacts
    recording_url TEXT,
    transcript TEXT,
    summary TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add foreign key for meetings
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'meetings' AND constraint_name = 'meetings_pod_id_fkey'
    ) THEN
        ALTER TABLE meetings ADD CONSTRAINT meetings_pod_id_fkey 
        FOREIGN KEY (pod_id) REFERENCES pods(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added foreign key for meetings';
    END IF;
END $$;

-- Automation Tables
CREATE TABLE IF NOT EXISTS automation_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    
    -- Triggers
    trigger_type TEXT NOT NULL CHECK (trigger_type IN (
        'new_user', 'pod_joined', 'payment_made', 'first_commitment', 
        'streak_milestone', 'missed_meeting', 'goal_completed',
        'inactive_user', 'referral_made'
    )),
    trigger_conditions JSONB DEFAULT '{}'::jsonb,
    
    -- Sequence configuration
    steps JSONB NOT NULL,
    
    -- Settings
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5,
    max_executions_per_user INTEGER,
    
    -- Analytics
    total_started INTEGER DEFAULT 0,
    total_completed INTEGER DEFAULT 0,
    avg_completion_rate DECIMAL(5,2) DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);

CREATE TABLE IF NOT EXISTS sequence_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    sequence_id UUID,
    
    current_step INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'paused', 'cancelled')),
    
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    next_step_at TIMESTAMPTZ,
    
    execution_log JSONB DEFAULT '[]'::jsonb,
    error_details JSONB,
    
    -- Context for personalization
    execution_context JSONB DEFAULT '{}'::jsonb
);

-- Add foreign keys for automation tables
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'automation_sequences' AND constraint_name = 'automation_sequences_created_by_fkey'
    ) THEN
        ALTER TABLE automation_sequences ADD CONSTRAINT automation_sequences_created_by_fkey 
        FOREIGN KEY (created_by) REFERENCES users(id);
        RAISE NOTICE 'Added foreign key for automation_sequences';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'sequence_executions' AND constraint_name = 'sequence_executions_user_id_fkey'
    ) THEN
        ALTER TABLE sequence_executions ADD CONSTRAINT sequence_executions_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added user foreign key for sequence_executions';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'sequence_executions' AND constraint_name = 'sequence_executions_sequence_id_fkey'
    ) THEN
        ALTER TABLE sequence_executions ADD CONSTRAINT sequence_executions_sequence_id_fkey 
        FOREIGN KEY (sequence_id) REFERENCES automation_sequences(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added sequence foreign key for sequence_executions';
    END IF;
END $$;

-- =============================================================================
-- STEP 7: Create indexes for performance (only if they don't exist)
-- =============================================================================

-- Helper function to create index if not exists
CREATE OR REPLACE FUNCTION create_index_if_not_exists(index_name TEXT, table_name TEXT, definition TEXT)
RETURNS VOID AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c 
        JOIN pg_namespace n ON n.oid = c.relnamespace 
        WHERE c.relname = index_name AND n.nspname = 'public'
    ) THEN
        EXECUTE 'CREATE INDEX ' || index_name || ' ON ' || table_name || ' ' || definition;
        RAISE NOTICE 'Created index: %', index_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create indexes
SELECT create_index_if_not_exists('idx_users_telegram_id', 'users', '(telegram_user_id)');
SELECT create_index_if_not_exists('idx_users_active', 'users', '(is_active) WHERE is_active = true');
SELECT create_index_if_not_exists('idx_users_timezone', 'users', '(timezone)');
SELECT create_index_if_not_exists('idx_users_last_activity', 'users', '(last_activity_at)');

SELECT create_index_if_not_exists('idx_user_roles_user_id', 'user_roles', '(user_id)');
SELECT create_index_if_not_exists('idx_user_roles_type', 'user_roles', '(role_type)');

SELECT create_index_if_not_exists('idx_commitments_user', 'commitments', '(user_id)');
SELECT create_index_if_not_exists('idx_commitments_status', 'commitments', '(status)');
SELECT create_index_if_not_exists('idx_commitments_created', 'commitments', '(created_at DESC)');

-- Drop the helper function
DROP FUNCTION create_index_if_not_exists;

-- =============================================================================
-- STEP 8: Create KPI Views (replace if they exist)
-- =============================================================================

-- Bot Usage KPI
CREATE OR REPLACE VIEW kpi_bot_usage AS
SELECT 
    COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '7 days' THEN id END) as weekly_active_users,
    COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '30 days' THEN id END) as monthly_active_users,
    COUNT(*) as total_users,
    (COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '7 days' THEN id END) * 100.0 / NULLIF(COUNT(*), 0)) as weekly_active_percentage,
    COALESCE(AVG(current_streak), 0) as avg_current_streak
FROM users
WHERE is_active = true;

-- New Users KPI
CREATE OR REPLACE VIEW kpi_new_users AS
SELECT 
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 day') as new_users_today,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as new_users_this_week,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days') as new_users_this_month,
    COUNT(*) FILTER (WHERE first_commitment_at IS NOT NULL AND created_at > NOW() - INTERVAL '7 days') as activated_users_this_week,
    (COUNT(*) FILTER (WHERE first_commitment_at IS NOT NULL AND created_at > NOW() - INTERVAL '7 days') * 100.0 / 
     NULLIF(COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days'), 0)) as activation_rate
FROM users;

-- Commitment Fulfillment KPI  
CREATE OR REPLACE VIEW kpi_commitment_fulfillment AS
SELECT 
    COUNT(*) FILTER (WHERE status = 'completed' AND created_at > NOW() - INTERVAL '7 days') as completed_this_week,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as total_this_week,
    (COUNT(*) FILTER (WHERE status = 'completed' AND created_at > NOW() - INTERVAL '7 days') * 100.0 / 
     NULLIF(COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days'), 0)) as weekly_completion_rate,
    
    COALESCE(AVG(u.completed_commitments * 100.0 / NULLIF(u.total_commitments, 0)), 0) as overall_completion_rate,
    COALESCE(AVG(u.current_streak), 0) as avg_current_streak,
    COALESCE(MAX(u.longest_streak), 0) as max_streak_achieved
FROM commitments c
RIGHT JOIN users u ON c.user_id = u.id
WHERE u.is_active = true;

-- Pod Health KPI (will show zeros until pods are created)
CREATE OR REPLACE VIEW kpi_pod_health AS
SELECT 
    COALESCE(COUNT(*) FILTER (WHERE status = 'active'), 0) as active_pods,
    COALESCE(AVG(avg_attendance_rate), 0) as avg_health_score,
    COALESCE(COUNT(*) FILTER (WHERE avg_attendance_rate >= 80), 0) as healthy_pods,
    COALESCE(COUNT(*) FILTER (WHERE avg_attendance_rate < 60), 0) as struggling_pods,
    COALESCE(AVG(avg_attendance_rate), 0) as overall_attendance,
    COALESCE(SUM(current_members), 0) as total_pod_members
FROM pods;

-- Pod Attendance KPI (will show zeros until meetings exist)
CREATE OR REPLACE VIEW kpi_pod_attendance AS
SELECT 
    COALESCE(AVG(attendance_count * 100.0 / NULLIF(expected_attendance, 0)), 0) as overall_attendance_rate,
    COUNT(*) as total_meetings_this_week,
    COUNT(*) FILTER (WHERE (attendance_count * 100.0 / NULLIF(expected_attendance, 0)) >= 80) as high_attendance_meetings,
    COALESCE(AVG(overall_satisfaction), 0) as avg_satisfaction
FROM meetings 
WHERE scheduled_at > NOW() - INTERVAL '7 days'
  AND status = 'completed';

-- =============================================================================
-- STEP 9: Create utility functions
-- =============================================================================

-- Function to check user roles
CREATE OR REPLACE FUNCTION user_has_role(user_uuid UUID, role_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles 
        WHERE user_id = user_uuid 
        AND role_type = role_name 
        AND is_active = true
        AND (expires_at IS NULL OR expires_at > NOW())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to grant role to user
CREATE OR REPLACE FUNCTION grant_user_role(user_uuid UUID, role_name TEXT, granted_by_uuid UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO user_roles (user_id, role_type, granted_by)
    VALUES (user_uuid, role_name, granted_by_uuid)
    ON CONFLICT (user_id, role_type) 
    DO UPDATE SET is_active = true, expires_at = NULL, granted_at = NOW();
    
    RETURN true;
EXCEPTION WHEN OTHERS THEN
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update user metrics
CREATE OR REPLACE FUNCTION update_user_metrics(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users SET 
        total_commitments = (SELECT COUNT(*) FROM commitments WHERE user_id = user_uuid),
        completed_commitments = (SELECT COUNT(*) FROM commitments WHERE user_id = user_uuid AND status = 'completed'),
        last_activity_at = NOW()
    WHERE id = user_uuid;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- STEP 10: Create triggers
-- =============================================================================

-- Drop trigger if exists, then recreate
DROP TRIGGER IF EXISTS update_user_metrics_trigger ON commitments;

-- Trigger to update user metrics when commitments change
CREATE OR REPLACE FUNCTION trigger_update_user_metrics()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM update_user_metrics(OLD.user_id);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM update_user_metrics(NEW.user_id);
        IF OLD.user_id != NEW.user_id THEN
            PERFORM update_user_metrics(OLD.user_id);
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        PERFORM update_user_metrics(NEW.user_id);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_metrics_trigger
    AFTER INSERT OR UPDATE OR DELETE ON commitments
    FOR EACH ROW EXECUTE FUNCTION trigger_update_user_metrics();

-- =============================================================================
-- STEP 11: Enable Row Level Security
-- =============================================================================

-- Enable RLS on new tables (existing tables may already have it)
DO $$
BEGIN
    -- Enable RLS on all tables
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE pods ENABLE ROW LEVEL SECURITY;
    ALTER TABLE pod_memberships ENABLE ROW LEVEL SECURITY;
    ALTER TABLE commitments ENABLE ROW LEVEL SECURITY;
    ALTER TABLE long_term_goals ENABLE ROW LEVEL SECURITY;
    ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
    ALTER TABLE automation_sequences ENABLE ROW LEVEL SECURITY;
    ALTER TABLE sequence_executions ENABLE ROW LEVEL SECURITY;
    
    RAISE NOTICE 'Enabled Row Level Security on all tables';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'RLS enabling completed with some warnings (may already be enabled)';
END $$;

-- Create service role policies (drop and recreate to avoid conflicts)
DO $$
BEGIN
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Service role full access" ON users;
    DROP POLICY IF EXISTS "Service role full access" ON user_roles;
    DROP POLICY IF EXISTS "Service role full access" ON pods;
    DROP POLICY IF EXISTS "Service role full access" ON pod_memberships;
    DROP POLICY IF EXISTS "Service role full access" ON commitments;
    DROP POLICY IF EXISTS "Service role full access" ON long_term_goals;
    DROP POLICY IF EXISTS "Service role full access" ON meetings;
    DROP POLICY IF EXISTS "Service role full access" ON automation_sequences;
    DROP POLICY IF EXISTS "Service role full access" ON sequence_executions;
    
    -- Create new policies
    CREATE POLICY "Service role full access" ON users FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON user_roles FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON pods FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON pod_memberships FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON commitments FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON long_term_goals FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON meetings FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON automation_sequences FOR ALL TO service_role USING (true);
    CREATE POLICY "Service role full access" ON sequence_executions FOR ALL TO service_role USING (true);
    
    RAISE NOTICE 'Created service role policies';
END $$;

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =============================================================================
-- STEP 12: Final verification and cleanup
-- =============================================================================

-- Update user metrics for all existing users
SELECT update_user_metrics(id) FROM users WHERE id IS NOT NULL;

-- Show final table counts
SELECT 
    'users' as table_name,
    COUNT(*) as row_count,
    'Enhanced with new columns' as status
FROM users
UNION ALL
SELECT 
    'user_roles' as table_name,
    COUNT(*) as row_count,
    'New table created' as status
FROM user_roles
UNION ALL
SELECT 
    'commitments' as table_name,
    COUNT(*) as row_count,
    'Enhanced with new columns' as status
FROM commitments
UNION ALL
SELECT 
    'pods' as table_name,
    COUNT(*) as row_count,
    'New table created' as status
FROM pods
UNION ALL
SELECT 
    'pod_memberships' as table_name,
    COUNT(*) as row_count,
    'New table created' as status
FROM pod_memberships
UNION ALL
SELECT 
    'long_term_goals' as table_name,
    COUNT(*) as row_count,
    'New table created' as status
FROM long_term_goals
ORDER BY table_name;

-- Show user role distribution
SELECT 
    role_type,
    COUNT(*) as user_count
FROM user_roles
WHERE is_active = true
GROUP BY role_type
ORDER BY user_count DESC;

SELECT 'Super safe migration completed successfully! 🎉' as final_status;