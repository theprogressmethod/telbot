#!/usr/bin/env python3
"""
Recurring Meeting Management System
Handles recurring meetings, schedules, and time management for pods
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
import logging
from dateutil.rrule import rrule, WEEKLY, DAILY, MONTHLY

logger = logging.getLogger(__name__)

class RecurrenceType(Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class WeekDay(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

@dataclass
class RecurringMeetingSchedule:
    """Defines a recurring meeting schedule for a pod"""
    id: str
    pod_id: str
    recurrence_type: RecurrenceType
    meeting_day: WeekDay  # Day of week for weekly/biweekly
    meeting_time: str  # HH:MM format (e.g., "19:00")
    timezone: str  # e.g., "America/New_York"
    duration_minutes: int  # Standard meeting duration
    start_date: datetime  # When the recurring series starts
    end_date: Optional[datetime]  # When the series ends (optional)
    google_calendar_event_id: Optional[str]  # For Google Calendar recurring event
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    def get_next_occurrence(self, after_date: datetime = None) -> datetime:
        """Get the next occurrence of this recurring meeting"""
        if after_date is None:
            after_date = datetime.now()
        
        # Parse meeting time
        hour, minute = map(int, self.meeting_time.split(':'))
        meeting_time_obj = time(hour, minute)
        
        # Calculate next occurrence based on recurrence type
        if self.recurrence_type == RecurrenceType.WEEKLY:
            # Find next occurrence on the specified weekday
            days_ahead = self.meeting_day.value - after_date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            next_date = after_date + timedelta(days=days_ahead)
            return datetime.combine(next_date.date(), meeting_time_obj)
        
        elif self.recurrence_type == RecurrenceType.BIWEEKLY:
            # Similar to weekly but skip every other week
            days_ahead = self.meeting_day.value - after_date.weekday()
            if days_ahead <= 0:
                days_ahead += 14  # Skip to next occurrence in 2 weeks
            else:
                # Check if this is an "off" week
                weeks_since_start = (after_date - self.start_date).days // 7
                if weeks_since_start % 2 == 1:
                    days_ahead += 7  # Skip to the "on" week
            
            next_date = after_date + timedelta(days=days_ahead)
            return datetime.combine(next_date.date(), meeting_time_obj)
        
        elif self.recurrence_type == RecurrenceType.MONTHLY:
            # Same day of month
            next_month = after_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=min(self.start_date.day, 
                                                    self._last_day_of_month(next_month)))
            return datetime.combine(next_month.date(), meeting_time_obj)
        
        return after_date
    
    def _last_day_of_month(self, any_day: datetime) -> int:
        """Get the last day of the month for a given date"""
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return (next_month - timedelta(days=next_month.day)).day
    
    def generate_occurrences(self, start: datetime, end: datetime) -> List[datetime]:
        """Generate all meeting occurrences between start and end dates"""
        occurrences = []
        
        # Parse meeting time
        hour, minute = map(int, self.meeting_time.split(':'))
        
        if self.recurrence_type == RecurrenceType.WEEKLY:
            freq = WEEKLY
            interval = 1
        elif self.recurrence_type == RecurrenceType.BIWEEKLY:
            freq = WEEKLY
            interval = 2
        elif self.recurrence_type == RecurrenceType.MONTHLY:
            freq = MONTHLY
            interval = 1
        else:
            return occurrences
        
        # Use dateutil.rrule for robust recurrence calculation
        rule = rrule(
            freq,
            interval=interval,
            byweekday=self.meeting_day.value if freq == WEEKLY else None,
            byhour=hour,
            byminute=minute,
            dtstart=max(self.start_date, start),
            until=min(self.end_date, end) if self.end_date else end
        )
        
        return list(rule)

class RecurringMeetingManager:
    """Manages recurring meetings for pods"""
    
    def __init__(self, supabase_client, attendance_system, google_calendar=None):
        self.supabase = supabase_client
        self.attendance_system = attendance_system
        self.google_calendar = google_calendar
        logger.info("📅 Recurring Meeting Manager initialized")
    
    async def create_recurring_schedule(
        self,
        pod_id: str,
        recurrence_type: RecurrenceType,
        meeting_day: WeekDay,
        meeting_time: str,
        timezone: str = "UTC",
        duration_minutes: int = 60,
        start_date: datetime = None,
        end_date: datetime = None,
        create_calendar_events: bool = True
    ) -> RecurringMeetingSchedule:
        """Create a new recurring meeting schedule for a pod"""
        
        if start_date is None:
            start_date = datetime.now()
        
        schedule_id = str(uuid.uuid4())
        
        schedule = RecurringMeetingSchedule(
            id=schedule_id,
            pod_id=pod_id,
            recurrence_type=recurrence_type,
            meeting_day=meeting_day,
            meeting_time=meeting_time,
            timezone=timezone,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date,
            google_calendar_event_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        # Save to database (you might want to create a recurring_schedules table)
        try:
            self.supabase.table("recurring_schedules").insert({
                "id": schedule.id,
                "pod_id": schedule.pod_id,
                "recurrence_type": schedule.recurrence_type.value,
                "meeting_day": schedule.meeting_day.value,
                "meeting_time": schedule.meeting_time,
                "timezone": schedule.timezone,
                "duration_minutes": schedule.duration_minutes,
                "start_date": schedule.start_date.isoformat(),
                "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
                "is_active": schedule.is_active,
                "created_at": schedule.created_at.isoformat(),
                "updated_at": schedule.updated_at.isoformat()
            }).execute()
            
            logger.info(f"✅ Created recurring schedule {schedule_id} for pod {pod_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not save to database (table may not exist): {e}")
        
        # Create Google Calendar recurring event if enabled
        if create_calendar_events and self.google_calendar:
            try:
                event_id = await self._create_google_calendar_recurring_event(schedule)
                schedule.google_calendar_event_id = event_id
                logger.info(f"📅 Created Google Calendar recurring event: {event_id}")
            except Exception as e:
                logger.error(f"❌ Failed to create Google Calendar event: {e}")
        
        # Generate initial meetings for the next month
        await self.generate_meetings_from_schedule(schedule, weeks_ahead=4)
        
        return schedule
    
    async def generate_meetings_from_schedule(
        self,
        schedule: RecurringMeetingSchedule,
        weeks_ahead: int = 4
    ) -> List[str]:
        """Generate individual meeting instances from a recurring schedule"""
        
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=weeks_ahead)
        
        occurrences = schedule.generate_occurrences(start_date, end_date)
        meeting_ids = []
        
        for occurrence in occurrences:
            # Check if meeting already exists for this date
            meeting_date = occurrence.date().isoformat()
            
            existing = self.supabase.table("pod_meetings").select("id").eq(
                "pod_id", schedule.pod_id
            ).eq("meeting_date", meeting_date).execute()
            
            if not existing.data:
                # Create the meeting
                meeting = await self.attendance_system.create_pod_meeting(
                    pod_id=schedule.pod_id,
                    meeting_date=meeting_date,
                    status="scheduled"
                )
                
                # Store additional metadata (time, duration, etc.)
                try:
                    self.supabase.table("pod_meetings").update({
                        "meeting_time": schedule.meeting_time,
                        "duration_minutes": schedule.duration_minutes,
                        "recurring_schedule_id": schedule.id
                    }).eq("id", meeting.id).execute()
                except:
                    pass  # Columns might not exist yet
                
                meeting_ids.append(meeting.id)
                logger.info(f"📅 Generated meeting {meeting.id} for {meeting_date}")
        
        return meeting_ids
    
    async def update_recurring_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> RecurringMeetingSchedule:
        """Update an existing recurring schedule"""
        
        # Update in database
        updates["updated_at"] = datetime.now().isoformat()
        
        result = self.supabase.table("recurring_schedules").update(
            updates
        ).eq("id", schedule_id).execute()
        
        if result.data:
            logger.info(f"✅ Updated recurring schedule {schedule_id}")
            
            # If schedule changed, regenerate future meetings
            if any(key in updates for key in ["meeting_day", "meeting_time", "recurrence_type"]):
                # Cancel future meetings and regenerate
                await self.cancel_future_meetings(schedule_id)
                # Regenerate based on new schedule
                # (implementation depends on your needs)
        
        return result.data[0] if result.data else None
    
    async def cancel_recurring_schedule(self, schedule_id: str):
        """Cancel a recurring schedule and all future meetings"""
        
        # Mark schedule as inactive
        self.supabase.table("recurring_schedules").update({
            "is_active": False,
            "updated_at": datetime.now().isoformat()
        }).eq("id", schedule_id).execute()
        
        # Cancel future meetings
        await self.cancel_future_meetings(schedule_id)
        
        logger.info(f"❌ Cancelled recurring schedule {schedule_id}")
    
    async def cancel_future_meetings(self, schedule_id: str):
        """Cancel all future meetings for a recurring schedule"""
        
        today = datetime.now().date().isoformat()
        
        # Update status of future meetings to cancelled
        self.supabase.table("pod_meetings").update({
            "status": "cancelled"
        }).eq("recurring_schedule_id", schedule_id).gte("meeting_date", today).execute()
        
        logger.info(f"❌ Cancelled future meetings for schedule {schedule_id}")
    
    async def _create_google_calendar_recurring_event(
        self,
        schedule: RecurringMeetingSchedule
    ) -> str:
        """Create a recurring event in Google Calendar"""
        
        if not self.google_calendar:
            return None
        
        # Build recurrence rule string (RFC 5545 format)
        if schedule.recurrence_type == RecurrenceType.WEEKLY:
            rrule_str = f"RRULE:FREQ=WEEKLY;BYDAY={self._weekday_to_rrule(schedule.meeting_day)}"
        elif schedule.recurrence_type == RecurrenceType.BIWEEKLY:
            rrule_str = f"RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY={self._weekday_to_rrule(schedule.meeting_day)}"
        elif schedule.recurrence_type == RecurrenceType.MONTHLY:
            rrule_str = f"RRULE:FREQ=MONTHLY;BYMONTHDAY={schedule.start_date.day}"
        else:
            rrule_str = ""
        
        if schedule.end_date:
            rrule_str += f";UNTIL={schedule.end_date.strftime('%Y%m%dT%H%M%SZ')}"
        
        # Parse meeting time
        hour, minute = map(int, schedule.meeting_time.split(':'))
        
        # Create the first occurrence
        first_occurrence = schedule.get_next_occurrence()
        
        event = {
            'summary': f'Pod Meeting - Recurring',
            'description': f'Regular pod meeting\nPod ID: {schedule.pod_id}',
            'start': {
                'dateTime': first_occurrence.isoformat(),
                'timeZone': schedule.timezone,
            },
            'end': {
                'dateTime': (first_occurrence + timedelta(minutes=schedule.duration_minutes)).isoformat(),
                'timeZone': schedule.timezone,
            },
            'recurrence': [rrule_str] if rrule_str else [],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'pod-recurring-{schedule.id}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        try:
            created_event = self.google_calendar.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='none'
            ).execute()
            
            return created_event['id']
        except Exception as e:
            logger.error(f"❌ Failed to create Google Calendar event: {e}")
            return None
    
    def _weekday_to_rrule(self, weekday: WeekDay) -> str:
        """Convert WeekDay enum to RRULE format"""
        mapping = {
            WeekDay.MONDAY: "MO",
            WeekDay.TUESDAY: "TU",
            WeekDay.WEDNESDAY: "WE",
            WeekDay.THURSDAY: "TH",
            WeekDay.FRIDAY: "FR",
            WeekDay.SATURDAY: "SA",
            WeekDay.SUNDAY: "SU"
        }
        return mapping[weekday]
    
    async def get_pod_schedules(self, pod_id: str) -> List[RecurringMeetingSchedule]:
        """Get all recurring schedules for a pod"""
        
        try:
            result = self.supabase.table("recurring_schedules").select("*").eq(
                "pod_id", pod_id
            ).eq("is_active", True).execute()
            
            schedules = []
            for data in result.data:
                schedule = RecurringMeetingSchedule(
                    id=data["id"],
                    pod_id=data["pod_id"],
                    recurrence_type=RecurrenceType(data["recurrence_type"]),
                    meeting_day=WeekDay(data["meeting_day"]),
                    meeting_time=data["meeting_time"],
                    timezone=data["timezone"],
                    duration_minutes=data["duration_minutes"],
                    start_date=datetime.fromisoformat(data["start_date"]),
                    end_date=datetime.fromisoformat(data["end_date"]) if data["end_date"] else None,
                    google_calendar_event_id=data.get("google_calendar_event_id"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    is_active=data["is_active"]
                )
                schedules.append(schedule)
            
            return schedules
            
        except Exception as e:
            logger.warning(f"Could not get schedules (table may not exist): {e}")
            return []

# Example usage
async def example_usage():
    """Example of how to use the recurring meeting system"""
    
    from telbot import Config
    from supabase import create_client
    from attendance_system_adapted import AttendanceSystemAdapted
    
    config = Config()
    supabase = create_client(config.supabase_url, config.supabase_key)
    attendance_system = AttendanceSystemAdapted(supabase)
    
    manager = RecurringMeetingManager(supabase, attendance_system)
    
    # Create a weekly recurring meeting for a pod
    # Every Wednesday at 7 PM Eastern
    schedule = await manager.create_recurring_schedule(
        pod_id="11111111-1111-1111-1111-111111111111",
        recurrence_type=RecurrenceType.WEEKLY,
        meeting_day=WeekDay.WEDNESDAY,
        meeting_time="19:00",
        timezone="America/New_York",
        duration_minutes=60,
        start_date=datetime(2025, 8, 20),  # Starting August 20, 2025
        end_date=None,  # No end date - continues indefinitely
        create_calendar_events=True
    )
    
    print(f"✅ Created recurring schedule: {schedule.id}")
    print(f"   Next meeting: {schedule.get_next_occurrence()}")
    
    # Generate meetings for the next 4 weeks
    meeting_ids = await manager.generate_meetings_from_schedule(schedule, weeks_ahead=4)
    print(f"📅 Generated {len(meeting_ids)} meetings")

if __name__ == "__main__":
    print("Recurring Meeting Management System")
    print("Handles weekly, biweekly, and monthly recurring meetings")
    print("Integrates with Google Calendar for automatic event creation")