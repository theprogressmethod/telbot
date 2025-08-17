#!/usr/bin/env python3
"""
Retro Business Intelligence Dashboard
Miami Vice + Commodore 64 aesthetic with behavioral analytics
"""

from retro_styles import get_retro_css, get_retro_js

def get_retro_business_intelligence_html():
    """Generate retro business intelligence dashboard"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>BUSINESS_INTELLIGENCE.EXE - BEHAVIORAL ANALYTICS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {get_retro_css()}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 6px;
            margin: 6px 0;
        }}
        
        .chart-container {{
            background: #000a11;
            border: 1px solid #333;
            border-radius: 2px;
            padding: 6px;
            margin: 6px 0;
            min-height: 120px;
        }}
        
        .behavior-pattern {{
            background: #001122;
            border-left: 2px solid #ff006b;
            padding: 4px;
            margin: 3px 0;
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="terminal">
        <div class="screen">
            <div class="header">
                <h1>BUSINESS_INTELLIGENCE.EXE</h1>
                <div style="color: #ff006b; font-size: 12px;">BEHAVIORAL ANALYTICS CORE v2.0</div>
            </div>
            
            <div class="ascii-border">
═══════════════════════════════════════════════════════════════════════════════
            </div>
            
            <div class="status-bar">
                <span>STATUS: <span style="color: #00ff88;">OPERATIONAL</span></span>
                <span>DB: <span style="color: #3a86ff;">CONNECTED</span></span>
                <span>ANALYTICS: <span style="color: #ff006b;">CRITICAL</span></span>
                <span>TIME: <span id="time">--:--:--</span></span>
                <span class="blink">█</span>
            </div>
            
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('overview')">OVERVIEW</button>
                <button class="tab-btn" onclick="showTab('onboarding')">ONBOARDING</button>
                <button class="tab-btn" onclick="showTab('behavior')">BEHAVIOR</button>
                <button class="tab-btn" onclick="showTab('retention')">RETENTION</button>
                <button class="tab-btn" onclick="showTab('growth')">GROWTH</button>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content active">
                <div class="data-section">
                    <div class="data-header">CRITICAL METRICS OVERVIEW</div>
                    <div class="data-content">
                        <div class="metric-grid" id="overview-metrics">
                            <div class="loading">LOADING METRICS...</div>
                        </div>
                    </div>
                </div>
                
                <div class="data-section">
                    <div class="data-header">BEHAVIORAL INTELLIGENCE STATUS</div>
                    <div class="data-content" id="system-status">
                        <div class="loading">ANALYZING BEHAVIORAL PATTERNS...</div>
                    </div>
                </div>
            </div>
            
            <!-- Onboarding Tab -->
            <div id="onboarding-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">ONBOARDING CONVERSION ANALYSIS</div>
                    <div class="data-content">
                        <div class="metric-grid" id="onboarding-metrics">
                            <div class="loading">LOADING ONBOARDING DATA...</div>
                        </div>
                        <div id="onboarding-insights"></div>
                    </div>
                </div>
            </div>
            
            <!-- Behavior Tab -->
            <div id="behavior-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">BEHAVIORAL PATTERN ANALYSIS</div>
                    <div class="data-content">
                        <div class="metric-grid" id="behavior-metrics">
                            <div class="loading">LOADING BEHAVIORAL DATA...</div>
                        </div>
                        <div id="behavior-patterns"></div>
                    </div>
                </div>
            </div>
            
            <!-- Retention Tab -->
            <div id="retention-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">USER RETENTION ANALYSIS</div>
                    <div class="data-content">
                        <div class="metric-grid" id="retention-metrics">
                            <div class="loading">LOADING RETENTION DATA...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Growth Tab -->
            <div id="growth-tab" class="tab-content">
                <div class="data-section">
                    <div class="data-header">GROWTH INDICATORS</div>
                    <div class="data-content">
                        <div class="metric-grid" id="growth-metrics">
                            <div class="loading">LOADING GROWTH DATA...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
BUSINESS_INTELLIGENCE.EXE v2.0 © 2025 // LAST_UPDATE: <span id="footer-time">--:--:--</span>
            </div>
        </div>
    </div>

    <script>
        {get_retro_js()}
        
        // Load business intelligence data
        async function loadBusinessIntelligence() {{
            try {{
                const response = await fetch('/api/business-intelligence');
                const data = await response.json();
                
                updateOverviewMetrics(data);
                updateOnboardingData(data);
                updateBehaviorData(data);
                updateRetentionData(data);
                updateGrowthData(data);
                updateSystemStatus(data);
                
            }} catch (error) {{
                console.error('Error loading BI data:', error);
                showError('overview-metrics', 'FAILED TO LOAD DATA');
            }}
        }}
        
        function updateOverviewMetrics(data) {{
            const onboarding = data.onboarding_funnel || {{}};
            const behavior = data.behavioral_insights || {{}};
            const commitment = data.commitment_intelligence || {{}};
            
            const html = `
                <div class="metric-card ${{getHealthClass(onboarding.health_status)}}">
                    <div class="metric-value">${{onboarding.conversion_rate || '0'}}%</div>
                    <div class="metric-label">CONVERSION</div>
                </div>
                <div class="metric-card ${{getHealthClass(behavior.health_status)}}">
                    <div class="metric-value">${{behavior.completion_rate || '0'}}%</div>
                    <div class="metric-label">COMPLETION</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{commitment.total_commitments || '0'}}</div>
                    <div class="metric-label">COMMITMENTS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{commitment.active_users || '0'}}</div>
                    <div class="metric-label">ACTIVE_USERS</div>
                </div>
            `;
            document.getElementById('overview-metrics').innerHTML = html;
        }}
        
        function updateOnboardingData(data) {{
            const onboarding = data.onboarding_funnel || {{}};
            
            const html = `
                <div class="metric-card ${{getHealthClass(onboarding.health_status)}}">
                    <div class="metric-value">${{onboarding.conversion_rate || '0'}}%</div>
                    <div class="metric-label">CURRENT_RATE</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{onboarding.target_rate || '80'}}%</div>
                    <div class="metric-label">TARGET_RATE</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{onboarding.users_with_commitments || '0'}}</div>
                    <div class="metric-label">CONVERTED</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{onboarding.total_users || '0'}}</div>
                    <div class="metric-label">TOTAL_USERS</div>
                </div>
            `;
            document.getElementById('onboarding-metrics').innerHTML = html;
            
            const improvement = onboarding.improvement_needed || 0;
            const insights = `
                <div class="behavior-pattern">
                    CRITICAL: Conversion rate at ${{onboarding.conversion_rate}}% (Target: ${{onboarding.target_rate}}%)
                </div>
                <div class="behavior-pattern">
                    IMPROVEMENT NEEDED: +${{improvement.toFixed(1)}}% to reach target
                </div>
                <div class="behavior-pattern">
                    SUPERIOR ONBOARDING SYSTEM: Ready for deployment
                </div>
            `;
            document.getElementById('onboarding-insights').innerHTML = insights;
        }}
        
        function updateBehaviorData(data) {{
            const behavior = data.behavioral_insights || {{}};
            
            const html = `
                <div class="metric-card ${{getHealthClass(behavior.health_status)}}">
                    <div class="metric-value">${{behavior.completion_rate || '0'}}%</div>
                    <div class="metric-label">COMPLETION</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{behavior.avg_completion_hours || '0'}}</div>
                    <div class="metric-label">AVG_HOURS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{behavior.completed_commitments || '0'}}</div>
                    <div class="metric-label">COMPLETED</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{behavior.quick_completions || '0'}}</div>
                    <div class="metric-label">QUICK_WINS</div>
                </div>
            `;
            document.getElementById('behavior-metrics').innerHTML = html;
            
            const patterns = behavior.behavioral_patterns || [];
            const patternsHtml = patterns.map(pattern => 
                `<div class="behavior-pattern">${{pattern}}</div>`
            ).join('');
            document.getElementById('behavior-patterns').innerHTML = patternsHtml;
        }}
        
        function updateRetentionData(data) {{
            const retention = data.retention_analysis || {{}};
            
            const html = `
                <div class="metric-card warning">
                    <div class="metric-value">${{retention.week_1_retention || 'N/A'}}</div>
                    <div class="metric-label">WEEK_1</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">--</div>
                    <div class="metric-label">WEEK_4</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">--</div>
                    <div class="metric-label">MONTH_3</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">--</div>
                    <div class="metric-label">COHORT</div>
                </div>
            `;
            document.getElementById('retention-metrics').innerHTML = html;
        }}
        
        function updateGrowthData(data) {{
            const growth = data.growth_indicators || {{}};
            
            const html = `
                <div class="metric-card">
                    <div class="metric-value">${{growth.last_7_days_signups || '0'}}</div>
                    <div class="metric-label">LAST_7D</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{growth.growth_rate || '0'}}%</div>
                    <div class="metric-label">GROWTH_RATE</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{growth.avg_daily_signups || '0'}}</div>
                    <div class="metric-label">DAILY_AVG</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${{growth.total_last_30_days || '0'}}</div>
                    <div class="metric-label">MONTH_TOTAL</div>
                </div>
            `;
            document.getElementById('growth-metrics').innerHTML = html;
        }}
        
        function updateSystemStatus(data) {{
            const health = data.system_health || {{}};
            
            const html = `
                <div class="behavior-pattern">
                    SYSTEM_HEALTH: ${{health.health_score || '0'}}% (${{health.status || 'unknown'}})
                </div>
                <div class="behavior-pattern">
                    DATABASE_RESPONSE: ${{health.database_response_time || '0'}}ms
                </div>
                <div class="behavior-pattern">
                    LAST_CHECK: ${{health.last_check || 'unknown'}}
                </div>
            `;
            document.getElementById('system-status').innerHTML = html;
        }}
        
        function getHealthClass(status) {{
            if (status === 'critical') return 'critical';
            if (status === 'warning') return 'warning';
            if (status === 'good') return 'good';
            return '';
        }}
        
        // Initialize
        loadBusinessIntelligence();
        setInterval(loadBusinessIntelligence, 30000);
    </script>
</body>
</html>
    """
    
    return html_content