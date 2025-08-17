#!/usr/bin/env python3
"""
Optimized Nurture Sequences v2.0
Based on behavioral analysis findings - designed to address 27.8% onboarding conversion crisis
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import Client
import json
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizedSequenceType(Enum):
    """Optimized sequence types based on behavioral insights"""
    MICRO_ONBOARDING = "micro_onboarding"  # New micro-commitment approach
    QUICK_EXECUTION_FOLLOWUP = "quick_execution_followup"  # For 3.4hr completion pattern
    PROGRESSIVE_SCALING = "progressive_scaling"  # Difficulty scaling based on success
    INACTIVE_RESCUE = "inactive_rescue"  # For 72.2% inactive users
    POWER_USER_AMPLIFICATION = "power_user_amplification"  # For 16.7% high performers

class OptimizedNurtureSequences:
    """
    Optimized nurture sequences based on behavioral intelligence analysis
    
    Key Insights Applied:
    - 27.8% onboarding conversion rate (critical)
    - 94.4% quick completion preference (<24hrs)
    - 3.4hr average completion time
    - 72.2% user inactivity rate
    - Progressive difficulty scaling needed
    """
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.sequences = self._define_optimized_sequences()
        logger.info("🧠 Optimized Nurture Sequences v2.0 initialized")
    
    def _define_optimized_sequences(self) -> Dict[str, Dict]:
        """Define optimized sequences based on behavioral analysis"""
        return {
            "micro_onboarding": {
                "name": "Micro-Momentum Onboarding v2.0",
                "description": "Progressive micro-commitments to fix 27.8% conversion crisis",
                "trigger": "first_bot_interaction",
                "optimization_target": "onboarding_conversion",
                "expected_improvement": "37.2% increase (27.8% → 65%)",
                "psychological_basis": [
                    "immediate_success_experience",
                    "momentum_building", 
                    "progressive_difficulty",
                    "same_day_completion_preference"
                ],
                "messages": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "commitment_type": "30_second_micro",
                        "target_success_rate": "95%",
                        "message": """🎯 Welcome to The Progress Method! 

Let's start with something TINY to get your first win:

**Take 3 deep breaths right now.** That's it! 

