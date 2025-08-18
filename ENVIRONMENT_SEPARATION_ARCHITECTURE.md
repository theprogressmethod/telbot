# ENVIRONMENT SEPARATION ARCHITECTURE
**Date:** August 18, 2025  
**Purpose:** Prevent production contamination and enable safe development  
**Status:** Design Phase - Ready for Implementation  

## OVERVIEW

This document outlines a complete environment separation strategy to prevent the production outage that occurred due to development feature bleeding into production.

## CURRENT PROBLEMS

1. **Single Environment:** All development happens in production
2. **No Boundaries:** Dev features leak into prod
3. **No Testing Gate:** Changes deploy without validation  
4. **No Rollback:** No way to quickly revert problematic changes
5. **No Monitoring:** No visibility into environment health

## PROPOSED ARCHITECTURE

### Three-Tier Environment Strategy

```
DEVELOPMENT  →  STAGING  →  PRODUCTION
    ↓              ↓            ↓
  Feature      Release      Stable
  Testing     Validation   Operations
```

### Environment Specifications

#### DEVELOPMENT ENVIRONMENT
**Purpose:** Active development and feature testing  
**Stability:** Unstable - breaking changes expected  
**Data:** Synthetic test data  
**Users:** Developers only  

**Configuration:**
- Environment: `development`
- Bot Token: `DEV_BOT_TOKEN` (separate test bot)
- Database: `DEV_SUPABASE_URL` (isolated test database)
- Domain: `telbot-dev.render.com`
- Deployment: Automatic on `development` branch push

#### STAGING ENVIRONMENT  
**Purpose:** Release candidate testing and QA  
**Stability:** Stable - only release candidates  
**Data:** Production-like test data  
**Users:** QA team + selected beta testers  

**Configuration:**
- Environment: `staging`
- Bot Token: `STAGING_BOT_TOKEN` (separate staging bot)
- Database: `STAGING_SUPABASE_URL` (production replica)
- Domain: `telbot-staging.render.com`
- Deployment: Manual approval from `staging` branch

#### PRODUCTION ENVIRONMENT
**Purpose:** Live user-facing service  
**Stability:** Highly stable - only tested releases  
**Data:** Live user data  
**Users:** All end users  

**Configuration:**
- Environment: `production`
- Bot Token: `PROD_BOT_TOKEN` (live bot)
- Database: `PROD_SUPABASE_URL` (live database)
- Domain: `telbot.render.com`
- Deployment: Manual approval with rollback plan

## IMPLEMENTATION PLAN

### Phase 1: Environment Detection System

Create a robust environment management system:

```python
# environments.py
import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

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
    webhook_url: str
    debug_mode: bool
    safety_mode: bool
    feature_flags: Dict[str, bool]

class EnvironmentManager:
    def __init__(self):
        self.current_env = self._detect_environment()
        self.config = self._load_config()
    
    def _detect_environment(self) -> Environment:
        env_name = os.getenv("TELBOT_ENVIRONMENT", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            # Default to development for safety
            return Environment.DEVELOPMENT
    
    def _load_config(self) -> EnvironmentConfig:
        env = self.current_env.value
        
        configs = {
            "development": EnvironmentConfig(
                name="development",
                bot_token=os.getenv("DEV_BOT_TOKEN"),
                supabase_url=os.getenv("DEV_SUPABASE_URL"),
                supabase_key=os.getenv("DEV_SUPABASE_KEY"),
                webhook_url=os.getenv("DEV_WEBHOOK_URL"),
                debug_mode=True,
                safety_mode=True,
                feature_flags={
                    "new_onboarding": True,
                    "advanced_analytics": True,
                    "beta_features": True
                }
            ),
            "staging": EnvironmentConfig(
                name="staging",
                bot_token=os.getenv("STAGING_BOT_TOKEN"),
                supabase_url=os.getenv("STAGING_SUPABASE_URL"),
                supabase_key=os.getenv("STAGING_SUPABASE_KEY"),
                webhook_url=os.getenv("STAGING_WEBHOOK_URL"),
                debug_mode=True,
                safety_mode=True,
                feature_flags={
                    "new_onboarding": True,
                    "advanced_analytics": False,
                    "beta_features": False
                }
            ),
            "production": EnvironmentConfig(
                name="production",
                bot_token=os.getenv("PROD_BOT_TOKEN"),
                supabase_url=os.getenv("PROD_SUPABASE_URL"),
                supabase_key=os.getenv("PROD_SUPABASE_KEY"),
                webhook_url=os.getenv("PROD_WEBHOOK_URL"),
                debug_mode=False,
                safety_mode=False,
                feature_flags={
                    "new_onboarding": False,  # Disable until stable
                    "advanced_analytics": False,
                    "beta_features": False
                }
            )
        }
        
        return configs[env]
    
    def is_development(self) -> bool:
        return self.current_env == Environment.DEVELOPMENT
    
    def is_staging(self) -> bool:
        return self.current_env == Environment.STAGING
    
    def is_production(self) -> bool:
        return self.current_env == Environment.PRODUCTION
    
    def get_feature_flag(self, flag_name: str) -> bool:
        return self.config.feature_flags.get(flag_name, False)
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate all required environment variables are set"""
        validation = {
            "bot_token": bool(self.config.bot_token),
            "supabase_url": bool(self.config.supabase_url),
            "supabase_key": bool(self.config.supabase_key),
            "webhook_url": bool(self.config.webhook_url)
        }
        
        return validation
```

