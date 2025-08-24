#!/usr/bin/env python3
"""
Staging Preparation Module
Prepares selected features for staging deployment with comprehensive documentation
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def load_selection_report(deployment_dir):
    """Load the feature selection report"""
    report_path = Path(deployment_dir) / "feature_selection.json"
    with open(report_path, 'r') as f:
        return json.load(f)

def generate_test_plan(selected_features):
    """Generate a comprehensive test plan for selected features"""
    test_plan = {
        "unit_tests": [],
        "integration_tests": [],
        "smoke_tests": [],
        "performance_tests": [],
        "security_checks": []
    }
    
    for feature in selected_features:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        
        # Unit tests for all features
        test_plan["unit_tests"].append({
            "feature": feature_id,
            "test": f"Test {feature_id} functionality",
            "priority": "high" if feature.get("impact") == "high" else "medium"
        })
        
        # Integration tests for high/medium impact
        if feature.get("impact") in ["high", "medium"]:
            test_plan["integration_tests"].append({
                "feature": feature_id,
                "test": f"Test {feature_id} integration with existing systems",
                "priority": "high"
            })
        
        # Smoke tests for new modules
        if feature.get("type") == "new_module":
            test_plan["smoke_tests"].append({
                "feature": feature_id,
                "test": f"Basic functionality check for {feature_id}",
                "priority": "high"
            })
        
        # Performance tests for API changes
        if "api" in feature_id.lower() or feature.get("api_changes"):
            test_plan["performance_tests"].append({
                "feature": feature_id,
                "test": f"Load test for {feature_id}",
                "baseline": "< 200ms response time",
                "priority": "medium"
            })
        
        # Security checks for high impact features
        if feature.get("impact") == "high":
            test_plan["security_checks"].append({
                "feature": feature_id,
                "test": f"Security audit for {feature_id}",
                "priority": "high"
            })
    
    return test_plan

def create_deployment_checklist(selected_features, test_plan):
    """Create a deployment checklist"""
    checklist = {
        "pre_deployment": [
            {"task": "Backup current production database", "status": "pending", "critical": True},
            {"task": "Update environment variables", "status": "pending", "critical": True},
            {"task": "Review security configurations", "status": "pending", "critical": True},
            {"task": "Verify rollback procedure", "status": "pending", "critical": True}
        ],
        "testing": [],
        "deployment": [
            {"task": "Deploy to staging environment", "status": "pending", "critical": True},
            {"task": "Run smoke tests", "status": "pending", "critical": True},
            {"task": "Verify feature functionality", "status": "pending", "critical": True},
            {"task": "Check monitoring dashboards", "status": "pending", "critical": False}
        ],
        "post_deployment": [
            {"task": "Monitor error rates", "status": "pending", "critical": True},
            {"task": "Check performance metrics", "status": "pending", "critical": False},
            {"task": "Verify user access", "status": "pending", "critical": True},
            {"task": "Document any issues", "status": "pending", "critical": False}
        ]
    }
    
    # Add test tasks
    for test_type, tests in test_plan.items():
        for test in tests:
            checklist["testing"].append({
                "task": f"Run {test_type}: {test['test']}",
                "status": "pending",
                "critical": test.get("priority") == "high"
            })
    
    return checklist

def generate_rollback_plan(selected_features):
    """Generate a rollback plan"""
    rollback_plan = {
        "triggers": [
            "Error rate > 5%",
            "Response time > 1000ms",
            "Critical functionality failure",
            "Database corruption detected"
        ],
        "steps": [
            {
                "step": 1,
                "action": "Identify the issue",
                "command": "kubectl logs -n production --tail=100",
                "estimated_time": "1 minute"
            },
            {
                "step": 2,
                "action": "Initiate rollback",
                "command": "git revert HEAD && git push",
                "estimated_time": "2 minutes"
            },
            {
                "step": 3,
                "action": "Deploy previous version",
                "command": "./deploy.sh rollback",
                "estimated_time": "5 minutes"
            },
            {
                "step": 4,
                "action": "Verify rollback success",
                "command": "curl https://api.example.com/health",
                "estimated_time": "1 minute"
            },
            {
                "step": 5,
                "action": "Notify stakeholders",
                "command": "Send notification to Slack",
                "estimated_time": "1 minute"
            }
        ],
        "total_rollback_time": "10 minutes",
        "data_recovery": {
            "backup_location": "/backups/production/",
            "recovery_command": "pg_restore -d production /backups/production/latest.dump"
        }
    }
    
    return rollback_plan

def create_staging_config(deployment_dir, selected_features):
    """Create staging environment configuration"""
    config = {
        "environment": "staging",
        "features_enabled": [f.get("name", f.get("description")) for f in selected_features],
        "feature_flags": {},
        "monitoring": {
            "error_threshold": 0.01,  # 1% error rate
            "latency_threshold": 500,  # 500ms
            "alerts_enabled": True
        },
        "scaling": {
            "min_instances": 1,
            "max_instances": 3,
            "target_cpu": 70
        }
    }
    
    # Create feature flags for gradual rollout
    for feature in selected_features:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        config["feature_flags"][feature_id] = {
            "enabled": True,
            "rollout_percentage": 100 if feature.get("impact") == "low" else 50,
            "whitelist_users": []
        }
    
    return config

def generate_deployment_documentation(deployment_dir, selected_features, test_plan, checklist, rollback_plan):
    """Generate comprehensive deployment documentation"""
    doc_content = f"""# Deployment Documentation
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Overview
This deployment includes {len(selected_features)} features moving from development to staging.

