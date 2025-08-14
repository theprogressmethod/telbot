import json
import logging
import os
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, BotCommand, Update
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from supabase import create_client, Client
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Class
class Config:
    """Secure configuration management"""
    
    def __init__(self):
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate all required environment variables are present"""
        required_vars = {
            "BOT_TOKEN": "Telegram Bot Token",
            "SUPABASE_URL": "Supabase Project URL", 
            "SUPABASE_KEY": "Supabase API Key",
            "OPENAI_API_KEY": "OpenAI API Key"
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            logger.error("❌ Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"   - {var}")
            raise ValueError(f"Missing required environment variables: {len(missing_vars)} variables")
    
    @property
    def bot_token(self) -> str:
        return os.getenv("BOT_TOKEN", "").strip()
    
    @property
    def supabase_url(self) -> str:
        return os.getenv("SUPABASE_URL", "").strip()
    
    @property
    def supabase_key(self) -> str:
        return os.getenv("SUPABASE_KEY", "").strip()
    
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

# Initialize configuration
config = Config()

# Initialize bot and dispatcher
bot = Bot(token=config.bot_token)
dp = Dispatcher(storage=MemoryStorage())

# Initialize database client
try:
    supabase: Client = create_client(config.supabase_url, config.supabase_key)
    logger.info("✅ Supabase client created successfully")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    supabase = None

# Initialize OpenAI
openai.api_key = config.openai_api_key

# States for FSM
class CommitmentStates(StatesGroup):
    waiting_for_commitment = State()
    processing_smart = State()

class SmartAnalysis:
    """SMART goal analysis class with secure configuration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key)
    
    async def analyze_commitment(self, commitment: str, chat_id: int = None) -> Dict[str, Any]:
        """Analyze commitment using OpenAI for SMART criteria"""
        try:
            logger.info(f"🧠 Starting AI analysis for: {commitment}")
            
            if not self.config.openai_api_key:
                logger.error("❌ OpenAI API key not set")
                return self._fallback_analysis(commitment)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": '''You are a SMART goal analyzer. Analyze the given commitment and score it on SMART criteria:
- Specific (clear and well-defined)
- Measurable (quantifiable)
- Achievable (realistic)
- Relevant (important to the user)
- Time-bound (has a deadline)

Return a JSON object with:
{
  "score": (1-10 overall SMART score),
  "analysis": {
    "specific": (1-10),
    "measurable": (1-10),
    "achievable": (1-10),
    "relevant": (1-10),
    "timeBound": (1-10)
  },
  "smartVersion": "improved version of the commitment",
  "feedback": "brief explanation of improvements"
}'''
                    },
                    {"role": "user", "content": commitment}
                ],
                temperature=0.7,
                timeout=10
            )
            
            content = response.choices[0].message.content
            
            try:
                if "```json" in content:
                    json_match = content.split("```json")[1].split("```")[0]
                    result = json.loads(json_match.strip())
                else:
                    result = json.loads(content)
                
                logger.info(f"✅ SMART analysis successful: Score {result.get('score', 'unknown')}")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                return self._fallback_analysis(commitment)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing commitment: {e}")
            return self._fallback_analysis(commitment)
    
    def _fallback_analysis(self, commitment: str) -> Dict[str, Any]:
        """Provide a fallback analysis when AI fails"""
        score = 5
        
        if len(commitment) > 20:
            score += 1
        if any(word in commitment.lower() for word in ["today", "tomorrow", "week", "month", "by"]):
            score += 1
        if any(word in commitment.lower() for word in ["minutes", "pages", "times", "hours", "km", "miles"]):
            score += 1
        
        return {
            "score": min(score, 8),
            "analysis": {"specific": score, "measurable": score-1, "achievable": score, "relevant": score, "timeBound": score-2},
            "smartVersion": f"{commitment} by the end of this week",
            "feedback": "AI analysis unavailable. Added time frame for better tracking."
        }

class DatabaseManager:
    """Handle database operations"""
    
    @staticmethod
    async def test_database():
        """Test database connection"""
        try:
            if supabase is None:
                return False
            result = supabase.table("commitments").select("*").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}")
            return False
    
    @staticmethod
    async def save_commitment(telegram_user_id: int, commitment: str, original_commitment: str, smart_score: int) -> bool:
        """Save commitment to database"""
        try:
            if supabase is None:
                return False
            
            commitment_data = {
                "telegram_user_id": telegram_user_id,
                "commitment": commitment,
                "original_commitment": original_commitment,
                "status": "active",
                "smart_score": smart_score,
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table("commitments").insert(commitment_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving commitment: {e}")
            return False
    
    @staticmethod
    async def get_active_commitments(telegram_user_id: int) -> List[Dict]:
        """Get active commitments for user"""
        try:
            if supabase is None:
                return []
            
            result = supabase.table("commitments").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "active").execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error getting commitments: {e}")
            return []
    
    @staticmethod
    async def complete_commitment(commitment_id: str) -> bool:
        """Mark commitment as completed"""
        try:
            if supabase is None:
                return False
            
            result = supabase.table("commitments").update({
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }).eq("id", commitment_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error completing commitment: {e}")
            return False

# Initialize analysis engine
smart_analyzer = SmartAnalysis(config)
temp_storage = {}

# Handlers
@dp.message(CommandStart())
async def start_handler(message: Message):
    """Handle /start command"""
    welcome_text = '''Welcome to the Progress Method Accountability Bot! 🎯

