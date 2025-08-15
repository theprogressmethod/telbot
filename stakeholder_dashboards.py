#!/usr/bin/env python3
"""
Progress Method - Stakeholder-Specific Dashboards
Custom dashboards tailored for different user roles and stakeholders
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class StakeholderType(Enum):
    EXECUTIVE = "executive"
    PRODUCT_MANAGER = "product_manager"
    DEVELOPER = "developer"
    SUPPORT = "support"
    USER = "user"

class DashboardWidget(Enum):
    KPI_CARD = "kpi_card"
    TREND_CHART = "trend_chart"
    GAUGE = "gauge"
    TABLE = "table"
    ALERT_LIST = "alert_list"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"

@dataclass
class DashboardConfig:
    stakeholder: StakeholderType
    title: str
    description: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int = 300  # seconds
    access_level: str = "admin"

class StakeholderDashboards:
    """Generate role-specific dashboards for different stakeholders"""
    
    def __init__(self, monitor_system, metrics_system, alerting_system):
        self.monitor = monitor_system
        self.metrics = metrics_system
        self.alerting = alerting_system
        self.dashboard_configs = self._setup_dashboard_configs()
    
    def _setup_dashboard_configs(self) -> Dict[StakeholderType, DashboardConfig]:
        """Setup dashboard configurations for each stakeholder type"""
        
        return {
            StakeholderType.EXECUTIVE: DashboardConfig(
                stakeholder=StakeholderType.EXECUTIVE,
                title="Executive Dashboard",
                description="High-level business metrics and KPIs",
                widgets=[
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Monthly Active Users",
                        "metric": "mau",
                        "format": "number",
                        "trend": True,
                        "size": "large"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Platform Health Score",
                        "metric": "platform_health_score",
                        "format": "percentage",
                        "threshold": {"warning": 70, "critical": 50},
                        "size": "large"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "User Growth Rate",
                        "metric": "user_growth_rate",
                        "format": "percentage",
                        "trend": True,
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Monthly Completion Rate",
                        "metric": "monthly_completion_rate",
                        "format": "percentage",
                        "target": 60.0,
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.TREND_CHART.value,
                        "title": "User Engagement Trends",
                        "metrics": ["dau", "wau", "user_retention_rate"],
                        "period": "30d",
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.ALERT_LIST.value,
                        "title": "Business Impact Alerts",
                        "filter": {"severity": ["critical", "emergency"], "category": "business"},
                        "size": "medium"
                    }
                ],
                refresh_interval=600,  # 10 minutes
                access_level="executive"
            ),
            
            StakeholderType.PRODUCT_MANAGER: DashboardConfig(
                stakeholder=StakeholderType.PRODUCT_MANAGER,
                title="Product Manager Dashboard",
                description="Feature usage, user behavior, and product analytics",
                widgets=[
                    {
                        "type": DashboardWidget.FUNNEL.value,
                        "title": "User Onboarding Funnel",
                        "stages": ["registration", "first_commitment", "completion", "retention"],
                        "size": "large"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Feature Discovery Rate",
                        "metric": "feature_discovery_rate",
                        "format": "percentage",
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "SMART Goal Adoption",
                        "metric": "smart_goal_adoption",
                        "format": "percentage",
                        "threshold": {"warning": 60},
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.TABLE.value,
                        "title": "Feature Usage Stats",
                        "columns": ["Feature", "Usage", "Success Rate", "Trend"],
                        "data_source": "feature_analytics",
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.HEATMAP.value,
                        "title": "User Activity Heatmap",
                        "metric": "user_activity",
                        "dimensions": ["hour", "day_of_week"],
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Pod Adoption Rate",
                        "metric": "pod_membership_rate",
                        "format": "percentage",
                        "size": "small"
                    }
                ],
                refresh_interval=300,  # 5 minutes
                access_level="admin"
            ),
            
            StakeholderType.DEVELOPER: DashboardConfig(
                stakeholder=StakeholderType.DEVELOPER,
                title="Developer Dashboard", 
                description="System performance, errors, and technical metrics",
                widgets=[
                    {
                        "type": DashboardWidget.GAUGE.value,
                        "title": "System Health",
                        "metric": "system_health_percentage",
                        "min": 0,
                        "max": 100,
                        "threshold": {"warning": 70, "critical": 50},
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "API Response Time",
                        "metric": "avg_response_time",
                        "format": "milliseconds",
                        "threshold": {"warning": 500, "critical": 1000},
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "AI Success Rate",
                        "metric": "ai_success_rate",
                        "format": "percentage",
                        "threshold": {"warning": 80, "critical": 60},
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.TREND_CHART.value,
                        "title": "Error Rates",
                        "metrics": ["database_errors", "api_errors", "ai_errors"],
                        "period": "24h",
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.TABLE.value,
                        "title": "Test Results",
                        "columns": ["Test Suite", "Status", "Duration", "Last Run"],
                        "data_source": "test_results",
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.ALERT_LIST.value,
                        "title": "System Alerts",
                        "filter": {"category": ["system", "infrastructure"]},
                        "size": "medium"
                    }
                ],
                refresh_interval=120,  # 2 minutes
                access_level="admin"
            ),
            
            StakeholderType.SUPPORT: DashboardConfig(
                stakeholder=StakeholderType.SUPPORT,
                title="Support Dashboard",
                description="User issues, system status, and support metrics",
                widgets=[
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "System Status",
                        "metric": "system_status",
                        "format": "status",
                        "size": "large"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Users Affected by Issues",
                        "metric": "affected_users",
                        "format": "number",
                        "threshold": {"warning": 1, "critical": 5},
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Average Response Time",
                        "metric": "avg_response_time",
                        "format": "milliseconds",
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.TABLE.value,
                        "title": "Recent User Activity",
                        "columns": ["User", "Last Action", "Status", "Issues"],
                        "data_source": "user_activity",
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.ALERT_LIST.value,
                        "title": "Active Issues",
                        "filter": {"status": ["active", "acknowledged"]},
                        "size": "full"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Feature Availability",
                        "metric": "feature_availability",
                        "format": "percentage",
                        "threshold": {"warning": 95, "critical": 90},
                        "size": "small"
                    }
                ],
                refresh_interval=180,  # 3 minutes
                access_level="support"
            ),
            
            StakeholderType.USER: DashboardConfig(
                stakeholder=StakeholderType.USER,
                title="System Status",
                description="Public system status and service health",
                widgets=[
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Service Status",
                        "metric": "service_status",
                        "format": "status",
                        "size": "large"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Response Time",
                        "metric": "avg_response_time",
                        "format": "milliseconds",
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.KPI_CARD.value,
                        "title": "Uptime",
                        "metric": "uptime_percentage",
                        "format": "percentage",
                        "size": "medium"
                    },
                    {
                        "type": DashboardWidget.TABLE.value,
                        "title": "Service Components",
                        "columns": ["Component", "Status", "Last Updated"],
                        "data_source": "component_status",
                        "size": "full"
                    }
                ],
                refresh_interval=300,  # 5 minutes
                access_level="public"
            )
        }
    
    async def generate_dashboard_html(self, stakeholder: StakeholderType, data: Dict[str, Any]) -> str:
        """Generate HTML dashboard for specific stakeholder"""
        
        config = self.dashboard_configs.get(stakeholder)
        if not config:
            return self._generate_error_dashboard(f"Dashboard not found for {stakeholder.value}")
        
        return await self._render_dashboard(config, data)
    
    async def _render_dashboard(self, config: DashboardConfig, data: Dict[str, Any]) -> str:
        """Render dashboard HTML from configuration"""
        
        # Get dashboard theme based on stakeholder
        theme = self._get_dashboard_theme(config.stakeholder)
        
        # Render widgets
        widgets_html = ""
        for widget_config in config.widgets:
            widget_html = await self._render_widget(widget_config, data)
            widgets_html += widget_html
        
        # Dashboard HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.title} - Progress Method</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="refresh" content="{config.refresh_interval}">
            <style>
                {self._get_dashboard_css(theme)}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div class="dashboard-container">
                <header class="dashboard-header">
                    <h1>📊 {config.title}</h1>
                    <p>{config.description}</p>
                    <div class="header-meta">
                        <span>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        <span>•</span>
                        <span>Auto-refresh: {config.refresh_interval//60}min</span>
                        <button onclick="location.reload()" class="refresh-btn">🔄 Refresh</button>
                    </div>
                </header>
                
                <main class="dashboard-content">
                    {widgets_html}
                </main>
                
                <footer class="dashboard-footer">
                    <p>Progress Method Monitoring • {config.stakeholder.value.replace('_', ' ').title()} Dashboard</p>
                </footer>
            </div>
            
            <script>
                {self._get_dashboard_js()}
            </script>
        </body>
        </html>
        """
        
        return html
    
    async def _render_widget(self, widget_config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render individual widget HTML"""
        
        widget_type = widget_config.get("type")
        title = widget_config.get("title", "Widget")
        size = widget_config.get("size", "medium")
        
        if widget_type == DashboardWidget.KPI_CARD.value:
            return self._render_kpi_card(widget_config, data)
        elif widget_type == DashboardWidget.TREND_CHART.value:
            return self._render_trend_chart(widget_config, data)
        elif widget_type == DashboardWidget.GAUGE.value:
            return self._render_gauge(widget_config, data)
        elif widget_type == DashboardWidget.TABLE.value:
            return self._render_table(widget_config, data)
        elif widget_type == DashboardWidget.ALERT_LIST.value:
            return self._render_alert_list(widget_config, data)
        elif widget_type == DashboardWidget.HEATMAP.value:
            return self._render_heatmap(widget_config, data)
        elif widget_type == DashboardWidget.FUNNEL.value:
            return self._render_funnel(widget_config, data)
        else:
            return f'<div class="widget widget-{size}"><h3>{title}</h3><p>Unknown widget type: {widget_type}</p></div>'
    
    def _render_kpi_card(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render KPI card widget"""
        
        title = config.get("title", "KPI")
        metric = config.get("metric")
        format_type = config.get("format", "number")
        size = config.get("size", "medium")
        threshold = config.get("threshold", {})
        target = config.get("target")
        
        # Get metric value from data
        value = self._get_metric_value(metric, data)
        formatted_value = self._format_value(value, format_type)
        
        # Determine status based on thresholds
        status_class = self._get_status_class(value, threshold)
        
        # Calculate progress towards target
        progress_html = ""
        if target:
            progress = min(100, (value / target * 100)) if target > 0 else 0
            progress_html = f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <small>Target: {self._format_value(target, format_type)}</small>
            """
        
        return f"""
        <div class="widget widget-{size} kpi-card {status_class}">
            <h3>{title}</h3>
            <div class="kpi-value">{formatted_value}</div>
            {progress_html}
            <div class="kpi-meta">
                <small>Metric: {metric}</small>
            </div>
        </div>
        """
    
    def _render_trend_chart(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render trend chart widget"""
        
        title = config.get("title", "Trend Chart")
        metrics = config.get("metrics", [])
        period = config.get("period", "24h")
        size = config.get("size", "medium")
        
        chart_id = f"chart_{hash(title)}"
        
        return f"""
        <div class="widget widget-{size}">
            <h3>{title}</h3>
            <canvas id="{chart_id}" width="400" height="200"></canvas>
            <script>
                // Chart.js configuration would go here
                const ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx_{chart_id}, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Trend',
                            data: [12, 19, 3, 5, 2, 3],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            </script>
        </div>
        """
    
    def _render_gauge(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render gauge widget"""
        
        title = config.get("title", "Gauge")
        metric = config.get("metric")
        min_val = config.get("min", 0)
        max_val = config.get("max", 100)
        size = config.get("size", "medium")
        threshold = config.get("threshold", {})
        
        value = self._get_metric_value(metric, data)
        percentage = ((value - min_val) / (max_val - min_val) * 100) if (max_val - min_val) > 0 else 0
        status_class = self._get_status_class(value, threshold)
        
        return f"""
        <div class="widget widget-{size} gauge-widget {status_class}">
            <h3>{title}</h3>
            <div class="gauge">
                <div class="gauge-fill" style="--percentage: {percentage}%"></div>
                <div class="gauge-value">{value}</div>
            </div>
            <div class="gauge-range">
                <span>{min_val}</span>
                <span>{max_val}</span>
            </div>
        </div>
        """
    
    def _render_table(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render table widget"""
        
        title = config.get("title", "Table")
        columns = config.get("columns", [])
        data_source = config.get("data_source")
        size = config.get("size", "medium")
        
        # Get table data
        table_data = data.get(data_source, [])
        
        # Render table headers
        headers_html = "".join(f"<th>{col}</th>" for col in columns)
        
        # Render table rows
        rows_html = ""
        for row in table_data[:10]:  # Limit to 10 rows
            cells_html = "".join(f"<td>{row.get(col, 'N/A')}</td>" for col in columns)
            rows_html += f"<tr>{cells_html}</tr>"
        
        if not rows_html:
            rows_html = f"<tr><td colspan='{len(columns)}'>No data available</td></tr>"
        
        return f"""
        <div class="widget widget-{size} table-widget">
            <h3>{title}</h3>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>{headers_html}</tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _render_alert_list(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render alert list widget"""
        
        title = config.get("title", "Alerts")
        filter_config = config.get("filter", {})
        size = config.get("size", "medium")
        
        # Get alerts from data
        alerts = data.get("alerts", [])
        
        # Apply filters
        filtered_alerts = alerts
        if "severity" in filter_config:
            filtered_alerts = [a for a in filtered_alerts if a.get("severity") in filter_config["severity"]]
        
        # Render alerts
        alerts_html = ""
        for alert in filtered_alerts[:5]:  # Show max 5 alerts
            severity = alert.get("severity", "info")
            alert_title = alert.get("title", "Alert")
            description = alert.get("description", "")
            created_at = alert.get("created_at", "")
            
            alerts_html += f"""
            <div class="alert-item alert-{severity}">
                <div class="alert-header">
                    <span class="alert-severity">{severity.upper()}</span>
                    <span class="alert-time">{created_at}</span>
                </div>
                <div class="alert-title">{alert_title}</div>
                <div class="alert-description">{description}</div>
            </div>
            """
        
        if not alerts_html:
            alerts_html = '<div class="no-alerts">✅ No active alerts</div>'
        
        return f"""
        <div class="widget widget-{size} alert-widget">
            <h3>{title}</h3>
            <div class="alert-list">
                {alerts_html}
            </div>
        </div>
        """
    
    def _render_heatmap(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render heatmap widget"""
        
        title = config.get("title", "Heatmap")
        size = config.get("size", "medium")
        
        return f"""
        <div class="widget widget-{size} heatmap-widget">
            <h3>{title}</h3>
            <div class="heatmap-placeholder">
                <p>Heatmap visualization would be rendered here</p>
                <p>Requires specific data formatting and visualization library</p>
            </div>
        </div>
        """
    
    def _render_funnel(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Render funnel widget"""
        
        title = config.get("title", "Funnel")
        stages = config.get("stages", [])
        size = config.get("size", "medium")
        
        # Mock funnel data
        funnel_data = [
            {"stage": "Registration", "count": 100, "rate": 100},
            {"stage": "First Commitment", "count": 75, "rate": 75},
            {"stage": "Completion", "count": 45, "rate": 45},
            {"stage": "Retention", "count": 30, "rate": 30}
        ]
        
        funnel_html = ""
        for stage_data in funnel_data:
            width = stage_data["rate"]
            funnel_html += f"""
            <div class="funnel-stage">
                <div class="funnel-bar" style="width: {width}%">
                    <span class="funnel-label">{stage_data['stage']}</span>
                    <span class="funnel-value">{stage_data['count']} ({stage_data['rate']}%)</span>
                </div>
            </div>
            """
        
        return f"""
        <div class="widget widget-{size} funnel-widget">
            <h3>{title}</h3>
            <div class="funnel">
                {funnel_html}
            </div>
        </div>
        """
    
    def _get_metric_value(self, metric: str, data: Dict[str, Any]) -> float:
        """Extract metric value from data"""
        
        # Look in metrics data
        metrics = data.get("metrics", [])
        for m in metrics:
            if m.get("id") == metric:
                return float(m.get("value", 0))
        
        # Look in direct data
        if metric in data:
            return float(data[metric])
        
        # Default mock values for demo
        mock_values = {
            "mau": 42.0,
            "platform_health_score": 85.0,
            "user_growth_rate": 15.0,
            "monthly_completion_rate": 67.0,
            "feature_discovery_rate": 78.0,
            "smart_goal_adoption": 72.0,
            "pod_membership_rate": 34.0,
            "system_health_percentage": 92.0,
            "avg_response_time": 245.0,
            "ai_success_rate": 94.0,
            "uptime_percentage": 99.8
        }
        
        return mock_values.get(metric, 0.0)
    
    def _format_value(self, value: float, format_type: str) -> str:
        """Format value based on type"""
        
        if format_type == "percentage":
            return f"{value:.1f}%"
        elif format_type == "milliseconds":
            return f"{value:.0f}ms"
        elif format_type == "currency":
            return f"${value:,.2f}"
        elif format_type == "number":
            if value >= 1000000:
                return f"{value/1000000:.1f}M"
            elif value >= 1000:
                return f"{value/1000:.1f}K"
            else:
                return f"{value:.0f}"
        elif format_type == "status":
            status_map = {0: "🔴 Down", 1: "🟡 Degraded", 2: "🟢 Healthy"}
            return status_map.get(int(value), "🔴 Unknown")
        else:
            return str(value)
    
    def _get_status_class(self, value: float, threshold: Dict[str, float]) -> str:
        """Get CSS status class based on thresholds"""
        
        critical = threshold.get("critical")
        warning = threshold.get("warning")
        
        if critical and value <= critical:
            return "status-critical"
        elif warning and value <= warning:
            return "status-warning"
        else:
            return "status-healthy"
    
    def _get_dashboard_theme(self, stakeholder: StakeholderType) -> Dict[str, str]:
        """Get theme colors for stakeholder"""
        
        themes = {
            StakeholderType.EXECUTIVE: {"primary": "#2c3e50", "accent": "#3498db"},
            StakeholderType.PRODUCT_MANAGER: {"primary": "#8e44ad", "accent": "#9b59b6"},
            StakeholderType.DEVELOPER: {"primary": "#27ae60", "accent": "#2ecc71"},
            StakeholderType.SUPPORT: {"primary": "#e67e22", "accent": "#f39c12"},
            StakeholderType.USER: {"primary": "#34495e", "accent": "#95a5a6"}
        }
        
        return themes.get(stakeholder, {"primary": "#34495e", "accent": "#95a5a6"})
    
    def _get_dashboard_css(self, theme: Dict[str, str]) -> str:
        """Generate dashboard CSS with theme"""
        
        primary_color = theme['primary']
        accent_color = theme['accent']
        
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .dashboard-header {{
            background: {primary_color};
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .dashboard-header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header-meta {{
            margin-top: 20px;
            opacity: 0.9;
        }}
        
        .refresh-btn {{
            background: {accent_color};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 15px;
        }}
        
        .dashboard-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .widget {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid {accent_color};
        }}
        
        .widget-small {{ grid-column: span 1; }}
        .widget-medium {{ grid-column: span 1; }}
        .widget-large {{ grid-column: span 2; }}
        .widget-full {{ grid-column: 1 / -1; }}
        
        .widget h3 {{
            color: {primary_color};
            margin-bottom: 15px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        
        .kpi-card .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        
        .status-healthy {{ border-left-color: #27ae60; }}
        .status-warning {{ border-left-color: #f39c12; }}
        .status-critical {{ border-left-color: #e74c3c; }}
        
        .progress-bar {{
            background: #ecf0f1;
            height: 8px;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }}
        
        .progress-fill {{
            background: {accent_color};
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .gauge {{
            position: relative;
            width: 150px;
            height: 150px;
            margin: 20px auto;
            border-radius: 50%;
            background: conic-gradient(from 0deg, #e74c3c 0% 30%, #f39c12 30% 60%, #27ae60 60% 100%);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .gauge::after {{
            content: '';
            position: absolute;
            width: 120px;
            height: 120px;
            background: white;
            border-radius: 50%;
        }}
        
        .gauge-value {{
            position: relative;
            z-index: 2;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .table-container {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: {primary_color};
            color: white;
        }}
        
        .alert-item {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        
        .alert-critical {{ border-left-color: #e74c3c; background: #fdf2f2; }}
        .alert-warning {{ border-left-color: #f39c12; background: #fef9e7; }}
        .alert-info {{ border-left-color: #3498db; background: #f0f8ff; }}
        
        .funnel-stage {{
            margin: 10px 0;
        }}
        
        .funnel-bar {{
            background: {accent_color};
            color: white;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .dashboard-footer {{
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-content {{
                grid-template-columns: 1fr;
            }}
            
            .widget-large, .widget-full {{
                grid-column: span 1;
            }}
        }}
        """
    
    def _get_dashboard_js(self) -> str:
        """Generate dashboard JavaScript"""
        
        return """
        // Auto-refresh functionality
        let refreshInterval;
        
        function startAutoRefresh() {
            const refreshTime = parseInt(document.querySelector('meta[http-equiv="refresh"]')?.content) || 300;
            refreshInterval = setInterval(() => {
                location.reload();
            }, refreshTime * 1000);
        }
        
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        }
        
        // Start auto-refresh when page loads
        document.addEventListener('DOMContentLoaded', startAutoRefresh);
        
        // Stop auto-refresh when page is hidden (save resources)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                startAutoRefresh();
            }
        });
        """
    
    def _generate_error_dashboard(self, error_message: str) -> str:
        """Generate error dashboard"""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #e74c3c; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <h1>Dashboard Error</h1>
            <p class="error">{error_message}</p>
            <button onclick="location.reload()">🔄 Retry</button>
        </body>
        </html>
        """
    
    async def get_dashboard_data_for_stakeholder(self, stakeholder: StakeholderType) -> Dict[str, Any]:
        """Get data needed for stakeholder dashboard"""
        
        try:
            # Collect base data
            if hasattr(self.monitor, 'get_system_overview'):
                system_data = await self.monitor.get_system_overview()
            else:
                system_data = {}
            
            if hasattr(self.metrics, 'get_metrics_summary'):
                metrics_data = await self.metrics.get_metrics_summary()
            else:
                metrics_data = {}
            
            if hasattr(self.alerting, 'get_active_alerts'):
                alerts_data = await self.alerting.get_active_alerts()
            else:
                alerts_data = []
            
            # Combine and filter data based on stakeholder needs
            dashboard_data = {
                "system": system_data,
                "metrics": metrics_data.get("metrics_by_category", {}),
                "alerts": alerts_data,
                "kpis": metrics_data.get("business_kpis", []),
                "timestamp": datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Stakeholder Dashboards - Custom dashboards for different user roles")