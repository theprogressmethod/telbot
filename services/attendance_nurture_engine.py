#!/usr/bin/env python3
"""
Attendance-Triggered Nurture Sequence Engine
Connects meeting attendance data to automated nurture sequences
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from telbot import Config
from supabase import create_client, Client
from nurture_sequences import NurtureSequences, SequenceType
from pod_weekly_nurture import PodWeeklyNurture, WeeklyMoment
from safety_controls import safety_controls

logger = logging.getLogger(__name__)

class AttendanceTrigger(Enum):
    """Attendance events that trigger nurture sequences"""
    FIRST_MEETING_ATTENDED = "first_meeting_attended"
    MEETING_MISSED = "meeting_missed"
    STREAK_BROKEN = "streak_broken"
    CONSISTENT_ATTENDANCE = "consistent_attendance"
    LATE_ARRIVAL = "late_arrival"
    EARLY_ARRIVAL = "early_arrival"
    RE_ENGAGEMENT_NEEDED = "re_engagement_needed"
    WEEK_PERFECT_ATTENDANCE = "week_perfect_attendance"

@dataclass
class AttendanceEvent:
    """Represents an attendance event that can trigger nurtures"""
    user_id: str
    trigger_type: AttendanceTrigger
    meeting_id: str
    event_time: datetime
    metadata: Dict[str, Any]

class AttendanceNurtureEngine:
    """
    Core engine that processes attendance data and triggers appropriate nurture sequences
    """
    
    def __init__(self):
        self.config = Config()
        self.supabase = create_client(self.config.supabase_url, self.config.supabase_key)
        self.nurture_sequences = NurtureSequences(self.supabase)
        self.pod_weekly_nurture = PodWeeklyNurture(self.supabase)
        
        # Message queue for scheduled delivery
        self.message_queue = []
        
        logger.info("🤖 Attendance Nurture Engine initialized")
    
    async def process_attendance_data(self, sync_date: date = None) -> Dict[str, Any]:
        """
        Main entry point: process attendance data and trigger nurture sequences
        """
        if not sync_date:
            sync_date = date.today()
            
        logger.info(f"🔄 Processing attendance nurture triggers for {sync_date}")
        
        stats = {
            'date': sync_date.isoformat(),
            'meetings_processed': 0,
            'attendance_events': 0,
            'nurture_sequences_triggered': 0,
            'messages_queued': 0,
            'processing_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # 1. Get attendance data for the date
            attendance_data = await self._get_attendance_data(sync_date)
            stats['meetings_processed'] = len(attendance_data)
            
            # 2. Analyze attendance patterns and generate events
            attendance_events = await self._analyze_attendance_patterns(attendance_data)
            stats['attendance_events'] = len(attendance_events)
            
            # 3. Process each attendance event
            for event in attendance_events:
                await self._process_attendance_event(event)
                stats['nurture_sequences_triggered'] += 1
            
            # 4. Process scheduled weekly nurture touchpoints
            weekly_messages = await self._process_weekly_nurture_schedule(sync_date)
            stats['messages_queued'] += len(weekly_messages)
            
            # 5. Deliver queued messages
            delivery_results = await self._deliver_queued_messages()
            stats.update(delivery_results)
            
        except Exception as e:
            logger.error(f"❌ Error processing attendance nurture: {e}")
            raise
        
        finally:
            stats['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Attendance nurture processing completed: {stats}")
        return stats
    
    async def _get_attendance_data(self, sync_date: date) -> List[Dict[str, Any]]:
        """Get attendance data for analysis"""
        
        try:
            # Get meetings for the date
            meetings_result = self.supabase.table('pod_meetings').select(
                'id, pod_id, meeting_date, status, created_at'
            ).eq('meeting_date', sync_date.isoformat()).execute()
            
            meetings = meetings_result.data
            logger.info(f"📋 Found {len(meetings)} meetings for {sync_date}")
            
            attendance_data = []
            
            for meeting in meetings:
                # Get attendance records for this meeting
                attendance_result = self.supabase.table('meeting_attendance').select(
                    'user_id, attended, duration_minutes'
                ).eq('meeting_id', meeting['id']).execute()
                
                # Get Meet session data if available
                try:
                    meet_sessions_result = self.supabase.table('meet_sessions').select(
                        'meet_code, session_start, session_end, participant_count'
                    ).eq('meeting_id', meeting['id']).execute()
                except Exception as e:
                    logger.debug(f"Meet sessions query failed (table may not exist): {e}")
                    meet_sessions_result = type('MockResult', (), {'data': []})  # Empty result
                
                # Get Meet participants if available
                try:
                    meet_participants_result = self.supabase.table('meet_participants').select(
                        'email, joined_at, left_at, duration_minutes'
                    ).eq('meeting_id', meeting['id']).execute()
                except Exception as e:
                    logger.debug(f"Meet participants query failed (table may not exist): {e}")
                    meet_participants_result = type('MockResult', (), {'data': []})  # Empty result
                
                attendance_data.append({
                    'meeting': meeting,
                    'attendance_records': attendance_result.data,
                    'meet_sessions': meet_sessions_result.data,
                    'meet_participants': meet_participants_result.data
                })
            
            return attendance_data
            
        except Exception as e:
            logger.error(f"❌ Error getting attendance data: {e}")
            return []
    
    async def _analyze_attendance_patterns(self, attendance_data: List[Dict[str, Any]]) -> List[AttendanceEvent]:
        """Analyze attendance patterns and generate trigger events"""
        
        events = []
        
        for meeting_data in attendance_data:
            meeting = meeting_data['meeting']
            attendance_records = meeting_data['attendance_records']
            meet_participants = meeting_data['meet_participants']
            
            # Get pod members for this meeting
            pod_members = await self._get_pod_members(meeting['pod_id'])
            
            for member in pod_members:
                user_id = member['user_id']
                
                # Check if user attended
                user_attendance = next(
                    (record for record in attendance_records if record['user_id'] == user_id),
                    None
                )
                
                user_meet_data = next(
                    (participant for participant in meet_participants 
                     if participant['email'] == member.get('email')),
                    None
                )
                
                # Generate attendance events based on patterns
                if user_attendance and user_attendance['attended']:
                    # User attended - check for patterns
                    
                    # Check if this is their first meeting
                    if await self._is_first_meeting_attendance(user_id):
                        events.append(AttendanceEvent(
                            user_id=user_id,
                            trigger_type=AttendanceTrigger.FIRST_MEETING_ATTENDED,
                            meeting_id=meeting['id'],
                            event_time=datetime.now(),
                            metadata={
                                'meeting_date': meeting['meeting_date'],
                                'pod_id': meeting['pod_id']
                            }
                        ))
                    
                    # Check arrival time (if Meet data available)
                    if user_meet_data and user_meet_data.get('joined_at'):
                        join_time = datetime.fromisoformat(user_meet_data['joined_at'])
                        meeting_time = datetime.fromisoformat(f"{meeting['meeting_date']}T{meeting.get('meeting_time', '18:00:00')}")
                        
                        minutes_early = (meeting_time - join_time).total_seconds() / 60
                        
                        if minutes_early >= 5:  # 5+ minutes early
                            events.append(AttendanceEvent(
                                user_id=user_id,
                                trigger_type=AttendanceTrigger.EARLY_ARRIVAL,
                                meeting_id=meeting['id'],
                                event_time=join_time,
                                metadata={
                                    'minutes_early': minutes_early,
                                    'join_time': user_meet_data['joined_at']
                                }
                            ))
                        elif minutes_early < -10:  # 10+ minutes late
                            events.append(AttendanceEvent(
                                user_id=user_id,
                                trigger_type=AttendanceTrigger.LATE_ARRIVAL,
                                meeting_id=meeting['id'],
                                event_time=join_time,
                                metadata={
                                    'minutes_late': abs(minutes_early),
                                    'join_time': user_meet_data['joined_at']
                                }
                            ))
                    
                    # Check for perfect week attendance
                    if await self._check_perfect_week_attendance(user_id, meeting['meeting_date']):
                        events.append(AttendanceEvent(
                            user_id=user_id,
                            trigger_type=AttendanceTrigger.WEEK_PERFECT_ATTENDANCE,
                            meeting_id=meeting['id'],
                            event_time=datetime.now(),
                            metadata={'week_of': meeting['meeting_date']}
                        ))
                
                else:
                    # User missed meeting
                    events.append(AttendanceEvent(
                        user_id=user_id,
                        trigger_type=AttendanceTrigger.MEETING_MISSED,
                        meeting_id=meeting['id'],
                        event_time=datetime.now(),
                        metadata={
                            'meeting_date': meeting['meeting_date'],
                            'pod_id': meeting['pod_id']
                        }
                    ))
                    
                    # Check if this breaks a streak
                    if await self._check_streak_broken(user_id):
                        events.append(AttendanceEvent(
                            user_id=user_id,
                            trigger_type=AttendanceTrigger.STREAK_BROKEN,
                            meeting_id=meeting['id'],
                            event_time=datetime.now(),
                            metadata={'previous_streak_length': await self._get_previous_streak(user_id)}
                        ))
        
        logger.info(f"📊 Generated {len(events)} attendance events")
        return events
    
    async def _process_attendance_event(self, event: AttendanceEvent):
        """Process a single attendance event and trigger appropriate nurture sequence"""
        
        try:
            # Get user info
            user_result = self.supabase.table('users').select(
                'telegram_user_id, first_name, last_name, email'
            ).eq('id', event.user_id).single().execute()
            
            if not user_result.data:
                logger.warning(f"⚠️ User {event.user_id} not found")
                return
            
            user = user_result.data
            
            # Generate appropriate message based on trigger type
            message = await self._generate_attendance_message(event, user)
            
            if message:
                # Schedule message for delivery
                await self._schedule_message(
                    user_id=event.user_id,
                    telegram_user_id=user['telegram_user_id'],
                    message=message,
                    send_time=datetime.now()  # Immediate delivery for attendance events
                )
                
                logger.info(f"📨 Scheduled {event.trigger_type.value} message for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing attendance event {event.trigger_type}: {e}")
    
    async def _generate_attendance_message(self, event: AttendanceEvent, user: Dict[str, Any]) -> Optional[str]:
        """Generate personalized message based on attendance event"""
        
        first_name = user.get('first_name', 'there')
        
        if event.trigger_type == AttendanceTrigger.FIRST_MEETING_ATTENDED:
            return f"""🎉 **{first_name}, welcome to your pod!**

