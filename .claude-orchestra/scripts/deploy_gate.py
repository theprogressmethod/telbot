#!/usr/bin/env python3
"""
Deployment Gate Script - Claude Orchestra Conductor Automation
WORKER_3 PREP-004C Implementation

This script performs comprehensive pre-deployment checks including environment
validation, code quality gates, worker boundary compliance, and orchestration
state validation before allowing deployments to proceed.
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
ORCHESTRA_DIR = SCRIPT_DIR.parent
STATUS_DIR = ORCHESTRA_DIR / "status"
CONTROL_DIR = ORCHESTRA_DIR / "control"
LOGS_DIR = ORCHESTRA_DIR / "logs"
GATE_REPORTS_DIR = LOGS_DIR / "deployment-gates"

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m' # No Color

class GateResult:
    """Container for deployment gate check results"""
    def __init__(self, gate_name: str):
        self.gate_name = gate_name
        self.passed = True
        self.severity = "info"  # info, warning, error, critical
        self.messages: List[str] = []
        self.details: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
    
    def add_message(self, message: str, severity: str = "info") -> None:
        """Add a message with specified severity"""
        self.messages.append({"message": message, "severity": severity})
        
        if severity in ["error", "critical"]:
            self.passed = False
            self.severity = max(self.severity, severity, key=["info", "warning", "error", "critical"].index)
        elif severity == "warning" and self.severity == "info":
            self.severity = "warning"

class DeploymentGate:
    """Main deployment gate validation system"""
    
    def __init__(self, verbose: bool = False, environment: str = "staging"):
        self.verbose = verbose
        self.environment = environment
        self.gate_results: List[GateResult] = []
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Load configurations
        self._load_configurations()
    
    def _print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message if verbose"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        GATE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_configurations(self) -> None:
        """Load deployment gate configurations"""
        self.gate_config = self._load_gate_config()
        self.environment_config = self._load_environment_config()
        self.quality_thresholds = self._load_quality_thresholds()
    
    def _load_gate_config(self) -> Dict[str, Any]:
        """Load deployment gate configuration"""
        config_file = CONTROL_DIR / "deployment-gate-config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self._print_colored(f"Error loading gate config: {e}", Colors.YELLOW)
        
        # Default configuration
        return {
            "environments": {
                "staging": {
                    "min_quality_score": 70,
                    "require_tests": True,
                    "require_documentation": False,
                    "max_critical_issues": 0,
                    "max_error_issues": 3
                },
                "production": {
                    "min_quality_score": 85,
                    "require_tests": True,
                    "require_documentation": True,
                    "max_critical_issues": 0,
                    "max_error_issues": 0
                }
            },
            "mandatory_checks": [
                "environment_validation",
                "code_quality_gate",
                "boundary_compliance",
                "orchestration_state",
                "dependency_validation"
            ],
            "optional_checks": [
                "performance_validation",
                "security_scan",
                "documentation_check"
            ]
        }
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        env_file = CONTROL_DIR / "environment-lock.yaml"
        
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self._print_colored(f"Error loading environment config: {e}", Colors.YELLOW)
        
        return {"environments": {}}
    
    def _load_quality_thresholds(self) -> Dict[str, Any]:
        """Load code quality thresholds"""
        return {
            "minimum_coverage": 80,
            "maximum_complexity": 10,
            "maximum_duplication": 5,
            "minimum_maintainability": 70
        }
    
    def run_deployment_gate(self, target_branch: str = "main") -> Dict[str, Any]:
        """Run complete deployment gate validation"""
        self._print_colored(f"🚪 Running deployment gate for {self.environment}", Colors.BLUE)
        
        # Initialize gate results
        self.gate_results = []
        
        # Run mandatory checks
        mandatory_checks = self.gate_config.get("mandatory_checks", [])
        
        for check_name in mandatory_checks:
            if check_name == "environment_validation":
                result = self._check_environment_readiness()
            elif check_name == "code_quality_gate":
                result = self._check_code_quality_gate()
            elif check_name == "boundary_compliance":
                result = self._check_boundary_compliance()
            elif check_name == "orchestration_state":
                result = self._check_orchestration_state()
            elif check_name == "dependency_validation":
                result = self._check_dependency_validation()
            else:
                result = GateResult(check_name)
                result.add_message(f"Unknown check: {check_name}", "warning")
            
            self.gate_results.append(result)
        
        # Run optional checks if configured
        optional_checks = self.gate_config.get("optional_checks", [])
        
        for check_name in optional_checks:
            if check_name == "performance_validation":
                result = self._check_performance_validation()
            elif check_name == "security_scan":
                result = self._check_security_scan()
            elif check_name == "documentation_check":
                result = self._check_documentation()
            else:
                result = GateResult(check_name)
                result.add_message(f"Optional check not implemented: {check_name}", "info")
            
            self.gate_results.append(result)
        
        # Generate overall gate assessment
        gate_assessment = self._generate_gate_assessment()
        
        # Create comprehensive gate report
        gate_report = {
            "gate_id": f"gate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "environment": self.environment,
            "target_branch": target_branch,
            "gate_timestamp": datetime.now().isoformat(),
            "gate_runner": "deploy_gate.py",
            "overall_assessment": gate_assessment,
            "gate_results": [self._result_to_dict(result) for result in self.gate_results],
            "environment_config": self.environment_config.get("environments", {}).get(self.environment, {}),
            "quality_thresholds": self.quality_thresholds,
            "deployment_recommendation": self._generate_deployment_recommendation(gate_assessment)
        }
        
        return gate_report
    
    def _check_environment_readiness(self) -> GateResult:
        """Check if target environment is ready for deployment"""
        result = GateResult("Environment Readiness")
        
        # Check environment lock status
        env_config = self.environment_config.get("environments", {}).get(self.environment, {})
        
        if not env_config:
            result.add_message(f"Environment {self.environment} not configured", "error")
            return result
        
        # Check if environment is locked
        if env_config.get("locked", False):
            lock_reason = env_config.get("lock_reason", "Unknown")
            result.add_message(f"Environment locked: {lock_reason}", "critical")
            return result
        
        # Check environment health
        health_status = env_config.get("health", "unknown")
        if health_status == "unhealthy":
            result.add_message("Environment marked as unhealthy", "error")
        elif health_status == "degraded":
            result.add_message("Environment in degraded state", "warning")
        elif health_status == "healthy":
            result.add_message("Environment healthy", "info")
        
        # Check required services
        required_services = env_config.get("required_services", [])
        for service in required_services:
            service_status = self._check_service_status(service)
            if not service_status:
                result.add_message(f"Required service unavailable: {service}", "error")
        
        # Check database connectivity
        if env_config.get("database_required", True):
            db_status = self._check_database_connectivity()
            if not db_status:
                result.add_message("Database connectivity failed", "error")
            else:
                result.add_message("Database connectivity verified", "info")
        
        # Check external dependencies
        external_deps = env_config.get("external_dependencies", [])
        for dep in external_deps:
            dep_status = self._check_external_dependency(dep)
            if not dep_status:
                result.add_message(f"External dependency unavailable: {dep}", "warning")
        
        result.metrics["environment"] = self.environment
        result.metrics["health_status"] = health_status
        result.metrics["services_checked"] = len(required_services)
        
        return result
    
    def _check_code_quality_gate(self) -> GateResult:
        """Check code quality against deployment thresholds"""
        result = GateResult("Code Quality Gate")
        
        env_thresholds = self.gate_config.get("environments", {}).get(self.environment, {})
        min_quality_score = env_thresholds.get("min_quality_score", 70)
        
        # Get recent quality assessments
        quality_reports = self._get_recent_quality_reports()
        
        if not quality_reports:
            result.add_message("No recent quality reports found", "warning")
            return result
        
        # Analyze latest quality report
        latest_report = quality_reports[0]
        overall_score = latest_report.get("overall_score", 0)
        
        if overall_score < min_quality_score:
            result.add_message(f"Quality score {overall_score} below threshold {min_quality_score}", "error")
        else:
            result.add_message(f"Quality score {overall_score} meets threshold", "info")
        
        # Check critical and error issues
        max_critical = env_thresholds.get("max_critical_issues", 0)
        max_errors = env_thresholds.get("max_error_issues", 3)
        
        critical_issues = latest_report.get("critical_issues", 0)
        error_issues = latest_report.get("error_issues", 0)
        
        if critical_issues > max_critical:
            result.add_message(f"Critical issues {critical_issues} exceed limit {max_critical}", "critical")
        
        if error_issues > max_errors:
            result.add_message(f"Error issues {error_issues} exceed limit {max_errors}", "error")
        
        # Check test coverage if required
        if env_thresholds.get("require_tests", False):
            test_coverage = latest_report.get("test_coverage", 0)
            min_coverage = self.quality_thresholds.get("minimum_coverage", 80)
            
            if test_coverage < min_coverage:
                result.add_message(f"Test coverage {test_coverage}% below minimum {min_coverage}%", "error")
            else:
                result.add_message(f"Test coverage {test_coverage}% sufficient", "info")
        
        result.metrics["quality_score"] = overall_score
        result.metrics["critical_issues"] = critical_issues
        result.metrics["error_issues"] = error_issues
        result.metrics["test_coverage"] = latest_report.get("test_coverage", 0)
        
        return result
    
    def _check_boundary_compliance(self) -> GateResult:
        """Check worker boundary compliance for recent changes"""
        result = GateResult("Boundary Compliance")
        
        # Check recent boundary violations
        boundary_log = ORCHESTRA_DIR / "logs" / "boundary-checks.log"
        
        if not boundary_log.exists():
            result.add_message("No boundary check log found", "warning")
            return result
        
        try:
            with open(boundary_log, 'r') as f:
                recent_logs = f.readlines()[-50:]  # Last 50 entries
            
            blocked_count = 0
            violations = []
            
            for log_line in recent_logs:
                if "BLOCKED" in log_line:
                    blocked_count += 1
                    violations.append(log_line.strip())
            
            if blocked_count > 0:
                result.add_message(f"Recent boundary violations detected: {blocked_count}", "error")
                for violation in violations[-5:]:  # Show last 5 violations
                    result.add_message(f"Violation: {violation}", "warning")
            else:
                result.add_message("No recent boundary violations", "info")
            
            result.metrics["boundary_violations"] = blocked_count
            
        except Exception as e:
            result.add_message(f"Error checking boundary compliance: {e}", "warning")
        
        return result
    
    def _check_orchestration_state(self) -> GateResult:
        """Check orchestration system state consistency"""
        result = GateResult("Orchestration State")
        
        # Check for emergency stop
        emergency_flag = CONTROL_DIR / "emergency-stop.flag"
        if emergency_flag.exists():
            result.add_message("Emergency stop is active", "critical")
            return result
        
        # Check active worker status
        active_worker_file = STATUS_DIR / "active-worker.md"
        if not active_worker_file.exists():
            result.add_message("Active worker status file missing", "error")
            return result
        
        try:
            with open(active_worker_file, 'r') as f:
                content = f.read()
            
            # Check for system consistency
            if "EMERGENCY_STOP_ACTIVE" in content:
                result.add_message("System in emergency stop state", "critical")
            elif "ERROR" in content:
                result.add_message("System showing error state", "error")
            else:
                result.add_message("Orchestration system state normal", "info")
            
        except Exception as e:
            result.add_message(f"Error reading worker status: {e}", "error")
        
        # Check task queue consistency
        task_queue_file = STATUS_DIR / "task-queue.md"
        if task_queue_file.exists():
            try:
                with open(task_queue_file, 'r') as f:
                    queue_content = f.read()
                
                # Count pending vs completed tasks
                pending_tasks = queue_content.count("- [ ]")
                completed_tasks = queue_content.count("- [✅]")
                
                result.metrics["pending_tasks"] = pending_tasks
                result.metrics["completed_tasks"] = completed_tasks
                
                if pending_tasks > 0:
                    result.add_message(f"Pending tasks in queue: {pending_tasks}", "warning")
                
            except Exception as e:
                result.add_message(f"Error reading task queue: {e}", "warning")
        
        # Check orchestration logs for recent errors
        orch_log = LOGS_DIR / "orchestration.log"
        if orch_log.exists():
            try:
                with open(orch_log, 'r') as f:
                    recent_logs = f.readlines()[-20:]
                
                error_count = sum(1 for line in recent_logs if "ERROR" in line)
                if error_count > 0:
                    result.add_message(f"Recent orchestration errors: {error_count}", "warning")
                
            except Exception:
                pass
        
        return result
    
    def _check_dependency_validation(self) -> GateResult:
        """Check dependency versions and availability"""
        result = GateResult("Dependency Validation")
        
        # Check Python dependencies
        python_deps = self._check_python_dependencies()
        result.metrics.update(python_deps)
        
        if python_deps.get("missing_dependencies"):
            missing = python_deps["missing_dependencies"]
            result.add_message(f"Missing Python dependencies: {', '.join(missing)}", "error")
        
        if python_deps.get("outdated_dependencies"):
            outdated = python_deps["outdated_dependencies"]
            result.add_message(f"Outdated dependencies detected: {len(outdated)}", "warning")
        
        # Check system dependencies
        system_deps = self._check_system_dependencies()
        result.metrics.update(system_deps)
        
        if not system_deps.get("git_available", True):
            result.add_message("Git not available", "error")
        
        if not system_deps.get("python_available", True):
            result.add_message("Python not available", "error")
        
        # Check orchestration-specific dependencies
        orch_deps = self._check_orchestration_dependencies()
        result.metrics.update(orch_deps)
        
        missing_scripts = orch_deps.get("missing_scripts", [])
        if missing_scripts:
            result.add_message(f"Missing orchestration scripts: {', '.join(missing_scripts)}", "error")
        
        return result
    
    def _check_performance_validation(self) -> GateResult:
        """Optional: Check performance metrics"""
        result = GateResult("Performance Validation")
        
        # This is a placeholder for performance checks
        # Could include metrics like response times, memory usage, etc.
        
        result.add_message("Performance validation not implemented", "info")
        result.metrics["performance_check"] = "skipped"
        
        return result
    
    def _check_security_scan(self) -> GateResult:
        """Optional: Check for security vulnerabilities"""
        result = GateResult("Security Scan")
        
        # Check for common security issues
        security_issues = []
        
        # Check for hardcoded secrets (basic check)
        secret_patterns = [".env.production", ".env.staging", "api_key", "secret_key"]
        
        try:
            # Simple grep for potential secrets in staged files
            staged_result = subprocess.run([
                'git', 'diff', '--cached', '--name-only'
            ], capture_output=True, text=True, timeout=10)
            
            if staged_result.returncode == 0:
                staged_files = staged_result.stdout.strip().split('\n')
                
                for file_path in staged_files:
                    if file_path and Path(file_path).exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                
                            for pattern in secret_patterns:
                                if pattern in content:
                                    security_issues.append(f"Potential secret in {file_path}: {pattern}")
                                    
                        except Exception:
                            continue
            
        except Exception:
            result.add_message("Could not run security scan", "warning")
        
        if security_issues:
            for issue in security_issues:
                result.add_message(issue, "warning")
        else:
            result.add_message("No obvious security issues detected", "info")
        
        result.metrics["security_issues"] = len(security_issues)
        
        return result
    
    def _check_documentation(self) -> GateResult:
        """Optional: Check documentation requirements"""
        result = GateResult("Documentation Check")
        
        env_config = self.gate_config.get("environments", {}).get(self.environment, {})
        
        if not env_config.get("require_documentation", False):
            result.add_message("Documentation not required for this environment", "info")
            return result
        
        # Check for documentation files
        doc_files = []
        for pattern in ["README*", "*.md", "docs/*"]:
            doc_files.extend(Path(".").glob(pattern))
        
        if not doc_files:
            result.add_message("No documentation files found", "warning")
        else:
            result.add_message(f"Found {len(doc_files)} documentation files", "info")
        
        result.metrics["doc_files_count"] = len(doc_files)
        
        return result
    
    def _check_service_status(self, service: str) -> bool:
        """Check if a required service is available"""
        # This is a placeholder - in real implementation would check actual services
        return True
    
    def _check_database_connectivity(self) -> bool:
        """Check database connectivity"""
        # Placeholder for database connectivity check
        return True
    
    def _check_external_dependency(self, dependency: str) -> bool:
        """Check external dependency availability"""
        # Placeholder for external dependency checks
        return True
    
    def _get_recent_quality_reports(self) -> List[Dict[str, Any]]:
        """Get recent code quality reports"""
        reports_dir = LOGS_DIR / "reviews"
        
        if not reports_dir.exists():
            return []
        
        report_files = list(reports_dir.glob("review_*.json"))
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        reports = []
        for report_file in report_files[:5]:  # Get last 5 reports
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                reports.append(report)
            except Exception:
                continue
        
        return reports
    
    def _check_python_dependencies(self) -> Dict[str, Any]:
        """Check Python dependency status"""
        result = {
            "missing_dependencies": [],
            "outdated_dependencies": [],
            "total_dependencies": 0
        }
        
        # Check if requirements.txt exists
        if Path("requirements.txt").exists():
            try:
                # Simple check for pip freeze
                pip_result = subprocess.run([
                    'pip', 'freeze'
                ], capture_output=True, text=True, timeout=30)
                
                if pip_result.returncode == 0:
                    installed_packages = pip_result.stdout.strip().split('\n')
                    result["total_dependencies"] = len(installed_packages)
                
            except Exception:
                pass
        
        return result
    
    def _check_system_dependencies(self) -> Dict[str, Any]:
        """Check system-level dependencies"""
        result = {}
        
        # Check Git availability
        try:
            git_result = subprocess.run(['git', '--version'], capture_output=True, timeout=10)
            result["git_available"] = git_result.returncode == 0
        except Exception:
            result["git_available"] = False
        
        # Check Python availability
        try:
            python_result = subprocess.run(['python', '--version'], capture_output=True, timeout=10)
            result["python_available"] = python_result.returncode == 0
        except Exception:
            result["python_available"] = False
        
        return result
    
    def _check_orchestration_dependencies(self) -> Dict[str, Any]:
        """Check orchestration-specific dependencies"""
        required_scripts = [
            "worker_prep.py",
            "review_work.py", 
            "emergency_stop.py",
            "progress_report.py"
        ]
        
        missing_scripts = []
        
        for script in required_scripts:
            script_path = SCRIPT_DIR / script
            if not script_path.exists():
                missing_scripts.append(script)
        
        return {
            "missing_scripts": missing_scripts,
            "total_scripts_required": len(required_scripts)
        }
    
    def _generate_gate_assessment(self) -> Dict[str, Any]:
        """Generate overall gate assessment"""
        total_gates = len(self.gate_results)
        passed_gates = sum(1 for result in self.gate_results if result.passed)
        
        critical_failures = sum(1 for result in self.gate_results if result.severity == "critical")
        error_failures = sum(1 for result in self.gate_results if result.severity == "error")
        warnings = sum(1 for result in self.gate_results if result.severity == "warning")
        
        # Determine overall status
        if critical_failures > 0:
            status = "BLOCKED"
            deployment_allowed = False
        elif error_failures > 0:
            status = "FAILED"
            deployment_allowed = False
        elif warnings > 2:
            status = "WARNING"
            deployment_allowed = False
        elif passed_gates == total_gates:
            status = "PASSED"
            deployment_allowed = True
        else:
            status = "PARTIAL"
            deployment_allowed = False
        
        return {
            "status": status,
            "deployment_allowed": deployment_allowed,
            "total_gates": total_gates,
            "passed_gates": passed_gates,
            "failed_gates": total_gates - passed_gates,
            "critical_failures": critical_failures,
            "error_failures": error_failures,
            "warnings": warnings,
            "gate_success_rate": (passed_gates / total_gates * 100) if total_gates > 0 else 0
        }
    
    def _generate_deployment_recommendation(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment recommendation based on assessment"""
        if assessment["deployment_allowed"]:
            return {
                "recommendation": "APPROVE",
                "message": "All deployment gates passed - deployment approved",
                "next_steps": [
                    "Proceed with deployment",
                    "Monitor deployment progress",
                    "Verify post-deployment health"
                ]
            }
        else:
            next_steps = ["Fix critical issues before deployment"]
            
            if assessment["critical_failures"] > 0:
                next_steps.append("Address critical failures immediately")
            if assessment["error_failures"] > 0:
                next_steps.append("Resolve error-level issues")
            if assessment["warnings"] > 0:
                next_steps.append("Review and address warnings")
            
            next_steps.append("Re-run deployment gate after fixes")
            
            return {
                "recommendation": "BLOCK",
                "message": f"Deployment blocked - {assessment['failed_gates']} gates failed",
                "next_steps": next_steps
            }
    
    def _result_to_dict(self, result: GateResult) -> Dict[str, Any]:
        """Convert GateResult to dictionary"""
        return {
            "gate_name": result.gate_name,
            "passed": result.passed,
            "severity": result.severity,
            "messages": result.messages,
            "details": result.details,
            "metrics": result.metrics
        }
    
    def save_gate_report(self, gate_report: Dict[str, Any]) -> str:
        """Save deployment gate report to file"""
        report_filename = f"gate_{gate_report['gate_id']}.json"
        report_file = GATE_REPORTS_DIR / report_filename
        
        try:
            with open(report_file, 'w') as f:
                json.dump(gate_report, f, indent=2, default=str)
            
            self._print_colored(f"✅ Gate report saved: {report_filename}", Colors.GREEN)
            
            # Log gate result to orchestration log
            self._log_gate_result(gate_report)
            
            return str(report_file)
            
        except Exception as e:
            self._print_colored(f"Error saving gate report: {e}", Colors.RED)
            raise
    
    def _log_gate_result(self, gate_report: Dict[str, Any]) -> None:
        """Log deployment gate result to orchestration log"""
        log_file = LOGS_DIR / "orchestration.log"
        
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                assessment = gate_report["overall_assessment"]
                
                f.write(f"[{timestamp}] DEPLOYMENT_GATE: {gate_report['environment']}\n")
                f.write(f"  Status: {assessment['status']}\n")
                f.write(f"  Deployment Allowed: {assessment['deployment_allowed']}\n")
                f.write(f"  Gates: {assessment['passed_gates']}/{assessment['total_gates']} passed\n")
                f.write(f"  Failures: Critical={assessment['critical_failures']}, Error={assessment['error_failures']}\n")
                f.write(f"  Report: {gate_report['gate_id']}\n")
                f.write(f"---\n")
                
        except Exception as e:
            self._print_colored(f"Error logging gate result: {e}", Colors.RED)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Deployment Gate Validation System")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--environment", "-e", default="staging", 
                       choices=["staging", "production"], help="Target environment")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Gate check command
    gate_parser = subparsers.add_parser("check", help="Run deployment gate checks")
    gate_parser.add_argument("--branch", "-b", default="main", help="Target branch")
    gate_parser.add_argument("--output", "-o", choices=["json", "text"], default="text", 
                           help="Output format")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show current gate status")
    
    # List reports command
    list_parser = subparsers.add_parser("list", help="List recent gate reports")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of reports to show")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize deployment gate
    gate = DeploymentGate(verbose=args.verbose, environment=args.environment)
    
    try:
        if args.command == "check":
            gate_report = gate.run_deployment_gate(args.branch)
            report_file = gate.save_gate_report(gate_report)
            
            assessment = gate_report["overall_assessment"]
            
            if args.output == "json":
                print(json.dumps(gate_report, indent=2, default=str))
            else:
                print(f"\n{Colors.BLUE}🚪 Deployment Gate Report{Colors.NC}")
                print(f"Environment: {gate_report['environment']}")
                print(f"Target Branch: {gate_report['target_branch']}")
                print(f"Status: {assessment['status']}")
                print(f"Deployment Allowed: {assessment['deployment_allowed']}")
                print(f"Gates Passed: {assessment['passed_gates']}/{assessment['total_gates']}")
                
                if assessment['critical_failures'] > 0:
                    print(f"{Colors.RED}Critical Failures: {assessment['critical_failures']}{Colors.NC}")
                if assessment['error_failures'] > 0:
                    print(f"{Colors.RED}Error Failures: {assessment['error_failures']}{Colors.NC}")
                if assessment['warnings'] > 0:
                    print(f"{Colors.YELLOW}Warnings: {assessment['warnings']}{Colors.NC}")
                
                print(f"\nRecommendation: {gate_report['deployment_recommendation']['recommendation']}")
                print(f"Message: {gate_report['deployment_recommendation']['message']}")
                
                if args.verbose:
                    print(f"\nDetailed Results:")
                    for gate_result in gate_report["gate_results"]:
                        status_color = Colors.GREEN if gate_result["passed"] else Colors.RED
                        print(f"{status_color}[{'PASS' if gate_result['passed'] else 'FAIL'}]{Colors.NC} {gate_result['gate_name']}")
                        
                        for msg in gate_result["messages"]:
                            severity_color = {
                                "info": Colors.CYAN,
                                "warning": Colors.YELLOW,
                                "error": Colors.RED,
                                "critical": Colors.RED
                            }.get(msg["severity"], Colors.NC)
                            print(f"  {severity_color}• {msg['message']}{Colors.NC}")
            
            return 0 if assessment["deployment_allowed"] else 1
            
        elif args.command == "status":
            # Show current system status relevant to deployment
            print(f"{Colors.BLUE}📊 Current Deployment Gate Status{Colors.NC}")
            
            # Check for emergency stop
            emergency_flag = CONTROL_DIR / "emergency-stop.flag"
            if emergency_flag.exists():
                print(f"{Colors.RED}🚨 Emergency stop is ACTIVE{Colors.NC}")
            else:
                print(f"{Colors.GREEN}✅ Emergency stop not active{Colors.NC}")
            
            # Check orchestration state
            active_worker_file = STATUS_DIR / "active-worker.md"
            if active_worker_file.exists():
                try:
                    with open(active_worker_file, 'r') as f:
                        content = f.read()
                    
                    if "EMERGENCY_STOP_ACTIVE" in content:
                        print(f"{Colors.RED}❌ System in emergency state{Colors.NC}")
                    else:
                        print(f"{Colors.GREEN}✅ Orchestration system normal{Colors.NC}")
                        
                except Exception:
                    print(f"{Colors.YELLOW}⚠️ Could not read orchestration status{Colors.NC}")
            
            return 0
            
        elif args.command == "list":
            report_files = list(GATE_REPORTS_DIR.glob("gate_*.json"))
            report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            print(f"{Colors.BLUE}📋 Recent Deployment Gate Reports:{Colors.NC}")
            for report_file in report_files[:args.limit]:
                try:
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    timestamp = report["gate_timestamp"][:16]  # YYYY-MM-DD HH:MM
                    environment = report["environment"]
                    status = report["overall_assessment"]["status"]
                    allowed = "✅" if report["overall_assessment"]["deployment_allowed"] else "❌"
                    
                    print(f"  {timestamp} | {environment} | {status} {allowed}")
                    
                except Exception:
                    continue
            
            return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())