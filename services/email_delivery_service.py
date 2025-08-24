#!/usr/bin/env python3
"""
Email Delivery Service with Resend Integration
Phase 2: Multi-channel nurture sequence delivery
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import httpx
import json
import uuid
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EmailEventType(Enum):
    """Email event types from Resend webhooks"""
    SENT = "email.sent"
    DELIVERED = "email.delivered"
    BOUNCE = "email.bounced"
    COMPLAINT = "email.complained"
    OPEN = "email.opened"
    CLICK = "email.clicked"

@dataclass
class EmailTemplate:
    """Email template configuration"""
    template_id: str
    subject_template: str
    html_template: str
    text_template: str
    template_variables: List[str]

class EmailDeliveryService:
    """
    Email delivery service using Resend API with tracking and personalization
    """
    
    def __init__(self, api_key: str, from_email: str = "noreply@progressmethod.com"):
        self.api_key = api_key
        self.from_email = from_email
        self.base_url = "https://api.resend.com"
        self.supabase = None  # Will be injected
        
        # Email templates for nurture sequences
        self.templates = self._define_email_templates()
        
        logger.info("📧 Email Delivery Service initialized")
    
    def set_supabase_client(self, supabase_client):
        """Inject Supabase client for tracking"""
        self.supabase = supabase_client
        logger.info("🔗 Supabase client connected to email service")
    
    def _define_email_templates(self) -> Dict[str, EmailTemplate]:
        """Define email templates for different sequence types"""
        return {
            "nurture_sequence": EmailTemplate(
                template_id="nurture_sequence",
                subject_template="Your Progress Method Update - {subject_line}",
                html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Progress Method</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .content {{ padding: 30px 20px; }}
        .message {{ font-size: 16px; color: #374151; margin-bottom: 20px; white-space: pre-line; }}
        .cta {{ text-align: center; margin: 30px 0; }}
        .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
        .footer a {{ color: #667eea; text-decoration: none; }}
        .unsubscribe {{ margin-top: 20px; font-size: 12px; color: #9ca3af; }}
        .tracking-pixel {{ width: 1px; height: 1px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>The Progress Method</h1>
            <p>Your journey to meaningful progress</p>
        </div>
        
        <div class="content">
            <p>Hi {user_name},</p>
            
            <div class="message">{message_content}</div>
            
            {cta_section}
        </div>
        
        <div class="footer">
            <p>Keep making progress! 🚀</p>
            <p><a href="{dashboard_url}">View your progress dashboard</a></p>
            
            <div class="unsubscribe">
                <p>Don't want these emails? <a href="{unsubscribe_url}">Unsubscribe here</a></p>
                <p>The Progress Method | Building dreams through daily commitments</p>
            </div>
        </div>
    </div>
    
    <!-- Tracking pixel -->
    <img src="{tracking_url}" class="tracking-pixel" alt="" />
</body>
</html>
                """,
                text_template="""
Hi {user_name},

{message_content}

{cta_text}

Keep making progress!
The Progress Method Team

---
Don't want these emails? Unsubscribe: {unsubscribe_url}
View your dashboard: {dashboard_url}
                """,
                template_variables=["user_name", "message_content", "cta_section", "cta_text", "dashboard_url", "unsubscribe_url", "tracking_url", "subject_line"]
            ),
            
            "welcome_email": EmailTemplate(
                template_id="welcome_email",
                subject_template="Welcome to The Progress Method! 🚀",
                html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to The Progress Method</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 40px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; }}
        .content {{ padding: 40px 20px; }}
        .welcome-message {{ font-size: 18px; color: #374151; margin-bottom: 30px; text-align: center; }}
        .features {{ margin: 30px 0; }}
        .feature {{ display: flex; align-items: center; margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 6px; }}
        .feature-icon {{ font-size: 24px; margin-right: 15px; }}
        .feature-text {{ flex: 1; }}
        .cta {{ text-align: center; margin: 40px 0; }}
        .cta-button {{ display: inline-block; background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 18px; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome, {user_name}!</h1>
            <p>You're about to transform how you make progress</p>
        </div>
        
        <div class="content">
            <div class="welcome-message">
                <p><strong>Congratulations on taking the first step!</strong></p>
                <p>You've joined thousands of people who are turning their dreams into reality through small, consistent commitments.</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">📱</div>
                    <div class="feature-text">
                        <strong>Daily Commitments</strong><br>
                        Make small, achievable commitments that build momentum over time
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">👥</div>
                    <div class="feature-text">
                        <strong>Pod Support</strong><br>
                        Join a weekly accountability group to stay motivated and supported
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <div class="feature-text">
                        <strong>Progress Tracking</strong><br>
                        See your streaks, celebrate wins, and learn from patterns
                    </div>
                </div>
            </div>
            
            <div class="cta">
                <a href="{dashboard_url}" class="cta-button">Start Your First Commitment</a>
            </div>
            
            <p style="text-align: center; color: #6b7280; margin-top: 30px;">
                Need help getting started? Just reply to this email - we're here to support you! 💙
            </p>
        </div>
        
        <div class="footer">
            <p>The Progress Method | Building dreams through daily commitments</p>
            <p><a href="{unsubscribe_url}">Unsubscribe</a> | <a href="{dashboard_url}">Dashboard</a></p>
        </div>
    </div>
    
    <img src="{tracking_url}" style="width:1px;height:1px;" alt="" />
</body>
</html>
                """,
                text_template="""
🎉 Welcome to The Progress Method, {user_name}!

Congratulations on taking the first step! You've joined thousands of people who are turning their dreams into reality through small, consistent commitments.

What you can do:
📱 Make daily commitments that build momentum
👥 Join a pod for weekly accountability 
📊 Track your progress and celebrate wins

Ready to start? {dashboard_url}

Need help? Just reply to this email - we're here to support you! 💙

The Progress Method Team

---
Unsubscribe: {unsubscribe_url}
                """,
                template_variables=["user_name", "dashboard_url", "unsubscribe_url", "tracking_url"]
            )
        }
    
    async def send_nurture_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        user_name: str = "Friend",
        template_type: str = "nurture_sequence",
        tracking_id: Optional[str] = None,
        cta_text: Optional[str] = None,
        cta_url: Optional[str] = None
    ) -> bool:
        """Send a nurture sequence email"""
        
        try:
            # Generate tracking ID if not provided
            if not tracking_id:
                tracking_id = str(uuid.uuid4())
            
            # Get template
            template = self.templates.get(template_type, self.templates["nurture_sequence"])
            
            # Prepare template variables
            base_url = "https://progressmethod.com"  # Configure this
            template_vars = {
                "user_name": user_name,
                "message_content": content,
                "subject_line": subject,
                "dashboard_url": f"{base_url}/dashboard",
                "unsubscribe_url": f"{base_url}/unsubscribe?token={tracking_id}",
                "tracking_url": f"{base_url}/api/email/track/{tracking_id}",
                "cta_section": self._generate_cta_section(cta_text, cta_url) if cta_text else "",
                "cta_text": f"\n{cta_text}: {cta_url}\n" if cta_text else ""
            }
            
            # Render templates
            html_content = template.html_template.format(**template_vars)
            text_content = template.text_template.format(**template_vars)
            email_subject = template.subject_template.format(**template_vars)
            
            # Send email via Resend
            success = await self._send_via_resend(
                to_email=to_email,
                subject=email_subject,
                html_content=html_content,
                text_content=text_content,
                tracking_id=tracking_id
            )
            
            if success:
                logger.info(f"✅ Nurture email sent to {to_email}")
                return True
            else:
                logger.error(f"❌ Failed to send nurture email to {to_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending nurture email: {e}")
            return False
    
    def _generate_cta_section(self, cta_text: str, cta_url: str) -> str:
        """Generate HTML CTA section"""
        if not cta_text or not cta_url:
            return ""
        
        return f"""
        <div class="cta">
            <a href="{cta_url}" class="cta-button">{cta_text}</a>
        </div>
        """
    
    async def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        tracking_id: str
    ) -> bool:
        """Send email via Resend API"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "tags": [
                    {"name": "category", "value": "nurture_sequence"},
                    {"name": "tracking_id", "value": tracking_id}
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    email_id = result.get("id")
                    
                    # Store email tracking info
                    if self.supabase:
                        await self._store_email_tracking(tracking_id, email_id, to_email)
                    
                    logger.debug(f"📧 Email sent via Resend: {email_id}")
                    return True
                else:
                    logger.error(f"Resend API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending via Resend: {e}")
            return False
    
    async def _store_email_tracking(self, tracking_id: str, email_id: str, recipient: str):
        """Store email tracking information"""
        try:
            if not self.supabase:
                return
            
            tracking_data = {
                "tracking_id": tracking_id,
                "email_id": email_id,
                "recipient": recipient,
                "sent_at": datetime.now().isoformat(),
                "metadata": json.dumps({"provider": "resend"})
            }
            
            # Update delivery record if it exists
            self.supabase.table("message_deliveries").update({
                "delivery_status": "sent",
                "sent_at": datetime.now().isoformat(),
                "tracking_id": tracking_id
            }).eq("tracking_id", tracking_id).execute()
            
        except Exception as e:
            logger.error(f"Error storing email tracking: {e}")
    
    async def handle_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        """Handle Resend webhook events"""
        try:
            event_type = event_data.get("type")
            data = event_data.get("data", {})
            
            # Extract tracking information
            tags = data.get("tags", [])
            tracking_id = None
            
            for tag in tags:
                if tag.get("name") == "tracking_id":
                    tracking_id = tag.get("value")
                    break
            
            if not tracking_id:
                logger.warning("No tracking ID found in webhook event")
                return False
            
            # Map Resend events to our event types
            event_mapping = {
                "email.sent": "sent",
                "email.delivered": "delivered", 
                "email.bounced": "bounced",
                "email.complained": "complaint",
                "email.opened": "opened",
                "email.clicked": "clicked"
            }
            
            mapped_event = event_mapping.get(event_type)
            if not mapped_event:
                logger.warning(f"Unknown event type: {event_type}")
                return False
            
            # Update delivery status
            await self._update_delivery_status(tracking_id, mapped_event, data)
            
            # Store email event
            await self._store_email_event(tracking_id, mapped_event, data)
            
            logger.info(f"📨 Processed email event: {event_type} for tracking ID {tracking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
            return False
    
    async def _update_delivery_status(self, tracking_id: str, event_type: str, event_data: Dict):
        """Update delivery status based on event"""
        try:
            if not self.supabase:
                return
            
            update_data = {
                "updated_at": datetime.now().isoformat()
            }
            
            if event_type == "delivered":
                update_data["delivery_status"] = "delivered"
                update_data["delivered_at"] = datetime.now().isoformat()
            elif event_type == "opened":
                update_data["delivery_status"] = "opened"
                update_data["opened_at"] = datetime.now().isoformat()
            elif event_type == "clicked":
                update_data["delivery_status"] = "clicked"
                update_data["clicked_at"] = datetime.now().isoformat()
            elif event_type in ["bounced", "complaint"]:
                update_data["delivery_status"] = "failed"
                update_data["failed_at"] = datetime.now().isoformat()
                update_data["failure_reason"] = f"Email {event_type}"
            
            self.supabase.table("message_deliveries").update(update_data).eq(
                "tracking_id", tracking_id
            ).execute()
            
        except Exception as e:
            logger.error(f"Error updating delivery status: {e}")
    
    async def _store_email_event(self, tracking_id: str, event_type: str, event_data: Dict):
        """Store detailed email event"""
        try:
            if not self.supabase:
                return
            
            # Get delivery ID
            delivery_result = self.supabase.table("message_deliveries").select("id").eq(
                "tracking_id", tracking_id
            ).execute()
            
            if not delivery_result.data:
                logger.warning(f"No delivery found for tracking ID: {tracking_id}")
                return
            
            delivery_id = delivery_result.data[0]["id"]
            
            event_record = {
                "delivery_id": delivery_id,
                "event_type": event_type,
                "event_time": datetime.now().isoformat(),
                "event_data": json.dumps(event_data),
                "user_agent": event_data.get("user_agent"),
                "ip_address": event_data.get("ip_address")
            }
            
            self.supabase.table("email_events").insert(event_record).execute()
            
        except Exception as e:
            logger.error(f"Error storing email event: {e}")
    
    async def send_welcome_email(self, user_id: str, email_address: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        try:
            tracking_id = str(uuid.uuid4())
            
            success = await self.send_nurture_email(
                to_email=email_address,
                subject="Welcome to The Progress Method! 🚀",
                content="Welcome to your journey of meaningful progress!",
                user_name=user_name,
                template_type="welcome_email",
                tracking_id=tracking_id,
                cta_text="Start Your First Commitment",
                cta_url="https://progressmethod.com/dashboard"
            )
            
            if success and self.supabase:
                # Store welcome email record
                self.supabase.table("message_deliveries").insert({
                    "user_id": user_id,
                    "sequence_type": "welcome",
                    "message_step": 0,
                    "channel": "email",
                    "delivery_status": "sent",
                    "recipient_address": email_address,
                    "message_content": "Welcome email",
                    "scheduled_at": datetime.now().isoformat(),
                    "sent_at": datetime.now().isoformat(),
                    "tracking_id": tracking_id
                }).execute()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False
    
    async def verify_email_address(self, user_id: str, email_address: str) -> bool:
        """Send email verification message"""
        try:
            verification_token = str(uuid.uuid4())
            
            # Store verification request
            if self.supabase:
                self.supabase.table("user_email_preferences").upsert({
                    "user_id": user_id,
                    "email_address": email_address,
                    "is_verified": False,
                    "verification_token": verification_token,
                    "verification_sent_at": datetime.now().isoformat()
                }).execute()
            
            # Send verification email
            verification_url = f"https://progressmethod.com/verify-email?token={verification_token}"
            
            html_content = f"""
            <h2>Verify your email address</h2>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>If you didn't request this, you can safely ignore this email.</p>
            """
            
            text_content = f"""
            Verify your email address
            
            Please visit this link to verify your email address:
            {verification_url}
            
            If you didn't request this, you can safely ignore this email.
            """
            
            success = await self._send_via_resend(
                to_email=email_address,
                subject="Verify your email address - The Progress Method",
                html_content=html_content,
                text_content=text_content,
                tracking_id=verification_token
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False
    
    async def get_delivery_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get email delivery statistics"""
        try:
            if not self.supabase:
                return {"error": "Database not connected"}
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get email deliveries
            result = self.supabase.table("message_deliveries").select("*").eq(
                "channel", "email"
            ).gte("scheduled_at", cutoff_date).execute()
            
            deliveries = result.data
            
            stats = {
                "period_days": days,
                "total_scheduled": len(deliveries),
                "sent": len([d for d in deliveries if d["delivery_status"] in ["sent", "delivered", "opened", "clicked"]]),
                "delivered": len([d for d in deliveries if d["delivery_status"] in ["delivered", "opened", "clicked"]]),
                "opened": len([d for d in deliveries if d["delivery_status"] in ["opened", "clicked"]]),
                "clicked": len([d for d in deliveries if d["delivery_status"] == "clicked"]),
                "bounced": len([d for d in deliveries if d["delivery_status"] == "failed" and "bounce" in d.get("failure_reason", "").lower()]),
                "failed": len([d for d in deliveries if d["delivery_status"] == "failed"])
            }
            
            # Calculate rates
            stats["delivery_rate"] = round((stats["delivered"] / stats["sent"] * 100) if stats["sent"] > 0 else 0, 2)
            stats["open_rate"] = round((stats["opened"] / stats["delivered"] * 100) if stats["delivered"] > 0 else 0, 2)
            stats["click_rate"] = round((stats["clicked"] / stats["opened"] * 100) if stats["opened"] > 0 else 0, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting delivery stats: {e}")
            return {"error": str(e)}


# Test and CLI interface
async def main():
    """Test the email delivery service"""
    import argparse
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Email Delivery Service Test")
    parser.add_argument('--test-email', type=str, help='Email address to test with')
    parser.add_argument('--stats', action='store_true', help='Show delivery stats')
    
    args = parser.parse_args()
    
    # Initialize service
    api_key = os.getenv("RESEND_API_KEY", "re_eCPQhpxD_BiGA5QnXDALpz1qNUn43THqf")
    service = EmailDeliveryService(api_key)
    
    if args.stats:
        stats = await service.get_delivery_stats()
        print("Email Delivery Stats:")
        print("=" * 30)
        print(json.dumps(stats, indent=2))
    
    elif args.test_email:
        success = await service.send_nurture_email(
            to_email=args.test_email,
            subject="Test",
            content="This is a test message from the enhanced nurture system!",
            user_name="Test User"
        )
        print(f"Test email result: {success}")
    
    else:
        print("Email Delivery Service initialized successfully")
        print("Use --test-email to send a test email")
        print("Use --stats to view delivery statistics")

if __name__ == "__main__":
    asyncio.run(main())