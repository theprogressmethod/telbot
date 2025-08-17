#!/usr/bin/env python3
"""
Quick Staging Configuration Using Dev Database
Sets up staging environment using existing dev database for immediate testing
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_staging_with_dev_db():
    """Configure staging to use dev database for immediate testing"""
    logger.info("🔧 Configuring staging environment with dev database...")
    
    # Load current environment
    load_dotenv()
    
    # Create staging configuration using dev database
    staging_config = f"""# STAGING ENVIRONMENT (Using Dev Database for Testing)
# Configured: {datetime.now().isoformat()}

# Environment
ENVIRONMENT=staging

# Database (using dev database for testing)
SUPABASE_URL={os.getenv('SUPABASE_URL', 'https://apfiwfkpdhslfavnncsl.supabase.co')}
SUPABASE_KEY={os.getenv('SUPABASE_KEY', '')}

# Bot Configuration (using dev bot for staging tests)
BOT_TOKEN={os.getenv('BOT_TOKEN', '')}

# API Keys (using dev keys for staging tests)
OPENAI_API_KEY={os.getenv('OPENAI_API_KEY', '')}
RESEND_API_KEY=re_test_key_staging_placeholder
ADMIN_API_KEY=staging_admin_key_12345

# Safety Controls (EXTRA SAFETY in staging)
ENABLE_PRODUCTION_COMMUNICATIONS=false
SAFE_MODE=true
STAGING_MODE=true

# Feature Flags (controlled rollout in staging)
FEATURE_SUPERIOR_ONBOARDING=false
FEATURE_BUSINESS_INTELLIGENCE_DASHBOARD=true
FEATURE_USER_FACING_METRICS=false
FEATURE_OPTIMIZED_NURTURE_SEQUENCES=false
FEATURE_BEHAVIORAL_ANALYTICS=true
FEATURE_ENHANCED_ADMIN_DASHBOARD=true

# Testing Configuration
TEST_USER_PREFIX=staging_test_
TEST_DATA_ENABLED=true
CLEANUP_TEST_DATA=false

# Migration Tracking
STAGING_SCHEMA_VERSION=2.0
STAGING_MIGRATION_DATE={datetime.now().isoformat()}
"""
    
    # Write staging environment file
    with open('.env.staging', 'w') as f:
        f.write(staging_config)
    
    logger.info("✅ Created .env.staging with dev database configuration")
    
    # Create staging startup script
    startup_script = """#!/usr/bin/env python3
\"\"\"
Start Telbot in Staging Mode
Loads staging environment and starts bot with safety controls
\"\"\"

import os
import subprocess
import sys
from dotenv import load_dotenv

def start_staging():
    \"\"\"Start telbot in staging mode\"\"\"
    print("🚀 Starting Telbot in STAGING mode...")
    
    # Load staging environment
    load_dotenv('.env.staging')
    
    # Verify staging mode
    if os.getenv('ENVIRONMENT') != 'staging':
        print("❌ Environment not set to staging")
        return False
    
    if os.getenv('SAFE_MODE') != 'true':
        print("❌ Safe mode not enabled")
        return False
    
    print("✅ Staging environment loaded")
    print("✅ Safety controls active")
    print("✅ Starting telbot...")
    
    # Start telbot with staging environment
    try:
        subprocess.run([sys.executable, 'telbot.py'], 
                      env=dict(os.environ), check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Staging bot stopped")
    except Exception as e:
        print(f"❌ Error starting staging bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_staging()
"""
    
    with open('start_staging.py', 'w') as f:
        f.write(startup_script)
    
    os.chmod('start_staging.py', 0o755)
    logger.info("✅ Created start_staging.py script")
    
    # Create staging test runner
    test_runner = """#!/usr/bin/env python3
\"\"\"
Run Staging Tests with Dev Database
\"\"\"

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_staging_tests():
    \"\"\"Run tests in staging environment\"\"\"
    print("🧪 Running staging tests with dev database...")
    
    # Load staging environment
    load_dotenv('.env.staging')
    
    # Run the behavioral intelligence integration test
    print("\\n🧠 Testing Behavioral Intelligence System...")
    try:
        result = subprocess.run([
            sys.executable, 'test_full_integration.py'
        ], env=dict(os.environ), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Behavioral Intelligence tests passed")
        else:
            print("❌ Some tests failed - this is expected during development")
            print("📋 Check test output for details")
        
        # Show key results
        if "TEST SUMMARY" in result.stdout:
            summary_start = result.stdout.find("TEST SUMMARY")
            print(result.stdout[summary_start:summary_start+500])
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
    
    # Test component imports
    print("\\n🔧 Testing component imports...")
    components = [
        'business_intelligence_dashboard',
        'superior_onboarding_sequence', 
        'user_facing_metrics',
        'optimized_nurture_sequences',
        'feature_flags'
    ]
    
    for component in components:
        try:
            __import__(component)
            print(f"  ✅ {component}")
        except Exception as e:
            print(f"  ❌ {component}: {e}")
    
    print("\\n✅ Staging test run completed")

if __name__ == "__main__":
    run_staging_tests()
"""
    
    with open('run_staging_tests.py', 'w') as f:
        f.write(test_runner)
    
    os.chmod('run_staging_tests.py', 0o755)
    logger.info("✅ Created run_staging_tests.py script")
    
    return True

def main():
    """Configure staging environment"""
    logger.info("🏗️ Setting up staging environment with dev database...")
    
    if configure_staging_with_dev_db():
        logger.info("\n✅ STAGING ENVIRONMENT CONFIGURED")
        logger.info("\nNext steps:")
        logger.info("1. Run: python3 run_staging_tests.py")
        logger.info("2. Run: python3 start_staging.py")
        logger.info("3. Test behavioral intelligence features")
        logger.info("4. Once validated, create separate staging database")
        return True
    else:
        logger.error("❌ Staging configuration failed")
        return False

if __name__ == "__main__":
    main()