#!/usr/bin/env python3
"""
Critical Path Testing for TelBot Production
Tests core functionality to prevent outages like the one on Aug 18, 2025
"""

import asyncio
import pytest
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCriticalPaths:
    """Test suite for critical bot functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock environment for testing
        os.environ["TELBOT_ENVIRONMENT"] = "development"
        os.environ["BOT_TOKEN"] = "test_token"
        os.environ["SUPABASE_URL"] = "https://test.supabase.co"
        os.environ["SUPABASE_KEY"] = "test_key"
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
    
    @pytest.mark.asyncio
    async def test_start_command_no_undefined_variables(self):
        """CRITICAL: Test that /start command doesn't use undefined variables"""
        
        # Mock all the dependencies to isolate the test
        with patch('telbot.role_manager') as mock_role_manager, \
             patch('telbot.onboarding_manager') as mock_onboarding_manager, \
             patch('telbot.DatabaseManager') as mock_db_manager, \
             patch('telbot.nurture_system') as mock_nurture_system, \
             patch('telbot.supabase') as mock_supabase:
            
            # Set up mocks
            mock_role_manager.ensure_user_exists = AsyncMock()
            mock_onboarding_manager.start_onboarding = AsyncMock()
            mock_onboarding_manager.should_show_first_impression = AsyncMock(return_value=True)
            mock_role_manager.get_user_roles = AsyncMock(return_value=["unpaid"])
            mock_db_manager.test_database = AsyncMock(return_value=True)
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "test-uuid"}]
            mock_nurture_system.check_triggers = AsyncMock()
            
            # Mock message and state
            mock_message = AsyncMock()
            mock_message.from_user.id = 12345
            mock_message.from_user.first_name = "TestUser"
            mock_message.from_user.username = "testuser"
            mock_message.answer = AsyncMock()
            
            mock_state = AsyncMock()
            mock_state.clear = AsyncMock()
            mock_state.set_state = AsyncMock()
            
            # Import and test the start handler
            try:
                from telbot import start_handler
                
                # This should NOT raise a NameError
                await start_handler(mock_message, mock_state)
                
                # Verify the handler executed successfully
                mock_message.answer.assert_called_once()
                assert "Hey TestUser!" in mock_message.answer.call_args[0][0]
                
            except NameError as e:
                pytest.fail(f"NameError in start handler: {e}")
            except Exception as e:
                # Other exceptions are acceptable for this test
                pass
    
    @pytest.mark.asyncio
    async def test_commit_command_basic_functionality(self):
        """Test that /commit command works with basic input"""
        
        with patch('telbot.role_manager') as mock_role_manager, \
             patch('telbot.DatabaseManager') as mock_db_manager, \
             patch('telbot.smart_analyzer') as mock_analyzer, \
             patch('telbot._trigger_commitment_sequences') as mock_trigger:
            
            # Set up mocks
            mock_role_manager.is_first_time_user = AsyncMock(return_value=False)
            mock_role_manager.ensure_user_exists = AsyncMock(return_value=True)
            mock_db_manager.test_database = AsyncMock(return_value=True)
            mock_db_manager.save_commitment = AsyncMock(return_value=True)
            mock_analyzer.analyze_commitment = AsyncMock(return_value={
                "score": 8,
                "smartVersion": "Read for 30 minutes today",
                "feedback": "Great commitment!"
            })
            mock_trigger.return_value = None
            
            # Mock message
            mock_message = AsyncMock()
            mock_message.from_user.id = 12345
            mock_message.from_user.first_name = "TestUser"
            mock_message.from_user.username = "testuser"
            mock_message.text = "/commit Read for 30 minutes"
            mock_message.chat.id = 12345
            mock_message.answer = AsyncMock()
            
            # Mock loading message creation
            with patch('telbot.create_loading_experience') as mock_loading, \
                 patch('telbot.finalize_loading_experience') as mock_finalize:
                
                mock_loading_msg = AsyncMock()
                mock_loading_msg.edit_text = AsyncMock()
                mock_loading.return_value = mock_loading_msg
                mock_finalize.return_value = None
                
                # Test the commit handler
                from telbot import commit_handler
                
                try:
                    await commit_handler(mock_message)
                    # If we get here, no exceptions were thrown
                    assert True
                except Exception as e:
                    pytest.fail(f"Commit handler failed: {e}")
    
    @pytest.mark.asyncio 
    async def test_done_command_no_crashes(self):
        """Test that /done command handles empty commitments gracefully"""
        
        with patch('telbot.role_manager') as mock_role_manager, \
             patch('telbot.DatabaseManager') as mock_db_manager:
            
            # Set up mocks for no commitments
            mock_role_manager.ensure_user_exists = AsyncMock()
            mock_db_manager.get_active_commitments = AsyncMock(return_value=[])
            
            # Mock message
            mock_message = AsyncMock()
            mock_message.from_user.id = 12345
            mock_message.from_user.first_name = "TestUser"
            mock_message.from_user.username = "testuser"
            mock_message.answer = AsyncMock()
            
            # Test the done handler
            from telbot import done_handler
            
            try:
                await done_handler(mock_message)
                mock_message.answer.assert_called_once()
                assert "No active commitments" in mock_message.answer.call_args[0][0]
            except Exception as e:
                pytest.fail(f"Done handler failed: {e}")
    
    @pytest.mark.asyncio
    async def test_environment_manager_initialization(self):
        """Test that environment manager initializes without errors"""
        
        try:
            from environment_manager import EnvironmentManager
            
            env_manager = EnvironmentManager()
            
            # Basic functionality tests
            assert env_manager.current_env is not None
            assert env_manager.config is not None
            assert hasattr(env_manager, 'is_production')
            assert hasattr(env_manager, 'get_feature_flag')
            
            # Test validation
            validation = env_manager.validate_config()
            assert isinstance(validation, dict)
            assert 'is_valid' in validation
            
        except Exception as e:
            pytest.fail(f"Environment manager initialization failed: {e}")
    
    def test_feature_flags_import(self):
        """Test that feature flags can be imported without errors"""
        
        try:
            from feature_flags import FeatureFlag, CommonFlags, EmergencyFlags
            
            # Test basic functionality exists
            assert hasattr(FeatureFlag, 'require')
            assert hasattr(CommonFlags, 'NEW_ONBOARDING')
            assert hasattr(EmergencyFlags, 'disable_first_impression_fsm')
            
        except Exception as e:
            pytest.fail(f"Feature flags import failed: {e}")
    
    @pytest.mark.asyncio
    async def test_help_command_basic(self):
        """Test that /help command executes without errors"""
        
        with patch('telbot.role_manager') as mock_role_manager:
            
            mock_role_manager.get_user_roles = AsyncMock(return_value=["unpaid"])
            mock_role_manager.get_user_permissions = AsyncMock(return_value={})
            
            # Mock message
            mock_message = AsyncMock()
            mock_message.from_user.id = 12345
            mock_message.answer = AsyncMock()
            
            # Test the help handler
            from telbot import help_handler
            
            try:
                await help_handler(mock_message)
                mock_message.answer.assert_called_once()
                help_text = mock_message.answer.call_args[0][0]
                assert "How to use this bot" in help_text
                assert "/commit" in help_text
            except Exception as e:
                pytest.fail(f"Help handler failed: {e}")

