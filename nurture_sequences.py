# Nurture Sequences for The Progress Method
# Automated engagement messages to guide user journey and maintain engagement

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from supabase import Client
import json
from enum import Enum

logger = logging.getLogger(__name__)

class SequenceType(Enum):
    """Types of nurture sequences"""
    ONBOARDING = "onboarding"           # New user → first commitment
    COMMITMENT_FOLLOW_UP = "commitment_followup"  # After commitment creation
    RE_ENGAGEMENT = "re_engagement"     # Inactive users
    POD_JOURNEY = "pod_journey"         # Free user → pod member
    STREAK_CELEBRATION = "streak_celebration"  # Milestone celebrations
    GOAL_COACHING = "goal_coaching"     # Long-term goal guidance
    COMMUNITY_BUILDING = "community_building"  # Pod engagement

class NurtureSequences:
    """Manages automated nurture sequences and engagement messaging"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.sequences = self._define_sequences()
    
    def _define_sequences(self) -> Dict[str, Dict]:
        """Define all nurture sequences with their messages and timing"""
        return {
            "onboarding": {
                "name": "New User Onboarding",
                "trigger": "first_bot_interaction",
                "messages": [
                    {
                        "delay_hours": 0,
                        "message": """👋 Welcome to The Progress Method!

I'm here to help you turn your dreams into reality through small, consistent commitments.

🎯 **Ready to start?** Try: `/commit I will write one page of my book today`

Your journey to meaningful progress starts now! 🚀""",
                        "action": "send_message"
                    },
                    {
                        "delay_hours": 24,
                        "message": """💫 How's your first day going?

Remember: The magic happens in the consistency, not the size of the commitment.

🌱 **Small wins compound into big breakthroughs.**

Try another commitment today! Every step counts.""",
                        "action": "send_message",
                        "condition": "no_commitments_yet"
                    },
                    {
                        "delay_hours": 72,
                        "message": """🎉 Amazing! You've started your commitment journey!

📈 **Next level unlock:** Join a pod for weekly accountability calls.

Pods help you:
• Stay consistent with weekly check-ins
• Get support from like-minded dreamers
• Share wins and overcome challenges together

Ready to level up? Type `/pods` to learn more! 🚀""",
                        "action": "send_message",
                        "condition": "has_commitments_no_pod"
                    }
                ]
            },
            
            "commitment_followup": {
                "name": "Commitment Follow-up",
                "trigger": "commitment_created",
                "messages": [
                    {
                        "delay_hours": 6,
                        "message": """⏰ **Check-in time!**

How's your commitment going? 

✅ Done? Use `/done` to mark it complete!
💪 Still working? You've got this!
🤔 Stuck? Try breaking it into smaller steps.

Progress over perfection! 🎯""",
                        "action": "send_message",
                        "condition": "commitment_not_done"
                    },
                    {
                        "delay_hours": 22,
                        "message": """🌅 **New day, fresh energy!**

Yesterday's commitment: still open?

Remember: Consistency beats intensity. Even 5 minutes of progress counts!

🎯 **Today's wins are tomorrow's momentum.**""",
                        "action": "send_message",
                        "condition": "commitment_still_open"
                    }
                ]
            },
            
            "re_engagement": {
                "name": "Re-engagement for Inactive Users",
                "trigger": "7_days_inactive",
                "messages": [
                    {
                        "delay_hours": 0,
                        "message": """✨ We miss you!

It's been a week since your last commitment. No judgment - life happens! 💙

🌱 **Small restart idea:** What's one tiny thing you could commit to today? 

Even "I will drink one extra glass of water" counts. Progress is progress! 🎯""",
                        "action": "send_message"
                    },
                    {
                        "delay_hours": 168,  # 7 days later
                        "message": """🎯 **Your dreams are still waiting...**

Two weeks without progress can feel overwhelming, but here's the truth:

💪 **You're one commitment away from momentum.**

What matters most to you right now? Start there. Start small. Start today.

We believe in you! 🚀""",
                        "action": "send_message",
                        "condition": "still_inactive"
                    }
                ]
            },
            
            "pod_journey": {
                "name": "Free User to Pod Member Journey",
                "trigger": "5_commitments_completed",
                "messages": [
                    {
                        "delay_hours": 2,
                        "message": """🎉 **5 commitments completed!** You're building real momentum!

🤔 **Ready for the next level?**

Join a pod for:
• Weekly accountability calls with 6-8 committed dreamers
• Group support when you're stuck
• Celebration of wins (big and small!)
• Structured progress toward your biggest goals

Type `/pods` to explore pod membership! 🚀""",
                        "action": "send_message"
                    },
                    {
                        "delay_hours": 72,
                        "message": """💎 **You're doing amazing solo...**

