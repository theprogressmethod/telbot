#!/usr/bin/env python3
"""
Minimal FastAPI app to test admin routes in production
"""

from fastapi import FastAPI
from datetime import datetime
import os

# Create minimal FastAPI app
app = FastAPI(
    title="Progress Method Bot - Minimal Test",
    description="Minimal test version",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"status": "minimal app running", "timestamp": datetime.now().isoformat()}

@app.get("/admin/test-minimal")
async def admin_test():
    return {"admin": "working", "timestamp": datetime.now().isoformat()}

@app.get("/admin/debug")
async def admin_debug():
    return {
        "message": "Admin debug route working",
        "environment": "production" if os.getenv("NODE_ENV") == "production" else "development",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)