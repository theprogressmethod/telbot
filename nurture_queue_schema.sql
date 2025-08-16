-- Nurture Message Queue Schema
-- Database tables for attendance-triggered nurture sequences

-- Table to store nurture sequence states for each user
CREATE TABLE IF NOT EXISTS nurture_sequence_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_type TEXT NOT NULL,
    current_step INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_nurture_sequence_states_user_id ON nurture_sequence_states(user_id);
CREATE INDEX IF NOT EXISTS idx_nurture_sequence_states_type ON nurture_sequence_states(sequence_type);
CREATE INDEX IF NOT EXISTS idx_nurture_sequence_states_active ON nurture_sequence_states(user_id, sequence_type) WHERE completed_at IS NULL;

-- Table to store message queue for scheduled delivery
CREATE TABLE IF NOT EXISTS nurture_message_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_user_id BIGINT NOT NULL,
    message_content TEXT NOT NULL,
    message_type TEXT DEFAULT 'nurture_sequence',
    priority INTEGER DEFAULT 5, -- 1=highest, 10=lowest
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queue processing
CREATE INDEX IF NOT EXISTS idx_nurture_message_queue_scheduled ON nurture_message_queue(scheduled_for) WHERE sent_at IS NULL AND failed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_nurture_message_queue_user ON nurture_message_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_nurture_message_queue_telegram ON nurture_message_queue(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_nurture_message_queue_pending ON nurture_message_queue(scheduled_for, retry_count) WHERE sent_at IS NULL AND (failed_at IS NULL OR retry_count < max_retries);

-- Table to track attendance events and triggers
CREATE TABLE IF NOT EXISTS attendance_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    meeting_id UUID REFERENCES pod_meetings(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'first_meeting_attended', 'meeting_missed', 'early_arrival', etc.
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    nurture_triggered BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for attendance event processing
CREATE INDEX IF NOT EXISTS idx_attendance_events_user_id ON attendance_events(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_events_meeting_id ON attendance_events(meeting_id);
CREATE INDEX IF NOT EXISTS idx_attendance_events_type ON attendance_events(event_type);
CREATE INDEX IF NOT EXISTS idx_attendance_events_unprocessed ON attendance_events(event_time) WHERE processed_at IS NULL;

-- Table to track nurture sequence delivery metrics
CREATE TABLE IF NOT EXISTS nurture_delivery_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    sequence_type TEXT,
    message_type TEXT,
    messages_scheduled INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_failed INTEGER DEFAULT 0,
    messages_skipped INTEGER DEFAULT 0,
    unique_users_reached INTEGER DEFAULT 0,
    avg_delivery_time_minutes NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint to prevent duplicate metrics
CREATE UNIQUE INDEX IF NOT EXISTS idx_nurture_metrics_unique ON nurture_delivery_metrics(date, sequence_type, message_type);

-- Table to store user nurture preferences and opt-outs
CREATE TABLE IF NOT EXISTS nurture_user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_type TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    frequency TEXT DEFAULT 'normal', -- 'minimal', 'normal', 'frequent'
    time_preference TEXT DEFAULT 'morning', -- 'morning', 'afternoon', 'evening'
    timezone TEXT DEFAULT 'UTC',
    opted_out_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unique constraint for user preferences
CREATE UNIQUE INDEX IF NOT EXISTS idx_nurture_preferences_unique ON nurture_user_preferences(user_id, sequence_type);

-- View for active nurture sequences
CREATE OR REPLACE VIEW active_nurture_sequences AS
SELECT 
    nss.*,
    u.first_name,
    u.email,
    u.telegram_user_id,
    EXTRACT(EPOCH FROM (NOW() - nss.last_message_at))/3600 AS hours_since_last_message
FROM nurture_sequence_states nss
JOIN users u ON nss.user_id = u.id
WHERE nss.completed_at IS NULL
  AND (nss.last_message_at IS NULL OR nss.last_message_at < NOW() - INTERVAL '23 hours');

-- View for pending message queue
CREATE OR REPLACE VIEW pending_nurture_messages AS
SELECT 
    nmq.*,
    u.first_name,
    u.email,
    EXTRACT(EPOCH FROM (nmq.scheduled_for - NOW()))/60 AS minutes_until_send
FROM nurture_message_queue nmq
JOIN users u ON nmq.user_id = u.id
WHERE nmq.sent_at IS NULL 
  AND (nmq.failed_at IS NULL OR nmq.retry_count < nmq.max_retries)
  AND nmq.scheduled_for <= NOW() + INTERVAL '1 hour'
ORDER BY nmq.scheduled_for;

-- Function to clean up old processed messages (run via cron)
CREATE OR REPLACE FUNCTION cleanup_old_nurture_messages(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM nurture_message_queue 
    WHERE created_at < NOW() - (days_to_keep || ' days')::INTERVAL
      AND (sent_at IS NOT NULL OR (failed_at IS NOT NULL AND retry_count >= max_retries));
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's nurture stats
CREATE OR REPLACE FUNCTION get_user_nurture_stats(target_user_id UUID)
RETURNS TABLE (
    total_sequences INTEGER,
    active_sequences INTEGER,
    completed_sequences INTEGER,
    messages_sent INTEGER,
    messages_pending INTEGER,
    last_message_sent TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INTEGER FROM nurture_sequence_states WHERE user_id = target_user_id),
        (SELECT COUNT(*)::INTEGER FROM nurture_sequence_states WHERE user_id = target_user_id AND completed_at IS NULL),
        (SELECT COUNT(*)::INTEGER FROM nurture_sequence_states WHERE user_id = target_user_id AND completed_at IS NOT NULL),
        (SELECT COUNT(*)::INTEGER FROM nurture_message_queue WHERE user_id = target_user_id AND sent_at IS NOT NULL),
        (SELECT COUNT(*)::INTEGER FROM nurture_message_queue WHERE user_id = target_user_id AND sent_at IS NULL AND (failed_at IS NULL OR retry_count < max_retries)),
        (SELECT MAX(sent_at) FROM nurture_message_queue WHERE user_id = target_user_id AND sent_at IS NOT NULL);
END;
$$ LANGUAGE plpgsql;

-- Add RLS policies if enabled
-- Enable RLS on nurture tables
ALTER TABLE nurture_sequence_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE nurture_message_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE nurture_user_preferences ENABLE ROW LEVEL SECURITY;

-- Policies for service role (full access)
CREATE POLICY IF NOT EXISTS "Service role full access to nurture_sequence_states" ON nurture_sequence_states
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access to nurture_message_queue" ON nurture_message_queue
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access to attendance_events" ON attendance_events
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access to nurture_user_preferences" ON nurture_user_preferences
    FOR ALL USING (auth.role() = 'service_role');

-- Policies for authenticated users (own data only)
CREATE POLICY IF NOT EXISTS "Users can view own nurture states" ON nurture_sequence_states
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY IF NOT EXISTS "Users can view own message queue" ON nurture_message_queue
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY IF NOT EXISTS "Users can view own attendance events" ON attendance_events
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY IF NOT EXISTS "Users can manage own nurture preferences" ON nurture_user_preferences
    FOR ALL USING (user_id = auth.uid());

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON nurture_sequence_states TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON nurture_message_queue TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON attendance_events TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON nurture_delivery_metrics TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON nurture_user_preferences TO service_role;

GRANT SELECT ON active_nurture_sequences TO service_role;
GRANT SELECT ON pending_nurture_messages TO service_role;

GRANT EXECUTE ON FUNCTION cleanup_old_nurture_messages(INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION get_user_nurture_stats(UUID) TO service_role;

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'Nurture sequence database schema created successfully!';
    RAISE NOTICE 'Tables created: nurture_sequence_states, nurture_message_queue, attendance_events, nurture_delivery_metrics, nurture_user_preferences';
    RAISE NOTICE 'Views created: active_nurture_sequences, pending_nurture_messages';
    RAISE NOTICE 'Functions created: cleanup_old_nurture_messages, get_user_nurture_stats';
END $$;