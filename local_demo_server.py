#!/usr/bin/env python3
"""
Local Demo Server for Nurture Sequence System
Provides visual interface to demonstrate capabilities
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Nurture Sequence Demo",
    description="Interactive demo of The Progress Method nurture sequence system",
    version="1.0.0"
)

# Demo data
DEMO_USERS = [
    {
        "id": "demo-alice",
        "name": "Alice Johnson",
        "email": "alice.demo@theprogressmethod.com",
        "pod": "Leadership Accelerator",
        "engagement_score": 95,
        "attendance_rate": 100,
        "telegram_engagement": 85,
        "email_engagement": 70,
        "status": "high_performer",
        "current_sequences": ["pod_weekly_nurture", "leadership_development"],
        "recent_activity": "Completed commitment early, mentored new member"
    },
    {
        "id": "demo-bob",
        "name": "Bob Smith", 
        "email": "bob.demo@theprogressmethod.com",
        "pod": "Fitness Focused",
        "engagement_score": 72,
        "attendance_rate": 80,
        "telegram_engagement": 60,
        "email_engagement": 45,
        "status": "consistent_member",
        "current_sequences": ["pod_weekly_nurture"],
        "recent_activity": "Attended last 3 meetings, moderate engagement"
    },
    {
        "id": "demo-carol",
        "name": "Carol Davis",
        "email": "carol.demo@theprogressmethod.com", 
        "pod": "Creative Entrepreneurs",
        "engagement_score": 45,
        "attendance_rate": 45,
        "telegram_engagement": 30,
        "email_engagement": 20,
        "status": "needs_support",
        "current_sequences": ["re_engagement", "commitment_follow_up"],
        "recent_activity": "Missed last 2 meetings, low commitment completion"
    },
    {
        "id": "demo-david",
        "name": "David Wilson",
        "email": "david.demo@theprogressmethod.com",
        "pod": "Tech Leaders",
        "engagement_score": 25,
        "attendance_rate": 20,
        "telegram_engagement": 10,
        "email_engagement": 5,
        "status": "at_risk",
        "current_sequences": ["intervention_outreach"],
        "recent_activity": "No attendance for 3 weeks, minimal responses"
    }
]

DEMO_SEQUENCES = {
    "pod_weekly_nurture": {
        "name": "Pod Weekly Nurture",
        "description": "7-touch weekly sequence for pod members",
        "active_users": 3,
        "messages_per_week": 7,
        "avg_engagement": 68.5
    },
    "leadership_development": {
        "name": "Leadership Development",
        "description": "Advanced sequence for high performers",
        "active_users": 1,
        "messages_per_week": 4,
        "avg_engagement": 89.2
    },
    "re_engagement": {
        "name": "Re-engagement",
        "description": "Gentle outreach for inconsistent members",
        "active_users": 1,
        "messages_per_week": 3,
        "avg_engagement": 34.1
    },
    "intervention_outreach": {
        "name": "Intervention Outreach",
        "description": "Personal intervention for at-risk members",
        "active_users": 1,
        "messages_per_week": 2,
        "avg_engagement": 15.7
    }
}

DEMO_MESSAGES = [
    {
        "id": "msg-1",
        "user": "Alice Johnson",
        "sequence": "leadership_development",
        "channel": "telegram",
        "message": "🌟 Alice, ready for a leadership challenge? Consider mentoring a new pod member this week!",
        "scheduled_at": "2025-08-16T09:00:00",
        "status": "sent",
        "engagement": "high"
    },
    {
        "id": "msg-2", 
        "user": "Bob Smith",
        "sequence": "pod_weekly_nurture",
        "channel": "email",
        "message": "💪 How's your fitness commitment going this week, Bob? Remember, progress over perfection!",
        "scheduled_at": "2025-08-16T15:00:00",
        "status": "opened",
        "engagement": "medium"
    },
    {
        "id": "msg-3",
        "user": "Carol Davis", 
        "sequence": "re_engagement",
        "channel": "telegram",
        "message": "Hi Carol 👋 We miss you in Creative Entrepreneurs! What can we do to support you better?",
        "scheduled_at": "2025-08-16T11:00:00",
        "status": "delivered",
        "engagement": "low"
    },
    {
        "id": "msg-4",
        "user": "David Wilson",
        "sequence": "intervention_outreach", 
        "channel": "email",
        "message": "David, Thomas here. Let's schedule a quick call to reconnect and see how we can help.",
        "scheduled_at": "2025-08-16T14:00:00",
        "status": "pending",
        "engagement": "none"
    }
]

@app.get("/", response_class=HTMLResponse)
async def demo_dashboard(request: Request):
    """Main demo dashboard"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nurture Sequence System Demo</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .status-high {{ background: linear-gradient(135deg, #10b981, #059669); }}
            .status-medium {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
            .status-low {{ background: linear-gradient(135deg, #ef4444, #dc2626); }}
            .status-none {{ background: linear-gradient(135deg, #6b7280, #4b5563); }}
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Header -->
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <div class="flex items-center">
                            <h1 class="text-3xl font-bold text-gray-900">🚀 Nurture Sequence System</h1>
                            <span class="ml-4 px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">DEMO</span>
                        </div>
                        <div class="text-sm text-gray-500">
                            Live Demo • The Progress Method
                        </div>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <!-- Stats Overview -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="bg-white p-6 rounded-lg shadow">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                    <span class="text-white text-sm">📱</span>
                                </div>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Active Sequences</p>
                                <p class="text-2xl font-semibold text-gray-900">12</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <span class="text-white text-sm">📧</span>
                                </div>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Messages Today</p>
                                <p class="text-2xl font-semibold text-gray-900">47</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                                    <span class="text-white text-sm">📊</span>
                                </div>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Engagement Rate</p>
                                <p class="text-2xl font-semibold text-gray-900">73.2%</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                    <span class="text-white text-sm">📈</span>
                                </div>
                            </div>
                            <div class="ml-4">
                                <p class="text-sm font-medium text-gray-500">Attendance +</p>
                                <p class="text-2xl font-semibold text-gray-900">18.5%</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Navigation Tabs -->
                <div class="bg-white rounded-lg shadow mb-8">
                    <div class="border-b border-gray-200">
                        <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                            <button onclick="showTab('users')" id="tab-users" class="tab-button border-b-2 border-blue-500 py-4 px-1 text-sm font-medium text-blue-600">
                                Users & Engagement
                            </button>
                            <button onclick="showTab('sequences')" id="tab-sequences" class="tab-button border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                                Active Sequences
                            </button>
                            <button onclick="showTab('messages')" id="tab-messages" class="tab-button border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                                Message Queue
                            </button>
                            <button onclick="showTab('analytics')" id="tab-analytics" class="tab-button border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                                Analytics
                            </button>
                        </nav>
                    </div>

                    <!-- Tab Content -->
                    <div class="p-6">
                        <!-- Users Tab -->
                        <div id="content-users" class="tab-content">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">User Engagement Overview</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {generate_user_cards()}
                            </div>
                        </div>

                        <!-- Sequences Tab -->
                        <div id="content-sequences" class="tab-content hidden">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">Active Nurture Sequences</h3>
                            <div class="space-y-4">
                                {generate_sequence_cards()}
                            </div>
                        </div>

                        <!-- Messages Tab -->
                        <div id="content-messages" class="tab-content hidden">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Messages</h3>
                            <div class="space-y-4">
                                {generate_message_cards()}
                            </div>
                        </div>

                        <!-- Analytics Tab -->
                        <div id="content-analytics" class="tab-content hidden">
                            <h3 class="text-lg font-medium text-gray-900 mb-4">Performance Analytics</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <h4 class="font-medium mb-2">Channel Performance</h4>
                                    <canvas id="channelChart" width="400" height="200"></canvas>
                                </div>
                                <div class="bg-gray-50 p-4 rounded-lg">
                                    <h4 class="font-medium mb-2">Engagement Trends</h4>
                                    <canvas id="engagementChart" width="400" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>

        <script>
            function showTab(tabName) {{
                // Hide all content
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.tab-button').forEach(el => {{
                    el.classList.remove('border-blue-500', 'text-blue-600');
                    el.classList.add('border-transparent', 'text-gray-500');
                }});
                
                // Show selected content
                document.getElementById('content-' + tabName).classList.remove('hidden');
                document.getElementById('tab-' + tabName).classList.remove('border-transparent', 'text-gray-500');
                document.getElementById('tab-' + tabName).classList.add('border-blue-500', 'text-blue-600');
                
                // Initialize charts for analytics tab
                if (tabName === 'analytics') {{
                    setTimeout(initCharts, 100);
                }}
            }}
            
            function initCharts() {{
                // Channel Performance Chart
                const ctx1 = document.getElementById('channelChart');
                if (ctx1) {{
                    new Chart(ctx1, {{
                        type: 'doughnut',
                        data: {{
                            labels: ['Telegram', 'Email', 'Multi-Channel'],
                            datasets: [{{
                                data: [65, 25, 10],
                                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b']
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    }});
                }}
                
                // Engagement Trends Chart  
                const ctx2 = document.getElementById('engagementChart');
                if (ctx2) {{
                    new Chart(ctx2, {{
                        type: 'line',
                        data: {{
                            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            datasets: [{{
                                label: 'Engagement %',
                                data: [68, 72, 70, 75, 73, 69, 71],
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.4
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                y: {{
                                    beginAtZero: true,
                                    max: 100
                                }}
                            }}
                        }}
                    }});
                }}
            }}
            
            // Auto-refresh data every 10 seconds
            setInterval(() => {{
                console.log('Refreshing demo data...');
                // In real implementation, this would fetch fresh data
            }}, 10000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def generate_user_cards():
    """Generate HTML for user cards"""
    cards = ""
    for user in DEMO_USERS:
        status_class = f"status-{user['status'].split('_')[0]}"
        cards += f"""
        <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                    <div class="w-10 h-10 {status_class} rounded-full flex items-center justify-center text-white font-bold mr-3">
                        {user['name'][0]}
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900">{user['name']}</h4>
                        <p class="text-sm text-gray-500">{user['pod']}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-2xl font-bold text-gray-900">{user['engagement_score']}%</p>
                    <p class="text-xs text-gray-500">Engagement</p>
                </div>
            </div>
            <div class="grid grid-cols-3 gap-3 text-center">
                <div>
                    <p class="text-sm font-medium text-gray-900">{user['attendance_rate']}%</p>
                    <p class="text-xs text-gray-500">Attendance</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-900">{user['telegram_engagement']}%</p>
                    <p class="text-xs text-gray-500">Telegram</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-900">{user['email_engagement']}%</p>
                    <p class="text-xs text-gray-500">Email</p>
                </div>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100">
                <p class="text-xs text-gray-600">{user['recent_activity']}</p>
                <div class="flex flex-wrap gap-1 mt-2">
                    {"".join([f'<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{seq}</span>' for seq in user['current_sequences']])}
                </div>
            </div>
        </div>
        """
    return cards

def generate_sequence_cards():
    """Generate HTML for sequence cards"""
    cards = ""
    for seq_id, seq in DEMO_SEQUENCES.items():
        cards += f"""
        <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-medium text-gray-900">{seq['name']}</h4>
                    <p class="text-sm text-gray-500">{seq['description']}</p>
                </div>
                <div class="text-right">
                    <p class="text-lg font-bold text-gray-900">{seq['active_users']}</p>
                    <p class="text-xs text-gray-500">Active Users</p>
                </div>
            </div>
            <div class="mt-3 grid grid-cols-2 gap-4 text-center">
                <div>
                    <p class="text-sm font-medium text-gray-900">{seq['messages_per_week']}/week</p>
                    <p class="text-xs text-gray-500">Messages</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-900">{seq['avg_engagement']}%</p>
                    <p class="text-xs text-gray-500">Engagement</p>
                </div>
            </div>
        </div>
        """
    return cards

def generate_message_cards():
    """Generate HTML for message cards"""
    cards = ""
    status_colors = {
        'sent': 'bg-green-100 text-green-800',
        'opened': 'bg-blue-100 text-blue-800', 
        'delivered': 'bg-yellow-100 text-yellow-800',
        'pending': 'bg-gray-100 text-gray-800'
    }
    
    for msg in DEMO_MESSAGES:
        status_class = status_colors.get(msg['status'], 'bg-gray-100 text-gray-800')
        cards += f"""
        <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center">
                    <span class="text-lg mr-2">{'📱' if msg['channel'] == 'telegram' else '📧'}</span>
                    <div>
                        <h4 class="font-medium text-gray-900">{msg['user']}</h4>
                        <p class="text-sm text-gray-500">{msg['sequence'].replace('_', ' ').title()}</p>
                    </div>
                </div>
                <span class="px-2 py-1 {status_class} text-xs font-medium rounded">
                    {msg['status'].title()}
                </span>
            </div>
            <p class="text-sm text-gray-700 mb-2">{msg['message']}</p>
            <p class="text-xs text-gray-500">Scheduled: {msg['scheduled_at']}</p>
        </div>
        """
    return cards

@app.get("/api/users")
async def get_demo_users():
    """API endpoint for demo users"""
    return {"users": DEMO_USERS}

@app.get("/api/sequences")
async def get_demo_sequences():
    """API endpoint for demo sequences"""
    return {"sequences": DEMO_SEQUENCES}

@app.get("/api/messages")
async def get_demo_messages():
    """API endpoint for demo messages"""
    return {"messages": DEMO_MESSAGES}

@app.get("/api/stats")
async def get_demo_stats():
    """API endpoint for demo statistics"""
    return {
        "active_sequences": sum(seq["active_users"] for seq in DEMO_SEQUENCES.values()),
        "messages_today": len(DEMO_MESSAGES),
        "engagement_rate": 73.2,
        "attendance_improvement": 18.5
    }

if __name__ == "__main__":
    print("🚀 Starting Nurture Sequence Demo Server...")
    print("📊 Demo will be available at: http://localhost:8081")
    print("🎯 This demonstrates the full admin interface capabilities")
    print("")
    print("Features demonstrated:")
    print("  ✅ User engagement tracking with personalized scoring")
    print("  ✅ Active sequence monitoring and management")
    print("  ✅ Multi-channel message queue with delivery status")
    print("  ✅ Real-time analytics and performance metrics")
    print("")
    print("Press Ctrl+C to stop the demo server")
    
    uvicorn.run(app, host="0.0.0.0", port=8081)