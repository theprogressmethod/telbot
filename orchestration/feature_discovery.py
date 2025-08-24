#!/usr/bin/env python3
"""
Feature Discovery Module
Analyzes the dev environment to identify all changes and new features
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_git_command(command):
    """Execute a git command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return None

def analyze_changes():
    """Analyze all changes in the dev branch"""
    changes = {
        "new_files": [],
        "modified_files": [],
        "deleted_files": [],
        "features": [],
        "bug_fixes": [],
        "refactors": [],
        "dependencies_changed": False,
        "schema_changes": False,
        "api_changes": False
    }
    
    # Get all changed files
    diff_output = run_git_command("git diff --name-status main...HEAD")
    if diff_output:
        for line in diff_output.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    status, filename = parts[0], parts[1]
                    if status == 'A':
                        changes["new_files"].append(filename)
                    elif status == 'M':
                        changes["modified_files"].append(filename)
                    elif status == 'D':
                        changes["deleted_files"].append(filename)
    
    # Analyze commit messages for features
    commits = run_git_command("git log --oneline main...HEAD")
    if commits:
        for commit in commits.split('\n'):
            commit_lower = commit.lower()
            if 'feat:' in commit_lower or 'feature' in commit_lower:
                changes["features"].append(commit)
            elif 'fix:' in commit_lower or 'bug' in commit_lower:
                changes["bug_fixes"].append(commit)
            elif 'refactor:' in commit_lower:
                changes["refactors"].append(commit)
    
    # Check for specific change types
    all_files = changes["new_files"] + changes["modified_files"]
    for file in all_files:
        if 'requirements.txt' in file or 'package.json' in file:
            changes["dependencies_changed"] = True
        if '.sql' in file or 'schema' in file.lower():
            changes["schema_changes"] = True
        if 'api' in file.lower() or 'endpoint' in file.lower():
            changes["api_changes"] = True
    
    return changes

def extract_features_from_code(changes):
    """Extract features by analyzing code changes"""
    features = []
    
    # Analyze new files for potential features
    for file in changes["new_files"]:
        if file.endswith('.py'):
            feature = {
                "type": "new_module",
                "file": file,
                "name": Path(file).stem.replace('_', ' ').title(),
                "impact": "low",
                "testing_required": True
            }
            
            # Determine impact based on file location
            if 'core' in file or 'main' in file:
                feature["impact"] = "high"
            elif 'api' in file or 'handler' in file:
                feature["impact"] = "medium"
            
            features.append(feature)
    
    # Identify high-level features from commits
    for commit in changes["features"]:
        features.append({
            "type": "feature",
            "description": commit,
            "impact": "medium",
            "testing_required": True
        })
    
    return features

def generate_feature_report(deployment_dir, changes, features):
    """Generate a comprehensive feature discovery report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_changes": len(changes["new_files"]) + len(changes["modified_files"]),
            "new_files": len(changes["new_files"]),
            "modified_files": len(changes["modified_files"]),
            "deleted_files": len(changes["deleted_files"]),
            "features_identified": len(features),
            "bug_fixes": len(changes["bug_fixes"]),
            "requires_schema_update": changes["schema_changes"],
            "requires_dependency_update": changes["dependencies_changed"],
            "api_changes": changes["api_changes"]
        },
        "changes": changes,
        "features": features,
        "risk_assessment": {
            "overall_risk": "low",
            "risk_factors": []
        }
    }
    
    # Assess risk
    if changes["schema_changes"]:
        report["risk_assessment"]["risk_factors"].append("Database schema changes detected")
        report["risk_assessment"]["overall_risk"] = "medium"
    
    if changes["api_changes"]:
        report["risk_assessment"]["risk_factors"].append("API changes may affect clients")
        report["risk_assessment"]["overall_risk"] = "medium"
    
    if len(changes["deleted_files"]) > 5:
        report["risk_assessment"]["risk_factors"].append("Multiple files deleted")
        report["risk_assessment"]["overall_risk"] = "high"
    
    # Save report
    report_path = Path(deployment_dir) / "feature_discovery.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def display_summary(report):
    """Display a human-readable summary"""
    print("\n📊 Feature Discovery Summary")
    print("=" * 50)
    
    summary = report["summary"]
    print(f"Total Changes: {summary['total_changes']}")
    print(f"  • New files: {summary['new_files']}")
    print(f"  • Modified files: {summary['modified_files']}")
    print(f"  • Deleted files: {summary['deleted_files']}")
    
    print(f"\n✨ Features Identified: {summary['features_identified']}")
    for feature in report["features"][:5]:  # Show first 5
        if "description" in feature:
            print(f"  • {feature['description']}")
        else:
            print(f"  • {feature['name']} ({feature['file']})")
    
    if len(report["features"]) > 5:
        print(f"  ... and {len(report['features']) - 5} more")
    
    print(f"\n🐛 Bug Fixes: {summary['bug_fixes']}")
    
    print("\n⚠️  Risk Assessment:")
    print(f"  Overall Risk: {report['risk_assessment']['overall_risk'].upper()}")
    for risk in report['risk_assessment']['risk_factors']:
        print(f"  • {risk}")
    
    if summary["requires_schema_update"]:
        print("\n🗄️  Database schema changes required")
    if summary["requires_dependency_update"]:
        print("📦 Dependencies need updating")
    if summary["api_changes"]:
        print("🔌 API changes detected")

def main(deployment_dir):
    """Main execution"""
    print("🔍 Discovering features in dev environment...")
    
    # Analyze changes
    changes = analyze_changes()
    
    # Extract features
    features = extract_features_from_code(changes)
    
    # Generate report
    report = generate_feature_report(deployment_dir, changes, features)
    
    # Display summary
    display_summary(report)
    
    print(f"\n📄 Full report saved to: {deployment_dir}/feature_discovery.json")
    print("✅ Feature discovery complete!")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 feature_discovery.py <deployment_dir>")
        sys.exit(1)
    
    deployment_dir = sys.argv[1]
    sys.exit(main(deployment_dir))
