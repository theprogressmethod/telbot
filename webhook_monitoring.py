#!/usr/bin/env python3
"""
Webhook Monitoring & Health Endpoints
Add to main.py for production bot health monitoring
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
import aiohttp
import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

# Global health status
webhook_health_data = {
    "last_check": None,
    "is_healthy": True,
    "pending_updates": 0,
    "last_error": None,
    "response_time": 0.0,
    "consecutive_failures": 0,
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
}

def track_webhook_request(success: bool):
    """Track webhook request statistics"""
    webhook_health_data["total_requests"] += 1
    if success:
        webhook_health_data["successful_requests"] += 1
        webhook_health_data["consecutive_failures"] = 0
    else:
        webhook_health_data["failed_requests"] += 1
        webhook_health_data["consecutive_failures"] += 1

async def check_telegram_health() -> Dict[str, Any]:
    """Check Telegram webhook health"""
    bot_token = os.getenv("PROD_BOT_TOKEN", "8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0")
    telegram_api = f"https://api.telegram.org/bot{bot_token}"
    
    start_time = datetime.now()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{telegram_api}/getWebhookInfo", timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get('result', {})
                    
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "is_healthy": True,
                        "webhook_url": result.get('url', ''),
                        "pending_updates": result.get('pending_update_count', 0),
                        "last_error": result.get('last_error_message'),
                        "last_error_date": result.get('last_error_date'),
                        "response_time": response_time,
                        "timestamp": start_time.isoformat()
                    }
                else:
                    return {
                        "is_healthy": False,
                        "error": f"HTTP {resp.status}",
                        "response_time": (datetime.now() - start_time).total_seconds(),
                        "timestamp": start_time.isoformat()
                    }
    except Exception as e:
        return {
            "is_healthy": False,
            "error": str(e),
            "response_time": 999.0,
            "timestamp": start_time.isoformat()
        }

def add_webhook_monitoring_routes(app: FastAPI):
    """Add webhook monitoring routes to FastAPI app"""
    
    @app.get("/webhook/health")
    async def webhook_health_check():
        """Comprehensive webhook health check"""
        telegram_health = await check_telegram_health()
        
        # Update global health data
        webhook_health_data.update({
            "last_check": datetime.now().isoformat(),
            "is_healthy": telegram_health.get("is_healthy", False),
            "pending_updates": telegram_health.get("pending_updates", 0),
            "last_error": telegram_health.get("last_error"),
            "response_time": telegram_health.get("response_time", 0)
        })
        
        return {
            "status": "healthy" if telegram_health.get("is_healthy") else "unhealthy",
            "bot_name": "@ProgressMethodBot",
            "webhook_info": telegram_health,
            "server_info": {
                "environment": os.getenv("ENVIRONMENT", "production"),
                "timestamp": datetime.now().isoformat(),
                "uptime": "available"
            },
            "health_metrics": webhook_health_data
        }
    
    @app.get("/webhook/stats")
    async def webhook_stats():
        """Webhook statistics and metrics"""
        return {
            "total_requests": webhook_health_data["total_requests"],
            "successful_requests": webhook_health_data["successful_requests"],
            "failed_requests": webhook_health_data["failed_requests"],
            "success_rate": (webhook_health_data["successful_requests"] / max(webhook_health_data["total_requests"], 1)) * 100,
            "consecutive_failures": webhook_health_data["consecutive_failures"],
            "last_check": webhook_health_data["last_check"],
            "is_healthy": webhook_health_data["is_healthy"]
        }
    
    @app.post("/webhook/recover")
    async def webhook_recovery():
        """Manual webhook recovery endpoint"""
        bot_token = os.getenv("PROD_BOT_TOKEN", "8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0")
        telegram_api = f"https://api.telegram.org/bot{bot_token}"
        webhook_url = "https://telbot-f4on.onrender.com/webhook"
        
        recovery_steps = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Delete webhook
                async with session.get(f"{telegram_api}/deleteWebhook") as resp:
                    if resp.status == 200:
                        recovery_steps.append("✅ Webhook deleted")
                    else:
                        recovery_steps.append("❌ Failed to delete webhook")
                
                # Step 2: Clear updates
                async with session.get(f"{telegram_api}/getUpdates?offset=-1") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        updates_cleared = len(data.get('result', []))
                        recovery_steps.append(f"✅ Cleared {updates_cleared} pending updates")
                    else:
                        recovery_steps.append("❌ Failed to clear updates")
                
                # Step 3: Reset webhook
                async with session.get(f"{telegram_api}/setWebhook?url={webhook_url}") as resp:
                    if resp.status == 200:
                        recovery_steps.append("✅ Webhook reset")
                    else:
                        recovery_steps.append("❌ Failed to reset webhook")
                
                return {
                    "success": True,
                    "recovery_steps": recovery_steps,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recovery_steps": recovery_steps,
                "timestamp": datetime.now().isoformat()
            }
    
    @app.get("/bot/dashboard", response_class=HTMLResponse)
    async def bot_monitoring_dashboard():
        """Bot monitoring dashboard"""
        try:
            from retro_styles import get_retro_css, get_retro_js
        except ImportError:
            # Fallback styles if retro_styles is not available
            def get_retro_css():
                return """
                body { font-family: 'Courier New', monospace; background: #001122; color: #00ff88; margin: 0; padding: 20px; }
                .terminal { background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%); 
                           background-size: 400% 400%; animation: gradient 8s ease infinite; padding: 20px; border-radius: 10px; }
                .screen { background: rgba(0, 17, 34, 0.9); padding: 20px; border-radius: 5px; }
                .header h1 { color: #ff006b; font-size: 24px; margin: 0; text-align: center; }
                .ascii-border { color: #3a86ff; font-size: 8px; text-align: center; margin: 10px 0; }
                .status-bar { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #333; margin-bottom: 20px; }
                .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 10px 0; }
                .metric-card { padding: 10px; border: 1px solid #333; border-radius: 3px; text-align: center; }
                .metric-card.good { border-color: #00ff88; color: #00ff88; }
                .metric-card.warning { border-color: #ffbe0b; color: #ffbe0b; }
                .metric-card.critical { border-color: #ff006b; color: #ff006b; }
                .metric-value { font-size: 18px; font-weight: bold; }
                .metric-label { font-size: 10px; opacity: 0.8; }
                .data-section { margin: 20px 0; }
                .data-header { color: #3a86ff; font-weight: bold; margin-bottom: 10px; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 10px; }
                .blink { animation: blink 1s infinite; }
                .loading { color: #ffbe0b; text-align: center; }
                @keyframes gradient { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
                @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
                """
            def get_retro_js():
                return """
                function updateTime() {
                    const now = new Date();
                    document.getElementById('time').textContent = now.toLocaleTimeString();
                    document.getElementById('footer-time').textContent = now.toLocaleTimeString();
                }
                setInterval(updateTime, 1000);
                updateTime();
                """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BOT_MONITOR.EXE - PRODUCTION STATUS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {get_retro_css()}
        
        .alert-critical {{
            background: #220011;
            border: 2px solid #ff006b;
            color: #ff006b;
            padding: 8px;
            margin: 4px 0;
            border-radius: 2px;
            text-align: center;
            animation: pulse 1s infinite;
        }}
        
        .alert-warning {{
            background: #221100;
            border: 2px solid #ffbe0b;
            color: #ffbe0b;
            padding: 8px;
            margin: 4px 0;
            border-radius: 2px;
            text-align: center;
        }}
        
        .alert-success {{
            background: #001122;
            border: 2px solid #06ffa5;
            color: #06ffa5;
            padding: 8px;
            margin: 4px 0;
            border-radius: 2px;
            text-align: center;
        }}
        
        @keyframes pulse {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.5; }}
        }}
        
        .recovery-btn {{
            background: #001a33;
            border: 2px solid #ff006b;
            color: #ff006b;
            padding: 8px 16px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
            border-radius: 2px;
            margin: 4px;
        }}
        
        .recovery-btn:hover {{
            background: #002244;
            box-shadow: 0 0 8px #ff006b44;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>BOT_MONITOR.EXE</h1>
                <div style="color: #ff006b; font-size: 12px;">PRODUCTION BOT HEALTH MONITOR</div>
            </div>
            
            <div class="ascii-border">
██████╗  ██████╗ ████████╗    ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗ 
██╔══██╗██╔═══██╗╚══██╔══╝    ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
██████╔╝██║   ██║   ██║       ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
██╔══██╗██║   ██║   ██║       ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
██████╔╝╚██████╔╝   ██║       ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
            </div>
            
            <div class="status-bar">
                <span>BOT: <span id="bot-status" style="color: #00ff88;">@ProgressMethodBot</span></span>
                <span>WEBHOOK: <span id="webhook-status" style="color: #3a86ff;">CHECKING...</span></span>
                <span>UPTIME: <span id="uptime" style="color: #ff6b35;">--</span></span>
                <span>TIME: <span id="time">--:--:--</span></span>
                <span class="blink">█</span>
            </div>
            
            <div id="health-alert" class="alert-success" style="display: none;"></div>
            
            <div class="data-section">
                <div class="data-header">REAL-TIME HEALTH METRICS</div>
                <div class="data-content">
                    <div class="metric-grid" id="health-metrics">
                        <div class="loading">CHECKING BOT HEALTH...</div>
                    </div>
                </div>
            </div>
            
            <div class="data-section">
                <div class="data-header">WEBHOOK STATISTICS</div>
                <div class="data-content">
                    <div class="metric-grid" id="webhook-stats">
                        <div class="loading">LOADING STATS...</div>
                    </div>
                </div>
            </div>
            
            <div class="data-section">
                <div class="data-header">EMERGENCY CONTROLS</div>
                <div class="data-content" style="text-align: center;">
                    <button class="recovery-btn" onclick="performRecovery()">🚨 EMERGENCY RECOVERY</button>
                    <button class="recovery-btn" onclick="refreshHealth()" style="border-color: #00ff88; color: #00ff88;">🔄 REFRESH STATUS</button>
                    <div id="recovery-result" style="margin-top: 8px;"></div>
                </div>
            </div>
            
            <div class="footer">
BOT_MONITOR.EXE v1.0 © 2025 // AUTO_CHECK: 30s // LAST_UPDATE: <span id="footer-time">--:--:--</span>
            </div>
        </div>
    </div>

    <script>
        {get_retro_js()}
        
        async function checkBotHealth() {{
            try {{
                const response = await fetch('/webhook/health');
                const data = await response.json();
                
                updateHealthMetrics(data);
                updateWebhookStats();
                
                if (data.webhook_info.is_healthy) {{
                    showAlert('✅ BOT OPERATIONAL - All systems normal', 'success');
                    document.getElementById('webhook-status').textContent = 'HEALTHY';
                    document.getElementById('webhook-status').style.color = '#00ff88';
                }} else {{
                    showAlert('🚨 BOT UNHEALTHY - ' + (data.webhook_info.error || 'Unknown error'), 'critical');
                    document.getElementById('webhook-status').textContent = 'UNHEALTHY';
                    document.getElementById('webhook-status').style.color = '#ff006b';
                }}
                
            }} catch (error) {{
                showAlert('❌ MONITORING ERROR - ' + error.message, 'critical');
                document.getElementById('webhook-status').textContent = 'ERROR';
                document.getElementById('webhook-status').style.color = '#ff006b';
            }}
        }}
        
        function updateHealthMetrics(data) {{
            const webhookInfo = data.webhook_info;
            const html = `
                <div class="metric-card ${{webhookInfo.is_healthy ? 'good' : 'critical'}}">
                    <div class="metric-value">${{webhookInfo.is_healthy ? 'HEALTHY' : 'UNHEALTHY'}}</div>
                    <div class="metric-label">BOT_STATUS</div>
                </div>
                <div class="metric-card ${{webhookInfo.pending_updates > 5 ? 'critical' : 'good'}}">
                    <div class="metric-value">${{webhookInfo.pending_updates || 0}}</div>
                    <div class="metric-label">PENDING_MSGS</div>
                </div>
                <div class="metric-card ${{webhookInfo.response_time > 5 ? 'warning' : 'good'}}">
                    <div class="metric-value">${{webhookInfo.response_time?.toFixed(2) || '0'}}s</div>
                    <div class="metric-label">RESPONSE_TIME</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{webhookInfo.last_error ? 'ERROR' : 'NONE'}}</div>
                    <div class="metric-label">LAST_ERROR</div>
                </div>
            `;
            document.getElementById('health-metrics').innerHTML = html;
        }}
        
        async function updateWebhookStats() {{
            try {{
                const response = await fetch('/webhook/stats');
                const data = await response.json();
                
                const html = `
                    <div class="metric-card">
                        <div class="metric-value">${{data.total_requests || 0}}</div>
                        <div class="metric-label">TOTAL_REQUESTS</div>
                    </div>
                    <div class="metric-card good">
                        <div class="metric-value">${{data.successful_requests || 0}}</div>
                        <div class="metric-label">SUCCESSFUL</div>
                    </div>
                    <div class="metric-card ${{data.failed_requests > 0 ? 'warning' : 'good'}}">
                        <div class="metric-value">${{data.failed_requests || 0}}</div>
                        <div class="metric-label">FAILED</div>
                    </div>
                    <div class="metric-card ${{data.success_rate < 95 ? 'warning' : 'good'}}">
                        <div class="metric-value">${{data.success_rate?.toFixed(1) || '0'}}%</div>
                        <div class="metric-label">SUCCESS_RATE</div>
                    </div>
                `;
                document.getElementById('webhook-stats').innerHTML = html;
                
            }} catch (error) {{
                document.getElementById('webhook-stats').innerHTML = '<div class="error">Stats unavailable</div>';
            }}
        }}
        
        async function performRecovery() {{
            document.getElementById('recovery-result').innerHTML = '<div class="loading">PERFORMING EMERGENCY RECOVERY...</div>';
            
            try {{
                const response = await fetch('/webhook/recover', {{ method: 'POST' }});
                const data = await response.json();
                
                if (data.success) {{
                    const steps = data.recovery_steps.join('<br>');
                    document.getElementById('recovery-result').innerHTML = `<div class="success">RECOVERY COMPLETE<br>${{steps}}</div>`;
                    setTimeout(checkBotHealth, 3000); // Check health after recovery
                }} else {{
                    document.getElementById('recovery-result').innerHTML = `<div class="error">RECOVERY FAILED: ${{data.error}}</div>`;
                }}
                
            }} catch (error) {{
                document.getElementById('recovery-result').innerHTML = `<div class="error">RECOVERY ERROR: ${{error.message}}</div>`;
            }}
        }}
        
        function refreshHealth() {{
            document.getElementById('recovery-result').innerHTML = '<div class="loading">REFRESHING...</div>';
            checkBotHealth();
            setTimeout(() => {{
                document.getElementById('recovery-result').innerHTML = '<div class="success">STATUS REFRESHED</div>';
            }}, 1000);
        }}
        
        function showAlert(message, type) {{
            const alertEl = document.getElementById('health-alert');
            alertEl.className = `alert-${{type}}`;
            alertEl.textContent = message;
            alertEl.style.display = 'block';
        }}
        
        // Initialize
        checkBotHealth();
        setInterval(checkBotHealth, 30000); // Check every 30 seconds
    </script>
</body>
</html>
        """
        
        return html