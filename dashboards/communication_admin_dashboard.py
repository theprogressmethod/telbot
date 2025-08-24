#!/usr/bin/env python3
"""
Communication Admin Dashboard
Real-time visibility into nurture effectiveness and user preferences
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json

logger = logging.getLogger(__name__)

class CommunicationAdminDashboard:
    """Admin dashboard for communication system visibility and control"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_real_time_dashboard(self, pod_id: str = None) -> Dict[str, Any]:
        """Get comprehensive real-time communication dashboard"""
        try:
            dashboard_data = {
                "generated_at": datetime.now().isoformat(),
                "overview": await self._get_overview_metrics(pod_id),
                "user_preferences": await self._get_preference_distribution(),
                "message_performance": await self._get_message_performance(pod_id),
                "engagement_trends": await self._get_engagement_trends(pod_id),
                "user_segments": await self._get_user_segments(),
                "alerts": await self._get_system_alerts(),
                "recommendations": await self._get_actionable_recommendations()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return {"error": str(e)}
    
    async def _get_overview_metrics(self, pod_id: str = None) -> Dict[str, Any]:
        """Get high-level overview metrics"""
        try:
            # Last 7 days
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            # Build query
            query = self.supabase.table("message_analytics").select("*")
            if pod_id:
                query = query.eq("pod_id", pod_id)
            
            recent_messages = query.gte("sent_at", week_ago).execute()
            
            if not recent_messages.data:
                return {"total_messages": 0, "unique_users": 0, "response_rate": 0}
            
            total_messages = len(recent_messages.data)
            unique_users = len(set(msg["telegram_user_id"] for msg in recent_messages.data))
            responses = sum(1 for msg in recent_messages.data if msg.get("user_responded", False))
            clicks = sum(1 for msg in recent_messages.data if msg.get("clicked_link", False))
            
            # Get preference distribution
            prefs_result = self.supabase.table("communication_preferences").select("communication_style").execute()
            style_counts = {}
            for pref in prefs_result.data:
                style = pref["communication_style"]
                style_counts[style] = style_counts.get(style, 0) + 1
            
            return {
                "period": "last_7_days",
                "total_messages": total_messages,
                "unique_users": unique_users,
                "overall_response_rate": responses / total_messages if total_messages > 0 else 0,
                "overall_click_rate": clicks / total_messages if total_messages > 0 else 0,
                "messages_per_user": total_messages / unique_users if unique_users > 0 else 0,
                "user_style_distribution": style_counts,
                "most_common_style": max(style_counts.keys(), key=style_counts.get) if style_counts else None
            }
            
        except Exception as e:
            logger.error(f"Error getting overview metrics: {e}")
            return {"error": str(e)}
    
    async def _get_preference_distribution(self) -> Dict[str, Any]:
        """Get detailed breakdown of user communication preferences"""
        try:
            prefs_result = self.supabase.table("communication_preferences").select("*").execute()
            
            distribution = {
                "high_touch": 0,
                "balanced": 0, 
                "light_touch": 0,
                "meeting_only": 0,
                "paused": 0,
                "custom": 0
            }
            
            recent_changes = []
            
            for pref in prefs_result.data:
                style = pref["communication_style"]
                distribution[style] = distribution.get(style, 0) + 1
                
                # Check for recent changes (last 24 hours)
                last_updated = datetime.fromisoformat(pref["last_updated"].replace('Z', '+00:00'))
                if last_updated.replace(tzinfo=None) > datetime.now() - timedelta(hours=24):
                    recent_changes.append({
                        "telegram_user_id": pref["telegram_user_id"],
                        "new_style": style,
                        "changed_at": pref["last_updated"]
                    })
            
            total_users = sum(distribution.values())
            
            return {
                "total_users": total_users,
                "distribution": distribution,
                "percentages": {k: (v/total_users)*100 if total_users > 0 else 0 for k, v in distribution.items()},
                "recent_changes_24h": len(recent_changes),
                "recent_changes": recent_changes[:10]  # Last 10 changes
            }
            
        except Exception as e:
            logger.error(f"Error getting preference distribution: {e}")
            return {"error": str(e)}
    
    async def _get_message_performance(self, pod_id: str = None) -> Dict[str, Any]:
        """Get performance metrics by message type"""
        try:
            # Last 14 days
            two_weeks_ago = (datetime.now() - timedelta(days=14)).isoformat()
            
            query = self.supabase.table("message_analytics").select("*")
            if pod_id:
                query = query.eq("pod_id", pod_id)
            
            messages = query.gte("sent_at", two_weeks_ago).execute()
            
            if not messages.data:
                return {"message_types": {}}
            
            # Calculate metrics by message type
            type_metrics = {}
            
            for msg in messages.data:
                msg_type = msg["message_type"]
                
                if msg_type not in type_metrics:
                    type_metrics[msg_type] = {
                        "sent": 0,
                        "responses": 0,
                        "clicks": 0,
                        "avg_response_time": []
                    }
                
                type_metrics[msg_type]["sent"] += 1
                
                if msg.get("user_responded", False):
                    type_metrics[msg_type]["responses"] += 1
                    
                    # Calculate response time if available
                    if msg.get("responded_at") and msg.get("sent_at"):
                        sent_time = datetime.fromisoformat(msg["sent_at"])
                        responded_time = datetime.fromisoformat(msg["responded_at"])
                        response_time = (responded_time - sent_time).total_seconds() / 3600  # hours
                        type_metrics[msg_type]["avg_response_time"].append(response_time)
                
                if msg.get("clicked_link", False):
                    type_metrics[msg_type]["clicks"] += 1
            
            # Calculate rates and averages
            performance_summary = {}
            for msg_type, metrics in type_metrics.items():
                response_times = metrics["avg_response_time"]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                
                performance_summary[msg_type] = {
                    "total_sent": metrics["sent"],
                    "response_rate": metrics["responses"] / metrics["sent"] if metrics["sent"] > 0 else 0,
                    "click_rate": metrics["clicks"] / metrics["sent"] if metrics["sent"] > 0 else 0,
                    "avg_response_time_hours": round(avg_response_time, 2)
                }
            
            # Find best and worst performing types
            best_type = max(performance_summary.keys(), 
                          key=lambda x: performance_summary[x]["response_rate"]) if performance_summary else None
            worst_type = min(performance_summary.keys(), 
                           key=lambda x: performance_summary[x]["response_rate"]) if performance_summary else None
            
            return {
                "period": "last_14_days",
                "message_types": performance_summary,
                "best_performing": best_type,
                "worst_performing": worst_type,
                "total_types_tracked": len(performance_summary)
            }
            
        except Exception as e:
            logger.error(f"Error getting message performance: {e}")
            return {"error": str(e)}
    
    async def _get_engagement_trends(self, pod_id: str = None) -> Dict[str, Any]:
        """Get engagement trends over time"""
        try:
            # Last 30 days, grouped by day
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            query = self.supabase.table("message_analytics").select("*")
            if pod_id:
                query = query.eq("pod_id", pod_id)
            
            messages = query.gte("sent_at", thirty_days_ago).order("sent_at").execute()
            
            if not messages.data:
                return {"daily_trends": []}
            
            # Group by day
            daily_data = {}
            
            for msg in messages.data:
                sent_date = datetime.fromisoformat(msg["sent_at"]).date().isoformat()
                
                if sent_date not in daily_data:
                    daily_data[sent_date] = {
                        "sent": 0,
                        "responses": 0,
                        "clicks": 0,
                        "unique_users": set()
                    }
                
                daily_data[sent_date]["sent"] += 1
                daily_data[sent_date]["unique_users"].add(msg["telegram_user_id"])
                
                if msg.get("user_responded", False):
                    daily_data[sent_date]["responses"] += 1
                if msg.get("clicked_link", False):
                    daily_data[sent_date]["clicks"] += 1
            
            # Convert to trend format
            daily_trends = []
            for date_str, data in sorted(daily_data.items()):
                daily_trends.append({
                    "date": date_str,
                    "messages_sent": data["sent"],
                    "unique_users": len(data["unique_users"]),
                    "response_rate": data["responses"] / data["sent"] if data["sent"] > 0 else 0,
                    "click_rate": data["clicks"] / data["sent"] if data["sent"] > 0 else 0
                })
            
            # Calculate trend direction
            if len(daily_trends) >= 7:
                recent_avg = sum(day["response_rate"] for day in daily_trends[-7:]) / 7
                older_avg = sum(day["response_rate"] for day in daily_trends[-14:-7]) / 7
                trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
            else:
                trend_direction = "insufficient_data"
            
            return {
                "daily_trends": daily_trends,
                "trend_direction": trend_direction,
                "days_analyzed": len(daily_trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement trends: {e}")
            return {"error": str(e)}
    
    async def _get_user_segments(self) -> Dict[str, Any]:
        """Get user segmentation based on engagement"""
        try:
            # Get engagement summary from view
            engagement_data = self.supabase.table("user_engagement_summary").select("*").execute()
            
            if not engagement_data.data:
                return {"segments": {}}
            
            segments = {
                "highly_engaged": [],      # >70% response rate
                "moderately_engaged": [],  # 30-70% response rate  
                "low_engaged": [],         # 10-30% response rate
                "unresponsive": [],        # <10% response rate
                "new_users": []            # <5 messages sent
            }
            
            for user in engagement_data.data:
                response_rate = user["response_rate"] or 0
                total_messages = user["total_messages_sent"] or 0
                
                if total_messages < 5:
                    segments["new_users"].append(user)
                elif response_rate >= 0.7:
                    segments["highly_engaged"].append(user)
                elif response_rate >= 0.3:
                    segments["moderately_engaged"].append(user)
                elif response_rate >= 0.1:
                    segments["low_engaged"].append(user)
                else:
                    segments["unresponsive"].append(user)
            
            # Calculate segment sizes and characteristics
            segment_summary = {}
            for segment_name, users in segments.items():
                if users:
                    avg_response_rate = sum(u["response_rate"] or 0 for u in users) / len(users)
                    common_style = max(set(u["communication_style"] for u in users), 
                                     key=[u["communication_style"] for u in users].count)
                else:
                    avg_response_rate = 0
                    common_style = "none"
                
                segment_summary[segment_name] = {
                    "count": len(users),
                    "avg_response_rate": round(avg_response_rate, 3),
                    "most_common_style": common_style
                }
            
            return {
                "segments": segment_summary,
                "total_users": len(engagement_data.data),
                "recommendations": self._generate_segment_recommendations(segment_summary)
            }
            
        except Exception as e:
            logger.error(f"Error getting user segments: {e}")
            return {"error": str(e)}
    
    def _generate_segment_recommendations(self, segments: Dict) -> List[str]:
        """Generate actionable recommendations based on segments"""
        recommendations = []
        
        if segments.get("unresponsive", {}).get("count", 0) > 0:
            recommendations.append(f"🚨 {segments['unresponsive']['count']} unresponsive users - consider auto-reducing their message frequency")
        
        if segments.get("highly_engaged", {}).get("count", 0) > segments.get("low_engaged", {}).get("count", 0):
            recommendations.append("💪 More users are highly engaged than low engaged - system is working well!")
        
        if segments.get("new_users", {}).get("count", 0) > 10:
            recommendations.append(f"👋 {segments['new_users']['count']} new users - ensure good first impression with onboarding sequence")
        
        return recommendations
    
    async def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts for admin attention"""
        alerts = []
        
        try:
            # Check for users who paused recently
            recent_pauses = self.supabase.table("preference_change_log").select("*").eq("new_style", "paused").gte("timestamp", (datetime.now() - timedelta(days=1)).isoformat()).execute()
            
            if recent_pauses.data and len(recent_pauses.data) > 3:
                alerts.append({
                    "type": "warning",
                    "message": f"{len(recent_pauses.data)} users paused communications in the last 24h",
                    "action": "Review message frequency and content"
                })
            
            # Check for low engagement rates
            low_engagement = self.supabase.table("user_engagement_summary").select("*").lt("response_rate", 0.1).gt("total_messages_sent", 5).execute()
            
            if low_engagement.data and len(low_engagement.data) > 10:
                alerts.append({
                    "type": "attention",
                    "message": f"{len(low_engagement.data)} users have <10% response rate with 5+ messages sent",
                    "action": "Consider auto-adjusting their communication style to light touch"
                })
            
            # Check message volume
            today_messages = self.supabase.table("message_analytics").select("id", count="exact").gte("sent_at", datetime.now().replace(hour=0, minute=0, second=0).isoformat()).execute()
            
            if today_messages.count > 500:  # Adjust threshold as needed
                alerts.append({
                    "type": "info",
                    "message": f"{today_messages.count} messages sent today - high volume day",
                    "action": "Monitor for any spike in unsubscribes"
                })
            
        except Exception as e:
            logger.error(f"Error getting system alerts: {e}")
            alerts.append({
                "type": "error",
                "message": f"Error generating alerts: {str(e)}",
                "action": "Check system logs"
            })
        
        return alerts
    
    async def _get_actionable_recommendations(self) -> List[Dict[str, str]]:
        """Get actionable recommendations for improving communication"""
        recommendations = []
        
        try:
            # Get performance data
            performance = await self._get_message_performance()
            
            if "message_types" in performance:
                # Find underperforming message types
                for msg_type, metrics in performance["message_types"].items():
                    if metrics["response_rate"] < 0.15 and metrics["total_sent"] > 10:
                        recommendations.append({
                            "priority": "high",
                            "area": "content",
                            "message": f"'{msg_type}' messages have low {metrics['response_rate']:.1%} response rate",
                            "action": f"Review and improve '{msg_type}' message content and timing"
                        })
            
            # Check preference distribution
            prefs = await self._get_preference_distribution()
            if prefs.get("distribution", {}).get("paused", 0) > prefs.get("total_users", 1) * 0.1:
                recommendations.append({
                    "priority": "medium",
                    "area": "frequency", 
                    "message": "More than 10% of users have paused communications",
                    "action": "Review default message frequency and consider reducing overall volume"
                })
            
            # Engagement trends
            trends = await self._get_engagement_trends()
            if trends.get("trend_direction") == "declining":
                recommendations.append({
                    "priority": "high",
                    "area": "engagement",
                    "message": "Engagement has been declining over the past week",
                    "action": "Review recent message content and consider A/B testing new approaches"
                })
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append({
                "priority": "low",
                "area": "system",
                "message": f"Error generating recommendations: {str(e)}",
                "action": "Check system logs and data integrity"
            })
        
        return recommendations
    
    async def generate_weekly_report(self) -> str:
        """Generate comprehensive weekly communication report"""
        try:
            dashboard = await self.get_real_time_dashboard()
            
            report = f"""📊 **Weekly Communication Report**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**📈 Overview (Last 7 Days):**
• Total Messages: {dashboard['overview'].get('total_messages', 0)}
• Unique Users Reached: {dashboard['overview'].get('unique_users', 0)}
• Overall Response Rate: {dashboard['overview'].get('overall_response_rate', 0):.1%}
• Messages per User: {dashboard['overview'].get('messages_per_user', 0):.1f}

**🎛️ User Preferences:**
"""
            
            prefs = dashboard.get('user_preferences', {}).get('distribution', {})
            for style, count in prefs.items():
                percentage = dashboard.get('user_preferences', {}).get('percentages', {}).get(style, 0)
                report += f"• {style.replace('_', ' ').title()}: {count} users ({percentage:.1f}%)\n"
            
            report += f"""
**🏆 Best Performing Message Type:** {dashboard.get('message_performance', {}).get('best_performing', 'N/A')}
**📉 Worst Performing Message Type:** {dashboard.get('message_performance', {}).get('worst_performing', 'N/A')}

**🔔 Alerts:**
"""
            
            alerts = dashboard.get('alerts', [])
            if alerts:
                for alert in alerts:
                    report += f"• {alert.get('type', '').upper()}: {alert.get('message', '')}\n"
            else:
                report += "• No alerts - system running smoothly ✅\n"
            
            report += f"""
**💡 Top Recommendations:**
"""
            
            recommendations = dashboard.get('recommendations', [])[:3]  # Top 3
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec.get('message', '')} - {rec.get('action', '')}\n"
            else:
                report += "• No specific recommendations - keep monitoring\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return f"Error generating report: {str(e)}"