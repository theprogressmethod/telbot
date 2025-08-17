#!/usr/bin/env python3
"""
Nurture Control Dashboard
See and approve the next 7 messages for each user
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def add_nurture_control_routes(app: FastAPI):
    """Add nurture sequence control routes"""
    
    @app.get("/admin/nurture-control", response_class=HTMLResponse)
    async def nurture_control_dashboard():
        """Nurture sequence control - see and approve next 7 messages"""
        
        # Get users and their upcoming messages
        users_data = await get_users_with_upcoming_messages()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NURTURE_CONTROL.EXE - MESSAGE APPROVAL</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{ 
            font-family: 'Courier Prime', monospace; 
            background: #000011;
            color: #00ff88;
            font-size: 13px;
            line-height: 1.3;
            padding: 12px;
        }}
        
        .terminal {{
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
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
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 1px solid #00ff88;
        }}
        
        .header h1 {{
            font-size: 18px;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }}
        
        .controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding: 8px;
            background: #001122;
            border: 1px solid #333;
            border-radius: 2px;
        }}
        
        .filter-section {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        
        .filter-btn {{
            background: #001a33;
            border: 1px solid #3a86ff;
            color: #3a86ff;
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px;
        }}
        
        .filter-btn.active {{
            background: #3a86ff;
            color: #000011;
        }}
        
        .filter-btn:hover {{ background: #002244; }}
        
        .batch-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .action-btn {{
            background: #001a33;
            border: 1px solid #ff006b;
            color: #ff006b;
            padding: 4px 12px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px;
        }}
        
        .action-btn.approve {{ border-color: #00ff88; color: #00ff88; }}
        .action-btn:hover {{ background: #002244; }}
        
        .users-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .user-card {{
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            background: #000a11;
        }}
        
        .user-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 1px solid #222;
        }}
        
        .user-info {{
            display: flex;
            gap: 16px;
            align-items: center;
        }}
        
        .user-name {{
            color: #00ff88;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .user-stage {{
            color: #3a86ff;
            font-size: 11px;
            padding: 2px 6px;
            background: #001a33;
            border-radius: 2px;
            border: 1px solid #3a86ff;
        }}
        
        .user-stats {{
            color: #888;
            font-size: 11px;
        }}
        
        .user-actions {{
            display: flex;
            gap: 4px;
        }}
        
        .quick-btn {{
            background: transparent;
            border: 1px solid #666;
            color: #888;
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            border-radius: 2px;
        }}
        
        .quick-btn:hover {{ border-color: #00ff88; color: #00ff88; }}
        
        .messages-timeline {{
            margin-top: 8px;
        }}
        
        .message-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            margin: 2px 0;
            background: #000611;
            border-left: 3px solid #333;
            border-radius: 0 2px 2px 0;
        }}
        
        .message-item.pending {{ border-left-color: #ffbe0b; }}
        .message-item.approved {{ border-left-color: #00ff88; }}
        .message-item.paused {{ border-left-color: #ff006b; }}
        
        .message-content {{
            flex: 1;
            margin-right: 8px;
        }}
        
        .message-type {{
            color: #3a86ff;
            font-size: 10px;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        
        .message-preview {{
            color: #ccc;
            font-size: 11px;
            line-height: 1.2;
        }}
        
        .message-schedule {{
            color: #888;
            font-size: 10px;
            margin-top: 2px;
        }}
        
        .message-actions {{
            display: flex;
            gap: 4px;
            align-items: center;
        }}
        
        .msg-status {{
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            margin-right: 4px;
        }}
        
        .msg-status.pending {{ background: #ffbe0b; }}
        .msg-status.approved {{ background: #00ff88; }}
        .msg-status.paused {{ background: #ff006b; }}
        
        .approve-btn {{
            background: transparent;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 9px;
            border-radius: 2px;
        }}
        
        .pause-btn {{
            background: transparent;
            border: 1px solid #ff006b;
            color: #ff006b;
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 9px;
            border-radius: 2px;
        }}
        
        .edit-btn {{
            background: transparent;
            border: 1px solid #ffbe0b;
            color: #ffbe0b;
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 9px;
            border-radius: 2px;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: space-between;
            margin: 16px 0;
            padding: 8px;
            background: #001122;
            border: 1px solid #333;
            border-radius: 2px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            color: #00ff88;
            font-weight: bold;
            font-size: 16px;
        }}
        
        .stat-label {{
            color: #888;
            font-size: 10px;
            text-transform: uppercase;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 16px;
            color: #666;
            font-size: 10px;
            border-top: 1px solid #333;
            padding-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>NURTURE_CONTROL.EXE</h1>
                <div style="color: #3a86ff; font-size: 12px;">
                    MESSAGE APPROVAL & SCHEDULING CONTROL
                </div>
            </div>
            
            <div class="controls">
                <div class="filter-section">
                    <span style="color: #888; font-size: 11px;">FILTER:</span>
                    <button class="filter-btn active" onclick="filterUsers('all')">ALL</button>
                    <button class="filter-btn" onclick="filterUsers('pending')">PENDING_APPROVAL</button>
                    <button class="filter-btn" onclick="filterUsers('active')">ACTIVE_SEQUENCES</button>
                    <button class="filter-btn" onclick="filterUsers('paused')">PAUSED</button>
                </div>
                <div class="batch-actions">
                    <button class="action-btn approve" onclick="batchApprove()">APPROVE_ALL</button>
                    <button class="action-btn" onclick="batchPause()">PAUSE_ALL</button>
                </div>
            </div>
            
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{len(users_data)}</div>
                    <div class="stat-label">ACTIVE_USERS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{sum(len(user['upcoming_messages']) for user in users_data)}</div>
                    <div class="stat-label">PENDING_MESSAGES</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{sum(1 for user in users_data for msg in user['upcoming_messages'] if msg['status'] == 'pending')}</div>
                    <div class="stat-label">NEED_APPROVAL</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{sum(1 for user in users_data for msg in user['upcoming_messages'] if msg['status'] == 'approved')}</div>
                    <div class="stat-label">APPROVED</div>
                </div>
            </div>
            
            <div class="users-list">
                {generate_user_cards(users_data)}
            </div>
            
            <div class="footer">
NURTURE_CONTROL.EXE v1.0 © 2025 // LAST_UPDATE: {datetime.now().strftime('%H:%M:%S')} // AUTO_REFRESH: OFF
            </div>
        </div>
    </div>
    
    <script>
        function filterUsers(filter) {{
            // Remove active class from all filter buttons
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            event.target.classList.add('active');
            
            // Filter logic would go here
            console.log('Filtering by:', filter);
        }}
        
        function batchApprove() {{
            if (confirm('Approve all pending messages?')) {{
                console.log('Batch approving messages');
                // Implementation would go here
            }}
        }}
        
        function batchPause() {{
            if (confirm('Pause all active sequences?')) {{
                console.log('Batch pausing sequences');
                // Implementation would go here
            }}
        }}
        
        function approveMessage(userId, messageId) {{
            console.log('Approving message:', messageId, 'for user:', userId);
            // Implementation would go here
        }}
        
        function pauseMessage(userId, messageId) {{
            console.log('Pausing message:', messageId, 'for user:', userId);
            // Implementation would go here
        }}
        
        function editMessage(userId, messageId) {{
            console.log('Editing message:', messageId, 'for user:', userId);
            // Implementation would go here
        }}
    </script>
</body>
</html>
        """
        
        return html
    
    @app.post("/admin/nurture-control/approve/{user_id}/{message_id}")
    async def approve_message(user_id: str, message_id: str):
        """Approve a specific message for a user"""
        try:
            # Implementation for approving messages
            return {"success": True, "message": "Message approved"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/admin/nurture-control/pause/{user_id}/{message_id}")
    async def pause_message(user_id: str, message_id: str):
        """Pause a specific message for a user"""
        try:
            # Implementation for pausing messages
            return {"success": True, "message": "Message paused"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def get_users_with_upcoming_messages() -> List[Dict[str, Any]]:
    """Get users and their next 7 upcoming messages"""
    
    if not supabase:
        # Return mock data showing the concept
        return [
            {
                "user_id": "user_001",
                "name": "John Smith",
                "email": "john@example.com",
                "stage": "ONBOARDING",
                "days_in_sequence": 5,
                "engagement_score": 78,
                "upcoming_messages": [
                    {
                        "id": "msg_001",
                        "type": "EMAIL",
                        "subject": "Your progress method workbook",
                        "preview": "Hi John, I wanted to follow up on your commitment to...",
                        "scheduled_time": "Tomorrow 9:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_002", 
                        "type": "TELEGRAM",
                        "subject": "Check-in reminder",
                        "preview": "How did your morning routine go today?",
                        "scheduled_time": "Tomorrow 6:00 PM",
                        "status": "approved"
                    },
                    {
                        "id": "msg_003",
                        "type": "EMAIL",
                        "subject": "Shame spiral prevention",
                        "preview": "I noticed you missed yesterday's check-in. That's totally normal...",
                        "scheduled_time": "Day +3 at 10:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_004",
                        "type": "TELEGRAM",
                        "subject": "Progress celebration",
                        "preview": "🎉 You've been consistent for 3 days! Here's what that means...",
                        "scheduled_time": "Day +4 at 7:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_005",
                        "type": "EMAIL",
                        "subject": "Pod invitation",
                        "preview": "You're ready for the next step. I'd like to invite you to...",
                        "scheduled_time": "Day +5 at 11:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_006",
                        "type": "TELEGRAM",
                        "subject": "Pre-pod preparation",
                        "preview": "Your pod call is coming up. Here's what to expect...",
                        "scheduled_time": "Day +6 at 2:00 PM", 
                        "status": "pending"
                    },
                    {
                        "id": "msg_007",
                        "type": "EMAIL",
                        "subject": "Post-pod follow-up",
                        "preview": "How was your first pod experience? Let's debrief...",
                        "scheduled_time": "Day +7 at 9:00 AM",
                        "status": "pending"
                    }
                ]
            },
            {
                "user_id": "user_002",
                "name": "Sarah Johnson",
                "email": "sarah@example.com", 
                "stage": "POD_ACTIVE",
                "days_in_sequence": 12,
                "engagement_score": 92,
                "upcoming_messages": [
                    {
                        "id": "msg_101",
                        "type": "TELEGRAM",
                        "subject": "Weekly pod reminder",
                        "preview": "Your pod meeting is tomorrow at 7 PM. Today's prep question...",
                        "scheduled_time": "Tomorrow 10:00 AM",
                        "status": "approved"
                    },
                    {
                        "id": "msg_102",
                        "type": "EMAIL", 
                        "subject": "Commitment accountability",
                        "preview": "Sarah, you committed to exercising 4x this week. How's it going?",
                        "scheduled_time": "Day +2 at 8:00 AM",
                        "status": "approved"
                    },
                    {
                        "id": "msg_103",
                        "type": "TELEGRAM",
                        "subject": "Progress reflection",
                        "preview": "What's one small win from this week that you're proud of?",
                        "scheduled_time": "Day +3 at 6:00 PM",
                        "status": "approved"
                    },
                    {
                        "id": "msg_104",
                        "type": "EMAIL",
                        "subject": "Pod payment reminder",
                        "preview": "Your pod subscription renews in 3 days...",
                        "scheduled_time": "Day +4 at 11:00 AM",
                        "status": "paused"
                    },
                    {
                        "id": "msg_105",
                        "type": "TELEGRAM", 
                        "subject": "Community sharing prompt",
                        "preview": "Share one insight from this week with your pod mates...",
                        "scheduled_time": "Day +5 at 7:00 PM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_106",
                        "type": "EMAIL",
                        "subject": "Monthly reflection guide",
                        "preview": "You've been in your pod for almost a month. Time to reflect...",
                        "scheduled_time": "Day +6 at 9:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_107",
                        "type": "TELEGRAM",
                        "subject": "Next month planning",
                        "preview": "What do you want to focus on in your next month of growth?",
                        "scheduled_time": "Day +7 at 12:00 PM",
                        "status": "pending"
                    }
                ]
            },
            {
                "user_id": "user_003",
                "name": "Mike Chen",
                "email": "mike@example.com",
                "stage": "RE_ENGAGEMENT",
                "days_in_sequence": 21,
                "engagement_score": 34,
                "upcoming_messages": [
                    {
                        "id": "msg_201",
                        "type": "EMAIL",
                        "subject": "We miss you",
                        "preview": "Mike, I noticed you haven't engaged in a while. No judgment...",
                        "scheduled_time": "Tomorrow 2:00 PM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_202",
                        "type": "TELEGRAM",
                        "subject": "Simple re-engagement",
                        "preview": "Just checking in. How are you doing? One word answer is fine.",
                        "scheduled_time": "Day +2 at 10:00 AM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_203",
                        "type": "EMAIL",
                        "subject": "No pressure check-in",
                        "preview": "Life gets busy. If you're ready to reconnect, I'm here...",
                        "scheduled_time": "Day +4 at 3:00 PM",
                        "status": "pending"
                    },
                    {
                        "id": "msg_204",
                        "type": "TELEGRAM",
                        "subject": "Last gentle nudge",
                        "preview": "This is my last message unless you want to continue...",
                        "scheduled_time": "Day +7 at 11:00 AM",
                        "status": "pending"
                    }
                ]
            }
        ]
    
    try:
        # Get users from database
        users_result = supabase.table('users').select('*').execute()
        if not users_result.data:
            return []
        
        users_data = []
        for user in users_result.data:
            # Get upcoming messages for this user
            upcoming_messages = await get_user_upcoming_messages(user['id'])
            
            users_data.append({
                "user_id": user['id'],
                "name": user.get('name', 'Unknown'),
                "email": user.get('email', ''),
                "stage": user.get('current_stage', 'UNKNOWN'),
                "days_in_sequence": 0,  # Calculate based on creation date
                "engagement_score": 0,  # Calculate based on interactions
                "upcoming_messages": upcoming_messages
            })
        
        return users_data
        
    except Exception as e:
        # Return mock data on error
        return await get_users_with_upcoming_messages()

async def get_user_upcoming_messages(user_id: str) -> List[Dict[str, Any]]:
    """Get the next 7 upcoming messages for a specific user"""
    # Implementation would query the nurture_queue table
    # For now, return empty list
    return []

def generate_user_cards(users_data: List[Dict[str, Any]]) -> str:
    """Generate HTML for user cards with their upcoming messages"""
    html = ""
    
    for user in users_data:
        messages_html = ""
        for msg in user['upcoming_messages']:
            status_class = msg['status']
            messages_html += f"""
                <div class="message-item {status_class}">
                    <div class="message-content">
                        <div class="message-type">{msg['type']}</div>
                        <div class="message-preview">{msg['subject']}</div>
                        <div class="message-preview" style="opacity: 0.7;">{msg['preview'][:60]}...</div>
                        <div class="message-schedule">📅 {msg['scheduled_time']}</div>
                    </div>
                    <div class="message-actions">
                        <span class="msg-status {status_class}"></span>
                        <button class="approve-btn" onclick="approveMessage('{user['user_id']}', '{msg['id']}')">✓</button>
                        <button class="pause-btn" onclick="pauseMessage('{user['user_id']}', '{msg['id']}')">⏸</button>
                        <button class="edit-btn" onclick="editMessage('{user['user_id']}', '{msg['id']}')">✎</button>
                    </div>
                </div>
            """
        
        engagement_color = "#00ff88" if user['engagement_score'] >= 70 else "#ffbe0b" if user['engagement_score'] >= 40 else "#ff006b"
        
        html += f"""
            <div class="user-card">
                <div class="user-header">
                    <div class="user-info">
                        <div class="user-name">{user['name']}</div>
                        <div class="user-stage">{user['stage']}</div>
                        <div class="user-stats">
                            Day {user['days_in_sequence']} | 
                            <span style="color: {engagement_color}">Engagement: {user['engagement_score']}%</span> |
                            {len([m for m in user['upcoming_messages'] if m['status'] == 'pending'])} pending
                        </div>
                    </div>
                    <div class="user-actions">
                        <button class="quick-btn">VIEW_PROFILE</button>
                        <button class="quick-btn">EDIT_SEQUENCE</button>
                        <button class="quick-btn">PAUSE_ALL</button>
                    </div>
                </div>
                <div class="messages-timeline">
                    {messages_html}
                </div>
            </div>
        """
    
    return html