#!/usr/bin/env python3
"""
Check today's meetings and Google Meet attendance data
"""

import asyncio
from datetime import datetime, date, timedelta
from telbot import Config
from supabase import create_client
from google_admin_reports import GoogleAdminReports

async def check_todays_data():
    """Check both scheduled meetings and actual Google Meet attendance"""
    
    print("📊 TODAY'S MEETING ANALYSIS")
    print("=" * 60)
    
    # 1. Check scheduled meetings from dashboard
    print("\n🗓️ SCHEDULED MEETINGS:")
    print("-" * 30)
    
    try:
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        # Get meetings created today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_str = today_start.isoformat()
        
        result = supabase.table('pod_meetings').select('*').gte('created_at', today_start_str).order('created_at', desc=True).execute()
        
        if result.data:
            for i, meeting in enumerate(result.data, 1):
                print(f"{i}. Meeting: {meeting.get('title', 'Untitled')}")
                print(f"   Scheduled: {meeting.get('meeting_date')} at {meeting.get('meeting_time')}")
                print(f"   Duration: {meeting.get('duration_minutes', 'Unknown')} minutes")
                print(f"   Created: {meeting.get('created_at')}")
                print(f"   Meeting ID: {meeting.get('id')}")
                if meeting.get('google_calendar_event_id'):
                    print(f"   ✅ Google Calendar: {meeting.get('google_calendar_event_id')}")
                else:
                    print(f"   ❌ No Google Calendar event")
                print()
        else:
            print("No meetings scheduled today")
            
    except Exception as e:
        print(f"Error checking scheduled meetings: {e}")
    
    # 2. Check Google Meet attendance data  
    print("\n📞 GOOGLE MEET ATTENDANCE:")
    print("-" * 30)
    
    try:
        reports = GoogleAdminReports()
        await reports.initialize()
        
        # Get today's Meet events
        today = date.today()
        events = await reports.get_meet_events(today)
        
        if events:
            print(f"Found {len(events)} Meet events today:")
            print()
            
            # Group events by meet code and time
            meet_sessions = {}
            for event in events:
                key = f"{event.meet_code}_{event.event_time.strftime('%H:%M')}"
                if key not in meet_sessions:
                    meet_sessions[key] = []
                meet_sessions[key].append(event)
            
            for i, (session_key, session_events) in enumerate(meet_sessions.items(), 1):
                meet_code = session_key.split('_')[0]
                start_time = session_events[0].event_time
                
                print(f"{i}. Meet Code: {meet_code}")
                print(f"   Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Participants:")
                
                for event in session_events:
                    print(f"   - {event.user_email}: {event.event_type} at {event.event_time.strftime('%H:%M:%S')}")
                print()
        else:
            print("No Meet events found for today")
            print()
            print("This could mean:")
            print("- No meetings occurred today yet")
            print("- Meetings were not on Google Workspace domain")
            print("- Google data still processing (10-15 min delay)")
            print("- Meetings were not linked to Google Calendar")
            
    except Exception as e:
        print(f"Error checking Meet data: {e}")

    # 3. Summary
    print("\n🎯 NEXT STEPS:")
    print("-" * 30)
    print("To get automatic attendance tracking:")
    print("1. Create meetings with Google Calendar enabled")
    print("2. Join the Google Meet link from the calendar event")
    print("3. Wait 10-15 minutes for Google data processing")
    print("4. Run: python automatic_attendance_engine.py --sync-date today")

if __name__ == "__main__":
    asyncio.run(check_todays_data())