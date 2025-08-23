#!/usr/bin/env python3
"""
DASHBOARD ROUTES FOR 1.0 LAUNCH
================================
Additional FastAPI routes for admin and user dashboards
To be integrated with main.py
"""

from fastapi import HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
import os
import logging
from typing import Optional

# Import our integration system
from dashboard_integration_1_0 import get_dashboard_integration

logger = logging.getLogger(__name__)

# Admin authentication (reuse from main.py)
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def verify_admin(api_key: Optional[str] = Depends(api_key_header)):
    """Verify admin access"""
    expected_key = os.getenv("ADMIN_API_KEY")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # In development, allow access without key for convenience
    if environment == "development":
        logger.info("🔓 Admin access granted (development mode)")
        return True
    
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    return True

# Dashboard Routes to add to main.py FastAPI app

async def week1_admin_dashboard():
    """Week 1 Admin Dashboard - Unified user/pod management"""
    try:
        dashboard_integration = get_dashboard_integration()
        if not dashboard_integration:
            raise HTTPException(status_code=503, detail="Dashboard system not initialized")
        
        return await dashboard_integration.render_admin_dashboard()
        
    except Exception as e:
        logger.error(f"❌ Admin dashboard error: {e}")
        # Fallback simple admin page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard - Progress Method</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: #ff4444; color: white; padding: 20px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <h1>🔧 Admin Dashboard</h1>
            <div class="error">
                <h3>Dashboard Loading Error</h3>
                <p>Error: {str(e)}</p>
                <p>Please check system logs and try again.</p>
            </div>
            <p><a href="/admin/dashboard">← Back to System Dashboard</a></p>
        </body>
        </html>
        """)

async def week1_user_dashboard(request: Request, user_id: Optional[int] = None):
    """Week 1 User Dashboard - Progress visualization"""
    try:
        # For demo purposes, allow user_id in query params
        if not user_id:
            user_id = request.query_params.get("user_id")
            if user_id:
                user_id = int(user_id)
            else:
                raise HTTPException(status_code=400, detail="user_id required")
        
        dashboard_integration = get_dashboard_integration()
        if not dashboard_integration:
            raise HTTPException(status_code=503, detail="Dashboard system not initialized")
        
        return await dashboard_integration.render_user_dashboard(user_id)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    except Exception as e:
        logger.error(f"❌ User dashboard error: {e}")
        # Fallback simple user page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Progress Dashboard - Progress Method</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: #ff4444; color: white; padding: 20px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <h1>📊 Progress Dashboard</h1>
            <div class="error">
                <h3>Dashboard Loading Error</h3>
                <p>Error: {str(e)}</p>
                <p>Please check your user ID and try again.</p>
            </div>
        </body>
        </html>
        """)

async def week1_admin_dashboard_api():
    """API endpoint for admin dashboard data"""
    try:
        dashboard_integration = get_dashboard_integration()
        if not dashboard_integration:
            raise HTTPException(status_code=503, detail="Dashboard system not initialized")
        
        admin_data = await dashboard_integration.get_admin_dashboard_data()
        return JSONResponse(content=admin_data)
        
    except Exception as e:
        logger.error(f"❌ Admin API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def week1_user_dashboard_api(user_id: int):
    """API endpoint for user dashboard data"""
    try:
        dashboard_integration = get_dashboard_integration()
        if not dashboard_integration:
            raise HTTPException(status_code=503, detail="Dashboard system not initialized")
        
        user_data = await dashboard_integration.get_user_dashboard_data(user_id)
        return JSONResponse(content=user_data)
        
    except Exception as e:
        logger.error(f"❌ User API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Route registration helper
def register_week1_dashboard_routes(app):
    """Register Week 1 dashboard routes with FastAPI app"""
    
    # Admin dashboard routes
    app.add_api_route(
        "/admin/week1", 
        week1_admin_dashboard,
        methods=["GET"],
        response_class=HTMLResponse,
        dependencies=[Depends(verify_admin)],
        tags=["Admin Dashboard"]
    )
    
    app.add_api_route(
        "/admin/api/week1", 
        week1_admin_dashboard_api,
        methods=["GET"],
        dependencies=[Depends(verify_admin)],
        tags=["Admin API"]
    )
    
    # User dashboard routes (for demo - in production, add proper auth)
    app.add_api_route(
        "/dashboard", 
        week1_user_dashboard,
        methods=["GET"],
        response_class=HTMLResponse,
        tags=["User Dashboard"]
    )
    
    app.add_api_route(
        "/api/dashboard/{user_id}", 
        week1_user_dashboard_api,
        methods=["GET"],
        tags=["User API"]
    )
    
    logger.info("✅ Week 1 dashboard routes registered")

# Health check for dashboards
async def dashboard_health_check():
    """Check dashboard system health"""
    try:
        dashboard_integration = get_dashboard_integration()
        if not dashboard_integration:
            return {"status": "error", "message": "Dashboard integration not initialized"}
        
        # Test database connection
        test_data = await dashboard_integration.get_admin_dashboard_data()
        
        return {
            "status": "healthy",
            "dashboards": {
                "admin": "operational",
                "user": "operational"
            },
            "data_sources": {
                "users": test_data["total_users"],
                "pods": test_data["total_pods"],
                "commitments": test_data["total_commitments"]
            },
            "timestamp": test_data["last_updated"]
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "dashboards": {
                "admin": "error",
                "user": "error"
            }
        }