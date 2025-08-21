#!/usr/bin/env python3
"""
Retro Miami Vice + Commodore 64 Dashboards
Complete dashboard suite with vaporwave aesthetic
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from retro_styles import get_retro_css, get_retro_js
from retro_superadmin_dashboard import add_retro_superadmin_routes

def create_retro_admin_dashboard():
    """Generate retro admin dashboard HTML"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ADMIN.EXE - System Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_retro_css()}</style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>ADMIN DASHBOARD</h1>
                <h2>SYSTEM CONTROL INTERFACE</h2>
            </div>
            
            <div class="status-bar">
                <span class="status-item">STATUS: <span class="good">OPERATIONAL</span></span>
                <span class="status-item">USERS: <span style="color: #00ff88;">65</span></span>
                <span class="status-item">TIME: <span id="time">{datetime.now().strftime('%H:%M:%S')}</span></span>
            </div>
            
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('users')">USERS</button>
                <button class="tab-btn" onclick="showTab('pods')">PODS</button>
                <button class="tab-btn" onclick="showTab('system')">SYSTEM</button>
                <button class="tab-btn" onclick="showTab('alerts')">ALERTS</button>
            </div>
            
            <div id="users-tab" class="tab-content active">
                <div class="data-section">
                    <div class="data-header">USER MANAGEMENT</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">65</div>
                                <div class="metric-label">Total Users</div>
                            </div>
                            <div class="metric-card good">
                                <div class="metric-value">48</div>
                                <div class="metric-label">Active Today</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">12</div>
                                <div class="metric-label">New This Week</div>
                            </div>
                            <div class="metric-card warning">
                                <div class="metric-value">5</div>
                                <div class="metric-label">Inactive</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="pods-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">POD MANAGEMENT</div>
                    <div class="data-content">
                        <p style="color: #00ff88;">12 PODS CONFIGURED</p>
                        <p style="color: #ff6b35;">POD ASSIGNMENT SYSTEM READY</p>
                    </div>
                </div>
            </div>
            
            <div id="system-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">SYSTEM HEALTH</div>
                    <div class="data-content">
                        <p class="good">✓ DATABASE: CONNECTED</p>
                        <p class="good">✓ BOT API: ONLINE</p>
                        <p class="good">✓ WEBHOOKS: ACTIVE</p>
                        <p class="good">✓ MONITORING: ENABLED</p>
                    </div>
                </div>
            </div>
            
            <div id="alerts-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">SYSTEM ALERTS</div>
                    <div class="data-content">
                        <p class="success">No critical alerts</p>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <a href="/superadmin" style="color: #8338ec;">← BACK TO SUPERADMIN</a>
            </div>
        </div>
    </div>
    <script>{get_retro_js()}</script>
</body>
</html>
    """
    return html_content

def create_retro_business_dashboard():
    """Generate retro business analytics dashboard HTML"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BUSINESS.EXE - Analytics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_retro_css()}</style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>BUSINESS ANALYTICS</h1>
                <h2>BEHAVIORAL INTELLIGENCE METRICS</h2>
            </div>
            
            <div class="status-bar">
                <span class="status-item">REVENUE: <span class="good">$12,450</span></span>
                <span class="status-item">MRR: <span style="color: #00ff88;">$4,150</span></span>
                <span class="status-item">GROWTH: <span class="good">+23%</span></span>
            </div>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">87%</div>
                    <div class="metric-label">Retention Rate</div>
                </div>
                <div class="metric-card good">
                    <div class="metric-value">72%</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">4.8</div>
                    <div class="metric-label">Avg Rating</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">156</div>
                    <div class="metric-label">Total Commitments</div>
                </div>
            </div>
            
            <div class="data-section">
                <div class="data-header">KEY PERFORMANCE INDICATORS</div>
                <div class="data-content">
                    <table class="data-table">
                        <tr>
                            <th>METRIC</th>
                            <th>VALUE</th>
                            <th>TREND</th>
                        </tr>
                        <tr>
                            <td>User Acquisition</td>
                            <td>12/week</td>
                            <td class="good">↑ 15%</td>
                        </tr>
                        <tr>
                            <td>Engagement Rate</td>
                            <td>73.8%</td>
                            <td class="good">↑ 5%</td>
                        </tr>
                        <tr>
                            <td>Churn Rate</td>
                            <td>8.2%</td>
                            <td class="warning">↑ 2%</td>
                        </tr>
                        <tr>
                            <td>LTV</td>
                            <td>$245</td>
                            <td class="good">↑ 18%</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="footer">
                <a href="/superadmin" style="color: #8338ec;">← BACK TO SUPERADMIN</a>
            </div>
        </div>
    </div>
    <script>{get_retro_js()}</script>
