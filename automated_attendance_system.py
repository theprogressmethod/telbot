#!/usr/bin/env python3
"""
Automated Attendance System - Comprehensive pod meeting attendance tracking
Foundation for 10x-100x nurture sequence personalization based on attendance patterns
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
    LATE = "late"            # Arrived after scheduled start
    EARLY_DEPARTURE = "early_departure"  # Left before scheduled end
    PARTIAL = "partial"      # Present for part of meeting

class MeetingStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"     # No attendees showed up

class AttendancePattern(Enum):
    PERFECT_ATTENDER = "perfect_attender"    # 95%+ attendance
    REGULAR_ATTENDER = "regular_attender"    # 80-95% attendance
    INCONSISTENT = "inconsistent"            # 50-80% attendance
    FREQUENT_MISSER = "frequent_misser"      # 20-50% attendance
    GHOST_MEMBER = "ghost_member"            # <20% attendance

class EngagementLevel(Enum):
    HIGH = "high"              # Active participant, arrives on time
    MODERATE = "moderate"      # Consistent but passive
    LOW = "low"               # Inconsistent, often late/leaves early
    CRITICAL = "critical"      # Rarely attends or very disengaged

@dataclass
class MeetingSession:
    """Represents a single pod meeting instance"""
    session_id: str
    pod_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    meeting_platform: str  # "zoom", "google_meet", "teams", "manual"
    meeting_url: Optional[str]
    meeting_id: Optional[str]  # Platform-specific meeting ID
    facilitator_id: Optional[str]
    status: MeetingStatus
    total_attendees: int
    created_at: datetime
    metadata: Dict[str, Any]  # Platform-specific data
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AttendanceRecord:
    """Individual attendance record for a pod member at a meeting"""
    record_id: str
    session_id: str
    user_id: str
    pod_id: str
    attendance_status: AttendanceStatus
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    minutes_present: int
    was_late: bool
    left_early: bool
    engagement_notes: Optional[str]  # Facilitator notes on participation
    commitment_shared: bool  # Did they share commitments?
    auto_detected: bool  # Was this automatically detected or manually entered?
    created_at: datetime
    platform_data: Dict[str, Any]  # Platform-specific attendance data
    
    def __post_init__(self):
        if self.platform_data is None:
            self.platform_data = {}

@dataclass
class AttendanceAnalytics:
    """Calculated attendance analytics for a user"""
    user_id: str
    pod_id: str
    total_scheduled_meetings: int
    meetings_attended: int
    meetings_missed: int
    attendance_rate: float
    average_arrival_offset: float  # Minutes early/late (negative = early)
    average_duration_present: float  # Minutes present per meeting
    current_streak: int  # Consecutive meetings attended
    longest_streak: int
    attendance_pattern: AttendancePattern
    engagement_level: EngagementLevel
    last_attendance_date: Optional[datetime]
    prediction_score: float  # ML prediction of attending next meeting (0-1)
    risk_flags: List[str]  # Things like "declining_trend", "frequent_no_shows"
    calculated_at: datetime

@dataclass
class AttendanceInsight:
    """AI-generated insights about attendance patterns"""
    insight_id: str
    pod_id: str
    user_id: Optional[str]  # None for pod-level insights
    insight_type: str  # "attendance_trend", "engagement_drop", "perfect_streak", etc.
    priority: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    recommendation: str
    data_points: Dict[str, Any]
    confidence_score: float
    created_at: datetime

class AutomatedAttendanceSystem:
    """Comprehensive attendance tracking and analytics system"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
        # Active sessions being tracked
        self.active_sessions = {}
        
        # Platform integrations (will be expanded in Phase 2)
        self.platform_integrations = {}
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_expiry = timedelta(minutes=15)
        
        logger.info("✅ Automated Attendance System initialized")
    
    async def create_meeting_session(self, pod_id: str, scheduled_start: datetime, 
                                   scheduled_end: datetime, platform: str = "manual",
                                   meeting_url: str = None, facilitator_id: str = None) -> MeetingSession:
        """Create a new meeting session for attendance tracking"""
        try:
            session = MeetingSession(
                session_id=str(uuid.uuid4()),
                pod_id=pod_id,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                actual_start=None,
                actual_end=None,
                meeting_platform=platform,
                meeting_url=meeting_url,
                meeting_id=None,
                facilitator_id=facilitator_id,
                status=MeetingStatus.SCHEDULED,
                total_attendees=0,
                created_at=datetime.now(),
                metadata={}
            )
            
            # Store in database
            await self._store_meeting_session(session)
            
            # Add to active sessions for real-time tracking
            self.active_sessions[session.session_id] = session
            
            logger.info(f"✅ Created meeting session {session.session_id} for pod {pod_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creating meeting session: {e}")
            raise
    
    async def start_meeting_session(self, session_id: str) -> bool:
        """Mark a meeting session as started and begin attendance tracking"""
        try:
            session = await self._get_meeting_session(session_id)
            if not session:
                return False
            
            session.actual_start = datetime.now()
            session.status = MeetingStatus.IN_PROGRESS
            
            # Update in database
            await self._update_meeting_session(session)
            
            # Start real-time attendance tracking if platform supports it
            if session.meeting_platform in self.platform_integrations:
                await self._start_platform_tracking(session)
            
            logger.info(f"🎬 Started meeting session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting meeting session: {e}")
            return False
    
    async def end_meeting_session(self, session_id: str) -> Dict[str, Any]:
        """End a meeting session and finalize attendance"""
        try:
            session = await self._get_meeting_session(session_id)
            if not session:
                return {"error": "Session not found"}
            
            session.actual_end = datetime.now()
            session.status = MeetingStatus.COMPLETED
            
            # Get final attendance count
            attendance_records = await self._get_session_attendance(session_id)
            session.total_attendees = len(attendance_records)
            
            # Update in database
            await self._update_meeting_session(session)
            
            # Generate post-meeting analytics
            analytics = await self._generate_session_analytics(session, attendance_records)
            
            # Trigger nurture sequence updates based on attendance
            await self._trigger_attendance_based_sequences(session_id, attendance_records)
            
            # Remove from active tracking
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            logger.info(f"🏁 Ended meeting session {session_id} with {session.total_attendees} attendees")
            
            return {
                "session_id": session_id,
                "total_attendees": session.total_attendees,
                "duration_minutes": int((session.actual_end - session.actual_start).total_seconds() / 60),
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"❌ Error ending meeting session: {e}")
            return {"error": str(e)}
    
    async def record_attendance(self, session_id: str, user_id: str, 
                              attendance_status: AttendanceStatus,
                              joined_at: datetime = None, left_at: datetime = None,
                              engagement_notes: str = None, commitment_shared: bool = False,
                              auto_detected: bool = False) -> AttendanceRecord:
        """Record attendance for a specific user at a meeting"""
        try:
            session = await self._get_meeting_session(session_id)
            if not session:
                raise ValueError("Meeting session not found")
            
            # Calculate timing details
            if joined_at is None:
                joined_at = session.actual_start or session.scheduled_start
            
            if left_at is None and attendance_status != AttendanceStatus.ABSENT:
                left_at = session.actual_end or datetime.now()
            
            # Calculate presence duration
            minutes_present = 0
            if attendance_status != AttendanceStatus.ABSENT and joined_at and left_at:
                minutes_present = int((left_at - joined_at).total_seconds() / 60)
            
            # Check if late or early departure
            was_late = joined_at > session.scheduled_start + timedelta(minutes=5) if joined_at else False
            left_early = left_at < session.scheduled_end - timedelta(minutes=5) if left_at else False
            
            # Create attendance record
            record = AttendanceRecord(
                record_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                pod_id=session.pod_id,
                attendance_status=attendance_status,
                joined_at=joined_at,
                left_at=left_at,
                minutes_present=minutes_present,
                was_late=was_late,
                left_early=left_early,
                engagement_notes=engagement_notes,
                commitment_shared=commitment_shared,
                auto_detected=auto_detected,
                created_at=datetime.now(),
                platform_data={}
            )
            
            # Store in database
            await self._store_attendance_record(record)
            
            logger.info(f"📋 Recorded {attendance_status.value} for user {user_id} in session {session_id}")
            return record
            
        except Exception as e:
            logger.error(f"❌ Error recording attendance: {e}")
            raise
    
    async def calculate_user_attendance_analytics(self, user_id: str, pod_id: str,
                                                 weeks_back: int = 12) -> AttendanceAnalytics:
        """Calculate comprehensive attendance analytics for a user"""
        try:
            # Get attendance history
            cutoff_date = datetime.now() - timedelta(weeks=weeks_back)
            attendance_history = await self._get_user_attendance_history(user_id, pod_id, cutoff_date)
            
            if not attendance_history:
                return self._create_empty_analytics(user_id, pod_id)
            
            # Calculate basic metrics
            total_scheduled = len(attendance_history)
            meetings_attended = len([r for r in attendance_history if r.attendance_status in [
                AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.EARLY_DEPARTURE, AttendanceStatus.PARTIAL
            ]])
            meetings_missed = total_scheduled - meetings_attended
            attendance_rate = meetings_attended / total_scheduled if total_scheduled > 0 else 0
            
            # Calculate timing patterns
            timing_offsets = []
            durations = []
            for record in attendance_history:
                if record.attendance_status != AttendanceStatus.ABSENT and record.joined_at:
                    session = await self._get_meeting_session(record.session_id)
                    if session:
                        offset = (record.joined_at - session.scheduled_start).total_seconds() / 60
                        timing_offsets.append(offset)
                        durations.append(record.minutes_present)
            
            avg_arrival_offset = sum(timing_offsets) / len(timing_offsets) if timing_offsets else 0
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate streaks
            current_streak, longest_streak = self._calculate_attendance_streaks(attendance_history)
            
            # Determine patterns and engagement level
            attendance_pattern = self._classify_attendance_pattern(attendance_rate, attendance_history)
            engagement_level = self._assess_engagement_level(attendance_history, avg_arrival_offset, avg_duration)
            
            # Get last attendance date
            last_attendance = None
            for record in reversed(attendance_history):
                if record.attendance_status != AttendanceStatus.ABSENT:
                    last_attendance = record.joined_at
                    break
            
            # Calculate prediction score (ML-ready feature)
            prediction_score = self._calculate_attendance_prediction_score(attendance_history)
            
            # Identify risk flags
            risk_flags = self._identify_attendance_risk_flags(attendance_history, attendance_rate)
            
            analytics = AttendanceAnalytics(
                user_id=user_id,
                pod_id=pod_id,
                total_scheduled_meetings=total_scheduled,
                meetings_attended=meetings_attended,
                meetings_missed=meetings_missed,
                attendance_rate=attendance_rate,
                average_arrival_offset=avg_arrival_offset,
                average_duration_present=avg_duration,
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
            cache_key = f"{user_id}:{pod_id}"
            self.analytics_cache[cache_key] = {
                "analytics": analytics,
                "expires_at": datetime.now() + self.cache_expiry
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error calculating attendance analytics: {e}")
            return self._create_empty_analytics(user_id, pod_id)
    
    async def generate_attendance_insights(self, pod_id: str = None, user_id: str = None) -> List[AttendanceInsight]:
        """Generate AI-driven insights about attendance patterns"""
        try:
            insights = []
            
            if user_id:
                # Generate user-specific insights
                analytics = await self.calculate_user_attendance_analytics(user_id, pod_id)
                user_insights = await self._generate_user_attendance_insights(analytics)
                insights.extend(user_insights)
            
            if pod_id:
                # Generate pod-level insights
                pod_insights = await self._generate_pod_attendance_insights(pod_id)
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
            logger.error(f"❌ Error generating attendance insights: {e}")
            return []
    
    async def get_pod_attendance_summary(self, pod_id: str, weeks_back: int = 4) -> Dict[str, Any]:
        """Get comprehensive attendance summary for a pod"""
        try:
            cutoff_date = datetime.now() - timedelta(weeks=weeks_back)
            
            # Get all meetings for this pod
            meetings = await self._get_pod_meetings(pod_id, cutoff_date)
            
            # Get all attendance records
            attendance_records = []
            for meeting in meetings:
                session_records = await self._get_session_attendance(meeting.session_id)
                attendance_records.extend(session_records)
            
            # Calculate pod-level metrics
            total_meetings = len(meetings)
            total_possible_attendance = total_meetings * await self._get_pod_member_count(pod_id)
            total_actual_attendance = len([r for r in attendance_records if r.attendance_status != AttendanceStatus.ABSENT])
            
            pod_attendance_rate = total_actual_attendance / total_possible_attendance if total_possible_attendance > 0 else 0
            
            # Get member-level analytics
            member_analytics = []
            pod_members = await self._get_pod_members(pod_id)
            for member in pod_members:
                analytics = await self.calculate_user_attendance_analytics(member["user_id"], pod_id, weeks_back)
                member_analytics.append(analytics)
            
            # Identify patterns and trends
            high_performers = [a for a in member_analytics if a.attendance_pattern == AttendancePattern.PERFECT_ATTENDER]
            at_risk_members = [a for a in member_analytics if a.engagement_level == EngagementLevel.CRITICAL]
            
            return {
                "pod_id": pod_id,
                "summary_period_weeks": weeks_back,
                "total_meetings": total_meetings,
                "pod_attendance_rate": pod_attendance_rate,
                "average_meeting_size": total_actual_attendance / total_meetings if total_meetings > 0 else 0,
                "member_count": len(pod_members),
                "high_performers": len(high_performers),
                "at_risk_members": len(at_risk_members),
                "member_analytics": [asdict(a) for a in member_analytics],
                "recent_meetings": [asdict(m) for m in meetings],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating pod attendance summary: {e}")
            return {"error": str(e)}
    
    # Helper methods for database operations
    async def _store_meeting_session(self, session: MeetingSession):
        """Store meeting session in database"""
        try:
            data = {
                "session_id": session.session_id,
                "pod_id": session.pod_id,
                "scheduled_start": session.scheduled_start.isoformat(),
                "scheduled_end": session.scheduled_end.isoformat(),
                "actual_start": session.actual_start.isoformat() if session.actual_start else None,
                "actual_end": session.actual_end.isoformat() if session.actual_end else None,
                "meeting_platform": session.meeting_platform,
                "meeting_url": session.meeting_url,
                "meeting_id": session.meeting_id,
                "facilitator_id": session.facilitator_id,
                "status": session.status.value,
                "total_attendees": session.total_attendees,
                "created_at": session.created_at.isoformat(),
                "metadata": json.dumps(session.metadata)
            }
            
            result = self.supabase.table("meeting_sessions").insert(data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error storing meeting session: {e}")
            raise
    
    async def _store_attendance_record(self, record: AttendanceRecord):
        """Store attendance record in database"""
        try:
            data = {
                "record_id": record.record_id,
                "session_id": record.session_id,
                "user_id": record.user_id,
                "pod_id": record.pod_id,
                "attendance_status": record.attendance_status.value,
                "joined_at": record.joined_at.isoformat() if record.joined_at else None,
                "left_at": record.left_at.isoformat() if record.left_at else None,
                "minutes_present": record.minutes_present,
                "was_late": record.was_late,
                "left_early": record.left_early,
                "engagement_notes": record.engagement_notes,
                "commitment_shared": record.commitment_shared,
                "auto_detected": record.auto_detected,
                "created_at": record.created_at.isoformat(),
                "platform_data": json.dumps(record.platform_data)
            }
            
            result = self.supabase.table("attendance_records").insert(data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error storing attendance record: {e}")
            raise
    
    # Helper methods for analytics calculations
    def _calculate_attendance_streaks(self, attendance_history: List[AttendanceRecord]) -> Tuple[int, int]:
        """Calculate current and longest attendance streaks"""
        if not attendance_history:
            return 0, 0
        
        # Sort by date (most recent first)
        sorted_history = sorted(attendance_history, key=lambda x: x.created_at, reverse=True)
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        for record in sorted_history:
            if record.attendance_status != AttendanceStatus.ABSENT:
                temp_streak += 1
                if current_streak == 0:  # First in current streak
                    current_streak = temp_streak
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 0
                if current_streak > 0:  # End of current streak
                    current_streak = 0
        
        longest_streak = max(longest_streak, temp_streak)
        return current_streak, longest_streak
    
    def _classify_attendance_pattern(self, attendance_rate: float, history: List[AttendanceRecord]) -> AttendancePattern:
        """Classify attendance pattern based on rate and consistency"""
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
    
    def _assess_engagement_level(self, history: List[AttendanceRecord], avg_offset: float, avg_duration: float) -> EngagementLevel:
        """Assess engagement level based on attendance quality"""
        attendance_rate = len([r for r in history if r.attendance_status != AttendanceStatus.ABSENT]) / len(history) if history else 0
        
        # High engagement: good attendance, on time, full duration
        if attendance_rate >= 0.85 and avg_offset <= 5 and avg_duration >= 45:
            return EngagementLevel.HIGH
        
        # Moderate engagement: decent attendance, occasionally late
        elif attendance_rate >= 0.65 and avg_offset <= 10:
            return EngagementLevel.MODERATE
        
        # Low engagement: poor attendance or quality issues
        elif attendance_rate >= 0.35:
            return EngagementLevel.LOW
        
        # Critical: rarely attends or very problematic attendance
        else:
            return EngagementLevel.CRITICAL
    
    def _calculate_attendance_prediction_score(self, history: List[AttendanceRecord]) -> float:
        """Calculate ML prediction score for next meeting attendance (0-1)"""
        if not history:
            return 0.5  # Neutral prediction for new members
        
        recent_history = history[-6:]  # Last 6 meetings
        recent_attendance_rate = len([r for r in recent_history if r.attendance_status != AttendanceStatus.ABSENT]) / len(recent_history)
        
        # Simple prediction based on recent trend
        # In production, this would use ML models
        return min(1.0, max(0.1, recent_attendance_rate * 1.1))
    
    def _identify_attendance_risk_flags(self, history: List[AttendanceRecord], overall_rate: float) -> List[str]:
        """Identify risk flags for intervention"""
        flags = []
        
        if overall_rate < 0.5:
            flags.append("low_attendance_rate")
        
        # Check for declining trend
        if len(history) >= 6:
            recent_rate = len([r for r in history[-3:] if r.attendance_status != AttendanceStatus.ABSENT]) / 3
            earlier_rate = len([r for r in history[-6:-3] if r.attendance_status != AttendanceStatus.ABSENT]) / 3
            
            if recent_rate < earlier_rate - 0.3:
                flags.append("declining_trend")
        
        # Check for chronic lateness
        late_count = len([r for r in history if r.was_late])
        if late_count / len(history) > 0.5:
            flags.append("chronic_lateness")
        
        # Check for no recent attendance
        recent_attendance = any(r.attendance_status != AttendanceStatus.ABSENT for r in history[-2:])
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
            average_arrival_offset=0.0,
            average_duration_present=0.0,
            current_streak=0,
            longest_streak=0,
            attendance_pattern=AttendancePattern.INCONSISTENT,
            engagement_level=EngagementLevel.MODERATE,
            last_attendance_date=None,
            prediction_score=0.5,
            risk_flags=[],
            calculated_at=datetime.now()
        )
    
    async def _generate_user_attendance_insights(self, analytics: AttendanceAnalytics) -> List[AttendanceInsight]:
        """Generate insights for individual user attendance"""
        insights = []
        
        # Perfect attendance recognition
        if analytics.attendance_pattern == AttendancePattern.PERFECT_ATTENDER:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=analytics.pod_id,
                user_id=analytics.user_id,
                insight_type="perfect_streak",
                priority="medium",
                title="Perfect Attendance Achievement",
                description=f"Exceptional {analytics.attendance_rate:.1%} attendance rate with {analytics.current_streak} meeting streak",
                recommendation="Recognize this member's commitment and consider them for pod leadership opportunities",
                data_points={"attendance_rate": analytics.attendance_rate, "current_streak": analytics.current_streak},
                confidence_score=0.95,
                created_at=datetime.now()
            ))
        
        # At-risk member alert
        if analytics.engagement_level == EngagementLevel.CRITICAL:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=analytics.pod_id,
                user_id=analytics.user_id,
                insight_type="engagement_critical",
                priority="critical",
                title="Critical Engagement Alert",
                description=f"Very low {analytics.attendance_rate:.1%} attendance rate with multiple risk factors",
                recommendation="Immediate intervention needed - schedule 1:1 check-in and consider modified engagement approach",
                data_points={"attendance_rate": analytics.attendance_rate, "risk_flags": analytics.risk_flags},
                confidence_score=0.90,
                created_at=datetime.now()
            ))
        
        # Declining trend warning
        if "declining_trend" in analytics.risk_flags:
            insights.append(AttendanceInsight(
                insight_id=str(uuid.uuid4()),
                pod_id=analytics.pod_id,
                user_id=analytics.user_id,
                insight_type="attendance_decline",
                priority="high",
                title="Declining Attendance Pattern",
                description="Recent drop in attendance frequency detected",
                recommendation="Proactive outreach to understand barriers and provide support",
                data_points={"risk_flags": analytics.risk_flags},
                confidence_score=0.85,
                created_at=datetime.now()
            ))
        
        return insights
    
    async def _generate_pod_attendance_insights(self, pod_id: str) -> List[AttendanceInsight]:
        """Generate insights for pod-level attendance patterns"""
        insights = []
        
        try:
            summary = await self.get_pod_attendance_summary(pod_id)
            
            # Low overall pod attendance
            if summary["pod_attendance_rate"] < 0.65:
                insights.append(AttendanceInsight(
                    insight_id=str(uuid.uuid4()),
                    pod_id=pod_id,
                    user_id=None,
                    insight_type="pod_attendance_low",
                    priority="high",
                    title="Pod Attendance Below Optimal",
                    description=f"Pod attendance at {summary['pod_attendance_rate']:.1%} - below healthy threshold",
                    recommendation="Review meeting timing, format, and member engagement strategies",
                    data_points={"pod_attendance_rate": summary["pod_attendance_rate"], "member_count": summary["member_count"]},
                    confidence_score=0.88,
                    created_at=datetime.now()
                ))
            
            # Too many at-risk members
            if summary["at_risk_members"] > summary["member_count"] * 0.3:
                insights.append(AttendanceInsight(
                    insight_id=str(uuid.uuid4()),
                    pod_id=pod_id,
                    user_id=None,
                    insight_type="high_risk_member_count",
                    priority="critical",
                    title="High At-Risk Member Count",
                    description=f"{summary['at_risk_members']} of {summary['member_count']} members showing critical engagement",
                    recommendation="Pod health intervention needed - consider restructuring or intensive support",
                    data_points={"at_risk_count": summary["at_risk_members"], "total_members": summary["member_count"]},
                    confidence_score=0.92,
                    created_at=datetime.now()
                ))
        
        except Exception as e:
            logger.error(f"Error generating pod insights: {e}")
        
        return insights
    
    # Placeholder methods for database operations (to be implemented based on actual schema)
    async def _get_meeting_session(self, session_id: str) -> Optional[MeetingSession]:
        """Get meeting session from database"""
        # Implementation depends on actual database schema
        return self.active_sessions.get(session_id)
    
    async def _update_meeting_session(self, session: MeetingSession):
        """Update meeting session in database"""
        # Implementation depends on actual database schema
        pass
    
    async def _get_session_attendance(self, session_id: str) -> List[AttendanceRecord]:
        """Get attendance records for a session"""
        # Implementation depends on actual database schema
        return []
    
    async def _get_user_attendance_history(self, user_id: str, pod_id: str, since_date: datetime) -> List[AttendanceRecord]:
        """Get user's attendance history"""
        # Implementation depends on actual database schema
        return []
    
    async def _get_pod_meetings(self, pod_id: str, since_date: datetime) -> List[MeetingSession]:
        """Get pod meetings since date"""
        # Implementation depends on actual database schema
        return []
    
    async def _get_pod_member_count(self, pod_id: str) -> int:
        """Get count of pod members"""
        try:
            result = self.supabase.table("pod_memberships").select("id", count="exact").eq("pod_id", pod_id).eq("is_active", True).execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error getting pod member count: {e}")
            return 0
    
    async def _get_pod_members(self, pod_id: str) -> List[Dict[str, Any]]:
        """Get pod members"""
        try:
            result = self.supabase.table("pod_memberships").select("user_id").eq("pod_id", pod_id).eq("is_active", True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting pod members: {e}")
            return []
    
    async def _generate_session_analytics(self, session: MeetingSession, attendance_records: List[AttendanceRecord]) -> Dict[str, Any]:
        """Generate analytics for completed session"""
        return {
            "attendance_rate": len([r for r in attendance_records if r.attendance_status != AttendanceStatus.ABSENT]) / len(attendance_records) if attendance_records else 0,
            "average_duration": sum(r.minutes_present for r in attendance_records) / len(attendance_records) if attendance_records else 0,
            "late_arrivals": len([r for r in attendance_records if r.was_late]),
            "early_departures": len([r for r in attendance_records if r.left_early])
        }
    
    async def _trigger_attendance_based_sequences(self, session_id: str, attendance_records: List[AttendanceRecord]):
        """Trigger nurture sequences based on attendance patterns"""
        # This will integrate with the nurture sequence system
        logger.info(f"🎯 Triggered attendance-based sequences for session {session_id}")
    
    async def _start_platform_tracking(self, session: MeetingSession):
        """Start platform-specific attendance tracking"""
        # Will be implemented in Phase 2 for Zoom, Google Meet, etc.
        logger.info(f"📡 Started platform tracking for {session.meeting_platform}")

if __name__ == "__main__":
    print("Automated Attendance System - Foundation for intelligent pod nurture sequences")