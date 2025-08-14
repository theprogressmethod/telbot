from http.server import BaseHTTPRequestHandler
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for health check"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "Telegram Bot Webhook is running",
                "method": "GET",
                "env_vars_set": {
                    "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
                    "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
                    "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
                    "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"GET error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                webhook_data = json.loads(post_data.decode('utf-8'))
            else:
                webhook_data = {}
            
            logger.info(f"Received webhook data: {json.dumps(webhook_data, indent=2)}")
            
            # Check if we have environment variables
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                logger.error("BOT_TOKEN not set")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "BOT_TOKEN not configured"}).encode())
                return
            
            # Import and process with aiogram
            try:
                import asyncio
                from aiogram import Bot, Dispatcher
                from aiogram.types import Update
                from aiogram.fsm.storage.memory import MemoryStorage
                
                # Import handlers
                from . import bot_handlers
                
                # Create bot and dispatcher
                bot = Bot(token=bot_token)
                dp = Dispatcher(storage=MemoryStorage())
                
                # Register handlers
                bot_handlers.register_handlers(dp)
                
                # Process update
                update = Update.model_validate(webhook_data)
                
                # Run in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(dp.feed_update(bot, update))
                loop.close()
                
                logger.info("Successfully processed webhook")
                
            except Exception as bot_error:
                logger.error(f"Bot processing error: {bot_error}")
                # Still return 200 to Telegram so it doesn't retry
            
            # Always return 200 to Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "received",
                "update_id": webhook_data.get("update_id"),
                "has_message": "message" in webhook_data,
                "message_text": webhook_data.get("message", {}).get("text", "")
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"POST error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Still return 200 to prevent Telegram retries
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())