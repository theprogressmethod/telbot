"""
WEEK 1 MVP CONFIGURATION
========================
Ferrari engine running as a go-kart
Only activate core features, disable all advanced systems
"""

# WEEK 1 FEATURE FLAGS - STRICT LIMITS
WEEK_1_FEATURES = {
    # ✅ ACTIVATE - Core Week 1 functionality only
    'user_registration': True,      # Basic user sign-up via Telegram
    'basic_commitments': True,       # /commit, /done, /list commands
    'smart_scoring': True,           # AI scoring (but not ML systems)
    'smart_3_retry': True,           # Week 1 differentiator
    'simple_pods': True,             # Manual pod assignment only
    'basic_nurture': True,           # ONE simple sequence
    'basic_commands': True,          # Core bot commands
    
    # ❌ DISABLE - All Phase 2/3 features
    'advanced_analytics': False,     # No complex analytics
    'ml_systems': False,             # No ML optimization
    'predictive_analytics': False,   # No predictive systems
    'automated_scheduling': False,   # No auto-scheduling
    'stakeholder_dashboards': False, # No complex dashboards
    'payment_processing': False,     # No payments yet
    'web_intake': False,             # Telegram only for Week 1
    'auto_scaling': False,           # No scaling systems
    'intelligent_optimization': False, # No AI optimization
    'adaptive_personalization': False, # No personalization engine
    'anomaly_detection': False,      # No anomaly systems
    'enhanced_metrics': False,       # No enhanced metrics
    'alerting_system': False,        # No complex alerts
    'complex_nurture': False,        # No multi-path sequences
    'pod_analytics': False,          # No pod performance tracking
    'leaderboards': False,           # No gamification yet
    'attendance_tracking': False,    # No meeting attendance
    'role_management': False,        # Simple roles only
}

# ALLOWED BOT COMMANDS FOR WEEK 1
WEEK_1_COMMANDS = [
    '/start',      # Welcome message
    '/commit',     # Create commitment with SMART scoring
    '/done',       # Mark commitment complete
    '/list',       # Show active commitments
    '/help',       # Basic help
    '/feedback',   # Simple feedback collection
    '/mypod',      # Show pod assignment (if any)
]

# DISABLED COMMANDS (comment these out in telbot.py)
DISABLED_COMMANDS = [
    '/stats',      # Advanced analytics
    '/leaderboard', # Gamification
    '/champions',   # All-time leaders
    '/streaks',     # Streak tracking
    '/progress',    # Complex progress
    '/adminstats',  # Admin analytics
    '/grant_role',  # Role management
    '/sequences',   # Complex nurture
    '/podweek',     # Pod analytics
    '/attendance',  # Meeting tracking
    '/track',       # Detailed tracking
    '/checkin',     # Accountability
    '/streakboost', # Gamification
]

# DATABASE TABLES FOR WEEK 1
WEEK_1_TABLES = {
    'required': [
        'users',           # Core user data
        'commitments',     # Commitment tracking
        'pods',            # Basic pod structure
        'pod_memberships', # User-pod links
    ],
    'optional': [
        'feedback',        # User feedback
        'feature_flags',   # Feature control
        'user_roles',      # Basic permissions
    ],
    'ignore': [
        # All analytics tables
        'user_analytics',
        'pod_analytics', 
        'commitment_analytics',
        # All complex systems
        'ml_model_state',
        'prediction_logs',
        'optimization_runs',
        # Payment/subscription
        'payments',
        'subscriptions',
        'stripe_events',
    ]
}

# SIMPLE NURTURE SEQUENCE FOR WEEK 1
WEEK_1_NURTURE = {
    'welcome_sequence': {
        'trigger': 'user_registration',
        'messages': [
            {
                'delay_hours': 0,
                'text': "Welcome to The Progress Method! 🎯\n\nStart with /commit to create your first commitment."
            },
            {
                'delay_hours': 24,
                'text': "How's your first commitment going? Use /done to mark it complete when ready! 💪"
            },
            {
                'delay_hours': 72,
                'text': "Consistency is key! Try to complete one commitment daily. Use /list to see your active goals."
            }
        ]
    }
}

# WEEK 1 SUCCESS METRICS
WEEK_1_METRICS = {
    'user_can_register': True,
    'user_can_create_commitment': True,
    'smart_scoring_works': True,
    'three_retry_works': True,
    'user_can_complete_commitment': True,
    'user_can_list_commitments': True,
    'basic_pod_assignment': True,
    'one_nurture_sequence': True,
    'bot_responds_quickly': True,  # <2 seconds
    'no_crashes': True,             # With 10 users
}

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled for Week 1"""
    return WEEK_1_FEATURES.get(feature_name, False)

def is_command_allowed(command: str) -> bool:
    """Check if a command is allowed in Week 1"""
    return command in WEEK_1_COMMANDS

# DEPLOYMENT NOTES
"""
Week 1 Deployment Checklist:
1. ✅ Feature flags configured (this file)
2. ⬜ Phase 2/3 imports commented in main.py
3. ⬜ Advanced command handlers disabled in telbot.py
4. ⬜ Database has only Week 1 tables
5. ⬜ Test with @TPM_superbot
6. ⬜ Max 10 beta users initially
7. ⬜ Monitor for any crashes
8. ⬜ Verify <2 second response times
"""

print("📋 Week 1 Configuration Loaded")
print(f"   ✅ Enabled features: {sum(WEEK_1_FEATURES.values())}")
print(f"   ❌ Disabled features: {len(WEEK_1_FEATURES) - sum(WEEK_1_FEATURES.values())}")
print(f"   📝 Allowed commands: {len(WEEK_1_COMMANDS)}")
print(f"   🚫 Disabled commands: {len(DISABLED_COMMANDS)}")