# AI-Driven CI/CD Deployment Guide

## 🚀 Overview

This repository uses a **95% AI-automated CI/CD pipeline** powered by Claude AI, GitHub Actions, Render, and Supabase.

## 📊 Architecture

```
GitHub → AI Analysis → Tests → Deploy → Monitor
  ↓         ↓           ↓        ↓         ↓
Branch   Claude AI   Pytest   Render    Axiom
```

## 🔄 Deployment Flow

### 1. Development Environment
- **Branch**: `development`
- **URL**: https://telbot-dev.onrender.com
- **Database**: Supabase Dev (apfiwfkpdhslfavnncsl)
- **Auto-deploy**: On every push

### 2. Staging Environment  
- **Branch**: `staging`
- **URL**: https://telbot-staging.onrender.com
- **Database**: Supabase Dev (apfiwfkpdhslfavnncsl)
- **Auto-deploy**: On PR merge from development

### 3. Production Environment
- **Branch**: `master`
- **URL**: https://telbot-production.onrender.com
- **Database**: Supabase Prod (prtfkiodnbogqfcztruj)
- **Auto-deploy**: On PR merge from staging

## 🤖 AI Features

1. **Risk Analysis**: Every change is analyzed by Claude for deployment risks
2. **Auto-decision**: AI decides if deployment should proceed
3. **Test Analysis**: Failed tests are analyzed with fix suggestions
4. **Health Monitoring**: AI-powered health checks after deployment
5. **Auto-rollback**: Automatic rollback on failures

## 📝 Workflow

### For Developers

1. **Create feature branch** from `development`
   ```bash
   git checkout -b feature/my-feature development
   ```

2. **Push changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push origin feature/my-feature
   ```

3. **Create PR** to `development`
   - AI automatically reviews code
   - Tests run automatically
   - Merge when checks pass

4. **Deploy to Staging**
   - Create PR from `development` to `staging`
   - AI validates changes
   - Auto-deploys on merge

5. **Deploy to Production**
   - Create PR from `staging` to `master`
   - Requires manual approval
   - Auto-deploys on merge

## 🔑 Required Secrets

Configure these in GitHub Settings → Secrets:

| Secret | Description | Required |
|--------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude AI API key | ✅ |
| `RENDER_API_KEY` | Render.com API key | ✅ |
| `SUPABASE_ACCESS_TOKEN` | Supabase access token | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Optional |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Optional |
| `AXIOM_TOKEN` | Axiom logging token | Optional |
| `AXIOM_ORG_ID` | Axiom organization ID | Optional |

## 🛠️ Manual Commands

### Force Deployment
```bash
gh workflow run ai-cicd-pipeline.yml -f environment=production
```

### Check Status
```bash
gh run list --workflow=ai-cicd-pipeline.yml
```

### View Logs
```bash
gh run view [run-id] --log
```

## 📊 Monitoring

### Render Dashboard
- Development: [View](https://dashboard.render.com/web/srv-d2em4oripnbc73a5bmog)
- Staging: [View](https://dashboard.render.com/web/srv-d2ftel8gjchc73aekca0)
- Production: [View](https://dashboard.render.com/web/srv-d2h9ckggjchc73bumn60)

### GitHub Actions
- [View Workflows](https://github.com/theprogressmethod/telbot/actions)

### Supabase
- Dev: [Dashboard](https://app.supabase.com/project/apfiwfkpdhslfavnncsl)
- Prod: [Dashboard](https://app.supabase.com/project/prtfkiodnbogqfcztruj)

## 🚨 Troubleshooting

### Deployment Failed
1. Check GitHub Actions logs
2. Review Telegram notifications
3. Check Render logs

### Database Migration Failed
1. Test locally: `supabase db reset`
2. Check migration syntax
3. Review Supabase logs

### Health Check Failed
- Auto-rollback initiated
- Check `/health` endpoint
- Review application logs

### Rollback Needed
```bash
# Manual rollback via Render
curl -X POST "https://api.render.com/v1/services/[SERVICE_ID]/deploys" \
  -H "Authorization: Bearer [RENDER_API_KEY]" \
  -d '{"commitId": "[PREVIOUS_COMMIT]"}'
```

## 📈 Success Metrics

- ✅ 95%+ deployments automated
- ✅ < 5 minute deployment time
- ✅ Zero-downtime deployments
- ✅ Automatic rollback on failures
- ✅ AI-powered risk assessment

## 🆘 Support

- **GitHub Issues**: [Create Issue](https://github.com/theprogressmethod/telbot/issues)
- **Telegram**: Notifications sent to configured chat
- **Logs**: Check Axiom dashboard (if configured)

## 📚 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Render Docs](https://render.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Claude API Docs](https://docs.anthropic.com)

---

**Last Updated**: August 2025
**Maintained by**: The Progress Method
