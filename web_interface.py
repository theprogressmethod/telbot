#!/usr/bin/env python3
"""
Attendance System Web Interface
Locally hosted webpage to test all attendance features
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import asyncio
import json
import secrets
import uuid
from datetime import datetime, timedelta
from telbot import Config
from supabase import create_client
from attendance_system_adapted import AttendanceSystemAdapted
from recurring_meetings import (
    RecurringMeetingManager, 
    RecurringMeetingSchedule,
    RecurrenceType,
    WeekDay
)
from google_calendar_attendance import GoogleCalendarAttendance
from automatic_attendance_engine import AutomaticAttendanceEngine
from user_analytics import UserAnalytics
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate secure secret key
app.permanent_session_lifetime = timedelta(hours=24)  # Sessions expire after 24 hours

# Global variables for our systems
config = None
supabase = None
attendance_system = None
recurring_manager = None
google_calendar = None
automatic_attendance = None
user_analytics = None

def initialize_systems():
    """Initialize all our systems"""
    global config, supabase, attendance_system, recurring_manager, google_calendar, automatic_attendance, user_analytics
    
    try:
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        attendance_system = AttendanceSystemAdapted(supabase)
        
        # Initialize Google Calendar integration
        try:
            google_calendar = GoogleCalendarAttendance()
            # Initialize the service connection
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(google_calendar.initialize())
            logger.info("✅ Google Calendar integration initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google Calendar integration failed: {e}")
            google_calendar = None
            
        recurring_manager = RecurringMeetingManager(supabase, attendance_system, google_calendar)
        
        # Initialize automatic attendance engine
        try:
            automatic_attendance = AutomaticAttendanceEngine(supabase)
            # Note: We'll initialize this async when needed to avoid blocking startup
            logger.info("✅ Automatic attendance engine created")
        except Exception as e:
            logger.warning(f"⚠️ Automatic attendance engine failed to create: {e}")
            automatic_attendance = None
        
        # Initialize user analytics system
        try:
            user_analytics = UserAnalytics(supabase)
            logger.info("✅ User analytics system initialized")
        except Exception as e:
            logger.warning(f"⚠️ User analytics system failed to initialize: {e}")
            user_analytics = None
        
        logger.info("✅ All systems initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize systems: {e}")
        return False

# Authentication and Session Management
class AuthenticationManager:
    """Handles user authentication and session management"""
    
    @staticmethod
    def generate_auth_token():
        """Generate a secure authentication token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session_for_user(telegram_user_id: int, user_data: dict):
        """Create a secure session for authenticated user"""
        session.permanent = True
        session['user_id'] = user_data['id']
        session['telegram_user_id'] = telegram_user_id
        session['username'] = user_data.get('username', '')
        session['name'] = user_data.get('name', '')
        session['email'] = user_data.get('email', '')
        session['roles'] = user_data.get('roles', [])
        session['authenticated'] = True
        session['auth_token'] = AuthenticationManager.generate_auth_token()
        session['login_time'] = datetime.now().isoformat()
        
        # Store session in database for tracking
        try:
            session_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_data['id'],
                'telegram_user_id': telegram_user_id,
                'auth_token': session['auth_token'],
                'login_time': session['login_time'],
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            }
            
            supabase.table('user_sessions').insert(session_data).execute()
            logger.info(f"✅ Created session for user {telegram_user_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to store session in database: {e}")
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user data from session"""
        if not session.get('authenticated'):
            return None
            
        return {
            'user_id': session.get('user_id'),
            'telegram_user_id': session.get('telegram_user_id'),
            'username': session.get('username'),
            'name': session.get('name'),
            'email': session.get('email'),
            'roles': session.get('roles', []),
            'auth_token': session.get('auth_token'),
            'login_time': session.get('login_time')
        }
    
    @staticmethod
    def user_has_role(role: str):
        """Check if current user has specific role"""
        user = AuthenticationManager.get_current_user()
        if not user:
            return False
        return role in user.get('roles', [])
    
    @staticmethod
    def user_has_any_role(roles: list):
        """Check if current user has any of the specified roles"""
        return any(AuthenticationManager.user_has_role(role) for role in roles)
    
    @staticmethod
    def logout_user():
        """Log out current user and cleanup session"""
        try:
            # Remove session from database
            if session.get('auth_token'):
                supabase.table('user_sessions').delete().eq('auth_token', session['auth_token']).execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to remove session from database: {e}")
        
        # Clear Flask session
        session.clear()
        logger.info("✅ User logged out successfully")

def require_auth(f):
    """Decorator to require authentication for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthenticationManager.get_current_user():
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role for routes"""
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = AuthenticationManager.get_current_user()
            if not user:
                return redirect(url_for('login_page'))
            if not AuthenticationManager.user_has_role(required_role):
                flash(f'Access denied. Required role: {required_role}', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login')
def login_page():
    """Display login page with Telegram authentication"""
    return render_template('login.html')

@app.route('/api/telegram-auth', methods=['POST'])
def telegram_auth():
    """Handle Telegram authentication via bot-generated tokens"""
    try:
        data = request.json
        telegram_user_id = data.get('telegram_user_id')
        auth_code = data.get('auth_code')
        
        if not telegram_user_id or not auth_code:
            return jsonify({
                'status': 'error',
                'message': 'telegram_user_id and auth_code are required'
            }), 400
        
        # Verify auth code from temporary storage (should be generated by bot)
        temp_auth_result = supabase.table('temp_auth_codes').select('*').eq('telegram_user_id', telegram_user_id).eq('auth_code', auth_code).execute()
        
        if not temp_auth_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired authentication code'
            }), 401
        
        auth_record = temp_auth_result.data[0]
        
        # Check if code is still valid (within 10 minutes)
        code_created = datetime.fromisoformat(auth_record['created_at'].replace('Z', '+00:00'))
        if datetime.now() - code_created.replace(tzinfo=None) > timedelta(minutes=10):
            # Clean up expired code
            supabase.table('temp_auth_codes').delete().eq('id', auth_record['id']).execute()
            return jsonify({
                'status': 'error',
                'message': 'Authentication code expired'
            }), 401
        
        # Get user data from main users table
        user_result = supabase.table('users').select('*').eq('telegram_user_id', telegram_user_id).execute()
        
        if not user_result.data:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user_data = user_result.data[0]
        
        # Get user roles
        roles_result = supabase.table('user_roles').select('role').eq('user_id', user_data['id']).execute()
        user_roles = [role['role'] for role in roles_result.data] if roles_result.data else []
        user_data['roles'] = user_roles
        
        # Create session
        AuthenticationManager.create_session_for_user(telegram_user_id, user_data)
        
        # Clean up auth code
        supabase.table('temp_auth_codes').delete().eq('id', auth_record['id']).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Authentication successful',
            'user': {
                'name': user_data.get('name'),
                'username': user_data.get('username'),
                'roles': user_roles
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Authentication failed'
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Log out current user"""
    AuthenticationManager.logout_user()
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    })

