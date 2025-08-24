-- Staging environment seed data
-- This file contains realistic test data for staging environment
-- Data should be production-like but not contain real user information

-- Staging test users (with obvious test emails)
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at)
VALUES 
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'staging-admin@theprogressmethod.com', crypt('StagingAdmin2024!', gen_salt('bf')), NOW(), NOW(), NOW()),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'staging-user1@theprogressmethod.com', crypt('StagingUser2024!', gen_salt('bf')), NOW(), NOW(), NOW()),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'staging-bot@theprogressmethod.com', crypt('StagingBot2024!', gen_salt('bf')), NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Staging user profiles
INSERT INTO public.profiles (id, username, full_name, avatar_url)
VALUES 
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'staging_admin', 'Staging Admin', 'https://api.dicebear.com/7.x/avataaars/svg?seed=staging-admin'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'staging_user1', 'Staging User One', 'https://api.dicebear.com/7.x/avataaars/svg?seed=staging-user1'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'staging_bot', 'Staging Bot', 'https://api.dicebear.com/7.x/avataaars/svg?seed=staging-bot')
ON CONFLICT (id) DO NOTHING;

-- Staging telegram users
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'telegram_users') THEN
    INSERT INTO public.telegram_users (telegram_id, username, first_name, last_name, is_bot, language_code)
    VALUES 
      (900000001, 'staging_test1', 'Staging', 'Tester 1', false, 'en'),
      (900000002, 'staging_test2', 'Staging', 'Tester 2', false, 'en'),
      (900000003, 'staging_test3', 'Staging', 'Tester 3', false, 'en')
    ON CONFLICT (telegram_id) DO NOTHING;
  END IF;
END $$;

-- Realistic staging tasks
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tasks') THEN
    INSERT INTO public.tasks (title, description, status, priority, created_by)
    VALUES 
      ('Staging: User Onboarding Flow', 'Test the complete user onboarding process', 'in_progress', 'high', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
      ('Staging: Payment Integration', 'Verify payment gateway integration', 'pending', 'critical', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
      ('Staging: Email Notifications', 'Test all email notification templates', 'completed', 'medium', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
      ('Staging: API Rate Limiting', 'Verify API rate limiting works correctly', 'pending', 'low', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb')
    ON CONFLICT DO NOTHING;
  END IF;
END $$;

-- Staging bot configuration
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bot_config') THEN
    INSERT INTO public.bot_config (key, value, environment)
    VALUES 
      ('webhook_url', 'https://telbot-staging.onrender.com/webhook', 'staging'),
      ('max_message_length', '4096', 'staging'),
      ('rate_limit_messages', '30', 'staging'),
      ('rate_limit_window', '60', 'staging')
    ON CONFLICT (key, environment) DO UPDATE 
    SET value = EXCLUDED.value;
  END IF;
END $$;

-- Generate realistic staging activity
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_log') THEN
    -- Generate varied activity over the past week
    INSERT INTO public.activity_log (user_id, action, details, created_at)
    SELECT 
      (ARRAY['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 
             'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid,
             'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid])[floor(random() * 3 + 1)],
      (ARRAY['user.login', 'user.logout', 'task.create', 'task.update', 'task.complete', 
             'message.send', 'message.receive', 'webhook.received', 'api.call'])[floor(random() * 9 + 1)],
      'Staging test activity #' || generate_series,
      NOW() - (random() * interval '7 days')
    FROM generate_series(1, 100)
    ON CONFLICT DO NOTHING;
  END IF;
END $$;

DO $$ 
BEGIN
  RAISE NOTICE 'Staging seed data loaded successfully';
END $$;