## ✨ Features Being Deployed

"""
    
    # List features
    for i, feature in enumerate(selected_features, 1):
        feature_id = feature.get("name", feature.get("description", "unknown"))
        doc_content += f"{i}. **{feature_id}**\n"
        doc_content += f"   - Type: {feature.get('type', 'unknown')}\n"
        doc_content += f"   - Impact: {feature.get('impact', 'unknown')}\n"
        if "file" in feature:
            doc_content += f"   - File: `{feature['file']}`\n"
        doc_content += "\n"
    
    # Test plan
    doc_content += "## 🧪 Test Plan\n\n"
    
    for test_type, tests in test_plan.items():
        if tests:
            doc_content += f"### {test_type.replace('_', ' ').title()}\n"
            for test in tests:
                doc_content += f"- [ ] {test['test']}\n"
            doc_content += "\n"
    
    # Deployment checklist
    doc_content += "## ✅ Deployment Checklist\n\n"
    
    for phase, tasks in checklist.items():
        doc_content += f"### {phase.replace('_', ' ').title()}\n"
        for task in tasks:
            critical = " ⚠️" if task["critical"] else ""
            doc_content += f"- [ ] {task['task']}{critical}\n"
        doc_content += "\n"
    
    # Rollback plan
    doc_content += "## 🔄 Rollback Plan\n\n"
    doc_content += "### Triggers\n"
    for trigger in rollback_plan["triggers"]:
        doc_content += f"- {trigger}\n"
    doc_content += "\n### Rollback Steps\n"
    for step in rollback_plan["steps"]:
        doc_content += f"{step['step']}. **{step['action']}** ({step['estimated_time']})\n"
        doc_content += f"   ```bash\n   {step['command']}\n   ```\n"
    doc_content += f"\n**Total Rollback Time:** {rollback_plan['total_rollback_time']}\n"
    
    # Save documentation
    doc_path = Path(deployment_dir) / "deployment_documentation.md"
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    return doc_path

def create_staging_scripts(deployment_dir):
    """Create helper scripts for staging deployment"""
    
    # Create test script
    test_script = """#!/bin/bash
# Staging Test Script

