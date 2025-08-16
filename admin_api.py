#!/usr/bin/env python3
"""
Standalone Admin API for Progress Method Bot
Minimal dependencies to ensure it works in production
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing Supabase credentials")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized")

# Create FastAPI app
app = FastAPI(
    title="Progress Method Admin API",
    description="Admin dashboard and management API",
    version="1.0.0"
)

# Admin authentication
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

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

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ Admin API is running!",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if supabase else "disconnected"
    }

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Simple admin dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { display: inline-block; margin: 20px; }
            .metric-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
            .metric-label { color: #666; margin-top: 5px; }
            button { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background: #45a049; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>🚀 Progress Method Admin Dashboard</h1>
        
        <div class="card">
            <h2>📊 System Overview</h2>
            <div id="metrics">Loading metrics...</div>
        </div>
        
        <div class="card">
            <h2>👥 Users</h2>
            <button onclick="loadUsers()">Refresh Users</button>
            <div id="users">Loading users...</div>
        </div>
        
        <div class="card">
            <h2>📝 Recent Commitments</h2>
            <button onclick="loadCommitments()">Refresh Commitments</button>
            <div id="commitments">Loading commitments...</div>
        </div>
        
        <div class="card">
            <h2>🎯 Pods</h2>
            <button onclick="loadPods()">Refresh Pods</button>
            <div id="pods">Loading pods...</div>
        </div>
        
        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/admin/api/metrics');
                    const data = await response.json();
                    
                    document.getElementById('metrics').innerHTML = `
                        <div class="metric">
                            <div class="metric-value">${data.total_users}</div>
                            <div class="metric-label">Total Users</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.total_commitments}</div>
                            <div class="metric-label">Total Commitments</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.active_commitments}</div>
                            <div class="metric-label">Active Commitments</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.total_pods}</div>
                            <div class="metric-label">Active Pods</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('metrics').innerHTML = 'Error loading metrics: ' + error;
                }
            }
            
            async function loadUsers() {
                try {
                    const response = await fetch('/admin/api/users');
                    const data = await response.json();
                    
                    let html = '<table><tr><th>Name</th><th>Telegram ID</th><th>Role</th><th>Commitments</th><th>Created</th></tr>';
                    data.users.forEach(user => {
                        html += `<tr>
                            <td>${user.first_name || 'Unknown'}</td>
                            <td>${user.telegram_user_id}</td>
                            <td>${user.role || 'unpaid'}</td>
                            <td>${user.total_commitments || 0}</td>
                            <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('users').innerHTML = html;
                } catch (error) {
                    document.getElementById('users').innerHTML = 'Error loading users: ' + error;
                }
            }
            
            async function loadCommitments() {
                try {
                    const response = await fetch('/admin/api/commitments');
                    const data = await response.json();
                    
                    let html = '<table><tr><th>User</th><th>Commitment</th><th>Status</th><th>Score</th><th>Created</th></tr>';
                    data.commitments.forEach(c => {
                        html += `<tr>
                            <td>${c.telegram_user_id || 'Unknown'}</td>
                            <td>${c.commitment.substring(0, 50)}...</td>
                            <td>${c.status}</td>
                            <td>${c.smart_score || 0}</td>
                            <td>${new Date(c.created_at).toLocaleDateString()}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('commitments').innerHTML = html;
                } catch (error) {
                    document.getElementById('commitments').innerHTML = 'Error loading commitments: ' + error;
                }
            }
            
            async function loadPods() {
                try {
                    const response = await fetch('/admin/api/pods');
                    const data = await response.json();
                    
                    let html = '<table><tr><th>Pod Name</th><th>Members</th><th>Active</th><th>Created</th></tr>';
                    data.pods.forEach(pod => {
                        html += `<tr>
                            <td>${pod.name}</td>
                            <td>${pod.member_count || 0}</td>
                            <td>${pod.is_active ? '✅' : '❌'}</td>
                            <td>${new Date(pod.created_at).toLocaleDateString()}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    document.getElementById('pods').innerHTML = html;
                } catch (error) {
                    document.getElementById('pods').innerHTML = 'Error loading pods: ' + error;
                }
            }
            
            // Load all data on page load
            loadMetrics();
            loadUsers();
            loadCommitments();
            loadPods();
            
            // Refresh every 30 seconds
            setInterval(() => {
                loadMetrics();
            }, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/admin/api/metrics")
async def get_metrics():
    """Get system metrics"""
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
        pods = supabase.table("pods").select("id", count="exact").eq("is_active", True).execute()
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
    """Get all users"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Get users with their roles
        users = supabase.table("users").select("*").order("created_at", desc=True).limit(100).execute()
        
        # Get user roles
        user_data = []
        for user in users.data:
            user_id = user.get("id")
            
            # Get user roles
            roles = supabase.table("user_roles").select("role").eq("user_id", user_id).eq("is_active", True).execute()
            user_roles = [r["role"] for r in roles.data] if roles.data else ["unpaid"]
            
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
        
        # Get recent commitments
        commitments = supabase.table("commitments").select("*").order("created_at", desc=True).limit(50).execute()
        
        return {"commitments": commitments.data, "count": len(commitments.data)}
    except Exception as e:
        logger.error(f"Error getting commitments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/pods")
async def get_pods():
    """Get all pods"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Get pods
        pods = supabase.table("pods").select("*").order("created_at", desc=True).execute()
        
        # Get member counts
        pod_data = []
        for pod in pods.data:
            pod_id = pod.get("id")
            
            # Get member count
            members = supabase.table("pod_memberships").select("id", count="exact").eq("pod_id", pod_id).execute()
            member_count = members.count if members.count else 0
            
            pod_data.append({
                "id": pod_id,
                "name": pod.get("name"),
                "description": pod.get("description"),
                "member_count": member_count,
                "is_active": pod.get("is_active"),
                "created_at": pod.get("created_at")
            })
        
        return {"pods": pod_data, "count": len(pod_data)}
    except Exception as e:
        logger.error(f"Error getting pods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/users/{telegram_user_id}/grant-role")
async def grant_user_role(telegram_user_id: int, role: str, api_key: Optional[str] = Depends(verify_admin)):
    """Grant a role to a user"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Get user by telegram_user_id
        user = supabase.table("users").select("id").eq("telegram_user_id", telegram_user_id).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user.data[0]["id"]
        
        # Check if role already exists
        existing = supabase.table("user_roles").select("id").eq("user_id", user_id).eq("role", role).eq("is_active", True).execute()
        if existing.data:
            return {"message": f"User already has role {role}"}
        
        # Grant role
        role_data = {
            "user_id": user_id,
            "role": role,
            "is_active": True,
            "granted_at": datetime.now().isoformat(),
            "granted_by": "admin_api"
        }
        
        result = supabase.table("user_roles").insert(role_data).execute()
        
        return {"message": f"Role {role} granted to user {telegram_user_id}", "role_id": result.data[0]["id"]}
    except Exception as e:
        logger.error(f"Error granting role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)