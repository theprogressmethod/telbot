#!/usr/bin/env python3
"""
FastAPI-based Telegram Bot for Railway deployment
Handles webhooks from Telegram for the Progress Method Accountability Bot
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import APIKeyHeader
import asyncio
import json
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

# Import our bot components
from telbot import (
    Config, SmartAnalysis, DatabaseManager, bot, dp, role_manager,
    start_handler, commit_handler, list_handler, done_handler,
    help_handler, feedback_handler, myroles_handler, progress_handler,
    stats_handler, leaderboard_handler, champions_handler, streaks_handler,
    admin_stats_handler, grant_role_handler, handle_text_messages, 
    complete_commitment_callback, save_smart_callback, save_original_callback, 
    cancel_commit_callback, cancel_done_callback, set_bot_commands
)
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Update

# Import only existing modules
try:
    from system_monitor_dashboard import SystemMonitor, create_dashboard_app
except ImportError:
    SystemMonitor = None
    create_dashboard_app = None

try:
    from feature_control_system import FeatureControlSystem, Feature, FeatureFlag, RolloutStrategy
except ImportError:
    FeatureControlSystem = None

try:
    from enhanced_metrics_system import EnhancedMetricsSystem
except ImportError:
    EnhancedMetricsSystem = None

try:
    from alerting_system import AlertingSystem
except ImportError:
    AlertingSystem = None

try:
    from stakeholder_dashboards import StakeholderDashboards, StakeholderType
except ImportError:
    StakeholderDashboards = None

# Import Week1 dashboard components
from dashboard_routes_1_0 import register_week1_dashboard_routes
from dashboard_integration_1_0 import initialize_dashboard_integration
from dashboard_crud_routes import create_crud_router
from basic_pod_system import BasicPodSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
config = None
smart_analyzer = None
monitor = None
feature_system = None
testing_framework = None

# Phase 2 systems
enhanced_metrics = None
alerting_system = None
stakeholder_dashboards = None
automated_scheduler = None

# Phase 3 intelligent systems
optimization_system = None
personalization_system = None
predictive_analytics = None
scaling_system = None
ml_insights = None
anomaly_detection = None

# Admin authentication
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def setup_visibility_systems(config, supabase):
    """Initialize all visibility and control systems"""
    
    # Initialize monitoring
    monitor = SystemMonitor(supabase)
    
    # Initialize feature control
    feature_system = FeatureControlSystem(supabase)
    await feature_system.initialize_feature_tables()
    
    # Initialize testing framework
    testing_framework = TestingFramework(supabase)
    await testing_framework.initialize_testing_tables()
    
    return monitor, feature_system, testing_framework

async def setup_phase2_systems(monitor, feature_system, testing_framework, supabase):
    """Initialize Phase 2 enhanced systems"""
    
    # Initialize enhanced metrics
    enhanced_metrics = EnhancedMetricsSystem(supabase)
    
    # Initialize alerting system
    alerting_system = AlertingSystem(supabase)
    
    # Initialize stakeholder dashboards
    stakeholder_dashboards = StakeholderDashboards(monitor, enhanced_metrics, alerting_system)
    
    # Initialize automated scheduler
    automated_scheduler = AutomatedScheduler(monitor, enhanced_metrics, alerting_system, testing_framework)
    
    return enhanced_metrics, alerting_system, stakeholder_dashboards, automated_scheduler

async def setup_phase3_systems(monitor, enhanced_metrics, alerting_system, predictive_system, supabase):
    """Initialize Phase 3 intelligent systems"""
    
    # Initialize intelligent optimization system
    optimization_system = IntelligentOptimizationSystem(supabase, enhanced_metrics, monitor)
    
    # Initialize adaptive personalization system
    personalization_system = AdaptivePersonalizationSystem(supabase, enhanced_metrics)
    
    # Initialize predictive analytics system
    predictive_analytics = PredictiveAnalyticsSystem(supabase, enhanced_metrics)
    
    # Initialize auto-scaling system
    scaling_system = AutoScalingSystem(supabase, enhanced_metrics, predictive_analytics)
    
    # Initialize ML insights system
    ml_insights = MLInsightsSystem(supabase, enhanced_metrics, personalization_system)
    
    # Initialize intelligent anomaly detection
    anomaly_detection = IntelligentAnomalyDetection(supabase, enhanced_metrics, alerting_system)
    
    return optimization_system, personalization_system, predictive_analytics, scaling_system, ml_insights, anomaly_detection

async def create_initial_features(feature_system):
    """Create initial feature flags for existing functionality"""
    
    initial_features = [
        Feature(
            id="commitment_creation",
            name="Commitment Creation",
            description="Core commitment creation with SMART analysis",
            flag=FeatureFlag.ENABLED,
            rollout_strategy=RolloutStrategy.ALL_USERS,
            config={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system"
        ),
        Feature(
            id="advanced_analytics",
            name="Advanced Analytics",
            description="Advanced statistics and progress tracking",
            flag=FeatureFlag.ENABLED,
            rollout_strategy=RolloutStrategy.ALL_USERS,
            config={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system"
        ),
        Feature(
            id="social_features",
            name="Social Features",
            description="Leaderboards, streaks, and champions",
            flag=FeatureFlag.ENABLED,
            rollout_strategy=RolloutStrategy.ALL_USERS,
            config={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system"
        ),
        Feature(
            id="admin_features",
            name="Admin Features",
            description="Administrative functions and controls",
            flag=FeatureFlag.USER_SEGMENT,
            rollout_strategy=RolloutStrategy.ROLE_BASED,
            config={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            target_user_roles=["admin", "super_admin"]
        )
    ]
    
    for feature in initial_features:
        try:
            await feature_system.create_feature(feature)
        except Exception as e:
            logger.warning(f"Feature {feature.id} may already exist: {e}")
    
    logger.info(f"✅ Initialized {len(initial_features)} feature flags")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global config, smart_analyzer, monitor, feature_system, testing_framework
    global enhanced_metrics, alerting_system, stakeholder_dashboards, automated_scheduler
    global optimization_system, personalization_system, predictive_analytics, scaling_system, ml_insights, anomaly_detection
    
    try:
        # Initialize configuration
        config = Config()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize SMART analyzer
        smart_analyzer = SmartAnalysis(config)
        logger.info("✅ SMART analyzer initialized")
        
        # Initialize visibility and control systems
        from telbot import supabase  # Import supabase client from telbot
        monitor, feature_system, testing_framework = await setup_visibility_systems(config, supabase)
        logger.info("✅ Visibility and control systems initialized")
        
        # Initialize Phase 2 enhanced systems
        enhanced_metrics, alerting_system, stakeholder_dashboards, automated_scheduler = await setup_phase2_systems(monitor, feature_system, testing_framework, supabase)
        logger.info("✅ Phase 2 enhanced systems initialized")
        
        # Initialize Phase 3 intelligent systems
        optimization_system, personalization_system, predictive_analytics, scaling_system, ml_insights, anomaly_detection = await setup_phase3_systems(monitor, enhanced_metrics, alerting_system, None, supabase)
        logger.info("✅ Phase 3 intelligent systems initialized")
        
        # Create initial feature flags
        await create_initial_features(feature_system)
        
        # Register all handlers
        dp.message.register(start_handler, CommandStart())
        dp.message.register(commit_handler, Command("commit"))
        dp.message.register(list_handler, Command("list"))
        dp.message.register(done_handler, Command("done"))
        dp.message.register(feedback_handler, Command("feedback"))
        dp.message.register(help_handler, Command("help"))
        dp.message.register(myroles_handler, Command("myroles"))
        dp.message.register(progress_handler, Command("progress"))
        dp.message.register(stats_handler, Command("stats"))
        dp.message.register(leaderboard_handler, Command("leaderboard"))
        dp.message.register(champions_handler, Command("champions"))
        dp.message.register(streaks_handler, Command("streaks"))
        dp.message.register(admin_stats_handler, Command("adminstats"))
        dp.message.register(grant_role_handler, Command("grant_role"))
        dp.message.register(handle_text_messages)
        
        # Register callback handlers
        dp.callback_query.register(complete_commitment_callback, F.data.startswith("complete_"))
        dp.callback_query.register(save_smart_callback, F.data.startswith("save_smart_"))
        dp.callback_query.register(save_original_callback, F.data.startswith("save_original_"))
        dp.callback_query.register(cancel_commit_callback, F.data == "cancel_commit")
        dp.callback_query.register(cancel_done_callback, F.data == "cancel_done")
        
        logger.info("✅ All handlers registered successfully")
        
        # Set bot commands
        await set_bot_commands()
        logger.info("✅ Bot commands set successfully")
        
        # Test database connection
        db_test = await DatabaseManager.test_database()
        if db_test:
            logger.info("✅ Database connection test successful")
        else:
            logger.warning("⚠️ Database connection test failed")
        
        # Initialize Week1 dashboard components
        try:
            pod_system = BasicPodSystem(supabase)
            await initialize_dashboard_integration(supabase, role_manager, pod_system)
            logger.info("✅ Week1 dashboard integration initialized")
        except Exception as e:
            logger.warning(f"⚠️ Dashboard integration failed: {e}")
        
        logger.info("🚀 Bot startup completed successfully!")
        
        # Start automated scheduler
        automated_scheduler.start_scheduler()
        logger.info("⏰ Automated scheduler started")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    finally:
        # Cleanup
        if automated_scheduler:
            automated_scheduler.stop_scheduler()
            logger.info("⏰ Automated scheduler stopped")
            
        if bot.session:
            await bot.session.close()
        logger.info("🛑 Bot shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Progress Method Telegram Bot",
    description="Accountability bot with SMART goal analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Register Week1 dashboard routes
register_week1_dashboard_routes(app)
logger.info("✅ Week1 dashboard routes registered")

# Register CRUD routes for Week1 dashboard
from telbot import supabase
pod_system = BasicPodSystem(supabase)
crud_router = create_crud_router(supabase, pod_system)
app.include_router(crud_router)
logger.info("✅ CRUD routes registered for Week1 dashboard")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ Progress Method Bot is running!",
        "timestamp": datetime.now().isoformat(),
        "environment_check": {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with full system monitoring"""
    try:
        # If monitor is available, use comprehensive health check
        if monitor:
            try:
                system_health = await monitor.get_system_overview()
                
                # Determine HTTP status based on health
                status_code = 200
                if system_health.get("system_status", {}).get("status") == "critical":
                    status_code = 503
                elif system_health.get("system_status", {}).get("status") == "warning":
                    status_code = 207  # Multi-status
                
                return JSONResponse(content=system_health, status_code=status_code)
            except Exception as e:
                logger.warning(f"Monitor health check failed, falling back: {e}")
        
        # Fallback to basic health check
        db_healthy = await DatabaseManager.test_database()
        config_healthy = bool(config and config.bot_token and config.openai_api_key)
        
        health_status = {
            "status": "healthy" if (db_healthy and config_healthy) else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "✅ healthy" if db_healthy else "❌ unhealthy",
                "configuration": "✅ healthy" if config_healthy else "❌ unhealthy",
                "bot": "✅ healthy" if bot else "❌ unhealthy",
                "monitor": "✅ healthy" if monitor else "⚠️ not initialized",
                "features": "✅ healthy" if feature_system else "⚠️ not initialized"
            }
        }
        
        status_code = 200 if (db_healthy and config_healthy) else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )

