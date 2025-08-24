#!/usr/bin/env python3
"""
View History Module
Browse and analyze past deployments
"""

import json
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

def load_deployment_history():
    """Load all past deployments from history"""
    history_dir = Path("deployment_memory/history")
    deployments = []
    
    if not history_dir.exists():
        return deployments
    
    for deployment_dir in sorted(history_dir.iterdir(), reverse=True):
        if deployment_dir.is_dir():
            deployment_data = {
                "id": deployment_dir.name,
                "timestamp": None,
                "status": "unknown",
                "features": 0,
                "tests_passed": False,
                "production_success": False
            }
            
            # Load production report if exists
            prod_report_path = deployment_dir / "production_deployment_report.json"
            if prod_report_path.exists():
                with open(prod_report_path, 'r') as f:
                    prod_data = json.load(f)
                    deployment_data["timestamp"] = prod_data.get("timestamp")
                    deployment_data["status"] = prod_data.get("status", "unknown")
                    deployment_data["production_success"] = prod_data.get("status") == "success"
                    deployment_data["features"] = len(prod_data.get("manifest", {}).get("features", []))
            
            # Load test report if exists
            test_report_path = deployment_dir / "test_verification_report.json"
            if test_report_path.exists():
                with open(test_report_path, 'r') as f:
                    test_data = json.load(f)
                    deployment_data["tests_passed"] = test_data.get("overall_status") == "passed"
            
            # Try to get timestamp from any report
            if not deployment_data["timestamp"]:
                for report_file in deployment_dir.glob("*.json"):
                    with open(report_file, 'r') as f:
                        data = json.load(f)
                        if "timestamp" in data:
                            deployment_data["timestamp"] = data["timestamp"]
                            break
            
            deployments.append(deployment_data)
    
    return deployments

def display_deployment_list(deployments):
    """Display list of deployments in table format"""
    if not deployments:
        print("No deployment history found.")
        return
    
    # Prepare table data
    table_data = []
    for dep in deployments[:20]:  # Show last 20 deployments
        timestamp = dep["timestamp"]
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = "Unknown"
        else:
            time_str = "Unknown"
        
        status_emoji = "✅" if dep["production_success"] else "❌"
        test_emoji = "✅" if dep["tests_passed"] else "❌"
        
        table_data.append([
            dep["id"],
            time_str,
            f"{status_emoji} {dep['status']}",
            f"{test_emoji}",
            dep["features"]
        ])
    
    headers = ["Deployment ID", "Time", "Status", "Tests", "Features"]
    print("\n📚 Deployment History (Last 20)")
    print("=" * 80)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def view_deployment_details(deployment_id):
    """View detailed information about a specific deployment"""
    deployment_dir = Path("deployment_memory/history") / deployment_id
    
    if not deployment_dir.exists():
        print(f"❌ Deployment {deployment_id} not found")
        return
    
    print(f"\n📋 Deployment Details: {deployment_id}")
    print("=" * 60)
    
    # Load and display each report
    reports = [
        ("Feature Discovery", "feature_discovery.json"),
        ("Feature Selection", "feature_selection.json"),
        ("Staging Prep", "staging_prep.json"),
        ("Test Verification", "test_verification_report.json"),
        ("Production Deploy", "production_deployment_report.json"),
        ("Learning Report", "learning_report.json")
    ]
    
    for report_name, filename in reports:
        report_path = deployment_dir / filename
        if report_path.exists():
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            print(f"\n### {report_name}")
            
            # Display key information based on report type
            if "test_verification" in filename:
                print(f"  Overall Status: {data.get('overall_status', 'unknown')}")
                print(f"  Recommendation: {data.get('recommendation', 'N/A')}")
                summary = data.get('summary', {})
                print(f"  Tests Run: {summary.get('total_tests_run', 0)}")
                print(f"  Passed: {summary.get('total_passed', 0)}")
                print(f"  Failed: {summary.get('total_failed', 0)}")
            
            elif "production_deployment" in filename:
                print(f"  Status: {data.get('status', 'unknown')}")
                manifest = data.get('manifest', {})
                print(f"  Strategy: {manifest.get('rollout_strategy', 'unknown')}")
                print(f"  Features: {len(manifest.get('features', []))}")
            
            elif "feature_selection" in filename:
                print(f"  Selected Features: {data.get('total_selected', 0)}")
                plan = data.get('deployment_plan', {})
                print(f"  Risk Level: {plan.get('estimated_risk', 'unknown')}")
                print(f"  Phases: {len(plan.get('phases', []))}")
            
            elif "learning_report" in filename:
                print(f"  Success Rate: {data.get('overall_success_rate', 'N/A')}")
                recommendations = data.get('recommendations', [])
                if recommendations:
                    print("  Recommendations:")
                    for rec in recommendations[:3]:
                        print(f"    • {rec}")

