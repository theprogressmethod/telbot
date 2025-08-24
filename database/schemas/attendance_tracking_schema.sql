-- Attendance Tracking Database Schema
-- Comprehensive pod meeting attendance system with analytics

-- Meeting Sessions Table
-- Tracks individual pod meeting instances
CREATE TABLE IF NOT EXISTS meeting_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    scheduled_start TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_end TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    meeting_platform VARCHAR(50) NOT NULL DEFAULT 'manual', -- zoom, google_meet, teams, manual
    meeting_url TEXT,
    meeting_id VARCHAR(255), -- Platform-specific meeting ID
    facilitator_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled, no_show
    total_attendees INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}' -- Platform-specific data
);

-- Attendance Records Table
-- Individual attendance records for pod members at meetings
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES meeting_sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    attendance_status VARCHAR(20) NOT NULL, -- present, absent, late, early_departure, partial
    joined_at TIMESTAMP WITH TIME ZONE,
    left_at TIMESTAMP WITH TIME ZONE,
    minutes_present INTEGER DEFAULT 0,
    was_late BOOLEAN DEFAULT FALSE,
    left_early BOOLEAN DEFAULT FALSE,
    engagement_notes TEXT, -- Facilitator notes on participation
    commitment_shared BOOLEAN DEFAULT FALSE, -- Did they share commitments?
    auto_detected BOOLEAN DEFAULT FALSE, -- Was this automatically detected?
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    platform_data JSONB DEFAULT '{}', -- Platform-specific attendance data
    
    -- Ensure one record per user per session
    UNIQUE(session_id, user_id)
);

-- Attendance Analytics Table
-- Pre-calculated attendance analytics for performance
CREATE TABLE IF NOT EXISTS attendance_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    total_scheduled_meetings INTEGER DEFAULT 0,
    meetings_attended INTEGER DEFAULT 0,
    meetings_missed INTEGER DEFAULT 0,
    attendance_rate DECIMAL(5,4) DEFAULT 0, -- 0.0000 to 1.0000
    average_arrival_offset DECIMAL(6,2) DEFAULT 0, -- Minutes early/late (negative = early)
    average_duration_present DECIMAL(6,2) DEFAULT 0, -- Minutes present per meeting
    current_streak INTEGER DEFAULT 0, -- Consecutive meetings attended
    longest_streak INTEGER DEFAULT 0,
    attendance_pattern VARCHAR(20) DEFAULT 'inconsistent', -- perfect_attender, regular_attender, inconsistent, frequent_misser, ghost_member
    engagement_level VARCHAR(20) DEFAULT 'moderate', -- high, moderate, low, critical
    last_attendance_date TIMESTAMP WITH TIME ZONE,
    prediction_score DECIMAL(5,4) DEFAULT 0.5, -- ML prediction of attending next meeting (0-1)
    risk_flags JSONB DEFAULT '[]', -- Array of risk flags
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    
    -- Ensure one analytics record per user per pod
    UNIQUE(user_id, pod_id)
);

