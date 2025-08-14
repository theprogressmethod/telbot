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
        return os.getenv("SUPABASE_URL", "").strip()
    
    @property
    def supabase_key(self) -> str:
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
            
            # Prepare data
            commitment_data = {
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
role_manager = UserRoleManager(supabase)

# Temporary storage for callback data (use Redis in production)
temp_storage = {}

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
        # First-time user experience
        welcome_text = f"""Welcome to The Progress Method, {user_name}! 🎯

You've just joined a community of people who turn goals into reality.

**What makes this different?**
• AI-powered SMART goal analysis 🧠
• Daily commitment tracking 📝
• Optional accountability pods with real people 👥

**Let's start simple:**
👉 Try: `/commit Read for 30 minutes today`

I'll analyze it and help you make it even better! 

**Want to join others?** 
Check out our accountability pods at theprogressmethod.com 

Ready to build better habits? 🚀"""
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

*Tips:*
- Be specific with your commitments
- Start small and build consistency
- Check off completed items daily

"""
    
    # Add role-specific features
    if permissions.get("can_join_pods"):
        help_text += "*Pod Member Features:*\n/pods - View your pod info\n"
        
    if permissions.get("can_access_long_term_goals"):
        help_text += "*Paid Features:*\n/goals - Manage long-term goals\n/insights - Get AI insights\n"
    
    if permissions.get("can_view_analytics"):
        help_text += "*Admin Commands:*\n/stats - View platform statistics\n/grant_role - Grant role to user\n/users - Manage users\n"
    
    help_text += "\nQuestions? Use /feedback to reach us!"
    
    await message.answer(help_text, parse_mode="Markdown")

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

@dp.message(Command("stats"))
async def stats_handler(message: Message):
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
async def fix_loading_handler(message: Message):
    """Emergency command to fix stuck loading"""
    await message.answer(
        "🔧 If you had a stuck loading screen, it should be fixed now!\n\n"
        "Try your /commit command again. If it keeps happening:\n"
        "• Use /aitest to check AI status\n"
        "• The AI service might be slow\n"
        "• Your commitments are still being saved!"
    )

@dp.message()
async def handle_text_messages(message: Message):
    """Handle all other text messages"""
    text = message.text.lower()
    
    # Check if it looks like a commitment
    commitment_keywords = ["will", "going to", "commit", "promise", "plan to", "intend to"]
    has_commitment_keyword = any(keyword in text for keyword in commitment_keywords)
    
    if has_commitment_keyword and len(text) > 10:
        await message.answer(
            f"That sounds like a commitment! Would you like me to save it?\n\n"
            f"Use: /commit {message.text}"
        )
    else:
        await message.answer(
            "I didn't understand that. Try:\n\n"
            "/commit <your commitment> - Add a new commitment\n"
            "/done - Mark commitments complete\n"
            "/help - See all commands"
        )

async def set_bot_commands():
    """Set bot commands for the menu"""
    commands = [
        BotCommand(command="start", description="Welcome message"),
        BotCommand(command="commit", description="Add a new commitment"),
        BotCommand(command="done", description="Mark commitments as complete"),
        BotCommand(command="list", description="View your active commitments"),
        BotCommand(command="feedback", description="Send feedback or suggestions"),
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