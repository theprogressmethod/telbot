#!/usr/bin/env python3
"""
Create form_submissions table directly via Supabase
"""

import os
import logging
from dotenv import load_dotenv
from supabase import create_client
import requests

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials")
    exit(1)

# Create the table using REST API
def create_table_via_api():
    """Create the table using Supabase REST API"""
    logger.info("📋 Creating form_submissions table via API...")
    
    # First, let's try to create a minimal version to test
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try inserting a test record to force table creation
    test_data = {
        "form_type": "test",
        "form_data": {"test": "data"},
        "user_name": "Test User",
        "user_email": "test@example.com",
        "status": "test",
        "source": "test"
    }
    
    try:
        # This will fail but might give us better error info
        result = supabase.table("form_submissions").insert(test_data).execute()
        logger.info("✅ Table exists or was created!")
        # Delete the test record
        supabase.table("form_submissions").delete().eq("source", "test").execute()
        return True
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            logger.info("❌ Table doesn't exist and can't be auto-created")
            logger.info("📝 Please run the following SQL in Supabase Dashboard:")
            logger.info("   URL: https://supabase.com/dashboard/project/apfiwfkpdhslfavnncsl/sql/new")
            logger.info("\n" + "="*60)
            print("""
-- Create form_submissions table
CREATE TABLE IF NOT EXISTS public.form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_type TEXT DEFAULT 'user_registration',
    form_data JSONB DEFAULT '{}',
    user_name TEXT,
    user_email TEXT,
    user_phone TEXT,
    telegram_user_id BIGINT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    source TEXT DEFAULT 'form',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_form_submissions_email ON public.form_submissions(user_email);
CREATE INDEX idx_form_submissions_status ON public.form_submissions(status);
""")
            logger.info("="*60)
            return False
        else:
            logger.error(f"Unexpected error: {e}")
            return False

if __name__ == "__main__":
    create_table_via_api()