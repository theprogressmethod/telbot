#!/usr/bin/env python3
"""
Unit tests for bot functionality in telbot.py
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from aiogram.types import Message, User, Chat, CallbackQuery

from telbot import (
    Config, SmartAnalysis, DatabaseManager, CommitmentTracker,
    start_handler, commit_handler, done_handler, list_handler,
    help_handler, feedback_handler, complete_commitment_callback,
    save_smart_callback, save_original_callback
)


@pytest.mark.unit
@pytest.mark.bot
class TestConfig:
    """Test the Config class"""
    
    def test_config_initialization_with_all_vars(self, monkeypatch):
        """Test config loads with all environment variables"""
        monkeypatch.setenv("BOT_TOKEN", "test_bot_token")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test_key")
        
        config = Config()
        assert config.bot_token == "test_bot_token"
        assert config.supabase_url == "https://test.supabase.co"
        assert config.supabase_key == "test_key"
        assert config.openai_api_key == "sk-test_key"
    
    def test_config_missing_required_vars(self, monkeypatch):
        """Test config fails with missing environment variables"""
        monkeypatch.delenv("BOT_TOKEN", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        
        with pytest.raises(ValueError, match="Missing required environment variables"):
            Config()
    
    def test_config_development_environment(self, monkeypatch):
        """Test config uses development database in dev environment"""
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        monkeypatch.setenv("SUPABASE_URL", "https://prod.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "prod_key")
        monkeypatch.setenv("DEV_SUPABASE_URL", "https://dev.supabase.co")
        monkeypatch.setenv("DEV_SUPABASE_KEY", "dev_key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        config = Config()
        assert config.supabase_url == "https://dev.supabase.co"
        assert config.supabase_key == "dev_key"


@pytest.mark.unit
@pytest.mark.bot
class TestSmartAnalysis:
    """Test the SmartAnalysis class"""
    
    def test_smart_analysis_initialization(self, mock_config):
        """Test SmartAnalysis initializes with config"""
        analyzer = SmartAnalysis(mock_config)
        assert analyzer.config == mock_config
    
    @pytest.mark.asyncio
    async def test_analyze_commitment_success(self, mock_config):
        """Test successful commitment analysis"""
        analyzer = SmartAnalysis(mock_config)
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "score": 8,
            "analysis": {
                "specific": 8,
                "measurable": 7,
                "achievable": 9,
                "relevant": 8,
                "timeBound": 6
            },
            "smartVersion": "Read 30 pages of a business book by 6 PM today",
            "feedback": "Added specific page count and deadline"
        })
        
        with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response):
            result = await analyzer.analyze_commitment("read a book")
            
            assert result["score"] == 8
            assert result["analysis"]["specific"] == 8
            assert "Read 30 pages" in result["smartVersion"]
            assert "Added specific" in result["feedback"]
    
    @pytest.mark.asyncio
    async def test_analyze_commitment_fallback(self, mock_config):
        """Test fallback analysis when OpenAI fails"""
        mock_config.openai_api_key = ""  # Simulate missing API key
        analyzer = SmartAnalysis(mock_config)
        
        result = await analyzer.analyze_commitment("exercise today")
        
        assert result["score"] <= 8
        assert "by the end of this week" in result["smartVersion"]
        assert "AI analysis unavailable" in result["feedback"]
    
    @pytest.mark.asyncio 
    async def test_analyze_commitment_json_parsing_error(self, mock_config):
        """Test handling of malformed JSON response"""
        analyzer = SmartAnalysis(mock_config)
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response):
            result = await analyzer.analyze_commitment("test commitment")
            
            # Should fall back to heuristic analysis
            assert "score" in result
            assert "smartVersion" in result


@pytest.mark.unit
@pytest.mark.bot
class TestDatabaseManager:
    """Test the DatabaseManager class"""
    
    @pytest.mark.asyncio
    async def test_test_database_success(self, mock_supabase):
        """Test successful database connection test"""
        with patch('telbot.supabase', mock_supabase):
            result = await DatabaseManager.test_database()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_database_failure(self):
        """Test database connection failure"""
        with patch('telbot.supabase', None):
            result = await DatabaseManager.test_database()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_save_commitment_success(self, mock_supabase):
        """Test successful commitment saving"""
        # Mock user lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "user-uuid-123"}
        ]
        
        with patch('telbot.supabase', mock_supabase):
            result = await DatabaseManager.save_commitment(
                telegram_user_id=123456789,
                commitment="Test commitment",
                original_commitment="Original test",
                smart_score=8
            )
            
            assert result is True
            # Verify insert was called
            mock_supabase.table.return_value.insert.assert_called()
    
    @pytest.mark.asyncio
    async def test_save_commitment_user_not_found(self, mock_supabase):
        """Test commitment saving when user not found"""
        # Mock empty user lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        with patch('telbot.supabase', mock_supabase):
            result = await DatabaseManager.save_commitment(
                telegram_user_id=999999999,
                commitment="Test commitment", 
                original_commitment="Original test",
                smart_score=5
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_active_commitments(self, mock_supabase, sample_commitments):
        """Test getting active commitments"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = sample_commitments
        
        with patch('telbot.supabase', mock_supabase):
            result = await DatabaseManager.get_active_commitments(123456789)
            
            assert len(result) == 2
            assert result[0]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_complete_commitment(self, mock_supabase):
        """Test completing a commitment"""
        with patch('telbot.supabase', mock_supabase):
            result = await DatabaseManager.complete_commitment("commitment-id-123")
            
            assert result is True
            # Verify update was called with correct status
            mock_supabase.table.return_value.update.assert_called_once()
            update_call = mock_supabase.table.return_value.update.call_args[0][0]
            assert update_call["status"] == "completed"


