#!/usr/bin/env python3
"""
Week 1 MVP Main Application
===========================
Unified service with bot, API, and dashboard routes
"""

import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import components
try:
    from supabase import create_client
    from dashboard_crud_routes import create_crud_router
    from user_dashboard_template import get_user_dashboard_html
    from unified_admin_dashboard import create_unified_admin_dashboard
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase = create_client(supabase_url, supabase_key)

# Admin API Key protection
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)
admin_key = os.getenv("ADMIN_API_KEY")

if not admin_key:
    logger.warning("⚠️ No ADMIN_API_KEY set - admin routes are unprotected!")

async def verify_admin(api_key: Optional[str] = Depends(api_key_header)):
    """Verify admin API key"""
    if not admin_key:
        return True  # Allow if no key is set (development)
    
    if not api_key or api_key != admin_key:
        raise HTTPException(status_code=401, detail="Invalid or missing admin API key")
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Week 1 MVP starting up...")
    yield
    logger.info("🛑 Week 1 MVP shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Week 1 MVP - The Progress Method", 
    description="Unified bot and dashboard service",
    version="1.0.0",
    lifespan=lifespan
)

# Health endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "week1-mvp-v1.0",
        "components": {
            "database": "connected",
            "admin": "active",
            "dashboards": "active"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Week 1 MVP - The Progress Method",
        "status": "✅ Running!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "user_dashboard": "/dashboard?user_id=YOUR_USER_ID",
            "admin_dashboard": "/admin/week1",
            "api_docs": "/docs"
        }
    }

# User Dashboard Route
@app.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(user_id: str):
    """Week 1 MVP User Dashboard"""
    try:
        # Get user data
        user_result = supabase.table("users").select("*").eq("telegram_user_id", int(user_id)).execute()
        
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_result.data[0]
        
        # Get user commitments
        commitments_result = supabase.table("commitments").select("*").eq("telegram_user_id", int(user_id)).order("created_at", desc=True).execute()
        
        commitments = commitments_result.data if commitments_result.data else []
        
        # Calculate stats
        total_commitments = len(commitments)
        completed_commitments = len([c for c in commitments if c.get("status") == "completed"])
        
        dashboard_data = {
            "user": user,
            "commitments": commitments,
            "stats": {
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "success_rate": round((completed_commitments / total_commitments * 100) if total_commitments > 0 else 0, 1)
            }
        }
        
        return get_user_dashboard_html(dashboard_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return HTMLResponse(f"<h1>Dashboard Error</h1><p>{str(e)}</p>", status_code=500)

# Admin Dashboard Route
@app.get("/admin/week1", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def admin_dashboard():
    """Week 1 MVP Admin Dashboard"""
    try:
        # Get all users
        users_result = supabase.table("users").select("*").order("created_at", desc=True).execute()
        users = users_result.data if users_result.data else []
        
        # Get all pods
        pods_result = supabase.table("pods").select("*").order("created_at", desc=True).execute()
        pods = pods_result.data if pods_result.data else []
        
        # Get recent commitments
        commitments_result = supabase.table("commitments").select("*").order("created_at", desc=True).limit(50).execute()
        commitments = commitments_result.data if commitments_result.data else []
        
        admin_data = {
            "users": users,
            "pods": pods, 
            "commitments": commitments,
            "stats": {
                "total_users": len(users),
                "total_pods": len(pods),
                "total_commitments": len(commitments)
            }
        }
        
        return create_unified_admin_dashboard(admin_data)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        return HTMLResponse(f"<h1>Admin Error</h1><p>{str(e)}</p>", status_code=500)

# Include CRUD API routes
try:
    crud_router = create_crud_router(supabase, None)  # pod_system not needed for Week 1 MVP
    app.include_router(crud_router)
except Exception as e:
    logger.error(f"Could not include CRUD router: {e}")

# Telegram Bot Webhook (simplified)
@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram bot webhook"""
    try:
        update = await request.json()
        
        # Basic bot response - you can enhance this
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_message = update["message"]["text"]
            
            # Simple response
            if user_message.startswith("/start"):
                response_text = "🎯 Welcome to The Progress Method! Your Week 1 MVP is live!"
            elif user_message.startswith("/dashboard"):
                user_id = update["message"]["from"]["id"]
                response_text = f"📊 Your dashboard: https://telbot-production.onrender.com/dashboard?user_id={user_id}"
            else:
                response_text = "✅ Your message was received! Week 1 MVP is running."
            
            # Send response back to Telegram
            bot_token = os.getenv("BOT_TOKEN")
            if bot_token:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={"chat_id": chat_id, "text": response_text}
                    )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)