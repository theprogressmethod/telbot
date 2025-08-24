# GitHub Actions Automation Setup

## Quick Start

### 1. Add GitHub Secrets

Go to: Repository Settings → Secrets → Actions

Required secrets:
- `DEV_BOT_TOKEN` - Development bot token
- `STAGING_BOT_TOKEN` - Staging bot token  
- `PROD_BOT_TOKEN` - Production bot token
- `SUPABASE_URL` - Supabase URL
- `SUPABASE_KEY` - Supabase key
- `OPENAI_API_KEY` - OpenAI API key
- `RENDER_API_KEY` - Render API key
- `RENDER_DEPLOY_HOOK_development` - Dev deploy hook
- `RENDER_DEPLOY_HOOK_staging` - Staging deploy hook
- `RENDER_DEPLOY_HOOK_production` - Production deploy hook

### 2. How It Works

#### Automatic Deployment
- Push to `main` → Deploy to production
- Push to `development` → Deploy to development
- Push to `staging` → Deploy to staging

#### Manual Deployment
1. Go to Actions tab
2. Select "Telegram Bot Automated Deployment"
3. Click "Run workflow"
4. Choose environment

#### Scheduled Sync
- Runs daily at 2 AM UTC
- Syncs dev → staging automatically
- Can be triggered manually

### 3. Workflow Files

- `.github/workflows/deploy-bot.yml` - Main deployment
- `.github/workflows/scheduled-sync.yml` - Daily sync
- `.github/scripts/validate_bot.py` - Bot validation
- `.github/scripts/validate_env.py` - Environment check
- `.github/scripts/check_database.py` - Database check
- `.github/scripts/rollback.sh` - Rollback script

### 4. Features

✅ Automatic backups before deployment
✅ Configuration validation
✅ Health checks after deployment
✅ Automatic rollback on failure
✅ Slack notifications (optional)
✅ Issue creation on rollback

### 5. Testing

Test the workflow:
```bash
# Push to development branch
git checkout development
git push origin development

# Check Actions tab in GitHub
```

### 6. Monitoring

- Check Actions tab for deployment status
- Review artifacts for backup files
- Check issues for rollback notifications

## Troubleshooting

### Deployment Failed
1. Check Actions logs
2. Verify secrets are set
3. Check Render service status

### Bot Not Responding
1. Verify webhook URL
2. Check bot token
3. Review deployment logs

### Rollback Needed
- Automatic rollback triggers on production failures
- Manual: Run workflow with previous commit

## Support

For issues, check:
- GitHub Actions logs
- Render dashboard
- Telegram Bot API status