def calculate_statistics(deployments):
    """Calculate deployment statistics"""
    if not deployments:
        return None
    
    total = len(deployments)
    successful = sum(1 for d in deployments if d["production_success"])
    failed = total - successful
    
    total_features = sum(d["features"] for d in deployments)
    avg_features = total_features / total if total > 0 else 0
    
    tests_passed = sum(1 for d in deployments if d["tests_passed"])
    test_pass_rate = (tests_passed / total * 100) if total > 0 else 0
    
    return {
        "total_deployments": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "total_features": total_features,
        "avg_features": avg_features,
        "test_pass_rate": test_pass_rate
    }

def display_statistics(stats):
    """Display deployment statistics"""
    if not stats:
        print("No statistics available")
        return
    
    print("\n📊 Deployment Statistics")
    print("=" * 40)
    print(f"Total Deployments: {stats['total_deployments']}")
    print(f"Successful: {stats['successful']} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Total Features Deployed: {stats['total_features']}")
    print(f"Average Features per Deployment: {stats['avg_features']:.1f}")
    print(f"Test Pass Rate: {stats['test_pass_rate']:.1f}%")

def search_deployments(deployments, search_term):
    """Search deployments by various criteria"""
    results = []
    search_lower = search_term.lower()
    
    for dep in deployments:
        # Search by ID
        if search_lower in dep["id"].lower():
            results.append(dep)
            continue
        
        # Search by status
        if search_lower in dep["status"].lower():
            results.append(dep)
            continue
        
        # Load detailed data for deeper search
        deployment_dir = Path("deployment_memory/history") / dep["id"]
        
        # Search in features
        selection_path = deployment_dir / "feature_selection.json"
        if selection_path.exists():
            with open(selection_path, 'r') as f:
                selection_data = json.load(f)
                for feature in selection_data.get("selected_features", []):
                    feature_name = feature.get("name", feature.get("description", ""))
                    if search_lower in feature_name.lower():
                        results.append(dep)
                        break
    
    return results

def interactive_menu():
    """Interactive menu for browsing history"""
    deployments = load_deployment_history()
    
    while True:
        print("\n🎭 Claude Orchestra - Deployment History")
        print("=" * 50)
        print("1. List all deployments")
        print("2. View deployment details")
        print("3. Show statistics")
        print("4. Search deployments")
        print("5. Export history")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            display_deployment_list(deployments)
        
        elif choice == "2":
            deployment_id = input("Enter deployment ID: ").strip()
            view_deployment_details(deployment_id)
        
        elif choice == "3":
            stats = calculate_statistics(deployments)
            display_statistics(stats)
        
        elif choice == "4":
            search_term = input("Search term: ").strip()
            results = search_deployments(deployments, search_term)
            if results:
                print(f"\nFound {len(results)} matching deployments:")
                display_deployment_list(results)
            else:
                print("No matching deployments found")
        
        elif choice == "5":
            export_path = Path("deployment_history_export.json")
            with open(export_path, 'w') as f:
                json.dump(deployments, f, indent=2)
            print(f"✅ History exported to {export_path}")
        
        elif choice == "0":
            break
        
        else:
            print("Invalid option")

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) > 1:
        # Direct deployment view
        deployment_id = sys.argv[1]
        view_deployment_details(deployment_id)
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()
