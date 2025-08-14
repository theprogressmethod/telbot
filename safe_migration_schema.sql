-- The Progress Method - Safe Database Migration
-- Run this in Supabase SQL Editor

-- First, let's check what columns exist in the current users table
-- Then do a safe migration

-- =============================================================================
-- STEP 1: Check existing table structure and backup
-- =============================================================================

-- Create backup of existing users table
CREATE TABLE users_backup AS SELECT * FROM users;

-- Create backup of existing commitments table  
CREATE TABLE commitments_backup AS SELECT * FROM commitments;

-- Check what columns we have
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- =============================================================================
-- STEP 2: Create new enhanced users table
-- =============================================================================

CREATE TABLE users_enhanced (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    first_name TEXT,
    username TEXT,
    
    -- Journey tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    first_bot_interaction_at TIMESTAMPTZ DEFAULT NOW(),
    first_commitment_at TIMESTAMPTZ,
    first_pod_call_at TIMESTAMPTZ,
    
    -- Profile for pod matching
    timezone TEXT,
    goals_category TEXT CHECK (goals_category IN ('health', 'business', 'personal', 'learning', 'relationships', 'finance')),
    experience_level TEXT CHECK (experience_level IN ('beginner', 'intermediate', 'advanced')),
    preferred_meeting_style TEXT CHECK (preferred_meeting_style IN ('supportive', 'direct', 'mixed')),
    strengths JSONB DEFAULT '[]'::jsonb,
    help_needed JSONB DEFAULT '[]'::jsonb,
    bio TEXT,
    
    -- Engagement metrics
    total_commitments INTEGER DEFAULT 0,
    completed_commitments INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Settings
    notification_preferences JSONB DEFAULT '{
        "telegram": true,
        "email": true,
        "sms": false,
        "pod_reminders": true,
        "commitment_reminders": true,
        "weekly_summary": true
    }'::jsonb,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT valid_completion_rate CHECK (completed_commitments <= total_commitments),
    CONSTRAINT valid_streak CHECK (current_streak <= longest_streak OR longest_streak = 0)
);

-- =============================================================================
-- STEP 3: Safe data migration with dynamic column detection
-- =============================================================================

-- Migrate existing data safely
DO $$
DECLARE 
    has_telegram_user_id BOOLEAN := FALSE;
    has_created_at BOOLEAN := FALSE;
    migration_query TEXT;
BEGIN
    -- Check if telegram_user_id column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'telegram_user_id'
    ) INTO has_telegram_user_id;
    
    -- Check if created_at column exists  
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'created_at'
    ) INTO has_created_at;
    
    -- Build migration query based on available columns
    IF has_telegram_user_id AND has_created_at THEN
        -- Both columns exist
        migration_query := 'INSERT INTO users_enhanced (telegram_user_id, first_name, created_at, first_bot_interaction_at)
                           SELECT telegram_user_id, COALESCE(first_name, ''User''), created_at, created_at FROM users';
    ELSIF has_telegram_user_id THEN
        -- Only telegram_user_id exists
        migration_query := 'INSERT INTO users_enhanced (telegram_user_id, first_name)
                           SELECT telegram_user_id, COALESCE(first_name, ''User'') FROM users';
    ELSE
        -- Fallback - create sample data structure
        RAISE NOTICE 'No telegram_user_id column found. Creating empty enhanced table.';
        migration_query := 'SELECT 1'; -- No-op query
    END IF;
    
    -- Execute the migration
    IF migration_query != 'SELECT 1' THEN
        EXECUTE migration_query;
        RAISE NOTICE 'Successfully migrated % rows from users to users_enhanced', 
                     (SELECT COUNT(*) FROM users_enhanced);
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Migration error: %. Creating empty enhanced table.', SQLERRM;
END $$;

-- =============================================================================
-- STEP 4: Replace old table with new one
-- =============================================================================

-- Drop old table and rename new one
DROP TABLE IF EXISTS users;
ALTER TABLE users_enhanced RENAME TO users;

-- =============================================================================
-- STEP 5: Create all other tables
-- =============================================================================

-- User Roles Table
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_type TEXT NOT NULL CHECK (role_type IN (
        'unpaid', 'paid', 'pod_member', 'admin', 'super_admin', 
        'beta_tester', 'lifetime_member'
    )),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    
    UNIQUE(user_id, role_type)
);

-- Give all existing users the 'unpaid' role
INSERT INTO user_roles (user_id, role_type)
SELECT id, 'unpaid' FROM users;

