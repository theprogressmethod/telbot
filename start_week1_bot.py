#!/usr/bin/env python3
"""
WEEK 1 BOT STARTUP SCRIPT
=========================
Clean startup with conflict detection and resolution
"""

import subprocess
import sys
import time
import os
from datetime import datetime

def check_and_kill_conflicts():
    """Check for and kill conflicting bot processes"""
    
    print("🔍 Checking for conflicting bot processes...")
    
    try:
        # Check for existing telbot processes
        result = subprocess.run(['pgrep', '-f', 'telbot'], capture_output=True, text=True)
        
        if result.returncode == 0:
            processes = result.stdout.strip().split('\n')
            print(f"   ⚠️  Found {len(processes)} conflicting processes")
            print(f"   🔄 Killing conflicting processes...")
            
            # Kill the processes
            subprocess.run(['pkill', '-f', 'telbot'], capture_output=True)
            time.sleep(2)  # Wait for processes to die
            
            print(f"   ✅ Conflicts resolved")
        else:
            print(f"   ✅ No conflicts found")
            
    except Exception as e:
        print(f"   ⚠️  Could not check conflicts: {e}")

def start_bot():
    """Start the Week 1 bot with clean environment"""
    
    print("🚀 STARTING WEEK 1 MVP BOT")
    print("=" * 40)
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Bot: @TPM_superbot (development)")
    print(f"   Environment: Development only")
    print("=" * 40)
    
    # Check for conflicts first
    check_and_kill_conflicts()
    
    print(f"\n🎯 WEEK 1 FEATURES ACTIVE:")
    print(f"   ✅ User registration")
    print(f"   ✅ Basic commitments (/commit)")
    print(f"   ✅ SMART 3-retry enhancement")
    print(f"   ✅ Commitment listing (/list)")
    print(f"   ✅ Completion tracking (/done)")
    print(f"   ✅ Basic pod system (/mypod)")
    print(f"   ✅ User feedback (/feedback)")
    
    print(f"\n❌ ADVANCED FEATURES DISABLED:")
    print(f"   ML systems, analytics, scaling, payments")
    
    print(f"\n🧪 TEST COMMANDS:")
    print(f"   /start - Welcome message")
    print(f"   /commit read a book - Triggers 3-retry system")
    print(f"   /commit I will read 10 pages by 8pm - Saves directly")
    print(f"   /list - Show commitments")
    print(f"   /done - Mark complete")
    
    print(f"\n🚀 Starting bot...")
    print(f"   Press Ctrl+C to stop")
    print(f"   Bot will handle up to 10 beta users")
    print("=" * 40)
    
    # Import and run the main bot
    try:
        import telbot
        print("✅ Bot modules loaded successfully")
        
        # This will start the polling
        import asyncio
        asyncio.run(telbot.main())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
        print("✅ Shutdown complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_bot()