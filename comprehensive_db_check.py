#!/usr/bin/env python3
"""
COMPREHENSIVE DEVELOPMENT DATABASE STATE
Phase 1 Development - Complete database assessment
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load development environment
load_dotenv()

def get_all_tables():
    """Get all tables by testing common table names"""
    
    url = os.getenv("DEV_SUPABASE_URL")
    key = os.getenv("DEV_SUPABASE_KEY") 
    
    supabase = create_client(url, key)
    
    # Common table names to test
    possible_tables = [
        # Core tables
        'users', 'commitments', 'pods', 'pod_memberships',
        # User management 
        'user_roles', 'user_profiles', 'role_assignments',
        # Nurture system
        'nurture_sequences', 'nurture_templates', 'user_sequence_state',
        # Analytics and tracking
        'feedback', 'user_analytics', 'pod_analytics',
        'commitment_reminders', 'meeting_attendance',
        # Admin and system
        'feature_flags', 'system_metrics', 'bot_interactions',
        'waiting_list', 'payments', 'commitment_edits'
    ]
    
    existing_tables = {}
    
    print("🔍 SCANNING FOR ALL TABLES:")
    for table in possible_tables:
        try:
            result = supabase.table(table).select("*", count="exact").limit(0).execute()
            row_count = result.count if result.count is not None else 0
            existing_tables[table] = row_count
            print(f"   ✅ {table}: {row_count} rows")
        except Exception:
            # Table doesn't exist - skip silently
            pass
    
    return existing_tables, supabase

def analyze_current_state():
    """Analyze current database state and provide recommendations"""
    
    print("🚀 COMPREHENSIVE DEVELOPMENT DATABASE STATE")
    print("=" * 60)
    
    existing_tables, supabase = get_all_tables()
    
    print(f"\n📊 FOUND {len(existing_tables)} TABLES:")
    
    total_rows = sum(existing_tables.values())
    print(f"   Total rows across all tables: {total_rows:,}")
    
    # Categorize tables
    core_tables = ['users', 'commitments', 'pods', 'pod_memberships']
    core_exists = [t for t in core_tables if t in existing_tables]
    
    print(f"\n🎯 CORE SYSTEM STATUS:")
    print(f"   Core tables present: {len(core_exists)}/4")
    for table in core_tables:
        if table in existing_tables:
            print(f"   ✅ {table}: {existing_tables[table]} rows")
        else:
            print(f"   ❌ {table}: MISSING")
    
    # Check for system readiness
    print(f"\n⚙️  SYSTEM READINESS:")
    if len(core_exists) == 4:
        print("   ✅ All core tables present - Basic functionality available")
        
        # Check data quality
        if existing_tables.get('users', 0) > 0 and existing_tables.get('commitments', 0) > 0:
            print("   ✅ Has user data and commitments - Active system")
            system_state = "ACTIVE"
        else:
            print("   ⚠️  Tables exist but minimal data - Ready for testing")
            system_state = "READY"
    else:
        print("   ❌ Missing core tables - Needs schema setup")
        system_state = "NEEDS_SETUP"
    
    # Check advanced features
    advanced_tables = ['nurture_sequences', 'feature_flags', 'user_sequence_state']
    advanced_exists = [t for t in advanced_tables if t in existing_tables]
    
    print(f"\n🚀 ADVANCED FEATURES:")
    print(f"   Advanced tables present: {len(advanced_exists)}/{len(advanced_tables)}")
    for table in advanced_tables:
        if table in existing_tables:
            print(f"   ✅ {table}: {existing_tables[table]} rows")
        else:
            print(f"   ❌ {table}: MISSING")
    
    # Test bot functionality by checking environment
    print(f"\n🤖 BOT CONFIGURATION CHECK:")
    bot_token = os.getenv("BOT_TOKEN")
    env = os.getenv("ENVIRONMENT")
    safe_mode = os.getenv("SAFE_MODE")
    
    if bot_token:
        bot_id = bot_token.split(':')[0]
        print(f"   ✅ Bot token configured (ID: {bot_id})")
        print(f"   ✅ Environment: {env}")
        print(f"   ✅ Safe mode: {safe_mode}")
        
        if bot_id == "8308612114":  # @TPM_superbot
            print("   ✅ Using development bot (@TPM_superbot)")
        else:
            print("   ⚠️  Unknown bot token")
    else:
        print("   ❌ Bot token not configured")
    
    # Database activity check
    if 'commitments' in existing_tables and existing_tables['commitments'] > 0:
        print(f"\n📈 RECENT ACTIVITY CHECK:")
        try:
            recent = supabase.table('commitments').select("created_at, status").order("created_at", desc=True).limit(5).execute()
            if recent.data:
                latest_commit = recent.data[0]['created_at']
                active_count = len([c for c in recent.data if c['status'] == 'active'])
                completed_count = len([c for c in recent.data if c['status'] == 'completed'])
                
                print(f"   Latest commitment: {latest_commit[:10]}")
                print(f"   Recent commitments: {active_count} active, {completed_count} completed")
            else:
                print("   No commitment data")
        except Exception as e:
            print(f"   Error checking activity: {e}")
    
    return {
        'state': system_state,
        'tables': existing_tables,
        'core_complete': len(core_exists) == 4,
        'has_data': total_rows > 0,
        'bot_configured': bool(bot_token)
    }

if __name__ == "__main__":
    analysis = analyze_current_state()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 PHASE 1 DEVELOPMENT ASSESSMENT COMPLETE")
    print(f"   System State: {analysis['state']}")
    print(f"   Tables Found: {len(analysis['tables'])}")
    print(f"   Core Complete: {analysis['core_complete']}")
    print(f"   Has Data: {analysis['has_data']}")
    print(f"   Bot Ready: {analysis['bot_configured']}")
    print(f"=" * 60)