-- Pods Table
CREATE TABLE pods (
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
    
    -- Health metrics (calculated by triggers)
    avg_attendance_rate DECIMAL(5,2) DEFAULT 0,
    avg_completion_rate DECIMAL(5,2) DEFAULT 0,
    member_satisfaction_score DECIMAL(3,2) DEFAULT 0,
    health_score DECIMAL(5,2) GENERATED ALWAYS AS (
        (COALESCE(avg_attendance_rate, 0) + COALESCE(avg_completion_rate, 0) + COALESCE(member_satisfaction_score, 0) * 20) / 3
    ) STORED,
    
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
CREATE TABLE pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'left')),
    
    -- Individual metrics
    meetings_attended INTEGER DEFAULT 0,
    meetings_missed INTEGER DEFAULT 0,
    attendance_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN (meetings_attended + meetings_missed) = 0 THEN 0
            ELSE (meetings_attended * 100.0) / (meetings_attended + meetings_missed)
        END
    ) STORED,
    
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

-- Long Term Goals Table
CREATE TABLE long_term_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
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

-- Enhanced Commitments Table
CREATE TABLE commitments_enhanced (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    commitment TEXT NOT NULL,
    original_commitment TEXT,
    smart_score INTEGER CHECK (smart_score BETWEEN 1 AND 10),
    
    -- Classification
    category TEXT CHECK (category IN ('health', 'work', 'personal', 'learning', 'relationships', 'finance')),
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_time_minutes INTEGER,
    priority_level TEXT DEFAULT 'medium' CHECK (priority_level IN ('low', 'medium', 'high')),
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'paused')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    due_date DATE,
    
    -- Context & Memory (ZEP integration)
    related_long_term_goal_id UUID REFERENCES long_term_goals(id),
    context_from_previous JSONB DEFAULT '{}'::jsonb,
    ai_insights JSONB DEFAULT '{}'::jsonb,
    success_factors JSONB DEFAULT '[]'::jsonb,
    
    -- Pod integration
    shared_with_pod BOOLEAN DEFAULT false,
    pod_id UUID REFERENCES pods(id),
    pod_feedback JSONB DEFAULT '[]'::jsonb,
    
    -- Analytics
    completion_time_minutes INTEGER,
    reflection_notes TEXT
);

-- Migrate existing commitments data safely
DO $$
DECLARE 
    has_user_id_column BOOLEAN := FALSE;
    has_telegram_user_id_column BOOLEAN := FALSE;
    migration_query TEXT;
BEGIN
    -- Check what columns exist in commitments table
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'commitments' AND column_name = 'user_id'
    ) INTO has_user_id_column;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'commitments' AND column_name = 'telegram_user_id'
    ) INTO has_telegram_user_id_column;
    
    -- Build migration query based on available columns
    IF has_user_id_column THEN
        -- Direct user_id reference exists
        migration_query := 'INSERT INTO commitments_enhanced (
            user_id, commitment, original_commitment, smart_score, status, created_at, completed_at
        )
        SELECT 
            user_id, commitment, original_commitment, smart_score, status, created_at, completed_at
        FROM commitments';
    ELSIF has_telegram_user_id_column THEN
        -- Need to join with users table to get user_id
        migration_query := 'INSERT INTO commitments_enhanced (
            user_id, commitment, original_commitment, smart_score, status, created_at, completed_at
        )
        SELECT 
            u.id as user_id, 
            c.commitment, 
            c.original_commitment, 
            c.smart_score, 
            c.status, 
            c.created_at, 
            c.completed_at
        FROM commitments c
        JOIN users u ON u.telegram_user_id = c.telegram_user_id';
    ELSE
        RAISE NOTICE 'No compatible columns found in commitments table for migration.';
        migration_query := 'SELECT 1'; -- No-op
    END IF;
    
    -- Execute migration
    IF migration_query != 'SELECT 1' THEN
        EXECUTE migration_query;
        RAISE NOTICE 'Successfully migrated % commitments', 
                     (SELECT COUNT(*) FROM commitments_enhanced);
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Commitments migration error: %. Creating empty enhanced table.', SQLERRM;
END $$;

-- Replace old commitments table
DROP TABLE IF EXISTS commitments;
ALTER TABLE commitments_enhanced RENAME TO commitments;

-- =============================================================================
-- STEP 6: Create remaining tables
-- =============================================================================

-- Meetings Table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    
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
    attendance_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN expected_attendance = 0 THEN 0
            ELSE (attendance_count * 100.0) / expected_attendance
        END
    ) STORED,
    
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

-- Automation Sequences Tables
CREATE TABLE automation_sequences (
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
    total_steps INTEGER GENERATED ALWAYS AS (jsonb_array_length(steps)) STORED,
    
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
    created_by UUID REFERENCES users(id)
);

