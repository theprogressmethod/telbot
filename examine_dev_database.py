#!/usr/bin/env python3
"""
DEVELOPMENT DATABASE EXAMINATION SCRIPT
Phase 1 Development - Database State Assessment
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load development environment
load_dotenv()

def examine_database():
    """Examine the development database state"""
    
    # Use development credentials only
    url = os.getenv("DEV_SUPABASE_URL")
    key = os.getenv("DEV_SUPABASE_KEY") 
    
    if not url or not key:
        print("❌ Development database credentials not found")
        return False
        
    print(f"🔍 Examining Development Database")
    print(f"   URL: {url}")
    print(f"   Key: {key[:20]}...")
    
    try:
        # Create client
        supabase = create_client(url, key)
        print("✅ Database connection successful")
        
        # Get list of tables
        print("\n📊 EXAMINING EXISTING TABLES:")
        
        # Try to query information_schema to see what tables exist
        result = supabase.rpc('execute_sql', {
            'query': """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
            """
        }).execute()
        
        if result.data:
            existing_tables = [row['table_name'] for row in result.data]
            print(f"   Found {len(existing_tables)} tables:")
            for table in existing_tables:
                print(f"   ✓ {table}")
                
                # Get row count for each table
                try:
                    count_result = supabase.table(table).select("*", count="exact").execute()
                    count = count_result.count if count_result.count is not None else 0
                    print(f"     → {count} rows")
                except Exception as e:
                    print(f"     → Unable to count rows: {str(e)}")
        else:
            print("   No tables found or unable to query schema")
            
        # Check for critical tables
        print("\n🎯 CHECKING CRITICAL TABLES:")
        critical_tables = ['users', 'commitments', 'pods', 'pod_memberships']
        
        for table in critical_tables:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table} - accessible")
                
                # Get sample data structure
                if result.data:
                    sample = result.data[0]
                    print(f"      Sample fields: {list(sample.keys())[:5]}...")
                else:
                    print(f"      Empty table")
                    
            except Exception as e:
                print(f"   ❌ {table} - {str(e)}")
                
        # Check for any data that might be production-related
        print("\n⚠️  CHECKING FOR PRODUCTION DATA:")
        try:
            users_result = supabase.table('users').select("username, created_at").limit(5).execute()
            if users_result.data:
                print(f"   Found {len(users_result.data)} sample users:")
                for user in users_result.data:
                    username = user.get('username', 'No username')
                    created = user.get('created_at', 'Unknown date')
                    print(f"   - {username} (created: {created})")
            else:
                print("   No users found")
        except Exception as e:
            print(f"   Unable to check users: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_schema_file():
    """Check if we have a schema file to compare against"""
    
    print("\n📋 CHECKING SCHEMA DEFINITION FILES:")
    
    schema_files = [
        'progress_method_schema.sql',
        'database_schema.py', 
        'apply_production_schema.py',
        'apply_enhanced_schema.py'
    ]
    
    for filename in schema_files:
        filepath = f"/Users/thomasmulhern/projects/telbot_env/telbot/{filename}"
        if os.path.exists(filepath):
            print(f"   ✅ Found {filename}")
            
            # Get file size
            size = os.path.getsize(filepath)
            print(f"      Size: {size:,} bytes")
        else:
            print(f"   ❌ Missing {filename}")

if __name__ == "__main__":
    print("🚀 PHASE 1 DEVELOPMENT DATABASE EXAMINATION")
    print("=" * 50)
    print("⚠️  DEVELOPMENT ENVIRONMENT ONLY")
    print("⚠️  NO PRODUCTION ACCESS OR MODIFICATIONS")
    print("=" * 50)
    
    # Check schema files
    check_schema_file()
    
    # Examine database
    success = examine_database()
    
    if success:
        print("\n✅ Database examination complete")
    else:
        print("\n❌ Database examination failed")
        
    print("\n📝 Next steps will be determined based on findings")