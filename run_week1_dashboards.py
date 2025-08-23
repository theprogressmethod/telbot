#!/usr/bin/env python3
"""
WEEK 1 DASHBOARD SERVER
=======================
Standalone FastAPI server for Week 1 dashboards
Runs alongside main.py on a different port
"""

import asyncio
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Import our bot components
from telbot import supabase, role_manager, pod_system

# Import dashboard system
from dashboard_integration_1_0 import initialize_dashboard_integration
from dashboard_routes_1_0 import register_week1_dashboard_routes, dashboard_health_check

# Import retro dashboard system
from retro_evolved_dashboard import get_evolved_superadmin_html
from fastapi.responses import HTMLResponse

# Import CRUD routes
from dashboard_crud_routes import create_crud_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Progress Method - Week 1 Dashboards",
    description="Admin and User dashboards for Week 1 MVP",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dashboard integration
dashboard_integration = None

@app.on_event("startup")
async def startup_event():
    """Initialize dashboard system on startup"""
    global dashboard_integration
    
    logger.info("🚀 Starting Week 1 Dashboard Server")
    logger.info(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"   Database: Connected to Supabase")
    
    try:
        # Initialize dashboard integration
        dashboard_integration = await initialize_dashboard_integration(
            supabase, role_manager, pod_system
        )
        
        logger.info("✅ Dashboard integration initialized")
        
        # Register dashboard routes
        register_week1_dashboard_routes(app)
        
        logger.info("✅ Dashboard routes registered")
        
        # Add CRUD routes for database editing
        crud_router = create_crud_router(supabase, pod_system)
        app.include_router(crud_router)
        
        logger.info("✅ CRUD routes registered")
        
        # Add retro dashboard routes
        app.add_api_route(
            "/retro/superadmin", 
            lambda: HTMLResponse(content=get_evolved_superadmin_html()),
            methods=["GET"],
            response_class=HTMLResponse,
            tags=["Retro Dashboard"]
        )
        
        logger.info("✅ Retro dashboard routes added")
        logger.info("📊 Available endpoints:")
        logger.info("   • GET /admin/week1 - Admin dashboard")
        logger.info("   • GET /dashboard?user_id=123 - User dashboard") 
        logger.info("   • GET /admin/api/week1 - Admin API")
        logger.info("   • GET /api/dashboard/123 - User API")
        logger.info("   • GET /retro/superadmin - SuperAdmin dashboard")
        logger.info("   • GET /health - Health check")
        logger.info("📝 CRUD API endpoints:")
        logger.info("   • GET /api/crud/users - List all users")
        logger.info("   • PUT /api/crud/users/{id} - Update user")
        logger.info("   • GET /api/crud/pods - List all pods")
        logger.info("   • PUT /api/crud/pods/{id} - Update pod")
        logger.info("   • GET /api/crud/commitments - List commitments")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with dashboard links"""
    return {
        "service": "Progress Method - Week 1 Dashboards",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "admin_dashboard": "/admin/week1",
            "user_dashboard": "/dashboard?user_id={user_id}",
            "admin_api": "/admin/api/week1",
            "user_api": "/api/dashboard/{user_id}",
            "health": "/health"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return await dashboard_health_check()

async def main():
    """Main function to run the dashboard server"""
    
    # Determine port (use different port than main.py)
    port = int(os.getenv("DASHBOARD_PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌐 Starting dashboard server on {host}:{port}")
    logger.info(f"📊 Access dashboards at:")
    logger.info(f"   • Admin: http://localhost:{port}/admin/week1")
    logger.info(f"   • User: http://localhost:{port}/dashboard?user_id=865415132")
    
    # Run the server
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())