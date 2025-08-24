#!/bin/bash

# Render Services Configuration Script
# Updates branch mappings and environment variables

set -e

echo "🔧 Configuring Render Services"
echo "=============================="

RENDER_API_KEY="rnd_6MZiXVnDM2svzQjEM0bpa9XKBH8W"
API_URL="https://api.render.com/v1"

# Function to update service
update_service() {
    local SERVICE_ID=$1
    local SERVICE_NAME=$2
    local BRANCH=$3
    local ENV=$4
    
    echo ""
    echo "Updating $SERVICE_NAME..."
    echo "  Service ID: $SERVICE_ID"
    echo "  Branch: $BRANCH"
    echo "  Environment: $ENV"
    
    # Note: Render API doesn't support branch updates directly
    # You'll need to do this in the dashboard
    echo "  ⚠️  Please update branch mapping in Render Dashboard:"
    echo "     https://dashboard.render.com/web/$SERVICE_ID/settings"
    echo "     Set Auto-Deploy Branch to: $BRANCH"
}

# Update service configurations
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "MANUAL STEPS REQUIRED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

update_service "srv-d2em4oripnbc73a5bmog" "telbot-dev" "development" "development"
update_service "srv-d2ftel8gjchc73aekca0" "telbot-staging" "staging" "staging"
update_service "srv-d2h9ckggjchc73bumn60" "telbot-production" "master" "production"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ENVIRONMENT VARIABLES TO SET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📝 For telbot-dev (srv-d2em4oripnbc73a5bmog):"
echo "   ENVIRONMENT=development"
echo "   SUPABASE_URL=https://apfiwfkpdhslfavnncsl.supabase.co"
echo "   SUPABASE_ANON_KEY=<your-dev-anon-key>"
echo "   SUPABASE_SERVICE_KEY=<your-dev-service-key>"
echo "   TELEGRAM_BOT_TOKEN=8279715319:AAGQ-Jkz6Uf2R07orzZvsOXG7Eo8OHahb_w"
echo "   WEBHOOK_URL=https://telbot-dev.onrender.com/webhook"
echo "   LOG_LEVEL=DEBUG"

echo ""
echo "📝 For telbot-staging (srv-d2ftel8gjchc73aekca0):"
echo "   ENVIRONMENT=staging"
echo "   SUPABASE_URL=https://apfiwfkpdhslfavnncsl.supabase.co"
echo "   SUPABASE_ANON_KEY=<your-dev-anon-key>"
echo "   SUPABASE_SERVICE_KEY=<your-dev-service-key>"
echo "   TELEGRAM_BOT_TOKEN=8279715319:AAGQ-Jkz6Uf2R07orzZvsOXG7Eo8OHahb_w"
echo "   WEBHOOK_URL=https://telbot-staging.onrender.com/webhook"
echo "   LOG_LEVEL=INFO"

echo ""
echo "📝 For telbot-production (srv-d2h9ckggjchc73bumn60):"
echo "   ENVIRONMENT=production"
echo "   SUPABASE_URL=https://prtfkiodnbogqfcztruj.supabase.co"
echo "   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBydGZraW9kbmJvZ3FmY3p0cnVqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NzkwNzAsImV4cCI6MjA2ODU1NTA3MH0.PCmuGW__7PHOFuR0nMBnZUHwBLzNqdkyELIULHA2Zk8"
echo "   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBydGZraW9kbmJvZ3FmY3p0cnVqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjk3OTA3MCwiZXhwIjoyMDY4NTU1MDcwfQ.NvoMj7-PTZrflHDPDRxpD8b4cYwLj9-Xcacz5VLPoo8"
echo "   TELEGRAM_BOT_TOKEN=8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0"
echo "   WEBHOOK_URL=https://telbot-production.onrender.com/webhook"
echo "   LOG_LEVEL=WARNING"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "QUICK LINKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 telbot-dev:"
echo "   https://dashboard.render.com/web/srv-d2em4oripnbc73a5bmog/settings"
echo ""
echo "🔗 telbot-staging:"
echo "   https://dashboard.render.com/web/srv-d2ftel8gjchc73aekca0/settings"
echo ""
echo "🔗 telbot-production:"
echo "   https://dashboard.render.com/web/srv-d2h9ckggjchc73bumn60/settings"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  IMPORTANT ACTIONS REQUIRED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open each link above"
echo "2. Update 'Auto-Deploy Branch' to the correct branch"
echo "3. Add/Update environment variables listed above"
echo "4. Click 'Save Changes'"
echo "5. Trigger a manual deploy to apply changes"
echo ""
echo "This needs to be done manually in the Render Dashboard"
echo "as the API doesn't support branch updates."
