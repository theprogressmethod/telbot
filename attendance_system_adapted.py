#!/usr/bin/env python3
"""
Attendance System Adapted for Existing Database Schema
Works with existing pod_meetings and meeting_attendance tables
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from supabase import Client

logger = logging.getLogger(__name__)

class AttendanceStatus(Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EARLY_DEPARTURE = "early_departure"
    PARTIAL = "partial"

class MeetingStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AttendancePattern(Enum):
    PERFECT_ATTENDER = "perfect_attender"    # 95%+ attendance
    REGULAR_ATTENDER = "regular_attender"    # 80-95% attendance
    INCONSISTENT = "inconsistent"            # 50-80% attendance
    FREQUENT_MISSER = "frequent_misser"      # 20-50% attendance
    GHOST_MEMBER = "ghost_member"            # <20% attendance

class EngagementLevel(Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    CRITICAL = "critical"

@dataclass
class PodMeeting:
    """Represents a pod meeting using existing schema"""
    id: str
    pod_id: str
    meeting_date: str  # Date string
    status: str
    created_at: datetime

@dataclass
class AttendanceRecord:
    """Attendance record using existing schema"""
    id: str
    meeting_id: str
    user_id: str
    attended: bool
    duration_minutes: int
    created_at: datetime

@dataclass
class AttendanceAnalytics:
    """Calculated attendance analytics for a user"""
    user_id: str
    pod_id: str
    total_scheduled_meetings: int
    meetings_attended: int
    meetings_missed: int
    attendance_rate: float
    average_duration: float
    current_streak: int
    longest_streak: int
    attendance_pattern: AttendancePattern
    engagement_level: EngagementLevel
    last_attendance_date: Optional[datetime]
    prediction_score: float
    risk_flags: List[str]
    calculated_at: datetime

@dataclass
class AttendanceInsight:
    """AI-generated insights about attendance patterns"""
    insight_id: str
    pod_id: str
    user_id: Optional[str]
    insight_type: str
    priority: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    recommendation: str
    data_points: Dict[str, Any]
    confidence_score: float
    created_at: datetime

class AttendanceSystemAdapted:
    """Attendance system adapted to work with existing database schema"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_expiry = timedelta(minutes=15)
        
        logger.info("✅ Adapted Attendance System initialized")
    
    async def create_pod_meeting(self, pod_id: str, meeting_date: str, status: str = "scheduled") -> PodMeeting:
        """Create a new pod meeting"""
        try:
            meeting_id = str(uuid.uuid4())
            
            data = {
                "id": meeting_id,
                "pod_id": pod_id,
                "meeting_date": meeting_date,
                "status": status,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("pod_meetings").insert(data).execute()
            
            if result.data:
                meeting_data = result.data[0]
                meeting = PodMeeting(
                    id=meeting_data["id"],
                    pod_id=meeting_data["pod_id"],
                    meeting_date=meeting_data["meeting_date"],
                    status=meeting_data["status"],
                    created_at=datetime.fromisoformat(meeting_data["created_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"✅ Created pod meeting {meeting.id} for pod {pod_id}")
                return meeting
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"❌ Error creating pod meeting: {e}")
            raise
    
    async def record_attendance(self, meeting_id: str, user_id: str, attended: bool = True, 
                              duration_minutes: int = 60) -> AttendanceRecord:
        """Record attendance for a user at a meeting"""
        try:
            record_id = str(uuid.uuid4())
            
            data = {
                "id": record_id,
                "meeting_id": meeting_id,
                "user_id": user_id,
                "attended": attended,
                "duration_minutes": duration_minutes,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("meeting_attendance").insert(data).execute()
            
            if result.data:
                record_data = result.data[0]
                record = AttendanceRecord(
                    id=record_data["id"],
                    meeting_id=record_data["meeting_id"],
                    user_id=record_data["user_id"],
                    attended=record_data["attended"],
                    duration_minutes=record_data["duration_minutes"],
                    created_at=datetime.fromisoformat(record_data["created_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"📋 Recorded attendance for user {user_id} in meeting {meeting_id}: {'present' if attended else 'absent'}")
                return record
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"❌ Error recording attendance: {e}")
            raise
    
    async def get_user_attendance_history(self, user_id: str, pod_id: str, weeks_back: int = 12) -> List[AttendanceRecord]:
        """Get user's attendance history for a pod"""
        try:
            cutoff_date = (datetime.now() - timedelta(weeks=weeks_back)).isoformat()
            
            # Get meetings for the pod
            meetings_result = self.supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).gte("created_at", cutoff_date).execute()
            
            if not meetings_result.data:
                return []
            
            meeting_ids = [m["id"] for m in meetings_result.data]
            
            # Get attendance records for this user at these meetings
            attendance_result = self.supabase.table("meeting_attendance").select("*").eq("user_id", user_id).in_("meeting_id", meeting_ids).execute()
            
            records = []
            for record_data in attendance_result.data:
                record = AttendanceRecord(
                    id=record_data["id"],
                    meeting_id=record_data["meeting_id"],
                    user_id=record_data["user_id"],
                    attended=record_data["attended"],
                    duration_minutes=record_data["duration_minutes"],
                    created_at=datetime.fromisoformat(record_data["created_at"].replace('Z', '+00:00'))
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error getting attendance history: {e}")
            return []
    
    async def calculate_user_attendance_analytics(self, user_id: str, pod_id: str, weeks_back: int = 12) -> AttendanceAnalytics:
        """Calculate comprehensive attendance analytics for a user"""
        try:
            # Check cache first
            cache_key = f"{user_id}:{pod_id}:{weeks_back}"
            if cache_key in self.analytics_cache:
                cached = self.analytics_cache[cache_key]
                if datetime.now() < cached["expires_at"]:
                    return cached["analytics"]
            
            # Get attendance history
            attendance_history = await self.get_user_attendance_history(user_id, pod_id, weeks_back)
            
            # Get total scheduled meetings for this pod in the period
            cutoff_date = (datetime.now() - timedelta(weeks=weeks_back)).isoformat()
            meetings_result = self.supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).gte("created_at", cutoff_date).execute()
            total_scheduled = len(meetings_result.data) if meetings_result.data else 0
            
            if total_scheduled == 0:
                return self._create_empty_analytics(user_id, pod_id)
            
            # Calculate basic metrics
            meetings_attended = len([r for r in attendance_history if r.attended])
            meetings_missed = total_scheduled - meetings_attended
            attendance_rate = meetings_attended / total_scheduled if total_scheduled > 0 else 0
            
            # Calculate average duration for attended meetings
            attended_durations = [r.duration_minutes for r in attendance_history if r.attended]
            average_duration = sum(attended_durations) / len(attended_durations) if attended_durations else 0
            
            # Calculate streaks
            current_streak, longest_streak = self._calculate_attendance_streaks(attendance_history)
            
            # Determine patterns and engagement level
            attendance_pattern = self._classify_attendance_pattern(attendance_rate)
            engagement_level = self._assess_engagement_level(attendance_rate, average_duration)
            
            # Get last attendance date
            last_attendance = None
            for record in sorted(attendance_history, key=lambda x: x.created_at, reverse=True):
                if record.attended:
                    last_attendance = record.created_at
                    break
            
            # Calculate prediction score
            prediction_score = self._calculate_prediction_score(attendance_history)
            
            # Identify risk flags
            risk_flags = self._identify_risk_flags(attendance_history, attendance_rate)
            
            analytics = AttendanceAnalytics(
                user_id=user_id,
                pod_id=pod_id,
                total_scheduled_meetings=total_scheduled,
                meetings_attended=meetings_attended,
                meetings_missed=meetings_missed,
                attendance_rate=attendance_rate,
                average_duration=average_duration,
                current_streak=current_streak,
                longest_streak=longest_streak,
                attendance_pattern=attendance_pattern,
                engagement_level=engagement_level,
                last_attendance_date=last_attendance,
                prediction_score=prediction_score,
                risk_flags=risk_flags,
                calculated_at=datetime.now()
            )
            
            # Cache the results
            self.analytics_cache[cache_key] = {
                "analytics": analytics,
                "expires_at": datetime.now() + self.cache_expiry
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error calculating attendance analytics: {e}")
            return self._create_empty_analytics(user_id, pod_id)
    
    async def get_pod_attendance_summary(self, pod_id: str, weeks_back: int = 4) -> Dict[str, Any]:
        """Get comprehensive attendance summary for a pod"""
        try:
            cutoff_date = (datetime.now() - timedelta(weeks=weeks_back)).isoformat()
            
            # Get all meetings for this pod
            meetings_result = self.supabase.table("pod_meetings").select("*").eq("pod_id", pod_id).gte("created_at", cutoff_date).execute()
            total_meetings = len(meetings_result.data) if meetings_result.data else 0
            
            # Get all attendance records for these meetings
            if meetings_result.data:
                meeting_ids = [m["id"] for m in meetings_result.data]
                attendance_result = self.supabase.table("meeting_attendance").select("*").in_("meeting_id", meeting_ids).execute()
                attendance_records = attendance_result.data or []
            else:
                attendance_records = []
            
            # Get pod members count
            members_result = self.supabase.table("pod_memberships").select("user_id").eq("pod_id", pod_id).eq("is_active", True).execute()
            member_count = len(members_result.data) if members_result.data else 0
            
            # Calculate metrics
            total_possible_attendance = total_meetings * member_count
            total_actual_attendance = len([r for r in attendance_records if r["attended"]])
            pod_attendance_rate = total_actual_attendance / total_possible_attendance if total_possible_attendance > 0 else 0
            
            # Get member analytics
            member_analytics = []
            if members_result.data:
                for member in members_result.data:
                    analytics = await self.calculate_user_attendance_analytics(member["user_id"], pod_id, weeks_back)
                    member_analytics.append(analytics)
            
            # Identify high performers and at-risk members
            high_performers = [a for a in member_analytics if a.attendance_pattern == AttendancePattern.PERFECT_ATTENDER]
            at_risk_members = [a for a in member_analytics if a.engagement_level == EngagementLevel.CRITICAL]
            
            return {
                "pod_id": pod_id,
                "summary_period_weeks": weeks_back,
                "total_meetings": total_meetings,
                "pod_attendance_rate": pod_attendance_rate,
                "average_meeting_size": total_actual_attendance / total_meetings if total_meetings > 0 else 0,
                "member_count": member_count,
                "high_performers": len(high_performers),
                "at_risk_members": len(at_risk_members),
                "member_analytics": [asdict(a) for a in member_analytics],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating pod summary: {e}")
            return {"error": str(e)}
    
    async def generate_attendance_insights(self, pod_id: str = None, user_id: str = None) -> List[AttendanceInsight]:
        """Generate AI-driven insights about attendance patterns"""
        insights = []
        
        try:
            if user_id and pod_id:
                analytics = await self.calculate_user_attendance_analytics(user_id, pod_id)
                user_insights = self._generate_user_insights(analytics)
                insights.extend(user_insights)
            
            if pod_id:
                pod_summary = await self.get_pod_attendance_summary(pod_id)
                if "error" not in pod_summary:
                    pod_insights = self._generate_pod_insights(pod_summary)
                    insights.extend(pod_insights)
            
            # Sort by priority and confidence
            insights.sort(key=lambda x: (
                0 if x.priority == "critical" else
                1 if x.priority == "high" else
                2 if x.priority == "medium" else 3,
                -x.confidence_score
            ))
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            return []
    
    # Helper methods
    def _calculate_attendance_streaks(self, history: List[AttendanceRecord]) -> Tuple[int, int]:
        """Calculate current and longest attendance streaks"""
        if not history:
            return 0, 0
        
        sorted_history = sorted(history, key=lambda x: x.created_at, reverse=True)
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        for record in sorted_history:
            if record.attended:
                temp_streak += 1
                if current_streak == 0:
                    current_streak = temp_streak
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 0
                if current_streak > 0:
                    current_streak = 0
        
        longest_streak = max(longest_streak, temp_streak)
        return current_streak, longest_streak
    
    def _classify_attendance_pattern(self, attendance_rate: float) -> AttendancePattern:
        """Classify attendance pattern based on rate"""
        if attendance_rate >= 0.95:
            return AttendancePattern.PERFECT_ATTENDER
        elif attendance_rate >= 0.80:
            return AttendancePattern.REGULAR_ATTENDER
        elif attendance_rate >= 0.50:
            return AttendancePattern.INCONSISTENT
        elif attendance_rate >= 0.20:
            return AttendancePattern.FREQUENT_MISSER
        else:
            return AttendancePattern.GHOST_MEMBER
    
    def _assess_engagement_level(self, attendance_rate: float, avg_duration: float) -> EngagementLevel:
        """Assess engagement level based on attendance and duration"""
        if attendance_rate >= 0.85 and avg_duration >= 45:
            return EngagementLevel.HIGH
        elif attendance_rate >= 0.65 and avg_duration >= 30:
            return EngagementLevel.MODERATE
        elif attendance_rate >= 0.35:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.CRITICAL
    
    def _calculate_prediction_score(self, history: List[AttendanceRecord]) -> float:
        """Calculate prediction score for next meeting attendance"""
        if not history:
            return 0.5
        
        recent_history = history[-6:]  # Last 6 meetings
        recent_attendance_rate = len([r for r in recent_history if r.attended]) / len(recent_history)
        
        return min(1.0, max(0.1, recent_attendance_rate * 1.1))
    
    def _identify_risk_flags(self, history: List[AttendanceRecord], overall_rate: float) -> List[str]:
        """Identify risk flags for intervention"""
        flags = []
        
        if overall_rate < 0.5:
            flags.append("low_attendance_rate")
        
        if len(history) >= 6:
            recent_rate = len([r for r in history[-3:] if r.attended]) / 3
            earlier_rate = len([r for r in history[-6:-3] if r.attended]) / 3
            
            if recent_rate < earlier_rate - 0.3:
                flags.append("declining_trend")
        
        recent_attendance = any(r.attended for r in history[-2:])
        if not recent_attendance:
            flags.append("recent_no_show")
        
        return flags
    
    def _create_empty_analytics(self, user_id: str, pod_id: str) -> AttendanceAnalytics:
        """Create empty analytics for new users"""
        return AttendanceAnalytics(
            user_id=user_id,
            pod_id=pod_id,
            total_scheduled_meetings=0,
            meetings_attended=0,
            meetings_missed=0,
            attendance_rate=0.0,
            average_duration=0.0,
            current_streak=0,
            longest_streak=0,
            attendance_pattern=AttendancePattern.INCONSISTENT,
            engagement_level=EngagementLevel.MODERATE,
            last_attendance_date=None,
            prediction_score=0.5,
            risk_flags=[],
            calculated_at=datetime.now()
        )
    
    def _generate_user_insights(self, analytics: AttendanceAnalytics) -> List[AttendanceInsight]:
        """Generate insights for individual user"""
        insights = []
        
        if analytics.attendance_pattern == AttendancePattern.PERFECT_ATTENDER:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=analytics.pod_id,
                user_id=analytics.user_id,
                insight_type="perfect_attendance",
                priority="medium",
                title="Perfect Attendance Achievement",
                description=f"Exceptional {analytics.attendance_rate:.1%} attendance rate",
                recommendation="Recognize this member's commitment",
                data_points={"attendance_rate": analytics.attendance_rate},
                confidence_score=0.95,
                created_at=datetime.now()
            ))
        
        if analytics.engagement_level == EngagementLevel.CRITICAL:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=analytics.pod_id,
                user_id=analytics.user_id,
                insight_type="critical_engagement",
                priority="critical",
                title="Critical Engagement Alert",
                description=f"Very low {analytics.attendance_rate:.1%} attendance rate",
                recommendation="Immediate intervention needed",
                data_points={"attendance_rate": analytics.attendance_rate, "risk_flags": analytics.risk_flags},
                confidence_score=0.90,
                created_at=datetime.now()
            ))
        
        return insights
    
    def _generate_pod_insights(self, summary: Dict[str, Any]) -> List[AttendanceInsight]:
        """Generate insights for pod-level patterns"""
        insights = []
        
        if summary["pod_attendance_rate"] < 0.65:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=summary["pod_id"],
                user_id=None,
                insight_type="low_pod_attendance",
                priority="high",
                title="Pod Attendance Below Optimal",
                description=f"Pod attendance at {summary['pod_attendance_rate']:.1%}",
                recommendation="Review meeting format and timing",
                data_points={"attendance_rate": summary["pod_attendance_rate"]},
                confidence_score=0.88,
                created_at=datetime.now()
            ))
        
        return insights

if __name__ == "__main__":
    print("Adapted Attendance System - Works with existing database schema")