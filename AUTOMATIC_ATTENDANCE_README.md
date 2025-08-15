# Automatic Google Meet Attendance Detection System

## Overview

This system automatically detects attendance from Google Meet sessions and correlates them with pod meetings, eliminating manual attendance entry and providing detailed timing analytics for punctuality tracking.

## 🎯 Key Features

- **Real-time attendance detection** from Google Admin Reports API
- **Participant email matching** with confidence scoring 
- **Precise join/leave timestamps** for punctuality analytics
- **Automatic attendance record creation/updates**
- **Web interface for management and monitoring**
- **Meeting duration accuracy** (actual time spent vs manual estimates)

## 📋 System Components

### Core Files

1. **`google_admin_reports.py`** - Google Admin Reports API integration
2. **`meet_correlation_engine.py`** - Links Meet sessions to pod meetings  
3. **`automatic_attendance_engine.py`** - Main orchestrator for processing
4. **`meet_session_schema.sql`** - Database schema for Meet tracking
5. **`web_interface.py`** - Web API endpoints for management

### Database Schema

- **`meet_sessions`** - Tracks Google Meet sessions linked to meetings
- **`meet_participants`** - Individual participant data with timing
- **`meet_reports_sync`** - API synchronization tracking
- **`meet_audit_events`** - Raw Google Meet audit events
- **`participant_email_mapping`** - External email to user mapping
- **Enhanced `meeting_attendance`** - Meet correlation fields added

## 🚀 Setup Instructions

### 1. Google Admin API Setup

```bash
# Set required environment variables
export GOOGLE_MEET_SERVICE_ACCOUNT_FILE="/path/to/service-account.json"
export GOOGLE_CALENDAR_USER_EMAIL="admin@yourdomain.com"
export ORGANIZATION_DOMAIN="yourdomain.com"
```

**Required Google API Scopes:**
- `https://www.googleapis.com/auth/admin.reports.audit.readonly`
- `https://www.googleapis.com/auth/admin.reports.usage.readonly`

### 2. Database Schema Setup

Apply the Meet session tracking schema:

```bash
# Apply schema to enable Meet tracking
psql -h your-db-host -d your-db -f meet_session_schema.sql
```

### 3. Web Interface Access

New endpoints available at `http://localhost:8080`:

- **`/automatic-attendance`** - Management dashboard
- **`POST /api/automatic-attendance/sync-date`** - Manual sync for specific date
- **`POST /api/automatic-attendance/daily-sync`** - Run daily sync
- **`GET /api/meet-sessions`** - View Meet sessions
- **`GET /api/meet-sessions/<id>/participants`** - Session participants
- **`POST /api/meet-sessions/<id>/sync`** - Manual session sync

## 🔧 Usage Examples

### Manual Daily Sync
```python
from automatic_attendance_engine import AutomaticAttendanceEngine
from supabase import create_client

# Initialize
supabase = create_client(url, key)
engine = AutomaticAttendanceEngine(supabase)
await engine.initialize()

# Process yesterday's meetings
result = await engine.run_daily_sync()
print(f"Processed {result.total_meetings_processed} meetings")
```

### Check Specific Date
```python
from datetime import date

# Process specific date
target_date = date(2025, 8, 15)
result = await engine.process_meetings_for_date(target_date)
```

### Web API Usage
```bash
# Trigger sync for specific date
curl -X POST http://localhost:8080/api/automatic-attendance/sync-date \
  -H "Content-Type: application/json" \
  -d '{"sync_date": "2025-08-15"}'

# Get Meet sessions
curl http://localhost:8080/api/meet-sessions
```

## 📊 Punctuality Analytics

The system provides detailed timing data for encouraging punctuality:

### Join Time Tracking
- **Early arrivals** - Who joins 2-3 minutes before start
- **On-time participants** - Joins within 1 minute of start
- **Late arrivals** - How late and how often
- **Consistent patterns** - Track individual punctuality trends

### Available Metrics
```sql
-- Get punctuality data
SELECT 
  u.name,
  mp.joined_at,
  mp.left_at,
  mp.duration_minutes,
  ms.started_at as meeting_start,
  EXTRACT(EPOCH FROM (mp.joined_at - ms.started_at))/60 as minutes_late
FROM meet_participants mp
JOIN meet_sessions ms ON mp.meet_session_id = ms.id
JOIN users u ON mp.user_id = u.id
WHERE mp.joined_at IS NOT NULL;
```

## 🐛 Debugging & Troubleshooting

### Common Issues

1. **"55-minute duration" showing for 15-minute meetings**
   - **Cause:** Test files with hardcoded durations
   - **Location:** `test_attendance_adapted.py:70`, `test_working_integration.py:145`
   - **Solution:** These are test artifacts, not real tracking data

2. **Meet sessions table not found**
   - **Cause:** Database schema not applied
   - **Solution:** Run `meet_session_schema.sql`

3. **No participants detected**
   - **Cause:** Google Admin API not configured or no Meet link
   - **Solution:** Check environment variables and Meet link association

### Investigation Tools

Check meeting creation vs attendance timing:
```python
# Analyze suspicious records
meeting_created = datetime.fromisoformat(meeting['created_at'])
attendance_recorded = datetime.fromisoformat(attendance['created_at'])
time_diff = (attendance_recorded - meeting_created).total_seconds()

if time_diff < 10:
    print("⚠️ Suspicious: Manual entry detected")
```

## 🔍 Recent Investigation (August 15, 2025)

**Issue:** 55-minute duration showing for 15-minute meetings

**Root Cause Found:**
- Test files contained hardcoded `duration_minutes=55`
- Attendance recorded 0.2 seconds after meeting creation
- Indicates automatic test data insertion, not real tracking

**Files with Test Data:**
- `test_attendance_adapted.py` line 70
- `test_working_integration.py` line 145

**Resolution:** Apply Meet session schema for real timing data

## 🎯 Next Steps

1. **Apply database schema** to enable real timing tracking
2. **Configure Google Admin API** with proper credentials
3. **Test with real Meet sessions** to verify join time accuracy
4. **Set up daily sync schedule** for automatic processing
5. **Monitor punctuality trends** and encourage early arrivals

## 📈 Expected Results

Once fully deployed:
- **Automatic attendance detection** eliminates manual entry
- **Real join/leave timestamps** enable punctuality coaching
- **Duration accuracy** shows actual participation time
- **Trend analysis** identifies patterns for improvement
- **Early arrival encouragement** through visible metrics

## 🔐 Security & Privacy

- Uses Domain-Wide Delegation for admin access
- Only processes organizational Meet data
- Stores minimal participant information
- Includes safety controls to prevent spam
- Audit trail for all automatic detections

---

*Generated with Claude Code - Automatic Google Meet Attendance Detection System*