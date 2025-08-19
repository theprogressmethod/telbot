#!/usr/bin/env python3
"""
Git Boundary Check Script - Claude Orchestra System
WORKER_3 PREP-001C Implementation

This script validates that Git operations respect worker boundaries and
orchestration rules. It's called by Git hooks to ensure workers only
modify files within their assigned boundaries.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import argparse

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent
ORCHESTRA_DIR = REPO_ROOT / ".claude-orchestra"

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class WorkerBoundary:
    """Represents a worker's file modification boundaries"""
    def __init__(self, worker_id: str, specialization: str):
        self.worker_id = worker_id
        self.specialization = specialization
        self.allowed_patterns: List[str] = []
        self.forbidden_patterns: List[str] = []
        self.allowed_directories: List[str] = []
        self.forbidden_directories: List[str] = []
    
    def can_modify_file(self, file_path: str) -> Tuple[bool, str]:
        """Check if this worker can modify the given file path"""
        # Convert to Path for easier handling
        path = Path(file_path)
        
        # Check forbidden patterns first (more restrictive)
        for pattern in self.forbidden_patterns:
            if self._matches_pattern(str(path), pattern):
                return False, f"File matches forbidden pattern: {pattern}"
        
        # Check forbidden directories
        for forbidden_dir in self.forbidden_directories:
            if str(path).startswith(forbidden_dir):
                return False, f"File in forbidden directory: {forbidden_dir}"
        
        # Check allowed patterns
        for pattern in self.allowed_patterns:
            if self._matches_pattern(str(path), pattern):
                return True, f"File matches allowed pattern: {pattern}"
        
        # Check allowed directories
        for allowed_dir in self.allowed_directories:
            if str(path).startswith(allowed_dir):
                return True, f"File in allowed directory: {allowed_dir}"
        
        # Default is forbidden if no explicit allowance
        return False, "File not in any allowed pattern or directory"
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a pattern (supports glob-like patterns)"""
        # Convert glob pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        regex_pattern = f"^{regex_pattern}$"
        
        try:
            return bool(re.match(regex_pattern, file_path))
        except re.error:
            # If regex fails, fall back to simple string matching
            return pattern in file_path

class GitBoundaryChecker:
    """Main class for checking Git operation boundaries"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.worker_boundaries: Dict[str, WorkerBoundary] = {}
        self.current_worker: Optional[str] = None
        
        # Load worker boundaries and current state
        self._load_worker_boundaries()
        self._load_current_worker()
    
    def _print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message if verbose"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")
    
    def _load_worker_boundaries(self) -> None:
        """Load worker boundary definitions"""
        # Default boundaries for known worker types
        self._setup_default_boundaries()
        
        # Try to load custom boundaries from configuration
        boundaries_file = ORCHESTRA_DIR / "config" / "worker-boundaries.json"
        if boundaries_file.exists():
            try:
                with open(boundaries_file, 'r') as f:
                    custom_boundaries = json.load(f)
                self._apply_custom_boundaries(custom_boundaries)
            except Exception as e:
                if self.verbose:
                    self._print_colored(f"Warning: Could not load custom boundaries: {e}", Colors.YELLOW)
    
    def _setup_default_boundaries(self) -> None:
        """Setup default worker boundaries based on specializations"""
        
        # WORKER_1: Bot Developer
        bot_worker = WorkerBoundary("WORKER_1", "Bot Developer")
        bot_worker.allowed_patterns = [
            "*.py",
            "requirements*.txt",
            "config/bot/*",
            "src/bot/*",
            "bot/*",
            "telegram/*",
            "handlers/*"
        ]
        bot_worker.allowed_directories = [
            "bot/",
            "telegram/",
            "handlers/",
            "src/bot/",
            "config/bot/"
        ]
        bot_worker.forbidden_patterns = [
            "*.production.*",
            "*.staging.*",
            ".env.production",
            ".env.staging"
        ]
        bot_worker.forbidden_directories = [
            ".claude-orchestra/control/",
            "production/",
            "deployment/"
        ]
        self.worker_boundaries["WORKER_1"] = bot_worker
        
        # WORKER_2: Dashboard Developer  
        dashboard_worker = WorkerBoundary("WORKER_2", "Dashboard Developer")
        dashboard_worker.allowed_patterns = [
            "*.html",
            "*.css",
            "*.js",
            "*.ts",
            "*.py",
            "templates/*",
            "static/*",
            "dashboard/*",
            "web/*"
        ]
        dashboard_worker.allowed_directories = [
            "dashboard/",
            "web/", 
            "templates/",
            "static/",
            "src/dashboard/",
            "config/dashboard/"
        ]
        dashboard_worker.forbidden_patterns = [
            "*.production.*",
            "*.staging.*",
            ".env.production",
            ".env.staging"
        ]
        dashboard_worker.forbidden_directories = [
            ".claude-orchestra/control/",
            "production/",
            "deployment/"
        ]
        self.worker_boundaries["WORKER_2"] = dashboard_worker
        
        # WORKER_3: Test Builder & Quality Assurance / Automation Developer
        test_worker = WorkerBoundary("WORKER_3", "Test Builder & Automation Developer")
        test_worker.allowed_patterns = [
            "test*.py",
            "tests/*",
            "conftest.py",
            "pytest.ini",
            "requirements-test.txt",
            ".env.test",
            "*.sh",
            "scripts/*",
            ".claude-orchestra/git-safety/*",
            ".claude-orchestra/scripts/*",
            ".github/workflows/*",
            "Dockerfile.test"
        ]
        test_worker.allowed_directories = [
            "tests/",
            "test/",
            "scripts/",
            ".claude-orchestra/git-safety/",
            ".claude-orchestra/scripts/",
            ".github/workflows/",
            "ci/",
            "automation/"
        ]
        test_worker.forbidden_patterns = [
            "*.production.*",
            "*.staging.*", 
            ".env.production",
            ".env.staging"
        ]
        test_worker.forbidden_directories = [
            ".claude-orchestra/control/",
            "production/config/",
            "deployment/production/"
        ]
        self.worker_boundaries["WORKER_3"] = test_worker
    
    def _apply_custom_boundaries(self, custom_boundaries: Dict) -> None:
        """Apply custom boundary definitions from configuration"""
        for worker_id, config in custom_boundaries.items():
            if worker_id in self.worker_boundaries:
                boundary = self.worker_boundaries[worker_id]
                
                # Update allowed patterns
                if "allowed_patterns" in config:
                    boundary.allowed_patterns.extend(config["allowed_patterns"])
                
                # Update forbidden patterns
                if "forbidden_patterns" in config:
                    boundary.forbidden_patterns.extend(config["forbidden_patterns"])
                
                # Update allowed directories
                if "allowed_directories" in config:
                    boundary.allowed_directories.extend(config["allowed_directories"])
                
                # Update forbidden directories
                if "forbidden_directories" in config:
                    boundary.forbidden_directories.extend(config["forbidden_directories"])
    
    def _load_current_worker(self) -> None:
        """Load the currently active worker from status files"""
        active_worker_file = ORCHESTRA_DIR / "status" / "active-worker.md"
        
        if not active_worker_file.exists():
            self._print_colored("No active worker file found", Colors.YELLOW)
            return
        
        try:
            with open(active_worker_file, 'r') as f:
                content = f.read()
            
            # Extract current worker ID
            for line in content.split('\n'):
                if line.startswith('**CURRENT_WORKER**'):
                    worker_info = line.split(':', 1)[1].strip()
                    if worker_info and worker_info != "NONE":
                        self.current_worker = worker_info
                        self._print_colored(f"Current active worker: {worker_info}", Colors.BLUE)
                    else:
                        self._print_colored("No worker currently active", Colors.CYAN)
                    break
        
        except Exception as e:
            self._print_colored(f"Error reading active worker file: {e}", Colors.RED)
    
    def check_file_modification(self, file_path: str, worker_id: Optional[str] = None) -> Tuple[bool, str]:
        """Check if a file modification is allowed for the current or specified worker"""
        # Use specified worker or current worker
        check_worker = worker_id or self.current_worker
        
        if not check_worker:
            # If no worker is active, allow modifications but warn
            return True, "No active worker - allowing modification with warning"
        
        if check_worker not in self.worker_boundaries:
            return False, f"Unknown worker ID: {check_worker}"
        
        boundary = self.worker_boundaries[check_worker]
        return boundary.can_modify_file(file_path)
    
    def check_multiple_files(self, file_paths: List[str], worker_id: Optional[str] = None) -> Dict[str, Tuple[bool, str]]:
        """Check multiple file modifications"""
        results = {}
        for file_path in file_paths:
            results[file_path] = self.check_file_modification(file_path, worker_id)
        return results
    
    def validate_git_operation(self, operation: str = "commit") -> Tuple[bool, List[str]]:
        """Validate a Git operation (commit, push, etc.) against worker boundaries"""
        violations = []
        
        if operation == "commit":
            # Get staged files for commit validation
            try:
                import subprocess
                result = subprocess.run(
                    ['git', 'diff', '--cached', '--name-only'],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    return False, ["Could not get staged files from Git"]
                
                staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
            except Exception as e:
                return False, [f"Error running Git command: {e}"]
        
        else:
            # For other operations, we'd need different logic
            return True, []
        
        # Check each staged file
        for file_path in staged_files:
            if not file_path:  # Skip empty lines
                continue
                
            allowed, reason = self.check_file_modification(file_path)
            if not allowed:
                violations.append(f"{file_path}: {reason}")
        
        return len(violations) == 0, violations
    
    def get_worker_summary(self, worker_id: Optional[str] = None) -> str:
        """Get a summary of worker boundaries"""
        check_worker = worker_id or self.current_worker
        
        if not check_worker or check_worker not in self.worker_boundaries:
            return f"No boundary information available for worker: {check_worker}"
        
        boundary = self.worker_boundaries[check_worker]
        
        summary = []
        summary.append(f"Worker: {boundary.worker_id}")
        summary.append(f"Specialization: {boundary.specialization}")
        summary.append("")
        
        if boundary.allowed_patterns:
            summary.append("Allowed file patterns:")
            for pattern in boundary.allowed_patterns:
                summary.append(f"  • {pattern}")
            summary.append("")
        
        if boundary.allowed_directories:
            summary.append("Allowed directories:")
            for directory in boundary.allowed_directories:
                summary.append(f"  • {directory}")
            summary.append("")
        
        if boundary.forbidden_patterns:
            summary.append("Forbidden file patterns:")
            for pattern in boundary.forbidden_patterns:
                summary.append(f"  • {pattern}")
            summary.append("")
        
        if boundary.forbidden_directories:
            summary.append("Forbidden directories:")
            for directory in boundary.forbidden_directories:
                summary.append(f"  • {directory}")
        
        return "\n".join(summary)
    
    def log_boundary_check(self, file_path: str, allowed: bool, reason: str) -> None:
        """Log boundary check results"""
        log_file = ORCHESTRA_DIR / "logs" / "boundary-checks.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                status = "ALLOWED" if allowed else "BLOCKED"
                worker = self.current_worker or "NONE"
                f.write(f"[{timestamp}] {status}: {worker} -> {file_path} ({reason})\n")
        except Exception as e:
            if self.verbose:
                self._print_colored(f"Warning: Could not log boundary check: {e}", Colors.YELLOW)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Git Boundary Check Script")
    parser.add_argument("files", nargs="*", help="Files to check (if not provided, checks staged files)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--worker", "-w", help="Specific worker ID to check against")
    parser.add_argument("--summary", "-s", action="store_true", help="Show worker boundary summary")
    parser.add_argument("--operation", "-o", default="commit", 
                       choices=["commit", "push", "checkout"],
                       help="Git operation being performed")
    
    args = parser.parse_args()
    
    # Create boundary checker
    checker = GitBoundaryChecker(verbose=args.verbose)
    
    # Show summary if requested
    if args.summary:
        print(checker.get_worker_summary(args.worker))
        return 0
    
    # Check specific files if provided
    if args.files:
        checker._print_colored("🔍 Checking file boundaries...", Colors.BLUE)
        
        violations = []
        for file_path in args.files:
            allowed, reason = checker.check_file_modification(file_path, args.worker)
            checker.log_boundary_check(file_path, allowed, reason)
            
            if args.verbose:
                status_color = Colors.GREEN if allowed else Colors.RED
                status_text = "✅ ALLOWED" if allowed else "❌ BLOCKED"
                print(f"{status_color}{status_text}{Colors.NC} {file_path}")
                print(f"  Reason: {reason}")
            
            if not allowed:
                violations.append(f"{file_path}: {reason}")
        
        if violations:
            if args.verbose:
                print(f"\n{Colors.RED}❌ Boundary violations found:{Colors.NC}")
                for violation in violations:
                    print(f"  • {violation}")
            return 1
        else:
            if args.verbose:
                print(f"\n{Colors.GREEN}✅ All files pass boundary checks{Colors.NC}")
            return 0
    
    # Validate Git operation
    else:
        checker._print_colored(f"🔍 Validating {args.operation} operation boundaries...", Colors.BLUE)
        
        allowed, violations = checker.validate_git_operation(args.operation)
        
        if violations:
            if args.verbose:
                print(f"\n{Colors.RED}❌ Worker boundary violations found:{Colors.NC}")
                for violation in violations:
                    print(f"  • {violation}")
                    
                print(f"\n{Colors.BLUE}💡 Worker boundary summary:{Colors.NC}")
                print(checker.get_worker_summary(args.worker))
            return 1
        else:
            if args.verbose:
                print(f"\n{Colors.GREEN}✅ {args.operation.title()} operation respects worker boundaries{Colors.NC}")
            return 0

if __name__ == "__main__":
    sys.exit(main())