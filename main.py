#!/usr/bin/env python3
"""
Enhanced main.py - Complete admin system with bot webhook support
Combines comprehensive admin features with Telegram bot functionality
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import json
import logging
from dotenv import load_dotenv
from collections import deque
from supabase import create_client
from essential_business_dashboard import add_business_metrics_routes
from nurture_control_dashboard import add_nurture_control_routes
from retro_admin_dashboard import add_retro_admin_routes
from retro_superadmin_dashboard import add_superadmin_routes
# Load environment
load_dotenv()

# Setup logging with in-memory storage for recent logs
recent_logs = deque(maxlen=100)  # Store last 100 log entries

class MemoryLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self.format(record)
        }
        recent_logs.append(log_entry)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add memory handler to capture logs
memory_handler = MemoryLogHandler()
memory_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(memory_handler)

try:
    from webhook_monitoring import add_webhook_monitoring_routes, track_webhook_request
    monitoring_available = True
except ImportError as e:
    logger.warning(f"Monitoring not available: {e}")
    monitoring_available = False
    def track_webhook_request(success: bool):
        pass  # No-op if monitoring not available

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing Supabase credentials")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized (v2)")

# Create FastAPI app
app = FastAPI(
    title="Progress Method - Complete System",
    description="Telegram bot with comprehensive admin dashboard",
    version="2.0.0"
)

# Admin authentication
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def verify_admin(api_key: Optional[str] = Depends(api_key_header)):
    """Verify admin API key"""
    admin_key = os.getenv("ADMIN_API_KEY")
    app_env = os.getenv("APP_ENV", "production")
    allow_unprotected = os.getenv("ALLOW_UNPROTECTED_ADMIN", "false").lower() == "true"
    
    if not admin_key:
        if app_env == "development" and allow_unprotected:
            logger.warning("⚠️ No ADMIN_API_KEY set - allowing unprotected access in development mode")
            return True
        else:
            logger.error("❌ ADMIN_API_KEY not configured - denying access")
            raise HTTPException(status_code=403, detail="Admin access required")
    
    if not api_key or api_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return True

# ========================================
# BASIC ENDPOINTS
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ Progress Method Bot is running!",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "bot": "active",
            "admin": "active", 
            "database": "connected" if supabase else "disconnected"
        },
        "environment_check": {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
        }
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "commitment-fix-v2"}

@app.get("/webhook/health")
async def webhook_health():
    """Specific health check for webhook functionality"""
    try:
        # Check if we can import bot components
        from telbot import bot, dp, config
        
        # Check environment variables
        env_status = {
            "BOT_TOKEN": bool(os.getenv("BOT_TOKEN")),
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY": bool(os.getenv("SUPABASE_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
        }
        
        missing_vars = [k for k, v in env_status.items() if not v]
        
        return {
            "status": "healthy" if not missing_vars else "degraded",
            "timestamp": datetime.now().isoformat(),
            "environment_variables": env_status,
            "missing_variables": missing_vars,
            "bot_configured": bool(bot),
            "dispatcher_configured": bool(dp)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "error_type": type(e).__name__
        }

# ========================================
# BOT WEBHOOK ENDPOINTS (CRITICAL - DON'T CHANGE)
# ========================================


# Add webhook monitoring routes
if monitoring_available:
    add_webhook_monitoring_routes(app)
    logger.info("✅ Webhook monitoring routes added")
else:
    logger.warning("⚠️ Webhook monitoring routes not available")

# Add essential business dashboard routes
add_business_metrics_routes(app)
add_nurture_control_routes(app)
add_superadmin_routes(app)
logger.info("✅ Essential dashboard routes added")

# Override admin dashboard with retro version
add_retro_admin_routes(app)
logger.info("✅ Retro admin dashboard added")
@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhooks from Telegram"""
    try:
        # Get request body
        data = await request.json()
        logger.info(f"Webhook received update_id: {data.get('update_id', 'unknown')}")
        
        # Validate basic structure
        if not isinstance(data, dict):
            logger.error("Invalid webhook data - not a dict")
            track_webhook_request(False)
            return {"ok": False, "error": "Invalid data format"}
        
        # Import bot components only when needed
        try:
            from telbot import bot, dp
            from aiogram.types import Update
        except ImportError as ie:
            logger.error(f"Import error: {ie}")
            track_webhook_request(False)
            return {"ok": False, "error": "Bot import failed"}
        
        # Validate Update object more safely
        try:
            update = Update.model_validate(data)
        except Exception as ve:
            logger.error(f"Validation error: {ve}")
            logger.error(f"Data structure: {json.dumps(data, indent=2)}")
            track_webhook_request(False)
            return {"ok": False, "error": f"Validation failed: {str(ve)}"}
        
        # Process update
        await dp.feed_update(bot, update)
        
        track_webhook_request(True)
        return {"ok": True}
        
    except json.JSONDecodeError as je:
        logger.error(f"JSON decode error: {je}")
        return {"ok": False, "error": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"ok": False, "error": str(e)}

