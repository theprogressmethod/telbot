#!/usr/bin/env python3
"""
Deployment Status Module
Real-time monitoring of active deployments
"""

import json
import time
from pathlib import Path
from datetime import datetime

def get_current_deployment():
    """Get the current active deployment if any"""
    current_dir = Path("deployment_memory/current")
    if not current_dir.exists():
        return None
    
    # Find the most recent deployment directory
    deployments = [d for d in current_dir.iterdir() if d.is_dir()]
    if not deployments:
        return None
    
    # Get the most recent one
    latest = sorted(deployments, reverse=True)[0]
    return latest

def check_deployment_stage(deployment_dir):
    """Determine which stage the deployment is in"""
    stages = {
        "feature_discovery": False,
        "feature_selection": False,
        "staging_prep": False,
        "testing": False,
        "production": False,
        "learning": False
    }
    
    # Check which files exist
    if (deployment_dir / "feature_discovery.json").exists():
        stages["feature_discovery"] = True
    
    if (deployment_dir / "feature_selection.json").exists():
        stages["feature_selection"] = True
    
    if (deployment_dir / "staging_prep.json").exists():
        stages["staging_prep"] = True
    
    if (deployment_dir / "test_verification_report.json").exists():
        stages["testing"] = True
    
    if (deployment_dir / "production_deployment_report.json").exists():
        stages["production"] = True
    
    if (deployment_dir / "learning_report.json").exists():
        stages["learning"] = True
    
    # Determine current stage
    if stages["learning"]:
        return "completed", stages
    elif stages["production"]:
        return "production_deployment", stages
    elif stages["testing"]:
        return "testing_verification", stages
    elif stages["staging_prep"]:
        return "staging_preparation", stages
    elif stages["feature_selection"]:
        return "feature_selection", stages
    elif stages["feature_discovery"]:
        return "feature_discovery", stages
    else:
        return "initializing", stages

def calculate_progress(stages):
    """Calculate deployment progress percentage"""
    total_stages = len(stages)
    completed = sum(1 for v in stages.values() if v)
    return (completed / total_stages) * 100

def display_progress_bar(percentage, width=50):
    """Display a visual progress bar"""
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.1f}%"

def get_deployment_metrics(deployment_dir):
    """Get metrics for the current deployment"""
    metrics = {
        "features_selected": 0,
        "tests_run": 0,
        "tests_passed": 0,
        "current_risk": "unknown",
        "elapsed_time": "unknown"
    }
    
    # Get feature count
    selection_path = deployment_dir / "feature_selection.json"
    if selection_path.exists():
        with open(selection_path, 'r') as f:
            data = json.load(f)
            metrics["features_selected"] = data.get("total_selected", 0)
            plan = data.get("deployment_plan", {})
            metrics["current_risk"] = plan.get("estimated_risk", "unknown")
    
    # Get test metrics
    test_path = deployment_dir / "test_verification_report.json"
    if test_path.exists():
        with open(test_path, 'r') as f:
            data = json.load(f)
            summary = data.get("summary", {})
            metrics["tests_run"] = summary.get("total_tests_run", 0)
            metrics["tests_passed"] = summary.get("total_passed", 0)
    
    # Calculate elapsed time
    discovery_path = deployment_dir / "feature_discovery.json"
    if discovery_path.exists():
        with open(discovery_path, 'r') as f:
            data = json.load(f)
            start_time = data.get("timestamp")
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    elapsed = datetime.now() - start_dt
                    hours = elapsed.seconds // 3600
                    minutes = (elapsed.seconds % 3600) // 60
                    metrics["elapsed_time"] = f"{hours}h {minutes}m"
                except:
                    pass
    
    return metrics

def get_recent_logs(deployment_dir, lines=10):
    """Get recent log entries or activities"""
    logs = []
    
    # Check each stage file and get timestamp
    stage_files = [
        ("Feature Discovery Started", "feature_discovery.json"),
        ("Features Selected", "feature_selection.json"),
        ("Staging Prepared", "staging_prep.json"),
        ("Tests Completed", "test_verification_report.json"),
        ("Production Deployed", "production_deployment_report.json"),
        ("Learning Complete", "learning_report.json")
    ]
    
    for message, filename in stage_files:
        file_path = deployment_dir / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                timestamp = data.get("timestamp")
                if timestamp:
                    logs.append({
                        "time": timestamp,
                        "message": message
                    })
    
    # Sort by timestamp
    logs.sort(key=lambda x: x["time"], reverse=True)
    
    return logs[:lines]