-- Attendance Insights Table
-- AI-generated insights about attendance patterns
CREATE TABLE IF NOT EXISTS attendance_insights (
    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL for pod-level insights
    insight_type VARCHAR(50) NOT NULL, -- attendance_trend, engagement_drop, perfect_streak, etc.
    priority VARCHAR(20) NOT NULL, -- critical, high, medium, low
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    data_points JSONB DEFAULT '{}',
    confidence_score DECIMAL(5,4) DEFAULT 0, -- 0-1 confidence in insight
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE, -- When admin/facilitator acknowledged
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE, -- When insight was resolved/acted upon
    
    -- Index for efficient querying
    CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Meeting Platform Integrations Table
-- Configuration for external meeting platform integrations
CREATE TABLE IF NOT EXISTS meeting_platform_integrations (
    integration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- zoom, google_meet, teams
    platform_config JSONB NOT NULL DEFAULT '{}', -- Platform-specific configuration
    webhook_url TEXT, -- For receiving attendance data
    api_credentials JSONB DEFAULT '{}', -- Encrypted API credentials
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    
    -- Ensure one integration per pod per platform
    UNIQUE(pod_id, platform)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_meeting_sessions_pod_id ON meeting_sessions(pod_id);
CREATE INDEX IF NOT EXISTS idx_meeting_sessions_scheduled_start ON meeting_sessions(scheduled_start);
CREATE INDEX IF NOT EXISTS idx_meeting_sessions_status ON meeting_sessions(status);

CREATE INDEX IF NOT EXISTS idx_attendance_records_session_id ON attendance_records(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_user_id ON attendance_records(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_pod_id ON attendance_records(pod_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_attendance_status ON attendance_records(attendance_status);
CREATE INDEX IF NOT EXISTS idx_attendance_records_created_at ON attendance_records(created_at);

CREATE INDEX IF NOT EXISTS idx_attendance_analytics_user_pod ON attendance_analytics(user_id, pod_id);
CREATE INDEX IF NOT EXISTS idx_attendance_analytics_attendance_rate ON attendance_analytics(attendance_rate);
CREATE INDEX IF NOT EXISTS idx_attendance_analytics_engagement_level ON attendance_analytics(engagement_level);
CREATE INDEX IF NOT EXISTS idx_attendance_analytics_expires_at ON attendance_analytics(expires_at);

CREATE INDEX IF NOT EXISTS idx_attendance_insights_pod_id ON attendance_insights(pod_id);
CREATE INDEX IF NOT EXISTS idx_attendance_insights_user_id ON attendance_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_insights_priority ON attendance_insights(priority);
CREATE INDEX IF NOT EXISTS idx_attendance_insights_created_at ON attendance_insights(created_at);

-- Views for Common Queries

-- Recent Meeting Sessions with Attendance Stats
CREATE OR REPLACE VIEW recent_meeting_sessions AS
SELECT 
    ms.*,
    COUNT(ar.record_id) as total_responses,
    COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END) as attendees,
    COUNT(CASE WHEN ar.attendance_status = 'absent' THEN 1 END) as absences,
    ROUND(
        COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(ar.record_id), 0) * 100, 
        2
    ) as attendance_percentage
FROM meeting_sessions ms
LEFT JOIN attendance_records ar ON ms.session_id = ar.session_id
WHERE ms.scheduled_start >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ms.session_id
ORDER BY ms.scheduled_start DESC;

-- User Attendance Summary (Last 30 Days)
CREATE OR REPLACE VIEW user_attendance_summary AS
SELECT 
    u.id as user_id,
    u.first_name,
    pm.pod_id,
    p.name as pod_name,
    COUNT(ms.session_id) as total_scheduled,
    COUNT(ar.record_id) as total_responses,
    COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END) as meetings_attended,
    COUNT(CASE WHEN ar.attendance_status = 'absent' THEN 1 END) as meetings_missed,
    ROUND(
        COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(ms.session_id), 0) * 100, 
        2
    ) as attendance_rate,
    AVG(ar.minutes_present) as avg_minutes_present,
    COUNT(CASE WHEN ar.was_late THEN 1 END) as times_late,
    MAX(ar.created_at) as last_attendance
FROM users u
JOIN pod_memberships pm ON u.id = pm.user_id AND pm.is_active = TRUE
JOIN pods p ON pm.pod_id = p.id
LEFT JOIN meeting_sessions ms ON p.id = ms.pod_id 
    AND ms.scheduled_start >= CURRENT_DATE - INTERVAL '30 days'
    AND ms.status IN ('completed', 'in_progress')
LEFT JOIN attendance_records ar ON ms.session_id = ar.session_id AND u.id = ar.user_id
GROUP BY u.id, u.first_name, pm.pod_id, p.name
ORDER BY attendance_rate DESC NULLS LAST;

-- Pod Health Dashboard
CREATE OR REPLACE VIEW pod_health_dashboard AS
SELECT 
    p.id as pod_id,
    p.name as pod_name,
    COUNT(DISTINCT pm.user_id) as total_members,
    COUNT(DISTINCT ms.session_id) as meetings_held,
    COUNT(DISTINCT ar.user_id) as unique_attendees,
    ROUND(
        COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(ms.session_id) * COUNT(DISTINCT pm.user_id), 0) * 100, 
        2
    ) as overall_attendance_rate,
    ROUND(AVG(ar.minutes_present), 2) as avg_session_duration,
    COUNT(CASE WHEN ai.priority = 'critical' THEN 1 END) as critical_insights,
    COUNT(CASE WHEN ai.priority = 'high' THEN 1 END) as high_priority_insights
FROM pods p
JOIN pod_memberships pm ON p.id = pm.pod_id AND pm.is_active = TRUE
LEFT JOIN meeting_sessions ms ON p.id = ms.pod_id 
    AND ms.scheduled_start >= CURRENT_DATE - INTERVAL '30 days'
    AND ms.status IN ('completed', 'in_progress')
LEFT JOIN attendance_records ar ON ms.session_id = ar.session_id
LEFT JOIN attendance_insights ai ON p.id = ai.pod_id 
    AND ai.created_at >= CURRENT_DATE - INTERVAL '7 days'
    AND ai.resolved_at IS NULL
