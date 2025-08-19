#!/bin/bash
#
# Emergency Override Script - Claude Orchestra Git Safety System
# WORKER_3 PREP-001C Implementation
#
# This script provides emergency override capabilities for the Git safety system
# when critical operations need to bypass safety checks. Use with extreme caution.
#

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration paths
ORCHESTRA_DIR=".claude-orchestra"
EMERGENCY_FLAG="$ORCHESTRA_DIR/control/emergency-stop.flag"
LOGS_DIR="$ORCHESTRA_DIR/logs"
OVERRIDE_LOG="$LOGS_DIR/emergency-overrides.log"
GIT_HOOKS_DIR=".git/hooks"

# Function to print colored messages
print_colored() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to print header
print_header() {
    local title="$1"
    echo ""
    print_colored "$BLUE" "================================================================"
    print_colored "$WHITE" " $title"
    print_colored "$BLUE" "================================================================"
}

# Function to log override action
log_override() {
    local action="$1"
    local reason="$2"
    local user="${3:-unknown}"
    
    mkdir -p "$LOGS_DIR" 2>/dev/null || true
    
    {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] EMERGENCY_OVERRIDE: $action"
        echo "  User: $user"
        echo "  Reason: $reason"
        echo "  Git branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
        echo "  Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
        echo "  ---"
    } >> "$OVERRIDE_LOG"
}

# Function to show warning and get confirmation
get_user_confirmation() {
    local action="$1"
    
    print_colored "$RED" "⚠️  EMERGENCY OVERRIDE WARNING ⚠️"
    echo ""
    print_colored "$YELLOW" "You are about to perform an emergency override:"
    print_colored "$WHITE" "Action: $action"
    echo ""
    print_colored "$RED" "This will bypass ALL Git safety checks and orchestration protections!"
    print_colored "$RED" "This should only be used in genuine emergency situations."
    echo ""
    
    # Show current status
    if [ -f "$EMERGENCY_FLAG" ]; then
        print_colored "$RED" "🚨 Emergency stop is currently ACTIVE"
    else
        print_colored "$GREEN" "ℹ️  Emergency stop is not currently active"
    fi
    
    # Show active worker if any
    if [ -f "$ORCHESTRA_DIR/status/active-worker.md" ]; then
        current_worker=$(grep "CURRENT_WORKER:" "$ORCHESTRA_DIR/status/active-worker.md" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "unknown")
        if [ "$current_worker" != "NONE" ] && [ -n "$current_worker" ]; then
            print_colored "$YELLOW" "⚠️  Active worker detected: $current_worker"
        fi
    fi
    
    echo ""
    print_colored "$WHITE" "Do you want to proceed? (Type 'YES I UNDERSTAND' to confirm)"
    read -r confirmation
    
    if [ "$confirmation" != "YES I UNDERSTAND" ]; then
        print_colored "$BLUE" "Override cancelled. Exiting safely."
        exit 0
    fi
    
    echo ""
    print_colored "$WHITE" "Please provide a reason for this emergency override:"
    read -r reason
    
    if [ -z "$reason" ]; then
        print_colored "$RED" "A reason is required for emergency overrides."
        exit 1
    fi
    
    # Return the reason via a global variable (bash limitation workaround)
    OVERRIDE_REASON="$reason"
}

# Function to backup current Git hooks
backup_git_hooks() {
    local backup_dir="$GIT_HOOKS_DIR/emergency-backup-$(date '+%Y%m%d-%H%M%S')"
    
    if [ -d "$GIT_HOOKS_DIR" ]; then
        mkdir -p "$backup_dir"
        
        # Backup existing hooks
        for hook in pre-commit pre-push post-commit post-checkout; do
            if [ -f "$GIT_HOOKS_DIR/$hook" ]; then
                cp "$GIT_HOOKS_DIR/$hook" "$backup_dir/"
                print_colored "$BLUE" "  • Backed up $hook to $backup_dir/"
            fi
        done
        
        print_colored "$GREEN" "✅ Git hooks backed up to $backup_dir"
        echo "$backup_dir" > "$ORCHESTRA_DIR/.last-hook-backup"
    fi
}

# Function to temporarily disable Git hooks
disable_git_hooks() {
    print_colored "$YELLOW" "🔧 Temporarily disabling Git safety hooks..."
    
    # Backup first
    backup_git_hooks
    
    # Rename hooks to disable them
    for hook in pre-commit pre-push post-commit post-checkout; do
        if [ -f "$GIT_HOOKS_DIR/$hook" ]; then
            mv "$GIT_HOOKS_DIR/$hook" "$GIT_HOOKS_DIR/$hook.disabled"
            print_colored "$YELLOW" "  • Disabled $hook"
        fi
    done
    
    print_colored "$GREEN" "✅ Git hooks temporarily disabled"
}

