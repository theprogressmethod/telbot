-- Step-by-Step Google Meet Schema Application
-- Apply each section individually to identify any issues

-- STEP 1: Enable UUID extension (run this first if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- STEP 2: Create meet_sessions table
CREATE TABLE meet_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID NOT NULL REFERENCES pod_meetings(id) ON DELETE CASCADE,
    meet_event_id VARCHAR(255),
    meet_link VARCHAR(500),
    meet_code VARCHAR(50),
    organizer_email VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    participant_count INTEGER DEFAULT 0,
    total_minutes_all_participants INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sync_status VARCHAR(50) DEFAULT 'pending',
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT
);

-- STEP 3: Create indexes for meet_sessions
CREATE INDEX idx_meet_sessions_meeting_id ON meet_sessions(meeting_id);
CREATE INDEX idx_meet_sessions_meet_event_id ON meet_sessions(meet_event_id);
CREATE INDEX idx_meet_sessions_meet_code ON meet_sessions(meet_code);
CREATE INDEX idx_meet_sessions_sync_status ON meet_sessions(sync_status);

-- STEP 4: Create meet_participants table
CREATE TABLE meet_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meet_session_id UUID NOT NULL REFERENCES meet_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    participant_email VARCHAR(255),
    participant_name VARCHAR(255),
    device_type VARCHAR(50),
    is_external BOOLEAN DEFAULT FALSE,
    is_phone_participant BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP WITH TIME ZONE,
    left_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    reconnect_count INTEGER DEFAULT 0,
    audio_minutes INTEGER DEFAULT 0,
    video_minutes INTEGER DEFAULT 0,
    ip_address INET,
    location_country VARCHAR(100),
    location_region VARCHAR(100),
    call_rating INTEGER,
    network_recv_jitter_mean FLOAT,
    network_send_jitter_mean FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- STEP 5: Create indexes for meet_participants
CREATE INDEX idx_meet_participants_session_id ON meet_participants(meet_session_id);
CREATE INDEX idx_meet_participants_user_id ON meet_participants(user_id);
CREATE INDEX idx_meet_participants_email ON meet_participants(participant_email);
CREATE INDEX idx_meet_participants_joined_at ON meet_participants(joined_at);

-- Add unique constraint to prevent duplicates
ALTER TABLE meet_participants ADD CONSTRAINT unique_session_email_join 
UNIQUE(meet_session_id, participant_email, joined_at);

-- STEP 6: Create remaining support tables
CREATE TABLE meet_reports_sync (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_date DATE NOT NULL,
    application_name VARCHAR(50) DEFAULT 'meet',
    event_types TEXT[],
    total_events_processed INTEGER DEFAULT 0,
    successful_matches INTEGER DEFAULT 0,
    failed_matches INTEGER DEFAULT 0,
    sync_status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    next_page_token VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE meet_audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    user_email VARCHAR(255),
    meet_code VARCHAR(50),
    organizer_email VARCHAR(255),
    participant_email VARCHAR(255),
    event_data JSONB,
    processed BOOLEAN DEFAULT FALSE,
    meet_session_id UUID REFERENCES meet_sessions(id),
    processing_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE participant_email_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    external_email VARCHAR(255) NOT NULL,
    confidence_level VARCHAR(50) DEFAULT 'high',
    mapping_source VARCHAR(50) DEFAULT 'manual',
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- STEP 7: Add indexes for support tables
CREATE INDEX idx_meet_reports_sync_date ON meet_reports_sync(sync_date);
CREATE INDEX idx_meet_reports_sync_status ON meet_reports_sync(sync_status);
CREATE UNIQUE INDEX idx_meet_reports_sync_unique ON meet_reports_sync(sync_date, application_name);

CREATE INDEX idx_meet_audit_events_event_id ON meet_audit_events(event_id);
CREATE INDEX idx_meet_audit_events_type ON meet_audit_events(event_type);
CREATE INDEX idx_meet_audit_events_time ON meet_audit_events(event_time);
CREATE INDEX idx_meet_audit_events_code ON meet_audit_events(meet_code);
CREATE INDEX idx_meet_audit_events_processed ON meet_audit_events(processed);
CREATE INDEX idx_meet_audit_events_session ON meet_audit_events(meet_session_id);

CREATE INDEX idx_participant_mapping_user ON participant_email_mapping(user_id);
CREATE INDEX idx_participant_mapping_email ON participant_email_mapping(external_email);
CREATE UNIQUE INDEX idx_participant_mapping_unique ON participant_email_mapping(user_id, external_email);

-- STEP 8: Enhance meeting_attendance table
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_participant_id UUID REFERENCES meet_participants(id);
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS detection_method VARCHAR(50) DEFAULT 'manual';
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_join_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_leave_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_duration_minutes INTEGER;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_reconnect_count INTEGER DEFAULT 0;
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS meet_device_type VARCHAR(50);
ALTER TABLE meeting_attendance ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 1.0;

-- STEP 9: Create indexes for new meeting_attendance columns
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meet_participant ON meeting_attendance(meet_participant_id);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_detection_method ON meeting_attendance(detection_method);
CREATE INDEX IF NOT EXISTS idx_meeting_attendance_meet_join_time ON meeting_attendance(meet_join_time);

-- STEP 10: Add comments for documentation
COMMENT ON TABLE meet_sessions IS 'Tracks Google Meet sessions linked to pod meetings';
COMMENT ON TABLE meet_participants IS 'Individual participant data from Google Meet sessions';
COMMENT ON TABLE meet_reports_sync IS 'Tracks synchronization status with Google Admin Reports API';
COMMENT ON TABLE meet_audit_events IS 'Raw Google Meet audit events for debugging and analysis';
COMMENT ON TABLE participant_email_mapping IS 'Maps external emails to internal user accounts';