#!/usr/bin/env python3
"""
Start Telbot in Staging Mode
Loads staging environment and starts bot with safety controls
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def start_staging():
    """Start telbot in staging mode"""
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
        print("\n🛑 Staging bot stopped")
    except Exception as e:
        print(f"❌ Error starting staging bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_staging()
