#!/usr/bin/env python3
"""
Meet Event Correlation Engine
Links Google Meet sessions to pod meetings and processes attendance data
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple, Set
import uuid
import re
from dataclasses import dataclass, asdict
from supabase import Client
from google_admin_reports import GoogleAdminReports, MeetEvent, MeetParticipant

logger = logging.getLogger(__name__)

@dataclass
class MeetSession:
    """Represents a tracked Google Meet session"""
    id: str
    meeting_id: str
    meet_event_id: Optional[str]
    meet_link: str
    meet_code: str
    organizer_email: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_minutes: Optional[int]
    participant_count: int
    total_minutes_all_participants: int
    sync_status: str
    last_sync_at: Optional[datetime]

@dataclass
class ParticipantMatch:
    """Represents a matched participant between Meet and our user system"""
    meet_participant_email: str
    user_id: Optional[str]
    user_email: Optional[str]
    confidence_score: float  # 0.0 to 1.0
    match_method: str  # 'exact_email', 'domain_match', 'manual_mapping', 'no_match'

class MeetCorrelationEngine:
    """Correlates Google Meet sessions with pod meetings and processes attendance"""
    
    def __init__(self, supabase_client: Client, admin_reports: GoogleAdminReports):
        self.supabase = supabase_client
        self.admin_reports = admin_reports
        self.domain = None  # Will be set from organization domain
        
        logger.info("🔗 Meet Correlation Engine initialized")
    
    async def initialize(self):
        """Initialize the correlation engine"""
        try:
            # Get organization domain from environment or config
            import os
            self.domain = os.getenv('ORGANIZATION_DOMAIN', 'theprogressmethod.com')
            logger.info(f"✅ Meet Correlation Engine ready for domain: {self.domain}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize correlation engine: {e}")
            raise
    
    async def create_meet_session(self, meeting_id: str, meet_event_id: str, 
                                 meet_link: str, organizer_email: str) -> str:
        """
        Create a new Meet session tracking record
        
        Args:
            meeting_id: Our internal pod meeting ID
            meet_event_id: Google Calendar event ID
            meet_link: Google Meet link URL
            organizer_email: Email of meeting organizer
        
        Returns:
            Meet session ID
        """
        try:
            # Extract Meet code from link
            meet_code = self._extract_meet_code(meet_link)
            if not meet_code:
                raise ValueError(f"Could not extract Meet code from link: {meet_link}")
            
            session_id = str(uuid.uuid4())
            
            # Insert into database
            session_data = {
                'id': session_id,
                'meeting_id': meeting_id,
                'meet_event_id': meet_event_id,
                'meet_link': meet_link,
                'meet_code': meet_code,
                'organizer_email': organizer_email,
                'participant_count': 0,
                'total_minutes_all_participants': 0,
                'sync_status': 'pending'
            }
            
            result = self.supabase.table('meet_sessions').insert(session_data).execute()
            
            logger.info(f"✅ Created Meet session {session_id} for meeting {meeting_id}")
            logger.info(f"   Meet code: {meet_code}, Link: {meet_link}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Meet session: {e}")
            raise
    
    async def sync_meet_session_data(self, session_id: str, 
                                    sync_date: date = None) -> Dict[str, Any]:
        """
        Sync attendance data for a specific Meet session
        
        Args:
            session_id: Meet session ID to sync
            sync_date: Date to search for Meet data (defaults to today)
        
        Returns:
            Dictionary with sync results
        """
        if not sync_date:
            sync_date = date.today()
        
        try:
            # Get session details from database
            session_result = self.supabase.table('meet_sessions').select('*').eq('id', session_id).execute()
            if not session_result.data:
                raise ValueError(f"Meet session {session_id} not found")
            
            session_data = session_result.data[0]
            meet_code = session_data['meet_code']
            
            logger.info(f"🔄 Syncing Meet session {session_id} (code: {meet_code}) for {sync_date}")
            
            # Update sync status
            await self._update_session_sync_status(session_id, 'syncing')
            
            # Get Meet events for this session
            participants = await self.admin_reports.get_meet_participants(
                meet_code, sync_date, sync_date
            )
            
            if not participants:
                logger.warning(f"⚠️ No Meet data found for session {session_id} on {sync_date}")
                await self._update_session_sync_status(session_id, 'no_data')
                return {'status': 'no_data', 'participants_found': 0}
            
            # Process participants and create attendance records
            results = await self._process_session_participants(session_id, participants)
            
            # Update session statistics
            await self._update_session_statistics(session_id, participants)
            
            # Mark as successfully synced
            await self._update_session_sync_status(session_id, 'synced')
            
            logger.info(f"✅ Successfully synced Meet session {session_id}")
            logger.info(f"   Found {len(participants)} participants, {results['matched_users']} matched to users")
            
            return {
                'status': 'success',
                'participants_found': len(participants),
                'matched_users': results['matched_users'],
                'new_attendance_records': results['new_records'],
                'updated_records': results['updated_records']
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to sync Meet session {session_id}: {e}")
            await self._update_session_sync_status(session_id, 'failed', str(e))
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_session_participants(self, session_id: str, 
                                          participants: List[MeetParticipant]) -> Dict[str, int]:
        """Process Meet participants and create/update attendance records"""
        results = {'matched_users': 0, 'new_records': 0, 'updated_records': 0}
        
        # Get session meeting ID
        session_result = self.supabase.table('meet_sessions').select('meeting_id').eq('id', session_id).execute()
        meeting_id = session_result.data[0]['meeting_id']
        
        for participant in participants:
            try:
                # Store raw participant data
                participant_id = await self._store_meet_participant(session_id, participant)
                
                # Match participant to our user system
                user_match = await self._match_participant_to_user(participant)
                
                if user_match.user_id:
                    results['matched_users'] += 1
                    
                    # Create or update attendance record
                    attendance_result = await self._create_attendance_record(
                        meeting_id, user_match.user_id, participant_id, participant, user_match
                    )
                    
                    if attendance_result == 'created':
                        results['new_records'] += 1
                    elif attendance_result == 'updated':
                        results['updated_records'] += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to process participant {participant.email}: {e}")
        
        return results
    
    async def _store_meet_participant(self, session_id: str, 
                                     participant: MeetParticipant) -> str:
        """Store Meet participant data in database"""
        participant_id = str(uuid.uuid4())
        
        participant_data = {
            'id': participant_id,
            'meet_session_id': session_id,
            'participant_email': participant.email,
            'participant_name': participant.display_name,
            'device_type': participant.device_type,
            'is_external': participant.is_external,
            'is_phone_participant': participant.is_phone,
            'joined_at': participant.joined_at.isoformat() if participant.joined_at else None,
            'left_at': participant.left_at.isoformat() if participant.left_at else None,
            'duration_minutes': participant.duration_minutes,
            'reconnect_count': participant.reconnect_count,
            'audio_minutes': participant.audio_minutes,
            'video_minutes': participant.video_minutes,
            'ip_address': participant.ip_address,
            'location_country': participant.location_country,
            'call_rating': participant.call_rating
        }
        
        # Check if participant already exists (prevent duplicates)
        existing = self.supabase.table('meet_participants').select('id').eq(
            'meet_session_id', session_id
        ).eq('participant_email', participant.email).execute()
        
        if existing.data:
            # Update existing record
            self.supabase.table('meet_participants').update(participant_data).eq(
                'id', existing.data[0]['id']
            ).execute()
            return existing.data[0]['id']
        else:
            # Create new record
            result = self.supabase.table('meet_participants').insert(participant_data).execute()
            return result.data[0]['id']
    
    async def _match_participant_to_user(self, participant: MeetParticipant) -> ParticipantMatch:
        """Match a Meet participant to a user in our system"""
        email = participant.email.lower().strip()
        
        # Try exact email match first
        user_result = self.supabase.table('users').select('id, email').eq('email', email).execute()
        if user_result.data:
            return ParticipantMatch(
                meet_participant_email=email,
                user_id=user_result.data[0]['id'],
                user_email=user_result.data[0]['email'],
                confidence_score=1.0,
                match_method='exact_email'
            )
        
        # Try manual mapping table
        mapping_result = self.supabase.table('participant_email_mapping').select(
            'user_id, confidence_level'
        ).eq('external_email', email).execute()
        
        if mapping_result.data:
            mapping = mapping_result.data[0]
            confidence = {'high': 0.9, 'medium': 0.7, 'low': 0.5}.get(
                mapping['confidence_level'], 0.5
            )
            
            # Get user details
            user_result = self.supabase.table('users').select('id, email').eq(
                'id', mapping['user_id']
            ).execute()
            
            if user_result.data:
                return ParticipantMatch(
                    meet_participant_email=email,
                    user_id=user_result.data[0]['id'],
                    user_email=user_result.data[0]['email'],
                    confidence_score=confidence,
                    match_method='manual_mapping'
                )
        
        # Try domain matching for internal users
        if self.domain and email.endswith(f'@{self.domain}'):
            # Look for similar emails in our system
            base_email = email.replace(f'@{self.domain}', '')
            like_pattern = f'%{base_email}%'
            
            similar_users = self.supabase.table('users').select('id, email').ilike(
                'email', like_pattern
            ).execute()
            
            if similar_users.data:
                return ParticipantMatch(
                    meet_participant_email=email,
                    user_id=similar_users.data[0]['id'],
                    user_email=similar_users.data[0]['email'],
                    confidence_score=0.8,
                    match_method='domain_match'
                )
        
        # No match found
        return ParticipantMatch(
            meet_participant_email=email,
            user_id=None,
            user_email=None,
            confidence_score=0.0,
            match_method='no_match'
        )
    
    async def _create_attendance_record(self, meeting_id: str, user_id: str, 
                                       participant_id: str, participant: MeetParticipant,
                                       user_match: ParticipantMatch) -> str:
        """Create or update attendance record for matched participant"""
        
        # Check if attendance record already exists
        existing = self.supabase.table('meeting_attendance').select('id').eq(
            'meeting_id', meeting_id
        ).eq('user_id', user_id).execute()
        
        attendance_data = {
            'meeting_id': meeting_id,
            'user_id': user_id,
            'attended': True,  # Present in Meet = attended
            'duration_minutes': participant.duration_minutes,
            'meet_participant_id': participant_id,
            'detection_method': 'automatic_meet',
            'meet_join_time': participant.joined_at.isoformat() if participant.joined_at else None,
            'meet_leave_time': participant.left_at.isoformat() if participant.left_at else None,
            'meet_duration_minutes': participant.duration_minutes,
            'meet_reconnect_count': participant.reconnect_count,
            'meet_device_type': participant.device_type,
            'confidence_score': user_match.confidence_score
        }
        
        if existing.data:
            # Update existing record only if this has higher confidence
            existing_record = self.supabase.table('meeting_attendance').select(
                'confidence_score, detection_method'
            ).eq('id', existing.data[0]['id']).execute()
            
            existing_confidence = existing_record.data[0].get('confidence_score', 0.0)
            existing_method = existing_record.data[0].get('detection_method', 'manual')
            
            # Only update if our confidence is higher or if existing was manual
            if user_match.confidence_score > existing_confidence or existing_method == 'manual':
                self.supabase.table('meeting_attendance').update(attendance_data).eq(
                    'id', existing.data[0]['id']
                ).execute()
                
                logger.info(f"📝 Updated attendance for user {user_id} (confidence: {user_match.confidence_score})")
                return 'updated'
            else:
                logger.info(f"⏭️ Skipped update for user {user_id} (lower confidence)")
                return 'skipped'
        else:
            # Create new attendance record
            self.supabase.table('meeting_attendance').insert(attendance_data).execute()
            
            logger.info(f"✅ Created attendance for user {user_id} (confidence: {user_match.confidence_score})")
            return 'created'
    
    async def _update_session_statistics(self, session_id: str, 
                                        participants: List[MeetParticipant]):
        """Update Meet session statistics"""
        total_minutes = sum(p.duration_minutes for p in participants)
        participant_count = len(participants)
        
        # Calculate session duration from participants
        if participants:
            earliest_join = min(p.joined_at for p in participants if p.joined_at)
            latest_leave = max(p.left_at for p in participants if p.left_at)
            
            if earliest_join and latest_leave:
                session_duration = int((latest_leave - earliest_join).total_seconds() // 60)
            else:
                session_duration = None
        else:
            session_duration = None
        
        update_data = {
            'participant_count': participant_count,
            'total_minutes_all_participants': total_minutes,
            'last_sync_at': datetime.now().isoformat()
        }
        
        if session_duration:
            update_data['duration_minutes'] = session_duration
        
        self.supabase.table('meet_sessions').update(update_data).eq('id', session_id).execute()
    
    async def _update_session_sync_status(self, session_id: str, status: str, error: str = None):
        """Update Meet session sync status"""
        update_data = {
            'sync_status': status,
            'last_sync_at': datetime.now().isoformat()
        }
        
        if error:
            update_data['sync_error'] = error
        
        self.supabase.table('meet_sessions').update(update_data).eq('id', session_id).execute()
    
    def _extract_meet_code(self, meet_link: str) -> Optional[str]:
        """Extract Meet code from Google Meet link"""
        if not meet_link:
            return None
        
        # Match patterns like:
        # https://meet.google.com/abc-defg-hij
        # https://meet.google.com/lookup/abc123def
        patterns = [
            r'meet\.google\.com/([a-z]{3}-[a-z]{4}-[a-z]{3})',  # Standard format
            r'meet\.google\.com/lookup/([a-zA-Z0-9]+)',  # Lookup format
            r'meet\.google\.com/([a-zA-Z0-9\-]+)'  # General format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, meet_link)
            if match:
                return match.group(1)
        
        logger.warning(f"⚠️ Could not extract Meet code from: {meet_link}")
        return None
    
    async def sync_all_pending_sessions(self, sync_date: date = None) -> Dict[str, Any]:
        """Sync all pending Meet sessions for a given date"""
        if not sync_date:
            sync_date = date.today()
        
        try:
            # Get all pending Meet sessions
            pending_sessions = self.supabase.table('meet_sessions').select('*').eq(
                'sync_status', 'pending'
            ).execute()
            
            logger.info(f"🔄 Syncing {len(pending_sessions.data)} pending Meet sessions")
            
            results = {
                'total_sessions': len(pending_sessions.data),
                'successful_syncs': 0,
                'failed_syncs': 0,
                'no_data_sessions': 0
            }
            
            for session in pending_sessions.data:
                try:
                    sync_result = await self.sync_meet_session_data(session['id'], sync_date)
                    
                    if sync_result['status'] == 'success':
                        results['successful_syncs'] += 1
                    elif sync_result['status'] == 'no_data':
                        results['no_data_sessions'] += 1
                    else:
                        results['failed_syncs'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Failed to sync session {session['id']}: {e}")
                    results['failed_syncs'] += 1
            
            logger.info(f"✅ Sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to sync pending sessions: {e}")
            return {'error': str(e)}

# Example usage
async def example_usage():
    """Example of how to use the Meet Correlation Engine"""
    
    from telbot import Config
    from supabase import create_client
    
    try:
        # Initialize dependencies
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        admin_reports = GoogleAdminReports()
        await admin_reports.initialize()
        
        correlation_engine = MeetCorrelationEngine(supabase, admin_reports)
        await correlation_engine.initialize()
        
        # Example: Create a Meet session
        session_id = await correlation_engine.create_meet_session(
            meeting_id="test-meeting-123",
            meet_event_id="test-event-456", 
            meet_link="https://meet.google.com/abc-defg-hij",
            organizer_email="thomas@theprogressmethod.com"
        )
        
        print(f"✅ Created Meet session: {session_id}")
        
        # Example: Sync session data
        sync_result = await correlation_engine.sync_meet_session_data(session_id)
        print(f"📊 Sync result: {sync_result}")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    print("Meet Event Correlation Engine")
    print("=" * 50)
    print("Links Google Meet sessions to pod meetings")
    
    # Run example if executed directly
    asyncio.run(example_usage())