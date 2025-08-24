-- Development environment seed data
-- This file contains test data for local development
-- WARNING: This data should NEVER be used in production

-- Test users for development
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'admin@test.com', crypt('admin123', gen_salt('bf')), NOW(), NOW(), NOW()),
  ('22222222-2222-2222-2222-222222222222', 'user@test.com', crypt('user123', gen_salt('bf')), NOW(), NOW(), NOW()),
  ('33333333-3333-3333-3333-333333333333', 'bot@test.com', crypt('bot123', gen_salt('bf')), NOW(), NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Test user profiles
INSERT INTO public.profiles (id, username, full_name, avatar_url)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'admin', 'Admin User', 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin'),
  ('22222222-2222-2222-2222-222222222222', 'testuser', 'Test User', 'https://api.dicebear.com/7.x/avataaars/svg?seed=user'),
  ('33333333-3333-3333-3333-333333333333', 'botuser', 'Bot User', 'https://api.dicebear.com/7.x/avataaars/svg?seed=bot')
ON CONFLICT (id) DO NOTHING;

-- Test telegram data
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'telegram_users') THEN
    INSERT INTO public.telegram_users (telegram_id, username, first_name, last_name, is_bot, language_code)
    VALUES 
      (123456789, 'testuser1', 'Test', 'User 1', false, 'en'),
      (987654321, 'testuser2', 'Test', 'User 2', false, 'en'),
      (16861999, 'dev_admin', 'Dev', 'Admin', false, 'en')
    ON CONFLICT (telegram_id) DO NOTHING;
  END IF;
END $$;

-- Test messages/tasks
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tasks') THEN
    INSERT INTO public.tasks (title, description, status, created_by, assigned_to)
    VALUES 
      ('Test Task 1', 'This is a test task for development', 'pending', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
      ('Test Task 2', 'Another test task', 'in_progress', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
      ('Test Task 3', 'Completed test task', 'completed', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111')
    ON CONFLICT DO NOTHING;
  END IF;
END $$;

-- Test bot commands
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bot_commands') THEN
    INSERT INTO public.bot_commands (command, description, handler, is_active)
    VALUES 
      ('/start', 'Start the bot', 'start_handler', true),
      ('/help', 'Show help message', 'help_handler', true),
      ('/status', 'Check bot status', 'status_handler', true),
      ('/test', 'Test command (dev only)', 'test_handler', true)
    ON CONFLICT (command) DO NOTHING;
  END IF;
END $$;

-- Generate some test activity data
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_log') THEN
    INSERT INTO public.activity_log (user_id, action, details, created_at)
    SELECT 
      (ARRAY['11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid])[floor(random() * 2 + 1)],
      (ARRAY['login', 'logout', 'create', 'update', 'delete'])[floor(random() * 5 + 1)],
      'Test activity ' || generate_series,
      NOW() - (random() * interval '30 days')
    FROM generate_series(1, 50)
    ON CONFLICT DO NOTHING;
  END IF;
END $$;

DO $$ 
BEGIN
  RAISE NOTICE 'Development seed data loaded successfully';
END $$;