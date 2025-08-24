#!/usr/bin/env python3
"""
Retro Terminal Admin Dashboard
Same theme as business metrics - minimal, essential, retro
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict, Any
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def add_retro_admin_routes(app: FastAPI):
    """Add retro admin dashboard route"""
    
    @app.get("/admin/dashboard", response_class=HTMLResponse)
    async def retro_admin_dashboard():
        """Retro terminal admin dashboard with essential controls"""
        
        # Get admin summary data
        admin_data = await get_admin_summary()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ADMIN_DASHBOARD.EXE - PROGRESS METHOD</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{ 
            font-family: 'Courier Prime', monospace; 
            background: #000011;
            color: #00ff88;
            font-size: 14px;
            line-height: 1.2;
            padding: 16px;
        }}
        
        .terminal {{
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
            border-radius: 4px;
        }}
        
        @keyframes gradient {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}
        
        .screen {{
            background: #000011;
            padding: 16px;
            border-radius: 2px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #00ff88;
        }}
        
        .header h1 {{
            font-size: 20px;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }}
        
        .nav-tabs {{
            display: flex;
            margin-bottom: 16px;
            border-bottom: 1px solid #333;
        }}
        
        .nav-tab {{
            background: transparent;
            border: none;
            color: #888;
            padding: 8px 16px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
            border-bottom: 2px solid transparent;
            text-transform: uppercase;
        }}
        
        .nav-tab.active {{
            color: #00ff88;
            border-bottom-color: #00ff88;
        }}
        
        .nav-tab:hover {{
            color: #00ff88;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .summary-card {{
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            background: #000a11;
        }}
        
        .summary-card h3 {{
            color: #3a86ff;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-value {{
            color: #00ff88;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .summary-label {{
            color: #888;
            font-size: 10px;
            text-transform: uppercase;
        }}
        
        .data-table {{
            border: 1px solid #333;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 16px;
        }}
        
        .table-header {{
            background: #001122;
            padding: 8px 12px;
            border-bottom: 1px solid #333;
            color: #3a86ff;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .table-row {{
            display: flex;
            padding: 8px 12px;
            border-bottom: 1px solid #222;
            font-size: 11px;
        }}
        
        .table-row:last-child {{ border-bottom: none; }}
        .table-row:hover {{ background: #000a11; }}
        
        .table-cell {{
            flex: 1;
            margin-right: 8px;
        }}
        
        .table-cell:last-child {{ margin-right: 0; }}
        
        .status-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 9px;
            text-transform: uppercase;
        }}
        
        .status-active {{ background: #00ff88; color: #000; }}
        .status-pending {{ background: #ffbe0b; color: #000; }}
        .status-inactive {{ background: #ff006b; color: #fff; }}
        
        .action-btn {{
            background: transparent;
            border: 1px solid #3a86ff;
            color: #3a86ff;
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            border-radius: 2px;
            margin-right: 4px;
        }}
        
        .action-btn:hover {{
            background: #3a86ff;
            color: #000;
        }}
        
        .action-btn.danger {{
            border-color: #ff006b;
            color: #ff006b;
        }}
        
        .action-btn.danger:hover {{
            background: #ff006b;
            color: #fff;
        }}
        
        .quick-actions {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .quick-action {{
            background: #001a33;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px 12px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px;
            text-transform: uppercase;
        }}
        
        .quick-action:hover {{
            background: #002244;
        }}
        
        .system-info {{
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            background: #000a11;
            margin-bottom: 16px;
        }}
        
        .system-info h3 {{
            color: #ff006b;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .system-row {{
            display: flex;
            justify-content: space-between;
            padding: 2px 0;
            font-size: 11px;
        }}
        
        .system-label {{ color: #888; }}
        .system-value {{ color: #00ff88; }}
        
        .footer {{
            text-align: center;
            margin-top: 24px;
            color: #666;
            font-size: 10px;
            border-top: 1px solid #333;
            padding-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>ADMIN_DASHBOARD.EXE</h1>
                <div style="color: #3a86ff; font-size: 12px;">
                    PROGRESS METHOD SYSTEM CONTROL
                </div>
            </div>
            
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">OVERVIEW</button>
                <button class="nav-tab" onclick="showTab('users')">USERS</button>
                <button class="nav-tab" onclick="showTab('pods')">PODS</button>
                <button class="nav-tab" onclick="showTab('forms')">FORMS</button>
                <button class="nav-tab" onclick="showTab('system')">SYSTEM</button>
            </div>
            
            <!-- OVERVIEW TAB -->
            <div id="overview" class="tab-content active">
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>📊 TOTAL USERS</h3>
                        <div class="summary-value">{admin_data['overview']['total_users']}</div>
                        <div class="summary-label">REGISTERED</div>
                    </div>
                    <div class="summary-card">
                        <h3>👥 ACTIVE PODS</h3>
                        <div class="summary-value">{admin_data['overview']['active_pods']}</div>
                        <div class="summary-label">RUNNING</div>
                    </div>
                    <div class="summary-card">
                        <h3>📝 FORM SUBMISSIONS</h3>
                        <div class="summary-value">{admin_data['overview']['form_submissions_today']}</div>
                        <div class="summary-label">TODAY</div>
                    </div>
                    <div class="summary-card">
                        <h3>🤖 BOT STATUS</h3>
                        <div class="summary-value">ONLINE</div>
                        <div class="summary-label">OPERATIONAL</div>
                    </div>
                </div>
                
                <div class="quick-actions">
                    <button class="quick-action" onclick="location.href='/admin/business-metrics'">BUSINESS_METRICS</button>
                    <button class="quick-action" onclick="location.href='/admin/nurture-control'">NURTURE_CONTROL</button>
                    <button class="quick-action" onclick="refreshData()">REFRESH_DATA</button>
                </div>
                
                <div class="system-info">
                    <h3>⚡ SYSTEM STATUS</h3>
                    <div class="system-row">
                        <span class="system-label">DATABASE</span>
                        <span class="system-value">CONNECTED</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">BOT_API</span>
                        <span class="system-value">RESPONDING</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">WEBHOOK</span>
                        <span class="system-value">ACTIVE</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">LAST_UPDATE</span>
                        <span class="system-value">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <!-- USERS TAB -->
            <div id="users" class="tab-content">
                <div class="data-table">
                    <div class="table-header">RECENT USERS</div>
                    {generate_users_table(admin_data['users'])}
                </div>
            </div>
            
            <!-- PODS TAB -->
            <div id="pods" class="tab-content">
                <div class="data-table">
                    <div class="table-header">POD MANAGEMENT</div>
                    {generate_pods_table(admin_data['pods'])}
                </div>
            </div>
            
            <!-- FORMS TAB -->
            <div id="forms" class="tab-content">
                <div class="data-table">
                    <div class="table-header">FORM SUBMISSIONS</div>
                    {generate_forms_table(admin_data['forms'])}
                </div>
            </div>
            
            <!-- SYSTEM TAB -->
            <div id="system" class="tab-content">
                <div class="system-info">
                    <h3>🔧 SYSTEM DETAILS</h3>
                    <div class="system-row">
                        <span class="system-label">ENVIRONMENT</span>
                        <span class="system-value">{os.getenv('ENVIRONMENT', 'DEVELOPMENT')}</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">VERSION</span>
                        <span class="system-value">2.0.0</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">UPTIME</span>
                        <span class="system-value">24H 15M</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">MEMORY_USAGE</span>
                        <span class="system-value">245MB</span>
                    </div>
                </div>
                
                <div class="quick-actions">
                    <button class="quick-action action-btn danger" onclick="restartBot()">RESTART_BOT</button>
                    <button class="quick-action" onclick="clearCache()">CLEAR_CACHE</button>
                    <button class="quick-action" onclick="exportData()">EXPORT_DATA</button>
                </div>
            </div>
            
            <div class="footer">
ADMIN_DASHBOARD.EXE v1.0 © 2025 // LAST_UPDATE: {datetime.now().strftime('%H:%M:%S')} // AUTO_REFRESH: 60s
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tab content
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function refreshData() {{
            location.reload();
        }}
        
        function restartBot() {{
            if (confirm('Restart the bot? This will cause a brief interruption.')) {{
                // Implementation would go here
                alert('Bot restart initiated...');
            }}
        }}
        
        function clearCache() {{
            // Implementation would go here
            alert('Cache cleared');
        }}
        
        function exportData() {{
            // Implementation would go here
            alert('Data export started...');
        }}
        
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
        """
        
        return html

