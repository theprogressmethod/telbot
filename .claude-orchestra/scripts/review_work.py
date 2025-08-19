#!/usr/bin/env python3
"""
Work Review Script - Claude Orchestra Conductor Automation
WORKER_3 PREP-004B Implementation

This script validates worker outputs, checks boundary compliance,
analyzes code quality, and generates comprehensive review reports.
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
LOGS_DIR = ORCHESTRA_DIR / "logs"
CONTEXTS_DIR = ORCHESTRA_DIR / "contexts"
REPORTS_DIR = LOGS_DIR / "reviews"

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

class ReviewResult:
    """Container for review results"""
    def __init__(self, component: str):
        self.component = component
        self.passed = True
        self.score = 100
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []
        self.metrics: Dict[str, Any] = {}
    
    def add_issue(self, message: str, severity: str = "error") -> None:
        """Add an issue to the review"""
        if severity == "error":
            self.issues.append(message)
            self.passed = False
            self.score = max(0, self.score - 20)
        elif severity == "warning":
            self.warnings.append(message)
            self.score = max(0, self.score - 5)
    
    def add_recommendation(self, message: str) -> None:
        """Add a recommendation"""
        self.recommendations.append(message)

class WorkReviewer:
    """Main class for reviewing worker outputs"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.review_results: List[ReviewResult] = []
        
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
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_configurations(self) -> None:
        """Load review configurations and standards"""
        self.quality_standards = self._load_quality_standards()
        self.boundary_rules = self._load_boundary_rules()
    
    def _load_quality_standards(self) -> Dict[str, Any]:
        """Load code quality standards"""
        return {
            "python": {
                "max_line_length": 120,
                "max_function_length": 50,
                "max_class_length": 500,
                "required_docstrings": True,
                "required_type_hints": False,
                "max_complexity": 10
            },
            "bash": {
                "max_line_length": 120,
                "required_comments": True,
                "error_handling": True
            },
            "general": {
                "max_file_size": 10000,  # lines
                "required_headers": True,
                "consistent_style": True
            }
        }
    
    def _load_boundary_rules(self) -> Dict[str, Any]:
        """Load worker boundary rules"""
        try:
            boundaries_file = ORCHESTRA_DIR / "control" / "worker-boundaries.yaml"
            if boundaries_file.exists():
                with open(boundaries_file, 'r') as f:
                    return yaml.safe_load(f)
        except Exception:
            pass
        
        # Default boundary rules
        return {
            "WORKER_1": {
                "allowed_paths": [".claude-orchestra/control/**", "config/**", "database/**"],
                "forbidden_paths": [".env.production", ".env.staging"]
            },
            "WORKER_2": {
                "allowed_paths": [".claude-orchestra/workflows/**", "api/**", "integrations/**"],
                "forbidden_paths": [".claude-orchestra/control/**", ".env.production"]
            },
            "WORKER_3": {
                "allowed_paths": [".claude-orchestra/scripts/**", ".claude-orchestra/automation/**"],
                "forbidden_paths": [".claude-orchestra/control/**", ".env.production"]
            }
        }
    
    def review_task_completion(self, worker_id: str, task_id: str) -> Dict[str, Any]:
        """Review a completed task for quality and compliance"""
        self._print_colored(f"🔍 Reviewing {task_id} by {worker_id}", Colors.BLUE)
        
        # Load task context
        task_context = self._load_task_context(worker_id, task_id)
        
        # Perform various review checks
        boundary_result = self._review_boundary_compliance(worker_id, task_id)
        quality_result = self._review_code_quality(worker_id, task_id)
        completion_result = self._review_task_completion_criteria(worker_id, task_id, task_context)
        testing_result = self._review_testing_coverage(worker_id, task_id)
        documentation_result = self._review_documentation(worker_id, task_id)
        
        # Collect all results
        self.review_results = [
            boundary_result,
            quality_result, 
            completion_result,
            testing_result,
            documentation_result
        ]
        
        # Generate overall assessment
        overall_result = self._generate_overall_assessment()
        
        # Create comprehensive review report
        review_report = {
            "review_id": f"{worker_id}_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "worker_id": worker_id,
            "task_id": task_id,
            "review_timestamp": datetime.now().isoformat(),
            "reviewer": "review_work.py",
            "overall_assessment": overall_result,
            "detailed_results": {
                "boundary_compliance": self._result_to_dict(boundary_result),
                "code_quality": self._result_to_dict(quality_result),
                "task_completion": self._result_to_dict(completion_result),
                "testing_coverage": self._result_to_dict(testing_result),
                "documentation": self._result_to_dict(documentation_result)
            },
            "recommendations": self._compile_recommendations(),
            "next_steps": self._generate_next_steps(overall_result)
        }
        
        return review_report
    
    def _load_task_context(self, worker_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task context from file"""
        context_file = CONTEXTS_DIR / f"{worker_id}_{task_id}_context.json"
        
        if not context_file.exists():
            self._print_colored(f"⚠️ Context file not found: {context_file}", Colors.YELLOW)
            return None
        
        try:
            with open(context_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._print_colored(f"Error loading context: {e}", Colors.RED)
            return None
    
    def _review_boundary_compliance(self, worker_id: str, task_id: str) -> ReviewResult:
        """Review worker boundary compliance"""
        result = ReviewResult("Boundary Compliance")
        
        # Get recent commits by this worker for this task
        commits = self._get_worker_commits(worker_id, task_id)
        
        # Check each modified file against boundaries
        worker_boundaries = self.boundary_rules.get(worker_id, {})
        allowed_paths = worker_boundaries.get("allowed_paths", [])
        forbidden_paths = worker_boundaries.get("forbidden_paths", [])
        
        for commit in commits:
            modified_files = self._get_commit_files(commit)
            
            for file_path in modified_files:
                # Check if file is allowed
                is_allowed = self._check_path_allowed(file_path, allowed_paths)
                is_forbidden = self._check_path_forbidden(file_path, forbidden_paths)
                
                if is_forbidden:
                    result.add_issue(f"Modified forbidden file: {file_path}", "error")
                elif not is_allowed:
                    result.add_issue(f"Modified file outside boundaries: {file_path}", "warning")
        
        # Check if boundary script was consulted
        if not self._check_boundary_script_usage(worker_id, task_id):
            result.add_recommendation("Consider using boundary check script before file modifications")
        
        result.metrics["commits_reviewed"] = len(commits)
        result.metrics["files_checked"] = sum(len(self._get_commit_files(c)) for c in commits)
        
        return result
    
    def _review_code_quality(self, worker_id: str, task_id: str) -> ReviewResult:
        """Review code quality of worker outputs"""
        result = ReviewResult("Code Quality")
        
        # Get files created/modified by this worker
        created_files = self._get_worker_created_files(worker_id, task_id)
        
        for file_path in created_files:
            file_result = self._analyze_file_quality(file_path)
            
            # Merge file analysis into overall result
            result.issues.extend(file_result.get("issues", []))
            result.warnings.extend(file_result.get("warnings", []))
            result.recommendations.extend(file_result.get("recommendations", []))
            
            if file_result.get("score", 100) < 70:
                result.score = min(result.score, file_result["score"])
        
        result.metrics["files_analyzed"] = len(created_files)
        result.metrics["average_quality_score"] = result.score
        
        return result
    
    def _review_task_completion_criteria(self, worker_id: str, task_id: str, context: Optional[Dict]) -> ReviewResult:
        """Review if task completion criteria were met"""
        result = ReviewResult("Task Completion")
        
        if not context:
            result.add_issue("No task context available for verification", "error")
            return result
        
        success_criteria = context.get("success_criteria", [])
        
        if not success_criteria:
            result.add_issue("No success criteria defined in task context", "warning")
            return result
        
        # Check each success criterion
        for criterion in success_criteria:
            met = self._check_success_criterion(criterion, worker_id, task_id)
            
            if not met:
                result.add_issue(f"Success criterion not met: {criterion}", "error")
            else:
                result.metrics[f"criterion_met_{len(result.metrics)}"] = criterion
        
        completion_rate = (len(result.metrics) / len(success_criteria)) * 100
        result.score = int(completion_rate)
        result.metrics["completion_rate"] = completion_rate
        
        return result
    
    def _review_testing_coverage(self, worker_id: str, task_id: str) -> ReviewResult:
        """Review testing coverage and quality"""
        result = ReviewResult("Testing Coverage")
        
        # Look for test files created
        test_files = self._find_test_files(worker_id, task_id)
        
        if not test_files:
            result.add_issue("No test files found", "warning")
            result.score = 50
        else:
            # Analyze test quality
            for test_file in test_files:
                test_quality = self._analyze_test_file(test_file)
                
                if test_quality["test_count"] < 3:
                    result.add_issue(f"Insufficient tests in {test_file}: {test_quality['test_count']}", "warning")
                
                if not test_quality["has_assertions"]:
                    result.add_issue(f"Tests without assertions in {test_file}", "error")
        
        # Check if tests can be executed
        executable_tests = self._check_test_executability(test_files)
        result.metrics["test_files"] = len(test_files)
        result.metrics["executable_tests"] = executable_tests
        
        return result
    
    def _review_documentation(self, worker_id: str, task_id: str) -> ReviewResult:
        """Review documentation quality"""
        result = ReviewResult("Documentation")
        
        # Check for docstrings in Python files
        python_files = self._get_python_files(worker_id, task_id)
        
        total_functions = 0
        documented_functions = 0
        
        for py_file in python_files:
            file_stats = self._analyze_python_documentation(py_file)
            total_functions += file_stats["total_functions"]
            documented_functions += file_stats["documented_functions"]
        
        if total_functions > 0:
            doc_coverage = (documented_functions / total_functions) * 100
            result.score = int(doc_coverage)
            
            if doc_coverage < 80:
                result.add_issue(f"Low documentation coverage: {doc_coverage:.1f}%", "warning")
        
        # Check for README or documentation files
        doc_files = self._find_documentation_files(worker_id, task_id)
        
        if not doc_files:
            result.add_recommendation("Consider adding README or documentation files")
        
        result.metrics["doc_coverage"] = doc_coverage if total_functions > 0 else 100
        result.metrics["total_functions"] = total_functions
        result.metrics["documented_functions"] = documented_functions
        
        return result
    
    def _get_worker_commits(self, worker_id: str, task_id: str) -> List[str]:
        """Get recent commits by worker for task"""
        try:
            # Get commits containing worker ID and task ID
            result = subprocess.run([
                'git', 'log', '--oneline', '--grep', worker_id, '--grep', task_id, '--since=1 day ago'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return [line.split()[0] for line in result.stdout.strip().split('\n') if line]
            
        except Exception as e:
            self._print_colored(f"Error getting commits: {e}", Colors.YELLOW)
        
        return []
    
    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """Get files modified in a specific commit"""
        try:
            result = subprocess.run([
                'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.strip().split('\n') if line]
                
        except Exception as e:
            self._print_colored(f"Error getting commit files: {e}", Colors.YELLOW)
        
        return []
    
    def _check_path_allowed(self, file_path: str, allowed_paths: List[str]) -> bool:
        """Check if file path matches allowed patterns"""
        for pattern in allowed_paths:
            if self._path_matches_pattern(file_path, pattern):
                return True
        return False
    
    def _check_path_forbidden(self, file_path: str, forbidden_paths: List[str]) -> bool:
        """Check if file path matches forbidden patterns"""
        for pattern in forbidden_paths:
            if self._path_matches_pattern(file_path, pattern):
                return True
        return False
    
    def _path_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a glob-like pattern"""
        # Simple pattern matching - could be enhanced with fnmatch
        if pattern.endswith("/**"):
            return file_path.startswith(pattern[:-3])
        elif "*" in pattern:
            # Basic wildcard matching
            parts = pattern.split("*")
            if len(parts) == 2:
                return file_path.startswith(parts[0]) and file_path.endswith(parts[1])
        
        return file_path == pattern or file_path.startswith(pattern)
    
    def _check_boundary_script_usage(self, worker_id: str, task_id: str) -> bool:
        """Check if worker used boundary checking script"""
        # Look for boundary check usage in logs
        try:
            boundary_log = ORCHESTRA_DIR / "logs" / "boundary-checks.log"
            if boundary_log.exists():
                with open(boundary_log, 'r') as f:
                    content = f.read()
                    return worker_id in content and task_id in content
        except Exception:
            pass
        
        return False
    
    def _get_worker_created_files(self, worker_id: str, task_id: str) -> List[str]:
        """Get files created/modified by worker for this task"""
        commits = self._get_worker_commits(worker_id, task_id)
        all_files = set()
        
        for commit in commits:
            files = self._get_commit_files(commit)
            all_files.update(files)
        
        return list(all_files)
    
    def _analyze_file_quality(self, file_path: str) -> Dict[str, Any]:
        """Analyze quality of a single file"""
        result = {
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "score": 100
        }
        
        if not Path(file_path).exists():
            result["issues"].append(f"File not found: {file_path}")
            result["score"] = 0
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Basic quality checks
            line_count = len(lines)
            
            if line_count > self.quality_standards["general"]["max_file_size"]:
                result["warnings"].append(f"Large file: {line_count} lines")
                result["score"] -= 10
            
            # Check for header comment
            if not any(line.strip().startswith('#') for line in lines[:5]):
                result["recommendations"].append("Consider adding file header comment")
            
            # File-type specific checks
            if file_path.endswith('.py'):
                result.update(self._analyze_python_file_quality(lines))
            elif file_path.endswith('.sh'):
                result.update(self._analyze_bash_file_quality(lines))
            
        except Exception as e:
            result["issues"].append(f"Error analyzing {file_path}: {e}")
            result["score"] = 0
        
        return result
    
    def _analyze_python_file_quality(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze Python file quality"""
        result = {"issues": [], "warnings": [], "recommendations": []}
        
        function_count = 0
        documented_functions = 0
        long_lines = 0
        
        in_function = False
        current_function_lines = 0
        
        for i, line in enumerate(lines):
            # Check line length
            if len(line.rstrip()) > self.quality_standards["python"]["max_line_length"]:
                long_lines += 1
            
            # Count functions and check documentation
            if line.strip().startswith('def '):
                function_count += 1
                in_function = True
                current_function_lines = 0
                
                # Check if next non-empty line is a docstring
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            documented_functions += 1
                        break
            
            elif in_function:
                current_function_lines += 1
                if current_function_lines > self.quality_standards["python"]["max_function_length"]:
                    result["warnings"].append(f"Long function at line {i-current_function_lines}")
                    in_function = False
                
                if line.strip() == "" or not line.startswith("    "):
                    in_function = False
        
        # Generate quality feedback
        if long_lines > 5:
            result["warnings"].append(f"Many long lines: {long_lines}")
        
        if function_count > 0:
            doc_ratio = documented_functions / function_count
            if doc_ratio < 0.8:
                result["recommendations"].append(f"Low docstring coverage: {doc_ratio:.1%}")
        
        return result
    
    def _analyze_bash_file_quality(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze Bash file quality"""
        result = {"issues": [], "warnings": [], "recommendations": []}
        
        has_shebang = lines[0].startswith('#!') if lines else False
        has_error_handling = any('set -e' in line for line in lines)
        comment_ratio = sum(1 for line in lines if line.strip().startswith('#')) / max(len(lines), 1)
        
        if not has_shebang:
            result["issues"].append("Missing shebang line")
        
        if not has_error_handling:
            result["recommendations"].append("Consider adding 'set -e' for error handling")
        
        if comment_ratio < 0.1:
            result["recommendations"].append("Consider adding more comments")
        
        return result
    
    def _check_success_criterion(self, criterion: str, worker_id: str, task_id: str) -> bool:
        """Check if a specific success criterion was met"""
        # This is a simplified check - could be enhanced with more sophisticated analysis
        created_files = self._get_worker_created_files(worker_id, task_id)
        
        # Look for key terms from criterion in created files
        key_terms = criterion.lower().split()
        
        for file_path in created_files:
            file_name = Path(file_path).name.lower()
            if any(term in file_name for term in key_terms):
                return True
            
            # Check file content for key terms
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if any(term in content for term in key_terms):
                        return True
            except Exception:
                continue
        
        return False
    
    def _find_test_files(self, worker_id: str, task_id: str) -> List[str]:
        """Find test files created by worker"""
        created_files = self._get_worker_created_files(worker_id, task_id)
        return [f for f in created_files if 'test' in f.lower() or f.endswith('_test.py')]
    
    def _analyze_test_file(self, test_file: str) -> Dict[str, Any]:
        """Analyze quality of a test file"""
        result = {
            "test_count": 0,
            "has_assertions": False
        }
        
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count test functions
            result["test_count"] = content.count('def test_')
            
            # Check for assertions
            result["has_assertions"] = any(assertion in content for assertion in [
                'assert', 'assertEqual', 'assertTrue', 'assertFalse'
            ])
            
        except Exception:
            pass
        
        return result
    
    def _check_test_executability(self, test_files: List[str]) -> int:
        """Check how many test files can be executed"""
        executable_count = 0
        
        for test_file in test_files:
            try:
                # Simple syntax check for Python files
                if test_file.endswith('.py'):
                    subprocess.run([
                        'python', '-m', 'py_compile', test_file
                    ], capture_output=True, timeout=10, check=True)
                    executable_count += 1
            except Exception:
                continue
        
        return executable_count
    
    def _get_python_files(self, worker_id: str, task_id: str) -> List[str]:
        """Get Python files created by worker"""
        created_files = self._get_worker_created_files(worker_id, task_id)
        return [f for f in created_files if f.endswith('.py')]
    
    def _analyze_python_documentation(self, py_file: str) -> Dict[str, int]:
        """Analyze documentation in Python file"""
        result = {
            "total_functions": 0,
            "documented_functions": 0
        }
        
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    result["total_functions"] += 1
                    
                    # Check for docstring in next few lines
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line:
                            if next_line.startswith('"""') or next_line.startswith("'''"):
                                result["documented_functions"] += 1
                            break
                            
        except Exception:
            pass
        
        return result
    
    def _find_documentation_files(self, worker_id: str, task_id: str) -> List[str]:
        """Find documentation files created by worker"""
        created_files = self._get_worker_created_files(worker_id, task_id)
        doc_extensions = ['.md', '.rst', '.txt']
        doc_names = ['readme', 'documentation', 'docs']
        
        doc_files = []
        for file_path in created_files:
            file_name = Path(file_path).name.lower()
            
            if any(file_path.endswith(ext) for ext in doc_extensions):
                doc_files.append(file_path)
            elif any(name in file_name for name in doc_names):
                doc_files.append(file_path)
        
        return doc_files
    
    def _generate_overall_assessment(self) -> Dict[str, Any]:
        """Generate overall assessment from all review results"""
        total_score = sum(result.score for result in self.review_results)
        average_score = total_score / len(self.review_results) if self.review_results else 0
        
        all_passed = all(result.passed for result in self.review_results)
        total_issues = sum(len(result.issues) for result in self.review_results)
        total_warnings = sum(len(result.warnings) for result in self.review_results)
        
        # Determine overall status
        if average_score >= 90 and all_passed:
            status = "EXCELLENT"
        elif average_score >= 80 and all_passed:
            status = "GOOD"
        elif average_score >= 70:
            status = "ACCEPTABLE"
        elif average_score >= 60:
            status = "NEEDS_IMPROVEMENT"
        else:
            status = "POOR"
        
        return {
            "status": status,
            "overall_score": round(average_score, 1),
            "passed": all_passed,
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "component_scores": {result.component: result.score for result in self.review_results}
        }
    
    def _result_to_dict(self, result: ReviewResult) -> Dict[str, Any]:
        """Convert ReviewResult to dictionary"""
        return {
            "component": result.component,
            "passed": result.passed,
            "score": result.score,
            "issues": result.issues,
            "warnings": result.warnings,
            "recommendations": result.recommendations,
            "metrics": result.metrics
        }
    
    def _compile_recommendations(self) -> List[str]:
        """Compile all recommendations from review results"""
        all_recommendations = []
        for result in self.review_results:
            all_recommendations.extend(result.recommendations)
        return list(set(all_recommendations))  # Remove duplicates
    
    def _generate_next_steps(self, overall_assessment: Dict[str, Any]) -> List[str]:
        """Generate next steps based on review results"""
        next_steps = []
        
        if overall_assessment["status"] in ["POOR", "NEEDS_IMPROVEMENT"]:
            next_steps.append("Address critical issues before task approval")
            next_steps.append("Implement recommended improvements")
            next_steps.append("Request re-review after fixes")
        elif overall_assessment["status"] == "ACCEPTABLE":
            next_steps.append("Consider implementing recommendations for better quality")
            next_steps.append("Task can proceed with minor improvements")
        else:
            next_steps.append("Task approved - excellent work quality")
            next_steps.append("No immediate action required")
        
        return next_steps
    
    def save_review_report(self, review_report: Dict[str, Any]) -> str:
        """Save review report to file"""
        report_filename = f"review_{review_report['review_id']}.json"
        report_file = REPORTS_DIR / report_filename
        
        try:
            with open(report_file, 'w') as f:
                json.dump(review_report, f, indent=2, default=str)
            
            self._print_colored(f"✅ Review report saved: {report_filename}", Colors.GREEN)
            
            # Also save summary to orchestration log
            self._log_review_summary(review_report)
            
            return str(report_file)
            
        except Exception as e:
            self._print_colored(f"Error saving review report: {e}", Colors.RED)
            raise
    
    def _log_review_summary(self, review_report: Dict[str, Any]) -> None:
        """Log review summary to orchestration log"""
        log_file = LOGS_DIR / "orchestration.log"
        
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                assessment = review_report["overall_assessment"]
                
                f.write(f"[{timestamp}] WORK_REVIEW: {review_report['worker_id']} {review_report['task_id']}\n")
                f.write(f"  Status: {assessment['status']}\n")
                f.write(f"  Score: {assessment['overall_score']}/100\n")
                f.write(f"  Issues: {assessment['total_issues']}, Warnings: {assessment['total_warnings']}\n")
                f.write(f"  Report: {review_report['review_id']}\n")
                f.write(f"---\n")
                
        except Exception as e:
            self._print_colored(f"Error logging review summary: {e}", Colors.RED)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Work Review and Quality Analysis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Review completed work")
    review_parser.add_argument("worker_id", help="Worker ID (e.g., WORKER_1)")
    review_parser.add_argument("task_id", help="Task ID (e.g., PREP-004A)")
    
    # Quick check command
    quick_parser = subparsers.add_parser("quick", help="Quick quality check")
    quick_parser.add_argument("file_path", help="File to check")
    
    # List reviews command
    list_parser = subparsers.add_parser("list", help="List recent reviews")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of reviews to show")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize reviewer
    reviewer = WorkReviewer(verbose=args.verbose)
    
    try:
        if args.command == "review":
            review_report = reviewer.review_task_completion(args.worker_id, args.task_id)
            report_file = reviewer.save_review_report(review_report)
            
            if args.verbose:
                assessment = review_report["overall_assessment"]
                print(f"\n{Colors.BLUE}📊 Review Summary:{Colors.NC}")
                print(f"Status: {assessment['status']}")
                print(f"Score: {assessment['overall_score']}/100")
                print(f"Issues: {assessment['total_issues']}, Warnings: {assessment['total_warnings']}")
                print(f"Report saved: {report_file}")
            
            return 0 if review_report["overall_assessment"]["passed"] else 1
            
        elif args.command == "quick":
            quality_result = reviewer._analyze_file_quality(args.file_path)
            
            print(f"{Colors.BLUE}📋 Quality Check: {args.file_path}{Colors.NC}")
            print(f"Score: {quality_result['score']}/100")
            
            if quality_result["issues"]:
                print(f"{Colors.RED}Issues:{Colors.NC}")
                for issue in quality_result["issues"]:
                    print(f"  • {issue}")
            
            if quality_result["warnings"]:
                print(f"{Colors.YELLOW}Warnings:{Colors.NC}")
                for warning in quality_result["warnings"]:
                    print(f"  • {warning}")
            
            if quality_result["recommendations"]:
                print(f"{Colors.CYAN}Recommendations:{Colors.NC}")
                for rec in quality_result["recommendations"]:
                    print(f"  • {rec}")
            
            return 0 if quality_result["score"] >= 70 else 1
            
        elif args.command == "list":
            report_files = list(REPORTS_DIR.glob("review_*.json"))
            report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            print(f"{Colors.BLUE}📋 Recent Reviews:{Colors.NC}")
            for report_file in report_files[:args.limit]:
                try:
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    timestamp = report["review_timestamp"][:16]  # YYYY-MM-DD HH:MM
                    worker = report["worker_id"]
                    task = report["task_id"]
                    status = report["overall_assessment"]["status"]
                    score = report["overall_assessment"]["overall_score"]
                    
                    print(f"  {timestamp} | {worker} {task} | {status} ({score}/100)")
                    
                except Exception:
                    continue
            
            return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())