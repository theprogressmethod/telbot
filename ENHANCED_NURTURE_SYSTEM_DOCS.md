# Enhanced Nurture Sequence System Documentation

## Phase 2 Implementation: Multi-Channel Delivery & Engagement-Based Personalization

### Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Documentation](#api-documentation)
5. [Admin Interface](#admin-interface)
6. [Email Integration](#email-integration)
7. [Testing Framework](#testing-framework)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting](#troubleshooting)

---

## System Overview

The Enhanced Nurture Sequence System builds upon the existing Progress Method bot to provide:

- **Multi-Channel Delivery**: Messages sent via both Telegram and Email
- **Engagement-Based Personalization**: Content adapted based on user interaction patterns
- **Unified Admin Control**: Centralized management of all sequence types
- **Advanced Analytics**: Comprehensive tracking and reporting
- **A/B Testing**: Sequence variant testing capabilities

### Key Features

✅ **Unified Sequence Controller** - Manages all nurture sequence types through a single interface  
✅ **Multi-Channel Fallback** - Automatically falls back from email to Telegram if delivery fails  
✅ **Engagement Scoring** - Dynamic user scoring based on interactions across all channels  
✅ **Email Templates** - Professional HTML email templates with tracking  
✅ **Admin Dashboard** - Enhanced interface for sequence management  
✅ **Comprehensive Testing** - Full test suite for validation  

---

## Architecture

### Component Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Telegram Bot      │    │   Admin Dashboard   │    │   Email Service     │
│                     │    │                     │    │   (Resend API)      │
└──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘
           │                          │                          │
           └─────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ Unified Nurture         │
                │ Controller              │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Enhanced Database       │
                │ Schema                  │
                └─────────────────────────┘
```

### Core Components

#### 1. Unified Nurture Controller (`unified_nurture_controller.py`)
- Central orchestrator for all nurture sequences
- Handles engagement-based personalization
- Manages multi-channel delivery scheduling
- Implements fallback logic

#### 2. Email Delivery Service (`email_delivery_service.py`)
- Resend API integration
- HTML email templates
- Webhook handling for delivery tracking
- Bounce and complaint management

#### 3. Enhanced Database Schema (`enhanced_nurture_schema.sql`)
- Multi-channel delivery tracking
- Engagement scoring tables
- A/B testing support
- Email preferences management

#### 4. Enhanced Admin API (`enhanced_admin_api.py`)
- RESTful API for sequence management
- Real-time analytics endpoints
- User preference management
- Test email functionality

---

## Database Schema

### New Tables

#### `message_deliveries`
Tracks all message deliveries across channels.

```sql
CREATE TABLE message_deliveries (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    sequence_type TEXT NOT NULL,
    message_step INTEGER NOT NULL,
    channel TEXT CHECK (channel IN ('telegram', 'email')),
    delivery_status TEXT CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'failed', 'bounced', 'opened', 'clicked')),
    recipient_address TEXT NOT NULL,
    message_content TEXT NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    tracking_id TEXT,
    attempt_count INTEGER DEFAULT 1,
    max_attempts INTEGER DEFAULT 3,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `engagement_scores`
Stores user engagement metrics.

```sql
CREATE TABLE engagement_scores (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    score_type TEXT CHECK (score_type IN ('overall', 'telegram', 'email', 'attendance', 'commitment')),
    score NUMERIC(5,2) CHECK (score >= 0 AND score <= 100),
    factors JSONB DEFAULT '{}',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);
```

#### `user_email_preferences`
Manages user email settings.

```sql
CREATE TABLE user_email_preferences (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    email_address TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    verification_sent_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    opt_in_sequences BOOLEAN DEFAULT TRUE,
    opt_in_announcements BOOLEAN DEFAULT TRUE,
    preferred_time TEXT DEFAULT 'morning',
    timezone TEXT DEFAULT 'UTC',
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Key Functions

#### `calculate_engagement_score(user_id, score_type)`
Calculates user engagement scores based on interaction history.

#### `get_preferred_channel(user_id)`
Determines optimal delivery channel for a user.

#### `schedule_multi_channel_message(...)`
Schedules message delivery across multiple channels with timing optimization.

---

## API Documentation

### Nurture Sequence Management

#### Trigger Sequence
```http
POST /admin/api/nurture/trigger
Content-Type: application/json

{
    "user_id": "uuid",
    "sequence_type": "onboarding",
    "context": {"key": "value"},
    "override_channel": "email"
}
```

#### Get Active Sequences
```http
GET /admin/api/nurture/active
```

#### Process Pending Deliveries
```http
POST /admin/api/nurture/process
```

### Analytics

#### Get Nurture Analytics
```http
GET /admin/api/nurture/analytics?days=30
```

#### Get Email Statistics
```http
GET /admin/api/email/stats?days=7
```

### Email Management

#### Send Test Email
```http
POST /admin/api/email/test
Content-Type: application/json

{
    "email_address": "test@example.com",
    "user_name": "Test User",
    "template_type": "nurture_sequence"
}
```

#### Handle Email Webhooks
```http
POST /admin/api/email/webhook
Content-Type: application/json

{
    "type": "email.opened",
    "data": {
        "tags": [{"name": "tracking_id", "value": "uuid"}],
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

---

## Admin Interface

### Dashboard Navigation

The enhanced admin dashboard includes five main tabs:

1. **📊 Overview** - System metrics and quick actions
2. **💌 Nurture Sequences** - Sequence management and triggering
3. **📧 Email Delivery** - Email system controls and testing
4. **👥 Users** - User management (existing functionality)
5. **📈 Analytics** - Detailed reporting and insights

### Nurture Sequences Tab

#### Sequence Triggering
- **User ID**: Target user identifier
- **Sequence Type**: Choose from available sequence types
- **Channel Override**: Force specific delivery channel
- **Context**: Additional data for personalization

#### User Preferences
- **Preferred Channel**: Set user's delivery preference
- **Email Preferences**: Configure email-specific settings

#### Active Sequences Monitor
Real-time view of all active sequences showing:
- User information
- Sequence type and progress
- Next message timing
- Delivery channel

### Email Delivery Tab

#### Test Email System
- Send test emails to validate templates
- Choose between different template types
- Verify delivery and tracking functionality

#### Queue Management
- Process pending email deliveries
- Clear failed email attempts
- Monitor delivery statistics

---

## Email Integration

### Resend API Configuration

Set the following environment variables:

```bash
RESEND_API_KEY=re_eCPQhpxD_BiGA5QnXDALpz1qNUn43THqf
FROM_EMAIL=noreply@progressmethod.com
```

### Email Templates

#### Template Types
- **nurture_sequence**: Standard nurture sequence emails
- **welcome_email**: New user welcome messages

#### Template Variables
All templates support these variables:
- `{user_name}` - User's first name
- `{message_content}` - Main message content
- `{dashboard_url}` - Link to user dashboard
- `{unsubscribe_url}` - Unsubscribe link with tracking
- `{tracking_url}` - Tracking pixel URL

#### HTML Template Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>The Progress Method</title>
    <!-- Responsive styles -->
</head>
<body>
    <div class="container">
        <div class="header">...</div>
        <div class="content">{message_content}</div>
        <div class="footer">...</div>
    </div>
    <img src="{tracking_url}" class="tracking-pixel" />
</body>
</html>
```

### Webhook Configuration

Configure Resend webhooks to point to:
```
POST https://yourdomain.com/admin/api/email/webhook
```

Supported webhook events:
- `email.sent`
- `email.delivered`
- `email.bounced`
- `email.complained`
- `email.opened`
- `email.clicked`

---

## Testing Framework

### Running Tests

#### Full Test Suite
```bash
python test_multi_channel_delivery.py
```

#### Specific Test
```bash
python test_multi_channel_delivery.py --test test_sequence_triggering
```

#### Performance Tests Only
```bash
python test_multi_channel_delivery.py --performance
```

#### Detailed Report
```bash
python test_multi_channel_delivery.py --report
```

### Test Categories

1. **Sequence Triggering** - Validates sequence creation and activation
2. **Channel Selection** - Tests delivery channel logic
3. **Engagement Scoring** - Verifies scoring calculations
4. **Message Personalization** - Tests content customization
5. **Multi-Channel Scheduling** - Validates delivery scheduling
6. **Telegram Delivery** - Tests Telegram message sending
7. **Email Delivery** - Tests email sending and tracking
8. **Delivery Fallback** - Tests failure recovery
9. **Webhook Handling** - Tests email event processing
10. **Analytics Generation** - Tests reporting functionality
11. **User Preferences** - Tests preference management
12. **Error Handling** - Tests system resilience
13. **Performance Load** - Tests system under load

### Mock Services

The test framework includes comprehensive mocks:
- **MockSupabaseClient** - Database operations
- **MockEmailService** - Email delivery simulation
- **MockTelegramService** - Telegram message simulation

---

## Deployment Guide

### Prerequisites

1. **Database Schema Updates**
   ```bash
   python apply_enhanced_schema.py --schema-file enhanced_nurture_schema.sql
   ```

2. **Environment Variables**
   ```bash
   RESEND_API_KEY=your_resend_api_key
   ADMIN_API_KEY=your_admin_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

3. **Dependencies**
   ```bash
   pip install httpx  # For email service
   ```

### Step-by-Step Deployment

#### 1. Database Migration
```bash
# Check existing schema
python apply_enhanced_schema.py --check-only

# Backup existing data
python apply_enhanced_schema.py --backup-only

# Apply full schema update
python apply_enhanced_schema.py
```

#### 2. Test System Integration
```bash
# Run comprehensive tests
python test_multi_channel_delivery.py

# Test specific components
python email_delivery_service.py --test-email admin@yourcompany.com
```

#### 3. Deploy Services

**Option A: Existing Service Integration**
```python
# In your main application
from unified_nurture_controller import UnifiedNurtureController
from email_delivery_service import EmailDeliveryService

# Initialize services
controller = UnifiedNurtureController(supabase_client)
email_service = EmailDeliveryService(resend_api_key)
email_service.set_supabase_client(supabase_client)
controller.set_email_service(email_service)
controller.set_telegram_service(telegram_bot)
```

**Option B: Standalone Admin API**
```bash
# Run enhanced admin API
python enhanced_admin_api.py
```

#### 4. Configure Webhooks

Set up Resend webhook endpoint:
```
URL: https://yourdomain.com/admin/api/email/webhook
Events: email.sent, email.delivered, email.bounced, email.opened, email.clicked
```

#### 5. Monitor and Validate

1. Check admin dashboard at `/admin/dashboard`
2. Send test emails via admin interface
3. Trigger test sequences
4. Monitor delivery analytics

### Production Considerations

#### Security
- Set strong `ADMIN_API_KEY`
- Use HTTPS for all webhook endpoints
- Implement rate limiting on admin endpoints
- Validate all webhook signatures

#### Performance
- Set up database connection pooling
- Implement Redis for message queue (production upgrade)
- Configure proper indexes on new tables
- Monitor email delivery rates

#### Monitoring
- Set up alerts for failed deliveries
- Monitor engagement score calculations
- Track email bounce rates
- Log sequence triggering patterns

---

## Troubleshooting

### Common Issues

#### 1. Schema Update Failures
**Problem**: Database schema update fails
**Solution**:
```bash
# Check existing schema
python apply_enhanced_schema.py --check-only

# Apply specific parts manually via Supabase dashboard
```

#### 2. Email Delivery Issues
**Problem**: Emails not being sent
**Solutions**:
- Verify `RESEND_API_KEY` is correct
- Check domain verification in Resend dashboard
- Validate email addresses are properly formatted
- Check Resend API rate limits

**Debug Commands**:
```bash
# Test email service directly
python email_delivery_service.py --test-email test@example.com

# Check email delivery stats
curl https://yourapi.com/admin/api/email/stats
```

#### 3. Engagement Score Calculation Issues
**Problem**: Engagement scores not updating
**Solutions**:
- Check if `calculate_engagement_score` function exists in database
- Verify user has interaction data
- Check score calculation logs

**Debug Commands**:
```sql
-- Check if function exists
SELECT routine_name FROM information_schema.routines 
WHERE routine_name = 'calculate_engagement_score';

-- Test function directly
SELECT calculate_engagement_score('user-id', 'overall');
```

#### 4. Sequence Triggering Problems
**Problem**: Sequences not being triggered
**Solutions**:
- Verify user exists in database
- Check sequence type is valid
- Ensure user doesn't already have active sequence of same type

**Debug Commands**:
```bash
# Test sequence triggering
curl -X POST https://yourapi.com/admin/api/nurture/trigger \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user","sequence_type":"onboarding"}'
```

#### 5. Webhook Processing Issues
**Problem**: Email webhooks not being processed
**Solutions**:
- Verify webhook URL is accessible
- Check webhook endpoint logs
- Validate Resend webhook configuration
- Ensure proper event types are configured

### Debugging Tools

#### 1. Admin Dashboard Diagnostics
Navigate to `/admin/dashboard` and check:
- System status indicators
- Recent delivery metrics
- Active sequence counts
- Error logs in browser console

#### 2. Database Queries
```sql
-- Check recent deliveries
SELECT * FROM message_deliveries 
ORDER BY created_at DESC LIMIT 10;

-- Check engagement scores
SELECT * FROM engagement_scores 
WHERE user_id = 'target-user-id';

-- Check email preferences
SELECT * FROM user_email_preferences 
WHERE user_id = 'target-user-id';
```

#### 3. API Testing
```bash
# Check system health
curl https://yourapi.com/

# Get nurture analytics
curl https://yourapi.com/admin/api/nurture/analytics

# Process pending deliveries
curl -X POST https://yourapi.com/admin/api/nurture/process
```

### Support

For additional support:
1. Check the test framework results for system validation
2. Review admin dashboard for real-time system status
3. Monitor database logs for query errors
4. Check Resend dashboard for email delivery issues

---

## Appendix

### File Structure
```
telbot/
├── unified_nurture_controller.py      # Main controller
├── email_delivery_service.py          # Email integration
├── enhanced_admin_api.py              # Admin interface
├── enhanced_nurture_schema.sql        # Database schema
├── test_multi_channel_delivery.py     # Test framework
├── apply_enhanced_schema.py           # Schema migration
└── ENHANCED_NURTURE_SYSTEM_DOCS.md   # This documentation
```

### Environment Variables Reference
```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
RESEND_API_KEY=re_your_resend_api_key

# Optional
ADMIN_API_KEY=your-admin-api-key
FROM_EMAIL=noreply@yourdomain.com
PORT=8001
ENVIRONMENT=production
```

### API Endpoint Summary
```
GET  /                                 # Health check
GET  /admin/dashboard                  # Admin interface
GET  /admin/api/metrics               # System metrics
GET  /admin/api/nurture/analytics     # Nurture analytics
GET  /admin/api/nurture/active        # Active sequences
POST /admin/api/nurture/trigger       # Trigger sequence
POST /admin/api/nurture/process       # Process queue
GET  /admin/api/email/stats           # Email statistics
POST /admin/api/email/test            # Send test email
POST /admin/api/email/webhook         # Email webhooks
GET  /admin/api/users                 # User management
```

---

*This documentation covers the complete enhanced nurture sequence system. For questions or additional features, refer to the test framework or admin interface for validation and testing capabilities.*