@app.route('/api/user-info')
def get_user_info():
    """Get current user information"""
    user = AuthenticationManager.get_current_user()
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Not authenticated'
        }), 401
        
    return jsonify({
        'status': 'success',
        'user': user
    })

@app.route('/user-dashboard')
@require_auth
def user_dashboard():
    """User's personal progress dashboard"""
    user = AuthenticationManager.get_current_user()
    return render_template('user_dashboard.html', user=user)

@app.route('/api/user-stats')
@require_auth
def get_user_stats():
    """Get comprehensive user statistics for the dashboard"""
    try:
        user = AuthenticationManager.get_current_user()
        if not user or not user_analytics:
            return jsonify({
                'status': 'error',
                'message': 'Analytics system not available'
            }), 500
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats = loop.run_until_complete(
            user_analytics.get_user_stats(user['telegram_user_id'])
        )
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load user statistics'
        }), 500

@app.route('/api/user-commitments')
@require_auth
def get_user_commitments():
    """Get user's recent commitments"""
    try:
        user = AuthenticationManager.get_current_user()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Not authenticated'
            }), 401
        
        # Get user's commitments from database
        commitments_result = supabase.table('commitments').select('*').eq('user_id', user['user_id']).order('created_at', desc=True).limit(20).execute()
        
        commitments = []
        for c in commitments_result.data:
            commitments.append({
                'id': c['id'],
                'commitment_text': c['commitment_text'],
                'status': c.get('status', 'active'),
                'smart_score': c.get('smart_score'),
                'category': c.get('category'),
                'created_at': c['created_at'],
                'due_date': c.get('due_date'),
                'completed_at': c.get('completed_at')
            })
        
        return jsonify({
            'status': 'success',
            'commitments': commitments
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting user commitments: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load commitments'
        }), 500

