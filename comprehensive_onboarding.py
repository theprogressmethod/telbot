#!/usr/bin/env python3
"""
Comprehensive Onboarding System for The Progress Method
Captures user identity and preferences from first interaction
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json
from enum import Enum

logger = logging.getLogger(__name__)

class OnboardingStage(Enum):
    """Onboarding stages for progressive data collection"""
    INITIAL_CONTACT = "initial_contact"         # Just started
    BASIC_INFO = "basic_info"                   # Name, email collection
    GOAL_DISCOVERY = "goal_discovery"           # What they want to achieve
    PREFERENCE_SETUP = "preference_setup"       # How they want to be supported
    FIRST_COMMITMENT = "first_commitment"       # Getting them started
    ECOSYSTEM_INTEGRATION = "ecosystem_integration"  # Connect to broader system
    COMPLETED = "completed"                     # Fully onboarded

class ComprehensiveOnboarding:
    """Manages comprehensive user onboarding with progressive data collection"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.onboarding_flows = self._define_onboarding_flows()
    
    def _define_onboarding_flows(self) -> Dict[str, Dict]:
        """Define comprehensive onboarding flows"""
        return {
            "initial_contact": {
                "message": """🎯 **Welcome to The Progress Method!**

I'm here to help you turn your dreams into daily progress.

Before we start building amazing habits together, I'd love to learn a bit about you!

**What should I call you?** 
(Your first name works great!)""",
                "next_stage": "basic_info",
                "data_to_collect": ["first_name"],
                "timeout_hours": 24
            },
            
            "basic_info": {
                "message": """Great to meet you, {first_name}! 👋

To personalize your experience and connect you with the right accountability tools, could you share your email?

**Email:** (This helps us sync your progress across platforms)

*Don't worry - we never spam and you can unsubscribe anytime!*""",
                "next_stage": "goal_discovery", 
                "data_to_collect": ["email"],
                "timeout_hours": 48
            },
            
            "goal_discovery": {
                "message": """Perfect! Now for the fun part... 🚀

**What's one big goal or dream you'd love to make progress on?**

Examples:
• "Start my own business"
• "Write a book"
• "Get healthier"
• "Learn guitar"
• "Build better relationships"

Dream big - I'll help you break it down into daily actions! ✨""",
                "next_stage": "preference_setup",
                "data_to_collect": ["goal_90_days"],
                "timeout_hours": 72
            },
            
            "preference_setup": {
                "message": """That's an amazing goal! 🎯

**How do you work best with accountability?**

1️⃣ **Solo Focus** - Just me and the bot, daily check-ins
2️⃣ **Small Group** - Weekly calls with 3-5 like-minded people  
3️⃣ **Community** - Part of a larger goal-focused community
4️⃣ **Not sure yet** - Let's start simple and see what works

Reply with just the number (1, 2, 3, or 4)""",
                "next_stage": "first_commitment",
                "data_to_collect": ["accountability_style"],
                "timeout_hours": 48
            },
            
            "first_commitment": {
                "message": """Perfect! Let's get you started with your first commitment. 💪

Based on your goal: "{goal_90_days}"

**What's ONE small thing you could commit to doing today?**

Make it:
• ✅ Specific: "Read for 30 minutes" not "Read more"
• ✅ Achievable: Something you can definitely do today
• ✅ Meaningful: A step toward your bigger goal

Try it: `/commit [your commitment here]`""",
                "next_stage": "ecosystem_integration",
                "data_to_collect": ["first_commitment"],
                "timeout_hours": 24
            },
            
            "ecosystem_integration": {
                "message": """🎉 **Amazing! You've made your first commitment!**

You're now part of The Progress Method ecosystem. Here's what happens next:

🤖 **Daily Support:** I'll check in and help you stay consistent
📊 **Progress Tracking:** Watch your momentum build over time
🎯 **Smart Analysis:** Get insights on what works best for you

{integration_options}

**Ready to see your progress?** Try `/progress` anytime!

Welcome to your transformation journey! 🚀""",
                "next_stage": "completed",
                "data_to_collect": [],
                "timeout_hours": 0
            }
        }
    
    async def start_onboarding(self, telegram_user_id: int, first_name: str, username: str) -> bool:
        """Start comprehensive onboarding for new user"""
        try:
            # Create onboarding state
            onboarding_data = {
                "telegram_user_id": telegram_user_id,
                "current_stage": OnboardingStage.INITIAL_CONTACT.value,
                "collected_data": json.dumps({
                    "telegram_first_name": first_name,
                    "telegram_username": username,
                    "started_at": datetime.now().isoformat()
                }),
                "stage_started_at": datetime.now().isoformat(),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("onboarding_states").upsert(onboarding_data).execute()
            
            if result.data:
                logger.info(f"✅ Started onboarding for user {telegram_user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting onboarding: {e}")
            
        return False
    
    async def get_onboarding_message(self, telegram_user_id: int) -> Optional[str]:
        """Get the next onboarding message for user"""
        try:
            # Get current onboarding state
            state_result = self.supabase.table("onboarding_states").select("*").eq("telegram_user_id", telegram_user_id).eq("is_active", True).execute()
            
            if not state_result.data:
                return None
                
            state = state_result.data[0]
            current_stage = state["current_stage"]
            collected_data = json.loads(state["collected_data"])
            
            if current_stage not in self.onboarding_flows:
                return None
                
            flow = self.onboarding_flows[current_stage]
            message = flow["message"]
            
            # Template substitution
            if "{first_name}" in message and "first_name" in collected_data:
                message = message.replace("{first_name}", collected_data["first_name"])
            if "{goal_90_days}" in message and "goal_90_days" in collected_data:
                message = message.replace("{goal_90_days}", collected_data["goal_90_days"])
            if "{integration_options}" in message:
                integration_options = self._get_integration_options(collected_data)
                message = message.replace("{integration_options}", integration_options)
                
            return message
            
        except Exception as e:
            logger.error(f"Error getting onboarding message: {e}")
            return None
    
    def _get_integration_options(self, collected_data: Dict) -> str:
        """Generate integration options based on user preferences"""
        accountability_style = collected_data.get("accountability_style", "1")
        
        if accountability_style == "2":
            return """🎯 **Want a pod?** You mentioned liking small groups! 
Check out our accountability pods at theprogressmethod.com"""
        elif accountability_style == "3":
            return """🌟 **Community Access:** Join our Discord for daily motivation!
Link: [community link]"""
        else:
            return """💡 **Pro tip:** If you ever want accountability partners, 
we have pods available at theprogressmethod.com"""
    
    async def process_onboarding_response(self, telegram_user_id: int, user_input: str) -> Dict[str, Any]:
        """Process user response and advance onboarding"""
        try:
            # Get current state
            state_result = self.supabase.table("onboarding_states").select("*").eq("telegram_user_id", telegram_user_id).eq("is_active", True).execute()
            
            if not state_result.data:
                return {"status": "no_onboarding", "message": None}
                
            state = state_result.data[0]
            current_stage = state["current_stage"]
            collected_data = json.loads(state["collected_data"])
            
            if current_stage not in self.onboarding_flows:
                return {"status": "invalid_stage", "message": None}
                
            flow = self.onboarding_flows[current_stage]
            data_to_collect = flow["data_to_collect"]
            
            # Process the input based on current stage
            if current_stage == "initial_contact" and data_to_collect:
                collected_data["first_name"] = user_input.strip()
                
            elif current_stage == "basic_info" and data_to_collect:
                # Validate email format
                if "@" in user_input and "." in user_input:
                    collected_data["email"] = user_input.strip().lower()
                else:
                    return {"status": "invalid_email", "message": "Please enter a valid email address (like: you@example.com)"}
                    
            elif current_stage == "goal_discovery" and data_to_collect:
                collected_data["goal_90_days"] = user_input.strip()
                
            elif current_stage == "preference_setup" and data_to_collect:
                # Validate accountability style choice
                if user_input.strip() in ["1", "2", "3", "4"]:
                    styles = {"1": "solo", "2": "small_group", "3": "community", "4": "exploring"}
                    collected_data["accountability_style"] = styles[user_input.strip()]
                else:
                    return {"status": "invalid_choice", "message": "Please reply with just the number: 1, 2, 3, or 4"}
                    
            elif current_stage == "first_commitment" and data_to_collect:
                collected_data["first_commitment_intent"] = user_input.strip()
                # Note: Actual commitment creation happens via /commit command
                
            # Advance to next stage
            next_stage = flow["next_stage"]
            
            # Update user's main profile with collected data
            await self._update_user_profile(telegram_user_id, collected_data)
            
            # Update onboarding state
            update_data = {
                "current_stage": next_stage,
                "collected_data": json.dumps(collected_data),
                "stage_started_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if next_stage == "completed":
                update_data["is_active"] = False
                update_data["completed_at"] = datetime.now().isoformat()
            
            self.supabase.table("onboarding_states").update(update_data).eq("id", state["id"]).execute()
            
            # Get next message
            if next_stage != "completed":
                next_message = await self.get_onboarding_message(telegram_user_id)
                return {"status": "continue", "message": next_message, "stage": next_stage}
            else:
                completion_message = self.onboarding_flows["ecosystem_integration"]["message"]
                # Template substitution for completion message
                if "{goal_90_days}" in completion_message:
                    completion_message = completion_message.replace("{goal_90_days}", collected_data.get("goal_90_days", "your goal"))
                if "{integration_options}" in completion_message:
                    integration_options = self._get_integration_options(collected_data)
                    completion_message = completion_message.replace("{integration_options}", integration_options)
                    
                return {"status": "completed", "message": completion_message}
                
        except Exception as e:
            logger.error(f"Error processing onboarding response: {e}")
            return {"status": "error", "message": "Sorry, something went wrong. Let's continue with /start"}
    
    async def _update_user_profile(self, telegram_user_id: int, collected_data: Dict):
        """Update user's main profile with onboarding data"""
        try:
            # Map onboarding data to user profile fields
            profile_updates = {}
            
            if "first_name" in collected_data:
                profile_updates["first_name"] = collected_data["first_name"]
            if "email" in collected_data:
                profile_updates["email"] = collected_data["email"]
            if "goal_90_days" in collected_data:
                profile_updates["goal_90_days"] = collected_data["goal_90_days"]
            if "accountability_style" in collected_data:
                profile_updates["accountability_style"] = collected_data["accountability_style"]
                
            profile_updates["updated_at"] = datetime.now().isoformat()
            
            if profile_updates:
                self.supabase.table("users").update(profile_updates).eq("telegram_user_id", telegram_user_id).execute()
                logger.info(f"✅ Updated user profile for {telegram_user_id}")
                
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
    
    async def check_onboarding_timeouts(self) -> List[Dict]:
        """Check for users with onboarding timeouts and send gentle reminders"""
        try:
            # Get active onboarding states that might have timed out
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            
            timeout_states = self.supabase.table("onboarding_states").select("*").eq("is_active", True).lt("stage_started_at", cutoff_time).execute()
            
            reminders = []
            
            for state in timeout_states.data:
                current_stage = state["current_stage"]
                collected_data = json.loads(state["collected_data"])
                
                # Create gentle reminder based on stage
                reminder_message = self._create_timeout_reminder(current_stage, collected_data)
                
                if reminder_message:
                    reminders.append({
                        "telegram_user_id": state["telegram_user_id"],
                        "message": reminder_message,
                        "stage": current_stage
                    })
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error checking onboarding timeouts: {e}")
            return []
    
    def _create_timeout_reminder(self, stage: str, collected_data: Dict) -> Optional[str]:
        """Create gentle timeout reminder message"""
        first_name = collected_data.get("first_name", "there")
        
        reminders = {
            "initial_contact": f"Hi {first_name}! 👋 Still interested in building better habits? Just reply with your preferred name to continue!",
            "basic_info": f"Hey {first_name}! Ready to connect your email so we can sync your progress? No rush! 😊",
            "goal_discovery": f"Hi {first_name}! I'm excited to help with your goals when you're ready. What's one thing you'd love to make progress on?",
            "preference_setup": f"Hey {first_name}! Just wondering what accountability style sounds best to you? Reply 1, 2, 3, or 4 when convenient!",
            "first_commitment": f"Hi {first_name}! Ready for your first commitment? Even something tiny counts! Try: /commit [something small]"
        }
        
        return reminders.get(stage)
    
    async def is_user_in_onboarding(self, telegram_user_id: int) -> bool:
        """Check if user is currently in onboarding process"""
        try:
            result = self.supabase.table("onboarding_states").select("id").eq("telegram_user_id", telegram_user_id).eq("is_active", True).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking onboarding status: {e}")
            return False
    
    async def get_user_onboarding_data(self, telegram_user_id: int) -> Dict:
        """Get all collected onboarding data for a user"""
        try:
            result = self.supabase.table("onboarding_states").select("*").eq("telegram_user_id", telegram_user_id).order("created_at", desc=True).limit(1).execute()
            
            if result.data:
                return json.loads(result.data[0]["collected_data"])
            return {}
            
        except Exception as e:
            logger.error(f"Error getting onboarding data: {e}")
            return {}
    
    async def create_onboarding_tables(self):
        """Create onboarding tracking tables"""
        try:
            logger.info("✅ Onboarding tables ready for creation")
            logger.info("Tables: onboarding_states, onboarding_analytics")
            return True
        except Exception as e:
            logger.error(f"Error creating onboarding tables: {e}")
            return False