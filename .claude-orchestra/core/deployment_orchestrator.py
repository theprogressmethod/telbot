#!/usr/bin/env python3
"""
Claude Orchestra Deployment Orchestrator
Main engine for managing deployments from dev to production
"""

import os
import sys
import json
import yaml
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import time

class DeploymentOrchestrator:
    """Main orchestration engine for deployments"""
    
    def __init__(self):
        self.orchestra_root = Path(__file__).parent.parent
        self.project_root = self.orchestra_root.parent
        self.config = self._load_config()
        self.current_environment = self._detect_environment()
        
    def _load_config(self) -> dict:
        """Load orchestration configuration"""
        config_path = self.orchestra_root / "config" / "orchestration-config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {config_path}")
            
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _detect_environment(self) -> str:
        """Detect current environment from git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            branch = result.stdout.strip()
            
            for env, config in self.config['environments'].items():
                if config['branch'] == branch:
                    return env
            return 'development'
        except:
            return 'development'
            
    def _log(self, message: str, level: str = "INFO"):
        """Log to orchestration log"""
        timestamp = datetime.now().isoformat()
        log_file = self.orchestra_root / "logs" / "orchestration.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
            
        print(f"[{level}] {message}")
        
    def _run_command(self, command: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run a shell command and return results"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
            
    def pre_deployment_checks(self, target_env: str) -> bool:
        """Run comprehensive pre-deployment checks"""
        self._log(f"Running pre-deployment checks for {target_env}")
        checks_passed = True
        
        # Check 1: Ensure we're on the right branch
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        ).stdout.strip()
        
        expected_branch = self.config['environments'][target_env]['branch']
        if current_branch != expected_branch and target_env == 'production':
            self._log(f"ERROR: Not on {expected_branch} branch (current: {current_branch})", "ERROR")
            checks_passed = False
            
        # Check 2: No uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True
        ).stdout.strip()
        
        if status:
            self._log("WARNING: Uncommitted changes detected", "WARNING")
            
        # Check 3: Tests pass (if required)
        if self.config['environments'][target_env].get('test_required', True):
            self._log("Running tests...")
            if not self.run_tests():
                self._log("ERROR: Tests failed", "ERROR")
                checks_passed = False
                
        # Check 4: No secrets in code
        if self.config['safety']['scan_for_secrets']:
            self._log("Scanning for secrets...")
            if self.scan_for_secrets():
                self._log("ERROR: Secrets detected in code", "ERROR")
                checks_passed = False
                
        # Check 5: Service health check
        if target_env in ['staging', 'production']:
            if not self.check_service_health(target_env):
                self._log(f"WARNING: {target_env} service health check failed", "WARNING")
                
        return checks_passed
        
    def run_tests(self) -> bool:
        """Run test suite"""
        self._log("Running test suite...")
        
        # Check if pytest is available
        test_command = ["python", "-m", "pytest", "-v", "--tb=short"]
        
        returncode, stdout, stderr = self._run_command(test_command, check=False)
        
        if returncode == 0:
            self._log("All tests passed ✅")
            return True
        else:
            self._log(f"Tests failed: {stderr}", "ERROR")
            return False
            
    def scan_for_secrets(self) -> bool:
        """Scan for potential secrets in code"""
        secrets_found = False
        patterns = [
            r"api[_-]?key.*=.*['\"][a-zA-Z0-9]{20,}['\"]",
            r"secret.*=.*['\"][a-zA-Z0-9]{20,}['\"]",
            r"token.*=.*['\"][a-zA-Z0-9]{20,}['\"]",
            r"sk-[a-zA-Z0-9]{48}",
            r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"
        ]
        
        # Only scan Python files and configs
        for file_path in self.project_root.glob("**/*.py"):
            if ".env" in str(file_path) or "test" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    for pattern in patterns:
                        import re
                        if re.search(pattern, content, re.IGNORECASE):
                            self._log(f"Potential secret in {file_path}", "WARNING")
                            secrets_found = True
            except:
                pass
                
        return secrets_found
        
    def check_service_health(self, environment: str) -> bool:
        """Check if service is healthy"""
        service_url = self.config['deployment']['services'][environment]['url']
        
        try:
            import requests
            response = requests.get(f"{service_url}/health", timeout=10)
            if response.status_code == 200:
                self._log(f"{environment} service is healthy ✅")
                return True
        except:
            pass
            
        self._log(f"{environment} service health check failed", "WARNING")
        return False
        
    def create_backup(self, environment: str) -> Optional[str]:
        """Create backup before deployment"""
        if not self.config['safety']['backup_before_deploy']:
            return None
            
        self._log(f"Creating backup for {environment}...")
        
        backup_dir = self.orchestra_root / "backups" / environment
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}.tar.gz"
        
        # Create tarball of current state
        subprocess.run([
            "tar", "-czf", str(backup_path),
            "--exclude=.git",
            "--exclude=__pycache__",
            "--exclude=venv",
            "--exclude=node_modules",
            "."
        ], cwd=self.project_root)
        
        self._log(f"Backup created: {backup_path}")
        return str(backup_path)
        
    def deploy_to_environment(self, target_env: str, force: bool = False) -> bool:
        """Deploy to target environment"""
        self._log(f"=== Starting deployment to {target_env.upper()} ===")
        
        # Pre-deployment checks
        if not force and not self.pre_deployment_checks(target_env):
            self._log("Pre-deployment checks failed. Use --force to override", "ERROR")
            return False
            
        # Create backup
        backup_path = self.create_backup(target_env)
        
        # Get deployment configuration
        env_config = self.config['environments'][target_env]
        service_config = self.config['deployment']['services'][target_env]
        
        # Deployment steps
        try:
            # Step 1: Push to correct branch
            target_branch = env_config['branch']
            self._log(f"Pushing to {target_branch} branch...")
            
            if target_env == 'production':
                # For production, we need to merge or push carefully
                self._run_command(["git", "push", "origin", f"HEAD:{target_branch}"])
            else:
                self._run_command(["git", "push", "origin", target_branch])
                
            # Step 2: Trigger deployment (Render auto-deploys on push)
            self._log(f"Deployment triggered for {service_config['url']}")
            
            # Step 3: Wait for deployment to complete
            self._log("Waiting for deployment to complete...")
            time.sleep(30)  # Initial wait
            
            # Step 4: Verify deployment
            if self.check_service_health(target_env):
                self._log(f"✅ Deployment to {target_env} successful!")
                
                # Log deployment
                self._log_deployment(target_env, "SUCCESS", backup_path)
                return True
            else:
                self._log(f"❌ Deployment verification failed", "ERROR")
                
                # Attempt rollback if configured
                if env_config.get('rollback_enabled', False) and backup_path:
                    self._log("Initiating rollback...")
                    self.rollback(target_env, backup_path)
                    
                self._log_deployment(target_env, "FAILED", backup_path)
                return False
                
        except Exception as e:
            self._log(f"Deployment failed: {str(e)}", "ERROR")
            self._log_deployment(target_env, "ERROR", backup_path)
            return False
            
    def _log_deployment(self, environment: str, status: str, backup_path: Optional[str]):
        """Log deployment to deployment history"""
        deployment_log = self.orchestra_root / "logs" / "deployments.log"
        
        with open(deployment_log, 'a') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "environment": environment,
                "status": status,
                "backup": backup_path,
                "user": os.environ.get('USER', 'unknown')
            }) + "\n")
            
    def rollback(self, environment: str, backup_path: str) -> bool:
        """Rollback to a previous backup"""
        self._log(f"Rolling back {environment} using {backup_path}")
        
        if not Path(backup_path).exists():
            self._log(f"Backup not found: {backup_path}", "ERROR")
            return False
            
        try:
            # Extract backup
            subprocess.run([
                "tar", "-xzf", backup_path
            ], cwd=self.project_root, check=True)
            
            # Push rollback
            subprocess.run([
                "git", "add", "."
            ], check=True)
            
            subprocess.run([
                "git", "commit", "-m", f"Rollback {environment} to {backup_path}"
            ], check=True)
            
            target_branch = self.config['environments'][environment]['branch']
            subprocess.run([
                "git", "push", "origin", target_branch
            ], check=True)
            
            self._log(f"Rollback completed for {environment}")
            return True
            
        except Exception as e:
            self._log(f"Rollback failed: {str(e)}", "ERROR")
            return False
            
    def promote(self, from_env: str, to_env: str) -> bool:
        """Promote code from one environment to another"""
        self._log(f"Promoting {from_env} → {to_env}")
        
        from_branch = self.config['environments'][from_env]['branch']
        to_branch = self.config['environments'][to_env]['branch']
        
        try:
            # Fetch latest
            subprocess.run(["git", "fetch", "origin"], check=True)
            
            # Checkout target branch
            subprocess.run(["git", "checkout", to_branch], check=True)
            
            # Merge from source
            subprocess.run(["git", "merge", f"origin/{from_branch}"], check=True)
            
            # Deploy to target
            return self.deploy_to_environment(to_env)
            
        except Exception as e:
            self._log(f"Promotion failed: {str(e)}", "ERROR")
            return False


def main():
    """CLI interface for deployment orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Orchestra Deployment Tool")
    parser.add_argument("action", choices=["deploy", "promote", "rollback", "status", "test"])
    parser.add_argument("--env", help="Target environment")
    parser.add_argument("--from", dest="from_env", help="Source environment for promotion")
    parser.add_argument("--force", action="store_true", help="Force deployment")
    parser.add_argument("--backup", help="Backup path for rollback")
    
    args = parser.parse_args()
    
    orchestrator = DeploymentOrchestrator()
    
    if args.action == "deploy":
        if not args.env:
            print("Error: --env required for deployment")
            sys.exit(1)
        success = orchestrator.deploy_to_environment(args.env, args.force)
        sys.exit(0 if success else 1)
        
    elif args.action == "promote":
        if not args.from_env or not args.env:
            print("Error: --from and --env required for promotion")
            sys.exit(1)
        success = orchestrator.promote(args.from_env, args.env)
        sys.exit(0 if success else 1)
        
    elif args.action == "rollback":
        if not args.env or not args.backup:
            print("Error: --env and --backup required for rollback")
            sys.exit(1)
        success = orchestrator.rollback(args.env, args.backup)
        sys.exit(0 if success else 1)
        
    elif args.action == "test":
        success = orchestrator.run_tests()
        sys.exit(0 if success else 1)
        
    elif args.action == "status":
        print(f"Current environment: {orchestrator.current_environment}")
        print(f"Configuration loaded: {orchestrator.config['system']['name']} v{orchestrator.config['system']['version']}")


if __name__ == "__main__":
    main()