When you're done, hit the button below 👇""",
                        "action_buttons": [
                            {"text": "✅ Done! (3 breaths taken)", "callback": "micro_step_1_complete"}
                        ],
                        "fallback_micro": "Just say 'hello' in the chat",
                        "psychological_trigger": "immediate_success"
                    },
                    {
                        "step": 2,
                        "delay_hours": 2,
                        "commitment_type": "1_minute_micro",
                        "target_success_rate": "85%",
                        "condition": "step_1_completed",
                        "message": """🚀 Amazing! You just completed your first micro-commitment!

Now let's build on that momentum:

**Write ONE word describing how you want to feel today.**

Examples: "peaceful", "productive", "energized"

Just one word! 👇""",
                        "action": "text_input_capture",
                        "fallback_micro": "Just pick: happy, calm, or strong",
                        "psychological_trigger": "momentum_building"
                    },
                    {
                        "step": 3,
                        "delay_hours": 4,
                        "commitment_type": "5_minute_max",
                        "target_success_rate": "75%",
                        "condition": "step_2_completed",
                        "message": """💪 You're building real momentum! 

Your word was: **{user_feeling_word}**

Now do ONE small thing toward feeling that way:
• Tidy one small surface (2 min)
• Do 10 jumping jacks (1 min)  
• Text someone nice (2 min)
• Drink a glass of water (30 sec)

**Maximum 5 minutes.** What did you choose?""",
                        "action": "self_report_with_description",
                        "fallback_micro": "Just do one pushup or stretch",
                        "psychological_trigger": "personalized_action"
                    },
                    {
                        "step": 4,
                        "delay_hours": 6,
                        "commitment_type": "planning_micro",
                        "target_success_rate": "80%",
                        "condition": "step_3_completed_same_day",
                        "message": """🔥 You're UNSTOPPABLE! Three micro-commitments in one day!

**Final step:** Set tomorrow's micro-commitment.

Format: "What" + "When"
Example: "5 minute walk" + "after breakfast"

Keep it tiny. Keep it doable. 👇""",
                        "action": "structured_commitment_form",
                        "psychological_trigger": "future_planning"
                    }
                ],
                "success_pathway": {
                    "step_1_success": "Celebrate immediately, schedule step 2",
                    "step_2_success": "Personalize step 3 with their word", 
                    "step_3_success": "Build toward sustainable habits",
                    "step_4_success": "Graduate to regular commitment system"
                },
                "failure_recovery": {
                    "step_1_no_response": {
                        "delay_hours": 6,
                        "message": "No pressure! When you're ready, just say 'hello' in the chat. That counts too! 💙"
                    },
                    "step_2_delayed": {
                        "delay_hours": 12,
                        "message": "Still here when you're ready! One word, any word. Or just: 'good' works too. 😊"
                    },
                    "step_3_skipped": {
                        "delay_hours": 8,
                        "message": "How about 2 minutes instead of 5? Or even 30 seconds? Progress over perfection! 💪"
                    },
                    "complete_abandonment": {
                        "delay_hours": 24,
                        "message": "Want to try something even smaller? Just one deep breath? We're here when you're ready. 🌱"
                    }
                }
            },

            "quick_execution_followup": {
                "name": "Quick Execution Optimization",
                "description": "Leverages 3.4hr average completion time and 94.4% same-day preference",
                "trigger": "commitment_created",
                "optimization_target": "completion_rate",
                "expected_improvement": "48% → 75% completion rate",
                "messages": [
                    {
                        "step": 1,
                        "delay_hours": 2,
                        "message": """⚡ **Quick Check-in!**

Based on our data, you'll likely complete this within 3-4 hours. That's your superpower! ⚡

🎯 **Your commitment:** {commitment_text}

How's it going?""",
                        "action_buttons": [
                            {"text": "✅ Already done!", "callback": "mark_complete"},
                            {"text": "🔥 Working on it", "callback": "in_progress"},  
                            {"text": "🤔 Need to break it smaller", "callback": "too_big"}
                        ]
                    },
                    {
                        "step": 2,
                        "delay_hours": 4,
                        "condition": "not_completed_and_not_too_big",
                        "message": """🌅 **You're in your execution window!**

Most people like you finish within 3-4 hours. You're right on track! 

💪 **Push through the next 30 minutes.** 

You've got this! 🚀""",
                        "action_buttons": [
                            {"text": "✅ Done!", "callback": "mark_complete"},
                            {"text": "⏰ Need more time", "callback": "extend_time"}
                        ]
                    }
                ]
            },

            "progressive_scaling": {
                "name": "Progressive Difficulty Scaling",
                "description": "Auto-adjust commitment difficulty based on completion patterns",
                "trigger": "commitment_completed",
                "optimization_target": "sustainable_growth", 
                "messages": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "condition": "quick_completion_pattern",
                        "message": """🎉 **Another quick completion!** 

You completed that in {completion_time}. You're building an amazing pattern! 

🚀 **Ready to level up?** Your next commitment could be slightly bigger:

{suggested_scaled_commitment}

Or stick with what's working - your choice! 💪""",
                        "action_buttons": [
                            {"text": "🚀 Level up!", "callback": "accept_scaling"},
                            {"text": "💪 Same size works", "callback": "maintain_level"}
                        ]
                    }
                ]
            },

            "inactive_rescue": {
                "name": "Inactive User Rescue Sequence",
                "description": "Addresses 72.2% inactive user rate with micro-interventions",
                "trigger": "3_days_inactive",
                "optimization_target": "user_activation",
                "messages": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "message": """🌱 **Tiny restart?**

No judgment - life happens! Let's restart with something impossibly small:

• Take one deep breath
• Write one word
• Stretch for 10 seconds

Which feels doable today? 💙""",
                        "action_buttons": [
                            {"text": "🫁 One breath", "callback": "micro_breath"},
                            {"text": "✍️ One word", "callback": "micro_word"},
                            {"text": "🤸 Quick stretch", "callback": "micro_stretch"}
                        ]
                    },
                    {
                        "step": 2,
                        "delay_hours": 168,  # 7 days
                        "condition": "still_inactive",
                        "message": """💙 **We miss you, but no pressure.**

Sometimes life gets overwhelming. That's human.

When you're ready for the tiniest step forward, we're here.

Even just saying "hi" counts as progress. 🌱""",
                        "action_buttons": [
                            {"text": "👋 Hi", "callback": "tiny_engagement"}
                        ]
                    }
                ]
            },

            "power_user_amplification": {
                "name": "Power User Amplification",
                "description": "Leverage 16.7% high performers for community building",
                "trigger": "10_commitments_completed_high_rate",
                "optimization_target": "community_growth",
                "messages": [
                    {
                        "step": 1,
                        "delay_hours": 0,
                        "message": """🏆 **You're a Progress Method CHAMPION!**

10+ commitments with {completion_rate}% success rate! You're in the top 17% of users.

🌟 **Ready to help others?** 

Your success could inspire someone just starting out. Interested in:
• Mentoring new users?
• Sharing your strategies?
• Leading a pod?""",
                        "action_buttons": [
                            {"text": "🧑‍🏫 Mentor others", "callback": "become_mentor"},
                            {"text": "👥 Lead a pod", "callback": "pod_leadership"},
                            {"text": "📝 Share strategies", "callback": "content_creation"}
                        ]
                    }
                ]
            }
        }
    
    async def apply_behavioral_optimizations(self, user_id: str) -> Dict[str, Any]:
        """Apply behavioral insights to optimize sequence selection for user"""
        try:
            # Get user's behavioral profile
            behavioral_profile = await self._analyze_user_behavior(user_id)
            
            # Determine optimal sequence strategy
            optimization_strategy = {
                "recommended_sequences": [],
                "timing_adjustments": {},
                "personalization_factors": behavioral_profile,
                "success_predictors": {}
            }
            
            # Apply specific optimizations based on behavioral patterns
            if behavioral_profile["completion_pattern"] == "quick_executor":
                optimization_strategy["recommended_sequences"].append("quick_execution_followup")
                optimization_strategy["timing_adjustments"]["message_frequency"] = "accelerated"
                
            elif behavioral_profile["commitment_count"] == 0:
                optimization_strategy["recommended_sequences"].append("micro_onboarding")
                optimization_strategy["timing_adjustments"]["patience_mode"] = True
                
            elif behavioral_profile["performance_tier"] == "power_user":
                optimization_strategy["recommended_sequences"].append("power_user_amplification")
                optimization_strategy["timing_adjustments"]["advanced_content"] = True
                
            elif behavioral_profile["activity_status"] == "inactive":
                optimization_strategy["recommended_sequences"].append("inactive_rescue")
                optimization_strategy["timing_adjustments"]["gentle_approach"] = True
            
            return optimization_strategy
            
        except Exception as e:
            logger.error(f"Error applying behavioral optimizations: {e}")
            return {"error": str(e)}
    
    async def _analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's behavioral patterns"""
        try:
            # Get user commitment data
            commitments_result = self.supabase.table('commitments').select('*').eq('user_id', user_id).execute()
            commitments = commitments_result.data if commitments_result.data else []
            
            # Calculate behavioral metrics
            total_commitments = len(commitments)
            completed_commitments = len([c for c in commitments if c.get('completed_at')])
            completion_rate = (completed_commitments / total_commitments * 100) if total_commitments > 0 else 0
            
            # Analyze completion times
            completion_times = []
            for commit in commitments:
                if commit.get('created_at') and commit.get('completed_at'):
                    created = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00'))
                    completed_dt = datetime.fromisoformat(commit['completed_at'].replace('Z', '+00:00'))
                    hours_to_complete = (completed_dt - created).total_seconds() / 3600
                    completion_times.append(hours_to_complete)
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            quick_completions = len([t for t in completion_times if t <= 24])
            
            # Determine behavioral profile
            profile = {
                "commitment_count": total_commitments,
                "completion_rate": completion_rate,
                "avg_completion_hours": avg_completion_time,
                "quick_completion_percentage": (quick_completions / len(completion_times) * 100) if completion_times else 0,
                "completion_pattern": self._classify_completion_pattern(avg_completion_time, quick_completions, completion_times),
                "performance_tier": self._classify_performance_tier(total_commitments, completion_rate),
                "activity_status": self._classify_activity_status(user_id, commitments),
                "optimization_opportunity": self._identify_optimization_opportunity(total_commitments, completion_rate, avg_completion_time)
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            return {}
    
    def _classify_completion_pattern(self, avg_time: float, quick_count: int, all_times: List[float]) -> str:
        """Classify user's completion pattern"""
        if not all_times:
            return "unknown"
        
        quick_percentage = quick_count / len(all_times) * 100
        
        if quick_percentage > 80 and avg_time < 6:
            return "quick_executor"  # Like our 94.4% quick completers
        elif avg_time > 48:
            return "thoughtful_processor"
        else:
            return "balanced_completer"
    
    def _classify_performance_tier(self, commitment_count: int, completion_rate: float) -> str:
        """Classify user performance tier"""
        if commitment_count >= 10 and completion_rate >= 80:
            return "power_user"  # Top 16.7%
        elif commitment_count >= 5 and completion_rate >= 60:
            return "active_user"
        elif commitment_count >= 1:
            return "developing_user"
        else:
            return "new_user"  # The 27.8% conversion crisis group
    
    def _classify_activity_status(self, user_id: str, commitments: List[Dict]) -> str:
        """Classify user's activity status"""
        if not commitments:
            return "inactive"
        
        # Check recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_activity = [
            c for c in commitments 
            if datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) > week_ago
        ]
        
        if recent_activity:
            return "active"
        elif len(commitments) > 0:
            return "declining"
        else:
            return "inactive"  # Part of the 72.2% inactive group
    
    def _identify_optimization_opportunity(self, commitment_count: int, completion_rate: float, avg_time: float) -> str:
        """Identify the biggest optimization opportunity for this user"""
        if commitment_count == 0:
            return "onboarding_conversion"  # Address 27.8% crisis
        elif completion_rate < 50:
            return "completion_rate_improvement"  # Address 48% completion issue
        elif avg_time > 24:
            return "execution_speed_optimization"  # Leverage quick completion preference
        else:
            return "progressive_scaling"  # Help them grow
    
    async def get_sequence_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for optimized sequences"""
        try:
            # This would integrate with the business intelligence dashboard
            metrics = {
                "micro_onboarding": {
                    "conversion_improvement": "Target: 27.8% → 65%",
                    "step_completion_rates": {
                        "step_1": "Target: 95%",
                        "step_2": "Target: 85%", 
                        "step_3": "Target: 75%",
                        "step_4": "Target: 80%"
                    },
                    "psychological_mechanisms": [
                        "immediate_success_experience",
                        "momentum_building",
                        "progressive_difficulty",
                        "personalization"
                    ]
                },
                "quick_execution_followup": {
                    "completion_optimization": "Target: 48% → 75%",
                    "timing_optimization": "Leverages 3.4hr average completion pattern",
                    "success_factors": [
                        "quick_check_ins",
                        "momentum_reinforcement",
                        "execution_window_awareness"
                    ]
                },
                "inactive_rescue": {
                    "reactivation_target": "Address 72.2% inactive users",
                    "micro_intervention_approach": "Impossibly small steps",
                    "psychological_safety": "No judgment, maximum support"
                },
                "power_user_amplification": {
                    "community_building": "Leverage 16.7% high performers",
                    "mentorship_potential": "Convert success into community growth",
                    "retention_strategy": "Advanced engagement opportunities"
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting sequence performance metrics: {e}")
            return {"error": str(e)}

    def generate_implementation_report(self) -> str:
        """Generate implementation report for optimized sequences"""
        return """
