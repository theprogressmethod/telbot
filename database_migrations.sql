-- Behavioral Intelligence System Database Migrations
-- Version: 2.0
-- Date: 2025-08-17
-- Purpose: Support superior onboarding and behavioral analytics

-- =====================================================
-- 1. SUPERIOR ONBOARDING TABLES
-- =====================================================

-- Superior onboarding states table
CREATE TABLE IF NOT EXISTS superior_onboarding_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    sequence_type VARCHAR(50) NOT NULL DEFAULT 'superior_onboarding_v2',
    sequence_version VARCHAR(10) NOT NULL DEFAULT '2.0',
    current_step INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    completion_success BOOLEAN DEFAULT false,
    
    -- Behavioral tracking
    target_conversion_rate DECIMAL(5,2) DEFAULT 65.0,
    baseline_conversion_rate DECIMAL(5,2) DEFAULT 27.8,
    step_completion_timestamps JSONB DEFAULT '{}',
    user_responses JSONB DEFAULT '{}',
    behavioral_flags JSONB DEFAULT '{}',
    
    -- Timing
    next_step_at TIMESTAMP WITH TIME ZONE,
    last_message_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Context
    context JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_active_onboarding UNIQUE (user_id, is_active)
);

-- Onboarding message deliveries table
CREATE TABLE IF NOT EXISTS onboarding_message_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    sequence_type VARCHAR(50) NOT NULL,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100),
    message_content TEXT NOT NULL,
    interaction_type VARCHAR(50),
    target_success_rate DECIMAL(5,2),
    psychological_goal VARCHAR(100),
    
    -- Delivery tracking
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    delivery_status VARCHAR(20) DEFAULT 'pending',
    delivery_channel VARCHAR(20) DEFAULT 'telegram',
    
    -- Response tracking
    user_response JSONB,
    response_time_seconds INTEGER,
    
    -- Flags
    is_recovery BOOLEAN DEFAULT false,
    is_celebration BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. BEHAVIORAL ANALYTICS TABLES
-- =====================================================

-- User engagement summary table
CREATE TABLE IF NOT EXISTS user_engagement_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    
    -- Engagement scores
    overall_engagement_score DECIMAL(5,2) DEFAULT 50.0,
    telegram_engagement_score DECIMAL(5,2) DEFAULT 0,
    email_engagement_score DECIMAL(5,2) DEFAULT 0,
    attendance_engagement_score DECIMAL(5,2) DEFAULT 0,
    commitment_engagement_score DECIMAL(5,2) DEFAULT 0,
    
    -- Behavioral patterns
    completion_pattern VARCHAR(50),
    performance_tier VARCHAR(50),
    activity_status VARCHAR(50),
    behavioral_type VARCHAR(50),
    
    -- Preferences
    preferred_channel VARCHAR(20) DEFAULT 'telegram',
    preferred_time_of_day VARCHAR(20),
    
    -- Statistics
    avg_completion_hours DECIMAL(5,2),
    quick_completion_percentage DECIMAL(5,2),
    total_commitments INTEGER DEFAULT 0,
    completed_commitments INTEGER DEFAULT 0,
    
    -- Timestamps
    last_engagement TIMESTAMP WITH TIME ZONE,
    last_message_sent TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Engagement scores table (for caching)
CREATE TABLE IF NOT EXISTS engagement_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    score_type VARCHAR(20) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    
    CONSTRAINT unique_user_score_type UNIQUE (user_id, score_type)
);

-- =====================================================
-- 3. OPTIMIZED NURTURE SEQUENCE TABLES
-- =====================================================

-- Sequence variants for A/B testing
CREATE TABLE IF NOT EXISTS sequence_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_type VARCHAR(50) NOT NULL,
    message_step INTEGER NOT NULL,
    variant_name VARCHAR(50) NOT NULL,
    variant_content TEXT NOT NULL,
    test_percentage INTEGER NOT NULL DEFAULT 50,
    is_active BOOLEAN DEFAULT true,
    
    -- Performance tracking
    total_sent INTEGER DEFAULT 0,
    total_opened INTEGER DEFAULT 0,
    total_clicked INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_variant UNIQUE (sequence_type, message_step, variant_name)
);