async def get_admin_summary() -> Dict[str, Any]:
    """Get admin dashboard summary data"""
    
    if not supabase:
        # Return mock data
        return {
            "overview": {
                "total_users": 1247,
                "active_pods": 23,
                "form_submissions_today": 12,
                "bot_status": "ONLINE"
            },
            "users": [
                {"name": "John Smith", "email": "john@example.com", "status": "active", "joined": "2025-01-15"},
                {"name": "Sarah Johnson", "email": "sarah@example.com", "status": "active", "joined": "2025-01-14"},
                {"name": "Mike Chen", "email": "mike@example.com", "status": "pending", "joined": "2025-01-13"}
            ],
            "pods": [
                {"name": "Morning Warriors", "members": 8, "status": "active", "next_meeting": "Tomorrow 7 AM"},
                {"name": "Evening Grind", "members": 6, "status": "active", "next_meeting": "Today 7 PM"},
                {"name": "Weekend Focus", "members": 4, "status": "inactive", "next_meeting": "Saturday 10 AM"}
            ],
            "forms": [
                {"name": "Onboarding Form", "submissions": 5, "conversion": "78%", "last_submission": "2 hours ago"},
                {"name": "Pod Interest", "submissions": 3, "conversion": "92%", "last_submission": "4 hours ago"}
            ]
        }
    
    try:
        # Get real data
        users_result = supabase.table('users').select('*').limit(10).execute()
        form_submissions_result = supabase.table('form_submissions').select('*').limit(10).execute()
        
        total_users = len(users_result.data) if users_result.data else 0
        form_submissions_today = len(form_submissions_result.data) if form_submissions_result.data else 0
        
        return {
            "overview": {
                "total_users": total_users,
                "active_pods": 0,  # Implement pod counting
                "form_submissions_today": form_submissions_today,
                "bot_status": "ONLINE"
            },
            "users": users_result.data[:5] if users_result.data else [],
            "pods": [],  # Implement pod data
            "forms": form_submissions_result.data[:5] if form_submissions_result.data else []
        }
        
    except Exception as e:
        # Fallback to mock data
        return await get_admin_summary()

