-- Enhanced Nurture Sequence Schema
-- Phase 2: Multi-channel delivery and engagement scoring extensions

-- Table for tracking message deliveries across all channels (Telegram, Email)
CREATE TABLE IF NOT EXISTS message_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_type TEXT NOT NULL,
    message_step INTEGER NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('telegram', 'email')),
    delivery_status TEXT NOT NULL CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'failed', 'bounced', 'opened', 'clicked')),
    recipient_address TEXT NOT NULL, -- telegram_user_id or email address
    message_content TEXT NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    tracking_id TEXT, -- for email tracking
    attempt_count INTEGER DEFAULT 1,
    max_attempts INTEGER DEFAULT 3,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for message deliveries
CREATE INDEX IF NOT EXISTS idx_message_deliveries_user_id ON message_deliveries(user_id);
CREATE INDEX IF NOT EXISTS idx_message_deliveries_sequence ON message_deliveries(sequence_type, message_step);
CREATE INDEX IF NOT EXISTS idx_message_deliveries_channel ON message_deliveries(channel);
CREATE INDEX IF NOT EXISTS idx_message_deliveries_status ON message_deliveries(delivery_status);
CREATE INDEX IF NOT EXISTS idx_message_deliveries_scheduled ON message_deliveries(scheduled_at) WHERE delivery_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_message_deliveries_tracking ON message_deliveries(tracking_id) WHERE tracking_id IS NOT NULL;

-- Table for user engagement scoring
CREATE TABLE IF NOT EXISTS engagement_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_type TEXT NOT NULL CHECK (score_type IN ('overall', 'telegram', 'email', 'attendance', 'commitment')),
    score NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    factors JSONB DEFAULT '{}', -- breakdown of score factors
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE, -- for caching
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for engagement scores
CREATE INDEX IF NOT EXISTS idx_engagement_scores_user_id ON engagement_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_engagement_scores_type ON engagement_scores(score_type);
CREATE INDEX IF NOT EXISTS idx_engagement_scores_valid ON engagement_scores(user_id, score_type, valid_until) WHERE valid_until > NOW();
CREATE UNIQUE INDEX IF NOT EXISTS idx_engagement_scores_latest ON engagement_scores(user_id, score_type) WHERE valid_until IS NULL OR valid_until > NOW();

-- Table for A/B testing sequence variants
CREATE TABLE IF NOT EXISTS sequence_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_type TEXT NOT NULL,
    variant_name TEXT NOT NULL,
    message_step INTEGER NOT NULL,
    variant_content TEXT NOT NULL,
    variant_metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    test_percentage NUMERIC(5,2) DEFAULT 50.0 CHECK (test_percentage >= 0 AND test_percentage <= 100),
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sequence variants
CREATE INDEX IF NOT EXISTS idx_sequence_variants_type ON sequence_variants(sequence_type);
CREATE INDEX IF NOT EXISTS idx_sequence_variants_active ON sequence_variants(sequence_type, is_active) WHERE is_active = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sequence_variants_unique ON sequence_variants(sequence_type, variant_name, message_step);

-- Table for user email preferences
CREATE TABLE IF NOT EXISTS user_email_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_address TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    verification_sent_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    opt_in_sequences BOOLEAN DEFAULT TRUE,
    opt_in_announcements BOOLEAN DEFAULT TRUE,
    opt_in_reminders BOOLEAN DEFAULT TRUE,
    preferred_time TEXT DEFAULT 'morning' CHECK (preferred_time IN ('morning', 'afternoon', 'evening')),
    timezone TEXT DEFAULT 'UTC',
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    unsubscribe_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for email preferences
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email_preferences_user ON user_email_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_email_preferences_email ON user_email_preferences(email_address);
CREATE INDEX IF NOT EXISTS idx_user_email_preferences_verified ON user_email_preferences(is_verified, opt_in_sequences) WHERE is_verified = TRUE;

-- Table for tracking email events (opens, clicks, bounces)
CREATE TABLE IF NOT EXISTS email_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID REFERENCES message_deliveries(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('sent', 'delivered', 'bounce', 'complaint', 'open', 'click', 'unsubscribe')),
    event_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_data JSONB DEFAULT '{}',
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for email events
CREATE INDEX IF NOT EXISTS idx_email_events_delivery ON email_events(delivery_id);
CREATE INDEX IF NOT EXISTS idx_email_events_type ON email_events(event_type);
CREATE INDEX IF NOT EXISTS idx_email_events_time ON email_events(event_time);

