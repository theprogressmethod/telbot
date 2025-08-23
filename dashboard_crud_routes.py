#!/usr/bin/env python3
"""
Dashboard CRUD Routes for Week 1 MVP
=====================================
API endpoints for direct database editing from dashboards
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Request/Response Models
class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    
class PodUpdateRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    time_utc: Optional[str] = None
    day_of_week: Optional[int] = None
    timezone: Optional[str] = None
    max_members: Optional[int] = None

class CommitmentUpdateRequest(BaseModel):
    commitment: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None

def create_crud_router(supabase_client, pod_system):
    """Create CRUD router with dependencies"""
    router = APIRouter(prefix="/api/crud", tags=["Dashboard CRUD"])
    
    # USERS CRUD
    @router.get("/users")
    async def get_all_users():
        """Get all users for admin dashboard"""
        try:
            result = supabase_client.table("users").select("*").order("created_at", desc=True).execute()
            return {"success": True, "data": result.data, "count": len(result.data)}
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/users/{user_id}")
    async def get_user(user_id: str):
        """Get specific user by telegram_user_id or UUID with roles"""
        try:
            # Try telegram_user_id first
            if user_id.isdigit():
                result = supabase_client.table("users").select("*").eq("telegram_user_id", int(user_id)).execute()
            else:
                result = supabase_client.table("users").select("*").eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_data = result.data[0]
            
            # Get user roles
            roles_result = supabase_client.table("user_roles").select("role_type, granted_at").eq(
                "user_id", user_data["id"]
            ).eq("is_active", True).execute()
            
            user_data["roles"] = [{"role": role["role_type"], "granted_at": role["granted_at"]} for role in roles_result.data]
            
            return {"success": True, "data": user_data}
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/users/{user_id}")
    async def update_user(user_id: str, user_data: UserUpdateRequest):
        """Update user information"""
        try:
            update_data = user_data.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No data provided for update")
            
            # Try telegram_user_id first
            if user_id.isdigit():
                result = supabase_client.table("users").update(update_data).eq("telegram_user_id", int(user_id)).execute()
            else:
                result = supabase_client.table("users").update(update_data).eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {"success": True, "data": result.data[0], "message": "User updated successfully"}
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # PODS CRUD
    @router.get("/pods")
    async def get_all_pods():
        """Get all pods for admin dashboard"""
        try:
            pods_data = await pod_system.list_all_pods()
            return {"success": True, "data": pods_data, "count": len(pods_data)}
        except Exception as e:
            logger.error(f"Error fetching pods: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/pods/{pod_id}")
    async def get_pod(pod_id: str):
        """Get specific pod by ID"""
        try:
            result = supabase_client.table("pods").select("*").eq("id", pod_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Pod not found")
            
            # Get pod members
            members_result = supabase_client.table("pod_memberships").select(
                "*, users(first_name, telegram_user_id, username)"
            ).eq("pod_id", pod_id).eq("is_active", True).execute()
            
            pod_data = result.data[0]
            pod_data["members"] = members_result.data
            
            return {"success": True, "data": pod_data}
        except Exception as e:
            logger.error(f"Error fetching pod {pod_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/pods/{pod_id}")
    async def update_pod(pod_id: str, pod_data: PodUpdateRequest):
        """Update pod information"""
        try:
            update_data = pod_data.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No data provided for update")
            
            result = supabase_client.table("pods").update(update_data).eq("id", pod_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Pod not found")
            
            return {"success": True, "data": result.data[0], "message": "Pod updated successfully"}
        except Exception as e:
            logger.error(f"Error updating pod {pod_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # COMMITMENTS CRUD
    @router.get("/commitments")
    async def get_all_commitments():
        """Get all commitments for admin dashboard"""
        try:
            result = supabase_client.table("commitments").select(
                "*, users(first_name, telegram_user_id)"
            ).order("created_at", desc=True).limit(100).execute()
            
            return {"success": True, "data": result.data, "count": len(result.data)}
        except Exception as e:
            logger.error(f"Error fetching commitments: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/commitments/user/{user_id}")
    async def get_user_commitments(user_id: str):
        """Get commitments for specific user"""
        try:
            # Convert to telegram_user_id if numeric
            if user_id.isdigit():
                result = supabase_client.table("commitments").select("*").eq("telegram_user_id", int(user_id)).order("created_at", desc=True).execute()
            else:
                # Get user first to get telegram_user_id
                user_result = supabase_client.table("users").select("telegram_user_id").eq("id", user_id).execute()
                if not user_result.data:
                    raise HTTPException(status_code=404, detail="User not found")
                
                telegram_user_id = user_result.data[0]["telegram_user_id"]
                result = supabase_client.table("commitments").select("*").eq("telegram_user_id", telegram_user_id).order("created_at", desc=True).execute()
            
            return {"success": True, "data": result.data, "count": len(result.data)}
        except Exception as e:
            logger.error(f"Error fetching commitments for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/commitments/{commitment_id}")
    async def update_commitment(commitment_id: str, commitment_data: CommitmentUpdateRequest):
        """Update commitment information"""
        try:
            update_data = commitment_data.dict(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No data provided for update")
            
            result = supabase_client.table("commitments").update(update_data).eq("id", commitment_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Commitment not found")
            
            return {"success": True, "data": result.data[0], "message": "Commitment updated successfully"}
        except Exception as e:
            logger.error(f"Error updating commitment {commitment_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # POD MEMBERSHIPS
    @router.post("/pods/{pod_id}/members/{user_id}")
    async def add_user_to_pod(pod_id: str, user_id: str):
        """Add user to pod"""
        try:
            # Get user UUID if telegram_user_id provided
            if user_id.isdigit():
                user_result = supabase_client.table("users").select("id").eq("telegram_user_id", int(user_id)).execute()
                if not user_result.data:
                    raise HTTPException(status_code=404, detail="User not found")
                user_uuid = user_result.data[0]["id"]
            else:
                user_uuid = user_id
            
            # Check if already a member
            existing = supabase_client.table("pod_memberships").select("id").eq("pod_id", pod_id).eq("user_id", user_uuid).eq("is_active", True).execute()
            
            if existing.data:
                return {"success": False, "message": "User is already a member of this pod"}
            
            # Add membership
            result = supabase_client.table("pod_memberships").insert({
                "pod_id": pod_id,
                "user_id": user_uuid,
                "is_active": True
            }).execute()
            
            return {"success": True, "data": result.data[0], "message": "User added to pod successfully"}
        except Exception as e:
            logger.error(f"Error adding user {user_id} to pod {pod_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/pods/{pod_id}/members/{user_id}")
    async def remove_user_from_pod(pod_id: str, user_id: str):
        """Remove user from pod"""
        try:
            # Get user UUID if telegram_user_id provided
            if user_id.isdigit():
                user_result = supabase_client.table("users").select("id").eq("telegram_user_id", int(user_id)).execute()
                if not user_result.data:
                    raise HTTPException(status_code=404, detail="User not found")
                user_uuid = user_result.data[0]["id"]
            else:
                user_uuid = user_id
            
            # Deactivate membership instead of deleting
            result = supabase_client.table("pod_memberships").update({
                "is_active": False
            }).eq("pod_id", pod_id).eq("user_id", user_uuid).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Membership not found")
            
            return {"success": True, "message": "User removed from pod successfully"}
        except Exception as e:
            logger.error(f"Error removing user {user_id} from pod {pod_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # USER ROLES MANAGEMENT
    @router.get("/roles")
    async def get_all_roles():
        """Get all available role types"""
        try:
            # Common role types in the system
            role_types = [
                {"role": "user", "description": "Basic user"},
                {"role": "paid", "description": "Premium user"},
                {"role": "pod_member", "description": "Pod member"},
                {"role": "pod_facilitator", "description": "Pod facilitator"},
                {"role": "admin", "description": "Administrator"},
                {"role": "superadmin", "description": "Super administrator"}
            ]
            return {"success": True, "data": role_types}
        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/users/{user_id}/roles/{role}")
    async def grant_user_role(user_id: str, role: str):
        """Grant a role to a user"""
        try:
            # Get user UUID if telegram_user_id provided
            if user_id.isdigit():
                user_result = supabase_client.table("users").select("id").eq("telegram_user_id", int(user_id)).execute()
                if not user_result.data:
                    raise HTTPException(status_code=404, detail="User not found")
                user_uuid = user_result.data[0]["id"]
            else:
                user_uuid = user_id
            
            # Check if role already exists
            existing = supabase_client.table("user_roles").select("id").eq("user_id", user_uuid).eq("role_type", role).eq("is_active", True).execute()
            
            if existing.data:
                return {"success": False, "message": "User already has this role"}
            
            # Grant role
            from datetime import datetime
            result = supabase_client.table("user_roles").insert({
                "user_id": user_uuid,
                "role_type": role,
                "is_active": True,
                "granted_at": datetime.now().isoformat()
            }).execute()
            
            return {"success": True, "data": result.data[0], "message": f"Role '{role}' granted successfully"}
        except Exception as e:
            logger.error(f"Error granting role {role} to user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/users/{user_id}/roles/{role}")
    async def revoke_user_role(user_id: str, role: str):
        """Revoke a role from a user"""
        try:
            # Get user UUID if telegram_user_id provided
            if user_id.isdigit():
                user_result = supabase_client.table("users").select("id").eq("telegram_user_id", int(user_id)).execute()
                if not user_result.data:
                    raise HTTPException(status_code=404, detail="User not found")
                user_uuid = user_result.data[0]["id"]
            else:
                user_uuid = user_id
            
            # Revoke role (deactivate)
            result = supabase_client.table("user_roles").update({
                "is_active": False
            }).eq("user_id", user_uuid).eq("role_type", role).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Role assignment not found")
            
            return {"success": True, "message": f"Role '{role}' revoked successfully"}
        except Exception as e:
            logger.error(f"Error revoking role {role} from user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router