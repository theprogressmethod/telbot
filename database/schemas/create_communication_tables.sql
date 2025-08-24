-- Communication Preferences & Analytics System Tables
-- Provides user control and visibility into nurture messaging

-- ============================================
-- COMMUNICATION PREFERENCES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS communication_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    telegram_user_id BIGINT NOT NULL UNIQUE,
    communication_style TEXT NOT NULL DEFAULT 'balanced',
    custom_preferences JSONB DEFAULT '{}',
    enabled_message_types JSONB DEFAULT '[]',
    pause_until TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comm_prefs_telegram_id ON communication_preferences(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_comm_prefs_style ON communication_preferences(communication_style);
CREATE INDEX IF NOT EXISTS idx_comm_prefs_active ON communication_preferences(is_active);

-- ============================================
-- MESSAGE ANALYTICS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS message_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL,
    message_type TEXT NOT NULL,
    pod_id UUID REFERENCES pods(id) ON DELETE SET NULL,
    message_length INT DEFAULT 0,
    message_hash BIGINT, -- For deduplication
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    user_responded BOOLEAN DEFAULT false,
    response_type TEXT, -- 'text_reply', 'command', 'button_click'
    responded_at TIMESTAMPTZ,
    clicked_link BOOLEAN DEFAULT false,
    click_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_msg_analytics_telegram_id ON message_analytics(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_msg_analytics_type ON message_analytics(message_type);
CREATE INDEX IF NOT EXISTS idx_msg_analytics_sent_at ON message_analytics(sent_at);
CREATE INDEX IF NOT EXISTS idx_msg_analytics_pod ON message_analytics(pod_id);

-- ============================================
-- PREFERENCE CHANGE LOG TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS preference_change_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL,
    action TEXT NOT NULL, -- 'preference_change', 'pause', 'resume'
    old_style TEXT,
    new_style TEXT,
    reason TEXT, -- 'user_initiated', 'low_engagement_auto', 'admin_override'
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pref_log_telegram_id ON preference_change_log(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_pref_log_action ON preference_change_log(action);
CREATE INDEX IF NOT EXISTS idx_pref_log_timestamp ON preference_change_log(timestamp);

-- ============================================
-- ENGAGEMENT METRICS VIEW
-- ============================================

CREATE OR REPLACE VIEW user_engagement_summary AS
SELECT 
    cp.telegram_user_id,
    cp.communication_style,
    cp.last_updated as preferences_updated,
    COUNT(ma.id) as total_messages_sent,
    COUNT(CASE WHEN ma.user_responded THEN 1 END) as messages_responded,
    COUNT(CASE WHEN ma.clicked_link THEN 1 END) as messages_clicked,
    COALESCE(
        COUNT(CASE WHEN ma.user_responded THEN 1 END)::float / 
        NULLIF(COUNT(ma.id), 0), 0
    ) as response_rate,
    COALESCE(
        COUNT(CASE WHEN ma.clicked_link THEN 1 END)::float / 
        NULLIF(COUNT(ma.id), 0), 0
    ) as click_rate,
    MAX(ma.sent_at) as last_message_sent,
    MAX(ma.responded_at) as last_response
FROM communication_preferences cp
LEFT JOIN message_analytics ma ON cp.telegram_user_id = ma.telegram_user_id 
    AND ma.sent_at >= NOW() - INTERVAL '30 days'
GROUP BY cp.telegram_user_id, cp.communication_style, cp.last_updated;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Insert default preferences for existing users
INSERT INTO communication_preferences (user_id, telegram_user_id, communication_style, enabled_message_types)
SELECT 
    id,
    telegram_user_id,
    'balanced',
    '["week_launch", "meeting_prep", "post_meeting", "reflection"]'::jsonb
FROM users 
WHERE telegram_user_id IS NOT NULL
ON CONFLICT (telegram_user_id) DO NOTHING;

-- ============================================
-- ANALYTICS FUNCTIONS
-- ============================================

-- Function to get communication analytics for a time period
CREATE OR REPLACE FUNCTION get_communication_analytics(
    days_back INTEGER DEFAULT 30,
    pod_filter UUID DEFAULT NULL
) RETURNS TABLE (
    total_messages BIGINT,
    unique_recipients BIGINT,
    overall_response_rate NUMERIC,
    overall_click_rate NUMERIC,
    message_type_breakdown JSONB,
    style_distribution JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH message_stats AS (
        SELECT 
            ma.message_type,
            cp.communication_style,
            COUNT(*) as msg_count,
            COUNT(CASE WHEN ma.user_responded THEN 1 END) as responses,
            COUNT(CASE WHEN ma.clicked_link THEN 1 END) as clicks,
            COUNT(DISTINCT ma.telegram_user_id) as unique_users
        FROM message_analytics ma
        LEFT JOIN communication_preferences cp ON ma.telegram_user_id = cp.telegram_user_id
        WHERE ma.sent_at >= NOW() - (days_back || ' days')::INTERVAL
          AND (pod_filter IS NULL OR ma.pod_id = pod_filter)
        GROUP BY ma.message_type, cp.communication_style
    ),
    totals AS (
        SELECT 
            SUM(msg_count) as total_msgs,
            COUNT(DISTINCT ma.telegram_user_id) as unique_recipients,
            SUM(responses)::NUMERIC / NULLIF(SUM(msg_count), 0) as resp_rate,
            SUM(clicks)::NUMERIC / NULLIF(SUM(msg_count), 0) as click_rate
        FROM message_analytics ma
        WHERE ma.sent_at >= NOW() - (days_back || ' days')::INTERVAL
          AND (pod_filter IS NULL OR ma.pod_id = pod_filter)
    )
    SELECT 
        t.total_msgs,
        t.unique_recipients,
        COALESCE(t.resp_rate, 0),
        COALESCE(t.click_rate, 0),
        (SELECT jsonb_object_agg(message_type, msg_count) FROM message_stats) as type_breakdown,
        (SELECT jsonb_object_agg(communication_style, SUM(msg_count)) FROM message_stats GROUP BY communication_style) as style_dist
    FROM totals t;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

SELECT 'Communication system tables created:' as status;

SELECT 'communication_preferences' as table_name, COUNT(*) as records FROM communication_preferences
UNION ALL
SELECT 'message_analytics', COUNT(*) FROM message_analytics
UNION ALL  
SELECT 'preference_change_log', COUNT(*) FROM preference_change_log;

-- Show sample engagement data
SELECT 
    communication_style,
    COUNT(*) as users,
    ROUND(AVG(response_rate)::numeric, 3) as avg_response_rate
FROM user_engagement_summary 
GROUP BY communication_style
ORDER BY users DESC;

SELECT '✅ Communication preferences & analytics system ready!' as message;