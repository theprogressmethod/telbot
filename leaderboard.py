# Leaderboard System for The Progress Method
# Shows top performers to create healthy competition and motivation

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, date
from supabase import Client

logger = logging.getLogger(__name__)

class Leaderboard:
    """Manages leaderboards and competitive elements"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_weekly_leaderboard(self) -> Dict:
        """Get this week's top performers"""
        try:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            
            # Get all users and their weekly stats
            users = self.supabase.table("users").select("*").execute()
            
            leaderboard_data = []
            
            for user in users.data:
                user_id = user["id"]
                
                # Get this week's commitments
                week_commitments = self.supabase.table("commitments").select("*").eq("user_id", user_id).gte("created_at", week_start.isoformat()).execute()
                
                if week_commitments.data:
                    total = len(week_commitments.data)
                    completed = len([c for c in week_commitments.data if c.get("status") == "completed"])
                    rate = (completed / total * 100) if total > 0 else 0
                    
                    leaderboard_data.append({
                        "telegram_user_id": user.get("telegram_user_id"),
                        "name": user.get("first_name", "Anonymous"),
                        "username": user.get("username"),
                        "completed": completed,
                        "total": total,
                        "rate": round(rate, 1),
                        "points": completed * 10 + total * 2
                    })
            
            # Sort by points (highest first)
            leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
            
            return {
                "week_start": week_start.isoformat(),
                "week_end": (week_start + timedelta(days=6)).isoformat(),
                "total_participants": len(leaderboard_data),
                "top_performers": leaderboard_data[:10],  # Top 10
                "leaderboard": leaderboard_data
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly leaderboard: {e}")
            return {"top_performers": [], "total_participants": 0}
    
    async def get_all_time_leaderboard(self) -> Dict:
        """Get all-time top performers"""
        try:
            users = self.supabase.table("users").select("*").execute()
            
            leaderboard_data = []
            
            for user in users.data:
                total = user.get("total_commitments", 0)
                completed = user.get("completed_commitments", 0)
                rate = (completed / total * 100) if total > 0 else 0
                current_streak = user.get("current_streak", 0)
                
                # Calculate total points
                points = completed * 10 + total * 2 + current_streak * 5
                
                leaderboard_data.append({
                    "telegram_user_id": user.get("telegram_user_id"),
                    "name": user.get("first_name", "Anonymous"),
                    "username": user.get("username"),
                    "total_commitments": total,
                    "completed_commitments": completed,
                    "completion_rate": round(rate, 1),
                    "current_streak": current_streak,
                    "points": points
                })
            
            # Sort by points
            leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
            
            return {
                "total_users": len(leaderboard_data),
                "top_performers": leaderboard_data[:10],
                "leaderboard": leaderboard_data
            }
            
        except Exception as e:
            logger.error(f"Error getting all-time leaderboard: {e}")
            return {"top_performers": [], "total_users": 0}
    
    async def get_streak_leaderboard(self) -> List[Dict]:
        """Get top users by current streak"""
        try:
            users = self.supabase.table("users").select(
                "telegram_user_id, first_name, username, current_streak, longest_streak"
            ).order("current_streak", desc=True).limit(10).execute()
            
            return [{
                "rank": i + 1,
                "name": u.get("first_name", "Anonymous"),
                "username": u.get("username"),
                "current_streak": u.get("current_streak", 0),
                "longest_streak": u.get("longest_streak", 0),
                "emoji": self._get_streak_emoji(u.get("current_streak", 0))
            } for i, u in enumerate(users.data)]
            
        except Exception as e:
            logger.error(f"Error getting streak leaderboard: {e}")
            return []
    
    async def get_user_rank(self, telegram_user_id: int) -> Dict:
        """Get specific user's rank in various leaderboards"""
        try:
            # Get user data
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return {"weekly_rank": 0, "all_time_rank": 0, "streak_rank": 0}
            
            user = user_result.data[0]
            user_id = user["id"]
            
            # Get weekly rank
            weekly_board = await self.get_weekly_leaderboard()
            weekly_rank = next((i + 1 for i, u in enumerate(weekly_board["leaderboard"]) 
                               if u["telegram_user_id"] == telegram_user_id), 0)
            
            # Get all-time rank
            all_time_board = await self.get_all_time_leaderboard()
            all_time_rank = next((i + 1 for i, u in enumerate(all_time_board["leaderboard"]) 
                                 if u["telegram_user_id"] == telegram_user_id), 0)
            
            # Get streak rank
            all_users = self.supabase.table("users").select("current_streak").execute()
            user_streak = user.get("current_streak", 0)
            streak_rank = sum(1 for u in all_users.data if u.get("current_streak", 0) > user_streak) + 1
            
            return {
                "weekly_rank": weekly_rank,
                "weekly_total": len(weekly_board["leaderboard"]),
                "all_time_rank": all_time_rank,
                "all_time_total": len(all_time_board["leaderboard"]),
                "streak_rank": streak_rank,
                "streak_total": len(all_users.data)
            }
            
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return {"weekly_rank": 0, "all_time_rank": 0, "streak_rank": 0}
    
    async def format_weekly_leaderboard_message(self) -> str:
        """Format weekly leaderboard for Telegram"""
        board = await self.get_weekly_leaderboard()
        
        if not board["top_performers"]:
            return "🏆 No activity this week yet. Be the first to commit!"
        
        message = "🏆 **This Week's Leaderboard**\n\n"
        
        for i, user in enumerate(board["top_performers"][:10], 1):
            medal = self._get_rank_emoji(i)
            name = user['name'][:15]  # Truncate long names
            
            message += f"{medal} **{i}. {name}**\n"
            message += f"   📊 {user['completed']}/{user['total']} ({user['rate']}%)\n"
            message += f"   ⭐ {user['points']} pts\n\n"
        
        message += f"\n👥 Total participants: {board['total_participants']}"
        
        return message
    
    async def format_all_time_leaderboard_message(self) -> str:
        """Format all-time leaderboard for Telegram"""
        board = await self.get_all_time_leaderboard()
        
        if not board["top_performers"]:
            return "🏆 No users yet. Be the first!"
        
        message = "🏆 **All-Time Champions**\n\n"
        
        for i, user in enumerate(board["top_performers"][:10], 1):
            medal = self._get_rank_emoji(i)
            name = user['name'][:15]
            
            message += f"{medal} **{i}. {name}**\n"
            message += f"   ✅ {user['completed_commitments']} completed\n"
            message += f"   🔥 {user['current_streak']} day streak\n"
            message += f"   ⭐ {user['points']} total pts\n\n"
        
        message += f"\n👥 Total users: {board['total_users']}"
        
        return message
    
    async def format_streak_leaderboard_message(self) -> str:
        """Format streak leaderboard for Telegram"""
        streakers = await self.get_streak_leaderboard()
        
        if not streakers:
            return "🔥 No active streaks yet. Start yours today!"
        
        message = "🔥 **Current Streak Leaders**\n\n"
        
        for user in streakers:
            medal = self._get_rank_emoji(user['rank'])
            name = user['name'][:15]
            
            message += f"{medal} **{user['rank']}. {name}** {user['emoji']}\n"
            message += f"   Current: {user['current_streak']} days\n"
            message += f"   Best: {user['longest_streak']} days\n\n"
        
        return message
    
    def _get_rank_emoji(self, rank: int) -> str:
        """Get emoji for rank position"""
        emojis = {
            1: "🥇",
            2: "🥈", 
            3: "🥉",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟"
        }
        return emojis.get(rank, "▫️")
    
    def _get_streak_emoji(self, days: int) -> str:
        """Get emoji based on streak length"""
        if days >= 100:
            return "🌟"
        elif days >= 50:
            return "💎"
        elif days >= 30:
            return "🔥"
        elif days >= 14:
            return "⚡"
        elif days >= 7:
            return "✨"
        elif days >= 3:
            return "⭐"
        else:
            return "🌱"