-- Production seed data
-- MINIMAL data only - essential configuration and nothing else
-- NO test users, NO test data

-- Essential system configuration only
INSERT INTO public.config (key, value, description)
VALUES 
  ('app_version', '1.0.0', 'Current application version'),
  ('maintenance_mode', 'false', 'System maintenance mode flag'),
  ('rate_limit_enabled', 'true', 'Enable rate limiting'),
  ('rate_limit_requests', '100', 'Max requests per window'),
  ('rate_limit_window', '60', 'Rate limit window in seconds')
ON CONFLICT (key) DO NOTHING;

-- Production bot configuration (if table exists)
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bot_config') THEN
    INSERT INTO public.bot_config (key, value, environment)
    VALUES 
      ('webhook_url', 'https://telbot-production.onrender.com/webhook', 'production'),
      ('max_message_length', '4096', 'production'),
      ('rate_limit_messages', '20', 'production'),
      ('rate_limit_window', '60', 'production'),
      ('error_reporting', 'true', 'production')
    ON CONFLICT (key, environment) DO UPDATE 
    SET value = EXCLUDED.value;
  END IF;
END $$;

-- System categories (if needed)
DO $$ 
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categories') THEN
    INSERT INTO public.categories (name, description, is_system)
    VALUES 
      ('system', 'System messages and notifications', true),
      ('user', 'User-generated content', false),
      ('automated', 'Automated messages', true)
    ON CONFLICT (name) DO NOTHING;
  END IF;
END $$;

DO $$ 
BEGIN
  RAISE NOTICE 'Production seed data loaded successfully (minimal configuration only)';
END $$;