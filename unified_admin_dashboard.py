def get_unified_admin_html(admin_data=None):
    """Generate unified admin dashboard with Users and Pods tabs"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ADMIN CONTROL • THE PROGRESS METHOD v3-loadRealData</title>
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
        
        .roles-list {{
            background: rgba(131,56,236,0.05);
            border: 1px solid rgba(131,56,236,0.1);
            border-radius: 2px;
            padding: var(--space-sm);
            max-height: 150px;
            overflow-y: auto;
            margin-bottom: var(--space-sm);
        }}
        
        .role-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-xs);
            margin-bottom: var(--space-xs);
            background: rgba(255,0,107,0.02);
            border: 1px solid rgba(255,0,107,0.1);
            border-radius: 2px;
        }}
        
        .role-item:last-child {{
            margin-bottom: 0;
        }}
        
        .role-name {{
            color: var(--terminal-green);
            font-weight: 600;
            text-transform: uppercase;
            font-size: var(--text-xs);
        }}
        
        .role-management {{
            display: flex;
            gap: var(--space-xs);
            align-items: center;
        }}
        
        .role-select {{
            flex: 1;
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 2px;
            padding: var(--space-xs);
            color: var(--terminal-green);
            font-family: inherit;
            font-size: var(--text-xs);
        }}
        
        .remove-role-btn {{
            background: linear-gradient(135deg, var(--neon-pink), #ff0040);
            border: none;
            color: white;
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-family: inherit;
            font-size: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }}
        
        .remove-role-btn:hover {{
            box-shadow: 0 0 10px rgba(255, 0, 107, 0.5);
            transform: translateY(-1px);
        }}
        
        .commitment-item {{
            display: flex;
            flex-direction: column;
            padding: var(--space-sm);
            margin-bottom: var(--space-sm);
            background: linear-gradient(135deg, rgba(58,134,255,0.02), rgba(131,56,236,0.02));
            border: 1px solid rgba(58,134,255,0.1);
            border-radius: 2px;
            transition: all 0.3s ease;
        }}
        
        .commitment-item:hover {{
            border-color: rgba(58,134,255,0.3);
            background: linear-gradient(135deg, rgba(58,134,255,0.05), rgba(131,56,236,0.03));
        }}
        
        .commitment-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--space-xs);
        }}
        
        .commitment-text {{
            flex: 1;
            color: var(--terminal-green);
            font-size: var(--text-sm);
            line-height: 1.4;
        }}
        
        .commitment-status-badge {{
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-size: var(--text-xs);
            text-transform: uppercase;
            font-weight: 700;
            margin-left: var(--space-sm);
        }}
        
        .status-active {{
            background: rgba(255, 190, 11, 0.2);
            color: var(--sunset-yellow);
            border: 1px solid var(--sunset-yellow);
        }}
        
        .status-completed {{
            background: rgba(0, 255, 136, 0.2);
            color: var(--terminal-green);
            border: 1px solid var(--terminal-green);
        }}
        
        .status-failed {{
            background: rgba(255, 0, 107, 0.2);
            color: var(--miami-pink);
            border: 1px solid var(--miami-pink);
        }}
        
        .commitment-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: var(--text-xs);
            color: var(--gray-400);
            margin-top: var(--space-xs);
        }}
        
        .commitment-date {{
            font-size: var(--text-xs);
            color: var(--gray-400);
        }}
        
        .commitment-actions {{
            display: flex;
            gap: var(--space-xs);
        }}
        
        .edit-commitment-btn, .delete-commitment-btn {{
            background: rgba(58, 134, 255, 0.2);
            border: 1px solid var(--cyber-blue);
            color: var(--cyber-blue);
            padding: 2px var(--space-xs);
            border-radius: 2px;
            font-family: inherit;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .delete-commitment-btn {{
            background: rgba(255, 0, 107, 0.2);
            border-color: var(--miami-pink);
            color: var(--miami-pink);
        }}
        
        .edit-commitment-btn:hover {{
            background: rgba(58, 134, 255, 0.4);
            box-shadow: 0 0 10px rgba(58, 134, 255, 0.3);
        }}
        
        .delete-commitment-btn:hover {{
            background: rgba(255, 0, 107, 0.4);
            box-shadow: 0 0 10px rgba(255, 0, 107, 0.3);
        }}
        
        .commitment-changelog {{
            margin-top: var(--space-xs);
            padding-top: var(--space-xs);
            border-top: 1px solid rgba(131,56,236,0.1);
        }}
        
        .changelog-entry {{
            font-size: var(--text-xs);
            color: var(--gray-600);
            margin-bottom: 2px;
        }}
        
        .changelog-admin {{
            color: var(--vapor-purple);
            font-weight: 600;
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
                    <div class="search-header" style="text-decoration: line-through; opacity: 0.6; color: var(--gray-600);">~~Find Users~~ [NOT BUILT - Use Dropdown]</div>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-sm); margin-bottom: var(--space-sm);">
                        <input 
                            type="text" 
                            class="search-bar" 
                            placeholder="~~Search by name, email, or ID...~~"
                            disabled
                            style="text-decoration: line-through; opacity: 0.3; background: rgba(102, 102, 136, 0.05); cursor: not-allowed;"
                        >
                        <select id="userDropdown" class="search-bar" onchange="loadUserById(this.value)" style="appearance: none;">
                            <option value="">Select User...</option>
                            <!-- Real users will be populated by JavaScript -->
                        </select>
                    </div>
                    <div style="font-size: var(--text-xs); color: var(--gray-400);">
                        💡 Search not built yet - use dropdown to find users
                    </div>
                </div>
                
                <!-- Empty state for when no user is selected -->
                <div id="userEmptyState" class="profile" style="display: block;">
                    <div class="profile-content">
                        <div style="text-align: center; padding: var(--space-xl); color: var(--gray-400);">
                            <div style="font-size: var(--text-lg); margin-bottom: var(--space-md);">👤 No User Selected</div>
                            <div style="font-size: var(--text-sm);">Select a user from the dropdown above to view and edit their information.</div>
                        </div>
                    </div>
                </div>
                
                <div id="userProfile" class="profile" style="display: none;">
                    <div class="profile-header">
                        <div class="profile-name" id="userName">-</div>
                        <div class="profile-id">USER ID: -</div>
                    </div>
                    
                    <div class="profile-content">
                        <div class="profile-section">
                            <div class="section-title">Account Information</div>
                            <div class="field-row">
                                <span class="field-label">First Name</span>
                                <input type="text" id="userFirstName" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Last Name</span>
                                <input type="text" id="userLastName" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Username</span>
                                <input type="text" id="userUsername" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Email</span>
                                <input type="email" id="userEmail" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Status</span>
                                <select class="field-input">
                                    <option value="" selected>-</option>
                                    <option value="paid">Paid</option>
                                    <option value="free">Free</option>
                                    <option value="suspended">Suspended</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Pod Assignment</span>
                                <select class="field-input">
                                    <option value="" selected>No Pod</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Join Date</span>
                                <span class="field-value">-</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Last Login</span>
                                <span class="field-value">-</span>
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
                                <span class="field-label">~~Streak (Current)~~</span>
                                <span class="field-value metric-value placeholder-metric">~~1 day~~</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">~~Total Revenue~~</span>
                                <span class="field-value metric-value placeholder-metric">~~$297~~</span>
                            </div>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">User Roles</div>
                            <div class="roles-list" id="userRoles">
                                <!-- Roles will be populated by JavaScript -->
                            </div>
                            <div class="role-management">
                                <select class="role-select" id="roleSelect">
                                    <option value="">Select Role to Add...</option>
                                    <!-- Will be populated by JavaScript -->
                                </select>
                                <button class="add-btn" onclick="addUserRole()">Add Role</button>
                            </div>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Recent Commitments</div>
                            <div class="commitments-list" id="userCommitments">
                                <!-- User commitments will be populated by JavaScript -->
                            </div>
                            <div style="margin-top: var(--space-sm); text-align: center;">
                                <button class="add-btn" onclick="addNewCommitment()" style="font-size: var(--text-xs);">Add New Commitment</button>
                            </div>
                        </div>
                        
                        <div class="profile-section" style="opacity: 0.6;">
                            <div class="section-title" style="text-decoration: line-through; color: var(--gray-600);">~~Recent Nurture Communications~~ [NOT BUILT]</div>
                            <div class="nurture-log" style="text-decoration: line-through; opacity: 0.5;">
                                <div class="log-date" style="text-decoration: line-through;">~~2024-08-22 08:00~~</div>
                                <div class="log-content" style="text-decoration: line-through;">~~Daily commitment reminder sent~~</div>
                            </div>
                            <div class="nurture-log" style="text-decoration: line-through; opacity: 0.5;">
                                <div class="log-date" style="text-decoration: line-through;">~~2024-08-21 18:30~~</div>
                                <div class="log-content" style="text-decoration: line-through;">~~Streak milestone celebration (7 days)~~</div>
                            </div>
                            <div class="nurture-log" style="text-decoration: line-through; opacity: 0.5;">
                                <div class="log-date" style="text-decoration: line-through;">~~2024-08-20 20:00~~</div>
                                <div class="log-content" style="text-decoration: line-through;">~~Weekly pod summary delivered~~</div>
                            </div>
                            <div class="nurture-log" style="text-decoration: line-through; opacity: 0.5;">
                                <div class="log-date" style="text-decoration: line-through;">~~2024-08-19 15:45~~</div>
                                <div class="log-content" style="text-decoration: line-through;">~~Commitment failure recovery sequence~~</div>
                            </div>
                        </div>
                        
                        <div class="profile-section" style="opacity: 0.6;">
                            <div class="section-title" style="text-decoration: line-through; color: var(--gray-600);">~~Administrative Notes~~ [NOT BUILT]</div>
                            <div class="field-row" style="text-decoration: line-through; opacity: 0.5;">
                                <span class="field-label" style="text-decoration: line-through;">~~Payment Method~~</span>
                                <span class="field-value" style="text-decoration: line-through;">~~Stripe (****4242)~~</span>
                            </div>
                            <div class="field-row" style="text-decoration: line-through; opacity: 0.5;">
                                <span class="field-label" style="text-decoration: line-through;">~~Referral Source~~</span>
                                <span class="field-value" style="text-decoration: line-through;">~~Twitter Ad Campaign~~</span>
                            </div>
                            <div class="field-row" style="text-decoration: line-through; opacity: 0.5;">
                                <span class="field-label" style="text-decoration: line-through;">~~Support Tickets~~</span>
                                <span class="field-value" style="text-decoration: line-through;">~~2 (Resolved)~~</span>
                            </div>
                            <div class="field-row" style="text-decoration: line-through; opacity: 0.5;">
                                <span class="field-label" style="text-decoration: line-through;">~~Admin Notes~~</span>
                                <textarea class="field-input" style="width: 100%; height: 60px; resize: vertical; text-decoration: line-through; opacity: 0.5;" disabled>~~High engagement user. Excellent pod participation.~~</textarea>
                            </div>
                            <button class="save-btn" onclick="updateNotes()" style="text-decoration: line-through; opacity: 0.5;" disabled>~~Update Notes~~</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- PODS TAB -->
            <div id="pods" class="tab-panel">
                <div class="search-section">
                    <div class="search-header" style="text-decoration: line-through; opacity: 0.6; color: var(--gray-600);">~~Find Pods~~ [NOT BUILT - Use Dropdown]</div>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-sm); margin-bottom: var(--space-sm);">
                        <input 
                            type="text" 
                            class="search-bar" 
                            placeholder="~~Search by pod name or ID...~~"
                            disabled
                            style="text-decoration: line-through; opacity: 0.3; background: rgba(102, 102, 136, 0.05); cursor: not-allowed;"
                        >
                        <select id="podDropdown" class="search-bar" onchange="loadPodById(this.value)" style="appearance: none;">
                            <option value="">Select Pod...</option>
                            <!-- Real pods will be populated by JavaScript -->
                        </select>
                    </div>
                    <div style="font-size: var(--text-xs); color: var(--gray-400);">
                        💡 Search not built yet - use dropdown to find pods
                    </div>
                </div>
                
                <!-- Empty state for when no pod is selected -->
                <div id="podEmptyState" class="profile" style="display: block;">
                    <div class="profile-content">
                        <div style="text-align: center; padding: var(--space-xl); color: var(--gray-400);">
                            <div style="font-size: var(--text-lg); margin-bottom: var(--space-md);">🏠 No Pod Selected</div>
                            <div style="font-size: var(--text-sm);">Select a pod from the dropdown above to view and edit its settings.</div>
                        </div>
                    </div>
                </div>
                
                <div id="podProfile" class="profile" style="display: none;">
                    <div class="profile-header">
                        <div class="profile-name" id="podName">-</div>
                        <div class="profile-id">POD ID: -</div>
                    </div>
                    
                    <div class="profile-content">
                        <div class="profile-section">
                            <div class="section-title">Pod Settings</div>
                            <div class="field-row">
                                <span class="field-label">Pod Name</span>
                                <input type="text" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Status</span>
                                <select class="field-input">
                                    <option value="" selected>-</option>
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                    <option value="full">Full</option>
                                    <option value="archived">Archived</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Max Members</span>
                                <input type="number" class="field-input" value="" min="2" max="12">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Created Date</span>
                                <span class="field-value">-</span>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Facilitator</span>
                                <select class="field-input">
                                    <option value="" selected>Select Facilitator</option>
                                </select>
                            </div>
                            <button class="save-btn" onclick="savePodSettings()">Save Settings</button>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Schedule & Meeting</div>
                            <div class="field-row">
                                <span class="field-label">Meeting Day</span>
                                <select class="field-input">
                                    <option value="" selected>-</option>
                                    <option value="monday">Monday</option>
                                    <option value="tuesday">Tuesday</option>
                                    <option value="wednesday">Wednesday</option>
                                    <option value="thursday">Thursday</option>
                                    <option value="friday">Friday</option>
                                    <option value="saturday">Saturday</option>
                                    <option value="sunday">Sunday</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Meeting Time</span>
                                <input type="time" class="field-input" value="">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Timezone</span>
                                <select class="field-input">
                                    <option value="" selected>-</option>
                                    <option value="PST">PST</option>
                                    <option value="MST">MST</option>
                                    <option value="CST">CST</option>
                                    <option value="EST">EST</option>
                                </select>
                            </div>
                            <div class="field-row">
                                <span class="field-label">Meeting Link</span>
                                <input type="url" class="field-input" value="" style="min-width: 200px;">
                            </div>
                            <div class="field-row">
                                <span class="field-label">Next Meeting</span>
                                <span class="field-value metric-value">-</span>
                            </div>
                            <button class="save-btn" onclick="saveSchedule()">Update Schedule</button>
                        </div>
                        
                        <div class="profile-section">
                            <div class="section-title">Pod Members (0/0)</div>
                            <div class="member-list" style="text-align: center; color: var(--gray-400); font-size: var(--text-sm); padding: var(--space-md);">
                                No members found
                            </div>
                            <div class="add-member-row">
                                <select class="add-input" id="newMemberSelect">
                                    <option value="">Select User to Add...</option>
                                    <!-- Users will be populated by JavaScript -->
                                </select>
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
            if (!currentUserId) {{
                alert('No user selected');
                return;
            }}
            
            // Get all user account fields
            const firstNameField = document.getElementById('userFirstName');
            const lastNameField = document.getElementById('userLastName');
            const usernameField = document.getElementById('userUsername');
            const emailField = document.getElementById('userEmail');
            const statusSelect = Array.from(document.querySelectorAll('#userProfile select.field-input')).find(select => 
                select.parentElement.textContent.includes('Status')
            );
            const podSelect = Array.from(document.querySelectorAll('#userProfile select.field-input')).find(select => 
                select.parentElement.textContent.includes('Pod Assignment')
            );
            
            // Collect user data
            const userData = {{}};
            if (firstNameField && firstNameField.value.trim()) userData.first_name = firstNameField.value.trim();
            if (lastNameField && lastNameField.value.trim()) userData.last_name = lastNameField.value.trim();
            if (usernameField && usernameField.value.trim()) userData.username = usernameField.value.trim();
            
            // Get current pod assignment for comparison
            let currentPodId = null;
            if (podSelect && window.realPods) {{
                for (const pod of window.realPods) {{
                    if (pod.members && Array.isArray(pod.members) && pod.members.some(member => member.users?.telegram_user_id == currentUserId)) {{
                        currentPodId = pod.id;
                        break;
                    }}
                }}
            }}
            
            console.log('🔄 Saving user account changes for user:', currentUserId, userData);
            
            // Make API call to update user
            fetch(`/api/crud/users/${{currentUserId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(userData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('User changes saved successfully!');
                    console.log('✅ User updated:', data);
                    
                    // Handle status changes (role management)
                    if (statusSelect && statusSelect.value) {{
                        console.log('🔄 Handling status change to:', statusSelect.value);
                        // Status changes are handled through role management
                        // This would require additional API calls to add/remove roles
                    }}
                    
                    // Handle pod assignment changes
                    if (podSelect && podSelect.value !== currentPodId) {{
                        console.log('🔄 Handling pod assignment change from:', currentPodId, 'to:', podSelect.value);
                        
                        // Remove from current pod if assigned
                        if (currentPodId) {{
                            fetch(`/api/crud/pods/${{currentPodId}}/members/${{currentUserId}}`, {{
                                method: 'DELETE'
                            }})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.success) {{
                                    console.log('✅ Removed from old pod:', currentPodId);
                                }} else {{
                                    console.error('❌ Failed to remove from old pod:', data.message);
                                }}
                            }})
                            .catch(error => console.error('❌ Error removing from pod:', error));
                        }}
                        
                        // Add to new pod if selected
                        if (podSelect.value) {{
                            fetch(`/api/crud/pods/${{podSelect.value}}/members/${{currentUserId}}`, {{
                                method: 'POST'
                            }})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.success) {{
                                    console.log('✅ Added to new pod:', podSelect.value);
                                }} else {{
                                    console.error('❌ Failed to add to new pod:', data.message);
                                    alert('Error assigning to pod: ' + (data.message || 'Unknown error'));
                                }}
                            }})
                            .catch(error => {{
                                console.error('❌ Error adding to pod:', error);
                                alert('Network error assigning to pod');
                            }});
                        }}
                    }}
                    
                    // Reload user data to show updated information
                    loadUserById(currentUserId);
                }} else {{
                    alert('Error saving user changes: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error saving user:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error saving user changes');
                console.error('❌ Network error:', error);
            }});
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
            // Get current pod ID
            const podDropdown = document.getElementById('podDropdown');
            const podId = podDropdown ? podDropdown.value : null;
            
            if (!podId) {{
                alert('No pod selected');
                return;
            }}
            
            // Get pod settings fields
            const podNameField = document.querySelector('#podProfile .profile-section:nth-child(1) input[type="text"]');
            const statusSelect = Array.from(document.querySelectorAll('#podProfile select.field-input')).find(select => 
                select.parentElement.textContent.includes('Status')
            );
            
            // Collect pod data
            const podData = {{}};
            if (podNameField) podData.name = podNameField.value;
            if (statusSelect) podData.status = statusSelect.value;
            
            console.log('🔄 Saving pod settings for pod:', podId, podData);
            
            // Make API call to update pod
            fetch(`/api/crud/pods/${{podId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(podData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Pod settings saved successfully!');
                    console.log('✅ Pod updated:', data);
                    
                    // Reload pod data to show updated information
                    loadPodById(podId);
                }} else {{
                    alert('Error saving pod settings: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error saving pod:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error saving pod settings');
                console.error('❌ Network error:', error);
            }});
        }}
        
        function saveSchedule() {{
            // Get current pod ID
            const podDropdown = document.getElementById('podDropdown');
            const podId = podDropdown ? podDropdown.value : null;
            
            if (!podId) {{
                alert('No pod selected');
                return;
            }}
            
            // Get all meeting schedule fields as a group
            const meetingDaySelect = Array.from(document.querySelectorAll('#podProfile select.field-input')).find(select => 
                select.parentElement.textContent.includes('Meeting Day')
            );
            const meetingTimeInput = document.querySelector('#podProfile input[type="time"]');
            const timezoneSelect = Array.from(document.querySelectorAll('#podProfile select.field-input')).find(select => 
                select.parentElement.textContent.includes('Timezone')
            );
            
            if (!meetingDaySelect || !meetingTimeInput || !timezoneSelect) {{
                alert('Error: Could not find meeting schedule fields');
                return;
            }}
            
            // Collect all schedule data as a group
            const scheduleData = {{}};
            
            // Convert meeting day name to number (0=Monday, 6=Sunday)
            if (meetingDaySelect.value) {{
                const dayNames = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
                const dayIndex = dayNames.indexOf(meetingDaySelect.value);
                if (dayIndex >= 0) {{
                    scheduleData.day_of_week = dayIndex;
                }}
            }}
            
            // Convert time to database format
            if (meetingTimeInput.value) {{
                scheduleData.time_utc = meetingTimeInput.value + ':00'; // Add seconds
            }}
            
            // Add timezone if provided
            if (timezoneSelect.value) {{
                scheduleData.timezone = timezoneSelect.value;
            }}
            
            console.log('🔄 Updating pod schedule as a group:', scheduleData);
            
            // Make API call to update pod schedule
            fetch(`/api/crud/pods/${{podId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(scheduleData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Schedule updated successfully!\\nAll meeting fields updated as a group.');
                    console.log('✅ Schedule updated:', data);
                    
                    // Log the group change for analytics
                    console.log('📊 Schedule change logged - Day:', scheduleData.meeting_day, 
                              'Time:', scheduleData.meeting_time, 'Timezone:', scheduleData.timezone);
                    
                    // Reload pod data to show updated schedule
                    loadPodById(podId);
                }} else {{
                    alert('Error updating schedule: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error updating schedule:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error updating schedule');
                console.error('❌ Network error:', error);
            }});
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
            const select = document.getElementById('newMemberSelect');
            const userId = select.value;
            
            if (!userId) {{
                alert('Please select a user to add');
                return;
            }}
            
            // Get current pod ID from the dropdown or URL
            const podDropdown = document.getElementById('podDropdown');
            const podId = podDropdown ? podDropdown.value : null;
            
            if (!podId) {{
                alert('No pod selected');
                return;
            }}
            
            console.log('🔄 Adding user', userId, 'to pod', podId);
            
            // Make API call to add member
            fetch(`/api/crud/pods/${{podId}}/members/${{userId}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Member added successfully!');
                    console.log('✅ Member added:', data);
                    
                    // Clear selection
                    select.value = '';
                    
                    // Reload the pod data to show updated member list
                    loadPodById(podId);
                }} else {{
                    alert('Error adding member: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error adding member:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error adding member');
                console.error('❌ Network error:', error);
            }});
        }}
        
        // DROPDOWN HANDLERS
        function loadUserById(userId) {{
            if (!userId) return;
            
            console.log('🔄 Loading user data for ID:', userId);
            
            // Set current user ID for role management
            currentUserId = userId;
            
            // Hide empty state and show user profile with loading state
            document.getElementById('userEmptyState').style.display = 'none';
            document.getElementById('userProfile').style.display = 'block';
            document.getElementById('userName').textContent = 'Loading...';
            
            // Fetch real user data from API
            fetch(`/api/crud/users/${{userId}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const user = data.data;
                        console.log('✅ User data loaded:', user);
                        
                        // Update user profile with real data - handle cleaner names
                        let displayName = user.first_name || 'Unknown User';
                        
                        // Clean up telegram format names like "123456@telegram"
                        if (displayName.includes('@telegram')) {{
                            displayName = `User ${{user.telegram_user_id || 'Unknown'}}`;
                        }}
                        
                        // Use username as fallback if available and cleaner
                        if (displayName === 'Unknown User' && user.username && !user.username.includes('@telegram')) {{
                            displayName = user.username;
                        }}
                        
                        document.getElementById('userName').textContent = displayName;
                        
                        // Update user fields with real data
                        const firstNameField = document.getElementById('userFirstName');
                        const lastNameField = document.getElementById('userLastName');
                        const usernameField = document.getElementById('userUsername');
                        const emailField = document.getElementById('userEmail');
                        
                        if (firstNameField) firstNameField.value = user.first_name || '';
                        if (lastNameField) lastNameField.value = user.last_name || '';
                        if (usernameField) usernameField.value = user.username || '';
                        if (emailField) emailField.value = user.email || '';
                        
                        // Update status dropdown with real data
                        const statusSelect = Array.from(document.querySelectorAll('#userProfile select.field-input')).find(select => 
                            select.parentElement.textContent.includes('Status')
                        );
                        if (statusSelect) {{
                            // Determine user status from roles
                            const userRoles = user.roles || [];
                            const isPaid = userRoles.some(role => role.role === 'paid' || role.role === 'premium');
                            statusSelect.value = isPaid ? 'paid' : 'free';
                            console.log('✅ Updated status to:', statusSelect.value);
                        }}
                        
                        // Update pod assignment dropdown with real data
                        const podSelect = Array.from(document.querySelectorAll('#userProfile select.field-input')).find(select => 
                            select.parentElement.textContent.includes('Pod Assignment')
                        );
                        if (podSelect && window.realPods) {{
                            // Find user's actual pod from pod memberships
                            let userPodId = null;
                            
                            // Check all pods to see which one the user is in
                            for (const pod of window.realPods) {{
                                if (pod.members && Array.isArray(pod.members) && pod.members.some(member => member.users?.telegram_user_id == user.telegram_user_id)) {{
                                    userPodId = pod.id;
                                    break;
                                }}
                            }}
                            
                            // Clear and repopulate pod options
                            podSelect.innerHTML = '<option value="">No Pod</option>';
                            window.realPods.forEach(pod => {{
                                const option = document.createElement('option');
                                option.value = pod.id;
                                option.textContent = pod.name;
                                if (pod.id === userPodId) option.selected = true;
                                podSelect.appendChild(option);
                            }});
                            
                            console.log('✅ Updated pod assignment to:', userPodId || 'No Pod');
                        }}
                        
                        // Update join date
                        const joinDateField = document.querySelector('#userProfile .field-row:nth-child(4) .field-value');
                        if (joinDateField) joinDateField.textContent = user.created_at ? user.created_at.split('T')[0] : 'Unknown';
                        
                        // Update telegram ID in profile header
                        const profileId = document.querySelector('#userProfile .profile-id');
                        if (profileId) profileId.textContent = `TELEGRAM ID: ${{user.telegram_user_id || 'N/A'}}`;
                        
                        // Update user roles
                        displayUserRoles(user.roles || []);
                        
                        // Fetch user commitments for metrics
                        return fetch(`/api/crud/commitments/user/${{userId}}`);
                    }} else {{
                        throw new Error(data.message || 'User not found');
                    }}
                }})
                .then(response => response.json())
                .then(commitmentData => {{
                    if (commitmentData.success) {{
                        const commitments = commitmentData.data;
                        const completedCommitments = commitments.filter(c => c.status === 'completed').length;
                        
                        console.log('✅ User commitments loaded:', commitments.length);
                        
                        // Update commitment metrics
                        const commitmentsMadeField = document.querySelector('#userProfile .field-row:nth-child(2) .metric-value');
                        if (commitmentsMadeField) commitmentsMadeField.textContent = commitments.length;
                        
                        const commitmentsKeptField = document.querySelector('#userProfile .field-row:nth-child(3) .metric-value');
                        if (commitmentsKeptField) {{
                            const rate = commitments.length > 0 ? Math.round((completedCommitments / commitments.length) * 100) : 0;
                            commitmentsKeptField.textContent = `${{completedCommitments}} (${{rate}}%)`;
                        }}
                        
                        // Display user commitments
                        displayUserCommitments(commitments);
                    }}
                }})
                .catch(error => {{
                    console.error('❌ Error loading user data:', error);
                    document.getElementById('userName').textContent = 'Error Loading User';
                    
                    // Show error message
                    const profileId = document.querySelector('#userProfile .profile-id');
                    if (profileId) profileId.textContent = `ERROR: ${{error.message}}`;
                }});
        }}
        
        function loadPodById(podId) {{
            if (!podId) return;
            
            console.log('🔄 Loading pod data for ID:', podId);
            
            // Hide empty state and show pod profile with loading state
            document.getElementById('podEmptyState').style.display = 'none';
            document.getElementById('podProfile').style.display = 'block';
            document.getElementById('podName').textContent = 'Loading...';
            
            // Fetch real pod data from API
            fetch(`/api/crud/pods/${{podId}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const pod = data.data;
                        console.log('✅ Pod data loaded:', pod);
                        
                        // Update pod profile with real data
                        document.getElementById('podName').textContent = pod.name || 'Unknown Pod';
                        
                        // Update pod ID in profile header
                        const profileId = document.querySelector('#podProfile .profile-id');
                        if (profileId) profileId.textContent = `POD ID: ${{podId}}`;
                        
                        // Update pod settings
                        const podNameField = document.querySelector('#podProfile .profile-section:nth-child(1) input[type="text"]');
                        if (podNameField) podNameField.value = pod.name || '';
                        
                        
                        // Update created date - find by label text
                        const createdDateField = Array.from(document.querySelectorAll('#podProfile .field-row')).find(row => 
                            row.textContent.includes('Created Date')
                        )?.querySelector('.field-value');
                        if (createdDateField) createdDateField.textContent = pod.created_at ? pod.created_at.split('T')[0] : 'Unknown';
                        
                        // Update meeting day dropdown
                        const meetingDaySelect = Array.from(document.querySelectorAll('#podProfile select.field-input')).find(select => 
                            select.parentElement.textContent.includes('Meeting Day')
                        );
                        if (meetingDaySelect && pod.day_of_week !== undefined) {{
                            const dayNames = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
                            const dayName = dayNames[pod.day_of_week] || '';
                            meetingDaySelect.value = dayName;
                        }}
                        
                        // Update meeting time
                        const meetingTimeField = document.querySelector('#podProfile input[type="time"]');
                        if (meetingTimeField && pod.time_utc) {{
                            // Convert from "19:00:00" to "19:00" format
                            const timeValue = pod.time_utc.substring(0, 5);
                            meetingTimeField.value = timeValue;
                        }}
                        
                        // Populate facilitator dropdown with pod members
                        const facilitatorSelect = Array.from(document.querySelectorAll('#podProfile select.field-input')).find(select => 
                            select.parentElement.textContent.includes('Facilitator')
                        );
                        if (facilitatorSelect && pod.members) {{
                            facilitatorSelect.innerHTML = '<option value="">Select Facilitator</option>';
                            pod.members.forEach(member => {{
                                const option = document.createElement('option');
                                option.value = member.user_id;
                                
                                // Clean up facilitator display name
                                let facilitatorName = member.users?.first_name || 'Unknown Member';
                                if (facilitatorName.includes('@telegram')) {{
                                    facilitatorName = `User ${{member.users?.telegram_user_id || 'Unknown'}}`;
                                }}
                                
                                option.textContent = facilitatorName;
                                facilitatorSelect.appendChild(option);
                            }});
                        }}
                        
                        // Populate add member dropdown with real users
                        const addMemberSelect = document.getElementById('newMemberSelect');
                        if (addMemberSelect && window.realUsers) {{
                            addMemberSelect.innerHTML = '<option value="">Select User to Add...</option>';
                            window.realUsers.forEach(user => {{
                                const option = document.createElement('option');
                                option.value = user.telegram_user_id;
                                
                                // Clean up user display name
                                let displayName = user.name || 'Unknown';
                                if (displayName.includes('@telegram')) {{
                                    displayName = `User ${{user.telegram_user_id}}`;
                                }}
                                
                                option.textContent = `${{displayName}} (ID: ${{user.telegram_user_id}})`;
                                addMemberSelect.appendChild(option);
                            }});
                        }}
                        
                        // Update member list
                        const memberListContainer = document.querySelector('#podProfile .member-list');
                        if (memberListContainer && pod.members) {{
                            memberListContainer.innerHTML = '';
                            
                            pod.members.forEach(member => {{
                                const memberDiv = document.createElement('div');
                                memberDiv.className = 'member-item';
                                
                                // Clean up member display name
                                let memberName = member.users?.first_name || 'Unknown';
                                if (memberName.includes('@telegram')) {{
                                    memberName = `User ${{member.users?.telegram_user_id || 'Unknown'}}`;
                                }}
                                
                                memberDiv.innerHTML = `
                                    <div>
                                        <div class="member-name">${{memberName}}</div>
                                        <div class="member-role">Member</div>
                                    </div>
                                    <button class="remove-btn" onclick="removeMember('${{member.user_id}}')">Remove</button>
                                `;
                                memberListContainer.appendChild(memberDiv);
                            }});
                            
                            // Update member count in section title
                            const memberSectionTitle = Array.from(document.querySelectorAll('#podProfile .section-title')).find(title => 
                                title.textContent.includes('Members')
                            );
                            if (memberSectionTitle) {{
                                const memberCount = pod.members.length;
                                memberSectionTitle.textContent = `Pod Members (${{memberCount}})`;
                            }}
                        }}
                    }} else {{
                        throw new Error(data.message || 'Pod not found');
                    }}
                }})
                .catch(error => {{
                    console.error('❌ Error loading pod data:', error);
                    document.getElementById('podName').textContent = 'Error Loading Pod';
                    
                    // Show error message
                    const profileId = document.querySelector('#podProfile .profile-id');
                    if (profileId) profileId.textContent = `ERROR: ${{error.message}}`;
                }});
        }}
        
        // LOAD DATA FROM API
        async function loadRealData() {
            console.log('🔄 Loading real data from API... (loadRealData function v3)');
            
            try {
                // Load users
                const usersResponse = await fetch('/api/crud/users');
                const usersData = await usersResponse.json();
                if (usersData.success) {
                    window.realUsers = usersData.data;
                    console.log('✅ Loaded', window.realUsers.length, 'users from API');
                } else {
                    console.error('❌ Failed to load users:', usersData.message);
                    window.realUsers = [];
                }
                
                // Load pods
                const podsResponse = await fetch('/api/crud/pods');
                const podsData = await podsResponse.json();
                if (podsData.success) {
                    window.realPods = podsData.data;
                    console.log('✅ Loaded', window.realPods.length, 'pods from API');
                } else {
                    console.error('❌ Failed to load pods:', podsData.message);
                    window.realPods = [];
                }
                
                // Now populate dropdowns
                populateDropdowns();
                
            } catch (error) {
                console.error('❌ Error loading real data:', error);
                window.realUsers = [];
                window.realPods = [];
                populateDropdowns(); // Still try to populate (will be empty)
            }
        }

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
                    
                    // Clean up user display name
                    let displayName = user.name || 'Unknown';
                    if (displayName.includes('@telegram')) {{
                        displayName = `User ${{user.telegram_user_id}}`;
                    }}
                    
                    option.textContent = `${{displayName}} (ID: ${{user.telegram_user_id}})`;
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
        
        // Multiple attempts to ensure dropdowns populate
        function ensureDropdownsPopulated() {{
            console.log('🔧 ensureDropdownsPopulated() called');
            
            // Load real data from API (which will call populateDropdowns)
            loadRealData();
            
            // Additional attempts with delays
            setTimeout(loadRealData, 100);
            setTimeout(loadRealData, 500);
            setTimeout(loadRealData, 1000);
        }}
        
        // Auto-populate dropdowns on load (but don't auto-show profiles)
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🔧 DOM loaded, attempting to populate dropdowns...');
            ensureDropdownsPopulated();
            // Profiles remain hidden until user selects from dropdown
        }});
        
        // Fallback for late script loading
        if (document.readyState === 'complete' || document.readyState === 'interactive') {{
            console.log('🔧 DOM already ready, populating dropdowns immediately...');
            ensureDropdownsPopulated();
        }}
        
        // Force population on window load as final fallback
        window.addEventListener('load', function() {{
            console.log('🔧 Window loaded, final dropdown population attempt...');
            ensureDropdownsPopulated();
            loadAvailableRoles();
        }});
        
        // COMMITMENT MANAGEMENT FUNCTIONS
        function displayUserCommitments(commitments) {{
            console.log('🔧 Displaying user commitments:', commitments);
            
            const commitmentsContainer = document.getElementById('userCommitments');
            if (!commitmentsContainer) return;
            
            if (!commitments || commitments.length === 0) {{
                commitmentsContainer.innerHTML = '<div style="color: var(--gray-400); font-size: var(--text-xs); text-align: center; padding: var(--space-md);">No commitments found</div>';
                return;
            }}
            
            commitmentsContainer.innerHTML = '';
            
            // Show most recent 5 commitments
            const recentCommitments = commitments.slice(0, 5);
            
            recentCommitments.forEach(commitment => {{
                const commitmentDiv = document.createElement('div');
                commitmentDiv.className = 'commitment-item';
                commitmentDiv.dataset.commitmentId = commitment.id;
                
                const statusClass = `status-${{commitment.status || 'active'}}`;
                const createdDate = commitment.created_at ? new Date(commitment.created_at).toLocaleDateString() : 'Unknown';
                
                commitmentDiv.innerHTML = `
                    <div class="commitment-header">
                        <div class="commitment-text" contenteditable="false" onblur="saveCommitmentText(this, '${{commitment.id}}')">${{commitment.commitment || 'No commitment text'}}</div>
                        <div class="commitment-status-badge ${{statusClass}}">${{commitment.status || 'active'}}</div>
                    </div>
                    <div class="commitment-meta">
                        <div class="commitment-date">Created: ${{createdDate}}</div>
                        <div class="commitment-actions">
                            <button class="edit-commitment-btn" onclick="editCommitment('${{commitment.id}}')">Edit</button>
                            <button class="edit-commitment-btn" onclick="changeCommitmentStatus('${{commitment.id}}', '${{commitment.status}}')">Status</button>
                            <button class="delete-commitment-btn" onclick="deleteCommitment('${{commitment.id}}')">Delete</button>
                        </div>
                    </div>
                    <div class="commitment-changelog" id="changelog-${{commitment.id}}">
                        <!-- Admin changes will be logged here -->
                    </div>
                `;
                commitmentsContainer.appendChild(commitmentDiv);
            }});
            
            console.log('✅ Displayed', recentCommitments.length, 'commitments');
        }}
        
        function editCommitment(commitmentId) {{
            const commitmentElement = document.querySelector(`[data-commitment-id="${{commitmentId}}"] .commitment-text`);
            if (commitmentElement) {{
                commitmentElement.contentEditable = 'true';
                commitmentElement.style.background = 'rgba(58, 134, 255, 0.1)';
                commitmentElement.style.border = '1px solid var(--cyber-blue)';
                commitmentElement.focus();
                
                console.log('📝 Editing commitment:', commitmentId);
            }}
        }}
        
        function saveCommitmentText(element, commitmentId) {{
            if (element.contentEditable === 'false') return;
            
            const newText = element.textContent.trim();
            const originalText = element.dataset.originalText || '';
            
            if (newText === originalText) {{
                element.contentEditable = 'false';
                element.style.background = '';
                element.style.border = '';
                return;
            }}
            
            console.log('💾 Saving commitment text change:', commitmentId, newText);
            
            // Save to API
            fetch(`/api/crud/commitments/${{commitmentId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ commitment: newText }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    console.log('✅ Commitment updated:', data);
                    
                    // Log the admin change
                    logCommitmentChange(commitmentId, 'text_changed', `Changed text from "${{originalText}}" to "${{newText}}"`);
                    
                    // Update UI
                    element.contentEditable = 'false';
                    element.style.background = '';
                    element.style.border = '';
                    element.dataset.originalText = newText;
                    
                    alert('Commitment text updated successfully!');
                }} else {{
                    alert('Error updating commitment: ' + (data.message || 'Unknown error'));
                    element.textContent = originalText; // Revert on error
                }}
            }})
            .catch(error => {{
                alert('Network error updating commitment');
                console.error('❌ Error:', error);
                element.textContent = originalText; // Revert on error
            }});
        }}
        
        function changeCommitmentStatus(commitmentId, currentStatus) {{
            const statuses = ['active', 'completed', 'failed'];
            const currentIndex = statuses.indexOf(currentStatus);
            const nextStatus = statuses[(currentIndex + 1) % statuses.length];
            
            console.log('🔄 Changing commitment status from', currentStatus, 'to', nextStatus);
            
            fetch(`/api/crud/commitments/${{commitmentId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ status: nextStatus }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    console.log('✅ Commitment status updated:', data);
                    
                    // Log the admin change
                    logCommitmentChange(commitmentId, 'status_changed', `Changed status from "${{currentStatus}}" to "${{nextStatus}}"`);
                    
                    // Reload user data to show updated commitment
                    if (currentUserId) {{
                        loadUserById(currentUserId);
                    }}
                    
                    alert(`Commitment status changed to "${{nextStatus}}"!`);
                }} else {{
                    alert('Error updating commitment status: ' + (data.message || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                alert('Network error updating commitment status');
                console.error('❌ Error:', error);
            }});
        }}
        
        function deleteCommitment(commitmentId) {{
            if (!confirm('Are you sure you want to delete this commitment? This action cannot be undone.')) {{
                return;
            }}
            
            console.log('🗑️ Deleting commitment:', commitmentId);
            
            // For now, we'll just mark as deleted rather than actually deleting
            // In a real system, you'd want to preserve the record for audit purposes
            fetch(`/api/crud/commitments/${{commitmentId}}`, {{
                method: 'PUT',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ status: 'deleted' }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    console.log('✅ Commitment deleted:', data);
                    
                    // Log the admin change
                    logCommitmentChange(commitmentId, 'deleted', 'Commitment deleted by admin');
                    
                    // Reload user data to show updated commitments
                    if (currentUserId) {{
                        loadUserById(currentUserId);
                    }}
                    
                    alert('Commitment deleted successfully!');
                }} else {{
                    alert('Error deleting commitment: ' + (data.message || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                alert('Network error deleting commitment');
                console.error('❌ Error:', error);
            }});
        }}
        
        function addNewCommitment() {{
            if (!currentUserId) {{
                alert('No user selected');
                return;
            }}
            
            const commitmentText = prompt('Enter the new commitment:');
            if (!commitmentText || !commitmentText.trim()) {{
                return;
            }}
            
            console.log('➕ Adding new commitment for user:', currentUserId);
            
            // Create commitment via API
            const commitmentData = {{
                commitment: commitmentText.trim(),
                telegram_user_id: parseInt(currentUserId),
                admin_user_id: "admin-dashboard" // TODO: Replace with actual admin user ID
            }};
            
            fetch('/api/crud/commitments', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(commitmentData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    console.log('✅ Commitment created successfully:', data.data);
                    alert('Commitment created successfully!');
                    
                    // Reload user commitments to show the new one
                    fetch(`/api/crud/commitments/user/${{currentUserId}}`)
                        .then(response => response.json())
                        .then(commitmentData => {{
                            if (commitmentData.success) {{
                                displayUserCommitments(commitmentData.data);
                            }}
                        }});
                }} else {{
                    console.error('❌ Error creating commitment:', data);
                    alert('Error creating commitment: ' + (data.message || data.detail || 'Unknown error'));
                }}
            }})
            .catch(error => {{
                console.error('❌ Network error creating commitment:', error);
                alert('Network error creating commitment. Please try again.');
            }});
            
            // Log the admin action
            logCommitmentChange(null, 'created', `Admin created new commitment: "${{commitmentText}}"`);        }}
        
        function logCommitmentChange(commitmentId, changeType, description) {{
            const timestamp = new Date().toISOString();
            const logEntry = {{
                commitment_id: commitmentId,
                change_type: changeType,
                description: description,
                admin_user: 'current_admin', // In real system, get from session
                timestamp: timestamp
            }};
            
            console.log('📊 Logging commitment change:', logEntry);
            
            // In a real system, this would be sent to an immutable audit log
            // For now, we'll display it in the UI
            if (commitmentId) {{
                const changelogDiv = document.getElementById(`changelog-${{commitmentId}}`);
                if (changelogDiv) {{
                    const entryDiv = document.createElement('div');
                    entryDiv.className = 'changelog-entry';
                    entryDiv.innerHTML = `<span class="changelog-admin">Admin</span> ${{description}} - ${{new Date().toLocaleString()}}`;
                    changelogDiv.appendChild(entryDiv);
                }}
            }}
            
            // TODO: Send to immutable audit log API
            // fetch('/api/audit/commitment-changes', {{ method: 'POST', body: JSON.stringify(logEntry) }});
        }}
        
        // ROLE MANAGEMENT FUNCTIONS
        let currentUserId = null;
        
        function displayUserRoles(roles) {{
            console.log('🔧 Displaying user roles:', roles);
            
            const rolesContainer = document.getElementById('userRoles');
            if (!rolesContainer) return;
            
            if (!roles || roles.length === 0) {{
                rolesContainer.innerHTML = '<div style="color: var(--gray-400); font-size: var(--text-xs);">No roles assigned</div>';
                return;
            }}
            
            rolesContainer.innerHTML = '';
            roles.forEach(roleData => {{
                const roleDiv = document.createElement('div');
                roleDiv.className = 'role-item';
                
                const roleName = roleData.role || roleData;
                const grantedDate = roleData.granted_at ? new Date(roleData.granted_at).toLocaleDateString() : '';
                
                roleDiv.innerHTML = `
                    <div>
                        <div class="role-name">${{roleName}}</div>
                        ${{grantedDate ? `<div style="font-size: 10px; color: var(--gray-400);">Granted: ${{grantedDate}}</div>` : ''}}
                    </div>
                    <button class="remove-role-btn" onclick="removeUserRole('${{roleName}}')">Remove</button>
                `;
                rolesContainer.appendChild(roleDiv);
            }});
        }}
        
        function loadAvailableRoles() {{
            console.log('🔧 Loading available roles...');
            
            fetch('/api/crud/roles')
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        console.log('✅ Available roles loaded:', data.data);
                        populateRoleSelect(data.data);
                    }} else {{
                        console.error('❌ Error loading roles:', data);
                    }}
                }})
                .catch(error => {{
                    console.error('❌ Network error loading roles:', error);
                }});
        }}
        
        function populateRoleSelect(availableRoles) {{
            const roleSelect = document.getElementById('roleSelect');
            if (!roleSelect) return;
            
            roleSelect.innerHTML = '<option value="">Select Role to Add...</option>';
            availableRoles.forEach(roleData => {{
                const option = document.createElement('option');
                option.value = roleData.role;
                option.textContent = `${{roleData.role}} - ${{roleData.description}}`;
                roleSelect.appendChild(option);
            }});
        }}
        
        function addUserRole() {{
            const roleSelect = document.getElementById('roleSelect');
            const role = roleSelect.value;
            
            if (!role) {{
                alert('Please select a role to add');
                return;
            }}
            
            if (!currentUserId) {{
                alert('No user selected');
                return;
            }}
            
            console.log('🔄 Adding role', role, 'to user', currentUserId);
            
            fetch(`/api/crud/users/${{currentUserId}}/roles/${{role}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert(`Role '${{role}}' added successfully!`);
                    console.log('✅ Role added:', data);
                    
                    // Clear selection
                    roleSelect.value = '';
                    
                    // Reload user data to show updated roles
                    loadUserById(currentUserId);
                }} else {{
                    alert('Error adding role: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error adding role:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error adding role');
                console.error('❌ Network error:', error);
            }});
        }}
        
        function removeUserRole(role) {{
            if (!currentUserId) {{
                alert('No user selected');
                return;
            }}
            
            if (!confirm(`Remove role '${{role}}' from this user?`)) {{
                return;
            }}
            
            console.log('🔄 Removing role', role, 'from user', currentUserId);
            
            fetch(`/api/crud/users/${{currentUserId}}/roles/${{role}}`, {{
                method: 'DELETE',
                headers: {{ 'Content-Type': 'application/json' }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert(`Role '${{role}}' removed successfully!`);
                    console.log('✅ Role removed:', data);
                    
                    // Reload user data to show updated roles
                    loadUserById(currentUserId);
                }} else {{
                    alert('Error removing role: ' + (data.message || 'Unknown error'));
                    console.error('❌ Error removing role:', data);
                }}
            }})
            .catch(error => {{
                alert('Network error removing role');
                console.error('❌ Network error:', error);
            }});
        }}
    </script>
</body>
</html>
"""
    return html_content