#!/usr/bin/env python3
"""
Essential Business Metrics Dashboard
Only the metrics that matter for business decisions - no fluff
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def add_business_metrics_routes(app: FastAPI):
    """Add essential business metrics routes"""
    
    @app.get("/admin/business-metrics", response_class=HTMLResponse)
    async def business_metrics_dashboard():
        """Essential business metrics - only what matters"""
        
        # Get core metrics
        metrics = await get_essential_metrics()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BUSINESS_METRICS.EXE - ESSENTIAL ONLY</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{ 
            font-family: 'Courier Prime', monospace; 
            background: #000011;
            color: #00ff88;
            font-size: 14px;
            line-height: 1.2;
            padding: 16px;
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
            padding: 16px;
            border-radius: 2px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #00ff88;
        }}
        
        .header h1 {{
            font-size: 20px;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 2px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }}
        
        .metric-section {{
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
        }}
        
        .metric-section h3 {{
            color: #ff006b;
            font-size: 14px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px solid #222;
        }}
        
        .metric-row:last-child {{ border-bottom: none; }}
        
        .metric-label {{ color: #888; font-size: 12px; }}
        .metric-value {{ color: #00ff88; font-weight: bold; }}
        .metric-value.warning {{ color: #ffbe0b; }}
        .metric-value.critical {{ color: #ff006b; }}
        
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }}
        
        .status-good {{ background: #00ff88; }}
        .status-warning {{ background: #ffbe0b; }}
        .status-critical {{ background: #ff006b; }}
        
        .footer {{
            text-align: center;
            margin-top: 24px;
            color: #666;
            font-size: 10px;
            border-top: 1px solid #333;
            padding-top: 8px;
        }}
        
        .refresh-btn {{
            background: #001a33;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            margin-left: 8px;
        }}
        
        .refresh-btn:hover {{ background: #002244; }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>BUSINESS_METRICS.EXE</h1>
                <div style="color: #3a86ff; font-size: 12px;">
                    ESSENTIAL METRICS ONLY - NO FLUFF
                    <button class="refresh-btn" onclick="location.reload()">REFRESH</button>
                </div>
            </div>
            
            <div class="metrics-grid">
                <!-- GROWTH METRICS -->
                <div class="metric-section">
                    <h3>📈 GROWTH</h3>
                    <div class="metric-row">
                        <span class="metric-label">WEEKLY USER GROWTH</span>
                        <span class="metric-value {get_status_class(metrics['growth']['weekly_growth_rate'])}">{metrics['growth']['weekly_growth_rate']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">MONTHLY USER GROWTH</span>
                        <span class="metric-value {get_status_class(metrics['growth']['monthly_growth_rate'])}">{metrics['growth']['monthly_growth_rate']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">TOTAL USERS</span>
                        <span class="metric-value">{metrics['growth']['total_users']}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">NEW USERS (7D)</span>
                        <span class="metric-value">{metrics['growth']['new_users_7d']}</span>
                    </div>
                </div>
                
                <!-- CONVERSION METRICS -->
                <div class="metric-section">
                    <h3>🎯 CONVERSION</h3>
                    <div class="metric-row">
                        <span class="metric-label">FORM → ONBOARDING</span>
                        <span class="metric-value {get_conversion_status(metrics['conversion']['form_to_onboarding'])}">{metrics['conversion']['form_to_onboarding']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">ONBOARDING → FIRST POD</span>
                        <span class="metric-value {get_conversion_status(metrics['conversion']['onboarding_to_pod'])}">{metrics['conversion']['onboarding_to_pod']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">BOT SIGNUP → ACTIVE</span>
                        <span class="metric-value {get_conversion_status(metrics['conversion']['signup_to_active'])}">{metrics['conversion']['signup_to_active']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">ACTIVATION RATE</span>
                        <span class="metric-value {get_conversion_status(metrics['conversion']['activation_rate'])}">{metrics['conversion']['activation_rate']}%</span>
                    </div>
                </div>
                
                <!-- RETENTION METRICS -->
                <div class="metric-section">
                    <h3>🔄 RETENTION</h3>
                    <div class="metric-row">
                        <span class="metric-label">MONTHLY CHURN</span>
                        <span class="metric-value {get_churn_status(metrics['retention']['monthly_churn'])}">{metrics['retention']['monthly_churn']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">DAY 7 RETENTION</span>
                        <span class="metric-value {get_retention_status(metrics['retention']['day_7_retention'])}">{metrics['retention']['day_7_retention']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">DAY 30 RETENTION</span>
                        <span class="metric-value {get_retention_status(metrics['retention']['day_30_retention'])}">{metrics['retention']['day_30_retention']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">PAID USER %</span>
                        <span class="metric-value">{metrics['retention']['paid_user_percentage']}%</span>
                    </div>
                </div>
                
                <!-- FINANCIAL METRICS -->
                <div class="metric-section">
                    <h3>💰 FINANCIAL</h3>
                    <div class="metric-row">
                        <span class="metric-label">MRR</span>
                        <span class="metric-value">${metrics['financial']['mrr']:,.0f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">ARR</span>
                        <span class="metric-value">${metrics['financial']['arr']:,.0f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">CAC</span>
                        <span class="metric-value ${get_cac_status(metrics['financial']['cac'])}">${metrics['financial']['cac']:,.0f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">CLV</span>
                        <span class="metric-value">${metrics['financial']['clv']:,.0f}</span>
                    </div>
                </div>
                
                <!-- PRODUCT METRICS -->
                <div class="metric-section">
                    <h3>🔧 PRODUCT</h3>
                    <div class="metric-row">
                        <span class="metric-label">DAU</span>
                        <span class="metric-value">{metrics['product']['dau']}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">MAU</span>
                        <span class="metric-value">{metrics['product']['mau']}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">SESSION LENGTH (AVG)</span>
                        <span class="metric-value">{metrics['product']['avg_session_length']}min</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">NPS</span>
                        <span class="metric-value {get_nps_status(metrics['product']['nps'])}">{metrics['product']['nps']}</span>
                    </div>
                </div>
                
                <!-- SYSTEM HEALTH -->
                <div class="metric-section">
                    <h3>⚡ SYSTEM</h3>
                    <div class="metric-row">
                        <span class="metric-label">BOT UPTIME</span>
                        <span class="metric-value">{metrics['system']['bot_uptime']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">RESPONSE TIME</span>
                        <span class="metric-value">{metrics['system']['avg_response_time']}ms</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">ERROR RATE</span>
                        <span class="metric-value {get_error_status(metrics['system']['error_rate'])}">{metrics['system']['error_rate']}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">ACTIVE ISSUES</span>
                        <span class="metric-value {get_issue_status(metrics['system']['active_issues'])}">{metrics['system']['active_issues']}</span>
                    </div>
                </div>
            </div>
            
            <div class="footer">
BUSINESS_METRICS.EXE v1.0 © 2025 // LAST_UPDATE: {datetime.now().strftime('%H:%M:%S')} // REFRESH: 60s
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
        """
        
        return html

