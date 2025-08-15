#!/usr/bin/env python3
"""
Safety Controls - Prevent accidental communication to real users
All external communications must be explicitly authorized by Thomas
"""

import os
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class CommunicationChannel(Enum):
    EMAIL = "email"
    CALENDAR_INVITE = "calendar_invite"
    TELEGRAM = "telegram"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    WEBHOOK = "webhook"

class SafetyMode(Enum):
    DEVELOPMENT = "development"  # Only send to authorized test accounts
    STAGING = "staging"         # Send to whitelist only
    PRODUCTION = "production"   # Full send capability (requires explicit enable)

class SafetyControls:
    """Centralized safety controls to prevent accidental user communications"""
    
    def __init__(self):
        # Get environment settings
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        
        # Determine safety mode
        if self.environment == 'production' and not self.debug:
            self.safety_mode = SafetyMode.PRODUCTION
        elif self.environment == 'staging':
            self.safety_mode = SafetyMode.STAGING
        else:
            self.safety_mode = SafetyMode.DEVELOPMENT
        
        # Authorized recipients (only these can receive communications)
        self.authorized_emails = {
            'thomas@theprogressmethod.com',
            'test@theprogressmethod.com',
            'demo@theprogressmethod.com',
            'dev@theprogressmethod.com'
        }
        
        # Communication blocking - override for absolute safety
        self.communications_enabled = {
            CommunicationChannel.EMAIL: False,
            CommunicationChannel.CALENDAR_INVITE: True,  # Only to authorized emails
            CommunicationChannel.TELEGRAM: False,
            CommunicationChannel.SMS: False,
            CommunicationChannel.PUSH_NOTIFICATION: False,
            CommunicationChannel.WEBHOOK: False
        }
        
        # Production safety lock - must be explicitly enabled
        self.production_communications_enabled = os.getenv('ENABLE_PRODUCTION_COMMUNICATIONS', 'false').lower() == 'true'
        
        logger.info(f"🔒 Safety Controls initialized")
        logger.info(f"   Environment: {self.environment}")
        logger.info(f"   Safety Mode: {self.safety_mode.value}")
        logger.info(f"   Authorized emails: {len(self.authorized_emails)}")
        logger.info(f"   Production communications: {'enabled' if self.production_communications_enabled else 'BLOCKED'}")
    
    def is_email_authorized(self, email: str) -> bool:
        """Check if an email is authorized to receive communications"""
        return email.lower().strip() in {e.lower() for e in self.authorized_emails}
    
    def can_send_communication(self, channel: CommunicationChannel, recipient: str = None) -> tuple[bool, str]:
        """
        Check if a communication can be sent
        Returns (allowed: bool, reason: str)
        """
        
        # Check if channel is enabled
        if not self.communications_enabled.get(channel, False):
            return False, f"Channel {channel.value} is disabled in safety controls"
        
        # In production, require explicit enable
        if self.safety_mode == SafetyMode.PRODUCTION and not self.production_communications_enabled:
            return False, "Production communications are safety-locked (set ENABLE_PRODUCTION_COMMUNICATIONS=true to override)"
        
        # Check recipient authorization for email-based channels
        if channel in [CommunicationChannel.EMAIL, CommunicationChannel.CALENDAR_INVITE] and recipient:
            if not self.is_email_authorized(recipient):
                return False, f"Recipient {recipient} is not in authorized list"
        
        return True, "Communication allowed"
    
    def filter_authorized_recipients(self, emails: List[str]) -> List[str]:
        """Filter a list of emails to only include authorized ones"""
        authorized = [email for email in emails if self.is_email_authorized(email)]
        
        if len(authorized) != len(emails):
            blocked = [email for email in emails if not self.is_email_authorized(email)]
            logger.warning(f"🚫 Blocked {len(blocked)} unauthorized recipients: {blocked}")
        
        return authorized
    
    def log_communication_attempt(self, channel: CommunicationChannel, recipients: List[str], 
                                 allowed: bool, reason: str, details: Dict[str, Any] = None):
        """Log all communication attempts for audit trail"""
        
        log_entry = {
            'channel': channel.value,
            'recipients': recipients,
            'allowed': allowed,
            'reason': reason,
            'safety_mode': self.safety_mode.value,
            'environment': self.environment,
            'details': details or {}
        }
        
        if allowed:
            logger.info(f"✅ Communication sent: {channel.value} to {recipients}")
        else:
            logger.warning(f"🚫 Communication blocked: {reason}")
            logger.warning(f"   Channel: {channel.value}, Recipients: {recipients}")
    
    def safe_calendar_invite(self, attendee_emails: List[str]) -> tuple[List[str], List[str]]:
        """
        Safely filter calendar invite attendees
        Returns (authorized_emails, blocked_emails)
        """
        authorized = self.filter_authorized_recipients(attendee_emails)
        blocked = [email for email in attendee_emails if email not in authorized]
        
        self.log_communication_attempt(
            CommunicationChannel.CALENDAR_INVITE,
            attendee_emails,
            len(blocked) == 0,
            f"Filtered {len(blocked)} unauthorized attendees" if blocked else "All attendees authorized",
            {'authorized': len(authorized), 'blocked': len(blocked)}
        )
        
        return authorized, blocked
    
    def require_explicit_approval(self, channel: CommunicationChannel, recipients: List[str], 
                                message_preview: str = "") -> bool:
        """
        For development - require explicit approval for any external communication
        In a real system, this would prompt the user or require a confirmation step
        """
        
        print(f"\n🚨 COMMUNICATION APPROVAL REQUIRED")
        print(f"Channel: {channel.value}")
        print(f"Recipients: {recipients}")
        if message_preview:
            print(f"Message Preview: {message_preview[:100]}...")
        print(f"Environment: {self.environment} ({self.safety_mode.value})")
        print(f"\nThis communication is blocked pending explicit approval.")
        
        return False  # Always block in development unless explicitly overridden
    
    def get_test_email(self) -> str:
        """Get a safe test email for development"""
        return "thomas@theprogressmethod.com"
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety control status"""
        return {
            'environment': self.environment,
            'safety_mode': self.safety_mode.value,
            'authorized_emails': list(self.authorized_emails),
            'communications_enabled': {k.value: v for k, v in self.communications_enabled.items()},
            'production_enabled': self.production_communications_enabled
        }

# Global safety controls instance
safety_controls = SafetyControls()

def safe_send_email(recipients: List[str], subject: str, body: str) -> bool:
    """Safe email sending with authorization checks"""
    authorized, blocked = safety_controls.safe_calendar_invite(recipients)
    
    if blocked:
        logger.error(f"🚫 EMAIL BLOCKED - Unauthorized recipients: {blocked}")
        return False
    
    allowed, reason = safety_controls.can_send_communication(CommunicationChannel.EMAIL)
    if not allowed:
        logger.error(f"🚫 EMAIL BLOCKED - {reason}")
        return False
    
    # In development, always require approval
    if safety_controls.safety_mode == SafetyMode.DEVELOPMENT:
        return safety_controls.require_explicit_approval(
            CommunicationChannel.EMAIL, 
            authorized, 
            f"{subject}: {body[:50]}..."
        )
    
    # Would implement actual email sending here
    logger.info(f"📧 Email would be sent to: {authorized}")
    return True

def safe_send_calendar_invite(attendee_emails: List[str], event_details: Dict[str, Any]) -> tuple[List[str], bool]:
    """Safe calendar invite sending with authorization checks"""
    authorized, blocked = safety_controls.safe_calendar_invite(attendee_emails)
    
    allowed, reason = safety_controls.can_send_communication(CommunicationChannel.CALENDAR_INVITE)
    if not allowed:
        logger.error(f"🚫 CALENDAR INVITE BLOCKED - {reason}")
        return [], False
    
    return authorized, True

if __name__ == "__main__":
    # Test safety controls
    print("🧪 Testing Safety Controls")
    print("=" * 30)
    
    controls = SafetyControls()
    status = controls.get_safety_status()
    
    print(f"Environment: {status['environment']}")
    print(f"Safety Mode: {status['safety_mode']}")
    print(f"Authorized Emails: {status['authorized_emails']}")
    print(f"Calendar Invites: {'Enabled' if status['communications_enabled']['calendar_invite'] else 'Disabled'}")
    
    # Test email filtering
    test_emails = [
        "thomas@theprogressmethod.com",
        "user@gmail.com",
        "test@theprogressmethod.com",
        "random@company.com"
    ]
    
    authorized, blocked = controls.safe_calendar_invite(test_emails)
    print(f"\nTest Email Filtering:")
    print(f"  Authorized: {authorized}")
    print(f"  Blocked: {blocked}")