#!/usr/bin/env python3
"""
Automatic Attendance Processing Engine
Main orchestrator for automatic Google Meet attendance detection
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass
from supabase import Client
from google_admin_reports import GoogleAdminReports
from meet_correlation_engine import MeetCorrelationEngine
from google_calendar_attendance import GoogleCalendarAttendance

logger = logging.getLogger(__name__)

@dataclass
class AttendanceProcessingResult:
    """Results from automatic attendance processing"""
    total_meetings_processed: int
    meetings_with_meet_data: int
    total_participants_found: int
    attendance_records_created: int
    attendance_records_updated: int
    errors: List[str]
    processing_time_seconds: float

class AutomaticAttendanceEngine:
    """Main engine for automatic Google Meet attendance detection and processing"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.admin_reports = None
        self.correlation_engine = None
        self.calendar_integration = None
        
        # Configuration
        self.max_days_to_process = 7  # Process up to 7 days of historical data
        self.batch_size = 50  # Process meetings in batches
        
        logger.info("🤖 Automatic Attendance Engine initialized")
    
    async def initialize(self):
        """Initialize all components of the attendance engine"""
        try:
            # Initialize Google Admin Reports API
            self.admin_reports = GoogleAdminReports()
            await self.admin_reports.initialize()
            
            # Initialize Meet correlation engine
            self.correlation_engine = MeetCorrelationEngine(self.supabase, self.admin_reports)
            await self.correlation_engine.initialize()
            
            # Initialize Google Calendar integration (for linking events)
            try:
                self.calendar_integration = GoogleCalendarAttendance()
                await self.calendar_integration.initialize()
            except Exception as e:
                logger.warning(f"⚠️ Calendar integration not available: {e}")
                self.calendar_integration = None
            
            logger.info("✅ Automatic Attendance Engine fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Automatic Attendance Engine: {e}")
            raise
    
    async def process_meetings_for_date(self, target_date: date = None) -> AttendanceProcessingResult:
        """
        Process automatic attendance for all meetings on a specific date
        
        Args:
            target_date: Date to process (defaults to yesterday)
        
        Returns:
            AttendanceProcessingResult with processing statistics
        """
        if not target_date:
            target_date = date.today() - timedelta(days=1)  # Default to yesterday
        
        start_time = datetime.now()
        result = AttendanceProcessingResult(
            total_meetings_processed=0,
            meetings_with_meet_data=0,
            total_participants_found=0,
            attendance_records_created=0,
            attendance_records_updated=0,
            errors=[],
            processing_time_seconds=0.0
        )
        
        try:
            logger.info(f"🔄 Processing automatic attendance for {target_date}")
            
            # Get all meetings that occurred on the target date
            meetings = await self._get_meetings_for_date(target_date)
            result.total_meetings_processed = len(meetings)
            
            if not meetings:
                logger.info(f"📭 No meetings found for {target_date}")
                return result
            
            logger.info(f"📊 Found {len(meetings)} meetings to process")
            
            # Process meetings in batches
            for i in range(0, len(meetings), self.batch_size):
                batch = meetings[i:i + self.batch_size]
                
                logger.info(f"🔄 Processing batch {i//self.batch_size + 1}/{(len(meetings)-1)//self.batch_size + 1}")
                
                batch_results = await self._process_meeting_batch(batch, target_date)
                
                # Aggregate results
                result.meetings_with_meet_data += batch_results['meetings_with_data']
                result.total_participants_found += batch_results['total_participants']
                result.attendance_records_created += batch_results['records_created']
                result.attendance_records_updated += batch_results['records_updated']
                result.errors.extend(batch_results['errors'])
            
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Completed processing for {target_date}")
            logger.info(f"   📊 {result.meetings_with_meet_data}/{result.total_meetings_processed} meetings had Meet data")
            logger.info(f"   👥 {result.total_participants_found} total participants found")
            logger.info(f"   📝 {result.attendance_records_created} new + {result.attendance_records_updated} updated records")
            logger.info(f"   ⏱️ Processing time: {result.processing_time_seconds:.2f} seconds")
            
            if result.errors:
                logger.warning(f"⚠️ {len(result.errors)} errors occurred during processing")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process meetings for {target_date}: {e}")
            result.errors.append(f"Processing failed: {str(e)}")
            return result
    
    async def _get_meetings_for_date(self, target_date: date) -> List[Dict]:
        """Get all meetings that occurred on a specific date"""
        try:
            # Query pod_meetings for the target date
            result = self.supabase.table('pod_meetings').select(
                'id, pod_id, meeting_date, status, created_at'
            ).eq('meeting_date', target_date.isoformat()).execute()
            
            meetings = result.data or []
            
            # Filter to only scheduled/completed meetings
            valid_meetings = [
                m for m in meetings 
                if m.get('status') in ['scheduled', 'completed', 'in_progress']
            ]
            
            logger.info(f"📋 Found {len(valid_meetings)} valid meetings for {target_date}")
            return valid_meetings
            
        except Exception as e:
            logger.error(f"❌ Failed to get meetings for {target_date}: {e}")
            return []
    
    async def _process_meeting_batch(self, meetings: List[Dict], target_date: date) -> Dict[str, Any]:
        """Process a batch of meetings for automatic attendance"""
        batch_results = {
            'meetings_with_data': 0,
            'total_participants': 0,
            'records_created': 0,
            'records_updated': 0,
            'errors': []
        }
        
        for meeting in meetings:
            try:
                meeting_id = meeting['id']
                
                # Check if this meeting has an associated Meet session
                meet_session = await self._get_or_create_meet_session(meeting)
                
                if not meet_session:
                    logger.debug(f"📭 No Meet session found for meeting {meeting_id}")
                    continue
                
                # Sync Meet data for this session
                sync_result = await self.correlation_engine.sync_meet_session_data(
                    meet_session['id'], target_date
                )
                
                if sync_result['status'] == 'success':
                    batch_results['meetings_with_data'] += 1
                    batch_results['total_participants'] += sync_result.get('participants_found', 0)
                    batch_results['records_created'] += sync_result.get('new_attendance_records', 0)
                    batch_results['records_updated'] += sync_result.get('updated_records', 0)
                    
                    logger.info(f"✅ Processed meeting {meeting_id}: {sync_result.get('participants_found', 0)} participants")
                    
                elif sync_result['status'] == 'no_data':
                    logger.debug(f"📭 No Meet data available for meeting {meeting_id}")
                    
                else:
                    error_msg = f"Failed to sync meeting {meeting_id}: {sync_result.get('error', 'unknown')}"
                    batch_results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                
            except Exception as e:
                error_msg = f"Failed to process meeting {meeting.get('id', 'unknown')}: {str(e)}"
                batch_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        return batch_results
    
    async def _get_or_create_meet_session(self, meeting: Dict) -> Optional[Dict]:
        """Get existing Meet session or create one if meeting has Meet link"""
        meeting_id = meeting['id']
        
        try:
            # Check if Meet session already exists
            existing_session = self.supabase.table('meet_sessions').select('*').eq(
                'meeting_id', meeting_id
            ).execute()
            
            if existing_session.data:
                return existing_session.data[0]
            
            # Try to find Meet link for this meeting
            meet_link = await self._find_meet_link_for_meeting(meeting)
            
            if not meet_link:
                return None
            
            # Create new Meet session
            session_id = await self.correlation_engine.create_meet_session(
                meeting_id=meeting_id,
                meet_event_id=None,  # May not have event ID for older meetings
                meet_link=meet_link,
                organizer_email=os.getenv('GOOGLE_CALENDAR_USER_EMAIL', 'unknown@domain.com')
            )
            
            # Return the newly created session
            new_session = self.supabase.table('meet_sessions').select('*').eq('id', session_id).execute()
            return new_session.data[0] if new_session.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get/create Meet session for meeting {meeting_id}: {e}")
            return None
    
    async def _find_meet_link_for_meeting(self, meeting: Dict) -> Optional[str]:
        """Try to find Google Meet link for a meeting"""
        meeting_id = meeting['id']
        
        try:
            # Strategy 1: Check if we stored the Meet link when creating the meeting
            # (This would be for newer meetings created through our system)
            
            # Strategy 2: Search calendar events for this meeting
            if self.calendar_integration:
                try:
                    # Look for calendar events on the meeting date
                    meeting_date = datetime.fromisoformat(meeting['meeting_date'])
                    
                    # Get events for the day
                    events = await self._get_calendar_events_for_date(meeting_date.date())
                    
                    # Look for events that might match this meeting
                    for event in events:
                        if self._event_matches_meeting(event, meeting):
                            meet_link = self._extract_meet_link_from_event(event)
                            if meet_link:
                                logger.info(f"📅 Found Meet link via calendar for meeting {meeting_id}")
                                return meet_link
                
                except Exception as e:
                    logger.debug(f"Could not search calendar for meeting {meeting_id}: {e}")
            
            # Strategy 3: Check database for stored Meet links
            # (Future enhancement - could store links when meetings are created)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find Meet link for meeting {meeting_id}: {e}")
            return None
    
    async def _get_calendar_events_for_date(self, target_date: date) -> List[Dict]:
        """Get calendar events for a specific date"""
        try:
            if not self.calendar_integration:
                return []
            
            # Get events for the day
            time_min = datetime.combine(target_date, datetime.min.time()).isoformat() + 'Z'
            time_max = datetime.combine(target_date, datetime.max.time()).isoformat() + 'Z'
            
            events_result = self.calendar_integration.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except Exception as e:
            logger.error(f"❌ Failed to get calendar events for {target_date}: {e}")
            return []
    
    def _event_matches_meeting(self, event: Dict, meeting: Dict) -> bool:
        """Check if a calendar event matches a pod meeting"""
        # Simple matching logic - could be enhanced
        event_summary = event.get('summary', '').lower()
        
        # Look for pod-related keywords
        pod_keywords = ['pod', 'meeting', 'progress', 'method']
        
        return any(keyword in event_summary for keyword in pod_keywords)
    
    def _extract_meet_link_from_event(self, event: Dict) -> Optional[str]:
        """Extract Google Meet link from calendar event"""
        # Check hangout link
        hangout_link = event.get('hangoutLink')
        if hangout_link and 'meet.google.com' in hangout_link:
            return hangout_link
        
        # Check conference data
        conference_data = event.get('conferenceData', {})
        entry_points = conference_data.get('entryPoints', [])
        
        for entry_point in entry_points:
            if entry_point.get('entryPointType') == 'video':
                uri = entry_point.get('uri', '')
                if 'meet.google.com' in uri:
                    return uri
        
        return None
    
    async def process_historical_data(self, days_back: int = 7) -> Dict[str, Any]:
        """Process automatic attendance for multiple historical days"""
        end_date = date.today() - timedelta(days=1)  # Start from yesterday
        start_date = end_date - timedelta(days=days_back - 1)
        
        logger.info(f"🔄 Processing historical attendance data from {start_date} to {end_date}")
        
        total_results = {
            'days_processed': 0,
            'total_meetings': 0,
            'total_participants': 0,
            'total_records_created': 0,
            'total_records_updated': 0,
            'total_errors': 0
        }
        
        current_date = start_date
        while current_date <= end_date:
            try:
                logger.info(f"📅 Processing {current_date}")
                
                day_result = await self.process_meetings_for_date(current_date)
                
                # Aggregate results
                total_results['days_processed'] += 1
                total_results['total_meetings'] += day_result.total_meetings_processed
                total_results['total_participants'] += day_result.total_participants_found
                total_results['total_records_created'] += day_result.attendance_records_created
                total_results['total_records_updated'] += day_result.attendance_records_updated
                total_results['total_errors'] += len(day_result.errors)
                
            except Exception as e:
                logger.error(f"❌ Failed to process {current_date}: {e}")
                total_results['total_errors'] += 1
            
            current_date += timedelta(days=1)
        
        logger.info(f"✅ Historical processing complete: {total_results}")
        return total_results
    
    async def run_daily_sync(self) -> AttendanceProcessingResult:
        """Run daily synchronization for yesterday's meetings"""
        yesterday = date.today() - timedelta(days=1)
        
        logger.info(f"📅 Running daily sync for {yesterday}")
        
        result = await self.process_meetings_for_date(yesterday)
        
        # Log summary
        if result.errors:
            logger.warning(f"⚠️ Daily sync completed with {len(result.errors)} errors")
        else:
            logger.info(f"✅ Daily sync completed successfully")
        
        return result

# Example usage and testing
async def example_usage():
    """Example of how to use the Automatic Attendance Engine"""
    
    from telbot import Config
    from supabase import create_client
    
    try:
        # Initialize
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        engine = AutomaticAttendanceEngine(supabase)
        await engine.initialize()
        
        # Process yesterday's meetings
        result = await engine.run_daily_sync()
        
        print(f"📊 Daily sync results:")
        print(f"   Meetings processed: {result.total_meetings_processed}")
        print(f"   Meetings with Meet data: {result.meetings_with_meet_data}")
        print(f"   Participants found: {result.total_participants_found}")
        print(f"   Records created: {result.attendance_records_created}")
        print(f"   Records updated: {result.attendance_records_updated}")
        print(f"   Processing time: {result.processing_time_seconds:.2f}s")
        
        if result.errors:
            print(f"   ⚠️ Errors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"     - {error}")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    print("Automatic Attendance Processing Engine")
    print("=" * 50)
    print("Orchestrates automatic Google Meet attendance detection")
    
    # Run example if executed directly
    asyncio.run(example_usage())