But imagine the power of a supportive community! 

Pod members are 3x more likely to achieve their long-term goals. Here's why:

✅ Weekly accountability calls
✅ Peer support during challenges  
✅ Shared wisdom and strategies
✅ Celebration of progress together

Ready to amplify your progress? `/pods` 🚀""",
                        "action": "send_message",
                        "condition": "not_pod_member"
                    }
                ]
            },
            
            "streak_celebration": {
                "name": "Streak Milestone Celebrations",
                "trigger": "streak_milestone",
                "messages": [
                    {
                        "delay_hours": 0,
                        "message": "🔥 **{streak_days} DAY STREAK!** 🔥\n\nYou're officially unstoppable! This is how dreams become reality - one consistent day at a time.\n\n{celebration_message}\n\nKeep going! Your future self is cheering you on! 🎉",
                        "action": "send_message",
                        "template": True
                    }
                ]
            },
            
            "community_building": {
                "name": "Pod Community Engagement",
                "trigger": "pod_member_inactive",
                "messages": [
                    {
                        "delay_hours": 0,
                        "message": """👥 **Your pod misses you!**

It's been a few days since your last commitment. Your pod family is here to support you! 💙

🎯 **This week's pod theme:** {pod_theme}

What's one small commitment you could share with the group? They're rooting for you! 

