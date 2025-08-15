#!/usr/bin/env python3
"""
Progress Method - System Monitoring Dashboard
Comprehensive visibility and control for all system components
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import time
import traceback

from supabase import Client
import aiohttp
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class FeatureStatus(Enum):
    PRODUCTION = "production"
    BETA = "beta"
    DEVELOPMENT = "development"
    DISABLED = "disabled"

@dataclass
class SystemMetric:
    name: str
    value: Any
    status: HealthStatus
    last_updated: datetime
    description: str
    target_value: Optional[Any] = None
    warning_threshold: Optional[Any] = None
    critical_threshold: Optional[Any] = None

@dataclass
class FeatureInfo:
    name: str
    command: Optional[str]
    status: FeatureStatus
    usage_count_24h: int
    error_count_24h: int
    last_used: Optional[datetime]
    description: str
    dependencies: List[str]
    user_roles_required: List[str]

@dataclass
class UserJourneyStep:
    step_name: str
    user_count: int
    completion_rate: float
    avg_time_to_complete: Optional[timedelta]
    drop_off_rate: float
    status: HealthStatus

class SystemMonitor:
    """Comprehensive system monitoring and control dashboard"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.start_time = datetime.now()
        self.metrics_cache = {}
        self.cache_duration = timedelta(minutes=5)
        
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system health overview"""
        try:
            overview = {
                "system_status": await self._get_overall_health(),
                "uptime": self._get_uptime(),
                "core_metrics": await self._get_core_metrics(),
                "feature_status": await self._get_feature_status(),
                "user_journey": await self._get_user_journey_health(),
                "infrastructure": await self._get_infrastructure_status(),
                "alerts": await self._get_active_alerts(),
                "last_updated": datetime.now().isoformat()
            }
            return overview
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _get_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        try:
            health_checks = [
                await self._check_database_health(),
                await self._check_bot_health(),
                await self._check_feature_health(),
                await self._check_user_experience_health()
            ]
            
            healthy_count = sum(1 for check in health_checks if check["status"] == HealthStatus.HEALTHY.value)
            total_checks = len(health_checks)
            health_percentage = (healthy_count / total_checks) * 100
            
            if health_percentage >= 90:
                overall_status = HealthStatus.HEALTHY
            elif health_percentage >= 70:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.CRITICAL
            
            return {
                "status": overall_status.value,
                "health_percentage": health_percentage,
                "healthy_components": healthy_count,
                "total_components": total_checks,
                "individual_checks": health_checks
            }
        except Exception as e:
            logger.error(f"Error calculating overall health: {e}")
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e)
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = self.supabase.table("users").select("id").limit(1).execute()
            query_time = time.time() - start_time
            
            # Check database metrics
            metrics = await self._get_database_metrics()
            
            # Determine health status
            if query_time > 2.0:
                status = HealthStatus.CRITICAL
            elif query_time > 1.0:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "component": "database",
                "status": status.value,
                "response_time_ms": round(query_time * 1000, 2),
                "metrics": metrics,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "component": "database",
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Get detailed database performance metrics"""
        try:
            metrics = {}
            
            # Table sizes and record counts
            tables = ["users", "commitments", "pods", "pod_memberships", "meetings"]
            for table in tables:
                try:
                    result = self.supabase.table(table).select("*", count="exact").execute()
                    metrics[f"{table}_count"] = result.count
                except:
                    metrics[f"{table}_count"] = "error"
            
            # Recent activity (last 24 hours)
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            # New users
            new_users = self.supabase.table("users").select("id", count="exact").gte("created_at", yesterday).execute()
            metrics["new_users_24h"] = new_users.count
            
            # New commitments
            new_commitments = self.supabase.table("commitments").select("id", count="exact").gte("created_at", yesterday).execute()
            metrics["new_commitments_24h"] = new_commitments.count
            
            # Completed commitments
            completed_commitments = self.supabase.table("commitments").select("id", count="exact").gte("completed_at", yesterday).execute()
            metrics["completed_commitments_24h"] = completed_commitments.count
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {"error": str(e)}
    
    async def _check_bot_health(self) -> Dict[str, Any]:
        """Check Telegram bot health and responsiveness"""
        try:
            # This would require bot instance access
            # For now, check if we can make basic queries that the bot would make
            
            # Test user lookup (common bot operation)
            start_time = time.time()
            result = self.supabase.table("users").select("id").limit(5).execute()
            query_time = time.time() - start_time
            
            # Check recent bot activity
            recent_activity = await self._get_recent_bot_activity()
            
            # Determine status based on recent activity and performance
            if recent_activity["messages_24h"] == 0:
                status = HealthStatus.WARNING
            elif query_time > 1.0:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "component": "telegram_bot",
                "status": status.value,
                "response_time_ms": round(query_time * 1000, 2),
                "recent_activity": recent_activity,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Bot health check failed: {e}")
            return {
                "component": "telegram_bot",
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    async def _get_recent_bot_activity(self) -> Dict[str, Any]:
        """Get recent bot activity metrics"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            # Count recent commitments as proxy for bot activity
            recent_commits = self.supabase.table("commitments").select("id", count="exact").gte("created_at", yesterday).execute()
            
            # Count recent completions
            recent_completions = self.supabase.table("commitments").select("id", count="exact").gte("completed_at", yesterday).execute()
            
            # Count active users (updated recently)
            active_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", yesterday).execute()
            
            return {
                "messages_24h": recent_commits.count + recent_completions.count,
                "active_users_24h": active_users.count,
                "new_commitments_24h": recent_commits.count,
                "completions_24h": recent_completions.count
            }
        except Exception as e:
            logger.error(f"Error getting bot activity: {e}")
            return {"error": str(e)}
    
    async def _check_feature_health(self) -> Dict[str, Any]:
        """Check health of individual features"""
        try:
            features = await self._get_all_features()
            
            # Calculate feature health metrics
            total_features = len(features)
            production_features = sum(1 for f in features if f.status == FeatureStatus.PRODUCTION)
            error_features = sum(1 for f in features if f.error_count_24h > 0)
            
            # Determine overall feature health
            if error_features == 0 and production_features >= total_features * 0.8:
                status = HealthStatus.HEALTHY
            elif error_features <= total_features * 0.1:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
            
            return {
                "component": "features",
                "status": status.value,
                "total_features": total_features,
                "production_features": production_features,
                "features_with_errors": error_features,
                "feature_details": [asdict(f) for f in features[:10]],  # Top 10
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Feature health check failed: {e}")
            return {
                "component": "features",
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    async def _get_all_features(self) -> List[FeatureInfo]:
        """Get comprehensive list of all system features"""
        
        # Define all known features with their metadata
        features = [
            # Core Features (Production)
            FeatureInfo("User Registration", "/start", FeatureStatus.PRODUCTION, 0, 0, None, 
                       "New user onboarding and registration", ["database", "telegram"], ["all"]),
            FeatureInfo("Commitment Creation", "/commit", FeatureStatus.PRODUCTION, 0, 0, None,
                       "SMART goal creation with AI analysis", ["database", "openai"], ["all"]),
            FeatureInfo("Commitment Completion", "/done", FeatureStatus.PRODUCTION, 0, 0, None,
                       "Mark commitments as complete", ["database"], ["all"]),
            FeatureInfo("Commitment Listing", "/list", FeatureStatus.PRODUCTION, 0, 0, None,
                       "View active commitments", ["database"], ["all"]),
            FeatureInfo("Progress Tracking", "/progress", FeatureStatus.PRODUCTION, 0, 0, None,
                       "Personal progress analytics", ["database"], ["all"]),
            FeatureInfo("Statistics", "/stats", FeatureStatus.PRODUCTION, 0, 0, None,
                       "Points and achievement tracking", ["database"], ["all"]),
            FeatureInfo("Help System", "/help", FeatureStatus.PRODUCTION, 0, 0, None,
                       "User guidance and support", [], ["all"]),
            FeatureInfo("Feedback Collection", "/feedback", FeatureStatus.PRODUCTION, 0, 0, None,
                       "User feedback and suggestions", ["database"], ["all"]),
            
            # Social Features (Production)
            FeatureInfo("Leaderboard", "/leaderboard", FeatureStatus.PRODUCTION, 0, 0, None,
                       "Weekly top performers", ["database"], ["all"]),
            FeatureInfo("Champions", "/champions", FeatureStatus.PRODUCTION, 0, 0, None,
                       "All-time achievement leaders", ["database"], ["all"]),
            FeatureInfo("Streaks", "/streaks", FeatureStatus.PRODUCTION, 0, 0, None,
                       "Consistency streak tracking", ["database"], ["all"]),
            
            # Pod Features (Beta)
            FeatureInfo("Pod Weekly Challenge", "/podweek", FeatureStatus.BETA, 0, 0, None,
                       "Pod-specific weekly challenges", ["database"], ["pod_member"]),
            FeatureInfo("Pod Leaderboard", "/podleaderboard", FeatureStatus.BETA, 0, 0, None,
                       "Pod-specific rankings", ["database"], ["pod_member"]),
            FeatureInfo("Attendance Tracking", "/attendance", FeatureStatus.BETA, 0, 0, None,
                       "Personal meeting attendance", ["database"], ["pod_member"]),
            FeatureInfo("Pod Attendance", "/podattendance", FeatureStatus.BETA, 0, 0, None,
                       "Pod attendance overview", ["database"], ["pod_member"]),
            FeatureInfo("Manual Attendance", "/markattendance", FeatureStatus.BETA, 0, 0, None,
                       "Manual attendance marking", ["database"], ["admin"]),
            
            # Advanced Features (Development)
            FeatureInfo("Automation Sequences", "/sequences", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "View active automation sequences", ["database"], ["all"]),
            FeatureInfo("Stop Sequences", "/stop_sequences", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "Pause automation sequences", ["database"], ["all"]),
            FeatureInfo("Role Management", "/myroles", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "Check user permissions and roles", ["database"], ["all"]),
            
            # Admin Features (Production)
            FeatureInfo("Admin Statistics", "/adminstats", FeatureStatus.PRODUCTION, 0, 0, None,
                       "System-wide analytics and metrics", ["database"], ["admin"]),
            FeatureInfo("Grant Roles", "/grant_role", FeatureStatus.PRODUCTION, 0, 0, None,
                       "User role management", ["database"], ["super_admin"]),
            
            # Development Features (Testing)
            FeatureInfo("Database Test", "/dbtest", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "Database connectivity testing", ["database"], ["admin"]),
            FeatureInfo("AI Test", "/aitest", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "OpenAI API connectivity testing", ["openai"], ["admin"]),
            FeatureInfo("Fix Utilities", "/fix", FeatureStatus.DEVELOPMENT, 0, 0, None,
                       "Data migration and fix utilities", ["database"], ["super_admin"]),
        ]
        
        # Get actual usage data for each feature
        for feature in features:
            if feature.command:
                usage_data = await self._get_feature_usage(feature.command)
                feature.usage_count_24h = usage_data.get("usage_24h", 0)
                feature.error_count_24h = usage_data.get("errors_24h", 0)
                feature.last_used = usage_data.get("last_used")
        
        return features
    
    async def _get_feature_status(self) -> Dict[str, Any]:
        """Get feature status overview"""
        try:
            features = await self._get_all_features()
            
            production_count = sum(1 for f in features if f.status == FeatureStatus.PRODUCTION)
            beta_count = sum(1 for f in features if f.status == FeatureStatus.BETA)
            development_count = sum(1 for f in features if f.status == FeatureStatus.DEVELOPMENT)
            
            total_usage_24h = sum(f.usage_count_24h for f in features)
            total_errors_24h = sum(f.error_count_24h for f in features)
            
            error_rate = (total_errors_24h / total_usage_24h * 100) if total_usage_24h > 0 else 0
            
            return {
                "total_features": len(features),
                "production_features": production_count,
                "beta_features": beta_count,
                "development_features": development_count,
                "total_usage_24h": total_usage_24h,
                "total_errors_24h": total_errors_24h,
                "error_rate_24h": round(error_rate, 2),
                "status": "healthy" if error_rate < 5 else "warning" if error_rate < 10 else "critical"
            }
        except Exception as e:
            logger.error(f"Error getting feature status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_feature_usage(self, command: str) -> Dict[str, Any]:
        """Get usage statistics for a specific command/feature"""
        try:
            # For now, estimate usage based on related database activity
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            if command == "/commit":
                result = self.supabase.table("commitments").select("created_at").gte("created_at", yesterday).execute()
                usage_24h = len(result.data)
                last_used = max([datetime.fromisoformat(r["created_at"]) for r in result.data]) if result.data else None
            elif command == "/done":
                result = self.supabase.table("commitments").select("completed_at").gte("completed_at", yesterday).execute()
                usage_24h = len(result.data)
                last_used = max([datetime.fromisoformat(r["completed_at"]) for r in result.data]) if result.data else None
            else:
                # For other commands, we'd need actual usage logging
                usage_24h = 0
                last_used = None
            
            return {
                "usage_24h": usage_24h,
                "errors_24h": 0,  # Would need error logging
                "last_used": last_used
            }
        except Exception as e:
            logger.error(f"Error getting feature usage for {command}: {e}")
            return {"usage_24h": 0, "errors_24h": 1, "last_used": None}
    
    async def _check_user_experience_health(self) -> Dict[str, Any]:
        """Check user experience and journey health"""
        try:
            ux_metrics = await self._get_user_experience_metrics()
            
            # Determine UX health based on metrics
            completion_rate = ux_metrics.get("commitment_completion_rate", 0)
            user_retention = ux_metrics.get("user_retention_rate", 0)
            
            if completion_rate >= 0.7 and user_retention >= 0.8:
                status = HealthStatus.HEALTHY
            elif completion_rate >= 0.5 and user_retention >= 0.6:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
            
            return {
                "component": "user_experience",
                "status": status.value,
                "metrics": ux_metrics,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"User experience health check failed: {e}")
            return {
                "component": "user_experience",
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    async def _get_user_experience_metrics(self) -> Dict[str, Any]:
        """Get comprehensive user experience metrics"""
        try:
            metrics = {}
            
            # Overall completion rate
            total_commitments = self.supabase.table("commitments").select("id", count="exact").execute()
            completed_commitments = self.supabase.table("commitments").select("id", count="exact").eq("status", "completed").execute()
            
            if total_commitments.count > 0:
                metrics["commitment_completion_rate"] = completed_commitments.count / total_commitments.count
            else:
                metrics["commitment_completion_rate"] = 0
            
            # User retention (active in last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            total_users = self.supabase.table("users").select("id", count="exact").execute()
            active_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", week_ago).execute()
            
            if total_users.count > 0:
                metrics["user_retention_rate"] = active_users.count / total_users.count
            else:
                metrics["user_retention_rate"] = 0
            
            # Average streak length
            users = self.supabase.table("users").select("current_streak, longest_streak").execute()
            if users.data:
                metrics["avg_current_streak"] = sum(u.get("current_streak", 0) for u in users.data) / len(users.data)
                metrics["avg_longest_streak"] = sum(u.get("longest_streak", 0) for u in users.data) / len(users.data)
            else:
                metrics["avg_current_streak"] = 0
                metrics["avg_longest_streak"] = 0
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting UX metrics: {e}")
            return {"error": str(e)}
    
    async def _get_infrastructure_status(self) -> Dict[str, Any]:
        """Check infrastructure components"""
        try:
            infrastructure = {
                "database": await self._check_database_infrastructure(),
                "external_apis": await self._check_external_apis(),
                "deployment": await self._check_deployment_status()
            }
            
            # Calculate overall infrastructure health
            healthy_components = sum(1 for comp in infrastructure.values() 
                                   if comp.get("status") == HealthStatus.HEALTHY.value)
            total_components = len(infrastructure)
            
            overall_status = HealthStatus.HEALTHY if healthy_components == total_components else HealthStatus.WARNING
            
            return {
                "overall_status": overall_status.value,
                "healthy_components": healthy_components,
                "total_components": total_components,
                "components": infrastructure
            }
        except Exception as e:
            logger.error(f"Error checking infrastructure: {e}")
            return {"error": str(e)}
    
    async def _check_database_infrastructure(self) -> Dict[str, Any]:
        """Check database infrastructure health"""
        try:
            # Test query performance
            start_time = time.time()
            self.supabase.table("users").select("id").limit(1).execute()
            query_time = time.time() - start_time
            
            status = HealthStatus.HEALTHY if query_time < 1.0 else HealthStatus.WARNING
            
            return {
                "status": status.value,
                "response_time_ms": round(query_time * 1000, 2),
                "provider": "Supabase",
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e),
                "provider": "Supabase"
            }
    
    async def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API health"""
        apis = {
            "openai": await self._check_openai_api(),
            "telegram": await self._check_telegram_api()
        }
        
        healthy_apis = sum(1 for api in apis.values() if api.get("status") == HealthStatus.HEALTHY.value)
        overall_status = HealthStatus.HEALTHY if healthy_apis == len(apis) else HealthStatus.WARNING
        
        return {
            "overall_status": overall_status.value,
            "apis": apis
        }
    
    async def _check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            # We can't easily test OpenAI without making a real API call
            # For now, just check if the API key is present
            api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key and api_key.startswith(("sk-", "sk-proj-")):
                status = HealthStatus.HEALTHY
                message = "API key configured correctly"
            else:
                status = HealthStatus.CRITICAL
                message = "API key missing or invalid"
            
            return {
                "status": status.value,
                "message": message,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e)
            }
    
    async def _check_telegram_api(self) -> Dict[str, Any]:
        """Check Telegram Bot API connectivity"""
        try:
            # Check if bot token is configured
            bot_token = os.getenv("BOT_TOKEN")
            
            if bot_token and ":" in bot_token:
                status = HealthStatus.HEALTHY
                message = "Bot token configured correctly"
            else:
                status = HealthStatus.CRITICAL
                message = "Bot token missing or invalid"
            
            return {
                "status": status.value,
                "message": message,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e)
            }
    
    async def _check_deployment_status(self) -> Dict[str, Any]:
        """Check deployment platform status"""
        try:
            # Detect deployment environment
            environment = "unknown"
            if os.getenv("RAILWAY_ENVIRONMENT"):
                environment = "railway"
            elif os.getenv("RENDER"):
                environment = "render"
            elif os.getenv("VERCEL"):
                environment = "vercel"
            
            return {
                "status": HealthStatus.HEALTHY.value,
                "environment": environment,
                "uptime": self._get_uptime(),
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "error": str(e)
            }
    
    async def _get_user_journey_health(self) -> Dict[str, Any]:
        """Analyze user journey funnel health"""
        try:
            journey_steps = [
                await self._analyze_journey_step("registration", "User Registration"),
                await self._analyze_journey_step("first_commit", "First Commitment"),
                await self._analyze_journey_step("engagement", "Regular Engagement"),
                await self._analyze_journey_step("retention", "Long-term Retention")
            ]
            
            # Calculate overall journey health
            avg_completion_rate = sum(step.completion_rate for step in journey_steps) / len(journey_steps)
            
            if avg_completion_rate >= 0.8:
                overall_status = HealthStatus.HEALTHY
            elif avg_completion_rate >= 0.6:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.CRITICAL
            
            return {
                "overall_status": overall_status.value,
                "avg_completion_rate": avg_completion_rate,
                "journey_steps": [asdict(step) for step in journey_steps]
            }
        except Exception as e:
            logger.error(f"Error analyzing user journey: {e}")
            return {"error": str(e)}
    
    async def _analyze_journey_step(self, step_type: str, step_name: str) -> UserJourneyStep:
        """Analyze a specific user journey step"""
        try:
            if step_type == "registration":
                # All users who registered
                total_users = self.supabase.table("users").select("id", count="exact").execute()
                return UserJourneyStep(
                    step_name=step_name,
                    user_count=total_users.count,
                    completion_rate=1.0,  # All registered users completed registration
                    avg_time_to_complete=None,
                    drop_off_rate=0.0,
                    status=HealthStatus.HEALTHY
                )
            
            elif step_type == "first_commit":
                # Users who made their first commitment
                total_users = self.supabase.table("users").select("id", count="exact").execute()
                users_with_commits = self.supabase.table("users").select("id", count="exact").not_.is_("first_commitment_at", "null").execute()
                
                completion_rate = users_with_commits.count / total_users.count if total_users.count > 0 else 0
                drop_off_rate = 1 - completion_rate
                
                status = HealthStatus.HEALTHY if completion_rate >= 0.7 else HealthStatus.WARNING
                
                return UserJourneyStep(
                    step_name=step_name,
                    user_count=users_with_commits.count,
                    completion_rate=completion_rate,
                    avg_time_to_complete=None,
                    drop_off_rate=drop_off_rate,
                    status=status
                )
            
            elif step_type == "engagement":
                # Users active in last 7 days
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                total_users = self.supabase.table("users").select("id", count="exact").execute()
                active_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", week_ago).execute()
                
                completion_rate = active_users.count / total_users.count if total_users.count > 0 else 0
                drop_off_rate = 1 - completion_rate
                
                status = HealthStatus.HEALTHY if completion_rate >= 0.6 else HealthStatus.WARNING
                
                return UserJourneyStep(
                    step_name=step_name,
                    user_count=active_users.count,
                    completion_rate=completion_rate,
                    avg_time_to_complete=None,
                    drop_off_rate=drop_off_rate,
                    status=status
                )
            
            elif step_type == "retention":
                # Users with current streak > 0
                total_users = self.supabase.table("users").select("id", count="exact").execute()
                retained_users = self.supabase.table("users").select("id", count="exact").gt("current_streak", 0).execute()
                
                completion_rate = retained_users.count / total_users.count if total_users.count > 0 else 0
                drop_off_rate = 1 - completion_rate
                
                status = HealthStatus.HEALTHY if completion_rate >= 0.4 else HealthStatus.WARNING
                
                return UserJourneyStep(
                    step_name=step_name,
                    user_count=retained_users.count,
                    completion_rate=completion_rate,
                    avg_time_to_complete=None,
                    drop_off_rate=drop_off_rate,
                    status=status
                )
            
            else:
                return UserJourneyStep(
                    step_name=step_name,
                    user_count=0,
                    completion_rate=0.0,
                    avg_time_to_complete=None,
                    drop_off_rate=1.0,
                    status=HealthStatus.UNKNOWN
                )
                
        except Exception as e:
            logger.error(f"Error analyzing journey step {step_type}: {e}")
            return UserJourneyStep(
                step_name=step_name,
                user_count=0,
                completion_rate=0.0,
                avg_time_to_complete=None,
                drop_off_rate=1.0,
                status=HealthStatus.CRITICAL
            )
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active system alerts"""
        alerts = []
        
        try:
            # Check for system issues that need attention
            
            # Low user activity alert
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            active_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", yesterday).execute()
            
            if active_users.count < 5:  # Threshold for concern
                alerts.append({
                    "severity": "warning",
                    "component": "user_activity",
                    "message": f"Low user activity: only {active_users.count} active users in last 24h",
                    "timestamp": datetime.now().isoformat(),
                    "suggested_action": "Check bot functionality and user engagement"
                })
            
            # Low commitment completion rate
            total_commits = self.supabase.table("commitments").select("id", count="exact").gte("created_at", yesterday).execute()
            completed_commits = self.supabase.table("commitments").select("id", count="exact").gte("completed_at", yesterday).execute()
            
            if total_commits.count > 0:
                completion_rate = completed_commits.count / total_commits.count
                if completion_rate < 0.3:
                    alerts.append({
                        "severity": "warning",
                        "component": "commitment_completion",
                        "message": f"Low commitment completion rate: {completion_rate:.1%} in last 24h",
                        "timestamp": datetime.now().isoformat(),
                        "suggested_action": "Review commitment difficulty and user support"
                    })
            
            # No new users alert
            new_users = self.supabase.table("users").select("id", count="exact").gte("created_at", yesterday).execute()
            if new_users.count == 0:
                alerts.append({
                    "severity": "info",
                    "component": "user_growth",
                    "message": "No new user registrations in last 24h",
                    "timestamp": datetime.now().isoformat(),
                    "suggested_action": "Check marketing and acquisition channels"
                })
            
        except Exception as e:
            alerts.append({
                "severity": "critical",
                "component": "monitoring_system",
                "message": f"Error generating alerts: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "suggested_action": "Check monitoring system functionality"
            })
        
        return alerts
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Calculate system uptime"""
        uptime_duration = datetime.now() - self.start_time
        
        return {
            "duration_seconds": uptime_duration.total_seconds(),
            "duration_human": str(uptime_duration).split('.')[0],  # Remove microseconds
            "started_at": self.start_time.isoformat()
        }
    
    async def _get_core_metrics(self) -> List[SystemMetric]:
        """Get core system performance metrics"""
        metrics = []
        
        try:
            # Total users
            total_users = self.supabase.table("users").select("id", count="exact").execute()
            metrics.append(SystemMetric(
                name="total_users",
                value=total_users.count,
                status=HealthStatus.HEALTHY,
                last_updated=datetime.now(),
                description="Total registered users"
            ))
            
            # Active users (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            active_users = self.supabase.table("users").select("id", count="exact").gte("last_activity_at", week_ago).execute()
            
            activity_rate = active_users.count / total_users.count if total_users.count > 0 else 0
            status = HealthStatus.HEALTHY if activity_rate >= 0.6 else HealthStatus.WARNING
            
            metrics.append(SystemMetric(
                name="weekly_active_users",
                value=active_users.count,
                status=status,
                last_updated=datetime.now(),
                description="Users active in last 7 days",
                target_value=int(total_users.count * 0.6)
            ))
            
            # Total commitments
            total_commitments = self.supabase.table("commitments").select("id", count="exact").execute()
            metrics.append(SystemMetric(
                name="total_commitments",
                value=total_commitments.count,
                status=HealthStatus.HEALTHY,
                last_updated=datetime.now(),
                description="Total commitments created"
            ))
            
            # Completion rate
            completed_commitments = self.supabase.table("commitments").select("id", count="exact").eq("status", "completed").execute()
            completion_rate = completed_commitments.count / total_commitments.count if total_commitments.count > 0 else 0
            
            completion_status = HealthStatus.HEALTHY if completion_rate >= 0.6 else HealthStatus.WARNING
            
            metrics.append(SystemMetric(
                name="completion_rate",
                value=f"{completion_rate:.1%}",
                status=completion_status,
                last_updated=datetime.now(),
                description="Overall commitment completion rate",
                target_value="60%",
                warning_threshold="40%"
            ))
            
        except Exception as e:
            logger.error(f"Error getting core metrics: {e}")
            metrics.append(SystemMetric(
                name="metrics_error",
                value=str(e),
                status=HealthStatus.CRITICAL,
                last_updated=datetime.now(),
                description="Error retrieving metrics"
            ))
        
        return metrics

