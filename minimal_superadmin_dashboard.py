#!/usr/bin/env python3
"""
Minimal SuperAdmin Dashboard
Clean, simple design with distinct access to all dashboards
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

def get_minimal_superadmin_html():
    """Generate minimal, clean SuperAdmin dashboard"""
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
    </style>
</head>
<body>
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
                <a href="/admin/dashboard-enhanced" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">📊</div>
                    <div class="dashboard-info">
                        <h3>Business Intelligence</h3>
                        <p>Behavioral analytics and conversion metrics</p>
                    </div>
                </a>
            </div>
            
            <div class="dashboard-item">
                <a href="/admin/dashboard" class="dashboard-link" target="_blank">
                    <div class="dashboard-icon">⚙️</div>
                    <div class="dashboard-info">
                        <h3>Enhanced Admin</h3>
                        <p>User management and system controls</p>
                    </div>
                </a>
            </div>
            
            <div class="dashboard-item">
                <a href="http://localhost:8082" class="dashboard-link" target="_blank">
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
        // Update timestamp every minute
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
        
        // Load system status
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
        
        // Initialize
        loadSystemStatus();
        setInterval(loadSystemStatus, 30000);
    </script>
</body>
</html>
    """
    
    return html_content

def add_minimal_superadmin_routes(app: FastAPI):
    """Add minimal SuperAdmin routes to FastAPI app"""
    
    @app.get("/superadmin", response_class=HTMLResponse)
    async def minimal_superadmin_dashboard():
        return get_minimal_superadmin_html()
    
    @app.get("/superadmin/status")
    async def superadmin_status():
        return {
            "status": "online",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "timestamp": datetime.now().isoformat(),
            "dashboards": {
                "business_intelligence": "/admin/dashboard-enhanced",
                "enhanced_admin": "/admin/dashboard", 
                "nurture_sequences": "http://localhost:8081",
                "api_docs": "/docs"
            }
        }