GROUP BY p.id, p.name
ORDER BY overall_attendance_rate DESC NULLS LAST;

-- Triggers for Automatic Updates

-- Update meeting_sessions.updated_at on changes
CREATE OR REPLACE FUNCTION update_meeting_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_update_meeting_session_timestamp ON meeting_sessions;
CREATE TRIGGER tr_update_meeting_session_timestamp
    BEFORE UPDATE ON meeting_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_meeting_session_timestamp();

-- Auto-expire old attendance analytics
CREATE OR REPLACE FUNCTION cleanup_expired_attendance_analytics()
RETURNS void AS $$
BEGIN
    DELETE FROM attendance_analytics 
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate attendance analytics (will be called by application)
CREATE OR REPLACE FUNCTION calculate_attendance_analytics(
    p_user_id UUID,
    p_pod_id UUID,
    p_weeks_back INTEGER DEFAULT 12
)
RETURNS TABLE (
    total_scheduled INTEGER,
    meetings_attended INTEGER,
    meetings_missed INTEGER,
    attendance_rate DECIMAL,
    avg_arrival_offset DECIMAL,
    avg_duration DECIMAL,
    current_streak INTEGER,
    longest_streak INTEGER
) AS $$
DECLARE
    cutoff_date TIMESTAMP WITH TIME ZONE;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (p_weeks_back || ' weeks')::INTERVAL;
    
    RETURN QUERY
    SELECT 
        COUNT(ms.session_id)::INTEGER as total_scheduled,
        COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END)::INTEGER as meetings_attended,
        COUNT(CASE WHEN ar.attendance_status = 'absent' THEN 1 END)::INTEGER as meetings_missed,
        ROUND(
            COUNT(CASE WHEN ar.attendance_status != 'absent' THEN 1 END)::DECIMAL / 
            NULLIF(COUNT(ms.session_id), 0), 
            4
        ) as attendance_rate,
        ROUND(
            AVG(CASE 
                WHEN ar.joined_at IS NOT NULL AND ar.attendance_status != 'absent' 
                THEN EXTRACT(EPOCH FROM (ar.joined_at - ms.scheduled_start)) / 60 
                ELSE NULL 
            END), 
            2
        ) as avg_arrival_offset,
        ROUND(AVG(ar.minutes_present), 2) as avg_duration,
        0::INTEGER as current_streak, -- Will be calculated by application logic
        0::INTEGER as longest_streak  -- Will be calculated by application logic
    FROM meeting_sessions ms
    LEFT JOIN attendance_records ar ON ms.session_id = ar.session_id AND ar.user_id = p_user_id
    WHERE ms.pod_id = p_pod_id 
        AND ms.scheduled_start >= cutoff_date
        AND ms.status IN ('completed', 'in_progress');
END;
$$ LANGUAGE plpgsql;

-- Sample Data for Testing (Optional - remove in production)
/*
-- Sample meeting session
INSERT INTO meeting_sessions (pod_id, scheduled_start, scheduled_end, meeting_platform, status)
VALUES (
    (SELECT id FROM pods LIMIT 1),
    CURRENT_TIMESTAMP + INTERVAL '1 hour',
    CURRENT_TIMESTAMP + INTERVAL '2 hours',
    'manual',
    'scheduled'
);
*/

-- Comments for Documentation
COMMENT ON TABLE meeting_sessions IS 'Individual pod meeting instances with timing and platform information';
COMMENT ON TABLE attendance_records IS 'Individual attendance records linking users to specific meeting sessions';
COMMENT ON TABLE attendance_analytics IS 'Pre-calculated attendance analytics for performance optimization';
COMMENT ON TABLE attendance_insights IS 'AI-generated insights about attendance patterns requiring attention';
COMMENT ON TABLE meeting_platform_integrations IS 'Configuration for external meeting platform integrations';

COMMENT ON COLUMN meeting_sessions.meeting_platform IS 'Platform used: zoom, google_meet, teams, or manual';
COMMENT ON COLUMN attendance_records.attendance_status IS 'present, absent, late, early_departure, or partial';
COMMENT ON COLUMN attendance_analytics.attendance_pattern IS 'perfect_attender, regular_attender, inconsistent, frequent_misser, or ghost_member';
COMMENT ON COLUMN attendance_analytics.engagement_level IS 'high, moderate, low, or critical';
COMMENT ON COLUMN attendance_insights.priority IS 'critical, high, medium, or low priority for intervention';