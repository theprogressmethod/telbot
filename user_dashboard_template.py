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
        }}
        
        body {{
            font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', monospace;
            background: var(--deep-black);
            color: var(--terminal-green);
            line-height: 1.5;
            min-height: 100vh;
            position: relative;
        }}
        
        .frame {{
            min-height: 100vh;
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
        
        @keyframes gradient-shift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        .viewport {{
            background: var(--deep-black);
            min-height: calc(100vh - 6px);
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
        }}
        
        .header {{
            padding: var(--space-md);
            background: linear-gradient(180deg, rgba(255,0,107,0.05) 0%, transparent 50%);
            text-align: center;
            border-bottom: 1px solid rgba(131,56,236,0.2);
        }}
        
        .user-title {{
            font-size: var(--text-2xl);
            font-weight: 700;
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: var(--space-xs);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .user-subtitle {{
            font-size: var(--text-sm);
            color: var(--gray-400);
            font-weight: 200;
            letter-spacing: 0.1em;
        }}
        
        .content {{
            flex: 1;
            padding: var(--space-md);
            overflow-y: auto;
            position: relative;
            z-index: 10;
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
            padding: var(--space-sm) var(--space-md);
            background: linear-gradient(135deg, rgba(131,56,236,0.03), rgba(255,0,107,0.03));
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 4px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            z-index: 10;
        }}
        
        .stat-card:hover {{
            border-color: var(--miami-pink);
            background: linear-gradient(135deg, rgba(255,0,107,0.08), rgba(131,56,236,0.05));
            transform: translateY(-2px);
        }}
        
        .stat-value {{
            font-size: var(--text-xl);
            font-weight: 700;
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: block;
            margin-bottom: var(--space-xs);
            position: relative;
            z-index: 20;
        }}
        
        .stat-label {{
            font-size: var(--text-xs);
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 400;
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
            color: var(--terminal-green);
            letter-spacing: 0.02em;
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
            color: var(--cyber-blue);
            margin-bottom: var(--space-sm);
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
            color: var(--terminal-green);
            font-weight: 700;
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
            background: linear-gradient(135deg, var(--vapor-purple), var(--miami-pink));
            color: white;
            border-radius: 20px;
            font-size: var(--text-sm);
            font-weight: 700;
            margin: var(--space-xs);
            box-shadow: 0 0 15px rgba(131, 56, 236, 0.3);
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
                <h1 class="user-title">{user_name}'s Progress</h1>
                <p class="user-subtitle">Your commitment journey</p>
            </header>
            
            <main class="content">
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