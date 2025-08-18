import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, BotCommand
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from supabase import create_client, Client
import openai

# Load environment variables securely
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
    print("📝 Using system environment variables instead")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secure Configuration Class
class Config:
    """Secure configuration management"""
    
    def __init__(self):
        self._validate_environment()
        self._log_config_status()
    
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
            logger.error("\n💡 Create a .env file with these variables:")
            logger.error("BOT_TOKEN=your_bot_token_here")
            logger.error("SUPABASE_URL=your_supabase_url_here")
            logger.error("SUPABASE_KEY=your_supabase_key_here")
            logger.error("OPENAI_API_KEY=your_openai_key_here")
            raise ValueError(f"Missing required environment variables: {len(missing_vars)} variables")
    
    def _log_config_status(self):
        """Log configuration status without exposing sensitive data"""
        logger.info("🔧 Configuration Status:")
        logger.info(f"   BOT_TOKEN: {'✅ Set' if self.bot_token else '❌ Missing'}")
        logger.info(f"   SUPABASE_URL: {'✅ Set' if self.supabase_url else '❌ Missing'}")
        logger.info(f"   SUPABASE_KEY: {'✅ Set' if self.supabase_key else '❌ Missing'}")
        logger.info(f"   OPENAI_API_KEY: {'✅ Set' if self.openai_api_key else '❌ Missing'}")
        
        # Validate key formats (without exposing the keys)
        self._validate_key_formats()
    
    def _validate_key_formats(self):
        """Validate API key formats for basic security"""
        if self.bot_token and ":" not in self.bot_token:
            logger.warning("⚠️ Bot token format looks incorrect (should contain ':')")
        
        if self.openai_api_key and not (self.openai_api_key.startswith("sk-") or self.openai_api_key.startswith("sk-proj-")):
            logger.warning("⚠️ OpenAI key should start with 'sk-' or 'sk-proj-'")
        
        if self.supabase_key and not self.supabase_key.startswith("eyJ"):
            logger.warning("⚠️ Supabase key format looks suspicious (should start with 'eyJ')")
        
        if self.supabase_url and not self.supabase_url.startswith("https://"):
            logger.warning("⚠️ Supabase URL should start with 'https://'")
    
    @property
    def bot_token(self) -> str:
        return os.getenv("BOT_TOKEN", "").strip()
    
    @property
    def supabase_url(self) -> str:
        # Use development database if in development environment
        if os.getenv("ENVIRONMENT") == "development":
            return os.getenv("DEV_SUPABASE_URL", "").strip()
        return os.getenv("SUPABASE_URL", "").strip()
    
    @property
    def supabase_key(self) -> str:
        # Use development database if in development environment
        if os.getenv("ENVIRONMENT") == "development":
            return os.getenv("DEV_SUPABASE_KEY", "").strip()
        return os.getenv("SUPABASE_KEY", "").strip()
    
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()
    
    @property
    def debug_mode(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"

# Initialize secure configuration
try:
    config = Config()
    logger.info("✅ Configuration loaded successfully")
except ValueError as e:
    logger.error(f"❌ Configuration failed: {e}")
    logger.error("\n📝 To fix this:")
    logger.error("1. Create a .env file in your project root")
    logger.error("2. Add your API keys to the .env file (see example above)")
    logger.error("3. Make sure the .env file is in the same directory as your bot.py")
    exit(1)

# Initialize clients with secure config
bot = Bot(token=config.bot_token)
dp = Dispatcher(storage=MemoryStorage())

# Test database connection
try:
    supabase: Client = create_client(config.supabase_url, config.supabase_key)
    logger.info("✅ Supabase client created successfully")
    
    # Test connection
    result = supabase.table("commitments").select("count", count="exact").execute()
    logger.info(f"✅ Database connection test successful.")
    
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    supabase = None

# Initialize OpenAI with secure config
openai.api_key = config.openai_api_key  # For backward compatibility
openai_client = openai.OpenAI(api_key=config.openai_api_key)  # New client for first impression

# States for FSM
class CommitmentStates(StatesGroup):
    waiting_for_commitment = State()
    processing_smart = State()

class OnboardingStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_goal = State()
    waiting_for_accountability = State()
    waiting_for_comprehensive_info = State()

class FirstImpressionStates(StatesGroup):
    waiting_for_first_goal = State()
    celebrating_first_win = State()
    collecting_bigger_goal = State()

class SmartAnalysis:
    """SMART goal analysis class with secure configuration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key)
    
    async def analyze_commitment(self, commitment: str, chat_id: int = None) -> Dict[str, Any]:
        """Analyze commitment using OpenAI for SMART criteria with progress updates"""
        try:
            logger.info(f"🧠 Starting AI analysis for: {commitment}")
            
            # Check if API key is set
            if not self.config.openai_api_key:
                logger.error("❌ OpenAI API key not set")
                return self._fallback_analysis(commitment)
            
            # Show typing indicator and optional tip
            if chat_id:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                
                # Randomly show a tip while processing (33% chance)
                import random
                if random.random() < 0.33:
                    asyncio.create_task(show_commitment_tips(chat_id))
            
            logger.info("🔗 Sending request to OpenAI...")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a SMART goal analyzer. Analyze the given commitment and score it on SMART criteria:
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
}"""
                    },
                    {"role": "user", "content": commitment}
                ],
                temperature=0.7,
                timeout=10  # 10 second timeout for OpenAI
            )
            
            logger.info("✅ Received response from OpenAI")
            content = response.choices[0].message.content
            logger.info(f"🧠 AI Response length: {len(content)} characters")
            
            # Try to parse JSON from response
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
                logger.error(f"Raw content: {content}")
                return self._fallback_analysis(commitment)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing commitment: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return self._fallback_analysis(commitment)
    
    def _fallback_analysis(self, commitment: str) -> Dict[str, Any]:
        """Provide a fallback analysis when AI fails"""
        logger.info("🔄 Using fallback analysis")
        
        # Simple heuristic scoring
        score = 5  # Default
        
        # Basic checks to improve score
        if len(commitment) > 20:  # More detailed = more specific
            score += 1
        if any(word in commitment.lower() for word in ["today", "tomorrow", "week", "month", "by"]):
            score += 1  # Has time element
        if any(word in commitment.lower() for word in ["minutes", "pages", "times", "hours", "km", "miles"]):
            score += 1  # Has measurable element
        
        return {
            "score": min(score, 8),  # Cap at 8 so we still show improvement options
            "analysis": {"specific": score, "measurable": score-1, "achievable": score, "relevant": score, "timeBound": score-2},
            "smartVersion": f"{commitment} by the end of this week",
            "feedback": "AI analysis unavailable. Added time frame for better tracking."
        }

