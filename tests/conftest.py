"""Pytest configuration and fixtures."""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-key"
os.environ["TELEGRAM_BOT_TOKEN"] = "test-token"

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = MagicMock()
    mock.table.return_value.select.return_value.execute.return_value.data = []
    mock.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
    mock.table.return_value.update.return_value.execute.return_value.data = [{"id": "test-id"}]
    mock.table.return_value.delete.return_value.execute.return_value.data = [{"id": "test-id"}]
    return mock

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot."""
    mock = AsyncMock()
    mock.send_message.return_value = MagicMock(message_id=12345)
    mock.edit_message_text.return_value = MagicMock(message_id=12345)
    mock.delete_message.return_value = True
    return mock

@pytest.fixture
def sample_telegram_update():
    """Sample Telegram update object."""
    return {
        "update_id": 123456789,
        "message": {
            "message_id": 100,
            "from": {
                "id": 16861999,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
                "language_code": "en"
            },
            "chat": {
                "id": 16861999,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1609459200,
            "text": "/start"
        }
    }

@pytest.fixture
def sample_task():
    """Sample task object."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "created_by": "11111111-1111-1111-1111-111111111111",
        "assigned_to": "22222222-2222-2222-2222-222222222222",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def mock_render_api():
    """Mock Render API responses."""
    mock = MagicMock()
    mock.get.return_value.json.return_value = {
        "id": "srv-test",
        "status": "live",
        "health": "healthy"
    }
    mock.post.return_value.json.return_value = {
        "id": "dep-test",
        "status": "live"
    }
    return mock