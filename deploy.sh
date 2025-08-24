#!/bin/bash

# Super Simple Deployment Script
# Usage: ./deploy.sh [staging|production|test|status|rollback]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Config
STAGING_URL="https://telbot-staging.onrender.com"
PRODUCTION_URL="https://telbot-f4on.onrender.com"

# Functions
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Deploy to staging
deploy_staging() {
    print_header "🚀 DEPLOYING TO STAGING"
    
    print_info "Checking branch..."
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "develop" ]]; then
        print_warning "Not on develop branch (currently on $current_branch)"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_info "Running tests..."
    if [ -f "run_test.sh" ]; then
        ./run_test.sh || { print_error "Tests failed!"; exit 1; }
    else
        print_warning "No test script found, skipping tests"
    fi
    
    print_info "Pushing to GitHub..."
    git push origin develop
    
    print_success "Deployment triggered!"
    print_info "Monitor at: $STAGING_URL"
    print_info "Logs: ./logs.sh staging"
}

# Deploy to production
deploy_production() {
    print_header "🚀 DEPLOYING TO PRODUCTION"
    
    print_warning "PRODUCTION DEPLOYMENT"
    read -p "Are you absolutely sure? Type 'yes' to continue: " confirm
    if [[ "$confirm" != "yes" ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
    
    print_info "Checking branch..."
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        print_error "Must be on main branch for production (currently on $current_branch)"
        exit 1
    fi
    
    print_info "Pulling latest changes..."
    git pull origin main
    
    print_info "Running tests..."
    if [ -f "run_test.sh" ]; then
        ./run_test.sh || { print_error "Tests failed!"; exit 1; }
    fi
    
    print_info "Creating backup tag..."
    timestamp=$(date +%Y%m%d-%H%M%S)
    git tag -a "backup-$timestamp" -m "Backup before production deployment"
    
    print_info "Pushing to production..."
    git push origin main --tags
    
    print_success "Production deployment triggered!"
    print_info "Monitor at: $PRODUCTION_URL"
    print_info "Check health: curl $PRODUCTION_URL/health"
}

# Run tests
run_tests() {
    print_header "🧪 RUNNING TESTS"
    
    if [ -f "run_test.sh" ]; then
        ./run_test.sh
    elif [ -d "tests" ]; then
        python -m pytest tests/ -v
    else
        print_warning "No tests found"
    fi
}

# Check status
check_status() {
    print_header "📊 DEPLOYMENT STATUS"
    
    print_info "Checking production..."
    if curl -s -f "$PRODUCTION_URL/health" > /dev/null 2>&1; then
        print_success "Production is healthy"
    else
        print_error "Production health check failed"
    fi
    
    print_info "Checking staging..."
    if curl -s -f "$STAGING_URL/health" > /dev/null 2>&1; then
        print_success "Staging is healthy"
    else
        print_warning "Staging health check failed"
    fi
    
    print_info "Recent commits:"
    git log --oneline -5
    
    print_info "Current branch: $(git branch --show-current)"
}

# Rollback
rollback() {
    print_header "🔄 ROLLBACK"
    
    print_warning "This will rollback to the previous version"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    print_info "Finding last backup tag..."
    last_tag=$(git tag -l "backup-*" | sort -r | head -1)
    
    if [ -z "$last_tag" ]; then
        print_error "No backup tags found"
        print_info "Manual rollback: git reset --hard <commit-hash>"
        exit 1
    fi
    
    print_info "Rolling back to: $last_tag"
    git checkout "$last_tag"
    git push origin main --force
    
    print_success "Rollback complete!"
    print_warning "Remember to investigate what went wrong"
}

# Main script
case "$1" in
    staging)
        deploy_staging
        ;;
    production|prod)
        deploy_production
        ;;
    test)
        run_tests
        ;;
    status)
        check_status
        ;;
    rollback)
        rollback
        ;;
    *)
        echo "🚀 Simple Deployment Tool"
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  staging    - Deploy to staging environment"
        echo "  production - Deploy to production (requires main branch)"
        echo "  test       - Run tests locally"
        echo "  status     - Check deployment status"
        echo "  rollback   - Rollback to previous version"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh staging"
        echo "  ./deploy.sh production"
        echo "  ./deploy.sh status"
        ;;
esac