I help you track your commitments and build consistency.

Commands:
/commit <text> - Add a new commitment
/done - Mark commitments as complete
/list - View your active commitments
/help - Show this help message

Let's build better habits together! 💪'''
    
    await message.answer(welcome_text)

@dp.message(Command("commit"))
async def commit_handler(message: Message):
    """Handle /commit command"""
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "Please provide a commitment after /commit\n\n"
            "Example: /commit Read for 30 minutes"
        )
        return
    
    commitment_text = command_parts[1].strip()
    user_id = message.from_user.id
    
    # Simple processing for webhook (no fancy loading animations)
    await message.answer("🤖 Analyzing your commitment...")
    
    try:
        analysis = await asyncio.wait_for(
            smart_analyzer.analyze_commitment(commitment_text),
            timeout=10.0
        )
        
        is_smart_enough = analysis["score"] >= 8
        
        if is_smart_enough:
            success = await DatabaseManager.save_commitment(
                telegram_user_id=user_id,
                commitment=commitment_text,
                original_commitment=commitment_text,
                smart_score=analysis["score"]
            )
            
            if success:
                await message.answer(
                    f"✅ Great commitment! (SMART Score: {analysis['score']}/10)\n\n"
                    f"📝 \"{commitment_text}\"\n\n"
                    f"Added to your commitments! Use /done when you complete it."
                )
            else:
                await message.answer("❌ Error saving commitment. Please try again.")
        else:
            # Offer improvement options
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💡 Use SMART version",
                    callback_data=f"save_smart_{user_id}"
                )],
                [InlineKeyboardButton(
                    text="📝 Keep original",
                    callback_data=f"save_original_{user_id}"
                )]
            ])
            
            improvement_text = (
                f"🤔 Your commitment could be more SMART! (Score: {analysis['score']}/10)\n\n"
                f"**Original:** \"{commitment_text}\"\n"
                f"**SMART Version:** \"{analysis['smartVersion']}\"\n\n"
                f"Which version would you like to save?"
            )
            
            temp_storage[f"commit_{user_id}"] = {
                "original": commitment_text,
                "smart": analysis['smartVersion'],
                "score": analysis['score']
            }
            
            await message.answer(improvement_text, reply_markup=keyboard, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"❌ Error in commit handler: {e}")
        # Save anyway with default score
        await DatabaseManager.save_commitment(
            telegram_user_id=user_id,
            commitment=commitment_text,
            original_commitment=commitment_text,
            smart_score=6
        )
        await message.answer(f"✅ Commitment saved!\n\n📝 \"{commitment_text}\"")

@dp.message(Command("list"))
async def list_handler(message: Message):
    """Handle /list command"""
    user_id = message.from_user.id
    commitments = await DatabaseManager.get_active_commitments(user_id)
    
    if not commitments:
        await message.answer("📋 No active commitments.\n\nUse /commit to add one!")
        return
    
    text = "📋 *Your Active Commitments:*\n\n"
    for i, commitment in enumerate(commitments, 1):
        text += f"{i}. {commitment['commitment']}\n"
    
    text += "\nUse /done to mark them complete!"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("done"))
