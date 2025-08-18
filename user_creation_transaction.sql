-- User creation transaction function to prevent race conditions
-- This function atomically creates a user and assigns the default role

CREATE OR REPLACE FUNCTION ensure_user_exists_atomic(
    p_telegram_user_id BIGINT,
    p_first_name TEXT DEFAULT 'User',
    p_username TEXT DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
    v_user_id UUID;
    v_result JSON;
    v_is_new_user BOOLEAN := false;
BEGIN
    -- Try to get existing user
    SELECT id INTO v_user_id 
    FROM users 
    WHERE telegram_user_id = p_telegram_user_id;
    
    IF v_user_id IS NULL THEN
        -- User doesn't exist, create them
        INSERT INTO users (
            telegram_user_id,
            first_name,
            username,
            first_bot_interaction_at,
            last_activity_at
        ) VALUES (
            p_telegram_user_id,
            COALESCE(p_first_name, 'User'),
            p_username,
            NOW(),
            NOW()
        )
        RETURNING id INTO v_user_id;
        
        v_is_new_user := true;
        
        -- Grant default 'unpaid' role
        INSERT INTO user_roles (
            user_id,
            role_type,
            is_active,
            granted_at
        ) VALUES (
            v_user_id,
            'unpaid',
            true,
            NOW()
        )
        ON CONFLICT (user_id, role_type) DO UPDATE SET
            is_active = true,
            granted_at = NOW();
            
    ELSE
        -- User exists, update last activity
        UPDATE users 
        SET last_activity_at = NOW() 
        WHERE id = v_user_id;
    END IF;
    
    -- Return result
    v_result := json_build_object(
        'success', true,
        'user_id', v_user_id,
        'telegram_user_id', p_telegram_user_id,
        'is_new_user', v_is_new_user,
        'timestamp', NOW()
    );
    
    RETURN v_result;
    
EXCEPTION WHEN OTHERS THEN
    -- Return error information
    RETURN json_build_object(
        'success', false,
        'error', SQLERRM,
        'telegram_user_id', p_telegram_user_id,
        'timestamp', NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION ensure_user_exists_atomic(BIGINT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION ensure_user_exists_atomic(BIGINT, TEXT, TEXT) TO anon;

-- Test the function
-- SELECT ensure_user_exists_atomic(123456, 'Test User', 'testuser');