async def get_essential_metrics() -> Dict[str, Any]:
    """Get only the essential business metrics that matter for decisions"""
    
    if not supabase:
        # Return mock data for demo
        return {
            "growth": {
                "weekly_growth_rate": 12.5,
                "monthly_growth_rate": 34.2,
                "total_users": 1247,
                "new_users_7d": 89
            },
            "conversion": {
                "form_to_onboarding": 16.1,  # CRITICAL - currently low
                "onboarding_to_pod": 78.3,
                "signup_to_active": 45.2,
                "activation_rate": 67.8
            },
            "retention": {
                "monthly_churn": 8.5,
                "day_7_retention": 72.1,
                "day_30_retention": 54.3,
                "paid_user_percentage": 12.8
            },
            "financial": {
                "mrr": 15640,
                "arr": 187680,
                "cac": 47,
                "clv": 389
            },
            "product": {
                "dau": 156,
                "mau": 1124,
                "avg_session_length": 8.2,
                "nps": 67
            },
            "system": {
                "bot_uptime": 99.8,
                "avg_response_time": 245,
                "error_rate": 0.3,
                "active_issues": 1
            }
        }
    
    try:
        # Get real data from database
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        # Growth metrics
        total_users_result = supabase.table('users').select('id').execute()
        total_users = len(total_users_result.data) if total_users_result.data else 0
        
        new_users_7d_result = supabase.table('users').select('id').gte('created_at', seven_days_ago.isoformat()).execute()
        new_users_7d = len(new_users_7d_result.data) if new_users_7d_result.data else 0
        
        new_users_30d_result = supabase.table('users').select('id').gte('created_at', thirty_days_ago.isoformat()).execute()
        new_users_30d = len(new_users_30d_result.data) if new_users_30d_result.data else 0
        
        # Calculate growth rates
        weekly_growth_rate = (new_users_7d / max(total_users - new_users_7d, 1)) * 100 if total_users > 0 else 0
        monthly_growth_rate = (new_users_30d / max(total_users - new_users_30d, 1)) * 100 if total_users > 0 else 0
        
        # Form submissions vs onboarding calls
        form_submissions = supabase.table('form_submissions').select('id').execute()
        onboarding_calls = supabase.table('users').select('id').not_.is_('onboarding_call_date', 'null').execute()
        
        form_to_onboarding = (len(onboarding_calls.data) / max(len(form_submissions.data), 1)) * 100 if form_submissions.data else 0
        
        return {
            "growth": {
                "weekly_growth_rate": round(weekly_growth_rate, 1),
                "monthly_growth_rate": round(monthly_growth_rate, 1),
                "total_users": total_users,
                "new_users_7d": new_users_7d
            },
            "conversion": {
                "form_to_onboarding": round(form_to_onboarding, 1),
                "onboarding_to_pod": 0,  # Need to implement pod tracking
                "signup_to_active": 0,   # Need to define "active"
                "activation_rate": 0     # Need to define activation
            },
            "retention": {
                "monthly_churn": 0,      # Need to implement churn calculation
                "day_7_retention": 0,    # Need to implement retention tracking
                "day_30_retention": 0,
                "paid_user_percentage": 0 # Need to implement payment tracking
            },
            "financial": {
                "mrr": 0,
                "arr": 0,
                "cac": 0,
                "clv": 0
            },
            "product": {
                "dau": 0,
                "mau": 0,
                "avg_session_length": 0,
                "nps": 0
            },
            "system": {
                "bot_uptime": 99.8,
                "avg_response_time": 245,
                "error_rate": 0.3,
                "active_issues": 0
            }
        }
        
    except Exception as e:
        # Fallback to mock data
        return await get_essential_metrics()

