"""
SMART 3-RETRY ENHANCEMENT SYSTEM
================================
Week 1 Key Differentiator: Allow users to improve their commitments
through up to 3 guided retry attempts with AI assistance
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class Smart3RetrySystem:
    """Enhanced SMART scoring with 3-retry improvement system"""
    
    def __init__(self, smart_analyzer, bot):
        self.smart_analyzer = smart_analyzer
        self.bot = bot
        self.retry_storage = {}  # In-memory storage for retry state
        
    async def process_commitment_with_retries(self, user_id: int, commitment_text: str, 
                                            message_to_edit, chat_id: int) -> Dict[str, Any]:
        """
        Process commitment with 3-retry enhancement system
        
        Flow:
        1. Initial SMART analysis
        2. If score < 8, offer first retry with suggestion
        3. If still < 8, offer second retry with more context
        4. If still < 8, offer third retry or graceful acceptance
        5. If still < 8, allow user to save whatever they have
        """
        
        # Initialize retry state
        retry_key = f"retry_{user_id}_{int(datetime.now().timestamp())}"
        self.retry_storage[retry_key] = {
            'original_commitment': commitment_text,
            'current_commitment': commitment_text,
            'retry_count': 0,
            'max_retries': 3,
            'user_id': user_id,
            'chat_id': chat_id,
            'attempts': []
        }
        
        # Start with initial analysis
        return await self._attempt_smart_analysis(retry_key, message_to_edit)
    
    async def _attempt_smart_analysis(self, retry_key: str, message_to_edit) -> Dict[str, Any]:
        """Perform SMART analysis attempt with retry tracking"""
        
        retry_data = self.retry_storage[retry_key]
        commitment = retry_data['current_commitment']
        user_id = retry_data['user_id']
        retry_count = retry_data['retry_count']
        
        logger.info(f"🎯 SMART analysis attempt {retry_count + 1} for user {user_id}")
        
        try:
            # Get SMART analysis
            analysis = await asyncio.wait_for(
                self.smart_analyzer.analyze_commitment(commitment, retry_data['chat_id']),
                timeout=15.0
            )
            
            # Store this attempt
            retry_data['attempts'].append({
                'attempt': retry_count + 1,
                'commitment': commitment,
                'score': analysis['score'],
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            })
            
            score = analysis['score']
            
            # Check if SMART enough (8+ score)
            if score >= 8:
                return await self._handle_success(retry_key, analysis, message_to_edit)
            
            # Check if we've reached max retries
            if retry_count >= 3:
                return await self._handle_final_attempt(retry_key, analysis, message_to_edit)
            
            # Offer retry with increasingly helpful guidance
            return await self._offer_retry(retry_key, analysis, message_to_edit)
            
        except asyncio.TimeoutError:
            logger.error("❌ SMART analysis timed out")
            return await self._handle_timeout(retry_key, message_to_edit)
        except Exception as e:
            logger.error(f"❌ SMART analysis error: {e}")
            return await self._handle_error(retry_key, str(e), message_to_edit)
    
    async def _handle_success(self, retry_key: str, analysis: Dict, message_to_edit) -> Dict[str, Any]:
        """Handle successful SMART score (8+)"""
        
        retry_data = self.retry_storage[retry_key]
        retry_count = retry_data['retry_count']
        
        success_messages = [
            f"🎉 Excellent! Your commitment is now SMART! (Score: {analysis['score']}/10)",
            f"✨ Perfect! That's a SMART commitment! (Score: {analysis['score']}/10)",
            f"🚀 Outstanding! Your refined commitment scored {analysis['score']}/10!",
        ]
        
        if retry_count == 0:
            success_msg = f"✅ Great commitment from the start! (Score: {analysis['score']}/10)"
        else:
            success_msg = success_messages[min(retry_count - 1, len(success_messages) - 1)]
            success_msg += f"\n\n🔄 Improved after {retry_count} refinement{'s' if retry_count > 1 else ''}!"
        
        success_msg += f"\n\n📝 \"{retry_data['current_commitment']}\"\n\n"
        success_msg += "Added to your commitments! Use /done when you complete it."
        
        await message_to_edit.edit_text(success_msg)
        
        # Clean up storage
        del self.retry_storage[retry_key]
        
        return {
            'success': True,
            'commitment': retry_data['current_commitment'],
            'original_commitment': retry_data['original_commitment'],
            'score': analysis['score'],
            'retry_count': retry_count
        }
    
    async def _offer_retry(self, retry_key: str, analysis: Dict, message_to_edit) -> Dict[str, Any]:
        """Offer retry with personalized guidance based on attempt number"""
        
        retry_data = self.retry_storage[retry_key]
        retry_count = retry_data['retry_count']
        score = analysis['score']
        
        # Personalized guidance based on retry count
        if retry_count == 0:
            # First retry - gentle suggestion
            guidance_title = "🤔 Let's make this more SMART!"
            guidance_text = (
                f"Your commitment scored {score}/10. Here's how to improve it:\n\n"
                f"**AI Suggestion:** \"{analysis['smartVersion']}\"\n\n"
                f"**Why this helps:** {analysis['feedback']}\n\n"
                f"Would you like to try refining it?"
            )
            
        elif retry_count == 1:
            # Second retry - more specific help
            guidance_title = "💡 Let's add more SMART details!"
            guidance_text = (
                f"Score: {score}/10 - Getting better! Let's make it even more specific:\n\n"
                f"**Enhanced suggestion:** \"{analysis['smartVersion']}\"\n\n"
                f"**SMART Tips:**\n"
                f"• Be specific about WHAT you'll do\n"
                f"• Add a measurable amount (time, quantity)\n"
                f"• Include WHEN you'll do it\n\n"
                f"Try one more refinement?"
            )
            
        else:  # retry_count == 2
            # Third retry - maximum help
            guidance_title = "🎯 One more try - let's nail it!"
            guidance_text = (
                f"Score: {score}/10 - You're close! Here's a complete SMART example:\n\n"
                f"**Best suggestion:** \"{analysis['smartVersion']}\"\n\n"
                f"**Perfect SMART format:**\n"
                f"\"I will [SPECIFIC ACTION] for [MEASURABLE AMOUNT] by [TIME/DEADLINE]\"\n\n"
                f"Example: \"I will read 10 pages of my book by 8pm today\"\n\n"
                f"Give it one final try?"
            )
        
        # Create retry keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"✏️ Try again ({retry_count + 1}/3)",
                callback_data=f"retry_improve_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="💡 Use AI suggestion",
                callback_data=f"retry_use_ai_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="📝 Keep original",
                callback_data=f"retry_keep_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=f"retry_cancel_{retry_key}"
            )]
        ])
        
        full_message = f"{guidance_title}\n\n{guidance_text}"
        
        await message_to_edit.edit_text(
            full_message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        return {
            'success': False,
            'awaiting_retry': True,
            'retry_key': retry_key
        }
    
    async def _handle_final_attempt(self, retry_key: str, analysis: Dict, message_to_edit) -> Dict[str, Any]:
        """Handle final attempt after 3 retries"""
        
        retry_data = self.retry_storage[retry_key]
        score = analysis['score']
        
        final_message = (
            f"🌟 You've worked hard on this commitment!\n\n"
            f"After 3 refinements, your score is {score}/10\n\n"
            f"**Your commitment:** \"{retry_data['current_commitment']}\"\n\n"
            f"Remember: Progress over perfection! 💪\n"
            f"Every commitment you make is a step forward.\n\n"
            f"Ready to save this commitment?"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Save my commitment",
                callback_data=f"retry_save_final_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="💡 Try AI suggestion once more",
                callback_data=f"retry_use_ai_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=f"retry_cancel_{retry_key}"
            )]
        ])
        
        await message_to_edit.edit_text(
            final_message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        return {
            'success': False,
            'final_attempt': True,
            'retry_key': retry_key
        }
    
    async def _handle_timeout(self, retry_key: str, message_to_edit):
        """Handle AI analysis timeout"""
        
        retry_data = self.retry_storage[retry_key]
        
        timeout_msg = (
            f"⏰ AI analysis took too long, but no worries!\n\n"
            f"📝 \"{retry_data['current_commitment']}\"\n\n"
            f"I'll save your commitment with a good default score.\n"
            f"You can always improve it later!"
        )
        
        await message_to_edit.edit_text(timeout_msg)
        
        # Clean up storage
        del self.retry_storage[retry_key]
        
        return {
            'success': True,
            'commitment': retry_data['current_commitment'],
            'original_commitment': retry_data['original_commitment'],
            'score': 6,  # Default score for timeout
            'retry_count': retry_data['retry_count'],
            'timeout': True
        }
    
    async def _handle_error(self, retry_key: str, error_msg: str, message_to_edit):
        """Handle analysis error"""
        
        retry_data = self.retry_storage[retry_key]
        
        error_text = (
            f"🤖 AI had a hiccup, but your commitment looks good!\n\n"
            f"📝 \"{retry_data['current_commitment']}\"\n\n"
            f"Saving with a default score. Keep up the great work!"
        )
        
        await message_to_edit.edit_text(error_text)
        
        # Clean up storage
        del self.retry_storage[retry_key]
        
        return {
            'success': True,
            'commitment': retry_data['current_commitment'],
            'original_commitment': retry_data['original_commitment'],
            'score': 5,  # Default score for error
            'retry_count': retry_data['retry_count'],
            'error': True
        }
    
    async def handle_retry_callback(self, callback_query, callback_data: str):
        """Handle callback from retry buttons"""
        
        parts = callback_data.split('_')
        action = parts[1]  # improve, use_ai, keep, cancel, save_final
        retry_key = '_'.join(parts[2:])
        
        if retry_key not in self.retry_storage:
            await callback_query.answer("Session expired. Please try /commit again.", show_alert=True)
            return None
        
        retry_data = self.retry_storage[retry_key]
        
        if action == "improve":
            # User wants to manually improve - wait for their input
            await callback_query.message.edit_text(
                f"✏️ Great! Please type your improved commitment:\n\n"
                f"**Current:** \"{retry_data['current_commitment']}\"\n\n"
                f"💡 **Tip:** Be specific, measurable, and include a deadline!"
            )
            
            # Mark as waiting for input
            retry_data['awaiting_input'] = True
            await callback_query.answer()
            return {'awaiting_input': True, 'retry_key': retry_key}
            
        elif action == "use" and parts[2] == "ai":
            # Use AI suggestion
            latest_attempt = retry_data['attempts'][-1]
            ai_suggestion = latest_attempt['analysis']['smartVersion']
            
            retry_data['current_commitment'] = ai_suggestion
            retry_data['retry_count'] += 1
            
            await callback_query.answer()
            return await self._attempt_smart_analysis(retry_key, callback_query.message)
            
        elif action == "keep":
            # Keep original commitment
            await callback_query.answer()
            
            result = {
                'success': True,
                'commitment': retry_data['original_commitment'],
                'original_commitment': retry_data['original_commitment'],
                'score': 5,  # Default score for keeping original
                'retry_count': 0,
                'kept_original': True
            }
            
            await callback_query.message.edit_text(
                f"✅ Commitment saved!\n\n"
                f"📝 \"{retry_data['original_commitment']}\"\n\n"
                f"Use /done when you complete it!"
            )
            
            del self.retry_storage[retry_key]
            return result
            
        elif action == "save" and parts[2] == "final":
            # Save final attempt
            await callback_query.answer()
            
            result = {
                'success': True,
                'commitment': retry_data['current_commitment'],
                'original_commitment': retry_data['original_commitment'],
                'score': retry_data['attempts'][-1]['score'],
                'retry_count': retry_data['retry_count'],
                'final_save': True
            }
            
            await callback_query.message.edit_text(
                f"✅ Commitment saved after thoughtful refinement!\n\n"
                f"📝 \"{retry_data['current_commitment']}\"\n\n"
                f"Great work on the improvement process! 💪"
            )
            
            del self.retry_storage[retry_key]
            return result
            
        elif action == "cancel":
            # Cancel commitment
            await callback_query.answer()
            await callback_query.message.edit_text(
                "❌ Commitment cancelled. Use /commit when you're ready to try again!"
            )
            
            del self.retry_storage[retry_key]
            return None
        
        return None
    
    async def handle_retry_input(self, message, retry_key: str):
        """Handle user input for retry improvement"""
        
        if retry_key not in self.retry_storage:
            await message.answer("Session expired. Please use /commit to start over.")
            return None
            
        retry_data = self.retry_storage[retry_key]
        
        if not retry_data.get('awaiting_input', False):
            return None
        
        # Update commitment and continue analysis
        new_commitment = message.text.strip()
        retry_data['current_commitment'] = new_commitment
        retry_data['retry_count'] += 1
        retry_data['awaiting_input'] = False
        
        # Create new loading message
        loading_msg = await message.answer("🔄 Analyzing your improved commitment...")
        
        return await self._attempt_smart_analysis(retry_key, loading_msg)
    
    def cleanup_expired_sessions(self, max_age_minutes: int = 30):
        """Clean up expired retry sessions"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self.retry_storage.items():
            if 'timestamp' in data:
                session_time = datetime.fromisoformat(data['timestamp'])
                if (current_time - session_time).total_seconds() > max_age_minutes * 60:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.retry_storage[key]
            
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired retry sessions")

# Global instance (will be initialized in telbot.py)
smart_3_retry = None