See you at the next call! 📞""",
                        "action": "send_message",
                        "template": True
                    }
                ]
            }
        }
    
    async def create_nurture_tables(self):
        """Create nurture sequence tracking tables"""
        try:
            logger.info("✅ Nurture sequence tables ready for creation")
            logger.info("Tables: nurture_sequences, sequence_messages, user_sequence_state")
            return True
        except Exception as e:
            logger.error(f"Error creating nurture tables: {e}")
            return False
    
    async def trigger_sequence(self, user_id: str, sequence_type: SequenceType, context: Dict[str, Any] = None) -> bool:
        """Trigger a nurture sequence for a user"""
        try:
            sequence_key = sequence_type.value
            sequence = self.sequences.get(sequence_key)
            
            if not sequence:
                logger.warning(f"Unknown sequence type: {sequence_key}")
                return False
            
            # Check if user is already in this sequence
            existing = self.supabase.table("user_sequence_state").select("*").eq("user_id", user_id).eq("sequence_type", sequence_key).eq("is_active", True).execute()
            
            if existing.data:
                logger.info(f"User {user_id} already in sequence {sequence_key}")
                return False
            
            # Create sequence state
            sequence_state = {
                "user_id": user_id,
                "sequence_type": sequence_key,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "context": json.dumps(context or {}),
                "is_active": True,
                "next_message_at": self._calculate_next_message_time(sequence, 0)
            }
            
            result = self.supabase.table("user_sequence_state").insert(sequence_state).execute()
            
            if result.data:
                logger.info(f"✅ Started sequence '{sequence_key}' for user {user_id}")
                
                # Send first message if it's immediate
                await self._process_immediate_messages(user_id, sequence_key)
                return True
            
        except Exception as e:
            logger.error(f"Error triggering sequence: {e}")
            
        return False
    
    async def _process_immediate_messages(self, user_id: str, sequence_type: str):
        """Process messages that should be sent immediately"""
        try:
            sequence = self.sequences[sequence_type]
            immediate_messages = [msg for msg in sequence["messages"] if msg["delay_hours"] == 0]
            
            for message_data in immediate_messages:
                if await self._should_send_message(user_id, message_data):
                    await self._send_sequence_message(user_id, message_data)
                    
        except Exception as e:
            logger.error(f"Error processing immediate messages: {e}")
    
    async def _should_send_message(self, user_id: str, message_data: Dict) -> bool:
        """Check if message should be sent based on conditions"""
        condition = message_data.get("condition")
        if not condition:
            return True
        
        try:
            if condition == "no_commitments_yet":
                commitments = self.supabase.table("commitments").select("id").eq("user_id", user_id).limit(1).execute()
                return len(commitments.data) == 0
            
            elif condition == "has_commitments_no_pod":
                commitments = self.supabase.table("commitments").select("id").eq("user_id", user_id).limit(1).execute()
                has_commitments = len(commitments.data) > 0
                
                pod_membership = self.supabase.table("pod_memberships").select("id").eq("user_id", user_id).limit(1).execute()
                has_pod = len(pod_membership.data) > 0
                
                return has_commitments and not has_pod
            
            elif condition == "not_pod_member":
                pod_membership = self.supabase.table("pod_memberships").select("id").eq("user_id", user_id).limit(1).execute()
                return len(pod_membership.data) == 0
            
            elif condition == "commitment_not_done":
                # Check if user has any pending commitments
                pending = self.supabase.table("commitments").select("id").eq("user_id", user_id).neq("status", "completed").limit(1).execute()
                return len(pending.data) > 0
            
            elif condition == "still_inactive":
                # Check if user is still inactive
                recent_activity = self.supabase.table("commitments").select("id").eq("user_id", user_id).gte("created_at", (datetime.now() - timedelta(days=3)).isoformat()).execute()
                return len(recent_activity.data) == 0
            
        except Exception as e:
            logger.error(f"Error checking message condition: {e}")
            
        return True
    
    async def _send_sequence_message(self, user_id: str, message_data: Dict) -> bool:
        """Send a sequence message to user"""
        try:
            # Get user's telegram ID
            user_result = self.supabase.table("users").select("telegram_user_id, first_name").eq("id", user_id).execute()
            if not user_result.data:
                return False
            
            telegram_id = user_result.data[0]["telegram_user_id"]
            user_name = user_result.data[0]["first_name"]
            
            # Process message template
            message_text = message_data["message"]
            if message_data.get("template"):
                # Replace template variables (add more as needed)
                message_text = message_text.replace("{user_name}", user_name)
            
            # Log the message (in production, this would queue for actual sending)
            logger.info(f"📤 Nurture message to {telegram_id}: {message_text[:50]}...")
            
            # In actual implementation, you'd send via bot:
            # await bot.send_message(telegram_id, message_text, parse_mode="Markdown")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending sequence message: {e}")
            return False
    
    def _calculate_next_message_time(self, sequence: Dict, current_step: int) -> str:
        """Calculate when the next message should be sent"""
        messages = sequence["messages"]
        if current_step >= len(messages):
            return None
        
        next_message = messages[current_step]
        next_time = datetime.now() + timedelta(hours=next_message["delay_hours"])
        return next_time.isoformat()
    
    async def process_pending_messages(self):
        """Process all pending nurture messages (run this on a schedule)"""
        try:
            # Get all active sequences with pending messages
            now = datetime.now().isoformat()
            
            pending = self.supabase.table("user_sequence_state").select("*").eq("is_active", True).lte("next_message_at", now).execute()
            
            processed = 0
            for sequence_state in pending.data:
                success = await self._process_sequence_step(sequence_state)
                if success:
                    processed += 1
            
            logger.info(f"📬 Processed {processed} nurture messages")
            return processed
            
        except Exception as e:
            logger.error(f"Error processing pending messages: {e}")
            return 0
    
    async def _process_sequence_step(self, sequence_state: Dict) -> bool:
        """Process the next step in a user's sequence"""
        try:
            sequence_type = sequence_state["sequence_type"]
            current_step = sequence_state["current_step"]
            user_id = sequence_state["user_id"]
            
            sequence = self.sequences.get(sequence_type)
            if not sequence or current_step >= len(sequence["messages"]):
                # End of sequence
                await self._complete_sequence(sequence_state["id"])
                return True
            
            message_data = sequence["messages"][current_step]
            
            # Check conditions
            if await self._should_send_message(user_id, message_data):
                # Send message
                success = await self._send_sequence_message(user_id, message_data)
                
                if success:
                    # Update sequence state
                    next_step = current_step + 1
                    next_message_time = self._calculate_next_message_time(sequence, next_step)
                    
                    update_data = {
                        "current_step": next_step,
                        "last_message_sent_at": datetime.now().isoformat(),
                        "next_message_at": next_message_time
                    }
                    
                    if next_message_time is None:
                        update_data["is_active"] = False
                        update_data["completed_at"] = datetime.now().isoformat()
                    
                    self.supabase.table("user_sequence_state").update(update_data).eq("id", sequence_state["id"]).execute()
                    
                    return True
            else:
                # Skip this message, move to next
                next_step = current_step + 1
                next_message_time = self._calculate_next_message_time(sequence, next_step)
                
                self.supabase.table("user_sequence_state").update({
                    "current_step": next_step,
                    "next_message_at": next_message_time
                }).eq("id", sequence_state["id"]).execute()
                
                return True
            
        except Exception as e:
            logger.error(f"Error processing sequence step: {e}")
            
        return False
    
    async def _complete_sequence(self, sequence_state_id: str):
        """Mark sequence as completed"""
        try:
            self.supabase.table("user_sequence_state").update({
                "is_active": False,
                "completed_at": datetime.now().isoformat()
            }).eq("id", sequence_state_id).execute()
            
        except Exception as e:
            logger.error(f"Error completing sequence: {e}")
    
    async def check_triggers(self, user_id: str, event: str, context: Dict[str, Any] = None):
        """Check if any sequences should be triggered by an event"""
        try:
            # Map events to sequence types
            trigger_map = {
                "first_interaction": SequenceType.ONBOARDING,
                "commitment_created": SequenceType.COMMITMENT_FOLLOW_UP,
                "7_days_inactive": SequenceType.RE_ENGAGEMENT,
                "5_commitments_completed": SequenceType.POD_JOURNEY,
                "streak_milestone": SequenceType.STREAK_CELEBRATION,
                "pod_member_inactive": SequenceType.COMMUNITY_BUILDING
            }
            
            sequence_type = trigger_map.get(event)
            if sequence_type:
                await self.trigger_sequence(user_id, sequence_type, context)
                
        except Exception as e:
            logger.error(f"Error checking triggers: {e}")
    
    async def get_user_sequence_status(self, user_id: str) -> List[Dict]:
        """Get all active sequences for a user"""
        try:
            result = self.supabase.table("user_sequence_state").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            
            status_list = []
            for sequence in result.data:
                sequence_def = self.sequences.get(sequence["sequence_type"])
                total_messages = len(sequence_def["messages"]) if sequence_def else 0
                
                status_list.append({
                    "sequence_name": sequence_def["name"] if sequence_def else sequence["sequence_type"],
                    "current_step": sequence["current_step"],
                    "total_steps": total_messages,
                    "progress": f"{sequence['current_step']}/{total_messages}",
                    "next_message_at": sequence["next_message_at"],
                    "started_at": sequence["started_at"]
                })
            
            return status_list
            
        except Exception as e:
            logger.error(f"Error getting sequence status: {e}")
            return []
    
    async def stop_sequence(self, user_id: str, sequence_type: str) -> bool:
        """Stop a specific sequence for a user"""
        try:
            result = self.supabase.table("user_sequence_state").update({
                "is_active": False,
                "stopped_at": datetime.now().isoformat()
            }).eq("user_id", user_id).eq("sequence_type", sequence_type).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error stopping sequence: {e}")
            return False
    
    async def get_sequence_analytics(self) -> Dict:
        """Get analytics on sequence performance"""
        try:
            # Get sequence completion rates
            all_sequences = self.supabase.table("user_sequence_state").select("*").execute()
            
            analytics = {
                "total_sequences_started": len(all_sequences.data),
                "sequence_stats": {},
                "completion_rates": {},
                "user_engagement": {}
            }
            
            # Analyze by sequence type
            for sequence in all_sequences.data:
                seq_type = sequence["sequence_type"]
                
                if seq_type not in analytics["sequence_stats"]:
                    analytics["sequence_stats"][seq_type] = {
                        "started": 0,
                        "completed": 0,
                        "active": 0,
                        "stopped": 0
                    }
                
                analytics["sequence_stats"][seq_type]["started"] += 1
                
                if sequence.get("completed_at"):
                    analytics["sequence_stats"][seq_type]["completed"] += 1
                elif sequence.get("stopped_at"):
                    analytics["sequence_stats"][seq_type]["stopped"] += 1
                elif sequence["is_active"]:
                    analytics["sequence_stats"][seq_type]["active"] += 1
            
            # Calculate completion rates
            for seq_type, stats in analytics["sequence_stats"].items():
                total_finished = stats["completed"] + stats["stopped"]
                if total_finished > 0:
                    analytics["completion_rates"][seq_type] = round((stats["completed"] / total_finished) * 100, 1)
                else:
                    analytics["completion_rates"][seq_type] = 0
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting sequence analytics: {e}")
            return {}
    
    async def format_sequence_status(self, user_id: str) -> str:
        """Format user's current sequence status for display"""
        try:
            sequences = await self.get_user_sequence_status(user_id)
            
            if not sequences:
                return "💌 **No active nurture sequences**\n\nYou're all caught up! Keep making commitments and I'll send helpful messages when appropriate."
            
            message = "💌 **Your Active Guidance Sequences:**\n\n"
            
            for seq in sequences:
                next_time = datetime.fromisoformat(seq["next_message_at"]) if seq["next_message_at"] else None
                time_until = ""
                
                if next_time:
                    delta = next_time - datetime.now()
                    if delta.days > 0:
                        time_until = f" (in {delta.days} days)"
                    elif delta.seconds > 3600:
                        hours = delta.seconds // 3600
                        time_until = f" (in {hours}h)"
                    else:
                        time_until = " (soon)"
                
                message += f"📬 **{seq['sequence_name']}**\n"
                message += f"   Progress: {seq['progress']}\n"
                message += f"   Next message{time_until}\n\n"
            
            message += "💡 Don't want guidance messages? Use `/stop_sequences`"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting sequence status: {e}")
            return "Error retrieving sequence status."