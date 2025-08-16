#!/usr/bin/env python3
"""
Create Demo Environment for Enhanced Nurture System
Sets up test pod with demo users for live presentation
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoEnvironmentSetup:
    """Setup demo environment for enhanced nurture system presentation"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Demo configuration
        self.demo_pod_name = "Demo Pod - Enhanced Nurture System"
        self.demo_users = [
            {"first_name": "Alice", "role": "high_engager"},
            {"first_name": "Bob", "role": "moderate_engager"}, 
            {"first_name": "Carol", "role": "low_engager"},
            {"first_name": "David", "role": "new_member"}
        ]
        
        self.created_resources = {
            "pod_id": None,
            "user_ids": [],
            "sequences": [],
            "deliveries": []
        }
        
        logger.info("🎬 Demo Environment Setup initialized")
    
    async def create_demo_pod(self) -> str:
        """Create demo pod for presentation"""
        try:
            # Check if demo pod already exists
            existing_pod = self.supabase.table("pods").select("*").eq("name", self.demo_pod_name).execute()
            
            if existing_pod.data:
                pod_id = existing_pod.data[0]["id"]
                logger.info(f"📦 Using existing demo pod: {pod_id}")
            else:
                # Create new demo pod
                pod_data = {
                    "name": self.demo_pod_name,
                    "day_of_week": 2,  # Tuesday
                    "time_utc": "19:00:00",  # 7 PM UTC
                    "status": "active"
                }
                
                result = self.supabase.table("pods").insert(pod_data).execute()
                pod_id = result.data[0]["id"]
                logger.info(f"✅ Created demo pod: {pod_id}")
            
            self.created_resources["pod_id"] = pod_id
            return pod_id
            
        except Exception as e:
            logger.error(f"❌ Error creating demo pod: {e}")
            raise
    
    async def create_demo_users(self, pod_id: str) -> List[str]:
        """Create demo users with different engagement profiles"""
        try:
            created_user_ids = []
            
            for user_info in self.demo_users:
                # Generate unique telegram ID for demo
                telegram_id = int(f"99{datetime.now().strftime('%m%d%H%M%S')}{len(created_user_ids)}")
                
                # Create user
                user_data = {
                    "id": str(uuid.uuid4()),
                    "telegram_user_id": telegram_id,
                    "first_name": user_info["first_name"],
                    "last_name": "Demo",
                    "username": f"demo_{user_info['first_name'].lower()}",
                    "email": f"{user_info['first_name'].lower()}.demo@progressmethod.com",
                    "created_at": datetime.now().isoformat()
                }
                
                # Check if user exists
                existing_user = self.supabase.table("users").select("*").eq("telegram_user_id", telegram_id).execute()
                
                if not existing_user.data:
                    result = self.supabase.table("users").insert(user_data).execute()
                    user_id = result.data[0]["id"]
                    logger.info(f"✅ Created demo user: {user_info['first_name']} ({user_id})")
                else:
                    user_id = existing_user.data[0]["id"]
                    logger.info(f"📦 Using existing demo user: {user_info['first_name']} ({user_id})")
                
                created_user_ids.append(user_id)
                
                # Add to pod
                membership_data = {
                    "pod_id": pod_id,
                    "user_id": user_id,
                    "is_active": True,
                    "joined_at": datetime.now().isoformat()
                }
                
                # Check if membership exists
                existing_membership = self.supabase.table("pod_memberships").select("*").eq("pod_id", pod_id).eq("user_id", user_id).execute()
                
                if not existing_membership.data:
                    self.supabase.table("pod_memberships").insert(membership_data).execute()
                    logger.info(f"✅ Added {user_info['first_name']} to demo pod")
                
                # Create communication preferences
                comm_prefs = {
                    "user_id": user_id,
                    "telegram_user_id": telegram_id,
                    "communication_style": "balanced",
                    "enabled_message_types": ["week_launch", "meeting_prep", "post_meeting", "reflection"],
                    "is_active": True
                }
                
                try:
                    self.supabase.table("communication_preferences").upsert(comm_prefs).execute()
                    logger.info(f"✅ Set communication preferences for {user_info['first_name']}")
                except:
                    pass  # May already exist
            
            self.created_resources["user_ids"] = created_user_ids
            return created_user_ids
            
        except Exception as e:
            logger.error(f"❌ Error creating demo users: {e}")
            raise
    
    async def create_demo_sequences(self, pod_id: str, user_ids: List[str]) -> List[str]:
        """Create demo nurture sequences with different states"""
        try:
            from nurture_sequences import SequenceType
            
            sequence_ids = []
            
            # Create sequences for each demo user with different progress
            sequence_configs = [
                {"user_idx": 0, "type": SequenceType.ONBOARDING, "step": 3, "status": "active"},
                {"user_idx": 1, "type": SequenceType.COMMITMENT_FOLLOWUP, "step": 1, "status": "active"},
                {"user_idx": 2, "type": SequenceType.RE_ENGAGEMENT, "step": 0, "status": "pending"},
                {"user_idx": 3, "type": SequenceType.POD_JOURNEY, "step": 2, "status": "active"}
            ]
            
            for config in sequence_configs:
                if config["user_idx"] < len(user_ids):
                    user_id = user_ids[config["user_idx"]]
                    
                    sequence_data = {
                        "user_id": user_id,
                        "sequence_type": config["type"].value,
                        "current_step": config["step"],
                        "is_active": config["status"] == "active",
                        "started_at": (datetime.now() - timedelta(days=config["step"])).isoformat(),
                        "last_message_at": (datetime.now() - timedelta(hours=6)).isoformat() if config["step"] > 0 else None,
                        "next_message_at": (datetime.now() + timedelta(hours=2)).isoformat() if config["status"] == "active" else None,
                        "engagement_score": 75.0,
                        "sequence_data": {"pod_id": pod_id, "demo": True}
                    }
                    
                    # Check if sequence exists
                    existing_seq = self.supabase.table("user_sequence_state").select("*").eq("user_id", user_id).eq("sequence_type", config["type"].value).execute()
                    
                    if not existing_seq.data:
                        result = self.supabase.table("user_sequence_state").insert(sequence_data).execute()
                        sequence_id = result.data[0]["id"]
                        sequence_ids.append(sequence_id)
                        logger.info(f"✅ Created {config['type'].value} sequence for user {config['user_idx']}")
                    else:
                        sequence_ids.append(existing_seq.data[0]["id"])
                        logger.info(f"📦 Using existing sequence for user {config['user_idx']}")
            
            self.created_resources["sequences"] = sequence_ids
            return sequence_ids
            
        except Exception as e:
            logger.error(f"❌ Error creating demo sequences: {e}")
            return []
    
    async def create_demo_analytics_data(self, pod_id: str, user_ids: List[str]) -> bool:
        """Create demo analytics and engagement data"""
        try:
            # Create message analytics
            analytics_data = []
            
            for i, user_id in enumerate(user_ids):
                # Create historical message data
                for days_back in range(1, 8):  # Last 7 days
                    date = datetime.now() - timedelta(days=days_back)
                    
                    # Simulate different engagement patterns
                    engagement_rates = [0.9, 0.7, 0.4, 0.8]  # High, moderate, low, new
                    base_engagement = engagement_rates[i % len(engagement_rates)]
                    
                    # Add some variance
                    daily_engagement = max(0.1, min(1.0, base_engagement + (0.1 * (days_back % 3 - 1))))
                    
                    analytics_entry = {
                        "user_id": user_id,
                        "message_date": date.date().isoformat(),
                        "messages_sent": 2,
                        "messages_opened": int(2 * daily_engagement),
                        "messages_responded": int(1 * daily_engagement),
                        "engagement_score": daily_engagement,
                        "sequence_type": ["onboarding", "commitment_followup", "re_engagement", "pod_journey"][i],
                        "created_at": date.isoformat()
                    }
                    
                    analytics_data.append(analytics_entry)
            
            # Batch insert analytics
            if analytics_data:
                try:
                    self.supabase.table("message_analytics").insert(analytics_data).execute()
                    logger.info(f"✅ Created {len(analytics_data)} analytics records")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create analytics data: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating demo analytics: {e}")
            return False
    
    async def create_demo_deliveries(self, user_ids: List[str]) -> List[str]:
        """Create demo message deliveries for testing"""
        try:
            delivery_ids = []
            
            # Only create if message_deliveries table exists
            try:
                # Test if table exists
                self.supabase.table("message_deliveries").select("*").limit(1).execute()
                table_exists = True
            except:
                table_exists = False
                logger.info("ℹ️ message_deliveries table not available, skipping demo deliveries")
            
            if table_exists:
                for i, user_id in enumerate(user_ids):
                    delivery_data = {
                        "user_id": user_id,
                        "sequence_type": ["onboarding", "commitment_followup", "re_engagement", "pod_journey"][i],
                        "message_step": i,
                        "channel": "telegram",
                        "delivery_status": ["delivered", "sent", "pending", "scheduled"][i],
                        "recipient_address": f"demo_user_{i}",
                        "message_content": f"Demo message for {user_id}",
                        "scheduled_at": (datetime.now() + timedelta(minutes=30 * i)).isoformat(),
                        "sent_at": datetime.now().isoformat() if i < 2 else None,
                        "tracking_id": str(uuid.uuid4()),
                        "attempt_count": 1,
                        "max_attempts": 3
                    }
                    
                    result = self.supabase.table("message_deliveries").insert(delivery_data).execute()
                    delivery_ids.append(result.data[0]["id"])
                    logger.info(f"✅ Created demo delivery for user {i}")
            
            self.created_resources["deliveries"] = delivery_ids
            return delivery_ids
            
        except Exception as e:
            logger.error(f"❌ Error creating demo deliveries: {e}")
            return []
    
    async def setup_complete_demo(self) -> Dict[str, Any]:
        """Set up complete demo environment"""
        try:
            logger.info("🎬 Setting up complete demo environment...")
            
            # Step 1: Create demo pod
            pod_id = await self.create_demo_pod()
            
            # Step 2: Create demo users
            user_ids = await self.create_demo_users(pod_id)
            
            # Step 3: Create demo sequences
            sequence_ids = await self.create_demo_sequences(pod_id, user_ids)
            
            # Step 4: Create demo analytics
            analytics_created = await self.create_demo_analytics_data(pod_id, user_ids)
            
            # Step 5: Create demo deliveries
            delivery_ids = await self.create_demo_deliveries(user_ids)
            
            # Summary
            demo_summary = {
                "pod_id": pod_id,
                "pod_name": self.demo_pod_name,
                "users_created": len(user_ids),
                "sequences_created": len(sequence_ids),
                "analytics_created": analytics_created,
                "deliveries_created": len(delivery_ids),
                "demo_urls": {
                    "admin_dashboard": "http://localhost:8001/admin/dashboard",
                    "enhanced_admin": "http://localhost:8001/admin/enhanced-dashboard",
                    "api_health": "http://localhost:8001/"
                },
                "resources": self.created_resources,
                "setup_completed": datetime.now().isoformat()
            }
            
            logger.info("🎉 Demo environment setup complete!")
            logger.info(f"📦 Pod ID: {pod_id}")
            logger.info(f"👥 Users: {len(user_ids)}")
            logger.info(f"🎯 Sequences: {len(sequence_ids)}")
            logger.info(f"📊 Analytics: {'✅' if analytics_created else '❌'}")
            logger.info(f"📨 Deliveries: {len(delivery_ids)}")
            
            return demo_summary
            
        except Exception as e:
            logger.error(f"❌ Error setting up demo environment: {e}")
            raise
    
    async def cleanup_demo(self) -> bool:
        """Clean up demo environment"""
        try:
            logger.info("🧹 Cleaning up demo environment...")
            
            # Clean up in reverse order
            resources = self.created_resources
            
            # Clean up deliveries
            if resources.get("deliveries"):
                try:
                    for delivery_id in resources["deliveries"]:
                        self.supabase.table("message_deliveries").delete().eq("id", delivery_id).execute()
                    logger.info(f"✅ Cleaned up {len(resources['deliveries'])} deliveries")
                except:
                    pass
            
            # Clean up sequences
            if resources.get("sequences"):
                for sequence_id in resources["sequences"]:
                    try:
                        self.supabase.table("user_sequence_state").delete().eq("id", sequence_id).execute()
                    except:
                        pass
                logger.info(f"✅ Cleaned up {len(resources['sequences'])} sequences")
            
            # Clean up users (optional - may want to keep for further demos)
            if resources.get("user_ids"):
                for user_id in resources["user_ids"]:
                    try:
                        # Remove from pod
                        self.supabase.table("pod_memberships").delete().eq("user_id", user_id).execute()
                        # Remove communication preferences
                        self.supabase.table("communication_preferences").delete().eq("user_id", user_id).execute()
                        # Remove analytics
                        self.supabase.table("message_analytics").delete().eq("user_id", user_id).execute()
                        # Remove user (optional)
                        # self.supabase.table("users").delete().eq("id", user_id).execute()
                    except:
                        pass
                logger.info(f"✅ Cleaned up {len(resources['user_ids'])} user associations")
            
            # Clean up pod (optional)
            # if resources.get("pod_id"):
            #     self.supabase.table("pods").delete().eq("id", resources["pod_id"]).execute()
            #     logger.info("✅ Cleaned up demo pod")
            
            logger.info("🎉 Demo cleanup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up demo: {e}")
            return False

