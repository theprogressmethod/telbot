#!/usr/bin/env python3
"""
Communication Preferences & Visibility System
Smart nurture with user control and analytics
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json
from enum import Enum

logger = logging.getLogger(__name__)

class CommunicationStyle(Enum):
    """User-defined communication preferences"""
    HIGH_TOUCH = "high_touch"         # All 7 weekly touches + extras
    BALANCED = "balanced"             # 4 key touches (Mon, Wed, Thu, Fri)
    LIGHT_TOUCH = "light_touch"       # 2 essential touches (Tue prep, Thu momentum)
    MEETING_ONLY = "meeting_only"     # Only pre-meeting reminders
    CUSTOM = "custom"                 # User-defined specific preferences
    PAUSED = "paused"                 # Temporarily off (with easy resume)

class MessageType(Enum):
    """Categories of nurture messages"""
    WEEK_LAUNCH = "week_launch"       # Monday motivation
    MEETING_PREP = "meeting_prep"     # Tuesday preparation
    PRE_MEETING = "pre_meeting"       # Wednesday energizer
    POST_MEETING = "post_meeting"     # Thursday momentum
    REFLECTION = "reflection"         # Friday review
    VISIONING = "visioning"           # Sunday planning
    RECOVERY = "recovery"             # Support messages
    CELEBRATION = "celebration"       # Milestone messages
    ADMIN = "admin"                   # Pod logistics

class CommunicationPreferences:
    """Manages user communication preferences and analytics"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.communication_matrix = self._define_communication_matrix()
    
    def _define_communication_matrix(self) -> Dict[str, List[str]]:
        """Define what messages each style receives"""
        return {
            "high_touch": [
                "week_launch", "meeting_prep", "pre_meeting", 
                "post_meeting", "reflection", "visioning", 
                "recovery", "celebration", "admin"
            ],
            "balanced": [
                "week_launch", "meeting_prep", "post_meeting", "reflection"
            ],
            "light_touch": [
                "meeting_prep", "post_meeting"
            ],
            "meeting_only": [
                "meeting_prep", "admin"
            ],
            "paused": [
                "admin"  # Only critical pod logistics
            ]
        }
    
    async def set_user_communication_style(self, telegram_user_id: int, style: CommunicationStyle, 
                                         custom_preferences: Dict = None) -> bool:
        """Set user's communication preferences"""
        try:
            user_uuid = await self._get_user_uuid(telegram_user_id)
            if not user_uuid:
                return False
            
            preferences_data = {
                "user_id": user_uuid,
                "telegram_user_id": telegram_user_id,
                "communication_style": style.value,
                "custom_preferences": json.dumps(custom_preferences or {}),
                "enabled_message_types": json.dumps(self.communication_matrix.get(style.value, [])),
                "last_updated": datetime.now().isoformat(),
                "pause_until": None if style != CommunicationStyle.PAUSED else None,
                "is_active": True
            }
            
            # Upsert preferences (on conflict with telegram_user_id, update)
            result = self.supabase.table("communication_preferences").upsert(
                preferences_data, 
                on_conflict="telegram_user_id"
            ).execute()
            
            # Log the preference change
            await self._log_preference_change(telegram_user_id, style.value, "user_initiated")
            
            logger.info(f"✅ Set communication style '{style.value}' for user {telegram_user_id}")
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error setting communication style: {e}")
            return False
    
    async def should_send_message(self, telegram_user_id: int, message_type: MessageType) -> Dict[str, Any]:
        """Check if user should receive this type of message"""
        try:
            # Get user preferences
            prefs_result = self.supabase.table("communication_preferences").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not prefs_result.data:
                # Default to balanced for new users
                await self.set_user_communication_style(telegram_user_id, CommunicationStyle.BALANCED)
                return {"should_send": True, "reason": "default_balanced"}
            
            prefs = prefs_result.data[0]
            
            # Check if paused
            if prefs["communication_style"] == "paused":
                pause_until = prefs.get("pause_until")
                if pause_until and datetime.fromisoformat(pause_until) > datetime.now():
                    return {"should_send": False, "reason": "user_paused"}
            
            # Check message type allowlist
            enabled_types = json.loads(prefs["enabled_message_types"])
            if message_type.value not in enabled_types:
                return {"should_send": False, "reason": "message_type_disabled"}
            
            # Check recent message frequency
            recent_messages = await self._get_recent_message_count(telegram_user_id, hours=24)
            
            # Frequency limits based on style
            style_limits = {
                "high_touch": 3,    # Max 3 per day
                "balanced": 2,      # Max 2 per day  
                "light_touch": 1,   # Max 1 per day
                "meeting_only": 1   # Max 1 per day
            }
            
            style = prefs["communication_style"]
            if recent_messages >= style_limits.get(style, 2):
                return {"should_send": False, "reason": "frequency_limit_reached"}
            
            # Check user engagement score
            engagement_score = await self._calculate_engagement_score(telegram_user_id)
            
            # If user has low engagement, reduce frequency
            if engagement_score < 0.3 and message_type not in [MessageType.MEETING_PREP, MessageType.ADMIN]:
                return {"should_send": False, "reason": "low_engagement_protection"}
            
            return {"should_send": True, "reason": "all_checks_passed", "engagement_score": engagement_score}
            
        except Exception as e:
            logger.error(f"Error checking message permission: {e}")
            return {"should_send": False, "reason": "error"}
    
    async def _calculate_engagement_score(self, telegram_user_id: int) -> float:
        """Calculate user engagement score (0.0 to 1.0)"""
        try:
            # Get recent message responses
            recent_responses = self.supabase.table("message_analytics").select("*").eq("telegram_user_id", telegram_user_id).gte("sent_at", (datetime.now() - timedelta(days=14)).isoformat()).execute()
            
            if not recent_responses.data:
                return 0.5  # Neutral score for new users
            
            total_sent = len(recent_responses.data)
            responses = sum(1 for msg in recent_responses.data if msg.get("user_responded", False))
            clicks = sum(1 for msg in recent_responses.data if msg.get("clicked_link", False))
            
            # Calculate engagement metrics
            response_rate = responses / total_sent if total_sent > 0 else 0
            click_rate = clicks / total_sent if total_sent > 0 else 0
            
            # Weight response rate higher than click rate
            engagement_score = (response_rate * 0.7) + (click_rate * 0.3)
            
            return min(1.0, engagement_score)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.5
    
    async def _get_recent_message_count(self, telegram_user_id: int, hours: int = 24) -> int:
        """Get count of messages sent to user in recent hours"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            result = self.supabase.table("message_analytics").select("id", count="exact").eq("telegram_user_id", telegram_user_id).gte("sent_at", cutoff_time).execute()
            return result.count
        except Exception as e:
            logger.error(f"Error getting recent message count: {e}")
            return 0
    
    async def log_message_sent(self, telegram_user_id: int, message_type: MessageType, 
                             message_content: str, pod_id: str = None) -> bool:
        """Log message for analytics and engagement tracking"""
        try:
            analytics_data = {
                "telegram_user_id": telegram_user_id,
                "message_type": message_type.value,
                "pod_id": pod_id,
                "message_length": len(message_content),
                "sent_at": datetime.now().isoformat(),
                "user_responded": False,  # Will be updated if user responds
                "clicked_link": False,    # Will be updated if user clicks
                "message_hash": hash(message_content[:100])  # For deduplication
            }
            
            result = self.supabase.table("message_analytics").insert(analytics_data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return False
    
    async def log_user_response(self, telegram_user_id: int, response_type: str = "text_reply") -> bool:
        """Log user response for engagement tracking"""
        try:
            # Find recent message to mark as responded
            recent_message = self.supabase.table("message_analytics").select("*").eq("telegram_user_id", telegram_user_id).order("sent_at", desc=True).limit(1).execute()
            
            if recent_message.data:
                message_id = recent_message.data[0]["id"]
                self.supabase.table("message_analytics").update({
                    "user_responded": True,
                    "response_type": response_type,
                    "responded_at": datetime.now().isoformat()
                }).eq("id", message_id).execute()
                
                return True
            
        except Exception as e:
            logger.error(f"Error logging user response: {e}")
            return False
    
    async def get_user_preferences_summary(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get comprehensive summary of user's communication preferences"""
        try:
            # Get preferences
            prefs_result = self.supabase.table("communication_preferences").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not prefs_result.data:
                return {"style": "not_set", "needs_setup": True}
            
            prefs = prefs_result.data[0]
            
            # Get recent analytics
            analytics_result = self.supabase.table("message_analytics").select("*").eq("telegram_user_id", telegram_user_id).gte("sent_at", (datetime.now() - timedelta(days=7)).isoformat()).execute()
            
            # Calculate metrics
            total_sent = len(analytics_result.data)
            responses = sum(1 for msg in analytics_result.data if msg.get("user_responded", False))
            
            engagement_score = await self._calculate_engagement_score(telegram_user_id)
            
            return {
                "style": prefs["communication_style"],
                "enabled_types": json.loads(prefs["enabled_message_types"]),
                "last_updated": prefs["last_updated"],
                "messages_this_week": total_sent,
                "response_rate": responses / total_sent if total_sent > 0 else 0,
                "engagement_score": engagement_score,
                "is_paused": prefs["communication_style"] == "paused",
                "pause_until": prefs.get("pause_until")
            }
            
        except Exception as e:
            logger.error(f"Error getting preferences summary: {e}")
            return {"error": str(e)}
    
    async def pause_communications(self, telegram_user_id: int, duration_days: int = 7) -> bool:
        """Temporarily pause communications with easy resume"""
        try:
            pause_until = (datetime.now() + timedelta(days=duration_days)).isoformat()
            
            result = self.supabase.table("communication_preferences").update({
                "communication_style": "paused",
                "pause_until": pause_until,
                "last_updated": datetime.now().isoformat()
            }).eq("telegram_user_id", telegram_user_id).execute()
            
            await self._log_preference_change(telegram_user_id, "paused", f"user_paused_{duration_days}d")
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error pausing communications: {e}")
            return False
    
    async def resume_communications(self, telegram_user_id: int, new_style: CommunicationStyle = CommunicationStyle.BALANCED) -> bool:
        """Resume communications after pause"""
        try:
            result = self.supabase.table("communication_preferences").update({
                "communication_style": new_style.value,
                "pause_until": None,
                "last_updated": datetime.now().isoformat()
            }).eq("telegram_user_id", telegram_user_id).execute()
            
            await self._log_preference_change(telegram_user_id, new_style.value, "user_resumed")
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error resuming communications: {e}")
            return False
    
    async def _log_preference_change(self, telegram_user_id: int, new_style: str, reason: str):
        """Log preference changes for analytics"""
        try:
            log_data = {
                "telegram_user_id": telegram_user_id,
                "action": "preference_change",
                "old_style": None,  # Could track previous style
                "new_style": new_style,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.table("preference_change_log").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging preference change: {e}")
    
    async def _get_user_uuid(self, telegram_user_id: int) -> Optional[str]:
        """Get user UUID from telegram_user_id"""
        try:
            result = self.supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
            if result.data:
                return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Error getting user UUID: {e}")
        return None
    
    async def get_communication_analytics_dashboard(self, pod_id: str = None) -> Dict[str, Any]:
        """Get comprehensive analytics for communication effectiveness"""
        try:
            # Build query
            query = self.supabase.table("message_analytics").select("*")
            if pod_id:
                query = query.eq("pod_id", pod_id)
            
            # Get recent data (last 30 days)
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            analytics_data = query.gte("sent_at", cutoff_date).execute()
            
            if not analytics_data.data:
                return {"message": "No data available"}
            
            # Calculate metrics
            total_messages = len(analytics_data.data)
            responses = sum(1 for msg in analytics_data.data if msg.get("user_responded", False))
            clicks = sum(1 for msg in analytics_data.data if msg.get("clicked_link", False))
            
            # Message type breakdown
            type_breakdown = {}
            for msg in analytics_data.data:
                msg_type = msg["message_type"]
                type_breakdown[msg_type] = type_breakdown.get(msg_type, 0) + 1
            
            # Response rates by type
            type_response_rates = {}
            for msg_type in type_breakdown.keys():
                type_messages = [msg for msg in analytics_data.data if msg["message_type"] == msg_type]
                type_responses = sum(1 for msg in type_messages if msg.get("user_responded", False))
                type_response_rates[msg_type] = type_responses / len(type_messages) if type_messages else 0
            
            # User preference distribution
            prefs_data = self.supabase.table("communication_preferences").select("communication_style").execute()
            style_distribution = {}
            for pref in prefs_data.data:
                style = pref["communication_style"]
                style_distribution[style] = style_distribution.get(style, 0) + 1
            
            return {
                "period": "last_30_days",
                "total_messages_sent": total_messages,
                "overall_response_rate": responses / total_messages if total_messages > 0 else 0,
                "overall_click_rate": clicks / total_messages if total_messages > 0 else 0,
                "message_type_breakdown": type_breakdown,
                "response_rates_by_type": type_response_rates,
                "user_style_distribution": style_distribution,
                "engagement_insights": {
                    "most_engaging_type": max(type_response_rates.keys(), key=type_response_rates.get) if type_response_rates else None,
                    "least_engaging_type": min(type_response_rates.keys(), key=type_response_rates.get) if type_response_rates else None,
                    "average_daily_messages": total_messages / 30
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {e}")
            return {"error": str(e)}

class CommunicationPreferencesBot:
    """Bot commands for managing communication preferences"""
    
    def __init__(self, preferences_system: CommunicationPreferences):
        self.prefs = preferences_system
    
    async def handle_preferences_command(self, telegram_user_id: int) -> str:
        """Handle /preferences command"""
        try:
            summary = await self.prefs.get_user_preferences_summary(telegram_user_id)
            
            if summary.get("needs_setup"):
                return self._create_preferences_setup_message()
            
            return self._create_preferences_summary_message(summary)
            
        except Exception as e:
            return f"Error getting preferences: {str(e)}"
    
    def _create_preferences_setup_message(self) -> str:
        """Create initial preferences setup message"""
        return """🎛️ **Communication Preferences Setup**

How much nurturing would you like from your pod?

**Choose your style:**

1️⃣ **High Touch** - All weekly messages (7 per week)
   • Monday motivation, Tuesday prep, Wednesday energy, Thursday momentum, Friday reflection, Sunday planning + celebrations

2️⃣ **Balanced** - Key moments (4 per week) 
   • Monday launch, Tuesday prep, Thursday momentum, Friday reflection

3️⃣ **Light Touch** - Essentials only (2 per week)
   • Tuesday meeting prep + Thursday follow-up

4️⃣ **Meeting Only** - Just reminders (1 per week)
   • Tuesday meeting preparation only

5️⃣ **Pause** - Take a break
   • Only critical pod logistics

Reply with the number of your choice!

💡 **You can change this anytime** with `/preferences`"""
    
    def _create_preferences_summary_message(self, summary: Dict) -> str:
        """Create preferences summary message"""
        style = summary["style"].replace("_", " ").title()
        
        message = f"""🎛️ **Your Communication Preferences**

**Current Style:** {style}
**Messages This Week:** {summary["messages_this_week"]}
**Response Rate:** {summary["response_rate"]:.1%}
**Engagement Score:** {summary["engagement_score"]:.1%}

**Enabled Message Types:**
"""
        
        for msg_type in summary["enabled_types"]:
            friendly_name = msg_type.replace("_", " ").title()
            message += f"• {friendly_name}\n"
        
        message += f"""
**Quick Actions:**
• `/preferences light` - Switch to light touch
• `/preferences pause` - Pause for 1 week  
• `/preferences resume` - Resume messages
• `/quiet` - Pause until I say otherwise

💡 **Your choice, your control** - change anytime!"""

        return message
    
    async def handle_preferences_change(self, telegram_user_id: int, new_style: str) -> str:
        """Handle preference change commands"""
        try:
            style_mapping = {
                "high": CommunicationStyle.HIGH_TOUCH,
                "balanced": CommunicationStyle.BALANCED,
                "light": CommunicationStyle.LIGHT_TOUCH,
                "meeting": CommunicationStyle.MEETING_ONLY,
                "pause": CommunicationStyle.PAUSED
            }
            
            if new_style.lower() in style_mapping:
                style = style_mapping[new_style.lower()]
                success = await self.prefs.set_user_communication_style(telegram_user_id, style)
                
                if success:
                    return f"✅ **Updated to {new_style.title()} Touch**\n\nYou'll now receive {self._get_style_description(style)}.\n\nChange anytime with `/preferences`"
                else:
                    return "❌ Error updating preferences. Please try again."
            else:
                return "Invalid style. Use: high, balanced, light, meeting, or pause"
                
        except Exception as e:
            return f"Error changing preferences: {str(e)}"
    
    def _get_style_description(self, style: CommunicationStyle) -> str:
        """Get friendly description of communication style"""
        descriptions = {
            CommunicationStyle.HIGH_TOUCH: "all weekly pod messages (7 per week)",
            CommunicationStyle.BALANCED: "key weekly messages (4 per week)",
            CommunicationStyle.LIGHT_TOUCH: "essential messages only (2 per week)",
            CommunicationStyle.MEETING_ONLY: "just meeting reminders (1 per week)",
            CommunicationStyle.PAUSED: "only critical pod logistics"
        }
        return descriptions.get(style, "customized messages")