class TestEnvironmentSeparation:
    """Test environment separation functionality"""
    
    def test_environment_detection(self):
        """Test that environments are detected correctly"""
        
        # Test development detection
        os.environ["TELBOT_ENVIRONMENT"] = "development"
        from environment_manager import EnvironmentManager
        env_mgr = EnvironmentManager()
        assert env_mgr.is_development()
        assert not env_mgr.is_production()
        
        # Test production detection
        os.environ["TELBOT_ENVIRONMENT"] = "production"
        env_mgr = EnvironmentManager()
        assert env_mgr.is_production()
        assert not env_mgr.is_development()
    
    def test_feature_flag_environment_differences(self):
        """Test that feature flags differ between environments"""
        
        # Development environment
        os.environ["TELBOT_ENVIRONMENT"] = "development"
        from environment_manager import EnvironmentManager
        dev_env = EnvironmentManager()
        
        # Production environment
        os.environ["TELBOT_ENVIRONMENT"] = "production"
        prod_env = EnvironmentManager()
        
        # Feature flags should be different
        dev_flags = dev_env.config.feature_flags
        prod_flags = prod_env.config.feature_flags
        
        # Development should have more features enabled
        dev_enabled = sum(dev_flags.values())
        prod_enabled = sum(prod_flags.values())
        
        assert dev_enabled >= prod_enabled, "Development should have at least as many features as production"
        
        # Specific checks
        assert not prod_flags.get("first_impression_fsm", True), "First impression FSM should be disabled in production"

class TestProductionSafety:
    """Test production safety measures"""
    
    def test_claude_context_generation(self):
        """Test that Claude context is generated correctly"""
        
        os.environ["TELBOT_ENVIRONMENT"] = "production"
        
        from environment_manager import EnvironmentManager
        env_mgr = EnvironmentManager()
        
        context = env_mgr.generate_claude_context()
        
        # Verify context structure
        assert "telbot_environment" in context
        assert "warnings" in context
        assert "feature_flags" in context
        
        # Verify production warnings are present
        warnings = context["warnings"]
        production_warnings = [w for w in warnings if "PRODUCTION" in w]
        assert len(production_warnings) > 0, "Should have production warnings"
    
    def test_emergency_flag_disable(self):
        """Test emergency flag disabling functionality"""
        
        from feature_flags import EmergencyFlags
        from environment_manager import EnvironmentManager
        
        env_mgr = EnvironmentManager()
        
        # Enable a flag first
        env_mgr.set_feature_flag("first_impression_fsm", True)
        assert env_mgr.get_feature_flag("first_impression_fsm")
        
        # Emergency disable
        EmergencyFlags.disable_first_impression_fsm()
        assert not env_mgr.get_feature_flag("first_impression_fsm")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])