@app.route('/api/user-achievements')
@require_auth
def get_user_achievements():
    """Get user's achievements"""
    try:
        user = AuthenticationManager.get_current_user()
        if not user or not user_analytics:
            return jsonify({
                'status': 'error',
                'message': 'Analytics system not available'
            }), 500
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        achievements = loop.run_until_complete(
            user_analytics._get_user_achievements(user['user_id'])
        )
        
        return jsonify({
            'status': 'success',
            'achievements': achievements
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting user achievements: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load achievements'
        }), 500

@app.route('/leaderboard')
@require_auth 
def leaderboard_page():
    """Global leaderboard page"""
    user = AuthenticationManager.get_current_user()
    return render_template('leaderboard.html', user=user)

@app.route('/api/leaderboard')
@require_auth
def get_leaderboard():
    """Get global leaderboard data"""
    try:
        # Get all users with commitment stats
        users_result = supabase.table('users').select('*').execute()
        
        leaderboard = []
        for user_data in users_result.data:
            if user_data.get('telegram_user_id'):  # Only include users with Telegram accounts
                # Get commitment counts
                commitments_result = supabase.table('commitments').select('status').eq('user_id', user_data['id']).execute()
                
                total_commitments = len(commitments_result.data)
                completed_commitments = len([c for c in commitments_result.data if c.get('status') == 'completed'])
                
                if total_commitments > 0:  # Only include users with commitments
                    completion_rate = (completed_commitments / total_commitments) * 100
                    
                    leaderboard.append({
                        'name': user_data.get('name', 'Anonymous'),
                        'username': user_data.get('username', ''),
                        'total_commitments': total_commitments,
                        'completed_commitments': completed_commitments,
                        'completion_rate': round(completion_rate, 1),
                        'score': completed_commitments * 10 + total_commitments * 2  # Weighting formula
                    })
        
        # Sort by score (completed commitments weighted higher)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Add ranks
        for i, user in enumerate(leaderboard):
            user['rank'] = i + 1
        
        return jsonify({
            'status': 'success',
            'leaderboard': leaderboard[:50]  # Top 50
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting leaderboard: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load leaderboard'
        }), 500

@app.route('/')
@require_auth
def dashboard():
    """Redirect to user dashboard by default"""
    return redirect(url_for('user_dashboard'))

@app.route('/admin-dashboard')
@require_role('admin')
def admin_dashboard():
    """Admin dashboard showing system overview"""
    user = AuthenticationManager.get_current_user()
    return render_template('dashboard.html', user=user)

