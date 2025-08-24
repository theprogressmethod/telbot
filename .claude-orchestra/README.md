# 🎭 Claude Orchestra v2.0

A comprehensive DevOps orchestration system for secure, automated deployments from development to production.

## 🌟 Features

### Security First
- **Smart Git Hooks**: Prevents accidental commits to protected branches
- **Secret Scanning**: Automatically detects API keys, tokens, and credentials
- **Protected Paths**: Blocks modifications to sensitive files
- **Deployment Mode**: Temporary security relaxation for deployments

### Deployment Automation
- **Multi-Environment Support**: Dev → Staging → Production pipeline
- **Automated Backups**: Creates backups before each deployment
- **One-Click Rollback**: Instant rollback to previous versions
- **Health Checks**: Validates service health after deployment

### Developer Experience
- **Simple CLI**: `python3 .claude-orchestra/deploy.py`
- **Interactive Wizard**: Guided deployment process
- **Quick Deploy**: Fast-track production deployments
- **Status Dashboard**: Real-time environment status

## 🚀 Quick Start

### Installation
```bash
# Install Claude Orchestra
python3 .claude-orchestra/deploy.py install
```

### Deploy to Production
```bash
# Quick production deployment
python3 .claude-orchestra/deploy.py quick

# Or interactive mode
python3 .claude-orchestra/deploy.py
```

### Check Status
```bash
python3 .claude-orchestra/deploy.py status
```

## 📚 Usage Guide

### Deployment Modes

#### 1. Interactive Deployment
Perfect for careful, step-by-step deployments:
```bash
python3 .claude-orchestra/deploy.py interactive
```
- Guides you through environment selection
- Runs comprehensive pre-deployment checks
- Requires confirmation for production

#### 2. Quick Deployment
For rapid production deployments:
```bash
python3 .claude-orchestra/deploy.py quick
```
- Automatically enables deployment mode
- Commits and pushes to master
- Sets up Telegram webhooks
- Verifies deployment health

#### 3. Status Check
Monitor all environments:
```bash
python3 .claude-orchestra/deploy.py status
```

### Security Features

#### Deployment Mode
When deploying to production, Claude Orchestra temporarily enables "deployment mode":
- Allows commits to protected branches
- Maintains secret scanning
- Auto-expires after 30 minutes

#### Secret Scanning
Automatically detects:
- API keys and tokens
- Passwords and secrets
- JWT tokens
- Cloud provider credentials
- Telegram bot tokens

#### Branch Protection
Protected branches by default:
- `master` / `main`
- `production`
- `staging`

## 🏗️ Architecture

```
.claude-orchestra/
├── config/
│   └── orchestration-config.yaml    # Central configuration
├── core/
│   ├── deployment_orchestrator.py   # Deployment engine
│   └── security_manager.py          # Security policies
├── logs/
│   ├── orchestration.log           # Main log
│   ├── deployments.log             # Deployment history
│   └── commits.log                 # Commit tracking
├── backups/                        # Automatic backups
├── status/                         # System status
└── deploy.py                       # Main interface
```

## ⚙️ Configuration

Edit `.claude-orchestra/config/orchestration-config.yaml`:

```yaml
environments:
  production:
    branch: "master"
    auto_deploy: false
    requires_approval: true
    test_required: true
    protected: true
    rollback_enabled: true

deployment:
  provider: "render"
  services:
    production:
      service_id: "srv-xxx"
      url: "https://your-app.onrender.com"

safety:
  scan_for_secrets: true
  backup_before_deploy: true
  protected_branches:
    - "master"
    - "production"
```

## 🔧 Advanced Usage

### Manual Security Management

```bash
# Enable deployment mode manually
python3 .claude-orchestra/core/security_manager.py enable-deploy

# Scan for secrets
python3 .claude-orchestra/core/security_manager.py scan

# Check security status
python3 .claude-orchestra/core/security_manager.py status
```

### Direct Orchestrator Commands

```bash
# Deploy to specific environment
python3 .claude-orchestra/core/deployment_orchestrator.py deploy --env production

# Promote staging to production
python3 .claude-orchestra/core/deployment_orchestrator.py promote --from staging --env production

# Rollback with specific backup
python3 .claude-orchestra/core/deployment_orchestrator.py rollback --env production --backup path/to/backup
```

## 🚨 Troubleshooting

### Git Hook Blocking Commits
```bash
# If you need to bypass for emergency:
python3 .claude-orchestra/deploy.py quick

# Or manually enable deployment mode:
python3 .claude-orchestra/core/security_manager.py enable-deploy --duration 60
```

### Deployment Failed
1. Check logs: `.claude-orchestra/logs/orchestration.log`
2. Verify service health: `python3 .claude-orchestra/deploy.py status`
3. Rollback if needed: Use backup path from deployment log

### Webhook Issues
The system automatically configures Telegram webhooks for production deployments.
Check webhook status:
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

## 🔒 Security Best Practices

1. **Never commit secrets**: Let Claude Orchestra scan for you
2. **Use deployment mode**: Don't bypass security permanently
3. **Review before production**: Always check staging first
4. **Keep backups**: Automatic backups are your safety net
5. **Monitor deployments**: Check status after each deployment

## 📊 Monitoring

After deployment, monitor:
- Service health: `https://your-app.onrender.com/health`
- Admin dashboard: `https://your-app.onrender.com/admin/week1`
- Render dashboard: Check service logs in Render console
- Telegram bot: Test commands with @YourBot

## 🤝 Contributing

Claude Orchestra is designed to be extended. Key extension points:
- Add new deployment providers in `core/deployment_orchestrator.py`
- Add secret patterns in `core/security_manager.py`
- Customize git hooks in `security_manager._generate_*_hook()`

## 📝 License

Internal use only. Part of The Progress Method infrastructure.

---

**Built with 🎭 by Claude Orchestra Team**

*Secure deployments, every time.*