You just attended your first meeting - what an amazing step toward your goals!

Your pod mates are excited to support you on this journey. The real magic happens in the consistency.

💪 **Keep the momentum going!** Your next meeting is your chance to build on today's progress.

Ready to make this week count? 🚀"""

        elif event.trigger_type == AttendanceTrigger.EARLY_ARRIVAL:
            minutes_early = event.metadata.get('minutes_early', 0)
            return f"""⭐ **{first_name}, you're setting the standard!**

Arriving {minutes_early:.0f} minutes early shows real commitment to your growth.

Early birds don't just catch the worm - they set the tone for everyone else's success too.

Your pod mates notice this kind of leadership. Keep inspiring! 🌅"""

        elif event.trigger_type == AttendanceTrigger.LATE_ARRIVAL:
            minutes_late = event.metadata.get('minutes_late', 0)
            return f"""💙 **{first_name}, glad you made it!**

I know life gets crazy - arriving {minutes_late:.0f} minutes late is still showing up, and that matters.

Pro tip: Try setting a reminder 15 minutes before your next pod meeting. Your future self (and pod mates) will thank you!

Progress isn't perfection - it's persistence. 🎯"""

        elif event.trigger_type == AttendanceTrigger.MEETING_MISSED:
            return f"""💙 **{first_name}, we missed you today!**

