#!/usr/bin/env python3
"""
Validate Environment Configuration
Ensures all required environment variables are set for the target environment
"""

import os
import sys
import argparse

# Required variables for each environment
REQUIRED_VARS = {
    'base': [
        'BOT_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'OPENAI_API_KEY'
    ],
    'development': [
        'DEV_BOT_TOKEN'
    ],
    'staging': [
        'STAGING_BOT_TOKEN'
    ],
    'production': [
        'PROD_BOT_TOKEN',
        'RENDER_DEPLOY_HOOK_production'
    ]
}

def validate_environment(environment):
    """Validate that all required environment variables are set"""
    print(f"🔍 Validating environment: {environment}")
    
    # Get required variables for this environment
    required = REQUIRED_VARS.get('base', [])
    env_specific = REQUIRED_VARS.get(environment, [])
    
    missing = []
    present = []
    
    # Check base variables
    for var in required:
        if os.environ.get(var):
            present.append(var)
        else:
            missing.append(var)
    
    # Check environment-specific variables (in CI/CD context)
    for var in env_specific:
        # In GitHub Actions, these would be passed as secrets
        if var in os.environ or environment == 'test':
            present.append(var)
        else:
            missing.append(var)
    
    # Report results
    if present:
        print(f"✅ Present variables ({len(present)}):")
        for var in present:
            # Don't print the actual values for security
            print(f"   - {var}: {'*' * 8}")
    
    if missing:
        print(f"❌ Missing variables ({len(missing)}):")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print(f"✅ All required variables are present for {environment} environment")
    return True

def check_env_file(environment):
    """Check if environment file exists"""
    env_file = f".env.{environment}"
    
    if os.path.exists(env_file):
        print(f"✅ Environment file exists: {env_file}")
        
        # Check file contents (without printing sensitive data)
        with open(env_file, 'r') as f:
            lines = f.readlines()
            var_count = sum(1 for line in lines if '=' in line and not line.strip().startswith('#'))
            print(f"   Contains {var_count} variables")
        return True
    else:
        print(f"⚠️  Environment file not found: {env_file}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate environment configuration')
    parser.add_argument('--environment', required=True, 
                       choices=['development', 'staging', 'production', 'test'],
                       help='Environment to validate')
    
    args = parser.parse_args()
    
    # Validate environment variables
    env_valid = validate_environment(args.environment)
    
    # Check environment file
    file_valid = check_env_file(args.environment)
    
    # Overall result
    if env_valid:
        print(f"\n✅ Environment validation passed for {args.environment}")
        sys.exit(0)
    else:
        print(f"\n❌ Environment validation failed for {args.environment}")
        sys.exit(1)

if __name__ == "__main__":
    main()