-- Message deliveries table (multi-channel)
CREATE TABLE IF NOT EXISTS message_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id VARCHAR(100) UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id),
    sequence_type VARCHAR(50),
    message_step INTEGER,
    
    -- Channel info
    channel VARCHAR(20) NOT NULL,
    recipient_address VARCHAR(255) NOT NULL,
    
    -- Content
    message_content TEXT NOT NULL,
    
    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    priority INTEGER DEFAULT 3,
    
    -- Delivery tracking
    delivery_status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    attempt_count INTEGER DEFAULT 0,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    
    -- Tracking
    tracking_id VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Delivery analytics table
CREATE TABLE IF NOT EXISTS delivery_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_date DATE NOT NULL,
    sequence_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    
    -- Metrics
    total_scheduled INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    
    -- Rates
    delivery_rate DECIMAL(5,2),
    open_rate DECIMAL(5,2),
    click_rate DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_daily_analytics UNIQUE (delivery_date, sequence_type, channel)
);

-- =====================================================
-- 4. USER PREFERENCES AND SETTINGS
-- =====================================================

-- User email preferences
CREATE TABLE IF NOT EXISTS user_email_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    
    -- Email settings
    email_enabled BOOLEAN DEFAULT true,
    email_frequency VARCHAR(20) DEFAULT 'normal',
    
    -- Timing preferences
    preferred_send_time TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Content preferences
    include_tips BOOLEAN DEFAULT true,
    include_community_updates BOOLEAN DEFAULT true,
    include_achievements BOOLEAN DEFAULT true,
    
    -- Unsubscribe
    unsubscribed BOOLEAN DEFAULT false,
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    unsubscribe_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 5. BUSINESS INTELLIGENCE VIEWS
-- =====================================================

-- Create materialized view for real-time analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS bi_dashboard_metrics AS
SELECT 
    -- Onboarding metrics
    (SELECT COUNT(DISTINCT user_id) FROM users) as total_users,
    (SELECT COUNT(DISTINCT user_id) FROM commitments) as users_with_commitments,
    (SELECT COUNT(DISTINCT user_id) FROM users WHERE created_at >= NOW() - INTERVAL '7 days') as recent_signups,
    
    -- Commitment metrics
    (SELECT COUNT(*) FROM commitments) as total_commitments,
    (SELECT COUNT(*) FROM commitments WHERE completed_at IS NOT NULL) as completed_commitments,
    
    -- Engagement metrics
    (SELECT AVG(overall_engagement_score) FROM user_engagement_summary) as avg_engagement_score,
    
    -- Superior onboarding metrics
    (SELECT COUNT(*) FROM superior_onboarding_states WHERE is_active = true) as active_onboardings,
    (SELECT COUNT(*) FROM superior_onboarding_states WHERE completion_success = true) as successful_onboardings,
    
    NOW() as last_updated;

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_bi_metrics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW bi_dashboard_metrics;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_onboarding_states_user_active ON superior_onboarding_states(user_id, is_active);
CREATE INDEX idx_onboarding_deliveries_user ON onboarding_message_deliveries(user_id);
CREATE INDEX idx_onboarding_deliveries_status ON onboarding_message_deliveries(delivery_status);
CREATE INDEX idx_engagement_summary_user ON user_engagement_summary(user_id);
CREATE INDEX idx_message_deliveries_status ON message_deliveries(delivery_status, scheduled_at);
CREATE INDEX idx_message_deliveries_user ON message_deliveries(user_id);
CREATE INDEX idx_delivery_analytics_date ON delivery_analytics(delivery_date);

-- =====================================================
-- 7. TRIGGERS FOR AUTO-UPDATES
-- =====================================================

-- Auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_onboarding_states_updated_at 
    BEFORE UPDATE ON superior_onboarding_states 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_engagement_summary_updated_at 
    BEFORE UPDATE ON user_engagement_summary 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_preferences_updated_at 
    BEFORE UPDATE ON user_email_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. STORED PROCEDURES FOR COMPLEX OPERATIONS
