-- Phase 2 Essential Tables Migration
-- These are the 4 critical tables needed for staging deployment

-- 1. Superior onboarding states table
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

-- 2. User engagement tracking table
CREATE TABLE IF NOT EXISTS user_engagement_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Behavioral metrics
    behavioral_score DECIMAL(5,2) DEFAULT 50.0,
    engagement_level VARCHAR(20) DEFAULT 'medium',
    commitment_consistency_score DECIMAL(5,2) DEFAULT 50.0,
    communication_preference VARCHAR(20) DEFAULT 'telegram',
    response_speed_score DECIMAL(5,2) DEFAULT 50.0,
    
    -- Activity tracking
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_messages_sent INTEGER DEFAULT 0,
    total_messages_received INTEGER DEFAULT 0,
    total_commitments_made INTEGER DEFAULT 0,
    total_commitments_completed INTEGER DEFAULT 0,
    
    -- Sequence performance
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_completion_time_hours INTEGER,
    onboarding_success_rate DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_engagement UNIQUE (user_id)
);

-- 3. Message deliveries table
CREATE TABLE IF NOT EXISTS message_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Message details
    message_type VARCHAR(50) NOT NULL,
    sequence_type VARCHAR(50),
    step_number INTEGER,
    message_content TEXT NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('telegram', 'email', 'both')),
    
    -- Delivery tracking
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    
    -- Status and metrics
    delivery_status VARCHAR(20) DEFAULT 'scheduled',
    engagement_score DECIMAL(5,2),
    response_type VARCHAR(50),
    
    -- Context
    context JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Behavioral insights table
CREATE TABLE IF NOT EXISTS behavioral_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Insight details
    insight_type VARCHAR(50) NOT NULL,
    insight_category VARCHAR(50) NOT NULL,
    insight_data JSONB NOT NULL,
    confidence_score DECIMAL(5,2) DEFAULT 50.0,
    
    -- Business value
    business_impact VARCHAR(20),
    recommended_action VARCHAR(100),
    priority_level VARCHAR(20) DEFAULT 'medium',
    
    -- Tracking
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE,
    outcome_tracked BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_superior_onboarding_user_active 
ON superior_onboarding_states(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_user_engagement_user_id 
ON user_engagement_tracking(user_id);

CREATE INDEX IF NOT EXISTS idx_message_deliveries_user_scheduled 
ON message_deliveries(user_id, scheduled_at);

CREATE INDEX IF NOT EXISTS idx_behavioral_insights_user_type 
ON behavioral_insights(user_id, insight_type);

-- Create updated_at triggers for timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_superior_onboarding_states_updated_at 
    BEFORE UPDATE ON superior_onboarding_states 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_user_engagement_tracking_updated_at 
    BEFORE UPDATE ON user_engagement_tracking 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_message_deliveries_updated_at 
    BEFORE UPDATE ON message_deliveries 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_behavioral_insights_updated_at 
    BEFORE UPDATE ON behavioral_insights 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();