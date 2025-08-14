-- The Progress Method - Complete Database Schema
-- Run this in Supabase SQL Editor

-- =============================================================================
-- 1. USERS TABLE (Enhanced from existing)
-- =============================================================================

-- First, let's migrate existing users table
-- Backup existing data, then recreate with new structure

CREATE TABLE users_new (
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

-- Migrate existing data
INSERT INTO users_new (telegram_user_id, first_name, created_at, first_bot_interaction_at)
SELECT telegram_user_id, 'User', created_at, created_at 
FROM users;

-- Drop old table and rename
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

-- Indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_timezone ON users(timezone);
CREATE INDEX idx_users_goals_category ON users(goals_category);
CREATE INDEX idx_users_last_activity ON users(last_activity_at);

-- =============================================================================
-- 2. USER ROLES (Multi-Role System)
-- =============================================================================

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

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_type ON user_roles(role_type);
CREATE INDEX idx_user_roles_active ON user_roles(user_id, role_type) WHERE is_active = true;

-- =============================================================================
-- 3. PODS (Business Core)
-- =============================================================================

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

CREATE INDEX idx_pods_status ON pods(status) WHERE status = 'active';
CREATE INDEX idx_pods_timezone ON pods(timezone);
CREATE INDEX idx_pods_next_meeting ON pods(next_meeting_at);
CREATE INDEX idx_pods_health ON pods(health_score DESC);

-- =============================================================================
-- 4. POD MEMBERSHIPS
-- =============================================================================

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

CREATE INDEX idx_pod_memberships_user ON pod_memberships(user_id);
CREATE INDEX idx_pod_memberships_pod ON pod_memberships(pod_id);
CREATE INDEX idx_pod_memberships_active ON pod_memberships(pod_id, status) WHERE status = 'active';

-- =============================================================================
-- 5. ENHANCED COMMITMENTS TABLE
-- =============================================================================

-- Migrate existing commitments table
CREATE TABLE commitments_new (
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
    related_long_term_goal_id UUID, -- Will reference long_term_goals
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

-- Migrate existing data
INSERT INTO commitments_new (
    user_id, commitment, original_commitment, smart_score, status, created_at, completed_at
)
SELECT 
    (SELECT id FROM users WHERE users.telegram_user_id = commitments.telegram_user_id),
    commitment,
    original_commitment,
    smart_score,
    status,
    created_at,
    completed_at
FROM commitments
WHERE EXISTS (SELECT 1 FROM users WHERE users.telegram_user_id = commitments.telegram_user_id);

-- Drop old table and rename
DROP TABLE commitments;
ALTER TABLE commitments_new RENAME TO commitments;

CREATE INDEX idx_commitments_user ON commitments(user_id);
CREATE INDEX idx_commitments_status ON commitments(status);
CREATE INDEX idx_commitments_created ON commitments(created_at DESC);
CREATE INDEX idx_commitments_due ON commitments(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_commitments_pod ON commitments(pod_id) WHERE pod_id IS NOT NULL;

-- =============================================================================
-- 6. LONG TERM GOALS (ZEP Context System)
-- =============================================================================

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

-- Add the foreign key reference now that the table exists
ALTER TABLE commitments ADD CONSTRAINT fk_commitments_long_term_goal 
FOREIGN KEY (related_long_term_goal_id) REFERENCES long_term_goals(id);

CREATE INDEX idx_long_term_goals_user ON long_term_goals(user_id);
CREATE INDEX idx_long_term_goals_status ON long_term_goals(status);
CREATE INDEX idx_long_term_goals_category ON long_term_goals(category);

-- =============================================================================
-- 7. MEETINGS (Pod Sessions)
-- =============================================================================

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

CREATE INDEX idx_meetings_pod ON meetings(pod_id);
CREATE INDEX idx_meetings_scheduled ON meetings(scheduled_at DESC);
CREATE INDEX idx_meetings_status ON meetings(status);

-- =============================================================================
-- 8. AUTOMATION SEQUENCES
-- =============================================================================

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
    steps JSONB NOT NULL, -- Array of step objects
    total_steps INTEGER GENERATED ALWAYS AS (jsonb_array_length(steps)) STORED,
    
    -- Settings
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5, -- Higher = more important
    max_executions_per_user INTEGER, -- NULL = unlimited
    
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

CREATE INDEX idx_automation_sequences_trigger ON automation_sequences(trigger_type) WHERE is_active = true;
CREATE INDEX idx_sequence_executions_user ON sequence_executions(user_id);
CREATE INDEX idx_sequence_executions_next_step ON sequence_executions(next_step_at) WHERE status = 'running';

-- =============================================================================
-- 9. KPI TRACKING VIEWS
-- =============================================================================

-- Pod Attendance KPI
CREATE OR REPLACE VIEW kpi_pod_attendance AS
SELECT 
    AVG(attendance_rate) as overall_attendance_rate,
    COUNT(*) as total_meetings_this_week,
    COUNT(*) FILTER (WHERE attendance_rate >= 80) as high_attendance_meetings,
    AVG(member_satisfaction_score) as avg_satisfaction
FROM meetings 
WHERE scheduled_at > NOW() - INTERVAL '7 days'
  AND status = 'completed';

-- Bot Usage KPI
CREATE OR REPLACE VIEW kpi_bot_usage AS
SELECT 
    COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '7 days' THEN id END) as weekly_active_users,
    COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '30 days' THEN id END) as monthly_active_users,
    COUNT(*) as total_users,
    (COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '7 days' THEN id END) * 100.0 / COUNT(*)) as weekly_active_percentage,
    AVG(current_streak) as avg_current_streak
