#!/usr/bin/env python3
"""
Enhanced User Onboarding - Working with existing user table
Immediately captures user identity and integrates with ecosystem
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json
import re

logger = logging.getLogger(__name__)

class EnhancedUserOnboarding:
    """Enhanced onboarding system working with existing database structure"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def handle_first_time_user(self, telegram_user_id: int, first_name: str, username: str) -> str:
        """Comprehensive first-time user onboarding message"""
        
        # Create user with comprehensive data collection prompt
        welcome_message = f"""🎯 **Welcome to The Progress Method, {first_name}!**

You've just joined a community of people who turn dreams into reality through small, daily commitments.

**Let's get you set up for success!** 

To personalize your experience and connect you with the right tools, I'd love to know:

**1. What should I call you?** (Your preferred name)
**2. What's your email?** (For syncing progress across platforms) 
**3. What's one big goal you want to make progress on?**

You can share all at once like:
`Sarah
sarah@email.com  
Write my first novel`

Or one at a time - whatever feels comfortable! 

**Once we have the basics, I'll help you:**
✅ Create your first smart commitment
📊 Set up progress tracking  
🎯 Connect with accountability tools
👥 Explore our pod community (optional)

Ready to transform your goals into reality? 🚀"""

        # Mark user as needing onboarding data
        await self._mark_user_for_data_collection(telegram_user_id)
        
        return welcome_message
    
    async def _mark_user_for_data_collection(self, telegram_user_id: int):
        """Mark user as needing additional data collection"""
        try:
            self.supabase.table("users").update({
                "status": "needs_onboarding_data",
                "updated_at": datetime.now().isoformat()
            }).eq("telegram_user_id", telegram_user_id).execute()
        except Exception as e:
            logger.error(f"Error marking user for data collection: {e}")
    
    async def process_onboarding_data(self, telegram_user_id: int, user_input: str) -> Dict[str, Any]:
        """Process comprehensive onboarding data from user"""
        try:
            # Get current user status
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return {"status": "error", "message": "User not found"}
            
            user = user_result.data[0]
            
            # Check if user needs onboarding data
            if user.get("status") != "needs_onboarding_data":
                return {"status": "not_needed", "message": None}
            
            # Parse the input
            parsed_data = self._parse_onboarding_input(user_input)
            
            if not parsed_data:
                return {
                    "status": "need_more_info", 
                    "message": """I'd love to help set you up! Please share:

**1. Your preferred name**
**2. Your email address** 
**3. One main goal you want to work on**

You can put each on a separate line or share them however is easiest! 😊"""
                }
            
            # Update user profile with collected data
            profile_updates = {
                "first_name": parsed_data.get("name", user.get("first_name")),
                "email": parsed_data.get("email"),
                "goal_90_days": parsed_data.get("goal"),
                "status": "onboarding_complete",
                "onboarded_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Remove None values
            profile_updates = {k: v for k, v in profile_updates.items() if v is not None}
            
            self.supabase.table("users").update(profile_updates).eq("telegram_user_id", telegram_user_id).execute()
            
            # Create personalized completion message
            completion_message = self._create_completion_message(parsed_data)
            
            logger.info(f"✅ Completed onboarding for user {telegram_user_id}")
            
            return {"status": "completed", "message": completion_message, "data": parsed_data}
            
        except Exception as e:
            logger.error(f"Error processing onboarding data: {e}")
            return {"status": "error", "message": "Sorry, something went wrong. Let's try again!"}
    
    def _parse_onboarding_input(self, user_input: str) -> Optional[Dict[str, str]]:
        """Parse user input to extract name, email, and goal"""
        lines = [line.strip() for line in user_input.split('\n') if line.strip()]
        
        if len(lines) < 2:
            # Try to parse from single line
            return self._parse_single_line_input(user_input)
        
        parsed = {}
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for line in lines:
            # Check if line contains email
            email_match = re.search(email_pattern, line)
            if email_match and "email" not in parsed:
                parsed["email"] = email_match.group()
            elif len(line.split()) == 1 and "name" not in parsed:
                # Single word, likely a name
                parsed["name"] = line
            elif "email" not in line.lower() and len(line) > 10:
                # Longer text, likely a goal
                parsed["goal"] = line
        
        # Require at least email to proceed
        if "email" in parsed:
            return parsed
        
        return None
    
    def _parse_single_line_input(self, user_input: str) -> Optional[Dict[str, str]]:
        """Parse single line input for email"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_input)
        
        if email_match:
            return {"email": email_match.group()}
        
        return None
    
    def _create_completion_message(self, parsed_data: Dict[str, str]) -> str:
        """Create personalized onboarding completion message"""
        name = parsed_data.get("name", "")
        email = parsed_data.get("email", "")
        goal = parsed_data.get("goal", "")
        
        message = f"""🎉 **Perfect! You're all set up{f', {name}' if name else ''}!**

Here's what I've got:
"""
        
        if email:
            message += f"📧 **Email:** {email} (for progress syncing)\\n"
        if goal:
            message += f"🎯 **Goal:** {goal}\\n"
        
        message += f"""
**🚀 Let's get started!**

**Your first commitment:** Based on your goal, what's ONE small thing you could do today?

Try it: `/commit [something specific and achievable]`

Examples:
• `/commit Research business ideas for 20 minutes`
• `/commit Write 200 words of my book`
• `/commit Do 10 push-ups`

**What's next:**
📊 `/progress` - See your meaningful progress stats
👥 `/pods` - Learn about accountability pods  
🏆 `/leaderboard` - See community progress
💬 `/feedback` - Send suggestions anytime

Welcome to your transformation journey! 💪"""

        return message
    
    async def check_user_needs_onboarding_data(self, telegram_user_id: int) -> bool:
        """Check if user needs to provide onboarding data"""
        try:
            user_result = self.supabase.table("users").select("status, email").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return False
            
            user = user_result.data[0]
            
            # User needs onboarding if:
            # 1. Status is specifically "needs_onboarding_data", OR  
            # 2. They don't have an email (key identifier)
            return (user.get("status") == "needs_onboarding_data" or 
                   not user.get("email"))
            
        except Exception as e:
            logger.error(f"Error checking onboarding status: {e}")
            return False
    
    async def get_user_identity_completeness(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get how complete a user's identity data is"""
        try:
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return {"completeness": 0, "missing": ["everything"]}
            
            user = user_result.data[0]
            
            # Check key identity fields
            identity_fields = {
                "first_name": user.get("first_name"),
                "email": user.get("email"), 
                "goal_90_days": user.get("goal_90_days"),
                "accountability_style": user.get("accountability_style")
            }
            
            filled_fields = sum(1 for v in identity_fields.values() if v)
            total_fields = len(identity_fields)
            completeness = (filled_fields / total_fields) * 100
            
            missing = [k for k, v in identity_fields.items() if not v]
            
            return {
                "completeness": round(completeness),
                "missing": missing,
                "data": identity_fields
            }
            
        except Exception as e:
            logger.error(f"Error checking identity completeness: {e}")
            return {"completeness": 0, "missing": ["unknown"]}
    
    async def create_gentle_data_request(self, telegram_user_id: int) -> Optional[str]:
        """Create a gentle request for missing user data"""
        try:
            identity_check = await self.get_user_identity_completeness(telegram_user_id)
            
            if identity_check["completeness"] >= 75:
                return None  # User has enough data
            
            missing = identity_check["missing"]
            
            if "email" in missing:
                return """👋 Quick favor! To sync your progress and unlock all features, could you share your email?

Just reply with: `your.email@example.com`

This helps us connect your Telegram progress with the web platform! 📧✨"""
            
            elif "goal_90_days" in missing:
                return """🎯 I'd love to personalize your experience! What's one main goal you're working toward?

Could be anything:
• Career/business goal
• Health & fitness
• Creative project  
• Personal development

Just share in a few words! This helps me give better suggestions. 💪"""
            
            elif "accountability_style" in missing:
                return """💡 Quick question: How do you work best with accountability?

1️⃣ **Solo focus** - Just daily bot check-ins
2️⃣ **Small group** - Weekly calls with 3-5 people
3️⃣ **Community** - Part of larger goal-focused group
4️⃣ **Still exploring** - Not sure yet

Just reply with the number! This helps us recommend the right tools. 🚀"""
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating data request: {e}")
            return None
    
    async def should_trigger_data_collection(self, telegram_user_id: int) -> bool:
        """Determine if we should proactively ask for more user data"""
        try:
            # Get user's activity and completeness
            user_result = self.supabase.table("users").select("total_commitments, created_at, last_activity_at").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return False
            
            user = user_result.data[0]
            commitments = user.get("total_commitments", 0)
            
            # Get identity completeness
            identity_check = await self.get_user_identity_completeness(telegram_user_id)
            
            # Trigger data collection if:
            # 1. User has made 2+ commitments (showing engagement) AND
            # 2. Identity completeness is less than 50%
            return commitments >= 2 and identity_check["completeness"] < 50
            
        except Exception as e:
            logger.error(f"Error checking data collection trigger: {e}")
            return False