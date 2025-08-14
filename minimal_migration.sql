-- Minimal Incremental Migration for The Progress Method
-- This only adds essential columns and the user_roles table
-- Run this in Supabase SQL Editor

-- =============================================================================
-- STEP 1: Add missing columns to existing users table
-- =============================================================================

-- First, let's check what columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Add telegram_user_id column if it doesn't exist
DO $$
BEGIN
    -- Check if telegram_user_id column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'telegram_user_id'
    ) THEN
        ALTER TABLE users ADD COLUMN telegram_user_id BIGINT;
        
        -- Add unique constraint
        ALTER TABLE users ADD CONSTRAINT users_telegram_user_id_unique UNIQUE (telegram_user_id);
        
        RAISE NOTICE 'Added telegram_user_id column to users table';
    ELSE
        RAISE NOTICE 'telegram_user_id column already exists';
    END IF;
    
    -- Add first_name if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'first_name'
    ) THEN
        ALTER TABLE users ADD COLUMN first_name TEXT;
        RAISE NOTICE 'Added first_name column';
    END IF;
    
    -- Add username if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'username'
    ) THEN
        ALTER TABLE users ADD COLUMN username TEXT;
        RAISE NOTICE 'Added username column';
    END IF;
    
    -- Add basic tracking columns
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'first_bot_interaction_at'
    ) THEN
        ALTER TABLE users ADD COLUMN first_bot_interaction_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added first_bot_interaction_at column';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'last_activity_at'
    ) THEN
        ALTER TABLE users ADD COLUMN last_activity_at TIMESTAMPTZ DEFAULT NOW();
        RAISE NOTICE 'Added last_activity_at column';
    END IF;
    
    -- Add basic metrics
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'total_commitments'
    ) THEN
        ALTER TABLE users ADD COLUMN total_commitments INTEGER DEFAULT 0;
        RAISE NOTICE 'Added total_commitments column';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'completed_commitments'
    ) THEN
        ALTER TABLE users ADD COLUMN completed_commitments INTEGER DEFAULT 0;
        RAISE NOTICE 'Added completed_commitments column';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'current_streak'
    ) THEN
        ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added current_streak column';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
        RAISE NOTICE 'Added is_active column';
    END IF;

END $$;

-- =============================================================================
-- STEP 2: Create user_roles table only
-- =============================================================================

-- Create user_roles table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_type TEXT NOT NULL CHECK (role_type IN (
        'unpaid', 'paid', 'pod_member', 'admin', 'super_admin', 
        'beta_tester', 'lifetime_member'
    )),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    
    UNIQUE(user_id, role_type)
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_type ON user_roles(role_type);
CREATE INDEX IF NOT EXISTS idx_user_roles_active ON user_roles(user_id, role_type) WHERE is_active = true;

-- =============================================================================
-- STEP 3: Give existing users default roles
-- =============================================================================

-- Give all existing users the 'unpaid' role (but only if they don't already have it)
INSERT INTO user_roles (user_id, role_type)
SELECT u.id, 'unpaid' 
FROM users u
WHERE u.id NOT IN (
    SELECT ur.user_id 
    FROM user_roles ur 
    WHERE ur.role_type = 'unpaid' AND ur.is_active = true
)
ON CONFLICT (user_id, role_type) DO NOTHING;

-- =============================================================================
-- STEP 4: Create simple utility functions
-- =============================================================================

-- Function to check user roles
CREATE OR REPLACE FUNCTION user_has_role(user_uuid UUID, role_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles 
        WHERE user_id = user_uuid 
        AND role_type = role_name 
        AND is_active = true
        AND (expires_at IS NULL OR expires_at > NOW())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to grant role to user
CREATE OR REPLACE FUNCTION grant_user_role(user_uuid UUID, role_name TEXT, granted_by_uuid UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO user_roles (user_id, role_type, granted_by)
    VALUES (user_uuid, role_name, granted_by_uuid)
    ON CONFLICT (user_id, role_type) 
    DO UPDATE SET is_active = true, expires_at = NULL, granted_at = NOW();
    
    RETURN true;
EXCEPTION WHEN OTHERS THEN
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- STEP 5: Enable Row Level Security (basic)
-- =============================================================================

-- Enable RLS on user_roles table
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Service role policy (for bot operations)
DROP POLICY IF EXISTS "Service role full access" ON user_roles;
CREATE POLICY "Service role full access" ON user_roles FOR ALL TO service_role USING (true);

-- Grant permissions
GRANT ALL ON user_roles TO service_role;
GRANT EXECUTE ON FUNCTION user_has_role(UUID, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION grant_user_role(UUID, TEXT, UUID) TO service_role;

-- =============================================================================
-- STEP 6: Summary
-- =============================================================================

SELECT 'Minimal migration completed successfully!' as status;

-- Show what was added
SELECT 
    'users' as table_name,
    COUNT(*) as row_count
FROM users
UNION ALL
SELECT 
    'user_roles' as table_name,
    COUNT(*) as row_count  
FROM user_roles
ORDER BY table_name;

-- Show role distribution
SELECT role_type, COUNT(*) as user_count
FROM user_roles 
WHERE is_active = true
GROUP BY role_type
ORDER BY user_count DESC;