### Phase 2: Feature Flag System

Implement feature flags to control rollout:

```python
# feature_flags.py
from functools import wraps
from typing import Callable

def feature_flag(flag_name: str, fallback_response: str = None):
    """Decorator to enable/disable features based on environment"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            env_manager = EnvironmentManager()
            
            if env_manager.get_feature_flag(flag_name):
                return await func(*args, **kwargs)
            else:
                # Feature disabled - return fallback or do nothing
                if fallback_response and len(args) > 0:
                    message = args[0]  # First arg should be Message
                    await message.answer(fallback_response)
                return
        return wrapper
    return decorator

# Usage examples:
@feature_flag("new_onboarding", "This feature is not available yet.")
async def new_onboarding_flow(message):
    # Only runs if new_onboarding flag is True
    pass

@feature_flag("beta_features")
async def beta_command(message):
    # Only available in development
    pass
```

### Phase 3: Environment-Aware Bot Initialization

Update the main bot code:

```python
# telbot_v2.py (environment-aware version)
from environments import EnvironmentManager
import logging

# Initialize environment management
env_manager = EnvironmentManager()
config = env_manager.config

# Validate configuration
config_validation = env_manager.validate_config()
missing_vars = [k for k, v in config_validation.items() if not v]

if missing_vars:
    logger.error(f"Missing environment variables for {env_manager.current_env.value}: {missing_vars}")
    exit(1)

# Initialize bot with environment-specific config
bot = Bot(token=config.bot_token)
supabase = create_client(config.supabase_url, config.supabase_key)

# Environment-aware logging
logging.basicConfig(
    level=logging.DEBUG if config.debug_mode else logging.INFO,
    format=f"[{env_manager.current_env.value.upper()}] %(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"🚀 Bot starting in {env_manager.current_env.value} environment")
logger.info(f"📊 Feature flags: {config.feature_flags}")
logger.info(f"🔒 Safety mode: {config.safety_mode}")
```

### Phase 4: Claude Code Context System

Create a visibility system for Claude Code:

```python
# claude_context.py
import json
from datetime import datetime
from pathlib import Path

class ClaudeCodeContext:
    """Provides Claude Code with current environment context"""
    
    def __init__(self, env_manager: EnvironmentManager):
        self.env_manager = env_manager
        self.context_file = Path("CLAUDE_CONTEXT.json")
    
    def generate_context(self) -> Dict[str, Any]:
        """Generate current context for Claude Code"""
        return {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "current": self.env_manager.current_env.value,
                "is_production": self.env_manager.is_production(),
                "debug_mode": self.env_manager.config.debug_mode,
                "safety_mode": self.env_manager.config.safety_mode
            },
            "database": {
                "url": self.env_manager.config.supabase_url,
                "key_set": bool(self.env_manager.config.supabase_key)
            },
            "bot": {
                "token_set": bool(self.env_manager.config.bot_token),
                "webhook_url": self.env_manager.config.webhook_url
            },
            "feature_flags": self.env_manager.config.feature_flags,
            "git": {
                "branch": self._get_git_branch(),
                "commit": self._get_git_commit(),
                "status": self._get_git_status()
            },
            "warnings": self._generate_warnings()
        }
    
    def _get_git_branch(self) -> str:
        try:
            import subprocess
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_git_commit(self) -> str:
        try:
            import subprocess
            result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_git_status(self) -> str:
        try:
            import subprocess
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                return "dirty"
            return "clean"
        except:
            return "unknown"
    
    def _generate_warnings(self) -> List[str]:
        """Generate warnings about current state"""
        warnings = []
        
        if self.env_manager.is_production():
            warnings.append("🚨 YOU ARE WORKING IN PRODUCTION ENVIRONMENT!")
            warnings.append("🛡️ Be extremely careful with changes")
            
        if self.env_manager.config.debug_mode and self.env_manager.is_production():
            warnings.append("⚠️ Debug mode enabled in production")
            
        git_status = self._get_git_status()
        if git_status == "dirty":
            warnings.append("📝 You have uncommitted changes")
            
        return warnings
    
    def save_context(self):
        """Save context to file for Claude Code to read"""
        context = self.generate_context()
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
    
    def display_banner(self):
        """Display environment banner in terminal"""
        context = self.generate_context()
        env_name = context["environment"]["current"].upper()
        
        banner = f"""
╔════════════════════════════════════════════════════════╗
║  TELBOT - {env_name:^45} ║
╠════════════════════════════════════════════════════════╣
║  Branch: {context['git']['branch']:<44} ║
║  Commit: {context['git']['commit']:<44} ║
║  Status: {context['git']['status']:<44} ║
║  Database: {context['database']['url'][:40]:<40} ║
╚════════════════════════════════════════════════════════╝
"""
        
        print(banner)
        
        # Show warnings
        for warning in context["warnings"]:
            print(f"🚨 {warning}")
        
        print()  # Empty line for readability

# Integration with main bot
if __name__ == "__main__":
    env_manager = EnvironmentManager()
    context_manager = ClaudeCodeContext(env_manager)
    
    # Save context for Claude Code
    context_manager.save_context()
    
    # Display banner
    context_manager.display_banner()
    
    # Start bot...
```

