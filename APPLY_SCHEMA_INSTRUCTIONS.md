# 📋 Apply Database Schema for Automatic Attendance

## Current Status ✅

**Tables that need to be created:**
- ❌ `meet_sessions` - NEEDS CREATION
- ❌ `meet_participants` - NEEDS CREATION  
- ❌ `meet_reports_sync` - NEEDS CREATION
- ❌ `meet_audit_events` - NEEDS CREATION
- ❌ `participant_email_mapping` - NEEDS CREATION

**Columns to add to `meeting_attendance`:**
- ⏳ `meet_participant_id`
- ⏳ `detection_method`
- ⏳ `meet_join_time`
- ⏳ `meet_leave_time`
- ⏳ `meet_duration_minutes`
- ⏳ `confidence_score`

## 🚀 How to Apply the Schema

### Option 1: Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard:**
   ```
   https://app.supabase.com
   ```

2. **Navigate to SQL Editor:**
   - Select your project (apfiwfkpdhslfavnncsl)
   - Click "SQL Editor" in left sidebar
   - Click "New Query" button

3. **Copy the Schema:**
   - Open file: `meet_session_schema.sql`
   - Copy ALL contents (Cmd+A, Cmd+C)

4. **Paste and Run:**
   - Paste into SQL Editor
   - Click "Run" button
   - Check for success messages

### Option 2: Supabase CLI

If you have Supabase CLI installed:

```bash
# From the telbot directory
cd /Users/thomasmulhern/projects/telbot_env/telbot

# Apply the schema
supabase db push --db-url "postgresql://postgres:[YOUR-PASSWORD]@db.apfiwfkpdhslfavnncsl.supabase.co:5432/postgres" < meet_session_schema.sql
```

### Option 3: Direct PostgreSQL Connection

```bash
# Using psql directly
psql "postgresql://postgres:[YOUR-PASSWORD]@db.apfiwfkpdhslfavnncsl.supabase.co:5432/postgres" -f meet_session_schema.sql
```

## ⚠️ Important Notes

1. **UUID Extension:** The schema uses `uuid_generate_v4()`. If you get an error, run this first:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

2. **Indexes:** The schema uses `INDEX` syntax. If Supabase complains, it will convert to:
   ```sql
   CREATE INDEX idx_meet_sessions_meeting_id ON meet_sessions(meeting_id);
   -- etc for other indexes
   ```

3. **Safe to Run:** The schema uses `CREATE TABLE` (not `CREATE TABLE IF NOT EXISTS`), so it won't overwrite existing data, but will error if tables exist.

## 🔍 Verify Success

After applying, verify by running these queries in SQL Editor:

```sql
-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'meet_sessions',
  'meet_participants',
  'meet_reports_sync',
  'meet_audit_events',
  'participant_email_mapping'
);

-- Check if columns were added to meeting_attendance
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'meeting_attendance'
AND column_name IN (
  'meet_participant_id',
  'detection_method',
  'meet_join_time',
  'meet_leave_time',
  'meet_duration_minutes',
  'confidence_score'
);
```

## ✅ Expected Result

You should see:
- 5 new tables created
- 6 new columns added to `meeting_attendance`
- 1 new view: `comprehensive_attendance`
- Multiple indexes created for performance

## 🎯 Next Steps After Schema Applied

1. **Configure Google Admin API** credentials
2. **Store Meet links** when creating meetings
3. **Run test sync** with a real meeting
4. **Enable daily sync** process

---

**Need Help?** 
- Check Supabase logs: Dashboard → Logs → Database
- Error messages will indicate if UUID extension is needed
- Index syntax errors can be ignored (Supabase auto-converts)