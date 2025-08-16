#!/usr/bin/env python3
"""
User Assignment Script for The Progress Method Pods
Assigns users to pods and sets up role management
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pod assignment strategy
PODS_TO_ASSIGN = [
    "Morning Momentum",
    "Evening Excellence", 
    "Midweek Warriors",
    "Weekend Builders",
    "Fitness Focus Pod",
    "Creative Collective",
    "Entrepreneur Alliance"
]

async def get_available_users():
    """Get users available for pod assignment (excluding test users and admin)"""
    logger.info("🔍 Getting available users...")
    
    users = supabase.table("users").select("*").order("created_at", desc=True).execute()
    
    # Filter out test users and keep real users
    real_users = []
    for user in users.data:
        username = user.get("username", "")
        first_name = user.get("first_name", "")
        telegram_id = user.get("telegram_user_id")
        
        # Skip test users and admin (me)
        if (
            username and "test" in username.lower() or
            first_name and "test" in first_name.lower() or
            telegram_id in [777777778, 999888776, 999888774, 999888777, 22222222, 44444444, 11111111] or
            telegram_id == 865415132  # Admin (Thomas)
        ):
            logger.info(f"⏭️ Skipping test/admin user: {first_name} (@{username})")
            continue
            
        real_users.append(user)
        logger.info(f"✅ Available for assignment: {first_name} (@{username}) - TG:{telegram_id}")
    
    return real_users

async def get_pods():
    """Get the 7 pods we created"""
    logger.info("🎯 Getting created pods...")
    
    pods = supabase.table("pods").select("*").in_("name", PODS_TO_ASSIGN).execute()
    
    logger.info(f"Found {len(pods.data)} pods for assignment:")
    for pod in pods.data:
        logger.info(f"  - {pod['name']} (ID: {pod['id']})")
    
    return pods.data

async def check_existing_memberships():
    """Check if any users are already assigned to pods"""
    logger.info("🔍 Checking existing pod memberships...")
    
    memberships = supabase.table("pod_memberships").select("*").eq("is_active", True).execute()
    
    if memberships.data:
        logger.info(f"Found {len(memberships.data)} existing memberships:")
        for membership in memberships.data:
            logger.info(f"  - User {membership['user_id']} in Pod {membership['pod_id']}")
    else:
        logger.info("No existing pod memberships found")
    
    return memberships.data

async def assign_users_to_pods():
    """Smart assignment of users to pods"""
    logger.info("🚀 Starting user assignment to pods...")
    
    # Get available users and pods
    users = await get_available_users()
    pods = await get_pods()
    existing_memberships = await check_existing_memberships()
    
    if not users:
        logger.warning("⚠️ No users available for assignment")
        return
    
    if not pods:
        logger.error("❌ No pods found for assignment")
        return
    
    logger.info(f"📊 Assignment Strategy: {len(users)} users → {len(pods)} pods")
    
    # Assign users round-robin style to pods
    assignments = []
    pod_index = 0
    
    for user in users:
        pod = pods[pod_index % len(pods)]
        
        assignment = {
            "user_id": user["id"],
            "pod_id": pod["id"],
            "is_active": True,
            "joined_at": datetime.now().isoformat()
        }
        
        assignments.append(assignment)
        logger.info(f"📝 {user['first_name']} → {pod['name']}")
        
        pod_index += 1
    
    # Insert assignments
    if assignments:
        logger.info(f"💾 Creating {len(assignments)} pod memberships...")
        
        try:
            result = supabase.table("pod_memberships").insert(assignments).execute()
            logger.info(f"✅ Successfully created {len(result.data)} pod memberships")
            
            # Show final assignment summary
            logger.info("📋 Final Pod Assignments:")
            pod_counts = {}
            for assignment in assignments:
                pod_name = next(p["name"] for p in pods if p["id"] == assignment["pod_id"])
                user_name = next(u["first_name"] for u in users if u["id"] == assignment["user_id"])
                
                if pod_name not in pod_counts:
                    pod_counts[pod_name] = []
                pod_counts[pod_name].append(user_name)
            
            for pod_name, members in pod_counts.items():
                logger.info(f"  🎯 {pod_name}: {', '.join(members)} ({len(members)} members)")
                
        except Exception as e:
            logger.error(f"❌ Error creating memberships: {e}")
            return False
    
    return True

async def grant_pod_member_roles():
    """Grant pod_member role to users who are now in pods"""
    logger.info("👑 Granting pod_member roles...")
    
    # Get all users who are now pod members
    memberships = supabase.table("pod_memberships").select("user_id").eq("is_active", True).execute()
    
    if not memberships.data:
        logger.warning("⚠️ No pod memberships found")
        return
    
    user_ids = [m["user_id"] for m in memberships.data]
    unique_user_ids = list(set(user_ids))
    
    logger.info(f"🎯 Granting pod_member role to {len(unique_user_ids)} users...")
    
    role_grants = []
    for user_id in unique_user_ids:
        # Check if user already has pod_member role
        existing_role = supabase.table("user_roles").select("id").eq("user_id", user_id).eq("role_type", "pod_member").eq("is_active", True).execute()
        
        if existing_role.data:
            logger.info(f"⏭️ User {user_id} already has pod_member role")
            continue
        
        role_grant = {
            "user_id": user_id,
            "role_type": "pod_member",
            "is_active": True,
            "granted_at": datetime.now().isoformat(),
            "granted_by": "assignment_script"
        }
        
        role_grants.append(role_grant)
    
    if role_grants:
        try:
            result = supabase.table("user_roles").insert(role_grants).execute()
            logger.info(f"✅ Successfully granted pod_member role to {len(result.data)} users")
        except Exception as e:
            logger.error(f"❌ Error granting roles: {e}")
            return False
    else:
        logger.info("ℹ️ All users already have appropriate roles")
    
    return True

async def show_final_summary():
    """Show final summary of assignments and roles"""
    logger.info("📊 FINAL ASSIGNMENT SUMMARY")
    logger.info("=" * 50)
    
    # Get pods with member counts
    pods = supabase.table("pods").select("*").in_("name", PODS_TO_ASSIGN).execute()
    
    for pod in pods.data:
        # Get members for this pod
        memberships = supabase.table("pod_memberships").select("user_id").eq("pod_id", pod["id"]).eq("is_active", True).execute()
        
        if memberships.data:
            # Get user details
            user_ids = [m["user_id"] for m in memberships.data]
            users = supabase.table("users").select("first_name, username").in_("id", user_ids).execute()
            
            member_names = [f"{u['first_name']} (@{u.get('username', 'no-username')})" for u in users.data]
            
            logger.info(f"🎯 {pod['name']}: {len(member_names)} members")
            for name in member_names:
                logger.info(f"    - {name}")
        else:
            logger.info(f"🎯 {pod['name']}: 0 members")
    
    # Get role summary
    roles = supabase.table("user_roles").select("role_type", count="exact").eq("is_active", True).execute()
    logger.info(f"\n👑 Active Roles: {roles.count}")
    
    role_counts = {}
    role_data = supabase.table("user_roles").select("role_type").eq("is_active", True).execute()
    for role in role_data.data:
        role_type = role["role_type"]
        role_counts[role_type] = role_counts.get(role_type, 0) + 1
    
    for role_type, count in role_counts.items():
        logger.info(f"    - {role_type}: {count}")

async def main():
    """Main assignment workflow"""
    logger.info("🚀 Starting Pod Assignment Workflow")
    logger.info("=" * 50)
    
    try:
        # Step 1: Check current state
        await check_existing_memberships()
        
        # Step 2: Assign users to pods
        success = await assign_users_to_pods()
        if not success:
            logger.error("❌ User assignment failed")
            return
        
        # Step 3: Grant pod_member roles
        await grant_pod_member_roles()
        
        # Step 4: Show final summary
        await show_final_summary()
        
        logger.info("🎉 Pod assignment workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Assignment workflow failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())