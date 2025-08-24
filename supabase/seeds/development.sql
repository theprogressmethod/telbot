-- Development seed data
-- This file contains test data for development environment

-- Insert test users
INSERT INTO users (telegram_id, username, first_name, last_name, email, is_admin) VALUES
    (123456789, 'test_user1', 'Test', 'User1', 'test1@example.com', false),
    (987654321, 'test_user2', 'Test', 'User2', 'test2@example.com', false),
    (555555555, 'admin_user', 'Admin', 'User', 'admin@example.com', true)
ON CONFLICT (telegram_id) DO NOTHING;

-- Insert test pods
INSERT INTO pods (name, description, max_members) VALUES
    ('Test Pod 1', 'Development test pod 1', 5),
    ('Test Pod 2', 'Development test pod 2', 5)
ON CONFLICT DO NOTHING;

-- Assign users to pods
INSERT INTO pod_members (pod_id, user_id, role)
SELECT 
    p.id,
    u.id,
    CASE WHEN u.username = 'admin_user' THEN 'leader' ELSE 'member' END
FROM pods p
CROSS JOIN users u
WHERE p.name = 'Test Pod 1'
    AND u.username IN ('test_user1', 'admin_user')
ON CONFLICT DO NOTHING;

-- Insert test commitments
INSERT INTO commitments (user_id, telegram_id, text, category, status) 
SELECT 
    u.id,
    u.telegram_id,
    'Test commitment for ' || u.username,
    'test',
    'pending'
FROM users u
WHERE u.username LIKE 'test%'
ON CONFLICT DO NOTHING;

-- Insert test messages
INSERT INTO messages (user_id, telegram_id, message_type, content, scheduled_for)
SELECT 
    u.id,
    u.telegram_id,
    'nurture',
    'Test nurture message for ' || u.username,
    CURRENT_TIMESTAMP + INTERVAL '1 day'
FROM users u
WHERE u.username LIKE 'test%'
ON CONFLICT DO NOTHING;