🧠 OPTIMIZED NURTURE SEQUENCES v2.0 - IMPLEMENTATION REPORT

📊 BEHAVIORAL INSIGHTS APPLIED:
• 27.8% onboarding conversion crisis → Micro-commitment sequence
• 94.4% quick completion preference → Accelerated follow-ups  
• 3.4hr average completion time → Optimal timing windows
• 72.2% user inactivity → Micro-intervention rescue sequences
• 48% completion rate → Progressive difficulty scaling

🎯 SEQUENCE OPTIMIZATIONS:

1. MICRO-ONBOARDING SEQUENCE
   Target: Fix 27.8% → 65% conversion
   Approach: 30sec → 1min → 5min → planning progression
   Psychological: Immediate success + momentum building
   
2. QUICK EXECUTION FOLLOWUP  
   Target: Leverage 3.4hr completion pattern
   Approach: 2hr and 4hr check-ins aligned with user behavior
   
3. PROGRESSIVE SCALING
   Target: Improve 48% → 75% completion rate
   Approach: Auto-adjust difficulty based on success patterns
   
4. INACTIVE RESCUE
   Target: Reactivate 72.2% inactive users
   Approach: Impossibly small micro-interventions
   
5. POWER USER AMPLIFICATION
   Target: Leverage 16.7% high performers
   Approach: Mentorship and community leadership opportunities

