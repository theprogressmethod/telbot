#!/usr/bin/env python3
"""
Unified Onboarding Manager - Single Source of Truth for User State
Eliminates conflicts between multiple user detection systems
"""

import logging
from typing import Optional
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)

class OnboardingManager:
    """Unified onboarding state management - single source of truth"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_user_onboarding_status(self, telegram_user_id: int) -> str:
        """Get user's onboarding status - single source of truth"""
        try:
            result = self.supabase.table("users").select("onboarding_status").eq("telegram_user_id", telegram_user_id).execute()
            
            if not result.data:
                return "new"  # User doesn't exist = new user
            
            return result.data[0].get("onboarding_status", "new")
            
        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            return "new"  # Default to new on error
    
    async def should_show_first_impression(self, telegram_user_id: int) -> bool:
        """Check if user should see first impression flow"""
        status = await self.get_user_onboarding_status(telegram_user_id)
        return status in ["new", "in_progress"]
    
    async def is_waiting_for_first_goal(self, telegram_user_id: int) -> bool:
        """Check if user is waiting to input their first goal"""
        status = await self.get_user_onboarding_status(telegram_user_id)
        return status == "new"
    
    async def is_waiting_for_completion(self, telegram_user_id: int) -> bool:
        """Check if user has goal but hasn't completed it yet"""
        status = await self.get_user_onboarding_status(telegram_user_id)
        return status == "in_progress"
    
    async def is_onboarding_complete(self, telegram_user_id: int) -> bool:
        """Check if user has completed onboarding"""
        status = await self.get_user_onboarding_status(telegram_user_id)
        return status == "completed"
    
    async def start_onboarding(self, telegram_user_id: int, first_name: str = None, username: str = None) -> bool:
        """Initialize user and start onboarding process"""
        try:
            # Check if user exists
            existing = self.supabase.table("users").select("id, onboarding_status").eq("telegram_user_id", telegram_user_id).execute()
            
            if not existing.data:
                # Create new user with 'new' status
                user_data = {
                    "telegram_user_id": telegram_user_id,
                    "first_name": first_name or "User",
                    "username": username,
                    "email": f"{telegram_user_id}@telegram.user",
                    "onboarding_status": "new",
                    "created_at": datetime.now().isoformat(),
                    "first_bot_interaction_at": datetime.now().isoformat(),
                    "last_activity_at": datetime.now().isoformat()
                }
                
                self.supabase.table("users").insert(user_data).execute()
                logger.info(f"Created new user {telegram_user_id} with onboarding_status: new")
                
            else:
                # Update existing user's last activity
                self.supabase.table("users").update({
                    "last_activity_at": datetime.now().isoformat()
                }).eq("telegram_user_id", telegram_user_id).execute()
                
                # If user was already created but status is missing, set to new
                if not existing.data[0].get("onboarding_status"):
                    await self.set_onboarding_status(telegram_user_id, "new")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting onboarding: {e}")
            return False
    
    async def advance_to_goal_created(self, telegram_user_id: int) -> bool:
        """Move user to 'in_progress' after they create their first goal"""
        return await self.set_onboarding_status(telegram_user_id, "in_progress")
    
    async def complete_onboarding(self, telegram_user_id: int) -> bool:
        """Mark onboarding as complete after first goal completion"""
        return await self.set_onboarding_status(telegram_user_id, "completed")
    
    async def set_onboarding_status(self, telegram_user_id: int, status: str) -> bool:
        """Set user's onboarding status"""
        try:
            valid_statuses = ["new", "in_progress", "completed"]
            if status not in valid_statuses:
                logger.error(f"Invalid onboarding status: {status}")
                return False
            
            self.supabase.table("users").update({
                "onboarding_status": status,
                "last_activity_at": datetime.now().isoformat()
            }).eq("telegram_user_id", telegram_user_id).execute()
            
            logger.info(f"Set onboarding status for user {telegram_user_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting onboarding status: {e}")
            return False
    
    async def get_user_stats(self, telegram_user_id: int) -> dict:
        """Get user stats for display purposes"""
        try:
            result = self.supabase.table("users").select(
                "total_commitments, completed_commitments, current_streak, onboarding_status"
            ).eq("telegram_user_id", telegram_user_id).execute()
            
            if not result.data:
                return {"total_commitments": 0, "completed_commitments": 0, "current_streak": 0, "onboarding_status": "new"}
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"total_commitments": 0, "completed_commitments": 0, "current_streak": 0, "onboarding_status": "new"}
    
    async def reset_user_onboarding(self, telegram_user_id: int) -> bool:
        """Reset user to beginning of onboarding (for debugging)"""
        try:
            # Set status back to new
            await self.set_onboarding_status(telegram_user_id, "new")
            
            # Optional: Clear FSM state if needed
            logger.info(f"Reset onboarding for user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting onboarding: {e}")
            return False