</body>
</html>
    """
    return html_content

def create_retro_nurture_dashboard():
    """Generate retro nurture sequences dashboard HTML"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NURTURE.EXE - Sequence Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_retro_css()}</style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>NURTURE CONTROL</h1>
                <h2>MESSAGE SEQUENCE MANAGEMENT</h2>
            </div>
            
            <div class="status-bar">
                <span class="status-item">SEQUENCES: <span class="good">5 ACTIVE</span></span>
                <span class="status-item">MESSAGES: <span style="color: #00ff88;">1,245 SENT</span></span>
                <span class="status-item">OPEN RATE: <span class="good">68%</span></span>
            </div>
            
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('sequences')">SEQUENCES</button>
                <button class="tab-btn" onclick="showTab('schedule')">SCHEDULE</button>
                <button class="tab-btn" onclick="showTab('analytics')">ANALYTICS</button>
            </div>
            
            <div id="sequences-tab" class="tab-content active">
                <div class="data-section">
                    <div class="data-header">ACTIVE SEQUENCES</div>
                    <div class="data-content">
                        <table class="data-table">
                            <tr>
                                <th>SEQUENCE</th>
                                <th>USERS</th>
                                <th>STATUS</th>
                            </tr>
                            <tr>
                                <td>Welcome Series</td>
                                <td>65</td>
                                <td class="good">ACTIVE</td>
                            </tr>
                            <tr>
                                <td>Weekly Check-in</td>
                                <td>48</td>
                                <td class="good">ACTIVE</td>
                            </tr>
                            <tr>
                                <td>Re-engagement</td>
                                <td>12</td>
                                <td class="warning">PAUSED</td>
                            </tr>
                            <tr>
                                <td>Pod Updates</td>
                                <td>34</td>
                                <td class="good">ACTIVE</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
            
            <div id="schedule-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">UPCOMING MESSAGES</div>
                    <div class="data-content">
                        <p class="good">NEXT: Sunday 6:00 PM - Commitment Reminders</p>
                        <p style="color: #ff6b35;">QUEUE: 34 messages pending</p>
                    </div>
                </div>
            </div>
            
            <div id="analytics-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">PERFORMANCE METRICS</div>
                    <div class="data-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">68%</div>
                                <div class="metric-label">Open Rate</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">42%</div>
                                <div class="metric-label">Click Rate</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">2.3%</div>
                                <div class="metric-label">Unsubscribe</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <a href="/superadmin" style="color: #8338ec;">← BACK TO SUPERADMIN</a>
            </div>
        </div>
    </div>
    <script>{get_retro_js()}</script>
</body>
</html>
    """
    return html_content

def add_all_retro_routes(app: FastAPI):
    """Add all retro dashboard routes to FastAPI app"""
    
    # Add superadmin routes
    add_retro_superadmin_routes(app)
    
    # Add other dashboard routes
    @app.get("/retro/admin", response_class=HTMLResponse)
    async def retro_admin():
        return create_retro_admin_dashboard()
    
    @app.get("/retro/business", response_class=HTMLResponse)
    async def retro_business():
        return create_retro_business_dashboard()
    
    @app.get("/retro/nurture", response_class=HTMLResponse)
    async def retro_nurture():
        return create_retro_nurture_dashboard()

# Standalone server for testing
if __name__ == "__main__":
    import uvicorn
    
    app = FastAPI(title="Retro Miami Vice + Commodore 64 Dashboards")
    add_all_retro_routes(app)
    
    print("🚀 Starting Retro Dashboard Suite")
    print("📍 Main Dashboard: http://localhost:7001/superadmin")
    print("📊 Admin Dashboard: http://localhost:7001/retro/admin")
    print("📈 Business Dashboard: http://localhost:7001/retro/business")
    print("💬 Nurture Dashboard: http://localhost:7001/retro/nurture")
    print("🎨 Miami Vice + Commodore 64 Aesthetic")
    
    uvicorn.run(app, host="0.0.0.0", port=7001)