# Function to re-enable Git hooks
enable_git_hooks() {
    print_colored "$BLUE" "🔧 Re-enabling Git safety hooks..."
    
    # Restore hooks from disabled state
    for hook in pre-commit pre-push post-commit post-checkout; do
        if [ -f "$GIT_HOOKS_DIR/$hook.disabled" ]; then
            mv "$GIT_HOOKS_DIR/$hook.disabled" "$GIT_HOOKS_DIR/$hook"
            print_colored "$GREEN" "  • Re-enabled $hook"
        fi
    done
    
    print_colored "$GREEN" "✅ Git hooks re-enabled"
}

# Function to restore Git hooks from backup
restore_git_hooks() {
    if [ -f "$ORCHESTRA_DIR/.last-hook-backup" ]; then
        local backup_dir
        backup_dir=$(cat "$ORCHESTRA_DIR/.last-hook-backup")
        
        if [ -d "$backup_dir" ]; then
            print_colored "$BLUE" "🔧 Restoring Git hooks from backup..."
            
            for hook in pre-commit pre-push post-commit post-checkout; do
                if [ -f "$backup_dir/$hook" ]; then
                    cp "$backup_dir/$hook" "$GIT_HOOKS_DIR/"
                    chmod +x "$GIT_HOOKS_DIR/$hook"
                    print_colored "$GREEN" "  • Restored $hook"
                fi
            done
            
            rm -f "$ORCHESTRA_DIR/.last-hook-backup"
            print_colored "$GREEN" "✅ Git hooks restored from backup"
        else
            print_colored "$RED" "❌ Backup directory not found: $backup_dir"
        fi
    else
        print_colored "$YELLOW" "⚠️  No backup file found - attempting to re-enable hooks"
        enable_git_hooks
    fi
}

# Function to force commit with override
force_commit() {
    local commit_message="$1"
    
    get_user_confirmation "Force commit bypassing all safety checks"
    
    print_colored "$RED" "🚨 PERFORMING EMERGENCY COMMIT OVERRIDE"
    
    # Log the override
    log_override "FORCE_COMMIT" "$OVERRIDE_REASON" "$(whoami)"
    
    # Disable hooks temporarily
    disable_git_hooks
    
    # Perform the commit
    print_colored "$BLUE" "📝 Performing commit with message: $commit_message"
    
    if git commit -m "$commit_message"; then
        print_colored "$GREEN" "✅ Emergency commit completed"
        
        # Log commit details
        commit_hash=$(git rev-parse --short HEAD)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] EMERGENCY_COMMIT: $commit_hash - $commit_message" >> "$OVERRIDE_LOG"
    else
        print_colored "$RED" "❌ Emergency commit failed"
    fi
    
    # Re-enable hooks
    restore_git_hooks
    
    print_colored "$YELLOW" "⚠️  EMERGENCY OVERRIDE COMPLETE - Please review the commit"
}

# Function to force push with override
force_push() {
    local remote="${1:-origin}"
    local branch="${2:-$(git branch --show-current)}"
    
    get_user_confirmation "Force push bypassing all safety checks"
    
    print_colored "$RED" "🚨 PERFORMING EMERGENCY PUSH OVERRIDE"
    
    # Log the override
    log_override "FORCE_PUSH" "$OVERRIDE_REASON" "$(whoami)"
    
    # Disable hooks temporarily
    disable_git_hooks
    
    # Perform the push
    print_colored "$BLUE" "🚀 Performing push to $remote/$branch"
    
    if git push "$remote" "$branch"; then
        print_colored "$GREEN" "✅ Emergency push completed"
        
        # Log push details
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] EMERGENCY_PUSH: $remote/$branch" >> "$OVERRIDE_LOG"
    else
        print_colored "$RED" "❌ Emergency push failed"
    fi
    
    # Re-enable hooks
    restore_git_hooks
    
    print_colored "$YELLOW" "⚠️  EMERGENCY OVERRIDE COMPLETE - Please review the push"
}

# Function to clear emergency stop
clear_emergency_stop() {
    if [ ! -f "$EMERGENCY_FLAG" ]; then
        print_colored "$GREEN" "ℹ️  Emergency stop is not currently active"
        return 0
    fi
    
    get_user_confirmation "Clear emergency stop flag"
    
    # Log the override
    log_override "CLEAR_EMERGENCY_STOP" "$OVERRIDE_REASON" "$(whoami)"
    
    # Remove emergency stop flag
    rm -f "$EMERGENCY_FLAG"
    
    # Update active worker status if needed
    if [ -f "$ORCHESTRA_DIR/status/active-worker.md" ]; then
        sed -i.bak 's/EMERGENCY_STOP_ACTIVE/SYSTEM_READY/' "$ORCHESTRA_DIR/status/active-worker.md" 2>/dev/null || true
        rm -f "$ORCHESTRA_DIR/status/active-worker.md.bak" 2>/dev/null || true
    fi
    
    print_colored "$GREEN" "✅ Emergency stop cleared"
    print_colored "$BLUE" "💡 System is now ready for normal operations"
    
    # Log in orchestration system
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] EMERGENCY_STOP_CLEARED: System ready for operations" >> "$LOGS_DIR/orchestration.log"
}

