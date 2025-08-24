def get_nurture_control_html():
    """Generate nurture control dashboard with deep messaging visibility and AI-assisted sequences"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NURTURE CONTROL • THE PROGRESS METHOD</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@200;400;700&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            -webkit-tap-highlight-color: transparent;
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
            --text-xs: 0.75rem;
            --text-sm: 0.875rem;
            --text-base: 1rem;
            --text-lg: 1.25rem;
            --text-xl: 1.5rem;
        }}
        
        @media (min-width: 768px) {{
            :root {{
                --space-xs: 0.375rem;
                --space-sm: 0.625rem;
                --space-md: 1rem;
                --space-lg: 1.375rem;
                --text-xs: 0.6875rem;
                --text-sm: 0.75rem;
                --text-base: 0.875rem;
                --text-lg: 1.125rem;
                --text-xl: 1.5rem;
            }}
        }}
        
        html {{ font-size: 16px; }}
        
        body {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--deep-black);
            color: var(--terminal-green);
            min-height: 100vh;
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
                radial-gradient(circle at 40% 40%, rgba(58, 134, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
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
        
        .frame::after {{
            content: '';
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: inherit;
            filter: blur(20px);
            z-index: -1;
        }}
        
        .dashboard {{
            background: var(--deep-black);
            min-height: calc(100vh - 6px);
            position: relative;
            z-index: 1;
            padding: var(--space-md);
            overflow: auto;
        }}
        
        @keyframes gradient-shift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 0.8; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.8; }}
        }}
        
        /* Header */
        .header {{
            text-align: center;
            margin-bottom: var(--space-lg);
            position: relative;
        }}
        
        .header::after {{
            content: '';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, 
                var(--miami-pink), 
                var(--cyber-blue), 
                var(--terminal-green));
            border-radius: 1px;
        }}
        
        @media (min-width: 768px) {{
            .header::after {{
                width: 300px;
            }}
        }}
        
        .title {{
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
        
        .subtitle {{
            color: var(--gray-400);
            font-size: var(--text-sm);
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.2em;
        }}
        
        /* Tab Navigation */
        .tab-nav {{
            display: flex;
            justify-content: center;
            margin-bottom: var(--space-lg);
            border-bottom: 1px solid var(--gray-800);
            overflow-x: auto;
            gap: var(--space-xs);
        }}
        
        .tab {{
            background: linear-gradient(135deg, 
                rgba(255,0,107,0.01), 
                rgba(131,56,236,0.01),
                rgba(58,134,255,0.01));
            border: none;
            color: var(--gray-400);
            padding: var(--space-sm) var(--space-md);
            cursor: pointer;
            font-family: inherit;
            font-size: var(--text-sm);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 5px rgba(131,56,236,0.05);
        }}
        
        .tab:hover {{
            background: linear-gradient(135deg, rgba(255,0,107,0.08), rgba(131,56,236,0.05));
            color: var(--terminal-green);
            box-shadow: 
                0 0 20px rgba(255,0,107,0.2),
                0 0 10px rgba(131,56,236,0.15);
            transform: translateY(-1px);
            border-bottom-color: rgba(255,0,107,0.3);
        }}
        
        .tab.active {{
            color: var(--terminal-green);
            border-bottom-color: var(--terminal-green);
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            background: linear-gradient(135deg, rgba(255,0,107,0.1), rgba(131,56,236,0.08));
            box-shadow: 
                0 0 25px rgba(0, 255, 136, 0.3),
                0 0 15px rgba(131,56,236,0.2);
        }}
        
        .tab-panel {{
            display: none;
        }}
        
        .tab-panel.active {{
            display: block;
        }}
        
        /* Search Section */
        .search-section {{
            background: linear-gradient(135deg, 
                rgba(255,0,107,0.03), 
                rgba(131,56,236,0.02));
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 2px;
            padding: var(--space-md);
            margin-bottom: var(--space-lg);
            box-shadow: 0 0 15px rgba(131,56,236,0.1);
            transition: all 0.3s ease;
        }}
        
        .search-section:hover {{
            border-color: rgba(255,0,107,0.3);
            box-shadow: 
                0 0 25px rgba(255,0,107,0.15),
                0 0 15px rgba(131,56,236,0.1);
        }}
        
        .search-header {{
            color: var(--terminal-green);
            font-size: var(--text-lg);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: var(--space-md);
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }}
        
        .search-bar {{
            width: 100%;
            background: rgba(255,0,107,0.05);
            border: 1px solid rgba(255,0,107,0.3);
            border-radius: 2px;
            padding: var(--space-sm);
            color: var(--terminal-green);
            font-family: inherit;
            font-size: var(--text-sm);
            transition: all 0.3s ease;
        }}
        
        .search-bar:focus {{
            outline: none;
            border-color: var(--terminal-green);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
            background: rgba(0,255,136,0.05);
        }}
        
        .search-bar::placeholder {{
            color: var(--gray-400);
        }}
        
        /* Message Timeline */
        .timeline-container {{
            background: linear-gradient(135deg, 
                rgba(131,56,236,0.02), 
                rgba(255,0,107,0.01));
            border: 1px solid rgba(131,56,236,0.15);
            border-radius: 2px;
            padding: var(--space-md);
            margin-bottom: var(--space-lg);
            transition: all 0.3s ease;
        }}
        
        .timeline-container:hover {{
            border-color: rgba(255,0,107,0.2);
            box-shadow: 
                0 0 20px rgba(255,0,107,0.1),
                0 0 10px rgba(131,56,236,0.08);
        }}
        
        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-md);
        }}
        
        .timeline-title {{
            color: var(--miami-pink);
            font-size: var(--text-sm);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            text-shadow: 0 0 8px rgba(255, 0, 107, 0.5);
        }}
        
        .timeline-count {{
            color: var(--cyber-blue);
            font-size: var(--text-xs);
            font-weight: 700;
            padding: 2px var(--space-xs);
            background: rgba(58, 134, 255, 0.2);
            border: 1px solid var(--cyber-blue);
            border-radius: 2px;
        }}
        
        .message-item {{
            background: rgba(131,56,236,0.05);
            border-left: 3px solid var(--vapor-purple);
            padding: var(--space-sm);
            margin-bottom: var(--space-sm);
            transition: all 0.3s ease;
            border-radius: 2px;
            position: relative;
        }}
        
        .message-item:hover {{
            background: rgba(255,0,107,0.08);
            border-left-color: var(--miami-pink);
            box-shadow: 0 0 15px rgba(255,0,107,0.1);
            transform: translateX(3px);
        }}
        
        .message-item.core {{
            border-left-color: var(--terminal-green);
        }}
        
        .message-item.encouragement {{
            border-left-color: var(--cyber-blue);
        }}
        
        .message-item.ai-assisted {{
            border-left-color: var(--sunset-yellow);
            animation: pulse 3s ease-in-out infinite;
        }}
        
        .message-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-xs);
        }}
        
        .message-time {{
            color: var(--gray-400);
            font-size: var(--text-xs);
            font-weight: 400;
        }}
        
        .message-type {{
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-size: var(--text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .type-core {{
            background: rgba(0, 255, 136, 0.2);
            color: var(--terminal-green);
            border: 1px solid var(--terminal-green);
        }}
        
        .type-encouragement {{
            background: rgba(58, 134, 255, 0.2);
            color: var(--cyber-blue);
            border: 1px solid var(--cyber-blue);
        }}
        
        .type-ai {{
            background: rgba(255, 190, 11, 0.2);
            color: var(--sunset-yellow);
            border: 1px solid var(--sunset-yellow);
        }}
        
        .message-content {{
            color: var(--terminal-green);
            font-size: var(--text-sm);
            line-height: 1.4;
            margin-bottom: var(--space-xs);
        }}
        
        .message-channel {{
            display: inline-flex;
            align-items: center;
            gap: var(--space-xs);
            color: var(--gray-400);
            font-size: var(--text-xs);
            margin-right: var(--space-sm);
        }}
        
        .message-actions {{
            display: flex;
            gap: var(--space-xs);
            margin-top: var(--space-xs);
        }}
        
        .action-btn {{
            background: rgba(131,56,236,0.1);
            border: 1px solid rgba(131,56,236,0.3);
            color: var(--vapor-purple);
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-family: inherit;
            font-size: var(--text-xs);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .action-btn:hover {{
            background: rgba(131,56,236,0.3);
            box-shadow: 0 0 10px rgba(131,56,236,0.3);
            color: var(--terminal-green);
        }}
        
        .edit-btn {{
            background: rgba(255,0,107,0.1);
            border-color: var(--miami-pink);
            color: var(--miami-pink);
        }}
        
        .edit-btn:hover {{
            background: rgba(255,0,107,0.3);
            box-shadow: 0 0 10px rgba(255,0,107,0.3);
        }}
        
        /* Sequence Builder */
        .sequence-section {{
            background: linear-gradient(135deg, 
                rgba(131,56,236,0.02), 
                rgba(255,0,107,0.01));
            border: 1px solid rgba(131,56,236,0.15);
            border-radius: 2px;
            padding: var(--space-md);
            margin-bottom: var(--space-lg);
            transition: all 0.3s ease;
        }}
        
        .sequence-section:hover {{
            border-color: rgba(255,0,107,0.2);
            box-shadow: 
                0 0 20px rgba(255,0,107,0.1),
                0 0 10px rgba(131,56,236,0.08);
            transform: translateY(-1px);
        }}
        
        .layer-indicator {{
            display: flex;
            gap: var(--space-sm);
            margin-bottom: var(--space-md);
        }}
        
        .layer {{
            flex: 1;
            padding: var(--space-sm);
            border-radius: 2px;
            text-align: center;
            font-size: var(--text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .layer.core {{
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--terminal-green);
            color: var(--terminal-green);
        }}
        
        .layer.encouragement {{
            background: rgba(58, 134, 255, 0.1);
            border: 1px solid var(--cyber-blue);
            color: var(--cyber-blue);
        }}
        
        .layer.ai {{
            background: rgba(255, 190, 11, 0.1);
            border: 1px solid var(--sunset-yellow);
            color: var(--sunset-yellow);
        }}
        
        .layer:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 15px currentColor;
        }}
        
        .layer.active {{
            background: currentColor;
            color: var(--deep-black);
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--space-sm);
            margin-bottom: var(--space-lg);
        }}
        
        @media (min-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(4, 1fr);
                gap: var(--space-md);
            }}
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, 
                rgba(131,56,236,0.02), 
                rgba(255,0,107,0.02));
            border: 1px solid rgba(131,56,236,0.2);
            border-radius: 2px;
            padding: var(--space-sm);
            text-align: center;
            transition: all 0.3s ease;
            overflow: hidden;
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
            font-weight: 400;
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        /* AI Status Indicator */
        .ai-status {{
            position: fixed;
            bottom: var(--space-md);
            right: var(--space-md);
            background: rgba(255, 190, 11, 0.1);
            border: 1px solid var(--sunset-yellow);
            padding: var(--space-xs) var(--space-sm);
            border-radius: 2px;
            font-size: var(--text-xs);
            color: var(--sunset-yellow);
            animation: pulse 2s ease-in-out infinite;
            z-index: 100;
        }}
        
        .ai-status.active {{
            background: rgba(0, 255, 136, 0.1);
            border-color: var(--terminal-green);
            color: var(--terminal-green);
        }}
        
        /* Navigation */
        .nav-links {{
            display: flex;
            justify-content: center;
            gap: var(--space-sm);
            margin-top: var(--space-lg);
            flex-wrap: wrap;
        }}
        
        .nav-link {{
            color: var(--cyber-blue);
            text-decoration: none;
            font-size: var(--text-xs);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: var(--space-xs) var(--space-sm);
            border: 1px solid rgba(58,134,255,0.3);
            border-radius: 2px;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, rgba(58,134,255,0.05), rgba(131,56,236,0.02));
        }}
        
        .nav-link:hover {{
            color: var(--terminal-green);
            border-color: var(--terminal-green);
            background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(58,134,255,0.05));
            box-shadow: 0 0 15px rgba(0,255,136,0.3);
        }}
        
        /* Message Editor Modal (hidden by default) */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 17, 0.95);
            z-index: 1000;
            padding: var(--space-lg);
            overflow: auto;
        }}
        
        .modal.active {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .modal-content {{
            background: var(--deep-black);
            border: 2px solid var(--miami-pink);
            border-radius: 2px;
            padding: var(--space-lg);
            max-width: 600px;
            width: 100%;
            box-shadow: 0 0 50px rgba(255, 0, 107, 0.3);
        }}
        
        .modal-header {{
            color: var(--terminal-green);
            font-size: var(--text-lg);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: var(--space-md);
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }}
        
        .modal-textarea {{
            width: 100%;
            min-height: 150px;
            background: rgba(255,0,107,0.05);
            border: 1px solid rgba(255,0,107,0.3);
            border-radius: 2px;
            padding: var(--space-sm);
            color: var(--terminal-green);
            font-family: inherit;
            font-size: var(--text-sm);
            resize: vertical;
        }}
        
        .modal-textarea:focus {{
            outline: none;
            border-color: var(--terminal-green);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }}
        
        .modal-actions {{
            display: flex;
            gap: var(--space-sm);
            margin-top: var(--space-md);
            justify-content: flex-end;
        }}
        
        .save-btn {{
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue));
            border: none;
            color: var(--deep-black);
            padding: var(--space-xs) var(--space-sm);
            border-radius: 2px;
            font-family: inherit;
            font-size: var(--text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .save-btn:hover {{
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            transform: translateY(-1px);
        }}
        
        .cancel-btn {{
            background: rgba(255, 0, 107, 0.2);
            border: 1px solid var(--miami-pink);
            color: var(--miami-pink);
            padding: var(--space-xs) var(--space-sm);
            border-radius: 2px;
            font-family: inherit;
            font-size: var(--text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .cancel-btn:hover {{
            background: rgba(255, 0, 107, 0.4);
            box-shadow: 0 0 10px rgba(255, 0, 107, 0.3);
        }}
    </style>
</head>
<body>
    <div class="frame">
        <div class="dashboard">
            <div class="header">
                <div class="title">Nurture Control</div>
            </div>
            
            <div class="tab-nav">
                <button class="tab active" onclick="showTab('user-view')">User View</button>
                <button class="tab" onclick="showTab('sequences')">Sequences</button>
                <button class="tab" onclick="showTab('templates')">Templates</button>
                <button class="tab" onclick="showTab('analytics')">Analytics</button>
            </div>
            
            <!-- USER VIEW TAB -->
            <div id="user-view" class="tab-panel active">
                <div class="search-section">
                    <div class="search-header">Search User</div>
                    <input 
                        type="text" 
                        class="search-bar" 
                        placeholder="Enter user name, email, or ID to view their nurture timeline..."
                        oninput="searchUsers(this.value)"
                        onkeypress="if(event.key==='Enter') loadUserTimeline(this.value)"
                    >
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">7</div>
                        <div class="stat-label">Upcoming Messages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">3</div>
                        <div class="stat-label">AI Personalized</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">92%</div>
                        <div class="stat-label">Engagement Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">ACTIVE</div>
                        <div class="stat-label">User State</div>
                    </div>
                </div>
                
                <div class="timeline-container">
                    <div class="timeline-header">
                        <div class="timeline-title">Next 7 Days Timeline - Sarah Chen</div>
                        <div class="timeline-count">7 Messages</div>
                    </div>
                    
                    <!-- Core Infrastructure Messages -->
                    <div class="message-item core">
                        <div class="message-header">
                            <div class="message-time">Today, 6:00 PM</div>
                            <div class="message-type type-core">CORE</div>
                        </div>
                        <div class="message-content">
                            📞 Pod call reminder: Your weekly accountability call starts in 1 hour. Join here: meet.google.com/abc-defg-hij
                        </div>
                        <div class="message-channel">
                            <span>📱 SMS</span>
                            <span>✉️ Email</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(1)">Edit</button>
                            <button class="action-btn">Reschedule</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <div class="message-item core">
                        <div class="message-header">
                            <div class="message-time">Tomorrow, 9:00 AM</div>
                            <div class="message-type type-core">CORE</div>
                        </div>
                        <div class="message-content">
                            ✅ Time to set your commitments for the week! Reply with 3 specific actions you'll take this week.
                        </div>
                        <div class="message-channel">
                            <span>💬 Telegram</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(2)">Edit</button>
                            <button class="action-btn">Reschedule</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <!-- Encouragement Messages -->
                    <div class="message-item encouragement">
                        <div class="message-header">
                            <div class="message-time">Wed, 2:00 PM</div>
                            <div class="message-type type-encouragement">ENCOURAGEMENT</div>
                        </div>
                        <div class="message-content">
                            🔥 Midweek check-in! You're on a 7-day streak! Your recent commitments: [✅ Morning routine, ✅ Sales calls, ⏳ Content creation]. Keep pushing!
                        </div>
                        <div class="message-channel">
                            <span>💬 Telegram</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(3)">Edit</button>
                            <button class="action-btn">Reschedule</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <!-- AI-Assisted Messages -->
                    <div class="message-item ai-assisted">
                        <div class="message-header">
                            <div class="message-time">Thu, 10:00 AM</div>
                            <div class="message-type type-ai">AI-ASSISTED</div>
                        </div>
                        <div class="message-content">
                            💪 Sarah, you've completed 82% of your commitments this week - that's above your average! Your consistency with morning routines is paying off. How about tackling that content creation today?
                        </div>
                        <div class="message-channel">
                            <span>💬 Telegram</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(4)">Edit</button>
                            <button class="action-btn">Regenerate</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <div class="message-item encouragement">
                        <div class="message-header">
                            <div class="message-time">Fri, 5:00 PM</div>
                            <div class="message-type type-encouragement">ENCOURAGEMENT</div>
                        </div>
                        <div class="message-content">
                            📊 Weekly wrap-up: 6/7 commitments completed! Your pod is crushing it with 89% completion rate. Weekend warrior mode: ON! 
                        </div>
                        <div class="message-channel">
                            <span>✉️ Email</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(5)">Edit</button>
                            <button class="action-btn">Reschedule</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <div class="message-item ai-assisted">
                        <div class="message-header">
                            <div class="message-time">Sat, 11:00 AM</div>
                            <div class="message-type type-ai">AI-ASSISTED</div>
                        </div>
                        <div class="message-content">
                            🎯 Pattern detected: Your best productivity happens Mon-Wed. Consider front-loading your hardest commitments early in the week. You've got this!
                        </div>
                        <div class="message-channel">
                            <span>💬 Telegram</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(6)">Edit</button>
                            <button class="action-btn">Regenerate</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                    
                    <div class="message-item core">
                        <div class="message-header">
                            <div class="message-time">Sun, 6:00 PM</div>
                            <div class="message-type type-core">CORE</div>
                        </div>
                        <div class="message-content">
                            📅 Weekly reflection time! Review your commitments and prepare for tomorrow's pod call. What worked? What needs adjustment?
                        </div>
                        <div class="message-channel">
                            <span>📱 SMS</span>
                            <span>✉️ Email</span>
                        </div>
                        <div class="message-actions">
                            <button class="action-btn edit-btn" onclick="editMessage(7)">Edit</button>
                            <button class="action-btn">Reschedule</button>
                            <button class="action-btn">Skip</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- SEQUENCES TAB -->
            <div id="sequences" class="tab-panel">
                <div class="sequence-section">
                    <div class="timeline-title">Message Layer Architecture</div>
                    <div class="layer-indicator">
                        <div class="layer core active">
                            Core Infrastructure
                            <br><small>Essential notifications</small>
                        </div>
                        <div class="layer encouragement">
                            Encouragement Layer
                            <br><small>Progress & motivation</small>
                        </div>
                        <div class="layer ai">
                            AI Intelligence
                            <br><small>Personalized insights</small>
                        </div>
                    </div>
                </div>
                
                <div class="sequence-section">
                    <div class="timeline-title">Active Sequences</div>
                    <div class="timeline-container" style="margin-top: var(--space-md);">
                        <div class="data-row">
                            <span>Onboarding Sequence</span>
                            <span style="color: var(--terminal-green);">12 Active Users</span>
                        </div>
                        <div class="data-row">
                            <span>Weekly Accountability</span>
                            <span style="color: var(--terminal-green);">247 Active Users</span>
                        </div>
                        <div class="data-row">
                            <span>Re-engagement Campaign</span>
                            <span style="color: var(--sunset-yellow);">8 Active Users</span>
                        </div>
                        <div class="data-row">
                            <span>Streak Celebration</span>
                            <span style="color: var(--terminal-green);">34 Active Users</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- TEMPLATES TAB -->
            <div id="templates" class="tab-panel">
                <div class="sequence-section">
                    <div class="timeline-title">Message Templates</div>
                    <div class="timeline-container" style="margin-top: var(--space-md);">
                        <div class="data-row">
                            <span>Call Reminders</span>
                            <button class="action-btn">Edit Template</button>
                        </div>
                        <div class="data-row">
                            <span>Commitment Prompts</span>
                            <button class="action-btn">Edit Template</button>
                        </div>
                        <div class="data-row">
                            <span>Streak Celebrations</span>
                            <button class="action-btn">Edit Template</button>
                        </div>
                        <div class="data-row">
                            <span>Recovery Messages</span>
                            <button class="action-btn">Edit Template</button>
                        </div>
                        <div class="data-row">
                            <span>Weekly Summaries</span>
                            <button class="action-btn">Edit Template</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ANALYTICS TAB -->
            <div id="analytics" class="tab-panel">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">1,247</div>
                        <div class="stat-label">Messages Sent Today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">68%</div>
                        <div class="stat-label">Open Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">42%</div>
                        <div class="stat-label">Response Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">2.3%</div>
                        <div class="stat-label">Opt-Out Rate</div>
                    </div>
                </div>
                
                <div class="sequence-section">
                    <div class="timeline-title">Performance by Layer</div>
                    <div class="timeline-container" style="margin-top: var(--space-md);">
                        <div class="data-row">
                            <span>Core Infrastructure</span>
                            <span style="color: var(--terminal-green);">94% Delivery Rate</span>
                        </div>
                        <div class="data-row">
                            <span>Encouragement Messages</span>
                            <span style="color: var(--cyber-blue);">72% Engagement</span>
                        </div>
                        <div class="data-row">
                            <span>AI-Assisted Messages</span>
                            <span style="color: var(--sunset-yellow);">89% Positive Sentiment</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/retro/superadmin" class="nav-link">SuperAdmin</a>
                <a href="/retro/admin" class="nav-link">Admin Control</a>
                <a href="/retro/business" class="nav-link">Business</a>
                <a href="/docs" class="nav-link">API Docs</a>
            </div>
        </div>
    </div>
    
    <!-- Message Editor Modal -->
    <div id="messageModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">Edit Message</div>
            <textarea class="modal-textarea" id="messageEditor">
Loading message content...
            </textarea>
            <div class="modal-actions">
                <button class="cancel-btn" onclick="closeModal()">Cancel</button>
                <button class="save-btn" onclick="saveMessage()">Save Changes</button>
            </div>
        </div>
    </div>
    
    <!-- AI Status Indicator -->
    <div class="ai-status active">
        🤖 AI Intelligence Active
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all panels
            document.querySelectorAll('.tab-panel').forEach(panel => {{
                panel.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected panel
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function searchUsers(query) {{
            if (query.length < 2) return;
            console.log('Searching for user:', query);
        }}
        
        function loadUserTimeline(query) {{
            if (query.length < 2) return;
            console.log('Loading timeline for:', query);
            // In real implementation, would load user-specific timeline
        }}
        
        function editMessage(messageId) {{
            console.log('Editing message:', messageId);
            const modal = document.getElementById('messageModal');
            const editor = document.getElementById('messageEditor');
            
            // Get the message content from the clicked message
            const messageItem = event.target.closest('.message-item');
            const content = messageItem.querySelector('.message-content').textContent;
            
            editor.value = content.trim();
            modal.classList.add('active');
        }}
        
        function closeModal() {{
            document.getElementById('messageModal').classList.remove('active');
        }}
        
        function saveMessage() {{
            const content = document.getElementById('messageEditor').value;
            console.log('Saving message:', content);
            alert('Message updated successfully!');
            closeModal();
        }}
        
        // Simulate AI status changes
        setInterval(() => {{
            const status = document.querySelector('.ai-status');
            const isActive = Math.random() > 0.3;
            
            if (isActive) {{
                status.classList.add('active');
                status.textContent = '🤖 AI Intelligence Active';
            }} else {{
                status.classList.remove('active');
                status.textContent = '🤖 AI Processing...';
            }}
        }}, 5000);
        
        // Helper for data rows
        document.querySelectorAll('.data-row').forEach(row => {{
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.padding = 'var(--space-xs) var(--space-sm)';
            row.style.borderBottom = '1px solid rgba(131,56,236,0.1)';
            row.style.fontSize = 'var(--text-sm)';
            row.style.transition = 'all 0.3s ease';
            
            row.addEventListener('mouseenter', () => {{
                row.style.background = 'rgba(255,0,107,0.05)';
                row.style.paddingLeft = 'var(--space-md)';
            }});
            
            row.addEventListener('mouseleave', () => {{
                row.style.background = 'transparent';
                row.style.paddingLeft = 'var(--space-sm)';
            }});
        }});
    </script>
</body>
</html>
"""
    return html_content