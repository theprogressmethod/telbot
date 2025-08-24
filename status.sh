#!/bin/bash

# Status Dashboard Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# URLs
PRODUCTION_URL="https://telbot-f4on.onrender.com"
STAGING_URL="https://telbot-staging.onrender.com"

print_success() { echo -e "${GREEN}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_info() { echo -e "${BLUE}$1${NC}"; }

echo ""
echo -e "${BOLD}${BLUE}📊 DEPLOYMENT STATUS DASHBOARD${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Production
echo -e "${BOLD}PRODUCTION${NC}"
if curl -s -f -m 5 "$PRODUCTION_URL/health" > /dev/null 2>&1; then
    print_success "✅ Healthy"
    
    # Get detailed health if possible
    health_data=$(curl -s "$PRODUCTION_URL/health" 2>/dev/null)
    if [ ! -z "$health_data" ]; then
        echo "$health_data" | python3 -m json.tool 2>/dev/null | head -20 || true
    fi
else
    print_error "❌ Down or unreachable"
fi
echo ""

# Check Staging
echo -e "${BOLD}STAGING${NC}"
if curl -s -f -m 5 "$STAGING_URL/health" > /dev/null 2>&1; then
    print_success "✅ Healthy"
else
    print_warning "⚠️  Down or unreachable"
fi
echo ""

# Git Status
echo -e "${BOLD}GIT STATUS${NC}"
branch=$(git branch --show-current 2>/dev/null)
echo "Current branch: $branch"
echo "Latest commits:"
git log --oneline -5 2>/dev/null || echo "Unable to get git log"
echo ""

# Check for uncommitted changes
if git diff-index --quiet HEAD -- 2>/dev/null; then
    print_success "✅ No uncommitted changes"
else
    print_warning "⚠️  You have uncommitted changes"
fi
echo ""

# Quick Actions
echo -e "${BOLD}QUICK ACTIONS${NC}"
echo "• Deploy to staging:     ./deploy.sh staging"
echo "• Deploy to production:  ./deploy.sh production"
echo "• View logs:            ./logs.sh production"
echo "• Fix issues:           ./fix.sh"
echo ""
