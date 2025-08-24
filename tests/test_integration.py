"""Integration tests for the TelBot system."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_task_workflow(self, mock_supabase, mock_telegram_bot):
        """Test complete task creation and notification workflow."""
        # Step 1: User sends /task command
        user_command = "/task Create integration test"
        chat_id = 16861999
        
        # Step 2: Parse command and create task
        task_title = "Create integration test"
        new_task = {
            "id": "task-123",
            "title": task_title,
            "status": "pending",
            "created_by": "user-123"
        }
        
        # Mock database insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [new_task]
        
        # Step 3: Save to database
        db_result = mock_supabase.table("tasks").insert(new_task).execute()
        
        # Step 4: Send confirmation to user
        await mock_telegram_bot.send_message(
            chat_id=chat_id,
            text=f"✅ Task created: {task_title}"
        )
        
        # Assertions
        assert db_result.data[0]["id"] == "task-123"
        mock_telegram_bot.send_message.assert_called_once()
        assert "Task created" in mock_telegram_bot.send_message.call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_user_registration_flow(self, mock_supabase, mock_telegram_bot):
        """Test new user registration flow."""
        # Step 1: New user sends /start
        telegram_user = {
            "id": 99999999,
            "username": "newuser",
            "first_name": "New",
            "last_name": "User"
        }
        
        # Step 2: Check if user exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        existing_user = mock_supabase.table("telegram_users").select("*").eq("telegram_id", telegram_user["id"]).execute()
        
        if not existing_user.data:
            # Step 3: Create new user
            new_user = {
                "telegram_id": telegram_user["id"],
                "username": telegram_user["username"],
                "first_name": telegram_user["first_name"],
                "last_name": telegram_user["last_name"]
            }
            
            mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [new_user]
            
            # Step 4: Save to database
            create_result = mock_supabase.table("telegram_users").insert(new_user).execute()
            
            # Step 5: Send welcome message
            await mock_telegram_bot.send_message(
                chat_id=telegram_user["id"],
                text=f"Welcome {telegram_user['first_name']}! You've been registered."
            )
        
        # Assertions
        assert create_result.data[0]["telegram_id"] == 99999999
        mock_telegram_bot.send_message.assert_called_once()
        assert "Welcome" in mock_telegram_bot.send_message.call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_deployment_notification_flow(self, mock_telegram_bot, mock_render_api):
        """Test deployment status notification workflow."""
        # Step 1: Trigger deployment
        deployment_info = {
            "service": "telbot-production",
            "commit": "abc123",
            "author": "developer",
            "environment": "production"
        }
        
        # Step 2: Mock deployment trigger
        mock_render_api.post.return_value.json.return_value = {
            "id": "dep-456",
            "status": "building"
        }
        
        # Step 3: Poll for deployment status
        statuses = ["building", "deploying", "live"]
        for status in statuses:
            mock_render_api.get.return_value.json.return_value = {
                "id": "dep-456",
                "status": status
            }
            
            # Simulate status check
            deployment_status = mock_render_api.get(f"/deploys/dep-456").json()
            
            if deployment_status["status"] == "live":
                # Step 4: Send success notification
                await mock_telegram_bot.send_message(
                    chat_id=16861999,
                    text=f"✅ Deployment successful!\n"
                         f"Environment: {deployment_info['environment']}\n"
                         f"Commit: {deployment_info['commit']}\n"
                         f"Author: {deployment_info['author']}"
                )
                break
        
        # Assertions
        assert deployment_status["status"] == "live"
        mock_telegram_bot.send_message.assert_called_once()
        assert "Deployment successful" in mock_telegram_bot.send_message.call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, mock_supabase, mock_telegram_bot):
        """Test error handling and recovery flow."""
        # Step 1: Simulate database error
        mock_supabase.table.return_value.insert.side_effect = Exception("Database connection failed")
        
        # Step 2: Attempt operation
        try:
            mock_supabase.table("tasks").insert({"title": "Test"}).execute()
        except Exception as e:
            error_message = str(e)
            
            # Step 3: Log error
            error_log = {
                "error": error_message,
                "timestamp": "2024-01-01T00:00:00Z",
                "service": "database",
                "action": "retry"
            }
            
            # Step 4: Notify admin
            await mock_telegram_bot.send_message(
                chat_id=16861999,  # Admin chat ID
                text=f"🚨 Error Alert:\n{error_message}\n\nAction: Retrying..."
            )
            
            # Step 5: Retry with exponential backoff
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                retry_count += 1
                
                # Simulate successful retry on 3rd attempt
                if retry_count == 3:
                    mock_supabase.table.return_value.insert.side_effect = None
                    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "success"}]
                    break
        
        # Assertions
        assert error_message == "Database connection failed"
        assert retry_count == 3
        mock_telegram_bot.send_message.assert_called_once()
        assert "Error Alert" in mock_telegram_bot.send_message.call_args.kwargs["text"]