#!/bin/bash

# One-Time Setup Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo ""
echo -e "${BLUE}🚀 TELBOT DEPLOYMENT SETUP${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    print_success "Python3 installed"
else
    print_error "Python3 not installed"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_success "Git installed"
else
    print_error "Git not installed"
    exit 1
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "No requirements.txt found"
fi

# Create .env files if missing
if [ ! -f ".env.production" ]; then
    print_info "Creating .env.production template..."
    echo "# Production Environment" > .env.production
    echo "ENVIRONMENT=production" >> .env.production
    echo "DATABASE_URL=" >> .env.production
    echo "TELEGRAM_BOT_TOKEN=" >> .env.production
    echo "SENTRY_DSN=" >> .env.production
    print_success "Created .env.production"
    print_warning "Edit .env.production with your credentials"
fi

# Make scripts executable
chmod +x deploy.sh 2>/dev/null || true
chmod +x status.sh 2>/dev/null || true
chmod +x fix.sh 2>/dev/null || true
chmod +x logs.sh 2>/dev/null || true

print_success "Scripts made executable"

# Setup git hooks
if [ -d ".git" ]; then
    print_info "Setting up git hooks..."
    echo '#!/bin/bash' > .git/hooks/pre-push
    echo 'echo "Running tests before push..."' >> .git/hooks/pre-push
    echo './deploy.sh test' >> .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    print_success "Git hooks configured"
fi

echo ""
print_success "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.production with your API keys"
echo "2. Run: ./deploy.sh status"
echo "3. Deploy: ./deploy.sh staging"
echo ""
