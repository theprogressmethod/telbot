# TelBot - Telegram Accountability Bot

A Telegram bot that helps users track commitments and build consistency using SMART goal analysis.

## Features

- **Smart Goal Analysis**: AI-powered analysis of commitments using OpenAI
- **SMART Scoring**: Evaluates commitments on Specific, Measurable, Achievable, Relevant, Time-bound criteria
- **Database Integration**: Stores commitments in Supabase
- **Interactive UI**: Inline keyboards for easy commitment management
- **Real-time Processing**: Webhook-based deployment for instant responses

## Commands

- `/start` - Welcome message and introduction
- `/commit <text>` - Add a new commitment
- `/done` - Mark commitments as complete
- `/list` - View your active commitments
- `/help` - Show help message

## Deployment

This bot is configured for Vercel serverless deployment using webhooks.

### Environment Variables

Set these in your Vercel dashboard:

- `BOT_TOKEN` - Your Telegram Bot Token from @BotFather
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key
- `OPENAI_API_KEY` - Your OpenAI API key

### Database Schema

The bot requires a `commitments` table in Supabase with the following structure:

```sql
CREATE TABLE commitments (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  telegram_user_id BIGINT NOT NULL,
  commitment TEXT NOT NULL,
  original_commitment TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  smart_score INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
```

3. Run the bot locally:
```bash
python telbot.py
```

## Webhook Setup

After deploying to Vercel, set your webhook URL:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-vercel-domain.vercel.app/api/webhook"}'
```

## License

MIT License