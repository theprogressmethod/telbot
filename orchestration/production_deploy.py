#!/usr/bin/env python3
"""
Production Deployment Module
Deploys verified features to production with safety checks
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def load_test_report(deployment_dir):
    """Load the test verification report"""
    report_path = Path(deployment_dir) / "test_verification_report.json"
    with open(report_path, 'r') as f:
        return json.load(f)

def load_staging_config(deployment_dir):
    """Load staging configuration"""
    config_path = Path(deployment_dir) / "staging_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def pre_deployment_checks():
    """Run final safety checks before production deployment"""
    print("\n🔍 Running Pre-Deployment Checks...")
    checks_passed = True
    
    checks = [
        {
            "name": "Production Health Check",
            "command": "curl -f https://api.example.com/health",
            "description": "Verify production is currently healthy"
        },
        {
            "name": "Database Backup",
            "command": "pg_dump production > /backups/pre_deploy_$(date +%Y%m%d_%H%M%S).sql",
            "description": "Create production database backup"
        },
        {
            "name": "Git Status Clean",
            "command": "git status --porcelain",
            "description": "Ensure no uncommitted changes"
        },
        {
            "name": "Branch Check",
            "command": "git branch --show-current",
            "description": "Verify on correct branch"
        }
    ]
    
    for check in checks:
        print(f"  • {check['name']}...")
        result = run_command(check["command"])
        
        if check["name"] == "Git Status Clean":
            # Empty output means clean
            if result["output"].strip():
                print(f"    ❌ Uncommitted changes detected")
                checks_passed = False
            else:
                print(f"    ✅ Working directory clean")
        elif check["name"] == "Branch Check":
            branch = result["output"].strip()
            if branch in ["main", "master", "production"]:
                print(f"    ✅ On branch: {branch}")
            else:
                print(f"    ❌ Wrong branch: {branch} (should be main/master/production)")
                checks_passed = False
        else:
            if result["success"]:
                print(f"    ✅ {check['description']}")
            else:
                print(f"    ❌ Failed: {check['description']}")
                checks_passed = False
    
    return checks_passed

def run_command(command, timeout=300):
    """Execute a command with timeout"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Command timed out after {timeout} seconds",
            "returncode": -1
        }

def create_deployment_manifest(deployment_dir, staging_config):
    """Create a deployment manifest for production"""
    manifest = {
        "deployment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "features": staging_config.get("features_enabled", []),
        "feature_flags": staging_config.get("feature_flags", {}),
        "rollout_strategy": "blue_green",  # or "canary", "rolling"
        "health_checks": {
            "enabled": True,
            "interval": 30,
            "timeout": 10,
            "retries": 3
        },
        "rollback_triggers": {
            "error_rate_threshold": 0.05,
            "latency_threshold": 1000,
            "health_check_failures": 3
        }
    }
    
    manifest_path = Path(deployment_dir) / "production_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

def blue_green_deployment(manifest):
    """Perform blue-green deployment"""
    print("\n🔄 Starting Blue-Green Deployment...")
    
    steps = [
        {
            "name": "Deploy to Blue Environment",
            "command": "kubectl apply -f k8s/blue-deployment.yaml",
            "verify": "kubectl get pods -l version=blue"
        },
        {
            "name": "Run Blue Health Checks",
            "command": "curl -f http://blue.internal.example.com/health",
            "verify": None
        },
        {
            "name": "Switch Traffic to Blue",
            "command": "kubectl patch service production -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'",
            "verify": "kubectl get service production -o yaml"
        },
        {
            "name": "Monitor Blue Environment",
            "command": "sleep 60",  # Monitor for 1 minute
            "verify": None
        },
        {
            "name": "Decommission Green Environment",
            "command": "kubectl delete deployment green-deployment",
            "verify": None
        }
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"\n  Step {i}/{len(steps)}: {step['name']}")
        
        # Execute main command
        result = run_command(step["command"])
        
        if not result["success"]:
            print(f"    ❌ Failed: {step['name']}")
            print(f"    Error: {result['error']}")
            return False
        
        print(f"    ✅ Completed: {step['name']}")
        
        # Run verification if specified
        if step["verify"]:
            verify_result = run_command(step["verify"])
            if verify_result["success"]:
                print(f"    ✅ Verified")
    
    return True