CREATE TABLE sequence_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sequence_id UUID REFERENCES automation_sequences(id) ON DELETE CASCADE,
    
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

-- =============================================================================
-- STEP 7: Create indexes for performance
-- =============================================================================

-- Users table indexes
CREATE INDEX idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_timezone ON users(timezone);
CREATE INDEX idx_users_goals_category ON users(goals_category);
CREATE INDEX idx_users_last_activity ON users(last_activity_at);

-- User roles indexes
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_type ON user_roles(role_type);
CREATE INDEX idx_user_roles_active ON user_roles(user_id, role_type) WHERE is_active = true;

-- Pods indexes
CREATE INDEX idx_pods_status ON pods(status) WHERE status = 'active';
CREATE INDEX idx_pods_timezone ON pods(timezone);
CREATE INDEX idx_pods_next_meeting ON pods(next_meeting_at);
CREATE INDEX idx_pods_health ON pods(health_score DESC);

-- Pod memberships indexes
CREATE INDEX idx_pod_memberships_user ON pod_memberships(user_id);
CREATE INDEX idx_pod_memberships_pod ON pod_memberships(pod_id);
CREATE INDEX idx_pod_memberships_active ON pod_memberships(pod_id, status) WHERE status = 'active';

-- Commitments indexes
CREATE INDEX idx_commitments_user ON commitments(user_id);
CREATE INDEX idx_commitments_status ON commitments(status);
CREATE INDEX idx_commitments_created ON commitments(created_at DESC);
CREATE INDEX idx_commitments_due ON commitments(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_commitments_pod ON commitments(pod_id) WHERE pod_id IS NOT NULL;

-- Long term goals indexes
CREATE INDEX idx_long_term_goals_user ON long_term_goals(user_id);
CREATE INDEX idx_long_term_goals_status ON long_term_goals(status);
CREATE INDEX idx_long_term_goals_category ON long_term_goals(category);

-- Meetings indexes
CREATE INDEX idx_meetings_pod ON meetings(pod_id);
CREATE INDEX idx_meetings_scheduled ON meetings(scheduled_at DESC);
CREATE INDEX idx_meetings_status ON meetings(status);

-- Automation indexes
CREATE INDEX idx_automation_sequences_trigger ON automation_sequences(trigger_type) WHERE is_active = true;
CREATE INDEX idx_sequence_executions_user ON sequence_executions(user_id);
CREATE INDEX idx_sequence_executions_next_step ON sequence_executions(next_step_at) WHERE status = 'running';

-- =============================================================================
-- STEP 8: Create KPI Views
-- =============================================================================

-- Pod Attendance KPI
CREATE OR REPLACE VIEW kpi_pod_attendance AS
SELECT 
    COALESCE(AVG(attendance_rate), 0) as overall_attendance_rate,
    COUNT(*) as total_meetings_this_week,
    COUNT(*) FILTER (WHERE attendance_rate >= 80) as high_attendance_meetings,
    COALESCE(AVG(overall_satisfaction), 0) as avg_satisfaction
FROM meetings 
WHERE scheduled_at > NOW() - INTERVAL '7 days'
  AND status = 'completed';

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

-- Pod Health KPI
CREATE OR REPLACE VIEW kpi_pod_health AS
SELECT 
    COUNT(*) FILTER (WHERE status = 'active') as active_pods,
    COALESCE(AVG(health_score), 0) as avg_health_score,
    COUNT(*) FILTER (WHERE health_score >= 80) as healthy_pods,
    COUNT(*) FILTER (WHERE health_score < 60) as struggling_pods,
    COALESCE(AVG(avg_attendance_rate), 0) as overall_attendance,
    COALESCE(SUM(current_members), 0) as total_pod_members
FROM pods;

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

-- Service role policies (for bot operations)
CREATE POLICY "Service role full access" ON users FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON user_roles FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON pods FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON pod_memberships FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON commitments FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON long_term_goals FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON meetings FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON automation_sequences FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access" ON sequence_executions FOR ALL TO service_role USING (true);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- =============================================================================
-- STEP 12: Summary and verification
-- =============================================================================

-- Show what was created
SELECT 'Migration completed successfully!' as status;

-- Show table counts
SELECT 
    'users' as table_name,
    COUNT(*) as row_count
FROM users
UNION ALL
SELECT 
    'user_roles' as table_name,
    COUNT(*) as row_count
FROM user_roles
UNION ALL
SELECT 
    'commitments' as table_name,
    COUNT(*) as row_count
FROM commitments
UNION ALL
SELECT 
    'pods' as table_name,
    COUNT(*) as row_count
FROM pods
ORDER BY table_name;