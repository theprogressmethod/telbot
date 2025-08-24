-- Essential Tables for Pod, Attendance, and Nurture Systems
-- Phase 1: Core functionality with reasonable scope
-- Run this in DEVELOPMENT database first for testing

-- ============================================
-- PODS AND MEMBERSHIP (Simplified)
-- ============================================

-- Basic pods table (minimal viable structure)
CREATE TABLE IF NOT EXISTS pods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    meeting_day INT CHECK (meeting_day >= 0 AND meeting_day <= 6), -- 0=Sunday, 6=Saturday
    meeting_time TIME DEFAULT '19:00:00', -- Default 7pm
    max_members INT DEFAULT 8,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pod memberships (who's in which pod)
CREATE TABLE IF NOT EXISTS pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, pod_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_pod_memberships_user ON pod_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_pod_memberships_pod ON pod_memberships(pod_id);

-- ============================================
-- POD WEEK TRACKING (Simplified)
-- ============================================

-- Track pod weeks (simplified - just track current week)
CREATE TABLE IF NOT EXISTS pod_weeks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    week_number INT NOT NULL,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(pod_id, week_number)
);

-- Link commitments to pod weeks
CREATE TABLE IF NOT EXISTS pod_week_commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_week_id UUID REFERENCES pod_weeks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    commitment_id INT REFERENCES commitments(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(commitment_id)
);

CREATE INDEX IF NOT EXISTS idx_pod_week_commitments_user ON pod_week_commitments(user_id);
CREATE INDEX IF NOT EXISTS idx_pod_week_commitments_week ON pod_week_commitments(pod_week_id);

-- ============================================
-- MEETING ATTENDANCE (Simplified)
-- ============================================

-- Track pod meetings
CREATE TABLE IF NOT EXISTS pod_meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    meeting_date DATE NOT NULL,
    meeting_time TIME DEFAULT '19:00:00',
    status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(pod_id, meeting_date)
);

-- Track who attended
CREATE TABLE IF NOT EXISTS meeting_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES pod_meetings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    attended BOOLEAN DEFAULT false,
    duration_minutes INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(meeting_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_attendance_meeting ON meeting_attendance(meeting_id);
CREATE INDEX IF NOT EXISTS idx_attendance_user ON meeting_attendance(user_id);

-- ============================================
-- NURTURE SEQUENCES (Simplified)
-- ============================================

-- Track which sequences users are in
CREATE TABLE IF NOT EXISTS user_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sequence_type TEXT NOT NULL, -- 'onboarding', 'commitment_followup', 're_engagement', etc.
    current_step INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_sent_at TIMESTAMPTZ,
    next_send_at TIMESTAMPTZ,
    UNIQUE(user_id, sequence_type)
);

-- Log sent messages (for tracking/debugging)
CREATE TABLE IF NOT EXISTS sent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sequence_type TEXT,
    message_type TEXT, -- 'nurture', 'reminder', 'celebration'
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    success BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_user_sequences_user ON user_sequences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sequences_active ON user_sequences(is_active);
CREATE INDEX IF NOT EXISTS idx_sent_messages_user ON sent_messages(user_id);

-- ============================================
-- TEST DATA (Safe for development)
-- ============================================

-- Create a test pod
INSERT INTO pods (id, name, meeting_day, meeting_time, status)
VALUES ('11111111-1111-1111-1111-111111111111', 'Test Pod Alpha', 1, '19:00:00', 'active')
ON CONFLICT DO NOTHING;

-- Add existing users to the test pod
INSERT INTO pod_memberships (user_id, pod_id)
SELECT u.id, '11111111-1111-1111-1111-111111111111'
FROM users u
WHERE u.telegram_user_id IN (865415132) -- Thomas
ON CONFLICT DO NOTHING;

-- Create a current pod week
INSERT INTO pod_weeks (pod_id, week_number, week_start, week_end)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    1,
    date_trunc('week', CURRENT_DATE)::date,
    (date_trunc('week', CURRENT_DATE) + interval '6 days')::date
)
ON CONFLICT DO NOTHING;

-- Create a test meeting for this week
INSERT INTO pod_meetings (pod_id, meeting_date, status)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    date_trunc('week', CURRENT_DATE)::date + 1, -- Monday
    'scheduled'
)
ON CONFLICT DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check what was created
SELECT 'Pods created:' as info, COUNT(*) as count FROM pods
UNION ALL
SELECT 'Pod memberships:', COUNT(*) FROM pod_memberships
UNION ALL
SELECT 'Pod weeks:', COUNT(*) FROM pod_weeks
UNION ALL
SELECT 'Pod meetings:', COUNT(*) FROM pod_meetings
UNION ALL
SELECT 'User sequences:', COUNT(*) FROM user_sequences;

-- Success message
SELECT '✅ Essential tables created successfully!' as message;