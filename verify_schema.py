#!/usr/bin/env python3
"""
Quick verification script for Meet schema application
"""

from telbot import Config
from supabase import create_client

def verify_schema():
    config = Config()
    supabase = create_client(config.supabase_url, config.supabase_key)
    
    print("🔍 SCHEMA VERIFICATION")
    print("=" * 40)
    
    # Test tables
    tables = [
        'meet_sessions',
        'meet_participants', 
        'meet_reports_sync',
        'meet_audit_events',
        'participant_email_mapping'
    ]
    
    success_count = 0
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table}")
            success_count += 1
        except:
            print(f"❌ {table}")
    
    print(f"\nResult: {success_count}/{len(tables)} tables found")
    
    if success_count == len(tables):
        print("\n🎉 SUCCESS! Schema applied correctly!")
        return True
    else:
        print("\n⚠️  Some tables missing - check for SQL errors")
        return False

if __name__ == "__main__":
    verify_schema()