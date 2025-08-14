-- Create table for accountability pod applications
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS pod_applications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    telegram_username TEXT,
    goal TEXT NOT NULL,
    why_accountability TEXT NOT NULL,
    timezone TEXT NOT NULL,
    weekly_commitment TEXT NOT NULL,
    agreed_to_terms BOOLEAN NOT NULL DEFAULT false,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Admin fields
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'waitlist')),
    admin_notes TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    pod_assignment TEXT,
    
    -- Tracking
    source TEXT DEFAULT 'web_form',
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT
);

-- Indexes for faster queries
CREATE INDEX idx_applications_status ON pod_applications(status);
CREATE INDEX idx_applications_email ON pod_applications(email);
CREATE INDEX idx_applications_applied_at ON pod_applications(applied_at DESC);

-- Prevent duplicate applications
CREATE UNIQUE INDEX idx_unique_email ON pod_applications(email) WHERE status != 'rejected';

-- Enable RLS
ALTER TABLE pod_applications ENABLE ROW LEVEL SECURITY;

-- Admin view for pending applications
CREATE OR REPLACE VIEW pending_applications AS
SELECT 
    id,
    name,
    email,
    telegram_username,
    goal,
    timezone,
    weekly_commitment,
    applied_at
FROM pod_applications
WHERE status = 'pending'
ORDER BY applied_at ASC;

-- Grant permissions
GRANT ALL ON pod_applications TO authenticated;
GRANT SELECT ON pending_applications TO authenticated;

COMMENT ON TABLE pod_applications IS 'Applications for accountability pod membership';
COMMENT ON COLUMN pod_applications.status IS 'Application status: pending, approved, rejected, or waitlist';
COMMENT ON COLUMN pod_applications.pod_assignment IS 'Which pod group they were assigned to';