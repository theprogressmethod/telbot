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
from supabase import create_client

# Load environment
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
    title="Progress Method - Complete System",
    description="Telegram bot with comprehensive admin dashboard",
    version="2.0.0"
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
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ========================================
# BOT WEBHOOK ENDPOINTS (CRITICAL - DON'T CHANGE)
# ========================================

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhooks from Telegram"""
    try:
        # Import bot components only when needed
        from telbot import bot, dp
        from aiogram.types import Update
        
        # Get request body
        data = await request.json()
        logger.info(f"Webhook received: {json.dumps(data)[:200]}...")
        
        # Process update
        update = Update(**data)
        await dp.feed_update(bot, update)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

# ========================================
# COMPREHENSIVE ADMIN DASHBOARD
# ========================================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Comprehensive admin dashboard with full control features"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin Dashboard</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f7fa; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; }
            .card-header { padding: 20px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
            .card-body { padding: 20px; }
            .card-title { margin: 0; color: #2d3748; font-size: 1.25rem; font-weight: 600; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
            .metric { text-align: center; padding: 15px; background: #f7fafc; border-radius: 8px; }
            .metric-value { font-size: 2.5rem; font-weight: bold; margin-bottom: 5px; }
            .metric-label { color: #718096; font-size: 0.875rem; }
            .metric-users .metric-value { color: #3182ce; }
            .metric-commitments .metric-value { color: #38a169; }
            .metric-pods .metric-value { color: #d69e2e; }
            .metric-active .metric-value { color: #e53e3e; }
            .btn { background: #4299e1; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin: 5px; font-size: 0.875rem; transition: all 0.2s; }
            .btn:hover { background: #3182ce; transform: translateY(-1px); }
            .btn-success { background: #38a169; }
            .btn-success:hover { background: #2f855a; }
            .btn-warning { background: #d69e2e; }
            .btn-warning:hover { background: #b7791f; }
            .btn-danger { background: #e53e3e; }
            .btn-danger:hover { background: #c53030; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
            th { background: #f7fafc; font-weight: 600; color: #4a5568; }
            tbody tr:hover { background: #f7fafc; }
            .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; }
            .status-active { background: #c6f6d5; color: #22543d; }
            .status-completed { background: #bee3f8; color: #2a4365; }
            .admin-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px; }
            .control-section { padding: 15px; background: #f7fafc; border-radius: 8px; border-left: 4px solid #4299e1; }
            .loading { color: #718096; font-style: italic; }
            .error { color: #e53e3e; padding: 10px; background: #fed7d7; border-radius: 6px; }
            .success { color: #22543d; padding: 10px; background: #c6f6d5; border-radius: 6px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Progress Method Admin Dashboard</h1>
            <p>Complete system management and monitoring</p>
            <div style="margin-top: 15px;">
                <button class="btn" onclick="refreshAll()">🔄 Refresh All Data</button>
                <button class="btn btn-success" onclick="showCreatePod()">➕ Create Pod</button>
                <button class="btn btn-warning" onclick="showGrantRole()">👑 Grant Role</button>
            </div>
        </div>
        
        <div class="container">
            <div class="dashboard-grid">
                
                <!-- System Metrics -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">📊 System Overview</h3>
                    </div>
                    <div class="card-body">
                        <div id="metrics" class="loading">Loading metrics...</div>
                    </div>
                </div>
                
                <!-- User Management -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">👥 User Management</h3>
                    </div>
                    <div class="card-body">
                        <button class="btn" onclick="loadUsers()">🔄 Refresh Users</button>
                        <button class="btn btn-success" onclick="exportUsers()">📊 Export Data</button>
                        <div id="users" class="loading">Loading users...</div>
                    </div>
                </div>
                
                <!-- Pod Management -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🎯 Pod Management</h3>
                    </div>
                    <div class="card-body">
                        <button class="btn" onclick="loadPods()">🔄 Refresh Pods</button>
                        <button class="btn btn-success" onclick="showCreatePod()">➕ Create New Pod</button>
                        <div id="pods" class="loading">Loading pods...</div>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">📝 Recent Commitments</h3>
                    </div>
                    <div class="card-body">
                        <button class="btn" onclick="loadCommitments()">🔄 Refresh</button>
                        <button class="btn btn-warning" onclick="exportCommitments()">📊 Export</button>
                        <div id="commitments" class="loading">Loading commitments...</div>
                    </div>
                </div>
                
                <!-- System Health -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🏥 System Health</h3>
                    </div>
                    <div class="card-body">
                        <div class="admin-controls">
                            <div class="control-section">
                                <h4>🤖 Bot Status</h4>
                                <button class="btn" onclick="checkBotHealth()">Check Bot</button>
                                <div id="bot-status">Ready</div>
                            </div>
                            <div class="control-section">
                                <h4>🗄️ Database</h4>
                                <button class="btn" onclick="checkDbHealth()">Check DB</button>
                                <div id="db-status">Connected</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">⚡ Quick Actions</h3>
                    </div>
                    <div class="card-body">
                        <div class="admin-controls">
                            <div class="control-section">
                                <h4>👑 Role Management</h4>
                                <button class="btn btn-success" onclick="showGrantRole()">Grant Role</button>
                                <button class="btn btn-danger" onclick="showRevokeRole()">Revoke Role</button>
                            </div>
                            <div class="control-section">
                                <h4>📊 Analytics</h4>
                                <button class="btn" onclick="generateReport()">Generate Report</button>
                                <button class="btn" onclick="exportAllData()">Export All Data</button>
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

            // Load all data on page load
            document.addEventListener('DOMContentLoaded', function() {
                refreshAll();
                // Auto-refresh metrics every 2 minutes
                setInterval(loadMetrics, 120000);
            });

            async function refreshAll() {
                await Promise.all([
                    loadMetrics(),
                    loadUsers(),
                    loadPods(),
                    loadCommitments()
                ]);
            }

            async function loadMetrics() {
                try {
                    const response = await fetch('/admin/api/metrics');
                    const data = await response.json();
                    systemMetrics = data;
                    
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
                } catch (error) {
                    document.getElementById('metrics').innerHTML = '<div class="error">Error loading metrics: ' + error + '</div>';
                }
            }
            
            async function loadUsers() {
                try {
                    const response = await fetch('/admin/api/users');
                    const data = await response.json();
                    allUsers = data.users || [];
                    
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Telegram ID</th>
                                    <th>Roles</th>
                                    <th>Commitments</th>
                                    <th>Joined</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    if (allUsers.length > 0) {
                        allUsers.forEach(user => {
                            html += `<tr>
                                <td><strong>${user.first_name || 'Unknown'}</strong><br>
                                    <small>@${user.username || 'no-username'}</small></td>
                                <td>${user.telegram_user_id}</td>
                                <td><span class="status-badge status-active">${user.role || 'unpaid'}</span></td>
                                <td>${user.total_commitments || 0}</td>
                                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn" onclick="manageUser(${user.telegram_user_id})">Manage</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="6" style="text-align: center; color: #718096;">No users found</td></tr>';
                    }
                    
                    html += '</tbody></table>';
                    document.getElementById('users').innerHTML = html;
                } catch (error) {
                    document.getElementById('users').innerHTML = '<div class="error">Error loading users: ' + error + '</div>';
                }
            }
            
            async function loadPods() {
                try {
                    const response = await fetch('/admin/api/pods');
                    const data = await response.json();
                    allPods = data.pods || [];
                    
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Pod Name</th>
                                    <th>Members</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    if (allPods.length > 0) {
                        allPods.forEach(pod => {
                            html += `<tr>
                                <td><strong>${pod.name}</strong><br>
                                    <small>${pod.description || 'No description'}</small></td>
                                <td>${pod.member_count || 0}</td>
                                <td><span class="status-badge ${pod.is_active ? 'status-active' : 'status-completed'}">
                                    ${pod.is_active ? 'Active' : 'Inactive'}</span></td>
                                <td>${new Date(pod.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn" onclick="managePod('${pod.id}')">Manage</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="5" style="text-align: center; color: #718096;">No pods found</td></tr>';
                    }
                    
                    html += '</tbody></table>';
                    document.getElementById('pods').innerHTML = html;
                } catch (error) {
                    document.getElementById('pods').innerHTML = '<div class="error">Error loading pods: ' + error + '</div>';
                }
            }
            
            async function loadCommitments() {
                try {
                    const response = await fetch('/admin/api/commitments');
                    const data = await response.json();
                    
                    let html = `
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Commitment</th>
                                    <th>Status</th>
                                    <th>Score</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    if (data.commitments && data.commitments.length > 0) {
                        data.commitments.forEach(c => {
                            html += `<tr>
                                <td>${c.telegram_user_id || 'Unknown'}</td>
                                <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                                    ${(c.commitment || '').substring(0, 50)}${(c.commitment || '').length > 50 ? '...' : ''}
                                </td>
                                <td><span class="status-badge ${c.status === 'active' ? 'status-active' : 'status-completed'}">
                                    ${c.status || 'unknown'}</span></td>
                                <td>${c.smart_score || 0}/10</td>
                                <td>${new Date(c.created_at).toLocaleDateString()}</td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="5" style="text-align: center; color: #718096;">No commitments found</td></tr>';
                    }
                    
                    html += '</tbody></table>';
                    document.getElementById('commitments').innerHTML = html;
                } catch (error) {
                    document.getElementById('commitments').innerHTML = '<div class="error">Error loading commitments: ' + error + '</div>';
                }
            }

            // Admin action functions
            function showGrantRole() {
                const telegramId = prompt("Enter Telegram User ID:");
                if (!telegramId) return;
                
                const role = prompt("Enter role (paid, pod_member, admin, super_admin):");
                if (!role) return;
                
                grantRole(parseInt(telegramId), role);
            }

            async function grantRole(telegramUserId, role) {
                try {
                    const response = await fetch(`/admin/api/users/${telegramUserId}/grant-role?role=${role}`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        alert('Role granted successfully!');
                        await loadUsers();
                    } else {
                        const error = await response.json();
                        alert('Error: ' + error.detail);
                    }
                } catch (error) {
                    alert('Error granting role: ' + error);
                }
            }

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
                    } else {
                        const error = await response.json();
                        alert('Error: ' + error.detail);
                    }
                } catch (error) {
                    alert('Error creating pod: ' + error);
                }
            }

            function manageUser(telegramUserId) {
                alert(`User management for ${telegramUserId} - Feature coming soon!`);
            }

            function managePod(podId) {
                alert(`Pod management for ${podId} - Feature coming soon!`);
            }

            function exportUsers() {
                const csv = convertToCSV(allUsers);
                downloadCSV(csv, 'users.csv');
            }

            function exportCommitments() {
                alert('Export commitments - Feature coming soon!');
            }

            function exportAllData() {
                alert('Export all data - Feature coming soon!');
            }

            function generateReport() {
                alert('Generate report - Feature coming soon!');
            }

            async function checkBotHealth() {
                try {
                    const response = await fetch('/webhook_info');
                    const data = await response.json();
                    document.getElementById('bot-status').innerHTML = 
                        `<div class="success">✅ Connected to: ${data.url || 'No webhook'}</div>`;
                } catch (error) {
                    document.getElementById('bot-status').innerHTML = 
                        `<div class="error">❌ Bot check failed</div>`;
                }
            }

            async function checkDbHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('db-status').innerHTML = 
                        `<div class="success">✅ ${data.status}</div>`;
                } catch (error) {
                    document.getElementById('db-status').innerHTML = 
                        `<div class="error">❌ Database check failed</div>`;
                }
            }

            function convertToCSV(data) {
                if (!data.length) return '';
                
                const headers = Object.keys(data[0]);
                const csvContent = [
                    headers.join(','),
                    ...data.map(row => headers.map(header => JSON.stringify(row[header])).join(','))
                ].join('\\n');
                
                return csvContent;
            }

            function downloadCSV(csv, filename) {
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.setAttribute('hidden', '');
                a.setAttribute('href', url);
                a.setAttribute('download', filename);
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
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
        
        # Get member counts for each pod
        pod_data = []
        for pod in pods.data:
            pod_id = pod.get("id")
            
            # Get member count
            members = supabase.table("pod_memberships").select("id", count="exact").eq("pod_id", pod_id).eq("is_active", True).execute()
            member_count = members.count if members.count else 0
            
            pod_data.append({
                "id": pod_id,
                "name": pod.get("name"),
                "description": pod.get("description"),
                "member_count": member_count,
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)