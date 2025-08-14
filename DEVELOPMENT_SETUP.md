# Development Setup Guide

Protect your production bot while developing new features.

## 🏗️ Current Setup

**Production Environment:**
- **Branch**: `master`
- **Render**: `https://telbot-f4on.onrender.com` 
- **Status**: ✅ Live and working
- **Bot**: Your main Telegram bot

**Development Environment:**
- **Branch**: `development` 
- **Render**: Create new service for testing
- **Bot**: Create separate test bot

## 🚀 Development Workflow

### Step 1: Create Test Bot (Optional but Recommended)

1. **Create new bot with BotFather:**
   ```
   /newbot
   Bot Name: Progress Method Dev Bot
   Username: your_bot_name_dev_bot
   ```
   
2. **Save the new bot token** for development environment variables

### Step 2: Set Up Development Render Service

1. **Create new Render service:**
   - Go to Render dashboard
   - "New +" → "Web Service" 
   - Connect same GitHub repo: `theprogressmethod/telbot`
   - **Important**: Select `development` branch
   - Name: `telbot-dev` (or similar)

2. **Use same settings as production:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free

3. **Environment Variables:**
   ```
   BOT_TOKEN=your_dev_bot_token_here
   SUPABASE_URL=same_as_production
   SUPABASE_KEY=same_as_production  
   OPENAI_API_KEY=same_as_production
   ```

### Step 3: Development Process

```bash
# Switch to development branch
git checkout development

# Make your changes
# - Add new features
# - Redesign components
# - Experiment freely

# Test locally (optional)
python main.py

# Commit and push to development
git add .
git commit -m "Add new feature: XYZ"
git push origin development

# Render auto-deploys development branch
# Test on: https://your-dev-service.onrender.com
```

### Step 4: Deploy to Production

When your features are ready:

```bash
# Switch to master
git checkout master

# Merge development changes
git merge development

# Push to production
git push origin master

# Production Render auto-deploys
```

## 🔒 Safety Features

**Protected Production:**
- Production only deploys from `master` branch
- Development changes don't affect production until merged
- Separate test bot prevents interference

**Easy Rollback:**
- If something breaks, revert the merge
- Production immediately rolls back to previous version

**Isolated Testing:**
- Test all features thoroughly in development
- Multiple people can test dev bot simultaneously

## 📁 Branch Strategy

```
master (production)
├── Always stable and working
├── Connected to production Render service
└── Your live bot users interact with this

development 
├── All new features and experiments
├── Connected to development Render service  
├── Test bot for safe testing
└── Merge to master when ready
```

## 🛠️ Alternative: Local Development Only

If you prefer simpler setup:

```bash
# Work on development branch
git checkout development

# Test locally with ngrok (like before)
python telbot.py  # Local testing
ngrok http 8000   # If needed

# When ready, merge to master
git checkout master
git merge development
git push
```

## 🔄 Recommended Workflow

1. **Always develop on `development` branch**
2. **Set up separate dev Render service** (5 minutes)
3. **Create test bot** for safe testing
4. **Test thoroughly** before merging to master
5. **Merge to master** when ready for production

This gives you complete freedom to experiment while keeping your working bot safe! 🎯

## Next Steps

1. Create development Render service
2. Set up test bot (optional)
3. Start developing new features on `development` branch
4. Test thoroughly before merging to production