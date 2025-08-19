#!/usr/bin/env python3
"""
Repository Safety Validation Script - Claude Orchestra System
WORKER_3 PREP-001C Implementation

This script validates the overall safety and integrity of the Git repository
and orchestration system. It can be called by Git hooks or run standalone.
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent
ORCHESTRA_DIR = REPO_ROOT / ".claude-orchestra"
GIT_HOOKS_DIR = REPO_ROOT / ".git" / "hooks"

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

class ValidationResult:
    """Container for validation results"""
    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.info: List[str] = []
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False
    
    def add_info(self, message: str) -> None:
        self.info.append(message)

class RepoSafetyValidator:
    """Main repository safety validation class"""
    
    def __init__(self, verbose: bool = False, quick_mode: bool = False):
        self.verbose = verbose
        self.quick_mode = quick_mode
        self.results: List[ValidationResult] = []
        
        # Load configuration if available
        self.config = self._load_config()
    
    def _load_config(self) -> Optional[Dict]:
        """Load Git safety configuration"""
        config_file = ORCHESTRA_DIR / "git-safety" / "config" / "git-safety-config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Could not load config: {e}")
        return None
    
    def _print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message if verbose"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")
    
    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a Git command and return success status and output"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def validate_git_repository(self) -> ValidationResult:
        """Validate basic Git repository health"""
        result = ValidationResult("Git Repository Health")
        
        # Check if we're in a Git repository
        if not (REPO_ROOT / ".git").exists():
            result.add_error("Not in a Git repository")
            return result
        
        # Check Git status
        success, output = self._run_git_command(['status', '--porcelain'])
        if not success:
            result.add_error(f"Git status command failed: {output}")
        else:
            if output:
                result.add_info(f"Repository has {len(output.splitlines())} uncommitted changes")
            else:
                result.add_info("Working directory is clean")
        
        # Check for Git hooks directory
        if not GIT_HOOKS_DIR.exists():
            result.add_warning("Git hooks directory does not exist")
        else:
            result.add_info("Git hooks directory exists")
        
        # Check current branch
        success, branch = self._run_git_command(['branch', '--show-current'])
        if success and branch:
            result.add_info(f"Current branch: {branch}")
            
            # Check if branch is protected
            protected_branches = ["main", "master", "production", "staging"]
            if branch in protected_branches:
                result.add_warning(f"Working on protected branch: {branch}")
        else:
            result.add_warning("Could not determine current branch")
        
        return result
    
    def validate_orchestration_system(self) -> ValidationResult:
        """Validate Claude Orchestra system integrity"""
        result = ValidationResult("Orchestration System")
        
        # Check if orchestration directory exists
        if not ORCHESTRA_DIR.exists():
            result.add_error("Claude Orchestra directory (.claude-orchestra) not found")
            return result
        
        # Check critical directories
        critical_dirs = [
            "control",
            "status", 
            "logs",
            "git-safety",
            "scripts"
        ]
        
        for dir_name in critical_dirs:
            dir_path = ORCHESTRA_DIR / dir_name
            if not dir_path.exists():
                result.add_warning(f"Missing orchestration directory: {dir_name}")
            else:
                result.add_info(f"Directory exists: {dir_name}")
        
        # Check critical files
        critical_files = [
            "status/active-worker.md",
            "status/task-queue.md",
            "logs/recent-work.log"
        ]
        
        for file_path in critical_files:
            full_path = ORCHESTRA_DIR / file_path
            if not full_path.exists():
                result.add_warning(f"Missing orchestration file: {file_path}")
            else:
                result.add_info(f"File exists: {file_path}")
        
        return result
    
    def validate_git_safety_hooks(self) -> ValidationResult:
        """Validate Git safety hooks installation and configuration"""
        result = ValidationResult("Git Safety Hooks")
        
        # Check Git safety directory
        safety_dir = ORCHESTRA_DIR / "git-safety"
        if not safety_dir.exists():
            result.add_error("Git safety directory not found")
            return result
        
        # Check hooks directory
        hooks_dir = safety_dir / "hooks"
        if not hooks_dir.exists():
            result.add_error("Git safety hooks directory not found")
            return result
        
        # Check individual hooks
        expected_hooks = ["pre-commit", "pre-push", "post-commit", "post-checkout"]
        
        for hook_name in expected_hooks:
            source_hook = hooks_dir / hook_name
            installed_hook = GIT_HOOKS_DIR / hook_name
            
            if not source_hook.exists():
                result.add_error(f"Source hook missing: {hook_name}")
                continue
                
            if not installed_hook.exists():
                result.add_warning(f"Hook not installed: {hook_name}")
                continue
                
            # Check if hook is executable
            if not os.access(installed_hook, os.X_OK):
                result.add_error(f"Hook not executable: {hook_name}")
                continue
                
            result.add_info(f"Hook properly installed: {hook_name}")
        
        # Check configuration files
        config_dir = safety_dir / "config"
        if config_dir.exists():
            config_files = ["git-safety-config.yaml", "protected-paths.txt"]
            for config_file in config_files:
                if (config_dir / config_file).exists():
                    result.add_info(f"Configuration file exists: {config_file}")
                else:
                    result.add_warning(f"Configuration file missing: {config_file}")
        else:
            result.add_warning("Git safety config directory not found")
        
        return result
    
    def validate_worker_state(self) -> ValidationResult:
        """Validate current worker state consistency"""
        result = ValidationResult("Worker State")
        
        # Check active worker file
        active_worker_file = ORCHESTRA_DIR / "status" / "active-worker.md"
        if not active_worker_file.exists():
            result.add_warning("Active worker file not found")
            return result
        
        try:
            with open(active_worker_file, 'r') as f:
                content = f.read()
                
            # Check for emergency stop
            if "EMERGENCY_STOP_ACTIVE" in content:
                result.add_warning("Emergency stop is currently active")
            
            # Extract current worker info
            lines = content.split('\n')
            current_worker = None
            for line in lines:
                if line.startswith('**CURRENT_WORKER**'):
                    current_worker = line.split(':', 1)[1].strip()
                    break
            
            if current_worker:
                if current_worker == "NONE":
                    result.add_info("No active worker currently assigned")
                else:
                    result.add_info(f"Active worker: {current_worker}")
                    
                    # Check if worker has recent activity
                    recent_work_file = ORCHESTRA_DIR / "logs" / "recent-work.log"
                    if recent_work_file.exists():
                        try:
                            with open(recent_work_file, 'r') as f:
                                recent_lines = f.readlines()[-10:]  # Last 10 lines
                                
                            worker_activity = any(current_worker in line for line in recent_lines)
                            if worker_activity:
                                result.add_info(f"Recent activity found for {current_worker}")
                            else:
                                result.add_warning(f"No recent activity for active worker {current_worker}")
                        except Exception:
                            result.add_warning("Could not read recent work log")
            else:
                result.add_warning("Could not determine current worker status")
                
        except Exception as e:
            result.add_error(f"Failed to read active worker file: {e}")
        
        return result
    
    def validate_emergency_state(self) -> ValidationResult:
        """Validate emergency stop and system state"""
        result = ValidationResult("Emergency State")
        
        # Check for emergency stop flag
        emergency_flag = ORCHESTRA_DIR / "control" / "emergency-stop.flag"
        if emergency_flag.exists():
            result.add_warning("Emergency stop flag is active")
            
            # Try to read emergency stop reason
            try:
                with open(emergency_flag, 'r') as f:
                    reason = f.read().strip()
                if reason:
                    result.add_info(f"Emergency stop reason: {reason}")
            except Exception:
                pass
        else:
            result.add_info("No emergency stop flag active")
        
        # Check system state file
        system_state_file = ORCHESTRA_DIR / "control" / "system-state.json"
        if system_state_file.exists():
            try:
                with open(system_state_file, 'r') as f:
                    state = json.load(f)
                
                if state.get('status') == 'emergency':
                    result.add_warning("System state indicates emergency mode")
                else:
                    result.add_info(f"System state: {state.get('status', 'unknown')}")
                    
            except Exception as e:
                result.add_warning(f"Could not read system state: {e}")
        
        return result
    
    def validate_file_permissions(self) -> ValidationResult:
        """Validate critical file permissions"""
        result = ValidationResult("File Permissions")
        
        if self.quick_mode:
            result.add_info("Skipping file permissions check (quick mode)")
            return result
        
        # Check that orchestration files are properly protected
        sensitive_paths = [
            ORCHESTRA_DIR / "control",
            ORCHESTRA_DIR / "git-safety" / "scripts"
        ]
        
        for path in sensitive_paths:
            if path.exists():
                try:
                    # Check if directory is readable/writable by owner
                    if path.is_dir():
                        if os.access(path, os.R_OK | os.W_OK):
                            result.add_info(f"Directory permissions OK: {path.relative_to(REPO_ROOT)}")
                        else:
                            result.add_warning(f"Directory permissions issue: {path.relative_to(REPO_ROOT)}")
                except Exception as e:
                    result.add_warning(f"Could not check permissions for {path}: {e}")
        
        # Check that scripts are executable
        scripts_dir = ORCHESTRA_DIR / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                if os.access(script_file, os.X_OK):
                    result.add_info(f"Script is executable: {script_file.name}")
                else:
                    result.add_warning(f"Script not executable: {script_file.name}")
        
        return result
    
    def validate_post_commit(self, commit_hash: Optional[str] = None) -> ValidationResult:
        """Special validation for post-commit hooks"""
        result = ValidationResult("Post-Commit Validation")
        
        if not commit_hash:
            # Get the latest commit
            success, commit_hash = self._run_git_command(['rev-parse', 'HEAD'])
            if not success:
                result.add_error("Could not get current commit hash")
                return result
        
        # Check if commit was properly logged
        orchestration_log = ORCHESTRA_DIR / "logs" / "orchestration.log"
        if orchestration_log.exists():
            try:
                with open(orchestration_log, 'r') as f:
                    recent_logs = f.readlines()[-20:]  # Last 20 lines
                
                commit_logged = any(commit_hash[:7] in line for line in recent_logs)
                if commit_logged:
                    result.add_info("Commit was properly logged to orchestration system")
                else:
                    result.add_warning("Commit may not have been logged to orchestration system")
                    
            except Exception as e:
                result.add_warning(f"Could not check orchestration log: {e}")
        else:
            result.add_warning("Orchestration log file not found")
        
        return result
    
    def run_validation(self, validation_types: List[str] = None) -> bool:
        """Run all validations or specific validation types"""
        if validation_types is None:
            validation_types = ["all"]
        
        self._print_colored("🔍 Starting repository safety validation...", Colors.BLUE)
        
        # Define all available validations
        all_validations = {
            "git": self.validate_git_repository,
            "orchestration": self.validate_orchestration_system,
            "hooks": self.validate_git_safety_hooks,
            "worker": self.validate_worker_state,
            "emergency": self.validate_emergency_state,
            "permissions": self.validate_file_permissions
        }
        
        # Run requested validations
        if "all" in validation_types:
            validations_to_run = all_validations
        else:
            validations_to_run = {k: v for k, v in all_validations.items() if k in validation_types}
        
        for name, validation_func in validations_to_run.items():
            self._print_colored(f"🔍 Running {name} validation...", Colors.CYAN)
            result = validation_func()
            self.results.append(result)
        
        return self._report_results()
    
    def _report_results(self) -> bool:
        """Report validation results and return overall success status"""
        total_errors = sum(len(result.errors) for result in self.results)
        total_warnings = sum(len(result.warnings) for result in self.results)
        
        # Print summary
        if self.verbose:
            print("\n" + "=" * 60)
            print(f"{Colors.WHITE} VALIDATION RESULTS SUMMARY{Colors.NC}")
            print("=" * 60)
            
            for result in self.results:
                status_color = Colors.GREEN if result.passed else Colors.RED
                status_text = "PASS" if result.passed else "FAIL"
                
                print(f"{status_color}[{status_text}]{Colors.NC} {result.name}")
                
                for info in result.info:
                    print(f"  {Colors.CYAN}ℹ️  {info}{Colors.NC}")
                
                for warning in result.warnings:
                    print(f"  {Colors.YELLOW}⚠️  {warning}{Colors.NC}")
                
                for error in result.errors:
                    print(f"  {Colors.RED}❌ {error}{Colors.NC}")
                
                if result.info or result.warnings or result.errors:
                    print()
        
        # Overall result
        overall_success = total_errors == 0
        
        if self.verbose:
            if overall_success:
                if total_warnings == 0:
                    print(f"{Colors.GREEN}✅ All validations passed with no issues{Colors.NC}")
                else:
                    print(f"{Colors.YELLOW}⚠️  All validations passed but {total_warnings} warnings found{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Validation failed with {total_errors} errors and {total_warnings} warnings{Colors.NC}")
        
        return overall_success

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Repository Safety Validation Script")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--quick-check", "-q", action="store_true",
                       help="Quick validation mode (skip expensive checks)")
    parser.add_argument("--post-commit", action="store_true",
                       help="Run post-commit specific validation")
    parser.add_argument("--types", nargs="+", 
                       choices=["git", "orchestration", "hooks", "worker", "emergency", "permissions"],
                       help="Specific validation types to run")
    
    args = parser.parse_args()
    
    # Create validator
    validator = RepoSafetyValidator(verbose=args.verbose, quick_mode=args.quick_check)
    
    # Determine validation types
    validation_types = args.types or ["all"]
    
    # Add post-commit validation if requested
    if args.post_commit:
        result = validator.validate_post_commit()
        validator.results.append(result)
        if not validator._report_results():
            return 1
        return 0
    
    # Run main validation
    success = validator.run_validation(validation_types)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())