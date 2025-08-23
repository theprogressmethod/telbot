"""
BASIC POD SYSTEM FOR 1.0 LAUNCH
================================
Simple pod management for Week 1 MVP
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json

logger = logging.getLogger(__name__)

class BasicPodSystem:
    """Basic pod system for 1.0 launch - admin managed pods with core features"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
    # ADMIN FUNCTIONS
    async def create_pod(self, pod_name: str, meeting_time: str, meeting_day: int, 
                         created_by_id: int, meeting_link: str = None) -> Dict[str, Any]:
        """Create a new pod (admin only)"""
        try:
            pod_data = {
                "name": pod_name,
                "day_of_week": meeting_day,  # 0=Monday, 6=Sunday
                "time_utc": meeting_time,  # Format: "19:00:00"
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("pods").insert(pod_data).execute()
            
            if result.data:
                logger.info(f"✅ Created pod '{pod_name}'")
                return {"success": True, "pod": result.data[0]}
            else:
                return {"success": False, "error": "Failed to create pod"}
                
        except Exception as e:
            logger.error(f"❌ Error creating pod: {e}")
            return {"success": False, "error": str(e)}
    
    async def assign_user_to_pod(self, telegram_user_id: int, pod_id: str, 
                                 assigned_by_id: int) -> Dict[str, Any]:
        """Assign a user to a pod (admin only)"""
        try:
            # Get user UUID
            user_result = self.supabase.table("users").select("id").eq(
                "telegram_user_id", telegram_user_id
            ).execute()
            
            if not user_result.data:
                return {"success": False, "error": "User not found"}
                
            user_uuid = user_result.data[0]["id"]
            
            # Check if already in a pod
            existing = self.supabase.table("pod_memberships").select("*").eq(
                "user_id", user_uuid
            ).eq("is_active", True).execute()
            
            if existing.data:
                return {"success": False, "error": "User already in a pod"}
            
            # Check pod exists
            pod_info = self.supabase.table("pods").select("*").eq("id", pod_id).execute()
            if not pod_info.data:
                return {"success": False, "error": "Pod not found"}
                
            pod = pod_info.data[0]
            
            # Add to pod (simplified - no member limits for now)
            member_data = {
                "pod_id": pod_id,
                "user_id": user_uuid,
                "is_active": True,
                "joined_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("pod_memberships").insert(member_data).execute()
            
            if result.data:
                # Grant pod_member role
                try:
                    self.supabase.table("user_roles").insert({
                        "user_id": user_uuid,
                        "role_type": "pod_member",
                        "granted_at": datetime.now().isoformat(),
                        "granted_by": user_uuid,  # Self-granted for now
                        "is_active": True
                    }).execute()
                except:
                    pass  # Role might already exist
                
                logger.info(f"✅ Added user {telegram_user_id} to pod {pod_id}")
                return {"success": True, "pod_name": pod["name"]}
            else:
                return {"success": False, "error": "Failed to add user to pod"}
                
        except Exception as e:
            logger.error(f"❌ Error assigning user to pod: {e}")
            return {"success": False, "error": str(e)}
    
    async def remove_user_from_pod(self, telegram_user_id: int, removed_by_id: int) -> Dict[str, Any]:
        """Remove a user from their pod (admin only)"""
        try:
            # Get user's pod membership
            member_result = self.supabase.table("pod_memberships").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "active").execute()
            
            if not member_result.data:
                return {"success": False, "error": "User not in a pod"}
            
            membership = member_result.data[0]
            pod_id = membership["pod_id"]
            
            # Update membership status
            self.supabase.table("pod_memberships").update({
                "status": "removed",
                "removed_at": datetime.now().isoformat(),
                "removed_by": removed_by_id
            }).eq("id", membership["id"]).execute()
            
            # Update pod member count
            pod_info = self.supabase.table("pods").select("*").eq("id", pod_id).execute()
            if pod_info.data:
                self.supabase.table("pods").update({
                    "current_members": max(0, pod_info.data[0]["current_members"] - 1)
                }).eq("id", pod_id).execute()
            
            logger.info(f"✅ Removed user {telegram_user_id} from pod")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Error removing user from pod: {e}")
            return {"success": False, "error": str(e)}
    
    # USER FUNCTIONS
    async def get_user_pod(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's pod information"""
        try:
            # Get user UUID first
            user_result = self.supabase.table("users").select("id").eq(
                "telegram_user_id", telegram_user_id
            ).execute()
            
            if not user_result.data:
                return None
                
            user_uuid = user_result.data[0]["id"]
            
            # Get user's active pod membership
            member_result = self.supabase.table("pod_memberships").select(
                "*, pods(*)"
            ).eq("user_id", user_uuid).eq("is_active", True).execute()
            
            if not member_result.data:
                return None
                
            membership = member_result.data[0]
            pod = membership["pods"]
            
            # Get pod members
            members_result = self.supabase.table("pod_memberships").select(
                "*, users(telegram_user_id, username, first_name)"
            ).eq("pod_id", pod["id"]).eq("is_active", True).execute()
            
            # Format member list with completion rates
            members = []
            for member in members_result.data:
                user_info = member["users"]
                
                # Get this week's stats for member
                week_stats = await self._get_member_week_stats(user_info["telegram_user_id"])
                
                members.append({
                    "name": user_info["first_name"] or user_info["username"] or "Anonymous",
                    "telegram_user_id": user_info["telegram_user_id"],
                    "role": "member",  # Default role
                    "week_completion_rate": week_stats["completion_rate"],
                    "week_commitments": week_stats["total"]
                })
            
            # Sort by completion rate
            members.sort(key=lambda x: x["week_completion_rate"], reverse=True)
            
            return {
                "pod_id": pod["id"],
                "pod_name": pod["name"],
                "meeting_day": pod["day_of_week"],
                "meeting_time": pod["time_utc"],
                "meeting_link": f"https://meet.google.com/{pod['name'].lower().replace(' ', '-')}",
                "members": members,
                "total_members": len(members),
                "max_members": 6  # Default
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user pod: {e}")
            return None
    
    async def get_pod_leaderboard(self, pod_id: str) -> List[Dict[str, Any]]:
        """Get pod leaderboard for current week"""
        try:
            # Get pod members
            members_result = self.supabase.table("pod_memberships").select(
                "*, users(telegram_user_id, username, first_name)"
            ).eq("pod_id", pod_id).eq("is_active", True).execute()
            
            if not members_result.data:
                return []
            
            leaderboard = []
            
            for member in members_result.data:
                user_info = member["users"]
                telegram_user_id = user_info["telegram_user_id"]
                
                # Get week stats
                week_stats = await self._get_member_week_stats(telegram_user_id)
                
                leaderboard.append({
                    "rank": 0,  # Will be set after sorting
                    "name": user_info["first_name"] or user_info["username"] or "Anonymous",
                    "telegram_user_id": telegram_user_id,
                    "week_completed": week_stats["completed"],
                    "week_total": week_stats["total"],
                    "completion_rate": week_stats["completion_rate"],
                    "points": week_stats["completed"] * 10  # Simple point system
                })
            
            # Sort by points (completed commitments)
            leaderboard.sort(key=lambda x: (x["points"], x["completion_rate"]), reverse=True)
            
            # Assign ranks
            for i, member in enumerate(leaderboard, 1):
                member["rank"] = i
                # Add emoji for top 3
                if i == 1:
                    member["emoji"] = "🥇"
                elif i == 2:
                    member["emoji"] = "🥈"
                elif i == 3:
                    member["emoji"] = "🥉"
                else:
                    member["emoji"] = "🎯"
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"❌ Error getting pod leaderboard: {e}")
            return []
    
    async def send_pod_announcement(self, pod_id: str, message: str, sender_id: int) -> Dict[str, Any]:
        """Send announcement to all pod members"""
        try:
            # Store announcement
            announcement_data = {
                "pod_id": pod_id,
                "message": message,
                "sender_telegram_id": sender_id,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("pod_announcements").insert(announcement_data).execute()
            
            if result.data:
                # Get all pod members
                members = self.supabase.table("pod_memberships").select(
                    "telegram_user_id"
                ).eq("pod_id", pod_id).eq("status", "active").execute()
                
                member_ids = [m["telegram_user_id"] for m in members.data] if members.data else []
                
                logger.info(f"✅ Pod announcement created for {len(member_ids)} members")
                return {
                    "success": True,
                    "announcement_id": result.data[0]["id"],
                    "recipient_ids": member_ids
                }
            else:
                return {"success": False, "error": "Failed to create announcement"}
                
        except Exception as e:
            logger.error(f"❌ Error sending pod announcement: {e}")
            return {"success": False, "error": str(e)}
    
    # HELPER FUNCTIONS
    async def _get_member_week_stats(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get member's statistics for current week"""
        try:
            from datetime import date, timedelta
            
            # Get start of current week (Monday)
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_start_str = week_start.isoformat()
            
            # Get all commitments created this week
            week_result = self.supabase.table("commitments").select("*").eq(
                "telegram_user_id", telegram_user_id
            ).gte("created_at", week_start_str).execute()
            
            week_total = len(week_result.data) if week_result.data else 0
            week_completed = sum(1 for c in week_result.data if c.get("status") == "completed") if week_result.data else 0
            completion_rate = round((week_completed / week_total * 100) if week_total > 0 else 0, 1)
            
            return {
                "total": week_total,
                "completed": week_completed,
                "completion_rate": completion_rate
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting member week stats: {e}")
            return {"total": 0, "completed": 0, "completion_rate": 0}
    
    async def list_all_pods(self) -> List[Dict[str, Any]]:
        """List all active pods (admin function)"""
        try:
            result = self.supabase.table("pods").select("*").eq("status", "active").execute()
            
            pods = []
            for pod in result.data if result.data else []:
                # Count members for this pod
                members_count = self.supabase.table("pod_memberships").select("count", count="exact").eq(
                    "pod_id", pod["id"]
                ).eq("is_active", True).execute()
                
                current_members = members_count.count or 0
                max_members = 6  # Default
                
                pods.append({
                    "id": pod["id"],
                    "name": pod["name"],
                    "members": f"{current_members}/{max_members}",
                    "meeting": f"{self._day_name(pod['day_of_week'])} at {pod['time_utc']}",
                    "status": "Full" if current_members >= max_members else "Open"
                })
            
            return pods
            
        except Exception as e:
            logger.error(f"❌ Error listing pods: {e}")
            return []
    
    def _day_name(self, day_num: int) -> str:
        """Convert day number to name"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[day_num] if 0 <= day_num <= 6 else "Unknown"
    
    async def get_pod_stats(self, pod_id: str) -> Dict[str, Any]:
        """Get comprehensive pod statistics"""
        try:
            # Get pod info
            pod_result = self.supabase.table("pods").select("*").eq("id", pod_id).execute()
            if not pod_result.data:
                return {}
            
            pod = pod_result.data[0]
            
            # Get members
            members_result = self.supabase.table("pod_memberships").select("*").eq(
                "pod_id", pod_id
            ).eq("status", "active").execute()
            
            member_count = len(members_result.data) if members_result.data else 0
            
            # Calculate pod-wide stats
            total_commitments = 0
            total_completed = 0
            
            for member in members_result.data if members_result.data else []:
                stats = await self._get_member_week_stats(member["telegram_user_id"])
                total_commitments += stats["total"]
                total_completed += stats["completed"]
            
            pod_completion_rate = round(
                (total_completed / total_commitments * 100) if total_commitments > 0 else 0, 
                1
            )
            
            return {
                "pod_name": pod["name"],
                "member_count": member_count,
                "max_members": pod["max_members"],
                "week_commitments": total_commitments,
                "week_completed": total_completed,
                "pod_completion_rate": pod_completion_rate,
                "meeting_day": self._day_name(pod["day_of_week"]),
                "meeting_time": pod["time_utc"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting pod stats: {e}")
            return {}