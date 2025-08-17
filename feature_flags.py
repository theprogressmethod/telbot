#!/usr/bin/env python3
"""
Feature Flags System
Controls deployment of new Behavioral Intelligence features
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import Client

class FeatureFlags:
    """
    Feature flag management system for controlled deployment
    """
    
    # Global feature flags (default: all disabled for safe deployment)
    DEFAULT_FLAGS = {
        "superior_onboarding": False,
        "business_intelligence_dashboard": False,
        "user_facing_metrics": False,
        "optimized_nurture_sequences": False,
        "behavioral_analytics": False,
        "enhanced_admin_dashboard": False,
        "micro_commitment_onboarding": False,
        "progressive_difficulty_scaling": False
    }
    
    # Test user IDs (these users can access features even when disabled)
    TEST_USERS = [
        # Add test user IDs here when ready for testing
        # Example: "123456789"  # Admin user
    ]
    
    # Admin user IDs (always have access to admin features)
    ADMIN_USERS = [
        # Add admin user IDs here
        # Example: "987654321"  # Product manager
    ]
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.supabase = supabase_client
        self.flags = self._load_flags()
        self._setup_environment_overrides()
    
    def _load_flags(self) -> Dict[str, bool]:
        """Load feature flags from environment or defaults"""
        flags = self.DEFAULT_FLAGS.copy()
        
        # Override with environment variables
        for flag_name in flags.keys():
            env_var = f"FEATURE_{flag_name.upper()}"
            env_value = os.getenv(env_var)
            if env_value is not None:
                flags[flag_name] = env_value.lower() in ('true', '1', 'yes', 'on')
        
        return flags
    
    def _setup_environment_overrides(self):
        """Setup environment-specific overrides"""
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment == "development":
            # In dev, enable features for testing
            self.flags.update({
                "superior_onboarding": True,
                "business_intelligence_dashboard": True,
                "user_facing_metrics": True,
                "behavioral_analytics": True,
                "enhanced_admin_dashboard": True
            })
        elif environment == "staging":
            # In staging, enable for testing but keep some disabled
            self.flags.update({
                "enhanced_admin_dashboard": True,
                "business_intelligence_dashboard": True,
                "behavioral_analytics": True
            })
        elif environment == "production":
            # In production, all flags default to False for safety
            pass
    
    def is_enabled(self, feature_name: str, user_id: Optional[str] = None, user_role: Optional[str] = None) -> bool:
        """
        Check if a feature is enabled for a specific user
        
        Args:
            feature_name: Name of the feature to check
            user_id: User ID to check (optional)
            user_role: User role (optional)
        
        Returns:
            True if feature is enabled for this user
        """
        # Check if feature exists
        if feature_name not in self.flags:
            return False
        
        # Admin users get access to admin features
        if self._is_admin_feature(feature_name) and self._is_admin_user(user_id, user_role):
            return True
        
        # Test users get access to all features
        if user_id and self._is_test_user(user_id):
            return True
        
        # Check global flag
        return self.flags.get(feature_name, False)
    
    def _is_admin_feature(self, feature_name: str) -> bool:
        """Check if this is an admin-only feature"""
        admin_features = [
            "business_intelligence_dashboard",
            "enhanced_admin_dashboard",
            "behavioral_analytics"
        ]
        return feature_name in admin_features
    
    def _is_admin_user(self, user_id: Optional[str], user_role: Optional[str]) -> bool:
        """Check if user is an admin"""
        if user_role in ["admin", "super_admin"]:
            return True
        if user_id and user_id in self.ADMIN_USERS:
            return True
        return False
    
    def _is_test_user(self, user_id: str) -> bool:
        """Check if user is a test user"""
        return user_id in self.TEST_USERS
    
    def enable_feature(self, feature_name: str, globally: bool = False, user_id: Optional[str] = None) -> bool:
        """
        Enable a feature globally or for specific user
        
        Args:
            feature_name: Feature to enable
            globally: Enable for all users
            user_id: Enable for specific user only
        
        Returns:
            True if successful
        """
        if feature_name not in self.DEFAULT_FLAGS:
            return False
        
        if globally:
            self.flags[feature_name] = True
            self._persist_flag_change(feature_name, True, "global")
        elif user_id:
            if user_id not in self.TEST_USERS:
                self.TEST_USERS.append(user_id)
            self._persist_flag_change(feature_name, True, f"user:{user_id}")
        
        return True
    
    def disable_feature(self, feature_name: str, globally: bool = False, user_id: Optional[str] = None) -> bool:
        """
        Disable a feature globally or for specific user
        
        Args:
            feature_name: Feature to disable
            globally: Disable for all users
            user_id: Remove from test users
        
        Returns:
            True if successful
        """
        if feature_name not in self.DEFAULT_FLAGS:
            return False
        
        if globally:
            self.flags[feature_name] = False
            self._persist_flag_change(feature_name, False, "global")
        elif user_id and user_id in self.TEST_USERS:
            self.TEST_USERS.remove(user_id)
            self._persist_flag_change(feature_name, False, f"user:{user_id}")
        
        return True
    
    def _persist_flag_change(self, feature_name: str, enabled: bool, scope: str):
        """Persist feature flag changes to database"""
        if not self.supabase:
            return
        
        try:
            change_record = {
                "feature_name": feature_name,
                "enabled": enabled,
                "scope": scope,
                "changed_at": datetime.now().isoformat(),
                "environment": os.getenv("ENVIRONMENT", "development")
            }
            
            self.supabase.table("feature_flag_changes").insert(change_record).execute()
        except Exception as e:
            print(f"Warning: Could not persist feature flag change: {e}")
    
    def get_all_flags(self) -> Dict[str, bool]:
        """Get all current feature flags"""
        return self.flags.copy()
    
    def get_user_features(self, user_id: str, user_role: Optional[str] = None) -> Dict[str, bool]:
        """Get all features available to a specific user"""
        return {
            feature: self.is_enabled(feature, user_id, user_role)
            for feature in self.DEFAULT_FLAGS.keys()
        }
    
    def add_test_user(self, user_id: str) -> bool:
        """Add user to test user list"""
        if user_id not in self.TEST_USERS:
            self.TEST_USERS.append(user_id)
            self._persist_flag_change("test_user_added", True, f"user:{user_id}")
            return True
        return False
    
    def remove_test_user(self, user_id: str) -> bool:
        """Remove user from test user list"""
        if user_id in self.TEST_USERS:
            self.TEST_USERS.remove(user_id)
            self._persist_flag_change("test_user_removed", True, f"user:{user_id}")
            return True
        return False
    
    def get_feature_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive feature status report"""
        return {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.now().isoformat(),
            "global_flags": self.flags,
            "test_users_count": len(self.TEST_USERS),
            "admin_users_count": len(self.ADMIN_USERS),
            "features_enabled": sum(1 for enabled in self.flags.values() if enabled),
            "features_total": len(self.flags),
            "safety_mode": not any(self.flags.values())  # True if all features disabled
        }

