#!/usr/bin/env python3
"""
Unit tests for dashboard functionality in web_interface.py
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask

from web_interface import app, initialize_systems, system_status, get_pods, create_meeting


@pytest.mark.unit
@pytest.mark.dashboard
class TestSystemInitialization:
    """Test system initialization functionality"""
    
    def test_initialize_systems_success(self):
        """Test successful system initialization"""
        with patch('web_interface.Config') as mock_config, \
             patch('web_interface.create_client') as mock_create_client, \
             patch('web_interface.AttendanceSystemAdapted') as mock_attendance, \
             patch('web_interface.GoogleCalendarAttendance') as mock_google, \
             patch('web_interface.RecurringMeetingManager') as mock_recurring, \
             patch('web_interface.AutomaticAttendanceEngine') as mock_auto_attendance, \
             patch('web_interface.UserAnalytics') as mock_analytics:
            
            # Mock successful initialization
            mock_config.return_value = Mock()
            mock_create_client.return_value = Mock()
            mock_attendance.return_value = Mock()
            mock_google.return_value = Mock()
            mock_recurring.return_value = Mock()
            mock_auto_attendance.return_value = Mock()
            mock_analytics.return_value = Mock()
            
            result = initialize_systems()
            
            assert result is True
    
    def test_initialize_systems_failure(self):
        """Test system initialization failure"""
        with patch('web_interface.Config', side_effect=Exception("Config error")):
            result = initialize_systems()
            assert result is False


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardEndpoints:
    """Test dashboard API endpoints"""
    
    def test_system_status_success(self, mock_flask_app):
        """Test successful system status endpoint"""
        with mock_flask_app.test_client() as client:
            mock_user = {'user_id': 'user-123'}
            mock_supabase_result = Mock()
            mock_supabase_result.data = [{'id': '1'}, {'id': '2'}]
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.supabase') as mock_supabase:
                
                # Setup mock responses
                mock_supabase.table.return_value.select.return_value.execute.return_value = mock_supabase_result
                mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_supabase_result
                
                response = client.get('/api/system-status')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert 'database' in json_data
                assert 'pod_count' in json_data
                assert 'recent_meetings' in json_data
    
    def test_system_status_database_error(self, mock_flask_app):
        """Test system status endpoint with database error"""
        with mock_flask_app.test_client() as client:
            mock_user = {'user_id': 'user-123'}
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.supabase.table', side_effect=Exception("DB Error")):
                
                response = client.get('/api/system-status')
                
                assert response.status_code == 500
                json_data = response.get_json()
                assert json_data['status'] == 'error'
    
    def test_get_pods_success(self, mock_flask_app):
        """Test successful pods retrieval"""
        with mock_flask_app.test_client() as client:
            mock_user = {'user_id': 'user-123'}
            mock_pods = [
                {'id': 'pod-1', 'name': 'Test Pod 1'},
                {'id': 'pod-2', 'name': 'Test Pod 2'}
            ]
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.supabase') as mock_supabase:
                
                mock_supabase.table.return_value.select.return_value.execute.return_value.data = mock_pods
                
                response = client.get('/api/pods')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['pods'] == mock_pods
    
    def test_get_pod_members_success(self, mock_flask_app):
        """Test successful pod members retrieval"""
        with mock_flask_app.test_client() as client:
            pod_id = 'pod-123'
            mock_memberships = [
                {'user_id': 'user-1', 'created_at': '2023-01-01'},
                {'user_id': 'user-2', 'created_at': '2023-01-02'}
            ]
            mock_users = [
                {'id': 'user-1', 'name': 'User 1', 'email': 'user1@test.com'},
                {'id': 'user-2', 'name': 'User 2', 'email': 'user2@test.com'}
            ]
            
            with patch('web_interface.supabase') as mock_supabase:
                def mock_table_chain(table_name):
                    if table_name == 'pod_memberships':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=mock_memberships))
                                ))
                            ))
                        )
                    elif table_name == 'users':
                        # Return different users based on query
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=[mock_users[0]]))  # First call
                                ))
                            ))
                        )
                
                mock_supabase.table.side_effect = mock_table_chain
                
                response = client.get(f'/api/pod/{pod_id}/members')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert len(json_data['members']) >= 1


@pytest.mark.unit
@pytest.mark.dashboard
class TestMeetingEndpoints:
    """Test meeting management endpoints"""
    
    def test_create_meeting_success(self, mock_flask_app):
        """Test successful meeting creation"""
        with mock_flask_app.test_client() as client:
            meeting_data = {
                'pod_id': 'pod-123',
                'meeting_date': '2023-12-01',
                'event_title': 'Test Meeting',
                'meeting_time': '14:00',
                'duration_minutes': 60
            }
            
            mock_meeting = Mock()
            mock_meeting.id = 'meeting-123'
            mock_meeting.pod_id = 'pod-123'
            mock_meeting.meeting_date = '2023-12-01'
            mock_meeting.status = 'scheduled'
            mock_meeting.created_at = datetime.now()
            
            with patch('web_interface.attendance_system') as mock_attendance, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.return_value = mock_meeting
                
                response = client.post('/api/create-meeting',
                                     json=meeting_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['meeting']['id'] == 'meeting-123'
    
    def test_create_meeting_with_calendar_integration(self, mock_flask_app):
        """Test meeting creation with Google Calendar integration"""
        with mock_flask_app.test_client() as client:
            meeting_data = {
                'pod_id': 'pod-123',
                'meeting_date': '2023-12-01',
                'create_calendar_event': True,
                'meeting_time': '14:00',
                'duration_minutes': 60,
                'timezone': 'America/New_York'
            }
            
            mock_meeting = Mock()
            mock_meeting.id = 'meeting-123'
            mock_meeting.pod_id = 'pod-123'
            mock_meeting.meeting_date = '2023-12-01'
            mock_meeting.status = 'scheduled'
            mock_meeting.created_at = datetime.now()
            
            with patch('web_interface.attendance_system') as mock_attendance, \
                 patch('web_interface.google_calendar') as mock_google_calendar, \
                 patch('web_interface.create_single_meeting_calendar_event') as mock_create_event, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.side_effect = [
                    mock_meeting,  # First call for meeting creation
                    ('cal-event-123', 'https://calendar.link')  # Second call for calendar event
                ]
                
                response = client.post('/api/create-meeting',
                                     json=meeting_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['meeting']['calendar_event_id'] == 'cal-event-123'
                assert json_data['meeting']['calendar_link'] == 'https://calendar.link'
    
    def test_record_attendance_success(self, mock_flask_app):
        """Test successful attendance recording"""
        with mock_flask_app.test_client() as client:
            attendance_data = {
                'meeting_id': 'meeting-123',
                'user_id': 'user-456',
                'attended': True,
                'duration_minutes': 45
            }
            
            with patch('web_interface.attendance_system') as mock_attendance, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.return_value = None  # Success
                
                response = client.post('/api/record-attendance',
                                     json=attendance_data,
                                     content_type='application/json')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert 'Attendance recorded successfully' in json_data['message']
    
    def test_get_pod_meetings_success(self, mock_flask_app):
        """Test successful pod meetings retrieval"""
        with mock_flask_app.test_client() as client:
            pod_id = 'pod-123'
            mock_meetings = [
                {
                    'id': 'meeting-1',
                    'meeting_date': '2023-12-01',
                    'status': 'scheduled',
                    'created_at': '2023-11-30'
                },
                {
                    'id': 'meeting-2', 
                    'meeting_date': '2023-12-02',
                    'status': 'completed',
                    'created_at': '2023-12-01'
                }
            ]
            
            mock_attendance_data = [
                {'attended': True},
                {'attended': False}
            ]
            
            with patch('web_interface.supabase') as mock_supabase:
                def mock_table_behavior(table_name):
                    if table_name == 'pod_meetings':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    order=Mock(return_value=Mock(
                                        limit=Mock(return_value=Mock(
                                            execute=Mock(return_value=Mock(data=mock_meetings))
                                        ))
                                    ))
                                ))
                            ))
                        )
                    elif table_name == 'meeting_attendance':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=mock_attendance_data))
                                ))
                            ))
                        )
                
                mock_supabase.table.side_effect = mock_table_behavior
                
                response = client.get(f'/api/pod/{pod_id}/meetings')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert len(json_data['meetings']) == len(mock_meetings)
    
    def test_get_meeting_attendance_success(self, mock_flask_app):
        """Test successful meeting attendance retrieval"""
        with mock_flask_app.test_client() as client:
            meeting_id = 'meeting-123'
            mock_attendance = [
                {
                    'user_id': 'user-1',
                    'attended': True,
                    'duration_minutes': 60,
                    'created_at': '2023-12-01'
                }
            ]
            
            mock_user = {
                'id': 'user-1',
                'name': 'Test User',
                'email': 'test@example.com'
            }
            
            with patch('web_interface.supabase') as mock_supabase:
                def mock_table_behavior(table_name):
                    if table_name == 'meeting_attendance':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=mock_attendance))
                                ))
                            ))
                        )
                    elif table_name == 'users':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=[mock_user]))
                                ))
                            ))
                        )
                
                mock_supabase.table.side_effect = mock_table_behavior
                
                response = client.get(f'/api/meeting/{meeting_id}/attendance')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert len(json_data['attendance']) == 1
                assert json_data['attendance'][0]['user_name'] == 'Test User'


@pytest.mark.unit
@pytest.mark.dashboard
class TestAnalyticsEndpoints:
    """Test analytics dashboard endpoints"""
    
    def test_get_user_analytics_success(self, mock_flask_app):
        """Test successful user analytics retrieval"""
        with mock_flask_app.test_client() as client:
            user_id = 'user-123'
            mock_analytics = Mock()
            mock_analytics.user_id = user_id
            mock_analytics.pod_id = 'pod-456'
            mock_analytics.total_scheduled_meetings = 10
            mock_analytics.meetings_attended = 8
            mock_analytics.meetings_missed = 2
            mock_analytics.attendance_rate = 0.8
            mock_analytics.average_duration = 45.5
            mock_analytics.current_streak = 3
            mock_analytics.longest_streak = 5
            mock_analytics.attendance_pattern = Mock(value='consistent')
            mock_analytics.engagement_level = Mock(value='high')
            mock_analytics.risk_flags = []
            mock_analytics.last_attendance_date = datetime.now()
            mock_analytics.prediction_score = 0.85
            
            with patch('web_interface.attendance_system') as mock_attendance_system, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.return_value = mock_analytics
                
                response = client.get(f'/api/user/{user_id}/analytics?pod_id=pod-456')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['analytics']['user_id'] == user_id
                assert json_data['analytics']['attendance_rate'] == 80.0  # Converted to percentage
    
    def test_get_user_analytics_error(self, mock_flask_app):
        """Test user analytics endpoint with error"""
        with mock_flask_app.test_client() as client:
            user_id = 'user-123'
            
            with patch('web_interface.attendance_system') as mock_attendance_system, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.side_effect = Exception("Analytics error")
                
                response = client.get(f'/api/user/{user_id}/analytics')
                
                assert response.status_code == 500
                json_data = response.get_json()
                assert json_data['status'] == 'error'


@pytest.mark.unit
@pytest.mark.dashboard
class TestUserDashboardEndpoints:
    """Test user dashboard specific endpoints"""
    
    def test_user_dashboard_page(self, mock_flask_app):
        """Test user dashboard page rendering"""
        with mock_flask_app.test_client() as client:
            mock_user = {'name': 'Test User', 'roles': ['user']}
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.render_template') as mock_render:
                
                mock_render.return_value = "dashboard_html"
                
                response = client.get('/user-dashboard')
                
                assert response.status_code == 200
                mock_render.assert_called_once_with('user_dashboard.html', user=mock_user)
    
    def test_get_user_stats_success(self, mock_flask_app):
        """Test successful user stats retrieval"""
        with mock_flask_app.test_client() as client:
            mock_user = {
                'telegram_user_id': 123456789,
                'user_id': 'user-123'
            }
            mock_stats = {
                'total_commitments': 15,
                'completed_commitments': 12,
                'completion_rate': 80.0,
                'current_streak': 5
            }
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.user_analytics') as mock_user_analytics, \
                 patch('web_interface.asyncio') as mock_asyncio:
                
                mock_loop = Mock()
                mock_asyncio.new_event_loop.return_value = mock_loop
                mock_loop.run_until_complete.return_value = mock_stats
                
                response = client.get('/api/user-stats')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['stats'] == mock_stats
    
    def test_get_user_stats_not_authenticated(self, mock_flask_app):
        """Test user stats endpoint when not authenticated"""
        with mock_flask_app.test_client() as client:
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=None):
                response = client.get('/api/user-stats')
                
                # Should redirect to login or return 401
                assert response.status_code in [302, 401]
    
    def test_get_user_commitments_success(self, mock_flask_app):
        """Test successful user commitments retrieval"""
        with mock_flask_app.test_client() as client:
            mock_user = {'user_id': 'user-123'}
            mock_commitments = [
                {
                    'id': 'commit-1',
                    'commitment_text': 'Read for 30 minutes',
                    'status': 'active',
                    'smart_score': 8,
                    'created_at': '2023-12-01'
                },
                {
                    'id': 'commit-2',
                    'commitment_text': 'Exercise for 1 hour',
                    'status': 'completed',
                    'smart_score': 9,
                    'created_at': '2023-12-02',
                    'completed_at': '2023-12-02'
                }
            ]
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.supabase') as mock_supabase:
                
                mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_commitments
                
                response = client.get('/api/user-commitments')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert len(json_data['commitments']) == 2
                assert json_data['commitments'][0]['commitment_text'] == 'Read for 30 minutes'
    
    def test_get_leaderboard_success(self, mock_flask_app):
        """Test successful leaderboard retrieval"""
        with mock_flask_app.test_client() as client:
            mock_user = {'user_id': 'user-123'}
            mock_users = [
                {
                    'id': 'user-1',
                    'telegram_user_id': 123,
                    'name': 'User 1',
                    'username': 'user1'
                },
                {
                    'id': 'user-2',
                    'telegram_user_id': 456,
                    'name': 'User 2',
                    'username': 'user2'
                }
            ]
            
            mock_commitments = [
                {'status': 'completed'},
                {'status': 'completed'},
                {'status': 'active'}
            ]
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user), \
                 patch('web_interface.supabase') as mock_supabase:
                
                def mock_table_behavior(table_name):
                    if table_name == 'users':
                        return Mock(
                            select=Mock(return_value=Mock(
                                execute=Mock(return_value=Mock(data=mock_users))
                            ))
                        )
                    elif table_name == 'commitments':
                        return Mock(
                            select=Mock(return_value=Mock(
                                eq=Mock(return_value=Mock(
                                    execute=Mock(return_value=Mock(data=mock_commitments))
                                ))
                            ))
                        )
                
                mock_supabase.table.side_effect = mock_table_behavior
                
                response = client.get('/api/leaderboard')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert 'leaderboard' in json_data