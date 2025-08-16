#!/usr/bin/env python3
"""
Check users table schema and import Excel data
"""

import os
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import uuid

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_schema_and_import():
    """Check schema and import Excel data"""
    
    # Check existing users structure
    logger.info("🔍 Checking users table structure...")
    existing = supabase.table("users").select("*").limit(1).execute()
    
    if existing.data:
        logger.info("📋 Users table columns:")
        for key in existing.data[0].keys():
            logger.info(f"  - {key}")
    
    # Read Excel
    df = pd.read_excel("/Users/thomasmulhern/Downloads/Data import.xlsx")
    logger.info(f"📊 Processing {len(df)} Excel rows")
    
    # Get existing emails to avoid duplicates
    all_users = supabase.table("users").select("first_name, last_name, username, telegram_user_id").execute()
    existing_names = {f"{u.get('first_name', '')} {u.get('last_name', '')}".strip() for u in all_users.data}
    logger.info(f"Found {len(existing_names)} existing users")
    
    # Process Excel data with only valid columns
    new_users = []
    skipped = 0
    
    for idx, row in df.iterrows():
        first_name = str(row.get('firstName', '')).strip()
        last_name = str(row.get('lastName', '')).strip()
        full_name = f"{first_name} {last_name}".strip()
        email = str(row.get('(Contact Info) Best email to reach you? ', '')).strip()
        phone = str(row.get('Best number for you? ', '')).strip()
        
        # Skip if user already exists
        if full_name in existing_names:
            logger.info(f"⏭️ Skipping existing user: {full_name}")
            skipped += 1
            continue
        
        # Generate fake telegram_user_id for Excel imports (starting at 100000)
        fake_telegram_id = 100000 + idx
        
        # Create user with only valid columns
        user_data = {
            "first_name": first_name or None,
            "last_name": last_name or None,
            "username": email.split('@')[0] if email and email != 'nan' else f"user_{idx}",
            "telegram_user_id": fake_telegram_id,
            "total_commitments": 0,
            "is_bot": False
        }
        
        new_users.append(user_data)
        logger.info(f"✅ {full_name} (telegram_id: {fake_telegram_id})")
    
    if skipped > 0:
        logger.info(f"⏭️ Skipped {skipped} existing users")
    
    if not new_users:
        logger.info("ℹ️ No new users to import")
        return True
    
    # Import users
    try:
        logger.info(f"📤 Importing {len(new_users)} new users...")
        result = supabase.table("users").insert(new_users).execute()
        
        if result.data:
            logger.info(f"✅ Successfully imported {len(result.data)} users!")
            
            # Show imported users
            for user in result.data:
                logger.info(f"  - {user['first_name']} {user['last_name']} (ID: {user['telegram_user_id']})")
                
            return True
        else:
            logger.error("❌ No data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    check_schema_and_import()