@app.route('/api/system-status')
@require_auth
def system_status():
    """Get current system status"""
    try:
        # Test database connection
        result = supabase.table("pods").select("count").execute()
        db_status = "✅ Connected" if result else "❌ Failed"
        
        # Get pod count
        pods_result = supabase.table("pods").select("id, name").execute()
        pod_count = len(pods_result.data) if pods_result.data else 0
        
        # Get recent meetings count
        meetings_result = supabase.table("pod_meetings").select("id").limit(10).execute()
        recent_meetings = len(meetings_result.data) if meetings_result.data else 0
        
        return jsonify({
            'status': 'success',
            'database': db_status,
            'pod_count': pod_count,
            'recent_meetings': recent_meetings,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/pods')
@require_auth
def get_pods():
    """Get all pods"""
    try:
        result = supabase.table("pods").select("*").execute()
        return jsonify({
            'status': 'success',
            'pods': result.data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/pod/<pod_id>/members')
def get_pod_members(pod_id):
    """Get members of a specific pod"""
    try:
        result = supabase.table("pod_memberships").select("*").eq("pod_id", pod_id).execute()
        
        # Get user details for each member
        members = []
        for membership in result.data:
            user_result = supabase.table("users").select("id, name, email").eq("id", membership["user_id"]).execute()
            if user_result.data:
                user = user_result.data[0]
                members.append({
                    'user_id': user['id'],
                    'name': user.get('name', 'Unknown'),
                    'email': user.get('email', 'No email'),
                    'joined_at': membership.get('created_at', 'Unknown')
                })
        
        return jsonify({
            'status': 'success',
            'members': members
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/create-meeting', methods=['POST'])
def create_meeting():
    """Create a new pod meeting with optional Google Calendar integration"""
    try:
        data = request.json
        pod_id = data.get('pod_id')
        meeting_date = data.get('meeting_date')
        event_title = data.get('event_title', '')
        meeting_time = data.get('meeting_time', '19:00')
        duration_minutes = int(data.get('duration_minutes', 60))
        timezone = data.get('timezone', 'America/New_York')
        create_calendar_event = data.get('create_calendar_event', False)
        
        # Create meeting using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        meeting = loop.run_until_complete(
            attendance_system.create_pod_meeting(
                pod_id=pod_id,
                meeting_date=meeting_date,
                status="scheduled"
            )
        )
        
        calendar_event_id = None
        calendar_link = None
        
        # Create Google Calendar event if requested and calendar is available
        if create_calendar_event and google_calendar:
            try:
                calendar_event_id, calendar_link = loop.run_until_complete(
                    create_single_meeting_calendar_event(
                        meeting, meeting_time, duration_minutes, timezone, event_title
                    )
                )
                logger.info(f"📅 Created Google Calendar event: {calendar_event_id}")
            except Exception as e:
                logger.error(f"❌ Failed to create Google Calendar event: {e}")
        
        response_data = {
            'status': 'success',
            'meeting': {
                'id': meeting.id,
                'pod_id': meeting.pod_id,
                'meeting_date': meeting.meeting_date,
                'meeting_time': meeting_time,
                'duration_minutes': duration_minutes,
                'timezone': timezone,
                'status': meeting.status,
                'created_at': meeting.created_at.isoformat(),
                'calendar_event_id': calendar_event_id,
                'calendar_link': calendar_link
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/record-attendance', methods=['POST'])
def record_attendance():
    """Record attendance for a meeting"""
    try:
        data = request.json
        meeting_id = data.get('meeting_id')
        user_id = data.get('user_id')
        attended = data.get('attended', True)
        duration_minutes = data.get('duration_minutes', 60)
        
        # Record attendance using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            attendance_system.record_attendance(
                meeting_id=meeting_id,
                user_id=user_id,
                attended=attended,
                duration_minutes=duration_minutes
            )
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Attendance recorded successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/user/<user_id>/analytics')
def get_user_analytics(user_id):
    """Get analytics for a specific user"""
    try:
        pod_id = request.args.get('pod_id')
        
        # Get analytics using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analytics = loop.run_until_complete(
            attendance_system.calculate_user_attendance_analytics(user_id, pod_id)
        )
        
        return jsonify({
            'status': 'success',
            'analytics': {
                'user_id': analytics.user_id,
                'pod_id': analytics.pod_id,
                'total_meetings': analytics.total_scheduled_meetings,
                'meetings_attended': analytics.meetings_attended,
                'meetings_missed': analytics.meetings_missed,
                'attendance_rate': round(analytics.attendance_rate * 100, 1),
                'average_duration': analytics.average_duration,
                'current_streak': analytics.current_streak,
                'longest_streak': analytics.longest_streak,
                'attendance_pattern': analytics.attendance_pattern.value,
                'engagement_level': analytics.engagement_level.value,
                'risk_flags': analytics.risk_flags,
                'last_attendance': analytics.last_attendance_date.isoformat() if analytics.last_attendance_date else None,
                'prediction_score': analytics.prediction_score
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/pod/<pod_id>/meetings')
def get_pod_meetings(pod_id):
    """Get meetings for a specific pod"""
    try:
        result = supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).order("created_at", desc=True).limit(20).execute()
        
        meetings = []
        for meeting in result.data:
            # Get attendance count for this meeting
            attendance_result = supabase.table("meeting_attendance").select("*").eq("meeting_id", meeting["id"]).execute()
            attendance_count = len([a for a in attendance_result.data if a.get("attended", False)])
            total_responses = len(attendance_result.data)
            
            meetings.append({
                'id': meeting['id'],
                'meeting_date': meeting['meeting_date'],
                'status': meeting['status'],
                'created_at': meeting['created_at'],
                'attendance_count': attendance_count,
                'total_responses': total_responses
            })
        
        return jsonify({
            'status': 'success',
            'meetings': meetings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/meeting/<meeting_id>/attendance')
def get_meeting_attendance(meeting_id):
    """Get attendance records for a specific meeting"""
    try:
        # Get attendance records
        attendance_result = supabase.table("meeting_attendance").select("*").eq("meeting_id", meeting_id).execute()
        
        attendance_records = []
        for record in attendance_result.data:
            # Get user details
            user_result = supabase.table("users").select("id, name, email").eq("id", record["user_id"]).execute()
            user_name = user_result.data[0].get('name', 'Unknown') if user_result.data else 'Unknown'
            
            attendance_records.append({
                'user_id': record['user_id'],
                'user_name': user_name,
                'attended': record.get('attended', False),
                'duration_minutes': record.get('duration_minutes', 0),
                'created_at': record['created_at']
            })
        
        return jsonify({
            'status': 'success',
            'attendance': attendance_records
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/test')
@require_auth
def test_page():
    """Test page with all functionality"""
    return render_template('test.html')

@app.route('/analytics')
@require_auth
def analytics_page():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/api/create-recurring-schedule', methods=['POST'])
def create_recurring_schedule():
    """Create a recurring meeting schedule"""
    try:
        data = request.json
        pod_id = data.get('pod_id')
        recurrence_type = RecurrenceType(data.get('recurrence_type'))
        meeting_day = WeekDay(int(data.get('meeting_day')))
        meeting_time = data.get('meeting_time')
        timezone = data.get('timezone', 'America/New_York')
        duration_minutes = int(data.get('duration_minutes', 60))
        start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None
        end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None
        create_calendar_events = data.get('create_calendar_event', False)
        
        # Create schedule using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        schedule = loop.run_until_complete(
            recurring_manager.create_recurring_schedule(
                pod_id=pod_id,
                recurrence_type=recurrence_type,
                meeting_day=meeting_day,
                meeting_time=meeting_time,
                timezone=timezone,
                duration_minutes=duration_minutes,
                start_date=start_date,
                end_date=end_date,
                create_calendar_events=create_calendar_events
            )
        )
        
        return jsonify({
            'status': 'success',
            'schedule': {
                'id': schedule.id,
                'pod_id': schedule.pod_id,
                'recurrence_type': schedule.recurrence_type.value,
                'meeting_day': schedule.meeting_day.value,
                'meeting_time': schedule.meeting_time,
                'timezone': schedule.timezone,
                'duration_minutes': schedule.duration_minutes,
                'start_date': schedule.start_date.isoformat(),
                'end_date': schedule.end_date.isoformat() if schedule.end_date else None,
                'next_occurrence': schedule.get_next_occurrence().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/pod/<pod_id>/recurring-schedules')
def get_pod_schedules(pod_id):
    """Get recurring schedules for a pod"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        schedules = loop.run_until_complete(
            recurring_manager.get_pod_schedules(pod_id)
        )
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'recurrence_type': schedule.recurrence_type.value,
                'meeting_day': schedule.meeting_day.value,
                'meeting_time': schedule.meeting_time,
                'timezone': schedule.timezone,
                'duration_minutes': schedule.duration_minutes,
                'start_date': schedule.start_date.isoformat(),
                'end_date': schedule.end_date.isoformat() if schedule.end_date else None,
                'is_active': schedule.is_active,
                'next_occurrence': schedule.get_next_occurrence().isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'schedules': schedule_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/generate-meetings-from-schedule', methods=['POST'])
def generate_meetings_from_schedule():
    """Generate individual meetings from a recurring schedule"""
    try:
        data = request.json
        schedule_id = data.get('schedule_id')
        weeks_ahead = int(data.get('weeks_ahead', 4))
        
        # Get the schedule first
        schedule_result = supabase.table("recurring_schedules").select("*").eq("id", schedule_id).execute()
        if not schedule_result.data:
            return jsonify({
                'status': 'error',
                'message': 'Schedule not found'
            }), 404
            
        schedule_data = schedule_result.data[0]
        schedule = RecurringMeetingSchedule(
            id=schedule_data["id"],
            pod_id=schedule_data["pod_id"],
            recurrence_type=RecurrenceType(schedule_data["recurrence_type"]),
            meeting_day=WeekDay(schedule_data["meeting_day"]),
            meeting_time=schedule_data["meeting_time"],
            timezone=schedule_data["timezone"],
            duration_minutes=schedule_data["duration_minutes"],
            start_date=datetime.fromisoformat(schedule_data["start_date"]),
            end_date=datetime.fromisoformat(schedule_data["end_date"]) if schedule_data["end_date"] else None,
            google_calendar_event_id=schedule_data.get("google_calendar_event_id"),
            created_at=datetime.fromisoformat(schedule_data["created_at"]),
            updated_at=datetime.fromisoformat(schedule_data["updated_at"]),
            is_active=schedule_data["is_active"]
        )
        
        # Generate meetings
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        meeting_ids = loop.run_until_complete(
            recurring_manager.generate_meetings_from_schedule(schedule, weeks_ahead)
        )
        
        return jsonify({
            'status': 'success',
            'meetings_generated': len(meeting_ids),
            'meeting_ids': meeting_ids
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

async def create_single_meeting_calendar_event(meeting, meeting_time, duration_minutes, timezone, event_title=""):
    """Create a Google Calendar event for a single meeting"""
    try:
        # Parse meeting time
        hour, minute = map(int, meeting_time.split(':'))
        
        # Create datetime for the meeting
        meeting_datetime = datetime.fromisoformat(meeting.meeting_date)
        meeting_datetime = meeting_datetime.replace(hour=hour, minute=minute)
        
        # Get pod info for the event title
        pod_result = supabase.table("pods").select("name").eq("id", meeting.pod_id).execute()
        pod_name = pod_result.data[0].get('name', f'Pod {meeting.pod_id[:8]}') if pod_result.data else f'Pod {meeting.pod_id[:8]}'
        
        # Use custom event title if provided, otherwise default to pod meeting
        if event_title.strip():
            summary = event_title.strip()
            description = f'{event_title.strip()}\\nPod: {pod_name}\\nMeeting ID: {meeting.id}'
        else:
            summary = f'{pod_name} Meeting'
            description = f'Pod meeting for {pod_name}\\nMeeting ID: {meeting.id}'
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': meeting_datetime.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': (meeting_datetime + timedelta(minutes=duration_minutes)).isoformat(),
                'timeZone': timezone,
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f'pod-meeting-{meeting.id}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 15},       # 15 minutes before
                ],
            },
        }
        
        created_event = google_calendar.service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='none'
        ).execute()
        
        calendar_link = created_event.get('htmlLink')
        meet_link = created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
        
        return created_event['id'], meet_link or calendar_link
        
    except Exception as e:
        logger.error(f"Failed to create calendar event: {e}")
        raise

@app.route('/api/automatic-attendance/sync-date', methods=['POST'])
def sync_attendance_for_date():
    """Manually trigger automatic attendance sync for a specific date"""
    try:
        data = request.json
        sync_date = data.get('sync_date')
        
        if not sync_date:
            return jsonify({
                'status': 'error',
                'message': 'sync_date is required (YYYY-MM-DD format)'
            }), 400
        
        # Parse date
        from datetime import date as date_class
        sync_date_obj = date_class.fromisoformat(sync_date)
        
        if not automatic_attendance:
            return jsonify({
                'status': 'error',
                'message': 'Automatic attendance engine not initialized'
            }), 500
        
        # Run sync in async loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize if needed
        if not automatic_attendance.admin_reports:
            loop.run_until_complete(automatic_attendance.initialize())
        
        result = loop.run_until_complete(
            automatic_attendance.process_meetings_for_date(sync_date_obj)
        )
        
        return jsonify({
            'status': 'success',
            'sync_date': sync_date,
            'results': {
                'total_meetings_processed': result.total_meetings_processed,
                'meetings_with_meet_data': result.meetings_with_meet_data,
                'total_participants_found': result.total_participants_found,
                'attendance_records_created': result.attendance_records_created,
                'attendance_records_updated': result.attendance_records_updated,
                'processing_time_seconds': result.processing_time_seconds,
                'errors': result.errors
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to sync attendance for date: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/automatic-attendance/daily-sync', methods=['POST'])
def run_daily_sync():
    """Run daily sync for yesterday's meetings"""
    try:
        if not automatic_attendance:
            return jsonify({
                'status': 'error',
                'message': 'Automatic attendance engine not initialized'
            }), 500
        
        # Run sync in async loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize if needed
        if not automatic_attendance.admin_reports:
            loop.run_until_complete(automatic_attendance.initialize())
        
        result = loop.run_until_complete(automatic_attendance.run_daily_sync())
        
        return jsonify({
            'status': 'success',
            'results': {
                'total_meetings_processed': result.total_meetings_processed,
                'meetings_with_meet_data': result.meetings_with_meet_data,
                'total_participants_found': result.total_participants_found,
                'attendance_records_created': result.attendance_records_created,
                'attendance_records_updated': result.attendance_records_updated,
                'processing_time_seconds': result.processing_time_seconds,
                'errors': result.errors
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to run daily sync: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/meet-sessions')
def get_meet_sessions():
    """Get all Meet sessions"""
    try:
        result = supabase.table("meet_sessions").select("*, pod_meetings(meeting_date)").order("created_at", desc=True).limit(50).execute()
        
        sessions = []
        for session in result.data:
            sessions.append({
                'id': session['id'],
                'meeting_id': session['meeting_id'],
                'meet_code': session['meet_code'],
                'meet_link': session['meet_link'],
                'organizer_email': session['organizer_email'],
                'participant_count': session['participant_count'],
                'duration_minutes': session.get('duration_minutes'),
                'sync_status': session['sync_status'],
                'last_sync_at': session.get('last_sync_at'),
                'meeting_date': session.get('pod_meetings', {}).get('meeting_date'),
                'created_at': session['created_at']
            })
        
        return jsonify({
            'status': 'success',
            'sessions': sessions
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/meet-sessions/<session_id>/participants')
def get_meet_session_participants(session_id):
    """Get participants for a specific Meet session"""
    try:
        result = supabase.table("meet_participants").select("*").eq("meet_session_id", session_id).execute()
        
        participants = []
        for participant in result.data:
            participants.append({
                'id': participant['id'],
                'participant_email': participant['participant_email'],
                'participant_name': participant.get('participant_name'),
                'device_type': participant['device_type'],
                'is_external': participant['is_external'],
                'joined_at': participant.get('joined_at'),
                'left_at': participant.get('left_at'),
                'duration_minutes': participant['duration_minutes'],
                'reconnect_count': participant['reconnect_count'],
                'audio_minutes': participant['audio_minutes'],
                'video_minutes': participant['video_minutes'],
                'call_rating': participant.get('call_rating')
            })
        
        return jsonify({
            'status': 'success',
            'participants': participants
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/meet-sessions/<session_id>/sync', methods=['POST'])
def sync_meet_session(session_id):
    """Manually sync a specific Meet session"""
    try:
        data = request.json
        sync_date = data.get('sync_date')
        
        if not automatic_attendance or not automatic_attendance.correlation_engine:
            return jsonify({
                'status': 'error',
                'message': 'Meet correlation engine not initialized'
            }), 500
        
        # Parse date if provided
        sync_date_obj = None
        if sync_date:
            from datetime import date as date_class
            sync_date_obj = date_class.fromisoformat(sync_date)
        
        # Run sync in async loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            automatic_attendance.correlation_engine.sync_meet_session_data(session_id, sync_date_obj)
        )
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'sync_result': result
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to sync Meet session {session_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/automatic-attendance')
@require_role('admin')
def automatic_attendance_page():
    """Automatic attendance management page"""
    return render_template('automatic_attendance.html')

if __name__ == '__main__':
    print("🚀 Starting Attendance System Web Interface")
    print("=" * 50)
    
    # Initialize systems
    if initialize_systems():
        print("✅ Systems initialized successfully")
        print("🌐 Starting web server at http://localhost:8080")
        print("📊 Available pages:")
        print("   - http://localhost:8080/ (Main Dashboard)")
        print("   - http://localhost:8080/test (Test Features)")
        print("   - http://localhost:8080/analytics (Analytics View)")
        print("   - http://localhost:8080/automatic-attendance (Meet Attendance)")
        
        app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
    else:
        print("❌ Failed to initialize systems")
        print("Check your .env configuration and database connection")