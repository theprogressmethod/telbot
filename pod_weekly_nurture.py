#!/usr/bin/env python3
"""
Pod Weekly Nurture Sequence
Comprehensive weekly journey for pod members
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from supabase import Client
import json
from enum import Enum

logger = logging.getLogger(__name__)

class WeeklyMoment(Enum):
    """Weekly nurture touchpoints for pod members"""
    MONDAY_LAUNCH = "monday_launch"           # Monday 9 AM - Week kickoff
    TUESDAY_PREP = "tuesday_prep"             # Tuesday 7 PM - Meeting prep
    WEDNESDAY_ENERGIZER = "wednesday_energizer" # 2 hours before meeting
    THURSDAY_MOMENTUM = "thursday_momentum"   # 24 hours after meeting
    FRIDAY_REFLECTION = "friday_reflection"   # Friday 4 PM - Week review
    SUNDAY_VISIONING = "sunday_visioning"     # Sunday 6 PM - Next week prep
    RECOVERY_SUPPORT = "recovery_support"     # Conditional - struggling members

class PodWeeklyNurture:
    """Manages comprehensive weekly nurture sequence for pod members"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.weekly_sequences = self._define_weekly_sequences()
    
    def _define_weekly_sequences(self) -> Dict[str, Dict]:
        """Define comprehensive weekly pod nurture sequences"""
        return {
            "monday_launch": {
                "name": "Monday Momentum - Week Launch",
                "optimal_time": "09:00",  # 9 AM local
                "message": """🌅 **New week, new possibilities!**

Your pod mates are starting their week too - what legacy will you all create together?

🎯 **This week's pod focus:** {pod_theme}

What's your key commitment for this week? Share it with your pod!
Try: `/commit [your weekly focus]`

🗓️ **Pod meetup:** {meeting_day} at {meeting_time}

Let's make this week count! 💪""",
                "psychological_purpose": "Capitalize on Monday motivation, create shared intentionality",
                "personalization": ["pod_theme", "meeting_day", "meeting_time", "pod_name"]
            },
            
            "tuesday_prep": {
                "name": "Pod Prep - Meeting Preparation",
                "optimal_time": "19:00",  # 7 PM local
                "message": """📋 **Pod meeting tomorrow at {meeting_time}!**

Quick prep to make your call amazing:

✅ **Review your week** - What's going well? What's challenging?
✅ **Check progress** - Use `/list` to see your commitments
✅ **Think celebration** - What wins (big or small) will you share?
✅ **Consider support** - Where could you use pod wisdom?

{pod_member_count} amazing people are preparing alongside you! 🎯

Meeting details: {meeting_link}""",
                "psychological_purpose": "Reduce meeting anxiety, increase engagement quality",
                "personalization": ["meeting_time", "pod_member_count", "meeting_link"]
            },
            
            "wednesday_energizer": {
                "name": "Pre-Meeting Energy Boost",
                "optimal_time": "meeting_minus_2h",  # 2 hours before meeting
                "message": """🔥 **T-minus 2 hours to {pod_name} time!**

Your weekly accountability moment is almost here!

💡 **Quick mindset prep:**
• Come curious, not perfect
• Share struggles - they lead to breakthroughs  
• Celebrate others' wins like your own
• Remember: vulnerability creates connection

✨ **{pod_name} is about to create some magic together!**

Ready to show up powerfully? 🚀""",
                "psychological_purpose": "Build anticipation, set positive meeting tone",
                "personalization": ["pod_name", "meeting_time"]
            },
            
            "thursday_momentum": {
                "name": "Post-Meeting Momentum Capture",
                "optimal_time": "meeting_plus_24h",  # 24 hours after meeting
                "message": """⭐ **That was an incredible {pod_name} call!**

The energy your group created yesterday was powerful. Now let's channel it:

🎯 **Your commitments from the call:**
{meeting_commitments}

🔗 **Pod momentum multiplier:** 
When you complete your commitments, you're not just helping yourself - you're inspiring {pod_members}!

💫 **This week's pod energy:** {meeting_sentiment}

Keep the momentum flowing! 🌟""",
                "psychological_purpose": "Capture post-meeting high, reinforce community impact",
                "personalization": ["pod_name", "meeting_commitments", "pod_members", "meeting_sentiment"]
            },
            
            "friday_reflection": {
                "name": "Weekly Reflection & Appreciation",
                "optimal_time": "16:00",  # 4 PM local Friday
                "message": """🌟 **Friday reflection time!**

Before the weekend, let's appreciate your growth:

📊 **This week you accomplished:**
{weekly_progress_summary}

👥 **{pod_name} collectively achieved:**
{pod_collective_wins}

📈 **Your momentum building:**
{consistency_data}

🎯 **Weekend intention:** What would make Monday feel even better?

Your pod family is proud of your commitment! 🙌""",
                "psychological_purpose": "Create positive week closure, maintain weekend motivation",
                "personalization": ["weekly_progress_summary", "pod_name", "pod_collective_wins", "consistency_data"]
            },
            
            "sunday_visioning": {
                "name": "Next Week Preparation",
                "optimal_time": "18:00",  # 6 PM Sunday
                "message": """🎯 **Tomorrow starts another powerful week!**

{pod_name} meets again {next_meeting_day} - what do you want to share with them?

💫 **Visualization moment:**
Picture yourself at {next_meeting_day}'s call, sharing a win from this coming week. What would make you feel most proud?

🌱 **Intention setting:** 
What commitment would create that feeling of pride and progress?

🚀 **Remember:** {pod_name} believes in your potential!

Ready to make magic happen? ✨""",
                "psychological_purpose": "Transform Sunday scaries into Sunday excitement",
                "personalization": ["pod_name", "next_meeting_day"]
            },
            
            "recovery_support": {
                "name": "Gentle Recovery & Re-engagement",
                "trigger": "no_commits_this_week",
                "message": """💙 **Hey there, {pod_name} warrior!**

Life happens - we see you. Your pod family has been there too.

💡 **Fresh start wisdom from your pod:**
"{pod_wisdom_quote}"

🎯 **Micro-commitment for tomorrow:** 
What's the smallest step you could take? Even 5 minutes counts!

📞 **Your pod meets {next_meeting}**
Come as you are - {pod_members} are rooting for you!

Remember: Progress isn't perfection, it's showing up again. 💪""",
                "psychological_purpose": "Prevent shame spiral, maintain pod connection",
                "personalization": ["pod_name", "pod_wisdom_quote", "next_meeting", "pod_members"]
            }
        }
    
    async def schedule_weekly_sequences_for_pod(self, pod_id: str) -> bool:
        """Schedule all weekly nurture sequences for pod members"""
        try:
            # Get pod details and members
            pod_result = self.supabase.table("pods").select("*").eq("id", pod_id).execute()
            if not pod_result.data:
                return False
                
            pod = pod_result.data[0]
            
            # Get active pod members
            members_result = self.supabase.table("pod_memberships").select("""
                user_id,
                users(telegram_user_id, first_name, timezone)
            """).eq("pod_id", pod_id).eq("is_active", True).execute()
            
            scheduled_count = 0
            
            for member in members_result.data:
                user_data = member["users"]
                success = await self._schedule_user_weekly_sequence(
                    user_data["telegram_user_id"], 
                    pod_id, 
                    pod, 
                    user_data.get("timezone", "UTC")
                )
                if success:
                    scheduled_count += 1
            
            logger.info(f"✅ Scheduled weekly sequences for {scheduled_count} members in pod {pod_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling weekly sequences: {e}")
            return False
    
    async def _schedule_user_weekly_sequence(self, telegram_user_id: int, pod_id: str, 
                                           pod_data: Dict, user_timezone: str) -> bool:
        """Schedule complete weekly sequence for individual user"""
        try:
            # Create weekly sequence state
            sequence_data = {
                "telegram_user_id": telegram_user_id,
                "pod_id": pod_id,
                "sequence_type": "weekly_pod_nurture",
                "week_start_date": self._get_current_week_start().isoformat(),
                "scheduled_messages": json.dumps(self._calculate_weekly_schedule(pod_data, user_timezone)),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            
            # Note: This would use the onboarding_states table or a new pod_weekly_sequences table
            # For now, we'll track in user_sequences table with pod context
            
            result = self.supabase.table("user_sequences").upsert({
                "user_id": await self._get_user_uuid(telegram_user_id),
                "sequence_type": "weekly_pod_nurture",
                "current_step": 0,
                "is_active": True,
                "started_at": datetime.now().isoformat(),
                "context": json.dumps({
                    "pod_id": pod_id,
                    "week_start": self._get_current_week_start().isoformat(),
                    "timezone": user_timezone
                })
            }).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error scheduling user weekly sequence: {e}")
            return False
    
    def _calculate_weekly_schedule(self, pod_data: Dict, user_timezone: str) -> List[Dict]:
        """Calculate optimal send times for weekly sequence"""
        week_start = self._get_current_week_start()
        schedule = []
        
        for sequence_key, sequence_data in self.weekly_sequences.items():
            if sequence_key == "recovery_support":
                continue  # Conditional sequence
                
            optimal_time = sequence_data["optimal_time"]
            
            if optimal_time == "meeting_minus_2h":
                # Calculate 2 hours before meeting
                send_time = self._calculate_meeting_relative_time(pod_data, -2)
            elif optimal_time == "meeting_plus_24h":
                # Calculate 24 hours after meeting
                send_time = self._calculate_meeting_relative_time(pod_data, 24)
            else:
                # Standard time on specific day
                send_time = self._calculate_weekly_time(week_start, sequence_key, optimal_time)
            
            schedule.append({
                "sequence": sequence_key,
                "send_at": send_time.isoformat(),
                "status": "pending"
            })
        
        return sorted(schedule, key=lambda x: x["send_at"])
    
    def _get_current_week_start(self) -> datetime:
        """Get Monday of current week"""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _calculate_meeting_relative_time(self, pod_data: Dict, hours_offset: int) -> datetime:
        """Calculate time relative to pod meeting"""
        meeting_day = pod_data.get("day_of_week", 2)  # Default Wednesday
        meeting_time = pod_data.get("time_utc", "19:00:00")  # Default 7 PM
        
        week_start = self._get_current_week_start()
        meeting_datetime = week_start + timedelta(days=meeting_day)
        
        # Parse meeting time
        hour, minute = map(int, meeting_time.split(":"))
        meeting_datetime = meeting_datetime.replace(hour=hour, minute=minute)
        
        return meeting_datetime + timedelta(hours=hours_offset)
    
    def _calculate_weekly_time(self, week_start: datetime, sequence_key: str, time_str: str) -> datetime:
        """Calculate specific day/time in week"""
        day_mapping = {
            "monday_launch": 0,      # Monday
            "tuesday_prep": 1,       # Tuesday  
            "friday_reflection": 4,  # Friday
            "sunday_visioning": 6    # Sunday
        }
        
        day_offset = day_mapping.get(sequence_key, 0)
        hour, minute = map(int, time_str.split(":"))
        
        target_datetime = week_start + timedelta(days=day_offset)
        return target_datetime.replace(hour=hour, minute=minute)
    
    async def _get_user_uuid(self, telegram_user_id: int) -> str:
        """Get user UUID from telegram_user_id"""
        result = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
        if result.data:
            return result.data[0]["id"]
        return None
    
    async def process_weekly_messages(self) -> List[Dict]:
        """Process and send pending weekly nurture messages"""
        try:
            # Get all active weekly sequences
            now = datetime.now()
            
            # This would query the weekly sequence tracking table
            # For now, we'll use a simplified approach
            
            pending_messages = []
            
            # Get all active pod members
            active_members = self.supabase.table("pod_memberships").select("""
                user_id,
                pod_id,
                users(telegram_user_id, first_name),
                pods(name, day_of_week, time_utc)
            """).eq("is_active", True).execute()
            
            for member in active_members.data:
                user_data = member["users"]
                pod_data = member["pods"]
                
                # Determine which message to send based on time/day
                message_data = await self._get_current_weekly_message(
                    user_data["telegram_user_id"],
                    member["pod_id"],
                    pod_data
                )
                
                if message_data:
                    pending_messages.append({
                        "telegram_user_id": user_data["telegram_user_id"],
                        "message": message_data["message"],
                        "sequence_type": message_data["sequence_type"]
                    })
            
            return pending_messages
            
        except Exception as e:
            logger.error(f"Error processing weekly messages: {e}")
            return []
    
    async def _get_current_weekly_message(self, telegram_user_id: int, pod_id: str, pod_data: Dict) -> Optional[Dict]:
        """Determine what weekly message should be sent now"""
        now = datetime.now()
        current_day = now.weekday()  # 0 = Monday
        current_hour = now.hour
        
        # Simple time-based logic (would be more sophisticated in production)
        if current_day == 0 and current_hour == 9:  # Monday 9 AM
            return await self._create_monday_launch_message(telegram_user_id, pod_id, pod_data)
        elif current_day == 1 and current_hour == 19:  # Tuesday 7 PM
            return await self._create_tuesday_prep_message(telegram_user_id, pod_id, pod_data)
        # Add other time checks...
        
        return None
    
    async def _create_monday_launch_message(self, telegram_user_id: int, pod_id: str, pod_data: Dict) -> Dict:
        """Create personalized Monday launch message"""
        template = self.weekly_sequences["monday_launch"]["message"]
        
        # Get personalization data
        pod_theme = await self._get_current_pod_theme(pod_id)
        meeting_day = self._get_meeting_day_name(pod_data.get("day_of_week", 2))
        meeting_time = pod_data.get("time_utc", "19:00")
        
        # Personalize message
        message = template.format(
            pod_theme=pod_theme,
            meeting_day=meeting_day,
            meeting_time=meeting_time,
            pod_name=pod_data["name"]
        )
        
        return {
            "message": message,
            "sequence_type": "monday_launch"
        }
    
    async def _create_tuesday_prep_message(self, telegram_user_id: int, pod_id: str, pod_data: Dict) -> Dict:
        """Create personalized Tuesday prep message"""
        template = self.weekly_sequences["tuesday_prep"]["message"]
        
        # Get dynamic data
        pod_member_count = await self._get_pod_member_count(pod_id)
        meeting_time = pod_data.get("time_utc", "19:00")
        meeting_link = await self._get_meeting_link(pod_id)
        
        message = template.format(
            meeting_time=meeting_time,
            pod_member_count=pod_member_count,
            meeting_link=meeting_link or "Check pod announcements for link"
        )
        
        return {
            "message": message,
            "sequence_type": "tuesday_prep"
        }
    
    async def _get_current_pod_theme(self, pod_id: str) -> str:
        """Get current monthly theme for pod"""
        themes = ["Focus & Clarity", "Creative Breakthrough", "Resilience Building", "Exponential Growth"]
        month = datetime.now().month
        return themes[month % len(themes)]
    
    def _get_meeting_day_name(self, day_number: int) -> str:
        """Convert day number to name"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[day_number % 7]
    
    async def _get_pod_member_count(self, pod_id: str) -> int:
        """Get active member count for pod"""
        result = self.supabase.table("pod_memberships").select("id", count="exact").eq("pod_id", pod_id).eq("is_active", True).execute()
        return result.count
    
    async def _get_meeting_link(self, pod_id: str) -> Optional[str]:
        """Get meeting link for pod (if stored)"""
        # This would come from pod settings or calendar integration
        return None  # Placeholder