-- Enhanced user_sequence_state table (extending the existing one from nurture_queue_schema.sql)
ALTER TABLE user_sequence_state ADD COLUMN IF NOT EXISTS preferred_channel TEXT DEFAULT 'telegram' CHECK (preferred_channel IN ('telegram', 'email', 'both'));
ALTER TABLE user_sequence_state ADD COLUMN IF NOT EXISTS engagement_score NUMERIC(5,2) DEFAULT 50.0;
ALTER TABLE user_sequence_state ADD COLUMN IF NOT EXISTS variant_assignments JSONB DEFAULT '{}';
ALTER TABLE user_sequence_state ADD COLUMN IF NOT EXISTS last_engagement_at TIMESTAMP WITH TIME ZONE;

-- Function to calculate user engagement score
CREATE OR REPLACE FUNCTION calculate_engagement_score(target_user_id UUID, score_type TEXT DEFAULT 'overall')
RETURNS NUMERIC AS $$
DECLARE
    engagement_score NUMERIC := 50.0;
    telegram_score NUMERIC := 0;
    email_score NUMERIC := 0;
    attendance_score NUMERIC := 0;
    commitment_score NUMERIC := 0;
    days_active INTEGER := 0;
    total_interactions INTEGER := 0;
BEGIN
    -- Calculate telegram engagement (0-25 points)
    SELECT COUNT(*) INTO total_interactions
    FROM message_deliveries 
    WHERE user_id = target_user_id 
      AND channel = 'telegram' 
      AND delivery_status IN ('delivered', 'opened')
      AND sent_at > NOW() - INTERVAL '30 days';
    
    telegram_score := LEAST(25, total_interactions * 2.0);
    
    -- Calculate email engagement (0-25 points)
    SELECT COUNT(*) INTO total_interactions
    FROM message_deliveries 
    WHERE user_id = target_user_id 
      AND channel = 'email' 
      AND delivery_status IN ('delivered', 'opened', 'clicked')
      AND sent_at > NOW() - INTERVAL '30 days';
    
    email_score := LEAST(25, total_interactions * 3.0);
    
    -- Calculate attendance score (0-25 points)
    SELECT COUNT(*) INTO total_interactions
    FROM meeting_attendance 
    WHERE user_id = target_user_id 
      AND attended = TRUE 
      AND created_at > NOW() - INTERVAL '30 days';
    
    attendance_score := LEAST(25, total_interactions * 5.0);
    
    -- Calculate commitment score (0-25 points)
    SELECT COUNT(*) INTO total_interactions
    FROM commitments 
    WHERE user_id = target_user_id 
      AND status = 'completed'
      AND created_at > NOW() - INTERVAL '30 days';
    
    commitment_score := LEAST(25, total_interactions * 2.0);
    
    -- Calculate overall score based on type
    IF score_type = 'telegram' THEN
        engagement_score := telegram_score * 4; -- Scale to 0-100
    ELSIF score_type = 'email' THEN
        engagement_score := email_score * 4; -- Scale to 0-100
    ELSIF score_type = 'attendance' THEN
        engagement_score := attendance_score * 4; -- Scale to 0-100
    ELSIF score_type = 'commitment' THEN
        engagement_score := commitment_score * 4; -- Scale to 0-100
    ELSE -- overall
        engagement_score := telegram_score + email_score + attendance_score + commitment_score;
    END IF;
    
    -- Ensure score is within bounds
    engagement_score := GREATEST(0, LEAST(100, engagement_score));
    
    RETURN engagement_score;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's preferred delivery channel based on engagement
CREATE OR REPLACE FUNCTION get_preferred_channel(target_user_id UUID)
RETURNS TEXT AS $$
DECLARE
    telegram_score NUMERIC;
    email_score NUMERIC;
    user_preference TEXT;
    has_email BOOLEAN := FALSE;
BEGIN
    -- Check if user has verified email
    SELECT TRUE INTO has_email
    FROM user_email_preferences 
    WHERE user_id = target_user_id 
      AND is_verified = TRUE 
      AND opt_in_sequences = TRUE
      AND unsubscribed_at IS NULL
    LIMIT 1;
    
    -- Get user's explicit preference
    SELECT preferred_channel INTO user_preference
    FROM user_sequence_state 
    WHERE user_id = target_user_id 
      AND is_active = TRUE
    ORDER BY started_at DESC
    LIMIT 1;
    
    -- If user explicitly wants both channels and has email, return 'both'
    IF user_preference = 'both' AND has_email THEN
        RETURN 'both';
    END IF;
    
    -- If user wants email only and has verified email
    IF user_preference = 'email' AND has_email THEN
        RETURN 'email';
    END IF;
    
    -- Default to telegram if no email or user prefers telegram
    RETURN 'telegram';
END;
$$ LANGUAGE plpgsql;

