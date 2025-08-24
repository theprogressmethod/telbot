"""
WEEK 1 SIMPLIFIED MAIN.PY
=========================
Ferrari engine configured as go-kart
All Phase 2/3 features DISABLED
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

# Core imports only
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Telegram bot imports
from aiogram import Bot, Dispatcher
from aiogram.types import Update

# Week 1 configuration
from week1_config import WEEK_1_FEATURES, is_feature_enabled

# ========== PHASE 2/3 IMPORTS DISABLED ==========
# All advanced system imports commented out per Week 1 scope
# from system_monitor_dashboard import SystemMonitor, create_dashboard_app
# from feature_control_system import FeatureControlSystem
# from testing_optimization_framework import TestingFramework
# from enhanced_metrics_system import EnhancedMetricsSystem
# from alerting_system import AlertingSystem
# from stakeholder_dashboards import StakeholderDashboards
# from automated_scheduler import AutomatedScheduler
# from intelligent_optimization_system import IntelligentOptimizationSystem
# from adaptive_personalization_system import AdaptivePersonalizationSystem
# from predictive_analytics_system import PredictiveAnalyticsSystem
# from auto_scaling_system import AutoScalingSystem
# from ml_insights_system import MLInsightsSystem
# from intelligent_anomaly_detection import IntelligentAnomalyDetection
# ==================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Basic configuration
config = {
    'bot_token': os.getenv('BOT_TOKEN'),
    'supabase_url': os.getenv('DEV_SUPABASE_URL'),  # Development only
    'supabase_key': os.getenv('DEV_SUPABASE_KEY'),  # Development only
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'environment': 'development',  # ALWAYS development for Week 1
}

# Global variables (simplified)
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
supabase: Optional[Client] = None

# Admin authentication disabled for Week 1 MVP

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simplified lifespan for Week 1 - no Phase 2/3 systems"""
    global bot, dp, supabase
    
    logger.info("🚀 Starting Week 1 MVP System")
    logger.info("=" * 50)
    
    try:
        # Initialize Supabase
        supabase = create_client(config['supabase_url'], config['supabase_key'])
        logger.info("✅ Database connected (development)")
        
        # Initialize bot
        bot = Bot(token=config['bot_token'])
        dp = Dispatcher()
        
        # Import and run the main bot
        from telbot import dp as telbot_dp
        logger.info("✅ Telegram bot initialized (@TPM_superbot)")
        
        # Log Week 1 status
        logger.info("\n📋 WEEK 1 CONFIGURATION:")
        enabled = [k for k, v in WEEK_1_FEATURES.items() if v]
        disabled = [k for k, v in WEEK_1_FEATURES.items() if not v]
        logger.info(f"   ✅ Enabled: {', '.join(enabled[:3])}...")
        logger.info(f"   ❌ Disabled: {', '.join(disabled[:3])}...")
        
        # NO Phase 2/3 system initialization
        logger.info("   ⚠️  All advanced systems DISABLED for Week 1")
        
        logger.info("=" * 50)
        logger.info("✅ Week 1 MVP Ready")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Cleanup
        if bot:
            await bot.session.close()
        logger.info("🛑 Week 1 system shutdown complete")

# Create FastAPI app with Week 1 scope
app = FastAPI(
    title="The Progress Method - Week 1 MVP",
    description="Simplified core functionality only - Phase 2/3 disabled",
    version="1.0-week1",
    lifespan=lifespan
)

# CORS middleware (basic)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== WEEK 1 ENDPOINTS ONLY ==========

@app.get("/")
async def root():
    """Root endpoint - Week 1 status"""
    return {
        "status": "active",
        "version": "1.0-week1",
        "bot": "@TPM_superbot",
        "environment": "development",
        "features": {
            "enabled": sum(WEEK_1_FEATURES.values()),
            "disabled": len(WEEK_1_FEATURES) - sum(WEEK_1_FEATURES.values())
        },
        "message": "Week 1 MVP - Core features only"
    }

@app.get("/health")
async def health_check():
    """Basic health check"""
    try:
        # Check database
        result = supabase.table("users").select("count", count="exact").execute()
        db_status = "healthy" if result else "degraded"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "bot": "active" if bot else "inactive",
            "week1_mode": True
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/webhook")
async def webhook(request: Request):
    """Telegram webhook endpoint"""
    if not is_feature_enabled('basic_commands'):
        raise HTTPException(status_code=503, detail="Bot commands disabled")
    
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/week1/status")
async def week1_status():
    """Week 1 feature status"""
    return {
        "mode": "week1_mvp",
        "features": WEEK_1_FEATURES,
        "database": {
            "users": supabase.table("users").select("count", count="exact").execute().count,
            "commitments": supabase.table("commitments").select("count", count="exact").execute().count,
        },
        "limits": {
            "max_users": 10,
            "commands_enabled": 7,
            "advanced_features": "disabled"
        }
    }

@app.get("/admin/week1")
async def admin_panel():
    """Simplified admin panel for Week 1"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Week 1 Admin - TPM</title>
        <style>
            body { 
                font-family: monospace; 
                background: #1a1a1a; 
                color: #00ff00;
                padding: 20px;
            }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #00ffff; }
            .feature { 
                padding: 10px; 
                margin: 5px 0; 
                background: #2a2a2a;
                border-left: 3px solid #00ff00;
            }
            .disabled { 
                border-left-color: #ff0000; 
                opacity: 0.5;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin: 20px 0;
            }
            .stat-box {
                background: #2a2a2a;
                padding: 15px;
                text-align: center;
            }
            .number { font-size: 2em; color: #00ffff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Week 1 MVP Admin</h1>
            <p>Ferrari engine running as go-kart mode</p>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="number">65</div>
                    <div>Users</div>
                </div>
                <div class="stat-box">
                    <div class="number">233</div>
                    <div>Commitments</div>
                </div>
                <div class="stat-box">
                    <div class="number">7</div>
                    <div>Commands</div>
                </div>
            </div>
            
            <h2>✅ Enabled Features</h2>
            <div class="feature">User Registration</div>
            <div class="feature">Basic Commitments</div>
            <div class="feature">SMART Scoring</div>
            <div class="feature">Simple Pods</div>
            
            <h2>❌ Disabled Features</h2>
            <div class="feature disabled">ML Systems</div>
            <div class="feature disabled">Predictive Analytics</div>
            <div class="feature disabled">Auto Scaling</div>
            <div class="feature disabled">Complex Dashboards</div>
            <div class="feature disabled">Payment Processing</div>
            
            <p style="margin-top: 30px; color: #ffff00;">
                ⚠️ Development Environment - @TPM_superbot only
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ========== DISABLED PHASE 2/3 ENDPOINTS ==========
# All complex endpoints removed for Week 1
# No analytics endpoints
# No ML endpoints
# No dashboard endpoints
# No payment endpoints
# ================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Week 1 MVP Server")
    logger.info("⚠️  Phase 2/3 features DISABLED")
    logger.info("✅ Core features only")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )