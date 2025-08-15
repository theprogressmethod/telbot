# Google Meet Attendance Tracking for The Progress Method
# Tracks pod member attendance at weekly Google Meet calls

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta, date
from supabase import Client
import json
import re
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class GoogleMeetTracker:
    """Tracks Google Meet attendance for pod calls"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def create_attendance_tables(self):
        """Create attendance tracking tables"""
        try:
            logger.info("✅ Google Meet attendance tables ready for creation")
            logger.info("Tables: pod_meetings, meeting_attendance")
            return True
        except Exception as e:
            logger.error(f"Error creating attendance tables: {e}")
            return False
    
    async def log_attendance(self, pod_id: str, user_id: str, meeting_date: datetime, 
                           joined_at: datetime, left_at: Optional[datetime] = None, 
                           duration_minutes: Optional[int] = None) -> bool:
        """Log user attendance for a pod meeting"""
        try:
            # Get or create meeting record
            meeting = await self._get_or_create_meeting(pod_id, meeting_date)
            if not meeting:
                return False
            
            # Calculate duration if not provided
            if left_at and not duration_minutes:
                duration = left_at - joined_at
                duration_minutes = int(duration.total_seconds() / 60)
            
            # Record attendance
            attendance_data = {
                "meeting_id": meeting["id"],
                "user_id": user_id,
                "joined_at": joined_at.isoformat(),
                "left_at": left_at.isoformat() if left_at else None,
                "duration_minutes": duration_minutes or 0,
                "was_present": True,
                "attendance_quality": self._calculate_attendance_quality(duration_minutes or 0)
            }
            
            # Use upsert to handle duplicate entries
            result = self.supabase.table("meeting_attendance").upsert(
                attendance_data, 
                on_conflict="meeting_id,user_id"
            ).execute()
            
            if result.data:
                logger.info(f"✅ Logged attendance for user {user_id} at meeting {meeting['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Error logging attendance: {e}")
            
        return False
    
    async def _get_or_create_meeting(self, pod_id: str, meeting_date: datetime) -> Optional[Dict]:
        """Get existing meeting or create new one"""
        try:
            # Check if meeting exists for this date
            meeting_date_str = meeting_date.date().isoformat()
            
            result = self.supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).eq("meeting_date", meeting_date_str).execute()
            
            if result.data:
                return result.data[0]
            
            # Create new meeting
            meeting_data = {
                "pod_id": pod_id,
                "meeting_date": meeting_date_str,
                "scheduled_start_time": meeting_date.isoformat(),
                "actual_start_time": meeting_date.isoformat(),
                "meeting_type": "weekly_pod_call",
                "status": "completed"
            }
            
            create_result = self.supabase.table("pod_meetings").insert(meeting_data).execute()
            
            if create_result.data:
                return create_result.data[0]
                
        except Exception as e:
            logger.error(f"Error getting/creating meeting: {e}")
            
        return None
    
    def _calculate_attendance_quality(self, duration_minutes: int) -> str:
        """Calculate attendance quality based on duration"""
        if duration_minutes >= 45:
            return "excellent"  # Full meeting
        elif duration_minutes >= 30:
            return "good"       # Most of meeting
        elif duration_minutes >= 15:
            return "partial"    # Some participation
        else:
            return "brief"      # Very short
    
    async def get_pod_attendance_stats(self, pod_id: str, weeks_back: int = 4) -> Dict:
        """Get attendance statistics for a pod"""
        try:
            # Get recent meetings
            cutoff_date = (date.today() - timedelta(weeks=weeks_back)).isoformat()
            
            meetings = self.supabase.table("pod_meetings").select("""
                *,
                meeting_attendance(
                    user_id,
                    duration_minutes,
                    attendance_quality,
                    users(first_name, username)
                )
            """).eq("pod_id", pod_id).gte("meeting_date", cutoff_date).order("meeting_date", desc=True).execute()
            
            if not meetings.data:
                return {"total_meetings": 0, "member_stats": [], "attendance_trend": "stable"}
            
            # Calculate stats
            total_meetings = len(meetings.data)
            member_attendance = {}
            
            for meeting in meetings.data:
                for attendance in meeting.get("meeting_attendance", []):
                    user_id = attendance["user_id"]
                    user_data = attendance["users"]
                    
                    if user_id not in member_attendance:
                        member_attendance[user_id] = {
                            "name": user_data["first_name"],
                            "username": user_data["username"],
                            "meetings_attended": 0,
                            "total_duration": 0,
                            "quality_scores": []
                        }
                    
                    member_attendance[user_id]["meetings_attended"] += 1
                    member_attendance[user_id]["total_duration"] += attendance["duration_minutes"]
                    member_attendance[user_id]["quality_scores"].append(attendance["attendance_quality"])
            
            # Format member stats
            member_stats = []
            for user_id, stats in member_attendance.items():
                attendance_rate = (stats["meetings_attended"] / total_meetings) * 100
                avg_duration = stats["total_duration"] / stats["meetings_attended"] if stats["meetings_attended"] > 0 else 0
                
                member_stats.append({
                    "name": stats["name"],
                    "username": stats["username"],
                    "attendance_rate": round(attendance_rate, 1),
                    "meetings_attended": stats["meetings_attended"],
                    "total_meetings": total_meetings,
                    "avg_duration_minutes": round(avg_duration, 1),
                    "engagement_level": self._get_engagement_level(attendance_rate, avg_duration),
                    "trend_emoji": self._get_attendance_emoji(attendance_rate)
                })
            
            # Sort by attendance rate
            member_stats.sort(key=lambda x: x["attendance_rate"], reverse=True)
            
            return {
                "total_meetings": total_meetings,
                "member_stats": member_stats,
                "weeks_analyzed": weeks_back,
                "attendance_trend": self._calculate_attendance_trend(meetings.data)
            }
            
        except Exception as e:
            logger.error(f"Error getting pod attendance stats: {e}")
            return {"total_meetings": 0, "member_stats": [], "attendance_trend": "unknown"}
    
    def _get_engagement_level(self, attendance_rate: float, avg_duration: float) -> str:
        """Determine engagement level based on attendance and duration"""
        if attendance_rate >= 90 and avg_duration >= 40:
            return "🔥 Highly Engaged"
        elif attendance_rate >= 75 and avg_duration >= 30:
            return "⭐ Engaged" 
        elif attendance_rate >= 50:
            return "📈 Developing"
        else:
            return "💪 Needs Support"
    
    def _get_attendance_emoji(self, rate: float) -> str:
        """Get emoji for attendance rate"""
        if rate >= 90:
            return "🏆"
        elif rate >= 75:
            return "⭐"
        elif rate >= 50:
            return "📊"
        else:
            return "⚠️"
    
    def _calculate_attendance_trend(self, meetings: List[Dict]) -> str:
        """Calculate if attendance is improving or declining"""
        if len(meetings) < 2:
            return "stable"
        
        # Compare first half vs second half of meetings
        mid_point = len(meetings) // 2
        recent_meetings = meetings[:mid_point]
        older_meetings = meetings[mid_point:]
        
        recent_avg_attendance = sum(len(m.get("meeting_attendance", [])) for m in recent_meetings) / len(recent_meetings)
        older_avg_attendance = sum(len(m.get("meeting_attendance", [])) for m in older_meetings) / len(older_meetings)
        
        if recent_avg_attendance > older_avg_attendance * 1.1:
            return "improving"
        elif recent_avg_attendance < older_avg_attendance * 0.9:
            return "declining"
        else:
            return "stable"
    
    async def format_attendance_summary(self, pod_id: str, user_id: Optional[str] = None) -> str:
        """Format attendance summary for display"""
        try:
            stats = await self.get_pod_attendance_stats(pod_id)
            
            if stats["total_meetings"] == 0:
                return "📊 **Pod Attendance Summary**\n\nNo meetings recorded yet. Start tracking attendance with Google Meet integration!"
            
            message = f"""📊 **Pod Attendance Summary** ({stats['weeks_analyzed']} weeks)

