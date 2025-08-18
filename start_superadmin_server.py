#!/usr/bin/env python3
"""
Standalone SuperAdmin Server
Simple server to host the SuperAdmin dashboard
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from dotenv import load_dotenv

# Load staging environment
load_dotenv('.env.staging')

# Import dashboard components  
from retro_superadmin_dashboard import add_superadmin_routes
from enhanced_admin_dashboard import add_business_intelligence_routes
from essential_business_dashboard import add_business_metrics_routes

print("🚀 Starting SuperAdmin Dashboard Server...")
print("Environment:", os.getenv('ENVIRONMENT', 'development'))

# Create FastAPI app
app = FastAPI(
    title="SuperAdmin Dashboard",
    description="Central command center for Progress Method dashboards",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint with dashboard links"""
    return {
        "status": "✅ SuperAdmin Dashboard Server Running!",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "dashboards": {
            "superadmin": "/superadmin",
            "superadmin_status": "/superadmin/status",
            "business_intelligence": "/api/business-intelligence",
            "enhanced_admin": "/admin/dashboard-enhanced"
        },
        "quick_links": {
            "main_dashboard": "http://localhost:8000/superadmin",
            "business_intelligence": "http://localhost:8000/admin/dashboard-enhanced",
            "api_docs": "http://localhost:8000/docs"
        }
    }

# Add dashboard routes
add_superadmin_routes(app)
add_business_intelligence_routes(app)
add_business_metrics_routes(app)

if __name__ == "__main__":
    print("\n📊 SuperAdmin Dashboard Features:")
    print("  ✅ Central hub for all dashboards")
    print("  ✅ Business Intelligence integration")
    print("  ✅ System health monitoring")
    print("  ✅ Feature flag management")
    print("  ✅ Development tools")
    print("  ✅ Quick actions and exports")
    
    print(f"\n🔗 Access URLs:")
    print(f"  SuperAdmin Dashboard: http://localhost:8000/superadmin")
    print(f"  Business Intelligence: http://localhost:8000/admin/dashboard-enhanced")
    print(f"  API Status: http://localhost:8000/")
    print(f"  API Documentation: http://localhost:8000/docs")
    
    print(f"\n🎯 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("Press Ctrl+C to stop the server\n")
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8000)