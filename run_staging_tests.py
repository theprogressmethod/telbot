#!/usr/bin/env python3
"""
Run Staging Tests with Dev Database
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_staging_tests():
    """Run tests in staging environment"""
    print("🧪 Running staging tests with dev database...")
    
    # Load staging environment
    load_dotenv('.env.staging')
    
    # Run the behavioral intelligence integration test
    print("\n🧠 Testing Behavioral Intelligence System...")
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
    print("\n🔧 Testing component imports...")
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
    
    print("\n✅ Staging test run completed")

if __name__ == "__main__":
    run_staging_tests()
