"""
SMART 2-RETRY ENHANCEMENT SYSTEM
================================
Week 1 Key Differentiator: Allow users to improve their commitments
through up to 2 guided retry attempts with enthusiastic coaching
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class Smart2RetrySystem:
    """Enhanced SMART scoring with 2-retry improvement system - enthusiastic coach style"""
    
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
            'max_retries': 2,  # Changed from 3 to 2
            'user_id': user_id,
            'chat_id': chat_id,
            'attempts': []
        }
        
        # Start with initial analysis
        return await self._attempt_smart_analysis(retry_key, message_to_edit)
    
    def _get_smart_feedback_and_question(self, analysis: Dict) -> tuple[str, str]:
        """Get specific SMART feedback and refining question based on what needs improvement"""
        
        # Extract SMART scores if available
        feedback = analysis.get('feedback', '').lower()
        
        # Identify specific SMART dimensions that need work
        missing_dimensions = []
        question = ""
        
        if 'specific' in feedback or 'vague' in feedback:
            missing_dimensions.append('specific')
            question = "🎯 What exactly will you do? Instead of 'exercise,' try 'do 20 push-ups' or 'walk for 15 minutes.'"
        
        if 'measurable' in feedback or 'measure' in feedback:
            missing_dimensions.append('measurable')
            if not question:
                question = "📏 How will you measure success? Add numbers like 'for 30 minutes,' '10 pages,' or 'complete 3 tasks.'"
        
        if 'time' in feedback or 'when' in feedback or 'deadline' in feedback:
            missing_dimensions.append('time-bound')
            if not question:
                question = "⏰ When will you do this? Add a specific time like 'by 8pm today' or 'at 7am tomorrow morning.'"
        
        if 'achievable' in feedback or 'realistic' in feedback:
            missing_dimensions.append('achievable')
            if not question:
                question = "💪 Is this realistic for you right now? Maybe start smaller and build momentum!"
        
        if 'relevant' in feedback:
            missing_dimensions.append('relevant')
            if not question:
                question = "🎯 Why is this important to you? What bigger goal does this connect to?"
        
        # Create specific feedback about what dimensions need work
        if len(missing_dimensions) == 1:
            smart_feedback = f"Let's make this more {missing_dimensions[0]}!"
        elif len(missing_dimensions) == 2:
            smart_feedback = f"Let's make this more {missing_dimensions[0]} and {missing_dimensions[1]}!"
        elif len(missing_dimensions) > 2:
            smart_feedback = f"Let's make this more {', '.join(missing_dimensions[:-1])}, and {missing_dimensions[-1]}!"
        else:
            # Generic fallback
            smart_feedback = "Let's make this clearer and more actionable!"
            question = "✨ What exactly will you do, for how long, and by when?"
        
        return smart_feedback, question
    
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
            if retry_count >= 2:
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
            f"🎉 YES! You nailed it! That's a SMART commitment! (Score: {analysis['score']}/10)",
            f"✨ AMAZING! Look at you go! Perfect SMART commitment! (Score: {analysis['score']}/10)",
            f"🚀 BOOM! That's what I'm talking about! Outstanding! (Score: {analysis['score']}/10)",
        ]
        
        if retry_count == 0:
            success_msg = f"🌟 Excellent! That's a solid commitment right from the start! (Score: {analysis['score']}/10)\n\nYou've got this!"
        else:
            success_msg = success_messages[min(retry_count - 1, len(success_messages) - 1)]
            success_msg += f"\n\n💪 I really appreciate how you took the time to refine this. That's the growth mindset in action!"
        
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
        
        # Get specific SMART feedback and refining question
        smart_feedback, smart_question = self._get_smart_feedback_and_question(analysis)
        
        # Grounded, caring coaching guidance based on retry count
        if retry_count == 0:
            # First retry - encouraging and specific
            guidance_title = f"🌟 Good foundation! {smart_feedback}"
            guidance_text = (
                f"You scored {score}/10 - that's a solid start! 💪\n\n"
                f"{smart_question}\n\n"
                f"💡 **Here's what I'm thinking:** \"{analysis['smartVersion']}\"\n\n"
                f"Want to give it another try? I'm here to help! 🤝"
            )
            
        else:  # retry_count == 1 (final retry)
            # Second retry - supportive and clear
            guidance_title = f"🎯 You're getting there! {smart_feedback}"
            guidance_text = (
                f"Score: {score}/10 - I can see you're putting in the effort! 💪\n\n"
                f"{smart_question}\n\n"
                f"🌟 **My best suggestion:** \"{analysis['smartVersion']}\"\n\n"
                f"✨ **Quick reminder:**\n"
                f"• WHAT exactly will you do?\n"
                f"• HOW MUCH or for how long?\n"
                f"• BY WHEN will you finish?\n\n"
                f"You're doing great - one more try! 🚀"
            )
        
        # Create retry keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"🚀 Let's improve it! ({retry_count + 1}/2)",
                callback_data=f"retry_improve_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="✨ Use your suggestion",
                callback_data=f"retry_use_ai_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="📝 Keep my original",
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
            f"🎉 You know what? I'm PROUD of the effort you've put in!\n\n"
            f"Your commitment scored {score}/10 - and that's GREAT! 🌟\n\n"
            f"**Your commitment:** \"{retry_data['current_commitment']}\"\n\n"
            f"🔥 Here's the truth: DONE is better than perfect!\n"
            f"Taking action beats endless planning every single time! 💪\n\n"
            f"Let's lock this in and start making progress!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 YES! Save it and let's go!",
                callback_data=f"retry_save_final_{retry_key}"
            )],
            [InlineKeyboardButton(
                text="✨ Try your suggestion",
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
        
        logger.info(f"🔄 Raw callback data: '{callback_data}'")
        parts = callback_data.split('_')
        logger.info(f"🔄 Split parts: {parts}")
        
        # Handle compound actions like "use_ai" and "save_final"
        if len(parts) >= 3 and f"{parts[1]}_{parts[2]}" in ['use_ai', 'save_final']:
            action = f"{parts[1]}_{parts[2]}"
            retry_key = '_'.join(parts[3:])
        else:
            action = parts[1]  # improve, keep, cancel
            retry_key = '_'.join(parts[2:])
        
        logger.info(f"🔄 Parsed: action='{action}', key='{retry_key}'")
        
        if retry_key not in self.retry_storage:
            logger.error(f"❌ Session key '{retry_key}' not found in storage")
            logger.error(f"❌ Available keys: {list(self.retry_storage.keys())}")
            await callback_query.answer("Session expired. Please try /commit again.", show_alert=True)
            return None
        
        retry_data = self.retry_storage[retry_key]
        
        if action == "improve":
            # User wants to manually improve - wait for their input
            smart_feedback, smart_question = self._get_smart_feedback_and_question(retry_data['attempts'][-1]['analysis'])
            await callback_query.message.edit_text(
                f"🌟 Great! {smart_feedback}\n\n"
                f"**Your current commitment:** \"{retry_data['current_commitment']}\"\n\n"
                f"{smart_question}\n\n"
                f"Type your improved commitment below - I'm here to help! 🤝"
            )
            
            # Mark as waiting for input
            retry_data['awaiting_input'] = True
            await callback_query.answer()
            return {'awaiting_input': True, 'retry_key': retry_key}
            
        elif action == "use_ai":
            # Use AI suggestion
            latest_attempt = retry_data['attempts'][-1]
            ai_suggestion = latest_attempt['analysis']['smartVersion']
            
            retry_data['current_commitment'] = ai_suggestion
            retry_data['retry_count'] += 1
            
            await callback_query.answer("✨ Using my suggestion - let's see how it scores!")
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
                f"🌟 Perfect! Your commitment is saved!\n\n"
                f"📝 \"{retry_data['original_commitment']}\"\n\n"
                f"Now let's make it happen! Use /done when you complete it! 💪"
            )
            
            del self.retry_storage[retry_key]
            return result
            
        elif action == "save_final":
            # Save final attempt
            await callback_query.answer("🚀 Let's lock it in!")
            
            result = {
                'success': True,
                'commitment': retry_data['current_commitment'],
                'original_commitment': retry_data['original_commitment'],
                'score': retry_data['attempts'][-1]['score'],
                'retry_count': retry_data['retry_count'],
                'final_save': True
            }
            
            await callback_query.message.edit_text(
                f"🌟 Excellent! Your commitment is saved!\n\n"
                f"📝 \"{retry_data['current_commitment']}\"\n\n"
                f"Great work on refining this - now let's see you complete it! 💪"
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
smart_2_retry = None