#!/usr/bin/env python3
"""
Progress Method - Alerting and Notifications System
Smart alerting, notifications, and automated responses
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from supabase import Client

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class NotificationChannel(Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"
    SLACK = "slack"
    LOG = "log"

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    metric_id: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class NotificationRule:
    id: str
    name: str
    conditions: Dict[str, Any]
    channels: List[NotificationChannel]
    severity_threshold: AlertSeverity
    cooldown_minutes: int = 60
    enabled: bool = True
    recipients: List[str] = None
    template: Optional[str] = None
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []

@dataclass
class NotificationHistory:
    alert_id: str
    channel: NotificationChannel
    recipient: str
    sent_at: datetime
    success: bool
    error_message: Optional[str] = None

class AlertingSystem:
    """Smart alerting and notification system for Progress Method"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.active_alerts = {}
        self.notification_rules = []
        self.notification_history = []
        self.alert_handlers = {}
        self.setup_default_rules()
        
    def setup_default_rules(self):
        """Setup default notification rules for Progress Method"""
        
        # System Health Alerts
        self.notification_rules.extend([
            NotificationRule(
                id="system_critical",
                name="System Critical Alerts",
                conditions={"severity": "critical", "category": "system"},
                channels=[NotificationChannel.EMAIL, NotificationChannel.LOG],
                severity_threshold=AlertSeverity.CRITICAL,
                cooldown_minutes=30,
                recipients=["admin@progressmethod.com"],
                template="system_critical"
            ),
            NotificationRule(
                id="user_engagement_warning",
                name="Low User Engagement",
                conditions={"metric_id": "dau", "threshold_breach": "below"},
                channels=[NotificationChannel.EMAIL, NotificationChannel.LOG],
                severity_threshold=AlertSeverity.WARNING,
                cooldown_minutes=120,
                recipients=["admin@progressmethod.com"],
                template="engagement_warning"
            ),
            NotificationRule(
                id="ai_system_failure",
                name="AI System Failure",
                conditions={"metric_id": "ai_success_rate", "current_value": {"lt": 60}},
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                severity_threshold=AlertSeverity.CRITICAL,
                cooldown_minutes=60,
                recipients=["admin@progressmethod.com"],
                template="ai_failure"
            ),
            NotificationRule(
                id="business_kpi_degradation",
                name="Business KPI Degradation",
                conditions={"category": "business", "trend": "down", "percentage": {"lt": -20}},
                channels=[NotificationChannel.EMAIL],
                severity_threshold=AlertSeverity.WARNING,
                cooldown_minutes=240,  # 4 hours
                recipients=["admin@progressmethod.com"],
                template="business_alert"
            )
        ])
    
    async def process_metrics_for_alerts(self, metrics: List[Dict[str, Any]]) -> List[Alert]:
        """Process metrics and generate alerts based on thresholds"""
        new_alerts = []
        
        try:
            for metric in metrics:
                alerts = await self._check_metric_thresholds(metric)
                new_alerts.extend(alerts)
            
            # Check for pattern-based alerts
            pattern_alerts = await self._check_pattern_alerts(metrics)
            new_alerts.extend(pattern_alerts)
            
            # Process new alerts
            for alert in new_alerts:
                await self._process_alert(alert)
                
            return new_alerts
            
        except Exception as e:
            logger.error(f"❌ Error processing metrics for alerts: {e}")
            return []
    
    async def _check_metric_thresholds(self, metric: Dict[str, Any]) -> List[Alert]:
        """Check individual metric against thresholds"""
        alerts = []
        
        try:
            metric_id = metric.get("id")
            current_value = metric.get("value", 0)
            threshold_warning = metric.get("threshold_warning")
            threshold_critical = metric.get("threshold_critical")
            metric_name = metric.get("name", metric_id)
            
            # Check critical threshold
            if threshold_critical and current_value >= threshold_critical:
                alert = Alert(
                    id=f"{metric_id}_critical_{datetime.now().timestamp()}",
                    title=f"Critical: {metric_name}",
                    description=f"{metric_name} has reached critical threshold. Current value: {current_value}, Threshold: {threshold_critical}",
                    severity=AlertSeverity.CRITICAL,
                    status=AlertStatus.ACTIVE,
                    source="metric_monitor",
                    metric_id=metric_id,
                    threshold_value=threshold_critical,
                    current_value=current_value,
                    metadata={"metric": metric, "threshold_type": "critical"}
                )
                alerts.append(alert)
                
            # Check warning threshold
            elif threshold_warning and current_value >= threshold_warning:
                alert = Alert(
                    id=f"{metric_id}_warning_{datetime.now().timestamp()}",
                    title=f"Warning: {metric_name}",
                    description=f"{metric_name} has reached warning threshold. Current value: {current_value}, Threshold: {threshold_warning}",
                    severity=AlertSeverity.WARNING,
                    status=AlertStatus.ACTIVE,
                    source="metric_monitor",
                    metric_id=metric_id,
                    threshold_value=threshold_warning,
                    current_value=current_value,
                    metadata={"metric": metric, "threshold_type": "warning"}
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking metric thresholds: {e}")
            
        return alerts
    
    async def _check_pattern_alerts(self, metrics: List[Dict[str, Any]]) -> List[Alert]:
        """Check for pattern-based alerts across multiple metrics"""
        alerts = []
        
        try:
            # System Health Pattern: Multiple systems degraded
            degraded_systems = [m for m in metrics if m.get("severity") == "critical"]
            if len(degraded_systems) >= 3:
                alert = Alert(
                    id=f"system_degradation_{datetime.now().timestamp()}",
                    title="Multiple System Degradation",
                    description=f"Multiple critical systems detected: {len(degraded_systems)} components affected",
                    severity=AlertSeverity.EMERGENCY,
                    status=AlertStatus.ACTIVE,
                    source="pattern_detector",
                    metadata={"degraded_systems": [m.get("id") for m in degraded_systems]}
                )
                alerts.append(alert)
            
            # User Engagement Pattern: Low engagement across multiple metrics
            engagement_metrics = [m for m in metrics if m.get("tags", {}).get("category") == "engagement"]
            low_engagement = [m for m in engagement_metrics if m.get("severity") in ["warning", "critical"]]
            
            if len(low_engagement) >= 2:
                alert = Alert(
                    id=f"engagement_pattern_{datetime.now().timestamp()}",
                    title="User Engagement Decline",
                    description="Multiple user engagement metrics showing decline",
                    severity=AlertSeverity.WARNING,
                    status=AlertStatus.ACTIVE,
                    source="pattern_detector",
                    metadata={"affected_metrics": [m.get("id") for m in low_engagement]}
                )
                alerts.append(alert)
            
            # Business Impact Pattern: Core business metrics degraded
            business_metrics = [m for m in metrics if m.get("tags", {}).get("category") == "business"]
            critical_business = [m for m in business_metrics if m.get("severity") == "critical"]
            
            if critical_business:
                alert = Alert(
                    id=f"business_impact_{datetime.now().timestamp()}",
                    title="Business Impact Alert",
                    description="Critical business metrics degraded, immediate attention required",
                    severity=AlertSeverity.CRITICAL,
                    status=AlertStatus.ACTIVE,
                    source="pattern_detector",
                    metadata={"business_metrics": [m.get("id") for m in critical_business]}
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error checking pattern alerts: {e}")
            
        return alerts
    
    async def _process_alert(self, alert: Alert):
        """Process a new alert through notification rules"""
        try:
            # Store alert
            self.active_alerts[alert.id] = alert
            
            # Find matching notification rules
            matching_rules = self._find_matching_rules(alert)
            
            # Send notifications
            for rule in matching_rules:
                if self._should_send_notification(alert, rule):
                    await self._send_notifications(alert, rule)
                    
        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {e}")
    
    def _find_matching_rules(self, alert: Alert) -> List[NotificationRule]:
        """Find notification rules that match the alert"""
        matching_rules = []
        
        for rule in self.notification_rules:
            if not rule.enabled:
                continue
                
            # Check severity threshold
            severity_levels = {
                AlertSeverity.INFO: 0,
                AlertSeverity.WARNING: 1,
                AlertSeverity.CRITICAL: 2,
                AlertSeverity.EMERGENCY: 3
            }
            
            if severity_levels[alert.severity] < severity_levels[rule.severity_threshold]:
                continue
            
            # Check conditions
            conditions_match = True
            for condition_key, condition_value in rule.conditions.items():
                if condition_key == "severity" and alert.severity.value != condition_value:
                    conditions_match = False
                    break
                elif condition_key == "metric_id" and alert.metric_id != condition_value:
                    conditions_match = False
                    break
                elif condition_key == "category":
                    metric_category = alert.metadata.get("metric", {}).get("tags", {}).get("category")
                    if metric_category != condition_value:
                        conditions_match = False
                        break
            
            if conditions_match:
                matching_rules.append(rule)
                
        return matching_rules
    
    def _should_send_notification(self, alert: Alert, rule: NotificationRule) -> bool:
        """Check if notification should be sent based on cooldown and other factors"""
        
        # Check cooldown
        cooldown_key = f"{rule.id}_{alert.metric_id or alert.source}"
        recent_notifications = [
            n for n in self.notification_history
            if n.alert_id.startswith(cooldown_key) and 
            n.sent_at > datetime.now() - timedelta(minutes=rule.cooldown_minutes)
        ]
        
        if recent_notifications:
            logger.info(f"Notification suppressed due to cooldown: {rule.name}")
            return False
            
        return True
    
    async def _send_notifications(self, alert: Alert, rule: NotificationRule):
        """Send notifications through specified channels"""
        
        for channel in rule.channels:
            for recipient in rule.recipients:
                try:
                    success = await self._send_notification(alert, rule, channel, recipient)
                    
                    # Record notification history
                    history = NotificationHistory(
                        alert_id=alert.id,
                        channel=channel,
                        recipient=recipient,
                        sent_at=datetime.now(),
                        success=success
                    )
                    self.notification_history.append(history)
                    
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.value} to {recipient}: {e}")
                    
                    history = NotificationHistory(
                        alert_id=alert.id,
                        channel=channel,
                        recipient=recipient,
                        sent_at=datetime.now(),
                        success=False,
                        error_message=str(e)
                    )
                    self.notification_history.append(history)
    
    async def _send_notification(self, alert: Alert, rule: NotificationRule, channel: NotificationChannel, recipient: str) -> bool:
        """Send individual notification"""
        
        try:
            if channel == NotificationChannel.LOG:
                return await self._send_log_notification(alert, recipient)
            elif channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(alert, rule, recipient)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(alert, recipient)
            elif channel == NotificationChannel.TELEGRAM:
                return await self._send_telegram_notification(alert, recipient)
            else:
                logger.warning(f"Unsupported notification channel: {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending {channel.value} notification: {e}")
            return False
    
    async def _send_log_notification(self, alert: Alert, recipient: str) -> bool:
        """Send notification via logging"""
        try:
            log_level = logging.ERROR if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] else logging.WARNING
            logger.log(log_level, f"🚨 ALERT: {alert.title} - {alert.description}")
            return True
        except Exception as e:
            logger.error(f"Failed to send log notification: {e}")
            return False
    
    async def _send_email_notification(self, alert: Alert, rule: NotificationRule, recipient: str) -> bool:
        """Send notification via email"""
        try:
            # For now, just log that email would be sent
            # In production, you'd configure SMTP settings
            logger.info(f"📧 EMAIL ALERT to {recipient}: {alert.title}")
            logger.info(f"   Subject: [Progress Method Alert] {alert.title}")
            logger.info(f"   Body: {alert.description}")
            
            # Placeholder for actual email sending
            # from email.mime.multipart import MimeMultipart
            # from email.mime.text import MimeText
            # msg = MimeMultipart()
            # msg['From'] = "alerts@progressmethod.com"
            # msg['To'] = recipient
            # msg['Subject'] = f"[Progress Method Alert] {alert.title}"
            # body = self._generate_email_body(alert, rule.template)
            # msg.attach(MimeText(body, 'html'))
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    async def _send_webhook_notification(self, alert: Alert, webhook_url: str) -> bool:
        """Send notification via webhook"""
        try:
            import aiohttp
            
            payload = {
                "alert": asdict(alert),
                "timestamp": datetime.now().isoformat(),
                "source": "progress_method_monitoring"
            }
            
            # For now, just log the webhook payload
            logger.info(f"🔗 WEBHOOK to {webhook_url}: {json.dumps(payload, indent=2, default=str)}")
            
            # Placeholder for actual webhook sending
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(webhook_url, json=payload) as response:
            #         return response.status == 200
            
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    async def _send_telegram_notification(self, alert: Alert, chat_id: str) -> bool:
        """Send notification via Telegram"""
        try:
            # For now, just log that Telegram message would be sent
            message = f"🚨 *{alert.title}*\n\n{alert.description}\n\nSeverity: {alert.severity.value}\nTime: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            logger.info(f"📱 TELEGRAM to {chat_id}: {message}")
            
            # Placeholder for actual Telegram sending via bot
            # bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            # if bot_token:
            #     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            #     payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
            #     # Send HTTP request...
            
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def _generate_email_body(self, alert: Alert, template: Optional[str]) -> str:
        """Generate email body from template"""
        
        if template == "system_critical":
            return f"""
            <html>
            <body>
                <h2 style="color: #e74c3c;">🚨 Critical System Alert</h2>
                <p><strong>Alert:</strong> {alert.title}</p>
                <p><strong>Description:</strong> {alert.description}</p>
                <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
                <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                
                {f'<p><strong>Current Value:</strong> {alert.current_value}</p>' if alert.current_value else ''}
                {f'<p><strong>Threshold:</strong> {alert.threshold_value}</p>' if alert.threshold_value else ''}
                
                <hr>
                <p><em>This alert was generated by Progress Method Monitoring System</em></p>
            </body>
            </html>
            """
        else:
            # Default template
            return f"""
            <html>
            <body>
                <h2>📊 Progress Method Alert</h2>
                <p><strong>{alert.title}</strong></p>
                <p>{alert.description}</p>
                <p>Severity: {alert.severity.value}</p>
                <p>Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </body>
            </html>
            """
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.updated_at = datetime.now()
                
                logger.info(f"✅ Alert acknowledged: {alert.title} by {acknowledged_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                alert.updated_at = datetime.now()
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                logger.info(f"✅ Alert resolved: {alert.title} by {resolved_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        try:
            return [asdict(alert) for alert in self.active_alerts.values()]
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary and statistics"""
        try:
            active_alerts = list(self.active_alerts.values())
            
            # Count by severity
            severity_counts = {"info": 0, "warning": 0, "critical": 0, "emergency": 0}
            for alert in active_alerts:
                severity_counts[alert.severity.value] += 1
            
            # Recent notification stats
            recent_notifications = [
                n for n in self.notification_history 
                if n.sent_at > datetime.now() - timedelta(hours=24)
            ]
            
            return {
                "active_alerts_count": len(active_alerts),
                "severity_breakdown": severity_counts,
                "recent_notifications_24h": len(recent_notifications),
                "notification_success_rate": sum(1 for n in recent_notifications if n.success) / len(recent_notifications) * 100 if recent_notifications else 100,
                "active_rules_count": len([r for r in self.notification_rules if r.enabled]),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting alert summary: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Alerting System - Use AlertingSystem class for Progress Method notifications")