#!/usr/bin/env python3
"""
Business Intelligence Dashboard
Based on Mixpanel-style behavioral analytics for The Progress Method
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

class BusinessIntelligenceDashboard:
    """Enhanced metrics dashboard with behavioral intelligence insights"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_key_business_metrics(self) -> Dict[str, Any]:
        """Get comprehensive business intelligence metrics"""
        try:
            # Core business metrics based on our 27.8% analysis
            metrics = {
                'onboarding_funnel': await self._get_onboarding_metrics(),
                'behavioral_insights': await self._get_behavioral_insights(),
                'commitment_intelligence': await self._get_commitment_analytics(),
                'retention_analysis': await self._get_retention_metrics(),
                'growth_indicators': await self._get_growth_metrics(),
                'system_health': await self._get_system_health_metrics()
            }
            
            return metrics
        except Exception as e:
            print(f"Error getting business metrics: {e}")
            return self._get_fallback_metrics()
    
    async def _get_onboarding_metrics(self) -> Dict[str, Any]:
        """Critical onboarding conversion metrics"""
        try:
            # Get user onboarding funnel data
            users_result = self.supabase.table('users').select('id, created_at').execute()
            commitments_result = self.supabase.table('commitments').select('user_id, created_at, completed_at').execute()
            
            if not users_result.data:
                return {'conversion_rate': 0, 'users_with_commitments': 0, 'total_users': 0}
            
            total_users = len(users_result.data)
            users_with_commitments = len(set(c['user_id'] for c in commitments_result.data)) if commitments_result.data else 0
            conversion_rate = (users_with_commitments / total_users * 100) if total_users > 0 else 0
            
            # Recent onboarding (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recent_users = len([u for u in users_result.data if u['created_at'] >= week_ago])
            
            return {
                'conversion_rate': round(conversion_rate, 1),
                'users_with_commitments': users_with_commitments,
                'total_users': total_users,
                'recent_signups': recent_users,
                'health_status': 'critical' if conversion_rate < 50 else 'warning' if conversion_rate < 70 else 'good',
                'target_rate': 80.0,
                'improvement_needed': max(0, 80.0 - conversion_rate)
            }
        except Exception as e:
            print(f"Error in onboarding metrics: {e}")
            return {'conversion_rate': 0, 'error': str(e)}
    
    async def _get_behavioral_insights(self) -> Dict[str, Any]:
        """Advanced behavioral pattern analysis"""
        try:
            commitments_result = self.supabase.table('commitments').select('*').execute()
            
            if not commitments_result.data:
                return {'completion_rate': 0, 'behavioral_patterns': []}
            
            commitments = commitments_result.data
            total_commitments = len(commitments)
            completed_commitments = len([c for c in commitments if c.get('completed_at')])
            completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # Analyze timing patterns
            completion_times = []
            for commit in commitments:
                if commit.get('created_at') and commit.get('completed_at'):
                    created = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00'))
                    completed_dt = datetime.fromisoformat(commit['completed_at'].replace('Z', '+00:00'))
                    hours_to_complete = (completed_dt - created).total_seconds() / 3600
                    completion_times.append(hours_to_complete)
            
            # Behavioral insights
            quick_completions = len([t for t in completion_times if t <= 24])
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            behavioral_patterns = []
            if quick_completions / len(completion_times) > 0.8 if completion_times else False:
                behavioral_patterns.append("Users prefer quick completion within 24 hours")
            if completion_rate < 50:
                behavioral_patterns.append("Critical: Commitment completion rate indicates difficulty issues")
            if avg_completion_time > 168:  # More than a week
                behavioral_patterns.append("Warning: Long completion times suggest procrastination patterns")
            
            return {
                'completion_rate': round(completion_rate, 1),
                'total_commitments': total_commitments,
                'completed_commitments': completed_commitments,
                'quick_completions': quick_completions,
                'avg_completion_hours': round(avg_completion_time, 1),
                'behavioral_patterns': behavioral_patterns,
                'health_status': 'critical' if completion_rate < 50 else 'warning' if completion_rate < 70 else 'good'
            }
        except Exception as e:
            print(f"Error in behavioral insights: {e}")
            return {'completion_rate': 0, 'error': str(e)}
    
    async def _get_commitment_analytics(self) -> Dict[str, Any]:
        """Detailed commitment performance analytics"""
        try:
            # Get commitment data with user correlation
            commitments_result = self.supabase.table('commitments').select('*').execute()
            users_result = self.supabase.table('users').select('id, created_at').execute()
            
            if not commitments_result.data or not users_result.data:
                return {'average_per_user': 0, 'commitment_trends': []}
            
            commitments = commitments_result.data
            users = {u['id']: u for u in users_result.data}
            
            # User engagement analysis
            user_commitment_counts = {}
            for commit in commitments:
                user_id = commit['user_id']
                user_commitment_counts[user_id] = user_commitment_counts.get(user_id, 0) + 1
            
            # Calculate metrics
            active_users = len(user_commitment_counts)
            total_users = len(users)
            avg_commitments_per_active_user = sum(user_commitment_counts.values()) / active_users if active_users > 0 else 0
            engagement_rate = (active_users / total_users * 100) if total_users > 0 else 0
            
            # Identify power users (top 20%)
            if user_commitment_counts:
                sorted_users = sorted(user_commitment_counts.values(), reverse=True)
                top_20_percent = int(len(sorted_users) * 0.2) or 1
                power_user_threshold = sorted_users[top_20_percent - 1]
                power_users = len([count for count in user_commitment_counts.values() if count >= power_user_threshold])
            else:
                power_users = 0
            
            return {
                'total_commitments': len(commitments),
                'active_users': active_users,
                'engagement_rate': round(engagement_rate, 1),
                'avg_commitments_per_user': round(avg_commitments_per_active_user, 1),
                'power_users': power_users,
                'inactive_users': total_users - active_users,
                'user_distribution': {
                    'no_commitments': total_users - active_users,
                    'light_users': len([c for c in user_commitment_counts.values() if 1 <= c <= 3]),
                    'active_users': len([c for c in user_commitment_counts.values() if 4 <= c <= 10]),
                    'power_users': len([c for c in user_commitment_counts.values() if c > 10])
                }
            }
        except Exception as e:
            print(f"Error in commitment analytics: {e}")
            return {'average_per_user': 0, 'error': str(e)}
    
    async def _get_retention_metrics(self) -> Dict[str, Any]:
        """User retention and cohort analysis"""
        try:
            users_result = self.supabase.table('users').select('id, created_at').execute()
            commitments_result = self.supabase.table('commitments').select('user_id, created_at').execute()
            
            if not users_result.data:
                return {'week_1_retention': 0, 'cohort_analysis': []}
            
            users = users_result.data
            commitments = commitments_result.data if commitments_result.data else []
            
            # Calculate retention metrics
            now = datetime.now()
            week_1_active = 0
            week_2_active = 0
            month_1_active = 0
            
            for user in users:
                user_signup = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                days_since_signup = (now - user_signup).days
                
                if days_since_signup >= 7:
                    # Check if user was active in week 1
                    week_1_start = user_signup + timedelta(days=7)
                    week_1_end = user_signup + timedelta(days=14)
                    week_1_commits = [c for c in commitments if c['user_id'] == user['id'] 
                                     and week_1_start <= datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) <= week_1_end]
                    if week_1_commits:
                        week_1_active += 1
                
                if days_since_signup >= 14:
                    week_2_start = user_signup + timedelta(days=14)
                    week_2_end = user_signup + timedelta(days=21)
                    week_2_commits = [c for c in commitments if c['user_id'] == user['id']
                                     and week_2_start <= datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) <= week_2_end]
                    if week_2_commits:
                        week_2_active += 1
                
                if days_since_signup >= 30:
                    month_1_commits = [c for c in commitments if c['user_id'] == user['id']
                                      and datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) >= user_signup + timedelta(days=30)]
                    if month_1_commits:
                        month_1_active += 1
            
            eligible_week_1 = len([u for u in users if (now - datetime.fromisoformat(u['created_at'].replace('Z', '+00:00'))).days >= 7])
            eligible_week_2 = len([u for u in users if (now - datetime.fromisoformat(u['created_at'].replace('Z', '+00:00'))).days >= 14])
            eligible_month_1 = len([u for u in users if (now - datetime.fromisoformat(u['created_at'].replace('Z', '+00:00'))).days >= 30])
            
            week_1_retention = (week_1_active / eligible_week_1 * 100) if eligible_week_1 > 0 else 0
            week_2_retention = (week_2_active / eligible_week_2 * 100) if eligible_week_2 > 0 else 0
            month_1_retention = (month_1_active / eligible_month_1 * 100) if eligible_month_1 > 0 else 0
            
            return {
                'week_1_retention': round(week_1_retention, 1),
                'week_2_retention': round(week_2_retention, 1),
                'month_1_retention': round(month_1_retention, 1),
                'eligible_users': {
                    'week_1': eligible_week_1,
                    'week_2': eligible_week_2,
                    'month_1': eligible_month_1
                },
                'active_users': {
                    'week_1': week_1_active,
                    'week_2': week_2_active,
                    'month_1': month_1_active
                },
                'health_status': 'good' if week_1_retention > 60 else 'warning' if week_1_retention > 40 else 'critical'
            }
        except Exception as e:
            print(f"Error in retention metrics: {e}")
            return {'week_1_retention': 0, 'error': str(e)}
    
    async def _get_growth_metrics(self) -> Dict[str, Any]:
        """Growth and trend analysis"""
        try:
            users_result = self.supabase.table('users').select('created_at').execute()
            commitments_result = self.supabase.table('commitments').select('created_at').execute()
            
            if not users_result.data:
                return {'daily_growth': [], 'growth_rate': 0}
            
            # Calculate growth metrics for last 30 days
            now = datetime.now()
            daily_signups = {}
            daily_commitments = {}
            
            for i in range(30):
                date = (now - timedelta(days=i)).date()
                daily_signups[date] = 0
                daily_commitments[date] = 0
            
            # Count daily signups
            for user in users_result.data:
                signup_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).date()
                if signup_date in daily_signups:
                    daily_signups[signup_date] += 1
            
            # Count daily commitments
            if commitments_result.data:
                for commit in commitments_result.data:
                    commit_date = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00')).date()
                    if commit_date in daily_commitments:
                        daily_commitments[commit_date] += 1
            
            # Calculate growth rate (last 7 days vs previous 7 days)
            last_week_signups = sum([daily_signups[now.date() - timedelta(days=i)] for i in range(7)])
            prev_week_signups = sum([daily_signups[now.date() - timedelta(days=i)] for i in range(7, 14)])
            growth_rate = ((last_week_signups - prev_week_signups) / prev_week_signups * 100) if prev_week_signups > 0 else 0
            
            return {
                'last_7_days_signups': last_week_signups,
                'prev_7_days_signups': prev_week_signups,
                'growth_rate': round(growth_rate, 1),
                'total_last_30_days': sum(daily_signups.values()),
                'avg_daily_signups': round(sum(daily_signups.values()) / 30, 1),
                'avg_daily_commitments': round(sum(daily_commitments.values()) / 30, 1),
                'trend': 'growing' if growth_rate > 5 else 'stable' if growth_rate > -5 else 'declining'
            }
        except Exception as e:
            print(f"Error in growth metrics: {e}")
            return {'growth_rate': 0, 'error': str(e)}
    
    async def _get_system_health_metrics(self) -> Dict[str, Any]:
        """System performance and health indicators"""
        try:
            # Check database responsiveness
            start_time = datetime.now()
            test_query = self.supabase.table('users').select('id').limit(1).execute()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # System health indicators
            db_healthy = response_time < 1000  # Less than 1 second
            data_available = test_query.data is not None
            
            health_score = 100
            if not db_healthy:
                health_score -= 30
            if not data_available:
                health_score -= 50
            
            return {
                'health_score': health_score,
                'database_response_time': round(response_time, 1),
                'database_status': 'healthy' if db_healthy else 'slow',
                'data_availability': 'available' if data_available else 'limited',
                'last_check': datetime.now().isoformat(),
                'status': 'healthy' if health_score > 80 else 'warning' if health_score > 50 else 'critical'
            }
        except Exception as e:
            print(f"Error in system health: {e}")
            return {'health_score': 0, 'status': 'error', 'error': str(e)}
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Fallback metrics when database is unavailable"""
        return {
            'onboarding_funnel': {'conversion_rate': 0, 'error': 'Database unavailable'},
            'behavioral_insights': {'completion_rate': 0, 'error': 'Database unavailable'},
            'commitment_analytics': {'average_per_user': 0, 'error': 'Database unavailable'},
            'retention_analysis': {'week_1_retention': 0, 'error': 'Database unavailable'},
            'growth_indicators': {'growth_rate': 0, 'error': 'Database unavailable'},
            'system_health': {'health_score': 0, 'status': 'error', 'error': 'Database unavailable'}
        }

# API endpoints for the enhanced dashboard
def create_business_intelligence_routes(app: FastAPI):
    """Add business intelligence routes to the FastAPI app"""
    
    if not supabase:
        return
    
    dashboard = BusinessIntelligenceDashboard(supabase)
    
    @app.get("/api/business-intelligence")
    async def get_business_intelligence():
        """Get comprehensive business intelligence metrics"""
        return await dashboard.get_key_business_metrics()
    
    @app.get("/api/onboarding-funnel")
    async def get_onboarding_funnel():
        """Get detailed onboarding conversion metrics"""
        return await dashboard._get_onboarding_metrics()
    
    @app.get("/api/behavioral-insights")
    async def get_behavioral_insights():
        """Get behavioral pattern analysis"""
        return await dashboard._get_behavioral_insights()
    
    @app.get("/api/retention-analysis")
    async def get_retention_analysis():
        """Get user retention and cohort metrics"""
        return await dashboard._get_retention_metrics()

if __name__ == "__main__":
    # Test the dashboard functionality
    import asyncio
    
    async def test_dashboard():
        if supabase:
            dashboard = BusinessIntelligenceDashboard(supabase)
            metrics = await dashboard.get_key_business_metrics()
            print("Business Intelligence Metrics:")
            for category, data in metrics.items():
                print(f"\n{category.upper()}:")
                print(f"  {data}")
        else:
            print("Supabase client not available")
    
    asyncio.run(test_dashboard())