# Function to show emergency status
show_emergency_status() {
    print_header "Emergency System Status"
    
    # Emergency stop status
    if [ -f "$EMERGENCY_FLAG" ]; then
        print_colored "$RED" "🚨 Emergency stop: ACTIVE"
        if [ -s "$EMERGENCY_FLAG" ]; then
            echo "  Reason: $(cat "$EMERGENCY_FLAG")"
        fi
    else
        print_colored "$GREEN" "✅ Emergency stop: Not active"
    fi
    
    # Active worker status
    if [ -f "$ORCHESTRA_DIR/status/active-worker.md" ]; then
        current_worker=$(grep "CURRENT_WORKER:" "$ORCHESTRA_DIR/status/active-worker.md" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "unknown")
        system_status=$(grep "STATUS:" "$ORCHESTRA_DIR/status/active-worker.md" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "unknown")
        
        print_colored "$BLUE" "👤 Current worker: $current_worker"
        print_colored "$BLUE" "📊 System status: $system_status"
    fi
    
    # Git hooks status
    print_colored "$BLUE" "🔧 Git hooks status:"
    for hook in pre-commit pre-push post-commit post-checkout; do
        if [ -f "$GIT_HOOKS_DIR/$hook" ]; then
            if [ -x "$GIT_HOOKS_DIR/$hook" ]; then
                print_colored "$GREEN" "  ✅ $hook: Active"
            else
                print_colored "$YELLOW" "  ⚠️  $hook: Not executable"
            fi
        elif [ -f "$GIT_HOOKS_DIR/$hook.disabled" ]; then
            print_colored "$RED" "  🚫 $hook: Disabled"
        else
            print_colored "$YELLOW" "  ❓ $hook: Not found"
        fi
    done
    
    # Recent overrides
    if [ -f "$OVERRIDE_LOG" ]; then
        print_colored "$BLUE" "📝 Recent emergency overrides:"
        tail -5 "$OVERRIDE_LOG" 2>/dev/null || echo "  No recent overrides"
    fi
}

# Function to show help
show_help() {
    print_header "Emergency Override Script Help"
    
    print_colored "$WHITE" "Usage: $0 [command] [options]"
    echo ""
    print_colored "$YELLOW" "Available commands:"
    print_colored "$CYAN" "  commit [message]     Force commit bypassing all safety checks"
    print_colored "$CYAN" "  push [remote] [branch]   Force push bypassing all safety checks"
    print_colored "$CYAN" "  clear-stop          Clear emergency stop flag"
    print_colored "$CYAN" "  disable-hooks       Temporarily disable Git safety hooks"
    print_colored "$CYAN" "  enable-hooks        Re-enable Git safety hooks"
    print_colored "$CYAN" "  restore-hooks       Restore hooks from latest backup"
    print_colored "$CYAN" "  status              Show emergency system status"
    print_colored "$CYAN" "  help                Show this help message"
    echo ""
    print_colored "$RED" "⚠️  WARNING: These commands bypass all safety protections!"
    print_colored "$YELLOW" "Only use in genuine emergencies and always provide a reason."
    echo ""
    print_colored "$BLUE" "Examples:"
    print_colored "$WHITE" "  $0 commit \"Emergency fix for production issue\""
    print_colored "$WHITE" "  $0 push origin main"
    print_colored "$WHITE" "  $0 clear-stop"
    print_colored "$WHITE" "  $0 status"
}

# Main script logic
main() {
    local command="${1:-help}"
    
    case "$command" in
        "commit")
            local message="${2:-Emergency commit via override}"
            force_commit "$message"
            ;;
            
        "push")
            local remote="${2:-origin}"
            local branch="${3:-$(git branch --show-current)}"
            force_push "$remote" "$branch"
            ;;
            
        "clear-stop")
            clear_emergency_stop
            ;;
            
        "disable-hooks")
            get_user_confirmation "Disable Git safety hooks"
            log_override "DISABLE_HOOKS" "$OVERRIDE_REASON" "$(whoami)"
            disable_git_hooks
            ;;
            
        "enable-hooks")
            enable_git_hooks
            print_colored "$BLUE" "💡 Hooks re-enabled - normal safety checks active"
            ;;
            
        "restore-hooks")
            restore_git_hooks
            print_colored "$BLUE" "💡 Hooks restored - normal safety checks active"
            ;;
            
        "status")
            show_emergency_status
            ;;
            
        "help"|"--help"|"-h")
            show_help
            ;;
            
        *)
            print_colored "$RED" "❌ Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ensure we're in the right directory
if [ ! -d ".git" ] || [ ! -d "$ORCHESTRA_DIR" ]; then
    print_colored "$RED" "❌ This script must be run from the repository root with orchestration system"
    exit 1
fi

# Run main function with all arguments
main "$@"