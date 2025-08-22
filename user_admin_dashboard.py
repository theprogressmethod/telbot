def get_user_admin_html():
    """Generate evolved admin dashboard focused on user management and database editing"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>USER ADMIN • THE PROGRESS METHOD</title>
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
            color: var(--terminal-green);
            font-size: var(--text-xl);
            font-weight: 200;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            margin-bottom: var(--space-xs);
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        }}
        
        .subtitle {{
            color: var(--gray-400);
            font-size: var(--text-sm);
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.2em;
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
        
        /* User Profile Section */
        .user-profile {{
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
        
        .user-profile.active {{
            display: block;
        }}
        
        .user-profile:hover {{
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
        
        .status-badge {{
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-size: var(--text-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status-paid {{
            background: rgba(0, 255, 136, 0.2);
            color: var(--terminal-green);
            border: 1px solid var(--terminal-green);
        }}
        
        .status-free {{
            background: rgba(255, 0, 107, 0.2);
            color: var(--miami-pink);
            border: 1px solid var(--miami-pink);
        }}
        
        .metric-value {{
            color: var(--cyber-blue);
            font-weight: 700;
            text-shadow: 0 0 8px rgba(58, 134, 255, 0.5);
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
                <div class="title">User Admin</div>
                <div class="subtitle">Database Access • The Progress Method</div>
            </div>
            
            <div class="search-section">
                <div class="search-header">Search Users</div>
                <input 
                    type="text" 
                    class="search-bar" 
                    placeholder="Enter user name, email, or ID..."
                    oninput="searchUsers(this.value)"
                    onkeypress="if(event.key==='Enter') loadUser(this.value)"
                >
            </div>
            
            <div id="userProfile" class="user-profile">
                <div class="profile-header">
                    <div class="profile-name" id="profileName">Sarah Chen</div>
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
                            <span class="field-label">Call Attendance</span>
                            <span class="field-value metric-value">87.5% (14/16)</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Commitments Made</span>
                            <span class="field-value metric-value">23</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Commitments Kept</span>
                            <span class="field-value metric-value">19 (82.6%)</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Streak (Current)</span>
                            <span class="field-value metric-value">7 days</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Total Revenue</span>
                            <span class="field-value metric-value">$297</span>
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
            
            <div class="nav-links">
                <a href="/retro/superadmin" class="nav-link">SuperAdmin</a>
                <a href="/retro/pods" class="nav-link">Pod Admin</a>
                <a href="/retro/business" class="nav-link">Business</a>
                <a href="/retro/nurture" class="nav-link">Nurture</a>
                <a href="/docs" class="nav-link">API Docs</a>
            </div>
        </div>
    </div>
    
    <script>
        function searchUsers(query) {{
            if (query.length < 2) return;
            
            // Simulate search suggestions
            console.log('Searching for:', query);
            
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
                document.getElementById('profileName').textContent = 'John Doe';
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
        
        // Auto-show example user on load
        setTimeout(() => {{
            document.getElementById('userProfile').classList.add('active');
        }}, 500);
    </script>
</body>
</html>
"""
    return html_content