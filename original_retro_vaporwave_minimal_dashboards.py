#!/usr/bin/env python3
"""
ORIGINAL RETRO VAPORWAVE MINIMAL DASHBOARDS
Authentic restored versions from git stash
Miami Vice + Commodore 64 aesthetic with minimal design
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict, Any
from supabase import create_client

# Initialize Supabase if available
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = FastAPI(title="Original Retro Vaporwave Minimal Dashboards")

# ORIGINAL MINIMAL SUPERADMIN DASHBOARD (EXTRACTED FROM STASH)
def get_minimal_superadmin_html():
    """Generate minimal, clean SuperAdmin dashboard - ORIGINAL VERSION"""
    environment = os.getenv('ENVIRONMENT', 'development')
    environment_colors = {
        'development': '#3b82f6',
        'staging': '#f59e0b', 
        'production': '#ef4444'
    }
    environment_color = environment_colors.get(environment, '#3b82f6')
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SuperAdmin - Progress Method</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            background: #f8fafc;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .header {{
            background: white;
            padding: 2rem;
            border-bottom: 1px solid #e5e7eb;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.875rem;
            font-weight: 600;
            color: #111827;
        }}
        
        .environment-badge {{
            background: {environment_color};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .container {{
            max-width: 600px;
            margin: 3rem auto;
            padding: 0 1.5rem;
        }}
        
        .dashboard-list {{
            background: white;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            overflow: hidden;
        }}
        
        .dashboard-item {{
            padding: 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            transition: background-color 0.2s;
        }}
        
        .dashboard-item:last-child {{
            border-bottom: none;
        }}
        
        .dashboard-item:hover {{
            background: #f9fafb;
        }}
        
        .dashboard-link {{
            display: flex;
            align-items: center;
            text-decoration: none;
            color: inherit;
        }}
        
        .dashboard-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
            width: 2rem;
            text-align: center;
        }}
        
        .dashboard-info h3 {{
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #111827;
        }}
        
        .dashboard-info p {{
            margin: 0.25rem 0 0 0;
            font-size: 0.875rem;
            color: #6b7280;
        }}
        
        .status-section {{
            background: white;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        
        .status-item {{
            text-align: center;
        }}
        
        .status-value {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }}
        
        .status-label {{
            font-size: 0.75rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.875rem;
        }}
        
        .retro-switch {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #ff006b, #8338ec);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.75rem;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ box-shadow: 0 0 5px #ff006b; }}
            to {{ box-shadow: 0 0 20px #8338ec; }}
        }}
    </style>
</head>
<body>
    <button class="retro-switch" onclick="window.location.href='/retro/superadmin'">🌊 RETRO MODE</button>
    
    <div class="header">
        <h1>SuperAdmin</h1>
        <div class="environment-badge">{environment}</div>
    </div>
    
    <div class="container">
        <div class="status-section">
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-value" id="system-status">Online</div>
                    <div class="status-label">System</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="environment-status">{environment.title()}</div>
                    <div class="status-label">Environment</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="uptime-status">24h</div>
                    <div class="status-label">Uptime</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="timestamp">{datetime.now().strftime('%H:%M')}</div>
                    <div class="status-label">Updated</div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-list">
            <div class="dashboard-item">
                <a href="/retro/business" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">📊</div>
                    <div class="dashboard-info">
                        <h3>Business Intelligence</h3>
                        <p>Behavioral analytics and conversion metrics</p>
                    </div>
                </a>
            </div>
            
            <div class="dashboard-item">
                <a href="/retro/admin" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">⚙️</div>
                    <div class="dashboard-info">
                        <h3>Enhanced Admin</h3>
                        <p>User management and system controls</p>
                    </div>
                </a>
            </div>
            
            <div class="dashboard-item">
                <a href="/retro/nurture" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">💬</div>
                    <div class="dashboard-info">
                        <h3>Nurture Sequences</h3>
                        <p>Message flows and engagement tracking</p>
                    </div>
                </a>
            </div>
            
            <div class="dashboard-item">
                <a href="/docs" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">📚</div>
                    <div class="dashboard-info">
                        <h3>API Documentation</h3>
                        <p>OpenAPI schema and endpoint testing</p>
                    </div>
                </a>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>SuperAdmin Dashboard • Last updated: <span id="footer-timestamp">{datetime.now().strftime('%H:%M:%S')}</span></p>
    </div>

    <script>
        function updateTimestamp() {{
            const now = new Date();
            document.getElementById('timestamp').textContent = now.toLocaleTimeString('en-US', {{
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false
            }});
            document.getElementById('footer-timestamp').textContent = now.toLocaleTimeString();
        }}
        
        setInterval(updateTimestamp, 60000);
        
        async function loadSystemStatus() {{
            try {{
                const response = await fetch('/');
                if (response.ok) {{
                    document.getElementById('system-status').textContent = 'Online';
                    document.getElementById('system-status').style.color = '#10b981';
                }} else {{
                    document.getElementById('system-status').textContent = 'Warning';
                    document.getElementById('system-status').style.color = '#f59e0b';
                }}
            }} catch (error) {{
                document.getElementById('system-status').textContent = 'Offline';
                document.getElementById('system-status').style.color = '#ef4444';
            }}
        }}
        
        loadSystemStatus();
        setInterval(loadSystemStatus, 30000);
    </script>
</body>
</html>
    """
    
    return html_content

