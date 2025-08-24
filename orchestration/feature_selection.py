#!/usr/bin/env python3
"""
Feature Selection Module
Interactive feature selection with Claude's intelligence
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_feature_discovery(deployment_dir):
    """Load the feature discovery report"""
    report_path = Path(deployment_dir) / "feature_discovery.json"
    with open(report_path, 'r') as f:
        return json.load(f)

def load_deployment_history():
    """Load past deployment patterns for intelligent suggestions"""
    history_path = Path("deployment_memory/patterns/deployment_patterns.json")
    if history_path.exists():
        with open(history_path, 'r') as f:
            return json.load(f)
    return {
        "successful_patterns": [],
        "failure_patterns": [],
        "optimization_opportunities": []
    }

def analyze_feature_dependencies(features):
    """Analyze dependencies between features"""
    dependencies = {}
    
    for feature in features:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        dependencies[feature_id] = {
            "requires": [],
            "blocks": [],
            "related": []
        }
        
        # Check for file dependencies
        if "file" in feature:
            file_path = feature["file"]
            
            # Check if this feature depends on others
            for other in features:
                if other != feature:
                    other_id = other.get("name", other.get("description", "unknown"))
                    if "file" in other:
                        # Simple dependency check based on file paths
                        if Path(file_path).parent == Path(other["file"]).parent:
                            dependencies[feature_id]["related"].append(other_id)
    
    return dependencies

def calculate_deployment_score(feature, history):
    """Calculate a deployment score based on past patterns"""
    score = 50  # Base score
    
    # Adjust based on impact
    if feature.get("impact") == "low":
        score += 20
    elif feature.get("impact") == "medium":
        score += 10
    elif feature.get("impact") == "high":
        score -= 10
    
    # Adjust based on type
    if feature.get("type") == "bug_fix":
        score += 30  # Bug fixes should generally be deployed
    elif feature.get("type") == "new_module":
        score += 15
    
    # Check against successful patterns
    for pattern in history.get("successful_patterns", []):
        if feature.get("type") == pattern.get("type"):
            score += 10
    
    # Check against failure patterns
    for pattern in history.get("failure_patterns", []):
        if feature.get("type") == pattern.get("type"):
            score -= 15
    
    return min(100, max(0, score))

def generate_recommendations(features, dependencies, history):
    """Generate intelligent recommendations for feature selection"""
    recommendations = {
        "must_include": [],
        "recommended": [],
        "optional": [],
        "not_recommended": [],
        "rationale": {}
    }
    
    for feature in features:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        score = calculate_deployment_score(feature, history)
        
        # Categorize based on score and type
        if feature.get("type") == "bug_fix" or score >= 80:
            recommendations["must_include"].append(feature_id)
            recommendations["rationale"][feature_id] = "Critical bug fix or high-confidence feature"
        elif score >= 60:
            recommendations["recommended"].append(feature_id)
            recommendations["rationale"][feature_id] = "Good candidate for deployment"
        elif score >= 40:
            recommendations["optional"].append(feature_id)
            recommendations["rationale"][feature_id] = "Can be included if needed"
        else:
            recommendations["not_recommended"].append(feature_id)
            recommendations["rationale"][feature_id] = "Higher risk or incomplete feature"
    
    return recommendations

def interactive_selection(features, recommendations, dependencies):
    """Interactive feature selection process"""
    selected_features = []
    
    print("\n🎯 Feature Selection Assistant")
    print("=" * 50)
    
    # Display recommendations
    print("\n📋 AI Recommendations:")
    
    if recommendations["must_include"]:
        print("\n✅ Must Include:")
        for feature_id in recommendations["must_include"]:
            print(f"  • {feature_id}")
            print(f"    Reason: {recommendations['rationale'][feature_id]}")
    
    if recommendations["recommended"]:
        print("\n👍 Recommended:")
        for feature_id in recommendations["recommended"]:
            print(f"  • {feature_id}")
            print(f"    Reason: {recommendations['rationale'][feature_id]}")
    
    if recommendations["optional"]:
        print("\n🤔 Optional:")
        for feature_id in recommendations["optional"]:
            print(f"  • {feature_id}")
    
    if recommendations["not_recommended"]:
        print("\n⚠️  Not Recommended:")
        for feature_id in recommendations["not_recommended"]:
            print(f"  • {feature_id}")
            print(f"    Reason: {recommendations['rationale'][feature_id]}")
    
    # Quick selection options
    print("\n🚀 Quick Actions:")
    print("1. Deploy all recommended features")
    print("2. Deploy only critical fixes")
    print("3. Custom selection")
    print("4. Skip selection (use recommendations)")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        # Include must_include and recommended
        for feature in features:
            feature_id = feature.get("name", feature.get("description", "unknown"))
            if feature_id in recommendations["must_include"] or \
               feature_id in recommendations["recommended"]:
                selected_features.append(feature)
    
    elif choice == "2":
        # Only critical fixes
        for feature in features:
            if feature.get("type") == "bug_fix":
                selected_features.append(feature)
    
    elif choice == "3":
        # Custom selection
        print("\n📝 Custom Feature Selection")
        for i, feature in enumerate(features, 1):
            feature_id = feature.get("name", feature.get("description", "unknown"))
            impact = feature.get("impact", "unknown")
            print(f"\n{i}. {feature_id}")
            print(f"   Impact: {impact}")
            print(f"   Type: {feature.get('type', 'unknown')}")
            
            # Show recommendation
            for category in ["must_include", "recommended", "optional", "not_recommended"]:
                if feature_id in recommendations[category]:
                    print(f"   Recommendation: {category.replace('_', ' ').title()}")
                    break
            
            include = input("   Include? (y/n/q to quit): ").strip().lower()
            if include == 'q':
                break
            elif include == 'y':
                selected_features.append(feature)
    
    else:
        # Use AI recommendations
        for feature in features:
            feature_id = feature.get("name", feature.get("description", "unknown"))
            if feature_id in recommendations["must_include"] or \
               feature_id in recommendations["recommended"]:
                selected_features.append(feature)
    
    return selected_features

def generate_selection_report(deployment_dir, selected_features, recommendations, dependencies):
    """Generate a feature selection report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "selected_features": selected_features,
        "total_selected": len(selected_features),
        "recommendations": recommendations,
        "dependencies": dependencies,
        "deployment_plan": {
            "phases": [],
            "estimated_risk": "low",
            "rollback_strategy": "git revert to previous commit"
        }
    }
    
    # Calculate deployment phases
    high_impact = [f for f in selected_features if f.get("impact") == "high"]
    medium_impact = [f for f in selected_features if f.get("impact") == "medium"]
    low_impact = [f for f in selected_features if f.get("impact") == "low"]
    
    if low_impact:
        report["deployment_plan"]["phases"].append({
            "phase": 1,
            "description": "Deploy low-impact features",
            "features": low_impact
        })
    
    if medium_impact:
        report["deployment_plan"]["phases"].append({
            "phase": 2,
            "description": "Deploy medium-impact features",
            "features": medium_impact
        })
    
    if high_impact:
        report["deployment_plan"]["phases"].append({
            "phase": 3,
            "description": "Deploy high-impact features",
            "features": high_impact
        })
        report["deployment_plan"]["estimated_risk"] = "medium"
    
    # Save report
    report_path = Path(deployment_dir) / "feature_selection.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def display_selection_summary(report):
    """Display the selection summary"""
    print("\n✅ Feature Selection Complete!")
    print("=" * 50)
    
    print(f"\n📦 Selected Features: {report['total_selected']}")
    
    for feature in report["selected_features"][:5]:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        print(f"  • {feature_id} ({feature.get('impact', 'unknown')} impact)")
    
    if len(report["selected_features"]) > 5:
        print(f"  ... and {len(report['selected_features']) - 5} more")
    
    print(f"\n📈 Deployment Plan:")
    for phase in report["deployment_plan"]["phases"]:
        print(f"  Phase {phase['phase']}: {phase['description']}")
        print(f"    • {len(phase['features'])} features")
    
    print(f"\n⚠️  Estimated Risk: {report['deployment_plan']['estimated_risk'].upper()}")
    print(f"🔄 Rollback Strategy: {report['deployment_plan']['rollback_strategy']}")

def main(deployment_dir):
    """Main execution"""
    print("🎯 Starting feature selection process...")
    
    # Load feature discovery
    discovery = load_feature_discovery(deployment_dir)
    features = discovery["features"]
    
    if not features:
        print("⚠️  No features found to select")
        return 1
    
    # Load deployment history
    history = load_deployment_history()
    
    # Analyze dependencies
    dependencies = analyze_feature_dependencies(features)
    
    # Generate recommendations
    recommendations = generate_recommendations(features, dependencies, history)
    
    # Interactive selection
    selected_features = interactive_selection(features, recommendations, dependencies)
    
    if not selected_features:
        print("⚠️  No features selected for deployment")
        return 1
    
    # Generate report
    report = generate_selection_report(deployment_dir, selected_features, recommendations, dependencies)
    
    # Display summary
    display_selection_summary(report)
    
    print(f"\n📄 Selection report saved to: {deployment_dir}/feature_selection.json")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 feature_selection.py <deployment_dir>")
        sys.exit(1)
    
    deployment_dir = sys.argv[1]
    sys.exit(main(deployment_dir))
