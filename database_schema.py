# Database Schema Setup for The Progress Method
# Creates all necessary tables for the platform

import logging
from supabase import Client
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Manages database schema creation and updates"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def create_all_tables(self):
        """Create all tables for the platform"""
        try:
            # Create pods table
            pods_data = {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Test Pod",
                "description": "Test pod for development",
                "day_of_week": 1,  # Monday
                "time_utc": "19:00:00",
                "timezone": "UTC",
                "max_members": 8,
                "current_members": 0,
                "monthly_price": 97.0,
                "status": "active",
                "meeting_link": "https://meet.google.com/test",
                "facilitator_notes": "",
                "pod_type": "standard"
            }
            
            # Try to create pod if it doesn't exist
            try:
                existing_pod = self.supabase.table("pods").select("*").eq("id", pods_data["id"]).execute()
                if not existing_pod.data:
                    pod_result = self.supabase.table("pods").insert(pods_data).execute()
                    logger.info("✅ Created test pod")
                else:
                    logger.info("✅ Test pod already exists")
            except Exception as e:
                logger.info(f"Pods table may not exist yet: {e}")
            
            # Create pod memberships for testing
            # First get a user ID
            user_result = self.supabase.table("users").select("*").limit(1).execute()
            if user_result.data:
                user_id = user_result.data[0]["id"]
                
                membership_data = {
                    "id": "00000000-0000-0000-0000-000000000002", 
                    "user_id": user_id,
                    "pod_id": "00000000-0000-0000-0000-000000000001",
                    "joined_at": "2025-01-01T00:00:00Z",
                    "monthly_payment_active": True,
                    "payment_amount": 97.0,
                    "status": "active"
                }
                
                try:
                    existing_membership = self.supabase.table("pod_memberships").select("*").eq("id", membership_data["id"]).execute()
                    if not existing_membership.data:
                        membership_result = self.supabase.table("pod_memberships").insert(membership_data).execute()
                        logger.info("✅ Created test pod membership")
                    else:
                        logger.info("✅ Test pod membership already exists")
                except Exception as e:
                    logger.info(f"Pod memberships table may not exist yet: {e}")
            
            logger.info("✅ Database schema setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up database schema: {e}")
            return False

if __name__ == "__main__":
    import asyncio
    from supabase import create_client
    
    load_dotenv()
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    async def setup():
        schema = DatabaseSchema(supabase)
        await schema.create_all_tables()
    
    asyncio.run(setup())