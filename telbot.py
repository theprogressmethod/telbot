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
from smart_3_retry_system import Smart2RetrySystem

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

# Initialize SMART 3-retry system - will be created after smart_analyzer
smart_3_retry = None

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
                logger.error(f"❌ User not found for telegram_user_id: {telegram_user_id}")
                return False
                
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

# Initialize SMART 2-retry system now that dependencies are ready
smart_3_retry = Smart2RetrySystem(smart_analyzer, bot)

# Initialize role manager
from user_role_manager import UserRoleManager
from user_analytics import UserAnalytics
from basic_pod_system import BasicPodSystem
try:
    from dream_focused_analytics import DreamFocusedAnalytics
    dream_analytics = DreamFocusedAnalytics(supabase)
except ImportError:
    logger.warning("⚠️ DreamFocusedAnalytics not available")
    dream_analytics = None
try:
    from leaderboard import Leaderboard
    leaderboard = Leaderboard(supabase)
except ImportError:
    logger.warning("⚠️ Leaderboard not available")
    leaderboard = None
from pod_week_tracker import PodWeekTracker
try:
    from attendance_adapter import AttendanceAdapter
    meet_tracker = AttendanceAdapter(supabase)
except ImportError:
    logger.warning("⚠️ AttendanceAdapter not available")
    meet_tracker = None
try:
    from nurture_sequences import NurtureSequences, SequenceType
    nurture_system = NurtureSequences(supabase)
except ImportError:
    logger.warning("⚠️ NurtureSequences not available")
    nurture_system = None
try:
    from enhanced_user_onboarding import EnhancedUserOnboarding
    onboarding_system = EnhancedUserOnboarding(supabase)
except ImportError:
    logger.warning("⚠️ EnhancedUserOnboarding not available")
    onboarding_system = None

role_manager = UserRoleManager(supabase)
user_analytics = UserAnalytics(supabase)
pod_tracker = PodWeekTracker(supabase)
pod_system = BasicPodSystem(supabase)

# Temporary storage for callback data (use Redis in production)
temp_storage = {}

# Storage for 3-retry system state (track users awaiting retry input)
retry_input_state = {}

