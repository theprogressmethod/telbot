# Dream-Focused Analytics System for The Progress Method
# Aligns scoring with meaningful progress on important life goals

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from supabase import Client
import json

logger = logging.getLogger(__name__)

class DreamFocusedAnalytics:
    """Analytics system focused on dream progress, not gaming metrics"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_meaningful_stats(self, telegram_user_id: int) -> Dict:
        """Get stats focused on real progress toward dreams"""
        try:
            # Get user data
            user_result = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_user_id).execute()
            
            if not user_result.data:
                return self._empty_meaningful_stats()
            
            user = user_result.data[0]
            user_id = user["id"]
            
            # Get commitments with focus on quality
            commitments = self.supabase.table("commitments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            # Calculate meaningful metrics
            stats = {
                # Progress Metrics (not points)
                "weeks_active": await self._calculate_weeks_active(user_id),
                "consistency_score": await self._calculate_consistency_score(user_id),
                "commitment_quality": await self._calculate_quality_score(commitments.data),
                
                # Dream Alignment
                "dream_focused_commitments": await self._count_dream_aligned(commitments.data),
                "biggest_win_this_week": await self._get_biggest_win(user_id),
                "current_focus_area": await self._identify_focus_area(commitments.data),
                
                # Growth Indicators
                "improvement_trend": await self._calculate_improvement_trend(commitments.data),
                "reflection_depth": await self._measure_reflection_quality(user_id),
                "accountability_score": await self._calculate_accountability(user_id),
                
                # Momentum (not streaks)
                "momentum_state": await self._determine_momentum(user_id),
                "consistency_pattern": await self._identify_pattern(user_id),
                
                # Celebration Points (meaningful milestones)
                "milestones_reached": await self._get_milestones(user_id),
                "breakthrough_moments": await self._identify_breakthroughs(user_id),
                
                # Encouragement (not competition)
                "progress_message": await self._generate_progress_message(user_id),
                "next_focus": await self._suggest_next_focus(user_id),
                "strength_recognized": await self._identify_strength(commitments.data)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting meaningful stats: {e}")
            return self._empty_meaningful_stats()
    
    async def _calculate_weeks_active(self, user_id: str) -> int:
        """Count weeks with at least one commitment (consistency over volume)"""
        try:
            commitments = self.supabase.table("commitments").select("created_at").eq("user_id", user_id).execute()
            
            if not commitments.data:
                return 0
            
            weeks = set()
            for c in commitments.data:
                date = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).date()
                week_start = date - timedelta(days=date.weekday())
                weeks.add(week_start.isoformat())
            
            return len(weeks)
            
        except Exception as e:
            logger.error(f"Error calculating weeks active: {e}")
            return 0
    
    async def _calculate_consistency_score(self, user_id: str) -> Dict:
        """Measure consistency of engagement (not just streaks)"""
        try:
            # Look at last 4 weeks
            four_weeks_ago = date.today() - timedelta(weeks=4)
            
            commitments = self.supabase.table("commitments").select("created_at, status").eq("user_id", user_id).gte("created_at", four_weeks_ago.isoformat()).execute()
            
            # Group by week
            weeks_data = {}
            for c in commitments.data:
                date_obj = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).date()
                week_start = date_obj - timedelta(days=date_obj.weekday())
                week_key = week_start.isoformat()
                
                if week_key not in weeks_data:
                    weeks_data[week_key] = {"total": 0, "completed": 0}
                
                weeks_data[week_key]["total"] += 1
                if c.get("status") == "completed":
                    weeks_data[week_key]["completed"] += 1
            
            # Calculate consistency
            active_weeks = len(weeks_data)
            consistency_percent = (active_weeks / 4) * 100
            
            # Determine consistency level
            if consistency_percent >= 100:
                level = "🌟 Rock Solid"
            elif consistency_percent >= 75:
                level = "💪 Strong"
            elif consistency_percent >= 50:
                level = "📈 Building"
            else:
                level = "🌱 Starting"
            
            return {
                "percentage": round(consistency_percent, 0),
                "level": level,
                "weeks_active": active_weeks,
                "message": f"{active_weeks}/4 weeks active"
            }
            
        except Exception as e:
            logger.error(f"Error calculating consistency: {e}")
            return {"percentage": 0, "level": "🌱 Starting", "weeks_active": 0, "message": "Just getting started"}
    
    async def _calculate_quality_score(self, commitments: List[Dict]) -> Dict:
        """Measure commitment quality (specificity, not just SMART score)"""
        if not commitments:
            return {"average": 0, "trend": "➡️", "message": "No commitments yet"}
        
        # Recent quality
        recent = commitments[:10] if len(commitments) >= 10 else commitments
        recent_scores = [c.get("smart_score", 5) for c in recent]
        recent_avg = sum(recent_scores) / len(recent_scores)
        
        # Older quality for comparison
        if len(commitments) > 10:
            older = commitments[10:20]
            older_scores = [c.get("smart_score", 5) for c in older]
            older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
            
            trend = "📈" if recent_avg > older_avg else "📉" if recent_avg < older_avg else "➡️"
        else:
            trend = "🆕"
        
        return {
            "average": round(recent_avg, 1),
            "trend": trend,
            "message": self._get_quality_message(recent_avg)
        }
    
    def _get_quality_message(self, avg_score: float) -> str:
        """Generate message about commitment quality"""
        if avg_score >= 8:
            return "Crystal clear commitments!"
        elif avg_score >= 7:
            return "Well-defined goals"
        elif avg_score >= 6:
            return "Getting more specific"
        else:
            return "Try adding when/where/how"
    
    async def _count_dream_aligned(self, commitments: List[Dict]) -> int:
        """Count commitments that seem aligned with bigger goals"""
        # Look for patterns indicating dream alignment
        dream_keywords = [
            "project", "business", "health", "relationship", "skill",
            "learn", "build", "create", "improve", "develop", "practice",
            "study", "work on", "progress", "milestone"
        ]
        
        aligned_count = 0
        for c in commitments:
            text = c.get("commitment", "").lower()
            if any(keyword in text for keyword in dream_keywords):
                aligned_count += 1
        
        return aligned_count
    
    async def _get_biggest_win(self, user_id: str) -> Optional[str]:
        """Identify the biggest win this week"""
        try:
            week_start = date.today() - timedelta(days=date.today().weekday())
            
            completions = self.supabase.table("commitments").select("commitment, smart_score").eq("user_id", user_id).eq("status", "completed").gte("created_at", week_start.isoformat()).execute()
            
            if not completions.data:
                return None
            
            # Find highest quality completion
            best = max(completions.data, key=lambda x: x.get("smart_score", 0))
            return best.get("commitment", "A completed goal")
            
        except Exception as e:
            logger.error(f"Error getting biggest win: {e}")
            return None
    
    async def _identify_focus_area(self, commitments: List[Dict]) -> str:
        """Identify what area user is focusing on"""
        if not commitments:
            return "Exploring possibilities"
        
        # Simple categorization based on keywords
        categories = {
            "health": ["exercise", "workout", "run", "walk", "gym", "sleep", "meditate", "healthy", "diet"],
            "learning": ["read", "study", "learn", "course", "practice", "skill", "tutorial"],
            "work": ["work", "project", "task", "meeting", "email", "report", "presentation"],
            "personal": ["call", "family", "friend", "clean", "organize", "hobby"],
            "creation": ["write", "build", "create", "design", "make", "develop"]
        }
        
        category_counts = {cat: 0 for cat in categories}
        
        for c in commitments[:20]:  # Look at recent 20
            text = c.get("commitment", "").lower()
            for category, keywords in categories.items():
                if any(keyword in text for keyword in keywords):
                    category_counts[category] += 1
        
        if max(category_counts.values()) == 0:
            return "Diverse goals"
        
        focus = max(category_counts, key=category_counts.get)
        return focus.title()
    
    async def _calculate_improvement_trend(self, commitments: List[Dict]) -> str:
        """Identify if user is improving over time"""
        if len(commitments) < 4:
            return "📊 Building baseline"
        
        # Compare completion rates over time
        recent = commitments[:10]
        older = commitments[10:20] if len(commitments) >= 20 else commitments[5:10]
        
        recent_rate = len([c for c in recent if c.get("status") == "completed"]) / len(recent)
        older_rate = len([c for c in older if c.get("status") == "completed"]) / len(older) if older else 0
        
        if recent_rate > older_rate + 0.1:
            return "📈 Improving steadily"
        elif recent_rate < older_rate - 0.1:
            return "🔄 Adjusting approach"
        else:
            return "➡️ Maintaining rhythm"
    
    async def _determine_momentum(self, user_id: str) -> str:
        """Determine user's current momentum state"""
        try:
            # Check recent activity (last 7 days)
            week_ago = date.today() - timedelta(days=7)
            recent = self.supabase.table("commitments").select("created_at, status").eq("user_id", user_id).gte("created_at", week_ago.isoformat()).execute()
            
            if not recent.data:
                return "🌱 Ready to begin"
            
            completed = len([c for c in recent.data if c.get("status") == "completed"])
            total = len(recent.data)
            
            if completed >= 5:
                return "🔥 On fire!"
            elif completed >= 3:
                return "💪 Building momentum"
            elif total >= 3:
                return "🌊 Finding your flow"
            else:
                return "🌱 Planting seeds"
                
        except Exception as e:
            logger.error(f"Error determining momentum: {e}")
            return "🌱 Starting fresh"
    
    async def _generate_progress_message(self, user_id: str) -> str:
        """Generate an encouraging, personalized message"""
        weeks = await self._calculate_weeks_active(user_id)
        momentum = await self._determine_momentum(user_id)
        
        if weeks == 0:
            return "Welcome! Every master was once a beginner. What matters to you most?"
        elif weeks == 1:
            return "Great first week! You're building the foundation for lasting change."
        elif weeks < 4:
            return f"{weeks} weeks of showing up for yourself. That's how transformation begins!"
        elif "fire" in momentum.lower():
            return "You're in the zone! This is what consistent progress feels like."
        elif weeks < 12:
            return f"{weeks} weeks strong! You're proving you can stick with what matters."
        else:
            return f"{weeks} weeks of dedication. You're not the same person who started this journey!"
    
    async def _suggest_next_focus(self, user_id: str) -> str:
        """Suggest what to focus on next (not just more tasks)"""
        try:
            # Get recent patterns
            recent = self.supabase.table("commitments").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
            
            if not recent.data:
                return "Start with one small commitment that matters to you"
            
            # Analyze patterns
            avg_score = sum(c.get("smart_score", 5) for c in recent.data) / len(recent.data)
            completion_rate = len([c for c in recent.data if c.get("status") == "completed"]) / len(recent.data)
            
            if avg_score < 6:
                return "Try being more specific: add a time, place, or measurement"
            elif completion_rate < 0.5:
                return "Consider smaller steps that you can definitely complete"
            elif completion_rate > 0.8:
                return "You're ready for a bigger challenge! What's your next level?"
            else:
                return "Keep this rhythm going - you've found your sweet spot"
                
        except Exception as e:
            logger.error(f"Error suggesting focus: {e}")
            return "Focus on progress, not perfection"
    
    async def _identify_strength(self, commitments: List[Dict]) -> str:
        """Identify and celebrate user's strength"""
        if not commitments:
            return "Your willingness to start"
        
        completed = [c for c in commitments if c.get("status") == "completed"]
        
        if len(completed) > len(commitments) * 0.7:
            return "Your incredible follow-through"
        elif any(c.get("smart_score", 0) >= 8 for c in commitments[:5]):
            return "Your clarity and specificity"
        elif len(commitments) > 20:
            return "Your persistence and dedication"
        elif await self._identify_focus_area(commitments) != "Diverse goals":
            return "Your focused approach"
        else:
            return "Your commitment to growth"
    
    async def _get_milestones(self, user_id: str) -> List[str]:
        """Get meaningful milestones (not just numbers)"""
        milestones = []
        
        weeks = await self._calculate_weeks_active(user_id)
        if weeks >= 12:
            milestones.append("🏆 3 Month Warrior")
        elif weeks >= 4:
            milestones.append("📅 Month of Consistency")
        elif weeks >= 1:
            milestones.append("🌟 Week One Complete")
        
        return milestones
    
    async def _identify_breakthroughs(self, user_id: str) -> List[str]:
        """Identify breakthrough moments"""
        breakthroughs = []
        
        # This would ideally look for specific patterns
        # For now, return encouragement
        momentum = await self._determine_momentum(user_id)
        if "fire" in momentum.lower():
            breakthroughs.append("You're in your best streak ever!")
        
        return breakthroughs
    
    async def _identify_pattern(self, user_id: str) -> str:
        """Identify user's consistency pattern"""
        # Simplified for now
        return "Finding your rhythm"
    
    async def _measure_reflection_quality(self, user_id: str) -> str:
        """Measure how well user reflects (future feature with journal)"""
        return "Add reflection notes to deepen insights"
    
    async def _calculate_accountability(self, user_id: str) -> int:
        """Calculate accountability score (will integrate with pods)"""
        return 0  # Placeholder for pod integration
    
    def _empty_meaningful_stats(self) -> Dict:
        """Return empty stats structure focused on meaning"""
        return {
            "weeks_active": 0,
            "consistency_score": {"percentage": 0, "level": "🌱 Starting", "message": "Ready to begin"},
            "commitment_quality": {"average": 0, "trend": "🆕", "message": "Make your first commitment"},
            "dream_focused_commitments": 0,
            "biggest_win_this_week": None,
            "current_focus_area": "Exploring possibilities",
            "improvement_trend": "📊 Building baseline",
            "reflection_depth": "Add notes to track insights",
            "accountability_score": 0,
            "momentum_state": "🌱 Ready to begin",
            "consistency_pattern": "Just starting",
            "milestones_reached": [],
            "breakthrough_moments": [],
            "progress_message": "Welcome! Every journey begins with a single step.",
            "next_focus": "Start with one commitment that matters to you",
            "strength_recognized": "Your courage to begin"
        }
    
    async def format_meaningful_message(self, telegram_user_id: int) -> str:
        """Format stats into an inspiring, dream-focused message"""
        stats = await self.get_meaningful_stats(telegram_user_id)
        
        message = f"""
🌟 **Your Progress Journey**

**{stats['momentum_state']}**
{stats['consistency_score']['message']} • Focus: {stats['current_focus_area']}

**This Week's Highlight**
{stats['biggest_win_this_week'] or 'Your commitment to showing up'}

**What's Working**
Commitment Quality: {stats['commitment_quality']['message']}
Your Strength: {stats['strength_recognized']}
Trend: {stats['improvement_trend']}

**Milestones**
{' '.join(stats['milestones_reached']) if stats['milestones_reached'] else '🌱 Your journey is just beginning'}

💭 **{stats['progress_message']}**

**Next Step:** {stats['next_focus']}
"""
        
        return message