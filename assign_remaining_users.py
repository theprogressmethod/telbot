#!/usr/bin/env python3
"""
Assign remaining unassigned users to pods
Only assigns users who don't already have pod memberships
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

async def get_unassigned_users():
    """Get users who are not currently assigned to any pod"""
    logger.info("🔍 Getting users not assigned to pods...")
    
    # Get all users
    users = supabase.table("users").select("*").order("created_at", desc=True).execute()
    
    # Get users who already have pod memberships
    memberships = supabase.table("pod_memberships").select("user_id").eq("is_active", True).execute()
    assigned_user_ids = set(m["user_id"] for m in memberships.data)
    
    # Filter out test users and assigned users
    unassigned_users = []
    for user in users.data:
        username = user.get("username", "")
        first_name = user.get("first_name", "")
        telegram_id = user.get("telegram_user_id")
        user_id = user.get("id")
        
        # Skip test users and admin (me)
        if (
            username and "test" in username.lower() or
            first_name and "test" in first_name.lower() or
            telegram_id in [777777778, 999888776, 999888774, 999888777, 22222222, 44444444, 11111111] or
            telegram_id == 865415132  # Admin (Thomas)
        ):
            logger.info(f"⏭️ Skipping test/admin user: {first_name} (@{username})")
            continue
            
        # Skip already assigned users
        if user_id in assigned_user_ids:
            logger.info(f"⏭️ Already assigned: {first_name} (@{username}) - TG:{telegram_id}")
            continue
            
        unassigned_users.append(user)
        logger.info(f"✅ Available for assignment: {first_name} (@{username}) - TG:{telegram_id}")
    
    return unassigned_users

async def get_pod_member_counts():
    """Get current member count for each pod"""
    logger.info("📊 Getting current pod member counts...")
    
    pods = supabase.table("pods").select("*").in_("name", PODS_TO_ASSIGN).execute()
    
    pod_counts = {}
    for pod in pods.data:
        # Count members in this pod
        memberships = supabase.table("pod_memberships").select("user_id", count="exact").eq("pod_id", pod["id"]).eq("is_active", True).execute()
        member_count = memberships.count if memberships.count else 0
        
        pod_counts[pod["id"]] = {
            "name": pod["name"],
            "member_count": member_count,
            "pod_data": pod
        }
        logger.info(f"  🎯 {pod['name']}: {member_count} members")
    
    return pod_counts

async def assign_unassigned_users():
    """Assign unassigned users to pods with smallest member counts"""
    logger.info("🚀 Starting assignment of unassigned users...")
    
    # Get unassigned users and pod counts
    users = await get_unassigned_users()
    pod_counts = await get_pod_member_counts()
    
    if not users:
        logger.info("✅ All users are already assigned to pods!")
        return True
    
    if not pod_counts:
        logger.error("❌ No pods found for assignment")
        return False
    
    logger.info(f"📊 Assignment Strategy: {len(users)} unassigned users → {len(pod_counts)} pods")
    
    # Sort pods by member count (assign to least populated first)
    sorted_pods = sorted(pod_counts.items(), key=lambda x: x[1]["member_count"])
    
    assignments = []
    pod_index = 0
    
    for user in users:
        # Get the pod with the least members (round-robin through least populated)
        pod_id, pod_info = sorted_pods[pod_index % len(sorted_pods)]
        
        assignment = {
            "user_id": user["id"],
            "pod_id": pod_id,
            "is_active": True,
            "joined_at": datetime.now().isoformat()
        }
        
        assignments.append(assignment)
        logger.info(f"📝 {user['first_name']} → {pod_info['name']} (currently {pod_info['member_count']} members)")
        
        # Update the member count for balancing
        pod_counts[pod_id]["member_count"] += 1
        sorted_pods = sorted(pod_counts.items(), key=lambda x: x[1]["member_count"])
        
        pod_index += 1
    
    # Insert assignments
    if assignments:
        logger.info(f"💾 Creating {len(assignments)} new pod memberships...")
        
        try:
            result = supabase.table("pod_memberships").insert(assignments).execute()
            logger.info(f"✅ Successfully created {len(result.data)} pod memberships")
            
            # Show final assignment summary
            logger.info("📋 New Assignments:")
            for assignment in assignments:
                pod_name = pod_counts[assignment["pod_id"]]["name"]
                user_name = next(u["first_name"] for u in users if u["id"] == assignment["user_id"])
                logger.info(f"  ✅ {user_name} → {pod_name}")
                
        except Exception as e:
            logger.error(f"❌ Error creating memberships: {e}")
            return False
    
    return True

async def grant_pod_member_roles():
    """Grant pod_member role to newly assigned users"""
    logger.info("👑 Granting pod_member roles to newly assigned users...")
    
    # Get all users who are now pod members
    memberships = supabase.table("pod_memberships").select("user_id").eq("is_active", True).execute()
    
    if not memberships.data:
        logger.warning("⚠️ No pod memberships found")
        return
    
    user_ids = [m["user_id"] for m in memberships.data]
    unique_user_ids = list(set(user_ids))
    
    logger.info(f"🎯 Checking pod_member roles for {len(unique_user_ids)} users...")
    
    role_grants = []
    for user_id in unique_user_ids:
        # Check if user already has pod_member role
        existing_role = supabase.table("user_roles").select("id").eq("user_id", user_id).eq("role_type", "pod_member").eq("is_active", True).execute()
        
        if existing_role.data:
            continue  # User already has the role
        
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
            logger.info(f"✅ Successfully granted pod_member role to {len(result.data)} new users")
        except Exception as e:
            logger.error(f"❌ Error granting roles: {e}")
            return False
    else:
        logger.info("ℹ️ All users already have appropriate roles")
    
    return True

async def show_final_summary():
    """Show final summary of all assignments"""
    logger.info("📊 FINAL POD ASSIGNMENT SUMMARY")
    logger.info("=" * 60)
    
    # Get pods with member counts
    pods = supabase.table("pods").select("*").in_("name", PODS_TO_ASSIGN).execute()
    
    total_members = 0
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
            
            total_members += len(member_names)
        else:
            logger.info(f"🎯 {pod['name']}: 0 members")
    
    logger.info(f"\n📈 Total Users in Pods: {total_members}")
    
    # Get role summary
    role_data = supabase.table("user_roles").select("role_type").eq("is_active", True).execute()
    role_counts = {}
    for role in role_data.data:
        role_type = role["role_type"]
        role_counts[role_type] = role_counts.get(role_type, 0) + 1
    
    logger.info(f"\n👑 Active Roles:")
    for role_type, count in role_counts.items():
        logger.info(f"    - {role_type}: {count}")

async def main():
    """Main assignment workflow"""
    logger.info("🚀 Starting Unassigned User Assignment Workflow")
    logger.info("=" * 60)
    
    try:
        # Step 1: Assign unassigned users to pods
        success = await assign_unassigned_users()
        if not success:
            logger.error("❌ User assignment failed")
            return
        
        # Step 2: Grant pod_member roles
        await grant_pod_member_roles()
        
        # Step 3: Show final summary
        await show_final_summary()
        
        logger.info("🎉 Unassigned user assignment workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Assignment workflow failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())