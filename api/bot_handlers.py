import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, BotCommand
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from supabase import create_client, Client
import openai

# Configure logging
logger = logging.getLogger(__name__)

# Global variables for bot components
bot = None
supabase = None
smart_analyzer = None
temp_storage = {}

# Configuration Class
class Config:
    """Secure configuration management"""
    
    def __init__(self):
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate all required environment variables are present"""
        required_vars = ["BOT_TOKEN", "SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
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

# States for FSM
class CommitmentStates(StatesGroup):
    waiting_for_commitment = State()
    processing_smart = State()

class SmartAnalysis:
    """SMART goal analysis class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key)
    
    async def analyze_commitment(self, commitment: str) -> Dict[str, Any]:
        """Analyze commitment using OpenAI for SMART criteria"""
        try:
            if not self.config.openai_api_key:
                return self._fallback_analysis(commitment)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": '''Analyze the given commitment and score it on SMART criteria. Return JSON:
{
  "score": (1-10 overall SMART score),
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
                
                return result
                
            except json.JSONDecodeError:
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
        if any(word in commitment.lower() for word in ["minutes", "pages", "times", "hours"]):
            score += 1
        
        return {
            "score": min(score, 8),
            "smartVersion": f"{commitment} by the end of this week",
            "feedback": "AI analysis unavailable. Added time frame for better tracking."
        }

class DatabaseManager:
    """Handle database operations"""
    
    @staticmethod
    async def save_commitment(telegram_user_id: int, commitment: str, original_commitment: str, smart_score: int) -> bool:
        """Save commitment to database"""
        try:
            if supabase is None:
                logger.error("❌ Supabase client not available")
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
            logger.info(f"✅ Commitment saved successfully")
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

# Message Handlers
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

async def handle_text_messages(message: Message):
    """Handle all other text messages"""
    await message.answer(
        "I didn't understand that. Try:\n\n"
        "/commit <your commitment> - Add a new commitment\n"
        "/done - Mark commitments complete\n"
        "/help - See all commands"
    )

# Callback handlers
async def complete_commitment_callback(callback: CallbackQuery):
    """Handle commitment completion"""
    commitment_id = callback.data.split("_", 1)[1]
    
    success = await DatabaseManager.complete_commitment(commitment_id)
    
    if success:
        await callback.answer("✅ Marked as complete! Great job! 🎉")
        await callback.message.edit_text("🎉 Commitment completed! Great job! 🔥")
    else:
        await callback.answer("❌ Error marking commitment complete. Please try again.")

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

def register_handlers(dp: Dispatcher):
    """Register all handlers with the dispatcher"""
    global bot, supabase, smart_analyzer
    
    try:
        # Initialize configuration
        config = Config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize bot (will be set by the webhook handler)
        bot = Bot(token=config.bot_token)
        
        # Initialize database client
        try:
            supabase = create_client(config.supabase_url, config.supabase_key)
            logger.info("✅ Supabase client created successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            supabase = None
        
        # Initialize OpenAI
        openai.api_key = config.openai_api_key
        smart_analyzer = SmartAnalysis(config)
        
        # Register message handlers
        dp.message.register(start_handler, CommandStart())
        dp.message.register(commit_handler, Command("commit"))
        dp.message.register(list_handler, Command("list"))
        dp.message.register(done_handler, Command("done"))
        dp.message.register(help_handler, Command("help"))
        dp.message.register(handle_text_messages)
        
        # Register callback handlers
        dp.callback_query.register(complete_commitment_callback, F.data.startswith("complete_"))
        dp.callback_query.register(save_smart_callback, F.data.startswith("save_smart_"))
        dp.callback_query.register(save_original_callback, F.data.startswith("save_original_"))
        
        logger.info("✅ All handlers registered successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in register_handlers: {e}")
        raise