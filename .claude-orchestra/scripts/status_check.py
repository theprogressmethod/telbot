#!/usr/bin/env python3
"""
Comprehensive Status Check Script for Claude Orchestra
Provides complete system status overview
"""
import os
import yaml
from pathlib import Path
from datetime import datetime
import subprocess

def check_emergency_stop():
    """Check if emergency stop is active"""
    emergency_file = Path('.claude-orchestra/control/emergency-stop.flag')
    return emergency_file.exists()

def read_status_file(filename):
    """Read a status file and return its content"""
    filepath = Path(f'.claude-orchestra/status/{filename}')
    if filepath.exists():
        with open(filepath, 'r') as f:
            return f.read()
    return f"❌ File not found: {filename}"

def get_git_status():
    """Get current git status"""
    try:
        result = subprocess.run(['git', 'status', '--short'], 
                              capture_output=True, text=True, cwd='.')
        return result.stdout.strip() if result.returncode == 0 else "❌ Git error"
    except:
        return "❌ Git not available"

def get_current_branch():
    """Get current git branch"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, cwd='.')
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"

def check_recent_errors():
    """Check for recent errors in logs"""
    error_log = Path('.claude-orchestra/logs/errors.log')
    if error_log.exists():
        with open(error_log, 'r') as f:
            lines = f.readlines()
            return lines[-5:] if lines else ["No recent errors"]
    return ["Error log not found"]

def get_system_health():
    """Get overall system health status"""
    health_indicators = {
        'emergency_stop': not check_emergency_stop(),
        'boundaries_config': Path('.claude-orchestra/control/boundaries.yaml').exists(),
        'status_files': all([
            Path('.claude-orchestra/status/current-phase.md').exists(),
            Path('.claude-orchestra/status/active-worker.md').exists(),
            Path('.claude-orchestra/status/task-queue.md').exists()
        ]),
        'scripts_available': all([
            Path('.claude-orchestra/scripts/check_boundaries.py').exists(),
            Path('.claude-orchestra/scripts/status_check.py').exists()
        ])
    }
    
    health_score = sum(health_indicators.values()) / len(health_indicators)
    
    if health_score == 1.0:
        return "🟢 HEALTHY"
    elif health_score >= 0.75:
        return "🟡 MOSTLY_HEALTHY"
    elif health_score >= 0.5:
        return "🟠 DEGRADED"
    else:
        return "🔴 CRITICAL"

def main():
    print("=" * 60)
    print("🎼 CLAUDE ORCHESTRA - SYSTEM STATUS CHECK")
    print("=" * 60)
    
    # Basic system info
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🌿 Git Branch: {get_current_branch()}")
    print()
    
    # Emergency status
    emergency_active = check_emergency_stop()
    emergency_status = "🚨 EMERGENCY STOP ACTIVE" if emergency_active else "✅ Normal Operation"
    print(f"🚨 Emergency Status: {emergency_status}")
    print()
    
    # System health
    health = get_system_health()
    print(f"🏥 System Health: {health}")
    print()
    
    # Current phase
    print("📋 CURRENT PHASE:")
    phase_content = read_status_file('current-phase.md')
    phase_lines = phase_content.split('\n')[:8]  # First 8 lines
    for line in phase_lines:
        if line.strip():
            print(f"   {line}")
    print()
    
    # Active worker
    print("👷 ACTIVE WORKER:")
    worker_content = read_status_file('active-worker.md')
    for line in worker_content.split('\n')[:6]:
        if line.strip() and ('CURRENT_WORKER' in line or 'STATUS' in line):
            print(f"   {line}")
    print()
    
    # Task queue summary
    print("📝 TASK QUEUE SUMMARY:")
    queue_content = read_status_file('task-queue.md')
    pending_tasks = queue_content.count('- [ ]')
    in_progress_tasks = queue_content.count('- [🔄]') 
    completed_tasks = queue_content.count('- [✅]')
    blocked_tasks = queue_content.count('- [🚫]')
    
    print(f"   📋 Pending: {pending_tasks}")
    print(f"   🔄 In Progress: {in_progress_tasks}")
    print(f"   ✅ Completed: {completed_tasks}")
    print(f"   🚫 Blocked: {blocked_tasks}")
    print()
    
    # Git status
    print("📊 GIT STATUS:")
    git_status = get_git_status()
    if git_status:
        for line in git_status.split('\n')[:10]:  # First 10 files
            print(f"   {line}")
        git_lines = git_status.split('\n')
        if len(git_lines) > 10:
            remaining_count = len(git_lines) - 10
            print(f"   ... and {remaining_count} more files")
    else:
        print("   No changes")
    print()
    
    # Recent errors
    print("🚨 RECENT ERRORS:")
    recent_errors = check_recent_errors()
    if recent_errors and recent_errors[0] != "No recent errors":
        for error in recent_errors:
            print(f"   {error.strip()}")
    else:
        print("   ✅ No recent errors")
    print()
    
    print("=" * 60)
    print("Status check complete. System ready for orchestration.")
    print("=" * 60)

if __name__ == '__main__':
    main()