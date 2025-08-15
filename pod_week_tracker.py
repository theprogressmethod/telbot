# Pod Week Tracking System for The Progress Method
# Ties commitments to pod cycles and tracks progress within pod weeks

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date, time
from supabase import Client
import json

logger = logging.getLogger(__name__)

class PodWeekTracker:
    """Manages pod weeks and tracks commitments within pod cycles"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def create_pod_week_tables(self):
        """Create necessary tables for pod week tracking"""
        try:
            logger.info("✅ Pod week tracking tables already exist in Supabase schema")
            logger.info("Tables: pod_weeks, pod_week_commitments")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pod week tables: {e}")
            return False
    
    async def get_current_pod_week(self, pod_id: str) -> Optional[Dict]:
        """Get the current pod week for a pod"""
        try:
            current_date = date.today()
            
            # Find current week
            result = self.supabase.table("pod_weeks").select("*").eq("pod_id", pod_id).lte("week_start_date", current_date.isoformat()).gte("week_end_date", current_date.isoformat()).execute()
            
            if result.data:
                return result.data[0]
            
            # If no current week, create one
            return await self._create_current_week(pod_id)
            
        except Exception as e:
            logger.error(f"Error getting current pod week: {e}")
            return None
    
    async def _create_current_week(self, pod_id: str) -> Optional[Dict]:
        """Create a new pod week starting today"""
        try:
            # Get pod info
            pod = self.supabase.table("pods").select("*").eq("id", pod_id).execute()
            if not pod.data:
                return None
            
            pod_info = pod.data[0]
            
            # Calculate week dates
            today = date.today()
            
            # Find next week number
            last_week = self.supabase.table("pod_weeks").select("week_number").eq("pod_id", pod_id).order("week_number", desc=True).limit(1).execute()
            
            week_number = (last_week.data[0]["week_number"] + 1) if last_week.data else 1
            
            # Week starts on the pod's meeting day or Monday
            meeting_day = pod_info.get("day_of_week", 1)  # Default to Monday
            days_until_start = (meeting_day - today.weekday()) % 7
            
            week_start = today + timedelta(days=days_until_start)
            if days_until_start == 0 and datetime.now().hour > 12:  # If it's meeting day after noon, start next week
                week_start = today + timedelta(days=7)
                
            week_end = week_start + timedelta(days=6)
            
            # Calculate next meeting time
            meeting_time = pod_info.get("time_utc")
            if meeting_time:
                meeting_datetime = datetime.combine(week_start, datetime.strptime(meeting_time, "%H:%M:%S").time())
            else:
                meeting_datetime = datetime.combine(week_start, time(19, 0))  # Default 7pm
            
            # Create pod week
            pod_week_data = {
                "pod_id": pod_id,
                "week_number": week_number,
                "week_start_date": week_start.isoformat(),
                "week_end_date": week_end.isoformat(),
                "meeting_date": meeting_datetime.isoformat(),
                "theme": f"Pod Week {week_number}",
                "status": "active"
            }
            
            result = self.supabase.table("pod_weeks").insert(pod_week_data).execute()
            
            if result.data:
                logger.info(f"Created new pod week {week_number} for pod {pod_id}")
                return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creating current week: {e}")
            
        return None
    
    async def link_commitment_to_pod_week(self, commitment_id: str, user_id: str, pod_id: str, accountability_level: str = "standard") -> bool:
        """Link a commitment to the current pod week"""
        try:
            # Get current pod week
            pod_week = await self.get_current_pod_week(pod_id)
            if not pod_week:
                return False
            
            # Link commitment to pod week
            link_data = {
                "pod_week_id": pod_week["id"],
                "user_id": user_id,
                "commitment_id": commitment_id,
                "shared_in_pod": True,
                "accountability_level": accountability_level
            }
            
            result = self.supabase.table("pod_week_commitments").insert(link_data).execute()
            
            if result.data:
                logger.info(f"Linked commitment {commitment_id} to pod week {pod_week['week_number']}")
                return True
                
        except Exception as e:
            logger.error(f"Error linking commitment to pod week: {e}")
            
        return False
    
    async def get_pod_week_commitments(self, pod_id: str, week_number: Optional[int] = None) -> List[Dict]:
        """Get all commitments for a pod week"""
        try:
            # Get pod week
            if week_number:
                pod_week_query = self.supabase.table("pod_weeks").select("*").eq("pod_id", pod_id).eq("week_number", week_number)
            else:
                pod_week_query = self.supabase.table("pod_weeks").select("*").eq("pod_id", pod_id).order("week_number", desc=True).limit(1)
            
            pod_week_result = pod_week_query.execute()
            if not pod_week_result.data:
                return []
            
            pod_week = pod_week_result.data[0]
            
            # Get commitments for this week using Supabase joins
            result = self.supabase.table("pod_week_commitments").select("""
                *,
                commitments(commitment, status, smart_score, created_at),
                users(first_name, username)
            """).eq("pod_week_id", pod_week["id"]).order("created_at").execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting pod week commitments: {e}")
            return []
    
    async def get_user_pod_week_summary(self, user_id: str, pod_id: str) -> Dict:
        """Get user's summary for current pod week"""
        try:
            pod_week = await self.get_current_pod_week(pod_id)
            if not pod_week:
                return {}
            
            # Get user's commitments for this week
            user_commitments = self.supabase.table("pod_week_commitments").select("""
                *,
                commitments(commitment, status, smart_score, created_at)
            """).eq("pod_week_id", pod_week["id"]).eq("user_id", user_id).execute()
            
            commitments_data = user_commitments.data if user_commitments.data else []
            
            total_commitments = len(commitments_data)
            completed_commitments = len([c for c in commitments_data if c["commitments"]["status"] == "completed"])
            
            # Calculate days until meeting
            meeting_date = datetime.fromisoformat(pod_week["meeting_date"].replace("Z", "+00:00"))
            days_until_meeting = (meeting_date.date() - date.today()).days
            
            return {
                "pod_week": pod_week,
                "user_commitments": commitments_data,
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "completion_rate": (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0,
                "days_until_meeting": max(0, days_until_meeting),
                "meeting_date": meeting_date,
                "week_progress": min(100, ((7 - days_until_meeting) / 7) * 100) if days_until_meeting >= 0 else 100
            }
            
        except Exception as e:
            logger.error(f"Error getting user pod week summary: {e}")
            return {}
    
    async def get_pod_week_leaderboard(self, pod_id: str, week_number: Optional[int] = None) -> List[Dict]:
        """Get leaderboard for pod week"""
        try:
            pod_week = await self.get_current_pod_week(pod_id) if not week_number else None
            if not pod_week and not week_number:
                return []
            
            # Get all users' performance for this week
            if week_number:
                pod_week_query = self.supabase.table("pod_weeks").select("id").eq("pod_id", pod_id).eq("week_number", week_number)
            else:
                pod_week_query = self.supabase.table("pod_weeks").select("id").eq("pod_id", pod_id).order("week_number", desc=True).limit(1)
            
            pod_week_result = pod_week_query.execute()
            if not pod_week_result.data:
                return []
            
            pod_week_id = pod_week_result.data[0]["id"]
            
            # Get pod week commitments with user and commitment data
            commitments_result = self.supabase.table("pod_week_commitments").select("""
                *,
                users(first_name, username, id),
                commitments(status, smart_score)
            """).eq("pod_week_id", pod_week_id).execute()
            
            # Aggregate user performance
            user_stats = {}
            for commitment in commitments_result.data:
                user_id = commitment["user_id"]
                user_data = commitment["users"]
                commit_data = commitment["commitments"]
                
                if user_id not in user_stats:
                    user_stats[user_id] = {
                        "first_name": user_data["first_name"],
                        "username": user_data["username"],
                        "total_commitments": 0,
                        "completed_commitments": 0,
                        "smart_scores": []
                    }
                
                user_stats[user_id]["total_commitments"] += 1
                if commit_data["status"] == "completed":
                    user_stats[user_id]["completed_commitments"] += 1
                if commit_data["smart_score"]:
                    user_stats[user_id]["smart_scores"].append(commit_data["smart_score"])
            
            # Calculate scores and rankings
            leaderboard = []
            for i, (user_id, stats) in enumerate(sorted(user_stats.items(), 
                key=lambda x: (x[1]["completed_commitments"], sum(x[1]["smart_scores"])/len(x[1]["smart_scores"]) if x[1]["smart_scores"] else 0), 
                reverse=True)):
                
                completion_rate = (stats["completed_commitments"] / stats["total_commitments"]) * 100 if stats["total_commitments"] > 0 else 0
                avg_score = sum(stats["smart_scores"]) / len(stats["smart_scores"]) if stats["smart_scores"] else 0
                
                leaderboard.append({
                    "rank": i + 1,
                    "user_name": stats["first_name"],
                    "username": stats["username"],
                    "total_commitments": stats["total_commitments"],
                    "completed_commitments": stats["completed_commitments"],
                    "completion_rate": round(completion_rate, 1),
                    "avg_quality": round(avg_score, 1),
                    "emoji": self._get_rank_emoji(i + 1)
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting pod week leaderboard: {e}")
            return []
    
    def _get_rank_emoji(self, rank: int) -> str:
        """Get emoji for rank"""
        if rank == 1:
            return "🏆"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return "📊"
    
    async def format_pod_week_summary(self, user_id: str, pod_id: str) -> str:
        """Format pod week summary for user"""
        try:
            summary = await self.get_user_pod_week_summary(user_id, pod_id)
            if not summary:
                return "No active pod week found."
            
            pod_week = summary["pod_week"]
            meeting_date = summary["meeting_date"]
            
            message = f"""
🎯 **Pod Week {pod_week['week_number']} Progress**

**Your Stats This Week:**
✅ {summary['completed_commitments']}/{summary['total_commitments']} completed ({summary['completion_rate']:.1f}%)
📈 Week Progress: {summary['week_progress']:.0f}%

**Next Meeting:**
📅 {meeting_date.strftime('%A, %B %d at %I:%M %p')}
⏰ {summary['days_until_meeting']} days away

**This Week's Commitments:**
"""
            
            for i, commitment in enumerate(summary['user_commitments'], 1):
                c = commitment['commitments']
                status_emoji = "✅" if c['status'] == 'completed' else "⏳"
                message += f"{i}. {status_emoji} {c['commitment']}\n"
            
            if summary['days_until_meeting'] <= 1:
                message += f"\n🔥 **Meeting is {'today' if summary['days_until_meeting'] == 0 else 'tomorrow'}!** Get those commitments done!"
            elif summary['completion_rate'] >= 80:
                message += f"\n⭐ **You're crushing it!** Keep up the momentum!"
            elif summary['total_commitments'] == 0:
                message += f"\n💡 **Add some commitments for this pod week!** Use `/commit` and I'll track them."
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting pod week summary: {e}")
            return "Error generating pod week summary."
    