-- =====================================================

-- Calculate engagement score
CREATE OR REPLACE FUNCTION calculate_engagement_score(
    target_user_id UUID,
    score_type VARCHAR
)
RETURNS DECIMAL AS $$
DECLARE
    score DECIMAL(5,2);
BEGIN
    CASE score_type
        WHEN 'overall' THEN
            SELECT 
                CASE 
                    WHEN COUNT(*) = 0 THEN 50.0
                    ELSE LEAST(100, GREATEST(0, 
                        (COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL * 100)
                    ))
                END INTO score
            FROM commitments 
            WHERE user_id = target_user_id;
            
        WHEN 'telegram' THEN
            -- Calculate based on telegram interactions
            score := 50.0; -- Placeholder
            
        WHEN 'email' THEN
            -- Calculate based on email interactions
            score := 0.0; -- Placeholder
            
        WHEN 'commitment' THEN
            SELECT 
                CASE 
                    WHEN COUNT(*) = 0 THEN 0
                    ELSE (COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL * 100)
                END INTO score
            FROM commitments 
            WHERE user_id = target_user_id;
            
        ELSE
            score := 50.0;
    END CASE;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- Schedule multi-channel message
CREATE OR REPLACE FUNCTION schedule_multi_channel_message(
    target_user_id UUID,
    sequence_type VARCHAR,
    message_step INTEGER,
    message_content TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE(delivery_id VARCHAR, channel VARCHAR, recipient VARCHAR) AS $$
DECLARE
    user_record RECORD;
    delivery_uuid VARCHAR;
BEGIN
    -- Get user information
    SELECT u.*, 
           COALESCE(ues.preferred_channel, 'telegram') as pref_channel,
           uep.email_enabled
    INTO user_record
    FROM users u
    LEFT JOIN user_engagement_summary ues ON u.id = ues.user_id
    LEFT JOIN user_email_preferences uep ON u.id = uep.user_id
    WHERE u.id = target_user_id;
    
    -- Schedule based on preferred channel
    IF user_record.pref_channel IN ('telegram', 'both') THEN
        delivery_uuid := gen_random_uuid()::VARCHAR;
        
        INSERT INTO message_deliveries (
            delivery_id, user_id, sequence_type, message_step,
            channel, recipient_address, message_content, scheduled_at
        ) VALUES (
            delivery_uuid, target_user_id, sequence_type, message_step,
            'telegram', user_record.telegram_user_id::VARCHAR, message_content, scheduled_time
        );
        
        RETURN QUERY SELECT delivery_uuid, 'telegram'::VARCHAR, user_record.telegram_user_id::VARCHAR;
    END IF;
    
    IF user_record.pref_channel IN ('email', 'both') AND user_record.email IS NOT NULL AND user_record.email_enabled THEN
        delivery_uuid := gen_random_uuid()::VARCHAR;
        
        INSERT INTO message_deliveries (
            delivery_id, user_id, sequence_type, message_step,
            channel, recipient_address, message_content, scheduled_at
        ) VALUES (
            delivery_uuid, target_user_id, sequence_type, message_step,
            'email', user_record.email, message_content, scheduled_time
        );
        
        RETURN QUERY SELECT delivery_uuid, 'email'::VARCHAR, user_record.email;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 9. GRANT PERMISSIONS
-- =====================================================

-- Grant appropriate permissions (adjust based on your user roles)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- =====================================================
-- 10. INITIAL DATA SEEDING
-- =====================================================

-- Insert default sequence variants for A/B testing
INSERT INTO sequence_variants (sequence_type, message_step, variant_name, variant_content, test_percentage)
VALUES 
    ('micro_onboarding', 1, 'breathing', '🎯 Welcome! Let''s start tiny: Take 3 deep breaths right now.', 50),
    ('micro_onboarding', 1, 'smile', '🎯 Welcome! Let''s start tiny: Smile for 5 seconds right now.', 50)
ON CONFLICT DO NOTHING;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Run this script in your Supabase SQL editor to create all necessary tables
-- for the Behavioral Intelligence System