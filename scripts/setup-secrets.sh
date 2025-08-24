#!/bin/bash

# GitHub Secrets Setup Script
# Run this to configure all CI/CD secrets

echo "🔐 Setting up GitHub Secrets for TelBot"
echo "========================================"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
fi

# Authenticate if needed
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi

REPO="theprogressmethod/telbot"

# Function to set secret
set_secret() {
    echo "Setting secret: $1"
    echo "$2" | gh secret set "$1" --repo "$REPO" 2>/dev/null || echo "  ✓ Secret $1 updated"
}

echo ""
echo "📝 Adding secrets to repository: $REPO"
echo ""

# Get Anthropic API Key
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣ ANTHROPIC API KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Get your key from: https://console.anthropic.com/settings/keys"
echo "Leave empty to skip (you can add it later)"
read -p "Enter Anthropic API Key: " ANTHROPIC_KEY
if [ ! -z "$ANTHROPIC_KEY" ]; then
    set_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_KEY"
    echo "  ✅ Anthropic API Key set"
else
    echo "  ⏭️ Skipped - Add manually later"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣ RENDER API KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
set_secret "RENDER_API_KEY" "rnd_6MZiXVnDM2svzQjEM0bpa9XKBH8W"
echo "  ✅ Render API Key set"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣ TELEGRAM BOT TOKENS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
set_secret "TELEGRAM_BOT_TOKEN" "8279715319:AAGQ-Jkz6Uf2R07orzZvsOXG7Eo8OHahb_w"
set_secret "TELEGRAM_BOT_TOKEN_PROD" "8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0"
echo "  ✅ Telegram Bot Tokens set (Dev & Prod)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣ TELEGRAM CHAT ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
set_secret "TELEGRAM_CHAT_ID" "16861999"
echo "  ✅ Telegram Chat ID set"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣ AXIOM MONITORING (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
set_secret "AXIOM_TOKEN" "xaat-6ec790a0-6eb6-408f-8e3d-089782d5339d"
set_secret "AXIOM_ORG_ID" "telbot-org"
echo "  ✅ Axiom monitoring configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣ SUPABASE CREDENTIALS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Development Supabase
set_secret "SUPABASE_URL_DEV" "https://apfiwfkpdhslfavnncsl.supabase.co"
set_secret "SUPABASE_ANON_KEY_DEV" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZml3ZmtwZGhzbGZhdm5uY3NsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzM0ODE2MDAsImV4cCI6MTk4OTA1NzYwMH0.YOUR_DEV_ANON_KEY"
set_secret "SUPABASE_SERVICE_KEY_DEV" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwZml3ZmtwZGhzbGZhdm5uY3NsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY3MzQ4MTYwMCwiZXhwIjoxOTg5MDU3NjAwfQ.YOUR_DEV_SERVICE_KEY"

# Production Supabase
set_secret "SUPABASE_URL_PROD" "https://prtfkiodnbogqfcztruj.supabase.co"
set_secret "SUPABASE_ANON_KEY_PROD" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBydGZraW9kbmJvZ3FmY3p0cnVqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzkwNzAsImV4cCI6MjA2ODU1NTA3MH0.PCmuGW__7PHOFuR0nMBnZUHwBLzNqdkyELIULHA2Zk8"
set_secret "SUPABASE_SERVICE_KEY_PROD" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBydGZraW9kbmJvZ3FmY3p0cnVqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjk3OTA3MCwiZXhwIjoyMDY4NTU1MDcwfQ.NvoMj7-PTZrflHDPDRxpD8b4cYwLj9-Xcacz5VLPoo8"

echo "  ✅ Supabase credentials set (Dev & Prod)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣ CLAUDE CODE OAUTH (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "For automated PR reviews by Claude"
echo "Get from: https://github.com/settings/tokens"
read -p "Enter Claude Code OAuth Token (or press Enter to skip): " CLAUDE_TOKEN
if [ ! -z "$CLAUDE_TOKEN" ]; then
    set_secret "CLAUDE_CODE_OAUTH_TOKEN" "$CLAUDE_TOKEN"
    echo "  ✅ Claude Code OAuth set"
else
    echo "  ⏭️ Skipped - PR reviews will not work"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Secrets configured:"
echo "  ✓ Render API Key"
echo "  ✓ Telegram Bot Tokens (Dev & Prod)"
echo "  ✓ Telegram Chat ID"
echo "  ✓ Axiom Monitoring"
echo "  ✓ Supabase Credentials (Dev & Prod)"
if [ ! -z "$ANTHROPIC_KEY" ]; then
    echo "  ✓ Anthropic API Key"
fi
if [ ! -z "$CLAUDE_TOKEN" ]; then
    echo "  ✓ Claude Code OAuth"
fi

echo ""
echo "📝 Next steps:"
echo "1. Add Anthropic API Key if you haven't already"
echo "2. Run: ./scripts/setup-secrets.sh"
echo "3. Verify in GitHub: Settings → Secrets → Actions"
echo ""
echo "🚀 Ready to deploy!"
