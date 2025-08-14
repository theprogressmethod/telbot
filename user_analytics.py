# User Analytics & Gamification System for The Progress Method
# Provides streaks, achievements, leaderboards, and visual progress tracking

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from supabase import Client
import json

logger = logging.getLogger(__name__)

class UserAnalytics:
    """Manages user analytics, streaks, and gamification"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
        # Achievement definitions
        self.ACHIEVEMENTS = {
            "first_commit": {
                "name": "🌱 First Step",
                "description": "Made your first commitment",
                "points": 10
            },
            "week_warrior": {
                "name": "📅 Week Warrior", 
                "description": "7-day commitment streak",
                "points": 50
            },
            "consistency_king": {
                "name": "👑 Consistency King",
                "description": "30-day commitment streak",
                "points": 200
            },
            "centurion": {
                "name": "💯 Centurion",
                "description": "100 total commitments",
                "points": 500
            },
            "perfect_week": {
                "name": "⭐ Perfect Week",
                "description": "100% completion rate for a week",
                "points": 100
            },
            "early_bird": {
                "name": "🌅 Early Bird",
                "description": "5 commitments before 9am",
                "points": 30
            },
            "comeback_kid": {
                "name": "💪 Comeback Kid",
                "description": "Restart after breaking a streak",
                "points": 25
            },
            "pod_perfect": {
                "name": "🎯 Pod Perfect",
                "description": "Attended all pod calls in a month",
                "points": 150
            }
        }
        
        # Streak milestones for celebration
        self.STREAK_MILESTONES = [3, 7, 14, 21, 30, 50, 75, 100, 150, 200, 365]
    
    async def get_user_stats(self, telegram_user_id: int) -> Dict:
        """Get comprehensive user statistics with gamification elements"""
        try:
            # Get user data
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return self._empty_stats()
            
            user = user_result.data[0]
            user_id = user["id"]
            
            # Get commitment stats
            commitments = self.supabase.table("commitments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            # Calculate metrics
            total_commitments = len(commitments.data)
            completed_commitments = len([c for c in commitments.data if c.get("status") == "completed"])
            completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # Calculate streaks
            current_streak, longest_streak = await self._calculate_streaks(user_id)
            
            # Check for streak milestone
            streak_milestone = self._get_streak_milestone(current_streak)
            
            # Calculate weekly stats
            week_stats = await self._get_weekly_stats(user_id)
            
            # Calculate points and level
            total_points = await self._calculate_total_points(user_id)
            level, next_level_points = self._calculate_level(total_points)
            
            # Get achievements
            achievements = await self._get_user_achievements(user_id)
            
            # Get rank among all users
            rank = await self._get_user_rank(user_id)
            
            # Compile stats with motivational elements
            stats = {
                # Core metrics
                "total_commitments": total_commitments,
                "completed_commitments": completed_commitments,
                "completion_rate": round(completion_rate, 1),
                
                # Streaks (dopamine drivers)
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "streak_milestone": streak_milestone,
                "days_until_next_milestone": self._days_to_next_milestone(current_streak),
                
                # Gamification
                "total_points": total_points,
                "level": level,
                "level_name": self._get_level_name(level),
                "points_to_next_level": next_level_points - total_points,
                "level_progress_percent": self._calculate_level_progress(total_points, level),
                
                # Weekly performance
                "this_week_completions": week_stats["completions"],
                "this_week_rate": week_stats["rate"],
                "week_over_week_change": week_stats["wow_change"],
                "weekly_trend": week_stats["trend"],  # "📈", "📉", or "➡️"
                
                # Achievements & Recognition
                "achievements_earned": len(achievements),
                "latest_achievement": achievements[0] if achievements else None,
                "total_achievement_points": sum(a.get("points", 0) for a in achievements),
                
                # Social/Competition
                "global_rank": rank["global"],
                "percentile": rank["percentile"],
                "rank_change": rank["change"],  # vs last week
                
                # Motivational messages
                "motivational_message": self._get_motivational_message(current_streak, completion_rate),
                "next_goal": self._get_next_goal(stats=locals())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return self._empty_stats()
    
    async def _calculate_streaks(self, user_id: str) -> Tuple[int, int]:
        """Calculate current and longest streaks"""
        try:
            # Get all commitments ordered by date
            commitments = self.supabase.table("commitments").select("created_at, status").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            if not commitments.data:
                return 0, 0
            
            # Group by date and check daily completion
            dates_with_completions = set()
            for c in commitments.data:
                if c.get("status") == "completed":
                    commit_date = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).date()
                    dates_with_completions.add(commit_date)
            
            if not dates_with_completions:
                return 0, 0
            
            # Calculate current streak
            current_streak = 0
            check_date = date.today()
            
            while check_date in dates_with_completions or check_date == date.today():
                if check_date in dates_with_completions:
                    current_streak += 1
                check_date -= timedelta(days=1)
                
                # Stop if we miss a day (except today)
                if check_date not in dates_with_completions and check_date != date.today() - timedelta(days=1):
                    break
            
            # Calculate longest streak
            sorted_dates = sorted(dates_with_completions)
            longest_streak = 1
            current_run = 1
            
            for i in range(1, len(sorted_dates)):
                if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
                    current_run += 1
                    longest_streak = max(longest_streak, current_run)
                else:
                    current_run = 1
            
            return current_streak, longest_streak
            
        except Exception as e:
            logger.error(f"Error calculating streaks: {e}")
            return 0, 0
    
    async def _get_weekly_stats(self, user_id: str) -> Dict:
        """Get this week's performance stats"""
        try:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            last_week_start = week_start - timedelta(days=7)
            
            # This week's commitments
            this_week = self.supabase.table("commitments").select("*").eq("user_id", user_id).gte("created_at", week_start.isoformat()).execute()
            
            # Last week's commitments
            last_week = self.supabase.table("commitments").select("*").eq("user_id", user_id).gte("created_at", last_week_start.isoformat()).lt("created_at", week_start.isoformat()).execute()
            
            # Calculate metrics
            this_week_total = len(this_week.data)
            this_week_completed = len([c for c in this_week.data if c.get("status") == "completed"])
            this_week_rate = (this_week_completed / this_week_total * 100) if this_week_total > 0 else 0
            
            last_week_total = len(last_week.data)
            last_week_completed = len([c for c in last_week.data if c.get("status") == "completed"])
            last_week_rate = (last_week_completed / last_week_total * 100) if last_week_total > 0 else 0
            
            # Week over week change
            wow_change = this_week_rate - last_week_rate
            trend = "📈" if wow_change > 5 else "📉" if wow_change < -5 else "➡️"
            
            return {
                "completions": this_week_completed,
                "total": this_week_total,
                "rate": round(this_week_rate, 1),
                "wow_change": round(wow_change, 1),
                "trend": trend
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return {"completions": 0, "total": 0, "rate": 0, "wow_change": 0, "trend": "➡️"}
    
    async def _calculate_total_points(self, user_id: str) -> int:
        """Calculate total points from commitments and achievements"""
        try:
            # Base points from commitments
            commitments = self.supabase.table("commitments").select("status").eq("user_id", user_id).execute()
            
            base_points = 0
            for c in commitments.data:
                if c.get("status") == "completed":
                    base_points += 10  # 10 points per completion
                else:
                    base_points += 2   # 2 points for trying
            
            # Bonus points from achievements
            achievements = await self._get_user_achievements(user_id)
            achievement_points = sum(a.get("points", 0) for a in achievements)
            
            return base_points + achievement_points
            
        except Exception as e:
            logger.error(f"Error calculating points: {e}")
            return 0
    
    def _calculate_level(self, total_points: int) -> Tuple[int, int]:
        """Calculate level from points (exponential growth)"""
        # Level thresholds: 0, 50, 150, 350, 700, 1250, 2050, 3150, 4600...
        level = 1
        points_needed = 50
        accumulated = 0
        
        while accumulated + points_needed <= total_points:
            accumulated += points_needed
            level += 1
            points_needed = int(points_needed * 1.5)  # Exponential growth
        
        next_level_points = accumulated + points_needed
        return level, next_level_points
    
    def _calculate_level_progress(self, total_points: int, level: int) -> float:
        """Calculate progress percentage to next level"""
        _, next_level_points = self._calculate_level(total_points)
        
        # Calculate previous level threshold
        prev_points = 0
        points_needed = 50
        for _ in range(level - 1):
            prev_points += points_needed
            points_needed = int(points_needed * 1.5)
        
        level_span = next_level_points - prev_points
        progress_in_level = total_points - prev_points
        
        return round((progress_in_level / level_span) * 100, 1)
    
    def _get_level_name(self, level: int) -> str:
        """Get motivational level name"""
        level_names = {
            1: "🌱 Beginner",
            2: "🌿 Growing",
            3: "🌳 Committed",
            4: "⭐ Dedicated",
            5: "🏆 Achiever",
            6: "💎 Expert",
            7: "🚀 Master",
            8: "🌟 Champion",
            9: "👑 Legend",
            10: "🔥 Mythic"
        }
        return level_names.get(min(level, 10), f"🌌 Level {level}")
    
    async def _get_user_achievements(self, user_id: str) -> List[Dict]:
        """Get user's earned achievements"""
        achievements = []
        
        try:
            # Get user's commitment data
            commitments = self.supabase.table("commitments").select("*").eq("user_id", user_id).execute()
            
            # Check each achievement condition
            if len(commitments.data) >= 1:
                achievements.append({**self.ACHIEVEMENTS["first_commit"], "earned_at": commitments.data[0]["created_at"]})
            
            # Check for streaks
            current_streak, longest_streak = await self._calculate_streaks(user_id)
            
            if current_streak >= 7 or longest_streak >= 7:
                achievements.append(self.ACHIEVEMENTS["week_warrior"])
            
            if current_streak >= 30 or longest_streak >= 30:
                achievements.append(self.ACHIEVEMENTS["consistency_king"])
            
            if len(commitments.data) >= 100:
                achievements.append(self.ACHIEVEMENTS["centurion"])
            
            # Sort by points (highest first)
            achievements.sort(key=lambda x: x.get("points", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
        
        return achievements
    
    async def _get_user_rank(self, user_id: str) -> Dict:
        """Get user's global rank"""
        try:
            # Get all users with their points
            all_users = self.supabase.table("users").select("id, total_commitments, completed_commitments").execute()
            
            # Calculate points for each user
            user_scores = []
            user_score = 0
            
            for u in all_users.data:
                score = u.get("completed_commitments", 0) * 10 + u.get("total_commitments", 0) * 2
                user_scores.append({"id": u["id"], "score": score})
                if u["id"] == user_id:
                    user_score = score
            
            # Sort by score
            user_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Find rank
            rank = next((i + 1 for i, u in enumerate(user_scores) if u["id"] == user_id), len(user_scores))
            percentile = round((1 - rank / len(user_scores)) * 100) if user_scores else 50
            
            return {
                "global": rank,
                "total_users": len(user_scores),
                "percentile": percentile,
                "change": 0  # TODO: Track rank changes
            }
            
        except Exception as e:
            logger.error(f"Error getting rank: {e}")
            return {"global": 0, "total_users": 0, "percentile": 50, "change": 0}
    
    def _get_streak_milestone(self, current_streak: int) -> Optional[Dict]:
        """Check if user hit a streak milestone"""
        if current_streak in self.STREAK_MILESTONES:
            return {
                "days": current_streak,
                "celebration": self._get_milestone_celebration(current_streak)
            }
        return None
    
    def _days_to_next_milestone(self, current_streak: int) -> int:
        """Calculate days until next streak milestone"""
        for milestone in self.STREAK_MILESTONES:
            if milestone > current_streak:
                return milestone - current_streak
        return 365 - current_streak  # Default to one year
    
    def _get_milestone_celebration(self, days: int) -> str:
        """Get celebration message for milestone"""
        celebrations = {
            3: "🎯 3 days strong! You're building momentum!",
            7: "🔥 One week streak! You're on fire!",
            14: "💪 Two weeks! You're unstoppable!",
            21: "🌟 21 days - a habit is born!",
            30: "👑 30 days! You're a consistency champion!",
            50: "🚀 50 days! You're in rare territory!",
            75: "💎 75 days of pure dedication!",
            100: "💯 CENTURY! You're a legend!",
            365: "🌟 ONE YEAR! You've achieved the impossible!"
        }
        return celebrations.get(days, f"🎊 {days} days! Incredible achievement!")
    
    def _get_motivational_message(self, streak: int, completion_rate: float) -> str:
        """Generate personalized motivational message"""
        if streak == 0 and completion_rate < 50:
            return "💪 Every journey starts with a single step. Make today count!"
        elif streak == 1:
            return "🌱 Great start! One day down, keep the momentum going!"
        elif streak < 7:
            return f"🔥 {streak} days strong! You're building something special!"
        elif streak < 30:
            return f"⚡ {streak} day streak! You're becoming unstoppable!"
        elif completion_rate >= 90:
            return "🏆 Elite performer! Your consistency is inspiring!"
        elif completion_rate >= 75:
            return "⭐ You're crushing it! Keep up the amazing work!"
        else:
            return "💫 You're on the right path. Consistency is your superpower!"
    
    def _get_next_goal(self, stats: Dict) -> str:
        """Suggest next goal based on current performance"""
        streak = stats.get("current_streak", 0)
        completion_rate = stats.get("completion_rate", 0)
        total = stats.get("total_commitments", 0)
        
        if streak == 0:
            return "🎯 Start a streak today!"
        elif streak < 7:
            return f"🎯 {7 - streak} days to a week streak!"
        elif completion_rate < 70:
            return "🎯 Boost your completion rate above 70%!"
        elif total < 100:
            return f"🎯 {100 - total} commitments to Centurion!"
        else:
            return f"🎯 {self._days_to_next_milestone(streak)} days to next milestone!"
    
    def _empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            "total_commitments": 0,
            "completed_commitments": 0,
            "completion_rate": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "streak_milestone": None,
            "days_until_next_milestone": 3,
            "total_points": 0,
            "level": 1,
            "level_name": "🌱 Beginner",
            "points_to_next_level": 50,
            "level_progress_percent": 0,
            "this_week_completions": 0,
            "this_week_rate": 0,
            "week_over_week_change": 0,
            "weekly_trend": "➡️",
            "achievements_earned": 0,
            "latest_achievement": None,
            "total_achievement_points": 0,
            "global_rank": 0,
            "percentile": 0,
            "rank_change": 0,
            "motivational_message": "🚀 Ready to start your journey? Make your first commitment!",
            "next_goal": "🎯 Make your first commitment!"
        }
    
    async def format_stats_message(self, telegram_user_id: int) -> str:
        """Format stats into a beautiful Telegram message"""
        stats = await self.get_user_stats(telegram_user_id)
        
        # Build the message with visual elements
        message = f"""
📊 **Your Progress Dashboard**

**Level {stats['level']}: {stats['level_name']}**
{self._create_progress_bar(stats['level_progress_percent'])} {stats['level_progress_percent']}%
📍 {stats['total_points']} pts | {stats['points_to_next_level']} to next level

**🔥 Streaks**
Current: {stats['current_streak']} days {'🎉' if stats['streak_milestone'] else ''}
Best: {stats['longest_streak']} days
{f"⏰ {stats['days_until_next_milestone']} days to next milestone!" if stats['current_streak'] > 0 else ''}

**📈 Performance**
Completion Rate: {stats['completion_rate']}% {self._get_rate_emoji(stats['completion_rate'])}
This Week: {stats['this_week_completions']} completed ({stats['this_week_rate']}%)
Trend: {stats['weekly_trend']} {'+' if stats['week_over_week_change'] > 0 else ''}{stats['week_over_week_change']}%

**🏆 Recognition**
Global Rank: #{stats['global_rank']} (Top {stats['percentile']}%)
Achievements: {stats['achievements_earned']} earned
{f"Latest: {stats['latest_achievement']['name']}" if stats['latest_achievement'] else ''}

**{stats['motivational_message']}**

{stats['next_goal']}
"""
        
        return message
    
    def _create_progress_bar(self, percentage: float) -> str:
        """Create visual progress bar"""
        filled = int(percentage / 10)
        empty = 10 - filled
        return "█" * filled + "░" * empty
    
    def _get_rate_emoji(self, rate: float) -> str:
        """Get emoji based on completion rate"""
        if rate >= 90:
            return "🏆"
        elif rate >= 75:
            return "⭐"
        elif rate >= 60:
            return "✅"
        elif rate >= 40:
            return "📈"
        else:
            return "💪"