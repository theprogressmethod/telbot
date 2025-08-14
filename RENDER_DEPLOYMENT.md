# Render Deployment Guide (FREE)

Deploy your Telegram bot to Render's free tier for independent 24/7 operation.

## Why Render?

- ✅ **500 hours/month FREE** (enough for continuous operation)
- ✅ No authentication required for webhooks (unlike Vercel)
- ✅ Deploy directly from GitHub
- ✅ Automatic HTTPS and SSL
- ✅ Built-in environment variable management
- ✅ Simple Python/FastAPI deployment
- ⚠️ Apps "spin down" after 15 minutes of inactivity (1-2 second wake-up time)

## Quick Deployment (5 minutes)

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub (free)

### 2. Deploy from GitHub
1. Click "New +" → "Web Service"
2. Connect your GitHub account
3. Select your `telbot` repository
4. Choose these settings:
   - **Name**: `telbot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

### 3. Set Environment Variables
In the "Environment" section, add:
```
BOT_TOKEN=your_telegram_bot_token_here
SUPABASE_URL=https://your-project.supabase.co  
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### 4. Deploy
- Click "Create Web Service"
- Wait 2-3 minutes for deployment
- Note your URL: `https://telbot-abc123.onrender.com`

### 5. Set Telegram Webhook
**Option A**: Visit your bot's endpoint
```
https://your-render-url.onrender.com/set_webhook?url=https://your-render-url.onrender.com
```

**Option B**: Use curl
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
     -d "url=https://your-render-url.onrender.com/webhook"
```

### 6. Test Your Bot
1. **Health check**: `https://your-render-url.onrender.com/health`
2. **Test in Telegram**: Send `/start` to your bot
3. **Test full flow**: `/commit read a book for 30 minutes`

## Free Tier Details

**Render Free Tier Includes:**
- 500 hours/month (720 hours = full month)
- Automatic HTTPS
- Custom domains
- GitHub auto-deploy
- Environment variables
- Logs and monitoring

**Limitations:**
- Apps spin down after 15 minutes of inactivity
- 1-2 second wake-up time when bot receives first message after sleeping
- 512MB RAM limit (more than enough for this bot)

## Keeping Bot Active (Optional)

To minimize spin-down, you can:

1. **UptimeRobot** (free monitoring service):
   - Ping your health endpoint every 5 minutes
   - Sign up at uptimerobot.com
   - Monitor: `https://your-render-url.onrender.com/health`

2. **GitHub Actions** (ping script):
   ```yaml
   # .github/workflows/keepalive.yml
   name: Keep Alive
   on:
     schedule:
       - cron: '*/10 * * * *'  # Every 10 minutes
   jobs:
     ping:
       runs-on: ubuntu-latest
       steps:
         - run: curl https://your-render-url.onrender.com/health
   ```

## Monitoring

- **Render Dashboard**: Real-time logs and metrics
- **Health endpoint**: `/health` - shows database and bot status  
- **Webhook info**: `/webhook_info` - Telegram webhook status
- **Root status**: `/` - Basic bot information

## Troubleshooting

**Bot not responding:**
1. Check Render logs in dashboard
2. Verify environment variables
3. Test health endpoint
4. Check if app is sleeping (first message after inactivity takes 1-2s)

**Frequent sleeping:**
- Set up UptimeRobot to ping every 5-10 minutes
- Normal behavior for free tier

## Cost Comparison

| Platform | Free Tier | Always On | Webhook Support |
|----------|-----------|-----------|-----------------|
| **Render** | 500h/month | No (spins down) | ✅ Yes |
| Railway | $5 credit | Yes | ✅ Yes |
| Vercel | Unlimited | Yes | ❌ Auth required |
| Heroku | Limited | No (spins down) | ✅ Yes |

**Render is the best free option** for Telegram bots!

## Upgrade Path

When ready to upgrade:
- **Render Pro**: $7/month for always-on
- **Railway**: $5/month usage-based
- Both eliminate spin-down delays

Your bot will run independently with full functionality on Render's free tier!