#!/usr/bin/env python3
"""
Retro Terminal SuperAdmin Dashboard
Commodore 64 meets Miami Vice - tight, dense, neon gradients
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

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
            min-height: 100vh;
            font-size: 14px;
            line-height: 1.2;
            overflow-x: auto;
        }}
        
        .terminal {{
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
            margin: 8px;
            border-radius: 4px;
        }}
        
        @keyframes gradient {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}
        
        .screen {{
            background: #000011;
            padding: 12px;
            border-radius: 2px;
            border: 1px solid #00ff88;
            box-shadow: 0 0 20px #00ff8844;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 8px;
            border-bottom: 1px solid #00ff88;
            padding-bottom: 4px;
        }}
        
        .header h1 {{
            font-size: 18px;
            font-weight: 700;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }}
        
        .env-badge {{
            color: {environment_color};
            font-size: 12px;
            text-shadow: 0 0 8px {environment_color};
        }}
        
        .status-bar {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 4px 0;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            font-size: 12px;
        }}
        
        .status-item {{
            color: #ff6b35;
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
        
        .footer {{
            margin-top: 8px;
            padding-top: 4px;
            border-top: 1px solid #333;
            font-size: 10px;
            color: #666;
            text-align: center;
        }}
        
        .ascii-art {{
            color: #8338ec;
            font-size: 10px;
            text-align: center;
            margin: 4px 0;
            text-shadow: 0 0 8px #8338ec44;
        }}
        
        .blink {{
            animation: blink 1s infinite;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0; }}
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
                <span>SYS: <span style="color: #00ff88;">ONLINE</span></span>
                <span>ENV: <span style="color: {environment_color};">{environment.upper()}</span></span>
                <span>TIME: <span id="time">{datetime.now().strftime('%H:%M:%S')}</span></span>
                <span class="blink">█</span>
            </div>
            
            <div class="system-info">
PROGRESS METHOD CONTROL SYSTEM v2.0 // BEHAVIORAL INTELLIGENCE CORE
DATABASE: SUPABASE.CO // RUNTIME: FASTAPI // STATUS: OPERATIONAL
            </div>
            
            <div class="menu">
                <a href="/admin/dashboard" class="menu-item" target="_blank">
                    <span class="menu-icon">📊</span>ADMIN_DASHBOARD.EXE
                </a>
                <a href="/admin/business-metrics" class="menu-item" target="_blank">
                    <span class="menu-icon">📈</span>BUSINESS_METRICS.EXE
                </a>
                <a href="/admin/nurture-control" class="menu-item" target="_blank">
                    <span class="menu-icon">💬</span>NURTURE_CONTROL.EXE
                </a>
                <a href="/docs" class="menu-item" target="_blank">
                    <span class="menu-icon">📚</span>API_DOCUMENTATION.HTM
                </a>
                <a href="/superadmin/status" class="menu-item" target="_blank">
                    <span class="menu-icon">⚙️</span>SYSTEM_STATUS.LOG
                </a>
            </div>
            
            <div class="footer">
SUPERADMIN v2.0 © 2025 // UPTIME: 24H // LAST_UPDATE: <span id="footer-time">{datetime.now().strftime('%H:%M:%S')}</span>
            </div>
        </div>
    </div>

    <script>
        function updateTime() {{
            const now = new Date();
            document.getElementById('time').textContent = now.toTimeString().substring(0, 8);
            document.getElementById('footer-time').textContent = now.toTimeString().substring(0, 8);
        }}
        
        setInterval(updateTime, 1000);
        
        // Terminal startup effect
        document.addEventListener('DOMContentLoaded', function() {{
            document.body.style.opacity = '0';
            setTimeout(() => {{
                document.body.style.transition = 'opacity 0.5s';
                document.body.style.opacity = '1';
            }}, 100);
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === '1') window.open('/admin/dashboard-enhanced', '_blank');
            if (e.key === '2') window.open('/api/business-intelligence', '_blank');
            if (e.key === '3') window.open('http://localhost:8082', '_blank');
            if (e.key === '4') window.open('/docs', '_blank');
            if (e.key === '5') window.open('/superadmin/status', '_blank');
        }});
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
    
    @app.get("/superadmin/status")
    async def superadmin_status():
        return {
            "status": "online",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "timestamp": datetime.now().isoformat(),
            "uptime": "24h",
            "dashboards": {
                "admin_dashboard": "/admin/dashboard",
                "business_metrics": "/admin/business-metrics", 
                "nurture_control": "/admin/nurture-control",
                "api_docs": "/docs"
            },
            "system_info": {
                "database": "supabase.co",
                "runtime": "fastapi",
                "core": "behavioral_intelligence_v2"
            }
        }