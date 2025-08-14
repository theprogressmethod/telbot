# Railway Deployment Guide

This guide explains how to deploy the Progress Method Telegram Bot to Railway for independent operation.

## Why Railway?

- ✅ No authentication required for webhooks (unlike Vercel)
- ✅ Simple deployment from GitHub
- ✅ Built-in environment variable management
- ✅ Automatic HTTPS endpoints
- ✅ Python/FastAPI support out of the box

## Deployment Steps

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Verify your account

### 2. Deploy from GitHub
1. Click "New Project" in Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your `telbot` repository
4. Railway will automatically detect the Python project

### 3. Set Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```
BOT_TOKEN=your_telegram_bot_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### 4. Deploy
1. Railway will automatically deploy after you add the environment variables
2. Wait for the deployment to complete (2-3 minutes)
3. Note the generated URL (e.g., `https://telbot-production-abc123.up.railway.app`)

### 5. Set Telegram Webhook
Once deployed, set the webhook URL with Telegram:

**Option A: Using the bot's built-in endpoint**
- Visit: `https://your-railway-url.railway.app/set_webhook?url=https://your-railway-url.railway.app`

**Option B: Using Telegram Bot API directly**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-railway-url.railway.app/webhook"}'
```

### 6. Test the Bot
1. Check health: `https://your-railway-url.railway.app/health`
2. Test in Telegram: Send `/start` to your bot
3. Try `/commit read a book` to test full functionality

## Monitoring

- **Health Check**: `https://your-railway-url.railway.app/health`
- **Root Status**: `https://your-railway-url.railway.app/`
- **Webhook Info**: `https://your-railway-url.railway.app/webhook_info`
- **Railway Logs**: Available in Railway dashboard under "Deployments" tab

## Files Included

- `main.py` - FastAPI application for Railway
- `requirements.txt` - Python dependencies
- `Procfile` - Process configuration
- `railway.json` - Railway deployment settings
- `telbot.py` - Core bot logic (imported by main.py)

## Troubleshooting

### Bot not responding
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Test health endpoint: `/health`
4. Check webhook info: `/webhook_info`

### Database errors
1. Verify Supabase URL and key
2. Check if database tables exist
3. Test database connection: `/health`

### AI analysis failing
1. Verify OpenAI API key is correct
2. Check OpenAI account has credits
3. Bot will fallback to basic analysis if AI fails

## Cost

Railway offers:
- $5/month developer plan with generous usage
- Pay-as-you-use pricing
- Much more cost-effective than keeping a local machine running 24/7

## Next Steps

Once deployed successfully:
1. Test all bot commands thoroughly
2. Monitor logs for the first few days
3. Consider setting up monitoring alerts
4. Document the final webhook URL for future reference

The bot will now run completely independently without requiring any local infrastructure!