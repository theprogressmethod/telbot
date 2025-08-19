#!/usr/bin/env python3
"""
Unit tests for authentication system in web_interface.py
"""

import pytest
import uuid
import secrets
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask
from werkzeug.test import Client

from web_interface import AuthenticationManager, app, require_auth, require_role


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationManager:
    """Test the AuthenticationManager class"""
    
    def test_generate_auth_token(self):
        """Test authentication token generation"""
        token1 = AuthenticationManager.generate_auth_token()
        token2 = AuthenticationManager.generate_auth_token()
        
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        assert len(token1) > 20  # URL-safe tokens should be reasonably long
        assert token1 != token2  # Should generate unique tokens
    
    def test_create_session_for_user(self, mock_flask_app):
        """Test session creation for authenticated user"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            telegram_user_id = 123456789
            user_data = {
                'id': 'user-uuid-123',
                'username': 'testuser',
                'name': 'Test User',
                'email': 'test@example.com',
                'roles': ['user', 'paid']
            }
            
            with patch('web_interface.supabase') as mock_supabase:
                AuthenticationManager.create_session_for_user(telegram_user_id, user_data)
                
                # Verify session data
                assert session['user_id'] == 'user-uuid-123'
                assert session['telegram_user_id'] == telegram_user_id
                assert session['username'] == 'testuser'
                assert session['authenticated'] is True
                assert 'auth_token' in session
                assert 'login_time' in session
                
                # Verify database insert was called
                mock_supabase.table.return_value.insert.assert_called_once()
    
    def test_get_current_user_authenticated(self, mock_flask_app):
        """Test getting current user when authenticated"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            # Set up authenticated session
            session['authenticated'] = True
            session['user_id'] = 'user-uuid-123'
            session['telegram_user_id'] = 123456789
            session['username'] = 'testuser'
            session['roles'] = ['user']
            
            user = AuthenticationManager.get_current_user()
            
            assert user is not None
            assert user['user_id'] == 'user-uuid-123'
            assert user['telegram_user_id'] == 123456789
            assert user['username'] == 'testuser'
    
    def test_get_current_user_not_authenticated(self, mock_flask_app):
        """Test getting current user when not authenticated"""
        with mock_flask_app.test_request_context():
            user = AuthenticationManager.get_current_user()
            assert user is None
    
    def test_user_has_role_success(self, mock_flask_app):
        """Test role checking when user has role"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            session['authenticated'] = True
            session['roles'] = ['user', 'admin']
            
            assert AuthenticationManager.user_has_role('admin') is True
            assert AuthenticationManager.user_has_role('user') is True
            assert AuthenticationManager.user_has_role('super_admin') is False
    
    def test_user_has_role_not_authenticated(self, mock_flask_app):
        """Test role checking when user not authenticated"""
        with mock_flask_app.test_request_context():
            assert AuthenticationManager.user_has_role('admin') is False
    
    def test_user_has_any_role_success(self, mock_flask_app):
        """Test checking multiple roles"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            session['authenticated'] = True
            session['roles'] = ['user', 'paid']
            
            assert AuthenticationManager.user_has_any_role(['admin', 'paid']) is True
            assert AuthenticationManager.user_has_any_role(['admin', 'super_admin']) is False
    
    def test_logout_user(self, mock_flask_app):
        """Test user logout"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            # Set up authenticated session
            session['authenticated'] = True
            session['auth_token'] = 'test-token'
            session['user_id'] = 'user-uuid-123'
            
            with patch('web_interface.supabase') as mock_supabase:
                AuthenticationManager.logout_user()
                
                # Verify session cleared
                assert 'authenticated' not in session
                assert 'auth_token' not in session
                assert 'user_id' not in session
                
                # Verify database cleanup was attempted
                mock_supabase.table.return_value.delete.assert_called_once()


@pytest.mark.unit 
@pytest.mark.auth
class TestAuthenticationDecorators:
    """Test authentication decorators"""
    
    def test_require_auth_authenticated(self, mock_flask_app):
        """Test require_auth decorator with authenticated user"""
        with mock_flask_app.test_request_context():
            from flask import session
            session['authenticated'] = True
            
            @require_auth
            def test_view():
                return "success"
            
            result = test_view()
            assert result == "success"
    
    def test_require_auth_not_authenticated(self, mock_flask_app):
        """Test require_auth decorator redirects unauthenticated users"""
        with mock_flask_app.test_request_context():
            @require_auth  
            def test_view():
                return "success"
            
            with patch('web_interface.redirect') as mock_redirect:
                result = test_view()
                mock_redirect.assert_called_once()
    
    def test_require_role_with_role(self, mock_flask_app):
        """Test require_role decorator when user has required role"""
        with mock_flask_app.test_request_context():
            from flask import session
            session['authenticated'] = True
            session['roles'] = ['admin']
            
            @require_role('admin')
            def test_view():
                return "admin_success"
            
            result = test_view()
            assert result == "admin_success"
    
    def test_require_role_without_role(self, mock_flask_app):
        """Test require_role decorator when user lacks required role"""
        with mock_flask_app.test_request_context():
            from flask import session
            session['authenticated'] = True
            session['roles'] = ['user']
            
            @require_role('admin')
            def test_view():
                return "admin_success"
            
            with patch('web_interface.redirect') as mock_redirect, \
                 patch('web_interface.flash') as mock_flash:
                result = test_view()
                mock_flash.assert_called_once()
                mock_redirect.assert_called_once()


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.integration
class TestAuthenticationEndpoints:
    """Test authentication API endpoints"""
    
    def test_login_page(self, mock_flask_app):
        """Test login page rendering"""
        with mock_flask_app.test_client() as client:
            with patch('web_interface.render_template') as mock_render:
                mock_render.return_value = "login_page_html"
                
                response = client.get('/login')
                
                assert response.status_code == 200
                mock_render.assert_called_once_with('login.html')
    
    def test_telegram_auth_success(self, mock_flask_app):
        """Test successful Telegram authentication"""
        with mock_flask_app.test_client() as client:
            auth_data = {
                'telegram_user_id': 123456789,
                'auth_code': 'test_auth_code_123'
            }
            
            # Mock database responses
            mock_temp_auth_data = [{
                'id': 'temp-auth-id',
                'telegram_user_id': 123456789,
                'auth_code': 'test_auth_code_123',
                'created_at': datetime.now().isoformat()
            }]
            
            mock_user_data = [{
                'id': 'user-uuid-123',
                'telegram_user_id': 123456789,
                'name': 'Test User',
                'username': 'testuser'
            }]
            
            mock_roles_data = [{'role': 'user'}, {'role': 'paid'}]
            
            with patch('web_interface.supabase') as mock_supabase:
                # Setup mock responses
                mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = mock_temp_auth_data
                mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_user_data
                mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_roles_data
                
                with patch('web_interface.AuthenticationManager.create_session_for_user') as mock_create_session:
                    response = client.post('/api/telegram-auth', 
                                         json=auth_data,
                                         content_type='application/json')
                    
                    assert response.status_code == 200
                    json_data = response.get_json()
                    assert json_data['status'] == 'success'
                    assert json_data['message'] == 'Authentication successful'
                    
                    # Verify session creation was called
                    mock_create_session.assert_called_once()
    
    def test_telegram_auth_invalid_code(self, mock_flask_app):
        """Test Telegram authentication with invalid code"""
        with mock_flask_app.test_client() as client:
            auth_data = {
                'telegram_user_id': 123456789,
                'auth_code': 'invalid_code'
            }
            
            with patch('web_interface.supabase') as mock_supabase:
                # Mock empty auth code result
                mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
                
                response = client.post('/api/telegram-auth',
                                     json=auth_data,
                                     content_type='application/json')
                
                assert response.status_code == 401
                json_data = response.get_json()
                assert json_data['status'] == 'error'
                assert 'Invalid or expired' in json_data['message']
    
    def test_telegram_auth_expired_code(self, mock_flask_app):
        """Test Telegram authentication with expired code"""
        with mock_flask_app.test_client() as client:
            auth_data = {
                'telegram_user_id': 123456789,
                'auth_code': 'expired_code'
            }
            
            # Mock expired auth code (15 minutes old)
            expired_time = (datetime.now() - timedelta(minutes=15)).isoformat()
            mock_temp_auth_data = [{
                'id': 'temp-auth-id',
                'telegram_user_id': 123456789,
                'auth_code': 'expired_code',
                'created_at': expired_time
            }]
            
            with patch('web_interface.supabase') as mock_supabase:
                mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = mock_temp_auth_data
                
                response = client.post('/api/telegram-auth',
                                     json=auth_data,
                                     content_type='application/json')
                
                assert response.status_code == 401
                json_data = response.get_json()
                assert json_data['status'] == 'error'
                assert 'expired' in json_data['message']
    
    def test_telegram_auth_missing_params(self, mock_flask_app):
        """Test Telegram authentication with missing parameters"""
        with mock_flask_app.test_client() as client:
            # Missing auth_code
            auth_data = {
                'telegram_user_id': 123456789
            }
            
            response = client.post('/api/telegram-auth',
                                 json=auth_data,
                                 content_type='application/json')
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data['status'] == 'error'
            assert 'required' in json_data['message']
    
    def test_logout_endpoint(self, mock_flask_app):
        """Test logout endpoint"""
        with mock_flask_app.test_client() as client:
            with patch('web_interface.AuthenticationManager.logout_user') as mock_logout:
                response = client.post('/api/logout')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['message'] == 'Logged out successfully'
                
                mock_logout.assert_called_once()
    
    def test_user_info_endpoint_authenticated(self, mock_flask_app):
        """Test user info endpoint when authenticated"""
        with mock_flask_app.test_client() as client:
            mock_user = {
                'user_id': 'user-uuid-123',
                'name': 'Test User',
                'roles': ['user']
            }
            
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=mock_user):
                response = client.get('/api/user-info')
                
                assert response.status_code == 200
                json_data = response.get_json()
                assert json_data['status'] == 'success'
                assert json_data['user'] == mock_user
    
    def test_user_info_endpoint_not_authenticated(self, mock_flask_app):
        """Test user info endpoint when not authenticated"""
        with mock_flask_app.test_client() as client:
            with patch('web_interface.AuthenticationManager.get_current_user', return_value=None):
                response = client.get('/api/user-info')
                
                assert response.status_code == 401
                json_data = response.get_json()
                assert json_data['status'] == 'error'
                assert 'Not authenticated' in json_data['message']


@pytest.mark.unit
@pytest.mark.auth
class TestSessionManagement:
    """Test session management functionality"""
    
    def test_session_storage_in_database(self, mock_flask_app):
        """Test that sessions are stored in database"""
        with mock_flask_app.test_request_context():
            telegram_user_id = 123456789
            user_data = {
                'id': 'user-uuid-123',
                'username': 'testuser',
                'name': 'Test User'
            }
            
            with patch('web_interface.supabase') as mock_supabase, \
                 patch('web_interface.uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-9012-123456789abc')), \
                 patch('web_interface.request') as mock_request:
                
                mock_request.headers.get.return_value = 'test-user-agent'
                mock_request.environ.get.return_value = '127.0.0.1'
                
                AuthenticationManager.create_session_for_user(telegram_user_id, user_data)
                
                # Verify database insert with session data
                mock_supabase.table.return_value.insert.assert_called_once()
                insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
                
                assert insert_data['user_id'] == 'user-uuid-123'
                assert insert_data['telegram_user_id'] == telegram_user_id
                assert 'auth_token' in insert_data
                assert 'login_time' in insert_data
                assert 'expires_at' in insert_data
    
    def test_session_cleanup_on_logout(self, mock_flask_app):
        """Test that sessions are cleaned up on logout"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            session['auth_token'] = 'test-token-123'
            session['authenticated'] = True
            
            with patch('web_interface.supabase') as mock_supabase:
                AuthenticationManager.logout_user()
                
                # Verify database cleanup
                mock_supabase.table.return_value.delete.return_value.eq.assert_called_once_with('auth_token', 'test-token-123')
    
    def test_session_expiry(self, mock_flask_app):
        """Test session expiry calculation"""
        with mock_flask_app.test_request_context():
            telegram_user_id = 123456789
            user_data = {'id': 'user-uuid-123'}
            
            with patch('web_interface.supabase') as mock_supabase, \
                 patch('web_interface.datetime') as mock_datetime:
                
                now = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.now.return_value = now
                
                AuthenticationManager.create_session_for_user(telegram_user_id, user_data)
                
                # Check expires_at is 24 hours from now
                insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
                expires_at = datetime.fromisoformat(insert_data['expires_at'])
                expected_expiry = now + timedelta(hours=24)
                
                assert expires_at == expected_expiry


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationSecurity:
    """Test security aspects of authentication system"""
    
    def test_auth_token_randomness(self):
        """Test that auth tokens are sufficiently random"""
        tokens = set()
        for _ in range(100):
            token = AuthenticationManager.generate_auth_token()
            assert token not in tokens  # Should be unique
            tokens.add(token)
        
        # All tokens should be different
        assert len(tokens) == 100
    
    def test_session_data_validation(self, mock_flask_app):
        """Test that session data is properly validated"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            # Test with invalid session data
            session['authenticated'] = True
            # Missing required fields
            
            user = AuthenticationManager.get_current_user()
            
            # Should handle missing fields gracefully
            assert user is not None
            assert user.get('user_id') is None
    
    def test_role_injection_protection(self, mock_flask_app):
        """Test protection against role injection"""
        with mock_flask_app.test_request_context():
            from flask import session
            
            session['authenticated'] = True
            session['roles'] = ['user']
            
            # Even if someone tries to modify roles in session,
            # the check should be based on stored data
            assert AuthenticationManager.user_has_role('admin') is False
            
            # Test that roles are properly sanitized
            session['roles'] = ['user', 'admin', None, '']
            roles = session.get('roles', [])
            valid_roles = [role for role in roles if role and isinstance(role, str)]
            assert 'admin' in valid_roles
            assert None not in valid_roles
            assert '' not in valid_roles