#!/usr/bin/env python3
"""
FastAPI-based Telegram Bot for Railway deployment
Handles webhooks from Telegram for the Progress Method Accountability Bot
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Import our bot components
from telbot import (
    Config, SmartAnalysis, DatabaseManager, bot, dp,
    start_handler, commit_handler, list_handler, done_handler,
    help_handler, feedback_handler, handle_text_messages, complete_commitment_callback,
    save_smart_callback, save_original_callback, cancel_commit_callback,
    cancel_done_callback, set_bot_commands
)
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Update

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
config = None
smart_analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global config, smart_analyzer
    
    try:
        # Initialize configuration
        config = Config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize SMART analyzer
        smart_analyzer = SmartAnalysis(config)
        logger.info("✅ SMART analyzer initialized")
        
        # Register all handlers
        dp.message.register(start_handler, CommandStart())
        dp.message.register(commit_handler, Command("commit"))
        dp.message.register(list_handler, Command("list"))
        dp.message.register(done_handler, Command("done"))
        dp.message.register(feedback_handler, Command("feedback"))
        dp.message.register(help_handler, Command("help"))
        dp.message.register(handle_text_messages)
        
        # Register callback handlers
        dp.callback_query.register(complete_commitment_callback, F.data.startswith("complete_"))
        dp.callback_query.register(save_smart_callback, F.data.startswith("save_smart_"))
        dp.callback_query.register(save_original_callback, F.data.startswith("save_original_"))
        dp.callback_query.register(cancel_commit_callback, F.data == "cancel_commit")
        dp.callback_query.register(cancel_done_callback, F.data == "cancel_done")
        
        logger.info("✅ All handlers registered successfully")
        
        # Set bot commands
        await set_bot_commands()
        logger.info("✅ Bot commands set successfully")
        
        # Test database connection
        db_test = await DatabaseManager.test_database()
        if db_test:
            logger.info("✅ Database connection test successful")
        else:
            logger.warning("⚠️ Database connection test failed")
        
        logger.info("🚀 Bot startup completed successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    finally:
        # Cleanup
        if bot.session:
            await bot.session.close()
        logger.info("🛑 Bot shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Progress Method Telegram Bot",
    description="Accountability bot with SMART goal analysis",
    version="1.0.0",
    lifespan=lifespan
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
    """Detailed health check"""
    try:
        # Test database
        db_healthy = await DatabaseManager.test_database()
        
        # Test configuration
        config_healthy = bool(config and config.bot_token and config.openai_api_key)
        
        health_status = {
            "status": "healthy" if (db_healthy and config_healthy) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "✅ healthy" if db_healthy else "❌ unhealthy",
                "configuration": "✅ healthy" if config_healthy else "❌ unhealthy",
                "bot": "✅ healthy" if bot else "❌ unhealthy"
            }
        }
        
        status_code = 200 if (db_healthy and config_healthy) else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhooks from Telegram"""
    try:
        # Get request body
        body = await request.body()
        if not body:
            logger.warning("⚠️ Empty webhook body received")
            return JSONResponse(content={"status": "error", "message": "Empty body"}, status_code=400)
        
        # Parse JSON
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in webhook: {e}")
            return JSONResponse(content={"status": "error", "message": "Invalid JSON"}, status_code=400)
        
        logger.info(f"📨 Webhook received from Telegram")
        logger.debug(f"Webhook data: {json.dumps(data, indent=2)}")
        
        # Validate bot is ready
        if not bot:
            logger.error("❌ Bot not initialized")
            return JSONResponse(content={"status": "error", "message": "Bot not ready"}, status_code=503)
        
        # Create Update object
        try:
            update = Update.model_validate(data)
        except Exception as e:
            logger.error(f"❌ Failed to parse Telegram update: {e}")
            return JSONResponse(content={"status": "error", "message": "Invalid update format"}, status_code=400)
        
        # Process the update
        try:
            await dp.feed_update(bot, update)
            logger.info("✅ Update processed successfully")
            return JSONResponse(content={"status": "ok"})
            
        except Exception as e:
            logger.error(f"❌ Error processing update: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Still return 200 to prevent Telegram from retrying
            return JSONResponse(content={"status": "error", "message": "Processing failed"})
            
    except Exception as e:
        logger.error(f"❌ Webhook handler error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Always return 200 to Telegram to prevent retries
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.get("/set_webhook")
async def set_webhook(url: str = None):
    """Set webhook URL for the bot (for testing)"""
    if not url:
        return {"error": "Please provide URL parameter: /set_webhook?url=YOUR_WEBHOOK_URL"}
    
    try:
        webhook_url = f"{url}/webhook"
        result = await bot.set_webhook(url=webhook_url)
        
        if result:
            logger.info(f"✅ Webhook set successfully to: {webhook_url}")
            return {"status": "success", "webhook_url": webhook_url}
        else:
            logger.error("❌ Failed to set webhook")
            return {"status": "error", "message": "Failed to set webhook"}
            
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/webhook_info")
async def get_webhook_info():
    """Get current webhook information"""
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
    except Exception as e:
        logger.error(f"❌ Error getting webhook info: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)