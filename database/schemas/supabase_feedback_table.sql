-- Create feedback table in Supabase
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL,
    username TEXT,
    feedback TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_feedback_telegram_user_id ON feedback(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_reviewed ON feedback(reviewed);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow the service role to do everything
CREATE POLICY "Service role can do everything" ON feedback
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Optional: Create a view for unreviewed feedback
CREATE OR REPLACE VIEW unreviewed_feedback AS
SELECT 
    id,
    telegram_user_id,
    username,
    feedback,
    created_at
FROM feedback
WHERE reviewed = FALSE
ORDER BY created_at DESC;

-- Grant permissions
GRANT ALL ON feedback TO authenticated;
GRANT ALL ON feedback TO service_role;

COMMENT ON TABLE feedback IS 'User feedback from Telegram bot';
COMMENT ON COLUMN feedback.telegram_user_id IS 'Telegram user ID who submitted the feedback';
COMMENT ON COLUMN feedback.username IS 'Telegram username or first name';
COMMENT ON COLUMN feedback.feedback IS 'The actual feedback text';
COMMENT ON COLUMN feedback.reviewed IS 'Whether the feedback has been reviewed by admin';
COMMENT ON COLUMN feedback.notes IS 'Admin notes about the feedback';