-- Function to schedule multi-channel message delivery
CREATE OR REPLACE FUNCTION schedule_multi_channel_message(
    target_user_id UUID,
    sequence_type TEXT,
    message_step INTEGER,
    message_content TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    delivery_id UUID,
    channel TEXT,
    recipient TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE
) AS $$
DECLARE
    preferred_channel TEXT;
    user_telegram_id BIGINT;
    user_email TEXT;
    delivery_record RECORD;
BEGIN
    -- Get user's preferred channel
    preferred_channel := get_preferred_channel(target_user_id);
    
    -- Get user contact information
    SELECT telegram_user_id INTO user_telegram_id
    FROM users 
    WHERE id = target_user_id;
    
    SELECT email_address INTO user_email
    FROM user_email_preferences 
    WHERE user_id = target_user_id 
      AND is_verified = TRUE 
      AND opt_in_sequences = TRUE
      AND unsubscribed_at IS NULL;
    
    -- Schedule Telegram message if preferred or as fallback
    IF preferred_channel IN ('telegram', 'both') AND user_telegram_id IS NOT NULL THEN
        INSERT INTO message_deliveries (
            user_id, sequence_type, message_step, channel, delivery_status,
            recipient_address, message_content, scheduled_at
        ) VALUES (
            target_user_id, sequence_type, message_step, 'telegram', 'pending',
            user_telegram_id::TEXT, message_content, scheduled_time
        ) RETURNING id, channel, recipient_address, scheduled_at
        INTO delivery_record;
        
        delivery_id := delivery_record.id;
        channel := delivery_record.channel;
        recipient := delivery_record.recipient_address;
        scheduled_at := delivery_record.scheduled_at;
        RETURN NEXT;
    END IF;
    
    -- Schedule Email message if preferred and available
    IF preferred_channel IN ('email', 'both') AND user_email IS NOT NULL THEN
        INSERT INTO message_deliveries (
            user_id, sequence_type, message_step, channel, delivery_status,
            recipient_address, message_content, scheduled_at
        ) VALUES (
            target_user_id, sequence_type, message_step, 'email', 'pending',
            user_email, message_content, 
            -- Schedule email 2 hours after telegram if both channels
            CASE WHEN preferred_channel = 'both' THEN scheduled_time + INTERVAL '2 hours' 
                 ELSE scheduled_time END
        ) RETURNING id, channel, recipient_address, scheduled_at
        INTO delivery_record;
        
        delivery_id := delivery_record.id;
        channel := delivery_record.channel;
        recipient := delivery_record.recipient_address;
        scheduled_at := delivery_record.scheduled_at;
        RETURN NEXT;
    END IF;
    
    -- If no channels available, create a failed delivery record
    IF preferred_channel = 'email' AND user_email IS NULL THEN
        INSERT INTO message_deliveries (
            user_id, sequence_type, message_step, channel, delivery_status,
            recipient_address, message_content, scheduled_at, failed_at, failure_reason
        ) VALUES (
            target_user_id, sequence_type, message_step, 'email', 'failed',
            'no_email_available', message_content, scheduled_time, NOW(), 'No verified email address'
        ) RETURNING id, channel, recipient_address, scheduled_at
        INTO delivery_record;
        
        delivery_id := delivery_record.id;
        channel := delivery_record.channel;
        recipient := delivery_record.recipient_address;
        scheduled_at := delivery_record.scheduled_at;
        RETURN NEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- View for delivery analytics
CREATE OR REPLACE VIEW delivery_analytics AS
SELECT 
    d.sequence_type,
    d.channel,
    DATE(d.scheduled_at) AS delivery_date,
    COUNT(*) as total_scheduled,
    COUNT(*) FILTER (WHERE d.delivery_status = 'sent') as sent_count,
    COUNT(*) FILTER (WHERE d.delivery_status = 'delivered') as delivered_count,
    COUNT(*) FILTER (WHERE d.delivery_status = 'failed') as failed_count,
    COUNT(*) FILTER (WHERE d.delivery_status = 'opened') as opened_count,
    COUNT(*) FILTER (WHERE d.delivery_status = 'clicked') as clicked_count,
    ROUND(
        COUNT(*) FILTER (WHERE d.delivery_status = 'delivered')::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE d.delivery_status IN ('sent', 'delivered', 'failed')), 0) * 100, 2
    ) as delivery_rate,
    ROUND(
        COUNT(*) FILTER (WHERE d.delivery_status = 'opened')::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE d.delivery_status = 'delivered'), 0) * 100, 2
    ) as open_rate,
    ROUND(
        COUNT(*) FILTER (WHERE d.delivery_status = 'clicked')::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE d.delivery_status = 'opened'), 0) * 100, 2
    ) as click_rate
