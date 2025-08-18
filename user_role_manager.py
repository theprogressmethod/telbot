# User Role Management System for The Progress Method

import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from supabase import Client

logger = logging.getLogger(__name__)

class UserRoleManager:
    """Manages user roles and permissions for The Progress Method platform"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
    async def get_user_roles(self, telegram_user_id: int) -> List[str]:
        """Get all active roles for a user"""
        try:
            # First get user ID from telegram_user_id
            user_result = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                logger.warning(f"User not found for telegram_user_id: {telegram_user_id}")
                return []
            
            user_id = user_result.data[0]["id"]
            
            # Get active roles
            roles_result = self.supabase.table("user_roles").select("role_type").eq("user_id", user_id).eq("is_active", True).execute()
            
            return [role["role_type"] for role in roles_result.data]
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []
    
    async def user_has_role(self, telegram_user_id: int, role: str) -> bool:
        """Check if user has a specific role"""
        roles = await self.get_user_roles(telegram_user_id)
        return role in roles
    
    async def user_has_any_role(self, telegram_user_id: int, roles: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = await self.get_user_roles(telegram_user_id)
        return any(role in user_roles for role in roles)
    
    async def grant_role(self, telegram_user_id: int, role: str, granted_by_id: Optional[int] = None, expires_at: Optional[datetime] = None) -> bool:
        """Grant a role to a user"""
        try:
            # Get user ID
            user_result = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                logger.warning(f"User not found for telegram_user_id: {telegram_user_id}")
                return False
            
            user_id = user_result.data[0]["id"]
            granted_by_uuid = None
            
            # Get granted_by UUID if provided
            if granted_by_id:
                grantor_result = self.supabase.table("users").select("id").eq("telegram_user_id", granted_by_id).execute()
                if grantor_result.data:
                    granted_by_uuid = grantor_result.data[0]["id"]
            
            # Insert or update role
            role_data = {
                "user_id": user_id,
                "role_type": role,
                "granted_by": granted_by_uuid,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "is_active": True,
                "granted_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("user_roles").upsert(role_data, on_conflict="user_id,role_type").execute()
            
            logger.info(f"Granted role '{role}' to user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error granting role: {e}")
            return False
    
    async def revoke_role(self, telegram_user_id: int, role: str) -> bool:
        """Revoke a role from a user"""
        try:
            # Get user ID
            user_result = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return False
            
            user_id = user_result.data[0]["id"]
            
            # Deactivate role
            result = self.supabase.table("user_roles").update({
                "is_active": False
            }).eq("user_id", user_id).eq("role_type", role).execute()
            
            logger.info(f"Revoked role '{role}' from user {telegram_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking role: {e}")
            return False
    
    async def ensure_user_exists(self, telegram_user_id: int, first_name: str = None, username: str = None) -> bool:
        """Ensure user exists in database and has default 'unpaid' role using atomic transaction"""
        try:
            # Use atomic database function to prevent race conditions
            result = self.supabase.rpc('ensure_user_exists_atomic', {
                'p_telegram_user_id': telegram_user_id,
                'p_first_name': first_name or "User",
                'p_username': username
            }).execute()
            
            if result.data:
                response = result.data
                if response.get('success'):
                    if response.get('is_new_user'):
                        logger.info(f"✅ Created new user: {telegram_user_id} (ID: {response.get('user_id')})")
                    else:
                        logger.debug(f"✅ Updated existing user: {telegram_user_id}")
                    return True
                else:
                    logger.error(f"❌ Database function failed: {response.get('error')}")
                    return False
            else:
                logger.error(f"❌ No data returned from ensure_user_exists_atomic")
                return False
                
        except Exception as e:
            # Fallback to old method if function doesn't exist yet
            if "Could not find the function" in str(e):
                logger.warning(f"⚠️ Atomic function not available, falling back to legacy method for user {telegram_user_id}")
                return await self._ensure_user_exists_legacy(telegram_user_id, first_name, username)
            else:
                logger.error(f"❌ Error calling ensure_user_exists_atomic: {e}")
                return False

    async def _ensure_user_exists_legacy(self, telegram_user_id: int, first_name: str = None, username: str = None) -> bool:
        """Legacy user creation method (kept as fallback)"""
        try:
            # Check if user exists
            existing_user = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            
            if not existing_user.data:
                # Create new user
                user_data = {
                    "telegram_user_id": telegram_user_id,
                    "first_name": first_name or "User",
                    "username": username,
                    # Leave email null - users can provide it later for email features
                    "first_bot_interaction_at": datetime.now().isoformat(),
                    "last_activity_at": datetime.now().isoformat()
                }
                
                user_result = self.supabase.table("users").insert(user_data).execute()
                logger.info(f"Created new user (legacy): {telegram_user_id}")
                
                # Grant default 'unpaid' role
                await self.grant_role(telegram_user_id, "unpaid")
                
            else:
                # Update last activity
                user_id = existing_user.data[0]["id"]
                self.supabase.table("users").update({
                    "last_activity_at": datetime.now().isoformat()
                }).eq("id", user_id).execute()
            
            return True
            
        except Exception as e:
            # Check if it's a duplicate key error (user already exists)
            if "duplicate key value violates unique constraint" in str(e):
                logger.info(f"User {telegram_user_id} already exists (duplicate key), verifying...")
                # Re-query to ensure user actually exists and update last activity
                try:
                    existing_user = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
                    if existing_user.data:
                        user_id = existing_user.data[0]["id"]
                        # Update last activity for existing user
                        self.supabase.table("users").update({
                            "last_activity_at": datetime.now().isoformat()
                        }).eq("id", user_id).execute()
                        logger.info(f"✅ Verified user {telegram_user_id} exists and updated activity (legacy)")
                        return True
                    else:
                        logger.error(f"❌ User {telegram_user_id} should exist after duplicate key error but not found")
                        return False
                except Exception as verify_e:
                    logger.error(f"❌ Error verifying user after duplicate key: {verify_e}")
                    return False
            else:
                logger.error(f"Error ensuring user exists (legacy): {e}")
                return False
    
    async def is_first_time_user(self, telegram_user_id: int) -> bool:
        """Check if this is a first-time user (no commitments, no pod memberships)"""
        try:
            # Get user ID
            user_result = self.supabase.table("users").select("id, total_commitments").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return True  # User doesn't exist = first time
            
            user_data = user_result.data[0]
            user_id = user_data["id"]
            
            # Check if user has any commitments or pod memberships
            has_commitments = user_data["total_commitments"] > 0
            
            pod_membership = self.supabase.table("pod_memberships").select("id").eq("user_id", user_id).limit(1).execute()
            has_pod_membership = len(pod_membership.data) > 0
            
            return not (has_commitments or has_pod_membership)
            
        except Exception as e:
            logger.error(f"Error checking first-time user: {e}")
            return False
    
    async def upgrade_to_paid(self, telegram_user_id: int, payment_amount: float = None) -> bool:
        """Automatically upgrade user to paid status"""
        try:
            success = await self.grant_role(telegram_user_id, "paid")
            if success:
                # Also grant pod_member role if they have a pod membership with payment
                pod_memberships = self.supabase.table("pod_memberships").select("*").eq("user_id", 
                    self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute().data[0]["id"]
                ).execute()
                
                if pod_memberships.data:
                    await self.grant_role(telegram_user_id, "pod_member")
                    
                    # Update pod membership with payment info
                    self.supabase.table("pod_memberships").update({
                        "monthly_payment_active": True,
                        "last_payment_at": datetime.now().isoformat(),
                        "payment_amount": payment_amount
                    }).eq("id", pod_memberships.data[0]["id"]).execute()
                
                logger.info(f"Upgraded user {telegram_user_id} to paid status")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error upgrading user to paid: {e}")
            return False
    
    async def get_user_permissions(self, telegram_user_id: int) -> Dict[str, bool]:
        """Get user's permissions based on their roles"""
        roles = await self.get_user_roles(telegram_user_id)
        
        permissions = {
            # Basic permissions
            "can_create_commitments": True,  # Everyone can do this
            "can_view_commitments": True,
            
            # Paid features
            "can_join_pods": "paid" in roles or "pod_member" in roles,
            "can_access_long_term_goals": "paid" in roles,
            "can_get_ai_insights": "paid" in roles,
            "can_export_data": "paid" in roles,
            
            # Pod member features
            "can_see_pod_members": "pod_member" in roles,
            "can_share_commitments_with_pod": "pod_member" in roles,
            "can_rate_pod_members": "pod_member" in roles,
            
            # Admin features
            "can_view_analytics": "admin" in roles or "super_admin" in roles,
            "can_manage_users": "admin" in roles or "super_admin" in roles,
            "can_manage_pods": "admin" in roles or "super_admin" in roles,
            "can_send_broadcasts": "admin" in roles or "super_admin" in roles,
            
            # Super admin features
            "can_manage_admins": "super_admin" in roles,
            "can_access_financial_data": "super_admin" in roles,
            "can_modify_system_settings": "super_admin" in roles,
            
            # Beta features
            "can_access_beta_features": "beta_tester" in roles or "super_admin" in roles,
        }
        
        return permissions
    
    async def get_role_stats(self) -> Dict[str, int]:
        """Get statistics about user roles"""
        try:
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
            return {}