class DatabaseManager:
    """Handle database operations with detailed debugging"""
    
    @staticmethod
    async def test_database():
        """Test database connection and table structure"""
        try:
            logger.info("🔍 Testing database connection...")
            
            if supabase is None:
                logger.error("❌ Supabase client not initialized")
                return False
            
            # Test table exists and get structure
            result = supabase.table("commitments").select("*").limit(1).execute()
            logger.info(f"✅ Table query successful.")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            return False
    
    @staticmethod
    async def save_commitment(
        telegram_user_id: int,
        commitment: str,
        original_commitment: str,
        smart_score: int
    ) -> bool:
        """Save commitment to database with detailed debugging"""
        try:
            logger.info(f"💾 SAVING commitment for user {telegram_user_id}")
            logger.info(f"   Commitment: {commitment}")
            logger.info(f"   SMART Score: {smart_score}")
            
            if supabase is None:
                logger.error("❌ Supabase client not available")
                return False
            
            # Get user UUID from telegram_user_id
            user_result = supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                logger.warning(f"⚠️ User not found for telegram_user_id: {telegram_user_id}, attempting to create...")
                # Attempt to create user (should not happen if ensure_user_exists was called)
                try:
                    user_data = {
                        "telegram_user_id": telegram_user_id,
                        "first_name": "Emergency User",
                        "first_bot_interaction_at": datetime.now().isoformat(),
                        "last_activity_at": datetime.now().isoformat()
                    }
                    create_result = supabase.table("users").insert(user_data).execute()
                    if create_result.data:
                        user_uuid = create_result.data[0]["id"]
                        logger.info(f"✅ Emergency user creation successful: {user_uuid}")
                    else:
                        logger.error(f"❌ Emergency user creation failed")
                        return False
                except Exception as create_error:
                    logger.error(f"❌ Emergency user creation error: {create_error}")
                    return False
            else:
                user_uuid = user_result.data[0]["id"]
            
            # Prepare data
            commitment_data = {
                "user_id": user_uuid,
                "telegram_user_id": telegram_user_id,
                "commitment": commitment,
                "original_commitment": original_commitment,
                "status": "active",
                "smart_score": smart_score,
                "created_at": datetime.now().isoformat()
            }
            
            # Insert data
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
            logger.info(f"🔍 FETCHING commitments for user {telegram_user_id}")
            
            if supabase is None:
                logger.error("❌ Supabase client not available")
                return []
            
            result = supabase.table("commitments").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "active").execute()
            
            logger.info(f"✅ Found {len(result.data)} active commitments")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error getting commitments: {e}")
            return []
    
    @staticmethod
    async def complete_commitment(commitment_id: str) -> bool:
        """Mark commitment as completed"""
        try:
            logger.info(f"✅ COMPLETING commitment {commitment_id}")
            
            if supabase is None:
                logger.error("❌ Supabase client not available")
                return False
            
            result = supabase.table("commitments").update({
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }).eq("id", commitment_id).execute()
            
            logger.info(f"✅ Commitment marked as complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error completing commitment: {e}")
            return False
    
    @staticmethod
    async def save_feedback(telegram_user_id: int, username: str, feedback: str) -> bool:
        """Save user feedback to database"""
        try:
            logger.info(f"💬 SAVING feedback from user {telegram_user_id}")
            
            if supabase is None:
                logger.error("❌ Supabase client not available")
                return False
            
            # Prepare feedback data
            feedback_data = {
                "telegram_user_id": telegram_user_id,
                "username": username,
                "feedback": feedback,
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into feedback table (will create table if doesn't exist)
            result = supabase.table("feedback").insert(feedback_data).execute()
            
            logger.info(f"✅ Feedback saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving feedback: {e}")
            # If table doesn't exist, try to create it
            if "relation" in str(e) and "does not exist" in str(e):
                logger.info("📝 Feedback table doesn't exist, creating it...")
                try:
                    # For Supabase, tables should be created via dashboard
                    # But we'll still save the feedback locally or notify admin
                    logger.warning("⚠️ Please create 'feedback' table in Supabase with columns: id, telegram_user_id, username, feedback, created_at")
                except Exception as create_error:
                    logger.error(f"❌ Could not create feedback table: {create_error}")
            return False

# Initialize analysis engine with secure config
smart_analyzer = SmartAnalysis(config)

# Initialize role manager
from user_role_manager import UserRoleManager
from user_analytics import UserAnalytics
# from dream_focused_analytics import DreamFocusedAnalytics  # Temporarily disabled - missing module
from leaderboard import Leaderboard
from pod_week_tracker import PodWeekTracker
# from attendance_adapter import AttendanceAdapter  # Temporarily disabled - missing module
from nurture_sequences import NurtureSequences, SequenceType
from enhanced_user_onboarding import EnhancedUserOnboarding
from first_impression_experience import FirstImpressionExperience
from onboarding_manager import OnboardingManager
role_manager = UserRoleManager(supabase)
user_analytics = UserAnalytics(supabase)
# dream_analytics = DreamFocusedAnalytics(supabase)  # Temporarily disabled
leaderboard = Leaderboard(supabase)
pod_tracker = PodWeekTracker(supabase)
# meet_tracker = AttendanceAdapter(supabase)  # Temporarily disabled
nurture_system = NurtureSequences(supabase)
onboarding_system = EnhancedUserOnboarding(supabase)
onboarding_manager = OnboardingManager(supabase)
first_impression = FirstImpressionExperience(supabase, openai_client, onboarding_manager)

# Temporary storage for callback data (use Redis in production)
temp_storage = {}

# Helper function for nurture sequence triggers
async def _trigger_commitment_sequences(telegram_user_id: int):
    """Trigger appropriate nurture sequences after commitment creation"""
    try:
        # Get user UUID
        user_result = supabase.table("users").select("id, total_commitments").eq("telegram_user_id", telegram_user_id).execute()
        if not user_result.data:
            return
        
        user_uuid = user_result.data[0]["id"]
        total_commitments = user_result.data[0]["total_commitments"]
        
        # Trigger commitment follow-up sequence
        await nurture_system.check_triggers(user_uuid, "commitment_created")
        
        # Check for milestone triggers
        if total_commitments == 5:
            await nurture_system.check_triggers(user_uuid, "5_commitments_completed")
            
    except Exception as e:
        logger.error(f"Error triggering commitment sequences: {e}")

# Loading experience functions
async def create_loading_experience(message: Message, commitment_text: str) -> Message:
    """Create an entertaining loading experience while analyzing the commitment"""
    
    # Send "typing" action to show the bot is working
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Initial loading message
    loading_phases = [
        "🤔 Hmm, let me think about this commitment...",
        "🧠 Analyzing your commitment with AI brain power...",
        "📊 Running SMART goal diagnostics...",
        "⚡ Calculating commitment potential...",
        "🎯 Almost there, finalizing analysis..."
    ]
    
    # Send initial message
    loading_msg = await message.answer(loading_phases[0])
    
    try:
        # Animate through loading phases with timeout protection
        for i, phase in enumerate(loading_phases[1:], 1):
            await asyncio.sleep(0.6)  # Slightly faster
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Update message with progress
            progress_bar = "█" * i + "░" * (len(loading_phases) - i - 1)
            await loading_msg.edit_text(
                f"{phase}\n\n[{progress_bar}] {int((i/len(loading_phases)) * 100)}%"
            )
            
    except Exception as e:
        logger.error(f"Error in loading animation: {e}")
        # If animation fails, just show a simple message
        await loading_msg.edit_text("🤖 Analyzing your commitment...")
    
    return loading_msg

async def finalize_loading_experience(loading_message: Message, analysis: Dict[str, Any]):
    """Finalize the loading experience with the analysis result"""
    
    try:
        # Final animation before showing result
        await asyncio.sleep(0.3)
        
        # Show completion
        score = analysis["score"]
        
        # Choose reaction based on score
        if score >= 8:
            reaction = "🎉 Excellent commitment!"
            emoji = "✨"
        elif score >= 6:
            reaction = "🤔 Good commitment, but could be SMARTer!"
            emoji = "💡"
        else:
            reaction = "😬 This commitment needs some work!"
            emoji = "🛠️"
        
        # Final loading message
        await loading_message.edit_text(
            f"{emoji} Analysis complete!\n\n{reaction}\n\nSMART Score: {score}/10 🎯"
        )
        
        # Small delay before showing the actual result
        await asyncio.sleep(0.8)
        
    except Exception as e:
        logger.error(f"Error in loading finalization: {e}")
        # Just show simple completion
        await loading_message.edit_text("✅ Analysis complete!")

# Add entertaining commitment tips during analysis
async def show_commitment_tips(chat_id: int):
    """Show random commitment tips while AI is thinking"""
    tips = [
        "💡 Tip: Specific goals are 10x more likely to be achieved!",
        "⏰ Tip: Adding a deadline makes commitments 3x more effective!",
        "📏 Tip: Measurable goals help track your progress!",
        "🎯 Tip: Write down your commitments to boost success by 42%!",
        "🔥 Tip: Share your goals with someone to increase accountability!",
        "🏆 Tip: Celebrate small wins to build momentum!",
        "🧠 Tip: Your brain loves specific, achievable targets!",
        "📈 Tip: Track your progress daily for maximum impact!"
    ]
    
    import random
    tip = random.choice(tips)
    await bot.send_message(chat_id, tip)
    await asyncio.sleep(2)

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command with first-time user detection"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "there"
    username = message.from_user.username
    
    # EMERGENCY FIX: Clear any stuck FSM state first
    await state.clear()
    
    # Ensure user exists in database and get role info
    await role_manager.ensure_user_exists(user_id, user_name, username)
    
    # Initialize onboarding system (replaces is_first_time_user check)
    await onboarding_manager.start_onboarding(user_id, user_name, username)
    
    # Check onboarding status using unified system  
    should_show_first_impression = await onboarding_manager.should_show_first_impression(user_id)
    user_roles = await role_manager.get_user_roles(user_id)
    
    # EMERGENCY FIX: Use the correct variable instead of undefined is_first_time
    is_first_time = should_show_first_impression
    
    # Test database on first interaction
    db_test = await DatabaseManager.test_database()
    
    if should_show_first_impression:
        # GRACEFUL BYPASS: Avoid FSM states, provide direct experience
        welcome_text = f"""🎯 **Hey {user_name}!** 

Welcome to your Personal Progress Coach! ⚡

I help people like you turn big dreams into daily wins.

**Let's start simple - try one of these:**

📝 `/commit I want to finish this project today`
📝 `/commit I will exercise for 30 minutes`
📝 `/commit I'll read 10 pages of my book`

✅ Then use `/done` when you complete it
📊 Use `/progress` to see your wins adding up

*No complicated setup - just results!* 🚀

**Need help?** Use `/help` to see all commands."""
    else:
        # Returning user - personalized based on roles
        has_pod = "pod_member" in user_roles
        is_paid = "paid" in user_roles
        
        welcome_text = f"""Welcome back, {user_name}! 👋

"""
        
        if has_pod:
            welcome_text += "🎯 **Pod Member** - Keep that momentum going!\n\n"
        elif is_paid:
            welcome_text += "💎 **Paid Member** - Ready for your next breakthrough?\n\n"
        else:
            welcome_text += "Ready to continue building better habits? 💪\n\n"
        
        welcome_text += """**Quick Actions:**
📝 /commit - Add today's commitment
✅ /done - Mark commitments complete  
📋 /list - View active commitments
💬 /feedback - Send suggestions

"""
        
        if not has_pod and not is_paid:
            welcome_text += "**Want accountability partners?** Join a pod at theprogressmethod.com 🚀"
    
    if not db_test:
        welcome_text += "\n\n⚠️ Note: Database connection issue detected. Some features may not work properly."
    
    await message.answer(welcome_text, parse_mode="Markdown")
    
    # EMERGENCY FIX: Disable first impression FSM state to avoid loops
    # if is_first_time:
    #     await state.set_state(FirstImpressionStates.waiting_for_first_goal)
    
    # Trigger nurture sequence for first-time users
    if is_first_time:
        try:
            user_result = supabase.table("users").select("id").eq("telegram_user_id", user_id).execute()
            if user_result.data:
                user_uuid = user_result.data[0]["id"]
                await nurture_system.check_triggers(user_uuid, "first_interaction")
        except Exception as e:
            logger.error(f"Error triggering nurture sequence: {e}")
    
    # Log user activity
    logger.info(f"👋 {'New' if is_first_time else 'Returning'} user: {user_name} ({user_id}) - Roles: {user_roles}")

@dp.message(Command("dbtest"))
async def dbtest_handler(message: Message):
    """Test database connection"""
    await message.answer("🔍 Testing database connection...")
    
    db_test = await DatabaseManager.test_database()
    
    if db_test:
        await message.answer("✅ Database connection successful!")
    else:
        await message.answer("❌ Database connection failed. Check logs for details.")

@dp.message(Command("aitest"))
async def aitest_handler(message: Message):
    """Test AI analysis specifically"""
    await message.answer("🧪 Testing AI analysis...")
    
    try:
        # Test OpenAI connection
        if not config.openai_api_key:
            await message.answer("❌ OpenAI API key not configured")
            return
        
        # Simple test
        test_commitment = "read a book"
        analysis = await smart_analyzer.analyze_commitment(test_commitment)
        
        if analysis.get("score", 0) > 0:
            await message.answer(
                f"✅ AI is working!\n\n"
                f"Test: '{test_commitment}'\n"
                f"Score: {analysis['score']}/10\n"
                f"Suggestion: {analysis.get('smartVersion', 'none')}"
            )
        else:
            await message.answer("❌ AI returned invalid response")
            
    except Exception as e:
        await message.answer(f"❌ AI test failed: {str(e)}")

@dp.message(Command("commit"))
async def commit_handler(message: Message):
    """Handle /commit command with entertaining loading experience and timeout"""
    # Extract commitment text
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "Please provide a commitment after /commit\n\n"
            "Example: /commit Read for 30 minutes"
        )
        return
    
    commitment_text = command_parts[1].strip()
    user_id = message.from_user.id
    
    logger.info(f"🎯 Processing commitment from user {user_id}: {commitment_text}")
    
    # EMERGENCY FIX: Remove circular logic blocking first-time users from making commitments
    # The old logic prevented users from making their first commitment, creating an infinite loop
    # Now first-time users can make commitments immediately after /start
    
    # Ensure user exists in database with error handling
    user_created = await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    if not user_created:
        await message.answer("❌ Error setting up user account. Please try /start first, then try your commitment again.")
        return
    
    # Test database before proceeding
    if not await DatabaseManager.test_database():
        await message.answer("❌ Database connection error. Please try again later or contact support.")
        return
    
    # Start the entertaining loading experience
    loading_message = await create_loading_experience(message, commitment_text)
    
    try:
        # Analyze the commitment with SMART criteria (with timeout)
        analysis = await asyncio.wait_for(
            smart_analyzer.analyze_commitment(commitment_text, message.chat.id),
            timeout=15.0  # 15 second timeout
        )
        
        # Update with final result
        await finalize_loading_experience(loading_message, analysis)
        
        is_smart_enough = analysis["score"] >= 8
        
        if is_smart_enough:
            # Save directly as it's already SMART enough
            success = await DatabaseManager.save_commitment(
                telegram_user_id=user_id,
                commitment=commitment_text,
                original_commitment=commitment_text,
                smart_score=analysis["score"]
            )
            
            if success:
                # Trigger nurture sequences
                await _trigger_commitment_sequences(user_id)
                
                # Replace the loading message with success
                await loading_message.edit_text(
                    f"✅ Great commitment! (SMART Score: {analysis['score']}/10)\n\n"
                    f"📝 \"{commitment_text}\"\n\n"
                    f"Added to your commitments! Use /done when you complete it."
                )
            else:
                await loading_message.edit_text("❌ Error saving commitment. Please check /dbtest and try again.")
        else:
            # Offer improvement options
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💡 Use SMART version",
                    callback_data=f"save_smart_{user_id}_{analysis['score']}"
                )],
                [InlineKeyboardButton(
                    text="📝 Keep original",
                    callback_data=f"save_original_{user_id}_{analysis['score']}"
                )],
                [InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="cancel_commit"
                )]
            ])
            
            improvement_text = (
                f"🤔 Your commitment could be more SMART! (Score: {analysis['score']}/10)\n\n"
                f"**Original:** \"{commitment_text}\"\n"
                f"**SMART Version:** \"{analysis['smartVersion']}\"\n\n"
                f"**Why improve?** {analysis['feedback']}\n\n"
                f"Which version would you like to save?"
            )
            
            # Store commitment data for callback
            temp_storage[f"commit_{user_id}"] = {
                "original": commitment_text,
                "smart": analysis['smartVersion'],
                "score": analysis['score']
            }
            
            # Replace loading message with improvement options
            await loading_message.edit_text(
                improvement_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
    except asyncio.TimeoutError:
        logger.error("❌ AI analysis timed out")
        await loading_message.edit_text(
            f"⏰ AI analysis took too long! Let me save your commitment as-is:\n\n"
            f"📝 \"{commitment_text}\"\n\n"
            f"I'll give it a standard score and you can improve it later!"
        )
        
        # Save with default score
        success = await DatabaseManager.save_commitment(
            telegram_user_id=user_id,
            commitment=commitment_text,
            original_commitment=commitment_text,
            smart_score=6  # Default score when AI fails
        )
        
        if success:
            # Trigger nurture sequences
            await _trigger_commitment_sequences(user_id)
            
            await asyncio.sleep(1)
            await loading_message.edit_text(
                f"✅ Commitment saved! (Default Score: 6/10)\n\n"
                f"📝 \"{commitment_text}\"\n\n"
                f"Use /done when you complete it!"
            )
        else:
            await loading_message.edit_text("❌ Both AI analysis and saving failed. Please try again.")
            
    except Exception as e:
        logger.error(f"❌ Error in commit handler: {e}")
        await loading_message.edit_text(
            f"❌ Something went wrong! Let me save your commitment anyway:\n\n"
            f"📝 \"{commitment_text}\"\n\n"
            f"Added to your list!"
        )
        
        # Try to save anyway
        await DatabaseManager.save_commitment(
            telegram_user_id=user_id,
            commitment=commitment_text,
            original_commitment=commitment_text,
            smart_score=5  # Fallback score
        )

@dp.message(Command("list"))
async def list_handler(message: Message):
    """Handle /list command"""
    user_id = message.from_user.id
    
    # Ensure user exists in database
    await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    commitments = await DatabaseManager.get_active_commitments(user_id)
    
    if not commitments:
        await message.answer(
            "📋 No active commitments.\n\n"
            "Use /commit to add one!"
        )
        return
    
    text = "📋 *Your Active Commitments:*\n\n"
    for i, commitment in enumerate(commitments, 1):
        text += f"{i}. {commitment['commitment']}\n"
        if commitment.get('created_at'):
            try:
                date = datetime.fromisoformat(commitment['created_at'].replace('Z', '+00:00'))
                text += f"   _Added: {date.strftime('%Y-%m-%d')}_\n"
            except:
                pass
        text += "\n"
    
    text += "Use /done to mark them complete!"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("done"))
