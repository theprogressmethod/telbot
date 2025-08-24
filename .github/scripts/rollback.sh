#!/bin/bash
# Rollback Automation Script

echo "🔄 Starting rollback process..."

ENVIRONMENT=${1:-production}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "  Environment: $ENVIRONMENT"

# Restore configuration
echo "📋 Restoring configuration..."
LATEST_BACKUP=$(ls -t backups/.env.$ENVIRONMENT.* 2>/dev/null | head -1)

if [ -f "$LATEST_BACKUP" ]; then
    cp "$LATEST_BACKUP" ".env.$ENVIRONMENT"
    echo "  ✅ Restored from: $LATEST_BACKUP"
else
    echo "  ⚠️ No backup found for $ENVIRONMENT"
fi

# Trigger Render rollback
echo "🚀 Triggering Render rollback..."

if [ -n "$RENDER_DEPLOY_HOOK" ]; then
    curl -X POST "$RENDER_DEPLOY_HOOK"
    echo "  ✅ Rollback deployment triggered"
else
    echo "  ⚠️ RENDER_DEPLOY_HOOK not set"
fi

# Wait for rollback
echo "⏳ Waiting for rollback to complete..."
sleep 60

# Verify service health
echo "🔍 Verifying rollback..."
URL="https://telbot-$ENVIRONMENT.onrender.com/health"

if curl -f -s "$URL"; then
    echo "✅ Rollback successful - service is healthy"
    exit 0
else
    echo "❌ Rollback verification failed"
    exit 1
fi
