#!/usr/bin/env python3
"""
RETRO EVOLVED - The Next Evolution
Terminal aesthetic with breathing room, surgical precision, mobile-first
Miami Vice + Commodore 64 meets Swiss Design
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="Retro Evolved Dashboard")

def get_evolved_superadmin_html():
    """Generate evolved retro terminal dashboard - mobile-first, generous whitespace"""
    environment = os.getenv('ENVIRONMENT', 'development')
    environment_colors = {
        'development': '#00ff88',
        'staging': '#ff6b35', 
        'production': '#ff1744'
    }
    env_color = environment_colors.get(environment, '#00ff88')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <title>SUPERADMIN • THE PROGRESS METHOD</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@200;400;700&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        :root {{
            --terminal-green: #00ff88;
            --miami-pink: #ff006b;
            --vapor-purple: #8338ec;
            --cyber-blue: #3a86ff;
            --sunset-yellow: #ffbe0b;
            --deep-black: #000011;
            --soft-black: #0a0a1a;
            --gray-800: #1a1a2e;
            --gray-600: #444466;
            --gray-400: #666688;
            
            --env-color: {env_color};
            
            /* Spacing scale - ultra compact */
            --space-xs: 0.25rem;
            --space-sm: 0.5rem;
            --space-md: 0.875rem;
            --space-lg: 1.25rem;
            --space-xl: 1.75rem;
            --space-2xl: 2.25rem;
            --space-3xl: 3rem;
            
            /* Type scale - mobile first */
            --text-xs: 0.75rem;
            --text-sm: 0.875rem;
            --text-base: 1rem;
            --text-lg: 1.25rem;
            --text-xl: 1.5rem;
            --text-2xl: 2rem;
            --text-3xl: 2.5rem;
            
            /* Line heights */
            --leading-tight: 1.1;
            --leading-normal: 1.5;
            --leading-loose: 1.75;
        }}
        
        /* Tablet and up - ultra compact */
        @media (min-width: 768px) {{
            :root {{
                --space-xs: 0.375rem;
                --space-sm: 0.625rem;
                --space-md: 1rem;
                --space-lg: 1.375rem;
                --space-xl: 2rem;
                --space-2xl: 2.5rem;
                --space-3xl: 3.5rem;
                
                --text-xs: 0.6875rem;
                --text-sm: 0.75rem;
                --text-base: 0.875rem;
                --text-lg: 1.125rem;
                --text-xl: 1.5rem;
                --text-2xl: 1.875rem;
                --text-3xl: 2.5rem;
            }}
        }}
        
        html {{
            font-size: 16px;
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', monospace;
            background: var(--deep-black);
            color: var(--terminal-green);
            line-height: var(--leading-normal);
            min-height: 100vh;
            min-height: -webkit-fill-available;
            overflow-x: hidden;
            position: relative;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(255, 0, 107, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(131, 56, 236, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(58, 134, 255, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 90% 90%, rgba(0, 255, 136, 0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}
        
        /* Container with gradient border - MORE GLOW */
        .frame {{
            min-height: 100vh;
            min-height: -webkit-fill-available;
            background: linear-gradient(135deg, 
                var(--miami-pink) 0%, 
                var(--vapor-purple) 25%, 
                var(--cyber-blue) 50%, 
                var(--terminal-green) 75%, 
                var(--sunset-yellow) 100%);
            background-size: 400% 400%;
            animation: gradient-shift 8s ease infinite;
            padding: 3px;
            position: relative;
        }}
        
        .frame::after {{
            content: '';
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: inherit;
            filter: blur(40px);
            opacity: 0.7;
            z-index: -1;
            animation: gradient-shift 8s ease infinite;
        }}
        
        @keyframes gradient-shift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        .viewport {{
            background: var(--deep-black);
            min-height: calc(100vh - 6px);
            min-height: calc(-webkit-fill-available - 6px);
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
        }}
        
        /* Header - Ultra minimal, synthwave glow */
        .header {{
            padding: var(--space-sm) var(--space-md);
            background: 
                linear-gradient(180deg, rgba(255,0,107,0.05) 0%, transparent 50%),
                linear-gradient(90deg, transparent, rgba(131,56,236,0.03), transparent);
            position: relative;
            display: flex;
            justify-content: center;
        }}
        
        .header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--miami-pink), 
                var(--vapor-purple), 
                var(--cyber-blue), 
                transparent);
            opacity: 0.6;
        }}
        
        @media (min-width: 768px) {{
            .header::after {{
                width: 300px;
            }}
        }}
        
        .header-content {{
            text-align: center;
            position: relative;
        }}
        
        @media (min-width: 768px) {{
            .header-content {{
                display: flex;
                align-items: center;
                gap: var(--space-lg);
            }}
        }}
        
        .system-title {{
            font-size: var(--text-xs);
            font-weight: 200;
            letter-spacing: 0.3em;
            color: var(--miami-pink);
            margin-bottom: 0;
            text-transform: uppercase;
            opacity: 0.7;
            text-shadow: 0 0 10px rgba(255, 0, 107, 0.5);
        }}
        
        .main-title {{
            font-size: var(--text-xl);
            font-weight: 700;
            letter-spacing: 0.05em;
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue), var(--terminal-green));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: var(--space-xs);
            text-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
            filter: drop-shadow(0 0 20px rgba(58, 134, 255, 0.4));
            text-transform: uppercase;
        }}
        
        .header-group {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        @media (min-width: 768px) {{
            .header-group {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
        
        .env-indicator {{
            display: inline-block;
            font-size: var(--text-xs);
            font-weight: 400;
            letter-spacing: 0.15em;
            color: var(--env-color);
            padding: 0.125rem 0.5rem;
            border: 1px solid var(--env-color);
            border-radius: 2px;
            text-transform: uppercase;
            box-shadow: 
                0 0 20px rgba(0, 255, 136, 0.3),
                inset 0 0 10px rgba(0, 255, 136, 0.1);
            align-self: center;
        }}
        
        @media (min-width: 768px) {{
            .env-indicator {{
                align-self: auto;
            }}
        }}
        
        /* Content area - compact for single viewport */
        .content {{
            flex: 1;
            padding: var(--space-md) var(--space-md);
            overflow-y: auto;
            overflow-x: hidden;
        }}
        
        .content-inner {{
            max-width: 100%;
            margin: 0 auto;
        }}
        
        @media (min-width: 768px) {{
            .content-inner {{
                max-width: 960px;
            }}
        }}
        
        /* Status grid - Mobile first, compact */
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--space-sm);
            margin-bottom: var(--space-md);
        }}
        
        @media (min-width: 640px) {{
            .status-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (min-width: 1024px) {{
            .status-grid {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        
        .status-card {{
            padding: var(--space-xs) var(--space-sm);
            background: linear-gradient(135deg, rgba(131,56,236,0.02), rgba(255,0,107,0.02));
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 2px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 
                0 0 15px rgba(131,56,236,0.1),
                inset 0 0 10px rgba(255,0,107,0.05);
        }}
        
        .status-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--terminal-green), 
                transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .status-card:hover {{
            border-color: var(--miami-pink);
            background: linear-gradient(135deg, rgba(255,0,107,0.05), rgba(131,56,236,0.05));
            box-shadow: 
                0 0 40px rgba(255,0,107,0.3),
                0 0 20px rgba(131,56,236,0.2),
                inset 0 0 20px rgba(58,134,255,0.1);
            transform: translateY(-1px);
        }}
        
        .status-card:hover::before {{
            opacity: 1;
        }}
        
        .status-value {{
            font-size: var(--text-lg);
            font-weight: 700;
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
            letter-spacing: -0.02em;
            filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.5));
        }}
        
        .status-label {{
            font-size: var(--text-xs);
            font-weight: 400;
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        /* Dashboard links - Touch optimized, compact */
        .dashboard-list {{
            display: grid;
            grid-template-columns: 1fr;
            gap: var(--space-xs);
            margin-bottom: var(--space-md);
        }}
        
        @media (min-width: 768px) {{
            .dashboard-list {{
                grid-template-columns: repeat(2, 1fr);
                gap: var(--space-sm);
            }}
        }}
        
        .dashboard-link {{
            display: flex;
            align-items: center;
            padding: var(--space-xs) var(--space-sm);
            background: linear-gradient(135deg, 
                rgba(255,0,107,0.01), 
                rgba(131,56,236,0.01),
                rgba(58,134,255,0.01));
            border: 1px solid rgba(131,56,236,0.15);
            border-radius: 2px;
            text-decoration: none;
            color: var(--terminal-green);
            transition: all 0.3s ease;
            min-height: 48px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(131,56,236,0.05);
        }}
        
        .dashboard-link::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,0,107,0.15),
                rgba(131,56,236,0.1),
                transparent);
            transition: left 0.5s ease;
        }}
        
        .dashboard-link:hover::before {{
            left: 100%;
        }}
        
        .dashboard-link:hover {{
            border-color: var(--miami-pink);
            background: linear-gradient(135deg, 
                rgba(255,0,107,0.08), 
                rgba(131,56,236,0.05),
                rgba(0,255,136,0.03));
            box-shadow: 
                0 0 30px rgba(255,0,107,0.25),
                0 0 15px rgba(131,56,236,0.2),
                inset 0 0 20px rgba(0,255,136,0.05);
            transform: translateX(2px);
        }}
        
        .dashboard-icon {{
            font-size: var(--text-lg);
            margin-right: var(--space-sm);
            min-width: 32px;
            text-align: center;
            filter: drop-shadow(0 0 5px var(--miami-pink));
        }}
        
        .dashboard-info {{
            flex: 1;
        }}
        
        .dashboard-title {{
            font-size: var(--text-base);
            font-weight: 700;
            margin-bottom: 0.25rem;
            letter-spacing: -0.01em;
        }}
        
        .dashboard-desc {{
            font-size: var(--text-sm);
            font-weight: 200;
            color: var(--gray-400);
            letter-spacing: 0.02em;
        }}
        
        .dashboard-arrow {{
            margin-left: var(--space-md);
            color: var(--gray-400);
            transition: transform 0.3s ease;
        }}
        
        .dashboard-link:hover .dashboard-arrow {{
            transform: translateX(4px);
            color: var(--terminal-green);
        }}
        
        
        /* Footer - Minimal, synthwave */
        .footer {{
            padding: var(--space-xs) var(--space-md);
            border-top: 1px solid transparent;
            text-align: center;
            background: linear-gradient(0deg, rgba(131,56,236,0.03) 0%, transparent 100%);
            border-image: linear-gradient(90deg, var(--cyber-blue), var(--vapor-purple), var(--miami-pink)) 1;
            position: relative;
        }}
        
        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--cyber-blue), 
                var(--vapor-purple), 
                var(--miami-pink), 
                transparent);
            opacity: 0.4;
        }}
        
        .footer-text {{
            font-size: var(--text-xs);
            color: var(--gray-400);
            letter-spacing: 0.1em;
        }}
        
        .footer-time {{
            color: var(--terminal-green);
            font-weight: 400;
            text-shadow: 0 0 10px rgba(0,255,136,0.5);
        }}
        
        /* System info - Compact, visible */
        .system-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-xs);
            padding: var(--space-sm);
            background: var(--soft-black);
            border: 1px solid var(--gray-800);
            border-radius: 2px;
            margin-bottom: var(--space-md);
        }}
        
        
        .system-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.25rem 0;
            font-size: var(--text-xs);
        }}
        
        .system-label {{
            color: var(--gray-400);
            font-weight: 200;
        }}
        
        .system-value {{
            color: var(--terminal-green);
            font-weight: 400;
        }}
        
        /* Pulse animation for live indicators */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .pulse {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        /* Mobile tap highlight removal */
        * {{
            -webkit-tap-highlight-color: transparent;
        }}
        
        /* Safe area insets for modern phones */
        @supports (padding: max(0px)) {{
            .viewport {{
                padding-left: max(0px, env(safe-area-inset-left));
                padding-right: max(0px, env(safe-area-inset-right));
            }}
            
            .footer {{
                padding-bottom: max(var(--space-lg), env(safe-area-inset-bottom));
            }}
        }}
    </style>
</head>
<body>
    <div class="frame">
        <div class="viewport">
            <header class="header">
                <div class="header-content">
                    <div class="header-group">
                        <div class="system-title">System Control</div>
                        <h1 class="main-title">SUPERADMIN</h1>
                    </div>
                    <span class="env-indicator">{environment}</span>
                </div>
            </header>
            
            
            <main class="content">
                <div class="content-inner">
                    <div class="status-grid">
                        <div class="status-card">
                            <div class="status-value">65</div>
                            <div class="status-label">Active Users</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value">12</div>
                            <div class="status-label">Pods Running</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value pulse">100%</div>
                            <div class="status-label">System Health</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value">v2.0</div>
                            <div class="status-label">Version</div>
                        </div>
                    </div>
                    
                    <div class="system-info">
                        <div class="system-row">
                            <span class="system-label">DATABASE</span>
                            <span class="system-value">SUPABASE.CO</span>
                        </div>
                        <div class="system-row">
                            <span class="system-label">RUNTIME</span>
                            <span class="system-value">FASTAPI</span>
                        </div>
                        <div class="system-row">
                            <span class="system-label">CORE</span>
                            <span class="system-value">BEHAVIORAL_INTELLIGENCE_V2</span>
                        </div>
                    </div>
                    
                    <nav class="dashboard-list">
                        <a href="/retro/admin" class="dashboard-link">
                            <span class="dashboard-icon">⚙️</span>
                            <div class="dashboard-info">
                                <div class="dashboard-title">Admin Dashboard</div>
                                <div class="dashboard-desc">System administration & user management</div>
                            </div>
                            <span class="dashboard-arrow">→</span>
                        </a>
                        
                        <a href="/retro/business" class="dashboard-link">
                            <span class="dashboard-icon">📊</span>
                            <div class="dashboard-info">
                                <div class="dashboard-title">Business Metrics</div>
                                <div class="dashboard-desc">Analytics, KPIs & conversion tracking</div>
                            </div>
                            <span class="dashboard-arrow">→</span>
                        </a>
                        
                        <a href="/retro/nurture" class="dashboard-link">
                            <span class="dashboard-icon">💬</span>
                            <div class="dashboard-info">
                                <div class="dashboard-title">Nurture Control</div>
                                <div class="dashboard-desc">Sequence management & engagement</div>
                            </div>
                            <span class="dashboard-arrow">→</span>
                        </a>
                        
                        <a href="/docs" class="dashboard-link">
                            <span class="dashboard-icon">📚</span>
                            <div class="dashboard-info">
                                <div class="dashboard-title">API Documentation</div>
                                <div class="dashboard-desc">Technical reference & endpoints</div>
                            </div>
                            <span class="dashboard-arrow">→</span>
                        </a>
                    </nav>
                </div>
            </main>
            
            <footer class="footer">
                <div class="footer-text">
                    SUPERADMIN v2.0 • UPTIME: 24H • 
                    <span class="footer-time" id="time">{datetime.now().strftime('%H:%M:%S')}</span>
                </div>
            </footer>
        </div>
    </div>
    
    <script>
        // Update time
        function updateTime() {{
            const now = new Date();
            const timeString = now.toTimeString().split(' ')[0];
            document.getElementById('time').textContent = timeString;
        }}
        
        setInterval(updateTime, 1000);
        
        // Mobile viewport height fix
        function setViewportHeight() {{
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        }}
        
        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            const links = {{
                '1': '/retro/admin',
                '2': '/retro/business',
                '3': '/retro/nurture',
                '4': '/docs'
            }};
            
            if (links[e.key]) {{
                window.location.href = links[e.key];
            }}
        }});
        
        // Touch feedback
        document.querySelectorAll('.dashboard-link, .status-card').forEach(el => {{
            el.addEventListener('touchstart', function() {{
                this.style.transform = 'scale(0.98)';
            }});
            
            el.addEventListener('touchend', function() {{
                this.style.transform = '';
            }});
        }});
    </script>
</body>
</html>
    """
    
    return html_content

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_evolved_superadmin_html()

@app.get("/evolved", response_class=HTMLResponse)
async def evolved_dashboard():
    return get_evolved_superadmin_html()

if __name__ == "__main__":
    import uvicorn
    print("🚀 RETRO EVOLVED - The Next Evolution")
    print("📱 Mobile-first terminal aesthetic")
    print("🎨 Miami Vice + Commodore 64 meets Swiss Design")
    print("💎 Running on http://localhost:7004")
    print("")
    print("Design Principles Applied:")
    print("  • Generous whitespace - nothing competes")
    print("  • Subtle hierarchy - size and weight only")
    print("  • Clinical precision - perfect alignment")
    print("  • Mobile-first responsive design")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=7004)