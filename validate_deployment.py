#!/usr/bin/env python3
"""
Deployment Validation Script
Validates that the TelBot recovery and prevention measures are working
Run this before every production deployment
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.END}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

class DeploymentValidator:
    """Validates deployment readiness and environment safety"""
    
    def __init__(self):
        self.results = []
        self.warnings = []
        self.errors = []
    
    def add_result(self, check: str, status: bool, message: str):
        """Add a validation result"""
        result = {
            "check": check,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status:
            print_success(f"{check}: {message}")
        else:
            print_error(f"{check}: {message}")
            self.errors.append(message)
    
    def add_warning(self, check: str, message: str):
        """Add a warning"""
        self.warnings.append(f"{check}: {message}")
        print_warning(f"{check}: {message}")
    
    def validate_environment_system(self) -> bool:
        """Validate environment management system"""
        print_header("ENVIRONMENT SYSTEM VALIDATION")
        
        try:
            from environment_manager import EnvironmentManager
            env_manager = EnvironmentManager()
            
            # Check environment detection
            current_env = env_manager.current_env.value
            self.add_result("Environment Detection", True, f"Detected: {current_env}")
            
            # Check configuration
            config = env_manager.config
            has_bot_token = bool(config.bot_token)
            has_db_config = bool(config.supabase_url and config.supabase_key)
            
            self.add_result("Bot Token", has_bot_token, 
                          "Configured" if has_bot_token else "Missing")
            self.add_result("Database Config", has_db_config,
                          "Configured" if has_db_config else "Missing")
            
            # Check feature flags
            feature_flags = config.feature_flags
            dangerous_flags = ["first_impression_fsm"]
            
            for flag in dangerous_flags:
                if feature_flags.get(flag, False) and env_manager.is_production():
                    self.add_result(f"Feature Flag: {flag}", False,
                                  "DANGEROUS: Enabled in production")
                else:
                    self.add_result(f"Feature Flag: {flag}", True,
                                  f"Safe: {'Enabled' if feature_flags.get(flag, False) else 'Disabled'}")
            
            # Check Claude context generation
            context = env_manager.generate_claude_context()
            has_warnings = len(context.get("warnings", [])) > 0
            
            self.add_result("Claude Context", True, "Generated successfully")
            if has_warnings and env_manager.is_production():
                for warning in context["warnings"]:
                    self.add_warning("Production Warning", warning)
            
            return True
            
        except Exception as e:
            self.add_result("Environment System", False, f"Failed to import: {str(e)}")
            return False
    
    def validate_feature_flags(self) -> bool:
        """Validate feature flag system"""
        print_header("FEATURE FLAG VALIDATION")
        
        try:
            from feature_flags import FeatureFlag, CommonFlags, EmergencyFlags
            
            self.add_result("Feature Flag Import", True, "Successfully imported")
            
            # Check that emergency flags exist
            emergency_methods = dir(EmergencyFlags)
            critical_methods = ["disable_first_impression_fsm"]
            
            for method in critical_methods:
                if method in emergency_methods:
                    self.add_result(f"Emergency Method: {method}", True, "Available")
                else:
                    self.add_result(f"Emergency Method: {method}", False, "Missing")
            
            return True
            
        except Exception as e:
            self.add_result("Feature Flag System", False, f"Failed: {str(e)}")
            return False
    
    def validate_critical_paths(self) -> bool:
        """Validate that critical bot functions don't have obvious errors"""
        print_header("CRITICAL PATH VALIDATION")
        
        try:
            # Check that main telbot file can be imported without NameError
            import telbot
            
            # Check for the specific error that caused the outage
            start_handler_source = open('telbot.py', 'r').read()
            
            # Look for undefined variable references
            lines = start_handler_source.split('\n')
            in_start_handler = False
            issues_found = []
            
            for i, line in enumerate(lines):
                if 'def start_handler' in line:
                    in_start_handler = True
                elif in_start_handler and line.strip().startswith('def '):
                    in_start_handler = False
                
                if in_start_handler:
                    # Check for the specific bug that caused the outage
                    if 'if is_first_time:' in line and 'is_first_time =' not in start_handler_source[:start_handler_source.find(line)]:
                        issues_found.append(f"Line {i+1}: Undefined variable 'is_first_time'")
            
            if issues_found:
                for issue in issues_found:
                    self.add_result("Code Analysis", False, issue)
                return False
            else:
                self.add_result("Code Analysis", True, "No undefined variables detected")
            
            # Check that critical handlers exist
            critical_handlers = ['start_handler', 'commit_handler', 'done_handler', 'help_handler']
            for handler in critical_handlers:
                if hasattr(telbot, handler):
                    self.add_result(f"Handler: {handler}", True, "Exists")
                else:
                    self.add_result(f"Handler: {handler}", False, "Missing")
            
            return len(issues_found) == 0
            
        except NameError as e:
            self.add_result("TelBot Import", False, f"NameError: {str(e)}")
            return False
        except ImportError as e:
            self.add_result("TelBot Import", False, f"ImportError: {str(e)}")
            return False
        except Exception as e:
            self.add_result("Critical Path Check", False, f"Error: {str(e)}")
            return False
    
    def validate_deployment_checklist(self) -> bool:
        """Validate that deployment checklist exists and is complete"""
        print_header("DEPLOYMENT CHECKLIST VALIDATION")
        
        required_files = [
            "DEPLOYMENT_CHECKLIST.md",
            "PRODUCTION_OUTAGE_INCIDENT_REPORT.md", 
            "ENVIRONMENT_SEPARATION_ARCHITECTURE.md"
        ]
        
        all_exist = True
        for file in required_files:
            if os.path.exists(file):
                self.add_result(f"File: {file}", True, "Exists")
            else:
                self.add_result(f"File: {file}", False, "Missing")
                all_exist = False
        
        return all_exist
    
    def validate_git_state(self) -> bool:
        """Validate git state for deployment"""
        print_header("GIT STATE VALIDATION")
        
        try:
            import subprocess
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                self.add_warning("Git Status", "Uncommitted changes detected")
                return False
            else:
                self.add_result("Git Status", True, "Working directory clean")
            
            # Check current branch
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True)
            branch = result.stdout.strip()
            
            self.add_result("Git Branch", True, f"Current branch: {branch}")
            
            if branch not in ['main', 'master', 'production']:
                self.add_warning("Branch Warning", f"Not on main/production branch: {branch}")
            
            return True
            
        except Exception as e:
            self.add_result("Git Validation", False, f"Error: {str(e)}")
            return False
    
    def run_all_validations(self) -> Dict:
        """Run all validation checks"""
        print(f"{Colors.BOLD}TELBOT DEPLOYMENT VALIDATION")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Purpose: Prevent production outages like August 18, 2025{Colors.END}")
        
        validations = [
            ("Environment System", self.validate_environment_system),
            ("Feature Flags", self.validate_feature_flags), 
            ("Critical Paths", self.validate_critical_paths),
            ("Deployment Files", self.validate_deployment_checklist),
            ("Git State", self.validate_git_state)
        ]
        
        passed = 0
        total = len(validations)
        
        for name, validator in validations:
            try:
                if validator():
                    passed += 1
            except Exception as e:
                self.add_result(name, False, f"Validation failed: {str(e)}")
        
        # Summary
        print_header("VALIDATION SUMMARY")
        
        if passed == total and len(self.errors) == 0:
            print_success(f"ALL VALIDATIONS PASSED ({passed}/{total})")
            print_success("✅ SAFE TO DEPLOY TO PRODUCTION")
        else:
            print_error(f"VALIDATIONS FAILED ({passed}/{total} passed)")
            print_error("❌ DO NOT DEPLOY TO PRODUCTION")
            
            print(f"\n{Colors.RED}Errors found:{Colors.END}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.END}")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Save results
        report = {
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "total": total,
            "safe_to_deploy": passed == total and len(self.errors) == 0,
            "results": self.results,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        with open("validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Full report saved to: validation_report.json")
        
        return report

def main():
    """Run deployment validation"""
    validator = DeploymentValidator()
    report = validator.run_all_validations()
    
    # Exit with appropriate code
    if report["safe_to_deploy"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()