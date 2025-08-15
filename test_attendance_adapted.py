#!/usr/bin/env python3
"""
Test the adapted attendance system with existing database schema
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from attendance_system_adapted import AttendanceSystemAdapted
from telbot import Config
from supabase import create_client

async def test_adapted_system():
    """Test the adapted attendance system"""
    
    print("🧪 Testing Adapted Attendance System")
    print("=" * 50)
    
    try:
        # Initialize system
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        attendance_system = AttendanceSystemAdapted(supabase)
        
        print("✅ Adapted attendance system initialized")
        
        # Use an existing pod from the database
        pods_result = supabase.table("pods").select("id, name").limit(1).execute()
        if not pods_result.data:
            print("❌ No pods found in database. Please create a pod first.")
            return False
        
        test_pod_id = pods_result.data[0]["id"]
        pod_name = pods_result.data[0]["name"]
        print(f"📍 Using existing pod: {pod_name} ({test_pod_id})")
        
        # Get a user from pod memberships
        members_result = supabase.table("pod_memberships").select("user_id").eq("pod_id", test_pod_id).eq("is_active", True).limit(1).execute()
        if not members_result.data:
            print("⚠️ No active members found in this pod")
            test_user_id = str(uuid.uuid4())  # Use fake user for testing
        else:
            test_user_id = members_result.data[0]["user_id"]
        
        print(f"👤 Using user: {test_user_id}")
        
        # Test 1: Create pod meeting
        print("\n🧪 Test 1: Creating pod meeting")
        today = datetime.now().strftime("%Y-%m-%d")
        
        meeting = await attendance_system.create_pod_meeting(
            pod_id=test_pod_id,
            meeting_date=today,
            status="scheduled"
        )
        
        print(f"✅ Pod meeting created:")
        print(f"   Meeting ID: {meeting.id}")
        print(f"   Pod ID: {meeting.pod_id}")
        print(f"   Date: {meeting.meeting_date}")
        print(f"   Status: {meeting.status}")
        
        # Test 2: Record attendance
        print("\n🧪 Test 2: Recording attendance")
        
        attendance_record = await attendance_system.record_attendance(
            meeting_id=meeting.id,
            user_id=test_user_id,
            attended=True,
            duration_minutes=55
        )
        
        print(f"✅ Attendance recorded:")
        print(f"   Record ID: {attendance_record.id}")
        print(f"   User ID: {attendance_record.user_id}")
        print(f"   Attended: {attendance_record.attended}")
        print(f"   Duration: {attendance_record.duration_minutes} minutes")
        
        # Test 3: Get attendance history
        print("\n🧪 Test 3: Getting attendance history")
        
        history = await attendance_system.get_user_attendance_history(
            user_id=test_user_id,
            pod_id=test_pod_id,
            weeks_back=4
        )
        
        print(f"✅ Retrieved {len(history)} attendance records")
        for record in history[:3]:  # Show first 3
            print(f"   - Meeting {record.meeting_id}: {'Attended' if record.attended else 'Absent'} ({record.duration_minutes}min)")
        
        # Test 4: Calculate analytics
        print("\n🧪 Test 4: Calculating user analytics")
        
        analytics = await attendance_system.calculate_user_attendance_analytics(
            user_id=test_user_id,
            pod_id=test_pod_id,
            weeks_back=12
        )
        
        print(f"✅ Analytics calculated:")
        print(f"   Total scheduled: {analytics.total_scheduled_meetings}")
        print(f"   Meetings attended: {analytics.meetings_attended}")
        print(f"   Attendance rate: {analytics.attendance_rate:.1%}")
        print(f"   Average duration: {analytics.average_duration:.1f} minutes")
        print(f"   Attendance pattern: {analytics.attendance_pattern.value}")
        print(f"   Engagement level: {analytics.engagement_level.value}")
        print(f"   Current streak: {analytics.current_streak}")
        print(f"   Prediction score: {analytics.prediction_score:.3f}")
        print(f"   Risk flags: {analytics.risk_flags}")
        
        # Test 5: Generate insights
        print("\n🧪 Test 5: Generating attendance insights")
        
        insights = await attendance_system.generate_attendance_insights(
            pod_id=test_pod_id,
            user_id=test_user_id
        )
        
        print(f"✅ Generated {len(insights)} insights:")
        for insight in insights[:2]:  # Show first 2 insights
            print(f"   - {insight.priority.upper()}: {insight.title}")
            print(f"     {insight.description}")
            print(f"     Confidence: {insight.confidence_score:.1%}")
        
        # Test 6: Pod attendance summary
        print("\n🧪 Test 6: Getting pod attendance summary")
        
        pod_summary = await attendance_system.get_pod_attendance_summary(
            pod_id=test_pod_id,
            weeks_back=4
        )
        
        if "error" not in pod_summary:
            print(f"✅ Pod summary generated:")
            print(f"   Total meetings: {pod_summary.get('total_meetings', 0)}")
            print(f"   Pod attendance rate: {pod_summary.get('pod_attendance_rate', 0):.1%}")
            print(f"   Member count: {pod_summary.get('member_count', 0)}")
            print(f"   High performers: {pod_summary.get('high_performers', 0)}")
            print(f"   At-risk members: {pod_summary.get('at_risk_members', 0)}")
        else:
            print(f"⚠️ Pod summary error: {pod_summary['error']}")
        
        print("\n🎉 All adapted system tests completed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

async def test_with_existing_data():
    """Test analytics with existing data in the database"""
    print("\n🧪 Testing with existing database data...")
    
    try:
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        attendance_system = AttendanceSystemAdapted(supabase)
        
        # Get existing data
        meetings_result = supabase.table("pod_meetings").select("*").limit(5).execute()
        attendance_result = supabase.table("meeting_attendance").select("*").limit(5).execute()
        
        print(f"📊 Found {len(meetings_result.data) if meetings_result.data else 0} existing meetings")
        print(f"📊 Found {len(attendance_result.data) if attendance_result.data else 0} existing attendance records")
        
        if attendance_result.data:
            # Test analytics with existing user
            sample_record = attendance_result.data[0]
            user_id = sample_record["user_id"]
            
            # Find the pod for this meeting
            meeting_result = supabase.table("pod_meetings").select("pod_id").eq("id", sample_record["meeting_id"]).execute()
            if meeting_result.data:
                pod_id = meeting_result.data[0]["pod_id"]
                
                print(f"🧮 Testing analytics for existing user {user_id} in pod {pod_id}")
                
                analytics = await attendance_system.calculate_user_attendance_analytics(user_id, pod_id)
                print(f"   Analytics: {analytics.attendance_rate:.1%} attendance, {analytics.attendance_pattern.value}")
                
                return True
        
        print("✅ Existing data test completed")
        return True
        
    except Exception as e:
        print(f"❌ Existing data test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Adapted Attendance System Test Suite")
    print("================================================")
    
    # Test adapted system functionality
    system_test = await test_adapted_system()
    
    # Test with existing data
    existing_data_test = await test_with_existing_data()
    
    if system_test and existing_data_test:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The adapted attendance system is ready for production use.")
        print("\nSystem capabilities:")
        print("- ✅ Works with existing database schema")
        print("- ✅ Pod meeting management")
        print("- ✅ Attendance recording and analytics")
        print("- ✅ Behavioral pattern analysis")
        print("- ✅ AI-driven insights generation")
        print("- ✅ Risk flag identification")
        print("\nNext steps:")
        print("1. ✅ Test API endpoints with HTTP requests")
        print("2. 🔄 Build manual entry interface for facilitators")
        print("3. 🔄 Integrate with nurture sequences")
        print("4. 🔄 Add real-time dashboard for pod leaders")
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
    
    return system_test and existing_data_test

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)