# Decorators for role-based access control
def require_role(required_role: str):
    """Decorator to require specific role for bot commands"""
    def decorator(func):
        async def wrapper(message, role_manager: UserRoleManager, *args, **kwargs):
            if not await role_manager.user_has_role(message.from_user.id, required_role):
                await message.reply(f"⛔ This feature requires '{required_role}' access.")
                return
            return await func(message, role_manager, *args, **kwargs)
        return wrapper
    return decorator

def require_any_role(required_roles: List[str]):
    """Decorator to require any of the specified roles"""
    def decorator(func):
        async def wrapper(message, role_manager: UserRoleManager, *args, **kwargs):
            if not await role_manager.user_has_any_role(message.from_user.id, required_roles):
                roles_str = "', '".join(required_roles)
                await message.reply(f"⛔ This feature requires one of: '{roles_str}' access.")
                return
            return await func(message, role_manager, *args, **kwargs)
        return wrapper
    return decorator

# Permission checking functions
async def can_user_access_feature(telegram_user_id: int, feature: str, role_manager: UserRoleManager) -> bool:
    """Check if user can access a specific feature"""
    permissions = await role_manager.get_user_permissions(telegram_user_id)
    return permissions.get(feature, False)

# Role management commands for admins
async def admin_grant_role_command(message, role_manager: UserRoleManager, target_user_id: int, role: str):
    """Admin command to grant role to user"""
    if not await role_manager.user_has_any_role(message.from_user.id, ["admin", "super_admin"]):
        await message.reply("⛔ Admin access required.")
        return
    
    success = await role_manager.grant_role(target_user_id, role, granted_by_id=message.from_user.id)
    
    if success:
        await message.reply(f"✅ Granted '{role}' role to user {target_user_id}")
    else:
        await message.reply("❌ Failed to grant role. Check user exists.")

async def admin_revoke_role_command(message, role_manager: UserRoleManager, target_user_id: int, role: str):
    """Admin command to revoke role from user"""
    if not await role_manager.user_has_any_role(message.from_user.id, ["admin", "super_admin"]):
        await message.reply("⛔ Admin access required.")
        return
    
    success = await role_manager.revoke_role(target_user_id, role)
    
    if success:
        await message.reply(f"✅ Revoked '{role}' role from user {target_user_id}")
    else:
        await message.reply("❌ Failed to revoke role.")