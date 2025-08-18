#!/usr/bin/env python3
"""
Clean up duplicate user records created by emergency fallback systems
Identifies and safely removes duplicate users while preserving data integrity
"""

import os
import sys
from supabase import create_client
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Loaded environment variables")
except ImportError:
    logger.info("⚠️ Using system environment variables")

def cleanup_duplicate_users():
    """Find and clean up duplicate user records"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        missing_vars = []
        if not supabase_url:
            missing_vars.append("SUPABASE_URL")
        if not supabase_key:
            missing_vars.append("SUPABASE_KEY")
        logger.error(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("🔍 Starting duplicate user cleanup analysis...")
    
    try:
        # Find users with potentially problematic data patterns
        # 1. Users with emergency email patterns
        emergency_email_users = supabase.table("users").select("*").ilike("email", "%@telegram.emergency").execute()
        logger.info(f"📧 Found {len(emergency_email_users.data)} users with emergency email pattern")
        
        # 2. Users with @telegram.user email patterns  
        telegram_user_emails = supabase.table("users").select("*").ilike("email", "%@telegram.user").execute()
        logger.info(f"📧 Found {len(telegram_user_emails.data)} users with @telegram.user email pattern")
        
        # 3. Find actual duplicates by telegram_user_id
        all_users = supabase.table("users").select("telegram_user_id, id, first_name, email, created_at, total_commitments").execute()
        
        # Group by telegram_user_id to find duplicates
        user_groups = {}
        for user in all_users.data:
            telegram_id = user['telegram_user_id']
            if telegram_id not in user_groups:
                user_groups[telegram_id] = []
            user_groups[telegram_id].append(user)
        
        # Find groups with more than one user (duplicates)
        duplicates = {k: v for k, v in user_groups.items() if len(v) > 1}
        
        logger.info(f"🔍 Analysis Results:")
        logger.info(f"   📊 Total users: {len(all_users.data)}")
        logger.info(f"   📧 Emergency email users: {len(emergency_email_users.data)}")
        logger.info(f"   📧 @telegram.user email users: {len(telegram_user_emails.data)}")
        logger.info(f"   👥 Duplicate telegram_user_id groups: {len(duplicates)}")
        
        if len(duplicates) > 0:
            logger.info(f"\n🔍 Found {len(duplicates)} sets of duplicate users:")
            for telegram_id, users in duplicates.items():
                logger.info(f"\n   👤 Telegram ID {telegram_id} has {len(users)} records:")
                for i, user in enumerate(users):
                    logger.info(f"      {i+1}. UUID: {user['id'][:8]}... | Name: {user['first_name']} | Email: {user['email']} | Created: {user['created_at'][:10]} | Commitments: {user['total_commitments'] or 0}")
        
        # Clean up strategy:
        cleanup_actions = []
        
        # 1. Convert placeholder emails to NULL
        placeholder_email_count = len(emergency_email_users.data) + len(telegram_user_emails.data)
        if placeholder_email_count > 0:
            cleanup_actions.append(f"Set {placeholder_email_count} placeholder emails to NULL")
        
        # 2. For actual duplicates, keep the one with most data/activity
        users_to_delete = []
        for telegram_id, users in duplicates.items():
            # Sort by: commitments desc, created_at asc (keep oldest with most activity)
            sorted_users = sorted(users, key=lambda u: (-(u['total_commitments'] or 0), u['created_at']))
            keeper = sorted_users[0]
            to_delete = sorted_users[1:]
            
            logger.info(f"\n   🎯 For Telegram ID {telegram_id}:")
            logger.info(f"      ✅ KEEP: {keeper['id'][:8]}... (commitments: {keeper['total_commitments'] or 0}, created: {keeper['created_at'][:10]})")
            for user in to_delete:
                logger.info(f"      ❌ DELETE: {user['id'][:8]}... (commitments: {user['total_commitments'] or 0}, created: {user['created_at'][:10]})")
                users_to_delete.append(user['id'])
        
        if users_to_delete:
            cleanup_actions.append(f"Delete {len(users_to_delete)} duplicate user records")
        
        # Show cleanup plan
        if cleanup_actions:
            logger.info(f"\n📋 Cleanup Plan:")
            for i, action in enumerate(cleanup_actions, 1):
                logger.info(f"   {i}. {action}")
            
            # Ask for confirmation (auto-proceed in analysis mode)
            logger.info(f"\n⚠️ This would make changes to the database!")
            logger.info(f"\n📋 Analysis complete - run with --execute flag to perform cleanup")
            
            # Skip NULL telegram_user_id users (these are test/import data)
            if users_to_delete:
                filtered_deletes = []
                for user_id in users_to_delete:
                    # Find the user data
                    user_data = None
                    for telegram_id, users in duplicates.items():
                        for user in users:
                            if user['id'] == user_id:
                                user_data = user
                                break
                    
                    if user_data and user_data.get('telegram_user_id') is None:
                        logger.info(f"   ⚠️ Skipping NULL telegram_user_id user: {user_data['first_name']} ({user_id[:8]}...)")
                    else:
                        filtered_deletes.append(user_id)
                
                logger.info(f"   📊 Would delete {len(users_to_delete)} total, {len(filtered_deletes)} after filtering NULL telegram_user_ids")
                
            # For now, only clean up the @telegram.user emails as they're safe
            if telegram_user_emails and len(sys.argv) > 1 and sys.argv[1] == '--execute':
                logger.info("\n🧹 Executing safe cleanup (placeholder emails only)...")
                execute_safe_cleanup(supabase, telegram_user_emails)
            elif len(sys.argv) > 1 and sys.argv[1] == '--execute':
                logger.info("❌ Execution requested but only email cleanup is safe - other duplicates need manual review")
        else:
            logger.info("✅ No cleanup needed - database looks clean!")
            
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        return False

def execute_safe_cleanup(supabase, telegram_user_emails):
    """Execute safe cleanup operations (placeholder emails only)"""
    logger.info("🧹 Starting safe cleanup operations...")
    
    cleaned_count = 0
    errors = []
    
    try:
        # Clean up @telegram.user placeholder emails
        for user in telegram_user_emails:
            try:
                supabase.table("users").update({
                    "email": None
                }).eq("id", user["id"]).execute()
                cleaned_count += 1
                logger.info(f"✅ Cleaned placeholder email for user {user['first_name']} ({user['id'][:8]}...)")
            except Exception as e:
                error_msg = f"Failed to clean email for user {user['id']}: {e}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"\n✅ Safe cleanup completed!")
        logger.info(f"   📧 Emails cleaned: {cleaned_count}")
        logger.info(f"   ❌ Errors: {len(errors)}")
        
        if errors:
            logger.info(f"\n❌ Errors encountered:")
            for error in errors:
                logger.info(f"   - {error}")
                
    except Exception as e:
        logger.error(f"❌ Error during safe cleanup execution: {e}")

def execute_cleanup(supabase, emergency_email_users, telegram_user_emails, users_to_delete):
    """Execute the cleanup operations"""
    logger.info("🧹 Starting cleanup operations...")
    
    cleanup_results = {
        "emails_cleaned": 0,
        "users_deleted": 0,
        "errors": []
    }
    
    try:
        # 1. Clean up placeholder emails
        all_placeholder_users = emergency_email_users + telegram_user_emails
        for user in all_placeholder_users:
            try:
                supabase.table("users").update({
                    "email": None
                }).eq("id", user["id"]).execute()
                cleanup_results["emails_cleaned"] += 1
                logger.debug(f"✅ Cleaned email for user {user['id'][:8]}...")
            except Exception as e:
                error_msg = f"Failed to clean email for user {user['id']}: {e}"
                cleanup_results["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"📧 Cleaned {cleanup_results['emails_cleaned']} placeholder emails")
        
        # 2. Delete duplicate users
        for user_id in users_to_delete:
            try:
                # First, check if this user has any commitments or other data
                commitments = supabase.table("commitments").select("id").eq("user_id", user_id).execute()
                if commitments.data:
                    # Move commitments to the keeper user if needed
                    logger.warning(f"⚠️ User {user_id[:8]}... has {len(commitments.data)} commitments - skipping deletion")
                    continue
                
                # Safe to delete
                supabase.table("users").delete().eq("id", user_id).execute()
                cleanup_results["users_deleted"] += 1
                logger.debug(f"✅ Deleted duplicate user {user_id[:8]}...")
                
            except Exception as e:
                error_msg = f"Failed to delete user {user_id}: {e}"
                cleanup_results["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"🗑️ Deleted {cleanup_results['users_deleted']} duplicate users")
        
        # 3. Summary
        logger.info(f"\n✅ Cleanup completed!")
        logger.info(f"   📧 Emails cleaned: {cleanup_results['emails_cleaned']}")
        logger.info(f"   🗑️ Users deleted: {cleanup_results['users_deleted']}")
        logger.info(f"   ❌ Errors: {len(cleanup_results['errors'])}")
        
        if cleanup_results["errors"]:
            logger.info(f"\n❌ Errors encountered:")
            for error in cleanup_results["errors"]:
                logger.info(f"   - {error}")
        
        # Final verification
        logger.info(f"\n🔍 Running final verification...")
        final_check = supabase.table("users").select("telegram_user_id").execute()
        user_counts = {}
        for user in final_check.data:
            tid = user['telegram_user_id']
            user_counts[tid] = user_counts.get(tid, 0) + 1
        
        remaining_duplicates = {k: v for k, v in user_counts.items() if v > 1}
        
        if remaining_duplicates:
            logger.warning(f"⚠️ Still have {len(remaining_duplicates)} duplicate telegram_user_ids")
        else:
            logger.info(f"✅ All duplicates resolved!")
            
    except Exception as e:
        logger.error(f"❌ Error during cleanup execution: {e}")

if __name__ == "__main__":
    cleanup_duplicate_users()