#!/usr/bin/env python3
"""
Run First Impression Schema Migration
Adds the necessary database columns for tracking the 100x first impression experience
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
    """Run the first impression schema migration"""
    
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
        
        # Read migration SQL
        migration_file = "first_impression_schema_migration.sql"
        if not os.path.exists(migration_file):
            logger.error(f"❌ Migration file {migration_file} not found")
            return False
            
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        logger.info("📖 Read migration SQL file")
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        logger.info(f"🔄 Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith('--'):
                try:
                    logger.info(f"📝 Executing statement {i}/{len(statements)}")
                    logger.debug(f"SQL: {statement[:100]}...")
                    
                    # Execute the SQL statement
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    
                    if result.data:
                        logger.info(f"✅ Statement {i} executed successfully")
                    else:
                        logger.warning(f"⚠️ Statement {i} executed but returned no data")
                        
                except Exception as e:
                    logger.error(f"❌ Error executing statement {i}: {e}")
                    logger.error(f"Statement: {statement}")
                    return False
        
        logger.info("🎉 Migration completed successfully!")
        
        # Verify the migration by checking if columns exist
        try:
            # Test if new columns exist by querying them
            test_query = supabase.table("users").select("onboarding_started_at, first_impression_started_at").limit(1).execute()
            logger.info("✅ Migration verification successful - new columns are accessible")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting First Impression Schema Migration")
    
    success = run_migration()
    
    if success:
        logger.info("🎉 First Impression Schema Migration completed successfully!")
        logger.info("✅ The 100x experience can now track detailed user journey")
        sys.exit(0)
    else:
        logger.error("❌ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()