def get_unified_admin_html():
    """Generate unified admin dashboard with Users and Pods tabs"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ADMIN CONTROL • THE PROGRESS METHOD</title>
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
        
        /* Profile Section (shared between users and pods) */
        .profile {{
            display: none;
            background: linear-gradient(135deg, 
                rgba(255,0,107,0.02), 
                rgba(131,56,236,0.01));
            border: 1px solid rgba(131,56,236,0.15);
            border-radius: 2px;
            margin-bottom: var(--space-lg);
            box-shadow: 0 0 10px rgba(131,56,236,0.05);
            transition: all 0.3s ease;
        }}
        
        .profile.active {{
            display: block;
        }}
        
        .profile:hover {{
            border-color: rgba(255,0,107,0.2);
            box-shadow: 
                0 0 20px rgba(255,0,107,0.1),
                0 0 10px rgba(131,56,236,0.08);
        }}
        
        .profile-header {{
            background: linear-gradient(90deg, rgba(255,0,107,0.1), rgba(131,56,236,0.05));
            padding: var(--space-md);
            border-bottom: 1px solid rgba(131,56,236,0.2);
        }}
        
        .profile-name {{
            color: var(--terminal-green);
            font-size: var(--text-lg);
            font-weight: 700;
            margin-bottom: var(--space-xs);
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }}
        
        .profile-id {{
            color: var(--gray-400);
            font-size: var(--text-xs);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .profile-content {{
            display: grid;
            grid-template-columns: 1fr;
            gap: var(--space-md);
            padding: var(--space-md);
        }}
        
        @media (min-width: 768px) {{
            .profile-content {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        
        .profile-section {{
            background: rgba(131,56,236,0.02);
            border: 1px solid rgba(131,56,236,0.1);
            border-radius: 2px;
            padding: var(--space-sm);
            transition: all 0.3s ease;
        }}
        
        .profile-section:hover {{
            border-color: rgba(255,0,107,0.2);
            background: rgba(255,0,107,0.03);
            box-shadow: 
                0 0 15px rgba(255,0,107,0.08),
                0 0 8px rgba(131,56,236,0.05);
            transform: translateY(-1px);
        }}
        
        .section-title {{
            color: var(--miami-pink);
            font-size: var(--text-sm);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: var(--space-sm);
            text-shadow: 0 0 8px rgba(255, 0, 107, 0.5);
        }}
        
        .field-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-xs) 0;
            border-bottom: 1px solid rgba(131,56,236,0.05);
            font-size: var(--text-sm);
            transition: all 0.3s ease;
        }}
        
        .field-row:hover {{
            background: rgba(255,0,107,0.02);
            padding-left: var(--space-xs);
            padding-right: var(--space-xs);
            margin: 0 calc(-1 * var(--space-xs));
            border-radius: 2px;
        }}
        
        .field-row:last-child {{
            border-bottom: none;
        }}
        
        .field-label {{
            color: var(--gray-400);
            min-width: 120px;
        }}
        
        .field-value {{
            color: var(--terminal-green);
            font-weight: 400;
        }}
        
        .field-input {{
            background: rgba(255,0,107,0.05);
            border: 1px solid rgba(255,0,107,0.2);
            border-radius: 2px;
            padding: 2px var(--space-xs);
            color: var(--terminal-green);
            font-family: inherit;
            font-size: var(--text-xs);
            min-width: 100px;
            transition: all 0.3s ease;
        }}
        
        .field-input:focus {{
            outline: none;
            border-color: var(--terminal-green);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        }}
        
        .field-input:hover {{
            border-color: rgba(255,0,107,0.4);
            box-shadow: 0 0 8px rgba(255, 0, 107, 0.1);
        }}
        
        .metric-value {{
            color: var(--cyber-blue);
            font-weight: 700;
            text-shadow: 0 0 8px rgba(58, 134, 255, 0.5);
        }}
        
        .placeholder-metric {{
            text-decoration: line-through;
            opacity: 0.5;
            color: var(--gray-600) !important;
        }}
        
        .member-list {{
            background: rgba(131,56,236,0.05);
            border: 1px solid rgba(131,56,236,0.1);
            border-radius: 2px;
            padding: var(--space-sm);
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .member-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-xs);
            margin-bottom: var(--space-xs);
            background: rgba(255,0,107,0.02);
            border-radius: 2px;
            transition: all 0.3s ease;
        }}
        
        .member-item:hover {{
            background: rgba(255,0,107,0.08);
            transform: translateX(2px);
        }}
        
        .member-item:last-child {{
            margin-bottom: 0;
        }}
        
        .member-name {{
            color: var(--terminal-green);
            font-size: var(--text-xs);
        }}
        
        .member-role {{
            color: var(--gray-400);
            font-size: var(--text-xs);
            text-transform: uppercase;
        }}
        
        .nurture-log {{
            background: rgba(131,56,236,0.05);
            border-left: 3px solid var(--vapor-purple);
            padding: var(--space-xs);
            margin-bottom: var(--space-xs);
            font-size: var(--text-xs);
            transition: all 0.3s ease;
        }}
        
        .nurture-log:hover {{
            background: rgba(131,56,236,0.08);
            border-left-color: var(--miami-pink);
            box-shadow: 0 0 10px rgba(131,56,236,0.1);
            transform: translateX(2px);
        }}
        
        .nurture-log:last-child {{
            margin-bottom: 0;
        }}
        
        .log-date {{
            color: var(--gray-400);
            font-size: var(--text-xs);
        }}
        
        .log-content {{
            color: var(--terminal-green);
            margin-top: 2px;
        }}
        
        .remove-btn {{
            background: rgba(255, 0, 107, 0.2);
            border: 1px solid var(--miami-pink);
            color: var(--miami-pink);
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-family: inherit;
            font-size: var(--text-xs);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .remove-btn:hover {{
            background: rgba(255, 0, 107, 0.4);
            box-shadow: 0 0 10px rgba(255, 0, 107, 0.3);
        }}
        
        .add-member-row {{
            display: flex;
            gap: var(--space-xs);
            margin-top: var(--space-sm);
            align-items: center;
        }}
        
        .add-input {{
            flex: 1;
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 2px;
            padding: var(--space-xs);
            color: var(--terminal-green);
            font-family: inherit;
            font-size: var(--text-xs);
        }}
        
        .add-btn {{
            background: linear-gradient(135deg, var(--terminal-green), var(--cyber-blue));
            border: none;
            color: var(--deep-black);
            padding: var(--space-xs);
            border-radius: 2px;
            font-family: inherit;
            font-size: var(--text-xs);
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .add-btn:hover {{
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
            transform: translateY(-1px);
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
            margin-top: var(--space-sm);
        }}
        
        .save-btn:hover {{
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            transform: translateY(-1px);
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
    </style>
</head>
<body>
    <div class="frame">
        <div class="dashboard">
            <div class="header">
                <div class="title">Admin Control</div>
            </div>
            
            <div class="tab-nav">
                <button class="tab active" onclick="showTab('users')">Users</button>
                <button class="tab" onclick="showTab('pods')">Pods</button>
            </div>
            
            <!-- USERS TAB -->
            <div id="users" class="tab-panel active">
                <div class="search-section">
                    <div class="search-header">Find Users</div>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-sm); margin-bottom: var(--space-sm);">
                        <input 
                            type="text" 
                            class="search-bar" 
                            placeholder="Search by name, email, or ID..."
                            oninput="searchUsers(this.value)"
                            onkeypress="if(event.key==='Enter') loadUser(this.value)"
                        >
                        <select id="userDropdown" class="search-bar" onchange="loadUserById(this.value)" style="appearance: none;">
                            <option value="">Select User...</option>
                            <!-- Real users will be populated by JavaScript -->
                        </select>
                    </div>
                    <div style="font-size: var(--text-xs); color: var(--gray-400);">
                        💡 Use search box or dropdown to find users
                    </div>
                </div>
                
                <div id="userProfile" class="profile">
                    <div class="profile-header">
                        <div class="profile-name" id="userName">Sarah Chen</div>
                        <div class="profile-id">USER ID: USR_2024_1247</div>
                    </div>
                    
                    <div class="profile-content">
                        <div class="profile-section">
                            <div class="section-title">Account Information</div>
                            <div class="field-row">
                                <span class="field-label">Email</span>
                                <input type="email" class="field-input" value="sarah.chen@email.com">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Status</span>
                                <select class="field-input">
                                    <option value="paid" selected>Paid</option>
                                    <option value="free">Free</option>
                                    <option value="suspended">Suspended</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Pod Assignment</span>
                                <select class="field-input">
                                    <option value="">No Pod</option>
                                    <option value="pod_alpha" selected>Pod Alpha</option>
                                    <option value="pod_beta">Pod Beta</option>
                                    <option value="pod_gamma">Pod Gamma</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Join Date</span>
                                <span class="field-value">2024-08-15</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Last Login</span>
                                <span class="field-value">2024-08-22 09:34</span>
                            </div>
                            <button class="save-btn" onclick="saveUserChanges()">Save Changes</button>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Performance Metrics</div>
                            <div class="field-row">
                                <span class="field-label">~~Call Attendance~~</span>
                                <span class="field-value metric-value placeholder-metric">~~87.5% (14/16)~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Commitments Made</span>
                                <span class="field-value metric-value">12</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Commitments Kept</span>
                                <span class="field-value metric-value">12 (100%)</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Streak (Current)</span>
                                <span class="field-value metric-value">1 day</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Total Revenue~~</span>
                                <span class="field-value metric-value placeholder-metric">~~$297~~</span>
                            </div>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Recent Nurture Communications</div>
                            <div class="nurture-log">
                                <div class="log-date">2024-08-22 08:00</div>
                                <div class="log-content">Daily commitment reminder sent</div>
                            </div>
                            <div class="nurture-log">
                                <div class="log-date">2024-08-21 18:30</div>
                                <div class="log-content">Streak milestone celebration (7 days)</div>
                            </div>
                            <div class="nurture-log">
                                <div class="log-date">2024-08-20 20:00</div>
                                <div class="log-content">Weekly pod summary delivered</div>
                            </div>
                            <div class="nurture-log">
                                <div class="log-date">2024-08-19 15:45</div>
                                <div class="log-content">Commitment failure recovery sequence</div>
                            </div>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Administrative Notes</div>
                            <div class="field-row">
                                <span class="field-label">Payment Method</span>
                                <span class="field-value">Stripe (****4242)</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Referral Source</span>
                                <span class="field-value">Twitter Ad Campaign</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Support Tickets</span>
                                <span class="field-value">2 (Resolved)</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Admin Notes</span>
                                <textarea class="field-input" style="width: 100%; height: 60px; resize: vertical;">High engagement user. Excellent pod participation.</textarea>
                            </div>
                            <button class="save-btn" onclick="updateNotes()">Update Notes</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- PODS TAB -->
            <div id="pods" class="tab-panel">
                <div class="search-section">
                    <div class="search-header">Find Pods</div>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-sm); margin-bottom: var(--space-sm);">
                        <input 
                            type="text" 
                            class="search-bar" 
                            placeholder="Search by pod name or ID..."
                            oninput="searchPods(this.value)"
                            onkeypress="if(event.key==='Enter') loadPod(this.value)"
                        >
                        <select id="podDropdown" class="search-bar" onchange="loadPodById(this.value)" style="appearance: none;">
                            <option value="">Select Pod...</option>
                            <!-- Real pods will be populated by JavaScript -->
                        </select>
                    </div>
                    <div style="font-size: var(--text-xs); color: var(--gray-400);">
                        💡 Use search box or dropdown to find pods
                    </div>
                </div>
                
                <div id="podProfile" class="profile">
                    <div class="profile-header">
                        <div class="profile-name" id="podName">Pod Alpha</div>
                        <div class="profile-id">POD ID: POD_ALPHA_2024</div>
                    </div>
                    
                    <div class="profile-content">
                        <div class="profile-section">
                            <div class="section-title">Pod Settings</div>
                            <div class="field-row">
                                <span class="field-label">Pod Name</span>
                                <input type="text" class="field-input" value="Pod Alpha">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Status</span>
                                <select class="field-input">
                                    <option value="active" selected>Active</option>
                                    <option value="inactive">Inactive</option>
                                    <option value="full">Full</option>
                                    <option value="archived">Archived</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Max Members</span>
                                <input type="number" class="field-input" value="6" min="2" max="12">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Created Date</span>
                                <span class="field-value">2024-07-15</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Facilitator</span>
                                <select class="field-input">
                                    <option value="">Select Facilitator</option>
                                    <option value="alex_coach" selected>Alex Thompson</option>
                                    <option value="maria_coach">Maria Rodriguez</option>
                                    <option value="david_coach">David Kim</option>
                                </select>
                            </div>
                            <button class="save-btn" onclick="savePodSettings()">Save Settings</button>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Schedule & Meeting</div>
                            <div class="field-row">
                                <span class="field-label">Meeting Day</span>
                                <select class="field-input">
                                    <option value="monday">Monday</option>
                                    <option value="tuesday">Tuesday</option>
                                    <option value="wednesday" selected>Wednesday</option>
                                    <option value="thursday">Thursday</option>
                                    <option value="friday">Friday</option>
                                    <option value="saturday">Saturday</option>
                                    <option value="sunday">Sunday</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Meeting Time</span>
                                <input type="time" class="field-input" value="19:00">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Timezone</span>
                                <select class="field-input">
                                    <option value="PST" selected>PST</option>
                                    <option value="MST">MST</option>
                                    <option value="CST">CST</option>
                                    <option value="EST">EST</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Meeting Link</span>
                                <input type="url" class="field-input" value="https://meet.google.com/abc-defg-hij" style="min-width: 200px;">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Next Meeting</span>
                                <span class="field-value metric-value">Wed, Aug 28 7:00 PM</span>
                            </div>
                            <button class="save-btn" onclick="saveSchedule()">Update Schedule</button>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Pod Members (5/6)</div>
                            <div class="member-list">
                                <div class="member-item">
                                    <div>
                                        <div class="member-name">Sarah Chen</div>
                                        <div class="member-role">Member</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('sarah_chen')">Remove</button>
                                </div>
                                <div class="member-item">
                                    <div>
                                        <div class="member-name">Michael Torres</div>
                                        <div class="member-role">Member</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('michael_torres')">Remove</button>
                                </div>
                                <div class="member-item">
                                    <div>
                                        <div class="member-name">Jennifer Wu</div>
                                        <div class="member-role">Co-Leader</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('jennifer_wu')">Remove</button>
                                </div>
                                <div class="member-item">
                                    <div>
                                        <div class="member-name">David Rodriguez</div>
                                        <div class="member-role">Member</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('david_rodriguez')">Remove</button>
                                </div>
                                <div class="member-item">
                                    <div>
                                        <div class="member-name">Emily Johnson</div>
                                        <div class="member-role">Member</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('emily_johnson')">Remove</button>
                                </div>
                            </div>
                            <div class="add-member-row">
                                <input type="text" class="add-input" placeholder="Enter user email or ID..." id="newMemberInput">
                                <button class="add-btn" onclick="addMember()">Add</button>
                            </div>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Pod Metrics</div>
                            <div class="field-row">
                                <span class="field-label">~~Avg Attendance~~</span>
                                <span class="field-value metric-value placeholder-metric">~~92.3% (4.6/5)~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Total Meetings~~</span>
                                <span class="field-value metric-value placeholder-metric">~~16~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Commitments/Week~~</span>
                                <span class="field-value metric-value placeholder-metric">~~8.5~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Success Rate~~</span>
                                <span class="field-value metric-value placeholder-metric">~~84.7%~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Engagement Score~~</span>
                                <span class="field-value metric-value placeholder-metric">~~8.9/10~~</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/retro/superadmin" class="nav-link">SuperAdmin</a>
                <a href="/retro/business" class="nav-link">Business</a>
                <a href="/retro/nurture" class="nav-link">Nurture</a>
                <a href="/docs" class="nav-link">API Docs</a>
            </div>
        </div>
    </div>
    
    <!-- ADMIN_DATA_PLACEHOLDER -->
    
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
        
        // USER FUNCTIONS
        function searchUsers(query) {{
            if (query.length < 2) return;
            
            // Simulate search suggestions
            console.log('Searching for users:', query);
            
            // Show example users based on search
            if (query.toLowerCase().includes('sarah') || query.toLowerCase().includes('chen')) {{
                loadExampleUser('sarah');
            }} else if (query.toLowerCase().includes('john') || query.toLowerCase().includes('doe')) {{
                loadExampleUser('john');
            }}
        }}
        
        function loadUser(query) {{
            if (query.length < 2) return;
            
            // Show user profile
            document.getElementById('userProfile').classList.add('active');
            
            // Simulate loading user data
            console.log('Loading user profile for:', query);
        }}
        
        function loadExampleUser(type) {{
            document.getElementById('userProfile').classList.add('active');
            
            if (type === 'john') {{
                document.getElementById('userName').textContent = 'John Doe';
                // Update other fields for different user
            }}
        }}
        
        function saveUserChanges() {{
            // Simulate API call to save user changes
            alert('User changes saved successfully!');
            console.log('Saving user account changes...');
        }}
        
        function updateNotes() {{
            // Simulate API call to update admin notes
            alert('Admin notes updated successfully!');
            console.log('Updating admin notes...');
        }}
        
        // POD FUNCTIONS
        function searchPods(query) {{
            if (query.length < 2) return;
            
            // Simulate search suggestions
            console.log('Searching for pods:', query);
            
            // Show example pods based on search
            if (query.toLowerCase().includes('alpha')) {{
                loadExamplePod('alpha');
            }} else if (query.toLowerCase().includes('beta')) {{
                loadExamplePod('beta');
            }}
        }}
        
        function loadPod(query) {{
            if (query.length < 2) return;
            
            // Show pod profile
            document.getElementById('podProfile').classList.add('active');
            
            // Simulate loading pod data
            console.log('Loading pod profile for:', query);
        }}
        
        function loadExamplePod(type) {{
            document.getElementById('podProfile').classList.add('active');
            
            if (type === 'beta') {{
                document.getElementById('podName').textContent = 'Pod Beta';
                // Update other fields for different pod
            }}
        }}
        
        function savePodSettings() {{
            // Simulate API call to save pod settings
            alert('Pod settings saved successfully!');
            console.log('Saving pod settings...');
        }}
        
        function saveSchedule() {{
            // Simulate API call to save schedule
            alert('Schedule updated successfully!');
            console.log('Updating pod schedule...');
        }}
        
        function removeMember(memberId) {{
            // Simulate API call to remove member
            if (confirm('Remove this member from the pod?')) {{
                alert('Member removed successfully!');
                console.log('Removing member:', memberId);
                // Remove the member item from DOM
                event.target.closest('.member-item').remove();
            }}
        }}
        
        function addMember() {{
            const input = document.getElementById('newMemberInput');
            const memberInfo = input.value.trim();
            
            if (!memberInfo) {{
                alert('Please enter a user email or ID');
                return;
            }}
            
            // Simulate API call to add member
            alert('Member added successfully!');
            console.log('Adding member:', memberInfo);
            
            // Clear input
            input.value = '';
            
            // In real implementation, would update the member list
        }}
        
        // DROPDOWN HANDLERS
        function loadUserById(userId) {{
            if (!userId) return;
            
            // Show user profile
            document.getElementById('userProfile').classList.add('active');
            
            // Update user profile based on selection
            const userNames = {{
                '865415132': 'Thomas',
                'user_2': 'Sarah Chen', 
                'user_3': 'Mike Rodriguez',
                'user_4': 'Emma Watson',
                'user_5': 'David Kim'
            }};
            
            if (userNames[userId]) {{
                document.getElementById('userName').textContent = userNames[userId];
                console.log('Loading user from dropdown:', userNames[userId]);
            }}
        }}
        
        function loadPodById(podId) {{
            if (!podId) return;
            
            // Show pod profile
            document.getElementById('podProfile').classList.add('active');
            
            // Update pod profile based on selection
            const podNames = {{
                '11111111-1111-1111-1111-111111111111': 'Test Pod Alpha',
                '22222222-2222-2222-2222-222222222222': 'Healer Business DEV',
                '0135a55e-bb6b-447e-8446-5d80567436b5': 'Morning Momentum',
                '43679170-a8a5-44ab-a770-31ef9fbb08f9': 'Evening Excellence',
                '8c7375d5-0316-44ac-b5b3-2697e1bfb7b0': 'Fitness Focus Pod',
                '96ba5703-297f-4409-9fb5-21f0c434be3f': 'Creative Collective'
            }};
            
            if (podNames[podId]) {{
                document.getElementById('podName').textContent = podNames[podId];
                console.log('Loading pod from dropdown:', podNames[podId]);
            }}
        }}
        
        // POPULATE REAL DATA DROPDOWNS
        function populateDropdowns() {{
            console.log('🔧 populateDropdowns() called');
            console.log('📊 window.realUsers:', window.realUsers ? window.realUsers.length : 'undefined');
            console.log('🏠 window.realPods:', window.realPods ? window.realPods.length : 'undefined');
            
            // Populate users dropdown
            const userDropdown = document.getElementById('userDropdown');
            console.log('🔧 userDropdown element:', userDropdown);
            
            if (window.realUsers && userDropdown) {{
                userDropdown.innerHTML = '<option value="">Select User...</option>';
                
                window.realUsers.forEach(user => {{
                    const option = document.createElement('option');
                    option.value = user.telegram_user_id;
                    option.textContent = `${{user.name}} (TG: ${{user.telegram_user_id}})`;
                    userDropdown.appendChild(option);
                }});
                
                console.log('✅ Populated users dropdown with', window.realUsers.length, 'real users');
            }} else {{
                console.log('❌ Could not populate users dropdown - missing data or element');
            }}
            
            // Populate pods dropdown  
            const podDropdown = document.getElementById('podDropdown');
            console.log('🔧 podDropdown element:', podDropdown);
            
            if (window.realPods && podDropdown) {{
                podDropdown.innerHTML = '<option value="">Select Pod...</option>';
                
                window.realPods.forEach(pod => {{
                    const option = document.createElement('option');
                    option.value = pod.id;
                    option.textContent = `${{pod.name}} (${{pod.members || '0'}}/6)`;
                    podDropdown.appendChild(option);
                }});
                
                console.log('✅ Populated pods dropdown with', window.realPods.length, 'real pods');
            }} else {{
                console.log('❌ Could not populate pods dropdown - missing data or element');
            }}
        }}
        
        // Auto-show example profiles on load
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🔧 DOM loaded, attempting to populate dropdowns...');
            setTimeout(() => {{
                populateDropdowns();
                document.getElementById('userProfile').classList.add('active');
                document.getElementById('podProfile').classList.add('active');
            }}, 100);
        }});
        
        // Fallback for late script loading
        if (document.readyState === 'complete' || document.readyState === 'interactive') {{
            console.log('🔧 DOM already ready, populating dropdowns immediately...');
            setTimeout(populateDropdowns, 100);
        }}
    </script>
</body>
</html>
"""
    return html_content