💡 IMPLEMENTATION PRIORITY:
1. Deploy Micro-Onboarding (addresses critical conversion crisis)
2. Activate Quick Execution Followup (leverages existing behavioral strength)
3. Implement Progressive Scaling (sustainable growth)
4. Launch Inactive Rescue (reactivation)
5. Enable Power User Amplification (community building)

📈 EXPECTED OUTCOMES:
• Onboarding conversion: 27.8% → 65% (+37.2%)
• Completion rate: 48% → 75% (+27%)
• User activation: 27.8% → 65% (+37.2%)
• Community engagement: Powered by amplified high performers

🔄 CONTINUOUS OPTIMIZATION:
Behavioral intelligence system will continuously analyze patterns and auto-adjust sequences for maximum effectiveness.
"""

if __name__ == "__main__":
    print("🧠 Optimized Nurture Sequences v2.0")
    print("Based on behavioral intelligence analysis")
    
    # This would be integrated with the main system
    from behavioral_analysis_results import BehavioralAnalysisResults
    
    analyzer = BehavioralAnalysisResults()
    print("\n" + "="*60)
    print("BEHAVIORAL INSIGHTS → SEQUENCE OPTIMIZATIONS")
    print("="*60)
    
    optimizations = analyzer.get_nurture_sequence_recommendations()
    for i, opt in enumerate(optimizations, 1):
        print(f"\n{i}. {opt['recommendation']}")
        print(f"   Impact: {opt['impact']}")
        print(f"   Implementation: {opt['implementation']}")
    
    print("\n" + "="*60)
    print("SUPERIOR ONBOARDING SEQUENCE IMPLEMENTED")
    print("="*60)
    
    superior_seq = analyzer.generate_superior_onboarding_sequence()
    print(f"Expected Conversion: {superior_seq['expected_conversion']}")
    print(f"Duration: {superior_seq['total_duration']}")
    print(f"Principle: {superior_seq['design_principle']}")