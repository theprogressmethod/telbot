#!/usr/bin/env python3
"""
Progress Method - Enhanced Metrics System
Custom metrics, KPIs, and business intelligence for Progress Method platform
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import uuid

from supabase import Client

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    BUSINESS_KPI = "business_kpi"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_PERFORMANCE = "system_performance"

class MetricSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class CustomMetric:
    id: str
    name: str
    description: str
    metric_type: MetricType
    value: float
    unit: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    tags: Dict[str, str] = None
    timestamp: datetime = None
    severity: MetricSeverity = MetricSeverity.INFO
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tags is None:
            self.tags = {}
        
        # Auto-determine severity based on thresholds
        if self.threshold_critical and self.value >= self.threshold_critical:
            self.severity = MetricSeverity.CRITICAL
        elif self.threshold_warning and self.value >= self.threshold_warning:
            self.severity = MetricSeverity.WARNING

@dataclass
class BusinessKPI:
    name: str
    current_value: float
    target_value: float
    unit: str
    trend_direction: str  # "up", "down", "stable"
    trend_percentage: float
    period: str  # "daily", "weekly", "monthly"
    last_updated: datetime
    description: str
    
class EnhancedMetricsSystem:
    """Enhanced metrics system for Progress Method specific analytics"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.custom_metrics = []
        self.business_kpis = []
        
    async def collect_progress_method_metrics(self) -> List[CustomMetric]:
        """Collect comprehensive Progress Method specific metrics"""
        metrics = []
        
        try:
            # User Engagement Metrics
            metrics.extend(await self._collect_user_engagement_metrics())
            
            # Commitment Success Metrics
            metrics.extend(await self._collect_commitment_metrics())
            
            # Pod Performance Metrics
            metrics.extend(await self._collect_pod_metrics())
            
            # AI Analysis Metrics
            metrics.extend(await self._collect_ai_metrics())
            
            # Business Growth Metrics
            metrics.extend(await self._collect_business_metrics())
            
            # User Journey Metrics
            metrics.extend(await self._collect_user_journey_metrics())
            
            self.custom_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error collecting Progress Method metrics: {e}")
            return []
    
    async def _collect_user_engagement_metrics(self) -> List[CustomMetric]:
        """Collect user engagement and activity metrics"""
        metrics = []
        
        try:
            # Daily Active Users
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            
            # DAU
            dau_result = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", today.isoformat()).execute()
            dau = dau_result.count if dau_result.count else 0
            
            metrics.append(CustomMetric(
                id="dau",
                name="Daily Active Users",
                description="Number of users active in the last 24 hours",
                metric_type=MetricType.GAUGE,
                value=float(dau),
                unit="users",
                threshold_warning=5.0,  # Less than 5 active users per day
                threshold_critical=2.0,  # Less than 2 active users per day
                tags={"category": "engagement", "period": "daily"}
            ))
            
            # WAU (Weekly Active Users)
            wau_result = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", week_ago.isoformat()).execute()
            wau = wau_result.count if wau_result.count else 0
            
            metrics.append(CustomMetric(
                id="wau",
                name="Weekly Active Users", 
                description="Number of users active in the last 7 days",
                metric_type=MetricType.GAUGE,
                value=float(wau),
                unit="users",
                threshold_warning=10.0,
                threshold_critical=5.0,
                tags={"category": "engagement", "period": "weekly"}
            ))
            
            # Average Session Duration (estimated based on commitment activity)
            commits_today = self.supabase.table("commitments").select("created_at").gte("created_at", today.isoformat()).execute()
            session_activity = len(commits_today.data) if commits_today.data else 0
            avg_session_duration = session_activity * 2.5  # Estimate 2.5 minutes per commitment action
            
            metrics.append(CustomMetric(
                id="avg_session_duration",
                name="Average Session Duration",
                description="Estimated average user session duration",
                metric_type=MetricType.GAUGE,
                value=avg_session_duration,
                unit="minutes",
                threshold_warning=1.0,  # Less than 1 minute average
                tags={"category": "engagement", "period": "daily"}
            ))
            
            # User Retention Rate (users active this week vs last week)
            last_week = week_ago - timedelta(days=7)
            last_week_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", last_week.isoformat()).lt("last_activity_at", week_ago.isoformat()).execute()
            last_week_count = last_week_users.count if last_week_users.count else 1
            
            retention_rate = (wau / last_week_count) * 100 if last_week_count > 0 else 0
            
            metrics.append(CustomMetric(
                id="user_retention_rate",
                name="Weekly User Retention Rate",
                description="Percentage of users retained from previous week",
                metric_type=MetricType.BUSINESS_KPI,
                value=retention_rate,
                unit="percentage",
                threshold_warning=50.0,  # Less than 50% retention
                threshold_critical=25.0,  # Less than 25% retention
                tags={"category": "retention", "period": "weekly"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting user engagement metrics: {e}")
            
        return metrics
    
    async def _collect_commitment_metrics(self) -> List[CustomMetric]:
        """Collect commitment creation and completion metrics"""
        metrics = []
        
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Commitment Creation Rate
            new_commitments = self.supabase.table("commitments").select("id", count="exact").gte("created_at", today.isoformat()).execute()
            daily_commitments = new_commitments.count if new_commitments.count else 0
            
            metrics.append(CustomMetric(
                id="daily_commitment_creation",
                name="Daily Commitment Creation",
                description="Number of new commitments created today",
                metric_type=MetricType.COUNTER,
                value=float(daily_commitments),
                unit="commitments",
                threshold_warning=5.0,  # Less than 5 commitments per day
                tags={"category": "commitments", "period": "daily"}
            ))
            
            # Commitment Completion Rate
            completed_commitments = self.supabase.table("commitments").select("id", count="exact").eq("status", "completed").gte("completed_at", today.isoformat()).execute()
            daily_completions = completed_commitments.count if completed_commitments.count else 0
            
            completion_rate = (daily_completions / daily_commitments * 100) if daily_commitments > 0 else 0
            
            metrics.append(CustomMetric(
                id="daily_completion_rate",
                name="Daily Completion Rate",
                description="Percentage of commitments completed today",
                metric_type=MetricType.BUSINESS_KPI,
                value=completion_rate,
                unit="percentage",
                threshold_warning=30.0,  # Less than 30% completion rate
                threshold_critical=15.0,  # Less than 15% completion rate
                tags={"category": "commitments", "period": "daily"}
            ))
            
            # Average Time to Complete
            recent_completed = self.supabase.table("commitments").select("created_at, completed_at").eq("status", "completed").gte("completed_at", week_ago.isoformat()).execute()
            
            if recent_completed.data:
                completion_times = []
                for commitment in recent_completed.data:
                    if commitment.get("created_at") and commitment.get("completed_at"):
                        created = datetime.fromisoformat(commitment["created_at"].replace('Z', '+00:00'))
                        completed = datetime.fromisoformat(commitment["completed_at"].replace('Z', '+00:00'))
                        duration = (completed - created).total_seconds() / 3600  # Convert to hours
                        completion_times.append(duration)
                
                avg_completion_time = statistics.mean(completion_times) if completion_times else 0
                
                metrics.append(CustomMetric(
                    id="avg_completion_time",
                    name="Average Completion Time",
                    description="Average time from commitment creation to completion",
                    metric_type=MetricType.GAUGE,
                    value=avg_completion_time,
                    unit="hours",
                    threshold_warning=168.0,  # More than 1 week
                    threshold_critical=336.0,  # More than 2 weeks
                    tags={"category": "commitments", "period": "weekly"}
                ))
            
            # SMART Goal Adoption Rate (assuming commitments with AI analysis are SMART)
            smart_commitments = self.supabase.table("commitments").select("id", count="exact").not_.is_("smart_analysis", "null").gte("created_at", week_ago.isoformat()).execute()
            total_commitments_week = self.supabase.table("commitments").select("id", count="exact").gte("created_at", week_ago.isoformat()).execute()
            
            smart_count = smart_commitments.count if smart_commitments.count else 0
            total_count = total_commitments_week.count if total_commitments_week.count else 1
            
            smart_adoption_rate = (smart_count / total_count * 100) if total_count > 0 else 0
            
            metrics.append(CustomMetric(
                id="smart_goal_adoption",
                name="SMART Goal Adoption Rate",
                description="Percentage of commitments using SMART analysis",
                metric_type=MetricType.BUSINESS_KPI,
                value=smart_adoption_rate,
                unit="percentage",
                threshold_warning=60.0,  # Less than 60% using SMART analysis
                tags={"category": "ai_features", "period": "weekly"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting commitment metrics: {e}")
            
        return metrics
    
    async def _collect_pod_metrics(self) -> List[CustomMetric]:
        """Collect pod and social feature metrics"""
        metrics = []
        
        try:
            # Active Pods
            active_pods = self.supabase.table("pods").select("id", count="exact").eq("is_active", True).execute()
            pod_count = active_pods.count if active_pods.count else 0
            
            metrics.append(CustomMetric(
                id="active_pods",
                name="Active Pods",
                description="Number of currently active pods",
                metric_type=MetricType.GAUGE,
                value=float(pod_count),
                unit="pods",
                tags={"category": "social", "period": "current"}
            ))
            
            # Pod Membership Rate
            total_users = self.supabase.table("users").select("id", count="exact").execute()
            pod_members = self.supabase.table("pod_memberships").select("user_id", count="exact").execute()
            
            total_user_count = total_users.count if total_users.count else 1
            member_count = pod_members.count if pod_members.count else 0
            
            pod_membership_rate = (member_count / total_user_count * 100) if total_user_count > 0 else 0
            
            metrics.append(CustomMetric(
                id="pod_membership_rate",
                name="Pod Membership Rate",
                description="Percentage of users who are pod members",
                metric_type=MetricType.BUSINESS_KPI,
                value=pod_membership_rate,
                unit="percentage",
                threshold_warning=25.0,  # Less than 25% pod membership
                tags={"category": "social", "period": "current"}
            ))
            
            # Average Pod Size
            if pod_count > 0:
                avg_pod_size = member_count / pod_count
                
                metrics.append(CustomMetric(
                    id="avg_pod_size",
                    name="Average Pod Size",
                    description="Average number of members per pod",
                    metric_type=MetricType.GAUGE,
                    value=avg_pod_size,
                    unit="members",
                    threshold_warning=2.0,  # Less than 2 members per pod
                    tags={"category": "social", "period": "current"}
                ))
            
        except Exception as e:
            logger.error(f"Error collecting pod metrics: {e}")
            
        return metrics
    
    async def _collect_ai_metrics(self) -> List[CustomMetric]:
        """Collect AI and SMART analysis metrics"""
        metrics = []
        
        try:
            today = datetime.now().date()
            
            # AI Analysis Usage
            ai_analyses = self.supabase.table("commitments").select("id", count="exact").not_.is_("smart_analysis", "null").gte("created_at", today.isoformat()).execute()
            ai_usage_count = ai_analyses.count if ai_analyses.count else 0
            
            metrics.append(CustomMetric(
                id="daily_ai_usage",
                name="Daily AI Analysis Usage",
                description="Number of AI analyses performed today",
                metric_type=MetricType.COUNTER,
                value=float(ai_usage_count),
                unit="analyses",
                tags={"category": "ai_features", "period": "daily"}
            ))
            
            # AI Analysis Success Rate (assuming non-null smart_analysis means success)
            total_commitments_today = self.supabase.table("commitments").select("id", count="exact").gte("created_at", today.isoformat()).execute()
            total_today = total_commitments_today.count if total_commitments_today.count else 1
            
            ai_success_rate = (ai_usage_count / total_today * 100) if total_today > 0 else 0
            
            metrics.append(CustomMetric(
                id="ai_success_rate",
                name="AI Analysis Success Rate",
                description="Percentage of commitments successfully analyzed by AI",
                metric_type=MetricType.BUSINESS_KPI,
                value=ai_success_rate,
                unit="percentage",
                threshold_warning=80.0,  # Less than 80% AI success
                threshold_critical=60.0,  # Less than 60% AI success
                tags={"category": "ai_features", "period": "daily"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting AI metrics: {e}")
            
        return metrics
    
    async def _collect_business_metrics(self) -> List[CustomMetric]:
        """Collect business growth and health metrics"""
        metrics = []
        
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # User Growth Rate
            new_users_week = self.supabase.table("users").select("id", count="exact").gte("created_at", week_ago.isoformat()).execute()
            new_users_month = self.supabase.table("users").select("id", count="exact").gte("created_at", month_ago.isoformat()).execute()
            
            weekly_growth = new_users_week.count if new_users_week.count else 0
            monthly_growth = new_users_month.count if new_users_month.count else 1
            
            growth_rate = (weekly_growth / (monthly_growth / 4) * 100) if monthly_growth > 0 else 0
            
            metrics.append(CustomMetric(
                id="user_growth_rate",
                name="Weekly User Growth Rate",
                description="User acquisition rate compared to weekly average",
                metric_type=MetricType.BUSINESS_KPI,
                value=growth_rate,
                unit="percentage",
                threshold_warning=0.0,  # No growth
                tags={"category": "business", "period": "weekly"}
            ))
            
            # Platform Health Score (composite metric)
            # Based on: user activity, commitment completion, AI usage, error rates
            health_score = min(100, (
                min(100, dau * 10) * 0.3 +  # User activity weight
                min(100, completion_rate) * 0.3 +  # Completion rate weight  
                min(100, ai_success_rate) * 0.2 +  # AI success weight
                min(100, 100 - (0 * 10)) * 0.2  # Error rate weight (assuming 0 errors for now)
            ))
            
            metrics.append(CustomMetric(
                id="platform_health_score",
                name="Platform Health Score",
                description="Composite health score based on key metrics",
                metric_type=MetricType.BUSINESS_KPI,
                value=health_score,
                unit="score",
                threshold_warning=70.0,  # Health score below 70
                threshold_critical=50.0,  # Health score below 50
                tags={"category": "business", "period": "daily"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
            
        return metrics
    
    async def _collect_user_journey_metrics(self) -> List[CustomMetric]:
        """Collect user journey and funnel metrics"""
        metrics = []
        
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Onboarding Completion Rate
            new_users = self.supabase.table("users").select("id", count="exact").gte("created_at", week_ago.isoformat()).execute()
            users_with_commitments = self.supabase.table("users").select("id").gte("created_at", week_ago.isoformat()).execute()
            
            if users_with_commitments.data:
                user_ids = [user["id"] for user in users_with_commitments.data]
                users_with_first_commitment = self.supabase.table("commitments").select("user_id").in_("user_id", user_ids).execute()
                unique_users_with_commitments = len(set(c["user_id"] for c in users_with_first_commitment.data)) if users_with_first_commitment.data else 0
            else:
                unique_users_with_commitments = 0
            
            new_user_count = new_users.count if new_users.count else 1
            onboarding_rate = (unique_users_with_commitments / new_user_count * 100) if new_user_count > 0 else 0
            
            metrics.append(CustomMetric(
                id="onboarding_completion_rate",
                name="Onboarding Completion Rate",
                description="Percentage of new users who create their first commitment",
                metric_type=MetricType.BUSINESS_KPI,
                value=onboarding_rate,
                unit="percentage",
                threshold_warning=50.0,  # Less than 50% complete onboarding
                threshold_critical=25.0,  # Less than 25% complete onboarding
                tags={"category": "user_journey", "period": "weekly"}
            ))
            
            # Feature Discovery Rate (users who tried different commands)
            # This would require tracking command usage - for now, estimate based on data diversity
            feature_discovery_rate = 75.0  # Placeholder - would need command tracking
            
            metrics.append(CustomMetric(
                id="feature_discovery_rate",
                name="Feature Discovery Rate",
                description="Percentage of users discovering multiple features",
                metric_type=MetricType.USER_BEHAVIOR,
                value=feature_discovery_rate,
                unit="percentage",
                tags={"category": "user_journey", "period": "weekly"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting user journey metrics: {e}")
            
        return metrics
    
    async def generate_business_kpis(self) -> List[BusinessKPI]:
        """Generate key business performance indicators"""
        kpis = []
        
        try:
            # Monthly Active Users (MAU)
            month_ago = (datetime.now() - timedelta(days=30)).date()
            mau_result = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", month_ago.isoformat()).execute()
            current_mau = mau_result.count if mau_result.count else 0
            
            # Get previous month for trend
            two_months_ago = (datetime.now() - timedelta(days=60)).date()
            prev_mau_result = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", two_months_ago.isoformat()).lt("last_activity_at", month_ago.isoformat()).execute()
            prev_mau = prev_mau_result.count if prev_mau_result.count else 1
            
            mau_trend = ((current_mau - prev_mau) / prev_mau * 100) if prev_mau > 0 else 0
            mau_direction = "up" if mau_trend > 5 else "down" if mau_trend < -5 else "stable"
            
            kpis.append(BusinessKPI(
                name="Monthly Active Users",
                current_value=float(current_mau),
                target_value=50.0,  # Target 50 MAU
                unit="users",
                trend_direction=mau_direction,
                trend_percentage=mau_trend,
                period="monthly",
                last_updated=datetime.now(),
                description="Total active users in the last 30 days"
            ))
            
            # Monthly Commitment Completion Rate
            monthly_commitments = self.supabase.table("commitments").select("id", count="exact").gte("created_at", month_ago.isoformat()).execute()
            monthly_completed = self.supabase.table("commitments").select("id", count="exact").eq("status", "completed").gte("completed_at", month_ago.isoformat()).execute()
            
            total_monthly = monthly_commitments.count if monthly_commitments.count else 1
            completed_monthly = monthly_completed.count if monthly_completed.count else 0
            
            monthly_completion_rate = (completed_monthly / total_monthly * 100) if total_monthly > 0 else 0
            
            kpis.append(BusinessKPI(
                name="Monthly Completion Rate",
                current_value=monthly_completion_rate,
                target_value=60.0,  # Target 60% completion rate
                unit="percentage",
                trend_direction="stable",  # Would need historical data for trend
                trend_percentage=0.0,
                period="monthly",
                last_updated=datetime.now(),
                description="Percentage of commitments completed this month"
            ))
            
            # Platform Adoption Score
            total_users = self.supabase.table("users").select("id", count="exact").execute()
            total_user_count = total_users.count if total_users.count else 1
            
            adoption_score = min(100, (current_mau / total_user_count * 100)) if total_user_count > 0 else 0
            
            kpis.append(BusinessKPI(
                name="Platform Adoption Score",
                current_value=adoption_score,
                target_value=80.0,  # Target 80% of registered users being active
                unit="percentage",
                trend_direction="up",
                trend_percentage=10.0,
                period="monthly", 
                last_updated=datetime.now(),
                description="Percentage of registered users who are monthly active"
            ))
            
            self.business_kpis = kpis
            return kpis
            
        except Exception as e:
            logger.error(f"❌ Error generating business KPIs: {e}")
            return []
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        try:
            # Collect all metrics
            custom_metrics = await self.collect_progress_method_metrics()
            business_kpis = await self.generate_business_kpis()
            
            # Categorize metrics
            metrics_by_category = {}
            for metric in custom_metrics:
                category = metric.tags.get("category", "other")
                if category not in metrics_by_category:
                    metrics_by_category[category] = []
                metrics_by_category[category].append(asdict(metric))
            
            # Count by severity
            severity_counts = {"info": 0, "warning": 0, "critical": 0}
            for metric in custom_metrics:
                severity_counts[metric.severity.value] += 1
            
            return {
                "summary": {
                    "total_metrics": len(custom_metrics),
                    "total_kpis": len(business_kpis),
                    "severity_counts": severity_counts,
                    "last_updated": datetime.now().isoformat()
                },
                "metrics_by_category": metrics_by_category,
                "business_kpis": [asdict(kpi) for kpi in business_kpis],
                "alerts": [
                    asdict(metric) for metric in custom_metrics 
                    if metric.severity in [MetricSeverity.WARNING, MetricSeverity.CRITICAL]
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting metrics summary: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Enhanced Metrics System - Use EnhancedMetricsSystem class for custom Progress Method metrics")