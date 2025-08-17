#!/usr/bin/env python3
"""
Simple Migration for First Impression Columns
Uses direct table operations instead of raw SQL
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the first impression migration using table operations"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Connected to Supabase")
        
        # Test if columns already exist by trying to select them
        try:
            test_query = supabase.table("users").select("onboarding_started_at, first_impression_started_at").limit(1).execute()
            logger.info("✅ Migration columns already exist - skipping migration")
            return True
        except Exception as e:
            logger.info("📝 Columns don't exist yet, migration needed")
        
        # Since we can't run DDL through Supabase client, let's try a different approach
        # We'll create a test record to see what happens
        logger.info("🔄 Testing column creation through insert operation...")
        
        try:
            # Try to insert a record with the new columns
            test_result = supabase.table("users").insert({
                "telegram_user_id": 999999999,  # Test user ID
                "first_name": "Migration Test",
                "username": "migration_test",
                "email": "migration_test@test.com",
                "status": "test",
                "onboarding_started_at": "2025-01-01T00:00:00.000Z",
                "first_impression_started_at": "2025-01-01T00:00:00.000Z",
                "first_commitment_at": "2025-01-01T00:00:00.000Z",
                "first_celebration_at": "2025-01-01T00:00:00.000Z",
                "bigger_goal_collected_at": "2025-01-01T00:00:00.000Z"
            }).execute()
            
            if test_result.data:
                logger.info("✅ Test insert successful - columns exist!")
                
                # Clean up test record
                supabase.table("users").delete().eq("telegram_user_id", 999999999).execute()
                logger.info("🧹 Cleaned up test record")
                
                return True
            else:
                logger.error("❌ Test insert failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Column test failed: {e}")
            logger.info("🔧 You need to add the columns manually in Supabase dashboard")
            logger.info("📋 Run this SQL in the Supabase SQL editor:")
            print("\n" + "="*60)
            print("COPY AND RUN THIS SQL IN SUPABASE DASHBOARD:")
            print("="*60)
            with open("first_impression_schema_migration.sql", "r") as f:
                print(f.read())
            print("="*60)
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting Simple First Impression Migration Check")
    
    success = run_migration()
    
    if success:
        logger.info("🎉 Migration verification successful!")
        logger.info("✅ The 100x experience can now track detailed user journey")
        sys.exit(0)
    else:
        logger.error("❌ Migration needed - see instructions above")
        sys.exit(1)

if __name__ == "__main__":
    main()