def display_status_dashboard(deployment_dir):
    """Display a comprehensive status dashboard"""
    deployment_id = deployment_dir.name
    current_stage, stages = check_deployment_stage(deployment_dir)
    progress = calculate_progress(stages)
    metrics = get_deployment_metrics(deployment_dir)
    logs = get_recent_logs(deployment_dir)
    
    # Clear screen for dashboard effect
    print("\033[2J\033[H")  # Clear screen and move cursor to top
    
    print("=" * 80)
    print("🎭 CLAUDE ORCHESTRA - DEPLOYMENT STATUS DASHBOARD")
    print("=" * 80)
    
    print(f"\n📦 Deployment ID: {deployment_id}")
    print(f"🎯 Current Stage: {current_stage.replace('_', ' ').title()}")
    print(f"\n📊 Progress: {display_progress_bar(progress)}")
    
    # Stage indicators
    print("\n📋 Stages:")
    stage_names = {
        "feature_discovery": "1. Feature Discovery",
        "feature_selection": "2. Feature Selection",
        "staging_prep": "3. Staging Prep",
        "testing": "4. Testing",
        "production": "5. Production",
        "learning": "6. Learning"
    }
    
    for key, name in stage_names.items():
        if stages.get(key):
            print(f"  ✅ {name}")
        elif current_stage == key.replace("_", " "):
            print(f"  ⏳ {name} (In Progress)")
        else:
            print(f"  ⭕ {name}")
    
    # Metrics
    print("\n📈 Metrics:")
    print(f"  • Features Selected: {metrics['features_selected']}")
    print(f"  • Tests Run: {metrics['tests_run']}")
    print(f"  • Tests Passed: {metrics['tests_passed']}")
    print(f"  • Risk Level: {metrics['current_risk'].upper()}")
    print(f"  • Elapsed Time: {metrics['elapsed_time']}")
    
    # Recent activity
    print("\n📜 Recent Activity:")
    if logs:
        for log in logs[:5]:
            try:
                dt = datetime.fromisoformat(log["time"])
                time_str = dt.strftime("%H:%M:%S")
                print(f"  [{time_str}] {log['message']}")
            except:
                print(f"  [--:--:--] {log['message']}")
    else:
        print("  No activity recorded yet")
    
    # Next steps
    print("\n➡️  Next Steps:")
    if current_stage == "initializing":
        print("  • Waiting for deployment to start...")
    elif current_stage == "feature_discovery":
        print("  • Analyzing code changes")
        print("  • Identifying new features")
    elif current_stage == "feature_selection":
        print("  • Select features to deploy")
        print("  • Review AI recommendations")
    elif current_stage == "staging_preparation":
        print("  • Prepare staging environment")
        print("  • Generate test plans")
    elif current_stage == "testing_verification":
        print("  • Run automated tests")
        print("  • Verify feature functionality")
    elif current_stage == "production_deployment":
        print("  • Deploy to production")
        print("  • Monitor metrics")
    elif current_stage == "completed":
        print("  • Deployment complete!")
        print("  • Review learning report")
    
    print("\n" + "=" * 80)

def monitor_deployment(deployment_dir, refresh_interval=5):
    """Continuously monitor deployment status"""
    print("Starting deployment monitor... (Press Ctrl+C to stop)")
    
    try:
        while True:
            display_status_dashboard(deployment_dir)
            
            # Check if deployment is complete
            if (deployment_dir / "learning_report.json").exists():
                print("\n✅ Deployment Complete!")
                break
            
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    """Main execution"""
    import sys
    
    # Check for current deployment
    deployment_dir = get_current_deployment()
    
    if not deployment_dir:
        print("❌ No active deployment found")
        print("\nStart a new deployment with: ./orchestrate.sh deploy")
        return 1
    
    # Check for monitor flag
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        refresh = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        monitor_deployment(deployment_dir, refresh)
    else:
        display_status_dashboard(deployment_dir)
    
    return 0

if __name__ == "__main__":
    main()
