# Simplified User Role Management System for The Progress Method
# This version works with existing table structure and gracefully handles missing columns

import logging
from typing import List, Dict, Optional
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)

class SimpleRoleManager:
    """Simplified role manager that works with existing database structure"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self._has_telegram_user_id = None
        self._has_user_roles_table = None
    
    async def _check_table_structure(self):
        """Check what columns and tables exist"""
        if self._has_telegram_user_id is None:
            try:
                # Test if telegram_user_id column exists
                result = self.supabase.table("users").select("telegram_user_id").limit(1).execute()
                self._has_telegram_user_id = True
                logger.info("✅ telegram_user_id column exists")
            except Exception:
                self._has_telegram_user_id = False
                logger.info("ℹ️ telegram_user_id column missing - will use user id mapping")
        
        if self._has_user_roles_table is None:
            try:
                # Test if user_roles table exists
                result = self.supabase.table("user_roles").select("id").limit(1).execute()
                self._has_user_roles_table = True
                logger.info("✅ user_roles table exists")
            except Exception:
                self._has_user_roles_table = False
                logger.info("ℹ️ user_roles table missing - using fallback role system")
    
    async def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[Dict]:
        """Get user record by telegram user id, with fallback for existing structure"""
        try:
            await self._check_table_structure()
            
            if self._has_telegram_user_id:
                # Use telegram_user_id column if it exists
                result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
                if result.data:
                    return result.data[0]
            else:
                # Fallback: look for user by some other identifier
                # You might need to adapt this based on your current users table structure
                logger.warning(f"Cannot find user {telegram_user_id} - telegram_user_id column missing")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def ensure_user_exists(self, telegram_user_id: int, first_name: str = None, username: str = None) -> bool:
        """Ensure user exists, with fallback for current structure"""
        try:
            await self._check_table_structure()
            
            if not self._has_telegram_user_id:
                logger.warning("Cannot create user - enhanced schema needed")
                return False
            
            # Check if user exists
            existing_user = await self.get_user_by_telegram_id(telegram_user_id)
            
            if not existing_user:
                # Create new user with available columns
                user_data = {
                    "telegram_user_id": telegram_user_id,
                    # Handle required email column - use telegram_user_id as fallback
                    "email": f"{telegram_user_id}@telegram.user",
                }
                
                # Add optional columns if they exist
                if first_name:
                    user_data["first_name"] = first_name
                if username:
                    user_data["username"] = username
                
                # Try to add timestamp columns if they exist
                try:
                    user_data["first_bot_interaction_at"] = datetime.now().isoformat()
                    user_data["last_activity_at"] = datetime.now().isoformat()
                except:
                    pass  # These columns might not exist yet
                
                result = self.supabase.table("users").insert(user_data).execute()
                logger.info(f"Created new user: {telegram_user_id}")
                
                # Grant default role if roles table exists
                if self._has_user_roles_table:
                    await self.grant_role(telegram_user_id, "unpaid")
            else:
                # Update last activity if column exists
                try:
                    self.supabase.table("users").update({
                        "last_activity_at": datetime.now().isoformat()
                    }).eq("telegram_user_id", telegram_user_id).execute()
                except:
                    pass  # Column might not exist
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring user exists: {e}")
            return False
    
    async def get_user_roles(self, telegram_user_id: int) -> List[str]:
        """Get user roles with fallback"""
        try:
            await self._check_table_structure()
            
            if not self._has_user_roles_table:
                # Fallback: assume all users are 'unpaid'
                return ["unpaid"]
            
            user = await self.get_user_by_telegram_id(telegram_user_id)
            if not user:
                return []
            
            roles_result = self.supabase.table("user_roles").select("role_type").eq("user_id", user["id"]).eq("is_active", True).execute()
            
            roles = [role["role_type"] for role in roles_result.data]
            return roles if roles else ["unpaid"]  # Default to unpaid if no roles
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return ["unpaid"]  # Safe default
    
    async def user_has_role(self, telegram_user_id: int, role: str) -> bool:
        """Check if user has specific role"""
        roles = await self.get_user_roles(telegram_user_id)
        return role in roles
    
    async def grant_role(self, telegram_user_id: int, role: str, granted_by_id: Optional[int] = None) -> bool:
        """Grant role to user"""
        try:
            await self._check_table_structure()
            
            if not self._has_user_roles_table:
                logger.warning("Cannot grant role - user_roles table missing")
                return False
            
            user = await self.get_user_by_telegram_id(telegram_user_id)
            if not user:
                logger.warning(f"User not found: {telegram_user_id}")
                return False
            
            role_data = {
                "user_id": user["id"],
                "role_type": role,
                "is_active": True,
                "granted_at": datetime.now().isoformat()
            }
            
            if granted_by_id:
                grantor = await self.get_user_by_telegram_id(granted_by_id)
                if grantor:
                    role_data["granted_by"] = grantor["id"]
            
            # Use upsert to handle conflicts
            result = self.supabase.table("user_roles").upsert(role_data, on_conflict="user_id,role_type").execute()
            
            logger.info(f"Granted role '{role}' to user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error granting role: {e}")
            return False
    
    async def get_user_permissions(self, telegram_user_id: int) -> Dict[str, bool]:
        """Get user permissions based on roles"""
        roles = await self.get_user_roles(telegram_user_id)
        
        permissions = {
            # Basic permissions (everyone)
            "can_create_commitments": True,
            "can_view_commitments": True,
            
            # Paid features
            "can_join_pods": "paid" in roles or "pod_member" in roles,
            "can_access_analytics": "paid" in roles,
            
            # Admin features  
            "can_view_admin_stats": "admin" in roles or "super_admin" in roles,
            "can_manage_users": "admin" in roles or "super_admin" in roles,
            "can_grant_roles": "admin" in roles or "super_admin" in roles,
            
            # Super admin features
            "can_manage_admins": "super_admin" in roles,
        }
        
        return permissions
    
    async def is_first_time_user(self, telegram_user_id: int) -> bool:
        """Check if this is a first-time user (simplified check)"""
        try:
            user = await self.get_user_by_telegram_id(telegram_user_id)
            if not user:
                return True
            
            # Check if user has made any commitments
            # This works with your existing commitments table
            commitment_result = self.supabase.table("commitments").select("id").eq("user_id", user["id"]).limit(1).execute()
            
            return len(commitment_result.data) == 0
            
        except Exception as e:
            logger.error(f"Error checking first-time user: {e}")
            return False
    
    async def get_role_stats(self) -> Dict[str, int]:
        """Get basic role statistics"""
        try:
            await self._check_table_structure()
            
            if not self._has_user_roles_table:
                total_users = self.supabase.table("users").select("id", count="exact").execute().count
                return {
                    "total_users": total_users,
                    "unpaid": total_users,  # Assume all unpaid without roles table
                }
            
            # Get role counts
            result = self.supabase.table("user_roles").select("role_type").eq("is_active", True).execute()
            
            role_counts = {}
            for role_data in result.data:
                role_type = role_data["role_type"]
                role_counts[role_type] = role_counts.get(role_type, 0) + 1
            
            # Add total users
            total_users = self.supabase.table("users").select("id", count="exact").execute().count
            role_counts["total_users"] = total_users
            
            return role_counts
            
        except Exception as e:
            logger.error(f"Error getting role stats: {e}")
            return {"total_users": 0}