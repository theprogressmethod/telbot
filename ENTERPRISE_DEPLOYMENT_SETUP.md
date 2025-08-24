# 🚀 Enterprise Deployment Setup Guide

## Overview

This guide walks you through setting up a production-grade CI/CD pipeline with comprehensive monitoring, error tracking, and automated deployments.

## 🔧 Required Services

### 1. GitHub Repository
Your code must be in a GitHub repository to use GitHub Actions.

### 2. Sentry (Error Tracking)
1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project (Python)
3. Get your DSN from Project Settings → Client Keys
4. Create an auth token: Settings → Account → API → Auth Tokens

### 3. Uptime Robot (Monitoring)
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Get API key from: My Settings → API Settings → Main API Key

### 4. Slack (Notifications)
1. Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Add Incoming Webhooks
3. Install to your workspace
4. Copy the webhook URL

### 5. Render (Hosting)
1. Sign up at [render.com](https://render.com)
2. Create services for staging and production
3. Get API key from Account Settings → API Keys
4. Note your service IDs from the dashboard URLs

## 📋 Setup Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Create `requirements.txt`:
```txt
# Core
flask==3.0.0
gunicorn==21.2.0
python-telegram-bot==20.7

# Database
psycopg2-binary==2.9.9
redis==5.0.1

# Monitoring & Logging
sentry-sdk[flask]==1.40.0
python-json-logger==2.0.7
psutil==5.9.8

# Testing
pytest==7.4.4
pytest-cov==4.1.0
pytest-asyncio==0.23.3
black==23.12.1
flake8==7.0.0
mypy==1.8.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
```

### Step 2: Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

```yaml
# Sentry
SENTRY_DSN: your-sentry-dsn
SENTRY_AUTH_TOKEN: your-sentry-auth-token
SENTRY_ORG: your-sentry-org
SENTRY_PROJECT: your-project-name

# Render
RENDER_API_KEY: your-render-api-key
RENDER_STAGING_SERVICE_ID: srv-staging-id
RENDER_PRODUCTION_SERVICE_ID: srv-production-id

# Uptime Robot
UPTIME_ROBOT_API_KEY: your-uptime-robot-key
UPTIME_ROBOT_MONITOR_ID: your-monitor-id

# Slack
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Database (for testing)
TEST_DATABASE_URL: postgresql://user:pass@host/testdb

# Optional: SonarCloud
SONAR_TOKEN: your-sonar-token
```

### Step 3: Environment Configuration

Create `.env.production`:
```bash
# Application
ENVIRONMENT=production
APP_VERSION=1.0.0

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
UPTIME_ROBOT_API_KEY=your-key

# Deployment Info (set by CI/CD)
GIT_COMMIT=${GIT_COMMIT}
DEPLOYED_AT=${DEPLOYED_AT}
DEPLOYED_BY=${DEPLOYED_BY}
```

### Step 4: Update Your Main Application

Add health checks and logging to your main Flask app:

```python
# main.py or app.py
from flask import Flask
from logging_config import init_flask_logging, get_logger
from health_check import create_health_endpoints

# Create Flask app
app = Flask(__name__)

# Initialize logging
app = init_flask_logging(app)
logger = get_logger("main")

# Add health check endpoints
app = create_health_endpoints(app)

# Your existing routes...
@app.route('/')
def index():
    logger.logger.info("Index page accessed")
    return "Hello World"

if __name__ == "__main__":
    logger.logger.info("Application starting", extra={
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("APP_VERSION", "unknown")
    })
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

### Step 5: Configure Render Services

Create `render.yaml`:
```yaml
services:
  # Production
  - type: web
    name: telbot-production
    env: python
    region: oregon
    plan: standard
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: telbot-db
          property: connectionString
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: SENTRY_DSN
        sync: false
    healthCheckPath: /health
    autoDeploy: false

  # Staging
  - type: web
    name: telbot-staging
    env: python
    region: oregon
    plan: starter
    branch: develop
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app
    envVars:
      - key: ENVIRONMENT
        value: staging
      - key: DATABASE_URL
        fromDatabase:
          name: telbot-staging-db
          property: connectionString
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: telbot-db
    plan: standard
    
  - name: telbot-staging-db
    plan: starter
```

### Step 6: Set Up Monitoring

#### Uptime Robot Configuration

```python
# scripts/setup_monitoring.py
import os
from health_check import UptimeMonitor

monitor = UptimeMonitor()

# Create monitors for each environment
monitors = [
    {
        "name": "Telbot Production",
        "url": "https://telbot.onrender.com/health",
        "alert_contacts": ["your-alert-contact-id"]
    },
    {
        "name": "Telbot Staging",
        "url": "https://telbot-staging.onrender.com/health",
        "alert_contacts": ["your-alert-contact-id"]
    }
]

for m in monitors:
    result = monitor.create_monitor(**m)
    print(f"Created monitor: {result}")
```

#### Sentry Configuration

Sentry is automatically configured via the `SENTRY_DSN` environment variable. Additional configuration in `sentry.properties`:

```properties
defaults.url=https://sentry.io/
defaults.org=your-org
defaults.project=telbot
cli.executable=sentry-cli
```

### Step 7: Testing the Pipeline

1. **Test locally first:**
```bash
# Run tests
pytest tests/ -v --cov=.

# Check linting
black --check .
flake8 .

# Test health endpoint
python -c "from health_check import health_checker; import json; print(json.dumps(health_checker.get_overall_health(), indent=2))"
```

2. **Create a feature branch:**
```bash
git checkout -b feature/test-deployment
echo "# Test" >> README.md
git add .
git commit -m "Test deployment pipeline"
git push origin feature/test-deployment
```

3. **Open a PR to develop branch**
   - CI pipeline will run tests
   - Check the Actions tab for progress

4. **Merge to develop**
   - Staging deployment will trigger automatically

5. **Merge to main**
   - Production deployment requires manual approval
   - Check Slack for notifications

## 📊 Monitoring Dashboard

### Accessing Metrics

- **Health Check**: `https://your-app.com/health`
- **Readiness**: `https://your-app.com/health/ready`
- **Liveness**: `https://your-app.com/health/live`
- **Prometheus Metrics**: `https://your-app.com/metrics`

### Sentry Dashboard

1. Go to [sentry.io](https://sentry.io)
2. Select your project
3. View:
   - Issues: Real-time errors
   - Performance: Transaction monitoring
   - Releases: Deployment tracking
   - Alerts: Configure alert rules

### Uptime Robot Dashboard

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. View monitor status
3. Set up alert contacts (email, SMS, Slack)
4. Configure status pages

## 🔄 Deployment Workflow

### Development → Staging → Production

1. **Development**
   - Work in feature branches
   - Open PR to `develop`
   - Tests run automatically

2. **Staging**
   - Merge PR to `develop`
   - Auto-deploys to staging
   - Run integration tests

3. **Production**
   - Create PR from `develop` to `main`
   - Requires approval
   - Manual trigger or merge to deploy

### Rollback Procedure

If something goes wrong:

1. **Automatic Rollback** (if health checks fail):
   - Pipeline automatically triggers rollback
   - Previous version restored
   - Slack notification sent

2. **Manual Rollback**:
```bash
# Via Render Dashboard
# 1. Go to your service
# 2. Click "Events"
# 3. Find previous successful deploy
# 4. Click "Rollback to this deploy"

# Via API
curl -X POST https://api.render.com/v1/services/${SERVICE_ID}/deploys/${DEPLOY_ID}/rollback \
  -H "Authorization: Bearer ${RENDER_API_KEY}"
```

## 🔒 Security Best Practices

1. **Never commit secrets**
   - Use environment variables
   - Use GitHub Secrets
   - Use `.env` files (git-ignored)

2. **Rotate credentials regularly**
   - API keys every 90 days
   - Database passwords every 60 days
   - Bot tokens when team members leave

3. **Monitor access logs**
   - Check Sentry for suspicious errors
   - Review GitHub audit logs
   - Monitor database connections

4. **Use least privilege**
   - Separate staging/production databases
   - Different API keys per environment
   - Read-only database users where possible

## 📈 Performance Monitoring

### Key Metrics to Track

1. **Response Times**
   - P50: < 200ms
   - P95: < 1s
   - P99: < 2s

2. **Error Rates**
   - Target: < 1%
   - Alert threshold: > 5%

3. **Uptime**
   - Target: 99.9%
   - Monthly: < 43 minutes downtime

### Setting Up Alerts

In Sentry, create alert rules:
1. Projects → Settings → Alerts
2. Create Alert Rule
3. Set conditions (e.g., error rate > 5%)
4. Configure actions (Slack, email, PagerDuty)

## 🆘 Troubleshooting

### Common Issues

**Pipeline fails at test stage:**
```bash
# Check test output in GitHub Actions
# Run tests locally to debug
pytest tests/ -v --tb=short
```

**Health check failing:**
```bash
# Check each component
curl https://your-app.com/health | jq .

# Check logs
heroku logs --tail  # or equivalent for your platform
```

**Sentry not receiving errors:**
```python
# Test Sentry connection
import sentry_sdk
sentry_sdk.capture_message("Test message")
```

**Deployment stuck:**
```bash
# Check Render dashboard for build logs
# Force redeploy if needed
curl -X POST https://api.render.com/v1/services/${SERVICE_ID}/deploys \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -d '{"clearCache": true}'
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Sentry Python Documentation](https://docs.sentry.io/platforms/python/)
- [Uptime Robot API](https://uptimerobot.com/api/)
- [Render Documentation](https://render.com/docs)
- [Flask Best Practices](https://flask.palletsprojects.com/en/3.0.x/tutorial/)

## 🎯 Next Steps

1. **Set up staging environment** first
2. **Run a test deployment** to staging
3. **Configure monitoring** for staging
4. **Test rollback procedures**
5. **Document your specific workflows**
6. **Train team on procedures**
7. **Set up on-call rotation** if needed

---

## Summary

You now have:
- ✅ Automated CI/CD pipeline with GitHub Actions
- ✅ Error tracking with Sentry
- ✅ Uptime monitoring with Uptime Robot
- ✅ Structured logging with correlation IDs
- ✅ Health check endpoints
- ✅ Prometheus metrics
- ✅ Slack notifications
- ✅ Automated rollback capabilities
- ✅ Staging environment gates
- ✅ Production deployment controls

This is a production-grade setup used by enterprise teams. It provides visibility, reliability, and rapid recovery from issues.