Life happens, and that's totally okay. Your pod mates were thinking about you.

The beautiful thing about progress? Every day is a new chance to show up for yourself.

Your next meeting is an opportunity to jump back in. Your goals are still waiting for you! 🌟

Want to share what's on your mind? I'm here to listen."""

        elif event.trigger_type == AttendanceTrigger.WEEK_PERFECT_ATTENDANCE:
            return f"""🏆 **{first_name}, you're on FIRE!**

Perfect attendance this week! You're proving that consistency is your superpower.

This is how dreams become reality - one meeting, one commitment, one week at a time.

Your pod is lucky to have someone who shows up like you do. Keep building that momentum! 🚀"""

        elif event.trigger_type == AttendanceTrigger.STREAK_BROKEN:
            streak_length = event.metadata.get('previous_streak_length', 0)
            return f"""💪 **{first_name}, streaks are meant to be rebuilt!**

You had an amazing {streak_length}-meeting streak - that shows you've got what it takes.

One missed meeting doesn't erase all that progress. Champions get back up, and that's exactly what you'll do.

Your next meeting is your comeback moment. Ready to start a new streak? 🔥"""

        return None
    
    async def _process_weekly_nurture_schedule(self, sync_date: date) -> List[Dict[str, Any]]:
        """Process scheduled weekly nurture touchpoints"""
        
        weekday = sync_date.weekday()  # 0 = Monday, 6 = Sunday
        messages_queued = []
        
        # Get all active pod members
        pod_members = await self._get_all_active_pod_members()
        
        for member in pod_members:
            user_id = member['user_id']
            pod_id = member['pod_id']
            
            # Determine if today triggers a weekly nurture message
            weekly_message = None
            send_time = datetime.now()
            
            if weekday == 0:  # Monday - Week Launch
                weekly_message = await self._get_weekly_launch_message(user_id, pod_id)
                send_time = send_time.replace(hour=9, minute=0, second=0)  # 9 AM
                
            elif weekday == 1:  # Tuesday - Meeting Prep
                weekly_message = await self._get_meeting_prep_message(user_id, pod_id)
                send_time = send_time.replace(hour=19, minute=0, second=0)  # 7 PM
                
            elif weekday == 4:  # Friday - Week Reflection
                weekly_message = await self._get_week_reflection_message(user_id, pod_id)
                send_time = send_time.replace(hour=16, minute=0, second=0)  # 4 PM
                
            elif weekday == 6:  # Sunday - Next Week Prep
                weekly_message = await self._get_week_visioning_message(user_id, pod_id)
                send_time = send_time.replace(hour=18, minute=0, second=0)  # 6 PM
            
            if weekly_message:
                await self._schedule_message(
                    user_id=user_id,
                    telegram_user_id=member['telegram_user_id'],
                    message=weekly_message,
                    send_time=send_time
                )
                messages_queued.append({
                    'user_id': user_id,
                    'message_type': f'weekly_{weekday}',
                    'send_time': send_time
                })
        
        logger.info(f"📅 Queued {len(messages_queued)} weekly nurture messages")
        return messages_queued
    
    async def _schedule_message(self, user_id: str, telegram_user_id: int, message: str, send_time: datetime):
        """Schedule a message for delivery"""
        
        # In production, this would use Redis or a proper message queue
        # For now, store in database table
        
        try:
            self.supabase.table('nurture_message_queue').insert({
                'user_id': user_id,
                'telegram_user_id': telegram_user_id,
                'message_content': message,
                'scheduled_for': send_time.isoformat(),
                'created_at': datetime.now().isoformat()
            }).execute()
            
            logger.debug(f"📝 Message scheduled for user {user_id} at {send_time}")
            
        except Exception as e:
            logger.error(f"❌ Error scheduling message: {e}")
    
    async def _deliver_queued_messages(self) -> Dict[str, int]:
        """Deliver messages that are ready to be sent"""
        
        stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'messages_skipped': 0
        }
        
        try:
            # Get messages ready for delivery
            now = datetime.now()
            result = self.supabase.table('nurture_message_queue').select('*').lte(
                'scheduled_for', now.isoformat()
            ).is_('sent_at', 'null').execute()
            
            pending_messages = result.data
            logger.info(f"📨 Processing {len(pending_messages)} pending messages")
            
            for message in pending_messages:
                try:
                    # Check safety controls before sending
                    # Get user email to check authorization
                    user_result = self.supabase.table('users').select('email').eq(
                        'id', message['user_id']
                    ).single().execute()
                    
                    if user_result.data and user_result.data.get('email'):
                        user_email = user_result.data['email']
                        if not safety_controls.is_email_authorized(user_email):
                            stats['messages_skipped'] += 1
                            logger.debug(f"⏭️ Skipped message to unauthorized user {user_email}")
                            continue
                    else:
                        # No email found, skip for safety
                        stats['messages_skipped'] += 1
                        logger.warning(f"⚠️ No email found for user {message['user_id']}, skipping message")
                        continue
                    
                    # Send message via Telegram bot
                    success = await self._send_telegram_message(
                        message['telegram_user_id'],
                        message['message_content']
                    )
                    
                    if success:
                        # Mark as sent
                        self.supabase.table('nurture_message_queue').update({
                            'sent_at': datetime.now().isoformat()
                        }).eq('id', message['id']).execute()
                        
                        stats['messages_sent'] += 1
                        logger.debug(f"✅ Message sent to user {message['user_id']}")
                    else:
                        # Mark as failed
                        self.supabase.table('nurture_message_queue').update({
                            'failed_at': datetime.now().isoformat(),
                            'retry_count': message.get('retry_count', 0) + 1
                        }).eq('id', message['id']).execute()
                        
                        stats['messages_failed'] += 1
                        logger.warning(f"⚠️ Message failed for user {message['user_id']}")
                
                except Exception as e:
                    logger.error(f"❌ Error delivering message {message['id']}: {e}")
                    stats['messages_failed'] += 1
        
        except Exception as e:
            logger.error(f"❌ Error in message delivery: {e}")
        
        logger.info(f"📊 Message delivery complete: {stats}")
        return stats
    
    async def _send_telegram_message(self, telegram_user_id: int, message: str) -> bool:
        """Send message via Telegram bot"""
        
        try:
            # Import here to avoid circular imports
            from telbot import TelBot
            
            bot = TelBot()
            await bot.send_message(telegram_user_id, message, parse_mode='Markdown')
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending Telegram message: {e}")
            return False
    
    # Helper methods for attendance pattern analysis
    
    async def _get_pod_members(self, pod_id: str) -> List[Dict[str, Any]]:
        """Get all members of a pod"""
        try:
            result = self.supabase.table('pod_memberships').select(
                'user_id, users(telegram_user_id, first_name, email)'
            ).eq('pod_id', pod_id).execute()
            
            return [
                {
                    'user_id': member['user_id'],
                    'telegram_user_id': member['users']['telegram_user_id'],
                    'first_name': member['users']['first_name'],
                    'email': member['users']['email']
                }
                for member in result.data
            ]
        except Exception as e:
            logger.error(f"❌ Error getting pod members: {e}")
            return []
    
    async def _get_all_active_pod_members(self) -> List[Dict[str, Any]]:
        """Get all active pod members across all pods"""
        try:
            result = self.supabase.table('pod_memberships').select(
                'user_id, pod_id, users(telegram_user_id, first_name, email)'
            ).execute()
            
            return [
                {
                    'user_id': member['user_id'],
                    'pod_id': member['pod_id'],
                    'telegram_user_id': member['users']['telegram_user_id'],
                    'first_name': member['users']['first_name'],
                    'email': member['users']['email']
                }
                for member in result.data
            ]
        except Exception as e:
            logger.error(f"❌ Error getting all pod members: {e}")
            return []
    
    async def _is_first_meeting_attendance(self, user_id: str) -> bool:
        """Check if this is user's first meeting attendance"""
        try:
            result = self.supabase.table('meeting_attendance').select('id').eq(
                'user_id', user_id
            ).eq('attended', True).execute()
            
            return len(result.data) == 1  # Only one attendance record (this one)
        except:
            return False
    
    async def _check_perfect_week_attendance(self, user_id: str, meeting_date: str) -> bool:
        """Check if user has perfect attendance for the week"""
        try:
            # Get start of week (Monday)
            date_obj = datetime.strptime(meeting_date, '%Y-%m-%d').date()
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Get all meetings for user this week
            result = self.supabase.table('meeting_attendance').select(
                'attended'
            ).eq('user_id', user_id).gte(
                'meeting_date', week_start.isoformat()
            ).lte(
                'meeting_date', week_end.isoformat()
            ).execute()
            
            if not result.data:
                return False
            
            # Check if all attended
            return all(record['attended'] for record in result.data)
        except:
            return False
    
    async def _check_streak_broken(self, user_id: str) -> bool:
        """Check if user's attendance streak was broken"""
        # Simplified - in production would track streaks in separate table
        return False
    
    async def _get_previous_streak(self, user_id: str) -> int:
        """Get user's previous attendance streak length"""
        # Simplified - would calculate from attendance history
        return 3
    
    # Weekly nurture message generators
    
    async def _get_weekly_launch_message(self, user_id: str, pod_id: str) -> Optional[str]:
        """Generate Monday morning launch message"""
        
        user_result = self.supabase.table('users').select('first_name').eq('id', user_id).single().execute()
        first_name = user_result.data.get('first_name', 'there') if user_result.data else 'there'
        
        return f"""🌅 **Good morning, {first_name}!**

New week, new possibilities! Your pod journey continues today.

🎯 **This week's focus:** What's the ONE thing you want to make progress on?

Your pod mates are starting their week too - what legacy will you all create together?

Try: `/commit [your weekly focus]`

Let's make this week count! 💪"""
    
    async def _get_meeting_prep_message(self, user_id: str, pod_id: str) -> Optional[str]:
        """Generate Tuesday meeting prep message"""
        
        # Get next meeting info
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        meeting_result = self.supabase.table('pod_meetings').select(
            'meeting_time, title'
        ).eq('pod_id', pod_id).eq('meeting_date', tomorrow.isoformat()).execute()
        
        if not meeting_result.data:
            return None
        
        meeting = meeting_result.data[0]
        meeting_time = meeting.get('meeting_time', '6:00 PM')
        
        user_result = self.supabase.table('users').select('first_name').eq('id', user_id).single().execute()
        first_name = user_result.data.get('first_name', 'there') if user_result.data else 'there'
        
        return f"""🗓️ **{first_name}, tomorrow's your pod meeting!**

**Time:** {meeting_time}
**Focus:** Your progress and next steps

💭 **Come prepared to share:**
• One win from this week
• One challenge you're facing  
• What support you need from your pod

Your voice matters. Your pod mates are excited to hear from you! 🌟"""
    
    async def _get_week_reflection_message(self, user_id: str, pod_id: str) -> Optional[str]:
        """Generate Friday reflection message"""
        
        user_result = self.supabase.table('users').select('first_name').eq('id', user_id).single().execute()
        first_name = user_result.data.get('first_name', 'there') if user_result.data else 'there'
        
        return f"""🌟 **{first_name}, how was your week?**

Friday is for celebrating progress - no matter how small!

🎯 **This week you:**
• Showed up for your goals
• Connected with your pod
• Moved closer to your dreams

What's one thing you're proud of from this week?

Every step forward matters. You're building something amazing! 💫"""
    
    async def _get_week_visioning_message(self, user_id: str, pod_id: str) -> Optional[str]:
        """Generate Sunday visioning message"""
        
        user_result = self.supabase.table('users').select('first_name').eq('id', user_id).single().execute()
        first_name = user_result.data.get('first_name', 'there') if user_result.data else 'there'
        
        return f"""🌅 **{first_name}, tomorrow starts a new chapter!**

Sunday evening is perfect for setting intentions for the week ahead.

💭 **Reflect on:**
• What worked well this week?
• What would you do differently?
• What's your focus for next week?

Your pod meeting is your anchor. Everything else builds from there.

Ready to make next week even better? 🚀"""


# Command line interface for testing and manual execution
async def main():
    """Main entry point for manual execution"""
    import argparse
    from datetime import date
    
    parser = argparse.ArgumentParser(description="Attendance Nurture Engine")
    parser.add_argument('--sync-date', type=str, help='Date to sync (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Run without sending messages')
    
    args = parser.parse_args()
    
    sync_date = None
    if args.sync_date:
        if args.sync_date == 'today':
            sync_date = date.today()
        else:
            sync_date = datetime.strptime(args.sync_date, '%Y-%m-%d').date()
    
    engine = AttendanceNurtureEngine()
    
    if args.dry_run:
        logger.info("🧪 Running in DRY RUN mode - no messages will be sent")
        # Temporarily disable message sending for dry run
    
    results = await engine.process_attendance_data(sync_date)
    
    print("Attendance Nurture Engine Results:")
    print("=" * 40)
    for key, value in results.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())