def canary_deployment(manifest):
    """Perform canary deployment"""
    print("\n🐤 Starting Canary Deployment...")
    
    canary_stages = [
        {"percentage": 5, "duration": 300},    # 5% for 5 minutes
        {"percentage": 25, "duration": 600},   # 25% for 10 minutes
        {"percentage": 50, "duration": 600},   # 50% for 10 minutes
        {"percentage": 100, "duration": 0}     # 100% complete
    ]
    
    for stage in canary_stages:
        print(f"\n  Rolling out to {stage['percentage']}% of traffic...")
        
        # Update canary percentage
        command = f"kubectl set env deployment/production CANARY_PERCENTAGE={stage['percentage']}"
        result = run_command(command)
        
        if not result["success"]:
            print(f"    ❌ Failed to update canary percentage")
            return False
        
        print(f"    ✅ Updated to {stage['percentage']}%")
        
        if stage["duration"] > 0:
            print(f"    ⏰ Monitoring for {stage['duration']} seconds...")
            
            # Monitor metrics during canary stage
            if not monitor_deployment_health(stage["duration"]):
                print(f"    ❌ Health check failed during {stage['percentage']}% rollout")
                return False
    
    print("\n  ✅ Canary deployment successful!")
    return True

def monitor_deployment_health(duration):
    """Monitor deployment health for specified duration"""
    start_time = time.time()
    check_interval = 30
    
    while time.time() - start_time < duration:
        # Check error rate
        error_check = run_command("curl -s http://metrics.example.com/error_rate")
        if error_check["success"]:
            try:
                error_rate = float(error_check["output"])
                if error_rate > 0.05:  # 5% error threshold
                    print(f"      ⚠️ High error rate detected: {error_rate*100:.2f}%")
                    return False
            except:
                pass
        
        # Check latency
        latency_check = run_command("curl -s http://metrics.example.com/latency_p95")
        if latency_check["success"]:
            try:
                latency = float(latency_check["output"])
                if latency > 1000:  # 1000ms threshold
                    print(f"      ⚠️ High latency detected: {latency}ms")
                    return False
            except:
                pass
        
        # Wait before next check
        time.sleep(min(check_interval, duration - (time.time() - start_time)))
    
    return True

def update_feature_flags(manifest):
    """Update feature flags in production"""
    print("\n🚩 Updating Feature Flags...")
    
    for feature, config in manifest["feature_flags"].items():
        if config["enabled"]:
            percentage = config.get("rollout_percentage", 100)
            command = f"curl -X POST http://featureflags.example.com/api/flags -d '{{\"feature\":\"{feature}\",\"enabled\":true,\"percentage\":{percentage}}}'"
            
            result = run_command(command)
            if result["success"]:
                print(f"  ✅ Enabled {feature} at {percentage}%")
            else:
                print(f"  ❌ Failed to update {feature}")

def post_deployment_verification():
    """Verify deployment success"""
    print("\n🔍 Post-Deployment Verification...")
    
    verifications = [
        {
            "name": "Health Check",
            "command": "curl -f https://api.example.com/health"
        },
        {
            "name": "Feature Verification",
            "command": "curl -f https://api.example.com/api/v1/features"
        },
        {
            "name": "Database Connectivity",
            "command": "curl -f https://api.example.com/api/v1/db/status"
        },
        {
            "name": "External Services",
            "command": "curl -f https://api.example.com/api/v1/external/status"
        }
    ]
    
    all_passed = True
    for check in verifications:
        result = run_command(check["command"])
        if result["success"]:
            print(f"  ✅ {check['name']} - OK")
        else:
            print(f"  ❌ {check['name']} - Failed")
            all_passed = False
    
    return all_passed

def send_deployment_notification(deployment_dir, manifest, success):
    """Send deployment notification"""
    status = "SUCCESS" if success else "FAILED"
    emoji = "✅" if success else "❌"
    
    message = f"""{emoji} Production Deployment {status}
    
Deployment ID: {manifest['deployment_id']}
Time: {manifest['timestamp']}
Features: {len(manifest['features'])}
Strategy: {manifest['rollout_strategy']}

View full report: {deployment_dir}/deployment_report.html
"""
    
    # Send to Slack
    slack_command = f"""curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
        -H 'Content-Type: application/json' \
        -d '{{"text": "{message}"}}'"""
    
    run_command(slack_command)
    
    # Send email
    email_command = f"""echo "{message}" | mail -s "Deployment {status}" team@example.com"""
    run_command(email_command)

