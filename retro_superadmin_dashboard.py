#!/usr/bin/env python3
"""
Retro Terminal SuperAdmin Dashboard
Commodore 64 meets Miami Vice - tight, dense, neon gradients
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from retro_styles import get_retro_css, get_retro_js

def get_retro_superadmin_html():
    """Generate retro terminal-style SuperAdmin dashboard"""
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
        {get_retro_css()}
        
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
            font-size: 10px;
            text-align: center;
            margin: 4px 0;
            text-shadow: 0 0 8px #8338ec44;
            line-height: 1;
        }}
        
        .system-info {{
            font-size: 11px;
            color: #666;
            margin: 4px 0;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>SUPERADMIN.EXE</h1>
                <h2>MIAMI VICE + COMMODORE 64 AESTHETIC</h2>
                <div class="env-badge">[{environment.upper()}]</div>
            </div>
            
            <div class="ascii-art">
████████╗██╗  ██╗███████╗    ██████╗ ██████╗  ██████╗  ██████╗ ██████╗ ███████╗███████╗███████╗
╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗██╔════╗ ██╔══██╗██╔════╝██╔════╝██╔════╝
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
PROGRESS METHOD CONTROL SYSTEM v2.0 // BEHAVIORAL INTELLIGENCE CORE
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
                        <a href="/superadmin/status" class="menu-item">
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
        {get_retro_js()}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === '1') window.open('/retro/admin', '_blank');
            if (e.key === '2') window.open('/retro/business', '_blank');
            if (e.key === '3') window.open('/retro/nurture', '_blank');
            if (e.key === '4') window.open('/docs', '_blank');
            if (e.key === '5') window.open('/superadmin/status', '_blank');
        }});
    </script>
</body>
</html>
    """
    
    return html_content

def get_minimal_superadmin_html():
    """Generate minimal, clean SuperAdmin dashboard version"""
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
    <button class="retro-switch" onclick="window.location.href='/superadmin'">🌊 RETRO MODE</button>
    
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

def add_retro_superadmin_routes(app: FastAPI):
    """Add retro SuperAdmin routes to FastAPI app"""
    
    @app.get("/superadmin", response_class=HTMLResponse)
    async def retro_superadmin_dashboard():
        return get_retro_superadmin_html()
    
    @app.get("/superadmin/minimal", response_class=HTMLResponse)
    async def minimal_superadmin_dashboard():
        return get_minimal_superadmin_html()
    
    @app.get("/superadmin/status")
    async def superadmin_status():
        return {
            "status": "online",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "timestamp": datetime.now().isoformat(),
            "uptime": "24h",
            "users": 65,
            "pods": 12,
            "dashboards": {
                "admin_dashboard": "/retro/admin",
                "business_metrics": "/retro/business", 
                "nurture_control": "/retro/nurture",
                "api_docs": "/docs"
            },
            "system_info": {
                "database": "supabase.co",
                "runtime": "fastapi",
                "core": "behavioral_intelligence_v2",
                "version": "2.0"
            }
        }

# Standalone server for testing
if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Retro SuperAdmin Dashboard")
    add_retro_superadmin_routes(app)
    
    print("🚀 Starting Retro SuperAdmin Dashboard")
    print("📍 Access at: http://localhost:7000/superadmin")
    print("🎨 Miami Vice + Commodore 64 Aesthetic")
    
    uvicorn.run(app, host="0.0.0.0", port=7000)