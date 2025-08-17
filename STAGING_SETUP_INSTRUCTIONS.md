
# STAGING ENVIRONMENT SETUP INSTRUCTIONS

## 1. Create Staging Supabase Project
1. Go to https://supabase.com/dashboard
2. Create new project: "telbot-staging"
3. Copy the URL and anon key
4. Update .env.staging with the new credentials

## 2. Create Test Telegram Bot
1. Message @BotFather on Telegram
2. Create new bot: /newbot
3. Name it "Progress Method Staging Bot"
4. Username: "your_staging_bot"
5. Copy the token to .env.staging

## 3. Setup Test API Keys
1. OpenAI: Create test project with limited budget
2. Resend: Use test API key (starts with re_test_)
3. Admin API: Generate secure random key

## 4. Run Database Migrations
1. Open Supabase SQL Editor for staging project
2. Run: database_migrations.sql
3. Verify all tables created

## 5. Load Environment and Test
```bash
# Load staging environment
export $(cat .env.staging | xargs)

# Run staging tests
python3 test_staging_environment.py

# Start staging server
python3 telbot.py --staging
```

## 6. Validation Checklist
- [ ] Staging database created and migrations run
- [ ] Test bot responds to commands
- [ ] Admin dashboard accessible
- [ ] Business intelligence metrics display
- [ ] No production data visible
- [ ] Safety controls active