@app.get("/set_webhook")
async def set_webhook():
    """Set webhook URL for Telegram"""
    try:
        from telbot import bot
        
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            raise HTTPException(status_code=400, detail="WEBHOOK_URL not configured")
        
        # Remove any existing webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Set new webhook
        success = await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        if success:
            info = await bot.get_webhook_info()
            return {
                "status": "Webhook set successfully",
                "url": info.url,
                "pending_updates": info.pending_update_count
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")
            
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook_info")
async def webhook_info():
    """Get current webhook information"""
    try:
        from telbot import bot
        
        info = await bot.get_webhook_info()
        return {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        logger.error(f"Webhook info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/tables")
async def debug_tables():
    """Debug endpoint to check table existence and schemas"""
    try:
        if not supabase:
            return {"error": "Supabase not initialized", "success": False}
        
        result = {"tables": {}, "timestamp": datetime.now().isoformat()}
        
        # Test users table
        try:
            users_result = supabase.table("users").select("*").limit(1).execute()
            result["tables"]["users"] = {
                "exists": True,
                "sample_data": users_result.data[0] if users_result.data else None,
                "count": len(users_result.data)
            }
        except Exception as e:
            result["tables"]["users"] = {"exists": False, "error": str(e)}
        
        # Test commitments table
        try:
            commitments_result = supabase.table("commitments").select("*").limit(1).execute()
            result["tables"]["commitments"] = {
                "exists": True,
                "sample_data": commitments_result.data[0] if commitments_result.data else None,
                "count": len(commitments_result.data)
            }
        except Exception as e:
            result["tables"]["commitments"] = {"exists": False, "error": str(e)}
            
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/debug/commitment/{telegram_user_id}")
async def debug_commitment_save(telegram_user_id: int):
    """Debug endpoint to test commitment saving process"""
    try:
        if not supabase:
            return {"error": "Supabase not initialized", "success": False}
        
        # Test 1: Check if user exists
        user_result = supabase.table("users").select("id, telegram_user_id, first_name").eq("telegram_user_id", telegram_user_id).execute()
        
        user_exists = bool(user_result.data)
        user_info = user_result.data[0] if user_result.data else None
        
        result = {
            "telegram_user_id": telegram_user_id,
            "user_exists": user_exists,
            "user_info": user_info,
            "database_connected": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test 2: If user exists, try to save a test commitment
        if user_exists:
            try:
                user_uuid = user_info["id"]
                test_commitment_data = {
                    "user_id": user_uuid,
                    "telegram_user_id": telegram_user_id,
                    "commitment": "DEBUG TEST COMMITMENT - IGNORE",
                    "original_commitment": "DEBUG TEST COMMITMENT - IGNORE",
                    "status": "active",
                    "smart_score": 1,
                    "created_at": datetime.now().isoformat()
                }
                
                # Try to insert test commitment
                commit_result = supabase.table("commitments").insert(test_commitment_data).execute()
                result["test_commitment_save"] = True
                result["test_commitment_id"] = commit_result.data[0]["id"] if commit_result.data else None
                
                # Clean up test commitment
                if result["test_commitment_id"]:
                    supabase.table("commitments").delete().eq("id", result["test_commitment_id"]).execute()
                    result["test_cleanup"] = True
                    
            except Exception as commit_error:
                result["test_commitment_save"] = False
                result["commitment_error"] = str(commit_error)
                result["commitment_error_type"] = type(commit_error).__name__
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

# ========================================
# TALLY FORM WEBHOOK
# ========================================

@app.post("/webhook/tally")
async def tally_webhook_handler(request: Request):
    """Handle incoming webhooks from Tally forms"""
    try:
        logger.info("📝 Received Tally webhook")
        
        # Get the form data from Tally
        data = await request.json()
        logger.info(f"Tally data received: {json.dumps(data, indent=2)}")
        
        if not supabase:
            logger.error("❌ Supabase not initialized")
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Extract form information
        form_id = data.get("formId", "unknown")
        form_name = data.get("formName", "Unknown Form")
        submission_id = data.get("submissionId")
        
        # Extract form fields
        fields = data.get("fields", {})
        
        # Map Tally fields to our database structure
        user_name = None
        user_email = None
        user_phone = None
        
        # Extract common fields from Tally response
        for field_id, field_data in fields.items():
            field_type = field_data.get("type", "")
            field_value = field_data.get("value")
            field_label = field_data.get("label", "").lower()
            
            # Map fields based on type and label
            if field_type == "INPUT_EMAIL" or "email" in field_label:
                user_email = field_value
            elif field_type == "INPUT_PHONE" or "phone" in field_label:
                user_phone = field_value
            elif field_type == "INPUT_TEXT" and ("name" in field_label or "call" in field_label):
                user_name = field_value
        
        # Create form submission record
        form_submission = {
            "form_type": "tally_submission",
            "form_data": {
                "form_id": form_id,
                "form_name": form_name,
                "submission_id": submission_id,
                "fields": fields,
                "raw_data": data
            },
            "user_name": user_name,
            "user_email": user_email,
            "user_phone": user_phone,
            "status": "pending",
            "source": "tally_webhook",
            "submitted_at": datetime.now().isoformat()
        }
        
        # Insert into database
        result = supabase.table("form_submissions").insert(form_submission).execute()
        
        if result.data:
            submission_record = result.data[0]
            logger.info(f"✅ Form submission saved with ID: {submission_record['id']}")
            
            # Log key details
            logger.info(f"📊 Form: {form_name} ({form_id})")
            if user_name:
                logger.info(f"👤 User: {user_name}")
            if user_email:
                logger.info(f"📧 Email: {user_email}")
            if user_phone:
                logger.info(f"📱 Phone: {user_phone}")
            
            # Trigger n8n workflow for processing
            try:
                n8n_webhook_url = "https://n8n-digital-ocean.theprogressmethod.com/webhook/4b6076c8-7e51-4a64-9416-f5904996db63"
                
                # Send the original data to n8n in the format it expects
                import httpx
                async with httpx.AsyncClient() as client:
                    n8n_response = await client.post(
                        n8n_webhook_url,
                        json=data,  # Send original Tally data
                        headers={"Content-Type": "application/json"},
                        timeout=10.0
                    )
                    
                if n8n_response.status_code == 200:
                    logger.info(f"✅ n8n workflow triggered successfully")
                else:
                    logger.warning(f"⚠️ n8n workflow trigger failed: {n8n_response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to trigger n8n workflow: {e}")
                # Don't fail the webhook if n8n is down
            
            return {
                "status": "success", 
                "message": "Form submission received and stored",
                "submission_id": submission_record['id'],
                "form_name": form_name,
                "n8n_triggered": True
            }
        else:
            logger.error("❌ Failed to save form submission")
            raise HTTPException(status_code=500, detail="Failed to save submission")
            
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"❌ Tally webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

# ========================================
# COMPREHENSIVE ADMIN DASHBOARD
# ========================================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Tabbed admin dashboard with dedicated sections for pods, users, and system health"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin Dashboard</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f7fa; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
            
            /* Tab Navigation */
            .tab-nav { display: flex; background: white; border-radius: 12px 12px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; overflow: hidden; }
            .tab-btn { flex: 1; padding: 20px; text-align: center; border: none; background: white; cursor: pointer; font-size: 1rem; font-weight: 600; color: #4a5568; transition: all 0.3s; border-bottom: 3px solid transparent; }
            .tab-btn:hover { background: #f7fafc; }
            .tab-btn.active { background: #4299e1; color: white; border-bottom-color: #2b6cb0; }
            
            /* Tab Content */
            .tab-content { display: none; background: white; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); padding: 30px; min-height: 600px; }
            .tab-content.active { display: block; }
            
            /* Dashboard Layout */
            .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metrics-overview { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            
            /* Cards */
            .card { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; margin-bottom: 20px; }
            .metric-card { background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; }
            .metric-card.users { background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%); }
            .metric-card.pods { background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%); }
            .metric-card.commitments { background: linear-gradient(135deg, #38a169 0%, #2f855a 100%); }
            .metric-card.health { background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%); }
            
            .card-header { padding: 20px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
            .card-body { padding: 20px; }
            .card-title { margin: 0; color: #2d3748; font-size: 1.25rem; font-weight: 600; }
            
            /* Metrics */
            .metric-value { font-size: 3rem; font-weight: bold; margin-bottom: 5px; }
            .metric-label { font-size: 1rem; opacity: 0.9; }
            .metric-change { font-size: 0.875rem; margin-top: 10px; }
            
            /* Buttons */
            .btn { background: #4299e1; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; margin: 5px; font-size: 0.875rem; font-weight: 500; transition: all 0.2s; }
            .btn:hover { background: #3182ce; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3); }
            .btn-success { background: #38a169; }
            .btn-success:hover { background: #2f855a; box-shadow: 0 4px 12px rgba(56, 161, 105, 0.3); }
            .btn-warning { background: #d69e2e; }
            .btn-warning:hover { background: #b7791f; box-shadow: 0 4px 12px rgba(214, 158, 46, 0.3); }
            .btn-danger { background: #e53e3e; }
            .btn-danger:hover { background: #c53030; box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3); }
            .btn-small { padding: 8px 16px; font-size: 0.75rem; }
            
            /* Tables */
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 15px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
            th { background: #f7fafc; font-weight: 600; color: #4a5568; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }
            tbody tr:hover { background: #f7fafc; }
            tbody tr { transition: background-color 0.2s; }
            
            /* Status badges */
            .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
            .status-active { background: #c6f6d5; color: #22543d; }
            .status-inactive { background: #fed7d7; color: #742a2a; }
            .status-completed { background: #bee3f8; color: #2a4365; }
            .status-warning { background: #faf089; color: #744210; }
            
            /* Controls */
            .admin-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
            .control-section { padding: 20px; background: #f7fafc; border-radius: 12px; border-left: 4px solid #4299e1; }
            .control-section h4 { margin-top: 0; color: #2d3748; }
            
            /* Utilities */
            .loading { color: #718096; font-style: italic; text-align: center; padding: 40px; }
            .error { color: #e53e3e; padding: 15px; background: #fed7d7; border-radius: 8px; border-left: 4px solid #e53e3e; }
            .success { color: #22543d; padding: 15px; background: #c6f6d5; border-radius: 8px; border-left: 4px solid #38a169; }
            .info { color: #2c5aa0; padding: 15px; background: #bee3f8; border-radius: 8px; border-left: 4px solid #3182ce; }
            
            /* Search and filters */
            .search-bar { width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px; font-size: 1rem; }
            .filter-group { display: flex; gap: 10px; margin-bottom: 20px; align-items: center; }
            .filter-group select { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; }
            
            /* Responsive */
            @media (max-width: 768px) {
                .tab-nav { flex-direction: column; }
                .metrics-overview { grid-template-columns: 1fr; }
                .dashboard-grid { grid-template-columns: 1fr; }
                .admin-controls { grid-template-columns: 1fr; }
                .container { padding: 10px; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Progress Method Admin Dashboard</h1>
            <p>Complete system management and monitoring</p>
            <div style="margin-top: 15px;">
                <button class="btn" onclick="refreshAllData()">🔄 Refresh All</button>
                <button class="btn btn-success" onclick="showQuickActions()">⚡ Quick Actions</button>
            </div>
        </div>
        
        <div class="container">
            <!-- Tab Navigation -->
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('overview')">📊 Overview</button>
                <button class="tab-btn" onclick="showTab('pods')">🎯 Pods</button>
                <button class="tab-btn" onclick="showTab('users')">👥 Users</button>
                <button class="tab-btn" onclick="showTab('health')">🏥 System Health</button>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content active">
                <h2 style="margin-top: 0; color: #2d3748;">System Overview</h2>
                
                <!-- Key Metrics -->
                <div class="metrics-overview">
                    <div class="metric-card users">
                        <div class="metric-value" id="overview-users">-</div>
                        <div class="metric-label">Total Users</div>
                        <div class="metric-change" id="overview-users-change">+0 this week</div>
                    </div>
                    <div class="metric-card pods">
                        <div class="metric-value" id="overview-pods">-</div>
                        <div class="metric-label">Active Pods</div>
                        <div class="metric-change" id="overview-pods-change">7 total created</div>
                    </div>
                    <div class="metric-card commitments">
                        <div class="metric-value" id="overview-commitments">-</div>
                        <div class="metric-label">Total Commitments</div>
                        <div class="metric-change" id="overview-commitments-change">+0 today</div>
                    </div>
                    <div class="metric-card health">
                        <div class="metric-value" id="overview-health">100%</div>
                        <div class="metric-label">System Health</div>
                        <div class="metric-change">All systems operational</div>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">📈 Recent Activity</h3>
                    </div>
                    <div class="card-body">
                        <div id="recent-activity" class="loading">Loading recent activity...</div>
                    </div>
                </div>
                
                <!-- Quick Stats -->
                <div class="dashboard-grid">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">📊 User Distribution</h3>
                        </div>
                        <div class="card-body">
                            <div id="user-distribution" class="loading">Loading user distribution...</div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">🎯 Pod Utilization</h3>
                        </div>
                        <div class="card-body">
                            <div id="pod-utilization" class="loading">Loading pod utilization...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Pods Tab -->
            <div id="pods-tab" class="tab-content">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #2d3748;">Pod Management</h2>
                    <div>
                        <button class="btn btn-success" onclick="showCreatePod()">➕ Create Pod</button>
                        <button class="btn" onclick="loadPods()">🔄 Refresh</button>
                    </div>
                </div>
                
                <!-- Pod Filters -->
                <div class="filter-group">
                    <label>Filter by status:</label>
                    <select id="pod-status-filter" onchange="filterPods()">
                        <option value="all">All Pods</option>
                        <option value="active">Active Only</option>
                        <option value="inactive">Inactive Only</option>
                    </select>
                    <label>Sort by:</label>
                    <select id="pod-sort" onchange="sortPods()">
                        <option value="name">Name</option>
                        <option value="members">Member Count</option>
                        <option value="created">Date Created</option>
                    </select>
                </div>
                
                <!-- Pod Actions -->
                <div class="admin-controls">
                    <div class="control-section">
                        <h4>🎯 Pod Operations</h4>
                        <button class="btn btn-success" onclick="showCreatePod()">Create New Pod</button>
                        <button class="btn btn-warning" onclick="showBulkAssignUsers()">Bulk Assign Users</button>
                        <button class="btn" onclick="exportPodData()">Export Pod Data</button>
                    </div>
                    <div class="control-section">
                        <h4>📊 Pod Analytics</h4>
                        <button class="btn" onclick="generatePodReport()">Generate Report</button>
                        <button class="btn" onclick="showPodMetrics()">View Metrics</button>
                        <button class="btn" onclick="analyzePodHealth()">Health Analysis</button>
                    </div>
                </div>
                
                <!-- Pod List -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🎯 All Pods</h3>
                    </div>
                    <div class="card-body">
                        <div id="pods-list" class="loading">Loading pods...</div>
                    </div>
                </div>
            </div>
            
            <!-- Users Tab -->
            <div id="users-tab" class="tab-content">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #2d3748;">User Management</h2>
                    <div>
                        <button class="btn btn-warning" onclick="showGrantRole()">👑 Grant Role</button>
                        <button class="btn" onclick="loadUsers()">🔄 Refresh</button>
                    </div>
                </div>
                
                <!-- User Search and Filters -->
                <input type="text" id="user-search" class="search-bar" placeholder="Search users by name, username, or Telegram ID..." onkeyup="filterUsers()">
                
                <div class="filter-group">
                    <label>Filter by role:</label>
                    <select id="user-role-filter" onchange="filterUsers()">
                        <option value="all">All Roles</option>
                        <option value="unpaid">Unpaid</option>
                        <option value="pod_member">Pod Members</option>
                        <option value="admin">Admins</option>
                        <option value="super_admin">Super Admins</option>
                    </select>
                    <label>Sort by:</label>
                    <select id="user-sort" onchange="sortUsers()">
                        <option value="name">Name</option>
                        <option value="joined">Date Joined</option>
                        <option value="commitments">Commitments</option>
                    </select>
                </div>
                
                <!-- User Actions -->
                <div class="admin-controls">
                    <div class="control-section">
                        <h4>👥 User Operations</h4>
                        <button class="btn btn-warning" onclick="showGrantRole()">Grant Role</button>
                        <button class="btn btn-danger" onclick="showRevokeRole()">Revoke Role</button>
                        <button class="btn" onclick="exportUserData()">Export Users</button>
                    </div>
                    <div class="control-section">
                        <h4>📊 User Analytics</h4>
                        <button class="btn" onclick="generateUserReport()">Generate Report</button>
                        <button class="btn" onclick="analyzeUserEngagement()">Engagement Analysis</button>
                        <button class="btn" onclick="showUserMetrics()">View Metrics</button>
                    </div>
                </div>
                
                <!-- User List -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">👥 All Users</h3>
                    </div>
                    <div class="card-body">
                        <div id="users-list" class="loading">Loading users...</div>
                    </div>
                </div>
            </div>
            
            <!-- System Health Tab -->
            <div id="health-tab" class="tab-content">
                <h2 style="margin-top: 0; color: #2d3748;">System Health & Monitoring</h2>
                
                <!-- Health Overview -->
                <div class="dashboard-grid">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">🤖 Bot Status</h3>
                        </div>
                        <div class="card-body">
                            <button class="btn" onclick="checkBotHealth()">🔍 Check Bot Health</button>
                            <button class="btn" onclick="refreshWebhook()">🔄 Refresh Webhook</button>
                            <div id="bot-health-status" style="margin-top: 15px;">
                                <div class="info">Bot health check not run yet</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">🗄️ Database Status</h3>
                        </div>
                        <div class="card-body">
                            <button class="btn" onclick="checkDbHealth()">🔍 Check Database</button>
                            <button class="btn" onclick="runDbDiagnostics()">🩺 Run Diagnostics</button>
                            <div id="db-health-status" style="margin-top: 15px;">
                                <div class="info">Database health check not run yet</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">⚡ Performance</h3>
                        </div>
                        <div class="card-body">
                            <button class="btn" onclick="checkPerformance()">📊 Check Performance</button>
                            <button class="btn" onclick="clearCaches()">🧹 Clear Caches</button>
                            <div id="performance-status" style="margin-top: 15px;">
                                <div class="info">Performance check not run yet</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">📊 API Status</h3>
                        </div>
                        <div class="card-body">
                            <button class="btn" onclick="testAllAPIs()">🧪 Test All APIs</button>
                            <button class="btn" onclick="checkApiLimits()">📏 Check Limits</button>
                            <div id="api-status" style="margin-top: 15px;">
                                <div class="info">API status check not run yet</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- System Logs -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">📋 Recent System Activity</h3>
                    </div>
                    <div class="card-body">
                        <button class="btn" onclick="loadSystemLogs()">🔄 Refresh Logs</button>
                        <button class="btn btn-warning" onclick="downloadLogs()">📥 Download Logs</button>
                        <div id="system-logs" class="loading">Loading system logs...</div>
                    </div>
                </div>
                
                <!-- Emergency Controls -->
                <div class="card" style="border-left: 4px solid #e53e3e;">
                    <div class="card-header" style="background: #fed7d7;">
                        <h3 class="card-title" style="color: #742a2a;">🚨 Emergency Controls</h3>
                    </div>
                    <div class="card-body">
                        <div class="admin-controls">
                            <div class="control-section" style="border-left-color: #e53e3e;">
                                <h4>🛑 Emergency Actions</h4>
                                <button class="btn btn-danger" onclick="emergencyDisableBot()">Disable Bot</button>
                                <button class="btn btn-danger" onclick="emergencyMaintenanceMode()">Maintenance Mode</button>
                            </div>
                            <div class="control-section" style="border-left-color: #d69e2e;">
                                <h4>🔧 System Recovery</h4>
                                <button class="btn btn-warning" onclick="restartServices()">Restart Services</button>
                                <button class="btn btn-warning" onclick="clearAllCaches()">Clear All Caches</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Global state
            let allUsers = [];
            let allPods = [];
            let systemMetrics = {};
            let filteredUsers = [];
            let filteredPods = [];

            // Tab management
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
                
                // Load data for the tab
                switch(tabName) {
                    case 'overview':
                        loadOverviewData();
                        break;
                    case 'pods':
                        loadPods();
                        break;
                    case 'users':
                        loadUsers();
                        break;
                    case 'health':
                        loadHealthData();
                        break;
                }
            }

            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                loadOverviewData();
                // Auto-refresh overview every 5 minutes
                setInterval(loadOverviewData, 300000);
            });

            // Overview functions
            async function loadOverviewData() {
                await Promise.all([
                    loadMetrics(),
                    loadRecentActivity(),
                    loadUserDistribution(),
                    loadPodUtilization()
                ]);
            }

            async function loadMetrics() {
                try {
                    const response = await fetch('/admin/api/metrics');
                    const data = await response.json();
                    systemMetrics = data;
                    
                    // Update overview metrics
                    document.getElementById('overview-users').textContent = data.total_users || 0;
                    document.getElementById('overview-pods').textContent = data.total_pods || 0;
                    document.getElementById('overview-commitments').textContent = data.total_commitments || 0;
                    
                    // Update metric cards on other tabs too
                    if (document.getElementById('metrics')) {
                        document.getElementById('metrics').innerHTML = `
                            <div class="metrics-grid">
                                <div class="metric metric-users">
                                    <div class="metric-value">${data.total_users || 0}</div>
                                    <div class="metric-label">Total Users</div>
                                </div>
                                <div class="metric metric-commitments">
                                    <div class="metric-value">${data.total_commitments || 0}</div>
                                    <div class="metric-label">Total Commitments</div>
                                </div>
                                <div class="metric metric-active">
                                    <div class="metric-value">${data.active_commitments || 0}</div>
                                    <div class="metric-label">Active Commitments</div>
                                </div>
                                <div class="metric metric-pods">
                                    <div class="metric-value">${data.total_pods || 0}</div>
                                    <div class="metric-label">Active Pods</div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; color: #718096; font-size: 0.875rem;">
                                Last updated: ${new Date(data.timestamp).toLocaleString()}
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Error loading metrics:', error);
                }
            }

            async function loadRecentActivity() {
                try {
                    const [commitmentsRes, usersRes] = await Promise.all([
                        fetch('/admin/api/commitments'),
                        fetch('/admin/api/users')
                    ]);
                    
                    const commitments = await commitmentsRes.json();
                    const users = await usersRes.json();
                    
                    let activityHtml = '<div class="dashboard-grid">';
                    
                    // Recent commitments
                    activityHtml += '<div><h4>📝 Latest Commitments</h4>';
                    if (commitments.commitments && commitments.commitments.length > 0) {
                        commitments.commitments.slice(0, 5).forEach(c => {
                            activityHtml += `<div style="padding: 10px; margin: 5px 0; background: #f7fafc; border-radius: 6px;">
                                <strong>User ${c.telegram_user_id}</strong>: ${(c.commitment || '').substring(0, 80)}...
                                <div style="color: #718096; font-size: 0.875rem; margin-top: 5px;">
                                    ${new Date(c.created_at).toLocaleDateString()}
                                </div>
                            </div>`;
                        });
                    } else {
                        activityHtml += '<div class="info">No recent commitments</div>';
                    }
                    activityHtml += '</div>';
                    
                    // Recent users
                    activityHtml += '<div><h4>👥 New Users</h4>';
                    if (users.users && users.users.length > 0) {
                        users.users.slice(0, 5).forEach(u => {
                            activityHtml += `<div style="padding: 10px; margin: 5px 0; background: #f7fafc; border-radius: 6px;">
                                <strong>${u.first_name || 'Unknown'}</strong> (@${u.username || 'no-username'})
                                <div style="color: #718096; font-size: 0.875rem; margin-top: 5px;">
                                    Joined ${new Date(u.created_at).toLocaleDateString()}
                                </div>
                            </div>`;
                        });
                    } else {
                        activityHtml += '<div class="info">No recent users</div>';
                    }
                    activityHtml += '</div></div>';
                    
                    document.getElementById('recent-activity').innerHTML = activityHtml;
                } catch (error) {
                    document.getElementById('recent-activity').innerHTML = '<div class="error">Error loading activity</div>';
                }
            }

            async function loadUserDistribution() {
                try {
                    const response = await fetch('/admin/api/users');
                    const data = await response.json();
                    
                    const roleDistribution = {};
                    data.users.forEach(user => {
                        const role = user.role || 'unpaid';
                        roleDistribution[role] = (roleDistribution[role] || 0) + 1;
                    });
                    
                    let html = '<div style="display: grid; gap: 10px;">';
                    Object.entries(roleDistribution).forEach(([role, count]) => {
                        const percentage = ((count / data.users.length) * 100).toFixed(1);
                        html += `<div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="status-badge status-active">${role}</span>
                            <span><strong>${count}</strong> (${percentage}%)</span>
                        </div>`;
                    });
                    html += '</div>';
                    
                    document.getElementById('user-distribution').innerHTML = html;
                } catch (error) {
                    document.getElementById('user-distribution').innerHTML = '<div class="error">Error loading distribution</div>';
                }
            }

            async function loadPodUtilization() {
                try {
                    const response = await fetch('/admin/api/pods');
                    const data = await response.json();
                    
                    let html = '<div style="display: grid; gap: 10px;">';
                    if (data.pods && data.pods.length > 0) {
                        data.pods.forEach(pod => {
                            const utilization = pod.member_count > 0 ? 'Active' : 'Available';
                            const statusClass = pod.member_count > 0 ? 'status-active' : 'status-warning';
                            html += `<div style="display: flex; justify-content: space-between; align-items: center;">
                                <span><strong>${pod.name}</strong></span>
                                <div>
                                    <span>${pod.member_count} members</span>
                                    <span class="status-badge ${statusClass}">${utilization}</span>
                                </div>
                            </div>`;
                        });
                    } else {
                        html += '<div class="info">No pods found</div>';
                    }
                    html += '</div>';
                    
                    document.getElementById('pod-utilization').innerHTML = html;
                } catch (error) {
                    document.getElementById('pod-utilization').innerHTML = '<div class="error">Error loading utilization</div>';
                }
            }

            // Pod management functions
            async function loadPods() {
                try {
                    const response = await fetch('/admin/api/pods');
                    const data = await response.json();
                    allPods = data.pods || [];
                    filteredPods = [...allPods];
                    displayPods();
                } catch (error) {
                    document.getElementById('pods-list').innerHTML = '<div class="error">Error loading pods: ' + error + '</div>';
                }
            }

            function displayPods() {
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>Pod Name</th>
                                <th>Description</th>
                                <th>Members</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                if (filteredPods.length > 0) {
                    filteredPods.forEach(pod => {
                        html += `<tr>
                            <td><strong>${pod.name}</strong></td>
                            <td>${pod.description || 'No description'}</td>
                            <td>
                                <span class="status-badge ${pod.member_count > 0 ? 'status-active' : 'status-warning'}">
                                    ${pod.member_count || 0} members
                                </span>
                            </td>
                            <td>
                                <span class="status-badge ${pod.is_active ? 'status-active' : 'status-inactive'}">
                                    ${pod.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${new Date(pod.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-small" onclick="managePod('${pod.id}')">Manage</button>
                                <button class="btn btn-small btn-warning" onclick="assignUsersToPod('${pod.id}')">Assign Users</button>
                            </td>
                        </tr>`;
                    });
                } else {
                    html += '<tr><td colspan="6" style="text-align: center; color: #718096;">No pods found</td></tr>';
                }
                
                html += '</tbody></table>';
                document.getElementById('pods-list').innerHTML = html;
            }

            function filterPods() {
                const statusFilter = document.getElementById('pod-status-filter').value;
                
                filteredPods = allPods.filter(pod => {
                    if (statusFilter === 'all') return true;
                    if (statusFilter === 'active') return pod.is_active;
                    if (statusFilter === 'inactive') return !pod.is_active;
                    return true;
                });
                
                sortPods();
            }

            function sortPods() {
                const sortBy = document.getElementById('pod-sort').value;
                
                filteredPods.sort((a, b) => {
                    switch(sortBy) {
                        case 'name':
                            return a.name.localeCompare(b.name);
                        case 'members':
                            return (b.member_count || 0) - (a.member_count || 0);
                        case 'created':
                            return new Date(b.created_at) - new Date(a.created_at);
                        default:
                            return 0;
                    }
                });
                
                displayPods();
            }

            // User management functions
            async function loadUsers() {
                try {
                    const response = await fetch('/admin/api/users');
                    const data = await response.json();
                    allUsers = data.users || [];
                    filteredUsers = [...allUsers];
                    displayUsers();
                } catch (error) {
                    document.getElementById('users-list').innerHTML = '<div class="error">Error loading users: ' + error + '</div>';
                }
            }

            function displayUsers() {
                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Username</th>
                                <th>Telegram ID</th>
                                <th>Roles</th>
                                <th>Commitments</th>
                                <th>Joined</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                if (filteredUsers.length > 0) {
                    filteredUsers.forEach(user => {
                        html += `<tr>
                            <td><strong>${user.first_name || 'Unknown'}</strong></td>
                            <td>@${user.username || 'no-username'}</td>
                            <td>${user.telegram_user_id}</td>
                            <td><span class="status-badge status-active">${user.role || 'unpaid'}</span></td>
                            <td>${user.total_commitments || 0}</td>
                            <td>${new Date(user.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-small" onclick="manageUser(${user.telegram_user_id})">Manage</button>
                                <button class="btn btn-small btn-warning" onclick="showGrantRoleFor(${user.telegram_user_id})">Grant Role</button>
                            </td>
                        </tr>`;
                    });
                } else {
                    html += '<tr><td colspan="7" style="text-align: center; color: #718096;">No users found</td></tr>';
                }
                
                html += '</tbody></table>';
                document.getElementById('users-list').innerHTML = html;
            }

            function filterUsers() {
                const searchTerm = document.getElementById('user-search').value.toLowerCase();
                const roleFilter = document.getElementById('user-role-filter').value;
                
                filteredUsers = allUsers.filter(user => {
                    const matchesSearch = !searchTerm || 
                        (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
                        (user.username && user.username.toLowerCase().includes(searchTerm)) ||
                        (user.telegram_user_id && user.telegram_user_id.toString().includes(searchTerm));
                    
                    const matchesRole = roleFilter === 'all' || 
                        (user.role && user.role.includes(roleFilter));
                    
                    return matchesSearch && matchesRole;
                });
                
                sortUsers();
            }

            function sortUsers() {
                const sortBy = document.getElementById('user-sort').value;
                
                filteredUsers.sort((a, b) => {
                    switch(sortBy) {
                        case 'name':
                            return (a.first_name || '').localeCompare(b.first_name || '');
                        case 'joined':
                            return new Date(b.created_at) - new Date(a.created_at);
                        case 'commitments':
                            return (b.total_commitments || 0) - (a.total_commitments || 0);
                        default:
                            return 0;
                    }
                });
                
                displayUsers();
            }

            // Health monitoring functions
            async function loadHealthData() {
                // Health data loads on demand when buttons are clicked
                console.log('Health tab loaded - use buttons to check individual components');
            }

            async function checkBotHealth() {
                try {
                    const response = await fetch('/webhook_info');
                    const data = await response.json();
                    document.getElementById('bot-health-status').innerHTML = 
                        `<div class="success">✅ Bot Online - Webhook: ${data.url || 'Not configured'}</div>`;
                } catch (error) {
                    document.getElementById('bot-health-status').innerHTML = 
                        `<div class="error">❌ Bot check failed: ${error.message}</div>`;
                }
            }

            async function checkDbHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('db-health-status').innerHTML = 
                        `<div class="success">✅ Database: ${data.status}</div>`;
                } catch (error) {
                    document.getElementById('db-health-status').innerHTML = 
                        `<div class="error">❌ Database check failed: ${error.message}</div>`;
                }
            }

            // Action functions
            function showCreatePod() {
                const name = prompt("Enter pod name:");
                if (!name) return;
                
                const description = prompt("Enter pod description (optional):") || "";
                createPod(name, description);
            }

            async function createPod(name, description) {
                try {
                    const response = await fetch('/admin/api/pods', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, description })
                    });
                    
                    if (response.ok) {
                        alert('Pod created successfully!');
                        await loadPods();
                        await loadOverviewData();
                    } else {
                        const error = await response.json();
                        alert('Error: ' + error.detail);
                    }
                } catch (error) {
                    alert('Error creating pod: ' + error);
                }
            }

            function showGrantRole() {
                const telegramId = prompt("Enter Telegram User ID:");
                if (!telegramId) return;
                
                const role = prompt("Enter role (paid, pod_member, admin, super_admin):");
                if (!role) return;
                
                grantRole(parseInt(telegramId), role);
            }

            function showGrantRoleFor(telegramId) {
                const role = prompt("Enter role (paid, pod_member, admin, super_admin):");
                if (!role) return;
                
                grantRole(telegramId, role);
            }

            async function grantRole(telegramUserId, role) {
                try {
                    const response = await fetch(`/admin/api/users/${telegramUserId}/grant-role?role=${role}`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        alert('Role granted successfully!');
                        await loadUsers();
                        await loadOverviewData();
                    } else {
                        const error = await response.json();
                        alert('Error: ' + error.detail);
                    }
                } catch (error) {
                    alert('Error granting role: ' + error);
                }
            }

            // Utility functions
            async function refreshAllData() {
                await loadOverviewData();
                if (document.getElementById('pods-tab').classList.contains('active')) {
                    await loadPods();
                }
                if (document.getElementById('users-tab').classList.contains('active')) {
                    await loadUsers();
                }
            }

            function showQuickActions() {
                alert('Quick Actions menu - Feature coming soon!');
            }

            // Placeholder functions for advanced features
            function managePod(podId) { alert(`Pod management for ${podId} - Feature coming soon!`); }
            function manageUser(telegramUserId) { alert(`User management for ${telegramUserId} - Feature coming soon!`); }
            function assignUsersToPod(podId) { alert(`User assignment for pod ${podId} - Feature coming soon!`); }
            function showBulkAssignUsers() { alert('Bulk user assignment - Feature coming soon!'); }
            function exportPodData() { alert('Pod data export - Feature coming soon!'); }
            function exportUserData() { alert('User data export - Feature coming soon!'); }
            function generatePodReport() { alert('Pod report generation - Feature coming soon!'); }
            function generateUserReport() { alert('User report generation - Feature coming soon!'); }
            function showPodMetrics() { alert('Pod metrics - Feature coming soon!'); }
            function showUserMetrics() { alert('User metrics - Feature coming soon!'); }
            function analyzePodHealth() { alert('Pod health analysis - Feature coming soon!'); }
            function analyzeUserEngagement() { alert('User engagement analysis - Feature coming soon!'); }
            function showRevokeRole() { alert('Role revocation - Feature coming soon!'); }
            function refreshWebhook() { alert('Webhook refresh - Feature coming soon!'); }
            function runDbDiagnostics() { alert('Database diagnostics - Feature coming soon!'); }
            function checkPerformance() { alert('Performance check - Feature coming soon!'); }
            function clearCaches() { alert('Cache clearing - Feature coming soon!'); }
            function testAllAPIs() { alert('API testing - Feature coming soon!'); }
            function checkApiLimits() { alert('API limits check - Feature coming soon!'); }
            function loadSystemLogs() { alert('System logs - Feature coming soon!'); }
            function downloadLogs() { alert('Log download - Feature coming soon!'); }
            function emergencyDisableBot() { if(confirm('Disable bot?')) alert('Bot disabled - Feature coming soon!'); }
            function emergencyMaintenanceMode() { if(confirm('Enable maintenance mode?')) alert('Maintenance mode - Feature coming soon!'); }
            function restartServices() { if(confirm('Restart services?')) alert('Services restarted - Feature coming soon!'); }
            function clearAllCaches() { if(confirm('Clear all caches?')) alert('Caches cleared - Feature coming soon!'); }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ========================================
# ADMIN API ENDPOINTS
# ========================================

@app.get("/admin/api/metrics")
async def get_metrics():
    """Get comprehensive system metrics"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Get user count
        users = supabase.table("users").select("id", count="exact").execute()
        total_users = users.count if users.count else 0
        
        # Get commitment counts
        commitments = supabase.table("commitments").select("id", count="exact").execute()
        total_commitments = commitments.count if commitments.count else 0
        
        active_commitments = supabase.table("commitments").select("id", count="exact").eq("status", "active").execute()
        active_count = active_commitments.count if active_commitments.count else 0
        
        # Get pod count
        pods = supabase.table("pods").select("id", count="exact").eq("status", "active").execute()
        total_pods = pods.count if pods.count else 0
        
        return {
            "total_users": total_users,
            "total_commitments": total_commitments,
            "active_commitments": active_count,
            "total_pods": total_pods,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/users")
async def get_users():
    """Get all users with their roles"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Get users
        users = supabase.table("users").select("*").order("created_at", desc=True).limit(100).execute()
        
        # Get user roles for each user
        user_data = []
        for user in users.data:
            user_id = user.get("id")
            
            # Get user roles
            roles = supabase.table("user_roles").select("role_type").eq("user_id", user_id).eq("is_active", True).execute()
            user_roles = [r["role_type"] for r in roles.data] if roles.data else ["unpaid"]
            
            user_data.append({
                "id": user_id,
                "telegram_user_id": user.get("telegram_user_id"),
                "first_name": user.get("first_name"),
                "username": user.get("username"),
                "role": ", ".join(user_roles),
                "total_commitments": user.get("total_commitments", 0),
                "created_at": user.get("created_at")
            })
        
        return {"users": user_data, "count": len(user_data)}
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/commitments")
async def get_commitments():
    """Get recent commitments"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        commitments = supabase.table("commitments").select("*").order("created_at", desc=True).limit(50).execute()
        
        return {"commitments": commitments.data, "count": len(commitments.data)}
    except Exception as e:
        logger.error(f"Error getting commitments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/pods")
async def get_pods():
    """Get all pods with member counts"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        pods = supabase.table("pods").select("*").order("created_at", desc=True).execute()
        
        # Simplified: skip member count for now to debug the issue
        pod_data = []
        for pod in pods.data:
            pod_data.append({
                "id": pod.get("id"),
                "name": pod.get("name"),
                "description": pod.get("description"),
                "member_count": 0,  # Temporarily set to 0 to debug
                "is_active": pod.get("status") == "active",
                "created_at": pod.get("created_at")
            })
        
        return {"pods": pod_data, "count": len(pod_data)}
    except Exception as e:
        logger.error(f"Error getting pods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/users/{telegram_user_id}/grant-role")
async def grant_user_role(telegram_user_id: int, role: str):
    """Grant a role to a user"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Validate role
        valid_roles = ["paid", "pod_member", "admin", "super_admin", "beta_tester"]
        if role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Get user by telegram_user_id
        user = supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user.data[0]["id"]
        
        # Check if role already exists
        existing = supabase.table("user_roles").select("id").eq("user_id", user_id).eq("role_type", role).eq("is_active", True).execute()
        if existing.data:
            return {"message": f"User already has role {role}"}
        
        # Grant role
        role_data = {
            "user_id": user_id,
            "role_type": role,
            "is_active": True,
            "granted_at": datetime.now().isoformat(),
            "granted_by": "admin_dashboard"
        }
        
        result = supabase.table("user_roles").insert(role_data).execute()
        
        return {"message": f"Role {role} granted to user {telegram_user_id}", "role_id": result.data[0]["id"]}
    except Exception as e:
        logger.error(f"Error granting role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/pods/simple")
async def get_pods_simple():
    """Get simple pod list for debugging"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Simple query with minimal processing
        pods = supabase.table("pods").select("id, name, status, created_at").execute()
        
        return {
            "total_count": len(pods.data),
            "pods": [
                {
                    "id": pod["id"],
                    "name": pod["name"], 
                    "status": pod.get("status"),
                    "is_active": pod.get("status") == "active"
                }
                for pod in pods.data
            ]
        }
    except Exception as e:
        logger.error(f"Error getting simple pods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/pods")
async def create_pod(request: Request):
    """Create a new pod"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        data = await request.json()
        name = data.get("name")
        description = data.get("description", "")
        
        if not name:
            raise HTTPException(status_code=400, detail="Pod name is required")
        
        # Create pod with only fields that definitely exist
        pod_data = {
            "name": name,
            "status": "active"
        }
        
        # Only add description if provided and handle schema issues gracefully
        if description:
            pod_data["description"] = description
        
        result = supabase.table("pods").insert(pod_data).execute()
        
        return {"message": f"Pod '{name}' created successfully", "pod_id": result.data[0]["id"]}
    except Exception as e:
        logger.error(f"Error creating pod: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent_logs")
async def get_recent_logs(limit: int = 50):
    """Get recent log entries for debugging"""
    try:
        # Convert deque to list and get last N entries
        logs_list = list(recent_logs)
        return {
            "logs": logs_list[-limit:] if len(logs_list) > limit else logs_list,
            "total_captured": len(logs_list),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "success": False}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)