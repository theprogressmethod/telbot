#!/usr/bin/env python3
"""
Google Meet REST API Integration for Automated Attendance Tracking
Integrates with the existing attendance system for seamless pod meeting management
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

logger = logging.getLogger(__name__)

class GoogleMeetIntegration:
    """Google Meet REST API integration for attendance tracking"""
    
    def __init__(self, service_account_file: str = None, project_id: str = None):
        self.service_account_file = service_account_file or os.getenv('GOOGLE_MEET_SERVICE_ACCOUNT_FILE')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        
        # Required scopes
        self.scopes = [
            'https://www.googleapis.com/auth/meetings.space.created',
            'https://www.googleapis.com/auth/meetings.space.readonly'
        ]
        
        self.service = None
        self.credentials = None
        
        logger.info("🔗 Google Meet integration initialized")
    
    async def initialize(self):
        """Initialize Google Meet API connection"""
        try:
            if not self.service_account_file:
                raise ValueError("Google Meet service account file not configured")
            
            # Load service account credentials
            self.credentials = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=self.scopes
            )
            
            # Build the Meet API service - try different versions
            try:
                self.service = build('meet', 'v2', credentials=self.credentials)
            except Exception as e1:
                logger.warning(f"⚠️ Failed to build Meet v2 API, trying v1: {e1}")
                try:
                    self.service = build('meet', 'v1', credentials=self.credentials)
                except Exception as e2:
                    logger.error(f"❌ Failed to build Meet v1 API: {e2}")
                    # Try with cache_discovery=False
                    logger.info("🔄 Trying with cache_discovery=False...")
                    self.service = build('meet', 'v2', credentials=self.credentials, cache_discovery=False)
            
            logger.info("✅ Google Meet API connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Meet API: {e}")
            return False
    
    async def create_meeting_space(self, pod_name: str, meeting_date: str) -> Dict[str, Any]:
        """Create a Google Meet space for a pod meeting"""
        try:
            if not self.service:
                await self.initialize()
            
            # Create meeting space
            space_request = {
                'config': {
                    'access_type': 'OPEN',  # or 'TRUSTED' for workspace only
                    'entry_point_access': 'ALL'
                }
            }
            
            # Create the space
            space = self.service.spaces().create(body=space_request).execute()
            
            space_info = {
                'space_id': space['name'],  # Format: spaces/{space_id}
                'meeting_uri': space['meetingUri'],
                'meeting_code': space['meetingCode'],
                'config': space.get('config', {}),
                'created_time': space.get('createTime'),
                'pod_name': pod_name,
                'meeting_date': meeting_date
            }
            
            logger.info(f"✅ Created Google Meet space for {pod_name}: {space_info['meeting_code']}")
            return space_info
            
        except HttpError as e:
            logger.error(f"❌ Google Meet API error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error creating meeting space: {e}")
            raise
    
    async def get_meeting_participants(self, space_id: str) -> List[Dict[str, Any]]:
        """Get list of participants who joined the meeting"""
        try:
            if not self.service:
                await self.initialize()
            
            # Get participant sessions
            participants_response = self.service.spaces().participants().list(
                parent=space_id
            ).execute()
            
            participants = []
            
            for participant in participants_response.get('participants', []):
                participant_info = {
                    'participant_id': participant['name'],
                    'anonymous_id': participant.get('anonymousId'),
                    'user_info': participant.get('signedinUser', {}),
                    'earliest_start_time': participant.get('earliestStartTime'),
                    'latest_end_time': participant.get('latestEndTime')
                }
                participants.append(participant_info)
            
            logger.info(f"📊 Retrieved {len(participants)} participants for space {space_id}")
            return participants
            
        except HttpError as e:
            logger.error(f"❌ Google Meet API error getting participants: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting meeting participants: {e}")
            return []
    
    async def get_participant_sessions(self, space_id: str, participant_id: str) -> List[Dict[str, Any]]:
        """Get detailed session information for a specific participant"""
        try:
            if not self.service:
                await self.initialize()
            
            # Get participant sessions
            sessions_response = self.service.spaces().participants().participantSessions().list(
                parent=f"{space_id}/participants/{participant_id}"
            ).execute()
            
            sessions = []
            for session in sessions_response.get('participantSessions', []):
                session_info = {
                    'session_id': session['name'],
                    'start_time': session.get('startTime'),
                    'end_time': session.get('endTime'),
                    'duration_seconds': self._calculate_duration(
                        session.get('startTime'), 
                        session.get('endTime')
                    )
                }
                sessions.append(session_info)
            
            return sessions
            
        except HttpError as e:
            logger.error(f"❌ Google Meet API error getting sessions: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting participant sessions: {e}")
            return []
    
    async def get_meeting_attendance_data(self, space_id: str) -> Dict[str, Any]:
        """Get comprehensive attendance data for a meeting"""
        try:
            # Get all participants
            participants = await self.get_meeting_participants(space_id)
            
            attendance_data = {
                'space_id': space_id,
                'total_participants': len(participants),
                'participants': [],
                'meeting_stats': {
                    'earliest_join': None,
                    'latest_leave': None,
                    'total_duration_minutes': 0
                }
            }
            
            earliest_time = None
            latest_time = None
            
            for participant in participants:
                # Get detailed sessions for each participant
                participant_id = participant['participant_id'].split('/')[-1]
                sessions = await self.get_participant_sessions(space_id, participant_id)
                
                total_duration = sum(s.get('duration_seconds', 0) for s in sessions)
                
                participant_data = {
                    **participant,
                    'sessions': sessions,
                    'total_duration_seconds': total_duration,
                    'total_duration_minutes': round(total_duration / 60, 1),
                    'attended': total_duration > 0  # Consider attended if any duration
                }
                
                attendance_data['participants'].append(participant_data)
                
                # Track meeting bounds
                if participant.get('earliest_start_time'):
                    if not earliest_time or participant['earliest_start_time'] < earliest_time:
                        earliest_time = participant['earliest_start_time']
                
                if participant.get('latest_end_time'):
                    if not latest_time or participant['latest_end_time'] > latest_time:
                        latest_time = participant['latest_end_time']
            
            # Calculate meeting stats
            attendance_data['meeting_stats']['earliest_join'] = earliest_time
            attendance_data['meeting_stats']['latest_leave'] = latest_time
            
            if earliest_time and latest_time:
                meeting_duration = self._calculate_duration(earliest_time, latest_time)
                attendance_data['meeting_stats']['total_duration_minutes'] = round(meeting_duration / 60, 1)
            
            logger.info(f"📊 Processed attendance data for {len(participants)} participants")
            return attendance_data
            
        except Exception as e:
            logger.error(f"❌ Error getting meeting attendance data: {e}")
            return {'error': str(e)}
    
    async def sync_attendance_to_system(self, space_id: str, meeting_id: str, attendance_system) -> Dict[str, Any]:
        """Sync Google Meet attendance data to our attendance system"""
        try:
            # Get attendance data from Google Meet
            meet_data = await self.get_meeting_attendance_data(space_id)
            
            if 'error' in meet_data:
                return {'error': meet_data['error']}
            
            sync_results = {
                'meeting_id': meeting_id,
                'space_id': space_id,
                'synced_records': 0,
                'failed_records': 0,
                'participants_processed': meet_data['total_participants'],
                'sync_timestamp': datetime.now().isoformat()
            }
            
            # Process each participant
            for participant in meet_data['participants']:
                try:
                    # Try to match participant to a user in our system
                    user_id = await self._match_participant_to_user(participant)
                    
                    if user_id:
                        # Record attendance in our system
                        await attendance_system.record_attendance(
                            meeting_id=meeting_id,
                            user_id=user_id,
                            attended=participant['attended'],
                            duration_minutes=int(participant['total_duration_minutes'])
                        )
                        sync_results['synced_records'] += 1
                        logger.info(f"✅ Synced attendance for user {user_id}")
                    else:
                        logger.warning(f"⚠️ Could not match participant to user: {participant.get('user_info', {})}")
                        sync_results['failed_records'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing participant {participant.get('participant_id')}: {e}")
                    sync_results['failed_records'] += 1
            
            logger.info(f"🔄 Sync completed: {sync_results['synced_records']} synced, {sync_results['failed_records']} failed")
            return sync_results
            
        except Exception as e:
            logger.error(f"❌ Error syncing attendance: {e}")
            return {'error': str(e)}
    
    async def _match_participant_to_user(self, participant: Dict[str, Any]) -> Optional[str]:
        """Match Google Meet participant to user in our system"""
        try:
            user_info = participant.get('user_info', {})
            
            # Try to match by email first
            email = user_info.get('email')
            if email:
                # TODO: Query your user database to find user by email
                # For now, return None - this needs to be implemented based on your user schema
                pass
            
            # Try to match by display name
            display_name = user_info.get('displayName')
            if display_name:
                # TODO: Query user database to find user by name
                pass
            
            # For now, return None - implement based on your user matching logic
            return None
            
        except Exception as e:
            logger.error(f"❌ Error matching participant: {e}")
            return None
    
    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """Calculate duration in seconds between two ISO timestamps"""
        try:
            if not start_time or not end_time:
                return 0
            
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            return int((end - start).total_seconds())
            
        except Exception as e:
            logger.error(f"❌ Error calculating duration: {e}")
            return 0
    
    async def cleanup_old_spaces(self, days_old: int = 30):
        """Clean up old meeting spaces (optional maintenance)"""
        try:
            # This is a maintenance function to clean up old spaces
            # Google Meet spaces may have automatic cleanup, but this provides manual control
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            logger.info(f"🧹 Cleaning up spaces older than {days_old} days")
            
            # Implementation would depend on how you track created spaces
            # You might want to store space IDs in your database with creation timestamps
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Integration helper functions

async def create_pod_meeting_with_google_meet(
    attendance_system, 
    meet_integration: GoogleMeetIntegration,
    pod_id: str, 
    pod_name: str, 
    meeting_date: str
) -> Dict[str, Any]:
    """Create a pod meeting with integrated Google Meet space"""
    try:
        # Create the pod meeting in our system
        meeting = await attendance_system.create_pod_meeting(
            pod_id=pod_id,
            meeting_date=meeting_date,
            status="scheduled"
        )
        
        # Create Google Meet space
        space_info = await meet_integration.create_meeting_space(
            pod_name=pod_name,
            meeting_date=meeting_date
        )
        
        # TODO: Store space_info in meeting metadata or separate table
        # You might want to add a google_meet_space_id field to pod_meetings table
        
        return {
            'meeting_id': meeting.id,
            'pod_id': meeting.pod_id,
            'meeting_date': meeting.meeting_date,
            'google_meet': {
                'space_id': space_info['space_id'],
                'meeting_uri': space_info['meeting_uri'],
                'meeting_code': space_info['meeting_code']
            },
            'created_at': meeting.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating integrated meeting: {e}")
        raise

if __name__ == "__main__":
    print("Google Meet REST API Integration for Automated Attendance Tracking")
    print("Configure GOOGLE_MEET_SERVICE_ACCOUNT_FILE and GOOGLE_CLOUD_PROJECT_ID environment variables")