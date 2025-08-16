#!/usr/bin/env python3
"""
Enhanced Admin API with Nurture Sequence Management
Phase 2: Unified control and email delivery management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel

from unified_nurture_controller import UnifiedNurtureController, DeliveryChannel
from email_delivery_service import EmailDeliveryService
from nurture_sequences import SequenceType

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_eCPQhpxD_BiGA5QnXDALpz1qNUn43THqf")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing Supabase credentials")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized")

# Initialize nurture controller and email service
if supabase:
    nurture_controller = UnifiedNurtureController(supabase)
    email_service = EmailDeliveryService(RESEND_API_KEY)
    email_service.set_supabase_client(supabase)
    nurture_controller.set_email_service(email_service)
else:
    nurture_controller = None
    email_service = None

# Create FastAPI app
app = FastAPI(
    title="Enhanced Progress Method Admin API",
    description="Admin dashboard with nurture sequence management",
    version="2.0.0"
)

# Admin authentication
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def verify_admin(api_key: Optional[str] = Depends(api_key_header)):
    """Verify admin API key"""
    admin_key = os.getenv("ADMIN_API_KEY")
    if not admin_key:
        logger.warning("⚠️ No ADMIN_API_KEY set - admin routes are unprotected!")
        return True
    
    if not api_key or api_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return True

# Pydantic models for requests
class TriggerSequenceRequest(BaseModel):
    user_id: str
    sequence_type: str
    context: Optional[Dict[str, Any]] = None
    override_channel: Optional[str] = None

class UpdatePreferencesRequest(BaseModel):
    user_id: str
    preferred_channel: Optional[str] = None
    email_preferences: Optional[Dict[str, Any]] = None

class SendTestEmailRequest(BaseModel):
    email_address: str
    user_name: str = "Test User"
    template_type: str = "nurture_sequence"

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "✅ Enhanced Admin API is running!",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if supabase else "disconnected",
        "nurture_controller": "initialized" if nurture_controller else "not available",
        "email_service": "initialized" if email_service else "not available"
    }

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def enhanced_admin_dashboard():
    """Enhanced admin dashboard with nurture sequence management"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8fafc; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
            .header h1 { margin: 0; font-size: 28px; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .tabs { display: flex; background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .tab { flex: 1; padding: 15px; text-align: center; cursor: pointer; border-bottom: 3px solid transparent; transition: all 0.3s; }
            .tab.active { border-bottom-color: #667eea; background: #f8fafc; }
            .tab:hover { background: #f1f5f9; }
            .tab-content { display: none; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .tab-content.active { display: block; }
            .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }
            .metric-label { color: #64748b; font-size: 14px; }
            .metric-change { font-size: 12px; margin-top: 5px; }
            .metric-change.positive { color: #10b981; }
            .metric-change.negative { color: #ef4444; }
            .action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .action-card { background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
            .action-card h3 { margin-top: 0; color: #374151; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #374151; }
            .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; }
            .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.3s; }
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5a67d8; }
            .btn-success { background: #10b981; color: white; }
            .btn-success:hover { background: #059669; }
            .btn-warning { background: #f59e0b; color: white; }
            .btn-warning:hover { background: #d97706; }
            .data-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            .data-table th, .data-table td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
            .data-table th { background: #f9fafb; font-weight: 600; }
            .data-table tr:hover { background: #f9fafb; }
            .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
            .status-active { background: #d1fae5; color: #065f46; }
            .status-completed { background: #dbeafe; color: #1e40af; }
            .status-failed { background: #fee2e2; color: #991b1b; }
            .chart-container { height: 300px; margin: 20px 0; }
            .loading { text-align: center; padding: 40px; color: #64748b; }
            .error { color: #ef4444; padding: 20px; text-align: center; }
            .success { color: #10b981; padding: 10px; background: #d1fae5; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Progress Method Admin Dashboard</h1>
            <p>Enhanced with Nurture Sequence Management</p>
        </div>
        
        <div class="container">
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview')">📊 Overview</div>
                <div class="tab" onclick="showTab('nurture')">💌 Nurture Sequences</div>
                <div class="tab" onclick="showTab('email')">📧 Email Delivery</div>
                <div class="tab" onclick="showTab('users')">👥 Users</div>
                <div class="tab" onclick="showTab('analytics')">📈 Analytics</div>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content active">
                <div class="metric-grid" id="overview-metrics">
                    <div class="loading">Loading metrics...</div>
                </div>
                
                <div class="action-grid">
                    <div class="action-card">
                        <h3>🎯 Quick Actions</h3>
                        <button class="btn btn-primary" onclick="refreshAllData()">Refresh All Data</button>
                        <button class="btn btn-success" onclick="processNurtureQueue()" style="margin-left: 10px;">Process Nurture Queue</button>
                    </div>
                    
                    <div class="action-card">
                        <h3>📊 System Status</h3>
                        <div id="system-status">Checking system status...</div>
                    </div>
                </div>
            </div>
            
            <!-- Nurture Sequences Tab -->
            <div id="nurture-tab" class="tab-content">
                <div class="metric-grid" id="nurture-metrics">
                    <div class="loading">Loading nurture metrics...</div>
                </div>
                
                <div class="action-grid">
                    <div class="action-card">
                        <h3>🚀 Trigger Sequence</h3>
                        <div class="form-group">
                            <label>User ID:</label>
                            <input type="text" id="trigger-user-id" placeholder="Enter user ID">
                        </div>
                        <div class="form-group">
                            <label>Sequence Type:</label>
                            <select id="trigger-sequence-type">
                                <option value="onboarding">Onboarding</option>
                                <option value="commitment_followup">Commitment Follow-up</option>
                                <option value="re_engagement">Re-engagement</option>
                                <option value="pod_journey">Pod Journey</option>
                                <option value="streak_celebration">Streak Celebration</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Channel Override:</label>
                            <select id="trigger-channel">
                                <option value="">Auto (based on preference)</option>
                                <option value="telegram">Telegram Only</option>
                                <option value="email">Email Only</option>
                                <option value="both">Both Channels</option>
                            </select>
                        </div>
                        <button class="btn btn-primary" onclick="triggerSequence()">Trigger Sequence</button>
                        <div id="trigger-result"></div>
                    </div>
                    
                    <div class="action-card">
                        <h3>⚙️ Update User Preferences</h3>
                        <div class="form-group">
                            <label>User ID:</label>
                            <input type="text" id="pref-user-id" placeholder="Enter user ID">
                        </div>
                        <div class="form-group">
                            <label>Preferred Channel:</label>
                            <select id="pref-channel">
                                <option value="telegram">Telegram</option>
                                <option value="email">Email</option>
                                <option value="both">Both</option>
                            </select>
                        </div>
                        <button class="btn btn-success" onclick="updatePreferences()">Update Preferences</button>
                        <div id="pref-result"></div>
                    </div>
                </div>
                
                <div class="action-card">
                    <h3>📋 Active Sequences</h3>
                    <button class="btn btn-primary" onclick="loadActiveSequences()">Refresh</button>
                    <div id="active-sequences">Loading active sequences...</div>
                </div>
            </div>
            
            <!-- Email Delivery Tab -->
            <div id="email-tab" class="tab-content">
                <div class="metric-grid" id="email-metrics">
                    <div class="loading">Loading email metrics...</div>
                </div>
                
                <div class="action-grid">
                    <div class="action-card">
                        <h3>📧 Send Test Email</h3>
                        <div class="form-group">
                            <label>Email Address:</label>
                            <input type="email" id="test-email" placeholder="test@example.com">
                        </div>
                        <div class="form-group">
                            <label>User Name:</label>
                            <input type="text" id="test-name" placeholder="Test User">
                        </div>
                        <div class="form-group">
                            <label>Template:</label>
                            <select id="test-template">
                                <option value="nurture_sequence">Nurture Sequence</option>
                                <option value="welcome_email">Welcome Email</option>
                            </select>
                        </div>
                        <button class="btn btn-primary" onclick="sendTestEmail()">Send Test Email</button>
                        <div id="email-result"></div>
                    </div>
                    
                    <div class="action-card">
                        <h3>🔄 Email Queue Management</h3>
                        <button class="btn btn-success" onclick="processEmailQueue()">Process Email Queue</button>
                        <button class="btn btn-warning" onclick="clearFailedEmails()" style="margin-left: 10px;">Clear Failed Emails</button>
                        <div id="queue-result"></div>
                    </div>
                </div>
                
                <div class="action-card">
                    <h3>📊 Recent Email Deliveries</h3>
                    <button class="btn btn-primary" onclick="loadEmailDeliveries()">Refresh</button>
                    <div id="email-deliveries">Loading email deliveries...</div>
                </div>
            </div>
            
            <!-- Users Tab -->
            <div id="users-tab" class="tab-content">
                <div id="users-content">Loading users...</div>
            </div>
            
            <!-- Analytics Tab -->
            <div id="analytics-tab" class="tab-content">
                <div class="metric-grid" id="analytics-metrics">
                    <div class="loading">Loading analytics...</div>
                </div>
                <div class="chart-container" id="analytics-charts">
                    <div class="loading">Loading charts...</div>
                </div>
            </div>
        </div>
        
        <script>
            // Tab management
            function showTab(tabName) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                event.target.classList.add('active');
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Load tab-specific data
                if (tabName === 'nurture') {
                    loadNurtureMetrics();
                    loadActiveSequences();
                } else if (tabName === 'email') {
                    loadEmailMetrics();
                    loadEmailDeliveries();
                } else if (tabName === 'users') {
                    loadUsers();
                } else if (tabName === 'analytics') {
                    loadAnalytics();
                }
            }
            
            // Load overview metrics
            async function loadOverviewMetrics() {
                try {
                    const response = await fetch('/admin/api/metrics');
                    const data = await response.json();
                    
                    document.getElementById('overview-metrics').innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${data.total_users}</div>
                            <div class="metric-label">Total Users</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.total_commitments}</div>
                            <div class="metric-label">Total Commitments</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.active_commitments}</div>
                            <div class="metric-label">Active Commitments</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.total_pods}</div>
                            <div class="metric-label">Active Pods</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('overview-metrics').innerHTML = '<div class="error">Error loading metrics</div>';
                }
            }
            
            // Load nurture metrics
            async function loadNurtureMetrics() {
                try {
                    const response = await fetch('/admin/api/nurture/analytics');
                    const data = await response.json();
                    
                    document.getElementById('nurture-metrics').innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${data.total_deliveries || 0}</div>
                            <div class="metric-label">Total Deliveries</div>
                            <div class="metric-change positive">Last 30 days</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.overall_metrics?.delivery_rate || 0}%</div>
                            <div class="metric-label">Delivery Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.overall_metrics?.open_rate || 0}%</div>
                            <div class="metric-label">Open Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.overall_metrics?.click_rate || 0}%</div>
                            <div class="metric-label">Click Rate</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('nurture-metrics').innerHTML = '<div class="error">Error loading nurture metrics</div>';
                }
            }
            
            // Load email metrics
            async function loadEmailMetrics() {
                try {
                    const response = await fetch('/admin/api/email/stats');
                    const data = await response.json();
                    
                    document.getElementById('email-metrics').innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${data.total_scheduled || 0}</div>
                            <div class="metric-label">Emails Scheduled</div>
                            <div class="metric-change">Last 7 days</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.sent || 0}</div>
                            <div class="metric-label">Emails Sent</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.delivery_rate || 0}%</div>
                            <div class="metric-label">Delivery Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.open_rate || 0}%</div>
                            <div class="metric-label">Open Rate</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('email-metrics').innerHTML = '<div class="error">Error loading email metrics</div>';
                }
            }
            
            // Trigger sequence
            async function triggerSequence() {
                const userId = document.getElementById('trigger-user-id').value;
                const sequenceType = document.getElementById('trigger-sequence-type').value;
                const channel = document.getElementById('trigger-channel').value;
                
                if (!userId) {
                    document.getElementById('trigger-result').innerHTML = '<div class="error">Please enter a user ID</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/admin/api/nurture/trigger', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            user_id: userId,
                            sequence_type: sequenceType,
                            override_channel: channel || null
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('trigger-result').innerHTML = '<div class="success">✅ Sequence triggered successfully!</div>';
                        loadActiveSequences();
                    } else {
                        document.getElementById('trigger-result').innerHTML = `<div class="error">❌ Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    document.getElementById('trigger-result').innerHTML = '<div class="error">❌ Network error</div>';
                }
            }
            
            // Load active sequences
            async function loadActiveSequences() {
                try {
                    const response = await fetch('/admin/api/nurture/active');
                    const data = await response.json();
                    
                    let html = '<table class="data-table"><thead><tr><th>User</th><th>Sequence</th><th>Step</th><th>Channel</th><th>Next Message</th><th>Started</th></tr></thead><tbody>';
                    
                    data.sequences.forEach(seq => {
                        const nextMessage = seq.next_message_at ? new Date(seq.next_message_at).toLocaleString() : 'Completed';
                        html += `<tr>
                            <td>${seq.user_name || 'Unknown'}</td>
                            <td><span class="status-badge status-active">${seq.sequence_type}</span></td>
                            <td>${seq.current_step}</td>
                            <td>${seq.preferred_channel}</td>
                            <td>${nextMessage}</td>
                            <td>${new Date(seq.started_at).toLocaleDateString()}</td>
                        </tr>`;
                    });
                    
                    html += '</tbody></table>';
                    document.getElementById('active-sequences').innerHTML = html;
                } catch (error) {
                    document.getElementById('active-sequences').innerHTML = '<div class="error">Error loading active sequences</div>';
                }
            }
            
            // Send test email
            async function sendTestEmail() {
                const email = document.getElementById('test-email').value;
                const name = document.getElementById('test-name').value;
                const template = document.getElementById('test-template').value;
                
                if (!email) {
                    document.getElementById('email-result').innerHTML = '<div class="error">Please enter an email address</div>';
                    return;
                }
                
                try {
                    const response = await fetch('/admin/api/email/test', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            email_address: email,
                            user_name: name,
                            template_type: template
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('email-result').innerHTML = '<div class="success">✅ Test email sent successfully!</div>';
                    } else {
                        document.getElementById('email-result').innerHTML = `<div class="error">❌ Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    document.getElementById('email-result').innerHTML = '<div class="error">❌ Network error</div>';
                }
            }
            
            // Process nurture queue
            async function processNurtureQueue() {
                try {
                    const response = await fetch('/admin/api/nurture/process', {method: 'POST'});
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert(`✅ Processed ${result.total_processed} deliveries\\n📱 Telegram: ${result.telegram_sent} sent, ${result.telegram_failed} failed\\n📧 Email: ${result.email_sent} sent, ${result.email_failed} failed`);
                        loadNurtureMetrics();
                    } else {
                        alert(`❌ Error processing queue: ${result.detail}`);
                    }
                } catch (error) {
                    alert('❌ Network error');
                }
            }
            
            // Load users (existing function)
            async function loadUsers() {
                try {
                    const response = await fetch('/admin/api/users');
                    const data = await response.json();
                    
                    let html = '<table class="data-table"><thead><tr><th>Name</th><th>Telegram ID</th><th>Email</th><th>Role</th><th>Commitments</th><th>Created</th></tr></thead><tbody>';
                    data.users.forEach(user => {
                        html += `<tr>
                            <td>${user.first_name || 'Unknown'}</td>
                            <td>${user.telegram_user_id}</td>
                            <td>${user.email || 'Not provided'}</td>
                            <td>${user.role || 'unpaid'}</td>
                            <td>${user.total_commitments || 0}</td>
                            <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        </tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('users-content').innerHTML = html;
                } catch (error) {
                    document.getElementById('users-content').innerHTML = '<div class="error">Error loading users</div>';
                }
            }
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                loadOverviewMetrics();
                
                // Auto-refresh every 30 seconds
                setInterval(loadOverviewMetrics, 30000);
            });
            
            // Refresh all data
            function refreshAllData() {
                loadOverviewMetrics();
                if (document.getElementById('nurture-tab').classList.contains('active')) {
                    loadNurtureMetrics();
                    loadActiveSequences();
                }
                if (document.getElementById('email-tab').classList.contains('active')) {
                    loadEmailMetrics();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Enhanced API endpoints
@app.get("/admin/api/nurture/analytics")
async def get_nurture_analytics():
    """Get nurture sequence analytics"""
    try:
        if not nurture_controller:
            raise HTTPException(status_code=503, detail="Nurture controller not available")
        
        analytics = await nurture_controller.get_sequence_analytics(days=30)
        return analytics
    except Exception as e:
        logger.error(f"Error getting nurture analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/nurture/trigger")
async def trigger_nurture_sequence(request: TriggerSequenceRequest, admin: bool = Depends(verify_admin)):
    """Trigger a nurture sequence for a user"""
    try:
        if not nurture_controller:
            raise HTTPException(status_code=503, detail="Nurture controller not available")
        
        sequence_type = SequenceType(request.sequence_type)
        override_channel = DeliveryChannel(request.override_channel) if request.override_channel else None
        
        success = await nurture_controller.trigger_sequence(
            user_id=request.user_id,
            sequence_type=sequence_type,
            context=request.context,
            override_channel=override_channel
        )
        
        if success:
            return {"message": "Sequence triggered successfully", "success": True}
        else:
            raise HTTPException(status_code=400, detail="Failed to trigger sequence")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid sequence type or channel: {e}")
    except Exception as e:
        logger.error(f"Error triggering sequence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/nurture/active")
async def get_active_sequences():
    """Get all active nurture sequences"""
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        result = supabase.table("user_sequence_state").select(
            "*, users(first_name, email)"
        ).eq("is_active", True).order("started_at", desc=True).execute()
        
        sequences = []
        for seq in result.data:
            user_data = seq.get("users", {})
            sequences.append({
                "id": seq["id"],
                "user_id": seq["user_id"],
                "user_name": user_data.get("first_name"),
                "user_email": user_data.get("email"),
                "sequence_type": seq["sequence_type"],
                "current_step": seq["current_step"],
                "preferred_channel": seq.get("preferred_channel", "telegram"),
                "engagement_score": seq.get("engagement_score", 50),
                "started_at": seq["started_at"],
                "next_message_at": seq.get("next_message_at"),
                "last_message_at": seq.get("last_message_at")
            })
        
        return {"sequences": sequences, "count": len(sequences)}
    except Exception as e:
        logger.error(f"Error getting active sequences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/nurture/process")
async def process_nurture_queue(admin: bool = Depends(verify_admin)):
    """Process pending nurture deliveries"""
    try:
        if not nurture_controller:
            raise HTTPException(status_code=503, detail="Nurture controller not available")
        
        stats = await nurture_controller.process_pending_deliveries()
        return stats
    except Exception as e:
        logger.error(f"Error processing nurture queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/api/email/stats")
async def get_email_stats():
    """Get email delivery statistics"""
    try:
        if not email_service:
            raise HTTPException(status_code=503, detail="Email service not available")
        
        stats = await email_service.get_delivery_stats(days=7)
        return stats
    except Exception as e:
        logger.error(f"Error getting email stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/email/test")
async def send_test_email(request: SendTestEmailRequest, admin: bool = Depends(verify_admin)):
    """Send a test email"""
    try:
        if not email_service:
            raise HTTPException(status_code=503, detail="Email service not available")
        
        success = await email_service.send_nurture_email(
            to_email=request.email_address,
            subject="Test Email from Progress Method Admin",
            content="This is a test email from the admin dashboard. If you receive this, the email system is working correctly!",
            user_name=request.user_name,
            template_type=request.template_type
        )
        
        if success:
            return {"message": "Test email sent successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/api/email/webhook")
async def handle_email_webhook(webhook_data: Dict[str, Any]):
    """Handle email delivery webhooks from Resend"""
    try:
        if not email_service:
            raise HTTPException(status_code=503, detail="Email service not available")
        
        success = await email_service.handle_webhook_event(webhook_data)
        
        if success:
            return {"message": "Webhook processed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
            
    except Exception as e:
        logger.error(f"Error handling email webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Keep existing endpoints from admin_api.py
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
        
        # Get pod count (using 'status' field instead of 'is_active')
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
                "email": user.get("email"),
                "role": ", ".join(user_roles),
                "total_commitments": user.get("total_commitments", 0),
                "created_at": user.get("created_at")
            })
        
        return {"users": user_data, "count": len(user_data)}
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)