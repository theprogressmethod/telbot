#!/usr/bin/env python3
"""
Google Calendar Integration for Meeting Attendance Tracking
Alternative to Google Meet REST API - uses Calendar API which is readily available
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from safety_controls import safety_controls, safe_send_calendar_invite

logger = logging.getLogger(__name__)

class GoogleCalendarAttendance:
    """Google Calendar integration for meeting attendance tracking"""
    
    def __init__(self, service_account_file: str = None, project_id: str = None, user_email: str = None):
        self.service_account_file = service_account_file or os.getenv('GOOGLE_MEET_SERVICE_ACCOUNT_FILE')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.user_email = user_email or os.getenv('GOOGLE_CALENDAR_USER_EMAIL')  # Your email for delegation
        
        # Required scopes for Calendar API
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
        self.service = None
        self.credentials = None
        
        logger.info("🗓️ Google Calendar attendance integration initialized")
    
    async def initialize(self):
        """Initialize Google Calendar API connection with Domain-Wide Delegation"""
        try:
            if not self.service_account_file:
                raise ValueError("Google service account file not configured")
            
            if not self.user_email:
                raise ValueError("User email not configured for Domain-Wide Delegation")
            
            # Load service account credentials with Domain-Wide Delegation
            self.credentials = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=self.scopes,
                subject=self.user_email  # This enables Domain-Wide Delegation
            )
            
            # Build the Calendar API service
            self.service = build('calendar', 'v3', credentials=self.credentials, cache_discovery=False)
            
            logger.info(f"✅ Google Calendar API connection established with Domain-Wide Delegation for {self.user_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Calendar API: {e}")
            return False
    
    async def create_pod_meeting_event(self, pod_name: str, meeting_date: str, 
                                     start_time: str = "19:00", duration_minutes: int = 60,
                                     attendee_emails: List[str] = None) -> Dict[str, Any]:
        """Create a Google Calendar event for a pod meeting WITH SAFETY CONTROLS"""
        try:
            if not self.service:
                await self.initialize()
            
            # SAFETY CHECK: Filter attendees to only authorized emails
            original_attendees = attendee_emails or []
            authorized_attendees, invite_allowed = safe_send_calendar_invite(original_attendees, {
                'pod_name': pod_name,
                'meeting_date': meeting_date,
                'start_time': start_time
            })
            
            if not invite_allowed:
                logger.error("🚫 Calendar invite creation blocked by safety controls")
                raise ValueError("Calendar invite creation blocked by safety controls")
            
            if len(authorized_attendees) != len(original_attendees):
                blocked_count = len(original_attendees) - len(authorized_attendees)
                logger.warning(f"⚠️ Safety controls filtered out {blocked_count} unauthorized attendees")
            
            # Parse meeting datetime
            start_datetime = datetime.fromisoformat(f"{meeting_date}T{start_time}:00")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Create event with Google Meet integration
            event = {
                'summary': f'{pod_name} - Pod Meeting [SAFE MODE]',
                'description': f'Weekly accountability pod meeting for {pod_name}\n\n🔒 Safety Mode: Only authorized attendees invited\nOriginal attendees: {len(original_attendees)}\nAuthorized attendees: {len(authorized_attendees)}',
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'pod-meeting-{pod_name.lower().replace(" ", "-")}-{meeting_date}',
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'attendees': [{'email': email} for email in authorized_attendees],  # Only authorized attendees
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                        {'method': 'popup', 'minutes': 10},       # 10 minutes before
                    ],
                },
                'guestsCanSeeOtherGuests': True,
                'guestsCanInviteOthers': False,
                'guestsCanModify': False
            }
            
            # SAFETY: Always create without sending invites in development
            # Only send invites to authorized attendees and only if explicitly enabled
            send_invites = 'none'  # SAFE DEFAULT - never send automatically
            
            if safety_controls.environment == 'production' and authorized_attendees:
                # In production, could send to authorized attendees only
                # But still default to 'none' for maximum safety
                send_invites = 'none'  # Keep safe even in production
                logger.info(f"🔒 Production mode: Would send invites to {len(authorized_attendees)} authorized attendees")
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,  # Required for Google Meet integration
                sendUpdates=send_invites  # SAFETY CONTROLLED
            ).execute()
            
            # Log what happened for audit trail
            logger.info(f"📅 Calendar event created: {event['summary']}")
            logger.info(f"   Attendees: {len(authorized_attendees)} authorized, {len(original_attendees) - len(authorized_attendees)} blocked")
            logger.info(f"   Invites sent: {send_invites}")
            logger.info(f"   Safety mode: {safety_controls.safety_mode.value}")
            
            # Extract meeting information
            meet_link = None
            meet_id = None
            
            if 'conferenceData' in created_event:
                conf_data = created_event['conferenceData']
                if 'entryPoints' in conf_data:
                    for entry in conf_data['entryPoints']:
                        if entry['entryPointType'] == 'video':
                            meet_link = entry['uri']
                            meet_id = conf_data.get('conferenceId')
                            break
            
            event_info = {
                'event_id': created_event['id'],
                'calendar_id': 'primary',
                'meeting_link': meet_link,
                'meeting_id': meet_id,
                'event_link': created_event.get('htmlLink'),
                'summary': created_event['summary'],
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime'],
                'attendees_count': len(attendee_emails or []),
                'pod_name': pod_name,
                'meeting_date': meeting_date
            }
            
            logger.info(f"✅ Created Calendar event for {pod_name}: {event_info['event_id']}")
            return event_info
            
        except HttpError as e:
            logger.error(f"❌ Google Calendar API error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error creating calendar event: {e}")
            raise
    
    async def get_event_attendance(self, event_id: str, calendar_id: str = 'primary') -> List[Dict[str, Any]]:
        """Get attendance information from a calendar event"""
        try:
            if not self.service:
                await self.initialize()
            
            # Get the event details
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            attendance_data = []
            
            # Parse attendees and their response status
            attendees = event.get('attendees', [])
            
            for attendee in attendees:
                attendee_info = {
                    'email': attendee['email'],
                    'response_status': attendee.get('responseStatus', 'needsAction'),  # needsAction, declined, tentative, accepted
                    'optional': attendee.get('optional', False),
                    'organizer': attendee.get('organizer', False),
                    'display_name': attendee.get('displayName', ''),
                    'attended': attendee.get('responseStatus') == 'accepted'  # Simple attendance based on acceptance
                }
                attendance_data.append(attendee_info)
            
            logger.info(f"📊 Retrieved attendance for {len(attendees)} attendees")
            return attendance_data
            
        except HttpError as e:
            logger.error(f"❌ Google Calendar API error getting attendance: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting event attendance: {e}")
            return []
    
    async def sync_calendar_attendance_to_system(self, event_id: str, meeting_id: str, attendance_system) -> Dict[str, Any]:
        """Sync Google Calendar attendance to our attendance system"""
        try:
            # Get attendance data from Google Calendar
            calendar_attendance = await self.get_event_attendance(event_id)
            
            sync_results = {
                'meeting_id': meeting_id,
                'event_id': event_id,
                'synced_records': 0,
                'failed_records': 0,
                'participants_processed': len(calendar_attendance),
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Process each attendee
            for attendee in calendar_attendance:
                try:
                    # Try to match attendee email to a user in our system
                    user_id = await self._match_email_to_user(attendee['email'])
                    
                    if user_id:
                        # Record attendance in our system
                        # Use response status to determine attendance
                        attended = attendee['response_status'] == 'accepted'
                        duration = 60 if attended else 0  # Default duration
                        
                        await attendance_system.record_attendance(
                            meeting_id=meeting_id,
                            user_id=user_id,
                            attended=attended,
                            duration_minutes=duration
                        )
                        sync_results['synced_records'] += 1
                        logger.info(f"✅ Synced attendance for {attendee['email']}")
                    else:
                        logger.warning(f"⚠️ Could not match email to user: {attendee['email']}")
                        sync_results['failed_records'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing attendee {attendee['email']}: {e}")
                    sync_results['failed_records'] += 1
            
            logger.info(f"🔄 Calendar sync completed: {sync_results['synced_records']} synced, {sync_results['failed_records']} failed")
            return sync_results
            
        except Exception as e:
            logger.error(f"❌ Error syncing calendar attendance: {e}")
            return {'error': str(e)}
    
    async def get_upcoming_pod_meetings(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming pod meetings from calendar"""
        try:
            if not self.service:
                await self.initialize()
            
            # Calculate time range
            now = datetime.now()
            time_max = now + timedelta(days=days_ahead)
            
            # Search for pod meetings
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                q='Pod Meeting',  # Search for events with "Pod Meeting" in title
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            upcoming_meetings = []
            for event in events:
                meeting_info = {
                    'event_id': event['id'],
                    'summary': event['summary'],
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                    'end_time': event['end'].get('dateTime', event['end'].get('date')),
                    'attendees_count': len(event.get('attendees', [])),
                    'has_meet_link': 'conferenceData' in event,
                    'event_link': event.get('htmlLink')
                }
                upcoming_meetings.append(meeting_info)
            
            logger.info(f"📅 Found {len(upcoming_meetings)} upcoming pod meetings")
            return upcoming_meetings
            
        except Exception as e:
            logger.error(f"❌ Error getting upcoming meetings: {e}")
            return []
    
    async def _match_email_to_user(self, email: str) -> Optional[str]:
        """Match email to user in our system"""
        try:
            # TODO: Implement based on your user schema
            # This should query your users table to find user by email
            # For now, return None - needs to be implemented
            
            # Example implementation:
            # result = supabase.table("users").select("id").eq("email", email).execute()
            # if result.data:
            #     return result.data[0]["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error matching email to user: {e}")
            return None