### Phase 5: Deployment Pipeline

Create automated deployment workflow:

```yaml
# .github/workflows/deployment.yml
name: TelBot Deployment Pipeline

on:
  push:
    branches: [ development, staging, main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          python -m pytest tests/ -v
          python -m pytest tests/integration/ -v
      - name: Lint code
        run: |
          flake8 telbot.py
          black --check .

  deploy-dev:
    if: github.ref == 'refs/heads/development'
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Deploy to Development
        run: |
          # Trigger Render deployment for dev environment
          curl -X POST "${{ secrets.RENDER_DEV_DEPLOY_HOOK }}"

  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    needs: test
    environment: staging
    steps:
      - name: Deploy to Staging
        run: |
          # Trigger Render deployment for staging environment
          curl -X POST "${{ secrets.RENDER_STAGING_DEPLOY_HOOK }}"

  deploy-production:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: test
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          # Trigger Render deployment for production environment
          curl -X POST "${{ secrets.RENDER_PROD_DEPLOY_HOOK }}"
```

## MIGRATION STRATEGY

### Step 1: Create Environment Infrastructure
1. **Create separate Telegram bots** for dev/staging/production
2. **Set up separate Supabase projects** for each environment
3. **Configure Render services** for each environment
4. **Set environment variables** for each service

### Step 2: Update Codebase
1. **Implement EnvironmentManager** class
2. **Add feature flag system**
3. **Update all configuration references**
4. **Add Claude Code context system**

### Step 3: Test Migration
1. **Deploy to development** first
2. **Validate all functionality** works
3. **Test environment switching**
4. **Verify feature flags work**

### Step 4: Production Migration
1. **Deploy during low-usage period**
2. **Monitor for issues**
3. **Have rollback plan ready**
4. **Validate all commands work**

## MONITORING AND ALERTING

### Environment Health Checks
- **Startup validation**: All required env vars present
- **Database connectivity**: Can connect to correct database
- **Bot functionality**: Can send/receive messages
- **Feature flag validation**: Flags loading correctly

### Claude Code Integration
- **Context file updates**: Automatically generated on startup
- **Environment warnings**: Clear indicators when in production
- **Git status integration**: Show branch/commit/dirty status
- **Configuration display**: Show which database/bot being used

### Error Monitoring
- **Environment-tagged logging**: Easy to filter by environment
- **Real-time alerts**: Immediate notification of production issues
- **Dashboard views**: Separate metrics per environment
- **Rollback triggers**: Automatic rollback on critical errors

## SUCCESS METRICS

### Environment Isolation
- **0 cross-contamination incidents** between environments
- **100% feature flag compliance** in production
- **<1 minute** to identify which environment has issues
- **<5 minutes** to rollback problematic deployments

### Developer Experience
- **Clear environment indicators** in all tools
- **Automatic context switching** for Claude Code
- **Easy feature flag management**
- **Confident production deployments**

## NEXT STEPS

1. **Implement EnvironmentManager** class ✅ Ready to code
2. **Create separate bot tokens** (manual setup required)
3. **Set up staging environment** in Render
4. **Migrate current code** to use environment system
5. **Test full deployment pipeline**
6. **Deploy to production** with rollback plan

This architecture will prevent future production outages while enabling safe, rapid development and deployment.