@pytest.mark.unit
@pytest.mark.bot
class TestCommitmentTracker:
    """Test the CommitmentTracker class"""
    
    def test_commitment_tracker_initialization(self, mock_supabase, mock_bot):
        """Test CommitmentTracker initializes correctly"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        assert tracker.supabase == mock_supabase
        assert tracker.bot == mock_bot
    
    @pytest.mark.asyncio
    async def test_get_commitment_progress(self, mock_supabase, mock_bot):
        """Test getting commitment progress statistics"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Mock database responses for different queries
        mock_responses = {
            "total": Mock(count=10),
            "completed": Mock(count=7), 
            "active": Mock(count=3)
        }
        
        def mock_select_chain(*args, **kwargs):
            chain = Mock()
            chain.eq.return_value.execute.return_value = mock_responses["total"]
            chain.eq.return_value.eq.return_value.execute.return_value = mock_responses["completed"]
            return chain
        
        mock_supabase.table.return_value.select.side_effect = [
            mock_select_chain(),  # total
            mock_select_chain(),  # completed
            mock_select_chain()   # active
        ]
        
        with patch.object(tracker, 'calculate_commitment_streak', return_value=3):
            result = await tracker.get_commitment_progress(123456789)
            
            assert result["total_commitments"] == 10
            assert result["completed_commitments"] == 7
            assert result["completion_rate"] == 70.0
            assert result["current_streak"] == 3
    
    def test_get_progress_level(self, mock_supabase, mock_bot):
        """Test progress level calculation"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        assert tracker._get_progress_level(95, 20) == "🔥 Consistency Master"
        assert tracker._get_progress_level(80, 15) == "💪 Strong Performer"
        assert tracker._get_progress_level(60, 10) == "📈 Building Momentum"
        assert tracker._get_progress_level(30, 8) == "🎯 Finding Rhythm"
        assert tracker._get_progress_level(90, 3) == "🌱 Getting Started"


@pytest.mark.unit
@pytest.mark.bot
class TestBotHandlers:
    """Test bot command handlers"""
    
    @pytest.mark.asyncio
    async def test_start_handler_new_user(self, mock_message, mock_user):
        """Test /start handler for new user"""
        mock_message.from_user = mock_user
        
        with patch('telbot.role_manager') as mock_role_manager, \
             patch('telbot.DatabaseManager.test_database', return_value=True), \
             patch('telbot.onboarding_system') as mock_onboarding:
            
            mock_role_manager.ensure_user_exists = AsyncMock()
            mock_role_manager.is_first_time_user = AsyncMock(return_value=True)
            mock_role_manager.get_user_roles = AsyncMock(return_value=["user"])
            mock_onboarding.handle_first_time_user = AsyncMock(return_value="Welcome new user!")
            
            await start_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Welcome new user!" in call_args
    
    @pytest.mark.asyncio
    async def test_start_handler_returning_user(self, mock_message, mock_user):
        """Test /start handler for returning user"""
        mock_message.from_user = mock_user
        
        with patch('telbot.role_manager') as mock_role_manager, \
             patch('telbot.DatabaseManager.test_database', return_value=True):
            
            mock_role_manager.ensure_user_exists = AsyncMock()
            mock_role_manager.is_first_time_user = AsyncMock(return_value=False)
            mock_role_manager.get_user_roles = AsyncMock(return_value=["paid", "pod_member"])
            
            await start_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Welcome back" in call_args
            assert "Pod Member" in call_args
    
    @pytest.mark.asyncio
    async def test_commit_handler_no_commitment_text(self, mock_message):
        """Test /commit handler with no commitment text"""
        mock_message.text = "/commit"
        
        await commit_handler(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Please provide a commitment" in call_args
    
    @pytest.mark.asyncio
    async def test_commit_handler_success(self, mock_message):
        """Test successful commitment handling"""
        mock_message.text = "/commit read for 30 minutes"
        mock_message.from_user.id = 123456789
        mock_message.chat.id = 123456789
        
        with patch('telbot.DatabaseManager.test_database', return_value=True), \
             patch('telbot.create_loading_experience') as mock_loading, \
             patch('telbot.smart_analyzer') as mock_analyzer, \
             patch('telbot.DatabaseManager.save_commitment', return_value=True), \
             patch('telbot._trigger_commitment_sequences') as mock_trigger:
            
            mock_loading_msg = Mock()
            mock_loading.return_value = mock_loading_msg
            
            mock_analyzer.analyze_commitment = AsyncMock(return_value={
                "score": 9,
                "smartVersion": "Read for 30 minutes today",
                "feedback": "Great commitment!"
            })
            
            await commit_handler(mock_message)
            
            # Verify loading experience was created
            mock_loading.assert_called_once()
            
            # Verify commitment was saved
            mock_trigger.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_handler_no_commitments(self, mock_message):
        """Test /list handler with no active commitments"""
        mock_message.from_user.id = 123456789
        
        with patch('telbot.DatabaseManager.get_active_commitments', return_value=[]):
            await list_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "No active commitments" in call_args
    
    @pytest.mark.asyncio
    async def test_list_handler_with_commitments(self, mock_message, sample_commitments):
        """Test /list handler with active commitments"""
        mock_message.from_user.id = 123456789
        
        with patch('telbot.DatabaseManager.get_active_commitments', return_value=sample_commitments):
            await list_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Your Active Commitments" in call_args
            assert sample_commitments[0]["text"] in call_args
    
    @pytest.mark.asyncio
    async def test_done_handler_no_commitments(self, mock_message):
        """Test /done handler with no active commitments"""
        mock_message.from_user.id = 123456789
        
        with patch('telbot.DatabaseManager.get_active_commitments', return_value=[]):
            await done_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "No active commitments" in call_args
    
    @pytest.mark.asyncio
    async def test_done_handler_with_commitments(self, mock_message, sample_commitments):
        """Test /done handler with active commitments"""
        mock_message.from_user.id = 123456789
        
        with patch('telbot.DatabaseManager.get_active_commitments', return_value=sample_commitments):
            await done_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            # Should include inline keyboard with commitment options
            call_kwargs = mock_message.answer.call_args[1]
            assert 'reply_markup' in call_kwargs
    
    @pytest.mark.asyncio
    async def test_feedback_handler_no_text(self, mock_message):
        """Test /feedback handler with no feedback text"""
        mock_message.text = "/feedback"
        
        await feedback_handler(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Send us your feedback" in call_args
    
    @pytest.mark.asyncio
    async def test_feedback_handler_success(self, mock_message, mock_user):
        """Test successful feedback submission"""
        mock_message.text = "/feedback Great bot, love it!"
        mock_message.from_user = mock_user
        
        with patch('telbot.DatabaseManager.save_feedback', return_value=True):
            await feedback_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Thank you for your feedback" in call_args
    
    @pytest.mark.asyncio
    async def test_help_handler(self, mock_message):
        """Test /help handler"""
        mock_message.from_user.id = 123456789
        
        with patch('telbot.role_manager') as mock_role_manager:
            mock_role_manager.get_user_roles = AsyncMock(return_value=["user"])
            mock_role_manager.get_user_permissions = AsyncMock(return_value={
                "can_join_pods": False,
                "can_access_long_term_goals": False,
                "can_view_analytics": False
            })
            
            await help_handler(mock_message)
            
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "How to use this bot" in call_args
            assert "/commit" in call_args


@pytest.mark.unit
@pytest.mark.bot
class TestCallbackHandlers:
    """Test callback query handlers"""
    
    @pytest.mark.asyncio
    async def test_complete_commitment_callback_success(self):
        """Test successful commitment completion callback"""
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "complete_commitment-id-123"
        mock_callback.from_user.id = 123456789
        mock_callback.answer = AsyncMock()
        mock_callback.message.edit_text = AsyncMock()
        
        with patch('telbot.DatabaseManager.complete_commitment', return_value=True), \
             patch('telbot.DatabaseManager.get_active_commitments', return_value=[]):
            
            await complete_commitment_callback(mock_callback)
            
            mock_callback.answer.assert_called_once_with("✅ Marked as complete! Great job! 🎉")
            mock_callback.message.edit_text.assert_called_once()
            edit_text_args = mock_callback.message.edit_text.call_args[0][0]
            assert "ALL DONE" in edit_text_args
    
    @pytest.mark.asyncio
    async def test_complete_commitment_callback_failure(self):
        """Test commitment completion callback with database error"""
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "complete_commitment-id-123"
        mock_callback.from_user.id = 123456789
        mock_callback.answer = AsyncMock()
        
        with patch('telbot.DatabaseManager.complete_commitment', return_value=False):
            await complete_commitment_callback(mock_callback)
            
            mock_callback.answer.assert_called_once()
            call_args = mock_callback.answer.call_args[0][0]
            assert "Error marking commitment complete" in call_args
    
    @pytest.mark.asyncio
    async def test_save_smart_callback_success(self):
        """Test saving SMART version callback"""
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "save_smart_123456789_8"
        mock_callback.from_user.id = 123456789
        mock_callback.answer = AsyncMock()
        mock_callback.message.edit_text = AsyncMock()
        
        # Mock temporary storage
        with patch('telbot.temp_storage', {"commit_123456789": {
            "original": "read book",
            "smart": "read 30 pages by 6pm",
            "score": 8
        }}), \
        patch('telbot.DatabaseManager.save_commitment', return_value=True), \
        patch('telbot._trigger_commitment_sequences'):
            
            await save_smart_callback(mock_callback)
            
            mock_callback.message.edit_text.assert_called_once()
            edit_text_args = mock_callback.message.edit_text.call_args[0][0]
            assert "SMART commitment saved" in edit_text_args
    
    @pytest.mark.asyncio
    async def test_save_original_callback_success(self):
        """Test saving original version callback"""
        mock_callback = Mock(spec=CallbackQuery)
        mock_callback.data = "save_original_123456789_6"
        mock_callback.from_user.id = 123456789
        mock_callback.answer = AsyncMock()
        mock_callback.message.edit_text = AsyncMock()
        
        # Mock temporary storage
        with patch('telbot.temp_storage', {"commit_123456789": {
            "original": "read book",
            "smart": "read 30 pages by 6pm",
            "score": 6
        }}), \
        patch('telbot.DatabaseManager.save_commitment', return_value=True), \
        patch('telbot._trigger_commitment_sequences'):
            
            await save_original_callback(mock_callback)
            
            mock_callback.message.edit_text.assert_called_once()
            edit_text_args = mock_callback.message.edit_text.call_args[0][0]
            assert "Commitment saved" in edit_text_args


@pytest.mark.unit
@pytest.mark.bot
class TestLoadingExperience:
    """Test loading experience functions"""
    
    @pytest.mark.asyncio
    async def test_create_loading_experience(self, mock_message):
        """Test loading experience creation"""
        from telbot import create_loading_experience
        
        with patch('telbot.bot') as mock_bot:
            mock_bot.send_chat_action = AsyncMock()
            
            result = await create_loading_experience(mock_message, "test commitment")
            
            # Should return the loading message
            assert result == mock_message.answer.return_value
            # Should have sent typing action
            mock_bot.send_chat_action.assert_called()
    
    @pytest.mark.asyncio
    async def test_finalize_loading_experience(self):
        """Test loading experience finalization"""
        from telbot import finalize_loading_experience
        
        mock_loading_msg = Mock()
        mock_loading_msg.edit_text = AsyncMock()
        
        analysis = {"score": 8}
        
        await finalize_loading_experience(mock_loading_msg, analysis)
        
        # Should edit the loading message with results
        mock_loading_msg.edit_text.assert_called()
        edit_calls = [call[0][0] for call in mock_loading_msg.edit_text.call_args_list]
        assert any("Analysis complete" in call for call in edit_calls)


@pytest.mark.unit
@pytest.mark.bot 
class TestUtilityFunctions:
    """Test utility and helper functions"""
    
    @pytest.mark.asyncio
    async def test_show_commitment_tips(self):
        """Test commitment tips function"""
        from telbot import show_commitment_tips
        
        with patch('telbot.bot') as mock_bot:
            mock_bot.send_message = AsyncMock()
            
            await show_commitment_tips(123456789)
            
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == 123456789
            assert "Tip:" in call_args[1]["text"]
    
    @pytest.mark.asyncio
    async def test_trigger_commitment_sequences(self, mock_supabase):
        """Test nurture sequence triggering"""
        from telbot import _trigger_commitment_sequences
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "user-uuid", "total_commitments": 5}
        ]
        
        with patch('telbot.supabase', mock_supabase), \
             patch('telbot.nurture_system') as mock_nurture:
            
            mock_nurture.check_triggers = AsyncMock()
            
            await _trigger_commitment_sequences(123456789)
            
            # Should trigger commitment_created and milestone sequences
            assert mock_nurture.check_triggers.call_count >= 1