#!/usr/bin/env python3
"""
USER DASHBOARD TEMPLATE FOR 1.0 LAUNCH
=======================================
Personalized dashboard showing user progress, achievements, and pod info
"""

def get_user_dashboard_html(user_data: dict) -> str:
    """Generate personalized user dashboard HTML"""
    
    # Extract user data
    user_name = user_data.get("user_name", "User")
    total_commitments = user_data.get("total_commitments", 0)
    completed_commitments = user_data.get("completed_commitments", 0)
    completion_rate = user_data.get("completion_rate", 0)
    current_streak = user_data.get("current_streak", 0)
    pod_info = user_data.get("pod_info")
    achievements = user_data.get("achievements", [])
    recent_commitments = user_data.get("recent_commitments", [])
    
    # Pod section HTML
    pod_section = ""
    if pod_info:
        pod_members_count = len(pod_info.get("members", []))
        pod_section = f"""
        <div class="pod-section">
            <div class="section-header">
                <h3>🤝 Your Pod</h3>
            </div>
            <div class="pod-card">
                <div class="pod-name">{pod_info.get("pod_name", "Your Pod")}</div>
                <div class="pod-details">
                    <div class="pod-stat">
                        <span class="stat-value">{pod_members_count}</span>
                        <span class="stat-label">Members</span>
                    </div>
                    <div class="pod-stat">
                        <span class="stat-value">Mon</span>
                        <span class="stat-label">Meeting Day</span>
                    </div>
                    <div class="pod-stat">
                        <span class="stat-value">{pod_info.get("meeting_time", "19:00")}</span>
                        <span class="stat-label">Meeting Time</span>
                    </div>
                </div>
            </div>
        </div>
        """
    else:
        pod_section = """
        <div class="pod-section">
            <div class="section-header">
                <h3>🤝 Join a Pod</h3>
            </div>
            <div class="join-pod-card">
                <p>Ready for accountability and community support?</p>
                <p>Join a pod to connect with other committed achievers!</p>
                <div class="join-pod-btn">Contact admin to join a pod</div>
            </div>
        </div>
        """
    
    # Achievements HTML
    achievements_html = ""
    if achievements:
        achievements_html = "".join([f'<span class="achievement-badge">{achievement}</span>' for achievement in achievements])
    else:
        achievements_html = '<span class="no-achievements">Complete your first commitment to earn achievements!</span>'
    
    # Recent commitments HTML
    recent_html = ""
    if recent_commitments:
        for commitment in recent_commitments[-3:]:  # Show last 3
            status_icon = "✅" if commitment.get("status") == "completed" else "⏳"
            commitment_text = commitment.get("commitment", "")[:60] + ("..." if len(commitment.get("commitment", "")) > 60 else "")
            recent_html += f"""
            <div class="commitment-item">
                <span class="commitment-status">{status_icon}</span>
                <span class="commitment-text">{commitment_text}</span>
            </div>
            """
    else:
        recent_html = '<div class="no-commitments">No commitments yet. Start your journey today!</div>'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <title>Progress Dashboard • {user_name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@200;400;700&display=swap');
        
        /* Cache buster - forces fresh CSS load */
        html {{ --cache-bust: {user_name}-v3-evolved; }}
        
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
            
            --space-xs: 0.25rem;
            --space-sm: 0.5rem;
            --space-md: 0.875rem;
            --space-lg: 1.25rem;
            --space-xl: 1.75rem;
            --space-2xl: 2.25rem;
            
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
                
                --text-xs: 0.6875rem;
                --text-sm: 0.75rem;
                --text-base: 0.875rem;
                --text-lg: 1.125rem;
                --text-xl: 1.5rem;
                --text-2xl: 1.875rem;
                --text-3xl: 2.5rem;
            }}
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
        
        .frame {{
            min-height: 100vh;
            min-height: -webkit-fill-available;
            background: 
                radial-gradient(2px 2px at 20px 30px, #eee, transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
                radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.6), transparent),
                radial-gradient(2px 2px at 160px 30px, #fff, transparent),
                radial-gradient(1px 1px at 200px 60px, rgba(255,255,255,0.9), transparent),
                radial-gradient(2px 2px at 240px 90px, #eee, transparent),
                radial-gradient(1px 1px at 280px 40px, rgba(255,255,255,0.7), transparent),
                radial-gradient(2px 2px at 320px 70px, #fff, transparent),
                radial-gradient(1px 1px at 360px 20px, rgba(255,255,255,0.8), transparent),
                radial-gradient(ellipse 800px 200px at 50% 0%, rgba(131,56,236,0.1), transparent),
                radial-gradient(ellipse 600px 400px at 80% 100%, rgba(255,0,107,0.08), transparent),
                linear-gradient(180deg, #000011 0%, #0a0a1a 100%);
            background-size: 
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                400px 200px,
                100% 100%,
                100% 100%,
                100% 100%;
            background-repeat: repeat;
            position: relative;
        }}
        
        .viewport {{
            background: rgba(0,0,17,0.85);
            backdrop-filter: blur(1px);
            min-height: calc(100vh - 6px);
            min-height: calc(-webkit-fill-available - 6px);
            max-width: 600px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 8px;
        }}
        
        .header {{
            padding: var(--space-sm) var(--space-md);
            background: 
                linear-gradient(180deg, rgba(255,0,107,0.05) 0%, transparent 50%),
                linear-gradient(90deg, transparent, rgba(131,56,236,0.03), transparent);
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
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
        
        .user-title {{
            font-size: var(--text-2xl);
            font-weight: 700;
            color: white;
            margin-bottom: var(--space-xs);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-shadow: 
                0 0 5px rgba(255,255,255,0.36),
                0 0 10px rgba(255,255,255,0.28),
                0 0 14px rgba(131,56,236,0.2),
                0 0 19px rgba(255,0,107,0.12);
            filter: drop-shadow(0 0 8px rgba(255,255,255,0.32));
        }}
        
        .user-subtitle {{
            font-size: var(--text-sm);
            color: var(--gray-400);
            font-weight: 200;
            letter-spacing: 0.1em;
        }}
        
        .content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            position: relative;
            z-index: 10;
        }}
        
        .content-inner {{
            padding: var(--space-md);
            padding-top: var(--space-lg);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--space-sm);
            margin-bottom: var(--space-lg);
        }}
        
        @media (min-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        
        .stat-card {{
            padding: var(--space-xs) var(--space-sm);
            background: linear-gradient(135deg, rgba(131,56,236,0.02), rgba(255,0,107,0.02));
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 2px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            text-align: center;
            box-shadow: 
                0 0 15px rgba(131,56,236,0.1),
                inset 0 0 10px rgba(255,0,107,0.05);
        }}
        
        .stat-card:hover {{
            border-color: var(--miami-pink);
            background: linear-gradient(135deg, rgba(255,0,107,0.05), rgba(131,56,236,0.05));
            box-shadow: 
                0 0 40px rgba(255,0,107,0.3),
                0 0 20px rgba(131,56,236,0.2),
                inset 0 0 20px rgba(58,134,255,0.1);
            transform: translateY(-1px);
        }}
        
        .stat-value {{
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
        
        .stat-label {{
            font-size: var(--text-xs);
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 400;
            margin-top: var(--space-xs);
        }}
        
        .section {{
            margin-bottom: var(--space-xl);
        }}
        
        .section-header {{
            margin-bottom: var(--space-md);
            padding-bottom: var(--space-xs);
            border-bottom: 1px solid rgba(131,56,236,0.2);
        }}
        
        .section-header h3 {{
            font-size: var(--text-lg);
            font-weight: 700;
            color: white;
            letter-spacing: 0.02em;
            text-shadow: 
                0 0 3px rgba(255,255,255,0.36),
                0 0 6px rgba(255,255,255,0.24),
                0 0 10px rgba(0,255,136,0.16);
            filter: drop-shadow(0 0 4px rgba(255,255,255,0.2));
        }}
        
        .pod-card {{
            background: linear-gradient(135deg, rgba(58,134,255,0.05), rgba(131,56,236,0.05));
            border: 1px solid rgba(58,134,255,0.3);
            border-radius: 4px;
            padding: var(--space-md);
        }}
        
        .pod-name {{
            font-size: var(--text-lg);
            font-weight: 700;
            color: white;
            margin-bottom: var(--space-sm);
            text-shadow: 
                0 0 3px rgba(255,255,255,0.36),
                0 0 6px rgba(58,134,255,0.24);
        }}
        
        .pod-details {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--space-sm);
        }}
        
        .pod-stat {{
            text-align: center;
        }}
        
        .pod-stat .stat-value {{
            font-size: var(--text-base);
            color: white;
            font-weight: 700;
            text-shadow: 
                0 0 2px rgba(255,255,255,0.32),
                0 0 5px rgba(0,255,136,0.2);
        }}
        
        .pod-stat .stat-label {{
            font-size: var(--text-xs);
            color: var(--gray-400);
            text-transform: uppercase;
        }}
        
        .join-pod-card {{
            background: linear-gradient(135deg, rgba(255,190,11,0.05), rgba(255,0,107,0.05));
            border: 1px solid rgba(255,190,11,0.3);
            border-radius: 4px;
            padding: var(--space-md);
            text-align: center;
        }}
        
        .join-pod-card p {{
            margin-bottom: var(--space-sm);
            color: var(--gray-400);
        }}
        
        .join-pod-btn {{
            display: inline-block;
            padding: var(--space-sm) var(--space-md);
            background: linear-gradient(135deg, var(--sunset-yellow), var(--miami-pink));
            color: var(--deep-black);
            border-radius: 4px;
            font-weight: 700;
            font-size: var(--text-sm);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        
        .join-pod-btn:hover {{
            transform: scale(1.05);
        }}
        
        .achievements-section {{
            background: linear-gradient(135deg, rgba(131,56,236,0.02), rgba(255,0,107,0.02));
            border: 1px solid rgba(131,56,236,0.15);
            border-radius: 4px;
            padding: var(--space-md);
        }}
        
        .achievement-badge {{
            display: inline-block;
            padding: var(--space-xs) var(--space-sm);
            background: linear-gradient(135deg, rgba(131,56,236,0.3), rgba(255,0,107,0.3));
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px;
            font-size: var(--text-sm);
            font-weight: 700;
            margin: var(--space-xs);
            text-shadow: 
                0 0 2px rgba(255,255,255,0.36),
                0 0 5px rgba(255,255,255,0.24);
            box-shadow: 
                0 0 8px rgba(131,56,236,0.16),
                0 0 16px rgba(255,0,107,0.08),
                inset 0 1px 0 rgba(255,255,255,0.08);
        }}
        
        .no-achievements {{
            color: var(--gray-400);
            font-style: italic;
            text-align: center;
            padding: var(--space-md);
        }}
        
        .commitments-list {{
            background: var(--soft-black);
            border: 1px solid var(--gray-800);
            border-radius: 4px;
            padding: var(--space-md);
        }}
        
        .commitment-item {{
            display: flex;
            align-items: center;
            padding: var(--space-sm) 0;
            border-bottom: 1px solid var(--gray-800);
        }}
        
        .commitment-item:last-child {{
            border-bottom: none;
        }}
        
        .commitment-status {{
            margin-right: var(--space-sm);
            font-size: var(--text-lg);
        }}
        
        .commitment-text {{
            color: var(--gray-400);
            font-size: var(--text-sm);
            flex: 1;
        }}
        
        .no-commitments {{
            color: var(--gray-400);
            font-style: italic;
            text-align: center;
            padding: var(--space-lg);
        }}
        
        .footer {{
            padding: var(--space-sm) var(--space-md);
            border-top: 1px solid rgba(131,56,236,0.2);
            text-align: center;
            background: linear-gradient(0deg, rgba(131,56,236,0.03) 0%, transparent 100%);
        }}
        
        .footer-text {{
            font-size: var(--text-xs);
            color: var(--gray-400);
            letter-spacing: 0.1em;
        }}
        
        .footer-time {{
            color: var(--terminal-green);
            font-weight: 400;
        }}
    </style>
</head>
<body>
    <div class="frame">
        <div class="viewport">
            <header class="header">
                <h1 class="user-title">{user_name}'S SCOREBOARD</h1>
                <p class="user-subtitle">Your commitment journey</p>
            </header>
            
            <main class="content">
                <div class="content-inner">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="stat-value">{total_commitments}</span>
                            <span class="stat-label">Total</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-value">{completed_commitments}</span>
                            <span class="stat-label">Completed</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-value">{completion_rate}%</span>
                            <span class="stat-label">Success Rate</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-value">{current_streak}</span>
                            <span class="stat-label">Current Streak</span>
                        </div>
                    </div>
                    
                    {pod_section}
                    
                    <div class="section">
                        <div class="section-header">
                            <h3>🏆 Achievements</h3>
                        </div>
                        <div class="achievements-section">
                            {achievements_html}
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-header">
                            <h3>📝 Recent Commitments</h3>
                        </div>
                        <div class="commitments-list">
                            {recent_html}
                        </div>
                    </div>
                </div>
            </main>
            
            <footer class="footer">
                <div class="footer-text">
                    Progress Method • Keep going! • 
                    <span class="footer-time" id="time">Loading...</span>
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
        updateTime();
        
        // Mobile viewport height fix
        function setViewportHeight() {{
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        }}
        
        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        
        // Achievement badges animation
        document.querySelectorAll('.achievement-badge').forEach((badge, index) => {{
            setTimeout(() => {{
                badge.style.animation = 'fadeIn 0.5s ease forwards';
            }}, index * 100);
        }});
        
        // Touch feedback for interactive elements
        document.querySelectorAll('.stat-card, .achievement-badge, .pod-card').forEach(el => {{
            el.addEventListener('touchstart', function() {{
                this.style.transform = 'scale(0.98)';
            }});
            
            el.addEventListener('touchend', function() {{
                this.style.transform = '';
            }});
        }});
        
        // Add CSS for fade-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .achievement-badge {{
                opacity: 0;
            }}
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>"""