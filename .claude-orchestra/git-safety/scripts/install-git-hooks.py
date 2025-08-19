#!/usr/bin/env python3
"""
Git Safety Hooks Installation Script - Claude Orchestra System
WORKER_3 PREP-001C Implementation

This script installs and configures Git safety hooks for the orchestration system.
It copies hooks to .git/hooks/, makes them executable, and validates installation.
"""

import os
import sys
import shutil
import stat
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
ORCHESTRA_DIR = REPO_ROOT / ".claude-orchestra"
GIT_HOOKS_DIR = REPO_ROOT / ".git" / "hooks"
SAFETY_HOOKS_DIR = ORCHESTRA_DIR / "git-safety" / "hooks"

# Available hooks to install
AVAILABLE_HOOKS = {
    "pre-commit": {
        "description": "Pre-commit safety validation",
        "source": SAFETY_HOOKS_DIR / "pre-commit",
        "target": GIT_HOOKS_DIR / "pre-commit",
        "critical": True
    },
    "pre-push": {
        "description": "Pre-push branch protection",
        "source": SAFETY_HOOKS_DIR / "pre-push", 
        "target": GIT_HOOKS_DIR / "pre-push",
        "critical": True
    },
    "post-commit": {
        "description": "Post-commit orchestration logging",
        "source": SAFETY_HOOKS_DIR / "post-commit",
        "target": GIT_HOOKS_DIR / "post-commit",
        "critical": False
    },
    "post-checkout": {
        "description": "Post-checkout branch safety validation",
        "source": SAFETY_HOOKS_DIR / "post-checkout",
        "target": GIT_HOOKS_DIR / "post-checkout",
        "critical": False
    }
}

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

def print_colored(message: str, color: str = Colors.NC) -> None:
    """Print a message with color formatting"""
    print(f"{color}{message}{Colors.NC}")

def print_header(title: str) -> None:
    """Print a formatted header"""
    separator = "=" * 60
    print_colored(separator, Colors.BLUE)
    print_colored(f" {title}", Colors.WHITE)
    print_colored(separator, Colors.BLUE)

def validate_environment() -> bool:
    """Validate that we're in a Git repository with orchestration system"""
    print_colored("🔍 Validating environment...", Colors.BLUE)
    
    # Check if we're in a Git repository
    if not (REPO_ROOT / ".git").exists():
        print_colored("❌ Error: Not in a Git repository", Colors.RED)
        print_colored("💡 This script must be run from within a Git repository", Colors.YELLOW)
        return False
    
    # Check if orchestration system exists
    if not ORCHESTRA_DIR.exists():
        print_colored("❌ Error: Claude Orchestra system not found", Colors.RED)
        print_colored("💡 Expected .claude-orchestra/ directory not found", Colors.YELLOW)
        return False
    
    # Check if Git hooks directory exists
    if not GIT_HOOKS_DIR.exists():
        print_colored("📁 Creating .git/hooks directory...", Colors.BLUE)
        GIT_HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if safety hooks directory exists
    if not SAFETY_HOOKS_DIR.exists():
        print_colored("❌ Error: Safety hooks directory not found", Colors.RED)
        print_colored(f"💡 Expected directory: {SAFETY_HOOKS_DIR}", Colors.YELLOW)
        return False
    
    print_colored("✅ Environment validation passed", Colors.GREEN)
    return True

def backup_existing_hooks() -> bool:
    """Backup any existing Git hooks"""
    backup_dir = GIT_HOOKS_DIR / "backup"
    backup_created = False
    
    for hook_name in AVAILABLE_HOOKS.keys():
        existing_hook = GIT_HOOKS_DIR / hook_name
        if existing_hook.exists():
            if not backup_created:
                print_colored("📦 Backing up existing hooks...", Colors.BLUE)
                backup_dir.mkdir(exist_ok=True)
                backup_created = True
            
            backup_file = backup_dir / f"{hook_name}.backup"
            shutil.copy2(existing_hook, backup_file)
            print_colored(f"  • Backed up {hook_name} → {backup_file.name}", Colors.CYAN)
    
    if backup_created:
        print_colored("✅ Existing hooks backed up successfully", Colors.GREEN)
    
    return True

def install_hook(hook_name: str, hook_info: Dict) -> bool:
    """Install a single Git hook"""
    source_file = hook_info["source"]
    target_file = hook_info["target"]
    
    # Check if source exists
    if not source_file.exists():
        print_colored(f"❌ Source hook not found: {source_file}", Colors.RED)
        return False
    
    try:
        # Copy the hook file
        shutil.copy2(source_file, target_file)
        
        # Make it executable
        current_permissions = target_file.stat().st_mode
        target_file.chmod(current_permissions | stat.S_IEXEC)
        
        # Verify it's executable
        if not os.access(target_file, os.X_OK):
            print_colored(f"❌ Failed to make {hook_name} executable", Colors.RED)
            return False
        
        print_colored(f"✅ Installed {hook_name} hook", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"❌ Failed to install {hook_name}: {e}", Colors.RED)
        return False

def validate_hook_installation(hook_name: str, hook_info: Dict) -> bool:
    """Validate that a hook was installed correctly"""
    target_file = hook_info["target"]
    
    # Check if file exists
    if not target_file.exists():
        print_colored(f"❌ Hook file missing: {target_file}", Colors.RED)
        return False
    
    # Check if file is executable
    if not os.access(target_file, os.X_OK):
        print_colored(f"❌ Hook not executable: {target_file}", Colors.RED)
        return False
    
    # Check if file has correct shebang
    try:
        with open(target_file, 'r') as f:
            first_line = f.readline().strip()
            if not first_line.startswith('#!/'):
                print_colored(f"⚠️  Hook missing shebang: {hook_name}", Colors.YELLOW)
                return False
    except Exception as e:
        print_colored(f"❌ Failed to read hook file {hook_name}: {e}", Colors.RED)
        return False
    
    return True