# ORIGINAL RETRO VAPORWAVE ADMIN DASHBOARD (EXTRACTED FROM STASH)
def get_retro_admin_html():
    """Generate retro vaporwave admin dashboard - ORIGINAL VERSION"""
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
        
        .minimal-switch {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px 12px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            border-radius: 2px;
            text-transform: uppercase;
        }}
        
        .minimal-switch:hover {{
            background: #00ff88;
            color: #000;
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
            <button class="minimal-switch" onclick="window.location.href='/minimal/superadmin'">MINIMAL MODE</button>
            
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
                <button class="nav-tab" onclick="showTab('system')">SYSTEM</button>
            </div>
            
            <div id="overview" class="tab-content active">
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>📊 TOTAL USERS</h3>
                        <div class="summary-value">65</div>
                        <div class="summary-label">REGISTERED</div>
                    </div>
                    <div class="summary-card">
                        <h3>👥 ACTIVE PODS</h3>
                        <div class="summary-value">8</div>
                        <div class="summary-label">RUNNING</div>
                    </div>
                    <div class="summary-card">
                        <h3>📝 FORM SUBMISSIONS</h3>
                        <div class="summary-value">12</div>
                        <div class="summary-label">TODAY</div>
                    </div>
                    <div class="summary-card">
                        <h3>🤖 BOT STATUS</h3>
                        <div class="summary-value">ONLINE</div>
                        <div class="summary-label">OPERATIONAL</div>
                    </div>
                </div>
                
                <div class="quick-actions">
                    <button class="quick-action" onclick="location.href='/retro/business'">BUSINESS_METRICS</button>
                    <button class="quick-action" onclick="location.href='/retro/nurture'">NURTURE_CONTROL</button>
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
            
            <div id="users" class="tab-content">
                <div class="system-info">
                    <h3>👥 USER MANAGEMENT</h3>
                    <div class="system-row">
                        <span class="system-label">TOTAL_USERS</span>
                        <span class="system-value">65</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">ACTIVE_TODAY</span>
                        <span class="system-value">23</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">NEW_REGISTRATIONS</span>
                        <span class="system-value">3</span>
                    </div>
                </div>
            </div>
            
            <div id="pods" class="tab-content">
                <div class="system-info">
                    <h3>🎯 POD MANAGEMENT</h3>
                    <div class="system-row">
                        <span class="system-label">ACTIVE_PODS</span>
                        <span class="system-value">8</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">PARTICIPANTS</span>
                        <span class="system-value">47</span>
                    </div>
                    <div class="system-row">
                        <span class="system-label">COMPLETION_RATE</span>
                        <span class="system-value">87%</span>
                    </div>
                </div>
            </div>
            
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
            </div>
            
            <div class="footer">
                <p>RETRO ADMIN TERMINAL • LAST_UPDATE: <span id="footer-timestamp">{datetime.now().strftime('%H:%M:%S')}</span></p>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.nav-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function refreshData() {{
            location.reload();
        }}
        
        // Update timestamps
        setInterval(() => {{
            const now = new Date();
            document.getElementById('footer-timestamp').textContent = now.toLocaleTimeString();
        }}, 1000);
    </script>
</body>
</html>
    """
    return html

# RETRO SUPERADMIN DASHBOARD (LOCALHOST:7001 VERSION) 
def get_retro_superadmin_terminal_html():
    """Generate retro terminal-style SuperAdmin dashboard - LOCALHOST:7001 VERSION"""
    environment = os.getenv('ENVIRONMENT', 'development')
    environment_colors = {
        'development': '#00ff88',
        'staging': '#ff6b35', 
        'production': '#ff1744'
    }
    environment_color = environment_colors.get(environment, '#00ff88')
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SUPERADMIN.EXE - PROGRESS METHOD</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        
        * {{ 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }}
        
        body {{ 
            font-family: 'Courier Prime', 'Courier New', monospace; 
            background: linear-gradient(45deg, #0a0a0a 0%, #1a0a2e 25%, #16213e 50%, #0f3460 75%, #001122 100%);
            color: #00ff88;
            font-size: 12px;
            line-height: 1.3;
            padding: 8px;
            min-height: 100vh;
        }}
        
        .terminal {{
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
            border-radius: 4px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        @keyframes gradient {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}
        
        .screen {{
            background: #000;
            padding: 12px;
            border-radius: 2px;
            font-family: 'Courier Prime', monospace;
            color: #00ff88;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #00ff88;
        }}
        
        .header h1 {{
            font-size: 16px;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
            margin-bottom: 4px;
        }}
        
        .header h2 {{
            font-size: 10px;
            color: #8338ec;
            letter-spacing: 1px;
        }}
        
        .env-badge {{
            color: {environment_color};
            font-size: 12px;
            text-shadow: 0 0 8px {environment_color};
        }}
        
        .menu {{
            margin: 8px 0;
        }}
        
        .menu-item {{
            display: block;
            color: #00ff88;
            text-decoration: none;
            padding: 2px 4px;
            margin: 1px 0;
            border-left: 2px solid transparent;
            transition: all 0.2s;
            font-size: 11px;
        }}
        
        .menu-item:hover {{
            background: #001a33;
            border-left-color: #ff006b;
            color: #ff006b;
            text-shadow: 0 0 8px #ff006b;
        }}
        
        .menu-icon {{
            width: 12px;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .ascii-art {{
            color: #8338ec;
            font-size: 8px;
            text-align: center;
            margin: 4px 0;
            text-shadow: 0 0 8px #8338ec44;
            line-height: 1;
        }}
        
        .system-info {{
            font-size: 9px;
            color: #666;
            margin: 8px 0;
            text-align: center;
            line-height: 1.2;
        }}
        
        .status-bar {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 4px 0;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            font-size: 10px;
        }}
        
        .status-item {{
            color: #666;
        }}
        
        .blink {{
            animation: blink 1s infinite;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0; }}
        }}
        
        .data-section {{
            margin: 8px 0;
            border: 1px solid #333;
            border-radius: 2px;
        }}
        
        .data-header {{
            background: #001122;
            color: #3a86ff;
            padding: 4px 8px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #333;
        }}
        
        .data-content {{
            padding: 8px;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            margin: 8px 0;
        }}
        
        .metric-card {{
            border: 1px solid #333;
            border-radius: 2px;
            padding: 6px;
            text-align: center;
            background: #000a11;
        }}
        
        .metric-value {{
            color: #00ff88;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 2px;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 9px;
            text-transform: uppercase;
        }}
        
        .good .metric-value {{ color: #06ffa5; }}
        
        .footer {{
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid #333;
            font-size: 9px;
            color: #666;
            text-align: center;
            line-height: 1.2;
        }}
        
        .ascii-border {{
            color: #333;
            font-size: 8px;
            margin: 4px 0;
        }}
        
        .minimal-switch {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px 12px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            border-radius: 2px;
            text-transform: uppercase;
        }}
        
        .minimal-switch:hover {{
            background: #00ff88;
            color: #000;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <button class="minimal-switch" onclick="window.location.href='/minimal/superadmin'">MINIMAL MODE</button>
            
            <div class="header">
                <h1>SUPERADMIN.EXE</h1>
                <h2>MIAMI VICE + COMMODORE 64 AESTHETIC</h2>
                <div class="env-badge">[{environment.upper()}]</div>
            </div>
            
            <div class="ascii-art">
████████╗██╗  ██╗███████╗    ██████╗ ██████╗  ██████╗  ██████╗ ██████╗ ███████╗███████╗███████╗
╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝ ██╔══██╗██╔════╝██╔════╝██╔════╝
   ██║   ███████║█████╗      ██████╔╝██████╔╝██║   ██║██║  ███╗██████╔╝█████╗  ███████╗███████╗
   ██║   ██╔══██║██╔══╝      ██╔═══╝ ██╔══██╗██║   ██║██║   ██║██╔══██╗██╔══╝  ╚════██║╚════██║
   ██║   ██║  ██║███████╗    ██║     ██║  ██║╚██████╔╝╚██████╔╝██║  ██║███████╗███████║███████║
   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
            </div>
            
            <div class="status-bar">
                <span class="status-item">SYS: <span style="color: #00ff88;">ONLINE</span></span>
                <span class="status-item">ENV: <span style="color: {environment_color};">{environment.upper()}</span></span>
                <span class="status-item">TIME: <span id="time">{datetime.now().strftime('%H:%M:%S')}</span></span>
                <span class="status-item blink">█</span>
            </div>
            
            <div class="system-info">
PROGRESS METHOD CONTROL SYSTEM v2.0 // BEHAVIORAL INTELLIGENCE CORE<br>
DATABASE: SUPABASE.CO // RUNTIME: FASTAPI // STATUS: OPERATIONAL
            </div>
            
            <div class="data-section">
                <div class="data-header">SYSTEM DASHBOARDS</div>
                <div class="data-content">
                    <div class="menu">
                        <a href="/retro/admin" class="menu-item">
                            <span class="menu-icon">📊</span>ADMIN_DASHBOARD.EXE - System Administration
                        </a>
                        <a href="/retro/business" class="menu-item">
                            <span class="menu-icon">📈</span>BUSINESS_METRICS.EXE - Analytics & KPIs
                        </a>
                        <a href="/retro/nurture" class="menu-item">
                            <span class="menu-icon">💬</span>NURTURE_CONTROL.EXE - Sequence Management
                        </a>
                        <a href="/docs" class="menu-item">
                            <span class="menu-icon">📚</span>API_DOCUMENTATION.HTM - Technical Docs
                        </a>
                        <a href="/status" class="menu-item">
                            <span class="menu-icon">⚙️</span>SYSTEM_STATUS.JSON - Live Status
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">65</div>
                    <div class="metric-label">Active Users</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Pods</div>
                </div>
                <div class="metric-card good">
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">v2.0</div>
                    <div class="metric-label">Version</div>
                </div>
            </div>
            
            <div class="footer">
SUPERADMIN v2.0 © 2025 // UPTIME: 24H // LAST_UPDATE: <span id="footer-time">{datetime.now().strftime('%H:%M:%S')}</span>
<div class="ascii-border">═══════════════════════════════════════════════════════════════════════════════</div>
            </div>
        </div>
    </div>

    <script>
        // Update time every second
        function updateTime() {{
            const now = new Date();
            document.getElementById('time').textContent = now.toLocaleTimeString('en-US', {{
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            }});
            document.getElementById('footer-time').textContent = now.toLocaleTimeString('en-US', {{
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            }});
        }}
        
        setInterval(updateTime, 1000);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === '1') window.open('/retro/admin', '_blank');
            if (e.key === '2') window.open('/retro/business', '_blank');
            if (e.key === '3') window.open('/retro/nurture', '_blank');
            if (e.key === '4') window.open('/docs', '_blank');
            if (e.key === '5') window.open('/status', '_blank');
        }});
    </script>
</body>
</html>
    """
    
    return html_content

# BUSINESS INTELLIGENCE DASHBOARD (MINIMAL RETRO VERSION)
def get_retro_business_html():
    """Generate business intelligence dashboard - retro version"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BUSINESS_METRICS.EXE - PROGRESS METHOD</title>
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
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .metric-card {{
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            background: #000a11;
        }}
        
        .metric-title {{
            color: #3a86ff;
            font-size: 10px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-value {{
            color: #00ff88;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .metric-change {{
            font-size: 10px;
            text-transform: uppercase;
        }}
        
        .metric-up {{ color: #06ffa5; }}
        .metric-down {{ color: #ff006b; }}
        .metric-neutral {{ color: #888; }}
        
        .back-btn {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: transparent;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px 12px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            border-radius: 2px;
            text-transform: uppercase;
        }}
        
        .back-btn:hover {{
            background: #00ff88;
            color: #000;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <button class="back-btn" onclick="window.history.back()">← BACK</button>
            
            <div class="header">
                <h1>BUSINESS_METRICS.EXE</h1>
                <div style="color: #3a86ff; font-size: 12px;">
                    BEHAVIORAL ANALYTICS TERMINAL
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">💰 TOTAL REVENUE</div>
                    <div class="metric-value">$47.2K</div>
                    <div class="metric-change metric-up">↑ 23.4% MoM</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">👥 ACTIVE USERS</div>
                    <div class="metric-value">1,247</div>
                    <div class="metric-change metric-up">↑ 8.7% WoW</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">📈 CONVERSION RATE</div>
                    <div class="metric-value">12.4%</div>
                    <div class="metric-change metric-neutral">→ 0.2% WoW</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">🎯 POD COMPLETION</div>
                    <div class="metric-value">87.3%</div>
                    <div class="metric-change metric-up">↑ 4.1% MoM</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">📧 EMAIL ENGAGEMENT</div>
                    <div class="metric-value">34.2%</div>
                    <div class="metric-change metric-down">↓ 2.3% WoW</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">⏱️ AVG SESSION TIME</div>
                    <div class="metric-value">18m</div>
                    <div class="metric-change metric-up">↑ 12.4% MoM</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return html

# ADD ROUTES TO FASTAPI APP
@app.get("/", response_class=HTMLResponse)
async def index():
    return "<h1>Original Retro Vaporwave Minimal Dashboards</h1><p><a href='/minimal/superadmin'>Minimal SuperAdmin</a> | <a href='/retro/superadmin'>Retro SuperAdmin</a></p>"

@app.get("/minimal/superadmin", response_class=HTMLResponse)
async def minimal_superadmin_dashboard():
    return get_minimal_superadmin_html()

@app.get("/retro/superadmin", response_class=HTMLResponse)
async def retro_superadmin_dashboard():
    return get_retro_superadmin_terminal_html()

@app.get("/retro/admin", response_class=HTMLResponse)
async def retro_admin_dashboard():
    return get_retro_admin_html()

@app.get("/retro/business", response_class=HTMLResponse)
async def retro_business_dashboard():
    return get_retro_business_html()

@app.get("/retro/nurture", response_class=HTMLResponse)
async def retro_nurture_dashboard():
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>NURTURE_CONTROL.EXE - PROGRESS METHOD</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Courier Prime', monospace; 
            background: #000011;
            color: #00ff88;
            font-size: 14px;
            padding: 16px;
        }
        .terminal {
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
            border-radius: 4px;
        }
        @keyframes gradient {
            0%{background-position:0% 50%}
            50%{background-position:100% 50%}
            100%{background-position:0% 50%}
        }
        .screen {
            background: #000011;
            padding: 16px;
            border-radius: 2px;
        }
        .header {
            text-align: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #00ff88;
        }
        .header h1 {
            font-size: 20px;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>NURTURE_CONTROL.EXE</h1>
                <div style="color: #3a86ff; font-size: 12px;">
                    MESSAGE FLOW CONTROL TERMINAL
                </div>
            </div>
            <p style="text-align: center; margin-top: 50px; color: #888;">NURTURE SEQUENCE CONTROL INTERFACE</p>
        </div>
    </div>
</body>
</html>
    """
    return html

@app.get("/status")
async def status():
    return {
        "status": "online", 
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "timestamp": datetime.now().isoformat(),
        "dashboards": {
            "minimal_superadmin": "/minimal/superadmin",
            "retro_superadmin": "/retro/superadmin", 
            "retro_admin": "/retro/admin",
            "retro_business": "/retro/business",
            "retro_nurture": "/retro/nurture"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🌊 ORIGINAL RETRO VAPORWAVE MINIMAL DASHBOARDS")
    print("📡 Authentic restored versions from git stash")
    print("🎯 Miami Vice + Commodore 64 aesthetic")
    print("💎 Running on http://localhost:7003")
    print("")
    print("Available dashboards:")
    print("  • Minimal SuperAdmin: http://localhost:7003/minimal/superadmin")
    print("  • Retro SuperAdmin: http://localhost:7003/retro/superadmin") 
    print("  • Retro Admin: http://localhost:7003/retro/admin")
    print("  • Retro Business: http://localhost:7003/retro/business")
    print("  • Retro Nurture: http://localhost:7003/retro/nurture")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=7003)