def generate_deployment_report(deployment_dir, manifest, deployment_success, verification_success):
    """Generate final deployment report"""
    report = {
        "deployment_id": manifest["deployment_id"],
        "timestamp": datetime.now().isoformat(),
        "status": "success" if deployment_success and verification_success else "failed",
        "manifest": manifest,
        "deployment_success": deployment_success,
        "verification_success": verification_success,
        "metrics": {
            "deployment_duration": 0,
            "features_deployed": len(manifest["features"]),
            "rollout_strategy": manifest["rollout_strategy"]
        }
    }
    
    # Save JSON report
    report_path = Path(deployment_dir) / "production_deployment_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate HTML report
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Production Deployment Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: {'#d4edda' if report['status'] == 'success' else '#f8d7da'}; padding: 20px; border-radius: 5px; }}
        .status-success {{ color: green; }}
        .status-failed {{ color: red; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .feature {{ padding: 5px 10px; background: #f0f0f0; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Production Deployment Report</h1>
        <p>Deployment ID: {report['deployment_id']}</p>
        <p>Status: <span class="status-{report['status']}">{report['status'].upper()}</span></p>
        <p>Time: {report['timestamp']}</p>
    </div>
    
    <div class="section">
        <h2>Deployment Summary</h2>
        <p>Strategy: {manifest['rollout_strategy'].replace('_', ' ').title()}</p>
        <p>Features Deployed: {len(manifest['features'])}</p>
        <p>Deployment: {'✅ Success' if deployment_success else '❌ Failed'}</p>
        <p>Verification: {'✅ Success' if verification_success else '❌ Failed'}</p>
    </div>
    
    <div class="section">
        <h2>Features</h2>
        {"".join([f'<div class="feature">{feature}</div>' for feature in manifest['features']])}
    </div>
</body>
</html>
"""
    
    html_path = Path(deployment_dir) / "deployment_report.html"
    with open(html_path, 'w') as f:
        f.write(html)
    
    return report_path, html_path

def rollback_deployment():
    """Emergency rollback procedure"""
    print("\n🔄 INITIATING EMERGENCY ROLLBACK...")
    
    rollback_steps = [
        "git revert HEAD --no-edit",
        "git push origin main",
        "./deploy.sh production --emergency",
        "kubectl rollout undo deployment/production"
    ]
    
    for step in rollback_steps:
        print(f"  Executing: {step}")
        result = run_command(step)
        if result["success"]:
            print(f"    ✅ Success")
        else:
            print(f"    ❌ Failed - Manual intervention required!")
            print(f"    Error: {result['error']}")

def main(deployment_dir):
    """Main execution"""
    print("🚀 Starting Production Deployment...")
    print("=" * 50)
    
    # Load test report
    test_report = load_test_report(deployment_dir)
    
    # Check if tests passed
    if test_report["overall_status"] != "passed":
        print("\n❌ Cannot deploy to production - tests did not pass")
        print(f"Test recommendation: {test_report['recommendation']}")
        return 1
    
    # Load staging configuration
    staging_config = load_staging_config(deployment_dir)
    
    # Run pre-deployment checks
    if not pre_deployment_checks():
        print("\n❌ Pre-deployment checks failed")
        return 1
    
    # Create deployment manifest
    manifest = create_deployment_manifest(deployment_dir, staging_config)
    
    # Get user confirmation
    print("\n⚠️  PRODUCTION DEPLOYMENT CONFIRMATION")
    print(f"  Features to deploy: {len(manifest['features'])}")
    print(f"  Strategy: {manifest['rollout_strategy']}")
    confirmation = input("\n  Type 'DEPLOY' to proceed: ")
    
    if confirmation != "DEPLOY":
        print("❌ Deployment cancelled")
        return 1
    
    # Perform deployment based on strategy
    deployment_success = False
    if manifest["rollout_strategy"] == "blue_green":
        deployment_success = blue_green_deployment(manifest)
    elif manifest["rollout_strategy"] == "canary":
        deployment_success = canary_deployment(manifest)
    else:
        print(f"❌ Unknown deployment strategy: {manifest['rollout_strategy']}")
        return 1
    
    if not deployment_success:
        print("\n❌ Deployment failed - initiating rollback")
        rollback_deployment()
        return 1
    
    # Update feature flags
    update_feature_flags(manifest)
    
    # Post-deployment verification
    verification_success = post_deployment_verification()
    
    if not verification_success:
        print("\n⚠️  Post-deployment verification failed")
        rollback_confirmation = input("Rollback? (yes/no): ")
        if rollback_confirmation.lower() == "yes":
            rollback_deployment()
            return 1
    
    # Generate report
    json_report, html_report = generate_deployment_report(
        deployment_dir, manifest, deployment_success, verification_success
    )
    
    # Send notifications
    send_deployment_notification(deployment_dir, manifest, deployment_success and verification_success)
    
    # Display summary
    print("\n" + "=" * 50)
    if deployment_success and verification_success:
        print("✅ PRODUCTION DEPLOYMENT SUCCESSFUL!")
    else:
        print("⚠️  PRODUCTION DEPLOYMENT COMPLETED WITH ISSUES")
    
    print(f"\n📊 Reports:")
    print(f"  • JSON: {json_report}")
    print(f"  • HTML: {html_report}")
    
    return 0 if deployment_success and verification_success else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 production_deploy.py <deployment_dir>")
        sys.exit(1)
    
    deployment_dir = sys.argv[1]
    sys.exit(main(deployment_dir))
