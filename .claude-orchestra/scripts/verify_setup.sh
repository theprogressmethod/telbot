#!/bin/bash
# Claude Orchestra Setup Verification Script

echo "🎼 CLAUDE ORCHESTRA - SETUP VERIFICATION"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "✅ ${GREEN}$1${NC}"
    else
        echo -e "❌ ${RED}$1 - MISSING${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "✅ ${GREEN}$1/${NC}"
    else
        echo -e "❌ ${RED}$1/ - MISSING${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "📁 DIRECTORY STRUCTURE:"
check_dir ".claude-orchestra"
check_dir ".claude-orchestra/status"
check_dir ".claude-orchestra/control"
check_dir ".claude-orchestra/logs"
check_dir ".claude-orchestra/scripts"
check_dir ".claude-orchestra/contexts"
check_dir ".claude-orchestra/templates"

echo ""
echo "📋 STATUS FILES:"
check_file ".claude-orchestra/status/current-phase.md"
check_file ".claude-orchestra/status/active-worker.md"
check_file ".claude-orchestra/status/task-queue.md"
check_file ".claude-orchestra/status/system-health.md"
check_file ".claude-orchestra/status/completed-tasks.md"

echo ""
echo "⚙️  CONTROL FILES:"
check_file ".claude-orchestra/control/boundaries.yaml"
check_file ".claude-orchestra/control/current-environment.yaml"
check_file ".claude-orchestra/control/emergency-stop.flag.disabled"

echo ""
echo "🔧 SCRIPTS:"
check_file ".claude-orchestra/scripts/check_boundaries.py"
check_file ".claude-orchestra/scripts/status_check.py"

echo ""
echo "📝 LOG FILES:"
check_file ".claude-orchestra/logs/orchestration.log"
check_file ".claude-orchestra/logs/recent-work.log"
check_file ".claude-orchestra/logs/errors.log"
check_file ".claude-orchestra/logs/deployments.log"

echo ""
echo "📄 TEMPLATES:"
check_file ".claude-orchestra/contexts/worker-template.md"

echo ""
echo "🔍 FUNCTIONAL TESTS:"

# Test Python scripts
if command -v python3 &> /dev/null; then
    echo -e "✅ ${GREEN}Python3 available${NC}"
    
    # Test boundary checker
    if python3 .claude-orchestra/scripts/check_boundaries.py --worker WORKER_1 telbot.py &> /dev/null; then
        echo -e "✅ ${GREEN}Boundary checker functional${NC}"
    else
        echo -e "❌ ${RED}Boundary checker failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Test status checker
    if python3 .claude-orchestra/scripts/status_check.py &> /dev/null; then
        echo -e "✅ ${GREEN}Status checker functional${NC}"
    else
        echo -e "❌ ${RED}Status checker failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "❌ ${RED}Python3 not available${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test git availability
if command -v git &> /dev/null; then
    echo -e "✅ ${GREEN}Git available${NC}"
else
    echo -e "❌ ${RED}Git not available${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test YAML dependency
if python3 -c "import yaml" &> /dev/null; then
    echo -e "✅ ${GREEN}PyYAML available${NC}"
else
    echo -e "⚠️  ${YELLOW}PyYAML not available - install with: pip install pyyaml${NC}"
fi

echo ""
echo "========================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "🎉 ${GREEN}SETUP VERIFICATION COMPLETE - ALL SYSTEMS GO!${NC}"
    echo ""
    echo "🚀 Ready to assign first worker. Run:"
    echo "   python .claude-orchestra/scripts/status_check.py"
    exit 0
else
    echo -e "💥 ${RED}SETUP VERIFICATION FAILED - $ERRORS ERRORS FOUND${NC}"
    echo ""
    echo "🔧 Please fix the missing files/directories and run again."
    exit 1
fi