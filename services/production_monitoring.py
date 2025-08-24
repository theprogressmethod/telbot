#!/usr/bin/env python3
"""
Production Bot Monitoring System
Ensures @ProgressMethodBot never goes down
"""

import asyncio
import aiohttp
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BotHealth:
    """Bot health status"""
    is_healthy: bool
    webhook_status: str
    pending_updates: int
    last_error: Optional[str]
    response_time: float
    timestamp: datetime

class ProductionBotMonitor:
    """Monitor production bot health and auto-recover"""
    
    def __init__(self):
        self.bot_token = "8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0"
        self.webhook_url = "https://telbot-f4on.onrender.com/webhook"
        self.server_url = "https://telbot-f4on.onrender.com"
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Health thresholds
        self.max_pending_updates = 5
        self.max_response_time = 10.0  # seconds
        self.health_check_interval = 60  # seconds
        
        # Recovery settings
        self.max_recovery_attempts = 3
        self.recovery_backoff = [60, 300, 900]  # 1min, 5min, 15min
        
    async def check_bot_health(self) -> BotHealth:
        """Comprehensive bot health check"""
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check Telegram API
                async with session.get(f"{self.telegram_api}/getMe") as resp:
                    if resp.status != 200:
                        return BotHealth(
                            is_healthy=False,
                            webhook_status="API_ERROR",
                            pending_updates=0,
                            last_error=f"Telegram API error: {resp.status}",
                            response_time=0,
                            timestamp=start_time
                        )
                
                # Check webhook info
                async with session.get(f"{self.telegram_api}/getWebhookInfo") as resp:
                    webhook_data = await resp.json()
                    webhook_info = webhook_data.get('result', {})
                    
                    pending_updates = webhook_info.get('pending_update_count', 0)
                    last_error = webhook_info.get('last_error_message')
                    webhook_url = webhook_info.get('url', '')
                    
                    # Check server health
                    try:
                        async with session.get(f"{self.server_url}/health", timeout=5) as server_resp:
                            server_healthy = server_resp.status == 200
                    except:
                        server_healthy = False
                    
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    is_healthy = (
                        pending_updates <= self.max_pending_updates and
                        response_time <= self.max_response_time and
                        server_healthy and
                        webhook_url == self.webhook_url and
                        not last_error
                    )
                    
                    return BotHealth(
                        is_healthy=is_healthy,
                        webhook_status="HEALTHY" if is_healthy else "UNHEALTHY",
                        pending_updates=pending_updates,
                        last_error=last_error,
                        response_time=response_time,
                        timestamp=start_time
                    )
                    
        except Exception as e:
            return BotHealth(
                is_healthy=False,
                webhook_status="CONNECTION_ERROR",
                pending_updates=0,
                last_error=str(e),
                response_time=999.0,
                timestamp=start_time
            )
    
    async def auto_recover_bot(self, health: BotHealth) -> bool:
        """Automatic recovery procedures"""
        logger.warning(f"🚨 Bot unhealthy: {health.last_error}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Recovery Step 1: Clear pending updates if too many
                if health.pending_updates > self.max_pending_updates:
                    logger.info("🔧 Clearing pending updates...")
                    
                    # Delete webhook
                    async with session.get(f"{self.telegram_api}/deleteWebhook") as resp:
                        if resp.status == 200:
                            logger.info("✅ Webhook deleted")
                    
                    # Clear updates
                    async with session.get(f"{self.telegram_api}/getUpdates?offset=-1") as resp:
                        if resp.status == 200:
                            logger.info("✅ Pending updates cleared")
                    
                    # Reset webhook
                    webhook_url = f"{self.webhook_url}"
                    async with session.get(f"{self.telegram_api}/setWebhook?url={webhook_url}") as resp:
                        if resp.status == 200:
                            logger.info("✅ Webhook reset")
                            return True
                
                # Recovery Step 2: Reset webhook if missing/wrong
                webhook_info_resp = await session.get(f"{self.telegram_api}/getWebhookInfo")
                webhook_data = await webhook_info_resp.json()
                current_url = webhook_data.get('result', {}).get('url', '')
                
                if current_url != self.webhook_url:
                    logger.info("🔧 Resetting webhook URL...")
                    async with session.get(f"{self.telegram_api}/setWebhook?url={self.webhook_url}") as resp:
                        if resp.status == 200:
                            logger.info("✅ Webhook URL corrected")
                            return True
                
                # Recovery Step 3: Health check server restart (if supported)
                logger.info("🔧 Attempting server health check...")
                try:
                    async with session.get(f"{self.server_url}/health") as resp:
                        if resp.status == 200:
                            logger.info("✅ Server responding")
                            return True
                except:
                    logger.error("❌ Server not responding - manual intervention needed")
                
        except Exception as e:
            logger.error(f"❌ Auto-recovery failed: {e}")
            
        return False
    
    async def send_alert(self, health: BotHealth, recovery_success: bool = False):
        """Send alerts (can integrate with email, Slack, etc.)"""
        alert_level = "🚨 CRITICAL" if not recovery_success else "⚠️ WARNING"
        
        alert_data = {
            "timestamp": health.timestamp.isoformat(),
            "alert_level": alert_level,
            "bot_healthy": health.is_healthy,
            "webhook_status": health.webhook_status,
            "pending_updates": health.pending_updates,
            "last_error": health.last_error,
            "response_time": health.response_time,
            "recovery_attempted": not health.is_healthy,
            "recovery_success": recovery_success
        }
        
        # Log alert
        logger.warning(f"{alert_level} Bot Alert: {json.dumps(alert_data, indent=2)}")
        
        # TODO: Add integrations
        # - Email alerts via Resend
        # - Slack notifications
        # - Discord webhooks
        # - SMS alerts via Twilio
        
        return alert_data
    
    async def run_monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting production bot monitoring...")
        consecutive_failures = 0
        
        while True:
            try:
                # Check health
                health = await self.check_bot_health()
                
                if health.is_healthy:
                    if consecutive_failures > 0:
                        logger.info("✅ Bot recovered and healthy")
                        await self.send_alert(health, recovery_success=True)
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.warning(f"❌ Bot unhealthy (failure #{consecutive_failures})")
                    
                    # Attempt auto-recovery
                    if consecutive_failures <= self.max_recovery_attempts:
                        recovery_success = await self.auto_recover_bot(health)
                        
                        if recovery_success:
                            logger.info("✅ Auto-recovery successful")
                            consecutive_failures = 0
                        else:
                            # Wait with backoff
                            backoff_time = self.recovery_backoff[min(consecutive_failures-1, len(self.recovery_backoff)-1)]
                            logger.warning(f"⏳ Auto-recovery failed, waiting {backoff_time}s...")
                            await asyncio.sleep(backoff_time)
                    
                    # Send alert
                    await self.send_alert(health, recovery_success=False)
                
                # Log health status
                status = "✅ HEALTHY" if health.is_healthy else "❌ UNHEALTHY"
                logger.info(f"{status} | Pending: {health.pending_updates} | Response: {health.response_time:.2f}s")
                
                # Wait before next check
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)  # Short wait on errors

async def main():
    """Run the monitoring system"""
    monitor = ProductionBotMonitor()
    await monitor.run_monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main())