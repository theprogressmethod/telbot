#!/usr/bin/env python3
"""
Google Admin Reports API Integration
Automatically detects Google Meet attendance using Admin Reports API
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import os
import re
from dataclasses import dataclass
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from safety_controls import safety_controls

logger = logging.getLogger(__name__)

@dataclass
class MeetEvent:
    """Represents a Google Meet audit event"""
    event_id: str
    event_type: str
    event_time: datetime
    user_email: str
    meet_code: Optional[str]
    organizer_email: Optional[str]
    participant_email: Optional[str]
    duration_minutes: Optional[int]
    device_type: Optional[str]
    is_external: bool
    raw_data: dict

@dataclass
class MeetParticipant:
    """Represents a participant in a Google Meet session"""
    email: str
    display_name: Optional[str]
    joined_at: datetime
    left_at: Optional[datetime]
    duration_minutes: int
    device_type: str
    is_external: bool
    is_phone: bool
    reconnect_count: int
    audio_minutes: int
    video_minutes: int
    ip_address: Optional[str]
    location_country: Optional[str]
    call_rating: Optional[int]

class GoogleAdminReports:
    """Google Admin Reports API integration for Meet attendance tracking"""
    
    def __init__(self, service_account_file: str = None, user_email: str = None):
        self.service_account_file = service_account_file or os.getenv('GOOGLE_MEET_SERVICE_ACCOUNT_FILE')
        self.user_email = user_email or os.getenv('GOOGLE_CALENDAR_USER_EMAIL')
        
        # Required scopes for Admin Reports API
        self.scopes = [
            'https://www.googleapis.com/auth/admin.reports.audit.readonly',
            'https://www.googleapis.com/auth/admin.reports.usage.readonly'
        ]
        
        self.service = None
        self.credentials = None
        
        logger.info("📊 Google Admin Reports API integration initialized")
    
    async def initialize(self):
        """Initialize Google Admin Reports API connection with Domain-Wide Delegation"""
        try:
            if not self.service_account_file:
                raise ValueError("Google service account file not configured")
            
            if not self.user_email:
                raise ValueError("Admin user email not configured for Domain-Wide Delegation")
            
            # Load service account credentials with Domain-Wide Delegation
            self.credentials = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=self.scopes,
                subject=self.user_email  # This enables Domain-Wide Delegation as admin
            )
            
            # Build the Admin Reports service
            self.service = build('admin', 'reports_v1', credentials=self.credentials)
            
            logger.info(f"✅ Google Admin Reports API connection established for {self.user_email}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Admin Reports API: {e}")
            raise
    
    async def get_meet_events(self, 
                             start_date: date = None,
                             end_date: date = None,
                             event_types: List[str] = None,
                             max_results: int = 1000) -> List[MeetEvent]:
        """
        Retrieve Google Meet audit events from Admin Reports API
        
        Args:
            start_date: Start date for events (defaults to yesterday)
            end_date: End date for events (defaults to today)
            event_types: List of event types to filter ('call_ended', 'call_started')
            max_results: Maximum number of events to retrieve
        
        Returns:
            List of MeetEvent objects
        """
        if not self.service:
            raise RuntimeError("Admin Reports API not initialized")
        
        # Default to yesterday if no dates provided
        if not start_date:
            start_date = date.today() - timedelta(days=1)
        if not end_date:
            end_date = date.today()
        
        if not event_types:
            event_types = ['call_ended']  # Focus on completed calls for attendance
        
        events = []
        
        try:
            # Format dates for API (YYYY-MM-DD)
            start_time = start_date.strftime('%Y-%m-%d')
            end_time = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"🔍 Fetching Meet events from {start_time} to {end_time}")
            
            # Call the Admin Reports API for Meet activity
            next_page_token = None
            total_events = 0
            
            while True:
                request_params = {
                    'userKey': 'all',  # All users in domain
                    'applicationName': 'meet',
                    'startTime': start_time,
                    'endTime': end_time,
                    'maxResults': min(max_results - total_events, 1000)  # API limit is 1000 per page
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token
                
                # Filter by event types if specified
                if event_types:
                    # Build event name filter
                    event_filters = []
                    for event_type in event_types:
                        event_filters.append(f"meet:{event_type}")
                    request_params['eventName'] = ','.join(event_filters)
                
                response = self.service.activities().list(**request_params).execute()
                
                items = response.get('items', [])
                logger.info(f"📊 Retrieved {len(items)} events from API")
                
                # Process each event
                for item in items:
                    try:
                        meet_event = self._parse_meet_event(item)
                        if meet_event:
                            events.append(meet_event)
                            total_events += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse event {item.get('id', 'unknown')}: {e}")
                
                # Check if we have more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token or total_events >= max_results:
                    break
            
            logger.info(f"✅ Retrieved {len(events)} Meet events")
            return events
            
        except HttpError as e:
            logger.error(f"❌ Google Admin Reports API error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to retrieve Meet events: {e}")
            raise
    
    def _parse_meet_event(self, event_data: dict) -> Optional[MeetEvent]:
        """Parse a raw Google Admin Reports event into a MeetEvent object"""
        try:
            # Extract basic event information
            event_id = event_data.get('id', {}).get('uniqueQualifier', '')
            event_time_str = event_data.get('id', {}).get('time', '')
            event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
            
            # Extract actor information
            actor = event_data.get('actor', {})
            user_email = actor.get('email', '')
            
            # Extract event details
            events = event_data.get('events', [])
            if not events:
                return None
            
            # Process the first (main) event
            main_event = events[0]
            event_type = main_event.get('name', '').replace('meet:', '')
            
            # Extract parameters
            parameters = {p.get('name'): p.get('value') for p in main_event.get('parameters', [])}
            
            # Extract Meet-specific data
            meet_code = parameters.get('meeting_code') or parameters.get('conference_id')
            organizer_email = parameters.get('organizer_email')
            participant_email = parameters.get('participant_email') or user_email
            
            # Extract duration (usually in seconds, convert to minutes)
            duration_seconds = parameters.get('duration_seconds')
            duration_minutes = int(duration_seconds) // 60 if duration_seconds else None
            
            # Extract device type
            device_type = parameters.get('endpoint_type') or parameters.get('device_type', 'unknown')
            
            # Determine if external participant
            is_external = parameters.get('is_external', 'false').lower() == 'true'
            
            return MeetEvent(
                event_id=event_id,
                event_type=event_type,
                event_time=event_time,
                user_email=user_email,
                meet_code=meet_code,
                organizer_email=organizer_email,
                participant_email=participant_email,
                duration_minutes=duration_minutes,
                device_type=device_type,
                is_external=is_external,
                raw_data=event_data
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse Meet event: {e}")
            return None
    
    def extract_meet_code_from_link(self, meet_link: str) -> Optional[str]:
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
        
        return None
    
    async def get_meet_participants(self, meet_code: str, 
                                   start_date: date = None,
                                   end_date: date = None) -> List[MeetParticipant]:
        """
        Get detailed participant information for a specific Meet session
        
        Args:
            meet_code: Google Meet conference code
            start_date: Start date for participant events
            end_date: End date for participant events
        
        Returns:
            List of MeetParticipant objects
        """
        # Get all Meet events for the date range
        events = await self.get_meet_events(start_date, end_date, ['call_ended'])
        
        # Filter events for this specific Meet code
        meet_events = [e for e in events if e.meet_code == meet_code]
        
        participants = []
        
        for event in meet_events:
            try:
                # Extract detailed participant data from event
                raw_params = event.raw_data.get('events', [{}])[0].get('parameters', [])
                params = {p.get('name'): p.get('value') for p in raw_params}
                
                participant = MeetParticipant(
                    email=event.participant_email or event.user_email,
                    display_name=params.get('display_name'),
                    joined_at=event.event_time - timedelta(minutes=event.duration_minutes or 0),
                    left_at=event.event_time,
                    duration_minutes=event.duration_minutes or 0,
                    device_type=event.device_type,
                    is_external=event.is_external,
                    is_phone=params.get('is_phone', 'false').lower() == 'true',
                    reconnect_count=int(params.get('reconnect_count', 0)),
                    audio_minutes=int(params.get('audio_send_seconds', 0)) // 60,
                    video_minutes=int(params.get('video_send_seconds', 0)) // 60,
                    ip_address=params.get('ip_address'),
                    location_country=params.get('location_country'),
                    call_rating=int(params.get('call_rating', 0)) if params.get('call_rating') else None
                )
                
                participants.append(participant)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse participant data: {e}")
        
        logger.info(f"📊 Found {len(participants)} participants for Meet {meet_code}")
        return participants
    
    async def sync_meet_data_for_date(self, sync_date: date) -> Dict[str, int]:
        """
        Sync all Meet data for a specific date
        
        Args:
            sync_date: Date to sync Meet data for
        
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'total_events': 0,
            'processed_events': 0,
            'matched_meetings': 0,
            'new_participants': 0,
            'errors': 0
        }
        
        try:
            # Get all Meet events for the date
            events = await self.get_meet_events(
                start_date=sync_date,
                end_date=sync_date,
                event_types=['call_ended', 'call_started']
            )
            
            stats['total_events'] = len(events)
            
            for event in events:
                try:
                    # Process each event
                    # This would integrate with the database and correlation system
                    # For now, just count as processed
                    stats['processed_events'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process event {event.event_id}: {e}")
                    stats['errors'] += 1
            
            logger.info(f"✅ Meet data sync completed for {sync_date}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to sync Meet data for {sync_date}: {e}")
            stats['errors'] += 1
            return stats

# Example usage and testing
async def example_usage():
    """Example of how to use the Google Admin Reports integration"""
    
    try:
        # Initialize the reports API
        reports = GoogleAdminReports()
        await reports.initialize()
        
        # Get Meet events for yesterday
        yesterday = date.today() - timedelta(days=1)
        events = await reports.get_meet_events(start_date=yesterday, end_date=yesterday)
        
        print(f"📊 Found {len(events)} Meet events for {yesterday}")
        
        for event in events[:5]:  # Show first 5 events
            print(f"  🎯 {event.event_type}: {event.user_email} in {event.meet_code}")
            print(f"     Duration: {event.duration_minutes} minutes, Device: {event.device_type}")
        
        # Get participants for a specific Meet session
        if events:
            first_event = events[0]
            if first_event.meet_code:
                participants = await reports.get_meet_participants(
                    first_event.meet_code, 
                    yesterday, 
                    yesterday
                )
                print(f"👥 Found {len(participants)} participants in {first_event.meet_code}")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")

if __name__ == "__main__":
    print("Google Admin Reports API Integration")
    print("=" * 50)
    print("This module provides automatic Google Meet attendance detection")
    print("through the Google Admin Reports API.")
    
    # Run example if executed directly
    asyncio.run(example_usage())