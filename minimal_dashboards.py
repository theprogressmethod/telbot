#!/usr/bin/env python3
"""
Minimal Clean Dashboards
Simple, clean design inspired by Commodore output but minimal aesthetic
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

def get_minimal_css():
    """Get minimal clean CSS styles"""
    return """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f8fafc;
            color: #1f2937;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 2rem;
            border-bottom: 1px solid #e5e7eb;
            text-align: center;
        }
        
        .header h1 {
            margin: 0 0 0.5rem 0;
            font-size: 1.875rem;
            font-weight: 600;
            color: #111827;
        }
        
        .header h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            font-weight: 400;
            color: #6b7280;
        }
        
        .environment-badge {
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .environment-badge.staging {
            background: #f59e0b;
        }
        
        .environment-badge.production {
            background: #ef4444;
        }
        
        .container {
            max-width: 1200px;
            margin: 3rem auto;
            padding: 0 1.5rem;
        }
        
        .card {
            background: white;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            font-size: 1.125rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        
        .metric-item {
            text-align: center;
            padding: 1rem;
            background: #f9fafb;
            border-radius: 0.375rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #111827;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .status-item {
            text-align: center;
            padding: 0.75rem;
        }
        
        .status-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }
        
        .status-label {
            font-size: 0.75rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .dashboard-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .dashboard-item {
            padding: 1.5rem;
            background: #f9fafb;
            border-radius: 0.375rem;
            transition: all 0.2s;
            cursor: pointer;
        }
        
        .dashboard-item:hover {
            background: #f3f4f6;
            transform: translateY(-2px);
        }
        
        .dashboard-link {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: inherit;
        }
        
        .dashboard-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
            width: 2rem;
            text-align: center;
        }
        
        .dashboard-info h3 {
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #111827;
        }
        
        .dashboard-info p {
            margin: 0.25rem 0 0 0;
            font-size: 0.875rem;
            color: #6b7280;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .table th,
        .table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .table th {
            font-weight: 600;
            color: #374151;
            background: #f9fafb;
        }
        
        .table td {
            color: #111827;
        }
        
        .success { color: #10b981; }
        .warning { color: #f59e0b; }
        .error { color: #ef4444; }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.875rem;
        }
    """

def get_minimal_superadmin_html():
    """Generate minimal SuperAdmin dashboard"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SuperAdmin - Progress Method</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_minimal_css()}</style>
</head>
<body>
    <div class="header">
        <h1>SuperAdmin Dashboard</h1>
        <h2>Minimal Clean Interface</h2>
        <div class="environment-badge {environment}">{environment}</div>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-value success">Online</div>
                    <div class="status-label">System</div>
                </div>
                <div class="status-item">
                    <div class="status-value">65</div>
                    <div class="status-label">Users</div>
                </div>
                <div class="status-item">
                    <div class="status-value">12</div>
                    <div class="status-label">Pods</div>
                </div>
                <div class="status-item">
                    <div class="status-value">24h</div>
                    <div class="status-label">Uptime</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">System Dashboards</div>
            <div class="dashboard-list">
                <div class="dashboard-item" onclick="window.open('/minimal/admin', '_blank')">
                    <div class="dashboard-link">
                        <div class="dashboard-icon">⚙️</div>
                        <div class="dashboard-info">
                            <h3>Admin Dashboard</h3>
                            <p>User management and system controls</p>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-item" onclick="window.open('/minimal/business', '_blank')">
                    <div class="dashboard-link">
                        <div class="dashboard-icon">📊</div>
                        <div class="dashboard-info">
                            <h3>Business Analytics</h3>
                            <p>KPIs and growth metrics</p>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-item" onclick="window.open('/minimal/nurture', '_blank')">
                    <div class="dashboard-link">
                        <div class="dashboard-icon">💬</div>
                        <div class="dashboard-info">
                            <h3>Nurture Sequences</h3>
                            <p>Message flows and engagement</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Minimal Dashboard v1.0 • Updated: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
</body>
</html>
    """
    return html_content

def get_minimal_admin_html():
    """Generate minimal admin dashboard"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Minimal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_minimal_css()}</style>
</head>
<body>
    <div class="header">
        <h1>Admin Dashboard</h1>
        <h2>System Administration</h2>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="card-header">User Statistics</div>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-value">65</div>
                    <div class="metric-label">Total Users</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value success">48</div>
                    <div class="metric-label">Active Today</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">12</div>
                    <div class="metric-label">New This Week</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value warning">5</div>
                    <div class="metric-label">Inactive</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">Recent Activity</div>
            <table class="table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Action</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>User_42</td>
                        <td>Completed Commitment</td>
                        <td>2 mins ago</td>
                        <td class="success">✓</td>
                    </tr>
                    <tr>
                        <td>User_15</td>
                        <td>Started Onboarding</td>
                        <td>15 mins ago</td>
                        <td class="success">✓</td>
                    </tr>
                    <tr>
                        <td>User_33</td>
                        <td>Joined Pod</td>
                        <td>1 hour ago</td>
                        <td class="success">✓</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <a href="/superadmin-minimal" style="color: #6b7280;">← Back to SuperAdmin</a>
    </div>
</body>
</html>
    """
    return html_content

def get_minimal_business_html():
    """Generate minimal business dashboard"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Business Analytics - Minimal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{get_minimal_css()}</style>
</head>
<body>
    <div class="header">
        <h1>Business Analytics</h1>
        <h2>Key Performance Indicators</h2>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="card-header">Revenue Metrics</div>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-value success">$12,450</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">$4,150</div>
                    <div class="metric-label">MRR</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value success">+23%</div>
                    <div class="metric-label">Growth Rate</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">$245</div>
                    <div class="metric-label">Avg LTV</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">Engagement Metrics</div>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-value">87%</div>
                    <div class="metric-label">Retention Rate</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">72%</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">4.8</div>
                    <div class="metric-label">Avg Rating</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">8.2%</div>
                    <div class="metric-label">Churn Rate</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <a href="/superadmin-minimal" style="color: #6b7280;">← Back to SuperAdmin</a>
    </div>
</body>
</html>
    """
    return html_content

def add_minimal_routes(app: FastAPI):
    """Add minimal dashboard routes to FastAPI app"""
    
    @app.get("/superadmin-minimal", response_class=HTMLResponse)
    async def minimal_superadmin():
        return get_minimal_superadmin_html()
    
    @app.get("/minimal/admin", response_class=HTMLResponse)
    async def minimal_admin():
        return get_minimal_admin_html()
    
    @app.get("/minimal/business", response_class=HTMLResponse)
    async def minimal_business():
        return get_minimal_business_html()

# Standalone server for testing
if __name__ == "__main__":
    import uvicorn
    
    app = FastAPI(title="Minimal Clean Dashboards")
    add_minimal_routes(app)
    
    print("🚀 Starting Minimal Dashboard Suite")
    print("📍 SuperAdmin: http://localhost:7002/superadmin-minimal")
    print("⚙️ Admin: http://localhost:7002/minimal/admin")
    print("📊 Business: http://localhost:7002/minimal/business")
    print("✨ Clean, minimal aesthetic inspired by Commodore output")
    
    uvicorn.run(app, host="0.0.0.0", port=7002)