def test_hook_execution(hook_name: str) -> bool:
    """Test that a hook can be executed (basic syntax check)"""
    target_file = GIT_HOOKS_DIR / hook_name
    
    try:
        # For bash scripts, we can do a basic syntax check
        result = subprocess.run(
            ['bash', '-n', str(target_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print_colored(f"❌ Hook syntax error in {hook_name}:", Colors.RED)
            print_colored(f"   {result.stderr.strip()}", Colors.RED)
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print_colored(f"⚠️  Hook syntax check timed out for {hook_name}", Colors.YELLOW)
        return False
    except Exception as e:
        print_colored(f"⚠️  Could not test hook {hook_name}: {e}", Colors.YELLOW)
        return False

def create_installation_log() -> None:
    """Create a log of the installation"""
    log_file = ORCHESTRA_DIR / "logs" / "hook-installation.log"
    log_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(log_file, 'a') as f:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n[{timestamp}] HOOK_INSTALLATION: Git safety hooks installed successfully\n")
            
            for hook_name in AVAILABLE_HOOKS.keys():
                target_file = GIT_HOOKS_DIR / hook_name
                if target_file.exists():
                    f.write(f"  • {hook_name}: installed and executable\n")
                else:
                    f.write(f"  • {hook_name}: not installed\n")
        
        print_colored(f"📝 Installation logged to {log_file}", Colors.CYAN)
        
    except Exception as e:
        print_colored(f"⚠️  Could not create installation log: {e}", Colors.YELLOW)

def main():
    """Main installation process"""
    print_header("Claude Orchestra Git Safety Hooks Installer")
    print_colored("🔧 WORKER_3 PREP-001C Implementation", Colors.PURPLE)
    print()
    
    # Parse command line arguments
    install_all = "--all" in sys.argv
    force_install = "--force" in sys.argv
    test_only = "--test" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print_colored("Usage: python install-git-hooks.py [options]", Colors.WHITE)
        print_colored("Options:", Colors.WHITE)
        print_colored("  --all     Install all available hooks", Colors.CYAN)
        print_colored("  --force   Overwrite existing hooks without backup", Colors.CYAN)
        print_colored("  --test    Test existing hooks without installing", Colors.CYAN)
        print_colored("  --help    Show this help message", Colors.CYAN)
        return 0
    
    # Validate environment
    if not validate_environment():
        return 1
    
    # Test mode - just validate existing hooks
    if test_only:
        print_colored("🧪 Testing existing hooks...", Colors.BLUE)
        all_valid = True
        
        for hook_name, hook_info in AVAILABLE_HOOKS.items():
            target_file = GIT_HOOKS_DIR / hook_name
            if target_file.exists():
                print_colored(f"🔍 Testing {hook_name}...", Colors.BLUE)
                
                if validate_hook_installation(hook_name, hook_info):
                    if test_hook_execution(hook_name):
                        print_colored(f"✅ {hook_name} is valid", Colors.GREEN)
                    else:
                        all_valid = False
                else:
                    all_valid = False
            else:
                print_colored(f"⚠️  {hook_name} not installed", Colors.YELLOW)
                all_valid = False
        
        if all_valid:
            print_colored("✅ All hooks are valid", Colors.GREEN)
            return 0
        else:
            print_colored("❌ Some hooks have issues", Colors.RED)
            return 1
    
    # Backup existing hooks unless force mode
    if not force_install:
        if not backup_existing_hooks():
            return 1
    
    # Install hooks
    print_colored("🚀 Installing Git safety hooks...", Colors.BLUE)
    installation_success = True
    critical_failure = False
    
    for hook_name, hook_info in AVAILABLE_HOOKS.items():
        print_colored(f"📦 Installing {hook_name}...", Colors.BLUE)
        
        if install_hook(hook_name, hook_info):
            # Validate installation
            if validate_hook_installation(hook_name, hook_info):
                if test_hook_execution(hook_name):
                    print_colored(f"  ✅ {hook_info['description']}", Colors.GREEN)
                else:
                    print_colored(f"  ⚠️  {hook_name} installed but has syntax issues", Colors.YELLOW)
                    installation_success = False
            else:
                print_colored(f"  ❌ {hook_name} validation failed", Colors.RED)
                installation_success = False
                if hook_info['critical']:
                    critical_failure = True
        else:
            print_colored(f"  ❌ Failed to install {hook_name}", Colors.RED)
            installation_success = False
            if hook_info['critical']:
                critical_failure = True
    
    print()
    
    # Create installation log
    create_installation_log()
    
    # Summary
    if installation_success:
        print_colored("🎉 Git safety hooks installed successfully!", Colors.GREEN)
        print_colored("🔒 Your repository is now protected by orchestration safety rules", Colors.GREEN)
        print()
        print_colored("Next steps:", Colors.WHITE)
        print_colored("  • Test the hooks with a test commit", Colors.CYAN)
        print_colored("  • Review the configuration in .claude-orchestra/git-safety/config/", Colors.CYAN)
        print_colored("  • Ensure all team members install these hooks", Colors.CYAN)
        return 0
    elif critical_failure:
        print_colored("❌ CRITICAL: Failed to install critical safety hooks", Colors.RED)
        print_colored("🚨 Repository may not be adequately protected", Colors.RED)
        return 1
    else:
        print_colored("⚠️  Installation completed with warnings", Colors.YELLOW)
        print_colored("💡 Some non-critical hooks may not be fully functional", Colors.YELLOW)
        return 0

if __name__ == "__main__":
    sys.exit(main())