# Integration helper functions for main application

async def create_pod_meeting_with_google_calendar(
    attendance_system, 
    calendar_integration: GoogleCalendarAttendance,
    pod_id: str, 
    pod_name: str, 
    meeting_date: str,
    attendee_emails: List[str] = None
) -> Dict[str, Any]:
    """Create a pod meeting with integrated Google Calendar event"""
    try:
        # Create the pod meeting in our system
        meeting = await attendance_system.create_pod_meeting(
            pod_id=pod_id,
            meeting_date=meeting_date,
            status="scheduled"
        )
        
        # Create Google Calendar event with Meet link
        event_info = await calendar_integration.create_pod_meeting_event(
            pod_name=pod_name,
            meeting_date=meeting_date,
            attendee_emails=attendee_emails or []
        )
        
        # TODO: Store event_info in meeting metadata or separate table
        # You might want to add calendar_event_id field to pod_meetings table
        
        return {
            'meeting_id': meeting.id,
            'pod_id': meeting.pod_id,
            'meeting_date': meeting.meeting_date,
            'google_calendar': {
                'event_id': event_info['event_id'],
                'meeting_link': event_info['meeting_link'],
                'event_link': event_info['event_link']
            },
            'created_at': meeting.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating integrated calendar meeting: {e}")
        raise

if __name__ == "__main__":
    print("Google Calendar Integration for Pod Meeting Attendance Tracking")
    print("Provides Google Meet links and attendance tracking through Calendar API")