async def done_handler(message: Message):
    """Handle /done command"""
    user_id = message.from_user.id
    
    # Ensure user exists in database
    await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    commitments = await DatabaseManager.get_active_commitments(user_id)
    
    logger.info(f"🎯 /done command from user {user_id}, found {len(commitments)} commitments")
    
    if not commitments:
        await message.answer(
            "📝 No active commitments found.\n\n"
            "Use /commit to add one!"
        )
        return
    
    # Build inline keyboard with commitments
    keyboard_buttons = []
    
    for i, commitment in enumerate(commitments):
        button_text = f"✓ {i + 1}. {commitment['commitment']}"
        if len(button_text) > 60:
            button_text = button_text[:57] + "..."
        
        keyboard_buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"complete_{commitment['id']}"
        )])
    
    # Add cancel button
    keyboard_buttons.append([InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="cancel_done"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    message_text = (
        f"🎯 You have {len(commitments)} commitment{'s' if len(commitments) > 1 else ''} to complete:\n\n"
        f"Select which one you've completed:\n"
        f"💪 Click to mark complete!"
    )
    
    logger.info(f"📤 Sending /done message with {len(keyboard_buttons)} buttons")
    await message.answer(message_text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("complete_"))
async def complete_commitment_callback(callback: CallbackQuery, state: FSMContext):
    """Handle commitment completion"""
    commitment_id = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    
    logger.info(f"✅ User {user_id} completing commitment {commitment_id}")
    
    # Mark as complete
    success = await DatabaseManager.complete_commitment(commitment_id)
    
    if not success:
        await callback.answer("❌ Error marking commitment complete. Please try again.", show_alert=True)
        return
    
    # Check if this is their first completion for special celebration
    should_celebrate = await first_impression.should_trigger_celebration(user_id)
    
    if should_celebrate:
        # Send massive first completion celebration
        user_name = callback.from_user.first_name or "Champion"
        celebration_message = await first_impression.handle_first_completion_celebration(user_id, user_name)
        await callback.message.answer(celebration_message, parse_mode="Markdown")
        
        # Progressive data collection - ask for bigger goal
        bigger_goal_prompt = await first_impression.progressive_data_collection(user_id, user_name)
        await callback.message.answer(bigger_goal_prompt, parse_mode="Markdown")
        
        # Set state for bigger goal collection
        await state.set_state(FirstImpressionStates.collecting_bigger_goal)
        
        # Send celebration
        await callback.answer("🔥 FIRST WIN! You're amazing! 🔥")
    else:
        # Send normal celebration
        await callback.answer("✅ Marked as complete! Great job! 🎉")
    
    # Get remaining commitments
    remaining_commitments = await DatabaseManager.get_active_commitments(user_id)
    
    logger.info(f"📊 {len(remaining_commitments)} commitments remaining")
    
    if not remaining_commitments:
        # All done!
        await callback.message.edit_text(
            "🎉 ALL DONE! 🎉\n\n"
            "Amazing! You've completed all your commitments!\n\n"
            "You're on fire today! 🔥\n\n"
            "Ready for more? Use /commit to add new goals!"
        )
    else:
        # Rebuild button list
        celebration_emojis = ["✅", "👏", "🎯", "💪", "🔥", "⭐"]
        emoji = celebration_emojis[len(celebration_emojis) % len(remaining_commitments)]
        
        if len(remaining_commitments) == 1:
            text = f"{emoji} Great job!\n\nJust 1 commitment left:\n\nWhich one next? 🎯"
        else:
            text = f"{emoji} Great job!\n\n{len(remaining_commitments)} commitments remaining:\n\nWhich one next? 🎯"
        
        # Rebuild keyboard
        keyboard_buttons = []
        for i, commitment in enumerate(remaining_commitments):
            button_text = f"✓ {i + 1}. {commitment['commitment']}"
            if len(button_text) > 60:
                button_text = button_text[:57] + "..."
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"complete_{commitment['id']}"
            )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="cancel_done"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query(F.data == "cancel_done")
async def cancel_done_callback(callback: CallbackQuery):
    """Handle done cancellation"""
    await callback.message.edit_text(
        "Cancelled. Use /done again when you're ready to mark commitments complete."
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("save_smart_"))
async def save_smart_callback(callback: CallbackQuery):
    """Handle saving SMART version"""
    user_id = callback.from_user.id
    
    # Get stored commitment data
    stored_data = temp_storage.get(f"commit_{user_id}")
    if not stored_data:
        await callback.answer("Session expired. Please try again.", show_alert=True)
        return
    
    # Ensure user exists before saving
    await role_manager.ensure_user_exists(
        user_id,
        callback.from_user.first_name,
        callback.from_user.username
    )
    
    # Save SMART version
    success = await DatabaseManager.save_commitment(
        telegram_user_id=user_id,
        commitment=stored_data["smart"],
        original_commitment=stored_data["original"],
        smart_score=stored_data["score"]
    )
    
    if success:
        # Trigger nurture sequences
        await _trigger_commitment_sequences(user_id)
        
        await callback.message.edit_text(
            f"✅ SMART commitment saved!\n\n"
            f"📝 \"{stored_data['smart']}\"\n\n"
            f"Use /done when you complete it!"
        )
        # Clean up temporary storage
        del temp_storage[f"commit_{user_id}"]
    else:
        await callback.answer("❌ Error saving commitment. Please check /dbtest and try again.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data.startswith("save_original_"))
async def save_original_callback(callback: CallbackQuery):
    """Handle saving original version"""
    user_id = callback.from_user.id
    
    # Get stored commitment data
    stored_data = temp_storage.get(f"commit_{user_id}")
    if not stored_data:
        await callback.answer("Session expired. Please try again.", show_alert=True)
        return
    
    # Ensure user exists before saving
    await role_manager.ensure_user_exists(
        user_id,
        callback.from_user.first_name,
        callback.from_user.username
    )
    
    # Save original version
    success = await DatabaseManager.save_commitment(
        telegram_user_id=user_id,
        commitment=stored_data["original"],
        original_commitment=stored_data["original"],
        smart_score=5  # Default score for original
    )
    
    if success:
        # Trigger nurture sequences
        await _trigger_commitment_sequences(user_id)
        
        await callback.message.edit_text(
            f"✅ Commitment saved!\n\n"
            f"📝 \"{stored_data['original']}\"\n\n"
            f"Use /done when you complete it!"
        )
        # Clean up temporary storage
        del temp_storage[f"commit_{user_id}"]
    else:
        await callback.answer("❌ Error saving commitment. Please check /dbtest and try again.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "cancel_commit")
async def cancel_commit_callback(callback: CallbackQuery):
    """Handle commit cancellation"""
    user_id = callback.from_user.id
    
    # Clean up temporary storage
    if f"commit_{user_id}" in temp_storage:
        del temp_storage[f"commit_{user_id}"]
    
    await callback.message.edit_text(
        "Commitment cancelled. Use /commit when you're ready to add a new commitment."
    )
    await callback.answer()

@dp.message(Command("feedback"))
async def feedback_handler(message: Message):
    """Handle /feedback command"""
    # Extract feedback text
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "💬 *Send us your feedback!*\n\n"
            "Please provide your feedback after /feedback\n\n"
            "Example: /feedback The bot is great but I'd love to see reminders!\n\n"
            "Your feedback helps us improve! 🌟",
            parse_mode="Markdown"
        )
        return
    
    feedback_text = command_parts[1].strip()
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Unknown"
    
    logger.info(f"📝 Feedback from {username} ({user_id}): {feedback_text}")
    
    # Save feedback to database
    success = await DatabaseManager.save_feedback(
        telegram_user_id=user_id,
        username=username,
        feedback=feedback_text
    )
    
    if success:
        await message.answer(
            "✅ Thank you for your feedback! 🙏\n\n"
            "We really appreciate you taking the time to help us improve.\n"
            "Your message has been saved and will be reviewed soon! 💡"
        )
    else:
        # Still acknowledge the feedback even if database save fails
        await message.answer(
            "✅ Thank you for your feedback! 🙏\n\n"
            "We appreciate your input and will review it soon.\n"
            "Your feedback helps us build a better bot! 🚀"
        )
        logger.info(f"📋 Feedback (saved locally): User {username} ({user_id}) - {feedback_text}")

@dp.message(Command("help"))
async def help_handler(message: Message):
    """Handle /help command with role-based features"""
    user_id = message.from_user.id
    roles = await role_manager.get_user_roles(user_id)
    permissions = await role_manager.get_user_permissions(user_id)
    
    help_text = """📚 *How to use this bot:*

*Basic Commands:*
/commit <your commitment> - Add a commitment
/done - Mark commitments complete  
/list - View your active commitments
/feedback <message> - Send feedback
/sequences - View guidance messages
/stop_sequences - Turn off automated messages

*Tips:*
- Be specific with your commitments
- Start small and build consistency
- Check off completed items daily

"""
    
    # Add role-specific features
    if permissions.get("can_join_pods"):
        help_text += "*Pod Member Features:*\n/pods - View your pod info\n/podweek - Current pod week progress\n/podleaderboard - Pod week leaderboard\n/attendance - Your meeting attendance\n/podattendance - Pod attendance stats\n"
        
    if permissions.get("can_access_long_term_goals"):
        help_text += "*Paid Features:*\n/goals - Manage long-term goals\n/insights - Get AI insights\n"
    
    if permissions.get("can_view_analytics"):
        help_text += "*Admin Commands:*\n/stats - View platform statistics\n/grant_role - Grant role to user\n/users - Manage users\n/markattendance - Record meeting attendance\n"
    
    help_text += "\nQuestions? Use /feedback to reach us!"
    
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("progress"))
async def progress_handler(message: Message):
    """Show meaningful progress toward dreams (not just points)"""
    user_id = message.from_user.id
    
    # Ensure user exists
    await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    # Get and format dream-focused analytics
    # progress_message = await dream_analytics.format_meaningful_message(user_id)
    # Temporarily disabled - using simple message instead
    progress_message = "📊 Progress tracking is being updated. Please check back soon!"
    
    await message.answer(progress_message, parse_mode="Markdown")

@dp.message(Command("stats"))
async def stats_handler(message: Message):
    """Show user's personal analytics and gamification stats"""
    user_id = message.from_user.id
    
    # Ensure user exists
    await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    # Get and format analytics
    stats_message = await user_analytics.format_stats_message(user_id)
    
    await message.answer(stats_message, parse_mode="Markdown")

@dp.message(Command("leaderboard"))
async def leaderboard_handler(message: Message):
    """Show weekly leaderboard"""
    weekly_message = await leaderboard.format_weekly_leaderboard_message()
    await message.answer(weekly_message, parse_mode="Markdown")

@dp.message(Command("champions"))
async def champions_handler(message: Message):
    """Show all-time champions"""
    all_time_message = await leaderboard.format_all_time_leaderboard_message()
    await message.answer(all_time_message, parse_mode="Markdown")

@dp.message(Command("streaks"))
async def streaks_handler(message: Message):
    """Show streak leaders"""
    streak_message = await leaderboard.format_streak_leaderboard_message()
    await message.answer(streak_message, parse_mode="Markdown")

@dp.message(Command("podweek"))
async def pod_week_handler(message: Message):
    """Show current pod week progress"""
    user_id = message.from_user.id
    
    # Check if user is pod member
    if not await role_manager.user_has_role(user_id, "pod_member"):
        await message.answer("🎯 This feature is for pod members! Join a pod at theprogressmethod.com")
        return
    
    # For now, we'll simulate pod_id - in production this would come from user's pod membership
    # TODO: Get actual pod_id from user's pod membership
    pod_id = "demo-pod-id"  # Placeholder
    
    summary = await pod_tracker.format_pod_week_summary(str(user_id), pod_id)
    await message.answer(summary, parse_mode="Markdown")

@dp.message(Command("podleaderboard"))
async def pod_leaderboard_handler(message: Message):
    """Show pod week leaderboard"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_role(user_id, "pod_member"):
        await message.answer("🎯 This feature is for pod members!")
        return
    
    # TODO: Get actual pod_id from user's pod membership
    pod_id = "demo-pod-id"  # Placeholder
    
    leaderboard_data = await pod_tracker.get_pod_week_leaderboard(pod_id)
    
    if not leaderboard_data:
        await message.answer("📊 No pod activity this week yet! Be the first to make a commitment.")
        return
    
    message_text = "🏆 **This Week's Pod Leaderboard**\n\n"
    
    for user_data in leaderboard_data:
        message_text += f"{user_data['emoji']} **{user_data['rank']}. {user_data['user_name']}**\n"
        message_text += f"   ✅ {user_data['completed_commitments']}/{user_data['total_commitments']} ({user_data['completion_rate']}%)\n"
        message_text += f"   ⭐ Avg Quality: {user_data['avg_quality']}/10\n\n"
    
    message_text += "Keep up the great work, team! 💪"
    
    await message.answer(message_text, parse_mode="Markdown")

@dp.message(Command("attendance"))
async def attendance_handler(message: Message):
    """Show pod meeting attendance stats"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_role(user_id, "pod_member"):
        await message.answer("🎯 This feature is for pod members!")
        return
    
    # TODO: Get actual pod_id from user's pod membership
    pod_id = "demo-pod-id"  # Placeholder
    
    # Get user's specific attendance data
    user_result = supabase.table("users").select("id").eq("telegram_user_id", user_id).execute()
    if not user_result.data:
        await message.answer("❌ User not found in database.")
        return
    
    user_uuid = user_result.data[0]["id"]
    # attendance_summary = await meet_tracker.format_attendance_summary(pod_id, user_uuid)
    # Temporarily disabled - using simple message instead
    attendance_summary = "📊 Attendance tracking is being updated. Please check back soon!"
    
    await message.answer(attendance_summary, parse_mode="Markdown")

@dp.message(Command("podattendance"))
async def pod_attendance_handler(message: Message):
    """Show full pod attendance leaderboard"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_role(user_id, "pod_member"):
        await message.answer("🎯 This feature is for pod members!")
        return
    
    # TODO: Get actual pod_id from user's pod membership
    pod_id = "demo-pod-id"  # Placeholder
    
    # attendance_summary = await meet_tracker.format_attendance_summary(pod_id)
    # Temporarily disabled - using simple message instead  
    attendance_summary = "📊 Attendance tracking is being updated. Please check back soon!"
    
    await message.answer(attendance_summary, parse_mode="Markdown")

@dp.message(Command("markattendance"))
async def mark_attendance_handler(message: Message):
    """Manually mark attendance for a meeting (admin feature)"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    # Parse command: /markattendance @username 2025-01-15 attended 45
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("""
📝 **Mark Attendance Usage:**
`/markattendance @username YYYY-MM-DD attended [duration_minutes]`
`/markattendance @username YYYY-MM-DD absent`

Examples:
• `/markattendance @john 2025-01-15 attended 45`
• `/markattendance @sara 2025-01-15 absent`
""", parse_mode="Markdown")
        return
    
    username = parts[1].replace("@", "")
    meeting_date = parts[2]
    attendance_status = parts[3].lower()
    duration = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 60
    
    # Get target user
    target_user = supabase.table("users").select("id").eq("username", username).execute()
    if not target_user.data:
        await message.answer(f"❌ User @{username} not found.")
        return
    
    target_user_id = target_user.data[0]["id"]
    
    # TODO: Get actual pod_id
    pod_id = "demo-pod-id"
    
    attended = attendance_status == "attended"
    # success = await meet_tracker.manually_record_attendance(pod_id, target_user_id, meeting_date, attended, duration)
    # Temporarily disabled
    success = False
    
    if success:
        status_text = f"attended ({duration} min)" if attended else "absent"
        await message.answer(f"✅ Marked @{username} as {status_text} for {meeting_date}")
    else:
        await message.answer("❌ Failed to record attendance.")

@dp.message(Command("sequences"))
async def sequences_handler(message: Message):
    """Show user's active nurture sequences"""
    user_id = message.from_user.id
    
    # Get user UUID
    user_result = supabase.table("users").select("id").eq("telegram_user_id", user_id).execute()
    if not user_result.data:
        await message.answer("❌ User not found in database.")
        return
    
    user_uuid = user_result.data[0]["id"]
    sequence_status = await nurture_system.format_sequence_status(user_uuid)
    
    await message.answer(sequence_status, parse_mode="Markdown")

@dp.message(Command("stop_sequences"))
async def stop_sequences_handler(message: Message):
    """Stop all active nurture sequences"""
    user_id = message.from_user.id
    
    # Get user UUID
    user_result = supabase.table("users").select("id").eq("telegram_user_id", user_id).execute()
    if not user_result.data:
        await message.answer("❌ User not found in database.")
        return
    
    user_uuid = user_result.data[0]["id"]
    
    # Get active sequences
    active_sequences = supabase.table("user_sequence_state").select("sequence_type").eq("user_id", user_uuid).eq("is_active", True).execute()
    
    stopped_count = 0
    for seq in active_sequences.data:
        success = await nurture_system.stop_sequence(user_uuid, seq["sequence_type"])
        if success:
            stopped_count += 1
    
    if stopped_count > 0:
        await message.answer(f"✅ Stopped {stopped_count} nurture sequence{'s' if stopped_count != 1 else ''}.\n\n💡 You can still use all bot features manually!")
    else:
        await message.answer("📭 No active sequences to stop.")

@dp.message(Command("debug"))
async def debug_handler(message: Message, state: FSMContext):
    """Debug user's current state and system status"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    
    try:
        # Get user info from database
        user_result = supabase.table("users").select("*").eq("telegram_user_id", user_id).execute()
        user_data = user_result.data[0] if user_result.data else None
        
        # Get user roles
        roles = await role_manager.get_user_roles(user_id)
        
        # Get onboarding status from new system
        onboarding_status = await onboarding_manager.get_user_onboarding_status(user_id)
        first_impression_status = await first_impression.check_user_in_first_impression_flow(user_id)
        
        debug_info = f"""🔍 **Debug Information for User {user_id}**

**FSM State:** {current_state or 'None'}

**🆕 NEW Onboarding Status:** {onboarding_status}
**📜 Legacy First Impression:** {first_impression_status}

**Database Status:**
• Legacy Status: {user_data.get('status', 'Unknown') if user_data else 'User not found'}
• Onboarding Status: {user_data.get('onboarding_status', 'Not set') if user_data else 'N/A'}
• First impression started: {user_data.get('first_impression_started_at', 'No') if user_data else 'N/A'}
• First commitment: {user_data.get('first_commitment_at', 'No') if user_data else 'N/A'}
• Total commitments: {user_data.get('total_commitments', 0) if user_data else 0}

**Roles:** {', '.join(roles) if roles else 'None'}

**System Status:** ✅ Unified onboarding system active

Use /fix to reset if needed."""
        
        await message.answer(debug_info, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Debug command error: {e}")
        await message.answer(f"❌ Debug failed: {str(e)}")

@dp.message(Command("myroles"))
async def myroles_handler(message: Message):
    """Show user's current roles"""
    user_id = message.from_user.id
    roles = await role_manager.get_user_roles(user_id)
    permissions = await role_manager.get_user_permissions(user_id)
    
    if not roles:
        await message.answer("🔍 You don't have any roles assigned yet.")
        return
    
    role_text = f"👤 **Your Current Roles:**\n\n"
    
    for role in sorted(roles):
        role_emoji = {
            'unpaid': '🆓',
            'paid': '💎', 
            'pod_member': '🎯',
            'admin': '⚙️',
            'super_admin': '👑',
            'beta_tester': '🧪'
        }.get(role, '📝')
        
        role_text += f"{role_emoji} {role.replace('_', ' ').title()}\n"
    
    # Show key permissions
    key_perms = []
    if permissions.get("can_join_pods"): key_perms.append("Pod Access")
    if permissions.get("can_access_long_term_goals"): key_perms.append("Long-term Goals")
    if permissions.get("can_view_analytics"): key_perms.append("Analytics")
    
    if key_perms:
        role_text += f"\n**Available Features:** {', '.join(key_perms)}"
    
    await message.answer(role_text, parse_mode="Markdown")

@dp.message(Command("adminstats"))
async def admin_stats_handler(message: Message):
    """Admin command to view platform statistics"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    try:
        # Get role statistics
        role_stats = await role_manager.get_role_stats()
        
        # Get KPI data
        kpi_queries = {
            "new_users": "SELECT * FROM kpi_new_users",
            "bot_usage": "SELECT * FROM kpi_bot_usage", 
            "commitment_fulfillment": "SELECT * FROM kpi_commitment_fulfillment"
        }
        
        stats_text = "📊 **Platform Statistics**\n\n"
        
        # Role breakdown
        stats_text += f"👥 **User Roles:**\n"
        stats_text += f"• Total Users: {role_stats.get('total_users', 0)}\n"
        stats_text += f"• Unpaid: {role_stats.get('unpaid', 0)}\n"
        stats_text += f"• Paid: {role_stats.get('paid', 0)}\n"
        stats_text += f"• Pod Members: {role_stats.get('pod_member', 0)}\n"
        stats_text += f"• Admins: {role_stats.get('admin', 0)}\n\n"
        
        # Get recent activity
        for kpi_name, query in kpi_queries.items():
            try:
                result = supabase.rpc('execute_sql', {'query': query}).execute()
                if result.data:
                    kpi_data = result.data[0]
                    
                    if kpi_name == "new_users":
                        stats_text += f"📈 **New Users:** {kpi_data.get('new_users_this_week', 0)} this week\n"
                    elif kpi_name == "bot_usage":
                        stats_text += f"🤖 **Bot Usage:** {kpi_data.get('weekly_active_percentage', 0):.1f}% active\n"
                    elif kpi_name == "commitment_fulfillment":
                        stats_text += f"✅ **Completion Rate:** {kpi_data.get('weekly_completion_rate', 0):.1f}%\n"
            except:
                pass
        
        await message.answer(stats_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.answer("❌ Error retrieving statistics.")

@dp.message(Command("grant_role"))
async def grant_role_handler(message: Message):
    """Admin command to grant roles to users"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    # Parse command: /grant_role <user_id> <role>
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /grant_role <user_id> <role>\n\nAvailable roles: paid, pod_member, admin, beta_tester")
        return
    
    try:
        target_user_id = int(parts[1])
        role = parts[2]
        
        valid_roles = ["paid", "pod_member", "admin", "beta_tester"]
        if role not in valid_roles:
            await message.answer(f"❌ Invalid role. Choose from: {', '.join(valid_roles)}")
            return
        
        success = await role_manager.grant_role(target_user_id, role, granted_by_id=user_id)
        
        if success:
            await message.answer(f"✅ Granted '{role}' role to user {target_user_id}")
        else:
            await message.answer("❌ Failed to grant role. Check user exists.")
            
    except ValueError:
        await message.answer("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error in grant_role command: {e}")
        await message.answer("❌ Error processing command.")

@dp.message(Command("fix"))
async def fix_loading_handler(message: Message, state: FSMContext):
    """Emergency command to fix stuck loading and reset state"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    
    logger.info(f"🔧 EMERGENCY FIX triggered by user {user_id} | Current state: {current_state}")
    
    # Clear any stuck FSM state
    await state.clear()
    
    # Reset user status in database to clear any stuck states
    try:
        supabase.table("users").update({
            "status": "active",
            "first_impression_started_at": None,
            "first_commitment_at": None
        }).eq("telegram_user_id", user_id).execute()
        logger.info(f"✅ Reset user {user_id} state in database")
    except Exception as e:
        logger.error(f"❌ Failed to reset user state: {e}")
    
    await message.answer(
        "🔧 **Emergency Reset Complete!**\n\n"
        "✅ Cleared your conversation state\n"
        "✅ Reset your account status\n"
        "✅ Ready for fresh start\n\n"
        "**Try these commands:**\n"
        "📝 `/commit I want to get this finished`\n"
        "📊 `/progress` - See your dashboard\n"
        "❓ `/help` - Full command list\n\n"
        "Everything should work perfectly now! 🚀"
    )

@dp.message(lambda message: message.text and not message.text.startswith('/'))  # Only non-command messages
async def handle_text_messages(message: Message, state: FSMContext):
    """Handle text messages that aren't handled by specific FSM states"""
    user_id = message.from_user.id
    text = message.text.lower()
    
    # DEBUGGING: Log all message handling attempts
    current_state = await state.get_state()
    logger.info(f"🔍 Generic handler triggered for user {user_id}: '{message.text}' | State: {current_state}")
    
    # If user is in an FSM state, this shouldn't happen - the specific handler should have caught it
    if current_state is not None:
        logger.warning(f"⚠️ User {user_id} in state {current_state} reached generic handler - possible handler mismatch!")
        
        # Instead of circuit breaker, try to route correctly based on state
        if current_state == "FirstImpressionStates:waiting_for_first_goal":
            logger.info(f"🔄 Manually routing to first goal handler for user {user_id}")
            await handle_first_goal_magic(message, state)
            return
        
        # For other states, clear and restart
        logger.info(f"🔄 Clearing unknown state {current_state} for user {user_id}")
        await state.clear()
        await message.answer("Let me help you start fresh! 🔄")
        # Fall through to normal handling
    
    # Continue with normal routing only if no FSM state
    
    # GRACEFUL APPROACH: Help users regardless of onboarding status
    
    # Check if they might be trying to create a commitment
    if len(message.text) > 10:
        # This looks like a potential commitment
        await message.answer(
            f"That sounds like a great goal! 🎯\n\n"
            f"**To save it as a commitment, use:**\n"
            f"`/commit {message.text}`\n\n"
            f"Then use `/done` when you complete it! 🚀"
        )
        return
    
    # Check for completion words
    completion_words = ["done", "finished", "complete", "completed", "did it"]
    if any(word in message.text.lower() for word in completion_words):
        await message.answer(
            "🎉 **Awesome!** \n\n"
            "To mark a specific commitment as done:\n"
            "• Use `/done` and I'll show you your active commitments\n"
            "• Or use `/list` to see what you have pending\n\n"
            "Keep up the great work! 💪"
        )
        return
    
    # Legacy onboarding system check (for existing users)
    needs_onboarding = await onboarding_system.check_user_needs_onboarding_data(user_id)
    
    if needs_onboarding:
        # Process as potential onboarding data
        result = await onboarding_system.process_onboarding_data(user_id, message.text)
        
        if result["status"] == "completed":
            await message.answer(result["message"], parse_mode="Markdown")
            return
        elif result["status"] == "need_more_info":
            await message.answer(result["message"], parse_mode="Markdown")
            return
        elif result["status"] == "error":
            await message.answer(result["message"])
            return
        # If status is "not_needed", continue with normal processing
    
    # Check if it looks like a commitment
    commitment_keywords = ["will", "going to", "commit", "promise", "plan to", "intend to"]
    has_commitment_keyword = any(keyword in text for keyword in commitment_keywords)
    
    if has_commitment_keyword and len(text) > 10:
        await message.answer(
            f"That sounds like a commitment! Would you like me to save it?\n\n"
            f"Use: /commit {message.text}"
        )
    else:
        # Check if we should trigger gentle data collection
        should_collect = await onboarding_system.should_trigger_data_collection(user_id)
        if should_collect:
            data_request = await onboarding_system.create_gentle_data_request(user_id)
            if data_request:
                # Determine which state to set based on the request content
                if "email" in data_request.lower():
                    await state.set_state(OnboardingStates.waiting_for_email)
                elif "goal" in data_request.lower():
                    await state.set_state(OnboardingStates.waiting_for_goal)
                elif "accountability" in data_request.lower():
                    await state.set_state(OnboardingStates.waiting_for_accountability)
                    
                await message.answer(data_request, parse_mode="Markdown")
                return
        
        # Graceful default response with helpful guidance
        await message.answer(
            "I'm here to help you stay accountable! 🎯\n\n"
            "**Quick Start:**\n"
            "📝 `/commit <your goal>` - Save a commitment\n"
            "✅ `/done` - Mark something complete\n"
            "📊 `/progress` - See your wins\n"
            "❓ `/help` - See all commands\n\n"
            "What would you like to accomplish today?"
        )

# Onboarding state handlers
@dp.message(OnboardingStates.waiting_for_email)
async def handle_email_input(message: Message, state: FSMContext):
    """Handle email input during onboarding"""
    user_id = message.from_user.id
    email = message.text.strip()
    
    # Basic email validation
    if "@" in email and "." in email.split("@")[-1]:
        try:
            # Update user email in database
            result = supabase.table("users").update({
                "email": email
            }).eq("telegram_user_id", user_id).execute()
            
            await state.clear()
            await message.answer(
                f"✅ Perfect! I've saved your email: {email}\n\n"
                "This helps us sync your progress across platforms. Thanks! 🙌"
            )
            
            # Check if there are more onboarding steps needed
            should_collect = await onboarding_system.should_trigger_data_collection(user_id)
            if should_collect:
                data_request = await onboarding_system.create_gentle_data_request(user_id)
                if data_request:
                    if "goal" in data_request.lower():
                        await state.set_state(OnboardingStates.waiting_for_goal)
                    elif "accountability" in data_request.lower():
                        await state.set_state(OnboardingStates.waiting_for_accountability)
                    await message.answer(data_request, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error saving email: {e}")
            await state.clear()
            await message.answer("Sorry, there was an error saving your email. You can try again later!")
    else:
        await message.answer(
            "That doesn't look like a valid email address. Could you try again?\n\n"
            "Example: your.email@example.com"
        )

@dp.message(OnboardingStates.waiting_for_goal)
async def handle_goal_input(message: Message, state: FSMContext):
    """Handle goal input during onboarding"""
    user_id = message.from_user.id
    goal = message.text.strip()
    
    if len(goal) > 5:  # Basic validation
        try:
            # Update user goal in database
            result = supabase.table("users").update({
                "goal_90_days": goal
            }).eq("telegram_user_id", user_id).execute()
            
            await state.clear()
            await message.answer(
                f"🎯 Awesome goal: \"{goal}\"\n\n"
                "I'll keep this in mind when helping you stay accountable! 💪"
            )
            
            # Check if there are more onboarding steps needed
            should_collect = await onboarding_system.should_trigger_data_collection(user_id)
            if should_collect:
                data_request = await onboarding_system.create_gentle_data_request(user_id)
                if data_request:
                    if "accountability" in data_request.lower():
                        await state.set_state(OnboardingStates.waiting_for_accountability)
                    await message.answer(data_request, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error saving goal: {e}")
            await state.clear()
            await message.answer("Sorry, there was an error saving your goal. You can try again later!")
    else:
        await message.answer(
            "Could you share a bit more detail about your goal? A few words is fine! 🎯"
        )

@dp.message(OnboardingStates.waiting_for_accountability)
async def handle_accountability_input(message: Message, state: FSMContext):
    """Handle accountability preference input during onboarding"""
    user_id = message.from_user.id
    response = message.text.strip()
    
    # Map responses to accountability styles
    accountability_map = {
        "1": "solo_focus",
        "2": "small_group", 
        "3": "community",
        "4": "exploring"
    }
    
    if response in accountability_map:
        style = accountability_map[response]
        try:
            # Update user accountability style in database
            result = supabase.table("users").update({
                "accountability_style": style
            }).eq("telegram_user_id", user_id).execute()
            
            await state.clear()
            
            style_messages = {
                "solo_focus": "Perfect! I'll focus on daily check-ins and personal accountability. 📱",
                "small_group": "Great choice! Small groups are powerful for accountability. We'll let you know about pod opportunities! 👥",
                "community": "Awesome! Community support can be amazing. We'll keep you posted on group activities! 🌟",
                "exploring": "No worries! We'll help you figure out what works best as you go. 🧭"
            }
            
            await message.answer(
                f"✅ {style_messages[style]}\n\n"
                "Thanks for helping me personalize your experience! 🚀"
            )
            
        except Exception as e:
            logger.error(f"Error saving accountability style: {e}")
            await state.clear()
            await message.answer("Sorry, there was an error saving your preference. You can try again later!")
    else:
        await message.answer(
            "Please reply with just the number (1, 2, 3, or 4) for your preference! 😊"
        )

@dp.message(OnboardingStates.waiting_for_comprehensive_info)
async def handle_comprehensive_onboarding(message: Message, state: FSMContext):
    """Handle comprehensive onboarding response (name, email, goal all at once)"""
    user_id = message.from_user.id
    user_input = message.text.strip()
    
    try:
        # Process the comprehensive onboarding data
        result = await onboarding_system.process_onboarding_data(user_id, user_input)
        
        await state.clear()
        
        if result["status"] == "completed":
            await message.answer(result["message"], parse_mode="Markdown")
        elif result["status"] == "need_more_info":
            # Set state back to wait for more info
            await state.set_state(OnboardingStates.waiting_for_comprehensive_info)
            await message.answer(result["message"], parse_mode="Markdown")
        elif result["status"] == "not_needed":
            await message.answer("You're already all set up! 🎉")
        else:
            await message.answer("Sorry, something went wrong. Let's try again!")
            
    except Exception as e:
        logger.error(f"Error handling comprehensive onboarding: {e}")
        await state.clear()
        await message.answer("Sorry, there was an error processing your information. Please try again!")

# First Impression Experience handlers
@dp.message(FirstImpressionStates.waiting_for_first_goal)
async def handle_first_goal_magic(message: Message, state: FSMContext):
    """Handle first goal input and create instant magic experience"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Champion"
    user_input = message.text.strip()
    
    logger.info(f"✨ FIRST IMPRESSION HANDLER TRIGGERED for user {user_id}: '{user_input}'")
    
    try:
        # Create the magic experience using the new integrated system
        result = await first_impression.handle_first_goal_input(user_id, user_input, user_name)
        
        logger.info(f"✅ First impression result: {result.get('status', 'unknown')}")
        
        if result["status"] == "magic_created":
            # Clear FSM state and let onboarding manager handle state
            await state.clear()
            await message.answer(result["message"], parse_mode="Markdown")
            logger.info(f"🎉 Magic experience completed for user {user_id}")
        elif result["status"] == "error":
            await state.clear()
            await message.answer(result["message"], parse_mode="Markdown")
            logger.error(f"❌ First impression error for user {user_id}")
        else:
            await state.clear()
            await message.answer("Something amazing is happening... let me set that up for you! 🚀")
            
    except Exception as e:
        logger.error(f"Error in first goal magic: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        await state.clear()
        await message.answer(f"🎯 Love the energy, {user_name}! Let me save that for you and we'll get started! 🚀")

@dp.message(FirstImpressionStates.collecting_bigger_goal)
async def handle_bigger_goal_collection(message: Message, state: FSMContext):
    """Handle bigger goal collection during progressive onboarding"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Champion"
    bigger_goal = message.text.strip()
    
    try:
        # Save the bigger goal
        supabase.table("users").update({
            "goal_90_days": bigger_goal,
            "status": "first_impression_complete",
            "bigger_goal_collected_at": datetime.now().isoformat()
        }).eq("telegram_user_id", user_id).execute()
        
        await state.clear()
        
        # Show completion message with next steps
        completion_message = f"""🎯 **Perfect, {user_name}!**

**Your bigger goal:** "{bigger_goal}"

I'll keep this in mind as I help you build momentum toward it! 

**You're all set up! Here's what you can do:**

🚀 **/commit** - Add your next commitment
📊 **/progress** - See your wins adding up  
🏆 **/leaderboard** - Compare with other champions
💪 **/help** - Explore all features

**Welcome to your transformation journey!** 💪

*What's your next commitment going to be?*"""

        await message.answer(completion_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error collecting bigger goal: {e}")
        await state.clear()
        await message.answer(f"Got it, {user_name}! I'll remember that goal as we work together. Ready for your next commitment? 🚀")

async def set_bot_commands():
    """Set bot commands for the menu"""
    commands = [
        BotCommand(command="start", description="Welcome message"),
        BotCommand(command="commit", description="Add a new commitment"),
        BotCommand(command="done", description="Mark commitments as complete"),
        BotCommand(command="list", description="View your active commitments"),
        BotCommand(command="progress", description="See your meaningful progress"),
        BotCommand(command="stats", description="View points & achievements"),
        BotCommand(command="leaderboard", description="See this week's top performers"),
        BotCommand(command="feedback", description="Send feedback or suggestions"),
        BotCommand(command="debug", description="Debug your account status"),
        BotCommand(command="fix", description="Emergency reset if stuck"),
        BotCommand(command="help", description="Show help message"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Main function to run the bot"""
    try:
        await set_bot_commands()
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())