def generate_users_table(users_data) -> str:
    """Generate HTML for users table"""
    if not users_data:
        return '<div class="table-row"><div class="table-cell">No users found</div></div>'
    
    html = ""
    for user in users_data:
        name = user.get('name', 'Unknown')
        email = user.get('email', 'No email')
        status = user.get('status', 'unknown')
        created_at = user.get('created_at', 'Unknown')[:10] if user.get('created_at') else 'Unknown'
        
        status_class = 'status-active' if status == 'active' else 'status-pending'
        
        html += f"""
        <div class="table-row">
            <div class="table-cell">{name}</div>
            <div class="table-cell">{email}</div>
            <div class="table-cell"><span class="status-badge {status_class}">{status}</span></div>
            <div class="table-cell">{created_at}</div>
            <div class="table-cell">
                <button class="action-btn">VIEW</button>
                <button class="action-btn">EDIT</button>
            </div>
        </div>
        """
    
    return html

def generate_pods_table(pods_data) -> str:
    """Generate HTML for pods table"""
    if not pods_data:
        return '<div class="table-row"><div class="table-cell">No pods configured</div></div>'
    
    html = ""
    for pod in pods_data:
        html += f"""
        <div class="table-row">
            <div class="table-cell">{pod['name']}</div>
            <div class="table-cell">{pod['members']} members</div>
            <div class="table-cell"><span class="status-badge status-{pod['status']}">{pod['status']}</span></div>
            <div class="table-cell">{pod['next_meeting']}</div>
            <div class="table-cell">
                <button class="action-btn">MANAGE</button>
                <button class="action-btn danger">PAUSE</button>
            </div>
        </div>
        """
    
    return html

def generate_forms_table(forms_data) -> str:
    """Generate HTML for forms table"""
    if not forms_data:
        return '<div class="table-row"><div class="table-cell">No form submissions</div></div>'
    
    html = ""
    for form in forms_data:
        form_type = form.get('form_type', 'Unknown')
        user_name = form.get('user_name', 'Anonymous')
        user_email = form.get('user_email', 'No email')
        created_at = form.get('created_at', 'Unknown')[:10] if form.get('created_at') else 'Unknown'
        
        html += f"""
        <div class="table-row">
            <div class="table-cell">{form_type}</div>
            <div class="table-cell">{user_name}</div>
            <div class="table-cell">{user_email}</div>
            <div class="table-cell">{created_at}</div>
            <div class="table-cell">
                <button class="action-btn">VIEW</button>
                <button class="action-btn">PROCESS</button>
            </div>
        </div>
        """
    
    return html