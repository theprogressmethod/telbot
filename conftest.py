#!/usr/bin/env python3
"""
Test configuration and fixtures for The Progress Method bot testing
"""

import asyncio
import os
import pytest
import tempfile
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Test imports
from dotenv import load_dotenv
from supabase import create_client
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import User, Chat, Message, Update


# Load test environment
load_dotenv(".env.test")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Mock()
    config.bot_token = "test_bot_token"
    config.supabase_url = "https://test.supabase.co"
    config.supabase_key = "test_supabase_key"
    config.openai_api_key = "sk-test_openai_key"
    return config


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing"""
    supabase = Mock()
    
    # Mock table operations
    table = Mock()
    table.select.return_value.execute.return_value.data = []
    table.insert.return_value.execute.return_value.data = []
    table.update.return_value.execute.return_value.data = []
    table.delete.return_value.execute.return_value.data = []
    
    supabase.table.return_value = table
    
    return supabase


@pytest.fixture
def mock_user():
    """Mock Telegram user for testing"""
    return User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="en"
    )


@pytest.fixture
def mock_chat():
    """Mock Telegram chat for testing"""
    return Chat(
        id=-100123456789,
        type="private"
    )


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Mock Telegram message for testing"""
    message = Mock(spec=Message)
    message.message_id = 1
    message.from_user = mock_user
    message.chat = mock_chat
    message.date = datetime.now()
    message.text = "/start"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_bot():
    """Mock Telegram bot for testing"""
    bot = Mock(spec=Bot)
    bot.token = "test_token"
    bot.get_me = AsyncMock(return_value=User(
        id=987654321,
        is_bot=True,
        first_name="Test Bot",
        username="test_bot"
    ))
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.delete_message = AsyncMock()
    bot.session = Mock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def mock_dispatcher():
    """Mock Telegram dispatcher for testing"""
    dp = Mock(spec=Dispatcher)
    dp.start_polling = AsyncMock()
    dp.stop_polling = AsyncMock()
    return dp


@pytest.fixture
def test_user_data():
    """Test user data for database operations"""
    return {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_active": True
    }


@pytest.fixture
def test_commitment_data():
    """Test commitment data for testing"""
    return {
        "id": 1,
        "user_id": 123456789,
        "text": "Test commitment",
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "completion_date": None
    }


@pytest.fixture
def mock_database_manager(mock_supabase):
    """Mock database manager for testing"""
    db_manager = Mock()
    db_manager.supabase = mock_supabase
    
    # Mock user operations
    db_manager.create_user = AsyncMock(return_value={"id": 1, "telegram_id": 123456789})
    db_manager.get_user = AsyncMock(return_value={"id": 1, "telegram_id": 123456789})
    db_manager.update_user = AsyncMock(return_value={"id": 1, "telegram_id": 123456789})
    
    # Mock commitment operations
    db_manager.create_commitment = AsyncMock(return_value={"id": 1, "user_id": 123456789})
    db_manager.get_commitments = AsyncMock(return_value=[])
    db_manager.complete_commitment = AsyncMock(return_value={"id": 1, "status": "completed"})
    
    return db_manager


@pytest.fixture
def mock_role_manager():
    """Mock role manager for testing"""
    role_manager = Mock()
    role_manager.get_user_roles = AsyncMock(return_value=["user"])
    role_manager.has_role = AsyncMock(return_value=True)
    role_manager.grant_role = AsyncMock(return_value=True)
    role_manager.revoke_role = AsyncMock(return_value=True)
    return role_manager


@pytest.fixture
def temp_env_file():
    """Create a temporary .env.test file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("BOT_TOKEN=test_bot_token\n")
        f.write("SUPABASE_URL=https://test.supabase.co\n")
        f.write("SUPABASE_KEY=test_supabase_key\n")
        f.write("OPENAI_API_KEY=sk-test_openai_key\n")
        f.write("ENVIRONMENT=test\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables"""
    test_env_vars = {
        "BOT_TOKEN": "test_bot_token",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test_supabase_key",
        "OPENAI_API_KEY": "sk-test_openai_key",
        "ENVIRONMENT": "test"
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def mock_flask_app():
    """Mock Flask application for dashboard testing"""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    return app


@pytest.fixture
def mock_web_interface():
    """Mock web interface for dashboard testing"""
    web_interface = Mock()
    web_interface.app = mock_flask_app
    web_interface.initialize_systems = Mock()
    return web_interface


# Test data fixtures
@pytest.fixture
def sample_users():
    """Sample user data for testing"""
    return [
        {
            "id": 1,
            "telegram_id": 123456789,
            "username": "testuser1",
            "first_name": "Test",
            "last_name": "User1",
            "role": "user"
        },
        {
            "id": 2,
            "telegram_id": 987654321,
            "username": "testuser2",
            "first_name": "Test",
            "last_name": "User2",
            "role": "admin"
        }
    ]


@pytest.fixture
def sample_commitments():
    """Sample commitment data for testing"""
    return [
        {
            "id": 1,
            "user_id": 123456789,
            "text": "Complete project documentation",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        },
        {
            "id": 2,
            "user_id": 123456789,
            "text": "Review code changes",
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "completion_date": datetime.now().isoformat()
        }
    ]


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Perform cleanup operations
    pass