FROM users
WHERE is_active = true;

-- Commitment Fulfillment KPI
CREATE OR REPLACE VIEW kpi_commitment_fulfillment AS
SELECT 
    COUNT(*) FILTER (WHERE status = 'completed' AND created_at > NOW() - INTERVAL '7 days') as completed_this_week,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as total_this_week,
    (COUNT(*) FILTER (WHERE status = 'completed' AND created_at > NOW() - INTERVAL '7 days') * 100.0 / 
     NULLIF(COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days'), 0)) as weekly_completion_rate,
    
    SUM(u.completed_commitments) * 100.0 / NULLIF(SUM(u.total_commitments), 0) as overall_completion_rate,
    AVG(u.current_streak) as avg_current_streak,
    MAX(u.longest_streak) as max_streak_achieved
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
    AVG(health_score) as avg_health_score,
    COUNT(*) FILTER (WHERE health_score >= 80) as healthy_pods,
    COUNT(*) FILTER (WHERE health_score < 60) as struggling_pods,
    AVG(avg_attendance_rate) as overall_attendance,
    SUM(current_members) as total_pod_members
FROM pods;

-- =============================================================================
-- 10. SECURITY & ROW LEVEL SECURITY
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

-- User policies (for authenticated users)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Users can view own commitments" ON commitments FOR SELECT USING (
    auth.uid()::text IN (SELECT id::text FROM users WHERE users.id = commitments.user_id)
);

-- Admin policies will be added when we implement the admin interface

-- =============================================================================
-- 11. UTILITY FUNCTIONS
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

-- Function to update user metrics (called by triggers)
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
-- 12. TRIGGERS FOR AUTO-UPDATES
-- =============================================================================

-- Trigger to update user metrics when commitments change
CREATE OR REPLACE FUNCTION trigger_update_user_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user metrics for both old and new user (in case of user_id change)
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

-- Trigger to auto-grant 'paid' role when payment is detected
CREATE OR REPLACE FUNCTION trigger_grant_paid_role()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.monthly_payment_active = true AND (OLD.monthly_payment_active = false OR OLD.monthly_payment_active IS NULL) THEN
        PERFORM grant_user_role(NEW.user_id, 'paid');
        PERFORM grant_user_role(NEW.user_id, 'pod_member');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER grant_paid_role_trigger
    AFTER UPDATE ON pod_memberships
    FOR EACH ROW EXECUTE FUNCTION trigger_grant_paid_role();

-- Comments for documentation
COMMENT ON TABLE users IS 'Core user profiles with engagement metrics and pod matching data';
COMMENT ON TABLE user_roles IS 'Flexible multi-role system for permissions and features';
COMMENT ON TABLE pods IS 'Accountability pod groups with health metrics';
COMMENT ON TABLE pod_memberships IS 'User membership in pods with individual tracking';
COMMENT ON TABLE commitments IS 'Enhanced commitment tracking with AI context';
COMMENT ON TABLE long_term_goals IS 'Long-term goal tracking with ZEP-style context building';
COMMENT ON TABLE meetings IS 'Pod meeting sessions with attendance and engagement metrics';
COMMENT ON TABLE automation_sequences IS 'Configurable nurture sequences and automations';
COMMENT ON TABLE sequence_executions IS 'Tracking of automation sequence runs per user';

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;