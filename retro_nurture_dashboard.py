#!/usr/bin/env python3
"""
Retro Nurture Sequences Dashboard
Miami Vice + Commodore 64 aesthetic for message flow tracking
"""

from retro_styles import get_retro_css, get_retro_js

def get_retro_nurture_dashboard_html():
    """Generate retro nurture sequences dashboard"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NURTURE_SEQUENCES.EXE - MESSAGE FLOW CONTROL</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {get_retro_css()}
        
        .sequence-card {{
            background: #001122;
            border: 1px solid #00ff88;
            border-radius: 2px;
            padding: 6px;
            margin: 4px 0;
        }}
        
        .sequence-status {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 10px;
            font-weight: 700;
        }}
        
        .status-active {{ background: #001a33; color: #00ff88; border: 1px solid #00ff88; }}
        .status-completed {{ background: #000a22; color: #3a86ff; border: 1px solid #3a86ff; }}
        .status-failed {{ background: #220011; color: #ff006b; border: 1px solid #ff006b; }}
        .status-pending {{ background: #221100; color: #ffbe0b; border: 1px solid #ffbe0b; }}
        
        .user-engagement {{
            display: grid;
            grid-template-columns: 1fr auto auto auto;
            gap: 8px;
            align-items: center;
            padding: 4px;
            border-bottom: 1px solid #222;
            font-size: 11px;
        }}
        
        .engagement-high {{ color: #06ffa5; }}
        .engagement-medium {{ color: #ffbe0b; }}
        .engagement-low {{ color: #ff006b; }}
        
        .message-queue {{
            background: #000a11;
            border: 1px solid #333;
            border-radius: 2px;
            padding: 4px;
            margin: 4px 0;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .message-item {{
            padding: 3px;
            border-bottom: 1px solid #111;
            font-size: 10px;
        }}
        
        .channel-telegram {{ color: #3a86ff; }}
        .channel-email {{ color: #ff6b35; }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>NURTURE_SEQUENCES.EXE</h1>
                <div style="color: #ff006b; font-size: 12px;">MESSAGE FLOW CONTROL SYSTEM v2.0</div>
            </div>
            
            <div class="ascii-border">
███╗   ██╗██╗   ██╗██████╗ ████████╗██╗   ██╗██████╗ ███████╗
████╗  ██║██║   ██║██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝
██╔██╗ ██║██║   ██║██████╔╝   ██║   ██║   ██║██████╔╝█████╗  
██║╚██╗██║██║   ██║██╔══██╗   ██║   ██║   ██║██╔══██╗██╔══╝  
██║ ╚████║╚██████╔╝██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗
╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
            </div>
            
            <div class="status-bar">
                <span>SEQUENCES: <span style="color: #00ff88;">12</span></span>
                <span>MESSAGES: <span style="color: #3a86ff;">47</span></span>
                <span>ENGAGEMENT: <span style="color: #ff6b35;">73.2%</span></span>
                <span>CHANNELS: <span style="color: #ffbe0b;">2</span></span>
                <span class="blink">█</span>
            </div>
            
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('users')">USER_ENGAGEMENT</button>
                <button class="tab-btn" onclick="showTab('sequences')">ACTIVE_SEQUENCES</button>
                <button class="tab-btn" onclick="showTab('messages')">MESSAGE_QUEUE</button>
                <button class="tab-btn" onclick="showTab('analytics')">ANALYTICS</button>
            </div>
            
            <!-- Users Tab -->
            <div id="users-tab" class="tab-content active">
                <div class="data-section">
                    <div class="data-header">USER ENGAGEMENT MATRIX</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">12</div>
                                <div class="metric-label">ACTIVE_USERS</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">8</div>
                                <div class="metric-label">HIGH_ENGAGE</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">65%</div>
                                <div class="metric-label">RETENTION</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">31</div>
                                <div class="metric-label">TOTAL_USERS</div>
                            </div>
                        </div>
                        
                        <div id="user-list">
                            <div class="user-engagement">
                                <span class="engagement-high">Alice Johnson</span>
                                <span class="sequence-status status-active">LEADERSHIP</span>
                                <span class="engagement-high">95%</span>
                                <span class="channel-telegram">📱 TG</span>
                            </div>
                            <div class="user-engagement">
                                <span class="engagement-medium">Bob Smith</span>
                                <span class="sequence-status status-active">FITNESS</span>
                                <span class="engagement-medium">72%</span>
                                <span class="channel-email">📧 EM</span>
                            </div>
                            <div class="user-engagement">
                                <span class="engagement-low">Carol Davis</span>
                                <span class="sequence-status status-failed">RE_ENGAGE</span>
                                <span class="engagement-low">45%</span>
                                <span class="channel-telegram">📱 TG</span>
                            </div>
                            <div class="user-engagement">
                                <span class="engagement-low">David Wilson</span>
                                <span class="sequence-status status-pending">INTERVENTION</span>
                                <span class="engagement-low">25%</span>
                                <span class="channel-email">📧 EM</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Sequences Tab -->
            <div id="sequences-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">ACTIVE SEQUENCE MONITORING</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">4</div>
                                <div class="metric-label">ACTIVE_SEQ</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">7</div>
                                <div class="metric-label">MSG_PER_WEEK</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">68.5%</div>
                                <div class="metric-label">AVG_ENGAGE</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">24</div>
                                <div class="metric-label">DELIVERIES</div>
                            </div>
                        </div>
                        
                        <div id="sequence-list">
                            <div class="sequence-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #00ff88; font-weight: 700;">POD_WEEKLY_NURTURE</span>
                                    <span class="sequence-status status-active">ACTIVE</span>
                                </div>
                                <div style="font-size: 10px; color: #8338ec; margin: 2px 0;">
                                    7-touch weekly sequence • 3 users • 68.5% engagement
                                </div>
                            </div>
                            
                            <div class="sequence-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #3a86ff; font-weight: 700;">LEADERSHIP_DEVELOPMENT</span>
                                    <span class="sequence-status status-active">ACTIVE</span>
                                </div>
                                <div style="font-size: 10px; color: #8338ec; margin: 2px 0;">
                                    Advanced sequence • 1 user • 89.2% engagement
                                </div>
                            </div>
                            
                            <div class="sequence-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #ffbe0b; font-weight: 700;">RE_ENGAGEMENT</span>
                                    <span class="sequence-status status-pending">PENDING</span>
                                </div>
                                <div style="font-size: 10px; color: #8338ec; margin: 2px 0;">
                                    Gentle outreach • 1 user • 34.1% engagement
                                </div>
                            </div>
                            
                            <div class="sequence-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #ff006b; font-weight: 700;">INTERVENTION_OUTREACH</span>
                                    <span class="sequence-status status-failed">CRITICAL</span>
                                </div>
                                <div style="font-size: 10px; color: #8338ec; margin: 2px 0;">
                                    Personal intervention • 1 user • 15.7% engagement
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Messages Tab -->
            <div id="messages-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">MESSAGE QUEUE STATUS</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">4</div>
                                <div class="metric-label">SCHEDULED</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">2</div>
                                <div class="metric-label">SENT</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">1</div>
                                <div class="metric-label">DELIVERED</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">1</div>
                                <div class="metric-label">PENDING</div>
                            </div>
                        </div>
                        
                        <div class="message-queue" id="message-queue">
                            <div class="message-item">
                                <span class="channel-telegram">📱</span> ALICE → LEADERSHIP: Ready for challenge? Consider mentoring...
                                <div style="color: #666; font-size: 9px;">09:00 • SENT • HIGH_ENGAGEMENT</div>
                            </div>
                            <div class="message-item">
                                <span class="channel-email">📧</span> BOB → FITNESS: How's your fitness commitment going...
                                <div style="color: #666; font-size: 9px;">15:00 • OPENED • MEDIUM_ENGAGEMENT</div>
                            </div>
                            <div class="message-item">
                                <span class="channel-telegram">📱</span> CAROL → RE_ENGAGE: We miss you in Creative Entrepreneurs...
                                <div style="color: #666; font-size: 9px;">11:00 • DELIVERED • LOW_ENGAGEMENT</div>
                            </div>
                            <div class="message-item">
                                <span class="channel-email">📧</span> DAVID → INTERVENTION: Thomas here. Let's schedule call...
                                <div style="color: #666; font-size: 9px;">14:00 • PENDING • NO_ENGAGEMENT</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Analytics Tab -->
            <div id="analytics-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">PERFORMANCE ANALYTICS</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">73.2%</div>
                                <div class="metric-label">ENGAGEMENT</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">18.5%</div>
                                <div class="metric-label">ATTENDANCE_BOOST</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">65%</div>
                                <div class="metric-label">TELEGRAM_SHARE</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">1.2s</div>
                                <div class="metric-label">RESPONSE_TIME</div>
                            </div>
                        </div>
                        
                        <div class="chart-container">
                            <div style="color: #ff6b35; font-size: 12px; margin-bottom: 4px;">WEEKLY ENGAGEMENT TRENDS</div>
                            <div style="color: #666; font-size: 10px;">
                                MON: 68% • TUE: 72% • WED: 70% • THU: 75% • FRI: 73% • SAT: 69% • SUN: 71%
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
NURTURE_SEQUENCES.EXE v2.0 © 2025 // AUTO_REFRESH: 10s // LAST_UPDATE: <span id="footer-time">--:--:--</span>
            </div>
        </div>
    </div>

    <script>
        {get_retro_js()}
        
        // Auto-refresh data every 10 seconds
        setInterval(() => {{
            console.log('Refreshing nurture sequence data...');
            // In real implementation, this would fetch fresh data
        }}, 10000);
        
        // Initialize with first tab
        showTab('users');
    </script>
</body>
</html>
    """
    
    return html_content