echo "🧪 Running staging tests..."

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit/

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration/

# Run smoke tests
echo "Running smoke tests..."
curl -f http://staging.example.com/health || exit 1

echo "✅ All tests passed!"
"""
    
    test_script_path = Path(deployment_dir) / "run_staging_tests.sh"
    with open(test_script_path, 'w') as f:
        f.write(test_script)
    os.chmod(test_script_path, 0o755)
    
    # Create deployment script
    deploy_script = """#!/bin/bash
# Staging Deployment Script

echo "🚀 Deploying to staging..."

# Set staging environment
export ENVIRONMENT=staging

# Deploy
git push staging main:main

# Wait for deployment
sleep 30

# Verify deployment
curl -f http://staging.example.com/health || exit 1

echo "✅ Deployment successful!"
"""
    
    deploy_script_path = Path(deployment_dir) / "deploy_to_staging.sh"
    with open(deploy_script_path, 'w') as f:
        f.write(deploy_script)
    os.chmod(deploy_script_path, 0o755)

def main(deployment_dir):
    """Main execution"""
    print("🔧 Preparing for staging deployment...")
    
    # Load feature selection
    selection_report = load_selection_report(deployment_dir)
    selected_features = selection_report["selected_features"]
    
    if not selected_features:
        print("⚠️  No features selected for staging")
        return 1
    
    # Generate test plan
    print("\n📝 Generating test plan...")
    test_plan = generate_test_plan(selected_features)
    
    # Create deployment checklist
    print("✅ Creating deployment checklist...")
    checklist = create_deployment_checklist(selected_features, test_plan)
    
    # Generate rollback plan
    print("🔄 Generating rollback plan...")
    rollback_plan = generate_rollback_plan(selected_features)
    
    # Create staging configuration
    print("⚙️  Creating staging configuration...")
    staging_config = create_staging_config(deployment_dir, selected_features)
    
    # Save staging configuration
    config_path = Path(deployment_dir) / "staging_config.json"
    with open(config_path, 'w') as f:
        json.dump(staging_config, f, indent=2)
    
    # Generate documentation
    print("📚 Generating deployment documentation...")
    doc_path = generate_deployment_documentation(
        deployment_dir, selected_features, test_plan, checklist, rollback_plan
    )
    
    # Create helper scripts
    print("📜 Creating deployment scripts...")
    create_staging_scripts(deployment_dir)
    
    # Save complete staging prep report
    staging_prep_report = {
        "timestamp": datetime.now().isoformat(),
        "test_plan": test_plan,
        "checklist": checklist,
        "rollback_plan": rollback_plan,
        "staging_config": staging_config,
        "documentation_path": str(doc_path)
    }
    
    report_path = Path(deployment_dir) / "staging_prep.json"
    with open(report_path, 'w') as f:
        json.dump(staging_prep_report, f, indent=2)
    
    # Display summary
    print("\n✅ Staging Preparation Complete!")
    print("=" * 50)
    print(f"\n📋 Test Cases Generated: {sum(len(tests) for tests in test_plan.values())}")
    print(f"✅ Checklist Items: {sum(len(tasks) for tasks in checklist.values())}")
    print(f"🔄 Rollback Time: {rollback_plan['total_rollback_time']}")
    print(f"\n📄 Documentation: {doc_path}")
    print(f"📜 Test Script: {deployment_dir}/run_staging_tests.sh")
    print(f"🚀 Deploy Script: {deployment_dir}/deploy_to_staging.sh")
    
    print("\n🎯 Next Steps:")
    print("1. Review the deployment documentation")
    print("2. Run staging tests: ./run_staging_tests.sh")
    print("3. Deploy to staging: ./deploy_to_staging.sh")
    print("4. Verify staging deployment")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 staging_prep.py <deployment_dir>")
        sys.exit(1)
    
    deployment_dir = sys.argv[1]
    sys.exit(main(deployment_dir))
