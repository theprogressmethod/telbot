#!/usr/bin/env python3
"""
Claude Orchestra Security Manager
Manages git hooks, secret scanning, and security policies
"""

import os
import re
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime

class SecurityManager:
    """Manages security policies and git hooks"""
    
    def __init__(self):
        self.orchestra_root = Path(__file__).parent.parent
        self.project_root = self.orchestra_root.parent
        self.config = self._load_config()
        self.deployment_mode = False  # Can be enabled for deployments
        
    def _load_config(self) -> dict:
        """Load orchestration configuration"""
        config_path = self.orchestra_root / "config" / "orchestration-config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
        
    def enable_deployment_mode(self, duration_minutes: int = 30):
        """Temporarily enable deployment mode to allow production commits"""
        mode_file = self.orchestra_root / "status" / "deployment_mode.json"
        mode_file.parent.mkdir(parents=True, exist_ok=True)
        
        expire_time = datetime.now().timestamp() + (duration_minutes * 60)
        
        with open(mode_file, 'w') as f:
            json.dump({
                "enabled": True,
                "expire_at": expire_time,
                "started_at": datetime.now().isoformat()
            }, f)
            
        print(f"🚀 Deployment mode enabled for {duration_minutes} minutes")
        print("Git restrictions temporarily relaxed for deployment")
        
    def disable_deployment_mode(self):
        """Disable deployment mode"""
        mode_file = self.orchestra_root / "status" / "deployment_mode.json"
        if mode_file.exists():
            mode_file.unlink()
        print("🔒 Deployment mode disabled - normal security restored")
        
    def is_deployment_mode(self) -> bool:
        """Check if deployment mode is active"""
        mode_file = self.orchestra_root / "status" / "deployment_mode.json"
        
        if not mode_file.exists():
            return False
            
        try:
            with open(mode_file, 'r') as f:
                data = json.load(f)
                
            # Check if expired
            if datetime.now().timestamp() > data.get('expire_at', 0):
                self.disable_deployment_mode()
                return False
                
            return data.get('enabled', False)
        except:
            return False
            
    def scan_for_secrets(self, files: List[str] = None) -> List[Dict]:
        """Scan files for potential secrets"""
        secrets_found = []
        
        # Secret patterns to detect
        patterns = {
            'api_key': r"api[_-]?key.*[=:].*['\"][a-zA-Z0-9]{20,}['\"]",
            'secret': r"secret.*[=:].*['\"][a-zA-Z0-9]{20,}['\"]",
            'password': r"password.*[=:].*['\"][^'\"]{8,}['\"]",
            'token': r"token.*[=:].*['\"][a-zA-Z0-9]{20,}['\"]",
            'aws_key': r"AKIA[0-9A-Z]{16}",
            'github_token': r"ghp_[a-zA-Z0-9]{36}",
            'jwt': r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
            'stripe_key': r"sk_[a-zA-Z0-9]{32}",
            'telegram_token': r"\d{9,10}:[a-zA-Z0-9_-]{35}"
        }
        
        # Files to check
        if files is None:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True
            )
            files = result.stdout.strip().split('\n') if result.stdout else []
            
        for file_path in files:
            if not file_path or not Path(file_path).exists():
                continue
                
            # Skip certain files
            if any(skip in file_path for skip in ['.env', 'test', '__pycache__', '.git']):
                continue
                
            # Skip binary files
            if subprocess.run(
                ["file", file_path],
                capture_output=True, text=True
            ).stdout.find("binary") != -1:
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    line_num = 0
                    
                    for line in content.split('\n'):
                        line_num += 1
                        for pattern_name, pattern in patterns.items():
                            if re.search(pattern, line, re.IGNORECASE):
                                secrets_found.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'type': pattern_name,
                                    'content': line[:50] + '...' if len(line) > 50 else line
                                })
            except:
                pass
                
        return secrets_found
        
    def check_protected_paths(self, files: List[str] = None) -> List[str]:
        """Check if any protected paths are being modified"""
        violations = []
        
        # Get protected paths from config
        protected_paths = self.config.get('safety', {}).get('protected_paths', [])
        
        # Add default protected paths
        protected_paths.extend([
            '.env.production',
            '.env.staging',
            'config/production',
            'secrets/'
        ])
        
        if files is None:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True
            )
            files = result.stdout.strip().split('\n') if result.stdout else []
            
        for file_path in files:
            if not file_path:
                continue
                
            for protected in protected_paths:
                # Handle wildcards
                if '*' in protected:
                    import fnmatch
                    if fnmatch.fnmatch(file_path, protected):
                        violations.append(file_path)
                        break
                elif file_path.startswith(protected):
                    violations.append(file_path)
                    break
                    
        return violations
        
    def check_branch_protection(self) -> Tuple[bool, str]:
        """Check if current branch is protected"""
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        )
        current_branch = result.stdout.strip()
        
        # Check if in deployment mode
        if self.is_deployment_mode():
            return False, current_branch  # Allow commits in deployment mode
            
        # Get protected branches from config
        protected_branches = self.config.get('safety', {}).get('protected_branches', [])
        
        # Add defaults if not in config
        if not protected_branches:
            protected_branches = ['master', 'main', 'production', 'staging']
            
        return current_branch in protected_branches, current_branch
        
    def install_git_hooks(self):
        """Install or update git hooks"""
        hooks_dir = self.project_root / ".git" / "hooks"
        
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        with open(pre_commit_hook, 'w') as f:
            f.write(self._generate_pre_commit_hook())
        os.chmod(pre_commit_hook, 0o755)
        
        # Post-commit hook
        post_commit_hook = hooks_dir / "post-commit"
        with open(post_commit_hook, 'w') as f:
            f.write(self._generate_post_commit_hook())
        os.chmod(post_commit_hook, 0o755)
        
        print("✅ Git hooks installed successfully")
        
    def _generate_pre_commit_hook(self) -> str:
        """Generate pre-commit hook content"""
        return '''#!/bin/bash
# Claude Orchestra Pre-Commit Hook v2.0

# Colors
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
NC='\\033[0m'

echo -e "${BLUE}🔒 Claude Orchestra Security Check${NC}"
echo "================================================"

# Run security checks using Python
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../.claude-orchestra/core")

from security_manager import SecurityManager

manager = SecurityManager()

# Check deployment mode
if manager.is_deployment_mode():
    print("\\033[1;33m⚠️  Deployment mode active - security checks relaxed\\033[0m")
    sys.exit(0)

# Run security checks
violations = []

# Check for secrets
secrets = manager.scan_for_secrets()
if secrets:
    print("\\033[0;31m❌ Secrets detected in code:\\033[0m")
    for secret in secrets[:5]:  # Show first 5
        print(f"  • {secret['file']}:{secret['line']} - {secret['type']}")
    violations.append("secrets")

# Check protected paths
protected = manager.check_protected_paths()
if protected:
    print("\\033[0;31m❌ Protected paths modified:\\033[0m")
    for path in protected[:5]:  # Show first 5
        print(f"  • {path}")
    violations.append("protected_paths")

# Check branch protection
is_protected, branch = manager.check_branch_protection()
if is_protected:
    print(f"\\033[0;31m❌ Direct commits to protected branch '{branch}' not allowed\\033[0m")
    print("\\033[1;33m💡 Create a feature branch or enable deployment mode\\033[0m")
    violations.append("protected_branch")

if violations:
    print("\\033[0;31m================================================\\033[0m")
    print("\\033[0;31m❌ Pre-commit hook FAILED\\033[0m")
    print("\\033[1;33m💡 To deploy: python3 .claude-orchestra/deploy.py\\033[0m")
    print("\\033[0;31m================================================\\033[0m")
    sys.exit(1)
else:
    print("\\033[0;32m✅ All security checks passed\\033[0m")
    sys.exit(0)
EOF

exit $?
'''
        
    def _generate_post_commit_hook(self) -> str:
        """Generate post-commit hook content"""
        return '''#!/bin/bash
# Claude Orchestra Post-Commit Hook

# Log commit
echo "[$(date)] Commit: $(git log -1 --oneline)" >> .claude-orchestra/logs/commits.log

# Check if deployment mode should be disabled
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../.claude-orchestra/core")

from security_manager import SecurityManager

manager = SecurityManager()
if manager.is_deployment_mode():
    print("\\033[1;33m🚀 Deployment mode still active\\033[0m")
EOF
'''


def main():
    """CLI interface for security manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Orchestra Security Manager")
    parser.add_argument("action", choices=["install", "scan", "enable-deploy", "disable-deploy", "status"])
    parser.add_argument("--duration", type=int, default=30, help="Deployment mode duration in minutes")
    
    args = parser.parse_args()
    
    manager = SecurityManager()
    
    if args.action == "install":
        manager.install_git_hooks()
        
    elif args.action == "scan":
        secrets = manager.scan_for_secrets()
        if secrets:
            print("⚠️ Potential secrets found:")
            for secret in secrets:
                print(f"  • {secret['file']}:{secret['line']} - {secret['type']}")
        else:
            print("✅ No secrets detected")
            
    elif args.action == "enable-deploy":
        manager.enable_deployment_mode(args.duration)
        
    elif args.action == "disable-deploy":
        manager.disable_deployment_mode()
        
    elif args.action == "status":
        if manager.is_deployment_mode():
            print("🚀 Deployment mode: ACTIVE")
        else:
            print("🔒 Deployment mode: INACTIVE")
            
        is_protected, branch = manager.check_branch_protection()
        print(f"Current branch: {branch} {'(protected)' if is_protected else ''}")


if __name__ == "__main__":
    main()