async def main():
    """Main demo setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo Environment Setup")
    parser.add_argument('--setup', action='store_true', help='Set up demo environment')
    parser.add_argument('--cleanup', action='store_true', help='Clean up demo environment')
    parser.add_argument('--status', action='store_true', help='Show demo status')
    
    args = parser.parse_args()
    
    try:
        demo = DemoEnvironmentSetup()
        
        if args.setup:
            summary = await demo.setup_complete_demo()
            print("\n🎬 DEMO ENVIRONMENT READY")
            print("=" * 40)
            print(f"Pod Name: {summary['pod_name']}")
            print(f"Pod ID: {summary['pod_id']}")
            print(f"Users Created: {summary['users_created']}")
            print(f"Sequences Active: {summary['sequences_created']}")
            print(f"Analytics Data: {'✅ Available' if summary['analytics_created'] else '❌ Limited'}")
            print(f"Message Deliveries: {summary['deliveries_created']}")
            print("\n🎯 Demo URLs:")
            for name, url in summary['demo_urls'].items():
                print(f"  {name}: {url}")
            print("\n✅ Ready for live demonstration!")
            
        elif args.cleanup:
            success = await demo.cleanup_demo()
            if success:
                print("✅ Demo environment cleaned up successfully")
            else:
                print("❌ Error during cleanup")
                
        elif args.status:
            # Check current demo status
            existing_pod = demo.supabase.table("pods").select("*").eq("name", demo.demo_pod_name).execute()
            if existing_pod.data:
                pod_id = existing_pod.data[0]["id"]
                
                # Count members
                members = demo.supabase.table("pod_memberships").select("*").eq("pod_id", pod_id).eq("is_active", True).execute()
                member_count = len(members.data)
                
                # Count sequences
                sequences = demo.supabase.table("user_sequence_state").select("*").eq("is_active", True).execute()
                sequence_count = len([s for s in sequences.data if any(m["user_id"] == s["user_id"] for m in members.data)])
                
                print("\n📊 DEMO ENVIRONMENT STATUS")
                print("=" * 40)
                print(f"Demo Pod: {'✅ EXISTS' if existing_pod.data else '❌ NOT FOUND'}")
                print(f"Pod ID: {pod_id}")
                print(f"Active Members: {member_count}")
                print(f"Active Sequences: {sequence_count}")
                print(f"Status: {'🎬 READY' if member_count > 0 else '⚠️ NEEDS SETUP'}")
            else:
                print("❌ Demo environment not found. Run --setup to create it.")
        
        else:
            print("Demo Environment Manager")
            print("Usage:")
            print("  --setup    Create demo environment")
            print("  --cleanup  Remove demo environment")
            print("  --status   Check demo status")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Demo setup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)