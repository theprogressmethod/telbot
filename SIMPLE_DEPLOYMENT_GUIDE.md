# 🚀 Super Simple Deployment Guide

## Quick Start (5 minutes)

### 1. First Time Setup
```bash
chmod +x *.sh
./setup.sh
```

### 2. Check Everything Works
```bash
./status.sh
```

### 3. Deploy!
```bash
./deploy.sh staging      # Test environment
./deploy.sh production   # Live environment
```

That's it! 🎉

---

## 📚 All Commands (One-Liner Cheat Sheet)

| What You Want | Command | What It Does |
|--------------|---------|--------------|
| Set everything up | `./setup.sh` | One-time setup |
| Deploy to staging | `./deploy.sh staging` | Test your changes |
| Deploy to production | `./deploy.sh production` | Go live! |
| Check if everything's OK | `./status.sh` | Health check |
| Something broke! | `./fix.sh` | Auto-fix problems |
| View logs | `./logs.sh` | See what happened |
| Undo deployment | `./deploy.sh rollback` | Go back to previous |
| Run tests | `./deploy.sh test` | Test locally |

---

## 🎮 Daily Workflow

### Morning: Check Status
```bash
./status.sh
```
Shows you:
- ✅ Production: Healthy
- ✅ Staging: Healthy  
- Recent deployments
- Any issues

### Working on Features
```bash
# 1. Make your changes
# 2. Test locally
./deploy.sh test

# 3. Deploy to staging
./deploy.sh staging

# 4. Test on staging URL
# 5. Deploy to production
./deploy.sh production
```

### If Something Breaks
```bash
# Don't panic! Run:
./fix.sh

# Or just rollback:
./deploy.sh rollback
```

---

## 🚨 Emergency Procedures

### Production is Down!
```bash
./fix.sh
# Choose option 1 (rollback)
```

### Can't Deploy
```bash
./status.sh          # Check what's wrong
./fix.sh            # Try auto-fix
./logs.sh production # Check error logs
```

### Need to Rollback
```bash
./deploy.sh rollback
```

---

## 📝 What Each Script Does

### `deploy.sh`
Your main deployment tool. Handles everything:
- Checks you're on the right branch
- Runs tests automatically  
- Creates backups
- Deploys safely
- Shows clear success/failure

### `status.sh`
Your dashboard. Shows:
- Health of all environments
- Recent commits
- Quick actions
- Current branch

### `fix.sh`
Your emergency button:
- Diagnoses problems
- Suggests fixes
- Can rollback
- Restarts services

### `logs.sh`
View logs from anywhere:
- Production logs
- Staging logs
- Error logs only
- Local logs

### `setup.sh`
Run once to set up:
- Installs dependencies
- Creates config files
- Sets up git hooks
- Makes scripts executable

---

## ⚙️ Configuration

### Environment Files
Edit `.env.production` with your credentials:
```bash
DATABASE_URL=your_database_url
TELEGRAM_BOT_TOKEN=your_bot_token
SENTRY_DSN=your_sentry_dsn
```

### URLs
Edit the URLs in scripts if needed:
- `deploy.sh` - Line 17-18
- `status.sh` - Line 14-15  
- `fix.sh` - Line 13

---

## 🎯 Best Practices

1. **Always deploy to staging first**
   ```bash
   ./deploy.sh staging
   # Test it
   ./deploy.sh production
   ```

2. **Check status before deploying**
   ```bash
   ./status.sh
   ./deploy.sh production
   ```

3. **Keep main branch clean**
   - Work in feature branches
   - Merge to develop for staging
   - Merge to main for production

4. **Use the emergency tools**
   - Don't try to fix manually
   - Use `./fix.sh` first
   - Rollback if needed

---

## 🆘 Troubleshooting

### "Permission denied"
```bash
chmod +x *.sh
```

### "Command not found"
```bash
# Use ./ prefix
./deploy.sh status
```

### "Tests failed"
```bash
# Fix your code, then:
./deploy.sh test
```

### "Can't connect to health endpoint"
```bash
# Check your URLs in the scripts
# Check if services are running
./status.sh
```

---

## 💡 Pro Tips

1. **Add to your .bashrc/.zshrc:**
   ```bash
   alias deploy='./deploy.sh'
   alias status='./status.sh'
   alias fix='./fix.sh'
   ```

2. **Watch logs live:**
   ```bash
   watch -n 5 ./status.sh
   ```

3. **Quick deploy to staging:**
   ```bash
   ./deploy.sh staging && open https://telbot-staging.onrender.com
   ```

---

## 📞 Still Need Help?

1. Run `./status.sh` - shows current state
2. Run `./fix.sh` - tries to auto-fix
3. Check `./logs.sh` - see what went wrong
4. Use `./deploy.sh rollback` - undo changes

Remember: These scripts make deployment simple and safe. You can always rollback!

---

**Made deployment simple.** No more complex commands. No more remembering Git workflows. Just simple scripts that work. 🎉
