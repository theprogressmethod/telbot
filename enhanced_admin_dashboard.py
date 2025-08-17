#!/usr/bin/env python3
"""
Enhanced Admin Dashboard with Business Intelligence Tab
Integrates behavioral analytics based on our 27.8% onboarding analysis
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from business_intelligence_dashboard import BusinessIntelligenceDashboard, create_business_intelligence_routes
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def get_enhanced_admin_dashboard_html():
    """Generate enhanced admin dashboard with retro design"""
    from retro_business_intelligence import get_retro_business_intelligence_html
    return get_retro_business_intelligence_html()

def get_enhanced_admin_dashboard_html_original():
    """Generate original enhanced admin dashboard HTML with Business Intelligence tab"""
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Method Admin Dashboard - Enhanced</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f7fa; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
            
            /* Tab Navigation */
            .tab-nav { display: flex; background: white; border-radius: 12px 12px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; overflow: hidden; }
            .tab-btn { flex: 1; padding: 20px; text-align: center; border: none; background: white; cursor: pointer; font-size: 1rem; font-weight: 600; color: #4a5568; transition: all 0.3s; border-bottom: 3px solid transparent; }
            .tab-btn:hover { background: #f7fafc; }
            .tab-btn.active { background: #4299e1; color: white; border-bottom-color: #2b6cb0; }
            
            /* Tab Content */
            .tab-content { display: none; background: white; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); padding: 30px; min-height: 600px; }
            .tab-content.active { display: block; }
            
            /* Business Intelligence Specific Styles */
            .bi-metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .bi-section { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; }
            .bi-section-header { background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; padding: 20px; }
            .bi-section-body { padding: 20px; }
            
            /* Enhanced Metric Cards */
            .metric-card { background: white; border-radius: 12px; padding: 25px; text-align: center; position: relative; overflow: hidden; }
            .metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
            
            .metric-card.critical::before { background: linear-gradient(90deg, #e53e3e, #c53030); }
            .metric-card.warning::before { background: linear-gradient(90deg, #d69e2e, #b7791f); }
            .metric-card.good::before { background: linear-gradient(90deg, #38a169, #2f855a); }
            .metric-card.excellent::before { background: linear-gradient(90deg, #3182ce, #2c5aa0); }
            
            .metric-value { font-size: 2.5rem; font-weight: bold; margin-bottom: 8px; }
            .metric-label { font-size: 1rem; color: #4a5568; margin-bottom: 10px; }
            .metric-insight { font-size: 0.875rem; color: #718096; font-style: italic; }
            .metric-target { font-size: 0.75rem; color: #a0aec0; margin-top: 8px; }
            
            /* Status Indicators */
            .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
            .status-critical { background: #e53e3e; }
            .status-warning { background: #d69e2e; }
            .status-good { background: #38a169; }
            .status-excellent { background: #3182ce; }
            
            /* Insights List */
            .insights-list { list-style: none; padding: 0; margin: 0; }
            .insights-list li { padding: 12px; margin-bottom: 8px; border-radius: 8px; background: #f7fafc; border-left: 4px solid #4299e1; }
            .insights-list li.critical { border-left-color: #e53e3e; background: #fed7d7; }
            .insights-list li.warning { border-left-color: #d69e2e; background: #faf089; }
            .insights-list li.good { border-left-color: #38a169; background: #c6f6d5; }
            
            /* Progress Bars */
            .progress-bar { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-top: 8px; }
            .progress-fill { height: 100%; transition: width 0.3s ease; }
            .progress-critical { background: linear-gradient(90deg, #e53e3e, #c53030); }
            .progress-warning { background: linear-gradient(90deg, #d69e2e, #b7791f); }
            .progress-good { background: linear-gradient(90deg, #38a169, #2f855a); }
            
            /* Charts Container */
            .chart-container { height: 300px; background: #f7fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #718096; margin-top: 20px; }
            
            /* Action Buttons */
            .action-button { background: #4299e1; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 0.875rem; margin: 5px; transition: all 0.2s; }
            .action-button:hover { background: #3182ce; transform: translateY(-1px); }
            .action-button.danger { background: #e53e3e; }
            .action-button.success { background: #38a169; }
            .action-button.warning { background: #d69e2e; }
            
            /* Loading States */
            .loading { display: flex; align-items: center; justify-content: center; height: 200px; color: #718096; }
            .loading::after { content: '...'; animation: loading 1s infinite; }
            @keyframes loading { 0%, 20% { content: '.'; } 40%, 60% { content: '..'; } 80%, 100% { content: '...'; } }
            
            /* Responsive */
            @media (max-width: 768px) {
                .tab-nav { flex-direction: column; }
                .bi-metrics-grid { grid-template-columns: 1fr; }
                .container { padding: 10px; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Progress Method Admin Dashboard</h1>
            <p>Complete system management with Business Intelligence</p>
            <div style="margin-top: 15px;">
                <button class="action-button" onclick="refreshAllData()">🔄 Refresh All</button>
                <button class="action-button success" onclick="exportMetrics()">📊 Export Metrics</button>
                <button class="action-button warning" onclick="showAlerts()">⚠️ Alerts</button>
            </div>
        </div>
        
        <div class="container">
            <!-- Enhanced Tab Navigation -->
            <div class="tab-nav">
                <button class="tab-btn active" onclick="showTab('business-intelligence')">📈 Business Intelligence</button>
                <button class="tab-btn" onclick="showTab('overview')">📊 Overview</button>
                <button class="tab-btn" onclick="showTab('pods')">🎯 Pods</button>
                <button class="tab-btn" onclick="showTab('users')">👥 Users</button>
                <button class="tab-btn" onclick="showTab('health')">🏥 System Health</button>
            </div>
            
            <!-- Business Intelligence Tab -->
            <div id="business-intelligence-tab" class="tab-content active">
                <h2 style="margin-top: 0; color: #2d3748;">📈 Business Intelligence Dashboard</h2>
                <p style="color: #718096; margin-bottom: 30px;">
                    Comprehensive behavioral analytics and business insights based on user engagement patterns.
                </p>
                
                <!-- Critical Metrics Overview -->
                <div class="bi-metrics-grid">
                    <div class="metric-card" id="onboarding-card">
                        <div class="metric-value" id="onboarding-rate">-</div>
                        <div class="metric-label">Onboarding Conversion</div>
                        <div class="metric-insight" id="onboarding-insight">Loading...</div>
                        <div class="metric-target">Target: 80%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="onboarding-progress" style="width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="completion-card">
                        <div class="metric-value" id="completion-rate">-</div>
                        <div class="metric-label">Commitment Completion</div>
                        <div class="metric-insight" id="completion-insight">Loading...</div>
                        <div class="metric-target">Target: 70%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="completion-progress" style="width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="retention-card">
                        <div class="metric-value" id="retention-rate">-</div>
                        <div class="metric-label">Week 1 Retention</div>
                        <div class="metric-insight" id="retention-insight">Loading...</div>
                        <div class="metric-target">Target: 60%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="retention-progress" style="width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="growth-card">
                        <div class="metric-value" id="growth-rate">-</div>
                        <div class="metric-label">Weekly Growth Rate</div>
                        <div class="metric-insight" id="growth-insight">Loading...</div>
                        <div class="metric-target">Target: >5%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="growth-progress" style="width: 0%;"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Detailed Analysis Sections -->
                <div class="bi-metrics-grid">
                    <!-- Onboarding Funnel Analysis -->
                    <div class="bi-section">
                        <div class="bi-section-header">
                            <h3 style="margin: 0;">🎯 Onboarding Funnel Analysis</h3>
                        </div>
                        <div class="bi-section-body">
                            <div id="onboarding-details">
                                <div class="loading">Loading onboarding data</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Behavioral Insights -->
                    <div class="bi-section">
                        <div class="bi-section-header">
                            <h3 style="margin: 0;">🧠 Behavioral Insights</h3>
                        </div>
                        <div class="bi-section-body">
                            <div id="behavioral-insights">
                                <div class="loading">Analyzing behavioral patterns</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Commitment Analytics -->
                    <div class="bi-section">
                        <div class="bi-section-header">
                            <h3 style="margin: 0;">📊 Commitment Analytics</h3>
                        </div>
                        <div class="bi-section-body">
                            <div id="commitment-analytics">
                                <div class="loading">Processing commitment data</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Growth Trends -->
                    <div class="bi-section">
                        <div class="bi-section-header">
                            <h3 style="margin: 0;">📈 Growth Trends</h3>
                        </div>
                        <div class="bi-section-body">
                            <div id="growth-trends">
                                <div class="loading">Calculating growth metrics</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Actionable Insights -->
                <div class="bi-section">
                    <div class="bi-section-header">
                        <h3 style="margin: 0;">💡 Actionable Insights & Recommendations</h3>
                    </div>
                    <div class="bi-section-body">
                        <ul class="insights-list" id="actionable-insights">
                            <li class="loading">Generating personalized insights...</li>
                        </ul>
                        <div style="margin-top: 20px;">
                            <button class="action-button" onclick="implementRecommendations()">🚀 Implement Priority Fixes</button>
                            <button class="action-button warning" onclick="exportInsights()">📋 Export Insights</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Existing tabs would go here -->
            <div id="overview-tab" class="tab-content">
                <h2>System Overview</h2>
                <p>Traditional system metrics and overview information.</p>
            </div>
            
            <div id="pods-tab" class="tab-content">
                <h2>Pod Management</h2>
                <p>Pod creation, management, and analytics.</p>
            </div>
            
            <div id="users-tab" class="tab-content">
                <h2>User Management</h2>
                <p>User administration and account management.</p>
            </div>
            
            <div id="health-tab" class="tab-content">
                <h2>System Health</h2>
                <p>System performance monitoring and health checks.</p>
            </div>
        </div>

        <script>
            // Business Intelligence Dashboard JavaScript
            let businessData = {};
            
            // Tab Management
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
                
                // Load data if business intelligence tab
                if (tabName === 'business-intelligence') {
                    loadBusinessIntelligenceData();
                }
            }
            
            // Load Business Intelligence Data
            async function loadBusinessIntelligenceData() {
                try {
                    const response = await fetch('/api/business-intelligence');
                    businessData = await response.json();
                    
                    updateMetricCards();
                    updateDetailedSections();
                    updateActionableInsights();
                } catch (error) {
                    console.error('Error loading business intelligence data:', error);
                    showErrorState();
                }
            }
            
            // Update Main Metric Cards
            function updateMetricCards() {
                const { onboarding_funnel, behavioral_insights, retention_analysis, growth_indicators } = businessData;
                
                // Onboarding Conversion
                updateMetricCard('onboarding', 
                    onboarding_funnel.conversion_rate + '%',
                    onboarding_funnel.health_status,
                    `${onboarding_funnel.users_with_commitments} of ${onboarding_funnel.total_users} users`,
                    onboarding_funnel.conversion_rate
                );
                
                // Completion Rate
                updateMetricCard('completion',
                    behavioral_insights.completion_rate + '%',
                    behavioral_insights.health_status,
                    `${behavioral_insights.completed_commitments} of ${behavioral_insights.total_commitments} completed`,
                    behavioral_insights.completion_rate
                );
                
                // Retention Rate
                updateMetricCard('retention',
                    retention_analysis.week_1_retention + '%',
                    retention_analysis.health_status,
                    `${retention_analysis.active_users.week_1} of ${retention_analysis.eligible_users.week_1} retained`,
                    retention_analysis.week_1_retention
                );
                
                // Growth Rate
                updateMetricCard('growth',
                    growth_indicators.growth_rate + '%',
                    growth_indicators.trend === 'growing' ? 'good' : growth_indicators.trend === 'stable' ? 'warning' : 'critical',
                    `${growth_indicators.last_7_days_signups} signups this week`,
                    Math.max(0, growth_indicators.growth_rate)
                );
            }
            
            function updateMetricCard(type, value, status, insight, progressValue) {
                document.getElementById(type + '-rate').textContent = value;
                document.getElementById(type + '-insight').textContent = insight;
                
                const card = document.getElementById(type + '-card');
                const progress = document.getElementById(type + '-progress');
                
                // Update card status
                card.className = 'metric-card ' + status;
                
                // Update progress bar
                progress.style.width = Math.min(100, progressValue) + '%';
                progress.className = 'progress-fill progress-' + status;
            }
            
            // Update Detailed Sections
            function updateDetailedSections() {
                updateOnboardingDetails();
                updateBehavioralInsights();
                updateCommitmentAnalytics();
                updateGrowthTrends();
            }
            
            function updateOnboardingDetails() {
                const data = businessData.onboarding_funnel;
                const html = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #2d3748;">${data.total_users}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Total Users</div>
                        </div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #2d3748;">${data.users_with_commitments}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Created Commitments</div>
                        </div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #2d3748;">${data.recent_signups}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Recent Signups (7 days)</div>
                        </div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #e53e3e;">${data.improvement_needed.toFixed(1)}%</div>
                            <div style="font-size: 0.875rem; color: #718096;">Improvement Needed</div>
                        </div>
                    </div>
                `;
                document.getElementById('onboarding-details').innerHTML = html;
            }
            
            function updateBehavioralInsights() {
                const data = businessData.behavioral_insights;
                const patterns = data.behavioral_patterns || [];
                
                const html = `
                    <div style="margin-bottom: 20px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                            <div>
                                <div style="font-size: 1.2rem; font-weight: bold;">${data.quick_completions}</div>
                                <div style="font-size: 0.875rem; color: #718096;">Quick Completions</div>
                            </div>
                            <div>
                                <div style="font-size: 1.2rem; font-weight: bold;">${data.avg_completion_hours}h</div>
                                <div style="font-size: 0.875rem; color: #718096;">Avg Completion Time</div>
                            </div>
                        </div>
                        <div style="font-weight: 600; margin-bottom: 10px;">Behavioral Patterns:</div>
                        ${patterns.map(pattern => `<div style="padding: 8px; background: #f7fafc; border-radius: 6px; margin-bottom: 5px; font-size: 0.875rem;">${pattern}</div>`).join('')}
                    </div>
                `;
                document.getElementById('behavioral-insights').innerHTML = html;
            }
            
            function updateCommitmentAnalytics() {
                const data = businessData.commitment_analytics;
                const dist = data.user_distribution || {};
                
                const html = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${data.active_users}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Active Users</div>
                        </div>
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${data.avg_commitments_per_user}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Avg Commitments/User</div>
                        </div>
                    </div>
                    <div style="font-weight: 600; margin-bottom: 10px;">User Distribution:</div>
                    <div style="font-size: 0.875rem;">
                        <div>No Commitments: ${dist.no_commitments || 0}</div>
                        <div>Light Users (1-3): ${dist.light_users || 0}</div>
                        <div>Active Users (4-10): ${dist.active_users || 0}</div>
                        <div>Power Users (10+): ${dist.power_users || 0}</div>
                    </div>
                `;
                document.getElementById('commitment-analytics').innerHTML = html;
            }
            
            function updateGrowthTrends() {
                const data = businessData.growth_indicators;
                
                const html = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${data.last_7_days_signups}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Last 7 Days</div>
                        </div>
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${data.prev_7_days_signups}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Previous 7 Days</div>
                        </div>
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${data.avg_daily_signups}</div>
                            <div style="font-size: 0.875rem; color: #718096;">Avg Daily Signups</div>
                        </div>
                        <div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: ${data.trend === 'growing' ? '#38a169' : data.trend === 'declining' ? '#e53e3e' : '#d69e2e'};">
                                ${data.trend.toUpperCase()}
                            </div>
                            <div style="font-size: 0.875rem; color: #718096;">Trend</div>
                        </div>
                    </div>
                `;
                document.getElementById('growth-trends').innerHTML = html;
            }
            
            // Update Actionable Insights
            function updateActionableInsights() {
                const insights = generateActionableInsights();
                const html = insights.map(insight => 
                    `<li class="${insight.priority}">${insight.text}</li>`
                ).join('');
                document.getElementById('actionable-insights').innerHTML = html;
            }
            
            function generateActionableInsights() {
                const insights = [];
                const { onboarding_funnel, behavioral_insights, retention_analysis, growth_indicators } = businessData;
                
                if (onboarding_funnel.conversion_rate < 50) {
                    insights.push({
                        priority: 'critical',
                        text: `🚨 CRITICAL: Only ${onboarding_funnel.conversion_rate}% onboarding conversion. Implement micro-commitment sequence immediately.`
                    });
                }
                
                if (behavioral_insights.completion_rate < 50) {
                    insights.push({
                        priority: 'critical', 
                        text: `⚠️ CRITICAL: ${behavioral_insights.completion_rate}% completion rate indicates commitments too difficult. Deploy progressive difficulty system.`
                    });
                }
                
                if (retention_analysis.week_1_retention < 40) {
                    insights.push({
                        priority: 'warning',
                        text: `📉 Week 1 retention at ${retention_analysis.week_1_retention}%. Implement shame spiral prevention system.`
                    });
                }
                
                if (growth_indicators.growth_rate < 0) {
                    insights.push({
                        priority: 'warning',
                        text: `📈 Negative growth rate (${growth_indicators.growth_rate}%). Review user acquisition strategy.`
                    });
                }
                
                if (behavioral_insights.quick_completions > behavioral_insights.completed_commitments * 0.8) {
                    insights.push({
                        priority: 'good',
                        text: `✅ Strong quick completion pattern. Leverage this in onboarding sequence design.`
                    });
                }
                
                return insights;
            }
            
            // Error Handling
            function showErrorState() {
                document.querySelectorAll('.loading').forEach(el => {
                    el.innerHTML = '<span style="color: #e53e3e;">⚠️ Error loading data. Please refresh.</span>';
                });
            }
            
            // Action Functions
            function refreshAllData() {
                if (document.getElementById('business-intelligence-tab').classList.contains('active')) {
                    loadBusinessIntelligenceData();
                }
            }
            
            function exportMetrics() {
                const dataStr = JSON.stringify(businessData, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `business-intelligence-${new Date().toISOString().split('T')[0]}.json`;
                link.click();
            }
            
            function implementRecommendations() {
                alert('Implementation wizard coming soon! Priority fixes will be automatically applied.');
            }
            
            function exportInsights() {
                const insights = generateActionableInsights();
                const text = insights.map(i => `${i.priority.toUpperCase()}: ${i.text}`).join('\\n\\n');
                
                const textBlob = new Blob([text], {type: 'text/plain'});
                const url = URL.createObjectURL(textBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `actionable-insights-${new Date().toISOString().split('T')[0]}.txt`;
                link.click();
            }
            
            function showAlerts() {
                const { onboarding_funnel, behavioral_insights } = businessData;
                let alerts = [];
                
                if (onboarding_funnel.conversion_rate < 30) {
                    alerts.push('🚨 CRITICAL: Onboarding conversion crisis');
                }
                if (behavioral_insights.completion_rate < 50) {
                    alerts.push('⚠️ HIGH: Commitment completion needs immediate attention');
                }
                
                alert(alerts.length > 0 ? alerts.join('\\n') : '✅ No critical alerts');
            }
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadBusinessIntelligenceData();
            });
        </script>
    </body>
    </html>
    """

def add_business_intelligence_routes(app: FastAPI):
    """Add the enhanced admin dashboard and BI routes to FastAPI app"""
    
    # Create BI routes
    create_business_intelligence_routes(app)
    
    @app.get("/admin/dashboard-enhanced", response_class=HTMLResponse)
    async def enhanced_admin_dashboard():
        """Enhanced admin dashboard with Business Intelligence tab"""
        return get_enhanced_admin_dashboard_html()

if __name__ == "__main__":
    print("Enhanced Admin Dashboard with Business Intelligence")
    print("Features:")
    print("- Onboarding conversion analysis (27.8% problem detection)")
    print("- Behavioral pattern insights")
    print("- Commitment completion analytics") 
    print("- Retention and growth metrics")
    print("- Actionable recommendations")
    print("- Real-time data updates")
    print("- Export capabilities")