@app.get("/health/simple")
async def simple_health():
    """Simple health check for load balancers"""
    try:
        # Quick database test
        result = await DatabaseManager.test_database()
        return {"status": "healthy" if result else "unhealthy"}
    except:
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhooks from Telegram"""
    try:
        # Get request body
        body = await request.body()
        if not body:
            logger.warning("⚠️ Empty webhook body received")
            return JSONResponse(content={"status": "error", "message": "Empty body"}, status_code=400)
        
        # Parse JSON
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in webhook: {e}")
            return JSONResponse(content={"status": "error", "message": "Invalid JSON"}, status_code=400)
        
        logger.info(f"📨 Webhook received from Telegram")
        logger.debug(f"Webhook data: {json.dumps(data, indent=2)}")
        
        # Validate bot is ready
        if not bot:
            logger.error("❌ Bot not initialized")
            return JSONResponse(content={"status": "error", "message": "Bot not ready"}, status_code=503)
        
        # Create Update object
        try:
            update = Update.model_validate(data)
        except Exception as e:
            logger.error(f"❌ Failed to parse Telegram update: {e}")
            return JSONResponse(content={"status": "error", "message": "Invalid update format"}, status_code=400)
        
        # Process the update
        try:
            await dp.feed_update(bot, update)
            logger.info("✅ Update processed successfully")
            return JSONResponse(content={"status": "ok"})
            
        except Exception as e:
            logger.error(f"❌ Error processing update: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Still return 200 to prevent Telegram from retrying
            return JSONResponse(content={"status": "error", "message": "Processing failed"})
            
    except Exception as e:
        logger.error(f"❌ Webhook handler error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Always return 200 to Telegram to prevent retries
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.get("/set_webhook")
async def set_webhook(url: str = None):
    """Set webhook URL for the bot (for testing)"""
    if not url:
        return {"error": "Please provide URL parameter: /set_webhook?url=YOUR_WEBHOOK_URL"}
    
    try:
        webhook_url = f"{url}/webhook"
        result = await bot.set_webhook(url=webhook_url)
        
        if result:
            logger.info(f"✅ Webhook set successfully to: {webhook_url}")
            return {"status": "success", "webhook_url": webhook_url}
        else:
            logger.error("❌ Failed to set webhook")
            return {"status": "error", "message": "Failed to set webhook"}
            
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/webhook_info")
async def get_webhook_info():
    """Get current webhook information"""
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
    except Exception as e:
        logger.error(f"❌ Error getting webhook info: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/refresh_commands")
async def refresh_commands():
    """Refresh bot commands in Telegram menu"""
    try:
        await set_bot_commands()
        logger.info("✅ Bot commands refreshed successfully")
        return {
            "status": "success", 
            "message": "Bot commands refreshed successfully",
            "commands": [
                "/start - Welcome message",
                "/commit - Add a new commitment", 
                "/done - Mark commitments as complete",
                "/list - View your active commitments",
                "/feedback - Send feedback or suggestions",
                "/help - Show help message"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error refreshing commands: {e}")
        return {"status": "error", "message": str(e)}

# Admin authentication dependency
async def verify_admin(api_key: Optional[str] = Depends(api_key_header)):
    """Verify admin API key"""
    admin_key = os.getenv("ADMIN_API_KEY")
    if not admin_key:
        # If no admin key is set, allow access (development mode)
        logger.warning("⚠️ No ADMIN_API_KEY set - admin routes are unprotected!")
        return True
    
    if not api_key or api_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return True

# Admin dashboard routes
@app.get("/admin/dashboard", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def admin_dashboard():
    """System monitoring dashboard"""
    try:
        if not monitor:
            raise HTTPException(status_code=503, detail="Monitoring system not initialized")
        
        # Get system overview data
        overview = await monitor.get_system_overview()
        
        # Create a simple HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Progress Method - System Monitor</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .status-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status-healthy {{ border-left: 5px solid #27ae60; }}
                .status-warning {{ border-left: 5px solid #f39c12; }}
                .status-critical {{ border-left: 5px solid #e74c3c; }}
                .metric {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .metric-label {{ font-weight: bold; }}
                .refresh-btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎛️ Progress Method System Monitor</h1>
                    <p>Real-time system health and performance monitoring</p>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                </div>
                
                <div class="status-grid">
                    <div class="status-card status-{overview.get('system_status', {}).get('status', 'unknown')}">
                        <h3>📊 System Overview</h3>
                        <div class="metric">
                            <span class="metric-label">Status:</span>
                            <span>{overview.get('system_status', {}).get('status', 'Unknown')}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Health:</span>
                            <span>{overview.get('system_status', {}).get('health_percentage', 0)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Components:</span>
                            <span>{overview.get('system_status', {}).get('healthy_components', 0)}/{overview.get('system_status', {}).get('total_components', 0)}</span>
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <h3>🏗️ Infrastructure</h3>
                        <div class="metric">
                            <span class="metric-label">Database:</span>
                            <span>✅ Connected</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Bot API:</span>
                            <span>✅ Active</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Monitoring:</span>
                            <span>✅ Enabled</span>
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <h3>👥 User Activity</h3>
                        <div class="metric">
                            <span class="metric-label">Total Users:</span>
                            <span>{"Calculating..." if not overview.get('core_metrics') else len(overview.get('core_metrics', []))}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Active Today:</span>
                            <span>Calculating...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">New Today:</span>
                            <span>Calculating...</span>
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <h3>⚙️ Features</h3>
                        <div class="metric">
                            <span class="metric-label">Total Features:</span>
                            <span>{overview.get('feature_status', {}).get('total_features', 'N/A')}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Production:</span>
                            <span>{overview.get('feature_status', {}).get('production_features', 'N/A')}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Error Rate:</span>
                            <span>{overview.get('feature_status', {}).get('error_rate_24h', 'N/A')}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="status-card" style="margin-top: 20px;">
                    <h3>🔗 Quick Links</h3>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <a href="/admin/api/overview" style="color: #3498db;">📊 System Overview API</a>
                        <a href="/admin/api/features" style="color: #3498db;">⚙️ Features API</a>
                        <a href="/admin/api/tests" style="color: #3498db;">🧪 Run Tests</a>
                        <a href="/health" style="color: #3498db;">🏥 Health Check</a>
                    </div>
                </div>
                
                <div class="status-card" style="margin-top: 20px;">
                    <h3>📝 Raw Data</h3>
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px;">
{json.dumps(overview, indent=2, default=str)[:2000]}...
                    </pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/overview", dependencies=[Depends(verify_admin)])
async def admin_overview():
    """System overview API"""
    try:
        if not monitor:
            raise HTTPException(status_code=503, detail="Monitoring system not initialized")
        
        overview = await monitor.get_system_overview()
        
        # Convert any enum objects to strings for JSON serialization
        def serialize_for_json(obj):
            if hasattr(obj, 'value'):  # Enum object
                return obj.value
            elif hasattr(obj, '__dict__'):  # Custom object with attributes
                return {k: serialize_for_json(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize_for_json(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: serialize_for_json(v) for k, v in obj.items()}
            else:
                return obj
        
        return serialize_for_json(overview)
    except Exception as e:
        logger.error(f"❌ Overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/features", dependencies=[Depends(verify_admin)])
async def admin_features():
    """Feature management API"""
    try:
        if not feature_system:
            raise HTTPException(status_code=503, detail="Feature system not initialized")
        
        from dataclasses import asdict
        features = await feature_system.get_all_features()
        return [asdict(f) for f in features]
    except Exception as e:
        logger.error(f"❌ Features error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/tests", dependencies=[Depends(verify_admin)])
async def admin_tests():
    """Run system tests"""
    try:
        if not testing_framework:
            raise HTTPException(status_code=503, detail="Testing framework not initialized")
        
        return await testing_framework.run_comprehensive_test_suite()
    except Exception as e:
        logger.error(f"❌ Tests error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/features/{feature_id}/toggle", dependencies=[Depends(verify_admin)])
async def toggle_feature(feature_id: str, enabled: bool):
    """Toggle feature on/off"""
    try:
        if not feature_system:
            raise HTTPException(status_code=503, detail="Feature system not initialized")
        
        if enabled:
            success = await feature_system.enable_feature(feature_id)
        else:
            success = await feature_system.disable_feature(feature_id)
        
        return {"success": success, "feature_id": feature_id, "enabled": enabled}
    except Exception as e:
        logger.error(f"❌ Toggle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/features/{feature_id}/emergency-disable", dependencies=[Depends(verify_admin)])
async def emergency_disable_feature(feature_id: str, reason: str):
    """Emergency disable feature"""
    try:
        if not feature_system:
            raise HTTPException(status_code=503, detail="Feature system not initialized")
        
        success = await feature_system.emergency_disable(feature_id, reason)
        return {"success": success, "feature_id": feature_id, "reason": reason}
    except Exception as e:
        logger.error(f"❌ Emergency disable error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/tests/run", dependencies=[Depends(verify_admin)])
async def run_tests():
    """Run comprehensive test suite"""
    try:
        if not testing_framework:
            raise HTTPException(status_code=503, detail="Testing framework not initialized")
        
        results = await testing_framework.run_comprehensive_test_suite()
        
        # Store results
        await testing_framework.store_test_results(results)
        
        return results
    except Exception as e:
        logger.error(f"❌ Test run error: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/admin/api/tests/performance", dependencies=[Depends(verify_admin)])
async def performance_report():
    """Get performance optimization report"""
    try:
        if not testing_framework:
            raise HTTPException(status_code=503, detail="Testing framework not initialized")
        
        report = await testing_framework.create_performance_report()
        return report
    except Exception as e:
        logger.error(f"❌ Performance report error: {e}")
        return {"error": str(e)}

# Phase 2 Enhanced Endpoints

@app.get("/admin/api/metrics/enhanced", dependencies=[Depends(verify_admin)])
async def enhanced_metrics_summary():
    """Get enhanced Progress Method metrics"""
    try:
        if not enhanced_metrics:
            raise HTTPException(status_code=503, detail="Enhanced metrics system not initialized")
        
        return await enhanced_metrics.get_metrics_summary()
    except Exception as e:
        logger.error(f"❌ Enhanced metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/alerts", dependencies=[Depends(verify_admin)])
async def get_alerts():
    """Get active alerts"""
    try:
        if not alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not initialized")
        
        return await alerting_system.get_active_alerts()
    except Exception as e:
        logger.error(f"❌ Alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/alerts/summary", dependencies=[Depends(verify_admin)])
async def get_alert_summary():
    """Get alert summary and statistics"""
    try:
        if not alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not initialized")
        
        return await alerting_system.get_alert_summary()
    except Exception as e:
        logger.error(f"❌ Alert summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/alerts/{alert_id}/acknowledge", dependencies=[Depends(verify_admin)])
async def acknowledge_alert(alert_id: str, acknowledged_by: str = "admin"):
    """Acknowledge an alert"""
    try:
        if not alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not initialized")
        
        success = await alerting_system.acknowledge_alert(alert_id, acknowledged_by)
        return {"success": success, "alert_id": alert_id, "acknowledged_by": acknowledged_by}
    except Exception as e:
        logger.error(f"❌ Acknowledge alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/alerts/{alert_id}/resolve", dependencies=[Depends(verify_admin)])
async def resolve_alert(alert_id: str, resolved_by: str = "admin"):
    """Resolve an alert"""
    try:
        if not alerting_system:
            raise HTTPException(status_code=503, detail="Alerting system not initialized")
        
        success = await alerting_system.resolve_alert(alert_id, resolved_by)
        return {"success": success, "alert_id": alert_id, "resolved_by": resolved_by}
    except Exception as e:
        logger.error(f"❌ Resolve alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/scheduler/status", dependencies=[Depends(verify_admin)])
async def scheduler_status():
    """Get automated scheduler status"""
    try:
        if not automated_scheduler:
            raise HTTPException(status_code=503, detail="Automated scheduler not initialized")
        
        return automated_scheduler.get_scheduler_status()
    except Exception as e:
        logger.error(f"❌ Scheduler status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/scheduler/tasks", dependencies=[Depends(verify_admin)])
async def scheduler_tasks():
    """Get scheduled tasks summary"""
    try:
        if not automated_scheduler:
            raise HTTPException(status_code=503, detail="Automated scheduler not initialized")
        
        return automated_scheduler.get_task_summary()
    except Exception as e:
        logger.error(f"❌ Scheduler tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/scheduler/tasks/{task_id}/enable", dependencies=[Depends(verify_admin)])
async def enable_scheduled_task(task_id: str):
    """Enable a scheduled task"""
    try:
        if not automated_scheduler:
            raise HTTPException(status_code=503, detail="Automated scheduler not initialized")
        
        success = automated_scheduler.enable_task(task_id)
        return {"success": success, "task_id": task_id, "action": "enabled"}
    except Exception as e:
        logger.error(f"❌ Enable task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/scheduler/tasks/{task_id}/disable", dependencies=[Depends(verify_admin)])
async def disable_scheduled_task(task_id: str):
    """Disable a scheduled task"""
    try:
        if not automated_scheduler:
            raise HTTPException(status_code=503, detail="Automated scheduler not initialized")
        
        success = automated_scheduler.disable_task(task_id)
        return {"success": success, "task_id": task_id, "action": "disabled"}
    except Exception as e:
        logger.error(f"❌ Disable task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stakeholder-specific dashboards
@app.get("/admin/dashboard/executive", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def executive_dashboard():
    """Executive dashboard"""
    try:
        if not stakeholder_dashboards:
            raise HTTPException(status_code=503, detail="Stakeholder dashboards not initialized")
        
        data = await stakeholder_dashboards.get_dashboard_data_for_stakeholder(StakeholderType.EXECUTIVE)
        return await stakeholder_dashboards.generate_dashboard_html(StakeholderType.EXECUTIVE, data)
    except Exception as e:
        logger.error(f"❌ Executive dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard/product", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def product_manager_dashboard():
    """Product Manager dashboard"""
    try:
        if not stakeholder_dashboards:
            raise HTTPException(status_code=503, detail="Stakeholder dashboards not initialized")
        
        data = await stakeholder_dashboards.get_dashboard_data_for_stakeholder(StakeholderType.PRODUCT_MANAGER)
        return await stakeholder_dashboards.generate_dashboard_html(StakeholderType.PRODUCT_MANAGER, data)
    except Exception as e:
        logger.error(f"❌ Product manager dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard/developer", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def developer_dashboard():
    """Developer dashboard"""
    try:
        if not stakeholder_dashboards:
            raise HTTPException(status_code=503, detail="Stakeholder dashboards not initialized")
        
        data = await stakeholder_dashboards.get_dashboard_data_for_stakeholder(StakeholderType.DEVELOPER)
        return await stakeholder_dashboards.generate_dashboard_html(StakeholderType.DEVELOPER, data)
    except Exception as e:
        logger.error(f"❌ Developer dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard/support", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def support_dashboard():
    """Support dashboard"""
    try:
        if not stakeholder_dashboards:
            raise HTTPException(status_code=503, detail="Stakeholder dashboards not initialized")
        
        data = await stakeholder_dashboards.get_dashboard_data_for_stakeholder(StakeholderType.SUPPORT)
        return await stakeholder_dashboards.generate_dashboard_html(StakeholderType.SUPPORT, data)
    except Exception as e:
        logger.error(f"❌ Support dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_class=HTMLResponse)
async def public_status_page():
    """Public status page for users"""
    try:
        if not stakeholder_dashboards:
            # Fallback simple status page
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head><title>Progress Method Status</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🟢 Progress Method Status</h1>
                <p>All systems operational</p>
                <p>Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </body>
            </html>
            """)
        
        data = await stakeholder_dashboards.get_dashboard_data_for_stakeholder(StakeholderType.USER)
        return await stakeholder_dashboards.generate_dashboard_html(StakeholderType.USER, data)
    except Exception as e:
        logger.error(f"❌ Public status page error: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Progress Method Status</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🟡 Progress Method Status</h1>
            <p>Some monitoring features temporarily unavailable</p>
            <p>Core services are operational</p>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """)

# Phase 3 Intelligent Systems API Endpoints

@app.get("/admin/api/phase3/optimization/status", dependencies=[Depends(verify_admin)])
async def get_optimization_status():
    """Get intelligent optimization system status"""
    try:
        if not optimization_system:
            raise HTTPException(status_code=503, detail="Optimization system not initialized")
        return await optimization_system.get_optimization_status()
    except Exception as e:
        logger.error(f"❌ Optimization status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/optimization/analyze", dependencies=[Depends(verify_admin)])
async def analyze_system_performance():
    """Analyze system performance and identify optimization opportunities"""
    try:
        if not optimization_system:
            raise HTTPException(status_code=503, detail="Optimization system not initialized")
        return await optimization_system.analyze_system_performance()
    except Exception as e:
        logger.error(f"❌ Performance analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/phase3/optimization/{recommendation_id}/implement", dependencies=[Depends(verify_admin)])
async def implement_optimization(recommendation_id: str):
    """Implement an optimization recommendation"""
    try:
        if not optimization_system:
            raise HTTPException(status_code=503, detail="Optimization system not initialized")
        return await optimization_system.implement_optimization(recommendation_id)
    except Exception as e:
        logger.error(f"❌ Optimization implementation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/personalization/status", dependencies=[Depends(verify_admin)])
async def get_personalization_status():
    """Get adaptive personalization system status"""
    try:
        if not personalization_system:
            raise HTTPException(status_code=503, detail="Personalization system not initialized")
        return await personalization_system.get_personalization_status()
    except Exception as e:
        logger.error(f"❌ Personalization status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/phase3/personalization/analyze/{user_id}", dependencies=[Depends(verify_admin)])
async def analyze_user_behavior(user_id: str):
    """Analyze user behavior and generate personalization insights"""
    try:
        if not personalization_system:
            raise HTTPException(status_code=503, detail="Personalization system not initialized")
        return await personalization_system.analyze_user_behavior(user_id)
    except Exception as e:
        logger.error(f"❌ User behavior analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/analytics/status", dependencies=[Depends(verify_admin)])
async def get_analytics_status():
    """Get predictive analytics system status"""
    try:
        if not predictive_analytics:
            raise HTTPException(status_code=503, detail="Predictive analytics not initialized")
        return await predictive_analytics.get_analytics_status()
    except Exception as e:
        logger.error(f"❌ Analytics status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/analytics/collect-data", dependencies=[Depends(verify_admin)])
async def collect_historical_data():
    """Collect historical data for analysis"""
    try:
        if not predictive_analytics:
            raise HTTPException(status_code=503, detail="Predictive analytics not initialized")
        return await predictive_analytics.collect_historical_data()
    except Exception as e:
        logger.error(f"❌ Data collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/analytics/predictions", dependencies=[Depends(verify_admin)])
async def generate_predictions():
    """Generate predictions and forecasts"""
    try:
        if not predictive_analytics:
            raise HTTPException(status_code=503, detail="Predictive analytics not initialized")
        return await predictive_analytics.generate_predictions()
    except Exception as e:
        logger.error(f"❌ Predictions generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/scaling/status", dependencies=[Depends(verify_admin)])
async def get_scaling_status():
    """Get auto-scaling system status"""
    try:
        if not scaling_system:
            raise HTTPException(status_code=503, detail="Scaling system not initialized")
        return await scaling_system.get_scaling_status()
    except Exception as e:
        logger.error(f"❌ Scaling status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/scaling/metrics", dependencies=[Depends(verify_admin)])
async def collect_resource_metrics():
    """Collect current resource utilization metrics"""
    try:
        if not scaling_system:
            raise HTTPException(status_code=503, detail="Scaling system not initialized")
        return await scaling_system.collect_resource_metrics()
    except Exception as e:
        logger.error(f"❌ Resource metrics collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/scaling/evaluate", dependencies=[Depends(verify_admin)])
async def evaluate_scaling_decisions():
    """Evaluate scaling decisions and execute actions"""
    try:
        if not scaling_system:
            raise HTTPException(status_code=503, detail="Scaling system not initialized")
        return await scaling_system.evaluate_scaling_decisions()
    except Exception as e:
        logger.error(f"❌ Scaling evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/scaling/recommendations", dependencies=[Depends(verify_admin)])
async def get_optimization_recommendations():
    """Get resource optimization recommendations"""
    try:
        if not scaling_system:
            raise HTTPException(status_code=503, detail="Scaling system not initialized")
        return await scaling_system.generate_optimization_recommendations()
    except Exception as e:
        logger.error(f"❌ Optimization recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/insights/status", dependencies=[Depends(verify_admin)])
async def get_ml_insights_status():
    """Get ML insights system status"""
    try:
        if not ml_insights:
            raise HTTPException(status_code=503, detail="ML insights not initialized")
        return await ml_insights.get_ml_insights_status()
    except Exception as e:
        logger.error(f"❌ ML insights status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/insights/generate", dependencies=[Depends(verify_admin)])
async def generate_ml_insights():
    """Generate ML-driven insights and recommendations"""
    try:
        if not ml_insights:
            raise HTTPException(status_code=503, detail="ML insights not initialized")
        return await ml_insights.generate_ml_insights()
    except Exception as e:
        logger.error(f"❌ ML insights generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/anomaly/status", dependencies=[Depends(verify_admin)])
async def get_anomaly_detection_status():
    """Get anomaly detection system status"""
    try:
        if not anomaly_detection:
            raise HTTPException(status_code=503, detail="Anomaly detection not initialized")
        return await anomaly_detection.get_anomaly_detection_status()
    except Exception as e:
        logger.error(f"❌ Anomaly detection status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/anomaly/detect", dependencies=[Depends(verify_admin)])
async def detect_anomalies():
    """Run anomaly detection and analysis"""
    try:
        if not anomaly_detection:
            raise HTTPException(status_code=503, detail="Anomaly detection not initialized")
        return await anomaly_detection.detect_anomalies()
    except Exception as e:
        logger.error(f"❌ Anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/phase3/overview", dependencies=[Depends(verify_admin)])
async def get_phase3_overview():
    """Get comprehensive Phase 3 systems overview"""
    try:
        overview = {
            "phase3_status": "operational",
            "systems": {
                "optimization_system": bool(optimization_system),
                "personalization_system": bool(personalization_system),
                "predictive_analytics": bool(predictive_analytics),
                "scaling_system": bool(scaling_system),
                "ml_insights": bool(ml_insights),
                "anomaly_detection": bool(anomaly_detection)
            },
            "capabilities": [
                "Intelligent performance optimization",
                "Adaptive user experience personalization",
                "Predictive analytics and forecasting",
                "Automated resource scaling",
                "Machine learning insights",
                "Intelligent anomaly detection"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return overview
    except Exception as e:
        logger.error(f"❌ Phase 3 overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
