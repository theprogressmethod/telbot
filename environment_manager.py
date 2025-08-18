#!/usr/bin/env python3
"""
Environment Management System for TelBot
Provides complete environment separation and Claude Code integration
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class EnvironmentConfig:
    name: str
    bot_token: str
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    webhook_url: Optional[str] = None
    debug_mode: bool = False
    safety_mode: bool = True
    feature_flags: Optional[Dict[str, bool]] = None
    admin_api_key: Optional[str] = None

    def __post_init__(self):
        if self.feature_flags is None:
            self.feature_flags = {}

class EnvironmentManager:
    """Manages environment detection, configuration, and Claude Code integration"""
    
    def __init__(self):
        self.current_env = self._detect_environment()
        self.config = self._load_config()
        self.context_file = Path("CLAUDE_CONTEXT.json")
        
        # Log environment startup
        logger.info(f"🚀 Environment Manager initialized for {self.current_env.value}")
        
    def _detect_environment(self) -> Environment:
        """Detect current environment from environment variables"""
        # Try multiple environment variable names for flexibility
        env_vars = [
            "TELBOT_ENVIRONMENT", 
            "ENVIRONMENT", 
            "ENV", 
            "NODE_ENV"  # Common in many projects
        ]
        
        for env_var in env_vars:
            env_name = os.getenv(env_var, "").lower().strip()
            if env_name:
                try:
                    return Environment(env_name)
                except ValueError:
                    logger.warning(f"Invalid environment value '{env_name}' in {env_var}")
                    continue
        
        # If no environment specified, detect based on other indicators
        if os.getenv("RENDER_SERVICE_NAME"):  # Running on Render
            if "prod" in os.getenv("RENDER_SERVICE_NAME", "").lower():
                return Environment.PRODUCTION
            elif "staging" in os.getenv("RENDER_SERVICE_NAME", "").lower():
                return Environment.STAGING
        
        # Default to development for safety
        logger.warning("No environment specified, defaulting to DEVELOPMENT")
        return Environment.DEVELOPMENT
    
    def _load_config(self) -> EnvironmentConfig:
        """Load configuration for current environment"""
        env = self.current_env.value
        
        # Development configuration
        if env == "development":
            return EnvironmentConfig(
                name="development",
                bot_token=os.getenv("DEV_BOT_TOKEN") or os.getenv("BOT_TOKEN"),
                supabase_url=os.getenv("DEV_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
                supabase_key=os.getenv("DEV_SUPABASE_KEY") or os.getenv("SUPABASE_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                webhook_url=os.getenv("DEV_WEBHOOK_URL") or os.getenv("WEBHOOK_URL"),
                admin_api_key=os.getenv("DEV_ADMIN_API_KEY") or os.getenv("ADMIN_API_KEY"),
                debug_mode=True,
                safety_mode=True,
                feature_flags={
                    "new_onboarding": True,
                    "advanced_analytics": True,
                    "beta_features": True,
                    "first_impression_fsm": False,  # Disabled due to production bug
                    "nurture_sequences": True,
                    "google_meet_integration": True
                }
            )
        
        # Staging configuration
        elif env == "staging":
            return EnvironmentConfig(
                name="staging",
                bot_token=os.getenv("STAGING_BOT_TOKEN") or os.getenv("BOT_TOKEN"),
                supabase_url=os.getenv("STAGING_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
                supabase_key=os.getenv("STAGING_SUPABASE_KEY") or os.getenv("SUPABASE_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                webhook_url=os.getenv("STAGING_WEBHOOK_URL") or os.getenv("WEBHOOK_URL"),
                admin_api_key=os.getenv("STAGING_ADMIN_API_KEY") or os.getenv("ADMIN_API_KEY"),
                debug_mode=True,
                safety_mode=True,
                feature_flags={
                    "new_onboarding": True,
                    "advanced_analytics": False,
                    "beta_features": False,
                    "first_impression_fsm": False,  # Test carefully before enabling
                    "nurture_sequences": True,
                    "google_meet_integration": False  # Not needed in staging
                }
            )
        
        # Production configuration
        else:  # production
            return EnvironmentConfig(
                name="production",
                bot_token=os.getenv("PROD_BOT_TOKEN") or os.getenv("BOT_TOKEN"),
                supabase_url=os.getenv("PROD_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
                supabase_key=os.getenv("PROD_SUPABASE_KEY") or os.getenv("SUPABASE_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                webhook_url=os.getenv("PROD_WEBHOOK_URL") or os.getenv("WEBHOOK_URL"),
                admin_api_key=os.getenv("PROD_ADMIN_API_KEY") or os.getenv("ADMIN_API_KEY"),
                debug_mode=False,
                safety_mode=False,
                feature_flags={
                    "new_onboarding": False,  # Disabled until thoroughly tested
                    "advanced_analytics": False,
                    "beta_features": False,
                    "first_impression_fsm": False,  # DISABLED - caused production outage
                    "nurture_sequences": True,  # This is stable
                    "google_meet_integration": True  # Stable feature
                }
            )
    
    # Environment Detection Methods
    def is_development(self) -> bool:
        return self.current_env == Environment.DEVELOPMENT
    
    def is_staging(self) -> bool:
        return self.current_env == Environment.STAGING
    
    def is_production(self) -> bool:
        return self.current_env == Environment.PRODUCTION
    
    # Feature Flag Methods
    def get_feature_flag(self, flag_name: str) -> bool:
        return self.config.feature_flags.get(flag_name, False)
    
    def set_feature_flag(self, flag_name: str, enabled: bool):
        """Temporarily enable/disable feature flag (runtime only)"""
        self.config.feature_flags[flag_name] = enabled
        logger.info(f"Feature flag '{flag_name}' set to {enabled}")
    
    # Configuration Validation
    def validate_config(self) -> Dict[str, Any]:
        """Validate all required configuration is present"""
        validation = {
            "environment_detected": True,
            "bot_token": bool(self.config.bot_token),
            "supabase_url": bool(self.config.supabase_url),
            "supabase_key": bool(self.config.supabase_key),
            "openai_api_key": bool(self.config.openai_api_key),
            "webhook_url": bool(self.config.webhook_url)
        }
        
        # Check for missing critical configs
        missing = [k for k, v in validation.items() if not v]
        validation["is_valid"] = len(missing) == 0
        validation["missing"] = missing
        validation["warnings"] = self._get_config_warnings()
        
        return validation
    
    def _get_config_warnings(self) -> List[str]:
        """Get configuration warnings"""
        warnings = []
        
        if self.is_production():
            if self.config.debug_mode:
                warnings.append("Debug mode enabled in production")
            if not self.config.admin_api_key:
                warnings.append("No admin API key set for production")
        
        if not self.config.webhook_url:
            warnings.append("No webhook URL configured")
            
        return warnings
    
    # Git Integration
    def _run_git_command(self, command: List[str]) -> str:
        """Run git command safely and return output"""
        try:
            result = subprocess.run(
                ["git"] + command, 
                capture_output=True, 
                text=True, 
                timeout=5,  # 5 second timeout
                cwd=Path(__file__).parent  # Run in project directory
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return "unknown"
    
    def get_git_info(self) -> Dict[str, str]:
        """Get current git information"""
        return {
            "branch": self._run_git_command(["branch", "--show-current"]),
            "commit": self._run_git_command(["rev-parse", "--short", "HEAD"]),
            "status": "dirty" if self._run_git_command(["status", "--porcelain"]) else "clean",
            "remote": self._run_git_command(["config", "--get", "remote.origin.url"])
        }
    
    # Claude Code Integration
    def generate_claude_context(self) -> Dict[str, Any]:
        """Generate comprehensive context for Claude Code"""
        git_info = self.get_git_info()
        validation = self.validate_config()
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "telbot_environment": {
                "current": self.current_env.value,
                "is_production": self.is_production(),
                "is_staging": self.is_staging(), 
                "is_development": self.is_development(),
                "debug_mode": self.config.debug_mode,
                "safety_mode": self.config.safety_mode
            },
            "configuration": {
                "bot_token_set": validation["bot_token"],
                "database_connected": validation["supabase_url"] and validation["supabase_key"],
                "openai_configured": validation["openai_api_key"],
                "webhook_configured": validation["webhook_url"],
                "admin_access_configured": bool(self.config.admin_api_key)
            },
            "database": {
                "url": self.config.supabase_url[:50] + "..." if self.config.supabase_url else "not configured",
                "environment": self.current_env.value
            },
            "feature_flags": self.config.feature_flags,
            "git": git_info,
            "validation": validation,
            "warnings": self._generate_warnings(),
            "deployment_info": {
                "render_service": os.getenv("RENDER_SERVICE_NAME"),
                "render_region": os.getenv("RENDER_REGION"),
                "deployment_id": os.getenv("RENDER_DEPLOYMENT_ID")
            }
        }
        
        return context
    
    def _generate_warnings(self) -> List[str]:
        """Generate warnings about current state"""
        warnings = []
        
        if self.is_production():
            warnings.append("🚨 YOU ARE WORKING IN PRODUCTION ENVIRONMENT!")
            warnings.append("🛡️ Be extremely careful with any changes")
            warnings.append("🔄 Always test changes in staging first")
            
        git_info = self.get_git_info()
        if git_info["status"] == "dirty":
            warnings.append("📝 You have uncommitted changes")
            
        if git_info["branch"] != "main" and self.is_production():
            warnings.append(f"⚠️ Production running from non-main branch: {git_info['branch']}")
            
        validation = self.validate_config()
        if not validation["is_valid"]:
            warnings.append(f"⚠️ Missing configuration: {', '.join(validation['missing'])}")
            
        # Add configuration-specific warnings
        warnings.extend(validation["warnings"])
            
        return warnings
    
    def save_claude_context(self):
        """Save Claude Code context to file"""
        context = self.generate_claude_context()
        try:
            with open(self.context_file, 'w') as f:
                json.dump(context, f, indent=2)
            logger.debug(f"Claude context saved to {self.context_file}")
        except Exception as e:
            logger.error(f"Failed to save Claude context: {e}")
    
    def display_environment_banner(self):
        """Display environment banner for terminal/logs"""
        context = self.generate_claude_context()
        env_name = self.current_env.value.upper()
        git_info = context["git"]
        
        # Environment-specific colors (for terminals that support it)
        color = {
            "DEVELOPMENT": "\033[92m",  # Green
            "STAGING": "\033[93m",      # Yellow
            "PRODUCTION": "\033[91m"    # Red
        }.get(env_name, "\033[0m")
        reset_color = "\033[0m"
        
        banner = f"""
{color}╔════════════════════════════════════════════════════════╗
║  TELBOT - {env_name:^45} ║
╠════════════════════════════════════════════════════════╣
║  Branch: {git_info['branch'][:44]:<44} ║
║  Commit: {git_info['commit'][:44]:<44} ║
║  Status: {git_info['status'][:44]:<44} ║
║  Database: {self.config.supabase_url[:40]:<40} ║
╚════════════════════════════════════════════════════════╝{reset_color}
"""
        
        print(banner)
        
        # Show warnings
        for warning in context["warnings"]:
            print(f"🚨 {warning}")
        
        # Show feature flags in development/staging
        if not self.is_production():
            enabled_flags = [k for k, v in self.config.feature_flags.items() if v]
            if enabled_flags:
                print(f"🏴 Feature flags enabled: {', '.join(enabled_flags)}")
        
        print()  # Empty line for readability
    
    # Utility Methods
    def get_environment_summary(self) -> str:
        """Get a one-line summary of current environment"""
        git_info = self.get_git_info()
        return f"{self.current_env.value} | {git_info['branch']}@{git_info['commit']} | {git_info['status']}"
    
    def is_safe_for_destructive_operations(self) -> bool:
        """Check if it's safe to perform destructive operations"""
        return not self.is_production() or self.config.safety_mode
    
    def require_development(self):
        """Raise exception if not in development environment"""
        if not self.is_development():
            raise PermissionError(f"This operation requires development environment (currently in {self.current_env.value})")
    
    def require_non_production(self):
        """Raise exception if in production environment"""
        if self.is_production():
            raise PermissionError("This operation is not allowed in production environment")

# Global instance - can be imported directly
env_manager = EnvironmentManager()

# Convenience functions
def get_environment() -> str:
    return env_manager.current_env.value

def is_production() -> bool:
    return env_manager.is_production()

def is_development() -> bool:
    return env_manager.is_development()

def get_feature_flag(flag_name: str) -> bool:
    return env_manager.get_feature_flag(flag_name)

def get_config() -> EnvironmentConfig:
    return env_manager.config

# Initialize Claude context on import
if __name__ == "__main__":
    # Command line usage
    env_manager.display_environment_banner()
    env_manager.save_claude_context()
    
    # Validation
    validation = env_manager.validate_config()
    if not validation["is_valid"]:
        print(f"❌ Configuration errors: {validation['missing']}")
        exit(1)
    else:
        print("✅ Environment configuration valid")
else:
    # Save context when imported
    env_manager.save_claude_context()