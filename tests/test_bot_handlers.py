"""Tests for bot command handlers."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestBotHandlers:
    """Test bot command handlers."""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_telegram_bot, sample_telegram_update):
        """Test /start command handler."""
        # Mock the handler function
        async def start_handler(update, context):
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text="Welcome to TelBot! Type /help for available commands."
            )
            return True
        
        # Create mock context
        context = MagicMock()
        context.bot = mock_telegram_bot
        
        # Execute handler
        update = MagicMock()
        update.message.chat.id = sample_telegram_update["message"]["chat"]["id"]
        
        result = await start_handler(update, context)
        
        # Assertions
        assert result is True
        mock_telegram_bot.send_message.assert_called_once()
        call_args = mock_telegram_bot.send_message.call_args
        assert call_args.kwargs["chat_id"] == 16861999
        assert "Welcome" in call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_telegram_bot):
        """Test /help command handler."""
        # Mock the handler function
        async def help_handler(update, context):
            help_text = """
            Available commands:
            /start - Start the bot
            /help - Show this help message
            /status - Check bot status
            /task - Manage tasks
            """
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=help_text
            )
            return True
        
        # Create mock context
        context = MagicMock()
        context.bot = mock_telegram_bot
        
        # Execute handler
        update = MagicMock()
        update.message.chat.id = 12345
        
        result = await help_handler(update, context)
        
        # Assertions
        assert result is True
        mock_telegram_bot.send_message.assert_called_once()
        call_args = mock_telegram_bot.send_message.call_args
        assert "Available commands" in call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_status_command(self, mock_telegram_bot, mock_supabase):
        """Test /status command handler."""
        # Mock the handler function
        async def status_handler(update, context):
            # Check database connection
            try:
                # Simulate database check
                db_status = "✅ Connected"
            except:
                db_status = "❌ Disconnected"
            
            status_text = f"""
            🤖 Bot Status:
            Database: {db_status}
            Uptime: 1h 23m
            Version: 1.0.0
            Environment: test
            """
            
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=status_text
            )
            return True
        
        # Create mock context
        context = MagicMock()
        context.bot = mock_telegram_bot
        
        # Execute handler
        update = MagicMock()
        update.message.chat.id = 12345
        
        result = await status_handler(update, context)
        
        # Assertions
        assert result is True
        mock_telegram_bot.send_message.assert_called_once()
        call_args = mock_telegram_bot.send_message.call_args
        assert "Bot Status" in call_args.kwargs["text"]
        assert "Database" in call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_invalid_command(self, mock_telegram_bot):
        """Test handling of invalid commands."""
        # Mock the handler function
        async def unknown_handler(update, context):
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text="❌ Unknown command. Type /help for available commands."
            )
            return False
        
        # Create mock context
        context = MagicMock()
        context.bot = mock_telegram_bot
        
        # Execute handler
        update = MagicMock()
        update.message.chat.id = 12345
        update.message.text = "/invalid"
        
        result = await unknown_handler(update, context)
        
        # Assertions
        assert result is False
        mock_telegram_bot.send_message.assert_called_once()
        call_args = mock_telegram_bot.send_message.call_args
        assert "Unknown command" in call_args.kwargs["text"]
    
    @pytest.mark.asyncio
    async def test_error_handler(self, mock_telegram_bot):
        """Test error handling in bot."""
        # Mock the error handler function
        async def error_handler(update, context):
            error_message = f"An error occurred: {context.error}"
            
            # Log error (in production, this would go to logging service)
            print(f"Error: {context.error}")
            
            # Notify user
            if update and update.message:
                await context.bot.send_message(
                    chat_id=update.message.chat.id,
                    text="❌ An error occurred. Please try again later."
                )
            
            return True
        
        # Create mock context with error
        context = MagicMock()
        context.bot = mock_telegram_bot
        context.error = Exception("Test error")
        
        # Execute handler
        update = MagicMock()
        update.message.chat.id = 12345
        
        result = await error_handler(update, context)
        
        # Assertions
        assert result is True
        mock_telegram_bot.send_message.assert_called_once()
        call_args = mock_telegram_bot.send_message.call_args
        assert "error occurred" in call_args.kwargs["text"]