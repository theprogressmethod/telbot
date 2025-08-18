#!/usr/bin/env python3
"""
Apply the user creation transaction function to prevent race conditions
"""

import os
import sys
from supabase import create_client

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables")
except ImportError:
    print("⚠️ Using system environment variables")

def apply_user_transaction():
    """Apply the user creation transaction function"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        missing_vars = []
        if not supabase_url:
            missing_vars.append("SUPABASE_URL")
        if not supabase_key:
            missing_vars.append("SUPABASE_KEY")
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    print("🚀 Applying user creation transaction function...")
    
    # Read the SQL file
    try:
        with open("user_creation_transaction.sql", "r") as f:
            sql_content = f.read()
        
        # Try different RPC function names
        try:
            result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        except Exception as e1:
            try:
                result = supabase.rpc('query', {'query': sql_content}).execute()
            except Exception as e2:
                print(f"❌ Could not execute SQL via RPC. Errors:")
                print(f"   exec_sql: {e1}")
                print(f"   query: {e2}")
                print("📋 Please run the following SQL manually in Supabase SQL Editor:")
                print("=" * 60)
                print(sql_content)
                print("=" * 60)
                return False
        
        print("✅ User creation transaction function applied successfully!")
        
        # Test the function
        print("🧪 Testing the function...")
        test_result = supabase.rpc('ensure_user_exists_atomic', {
            'p_telegram_user_id': 999999999,
            'p_first_name': 'Test User',
            'p_username': 'testuser'
        }).execute()
        
        if test_result.data:
            print(f"✅ Test successful: {test_result.data}")
        else:
            print("❌ Test failed - no data returned")
            
        return True
        
    except FileNotFoundError:
        print("❌ Error: user_creation_transaction.sql file not found")
        return False
    except Exception as e:
        print(f"❌ Error applying function: {e}")
        return False

if __name__ == "__main__":
    apply_user_transaction()