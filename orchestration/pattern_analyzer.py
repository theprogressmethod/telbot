#!/usr/bin/env python3
"""
Pattern Analyzer Module
Analyzes deployment patterns to provide insights and predictions
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

def load_patterns():
    """Load deployment patterns from memory"""
    patterns_path = Path("deployment_memory/patterns/deployment_patterns.json")
    if patterns_path.exists():
        with open(patterns_path, 'r') as f:
            return json.load(f)
    return None

def load_config():
    """Load system configuration"""
    config_path = Path("deployment_memory/config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def analyze_success_patterns(patterns):
    """Analyze patterns in successful deployments"""
    insights = {
        "common_success_factors": [],
        "optimal_feature_count": 0,
        "best_deployment_times": [],
        "success_correlations": {}
    }
    
    successful = patterns.get("successful_patterns", [])
    if not successful:
        return insights
    
    # Find common success factors
    all_factors = []
    for pattern in successful:
        all_factors.extend(pattern.get("success_factors", []))
    
    factor_counts = Counter(all_factors)
    insights["common_success_factors"] = [
        {"factor": factor, "frequency": count}
        for factor, count in factor_counts.most_common(5)
    ]
    
    # Calculate optimal feature count
    feature_counts = [p.get("feature_count", 0) for p in successful if "feature_count" in p]
    if feature_counts:
        insights["optimal_feature_count"] = int(statistics.median(feature_counts))
    
    # Analyze deployment times
    timestamps = []
    for pattern in successful:
        if "timestamp" in pattern:
            try:
                dt = datetime.fromisoformat(pattern["timestamp"])
                timestamps.append(dt)
            except:
                pass
    
    if timestamps:
        # Find best day of week
        day_counts = Counter(dt.strftime("%A") for dt in timestamps)
        insights["best_deployment_times"] = [
            {"day": day, "count": count}
            for day, count in day_counts.most_common(3)
        ]
    
    return insights

def analyze_failure_patterns(patterns):
    """Analyze patterns in failed deployments"""
    insights = {
        "common_failure_causes": [],
        "risk_indicators": [],
        "failure_prevention_tips": []
    }
    
    failures = patterns.get("failure_patterns", [])
    if not failures:
        return insights
    
    # Find common failure causes
    all_factors = []
    for pattern in failures:
        all_factors.extend(pattern.get("failure_factors", []))
    
    factor_counts = Counter(all_factors)
    insights["common_failure_causes"] = [
        {"cause": factor, "frequency": count}
        for factor, count in factor_counts.most_common(5)
    ]
    
    # Identify risk indicators
    if factor_counts:
        for cause, count in factor_counts.most_common(3):
            if "test" in cause.lower():
                insights["risk_indicators"].append("Test failures are a major risk")
                insights["failure_prevention_tips"].append("Increase test coverage before deployment")
            elif "security" in cause.lower():
                insights["risk_indicators"].append("Security issues detected")
                insights["failure_prevention_tips"].append("Run security audits before deployment")
            elif "performance" in cause.lower():
                insights["risk_indicators"].append("Performance degradation risk")
                insights["failure_prevention_tips"].append("Implement performance benchmarks")
    
    return insights

def analyze_feature_success_rates(patterns):
    """Analyze success rates for different feature types"""
    feature_analysis = {
        "high_success_features": [],
        "risky_features": [],
        "feature_recommendations": {}
    }
    
    feature_rates = patterns.get("feature_success_rates", {})
    if not feature_rates:
        return feature_analysis
    
    # Calculate success rates
    for feature_id, stats in feature_rates.items():
        total = stats.get("successes", 0) + stats.get("failures", 0)
        if total > 0:
            success_rate = stats["successes"] / total
            
            feature_info = {
                "id": feature_id,
                "type": stats.get("type", "unknown"),
                "success_rate": success_rate,
                "total_deployments": total
            }
            
            if success_rate >= 0.8:
                feature_analysis["high_success_features"].append(feature_info)
            elif success_rate < 0.5:
                feature_analysis["risky_features"].append(feature_info)
            
            # Generate recommendations
            if success_rate >= 0.8:
                feature_analysis["feature_recommendations"][feature_id] = "Safe to deploy"
            elif success_rate >= 0.6:
                feature_analysis["feature_recommendations"][feature_id] = "Deploy with caution"
            else:
                feature_analysis["feature_recommendations"][feature_id] = "Requires additional testing"
    
    # Sort by success rate
    feature_analysis["high_success_features"].sort(key=lambda x: x["success_rate"], reverse=True)
    feature_analysis["risky_features"].sort(key=lambda x: x["success_rate"])
    
    return feature_analysis

def predict_deployment_outcome(current_features, patterns):
    """Predict the outcome of a deployment based on historical patterns"""
    prediction = {
        "success_probability": 0.5,
        "risk_factors": [],
        "confidence": "low",
        "recommendations": []
    }
    
    if not patterns or not current_features:
        return prediction
    
    # Base success rate from config
    config = load_config()
    if config:
        base_success_rate = config.get("success_rate", 0.5)
    else:
        base_success_rate = 0.5
    
    prediction["success_probability"] = base_success_rate
    
    # Adjust based on feature success rates
    feature_rates = patterns.get("feature_success_rates", {})
    total_weight = 0
    weighted_sum = 0
    
    for feature in current_features:
        feature_id = feature.get("name", feature.get("description", "unknown"))
        if feature_id in feature_rates:
            stats = feature_rates[feature_id]
            total = stats.get("successes", 0) + stats.get("failures", 0)
            if total > 0:
                success_rate = stats["successes"] / total
                weighted_sum += success_rate * total
                total_weight += total
    
    if total_weight > 0:
        feature_based_probability = weighted_sum / total_weight
        # Combine with base rate
        prediction["success_probability"] = (base_success_rate + feature_based_probability) / 2
    
    # Determine confidence
    if total_weight >= 10:
        prediction["confidence"] = "high"
    elif total_weight >= 5:
        prediction["confidence"] = "medium"
    else:
        prediction["confidence"] = "low"
    
    # Identify risk factors
    if prediction["success_probability"] < 0.6:
        prediction["risk_factors"].append("Low historical success rate")
    
    if len(current_features) > 10:
        prediction["risk_factors"].append("Large number of features")
        prediction["success_probability"] *= 0.9  # Reduce probability
    
    # Generate recommendations
    if prediction["success_probability"] < 0.5:
        prediction["recommendations"].append("Consider splitting deployment into smaller phases")
        prediction["recommendations"].append("Increase testing coverage")
    elif prediction["success_probability"] < 0.7:
        prediction["recommendations"].append("Deploy during low-traffic hours")
        prediction["recommendations"].append("Have rollback plan ready")
    else:
        prediction["recommendations"].append("Deployment looks safe to proceed")
    
    return prediction

def generate_optimization_report(patterns, config):
    """Generate optimization recommendations"""
    optimizations = {
        "process_improvements": [],
        "automation_opportunities": [],
        "risk_reduction_strategies": [],
        "efficiency_gains": []
    }
    
    # Analyze deployment frequency
    if config and config.get("deployment_count", 0) > 0:
        deployments = config["deployment_count"]
        success_rate = config.get("success_rate", 0)
        
        if deployments > 10:
            if success_rate < 0.7:
                optimizations["process_improvements"].append(
                    "Success rate below 70% - review deployment process"
                )
            else:
                optimizations["process_improvements"].append(
                    "Good success rate - consider increasing deployment frequency"
                )
    
    # Check for optimization opportunities in patterns
    if patterns:
        opportunities = patterns.get("optimization_opportunities", [])
        optimizations["automation_opportunities"] = opportunities[:5]
        
        # Risk reduction based on failure patterns
        failure_patterns = patterns.get("failure_patterns", [])
        if len(failure_patterns) > 5:
            optimizations["risk_reduction_strategies"].append(
                "Implement automated rollback triggers"
            )
            optimizations["risk_reduction_strategies"].append(
                "Add more comprehensive testing"
            )
        
        # Efficiency improvements
        successful_patterns = patterns.get("successful_patterns", [])
        if successful_patterns:
            avg_feature_count = statistics.mean(
                [p.get("feature_count", 0) for p in successful_patterns[-10:] if "feature_count" in p]
            ) if successful_patterns else 0
            
            if avg_feature_count > 0:
                optimizations["efficiency_gains"].append(
                    f"Optimal batch size: {int(avg_feature_count)} features per deployment"
                )
    
    return optimizations

def display_analysis_report(patterns, config):
    """Display comprehensive pattern analysis"""
    print("\n🔬 PATTERN ANALYSIS REPORT")
    print("=" * 60)
    
    if not patterns:
        print("No patterns available for analysis")
        return
    
    # Success patterns
    success_insights = analyze_success_patterns(patterns)
    print("\n✅ Success Pattern Analysis:")
    if success_insights["common_success_factors"]:
        print("  Common Success Factors:")
        for factor in success_insights["common_success_factors"][:3]:
            print(f"    • {factor['factor']} (seen {factor['frequency']} times)")
    
    if success_insights["optimal_feature_count"]:
        print(f"  Optimal Feature Count: {success_insights['optimal_feature_count']}")
    
    # Failure patterns
    failure_insights = analyze_failure_patterns(patterns)
    if failure_insights["common_failure_causes"]:
        print("\n❌ Failure Pattern Analysis:")
        print("  Common Failure Causes:")
        for cause in failure_insights["common_failure_causes"][:3]:
            print(f"    • {cause['cause']} (seen {cause['frequency']} times)")
    
    # Feature analysis
    feature_analysis = analyze_feature_success_rates(patterns)
    if feature_analysis["high_success_features"]:
        print("\n⭐ High Success Features:")
        for feature in feature_analysis["high_success_features"][:3]:
            print(f"  • {feature['type']}: {feature['success_rate']*100:.0f}% success rate")
    
    if feature_analysis["risky_features"]:
        print("\n⚠️  Risky Features:")
        for feature in feature_analysis["risky_features"][:3]:
            print(f"  • {feature['type']}: {feature['success_rate']*100:.0f}% success rate")
    
    # Optimization report
    optimizations = generate_optimization_report(patterns, config)
    if any(optimizations.values()):
        print("\n💡 Optimization Recommendations:")
        
        for category, items in optimizations.items():
            if items:
                print(f"\n  {category.replace('_', ' ').title()}:")
                for item in items[:2]:
                    print(f"    • {item}")

def generate_trend_analysis(patterns):
    """Analyze trends over time"""
    trends = {
        "success_trend": "stable",
        "complexity_trend": "stable",
        "risk_trend": "stable",
        "recommendations": []
    }
    
    if not patterns:
        return trends
    
    successful = patterns.get("successful_patterns", [])
    failures = patterns.get("failure_patterns", [])
    
    # Analyze success trend (recent vs older)
    if len(successful) >= 10:
        recent_success = len(successful[-5:])
        older_success = len(successful[-10:-5])
        
        if recent_success > older_success * 1.2:
            trends["success_trend"] = "improving"
            trends["recommendations"].append("Success rate improving - maintain current practices")
        elif recent_success < older_success * 0.8:
            trends["success_trend"] = "declining"
            trends["recommendations"].append("Success rate declining - review recent changes")
    
    # Analyze complexity trend
    if successful:
        recent_features = [p.get("feature_count", 0) for p in successful[-5:] if "feature_count" in p]
        older_features = [p.get("feature_count", 0) for p in successful[-10:-5] if "feature_count" in p]
        
        if recent_features and older_features:
            recent_avg = statistics.mean(recent_features)
            older_avg = statistics.mean(older_features)
            
            if recent_avg > older_avg * 1.3:
                trends["complexity_trend"] = "increasing"
                trends["recommendations"].append("Deployment complexity increasing - consider breaking down")
            elif recent_avg < older_avg * 0.7:
                trends["complexity_trend"] = "decreasing"
    
    return trends

def main():
    """Main execution"""
    print("🔬 Claude Orchestra - Pattern Analyzer")
    print("=" * 60)
    
    # Load data
    patterns = load_patterns()
    config = load_config()
    
    if not patterns and not config:
        print("\n❌ No deployment data available for analysis")
        print("Run some deployments first to build pattern database")
        return 1
    
    # Display analysis
    display_analysis_report(patterns, config)
    
    # Trend analysis
    trends = generate_trend_analysis(patterns)
    print("\n📈 Trend Analysis:")
    print(f"  • Success Trend: {trends['success_trend'].upper()}")
    print(f"  • Complexity Trend: {trends['complexity_trend'].upper()}")
    print(f"  • Risk Trend: {trends['risk_trend'].upper()}")
    
    if trends["recommendations"]:
        print("\n  Trend Recommendations:")
        for rec in trends["recommendations"]:
            print(f"    • {rec}")
    
    # Save analysis report
    report = {
        "timestamp": datetime.now().isoformat(),
        "success_insights": analyze_success_patterns(patterns) if patterns else {},
        "failure_insights": analyze_failure_patterns(patterns) if patterns else {},
        "feature_analysis": analyze_feature_success_rates(patterns) if patterns else {},
        "optimizations": generate_optimization_report(patterns, config),
        "trends": trends
    }
    
    report_path = Path("deployment_memory/pattern_analysis_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full analysis saved to: {report_path}")
    
    return 0

if __name__ == "__main__":
    main()
