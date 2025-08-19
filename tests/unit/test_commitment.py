#!/usr/bin/env python3
"""
Unit tests for commitment tracking functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from telbot import (
    CommitmentTracker, process_pending_reminders, 
    send_daily_accountability_checks, _trigger_commitment_sequences
)


@pytest.mark.unit
@pytest.mark.commitment
class TestCommitmentTracker:
    """Test the CommitmentTracker class"""
    
    def test_commitment_tracker_init(self, mock_supabase, mock_bot):
        """Test CommitmentTracker initialization"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        assert tracker.supabase == mock_supabase
        assert tracker.bot == mock_bot
    
    @pytest.mark.asyncio
    async def test_schedule_reminder_success(self, mock_supabase, mock_bot):
        """Test successful reminder scheduling"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        reminder_time = datetime.now() + timedelta(hours=2)
        
        result = await tracker.schedule_reminder(
            telegram_user_id=123456789,
            commitment_id="commit-123",
            reminder_time=reminder_time
        )
        
        assert result is True
        mock_supabase.table.return_value.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_schedule_reminder_failure(self, mock_supabase, mock_bot):
        """Test reminder scheduling failure"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        mock_supabase.table.return_value.insert.side_effect = Exception("DB Error")
        
        reminder_time = datetime.now() + timedelta(hours=2)
        
        result = await tracker.schedule_reminder(
            telegram_user_id=123456789,
            commitment_id="commit-123", 
            reminder_time=reminder_time
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_pending_reminders_success(self, mock_supabase, mock_bot):
        """Test getting pending reminders"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        mock_reminders = [
            {
                "id": "reminder-1",
                "telegram_user_id": 123456789,
                "commitment_id": "commit-123",
                "reminder_time": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "commitments": {
                    "id": "commit-123",
                    "commitment": "Test commitment",
                    "telegram_user_id": 123456789
                }
            }
        ]
        
        # Mock database chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.lte.return_value.execute.return_value.data = mock_reminders
        
        result = await tracker.get_pending_reminders()
        
        assert len(result) == 1
        assert result[0]["id"] == "reminder-1"
    
    @pytest.mark.asyncio
    async def test_get_pending_reminders_empty(self, mock_supabase, mock_bot):
        """Test getting pending reminders when none exist"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.lte.return_value.execute.return_value.data = []
        
        result = await tracker.get_pending_reminders()
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_send_reminder_success(self, mock_supabase, mock_bot):
        """Test successful reminder sending"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        reminder = {
            "id": "reminder-1",
            "telegram_user_id": 123456789,
            "commitments": {
                "commitment": "Test commitment"
            }
        }
        
        mock_bot.send_message = AsyncMock()
        
        with patch.object(tracker, 'mark_reminder_sent', new_callable=AsyncMock) as mock_mark_sent:
            result = await tracker.send_reminder(reminder)
            
            assert result is True
            mock_bot.send_message.assert_called_once()
            mock_mark_sent.assert_called_once_with("reminder-1")
    
    @pytest.mark.asyncio
    async def test_send_reminder_no_commitment(self, mock_supabase, mock_bot):
        """Test sending reminder with no commitment data"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        reminder = {
            "id": "reminder-1",
            "telegram_user_id": 123456789,
            "commitments": None
        }
        
        result = await tracker.send_reminder(reminder)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_commitment_progress_success(self, mock_supabase, mock_bot):
        """Test successful commitment progress calculation"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Mock database responses
        def mock_query_response(query_type):
            if "total" in str(query_type):
                return Mock(count=10)
            elif "completed" in str(query_type):
                return Mock(count=7)
            elif "active" in str(query_type):
                return Mock(count=3)
            return Mock(count=0)
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            mock_query_response("total"),
            mock_query_response("completed"),
            mock_query_response("active")
        ]
        
        with patch.object(tracker, 'calculate_commitment_streak', return_value=5):
            result = await tracker.get_commitment_progress(123456789)
            
            assert result["total_commitments"] == 10
            assert result["completed_commitments"] == 7
            assert result["active_commitments"] == 3
            assert result["completion_rate"] == 70.0
            assert result["current_streak"] == 5
            assert "progress_level" in result
    
    @pytest.mark.asyncio
    async def test_get_commitment_progress_no_commitments(self, mock_supabase, mock_bot):
        """Test commitment progress with no commitments"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Mock empty responses
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 0
        
        with patch.object(tracker, 'calculate_commitment_streak', return_value=0):
            result = await tracker.get_commitment_progress(123456789)
            
            assert result["total_commitments"] == 0
            assert result["completion_rate"] == 0
            assert result["current_streak"] == 0
    
    @pytest.mark.asyncio
    async def test_calculate_commitment_streak_success(self, mock_supabase, mock_bot):
        """Test commitment streak calculation"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Mock completed commitments data (last 3 days)
        today = datetime.now().date()
        mock_commitments = [
            {"completed_at": today.isoformat()},
            {"completed_at": (today - timedelta(days=1)).isoformat()},
            {"completed_at": (today - timedelta(days=2)).isoformat()},
            {"completed_at": (today - timedelta(days=5)).isoformat()}  # Gap - should break streak
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_commitments
        
        result = await tracker.calculate_commitment_streak(123456789)
        
        # Should count 3 consecutive days
        assert result == 3
    
    @pytest.mark.asyncio
    async def test_calculate_commitment_streak_no_completions(self, mock_supabase, mock_bot):
        """Test streak calculation with no completed commitments"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        
        result = await tracker.calculate_commitment_streak(123456789)
        
        assert result == 0
    
    def test_get_progress_level_getting_started(self, mock_supabase, mock_bot):
        """Test progress level for new users"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        level = tracker._get_progress_level(80.0, 3)  # High rate but few commitments
        assert level == "🌱 Getting Started"
    
    def test_get_progress_level_consistency_master(self, mock_supabase, mock_bot):
        """Test progress level for consistency masters"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        level = tracker._get_progress_level(95.0, 20)
        assert level == "🔥 Consistency Master"
    
    def test_get_progress_level_strong_performer(self, mock_supabase, mock_bot):
        """Test progress level for strong performers"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        level = tracker._get_progress_level(80.0, 15)
        assert level == "💪 Strong Performer"
    
    def test_get_progress_level_building_momentum(self, mock_supabase, mock_bot):
        """Test progress level for building momentum"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        level = tracker._get_progress_level(60.0, 10)
        assert level == "📈 Building Momentum"
    
    def test_get_progress_level_finding_rhythm(self, mock_supabase, mock_bot):
        """Test progress level for finding rhythm"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        level = tracker._get_progress_level(30.0, 10)
        assert level == "🎯 Finding Rhythm"
    
    @pytest.mark.asyncio
    async def test_send_accountability_check_success(self, mock_supabase, mock_bot):
        """Test successful accountability check sending"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Mock overdue commitments
        mock_overdue = [
            {"commitment": "Read book", "created_at": (datetime.now() - timedelta(days=2)).isoformat()},
            {"commitment": "Exercise", "created_at": (datetime.now() - timedelta(days=1)).isoformat()}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.lt.return_value.execute.return_value.data = mock_overdue
        mock_bot.send_message = AsyncMock()
        
        result = await tracker.send_accountability_check(123456789)
        
        assert result is True
        mock_bot.send_message.assert_called_once()
        
        # Check message content
        call_args = mock_bot.send_message.call_args
        message_text = call_args[1]["text"]
        assert "Accountability Check-In" in message_text
        assert "2 commitment" in message_text
    
    @pytest.mark.asyncio
    async def test_send_accountability_check_no_overdue(self, mock_supabase, mock_bot):
        """Test accountability check with no overdue commitments"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.lt.return_value.execute.return_value.data = []
        
        result = await tracker.send_accountability_check(123456789)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_mark_reminder_sent_success(self, mock_supabase, mock_bot):
        """Test marking reminder as sent"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        await tracker.mark_reminder_sent("reminder-123")
        
        mock_supabase.table.return_value.update.assert_called_once()
        update_data = mock_supabase.table.return_value.update.call_args[0][0]
        assert update_data["status"] == "sent"
        assert "sent_at" in update_data


@pytest.mark.unit
@pytest.mark.commitment
class TestCommitmentUtilityFunctions:
    """Test commitment-related utility functions"""
    
    @pytest.mark.asyncio
    async def test_process_pending_reminders_success(self, mock_supabase):
        """Test processing pending reminders"""
        with patch('telbot.commitment_tracker') as mock_tracker:
            mock_tracker.get_pending_reminders = AsyncMock(return_value=[
                {"id": "reminder-1"}, 
                {"id": "reminder-2"}
            ])
            mock_tracker.send_reminder = AsyncMock(return_value=True)
            
            result = await process_pending_reminders()
            
            assert result == 2
            assert mock_tracker.send_reminder.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_pending_reminders_no_reminders(self):
        """Test processing when no reminders are pending"""
        with patch('telbot.commitment_tracker') as mock_tracker:
            mock_tracker.get_pending_reminders = AsyncMock(return_value=[])
            
            result = await process_pending_reminders()
            
            assert result == 0
    
    @pytest.mark.asyncio
    async def test_process_pending_reminders_error(self):
        """Test processing pending reminders with error"""
        with patch('telbot.commitment_tracker') as mock_tracker:
            mock_tracker.get_pending_reminders = AsyncMock(side_effect=Exception("DB Error"))
            
            result = await process_pending_reminders()
            
            assert result == 0
    
    @pytest.mark.asyncio
    async def test_send_daily_accountability_checks_success(self, mock_supabase):
        """Test sending daily accountability checks"""
        mock_overdue_users = [
            {"telegram_user_id": 123456789},
            {"telegram_user_id": 987654321},
            {"telegram_user_id": 123456789}  # Duplicate should be deduplicated
        ]
        
        with patch('telbot.supabase', mock_supabase), \
             patch('telbot.commitment_tracker') as mock_tracker:
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.data = mock_overdue_users
            mock_tracker.send_accountability_check = AsyncMock(return_value=True)
            
            result = await send_daily_accountability_checks()
            
            # Should send to 2 unique users
            assert result == 2
            assert mock_tracker.send_accountability_check.call_count == 2
    
    @pytest.mark.asyncio
    async def test_send_daily_accountability_checks_no_users(self, mock_supabase):
        """Test accountability checks when no users have overdue commitments"""
        with patch('telbot.supabase', mock_supabase):
            mock_supabase.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.data = []
            
            result = await send_daily_accountability_checks()
            
            assert result == 0
    
    @pytest.mark.asyncio
    async def test_trigger_commitment_sequences_success(self, mock_supabase):
        """Test triggering commitment sequences"""
        mock_user_data = [
            {"id": "user-uuid-123", "total_commitments": 5}
        ]
        
        with patch('telbot.supabase', mock_supabase), \
             patch('telbot.nurture_system') as mock_nurture:
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_user_data
            mock_nurture.check_triggers = AsyncMock()
            
            await _trigger_commitment_sequences(123456789)
            
            # Should trigger both commitment_created and milestone sequences
            expected_calls = [
                (("user-uuid-123", "commitment_created"),),
                (("user-uuid-123", "5_commitments_completed"),)
            ]
            
            actual_calls = mock_nurture.check_triggers.call_args_list
            assert len(actual_calls) == 2
    
    @pytest.mark.asyncio
    async def test_trigger_commitment_sequences_user_not_found(self, mock_supabase):
        """Test triggering sequences when user not found"""
        with patch('telbot.supabase', mock_supabase), \
             patch('telbot.nurture_system') as mock_nurture:
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            mock_nurture.check_triggers = AsyncMock()
            
            # Should not raise error
            await _trigger_commitment_sequences(999999999)
            
            # Should not trigger any sequences
            mock_nurture.check_triggers.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_trigger_commitment_sequences_error(self, mock_supabase):
        """Test triggering sequences with database error"""
        with patch('telbot.supabase', mock_supabase), \
             patch('telbot.nurture_system') as mock_nurture:
            
            mock_supabase.table.side_effect = Exception("DB Error")
            mock_nurture.check_triggers = AsyncMock()
            
            # Should handle error gracefully
            await _trigger_commitment_sequences(123456789)
            
            # Should not trigger any sequences due to error
            mock_nurture.check_triggers.assert_not_called()


@pytest.mark.unit
@pytest.mark.commitment
class TestCommitmentStreakLogic:
    """Test commitment streak calculation logic"""
    
    @pytest.mark.asyncio
    async def test_streak_calculation_perfect_sequence(self, mock_supabase, mock_bot):
        """Test streak calculation with perfect daily sequence"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        today = datetime.now().date()
        mock_commitments = [
            {"completed_at": today.isoformat()},
            {"completed_at": (today - timedelta(days=1)).isoformat()},
            {"completed_at": (today - timedelta(days=2)).isoformat()},
            {"completed_at": (today - timedelta(days=3)).isoformat()},
            {"completed_at": (today - timedelta(days=4)).isoformat()}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_commitments
        
        result = await tracker.calculate_commitment_streak(123456789)
        
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_streak_calculation_with_gap(self, mock_supabase, mock_bot):
        """Test streak calculation with gap in completions"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        today = datetime.now().date()
        mock_commitments = [
            {"completed_at": today.isoformat()},
            {"completed_at": (today - timedelta(days=1)).isoformat()},
            # Gap on day 2
            {"completed_at": (today - timedelta(days=3)).isoformat()},
            {"completed_at": (today - timedelta(days=4)).isoformat()}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_commitments
        
        result = await tracker.calculate_commitment_streak(123456789)
        
        # Should only count 2 days (today and yesterday)
        assert result == 2
    
    @pytest.mark.asyncio
    async def test_streak_calculation_malformed_dates(self, mock_supabase, mock_bot):
        """Test streak calculation with malformed date data"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        today = datetime.now().date()
        mock_commitments = [
            {"completed_at": today.isoformat()},
            {"completed_at": "invalid-date"},  # Should be skipped
            {"completed_at": (today - timedelta(days=1)).isoformat()},
            {"completed_at": None}  # Should be skipped
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_commitments
        
        result = await tracker.calculate_commitment_streak(123456789)
        
        # Should handle malformed dates gracefully and count valid ones
        assert result == 2


@pytest.mark.unit
@pytest.mark.commitment
class TestCommitmentProgressLevels:
    """Test commitment progress level determination"""
    
    def test_all_progress_levels(self, mock_supabase, mock_bot):
        """Test all possible progress level classifications"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Test all level conditions
        test_cases = [
            # (completion_rate, total_commitments, expected_level)
            (95.0, 20, "🔥 Consistency Master"),
            (80.0, 15, "💪 Strong Performer"), 
            (60.0, 10, "📈 Building Momentum"),
            (30.0, 8, "🎯 Finding Rhythm"),
            (90.0, 3, "🌱 Getting Started"),  # High rate but few commitments
            (50.0, 2, "🌱 Getting Started")   # Few commitments overrides rate
        ]
        
        for rate, total, expected in test_cases:
            level = tracker._get_progress_level(rate, total)
            assert level == expected, f"Failed for rate={rate}, total={total}"
    
    def test_edge_case_progress_levels(self, mock_supabase, mock_bot):
        """Test edge cases for progress level determination"""
        tracker = CommitmentTracker(mock_supabase, mock_bot)
        
        # Test boundary conditions
        assert tracker._get_progress_level(75.0, 10) == "💪 Strong Performer"  # Exactly 75%
        assert tracker._get_progress_level(74.9, 10) == "📈 Building Momentum"  # Just under 75%
        assert tracker._get_progress_level(50.0, 10) == "📈 Building Momentum"  # Exactly 50%
        assert tracker._get_progress_level(49.9, 10) == "🎯 Finding Rhythm"  # Just under 50%
        assert tracker._get_progress_level(0.0, 5) == "🎯 Finding Rhythm"  # 0% completion