📈 **Overall Stats:**
Total Meetings: {stats['total_meetings']}
Trend: {stats['attendance_trend'].title()}

👥 **Member Attendance:**
"""
            
            # Show specific user if requested
            if user_id:
                user_stats = next((s for s in stats["member_stats"] if user_id in s.get("username", "")), None)
                if user_stats:
                    message += f"""
🎯 **Your Attendance:**
{user_stats['trend_emoji']} {user_stats['attendance_rate']}% rate ({user_stats['meetings_attended']}/{user_stats['total_meetings']})
⏱️ Avg Duration: {user_stats['avg_duration_minutes']} min
📊 {user_stats['engagement_level']}
"""
                else:
                    message += "\n❓ Your attendance data not found."
            else:
                # Show top performers
                for i, member in enumerate(stats["member_stats"][:5]):
                    rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i] if i < 5 else "📊"
                    message += f"{rank_emoji} {member['name']}: {member['attendance_rate']}% ({member['meetings_attended']}/{member['total_meetings']})\n"
            
            # Add motivational message based on trend
            if stats["attendance_trend"] == "improving":
                message += f"\n🚀 **Attendance is improving!** Keep building that momentum!"
            elif stats["attendance_trend"] == "declining":
                message += f"\n💪 **Let's boost attendance!** Every meeting matters for your pod's success."
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting attendance summary: {e}")
            return "Error generating attendance summary."
    
    async def manually_record_attendance(self, pod_id: str, user_id: str, meeting_date: str, 
                                       attended: bool, duration_minutes: int = 60) -> bool:
        """Manually record attendance for a meeting"""
        try:
            meeting_datetime = datetime.fromisoformat(meeting_date)
            
            if attended:
                joined_at = meeting_datetime
                left_at = meeting_datetime + timedelta(minutes=duration_minutes)
                return await self.log_attendance(pod_id, user_id, meeting_datetime, joined_at, left_at, duration_minutes)
            else:
                # Log as absent
                meeting = await self._get_or_create_meeting(pod_id, meeting_datetime)
                if meeting:
                    attendance_data = {
                        "meeting_id": meeting["id"],
                        "user_id": user_id,
                        "joined_at": None,
                        "left_at": None,
                        "duration_minutes": 0,
                        "was_present": False,
                        "attendance_quality": "absent"
                    }
                    
                    result = self.supabase.table("meeting_attendance").upsert(
                        attendance_data, 
                        on_conflict="meeting_id,user_id"
                    ).execute()
                    
                    return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error manually recording attendance: {e}")
            
        return False
    
    async def get_user_attendance_streak(self, user_id: str, pod_id: str) -> Dict:
        """Get user's meeting attendance streak"""
        try:
            # Get user's attendance history for this pod
            attendance_result = self.supabase.table("meeting_attendance").select("""
                *,
                pod_meetings(meeting_date, pod_id)
            """).eq("user_id", user_id).execute()
            
            # Filter by pod and sort by date
            pod_attendance = []
            for record in attendance_result.data:
                if record["pod_meetings"]["pod_id"] == pod_id:
                    pod_attendance.append({
                        "date": record["pod_meetings"]["meeting_date"],
                        "present": record["was_present"],
                        "duration": record["duration_minutes"]
                    })
            
            pod_attendance.sort(key=lambda x: x["date"], reverse=True)
            
            # Calculate current streak
            current_streak = 0
            for meeting in pod_attendance:
                if meeting["present"]:
                    current_streak += 1
                else:
                    break
            
            # Calculate longest streak
            longest_streak = 0
            temp_streak = 0
            for meeting in reversed(pod_attendance):
                if meeting["present"]:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0
            
            # Calculate overall attendance rate
            total_meetings = len(pod_attendance)
            attended_meetings = sum(1 for m in pod_attendance if m["present"])
            attendance_rate = (attended_meetings / total_meetings * 100) if total_meetings > 0 else 0
            
            return {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "total_meetings": total_meetings,
                "attended_meetings": attended_meetings,
                "attendance_rate": round(attendance_rate, 1),
                "status": self._get_attendance_status(current_streak, attendance_rate)
            }
            
        except Exception as e:
            logger.error(f"Error getting attendance streak: {e}")
            return {"current_streak": 0, "longest_streak": 0, "total_meetings": 0, "attended_meetings": 0, "attendance_rate": 0, "status": "unknown"}
    
    def _get_attendance_status(self, streak: int, rate: float) -> str:
        """Get attendance status message"""
        if streak >= 4 and rate >= 90:
            return "🔥 Perfect Attendee"
        elif streak >= 2 and rate >= 75:
            return "⭐ Consistent Member"
        elif rate >= 50:
            return "📈 Growing Commitment"
        else:
            return "💪 Building Habit"
    
    async def send_attendance_reminder(self, pod_id: str, hours_before: int = 2) -> List[str]:
        """Send attendance reminders to pod members"""
        try:
            # Get next meeting
            next_meeting = await self._get_next_meeting(pod_id)
            if not next_meeting:
                return []
            
            # Check if reminder should be sent
            meeting_time = datetime.fromisoformat(next_meeting["scheduled_start_time"])
            reminder_time = meeting_time - timedelta(hours=hours_before)
            
            if datetime.now() < reminder_time:
                return []  # Too early for reminder
            
            # Get pod members
            members = self.supabase.table("pod_memberships").select("""
                users(telegram_user_id, first_name)
            """).eq("pod_id", pod_id).eq("status", "active").execute()
            
            # Create personalized reminders
            reminders = []
            for member in members.data:
                user_data = member["users"]
                telegram_id = user_data["telegram_user_id"]
                name = user_data["first_name"]
                
                # Get attendance streak for personalization
                streak_data = await self.get_user_attendance_streak(user_data["id"], pod_id)
                
                reminder_message = self._create_reminder_message(name, meeting_time, streak_data)
                reminders.append({"telegram_id": telegram_id, "message": reminder_message})
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error sending attendance reminders: {e}")
            return []
    
    async def _get_next_meeting(self, pod_id: str) -> Optional[Dict]:
        """Get next scheduled meeting for pod"""
        try:
            now = datetime.now().isoformat()
            result = self.supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).gte("scheduled_start_time", now).order("scheduled_start_time").limit(1).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error getting next meeting: {e}")
            return None
    
    def _create_reminder_message(self, name: str, meeting_time: datetime, streak_data: Dict) -> str:
        """Create personalized meeting reminder"""
        time_str = meeting_time.strftime("%I:%M %p")
        
        if streak_data["current_streak"] >= 3:
            motivation = f"🔥 You're on a {streak_data['current_streak']}-meeting streak! Keep it going!"
        elif streak_data["attendance_rate"] >= 75:
            motivation = f"⭐ Great attendance record ({streak_data['attendance_rate']}%)! See you there!"
        else:
            motivation = "💪 Your pod is counting on you!"
        
        return f"""
🎯 **Pod Meeting Reminder**

Hi {name}! Your pod meeting is in 2 hours at {time_str}.

{motivation}

See you on the call! 🚀
"""
    
    async def export_attendance_data(self, pod_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Export attendance data for analysis"""
        try:
            # Build query with date filters
            query = self.supabase.table("pod_meetings").select("""
                *,
                meeting_attendance(
                    *,
                    users(first_name, username, telegram_user_id)
                )
            """).eq("pod_id", pod_id)
            
            if start_date:
                query = query.gte("meeting_date", start_date)
            if end_date:
                query = query.lte("meeting_date", end_date)
            
            result = query.order("meeting_date").execute()
            
            # Format for export
            export_data = {
                "pod_id": pod_id,
                "export_date": datetime.now().isoformat(),
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "meetings": []
            }
            
            for meeting in result.data:
                meeting_export = {
                    "date": meeting["meeting_date"],
                    "scheduled_time": meeting["scheduled_start_time"],
                    "attendees": []
                }
                
                for attendance in meeting.get("meeting_attendance", []):
                    user_data = attendance["users"]
                    meeting_export["attendees"].append({
                        "name": user_data["first_name"],
                        "username": user_data["username"],
                        "joined_at": attendance["joined_at"],
                        "duration_minutes": attendance["duration_minutes"],
                        "quality": attendance["attendance_quality"]
                    })
                
                export_data["meetings"].append(meeting_export)
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting attendance data: {e}")
            return {"error": str(e)}