#!/bin/bash

# =====================================================
# THE PROGRESS METHOD - DEPLOYMENT SCRIPT
# =====================================================
# Automated deployment helper for staging/production
# Usage: ./deploy.sh [staging|production]
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="telbot"
CURRENT_BRANCH=$(git branch --show-current)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if git is clean
    if [[ -n $(git status -s) ]]; then
        print_warning "You have uncommitted changes. Please commit or stash them first."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python version: $python_version"
    
    # Check if requirements file exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Run basic health checks
    python3 -c "import telbot; print('✓ Bot module loads')" || {
        print_error "Bot module failed to load"
        exit 1
    }
    
    # Check database connection
    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
if url and key:
    client = create_client(url, key)
    print('✓ Database connection OK')
else:
    print('✗ Database credentials missing')
    exit(1)
" || {
        print_error "Database connection failed"
        exit 1
    }
    
    print_success "Tests passed"
}

# Function to deploy to staging
deploy_staging() {
    print_status "🚀 Deploying to STAGING..."
    
    # Check if .env.staging exists
    if [ ! -f ".env.staging" ]; then
        print_error ".env.staging not found! Create it first."
        exit 1
    fi
    
    # Create/switch to staging branch
    git checkout -b staging 2>/dev/null || git checkout staging
    
    # Merge current branch
    print_status "Merging $CURRENT_BRANCH into staging..."
    git merge $CURRENT_BRANCH --no-edit
    
    # Push to remote
    print_status "Pushing to remote staging branch..."
    git push origin staging
    
    print_success "Staging deployment initiated!"
    print_warning "Remember to:"
    echo "  1. Set environment variables in Render dashboard"
    echo "  2. Trigger manual deploy if auto-deploy is disabled"
    echo "  3. Monitor build logs"
    echo "  4. Test all functionality"
}

# Function to deploy to production
deploy_production() {
    print_status "🚀 Deploying to PRODUCTION..."
    
    # Confirmation
    echo -e "${RED}⚠️  WARNING: You are about to deploy to PRODUCTION!${NC}"
    read -p "Have you tested everything in staging? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_error "Deployment cancelled"
        exit 1
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_error ".env.production not found! Create it first."
        exit 1
    fi
    
    # Create backup tag
    print_status "Creating backup tag..."
    git tag -a "backup-$TIMESTAMP" -m "Backup before production deployment"
    git push origin "backup-$TIMESTAMP"
    
    # Switch to main branch
    git checkout main
    
    # Merge staging into main
    print_status "Merging staging into main..."
    git merge staging --no-edit
    
    # Push to remote
    print_status "Pushing to main branch..."
    git push origin main
    
    print_success "Production deployment initiated!"
    print_warning "CRITICAL: Monitor the deployment closely!"
    echo "  1. Check Render build logs"
    echo "  2. Verify health checks"
    echo "  3. Test bot commands"
    echo "  4. Check dashboard access"
    echo "  5. Monitor error logs"
}

# Function to rollback
rollback() {
    print_error "🔄 Initiating ROLLBACK..."
    
    # Get last backup tag
    last_backup=$(git tag -l "backup-*" | tail -1)
    
    if [ -z "$last_backup" ]; then
        print_error "No backup tags found!"
        exit 1
    fi
    
    print_warning "Rolling back to: $last_backup"
    read -p "Confirm rollback? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_error "Rollback cancelled"
        exit 1
    fi
    
    # Reset to backup
    git checkout main
    git reset --hard $last_backup
    git push origin main --force
    
    print_success "Rollback completed to $last_backup"
    print_warning "Remember to investigate what went wrong!"
}

# Function to check deployment status
check_status() {
    print_status "Checking deployment status..."
    
    # Check local services
    echo "Local services:"
    ps aux | grep -E "python.*(main_week1|run_week1|telbot)" | grep -v grep || echo "  No local services running"
    
    # Check if production endpoints are responding
    if [ "$1" == "production" ]; then
        echo -e "\nProduction endpoints:"
        
        # Check bot webhook
        curl -s -o /dev/null -w "  Bot API: %{http_code}\n" https://api.theprogressmethod.com/health || echo "  Bot API: Not responding"
        
        # Check dashboard
        curl -s -o /dev/null -w "  Dashboard: %{http_code}\n" https://app.theprogressmethod.com/health || echo "  Dashboard: Not responding"
    fi
    
    print_success "Status check complete"
}

# Main script
echo "======================================"
echo "  THE PROGRESS METHOD DEPLOYMENT"
echo "======================================"
echo "Environment: $1"
echo "Current branch: $CURRENT_BRANCH"
echo "Timestamp: $TIMESTAMP"
echo "======================================"
echo ""

# Check command line arguments
if [ $# -eq 0 ]; then
    print_error "Usage: ./deploy.sh [staging|production|rollback|status]"
    exit 1
fi

# Run appropriate deployment
case $1 in
    staging)
        check_prerequisites
        run_tests
        deploy_staging
        ;;
    production)
        check_prerequisites
        run_tests
        deploy_production
        ;;
    rollback)
        rollback
        ;;
    status)
        check_status $2
        ;;
    *)
        print_error "Invalid option: $1"
        echo "Usage: ./deploy.sh [staging|production|rollback|status]"
        exit 1
        ;;
esac

echo ""
echo "======================================"
print_success "Deployment script completed"
echo "======================================" 