async def done_handler(message: Message):
    """Handle /done command"""
    user_id = message.from_user.id
    commitments = await DatabaseManager.get_active_commitments(user_id)
    
    if not commitments:
        await message.answer("📝 No active commitments found.\n\nUse /commit to add one!")
        return
    
    keyboard_buttons = []
    for i, commitment in enumerate(commitments):
        button_text = f"✓ {i + 1}. {commitment['commitment']}"
        if len(button_text) > 60:
            button_text = button_text[:57] + "..."
        
        keyboard_buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"complete_{commitment['id']}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Select which commitment you've completed:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("complete_"))
async def complete_commitment_callback(callback: CallbackQuery):
    """Handle commitment completion"""
    commitment_id = callback.data.split("_", 1)[1]
    
    success = await DatabaseManager.complete_commitment(commitment_id)
    
    if success:
        await callback.answer("✅ Marked as complete! Great job! 🎉")
        await callback.message.edit_text("🎉 Commitment completed! Great job! 🔥")
    else:
        await callback.answer("❌ Error marking commitment complete. Please try again.")

@dp.callback_query(F.data.startswith("save_smart_"))
async def save_smart_callback(callback: CallbackQuery):
    """Handle saving SMART version"""
    user_id = callback.from_user.id
    stored_data = temp_storage.get(f"commit_{user_id}")
    
    if not stored_data:
        await callback.answer("Session expired. Please try again.")
        return
    
    success = await DatabaseManager.save_commitment(
        telegram_user_id=user_id,
        commitment=stored_data["smart"],
        original_commitment=stored_data["original"],
        smart_score=stored_data["score"]
    )
    
    if success:
        await callback.message.edit_text(f"✅ SMART commitment saved!\n\n📝 \"{stored_data['smart']}\"")
        del temp_storage[f"commit_{user_id}"]
    
    await callback.answer()

@dp.callback_query(F.data.startswith("save_original_"))
async def save_original_callback(callback: CallbackQuery):
    """Handle saving original version"""
    user_id = callback.from_user.id
    stored_data = temp_storage.get(f"commit_{user_id}")
    
    if not stored_data:
        await callback.answer("Session expired. Please try again.")
        return
    
    success = await DatabaseManager.save_commitment(
        telegram_user_id=user_id,
        commitment=stored_data["original"],
        original_commitment=stored_data["original"],
        smart_score=5
    )
    
    if success:
        await callback.message.edit_text(f"✅ Commitment saved!\n\n📝 \"{stored_data['original']}\"")
        del temp_storage[f"commit_{user_id}"]
    
    await callback.answer()

@dp.message(Command("help"))
async def help_handler(message: Message):
    """Handle /help command"""
    help_text = '''📚 *How to use this bot:*

*Add a commitment:*
/commit <your commitment>
Example: /commit Read for 30 minutes

*Mark as complete:*
/done - Shows buttons for each commitment

*View commitments:*
/list - Shows all active commitments

*Tips:*
- Be specific with your commitments
- Start small and build consistency
- Check off completed items daily'''
    
    await message.answer(help_text, parse_mode="Markdown")

@dp.message()
async def handle_text_messages(message: Message):
    """Handle all other text messages"""
    await message.answer(
        "I didn't understand that. Try:\n\n"
        "/commit <your commitment> - Add a new commitment\n"
        "/done - Mark commitments complete\n"
        "/help - See all commands"
    )

async def handler(request):
    """Vercel serverless function handler"""
    try:
        # Handle different HTTP methods
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "Bot is running", "method": "GET"})
            }
        
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"error": "Method not allowed"})
            }
        
        # Get request body
        if hasattr(request, 'body'):
            body = request.body
        elif hasattr(request, 'data'):
            body = request.data
        else:
            # Try to read from request
            body = await request.read() if hasattr(request, 'read') else request
        
        # Parse JSON data
        if isinstance(body, bytes):
            data = json.loads(body.decode('utf-8'))
        elif isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        logger.info(f"Received webhook data: {data}")
        
        # Create Update object from webhook data
        update = Update.model_validate(data)
        
        # Process the update
        await dp.feed_update(bot, update)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"status": "ok"})
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e), "type": type(e).__name__})
        }

# Alternative handler format for Vercel
def lambda_handler(event, context):
    """Alternative lambda-style handler"""
    try:
        # Get body from event
        body = event.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        logger.info(f"Lambda handler received: {data}")
        
        # Create Update object
        update = Update.model_validate(data)
        
        # Process update in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(dp.feed_update(bot, update))
        loop.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"status": "ok"})
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        }