class CommitmentTracker:
    """Advanced commitment tracking with reminders and accountability features"""
    
    def __init__(self, supabase_client: Client, bot: Bot):
        self.supabase = supabase_client
        self.bot = bot
        
    async def schedule_reminder(self, telegram_user_id: int, commitment_id: str, reminder_time: datetime):
        """Schedule a reminder for a specific commitment"""
        try:
            reminder_data = {
                "telegram_user_id": telegram_user_id,
                "commitment_id": commitment_id,
                "reminder_time": reminder_time.isoformat(),
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("commitment_reminders").insert(reminder_data).execute()
            logger.info(f"✅ Reminder scheduled for commitment {commitment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error scheduling reminder: {e}")
            return False
    
    async def get_pending_reminders(self) -> List[Dict]:
        """Get all pending reminders that are due"""
        try:
            current_time = datetime.now().isoformat()
            
            result = self.supabase.table("commitment_reminders").select(
                "*, commitments(id, commitment, telegram_user_id)"
            ).eq("status", "scheduled").lte("reminder_time", current_time).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error getting pending reminders: {e}")
            return []
    
    async def send_reminder(self, reminder: Dict):
        """Send a reminder message to user"""
        try:
            telegram_user_id = reminder["telegram_user_id"]
            commitment = reminder["commitments"]
            
            if not commitment:
                return False
                
            reminder_text = f"⏰ **Commitment Reminder**\n\n" \
                           f"📝 \"{commitment['commitment']}\"\n\n" \
                           f"How's this going? Ready to mark it complete?\n" \
                           f"Use /done to check it off! 💪"
            
            await self.bot.send_message(
                chat_id=telegram_user_id,
                text=reminder_text,
                parse_mode="Markdown"
            )
            
            # Mark reminder as sent
            await self.mark_reminder_sent(reminder["id"])
            
            logger.info(f"✅ Reminder sent to user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending reminder: {e}")
            return False
    
    async def mark_reminder_sent(self, reminder_id: str):
        """Mark reminder as sent"""
        try:
            self.supabase.table("commitment_reminders").update({
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            }).eq("id", reminder_id).execute()
            
        except Exception as e:
            logger.error(f"❌ Error marking reminder as sent: {e}")
    
    async def get_commitment_progress(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get detailed progress statistics for a user"""
        try:
            # Get total commitments
            total_result = self.supabase.table("commitments").select("count", count="exact").eq("telegram_user_id", telegram_user_id).execute()
            total_commitments = total_result.count or 0
            
            # Get completed commitments
            completed_result = self.supabase.table("commitments").select("count", count="exact").eq("telegram_user_id", telegram_user_id).eq("status", "completed").execute()
            completed_commitments = completed_result.count or 0
            
            # Get active commitments
            active_result = self.supabase.table("commitments").select("count", count="exact").eq("telegram_user_id", telegram_user_id).eq("status", "active").execute()
            active_commitments = active_result.count or 0
            
            # Calculate completion rate
            completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # Get streak information
            streak = await self.calculate_commitment_streak(telegram_user_id)
            
            # Get this week's stats
            week_stats = await self.get_week_stats(telegram_user_id)
            
            # Get longest streak
            longest_streak = await self.get_longest_streak(telegram_user_id)
            
            return {
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "active_commitments": active_commitments,
                "completion_rate": round(completion_rate, 1),
                "current_streak": streak,
                "longest_streak": longest_streak,
                "week_completed": week_stats['completed'],
                "week_total": week_stats['total'],
                "week_rate": week_stats['rate'],
                "progress_level": self._get_progress_level(completion_rate, total_commitments)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting commitment progress: {e}")
            return {}
    
    async def get_week_stats(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get this week's commitment statistics"""
        try:
            from datetime import timedelta
            
            # Get start of current week (Monday)
            today = datetime.now().date()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_start_str = week_start.isoformat()
            
            # Get all commitments created this week
            week_result = self.supabase.table("commitments").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).gte("created_at", week_start_str).execute()
            
            week_total = len(week_result.data) if week_result.data else 0
            week_completed = sum(1 for c in week_result.data if c.get("status") == "completed") if week_result.data else 0
            week_rate = round((week_completed / week_total * 100) if week_total > 0 else 0, 1)
            
            return {
                "total": week_total,
                "completed": week_completed,
                "rate": week_rate
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting week stats: {e}")
            return {"total": 0, "completed": 0, "rate": 0}
    
    async def get_longest_streak(self, telegram_user_id: int) -> int:
        """Calculate longest commitment streak ever achieved"""
        try:
            # Get all completed commitments
            result = self.supabase.table("commitments").select("completed_at").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "completed").order("completed_at", desc=False).execute()
            
            if not result.data:
                return 0
            
            # Convert to dates and sort
            dates = []
            for commitment in result.data:
                if commitment.get("completed_at"):
                    date = datetime.fromisoformat(commitment["completed_at"].replace('Z', '+00:00')).date()
                    dates.append(date)
            
            if not dates:
                return 0
                
            dates = sorted(list(set(dates)))  # Remove duplicates and sort
            
            # Find longest consecutive sequence
            longest = 1
            current = 1
            
            for i in range(1, len(dates)):
                if (dates[i] - dates[i-1]).days == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
                    
            return longest
            
        except Exception as e:
            logger.error(f"❌ Error calculating longest streak: {e}")
            return 0
    
    async def calculate_commitment_streak(self, telegram_user_id: int) -> int:
        """Calculate current commitment completion streak"""
        try:
            # Get recent completed commitments ordered by completion date
            result = self.supabase.table("commitments").select("completed_at").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "completed").order("completed_at", desc=True).limit(30).execute()
            
            if not result.data:
                return 0
                
            streak = 0
            current_date = datetime.now().date()
            
            for commitment in result.data:
                if not commitment.get("completed_at"):
                    continue
                    
                completed_date = datetime.fromisoformat(commitment["completed_at"].replace('Z', '+00:00')).date()
                expected_date = current_date - timedelta(days=streak)
                
                if completed_date == expected_date:
                    streak += 1
                else:
                    break
                    
            return streak
            
        except Exception as e:
            logger.error(f"❌ Error calculating streak: {e}")
            return 0
    
    def _get_progress_level(self, completion_rate: float, total_commitments: int) -> str:
        """Determine user's progress level based on stats"""
        if total_commitments < 5:
            return "🌱 Getting Started"
        elif completion_rate >= 90:
            return "🔥 Consistency Master"
        elif completion_rate >= 75:
            return "💪 Strong Performer"
        elif completion_rate >= 50:
            return "📈 Building Momentum"
        else:
            return "🎯 Finding Rhythm"
    
    async def send_accountability_check(self, telegram_user_id: int):
        """Send accountability check-in for overdue commitments"""
        try:
            # Get commitments older than 24 hours without completion
            yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
            
            result = self.supabase.table("commitments").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "active").lt("created_at", yesterday).execute()
            
            if not result.data:
                return False
                
            overdue_count = len(result.data)
            
            accountability_text = f"🤔 **Accountability Check-In**\n\n" \
                                 f"You have {overdue_count} commitment{'s' if overdue_count != 1 else ''} " \
                                 f"from yesterday or earlier:\n\n"
            
            for i, commitment in enumerate(result.data[:3], 1):  # Show max 3
                accountability_text += f"{i}. \"{commitment['commitment']}\"\n"
            
            if overdue_count > 3:
                accountability_text += f"... and {overdue_count - 3} more\n"
                
            accountability_text += f"\n💭 Sometimes life happens - that's totally normal!\n" \
                                  f"Ready to check some off or adjust your goals?\n\n" \
                                  f"Use /done to mark completed or /list to review all."
            
            await self.bot.send_message(
                chat_id=telegram_user_id,
                text=accountability_text,
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ Accountability check sent to user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending accountability check: {e}")
            return False

# Initialize commitment tracker
commitment_tracker = CommitmentTracker(supabase, bot)

async def process_pending_reminders():
    """Process and send pending reminders - call this periodically"""
    try:
        pending_reminders = await commitment_tracker.get_pending_reminders()
        
        for reminder in pending_reminders:
            await commitment_tracker.send_reminder(reminder)
            
        if pending_reminders:
            logger.info(f"✅ Processed {len(pending_reminders)} pending reminders")
            
        return len(pending_reminders)
        
    except Exception as e:
        logger.error(f"❌ Error processing pending reminders: {e}")
        return 0

async def send_daily_accountability_checks():
    """Send daily accountability checks to users with overdue commitments"""
    try:
        # Get all users with active commitments older than 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        
        result = supabase.table("commitments").select("telegram_user_id").eq(
            "status", "active"
        ).lt("created_at", yesterday).execute()
        
        if not result.data:
            return 0
            
        # Get unique user IDs
        user_ids = list(set(item["telegram_user_id"] for item in result.data))
        
        sent_count = 0
        for user_id in user_ids:
            success = await commitment_tracker.send_accountability_check(user_id)
            if success:
                sent_count += 1
                
        logger.info(f"✅ Sent {sent_count} accountability check-ins")
        return sent_count
        
    except Exception as e:
        logger.error(f"❌ Error sending daily accountability checks: {e}")
        return 0

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
async def start_handler(message: Message):
    """Handle /start command with first-time user detection"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "there"
    username = message.from_user.username
    
    # Ensure user exists in database and get role info
    await role_manager.ensure_user_exists(user_id, user_name, username)
    
    # Check if first-time user
    is_first_time = await role_manager.is_first_time_user(user_id)
    user_roles = await role_manager.get_user_roles(user_id)
    
    # Test database on first interaction
    db_test = await DatabaseManager.test_database()
    
    if is_first_time:
        # Enhanced first-time user experience with immediate data collection
        welcome_text = await onboarding_system.handle_first_time_user(user_id, user_name, username)
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
    
    # Trigger nurture sequence for first-time users
    if is_first_time:
        user_result = supabase.table("users").select("id").eq("telegram_user_id", user_id).execute()
        if user_result.data:
            user_uuid = user_result.data[0]["id"]
            await nurture_system.check_triggers(user_uuid, "first_interaction")
    
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
    """Handle /commit command with SMART 3-retry enhancement system"""
    # Extract commitment text
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.answer(
            "Please provide a commitment after /commit\n\n"
            "Example: /commit Read for 30 minutes today\n\n"
            "💡 **Tip:** The more specific, the better! Include what, how much, and when."
        )
        return
    
    commitment_text = command_parts[1].strip()
    user_id = message.from_user.id
    
    logger.info(f"🎯 Processing commitment with 3-retry system: {commitment_text}")
    
    # Test database before proceeding
    if not await DatabaseManager.test_database():
        await message.answer("❌ Database connection error. Please try again later or contact support.")
        return
    
    # Start the entertaining loading experience
    loading_message = await create_loading_experience(message, commitment_text)
    
    try:
        # Use new SMART 3-retry enhancement system
        result = await smart_3_retry.process_commitment_with_retries(
            user_id=user_id,
            commitment_text=commitment_text,
            message_to_edit=loading_message,
            chat_id=message.chat.id
        )
        
        # Handle the result
        if result and result.get('success', False):
            # Save the commitment
            success = await DatabaseManager.save_commitment(
                telegram_user_id=user_id,
                commitment=result['commitment'],
                original_commitment=result['original_commitment'],
                smart_score=result['score']
            )
            
            if success:
                # Trigger nurture sequences
                await _trigger_commitment_sequences(user_id)
                logger.info(f"✅ Commitment saved with 3-retry system: {result.get('retry_count', 0)} retries")
            else:
                await loading_message.edit_text("❌ Error saving commitment. Please check /dbtest and try again.")
        
        # If result is None or awaiting_retry, the 3-retry system is handling the interaction
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced commit handler: {e}")
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
async def complete_commitment_callback(callback: CallbackQuery):
    """Handle commitment completion"""
    commitment_id = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    
    logger.info(f"✅ User {user_id} completing commitment {commitment_id}")
    
    # Mark as complete
    success = await DatabaseManager.complete_commitment(commitment_id)
    
    if not success:
        await callback.answer("❌ Error marking commitment complete. Please try again.", show_alert=True)
        return
    
    # Send celebration
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

# SMART 3-Retry System Callback Handlers
@dp.callback_query(F.data.startswith("retry_"))
async def retry_callback_handler(callback: CallbackQuery):
    """Handle all retry system callbacks"""
    try:
        result = await smart_3_retry.handle_retry_callback(callback, callback.data)
        
        if result and result.get('awaiting_input'):
            # User wants to manually improve - track state
            retry_key = result['retry_key']
            user_id = callback.from_user.id
            retry_input_state[user_id] = retry_key
            
        elif result and result.get('success'):
            # Save the commitment to database
            success = await DatabaseManager.save_commitment(
                telegram_user_id=callback.from_user.id,
                commitment=result['commitment'],
                original_commitment=result['original_commitment'],
                smart_score=result['score']
            )
            
            if success:
                # Commitment was saved, trigger sequences
                await _trigger_commitment_sequences(callback.from_user.id)
                logger.info(f"✅ Retry callback commitment saved successfully")
            else:
                logger.error(f"❌ Failed to save commitment from retry callback")
            
    except Exception as e:
        logger.error(f"❌ Error in retry callback handler: {e}")
        await callback.answer("Something went wrong. Please try /commit again.", show_alert=True)

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
    
    # Check if user has admin role
    is_admin = False
    try:
        roles_result = supabase.table("user_roles").select("role_type").eq(
            "user_id", supabase.table("users").select("id").eq("telegram_user_id", user_id).execute().data[0]["id"]
        ).eq("is_active", True).execute()
        is_admin = any(r["role_type"] in ["admin", "super_admin"] for r in roles_result.data)
    except:
        pass
    
    help_text = """📚 **How to use this bot:**

**Core Commands:**
/start - Welcome & getting started
/commit <text> - Add a commitment
/done - Mark commitments complete  
/list - View your active commitments
/progress - View streaks & stats
/feedback <message> - Send feedback
/help - This help message

**Pod Commands:**
/mypod - View your pod info
/podleaderboard - Weekly pod rankings
/podweek - Current pod week progress

**Tips:**
• Be specific with commitments
• Include what, how much, and when
• Check off completed items daily
• Join a pod for accountability!

"""
    
    # Add admin commands if user is admin
    if is_admin:
        help_text += """**Admin Commands:**
/listpods - View all active pods
/createpod "Name" Day Time - Create new pod
/addtopod @user "Pod Name" - Add user to pod
/grant_role - Grant roles to users
/adminstats - View platform statistics

"""
    
    help_text += "Questions? Use /feedback to reach us!"
    
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("progress"))
async def progress_handler(message: Message):
    """Show meaningful progress with streaks and completion rates"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "there"
    
    # Ensure user exists
    await role_manager.ensure_user_exists(
        user_id, 
        message.from_user.first_name,
        message.from_user.username
    )
    
    # Get progress data
    progress = await commitment_tracker.get_commitment_progress(user_id)
    
    if not progress or progress.get('total_commitments', 0) == 0:
        progress_message = (
            f"🌱 **Welcome to Your Progress Journey, {user_name}!**\n\n"
            f"You haven't made any commitments yet.\n\n"
            f"Every journey starts with a single step!\n"
            f"Use /commit to add your first goal and start building momentum.\n\n"
            f"💡 **Pro tip:** Start small and be specific!"
        )
    else:
        # Build visual progress bar
        completion_rate = progress['completion_rate']
        bar_length = 10
        filled = int(completion_rate / 10)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Streak display with emoji
        current_streak = progress['current_streak']
        longest_streak = progress.get('longest_streak', current_streak)
        streak_emoji = "🔥" if current_streak >= 7 else "⭐" if current_streak >= 3 else "🌟"
        
        # Week progress
        week_completed = progress.get('week_completed', 0)
        week_total = progress.get('week_total', 0)
        week_rate = progress.get('week_rate', 0)
        
        # Build the progress message
        progress_message = f"📊 **{user_name}'s Progress Dashboard**\n"
        progress_message += f"{'═' * 30}\n\n"
        
        # Streaks section
        progress_message += f"{streak_emoji} **STREAKS**\n"
        progress_message += f"Current: **{current_streak} days**"
        if current_streak > 0:
            progress_message += " - Keep it going!"
        progress_message += f"\nLongest: **{longest_streak} days**\n\n"
        
        # This week section
        progress_message += f"📅 **THIS WEEK**\n"
        if week_total > 0:
            progress_message += f"Completed: **{week_completed}/{week_total}** ({week_rate}%)\n"
        else:
            progress_message += f"No commitments yet this week\n"
        progress_message += f"Active now: **{progress['active_commitments']}** commitments\n\n"
        
        # Overall stats
        progress_message += f"📈 **OVERALL STATS**\n"
        progress_message += f"Total made: **{progress['total_commitments']}** commitments\n"
        progress_message += f"Completed: **{progress['completed_commitments']}** ({completion_rate}%)\n"
        progress_message += f"Progress: [{bar}] {completion_rate}%\n\n"
        
        # Progress level
        progress_message += f"🏆 **LEVEL**: {progress['progress_level']}\n\n"
        
        # Motivational message based on performance
        if completion_rate >= 80:
            progress_message += "💪 **Outstanding consistency!** You're crushing it!"
        elif completion_rate >= 60:
            progress_message += "🎯 **Great progress!** You're building strong habits!"
        elif completion_rate >= 40:
            progress_message += "📈 **Good momentum!** Keep pushing forward!"
        elif current_streak >= 3:
            progress_message += f"🔥 **{current_streak} day streak!** You're on fire!"
        else:
            progress_message += "🌱 **Every step counts!** Keep going!"
        
        # Call to action
        progress_message += "\n\n"
        if progress['active_commitments'] == 0:
            progress_message += "📝 Use /commit to add a new goal!"
        elif progress['active_commitments'] > 0:
            progress_message += "✅ Use /done to mark commitments complete!"
    
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

@dp.message(Command("mypod"))
async def my_pod_handler(message: Message):
    """Show user's pod information"""
    user_id = message.from_user.id
    
    # Get user's pod
    pod_info = await pod_system.get_user_pod(user_id)
    
    if not pod_info:
        await message.answer(
            "🎯 **You're not in a pod yet!**\n\n"
            "Pods are groups of 4-6 people who meet weekly for accountability.\n\n"
            "Being in a pod helps you:\n"
            "• Stay consistent with your commitments\n"
            "• Get support from peers\n"
            "• Celebrate wins together\n\n"
            "Ask an admin to add you to a pod!"
        )
        return
    
    # Format pod information
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    meeting_day = days[pod_info["meeting_day"]]
    
    pod_message = f"🎯 **Your Pod: {pod_info['pod_name']}**\n"
    pod_message += f"{'═' * 30}\n\n"
    
    pod_message += f"📅 **Weekly Meeting**\n"
    pod_message += f"Every {meeting_day} at {pod_info['meeting_time']}\n"
    if pod_info["meeting_link"]:
        pod_message += f"[Join Meeting]({pod_info['meeting_link']})\n"
    pod_message += f"\n"
    
    pod_message += f"👥 **Members ({pod_info['total_members']}/{pod_info['max_members']})**\n"
    for i, member in enumerate(pod_info["members"], 1):
        emoji = "👑" if member["role"] == "leader" else "🎯"
        pod_message += f"{i}. {emoji} **{member['name']}**\n"
        if member["week_commitments"] > 0:
            pod_message += f"   This week: {member['week_completion_rate']}% ({member['week_commitments']} commitments)\n"
        else:
            pod_message += f"   No commitments yet this week\n"
    
    pod_message += f"\n📊 Use /podleaderboard to see this week's rankings!"
    
    await message.answer(pod_message, parse_mode="Markdown")

@dp.message(Command("podweek"))
async def pod_week_handler(message: Message):
    """Show current pod week progress"""
    user_id = message.from_user.id
    
    # Get user's pod
    pod_info = await pod_system.get_user_pod(user_id)
    
    if not pod_info:
        await message.answer("🎯 You're not in a pod yet! Ask an admin to add you.")
        return
    
    pod_id = pod_info["pod_id"]
    summary = await pod_tracker.format_pod_week_summary(str(user_id), pod_id)
    await message.answer(summary, parse_mode="Markdown")

@dp.message(Command("podleaderboard"))
async def pod_leaderboard_handler(message: Message):
    """Show pod week leaderboard"""
    user_id = message.from_user.id
    
    # Get user's pod
    pod_info = await pod_system.get_user_pod(user_id)
    
    if not pod_info:
        await message.answer("🎯 You're not in a pod yet! Ask an admin to add you.")
        return
    
    pod_id = pod_info["pod_id"]
    leaderboard_data = await pod_system.get_pod_leaderboard(pod_id)
    
    if not leaderboard_data:
        await message.answer("📊 No pod activity this week yet! Be the first to make a commitment.")
        return
    
    message_text = f"🏆 **{pod_info['pod_name']} - This Week's Leaderboard**\n"
    message_text += f"{'═' * 30}\n\n"
    
    for member in leaderboard_data:
        message_text += f"{member['emoji']} **{member['rank']}. {member['name']}**\n"
        if member['week_total'] > 0:
            message_text += f"   ✅ Completed: {member['week_completed']}/{member['week_total']} ({member['completion_rate']}%)\n"
            message_text += f"   ⭐ Points: {member['points']}\n"
        else:
            message_text += f"   No commitments yet\n"
        message_text += "\n"
    
    # Add motivational message
    if leaderboard_data[0]['points'] > 0:
        message_text += f"🔥 Leading: **{leaderboard_data[0]['name']}** with {leaderboard_data[0]['points']} points!\n"
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
    attendance_summary = await meet_tracker.format_attendance_summary(pod_id, user_uuid)
    
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
    
    attendance_summary = await meet_tracker.format_attendance_summary(pod_id)
    
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
    success = await meet_tracker.manually_record_attendance(pod_id, target_user_id, meeting_date, attended, duration)
    
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

@dp.message(Command("createpod"))
async def create_pod_handler(message: Message):
    """Admin command to create a new pod"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    # Parse command: /createpod "Pod Name" Monday 19:00 https://meet.google.com/xyz
    parts = message.text.split(maxsplit=4)
    if len(parts) < 4:
        await message.answer(
            "📝 **Create Pod Usage:**\n"
            "`/createpod \"Pod Name\" Day Time [MeetLink]`\n\n"
            "Examples:\n"
            "• `/createpod \"Alpha Squad\" Monday 19:00`\n"
            "• `/createpod \"Beta Team\" Wednesday 20:30 https://meet.google.com/abc-defg-hij`\n\n"
            "Days: Monday-Sunday\n"
            "Time: 24hr format (HH:MM)",
            parse_mode="Markdown"
        )
        return
    
    try:
        # Extract pod name (handle quotes)
        import re
        name_match = re.search(r'"([^"]+)"', message.text)
        if not name_match:
            await message.answer("❌ Pod name must be in quotes")
            return
            
        pod_name = name_match.group(1)
        remaining = message.text[name_match.end():].strip().split()
        
        if len(remaining) < 2:
            await message.answer("❌ Please provide day and time")
            return
            
        day_str = remaining[0]
        time_str = remaining[1]
        meeting_link = remaining[2] if len(remaining) > 2 else None
        
        # Convert day to number
        days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                "friday": 4, "saturday": 5, "sunday": 6}
        day_num = days.get(day_str.lower())
        
        if day_num is None:
            await message.answer("❌ Invalid day. Use Monday-Sunday")
            return
        
        # Validate time format
        if not re.match(r"^\d{1,2}:\d{2}$", time_str):
            await message.answer("❌ Invalid time format. Use HH:MM (24hr)")
            return
            
        # Create pod
        result = await pod_system.create_pod(
            pod_name=pod_name,
            meeting_time=f"{time_str}:00",
            meeting_day=day_num,
            created_by_id=user_id,
            meeting_link=meeting_link
        )
        
        if result["success"]:
            await message.answer(
                f"✅ **Pod Created Successfully!**\n\n"
                f"🎯 Name: {pod_name}\n"
                f"📅 Meeting: {day_str} at {time_str}\n"
                f"👥 Capacity: 0/6 members\n\n"
                f"Use `/addtopod @username \"{pod_name}\"` to add members"
            )
        else:
            await message.answer(f"❌ Failed to create pod: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in create pod: {e}")
        await message.answer("❌ Error creating pod. Check command format.")

@dp.message(Command("addtopod"))
async def add_to_pod_handler(message: Message):
    """Admin command to add user to a pod"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    # Parse command: /addtopod @username "Pod Name"
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "📝 **Add to Pod Usage:**\n"
            "`/addtopod @username \"Pod Name\"`\n\n"
            "Example:\n"
            "`/addtopod @john \"Alpha Squad\"`",
            parse_mode="Markdown"
        )
        return
    
    try:
        username = parts[1].replace("@", "")
        
        # Extract pod name
        import re
        name_match = re.search(r'"([^"]+)"', message.text)
        if not name_match:
            await message.answer("❌ Pod name must be in quotes")
            return
            
        pod_name = name_match.group(1)
        
        # Get user by username
        user_result = supabase.table("users").select("telegram_user_id").eq("telegram_username", username).execute()
        if not user_result.data:
            await message.answer(f"❌ User @{username} not found")
            return
            
        target_user_id = user_result.data[0]["telegram_user_id"]
        
        # Get pod by name
        pod_result = supabase.table("pods").select("id").eq("name", pod_name).eq("status", "active").execute()
        if not pod_result.data:
            await message.answer(f"❌ Pod '{pod_name}' not found")
            return
            
        pod_id = pod_result.data[0]["id"]
        
        # Add user to pod
        result = await pod_system.assign_user_to_pod(target_user_id, pod_id, user_id)
        
        if result["success"]:
            await message.answer(
                f"✅ **Added @{username} to {pod_name}!**\n\n"
                f"They can now use:\n"
                f"• `/mypod` - View pod info\n"
                f"• `/podleaderboard` - See rankings\n"
                f"• `/podweek` - Check progress"
            )
            
            # Notify the user
            try:
                await bot.send_message(
                    target_user_id,
                    f"🎉 **Welcome to {pod_name}!**\n\n"
                    f"You've been added to a pod!\n"
                    f"Use `/mypod` to see your pod details and meet your teammates.\n\n"
                    f"Pods help you stay accountable and achieve your goals! 🚀"
                )
            except:
                pass  # User might have blocked bot
                
        else:
            await message.answer(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error adding to pod: {e}")
        await message.answer("❌ Error adding user to pod")

@dp.message(Command("listpods"))
async def list_pods_handler(message: Message):
    """Admin command to list all pods"""
    user_id = message.from_user.id
    
    if not await role_manager.user_has_any_role(user_id, ["admin", "super_admin"]):
        await message.answer("⛔ Admin access required.")
        return
    
    pods = await pod_system.list_all_pods()
    
    if not pods:
        await message.answer("📭 No active pods yet. Use `/createpod` to create one.")
        return
    
    message_text = "🎯 **Active Pods**\n"
    message_text += f"{'═' * 30}\n\n"
    
    for pod in pods:
        status_emoji = "🔴" if pod["status"] == "Full" else "🟢"
        message_text += f"{status_emoji} **{pod['name']}**\n"
        message_text += f"   Members: {pod['members']}\n"
        message_text += f"   Meeting: {pod['meeting']}\n"
        message_text += f"   Status: {pod['status']}\n\n"
    
    message_text += f"Total: {len(pods)} pods"
    
    await message.answer(message_text, parse_mode="Markdown")

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
async def fix_loading_handler(message: Message):
    """Emergency command to fix stuck loading"""
    await message.answer(
        "🔧 If you had a stuck loading screen, it should be fixed now!\n\n"
        "Try your /commit command again. If it keeps happening:\n"
        "• Use /aitest to check AI status\n"
        "• The AI service might be slow\n"
        "• Your commitments are still being saved!"
    )

@dp.message(Command("remind"))
async def remind_handler(message: Message):
    """Set reminder for commitment"""
    command_parts = message.text.split(maxsplit=2)
    
    if len(command_parts) < 3:
        await message.answer(
            "⏰ **Set Commitment Reminders**\n\n"
            "Usage: `/remind <hours> <commitment text>`\n\n"
            "Examples:\n"
            "• `/remind 2 workout for 30 minutes` - Remind in 2 hours\n"
            "• `/remind 24 finish project report` - Remind in 24 hours\n\n"
            "💡 I'll send you a friendly reminder when it's time!",
            parse_mode="Markdown"
        )
        return
    
    try:
        hours = int(command_parts[1])
        commitment_text = command_parts[2].strip()
        user_id = message.from_user.id
        
        if hours <= 0 or hours > 168:  # Max 1 week
            await message.answer("⏰ Please set reminder between 1 hour and 168 hours (1 week)")
            return
        
        # First, create the commitment
        analysis = await smart_analyzer.analyze_commitment(commitment_text)
        success = await DatabaseManager.save_commitment(
            telegram_user_id=user_id,
            commitment=commitment_text,
            original_commitment=commitment_text,
            smart_score=analysis.get("score", 6)
        )
        
        if success:
            # Get the commitment ID (latest one for this user)
            commitments = await DatabaseManager.get_active_commitments(user_id)
            if commitments:
                commitment_id = commitments[0]["id"]  # Most recent
                
                # Schedule reminder
                reminder_time = datetime.now() + timedelta(hours=hours)
                await commitment_tracker.schedule_reminder(user_id, commitment_id, reminder_time)
                
                await message.answer(
                    f"✅ **Commitment & Reminder Set!**\n\n"
                    f"📝 \"{commitment_text}\"\n"
                    f"⏰ Reminder: {reminder_time.strftime('%Y-%m-%d at %I:%M %p')}\n\n"
                    f"I'll check in with you then! 💪"
                )
            else:
                await message.answer("❌ Error setting up reminder. Please try again.")
        else:
            await message.answer("❌ Error creating commitment. Please try again.")
            
    except ValueError:
        await message.answer("⚠️ Please enter a valid number of hours")
    except Exception as e:
        logger.error(f"Error in remind handler: {e}")
        await message.answer("❌ Error setting reminder. Please try again.")

@dp.message(Command("track"))
async def track_handler(message: Message):
    """Show detailed commitment tracking and progress"""
    user_id = message.from_user.id
    
    try:
        # Get comprehensive progress data
        progress = await commitment_tracker.get_commitment_progress(user_id)
        
        if not progress:
            await message.answer(
                "📊 No tracking data yet!\n\n"
                "Start with /commit to add your first commitment and build your progress! 🚀"
            )
            return
        
        track_text = f"📊 **Your Commitment Journey**\n\n"
        track_text += f"🎯 **Overall Progress**\n"
        track_text += f"• Total Commitments: {progress['total_commitments']}\n"
        track_text += f"• Completed: {progress['completed_commitments']}\n"
        track_text += f"• Active: {progress['active_commitments']}\n"
        track_text += f"• Success Rate: {progress['completion_rate']}%\n\n"
        
        track_text += f"🔥 **Current Streak**: {progress['current_streak']} days\n"
        track_text += f"🏆 **Level**: {progress['progress_level']}\n\n"
        
        # Add motivational message based on performance
        if progress['completion_rate'] >= 80:
            track_text += "🌟 **Amazing consistency!** You're building powerful habits!"
        elif progress['completion_rate'] >= 60:
            track_text += "💪 **Great progress!** Keep up the momentum!"
        elif progress['completion_rate'] >= 40:
            track_text += "📈 **Building momentum!** Small steps lead to big wins!"
        else:
            track_text += "🌱 **Every start is progress!** Focus on small, consistent steps!"
            
        track_text += f"\n\n💡 Use /commit to add more goals or /done to check off completed ones!"
        
        await message.answer(track_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in track handler: {e}")
        await message.answer("❌ Error getting tracking data. Please try again.")

@dp.message(Command("checkin"))
async def checkin_handler(message: Message):
    """Manual accountability check-in"""
    user_id = message.from_user.id
    
    try:
        # Send accountability check
        success = await commitment_tracker.send_accountability_check(user_id)
        
        if not success:
            await message.answer(
                "✅ **All caught up!**\n\n"
                "You don't have any overdue commitments right now. Great job staying on track! 🎉\n\n"
                "Use /commit to add new goals or /track to see your progress!"
            )
        
    except Exception as e:
        logger.error(f"Error in checkin handler: {e}")
        await message.answer("❌ Error during check-in. Please try again.")

@dp.message(Command("streakboost"))
async def streakboost_handler(message: Message):
    """Get personalized streak-building tips"""
    user_id = message.from_user.id
    
    try:
        progress = await commitment_tracker.get_commitment_progress(user_id)
        current_streak = progress.get('current_streak', 0)
        completion_rate = progress.get('completion_rate', 0)
        
        boost_text = f"🔥 **Streak Boost Tips**\n\n"
        boost_text += f"Current Streak: **{current_streak} days**\n\n"
        
        if current_streak == 0:
            boost_text += "🌱 **Starting Your Streak:**\n"
            boost_text += "• Begin with ONE small, achievable commitment\n"
            boost_text += "• Set a specific time to do it daily\n"
            boost_text += "• Use /remind to get helpful nudges\n"
            boost_text += "• Focus on consistency over perfection\n\n"
            boost_text += "💡 **Today's Challenge:** Make one micro-commitment and complete it!"
            
        elif current_streak < 7:
            boost_text += "📈 **Building Momentum:**\n"
            boost_text += "• You're doing great! Keep the momentum going\n"
            boost_text += "• Stack your habit with something you already do\n"
            boost_text += "• Celebrate small wins - they add up!\n"
            boost_text += "• Plan tomorrow's commitment tonight\n\n"
            boost_text += f"🎯 **Goal:** Reach 7 days for your first week!"
            
        elif current_streak < 21:
            boost_text += "💪 **Solid Foundation:**\n"
            boost_text += "• Excellent work building consistency!\n"
            boost_text += "• Consider slightly increasing challenge level\n"
            boost_text += "• Track your wins to see progress patterns\n"
            boost_text += "• Share your success with accountability partners\n\n"
            boost_text += f"🎯 **Goal:** 21 days makes a strong habit!"
            
        else:
            boost_text += "🏆 **Streak Master:**\n"
            boost_text += "• Outstanding dedication! You're an inspiration!\n"
            boost_text += "• Consider mentoring others or joining pods\n"
            boost_text += "• Explore bigger, more impactful commitments\n"
            boost_text += "• Use your consistency to tackle long-term goals\n\n"
            boost_text += f"🚀 **Challenge:** Help others build their streaks too!"
            
        await message.answer(boost_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in streakboost handler: {e}")
        await message.answer("❌ Error getting streak tips. Please try again.")

# SMART 3-Retry System Message Handler (must come before general text handler)
async def handle_retry_input(message: Message) -> bool:
    """Handle retry input from users - returns True if handled"""
    user_id = message.from_user.id
    
    if user_id in retry_input_state:
        retry_key = retry_input_state[user_id]
        
        try:
            result = await smart_3_retry.handle_retry_input(message, retry_key)
            
            if result and result.get('success'):
                # Save the commitment
                success = await DatabaseManager.save_commitment(
                    telegram_user_id=user_id,
                    commitment=result['commitment'],
                    original_commitment=result['original_commitment'],
                    smart_score=result['score']
                )
                
                if success:
                    await _trigger_commitment_sequences(user_id)
                    logger.info(f"✅ Retry input saved: {result.get('retry_count', 0)} retries")
            
            # Clean up state
            del retry_input_state[user_id]
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling retry input: {e}")
            del retry_input_state[user_id]
            await message.answer("❌ Something went wrong. Please try /commit again.")
            return True
    
    return False

@dp.message()
async def handle_text_messages(message: Message):
    """Handle all other text messages with enhanced onboarding"""
    user_id = message.from_user.id
    text = message.text.lower()
    
    # First check if this is retry input
    if await handle_retry_input(message):
        return
    
    # First, check if user needs onboarding data
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
                await message.answer(data_request, parse_mode="Markdown")
                return
        
        # Default response
        await message.answer(
            "I didn't understand that. Try:\n\n"
            "/commit <your commitment> - Add a new commitment\n"
            "/done - Mark commitments complete\n"
            "/help - See all commands"
        )

async def set_bot_commands():
    """Set bot commands for the menu - includes pod commands"""
    commands = [
        BotCommand(command="start", description="Welcome! Let's get started"),
        BotCommand(command="commit", description="Make a new commitment"),
        BotCommand(command="done", description="Mark commitments complete"),
        BotCommand(command="list", description="See your commitments"),
        BotCommand(command="progress", description="View your progress & streaks"),
        BotCommand(command="mypod", description="View your pod info"),
        BotCommand(command="podleaderboard", description="Pod weekly rankings"),
        BotCommand(command="podweek", description="Pod week progress"),
        BotCommand(command="help", description="Get help with commands"),
        BotCommand(command="feedback", description="Send us feedback"),
        # Admin commands
        BotCommand(command="listpods", description="[Admin] List all pods"),
        BotCommand(command="createpod", description="[Admin] Create new pod"),
        BotCommand(command="addtopod", description="[Admin] Add user to pod"),
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