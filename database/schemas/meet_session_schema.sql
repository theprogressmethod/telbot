-- Google Meet Session Tracking Database Schema
-- Enables automatic attendance detection from Google Admin Reports API

-- Table to track Google Meet sessions linked to our pod meetings
CREATE TABLE meet_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID NOT NULL REFERENCES pod_meetings(id) ON DELETE CASCADE,
    meet_event_id VARCHAR(255), -- Google Calendar event ID
    meet_link VARCHAR(500), -- Google Meet link URL
    meet_code VARCHAR(50), -- Meet conference code (extracted from link)
    organizer_email VARCHAR(255), -- Meeting organizer (usually our system)
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    participant_count INTEGER DEFAULT 0,
    total_minutes_all_participants INTEGER DEFAULT 0, -- Sum of all participant durations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sync_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'synced', 'failed', 'no_data'
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT,
    INDEX(meeting_id),
    INDEX(meet_event_id),
    INDEX(meet_code),
    INDEX(sync_status)
);

-- Table to track individual participant sessions within Meet sessions
CREATE TABLE meet_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meet_session_id UUID NOT NULL REFERENCES meet_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id), -- Matched to our user system
    participant_email VARCHAR(255), -- Email from Google Meet reports
    participant_name VARCHAR(255), -- Display name from Meet
    device_type VARCHAR(50), -- 'web', 'mobile', 'hardware', etc.
    is_external BOOLEAN DEFAULT FALSE, -- External to organization
    is_phone_participant BOOLEAN DEFAULT FALSE, -- PSTN dial-in user
    joined_at TIMESTAMP WITH TIME ZONE,
    left_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    reconnect_count INTEGER DEFAULT 0, -- Number of times rejoined
    audio_minutes INTEGER DEFAULT 0, -- Time with audio enabled
    video_minutes INTEGER DEFAULT 0, -- Time with video enabled
    ip_address INET, -- Participant IP (if available)
    location_country VARCHAR(100), -- Geographic location
    location_region VARCHAR(100),
    call_rating INTEGER, -- Meeting quality rating (1-5)
    network_recv_jitter_mean FLOAT, -- Network quality metrics
    network_send_jitter_mean FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX(meet_session_id),
    INDEX(user_id),
    INDEX(participant_email),
    INDEX(joined_at),
    UNIQUE(meet_session_id, participant_email, joined_at) -- Prevent duplicate entries
);

-- Enhanced meeting_attendance table with Meet session correlation
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_participant_id UUID REFERENCES meet_participants(id);
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS detection_method VARCHAR(50) DEFAULT 'manual'; -- 'manual', 'automatic_meet', 'automatic_calendar'
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_join_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_leave_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_duration_minutes INTEGER;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_reconnect_count INTEGER DEFAULT 0;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_device_type VARCHAR(50);
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 1.0; -- Confidence in automatic detection (0.0-1.0)

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meet_participant ON meeting_attendance(meet_participant_id);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_detection_method ON meeting_attendance(detection_method);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meet_join_time ON meeting_attendance(meet_join_time);

-- Table to track Google Admin Reports API sync status
CREATE TABLE meet_reports_sync (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_date DATE NOT NULL, -- Date being synced (reports are daily)
    application_name VARCHAR(50) DEFAULT 'meet', -- Always 'meet' for our purposes
    event_types TEXT[], -- Array of event types processed: ['call_ended', 'call_started']
    total_events_processed INTEGER DEFAULT 0,
    successful_matches INTEGER DEFAULT 0, -- Events matched to our meetings
    failed_matches INTEGER DEFAULT 0, -- Events that couldn't be matched
    sync_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    next_page_token VARCHAR(500), -- For paginated API responses
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sync_date, application_name),
    INDEX(sync_date),
    INDEX(sync_status)
);

