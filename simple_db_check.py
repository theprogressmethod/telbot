#!/usr/bin/env python3
"""
SIMPLE DEVELOPMENT DATABASE CHECK
Phase 1 Development - Direct table access
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load development environment
load_dotenv()

def check_database():
    """Check development database with direct table queries"""
    
    # Use development credentials only
    url = os.getenv("DEV_SUPABASE_URL")
    key = os.getenv("DEV_SUPABASE_KEY") 
    
    print(f"🔍 DEVELOPMENT DATABASE CHECK")
    print(f"   URL: {url}")
    print(f"   Using development secret key")
    
    try:
        # Create client
        supabase = create_client(url, key)
        print("✅ Database connection successful")
        
        # Check for expected tables by attempting to query them
        print("\n📊 CHECKING FOR EXPECTED TABLES:")
        
        expected_tables = [
            'users',
            'commitments', 
            'pods',
            'pod_memberships',
            'user_roles',
            'role_assignments',
            'feedback',
            'user_profiles',
            'nurture_templates',
            'user_sequence_state'
        ]
        
        existing_tables = []
        table_data = {}
        
        for table in expected_tables:
            try:
                result = supabase.table(table).select("*", count="exact").limit(1).execute()
                row_count = result.count if result.count is not None else 0
                existing_tables.append(table)
                table_data[table] = {
                    'count': row_count,
                    'sample': result.data[0] if result.data else None
                }
                print(f"   ✅ {table}: {row_count} rows")
                
                # Show sample structure
                if result.data:
                    fields = list(result.data[0].keys())[:5]  # First 5 fields
                    print(f"      Fields: {', '.join(fields)}...")
                    
            except Exception as e:
                print(f"   ❌ {table}: {str(e)}")
                
        print(f"\n✅ Found {len(existing_tables)} tables out of {len(expected_tables)} expected")
        
        # Check for users to understand data state
        if 'users' in existing_tables:
            print(f"\n👥 USER DATA SAMPLE:")
            try:
                users = supabase.table('users').select("telegram_user_id, username, total_commitments, created_at").limit(3).execute()
                if users.data:
                    for user in users.data:
                        tid = user.get('telegram_user_id', 'N/A')
                        name = user.get('username', 'No username')
                        commits = user.get('total_commitments', 0)
                        created = user.get('created_at', 'Unknown')[:10] if user.get('created_at') else 'Unknown'
                        print(f"   - {name} (TG: {tid}, Commits: {commits}, Created: {created})")
                else:
                    print("   No users found")
            except Exception as e:
                print(f"   Error getting users: {e}")
                
        # Check for commitments to understand activity level
        if 'commitments' in existing_tables:
            print(f"\n🎯 COMMITMENT DATA SAMPLE:")
            try:
                commits = supabase.table('commitments').select("commitment, status, smart_score, created_at").limit(3).execute()
                if commits.data:
                    for commit in commits.data:
                        text = commit.get('commitment', 'No text')[:50] + '...'
                        status = commit.get('status', 'unknown')
                        score = commit.get('smart_score', 0)
                        created = commit.get('created_at', 'Unknown')[:10] if commit.get('created_at') else 'Unknown'
                        print(f"   - \"{text}\" ({status}, Score: {score}, {created})")
                else:
                    print("   No commitments found")
            except Exception as e:
                print(f"   Error getting commitments: {e}")
        
        return True, existing_tables, table_data
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False, [], {}

if __name__ == "__main__":
    print("🚀 PHASE 1 DEVELOPMENT DATABASE CHECK")
    print("=" * 50)
    print("⚠️  DEVELOPMENT ENVIRONMENT ONLY")
    print("=" * 50)
    
    success, tables, data = check_database()
    
    if success:
        print(f"\n✅ Database check complete - {len(tables)} tables found")
        
        if len(tables) == 0:
            print("\n🏗️  APPEARS TO BE EMPTY DATABASE - Ready for schema setup")
        elif len(tables) < 5:
            print("\n⚠️  PARTIAL SCHEMA - May need table creation")
        else:
            print("\n✅ SUBSTANTIAL SCHEMA - Database appears populated")
            
    else:
        print("\n❌ Database check failed")