# Web Dashboard
def create_dashboard_app(monitor: SystemMonitor) -> FastAPI:
    """Create FastAPI dashboard application"""
    
    app = FastAPI(title="Progress Method - System Monitor", version="1.0.0")
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home():
        """Main dashboard page"""
        overview = await monitor.get_system_overview()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Progress Method - System Monitor</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; padding: 20px; background: #f5f5f5; 
                }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .status-healthy {{ border-left: 4px solid #22c55e; }}
                .status-warning {{ border-left: 4px solid #f59e0b; }}
                .status-critical {{ border-left: 4px solid #ef4444; }}
                .status-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
                .healthy {{ background-color: #22c55e; }}
                .warning {{ background-color: #f59e0b; }}
                .critical {{ background-color: #ef4444; }}
                .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .metric-label {{ color: #666; font-size: 0.9em; }}
                .refresh-btn {{ 
                    background: #3b82f6; color: white; border: none; padding: 10px 20px; 
                    border-radius: 4px; cursor: pointer; margin-left: 10px;
                }}
                .alerts {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                .feature-list {{ max-height: 300px; overflow-y: auto; }}
                .feature-item {{ 
                    display: flex; justify-content: space-between; align-items: center; 
                    padding: 8px 0; border-bottom: 1px solid #eee; 
                }}
                pre {{ background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 0.85em; }}
            </style>
            <script>
                function refreshDashboard() {{
                    location.reload();
                }}
                
                // Auto-refresh every 30 seconds
                setInterval(refreshDashboard, 30000);
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Progress Method - System Monitor</h1>
                    <p>
                        <span class="status-indicator {overview.get('system_status', {}).get('status', 'unknown')}"></span>
                        System Status: <strong>{overview.get('system_status', {}).get('status', 'Unknown').title()}</strong>
                        <span style="margin-left: 20px;">
                            Health Score: <strong>{overview.get('system_status', {}).get('health_percentage', 0):.1f}%</strong>
                        </span>
                        <span style="float: right;">
                            Last Updated: {datetime.now().strftime('%H:%M:%S')}
                            <button class="refresh-btn" onclick="refreshDashboard()">Refresh</button>
                        </span>
                    </p>
                </div>
                
                {_generate_alerts_section(overview.get('alerts', []))}
                
                <div class="metrics-grid">
                    {_generate_metrics_cards(overview)}
                </div>
                
                <div style="margin-top: 30px;">
                    <h2>📊 Raw Data</h2>
                    <pre>{json.dumps(overview, indent=2, default=str)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    @app.get("/api/overview")
    async def api_overview():
        """API endpoint for system overview"""
        return await monitor.get_system_overview()
    
    @app.get("/api/metrics")
    async def api_metrics():
        """API endpoint for core metrics"""
        return await monitor._get_core_metrics()
    
    @app.get("/api/features")
    async def api_features():
        """API endpoint for feature status"""
        features = await monitor._get_all_features()
        return [asdict(f) for f in features]
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            health = await monitor._get_overall_health()
            return health
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    return app

def _generate_alerts_section(alerts: List[Dict]) -> str:
    """Generate HTML for alerts section"""
    if not alerts:
        return ""
    
    alerts_html = '<div class="alerts"><h3>⚠️ Active Alerts</h3><ul>'
    for alert in alerts:
        alerts_html += f"<li><strong>{alert['severity'].title()}:</strong> {alert['message']}</li>"
    alerts_html += '</ul></div>'
    
    return alerts_html

def _generate_metrics_cards(overview: Dict) -> str:
    """Generate HTML for metrics cards"""
    cards_html = ""
    
    # System health card
    system_status = overview.get('system_status', {})
    status_class = f"status-{system_status.get('status', 'unknown')}"
    
    cards_html += f"""
    <div class="metric-card {status_class}">
        <h3>System Health</h3>
        <div class="metric-value">{system_status.get('health_percentage', 0):.1f}%</div>
        <div class="metric-label">
            {system_status.get('healthy_components', 0)}/{system_status.get('total_components', 0)} components healthy
        </div>
    </div>
    """
    
    # Core metrics cards
    core_metrics = overview.get('core_metrics', [])
    for metric in core_metrics:
        status_class = f"status-{metric.get('status', 'unknown')}"
        cards_html += f"""
        <div class="metric-card {status_class}">
            <h3>{metric.get('name', 'Unknown').replace('_', ' ').title()}</h3>
            <div class="metric-value">{metric.get('value', 'N/A')}</div>
            <div class="metric-label">{metric.get('description', '')}</div>
        </div>
        """
    
    # Features card
    feature_status = overview.get('feature_status', {})
    cards_html += f"""
    <div class="metric-card">
        <h3>Features</h3>
        <div class="metric-value">{feature_status.get('production_features', 0)}</div>
        <div class="metric-label">Production features active</div>
        <div style="margin-top: 10px; font-size: 0.9em;">
            Total: {feature_status.get('total_features', 0)} | 
            Errors: {feature_status.get('features_with_errors', 0)}
        </div>
    </div>
    """
    
    # User journey card
    user_journey = overview.get('user_journey', {})
    cards_html += f"""
    <div class="metric-card">
        <h3>User Journey</h3>
        <div class="metric-value">{user_journey.get('avg_completion_rate', 0):.1%}</div>
        <div class="metric-label">Average completion rate</div>
        <div style="margin-top: 10px; font-size: 0.9em;">
            Status: {user_journey.get('overall_status', 'unknown').title()}
        </div>
    </div>
    """
    
    return cards_html

if __name__ == "__main__":
    # This would be run separately as a monitoring service
    print("System Monitor Dashboard - Use create_dashboard_app() to integrate with your main application")