#!/usr/bin/env python3
"""
Simple admin routes module to debug production issues
"""

from fastapi import FastAPI
from datetime import datetime

def add_simple_admin_routes(app: FastAPI):
    """Add simple admin routes to the FastAPI app"""
    
    @app.get("/admin/simple")
    async def simple_admin():
        """Ultra simple admin route"""
        return {
            "message": "Simple admin route working",
            "timestamp": datetime.now().isoformat(),
            "status": "ok"
        }
    
    @app.get("/admin/health")
    async def admin_health():
        """Admin health check"""
        return {
            "admin_health": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    print("✅ Simple admin routes added successfully")