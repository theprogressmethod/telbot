#!/usr/bin/env python3
"""
Feature Flag System for TelBot
Provides safe feature rollout with environment-specific controls
"""

import functools
import logging
from typing import Callable, Optional, Any, Dict

logger = logging.getLogger(__name__)

class FeatureFlag:
    """Feature flag decorator and management system"""
    
    @staticmethod
    def require(flag_name: str, fallback_response: Optional[str] = None):
        """
        Decorator that requires a feature flag to be enabled
        
        Args:
            flag_name: Name of the feature flag to check
            fallback_response: Message to send if feature is disabled (for bot commands)
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Import here to avoid circular imports
                from environment_manager import env_manager
                
                # Check if feature flag is enabled
                if env_manager.get_feature_flag(flag_name):
                    logger.debug(f"Feature flag '{flag_name}' enabled, executing {func.__name__}")
                    return await func(*args, **kwargs)
                else:
                    logger.info(f"Feature flag '{flag_name}' disabled, skipping {func.__name__}")
                    
                    # If this is a bot command handler, send fallback response
                    if fallback_response and len(args) > 0:
                        # First argument should be Message object
                        message = args[0]
                        if hasattr(message, 'answer'):
                            await message.answer(fallback_response)
                    
                    return None
            
            # Add metadata for debugging
            wrapper._feature_flag = flag_name
            wrapper._fallback_response = fallback_response
            return wrapper
        return decorator

# Convenience functions and common decorators
feature_flag = FeatureFlag.require

# Common feature flag configurations
class CommonFlags:
    """Common feature flag configurations"""
    
    NEW_ONBOARDING = "new_onboarding"
    FIRST_IMPRESSION_FSM = "first_impression_fsm"  # DISABLED after production incident
    NURTURE_SEQUENCES = "nurture_sequences"

# Example usage decorators with specific flags
def new_onboarding_required(fallback: str = "This onboarding feature is not available yet."):
    return feature_flag(CommonFlags.NEW_ONBOARDING, fallback)

def nurture_sequences_required(fallback: str = "Nurture sequences are not available."):
    return feature_flag(CommonFlags.NURTURE_SEQUENCES, fallback)

# Emergency feature disabling
class EmergencyFlags:
    """Emergency feature flags for incident response"""
    
    @staticmethod
    def disable_first_impression_fsm():
        """Emergency disable of first impression FSM due to production bug"""
        from environment_manager import env_manager
        env_manager.set_feature_flag(CommonFlags.FIRST_IMPRESSION_FSM, False)
        logger.warning("EMERGENCY: First impression FSM disabled due to production incident")

# Feature flag status reporting
def get_feature_status() -> Dict[str, Any]:
    """Get current status of all feature flags"""
    from environment_manager import env_manager
    return {
        "environment": env_manager.current_env.value,
        "safety_mode": env_manager.config.safety_mode,
        "debug_mode": env_manager.config.debug_mode,
        "feature_flags": env_manager.config.feature_flags,
        "enabled_count": sum(env_manager.config.feature_flags.values()),
        "total_count": len(env_manager.config.feature_flags)
    }