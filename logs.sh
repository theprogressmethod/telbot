#!/bin/bash

# Simple Logs Viewer

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Get environment
ENV=${1:-production}

echo ""
echo -e "${BOLD}${BLUE}📜 LOGS VIEWER${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

case "$ENV" in
    production|prod)
        print_info "Fetching production logs..."
        echo ""
        echo "Options:"
        echo "1. View in Render Dashboard"
        echo "2. View local log files"
        echo "3. View error logs only"
        echo ""
        
        read -p "Choose option (1-3): " choice
        
        case $choice in
            1)
                print_info "Opening Render dashboard..."
                echo "Go to: https://dashboard.render.com"
                echo "Select your service → Logs"
                ;;
            2)
                if [ -d "logs" ]; then
                    print_info "Recent logs:"
                    tail -n 50 logs/app-production.log 2>/dev/null || echo "No production logs found"
                else
                    echo "No local logs directory found"
                fi
                ;;
            3)
                if [ -f "logs/errors-production.log" ]; then
                    print_info "Recent errors:"
                    tail -n 30 logs/errors-production.log
                else
                    echo "No error logs found"
                fi
                ;;
        esac
        ;;
        
    staging)
        print_info "Fetching staging logs..."
        if [ -d "logs" ]; then
            tail -n 50 logs/app-staging.log 2>/dev/null || echo "No staging logs found"
        else
            echo "Go to: https://dashboard.render.com"
            echo "Select staging service → Logs"
        fi
        ;;
        
    local)
        print_info "Local logs:"
        if [ -d "logs" ]; then
            ls -la logs/
            echo ""
            echo "Most recent entries:"
            tail -n 30 logs/app-development.log 2>/dev/null || echo "No local logs"
        else
            echo "No logs directory found. Run the app first."
        fi
        ;;
        
    *)
        echo "Usage: ./logs.sh [production|staging|local]"
        echo ""
        echo "Examples:"
        echo "  ./logs.sh production  - View production logs"
        echo "  ./logs.sh staging     - View staging logs"
        echo "  ./logs.sh local       - View local development logs"
        ;;
esac

echo ""
