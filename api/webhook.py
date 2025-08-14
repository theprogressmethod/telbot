from http.server import BaseHTTPRequestHandler
import json
import logging
import os
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "Telegram Bot Webhook Active",
            "timestamp": datetime.now().isoformat(),
            "env_check": {
                "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
                "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
                "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
                "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            logger.info(f"📨 Webhook received: {json.dumps(data, indent=2)}")
            
            # Process with bot
            self.process_telegram_update(data)
            
            # Always return 200 to Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            # Still return 200 to prevent Telegram retries
            self.send_response(200)
            self.send_header('Content-type', 'application/json') 
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())
    
    def process_telegram_update(self, data):
        """Process Telegram update with asyncio"""
        try:
            # Import all the bot components
            import asyncio
            from aiogram import Bot, Dispatcher
            from aiogram.types import Update
            from aiogram.fsm.storage.memory import MemoryStorage
            
            # Import our bot configuration and handlers from the parent directory
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            # Now we can import from telbot.py (in parent directory)
            from telbot import Config, SmartAnalysis, DatabaseManager
            from telbot import (
                start_handler, commit_handler, list_handler, done_handler,
                help_handler, handle_text_messages, complete_commitment_callback,
                save_smart_callback, save_original_callback
            )
            from aiogram import F
            from aiogram.filters import Command, CommandStart
            
            # Initialize everything
            config = Config()
            bot = Bot(token=config.bot_token)
            dp = Dispatcher(storage=MemoryStorage())
            
            # Register handlers
            dp.message.register(start_handler, CommandStart())
            dp.message.register(commit_handler, Command("commit"))
            dp.message.register(list_handler, Command("list"))
            dp.message.register(done_handler, Command("done"))
            dp.message.register(help_handler, Command("help"))
            dp.message.register(handle_text_messages)
            
            dp.callback_query.register(complete_commitment_callback, F.data.startswith("complete_"))
            dp.callback_query.register(save_smart_callback, F.data.startswith("save_smart_"))
            dp.callback_query.register(save_original_callback, F.data.startswith("save_original_"))
            
            # Process the update
            update = Update.model_validate(data)
            
            # Run in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(dp.feed_update(bot, update))
            loop.close()
            
            logger.info("✅ Update processed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error processing update: {e}")
            import traceback
            logger.error(traceback.format_exc())