FROM message_deliveries d
WHERE d.scheduled_at >= NOW() - INTERVAL '30 days'
GROUP BY d.sequence_type, d.channel, DATE(d.scheduled_at)
ORDER BY delivery_date DESC, sequence_type, channel;

-- View for user engagement summary
CREATE OR REPLACE VIEW user_engagement_summary AS
SELECT 
    u.id as user_id,
    u.first_name,
    u.email as user_email,
    u.telegram_user_id,
    COALESCE(es_overall.score, 50.0) as overall_engagement_score,
    COALESCE(es_telegram.score, 0) as telegram_engagement_score,
    COALESCE(es_email.score, 0) as email_engagement_score,
    COALESCE(es_attendance.score, 0) as attendance_engagement_score,
    COALESCE(es_commitment.score, 0) as commitment_engagement_score,
    get_preferred_channel(u.id) as preferred_channel,
    uep.is_verified as email_verified,
    uep.opt_in_sequences as email_opt_in,
    COUNT(md.id) as total_messages_sent,
    COUNT(md.id) FILTER (WHERE md.delivery_status = 'opened') as messages_opened,
    MAX(md.sent_at) as last_message_sent
FROM users u
LEFT JOIN engagement_scores es_overall ON u.id = es_overall.user_id AND es_overall.score_type = 'overall' AND (es_overall.valid_until IS NULL OR es_overall.valid_until > NOW())
LEFT JOIN engagement_scores es_telegram ON u.id = es_telegram.user_id AND es_telegram.score_type = 'telegram' AND (es_telegram.valid_until IS NULL OR es_telegram.valid_until > NOW())
LEFT JOIN engagement_scores es_email ON u.id = es_email.user_id AND es_email.score_type = 'email' AND (es_email.valid_until IS NULL OR es_email.valid_until > NOW())
LEFT JOIN engagement_scores es_attendance ON u.id = es_attendance.user_id AND es_attendance.score_type = 'attendance' AND (es_attendance.valid_until IS NULL OR es_attendance.valid_until > NOW())
LEFT JOIN engagement_scores es_commitment ON u.id = es_commitment.user_id AND es_commitment.score_type = 'commitment' AND (es_commitment.valid_until IS NULL OR es_commitment.valid_until > NOW())
LEFT JOIN user_email_preferences uep ON u.id = uep.user_id
LEFT JOIN message_deliveries md ON u.id = md.user_id AND md.sent_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.first_name, u.email, u.telegram_user_id, es_overall.score, es_telegram.score, es_email.score, es_attendance.score, es_commitment.score, uep.is_verified, uep.opt_in_sequences;

-- Add RLS policies for new tables
ALTER TABLE message_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagement_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE sequence_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_email_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_events ENABLE ROW LEVEL SECURITY;

-- Service role policies (full access)
CREATE POLICY IF NOT EXISTS "Service role full access to message_deliveries" ON message_deliveries FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access to engagement_scores" ON engagement_scores FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access to sequence_variants" ON sequence_variants FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access to user_email_preferences" ON user_email_preferences FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY IF NOT EXISTS "Service role full access to email_events" ON email_events FOR ALL USING (auth.role() = 'service_role');

-- User policies (own data only)
CREATE POLICY IF NOT EXISTS "Users can view own message deliveries" ON message_deliveries FOR SELECT USING (user_id = auth.uid());
CREATE POLICY IF NOT EXISTS "Users can view own engagement scores" ON engagement_scores FOR SELECT USING (user_id = auth.uid());
CREATE POLICY IF NOT EXISTS "Users can manage own email preferences" ON user_email_preferences FOR ALL USING (user_id = auth.uid());

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON message_deliveries TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON engagement_scores TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON sequence_variants TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_email_preferences TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON email_events TO service_role;

GRANT SELECT ON delivery_analytics TO service_role;
GRANT SELECT ON user_engagement_summary TO service_role;

GRANT EXECUTE ON FUNCTION calculate_engagement_score(UUID, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION get_preferred_channel(UUID) TO service_role;
GRANT EXECUTE ON FUNCTION schedule_multi_channel_message(UUID, TEXT, INTEGER, TEXT, TIMESTAMP WITH TIME ZONE) TO service_role;

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'Enhanced nurture sequence schema created successfully!';
    RAISE NOTICE 'New tables: message_deliveries, engagement_scores, sequence_variants, user_email_preferences, email_events';
    RAISE NOTICE 'Enhanced table: user_sequence_state (added preferred_channel, engagement_score, variant_assignments, last_engagement_at)';
    RAISE NOTICE 'New functions: calculate_engagement_score, get_preferred_channel, schedule_multi_channel_message';
    RAISE NOTICE 'New views: delivery_analytics, user_engagement_summary';
END $$;