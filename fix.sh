#!/bin/bash

# Emergency Fix Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

PRODUCTION_URL="https://telbot-f4on.onrender.com"

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo ""
echo -e "${BOLD}${RED}🚨 EMERGENCY FIX TOOL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check what's wrong
print_info "Diagnosing issues..."

# Check if production is down
if ! curl -s -f -m 5 "$PRODUCTION_URL/health" > /dev/null 2>&1; then
    print_error "Production is down!"
    echo ""
    echo "Possible fixes:"
    echo "1. Rollback to previous version"
    echo "2. Restart the service"
    echo "3. Check error logs"
    echo "4. Redeploy from main branch"
    echo ""
    
    read -p "Choose an option (1-4): " choice
    
    case $choice in
        1)
            print_info "Rolling back..."
            ./deploy.sh rollback
            ;;
        2)
            print_info "Restarting service..."
            print_warning "This requires Render API access"
            echo "Go to: https://dashboard.render.com"
            echo "Click on your service → Manual Deploy → Deploy"
            ;;
        3)
            print_info "Checking logs..."
            ./logs.sh production
            ;;
        4)
            print_info "Redeploying from main..."
            git checkout main
            git pull origin main
            ./deploy.sh production
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
else
    print_success "Production is healthy!"
    
    # Check for other issues
    echo ""
    print_info "Running diagnostics..."
    
    # Check database
    echo -n "Database connection: "
    if curl -s "$PRODUCTION_URL/health" | grep -q "database.*healthy"; then
        print_success "OK"
    else
        print_warning "Issues detected"
    fi
    
    # Check bot
    echo -n "Telegram bot: "
    if curl -s "$PRODUCTION_URL/health" | grep -q "telegram.*healthy"; then
        print_success "OK"
    else
        print_warning "Issues detected"
    fi
    
    echo ""
    echo "Common fixes:"
    echo "• Clear cache: git clean -fd"
    echo "• Update deps: pip install -r requirements.txt"
    echo "• Reset branch: git reset --hard origin/main"
    echo "• View logs: ./logs.sh production"
fi

echo ""
