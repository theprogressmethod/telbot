#!/usr/bin/env python3
"""
User-Facing Metrics System
Provides personalized insights and metrics that users can access through the bot
Based on behavioral intelligence analysis
"""

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

class UserFacingMetrics:
    """Generate personalized metrics and insights for individual users"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard with personal metrics"""
        try:
            return {
                'personal_stats': await self._get_personal_stats(user_id),
                'progress_tracking': await self._get_progress_tracking(user_id),
                'behavioral_insights': await self._get_user_behavioral_insights(user_id),
                'community_comparison': await self._get_community_comparison(user_id),
                'achievements': await self._get_achievements(user_id),
                'recommendations': await self._get_personalized_recommendations(user_id)
            }
        except Exception as e:
            print(f"Error getting user dashboard: {e}")
            return self._get_fallback_dashboard()
    
    async def _get_personal_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's personal commitment and progress statistics"""
        try:
            # Get user's commitments
            commitments_result = self.supabase.table('commitments').select('*').eq('user_id', user_id).execute()
            
            if not commitments_result.data:
                return {
                    'total_commitments': 0,
                    'completed_commitments': 0,
                    'completion_rate': 0,
                    'current_streak': 0,
                    'best_streak': 0
                }
            
            commitments = commitments_result.data
            total_commitments = len(commitments)
            completed_commitments = len([c for c in commitments if c.get('completed_at')])
            completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # Calculate streaks
            current_streak = self._calculate_current_streak(commitments)
            best_streak = self._calculate_best_streak(commitments)
            
            # Get user join date
            user_result = self.supabase.table('users').select('created_at').eq('id', user_id).execute()
            join_date = user_result.data[0]['created_at'] if user_result.data else None
            days_active = (datetime.now() - datetime.fromisoformat(join_date.replace('Z', '+00:00'))).days if join_date else 0
            
            return {
                'total_commitments': total_commitments,
                'completed_commitments': completed_commitments,
                'completion_rate': round(completion_rate, 1),
                'current_streak': current_streak,
                'best_streak': best_streak,
                'days_active': days_active,
                'avg_commitments_per_week': round((total_commitments / max(1, days_active / 7)), 1),
                'status': self._get_user_status(completion_rate, current_streak, total_commitments)
            }
        except Exception as e:
            print(f"Error in personal stats: {e}")
            return {'total_commitments': 0, 'error': str(e)}
    
    async def _get_progress_tracking(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress over time"""
        try:
            # Get commitments for last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            recent_commitments = self.supabase.table('commitments').select('*').eq('user_id', user_id).gte('created_at', thirty_days_ago).execute()
            
            if not recent_commitments.data:
                return {'trend': 'no_data', 'weekly_progress': [], 'monthly_summary': {}}
            
            commitments = recent_commitments.data
            
            # Weekly breakdown
            weekly_progress = []
            for week in range(4):
                week_start = datetime.now() - timedelta(days=(week + 1) * 7)
                week_end = datetime.now() - timedelta(days=week * 7)
                
                week_commitments = [
                    c for c in commitments 
                    if week_start <= datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) <= week_end
                ]
                
                completed = len([c for c in week_commitments if c.get('completed_at')])
                total = len(week_commitments)
                
                weekly_progress.append({
                    'week': f"Week {4-week}",
                    'total': total,
                    'completed': completed,
                    'completion_rate': (completed / total * 100) if total > 0 else 0
                })
            
            # Calculate trend
            recent_week = weekly_progress[0]['completion_rate'] if weekly_progress else 0
            previous_week = weekly_progress[1]['completion_rate'] if len(weekly_progress) > 1 else 0
            trend = 'improving' if recent_week > previous_week else 'declining' if recent_week < previous_week else 'stable'
            
            return {
                'trend': trend,
                'weekly_progress': weekly_progress,
                'monthly_summary': {
                    'total_commitments': len(commitments),
                    'completed': len([c for c in commitments if c.get('completed_at')]),
                    'avg_per_week': len(commitments) / 4
                },
                'improvement': recent_week - previous_week if previous_week > 0 else 0
            }
        except Exception as e:
            print(f"Error in progress tracking: {e}")
            return {'trend': 'error', 'error': str(e)}
    
    async def _get_user_behavioral_insights(self, user_id: str) -> Dict[str, Any]:
        """Get behavioral insights specific to this user"""
        try:
            commitments_result = self.supabase.table('commitments').select('*').eq('user_id', user_id).execute()
            
            if not commitments_result.data:
                return {'insights': [], 'behavioral_type': 'new_user'}
            
            commitments = commitments_result.data
            insights = []
            
            # Analyze completion patterns
            completion_times = []
            for commit in commitments:
                if commit.get('created_at') and commit.get('completed_at'):
                    created = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00'))
                    completed_dt = datetime.fromisoformat(commit['completed_at'].replace('Z', '+00:00'))
                    hours_to_complete = (completed_dt - created).total_seconds() / 3600
                    completion_times.append(hours_to_complete)
            
            # Generate behavioral insights
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
                quick_completions = len([t for t in completion_times if t <= 24])
                
                if quick_completions / len(completion_times) > 0.7:
                    insights.append("🚀 You're a Quick Completer! You tend to finish commitments within 24 hours.")
                elif avg_completion_time > 72:
                    insights.append("🤔 You prefer to take your time with commitments. Consider setting smaller, quicker wins.")
                
                if len(commitments) >= 10:
                    completion_rate = len([c for c in commitments if c.get('completed_at')]) / len(commitments) * 100
                    
                    if completion_rate > 80:
                        insights.append("⭐ Consistency Champion! Your completion rate is outstanding.")
                    elif completion_rate < 50:
                        insights.append("💪 Room for Growth: Try breaking commitments into smaller steps.")
            
            # Determine behavioral type
            total_commitments = len(commitments)
            completion_rate = len([c for c in commitments if c.get('completed_at')]) / total_commitments * 100 if total_commitments > 0 else 0
            
            if total_commitments >= 20 and completion_rate > 80:
                behavioral_type = 'high_achiever'
            elif total_commitments >= 10 and completion_rate > 60:
                behavioral_type = 'steady_performer'
            elif total_commitments >= 5:
                behavioral_type = 'building_momentum'
            else:
                behavioral_type = 'getting_started'
            
            return {
                'insights': insights,
                'behavioral_type': behavioral_type,
                'completion_pattern': 'quick' if quick_completions / len(completion_times) > 0.5 else 'thoughtful' if completion_times else 'unknown',
                'avg_completion_hours': round(avg_completion_time, 1) if completion_times else 0
            }
        except Exception as e:
            print(f"Error in behavioral insights: {e}")
            return {'insights': [], 'behavioral_type': 'unknown'}
    
    async def _get_community_comparison(self, user_id: str) -> Dict[str, Any]:
        """Compare user's performance to community averages"""
        try:
            # Get user's stats
            user_stats = await self._get_personal_stats(user_id)
            
            # Get community averages
            all_users = self.supabase.table('users').select('id').execute()
            if not all_users.data:
                return {'comparison': 'no_data'}
            
            all_commitments = self.supabase.table('commitments').select('user_id, completed_at').execute()
            if not all_commitments.data:
                return {'comparison': 'no_data'}
            
            # Calculate community stats
            commitments = all_commitments.data
            user_commitment_counts = {}
            for commit in commitments:
                uid = commit['user_id']
                user_commitment_counts[uid] = user_commitment_counts.get(uid, 0) + 1
            
            # Community averages
            active_users = len(user_commitment_counts)
            total_users = len(all_users.data)
            community_avg_commitments = sum(user_commitment_counts.values()) / active_users if active_users > 0 else 0
            
            # Community completion rate
            total_commitments = len(commitments)
            completed_commitments = len([c for c in commitments if c.get('completed_at')])
            community_completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # User vs community comparison
            user_vs_avg_commitments = user_stats['total_commitments'] / community_avg_commitments if community_avg_commitments > 0 else 0
            user_vs_avg_completion = user_stats['completion_rate'] / community_completion_rate if community_completion_rate > 0 else 0
            
            # Percentile calculation
            user_commitment_count = user_stats['total_commitments']
            users_with_fewer_commitments = len([count for count in user_commitment_counts.values() if count < user_commitment_count])
            percentile = (users_with_fewer_commitments / active_users * 100) if active_users > 0 else 0
            
            return {
                'community_avg_commitments': round(community_avg_commitments, 1),
                'community_completion_rate': round(community_completion_rate, 1),
                'user_vs_avg_commitments': round(user_vs_avg_commitments, 2),
                'user_vs_avg_completion': round(user_vs_avg_completion, 2),
                'percentile': round(percentile, 1),
                'rank_description': self._get_rank_description(percentile),
                'active_community_size': active_users
            }
        except Exception as e:
            print(f"Error in community comparison: {e}")
            return {'comparison': 'error', 'error': str(e)}
    
    async def _get_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get user's achievements and milestones"""
        try:
            user_stats = await self._get_personal_stats(user_id)
            
            achievements = []
            upcoming_milestones = []
            
            # Achievement logic
            total = user_stats['total_commitments']
            completed = user_stats['completed_commitments']
            completion_rate = user_stats['completion_rate']
            streak = user_stats['current_streak']
            
            # Commitment milestones
            if total >= 1: achievements.append("🎯 First Commitment")
            if total >= 5: achievements.append("🔥 5 Commitments")
            if total >= 10: achievements.append("💪 Double Digits")
            if total >= 25: achievements.append("🚀 Quarter Century")
            if total >= 50: achievements.append("⭐ Half Century")
            if total >= 100: achievements.append("🏆 Centurion")
            
            # Completion achievements
            if completed >= 1: achievements.append("✅ First Completion")
            if completion_rate >= 50: achievements.append("📈 50% Club")
            if completion_rate >= 75: achievements.append("🎖️ 75% Club")
            if completion_rate >= 90: achievements.append("🥇 90% Club")
            if completion_rate == 100 and total >= 5: achievements.append("💎 Perfect Record")
            
            # Streak achievements
            if streak >= 3: achievements.append("🔥 3-Day Streak")
            if streak >= 7: achievements.append("📅 Weekly Warrior")
            if streak >= 30: achievements.append("🌟 Monthly Master")
            
            # Upcoming milestones
            next_commitment_milestone = next((m for m in [5, 10, 25, 50, 100] if m > total), None)
            if next_commitment_milestone:
                upcoming_milestones.append(f"🎯 {next_commitment_milestone} Commitments ({next_commitment_milestone - total} to go)")
            
            if completion_rate < 75:
                upcoming_milestones.append(f"📈 75% Completion Rate ({75 - completion_rate:.1f}% to go)")
            
            return {
                'earned_achievements': achievements,
                'upcoming_milestones': upcoming_milestones,
                'achievement_count': len(achievements),
                'next_milestone': upcoming_milestones[0] if upcoming_milestones else "🏆 You're at the top!"
            }
        except Exception as e:
            print(f"Error in achievements: {e}")
            return {'earned_achievements': [], 'upcoming_milestones': []}
    
    async def _get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations based on user's patterns"""
        try:
            user_stats = await self._get_personal_stats(user_id)
            behavioral_insights = await self._get_user_behavioral_insights(user_id)
            
            recommendations = []
            
            # Based on completion rate
            if user_stats['completion_rate'] < 50:
                recommendations.append({
                    'type': 'improvement',
                    'title': 'Try Micro-Commitments',
                    'description': 'Break your goals into smaller, 5-minute commitments to build momentum.',
                    'action': 'Create a micro-commitment now'
                })
            
            # Based on behavioral type
            behavioral_type = behavioral_insights['behavioral_type']
            
            if behavioral_type == 'getting_started':
                recommendations.append({
                    'type': 'guidance',
                    'title': 'Build Your Foundation',
                    'description': 'Focus on consistency over complexity. Aim for 3 simple commitments this week.',
                    'action': 'Set a simple daily commitment'
                })
            elif behavioral_type == 'building_momentum':
                recommendations.append({
                    'type': 'growth',
                    'title': 'Scale Gradually',
                    'description': 'You\'re building good habits! Try slightly longer commitments (10-15 minutes).',
                    'action': 'Create a medium commitment'
                })
            elif behavioral_type == 'steady_performer':
                recommendations.append({
                    'type': 'challenge',
                    'title': 'Ready for a Challenge',
                    'description': 'Your consistency is strong. Consider a weekly challenge or goal.',
                    'action': 'Set a weekly challenge'
                })
            elif behavioral_type == 'high_achiever':
                recommendations.append({
                    'type': 'leadership',
                    'title': 'Inspire Others',
                    'description': 'Share your success strategies with the community!',
                    'action': 'Join a pod as a mentor'
                })
            
            # Based on completion patterns
            if behavioral_insights['completion_pattern'] == 'quick':
                recommendations.append({
                    'type': 'optimization',
                    'title': 'Leverage Your Speed',
                    'description': 'You complete things quickly! Try batching similar commitments.',
                    'action': 'Create related commitments'
                })
            
            # Time-based recommendations
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 10:
                recommendations.append({
                    'type': 'timing',
                    'title': 'Morning Energy',
                    'description': 'Great time for commitments! Morning energy is typically highest.',
                    'action': 'Create a morning commitment'
                })
            elif 14 <= current_hour <= 16:
                recommendations.append({
                    'type': 'timing',
                    'title': 'Afternoon Boost',
                    'description': 'Beat the afternoon slump with a quick energy commitment.',
                    'action': 'Try a 5-minute movement break'
                })
            
            return {
                'recommendations': recommendations[:3],  # Limit to top 3
                'total_available': len(recommendations),
                'personalization_score': len(recommendations) * 20  # Score out of 100
            }
        except Exception as e:
            print(f"Error in recommendations: {e}")
            return {'recommendations': [], 'error': str(e)}
    
    # Helper methods
    def _calculate_current_streak(self, commitments: List[Dict]) -> int:
        """Calculate current consecutive completion streak"""
        if not commitments:
            return 0
        
        # Sort by creation date, most recent first
        sorted_commitments = sorted(commitments, key=lambda x: x['created_at'], reverse=True)
        
        streak = 0
        for commit in sorted_commitments:
            if commit.get('completed_at'):
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_best_streak(self, commitments: List[Dict]) -> int:
        """Calculate best ever consecutive completion streak"""
        if not commitments:
            return 0
        
        # Sort by creation date
        sorted_commitments = sorted(commitments, key=lambda x: x['created_at'])
        
        best_streak = 0
        current_streak = 0
        
        for commit in sorted_commitments:
            if commit.get('completed_at'):
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 0
        
        return best_streak
    
    def _get_user_status(self, completion_rate: float, streak: int, total_commitments: int) -> str:
        """Determine user's current status"""
        if total_commitments == 0:
            return 'new_user'
        elif completion_rate >= 80 and streak >= 5:
            return 'on_fire'
        elif completion_rate >= 60 and total_commitments >= 10:
            return 'steady'
        elif completion_rate >= 40:
            return 'building'
        else:
            return 'needs_support'
    
    def _get_rank_description(self, percentile: float) -> str:
        """Get description of user's rank in community"""
        if percentile >= 90:
            return 'Top 10% - Elite Performer'
        elif percentile >= 75:
            return 'Top 25% - High Achiever'
        elif percentile >= 50:
            return 'Top 50% - Above Average'
        elif percentile >= 25:
            return 'Active Member'
        else:
            return 'Getting Started'
    
    def _get_fallback_dashboard(self) -> Dict[str, Any]:
        """Fallback dashboard when data is unavailable"""
        return {
            'personal_stats': {'total_commitments': 0, 'error': 'Data unavailable'},
            'progress_tracking': {'trend': 'no_data'},
            'behavioral_insights': {'insights': [], 'behavioral_type': 'unknown'},
            'community_comparison': {'comparison': 'no_data'},
            'achievements': {'earned_achievements': [], 'upcoming_milestones': []},
            'recommendations': {'recommendations': []}
        }

# Bot command handlers
def format_user_metrics_message(metrics: Dict[str, Any]) -> str:
    """Format user metrics into a readable bot message"""
    
    personal = metrics.get('personal_stats', {})
    progress = metrics.get('progress_tracking', {})
    achievements = metrics.get('achievements', {})
    recommendations = metrics.get('recommendations', {})
    
    message = f"""
📊 **Your Progress Dashboard**

🎯 **Personal Stats**
• Total Commitments: {personal.get('total_commitments', 0)}
• Completed: {personal.get('completed_commitments', 0)}
• Success Rate: {personal.get('completion_rate', 0)}%
• Current Streak: {personal.get('current_streak', 0)} days
• Days Active: {personal.get('days_active', 0)}

📈 **Recent Progress**
• Trend: {progress.get('trend', 'Unknown').title()}
• This Month: {progress.get('monthly_summary', {}).get('total_commitments', 0)} commitments

🏆 **Achievements** ({achievements.get('achievement_count', 0)} earned)
{chr(10).join(f"• {achievement}" for achievement in achievements.get('earned_achievements', [])[:5]) or "• Start completing commitments to earn achievements!"}

💡 **Next Steps**
{chr(10).join(f"• {rec.get('title', '')}: {rec.get('description', '')}" for rec in recommendations.get('recommendations', [])[:2]) or "• Keep building your commitment habit!"}

Type `/insights` for detailed behavioral analysis!
"""
    
    return message.strip()

def format_quick_stats_message(metrics: Dict[str, Any]) -> str:
    """Format quick stats for inline bot responses"""
    
    personal = metrics.get('personal_stats', {})
    
    status_emoji = {
        'on_fire': '🔥',
        'steady': '💪', 
        'building': '📈',
        'needs_support': '🤝',
        'new_user': '🌱'
    }.get(personal.get('status', 'new_user'), '📊')
    
    return f"""{status_emoji} **Quick Stats**
{personal.get('completed_commitments', 0)}/{personal.get('total_commitments', 0)} completed ({personal.get('completion_rate', 0)}%) • {personal.get('current_streak', 0)}-day streak"""

if __name__ == "__main__":
    # Test the user metrics functionality
    import asyncio
    
    async def test_user_metrics():
        if supabase:
            metrics = UserFacingMetrics(supabase)
            
            # Get sample user data
            users_result = supabase.table('users').select('id').limit(1).execute()
            if users_result.data:
                user_id = users_result.data[0]['id']
                dashboard = await metrics.get_user_dashboard(user_id)
                
                print("User Dashboard:")
                for category, data in dashboard.items():
                    print(f"\n{category.upper()}:")
                    print(f"  {data}")
                
                print("\n" + "="*50)
                print("Formatted Bot Message:")
                print(format_user_metrics_message(dashboard))
            else:
                print("No users found for testing")
        else:
            print("Supabase client not available")
    
    asyncio.run(test_user_metrics())