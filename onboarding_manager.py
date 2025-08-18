#!/usr/bin/env python3
"""
Fixed Unified Onboarding Manager - Works with existing database schema
Eliminates conflicts between multiple user detection systems
"""

import logging
from typing import Optional
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)

class OnboardingManager:
    """Unified onboarding state management - works with existing schema"""
    
    def __init__(self, supabase_client: Client, role_manager=None):
        self.supabase = supabase_client
        self.role_manager = role_manager
    
    async def get_user_onboarding_status(self, telegram_user_id: int) -> str:
        """Get user's onboarding status - uses existing columns as proxy"""
        try:
            # Query existing columns instead of non-existent onboarding_status
            result = self.supabase.table("users").select(
                "first_bot_interaction_at, total_commitments, completed_commitments"
            ).eq("telegram_user_id", telegram_user_id).execute()
            
            if not result.data:
                return "new"  # User doesn't exist = new user
            
            user = result.data[0]
            
            # Determine status based on existing data
            has_first_interaction = user.get("first_bot_interaction_at") is not None
            total_commitments = user.get("total_commitments", 0) 
            completed_commitments = user.get("completed_commitments", 0)
            
            # Logic: 
            # - If no first interaction: new
            # - If has interaction but no commitments: new  
            # - If has commitments but none completed: in_progress
            # - If has completed commitments: completed
            
            if not has_first_interaction:
                return "new"
            elif total_commitments == 0:
                return "new"  # Started but never made commitments
            elif completed_commitments == 0:
                return "in_progress"  # Has commitments but none completed
            else:
                return "completed"  # Has completed at least one commitment
            
        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            # For existing users with data, assume completed to avoid blocking
            try:
                # Quick check if user exists with commitments
                check = self.supabase.table("users").select("total_commitments").eq("telegram_user_id", telegram_user_id).execute()
                if check.data and check.data[0].get("total_commitments", 0) > 0:
                    return "completed"  # Don't block existing users
            except:
                pass
            return "new"  # Default to new only for truly new users
    
    async def should_show_first_impression(self, telegram_user_id: int) -> bool:
        """Check if user should see first impression flow"""
        status = await self.get_user_onboarding_status(telegram_user_id)
        
        # CRITICAL FIX: Only show first impression for truly new users
        # Don't block users who already have commitments or interactions
        return status == "new"  # Removed "in_progress" to fix blocking issue
    
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
        """Initialize user and start onboarding process using centralized role manager"""
        try:
            if self.role_manager:
                # Use centralized user creation
                success = await self.role_manager.ensure_user_exists(telegram_user_id, first_name, username)
                if not success:
                    logger.error(f"❌ Failed to create user {telegram_user_id} via role_manager")
                    return False
                
                # Ensure first_bot_interaction_at is set
                try:
                    existing = self.supabase.table("users").select("first_bot_interaction_at").eq("telegram_user_id", telegram_user_id).execute()
                    if existing.data and not existing.data[0].get("first_bot_interaction_at"):
                        self.supabase.table("users").update({
                            "first_bot_interaction_at": datetime.now().isoformat()
                        }).eq("telegram_user_id", telegram_user_id).execute()
                        logger.info(f"✅ Set first_bot_interaction_at for user {telegram_user_id}")
                except Exception as update_e:
                    logger.warning(f"User created but couldn't update first_bot_interaction_at: {update_e}")
                    
                logger.info(f"✅ User {telegram_user_id} ready for onboarding via role_manager")
                return True
                
            else:
                # Fallback to legacy method
                logger.warning("⚠️ role_manager not available, using legacy onboarding creation")
                existing = self.supabase.table("users").select("id, first_bot_interaction_at").eq("telegram_user_id", telegram_user_id).execute()
                
                if not existing.data:
                    user_data = {
                        "telegram_user_id": telegram_user_id,
                        "first_name": first_name or "User",
                        "username": username,
                        "first_bot_interaction_at": datetime.now().isoformat(),
                        "last_activity_at": datetime.now().isoformat()
                    }
                    
                    self.supabase.table("users").insert(user_data).execute()
                    logger.info(f"Created new user {telegram_user_id} (legacy)")
                    
                else:
                    # Update existing user's activity
                    update_data = {
                        "last_activity_at": datetime.now().isoformat()
                    }
                    
                    # Set first_bot_interaction_at if it's missing  
                    if not existing.data[0].get("first_bot_interaction_at"):
                        update_data["first_bot_interaction_at"] = datetime.now().isoformat()
                
                self.supabase.table("users").update(update_data).eq("telegram_user_id", telegram_user_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting onboarding: {e}")
            return False
    
    async def advance_to_goal_created(self, telegram_user_id: int) -> bool:
        """Move user to 'in_progress' - update commitment counts"""
        # Since we don't have onboarding_status column, we'll rely on commitment counts
        # This will be automatically reflected in get_user_onboarding_status logic
        return True
    
    async def complete_onboarding(self, telegram_user_id: int) -> bool:
        """Mark onboarding as complete - update completion counts"""
        # Since we don't have onboarding_status column, we'll rely on completed_commitments count
        # This will be automatically reflected in get_user_onboarding_status logic  
        return True
    
    async def set_onboarding_status(self, telegram_user_id: int, status: str) -> bool:
        """Set onboarding status - NOOP since column doesn't exist"""
        # This method exists for compatibility but does nothing
        # Status is determined dynamically from commitment counts
        logger.info(f"Onboarding status set to {status} for user {telegram_user_id} (using commitment counts as proxy)")
        return True