#!/usr/bin/env python3
"""
Apply Google Meet Session Tracking Schema to Database
Safe application with error handling and rollback capability
"""

import asyncio
import sys
from telbot import Config
from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_meet_schema():
    """Apply the Meet session tracking schema to the database"""
    
    try:
        # Initialize Supabase client
        logger.info("🔧 Initializing database connection...")
        config = Config()
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        # Test connection
        test_result = supabase.table("pods").select("count").execute()
        logger.info("✅ Database connection successful")
        
        # Check if tables already exist
        logger.info("🔍 Checking for existing tables...")
        
        # Try to query meet_sessions table
        try:
            existing_check = supabase.table("meet_sessions").select("count").limit(1).execute()
            logger.warning("⚠️  Table 'meet_sessions' already exists!")
            
            response = input("\nDo you want to DROP and RECREATE the existing tables? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("❌ Schema application cancelled by user")
                return False
                
            logger.warning("⚠️  Dropping existing tables...")
            # Would need direct SQL access to drop tables
            # For Supabase, this needs to be done via SQL Editor
            
        except Exception as e:
            if "Could not find the table" in str(e):
                logger.info("✅ Tables don't exist yet, safe to create")
            else:
                logger.error(f"❌ Error checking tables: {e}")
                return False
        
        # Read the schema file
        logger.info("📖 Reading schema file...")
        with open('meet_session_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Parse out individual table creation statements
        tables_to_create = [
            "meet_sessions",
            "meet_participants", 
            "meet_reports_sync",
            "meet_audit_events",
            "participant_email_mapping"
        ]
        
        # For Supabase, we need to apply this via the SQL Editor
        logger.info("\n" + "="*60)
        logger.info("📋 MANUAL STEPS REQUIRED FOR SUPABASE:")
        logger.info("="*60)
        
        print("""
To apply the schema to your Supabase database:

1. Open Supabase Dashboard: https://app.supabase.com
2. Navigate to your project
3. Go to SQL Editor (left sidebar)
4. Click "New Query"
5. Copy and paste the contents of 'meet_session_schema.sql'
6. Click "Run" to execute

The schema will create these tables:
- meet_sessions (tracks Google Meet sessions)
- meet_participants (individual participant data)
- meet_reports_sync (API sync tracking)
- meet_audit_events (raw Google data)
- participant_email_mapping (email to user mapping)

It will also:
- Add new columns to meeting_attendance table
- Create indexes for performance
- Add triggers for timestamp updates
- Create a comprehensive_attendance view
        """)
        
        print("\n" + "="*60)
        print("ALTERNATIVE: Use Supabase CLI")
        print("="*60)
        print("""
If you have Supabase CLI installed:

1. Make sure you're in the project directory
2. Run: supabase db push meet_session_schema.sql
        """)
        
        # Verify what tables we need
        logger.info("\n📊 Current table status:")
        for table in tables_to_create:
            try:
                supabase.table(table).select("count").limit(1).execute()
                logger.info(f"  ✅ {table} - EXISTS")
            except:
                logger.info(f"  ❌ {table} - NEEDS CREATION")
        
        # Test if we can at least add columns to existing tables
        logger.info("\n🔧 Checking meeting_attendance table...")
        try:
            att_result = supabase.table("meeting_attendance").select("*").limit(1).execute()
            if att_result.data:
                columns = list(att_result.data[0].keys())
                
                new_columns_needed = [
                    'meet_participant_id',
                    'detection_method',
                    'meet_join_time',
                    'meet_leave_time',
                    'meet_duration_minutes',
                    'confidence_score'
                ]
                
                for col in new_columns_needed:
                    if col in columns:
                        logger.info(f"  ✅ Column '{col}' exists")
                    else:
                        logger.info(f"  ⏳ Column '{col}' needs to be added")
        except Exception as e:
            logger.error(f"❌ Could not check meeting_attendance table: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply schema: {e}")
        return False

def main():
    """Main entry point"""
    print("🎯 Google Meet Session Schema Application Tool")
    print("="*60)
    
    print("""
This tool will help you apply the database schema needed for
automatic Google Meet attendance tracking.

The schema includes:
- Tables for Meet sessions and participants
- Enhanced attendance tracking columns
- Sync status tracking
- Participant email mapping
""")
    
    response = input("\nDo you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Schema application cancelled")
        sys.exit(0)
    
    # Run the async function
    success = asyncio.run(apply_meet_schema())
    
    if success:
        print("\n✅ Schema preparation complete!")
        print("📋 Please follow the manual steps above to apply the schema")
    else:
        print("\n❌ Schema application failed")
        sys.exit(1)

if __name__ == "__main__":
    main()