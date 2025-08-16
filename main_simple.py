#!/usr/bin/env python3
"""
Simplified main.py for production with minimal dependencies
Only includes webhook and basic admin functionality
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Progress Method Telegram Bot",
    description="Accountability bot with SMART goal analysis",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ Progress Method Bot is running!",
        "timestamp": datetime.now().isoformat(),
        "environment_check": {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Simple admin dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h1>Progress Method Admin Dashboard</h1>
        <div class="card">
            <h2>System Status</h2>
            <p>✅ Admin dashboard is accessible!</p>
            <p>Timestamp: """ + datetime.now().isoformat() + """</p>
        </div>
        <div class="card">
            <h2>Quick Links</h2>
            <ul>
                <li><a href="/admin/api/test">Test API Endpoint</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/">Root Status</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/admin/api/test")
async def admin_api_test():
    """Test admin API endpoint"""
    return {
        "status": "Admin API working",
        "timestamp": datetime.now().isoformat(),
        "message": "If you see this, admin routes are loading correctly!"
    }

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhooks from Telegram"""
    try:
        # Import bot components only when needed
        from telbot import bot, dp
        from aiogram.types import Update
        
        # Get request body
        data = await request.json()
        logger.info(f"Webhook received: {json.dumps(data)[:200]}...")
        
        # Process update
        update = Update(**data)
        await dp.feed_update(bot, update)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/set_webhook")
async def set_webhook():
    """Set webhook URL for Telegram"""
    try:
        from telbot import bot
        
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            raise HTTPException(status_code=400, detail="WEBHOOK_URL not configured")
        
        # Remove any existing webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Set new webhook
        success = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        if success:
            info = await bot.get_webhook_info()
            return {
                "status": "Webhook set successfully",
                "url": info.url,
                "pending_updates": info.pending_update_count
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")
            
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook_info")
async def webhook_info():
    """Get current webhook information"""
    try:
        from telbot import bot
        
        info = await bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        logger.error(f"Webhook info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)