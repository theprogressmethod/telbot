-- Main seed file (runs for all environments by default)
-- This file contains minimal seed data that's safe for production
-- Environment-specific seeds are in the seeds/ directory

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enum types if they don't exist
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'user', 'moderator');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Insert default configuration values
INSERT INTO public.config (key, value, description)
VALUES 
  ('app_name', 'TelBot', 'Application name'),
  ('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
  ('max_retries', '3', 'Maximum number of retry attempts')
ON CONFLICT (key) DO NOTHING;

-- Insert default categories (if table exists)
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categories') THEN
    INSERT INTO public.categories (name, description)
    VALUES 
      ('general', 'General category'),
      ('important', 'Important messages'),
      ('system', 'System messages')
    ON CONFLICT (name) DO NOTHING;
  END IF;
END $$;