def get_pod_admin_html():
    """Generate evolved pod admin dashboard focused on pod management and member coordination"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>POD ADMIN • THE PROGRESS METHOD</title>
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
        
        /* Pod Profile Section */
        .pod-profile {{
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
        
        .pod-profile.active {{
            display: block;
        }}
        
        .pod-profile:hover {{
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
        
        .status-active {{
            background: rgba(0, 255, 136, 0.2);
            color: var(--terminal-green);
            border: 1px solid var(--terminal-green);
        }}
        
        .status-inactive {{
            background: rgba(255, 0, 107, 0.2);
            color: var(--miami-pink);
            border: 1px solid var(--miami-pink);
        }}
        
        .status-full {{
            background: rgba(255, 190, 11, 0.2);
            color: var(--sunset-yellow);
            border: 1px solid var(--sunset-yellow);
        }}
        
        .metric-value {{
            color: var(--cyber-blue);
            font-weight: 700;
            text-shadow: 0 0 8px rgba(58, 134, 255, 0.5);
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
                <div class="title">Pod Admin</div>
                <div class="subtitle">Member Management • The Progress Method</div>
            </div>
            
            <div class="search-section">
                <div class="search-header">Search Pods</div>
                <input 
                    type="text" 
                    class="search-bar" 
                    placeholder="Enter pod name or ID..."
                    oninput="searchPods(this.value)"
                    onkeypress="if(event.key==='Enter') loadPod(this.value)"
                >
            </div>
            
            <div id="podProfile" class="pod-profile">
                <div class="profile-header">
                    <div class="profile-name" id="profileName">Pod Alpha</div>
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
                            <span class="field-label">Avg Attendance</span>
                            <span class="field-value metric-value">92.3% (4.6/5)</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Total Meetings</span>
                            <span class="field-value metric-value">16</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Commitments/Week</span>
                            <span class="field-value metric-value">8.5</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Success Rate</span>
                            <span class="field-value metric-value">84.7%</span>
                        </div>
                        <div class="field-row">
                            <span class="field-label">Engagement Score</span>
                            <span class="field-value metric-value">8.9/10</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/retro/superadmin" class="nav-link">SuperAdmin</a>
                <a href="/retro/admin" class="nav-link">User Admin</a>
                <a href="/retro/business" class="nav-link">Business</a>
                <a href="/retro/nurture" class="nav-link">Nurture</a>
                <a href="/docs" class="nav-link">API Docs</a>
            </div>
        </div>
    </div>
    
    <script>
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
                document.getElementById('profileName').textContent = 'Pod Beta';
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
        
        // Auto-show example pod on load
        setTimeout(() => {{
            document.getElementById('podProfile').classList.add('active');
        }}, 500);
    </script>
</body>
</html>
"""
    return html_content