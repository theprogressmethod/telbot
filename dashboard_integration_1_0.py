#!/usr/bin/env python3
"""
DASHBOARD INTEGRATION FOR 1.0 LAUNCH
=====================================
Integrates existing dashboards with main.py for Week 1 MVP
Provides admin and user dashboard functionality
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from fastapi import HTTPException
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

# Import our dashboard generators
from unified_admin_dashboard import get_unified_admin_html
from retro_evolved_dashboard import get_evolved_superadmin_html
from user_dashboard_template import get_user_dashboard_html

class DashboardIntegration:
    """Handles dashboard integration for 1.0 launch"""
    
    def __init__(self, supabase_client, role_manager, pod_system):
        self.supabase = supabase_client
        self.role_manager = role_manager
        self.pod_system = pod_system
        
    async def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """Get data for admin dashboard"""
        try:
            # Get user statistics
            users_result = self.supabase.table("users").select("*").execute()
            total_users = len(users_result.data) if users_result.data else 0
            
            # Get commitment statistics
            commitments_result = self.supabase.table("commitments").select("*").execute()
            total_commitments = len(commitments_result.data) if commitments_result.data else 0
            completed_commitments = sum(1 for c in commitments_result.data if c.get("status") == "completed") if commitments_result.data else 0
            
            # Get pod statistics
            pods_result = self.supabase.table("pods").select("*").eq("status", "active").execute()
            total_pods = len(pods_result.data) if pods_result.data else 0
            
            # Get pod memberships
            members_result = self.supabase.table("pod_memberships").select("*").eq("is_active", True).execute()
            total_pod_members = len(members_result.data) if members_result.data else 0
            
            # Calculate completion rate
            completion_rate = round((completed_commitments / total_commitments * 100) if total_commitments > 0 else 0, 1)
            
            return {
                "total_users": total_users,
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "completion_rate": completion_rate,
                "total_pods": total_pods,
                "total_pod_members": total_pod_members,
                "active_users_today": await self._get_active_users_today(),
                "recent_users": await self._get_recent_users(),
                "pod_list": await self._get_pod_list(),
                "system_health": "healthy",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting admin data: {e}")
    
    async def get_user_dashboard_data(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get data for user dashboard"""
        try:
            # Get user info
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            if not user_result.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            user = user_result.data[0]
            
            # Get user commitments
            commitments_result = self.supabase.table("commitments").select("*").eq("telegram_user_id", telegram_user_id).execute()
            commitments = commitments_result.data if commitments_result.data else []
            
            total_commitments = len(commitments)
            completed_commitments = sum(1 for c in commitments if c.get("status") == "completed")
            active_commitments = sum(1 for c in commitments if c.get("status") == "active")
            completion_rate = round((completed_commitments / total_commitments * 100) if total_commitments > 0 else 0, 1)
            
            # Get pod info
            pod_info = await self.pod_system.get_user_pod(telegram_user_id)
            
            return {
                "user_name": user.get("first_name", "User"),
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "active_commitments": active_commitments,
                "completion_rate": completion_rate,
                "current_streak": await self._get_user_streak(telegram_user_id),
                "pod_info": pod_info,
                "recent_commitments": commitments[-5:] if commitments else [],
                "achievements": await self._get_user_achievements(telegram_user_id),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user data: {e}")
    
    async def render_admin_dashboard(self) -> HTMLResponse:
        """Render the admin dashboard"""
        try:
            # Get admin data
            admin_data = await self.get_admin_dashboard_data()
            
            # Get real users for dropdown
            real_users = await self._get_real_users_for_dropdown()
            
            # Get real pods for dropdown  
            real_pods = await self._get_real_pods_for_dropdown()
            
            # Debug logging
            logger.info(f"🔍 Data for injection - Users: {len(real_users)}, Pods: {len(real_pods)}")
            logger.info(f"📋 Real users sample: {real_users[:2] if real_users else 'None'}")
            logger.info(f"🏠 Real pods sample: {real_pods[:2] if real_pods else 'None'}")
            
            # For now, use the existing unified admin HTML
            # In a full implementation, we'd inject the data into the HTML template
            html_content = get_unified_admin_html()
            
            # Simple data injection (in production, use proper templating)
            import json
            html_content = html_content.replace(
                "<!-- ADMIN_DATA_PLACEHOLDER -->", 
                f"""
                <script>
                window.adminData = {json.dumps(admin_data)};
                window.realUsers = {json.dumps(real_users)};
                window.realPods = {json.dumps(real_pods)};
                console.log('Admin data loaded:', window.adminData);
                console.log('Real users loaded:', window.realUsers);
                console.log('Real pods loaded:', window.realPods);
                </script>
                """
            )
            
            return HTMLResponse(content=html_content)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error rendering admin dashboard: {e}")
    
    async def render_user_dashboard(self, telegram_user_id: int) -> HTMLResponse:
        """Render the user dashboard"""
        try:
            # Get user data
            user_data = await self.get_user_dashboard_data(telegram_user_id)
            
            # Use the personalized user dashboard template
            html_content = get_user_dashboard_html(user_data)
            
            return HTMLResponse(content=html_content)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error rendering user dashboard: {e}")
    
    # Helper methods
    async def _get_active_users_today(self) -> int:
        """Get count of users active today"""
        try:
            from datetime import date
            today = date.today().isoformat()
            
            result = self.supabase.table("users").select("count", count="exact").gte(
                "last_activity_at", today
            ).execute()
            
            return result.count or 0
        except:
            return 0
    
    async def _get_recent_users(self) -> List[Dict[str, Any]]:
        """Get recently joined users"""
        try:
            result = self.supabase.table("users").select(
                "first_name, telegram_user_id, created_at"
            ).order("created_at", desc=True).limit(10).execute()
            
            return result.data if result.data else []
        except:
            return []
    
    async def _get_pod_list(self) -> List[Dict[str, Any]]:
        """Get list of pods for admin"""
        try:
            return await self.pod_system.list_all_pods()
        except:
            return []
    
    async def _get_user_streak(self, telegram_user_id: int) -> int:
        """Get user's current streak"""
        try:
            # Simple implementation - could be enhanced
            result = self.supabase.table("commitments").select("completed_at").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "completed").order("completed_at", desc=True).limit(7).execute()
            
            if not result.data:
                return 0
            
            # Simple streak calculation
            streak = 0
            from datetime import datetime, timedelta
            
            current_date = datetime.now().date()
            
            for commitment in result.data:
                if commitment.get("completed_at"):
                    completed_date = datetime.fromisoformat(commitment["completed_at"].replace('Z', '+00:00')).date()
                    expected_date = current_date - timedelta(days=streak)
                    
                    if completed_date == expected_date:
                        streak += 1
                    else:
                        break
            
            return streak
        except:
            return 0
    
    async def _get_user_achievements(self, telegram_user_id: int) -> List[str]:
        """Get user achievements"""
        try:
            achievements = []
            
            # Get commitment count
            result = self.supabase.table("commitments").select("count", count="exact").eq(
                "telegram_user_id", telegram_user_id
            ).eq("status", "completed").execute()
            
            completed_count = result.count or 0
            
            # Simple achievement system
            if completed_count >= 1:
                achievements.append("🎯 First Commitment")
            if completed_count >= 10:
                achievements.append("🔟 Ten Strong")  
            if completed_count >= 50:
                achievements.append("💪 Half Century")
            if completed_count >= 100:
                achievements.append("🎖️ Centurion")
            
            # Check for pod membership
            pod_info = await self.pod_system.get_user_pod(telegram_user_id)
            if pod_info:
                achievements.append("🤝 Pod Member")
            
            return achievements
        except:
            return []
    
    async def _get_real_users_for_dropdown(self) -> List[Dict[str, Any]]:
        """Get real users from database for dropdown"""
        try:
            result = self.supabase.table("users").select(
                "first_name, telegram_user_id, created_at"
            ).not_.is_("telegram_user_id", "null").order(
                "created_at", desc=True
            ).limit(10).execute()
            
            users = []
            for user in result.data:
                users.append({
                    "name": user.get("first_name", "Unknown"),
                    "telegram_user_id": user.get("telegram_user_id"),
                    "created_at": user.get("created_at", "")[:10]
                })
            
            return users
        except Exception as e:
            logger.error(f"Error getting real users: {e}")
            return []
    
    async def _get_real_pods_for_dropdown(self) -> List[Dict[str, Any]]:
        """Get real pods from database for dropdown"""
        try:
            pods_data = await self.pod_system.list_all_pods()
            return pods_data[:10]  # Limit to 10 for dropdown
        except Exception as e:
            logger.error(f"Error getting real pods: {e}")
            return []

# Global instance for use in main.py
dashboard_integration = None

async def initialize_dashboard_integration(supabase, role_manager, pod_system):
    """Initialize the dashboard integration system"""
    global dashboard_integration
    dashboard_integration = DashboardIntegration(supabase, role_manager, pod_system)
    return dashboard_integration

def get_dashboard_integration():
    """Get the dashboard integration instance"""
    return dashboard_integration