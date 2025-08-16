#!/usr/bin/env python3
"""
Delayed Meeting Analysis - Check meetings created in last 30 minutes and their Google Meet attendance
"""

import asyncio
import time
from datetime import datetime, timedelta
from telbot import Config
from supabase import create_client
from google_admin_reports import GoogleAdminReports

async def analyze_recent_meetings():
    """Analyze meetings created in last 30 minutes and their attendance data"""
    
    print("⏰ DELAYED MEETING ANALYSIS")
    print(f"🕐 Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Time window: last 30 minutes
    now = datetime.now()
    thirty_min_ago = now - timedelta(minutes=30)
    thirty_min_ago_str = thirty_min_ago.isoformat()
    
    print(f"📅 Looking for meetings created between:")
    print(f"   From: {thirty_min_ago.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   To:   {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Check meetings created in last 30 minutes
    print("🗓️ MEETINGS CREATED IN LAST 30 MINUTES:")
    print("-" * 50)
    
    try:
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        result = supabase.table('pod_meetings').select('*').gte('created_at', thirty_min_ago_str).order('created_at', desc=True).execute()
        
        recent_meetings = []
        if result.data:
            print(f"Found {len(result.data)} meetings created in the last 30 minutes:")
            print()
            
            for i, meeting in enumerate(result.data, 1):
                created_time = datetime.fromisoformat(meeting.get('created_at').replace('Z', '+00:00'))
                
                meeting_info = {
                    'id': meeting.get('id'),
                    'title': meeting.get('title', 'Untitled'),
                    'date': meeting.get('meeting_date'),
                    'time': meeting.get('meeting_time'),
                    'duration': meeting.get('duration_minutes'),
                    'created_at': created_time,
                    'calendar_event': meeting.get('google_calendar_event_id'),
                    'meet_link': meeting.get('google_meet_link')
                }
                recent_meetings.append(meeting_info)
                
                print(f"{i}. Meeting: {meeting_info['title']}")
                print(f"   Created: {meeting_info['created_at'].strftime('%H:%M:%S')}")
                print(f"   Scheduled: {meeting_info['date']} at {meeting_info['time']}")
                print(f"   Duration: {meeting_info['duration']} minutes")
                print(f"   Meeting ID: {meeting_info['id']}")
                
                if meeting_info['calendar_event']:
                    print(f"   ✅ Google Calendar: {meeting_info['calendar_event']}")
                else:
                    print(f"   ❌ No Google Calendar event")
                    
                if meeting_info['meet_link']:
                    print(f"   🔗 Meet Link: {meeting_info['meet_link']}")
                else:
                    print(f"   ❌ No Meet link")
                print()
        else:
            print("No meetings created in the last 30 minutes")
            recent_meetings = []
            
    except Exception as e:
        print(f"Error checking recent meetings: {e}")
        recent_meetings = []
    
    # 2. Check Google Meet attendance for today
    print("📞 GOOGLE MEET ATTENDANCE DATA:")
    print("-" * 50)
    
    try:
        reports = GoogleAdminReports()
        await reports.initialize()
        
        # Get today's Meet events (Google data may span the day)
        today = now.date()
        events = await reports.get_meet_events(today)
        
        if events:
            print(f"Found {len(events)} Meet events for today:")
            print()
            
            # Group events by meet code and organize by time
            meet_sessions = {}
            for event in events:
                # Group by meet code and approximate time (within 5 minutes)
                time_bucket = event.event_time.replace(minute=(event.event_time.minute // 5) * 5, second=0, microsecond=0)
                key = f"{event.meet_code}_{time_bucket.strftime('%H:%M')}"
                
                if key not in meet_sessions:
                    meet_sessions[key] = {
                        'meet_code': event.meet_code,
                        'start_time': time_bucket,
                        'events': []
                    }
                meet_sessions[key]['events'].append(event)
            
            # Analyze each session
            for i, (session_key, session) in enumerate(meet_sessions.items(), 1):
                print(f"Session {i}: Meet Code {session['meet_code']}")
                print(f"   Time: {session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Events: {len(session['events'])}")
                
                # Track participants
                participants = {}
                for event in session['events']:
                    email = event.user_email
                    if email not in participants:
                        participants[email] = []
                    participants[email].append({
                        'type': event.event_type,
                        'time': event.event_time,
                        'duration': event.duration_minutes
                    })
                
                print(f"   Participants:")
                for email, events_list in participants.items():
                    join_events = [e for e in events_list if 'join' in e['type'] or 'start' in e['type']]
                    leave_events = [e for e in events_list if 'leave' in e['type'] or 'end' in e['type']]
                    
                    if join_events:
                        join_time = min(e['time'] for e in join_events)
                        leave_time = max(e['time'] for e in leave_events) if leave_events else None
                        
                        print(f"   - {email}:")
                        print(f"     Joined: {join_time.strftime('%H:%M:%S')}")
                        if leave_time:
                            print(f"     Left: {leave_time.strftime('%H:%M:%S')}")
                            duration = (leave_time - join_time).total_seconds() / 60
                            print(f"     Duration: {duration:.1f} minutes")
                        else:
                            print(f"     Left: Still in meeting or data incomplete")
                print()
        else:
            print("No Meet events found for today")
            print()
            print("Possible reasons:")
            print("- No meetings with Google Meet links were joined")
            print("- Meetings were on personal Gmail (not Workspace)")
            print("- Google data still processing (can take 10-15 minutes)")
            print("- Meetings created without Google Calendar integration")
            
    except Exception as e:
        print(f"Error checking Meet attendance: {e}")

    # 3. Correlation attempt
    print("🔗 CORRELATION ANALYSIS:")
    print("-" * 50)
    
    if recent_meetings and events:
        print("Attempting to correlate scheduled meetings with Meet sessions...")
        # This would be more sophisticated correlation logic
        print("(Full correlation engine would match by time, participants, etc.)")
    elif recent_meetings and not events:
        print("✅ Found scheduled meetings but no Meet attendance data")
        print("💡 This suggests meetings were created but not joined via Google Meet")
    elif not recent_meetings and events:
        print("✅ Found Meet attendance but no recent scheduled meetings")
        print("💡 This suggests ad-hoc meetings or meetings scheduled earlier")
    else:
        print("❌ No recent meetings or Meet data found")
        
    print()
    print("🎯 SUMMARY:")
    print("-" * 50)
    print(f"📅 Meetings created (last 30 min): {len(recent_meetings)}")
    print(f"📞 Meet events found (today): {len(events) if events else 0}")
    
    if recent_meetings:
        calendar_enabled = sum(1 for m in recent_meetings if m['calendar_event'])
        print(f"🗓️ With Google Calendar: {calendar_enabled}/{len(recent_meetings)}")
        
    print(f"⏰ Analysis completed at: {datetime.now().strftime('%H:%M:%S')}")

def run_delayed_analysis():
    """Run the analysis after a 20-minute delay"""
    
    print("⏰ SETTING UP DELAYED ANALYSIS")
    print("=" * 50)
    print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏳ Will analyze meetings in 20 minutes...")
    print("💤 Sleeping for 1200 seconds (20 minutes)")
    print()
    print("Feel free to:")
    print("1. Create meetings with Google Calendar enabled")
    print("2. Join those meetings via the Google Meet links")
    print("3. Come back in 20 minutes to see the results!")
    print()
    print("Analysis will automatically start at:", (datetime.now() + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # Sleep for 20 minutes (1200 seconds)
    time.sleep(1200)
    
    # Run the analysis
    asyncio.run(analyze_recent_meetings())

if __name__ == "__main__":
    run_delayed_analysis()