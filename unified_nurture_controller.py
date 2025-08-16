#!/usr/bin/env python3
"""
Unified Nurture Sequence Controller
Phase 2 Enhancement: Multi-channel delivery with email and engagement-based personalization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from supabase import Client
from nurture_sequences import NurtureSequences, SequenceType
from attendance_nurture_engine import AttendanceNurtureEngine, AttendanceTrigger

logger = logging.getLogger(__name__)

class DeliveryChannel(Enum):
    """Available delivery channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    BOTH = "both"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 5
    NORMAL = 3
    HIGH = 1
    URGENT = 0

@dataclass
class DeliveryResult:
    """Result of a message delivery attempt"""
    delivery_id: str
    channel: DeliveryChannel
    status: str
    recipient: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass 
class EngagementContext:
    """User engagement context for personalization"""
    user_id: str
    overall_score: float
    telegram_score: float
    email_score: float
    attendance_score: float
    commitment_score: float
    preferred_channel: DeliveryChannel
    last_engagement: Optional[datetime]

class UnifiedNurtureController:
    """
    Unified controller for managing all nurture sequences with multi-channel delivery
    """
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.nurture_sequences = NurtureSequences(supabase_client)
        self.attendance_engine = AttendanceNurtureEngine()
        
        # Email service will be injected
        self.email_service = None
        self.telegram_service = None
        
        logger.info("🎯 Unified Nurture Controller initialized")
    
    def set_email_service(self, email_service):
        """Inject email service for multi-channel delivery"""
        self.email_service = email_service
        logger.info("📧 Email service configured")
    
    def set_telegram_service(self, telegram_service):
        """Inject telegram service for multi-channel delivery"""
        self.telegram_service = telegram_service
        logger.info("📱 Telegram service configured")
    
    async def trigger_sequence(
        self, 
        user_id: str, 
        sequence_type: SequenceType, 
        context: Dict[str, Any] = None,
        override_channel: Optional[DeliveryChannel] = None
    ) -> bool:
        """
        Enhanced sequence triggering with engagement-based personalization
        """
        try:
            # Get user engagement context
            engagement_ctx = await self._get_user_engagement_context(user_id)
            
            # Determine optimal delivery strategy
            delivery_strategy = await self._determine_delivery_strategy(
                user_id, engagement_ctx, override_channel
            )
            
            # Check if sequence already active
            existing = await self._check_existing_sequence(user_id, sequence_type.value)
            if existing:
                logger.info(f"User {user_id} already has active {sequence_type.value} sequence")
                return False
            
            # Get A/B test variant if applicable
            variant_assignments = await self._get_variant_assignments(user_id, sequence_type.value)
            
            # Create enhanced sequence state
            sequence_state = {
                "user_id": user_id,
                "sequence_type": sequence_type.value,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "context": json.dumps(context or {}),
                "is_active": True,
                "preferred_channel": delivery_strategy.value,
                "engagement_score": engagement_ctx.overall_score,
                "variant_assignments": json.dumps(variant_assignments),
                "last_engagement_at": engagement_ctx.last_engagement.isoformat() if engagement_ctx.last_engagement else None,
                "next_message_at": self._calculate_next_message_time(sequence_type, 0, engagement_ctx)
            }
            
            # Insert sequence state
            result = self.supabase.table("user_sequence_state").insert(sequence_state).execute()
            
            if result.data:
                logger.info(f"✅ Started {sequence_type.value} sequence for user {user_id} with {delivery_strategy.value} channel")
                
                # Process immediate messages
                await self._process_immediate_messages(user_id, sequence_type.value, engagement_ctx)
                return True
                
        except Exception as e:
            logger.error(f"Error triggering sequence: {e}")
            return False
    
    async def _get_user_engagement_context(self, user_id: str) -> EngagementContext:
        """Get comprehensive user engagement context"""
        try:
            # Get engagement scores
            scores_result = self.supabase.table("user_engagement_summary").select("*").eq("user_id", user_id).execute()
            
            if scores_result.data:
                data = scores_result.data[0]
                return EngagementContext(
                    user_id=user_id,
                    overall_score=float(data.get("overall_engagement_score", 50.0)),
                    telegram_score=float(data.get("telegram_engagement_score", 0)),
                    email_score=float(data.get("email_engagement_score", 0)),
                    attendance_score=float(data.get("attendance_engagement_score", 0)),
                    commitment_score=float(data.get("commitment_engagement_score", 0)),
                    preferred_channel=DeliveryChannel(data.get("preferred_channel", "telegram")),
                    last_engagement=datetime.fromisoformat(data["last_message_sent"]) if data.get("last_message_sent") else None
                )
            else:
                # Calculate engagement scores for new user
                await self._calculate_and_store_engagement_scores(user_id)
                
                return EngagementContext(
                    user_id=user_id,
                    overall_score=50.0,
                    telegram_score=0,
                    email_score=0,
                    attendance_score=0,
                    commitment_score=0,
                    preferred_channel=DeliveryChannel.TELEGRAM,
                    last_engagement=None
                )
                
        except Exception as e:
            logger.error(f"Error getting engagement context: {e}")
            # Return default context
            return EngagementContext(
                user_id=user_id,
                overall_score=50.0,
                telegram_score=0,
                email_score=0,
                attendance_score=0,
                commitment_score=0,
                preferred_channel=DeliveryChannel.TELEGRAM,
                last_engagement=None
            )
    
    async def _calculate_and_store_engagement_scores(self, user_id: str):
        """Calculate and store engagement scores for user"""
        try:
            score_types = ['overall', 'telegram', 'email', 'attendance', 'commitment']
            
            for score_type in score_types:
                # Call database function to calculate score
                result = self.supabase.rpc('calculate_engagement_score', {
                    'target_user_id': user_id,
                    'score_type': score_type
                }).execute()
                
                if result.data:
                    score = float(result.data)
                    
                    # Store the score
                    score_data = {
                        "user_id": user_id,
                        "score_type": score_type,
                        "score": score,
                        "calculated_at": datetime.now().isoformat(),
                        "valid_until": (datetime.now() + timedelta(hours=24)).isoformat()  # Cache for 24 hours
                    }
                    
                    # Upsert the score
                    self.supabase.table("engagement_scores").upsert(score_data).execute()
                    
        except Exception as e:
            logger.error(f"Error calculating engagement scores: {e}")
    
    async def _determine_delivery_strategy(
        self, 
        user_id: str, 
        engagement_ctx: EngagementContext,
        override_channel: Optional[DeliveryChannel] = None
    ) -> DeliveryChannel:
        """Determine optimal delivery strategy based on engagement"""
        
        if override_channel:
            return override_channel
        
        # Use preferred channel from engagement context
        if engagement_ctx.preferred_channel:
            return engagement_ctx.preferred_channel
        
        # Fallback logic based on engagement scores
        if engagement_ctx.email_score > engagement_ctx.telegram_score and engagement_ctx.email_score > 20:
            return DeliveryChannel.EMAIL
        elif engagement_ctx.overall_score > 70:  # High engagement users get both channels
            return DeliveryChannel.BOTH
        else:
            return DeliveryChannel.TELEGRAM
    
    async def _get_variant_assignments(self, user_id: str, sequence_type: str) -> Dict[str, str]:
        """Get A/B test variant assignments for user"""
        try:
            # Get active variants for this sequence type
            variants_result = self.supabase.table("sequence_variants").select("*").eq(
                "sequence_type", sequence_type
            ).eq("is_active", True).execute()
            
            assignments = {}
            
            for variant in variants_result.data:
                step = variant["message_step"]
                variant_name = variant["variant_name"]
                test_percentage = variant["test_percentage"]
                
                # Simple hash-based assignment (consistent for user)
                user_hash = hash(f"{user_id}_{sequence_type}_{step}") % 100
                
                if user_hash < test_percentage:
                    assignments[f"step_{step}"] = variant_name
            
            return assignments
            
        except Exception as e:
            logger.error(f"Error getting variant assignments: {e}")
            return {}
    
    async def _check_existing_sequence(self, user_id: str, sequence_type: str) -> bool:
        """Check if user already has active sequence of this type"""
        try:
            result = self.supabase.table("user_sequence_state").select("id").eq(
                "user_id", user_id
            ).eq("sequence_type", sequence_type).eq("is_active", True).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking existing sequence: {e}")
            return False
    
    def _calculate_next_message_time(
        self, 
        sequence_type: SequenceType, 
        current_step: int,
        engagement_ctx: EngagementContext
    ) -> str:
        """Calculate next message time with engagement-based adjustments"""
        
        # Get base timing from sequence definition
        sequence_def = self.nurture_sequences.sequences.get(sequence_type.value)
        if not sequence_def or current_step >= len(sequence_def["messages"]):
            return None
        
        base_delay_hours = sequence_def["messages"][current_step]["delay_hours"]
        
        # Adjust timing based on engagement score
        if engagement_ctx.overall_score > 80:
            # High engagement users can receive messages more frequently
            adjusted_delay = max(1, base_delay_hours * 0.7)
        elif engagement_ctx.overall_score < 30:
            # Low engagement users get messages less frequently
            adjusted_delay = base_delay_hours * 1.5
        else:
            adjusted_delay = base_delay_hours
        
        next_time = datetime.now() + timedelta(hours=adjusted_delay)
        return next_time.isoformat()
    
    async def _process_immediate_messages(
        self, 
        user_id: str, 
        sequence_type: str, 
        engagement_ctx: EngagementContext
    ):
        """Process messages that should be sent immediately"""
        try:
            sequence_def = self.nurture_sequences.sequences[sequence_type]
            immediate_messages = [
                (idx, msg) for idx, msg in enumerate(sequence_def["messages"]) 
                if msg["delay_hours"] == 0
            ]
            
            for step_idx, message_data in immediate_messages:
                # Check conditions
                if await self._should_send_message(user_id, message_data):
                    # Get personalized message content
                    message_content = await self._personalize_message(
                        user_id, message_data, engagement_ctx
                    )
                    
                    # Schedule multi-channel delivery
                    await self._schedule_multi_channel_delivery(
                        user_id=user_id,
                        sequence_type=sequence_type,
                        message_step=step_idx,
                        message_content=message_content,
                        delivery_channel=engagement_ctx.preferred_channel,
                        priority=MessagePriority.NORMAL
                    )
                    
        except Exception as e:
            logger.error(f"Error processing immediate messages: {e}")
    
    async def _should_send_message(self, user_id: str, message_data: Dict) -> bool:
        """Enhanced message condition checking"""
        # Use existing logic from nurture_sequences.py
        return await self.nurture_sequences._should_send_message(user_id, message_data)
    
    async def _personalize_message(
        self, 
        user_id: str, 
        message_data: Dict, 
        engagement_ctx: EngagementContext
    ) -> str:
        """Personalize message content based on engagement context"""
        try:
            # Get user info
            user_result = self.supabase.table("users").select("first_name, last_name").eq("id", user_id).execute()
            if not user_result.data:
                return message_data["message"]
            
            user = user_result.data[0]
            first_name = user.get("first_name", "there")
            
            message_content = message_data["message"]
            
            # Basic personalization
            message_content = message_content.replace("{user_name}", first_name)
            message_content = message_content.replace("{first_name}", first_name)
            
            # Engagement-based personalization
            if engagement_ctx.overall_score > 80:
                # High engagement users get more advanced content
                message_content = self._enhance_message_for_high_engagement(message_content)
            elif engagement_ctx.overall_score < 30:
                # Low engagement users get simplified, more encouraging content
                message_content = self._simplify_message_for_low_engagement(message_content)
            
            return message_content
            
        except Exception as e:
            logger.error(f"Error personalizing message: {e}")
            return message_data["message"]
    
    def _enhance_message_for_high_engagement(self, message: str) -> str:
        """Enhance messages for highly engaged users"""
        # Add advanced tips and challenges
        enhancements = [
            "\n\n💡 **Pro tip:** Track your progress patterns to identify your peak performance times!",
            "\n\n🎯 **Challenge:** Try setting a stretch goal this week - you've got the momentum!",
            "\n\n🚀 **Level up:** Consider mentoring someone else in your progress journey!"
        ]
        
        # Add random enhancement
        import random
        return message + random.choice(enhancements)
    
    def _simplify_message_for_low_engagement(self, message: str) -> str:
        """Simplify messages for low engagement users"""
        # Make messages more encouraging and less overwhelming
        if len(message) > 200:
            # Truncate and add encouraging note
            simplified = message[:150] + "...\n\n💙 Remember: Small steps lead to big breakthroughs. You've got this!"
        else:
            simplified = message + "\n\n💪 Every small step counts. We believe in you!"
        
        return simplified
    
    async def _schedule_multi_channel_delivery(
        self,
        user_id: str,
        sequence_type: str,
        message_step: int,
        message_content: str,
        delivery_channel: DeliveryChannel,
        priority: MessagePriority = MessagePriority.NORMAL,
        scheduled_time: Optional[datetime] = None
    ) -> List[DeliveryResult]:
        """Schedule message delivery across multiple channels"""
        
        results = []
        
        try:
            # Use database function for scheduling
            schedule_result = self.supabase.rpc('schedule_multi_channel_message', {
                'target_user_id': user_id,
                'sequence_type': sequence_type,
                'message_step': message_step,
                'message_content': message_content,
                'scheduled_time': (scheduled_time or datetime.now()).isoformat()
            }).execute()
            
            # Process scheduled deliveries
            for delivery in schedule_result.data:
                delivery_result = DeliveryResult(
                    delivery_id=delivery["delivery_id"],
                    channel=DeliveryChannel(delivery["channel"]),
                    status="scheduled",
                    recipient=delivery["recipient"]
                )
                results.append(delivery_result)
                
                logger.info(f"📨 Scheduled {delivery['channel']} message for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling multi-channel delivery: {e}")
            
            # Fallback to single channel
            delivery_result = DeliveryResult(
                delivery_id=str(uuid.uuid4()),
                channel=DeliveryChannel.TELEGRAM,
                status="failed",
                recipient="unknown",
                error_message=str(e)
            )
            results.append(delivery_result)
        
        return results
    
    async def process_pending_deliveries(self) -> Dict[str, int]:
        """Process all pending message deliveries"""
        try:
            stats = {
                "telegram_sent": 0,
                "telegram_failed": 0,
                "email_sent": 0,
                "email_failed": 0,
                "total_processed": 0
            }
            
            # Get pending deliveries
            now = datetime.now().isoformat()
            pending_result = self.supabase.table("message_deliveries").select("*").eq(
                "delivery_status", "pending"
            ).lte("scheduled_at", now).execute()
            
            for delivery in pending_result.data:
                stats["total_processed"] += 1
                
                try:
                    if delivery["channel"] == "telegram":
                        success = await self._send_telegram_message(delivery)
                        if success:
                            stats["telegram_sent"] += 1
                        else:
                            stats["telegram_failed"] += 1
                    
                    elif delivery["channel"] == "email":
                        success = await self._send_email_message(delivery)
                        if success:
                            stats["email_sent"] += 1
                        else:
                            stats["email_failed"] += 1
                
                except Exception as e:
                    logger.error(f"Error processing delivery {delivery['id']}: {e}")
                    if delivery["channel"] == "telegram":
                        stats["telegram_failed"] += 1
                    else:
                        stats["email_failed"] += 1
            
            logger.info(f"📊 Processed {stats['total_processed']} pending deliveries: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing pending deliveries: {e}")
            return {"error": str(e)}
    
    async def _send_telegram_message(self, delivery: Dict) -> bool:
        """Send Telegram message"""
        try:
            if not self.telegram_service:
                logger.warning("Telegram service not configured")
                return False
            
            telegram_user_id = int(delivery["recipient_address"])
            message_content = delivery["message_content"]
            
            # Send via Telegram service
            success = await self.telegram_service.send_message(
                telegram_user_id, message_content, parse_mode='Markdown'
            )
            
            if success:
                # Update delivery status
                self.supabase.table("message_deliveries").update({
                    "delivery_status": "sent",
                    "sent_at": datetime.now().isoformat()
                }).eq("id", delivery["id"]).execute()
                
                logger.debug(f"✅ Telegram message sent to {telegram_user_id}")
                return True
            else:
                # Mark as failed
                self._mark_delivery_failed(delivery["id"], "Telegram send failed")
                return False
                
        except Exception as e:
            self._mark_delivery_failed(delivery["id"], f"Telegram error: {str(e)}")
            return False
    
    async def _send_email_message(self, delivery: Dict) -> bool:
        """Send email message"""
        try:
            if not self.email_service:
                logger.warning("Email service not configured")
                return False
            
            email_address = delivery["recipient_address"]
            message_content = delivery["message_content"]
            
            # Get user for personalization
            user_result = self.supabase.table("users").select("first_name").eq("id", delivery["user_id"]).execute()
            user_name = user_result.data[0]["first_name"] if user_result.data else "Friend"
            
            # Send via email service
            success = await self.email_service.send_nurture_email(
                to_email=email_address,
                subject=f"Your Progress Method Update",
                content=message_content,
                user_name=user_name,
                tracking_id=delivery["id"]
            )
            
            if success:
                # Update delivery status
                self.supabase.table("message_deliveries").update({
                    "delivery_status": "sent",
                    "sent_at": datetime.now().isoformat(),
                    "tracking_id": delivery["id"]
                }).eq("id", delivery["id"]).execute()
                
                logger.debug(f"✅ Email sent to {email_address}")
                return True
            else:
                self._mark_delivery_failed(delivery["id"], "Email send failed")
                return False
                
        except Exception as e:
            self._mark_delivery_failed(delivery["id"], f"Email error: {str(e)}")
            return False
    
    def _mark_delivery_failed(self, delivery_id: str, reason: str):
        """Mark delivery as failed"""
        try:
            self.supabase.table("message_deliveries").update({
                "delivery_status": "failed",
                "failed_at": datetime.now().isoformat(),
                "failure_reason": reason,
                "attempt_count": self.supabase.table("message_deliveries").select("attempt_count").eq("id", delivery_id).execute().data[0]["attempt_count"] + 1
            }).eq("id", delivery_id).execute()
        except Exception as e:
            logger.error(f"Error marking delivery failed: {e}")
    
    async def get_sequence_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive sequence analytics"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            # Get delivery analytics
            analytics_result = self.supabase.table("delivery_analytics").select("*").gte(
                "delivery_date", cutoff_date.isoformat()
            ).execute()
            
            # Aggregate data
            analytics = {
                "period_days": days,
                "total_deliveries": 0,
                "channel_breakdown": {},
                "sequence_breakdown": {},
                "overall_metrics": {
                    "delivery_rate": 0,
                    "open_rate": 0,
                    "click_rate": 0
                }
            }
            
            total_scheduled = 0
            total_delivered = 0
            total_opened = 0
            total_clicked = 0
            
            for row in analytics_result.data:
                sequence_type = row["sequence_type"]
                channel = row["channel"]
                
                # Channel breakdown
                if channel not in analytics["channel_breakdown"]:
                    analytics["channel_breakdown"][channel] = {
                        "scheduled": 0,
                        "delivered": 0,
                        "opened": 0,
                        "clicked": 0
                    }
                
                analytics["channel_breakdown"][channel]["scheduled"] += row["total_scheduled"]
                analytics["channel_breakdown"][channel]["delivered"] += row["delivered_count"]
                analytics["channel_breakdown"][channel]["opened"] += row["opened_count"]
                analytics["channel_breakdown"][channel]["clicked"] += row["clicked_count"]
                
                # Sequence breakdown
                if sequence_type not in analytics["sequence_breakdown"]:
                    analytics["sequence_breakdown"][sequence_type] = {
                        "scheduled": 0,
                        "delivered": 0,
                        "opened": 0,
                        "clicked": 0
                    }
                
                analytics["sequence_breakdown"][sequence_type]["scheduled"] += row["total_scheduled"]
                analytics["sequence_breakdown"][sequence_type]["delivered"] += row["delivered_count"]
                analytics["sequence_breakdown"][sequence_type]["opened"] += row["opened_count"]
                analytics["sequence_breakdown"][sequence_type]["clicked"] += row["clicked_count"]
                
                # Overall totals
                total_scheduled += row["total_scheduled"]
                total_delivered += row["delivered_count"]
                total_opened += row["opened_count"]
                total_clicked += row["clicked_count"]
            
            # Calculate overall metrics
            analytics["total_deliveries"] = total_scheduled
            analytics["overall_metrics"]["delivery_rate"] = round(
                (total_delivered / total_scheduled * 100) if total_scheduled > 0 else 0, 2
            )
            analytics["overall_metrics"]["open_rate"] = round(
                (total_opened / total_delivered * 100) if total_delivered > 0 else 0, 2
            )
            analytics["overall_metrics"]["click_rate"] = round(
                (total_clicked / total_opened * 100) if total_opened > 0 else 0, 2
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting sequence analytics: {e}")
            return {"error": str(e)}
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferred_channel: Optional[DeliveryChannel] = None,
        email_preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update user delivery preferences"""
        try:
            updated = False
            
            # Update sequence state preference
            if preferred_channel:
                self.supabase.table("user_sequence_state").update({
                    "preferred_channel": preferred_channel.value
                }).eq("user_id", user_id).eq("is_active", True).execute()
                updated = True
            
            # Update email preferences
            if email_preferences:
                self.supabase.table("user_email_preferences").upsert({
                    "user_id": user_id,
                    **email_preferences,
                    "updated_at": datetime.now().isoformat()
                }).execute()
                updated = True
            
            if updated:
                logger.info(f"✅ Updated preferences for user {user_id}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False


# Command line interface for testing
async def main():
    """Test the unified nurture controller"""
    import argparse
    from telbot import Config
    from supabase import create_client
    
    parser = argparse.ArgumentParser(description="Unified Nurture Controller Test")
    parser.add_argument('--user-id', type=str, help='User ID to test with')
    parser.add_argument('--sequence', type=str, help='Sequence type to trigger')
    parser.add_argument('--analytics', action='store_true', help='Show analytics')
    
    args = parser.parse_args()
    
    # Initialize
    config = Config()
    supabase = create_client(config.supabase_url, config.supabase_key)
    controller = UnifiedNurtureController(supabase)
    
    if args.analytics:
        analytics = await controller.get_sequence_analytics()
        print("Nurture Sequence Analytics:")
        print("=" * 50)
        print(json.dumps(analytics, indent=2))
    
    elif args.user_id and args.sequence:
        sequence_type = SequenceType(args.sequence)
        success = await controller.trigger_sequence(args.user_id, sequence_type)
        print(f"Sequence trigger result: {success}")
    
    else:
        print("Processing pending deliveries...")
        stats = await controller.process_pending_deliveries()
        print(f"Delivery stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())