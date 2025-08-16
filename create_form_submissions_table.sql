-- Create form_submissions table for storing user form data from various sources
CREATE TABLE IF NOT EXISTS public.form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_type TEXT NOT NULL DEFAULT 'user_registration',
    form_data JSONB NOT NULL DEFAULT '{}',
    user_name TEXT,
    user_email TEXT,
    user_phone TEXT,
    telegram_user_id BIGINT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    source TEXT DEFAULT 'form',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON public.form_submissions(status);
CREATE INDEX IF NOT EXISTS idx_form_submissions_source ON public.form_submissions(source);
CREATE INDEX IF NOT EXISTS idx_form_submissions_telegram_id ON public.form_submissions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_email ON public.form_submissions(user_email);
CREATE INDEX IF NOT EXISTS idx_form_submissions_created ON public.form_submissions(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.form_submissions ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to read
CREATE POLICY "Authenticated users can read form submissions"
    ON public.form_submissions
    FOR SELECT
    TO authenticated
    USING (true);

-- Create policy for service role to manage
CREATE POLICY "Service role can manage form submissions"
    ON public.form_submissions
    FOR ALL
    TO service_role
    USING (true);

-- Add comments for documentation
COMMENT ON TABLE public.form_submissions IS 'Stores form submissions from various sources including Excel imports, web forms, etc.';
COMMENT ON COLUMN public.form_submissions.form_type IS 'Type of form: user_registration, survey, feedback, etc.';
COMMENT ON COLUMN public.form_submissions.form_data IS 'JSON data containing all form fields';
COMMENT ON COLUMN public.form_submissions.status IS 'Processing status: pending, processed, failed, duplicate';
COMMENT ON COLUMN public.form_submissions.source IS 'Source of submission: form, excel_import, api, etc.';