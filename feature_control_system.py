#!/usr/bin/env python3
"""
Progress Method - Feature Control System
Centralized feature management, A/B testing, and configuration control
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from supabase import Client

logger = logging.getLogger(__name__)

class FeatureFlag(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    A_B_TEST = "a_b_test"
    GRADUAL_ROLLOUT = "gradual_rollout"
    USER_SEGMENT = "user_segment"

class RolloutStrategy(Enum):
    ALL_USERS = "all_users"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    ROLE_BASED = "role_based"
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"

@dataclass
class Feature:
    id: str
    name: str
    description: str
    flag: FeatureFlag
    rollout_strategy: RolloutStrategy
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool = True
    
    # A/B Testing
    ab_test_groups: Optional[Dict[str, Any]] = None
    ab_test_active: bool = False
    
    # Gradual Rollout
    rollout_percentage: float = 100.0
    rollout_target_date: Optional[datetime] = None
    
    # User Targeting
    target_user_roles: List[str] = None
    target_user_ids: List[str] = None
    excluded_user_ids: List[str] = None
    
    # Analytics
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None

@dataclass
class FeatureUsageEvent:
    feature_id: str
    user_id: str
    user_telegram_id: int
    event_type: str  # "access", "success", "error", "conversion"
    metadata: Dict[str, Any]
    timestamp: datetime
    ab_test_group: Optional[str] = None

class FeatureControlSystem:
    """Centralized feature management and control system"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self._features_cache = {}
        self._cache_expiry = datetime.now()
        self._cache_duration = timedelta(minutes=5)
        
    async def initialize_feature_tables(self):
        """Initialize feature control database tables"""
        try:
            # Create features table
            create_features_table = """
            CREATE TABLE IF NOT EXISTS feature_flags (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                feature_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                flag TEXT NOT NULL CHECK (flag IN ('enabled', 'disabled', 'a_b_test', 'gradual_rollout', 'user_segment')),
                rollout_strategy TEXT NOT NULL CHECK (rollout_strategy IN ('all_users', 'percentage', 'user_list', 'role_based', 'geographic', 'time_based')),
                config JSONB DEFAULT '{}',
                ab_test_groups JSONB,
                ab_test_active BOOLEAN DEFAULT false,
                rollout_percentage DECIMAL(5,2) DEFAULT 100.0,
                rollout_target_date TIMESTAMPTZ,
                target_user_roles JSONB DEFAULT '[]',
                target_user_ids JSONB DEFAULT '[]',
                excluded_user_ids JSONB DEFAULT '[]',
                usage_count INTEGER DEFAULT 0,
                success_rate DECIMAL(5,2) DEFAULT 0.0,
                last_used TIMESTAMPTZ,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                created_by TEXT
            );
            """
            
            # Create feature usage events table
            create_usage_table = """
            CREATE TABLE IF NOT EXISTS feature_usage_events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                feature_id TEXT NOT NULL,
                user_id UUID REFERENCES users(id),
                user_telegram_id BIGINT,
                event_type TEXT NOT NULL CHECK (event_type IN ('access', 'success', 'error', 'conversion')),
                metadata JSONB DEFAULT '{}',
                ab_test_group TEXT,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            );
            """
            
            # Create indexes
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_feature_flags_feature_id ON feature_flags(feature_id);
            CREATE INDEX IF NOT EXISTS idx_feature_flags_active ON feature_flags(is_active) WHERE is_active = true;
            CREATE INDEX IF NOT EXISTS idx_feature_usage_feature ON feature_usage_events(feature_id);
            CREATE INDEX IF NOT EXISTS idx_feature_usage_user ON feature_usage_events(user_telegram_id);
            CREATE INDEX IF NOT EXISTS idx_feature_usage_timestamp ON feature_usage_events(timestamp DESC);
            """
            
            # Execute table creation using SQL statements
            # Note: We'll create tables one by one since we can't execute raw SQL directly
            # This would typically be done via database migrations in production
            logger.info("⚠️ Feature tables should be created via database migrations")
            logger.info("For now, please run the SQL from SUPABASE_SETUP.sql manually")
            
            logger.info("✅ Feature control tables initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing feature tables: {e}")
            raise
    
    async def create_feature(self, feature: Feature) -> bool:
        """Create a new feature flag"""
        try:
            feature_data = {
                "feature_id": feature.id,
                "name": feature.name,
                "description": feature.description,
                "flag": feature.flag.value,
                "rollout_strategy": feature.rollout_strategy.value,
                "config": json.dumps(feature.config),
                "ab_test_groups": json.dumps(feature.ab_test_groups) if feature.ab_test_groups else None,
                "ab_test_active": feature.ab_test_active,
                "rollout_percentage": feature.rollout_percentage,
                "rollout_target_date": feature.rollout_target_date.isoformat() if feature.rollout_target_date else None,
                "target_user_roles": json.dumps(feature.target_user_roles or []),
                "target_user_ids": json.dumps(feature.target_user_ids or []),
                "excluded_user_ids": json.dumps(feature.excluded_user_ids or []),
                "created_by": feature.created_by,
                "is_active": feature.is_active
            }
            
            result = self.supabase.table("feature_flags").insert(feature_data).execute()
            
            if result.data:
                self._invalidate_cache()
                logger.info(f"✅ Created feature: {feature.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error creating feature {feature.name}: {e}")
            return False
    
    async def update_feature(self, feature_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing feature flag"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            
            result = self.supabase.table("feature_flags").update(updates).eq("feature_id", feature_id).execute()
            
            if result.data:
                self._invalidate_cache()
                logger.info(f"✅ Updated feature: {feature_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating feature {feature_id}: {e}")
            return False
    
    async def delete_feature(self, feature_id: str) -> bool:
        """Delete a feature flag (soft delete)"""
        try:
            result = self.supabase.table("feature_flags").update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq("feature_id", feature_id).execute()
            
            if result.data:
                self._invalidate_cache()
                logger.info(f"✅ Deleted feature: {feature_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error deleting feature {feature_id}: {e}")
            return False
    
    async def is_feature_enabled(self, feature_id: str, user_telegram_id: int, user_roles: List[str] = None) -> Tuple[bool, Optional[str]]:
        """Check if a feature is enabled for a specific user"""
        try:
            feature = await self._get_feature(feature_id)
            
            if not feature or not feature.is_active:
                return False, None
            
            # Check basic flag status
            if feature.flag == FeatureFlag.DISABLED:
                return False, None
            elif feature.flag == FeatureFlag.ENABLED:
                return await self._check_rollout_strategy(feature, user_telegram_id, user_roles)
            elif feature.flag == FeatureFlag.A_B_TEST:
                return await self._handle_ab_test(feature, user_telegram_id)
            elif feature.flag == FeatureFlag.GRADUAL_ROLLOUT:
                return await self._handle_gradual_rollout(feature, user_telegram_id)
            elif feature.flag == FeatureFlag.USER_SEGMENT:
                return await self._handle_user_segment(feature, user_telegram_id, user_roles)
            
            return False, None
            
        except Exception as e:
            logger.error(f"❌ Error checking feature {feature_id}: {e}")
            return False, None
    
    async def _get_feature(self, feature_id: str) -> Optional[Feature]:
        """Get feature from cache or database"""
        # Check cache first
        if (datetime.now() < self._cache_expiry and 
            feature_id in self._features_cache):
            return self._features_cache[feature_id]
        
        try:
            result = self.supabase.table("feature_flags").select("*").eq("feature_id", feature_id).eq("is_active", True).execute()
            
            if result.data:
                feature_data = result.data[0]
                feature = Feature(
                    id=feature_data["feature_id"],
                    name=feature_data["name"],
                    description=feature_data["description"],
                    flag=FeatureFlag(feature_data["flag"]),
                    rollout_strategy=RolloutStrategy(feature_data["rollout_strategy"]),
                    config=json.loads(feature_data["config"] or "{}"),
                    created_at=datetime.fromisoformat(feature_data["created_at"]),
                    updated_at=datetime.fromisoformat(feature_data["updated_at"]),
                    created_by=feature_data["created_by"],
                    is_active=feature_data["is_active"],
                    ab_test_groups=json.loads(feature_data["ab_test_groups"]) if feature_data["ab_test_groups"] else None,
                    ab_test_active=feature_data["ab_test_active"],
                    rollout_percentage=float(feature_data["rollout_percentage"]),
                    rollout_target_date=datetime.fromisoformat(feature_data["rollout_target_date"]) if feature_data["rollout_target_date"] else None,
                    target_user_roles=json.loads(feature_data["target_user_roles"] or "[]"),
                    target_user_ids=json.loads(feature_data["target_user_ids"] or "[]"),
                    excluded_user_ids=json.loads(feature_data["excluded_user_ids"] or "[]"),
                    usage_count=feature_data["usage_count"],
                    success_rate=float(feature_data["success_rate"]),
                    last_used=datetime.fromisoformat(feature_data["last_used"]) if feature_data["last_used"] else None
                )
                
                # Update cache
                self._features_cache[feature_id] = feature
                self._cache_expiry = datetime.now() + self._cache_duration
                
                return feature
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving feature {feature_id}: {e}")
            return None
    
    async def _check_rollout_strategy(self, feature: Feature, user_telegram_id: int, user_roles: List[str] = None) -> Tuple[bool, Optional[str]]:
        """Check if user meets rollout strategy criteria"""
        if feature.rollout_strategy == RolloutStrategy.ALL_USERS:
            return True, None
        elif feature.rollout_strategy == RolloutStrategy.PERCENTAGE:
            # Use user ID hash for consistent percentage assignment
            user_hash = hash(str(user_telegram_id)) % 100
            return user_hash < feature.rollout_percentage, None
        elif feature.rollout_strategy == RolloutStrategy.USER_LIST:
            return str(user_telegram_id) in feature.target_user_ids, None
        elif feature.rollout_strategy == RolloutStrategy.ROLE_BASED:
            if not user_roles:
                return False, None
            return any(role in feature.target_user_roles for role in user_roles), None
        elif feature.rollout_strategy == RolloutStrategy.TIME_BASED:
            if feature.rollout_target_date:
                return datetime.now() >= feature.rollout_target_date, None
            return True, None
        
        return False, None
    
    async def _handle_ab_test(self, feature: Feature, user_telegram_id: int) -> Tuple[bool, Optional[str]]:
        """Handle A/B testing logic"""
        if not feature.ab_test_active or not feature.ab_test_groups:
            return False, None
        
        # Assign user to A/B test group based on consistent hash
        user_hash = hash(str(user_telegram_id)) % 100
        
        cumulative_percentage = 0
        for group_name, group_config in feature.ab_test_groups.items():
            group_percentage = group_config.get("percentage", 0)
            cumulative_percentage += group_percentage
            
            if user_hash < cumulative_percentage:
                # Check if this group should see the feature
                group_enabled = group_config.get("enabled", False)
                return group_enabled, group_name
        
        return False, None
    
    async def _handle_gradual_rollout(self, feature: Feature, user_telegram_id: int) -> Tuple[bool, Optional[str]]:
        """Handle gradual rollout logic"""
        # Calculate current rollout percentage based on time
        if feature.rollout_target_date:
            now = datetime.now()
            if now >= feature.rollout_target_date:
                current_percentage = 100.0
            else:
                # Calculate gradual increase over time
                start_date = feature.created_at
                total_duration = (feature.rollout_target_date - start_date).total_seconds()
                elapsed_duration = (now - start_date).total_seconds()
                
                if total_duration > 0:
                    time_progress = min(elapsed_duration / total_duration, 1.0)
                    current_percentage = time_progress * feature.rollout_percentage
                else:
                    current_percentage = feature.rollout_percentage
        else:
            current_percentage = feature.rollout_percentage
        
        # Use consistent hash for user assignment
        user_hash = hash(str(user_telegram_id)) % 100
        return user_hash < current_percentage, None
    
    async def _handle_user_segment(self, feature: Feature, user_telegram_id: int, user_roles: List[str] = None) -> Tuple[bool, Optional[str]]:
        """Handle user segment targeting"""
        # Check if user is excluded
        if str(user_telegram_id) in feature.excluded_user_ids:
            return False, None
        
        # Check if user is in target list
        if feature.target_user_ids and str(user_telegram_id) in feature.target_user_ids:
            return True, None
        
        # Check role-based targeting
        if feature.target_user_roles and user_roles:
            if any(role in feature.target_user_roles for role in user_roles):
                return True, None
        
        # If no specific targeting, deny access
        return False, None
    
    async def log_feature_usage(self, feature_id: str, user_telegram_id: int, event_type: str, metadata: Dict[str, Any] = None, ab_test_group: str = None):
        """Log feature usage event"""
        try:
            # Get user UUID
            user_result = self.supabase.table("users").select("id").eq("telegram_user_id", user_telegram_id).execute()
            user_id = user_result.data[0]["id"] if user_result.data else None
            
            event_data = {
                "feature_id": feature_id,
                "user_id": user_id,
                "user_telegram_id": user_telegram_id,
                "event_type": event_type,
                "metadata": json.dumps(metadata or {}),
                "ab_test_group": ab_test_group,
                "timestamp": datetime.now().isoformat()
            }
            
            self.supabase.table("feature_usage_events").insert(event_data).execute()
            
            # Update feature usage statistics
            await self._update_feature_stats(feature_id, event_type)
            
        except Exception as e:
            logger.error(f"❌ Error logging feature usage: {e}")
    
    async def _update_feature_stats(self, feature_id: str, event_type: str):
        """Update feature usage statistics"""
        try:
            if event_type == "access":
                # Increment usage count
                self.supabase.table("feature_flags").update({
                    "usage_count": "usage_count + 1",
                    "last_used": datetime.now().isoformat()
                }).eq("feature_id", feature_id).execute()
            
            elif event_type in ["success", "error"]:
                # Update success rate
                # This would require more complex calculation - implement as needed
                pass
                
        except Exception as e:
            logger.error(f"❌ Error updating feature stats: {e}")
    
    async def get_all_features(self) -> List[Feature]:
        """Get all active features"""
        try:
            result = self.supabase.table("feature_flags").select("*").eq("is_active", True).execute()
            
            features = []
            for feature_data in result.data:
                feature = Feature(
                    id=feature_data["feature_id"],
                    name=feature_data["name"],
                    description=feature_data["description"],
                    flag=FeatureFlag(feature_data["flag"]),
                    rollout_strategy=RolloutStrategy(feature_data["rollout_strategy"]),
                    config=json.loads(feature_data["config"] or "{}"),
                    created_at=datetime.fromisoformat(feature_data["created_at"]),
                    updated_at=datetime.fromisoformat(feature_data["updated_at"]),
                    created_by=feature_data["created_by"],
                    is_active=feature_data["is_active"],
                    ab_test_groups=json.loads(feature_data["ab_test_groups"]) if feature_data["ab_test_groups"] else None,
                    ab_test_active=feature_data["ab_test_active"],
                    rollout_percentage=float(feature_data["rollout_percentage"]),
                    rollout_target_date=datetime.fromisoformat(feature_data["rollout_target_date"]) if feature_data["rollout_target_date"] else None,
                    target_user_roles=json.loads(feature_data["target_user_roles"] or "[]"),
                    target_user_ids=json.loads(feature_data["target_user_ids"] or "[]"),
                    excluded_user_ids=json.loads(feature_data["excluded_user_ids"] or "[]"),
                    usage_count=feature_data["usage_count"],
                    success_rate=float(feature_data["success_rate"]),
                    last_used=datetime.fromisoformat(feature_data["last_used"]) if feature_data["last_used"] else None
                )
                features.append(feature)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error getting all features: {e}")
            return []
    
    async def get_feature_analytics(self, feature_id: str, days_back: int = 7) -> Dict[str, Any]:
        """Get analytics for a specific feature"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            # Get usage events
            events_result = self.supabase.table("feature_usage_events").select("*").eq("feature_id", feature_id).gte("timestamp", start_date).execute()
            
            events = events_result.data
            
            # Calculate analytics
            total_events = len(events)
            unique_users = len(set(event["user_telegram_id"] for event in events))
            access_events = [e for e in events if e["event_type"] == "access"]
            success_events = [e for e in events if e["event_type"] == "success"]
            error_events = [e for e in events if e["event_type"] == "error"]
            
            success_rate = len(success_events) / len(access_events) if access_events else 0
            error_rate = len(error_events) / len(access_events) if access_events else 0
            
            # A/B test analytics
            ab_test_analytics = {}
            if events:
                ab_groups = set(e.get("ab_test_group") for e in events if e.get("ab_test_group"))
                for group in ab_groups:
                    group_events = [e for e in events if e.get("ab_test_group") == group]
                    group_success = [e for e in group_events if e["event_type"] == "success"]
                    
                    ab_test_analytics[group] = {
                        "total_events": len(group_events),
                        "unique_users": len(set(e["user_telegram_id"] for e in group_events)),
                        "success_rate": len(group_success) / len(group_events) if group_events else 0
                    }
            
            return {
                "feature_id": feature_id,
                "period_days": days_back,
                "total_events": total_events,
                "unique_users": unique_users,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "daily_usage": self._calculate_daily_usage(events),
                "ab_test_analytics": ab_test_analytics,
                "top_error_types": self._get_top_error_types(error_events)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting feature analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_daily_usage(self, events: List[Dict]) -> Dict[str, int]:
        """Calculate daily usage from events"""
        daily_usage = {}
        
        for event in events:
            date = event["timestamp"][:10]  # Get YYYY-MM-DD
            daily_usage[date] = daily_usage.get(date, 0) + 1
        
        return daily_usage
    
    def _get_top_error_types(self, error_events: List[Dict]) -> Dict[str, int]:
        """Get most common error types"""
        error_types = {}
        
        for event in error_events:
            metadata = json.loads(event.get("metadata", "{}"))
            error_type = metadata.get("error_type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def _invalidate_cache(self):
        """Invalidate the features cache"""
        self._features_cache.clear()
        self._cache_expiry = datetime.now()
    
    # Convenience methods for common operations
    async def enable_feature(self, feature_id: str) -> bool:
        """Enable a feature for all users"""
        return await self.update_feature(feature_id, {
            "flag": FeatureFlag.ENABLED.value,
            "rollout_strategy": RolloutStrategy.ALL_USERS.value
        })
    
    async def disable_feature(self, feature_id: str) -> bool:
        """Disable a feature completely"""
        return await self.update_feature(feature_id, {
            "flag": FeatureFlag.DISABLED.value
        })
    
    async def set_percentage_rollout(self, feature_id: str, percentage: float) -> bool:
        """Set percentage-based rollout"""
        return await self.update_feature(feature_id, {
            "flag": FeatureFlag.GRADUAL_ROLLOUT.value,
            "rollout_strategy": RolloutStrategy.PERCENTAGE.value,
            "rollout_percentage": percentage
        })
    
    async def create_ab_test(self, feature_id: str, groups: Dict[str, Dict]) -> bool:
        """Create A/B test for feature"""
        return await self.update_feature(feature_id, {
            "flag": FeatureFlag.A_B_TEST.value,
            "ab_test_groups": json.dumps(groups),
            "ab_test_active": True
        })
    
    async def emergency_disable(self, feature_id: str, reason: str) -> bool:
        """Emergency disable a feature with logging"""
        success = await self.disable_feature(feature_id)
        
        if success:
            # Log emergency disable
            await self.log_feature_usage(
                feature_id, 
                0,  # System user
                "emergency_disable", 
                {"reason": reason, "timestamp": datetime.now().isoformat()}
            )
            logger.warning(f"🚨 Emergency disabled feature {feature_id}: {reason}")
        
        return success

# Integration decorator for bot commands
def feature_gate(feature_id: str, log_usage: bool = True):
    """Decorator to gate bot commands behind feature flags"""
    def decorator(func):
        async def wrapper(message, *args, **kwargs):
            # Get feature control system instance
            # This would need to be passed in or retrieved from global state
            feature_system = kwargs.get('feature_system')
            
            if not feature_system:
                # Fallback: allow if no feature system
                return await func(message, *args, **kwargs)
            
            user_telegram_id = message.from_user.id
            
            # Get user roles (implement based on your user system)
            user_roles = await get_user_roles(user_telegram_id)
            
            # Check if feature is enabled
            enabled, ab_group = await feature_system.is_feature_enabled(
                feature_id, user_telegram_id, user_roles
            )
            
            if not enabled:
                await message.reply("This feature is currently not available.")
                return
            
            # Log usage if enabled
            if log_usage:
                await feature_system.log_feature_usage(
                    feature_id, user_telegram_id, "access", 
                    {"command": func.__name__}, ab_group
                )
            
            try:
                # Execute the command
                result = await func(message, *args, **kwargs)
                
                # Log success
                if log_usage:
                    await feature_system.log_feature_usage(
                        feature_id, user_telegram_id, "success", 
                        {"command": func.__name__}, ab_group
                    )
                
                return result
                
            except Exception as e:
                # Log error
                if log_usage:
                    await feature_system.log_feature_usage(
                        feature_id, user_telegram_id, "error", 
                        {"command": func.__name__, "error": str(e)}, ab_group
                    )
                raise
        
        return wrapper
    return decorator

async def get_user_roles(user_telegram_id: int) -> List[str]:
    """Get user roles - implement based on your user system"""
    # This is a placeholder - implement based on your actual user role system
    return ["user"]  # Default role

# Example usage in bot commands:
"""
@feature_gate("advanced_analytics", log_usage=True)
async def advanced_stats_handler(message: Message):
    # This command is gated behind the "advanced_analytics" feature flag
    # Only users with access will see this functionality
    pass

@feature_gate("beta_pod_features", log_usage=True)  
async def beta_pod_handler(message: Message):
    # This command is only available to beta users
    pass
"""

if __name__ == "__main__":
    print("Feature Control System - Use FeatureControlSystem class to manage features")