# Global instance
_feature_flags = None

def get_feature_flags(supabase_client: Optional[Client] = None) -> FeatureFlags:
    """Get global feature flags instance"""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags(supabase_client)
    return _feature_flags

def is_feature_enabled(feature_name: str, user_id: Optional[str] = None, user_role: Optional[str] = None) -> bool:
    """Convenience function to check if feature is enabled"""
    flags = get_feature_flags()
    return flags.is_enabled(feature_name, user_id, user_role)

# Decorators for easy feature flagging
def require_feature(feature_name: str):
    """Decorator to require a feature to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to extract user_id from args/kwargs
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            
            if not is_feature_enabled(feature_name, user_id):
                raise PermissionError(f"Feature '{feature_name}' is not enabled")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def feature_flag_check(feature_name: str, user_id: Optional[str] = None):
    """Context manager for feature flag checks"""
    class FeatureFlagContext:
        def __init__(self, enabled: bool):
            self.enabled = enabled
        
        def __enter__(self):
            return self.enabled
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    enabled = is_feature_enabled(feature_name, user_id)
    return FeatureFlagContext(enabled)

# Command line interface for managing feature flags
def main():
    """CLI for managing feature flags"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage feature flags")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all feature flags")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a feature")
    enable_parser.add_argument("feature", help="Feature name to enable")
    enable_parser.add_argument("--global", dest="global_flag", action="store_true", help="Enable globally")
    enable_parser.add_argument("--user", help="Enable for specific user")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a feature")
    disable_parser.add_argument("feature", help="Feature name to disable")
    disable_parser.add_argument("--global", dest="global_flag", action="store_true", help="Disable globally")
    disable_parser.add_argument("--user", help="Disable for specific user")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show feature flag status")
    
    # Test user commands
    test_parser = subparsers.add_parser("test-user", help="Manage test users")
    test_parser.add_argument("action", choices=["add", "remove", "list"])
    test_parser.add_argument("user_id", nargs="?", help="User ID")
    
    args = parser.parse_args()
    
    flags = get_feature_flags()
    
    if args.command == "list":
        print("Feature Flags:")
        for feature, enabled in flags.get_all_flags().items():
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            print(f"  {feature}: {status}")
    
    elif args.command == "enable":
        success = flags.enable_feature(args.feature, getattr(args, 'global_flag', False), args.user)
        if success:
            print(f"✅ Enabled feature: {args.feature}")
        else:
            print(f"❌ Failed to enable feature: {args.feature}")
    
    elif args.command == "disable":
        success = flags.disable_feature(args.feature, getattr(args, 'global_flag', False), args.user)
        if success:
            print(f"✅ Disabled feature: {args.feature}")
        else:
            print(f"❌ Failed to disable feature: {args.feature}")
    
    elif args.command == "status":
        report = flags.get_feature_status_report()
        print("Feature Flag Status Report:")
        print(f"Environment: {report['environment']}")
        print(f"Features enabled: {report['features_enabled']}/{report['features_total']}")
        print(f"Test users: {report['test_users_count']}")
        print(f"Safety mode: {report['safety_mode']}")
    
    elif args.command == "test-user":
        if args.action == "add" and args.user_id:
            success = flags.add_test_user(args.user_id)
            print(f"✅ Added test user: {args.user_id}" if success else f"❌ User already exists: {args.user_id}")
        elif args.action == "remove" and args.user_id:
            success = flags.remove_test_user(args.user_id)
            print(f"✅ Removed test user: {args.user_id}" if success else f"❌ User not found: {args.user_id}")
        elif args.action == "list":
            print(f"Test users: {flags.TEST_USERS}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()