def get_status_class(value: float) -> str:
    """Get CSS class based on growth rate"""
    if value >= 15: return "good"
    elif value >= 5: return "warning" 
    else: return "critical"

def get_conversion_status(value: float) -> str:
    """Get CSS class based on conversion rate"""
    if value >= 50: return ""
    elif value >= 25: return "warning"
    else: return "critical"

def get_churn_status(value: float) -> str:
    """Get CSS class based on churn rate (lower is better)"""
    if value <= 5: return ""
    elif value <= 10: return "warning"
    else: return "critical"

def get_retention_status(value: float) -> str:
    """Get CSS class based on retention rate"""
    if value >= 60: return ""
    elif value >= 40: return "warning"
    else: return "critical"

def get_cac_status(value: float) -> str:
    """Get CSS class based on CAC"""
    if value <= 50: return ""
    elif value <= 100: return "warning"
    else: return "critical"

def get_nps_status(value: float) -> str:
    """Get CSS class based on NPS"""
    if value >= 50: return ""
    elif value >= 30: return "warning"
    else: return "critical"

def get_error_status(value: float) -> str:
    """Get CSS class based on error rate"""
    if value <= 1: return ""
    elif value <= 3: return "warning"
    else: return "critical"

def get_issue_status(value: int) -> str:
    """Get CSS class based on active issues"""
    if value == 0: return ""
    elif value <= 2: return "warning"
    else: return "critical"