-- Table to store raw Google Meet audit events for debugging and analysis
CREATE TABLE meet_audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(255) NOT NULL, -- Unique event ID from Google
    event_type VARCHAR(100) NOT NULL, -- 'call_ended', 'call_started', etc.
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    user_email VARCHAR(255), -- Actor who performed the action
    meet_code VARCHAR(50), -- Meeting identifier
    organizer_email VARCHAR(255),
    participant_email VARCHAR(255),
    event_data JSONB, -- Full event payload from Google API
    processed BOOLEAN DEFAULT FALSE, -- Whether we've processed this event
    meet_session_id UUID REFERENCES meet_sessions(id), -- Linked to our session
    processing_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX(event_id),
    INDEX(event_type),
    INDEX(event_time),
    INDEX(meet_code),
    INDEX(processed),
    INDEX(meet_session_id),
    UNIQUE(event_id) -- Prevent duplicate events
);

-- Table to map external participant emails to our user system
CREATE TABLE participant_email_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    external_email VARCHAR(255) NOT NULL, -- Email used in Google Meet
    confidence_level VARCHAR(50) DEFAULT 'high', -- 'high', 'medium', 'low'
    mapping_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'automatic', 'domain_match'
    verified BOOLEAN DEFAULT FALSE, -- Whether mapping has been verified
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id), -- Who created this mapping
    INDEX(user_id),
    INDEX(external_email),
    UNIQUE(user_id, external_email)
);

-- View to get comprehensive meeting attendance with Meet data
CREATE OR REPLACE VIEW comprehensive_attendance AS
SELECT 
    ma.id as attendance_id,
    ma.meeting_id,
    ma.user_id,
    ma.attended,
    ma.duration_minutes as recorded_duration,
    ma.detection_method,
    ma.confidence_score,
    -- Meet session data
    ms.meet_link,
    ms.meet_code,
    ms.started_at as meeting_started,
    ms.ended_at as meeting_ended,
    ms.participant_count as total_participants,
    -- Meet participant data
    mp.participant_email,
    mp.participant_name,
    mp.device_type,
    mp.is_external,
    mp.joined_at as meet_joined,
    mp.left_at as meet_left,
    mp.duration_minutes as meet_duration,
    mp.reconnect_count,
    mp.audio_minutes,
    mp.video_minutes,
    mp.call_rating,
    -- User data
    u.name as user_name,
    u.email as user_email,
    -- Meeting data
    pm.meeting_date,
    pm.status as meeting_status
FROM meeting_attendance ma
LEFT JOIN users u ON ma.user_id = u.id
LEFT JOIN pod_meetings pm ON ma.meeting_id = pm.id
LEFT JOIN meet_participants mp ON ma.meet_participant_id = mp.id
LEFT JOIN meet_sessions ms ON mp.meet_session_id = ms.id;

-- Function to automatically update meet_sessions.updated_at
CREATE OR REPLACE FUNCTION update_meet_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_meet_sessions_updated_at
    BEFORE UPDATE ON meet_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_meet_sessions_updated_at();

-- Function to automatically update meet_participants.updated_at
CREATE OR REPLACE FUNCTION update_meet_participants_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_meet_participants_updated_at
    BEFORE UPDATE ON meet_participants
    FOR EACH ROW
    EXECUTE FUNCTION update_meet_participants_updated_at();

-- Comments for documentation
COMMENT ON TABLE meet_sessions IS 'Tracks Google Meet sessions linked to pod meetings';
COMMENT ON TABLE meet_participants IS 'Individual participant data from Google Meet sessions';
COMMENT ON TABLE meet_reports_sync IS 'Tracks synchronization status with Google Admin Reports API';
COMMENT ON TABLE meet_audit_events IS 'Raw Google Meet audit events for debugging and analysis';
COMMENT ON TABLE participant_email_mapping IS 'Maps external emails to internal user accounts';
COMMENT ON VIEW comprehensive_attendance IS 'Complete view of attendance data including Meet session details';