"""Tests for database operations."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    def test_create_user_profile(self, mock_supabase):
        """Test creating a user profile."""
        # Prepare test data
        user_data = {
            "id": str(uuid.uuid4()),
            "username": "testuser",
            "full_name": "Test User",
            "role": "user"
        }
        
        # Mock the insert operation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [user_data]
        
        # Execute insert
        result = mock_supabase.table("profiles").insert(user_data).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["username"] == "testuser"
        mock_supabase.table.assert_called_with("profiles")
        mock_supabase.table.return_value.insert.assert_called_with(user_data)
    
    def test_get_user_profile(self, mock_supabase):
        """Test retrieving a user profile."""
        # Prepare test data
        user_id = str(uuid.uuid4())
        expected_data = {
            "id": user_id,
            "username": "testuser",
            "full_name": "Test User"
        }
        
        # Mock the select operation
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [expected_data]
        
        # Execute select
        result = mock_supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["id"] == user_id
        mock_supabase.table.assert_called_with("profiles")
    
    def test_create_task(self, mock_supabase, sample_task):
        """Test creating a task."""
        # Mock the insert operation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [sample_task]
        
        # Execute insert
        result = mock_supabase.table("tasks").insert(sample_task).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["title"] == "Test Task"
        assert result.data[0]["status"] == "pending"
    
    def test_update_task_status(self, mock_supabase, sample_task):
        """Test updating task status."""
        # Prepare update data
        task_id = sample_task["id"]
        updated_task = {**sample_task, "status": "completed"}
        
        # Mock the update operation
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_task]
        
        # Execute update
        result = mock_supabase.table("tasks").update({"status": "completed"}).eq("id", task_id).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["status"] == "completed"
    
    def test_delete_task(self, mock_supabase):
        """Test deleting a task."""
        # Prepare test data
        task_id = str(uuid.uuid4())
        
        # Mock the delete operation
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": task_id}]
        
        # Execute delete
        result = mock_supabase.table("tasks").delete().eq("id", task_id).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["id"] == task_id
    
    def test_create_telegram_user(self, mock_supabase):
        """Test creating a Telegram user."""
        # Prepare test data
        telegram_user = {
            "telegram_id": 16861999,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "is_bot": False,
            "language_code": "en"
        }
        
        # Mock the insert operation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [telegram_user]
        
        # Execute insert
        result = mock_supabase.table("telegram_users").insert(telegram_user).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["telegram_id"] == 16861999
        assert result.data[0]["username"] == "testuser"
    
    def test_log_activity(self, mock_supabase):
        """Test logging user activity."""
        # Prepare test data
        activity = {
            "user_id": str(uuid.uuid4()),
            "action": "user.login",
            "details": "User logged in successfully",
            "metadata": {"ip": "127.0.0.1", "device": "mobile"},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Mock the insert operation
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [activity]
        
        # Execute insert
        result = mock_supabase.table("activity_log").insert(activity).execute()
        
        # Assertions
        assert len(result.data) == 1
        assert result.data[0]["action"] == "user.login"
        assert result.data[0]["metadata"]["ip"] == "127.0.0.1"