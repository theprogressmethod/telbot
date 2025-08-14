# The Progress Method - Data Architecture

## 🏗️ **Core Data Platform Recommendation**

### **Current Scale: Supabase Pro ($25/month)**
- Handles 100K+ users easily
- Real-time subscriptions for live updates
- Built-in auth and RLS
- Great for MVP → Scale

### **Future Scale: Consider Migration To:**
- **PostgreSQL + Redis** (when 50K+ users)
- **Planetscale** (serverless SQL at scale)
- **Neon** (PostgreSQL with branching)

---

## 📊 **Database Schema Design**

### **1. Users Table (Core Identity)**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    first_name TEXT,
    username TEXT,
    
    -- Journey tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    first_bot_interaction_at TIMESTAMPTZ,
    first_commitment_at TIMESTAMPTZ,
    first_pod_call_at TIMESTAMPTZ,
    
    -- Profile for pod matching
    timezone TEXT,
    goals_category TEXT, -- health, business, personal, etc
    experience_level TEXT, -- beginner, intermediate, advanced
    preferred_meeting_style TEXT, -- supportive, direct, mixed
    strengths JSONB, -- ["marketing", "discipline", "tech"]
    help_needed JSONB, -- ["time management", "motivation"]
    bio TEXT,
    
    -- Engagement metrics
    total_commitments INTEGER DEFAULT 0,
    completed_commitments INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ,
    
    -- Settings
    notification_preferences JSONB,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT valid_completion_rate CHECK (completed_commitments <= total_commitments)
);

-- Indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_timezone ON users(timezone);
```

### **2. User Roles (Flexible Multi-Role System)**
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_type TEXT NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ, -- For temporary roles
    metadata JSONB, -- Role-specific data
    
    UNIQUE(user_id, role_type)
);

-- Role types: 'unpaid', 'paid', 'pod_member', 'admin', 'super_admin'
-- Users start with 'unpaid', automatically get 'paid' when payment detected
-- Multiple roles allowed: user can be 'paid' + 'pod_member' + 'admin'

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_type ON user_roles(role_type);
```

### **3. Pods (Business Core)**
```sql
CREATE TABLE pods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    
    -- Schedule
    day_of_week INTEGER, -- 1=Monday, 7=Sunday
    time_utc TIME,
    timezone TEXT,
    duration_minutes INTEGER DEFAULT 60,
    
    -- Meeting details
    zoom_link TEXT,
    zoom_meeting_id TEXT,
    calendar_event_id TEXT,
    
    -- Capacity
    max_members INTEGER DEFAULT 6,
    current_members INTEGER DEFAULT 0,
    
    -- Health metrics (auto-calculated)
    avg_attendance_rate DECIMAL(5,2),
    avg_completion_rate DECIMAL(5,2),
    member_satisfaction_score DECIMAL(3,2),
    
    -- Status
    status TEXT DEFAULT 'active', -- active, paused, full, disbanded
    created_at TIMESTAMPTZ DEFAULT NOW(),
    next_meeting_at TIMESTAMPTZ,
    
    -- Matching criteria for smart assignment
    target_goals_category TEXT,
    target_experience_level TEXT,
    target_timezone_range TEXT[],
    
    CONSTRAINT valid_day CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT valid_members CHECK (current_members <= max_members)
);
```

### **4. Pod Memberships**
```sql
CREATE TABLE pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active', -- active, paused, left
    
    -- Individual metrics
    meetings_attended INTEGER DEFAULT 0,
    meetings_missed INTEGER DEFAULT 0,
    contribution_score DECIMAL(3,2), -- Peer ratings
    
    -- Payment tracking
    monthly_payment_active BOOLEAN DEFAULT false,
    last_payment_at TIMESTAMPTZ,
    
    UNIQUE(user_id, pod_id)
);
```

### **5. Commitments (Enhanced for Context)**
```sql
CREATE TABLE commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    commitment TEXT NOT NULL,
    original_commitment TEXT, -- Before SMART analysis
    smart_score INTEGER,
    
    -- Classification
    category TEXT, -- health, work, personal, learning
    difficulty_level INTEGER, -- 1-5
    estimated_time_minutes INTEGER,
    
    -- Status
    status TEXT DEFAULT 'active', -- active, completed, failed, paused
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    due_date DATE,
    
    -- Context & Memory
    related_long_term_goal_id UUID, -- Links to 90-day/yearly goals
    context_from_previous JSONB, -- ZEP-style memory
    ai_insights JSONB, -- Patterns, suggestions
    
    -- Pod integration
    shared_with_pod BOOLEAN DEFAULT false,
    pod_id UUID REFERENCES pods(id),
    
    CONSTRAINT valid_smart_score CHECK (smart_score BETWEEN 1 AND 10)
);
```

### **6. Long Term Goals (ZEP Context System)**
```sql
CREATE TABLE long_term_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    title TEXT NOT NULL,
    description TEXT,
    target_completion_date DATE,
    category TEXT,
    
    -- Progress tracking
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    status TEXT DEFAULT 'active',
    
    -- AI Context Building (ZEP-style)
    context_summary JSONB, -- Weekly/monthly summaries
    success_patterns JSONB, -- What's working
    struggle_patterns JSONB, -- What's challenging
    ai_recommendations JSONB, -- Evolving suggestions
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **7. Meetings (Pod Sessions)**
```sql
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled
    
    -- Attendance
    attendees JSONB, -- [user_ids] who showed up
    absent_members JSONB, -- [user_ids] who missed
    attendance_rate DECIMAL(5,2),
    
    -- Content
    agenda JSONB,
    notes TEXT,
    action_items JSONB,
    
    -- Metrics
    member_ratings JSONB, -- Post-meeting satisfaction
    energy_level INTEGER, -- 1-10 group energy
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **8. Automation Sequences**
```sql
CREATE TABLE automation_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    
    -- Triggers
    trigger_type TEXT, -- new_user, pod_joined, payment_made, etc.
    trigger_conditions JSONB,
    
    -- Sequence steps
    steps JSONB, -- [
                 --   {type: "telegram", delay_hours: 24, message: "..."},
                 --   {type: "sms", delay_hours: 48, message: "..."},
                 --   {type: "email", delay_hours: 72, template: "welcome"}
                 -- ]
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sequence_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sequence_id UUID REFERENCES automation_sequences(id),
    
    current_step INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running', -- running, completed, failed, paused
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    execution_log JSONB -- Track what was sent when
);
```

---

## 🔄 **Smart Pod Matching Algorithm**

### **Matching Criteria (When 10+ weekly signups):**
```sql
-- Match based on:
1. Timezone compatibility (±3 hours)
2. Goals category alignment  
3. Experience level balance
4. Meeting style preference
5. Availability overlap
6. Diversity of strengths/needs
```

### **Member Introduction System:**
```sql
-- Auto-generate intro cards:
SELECT 
    first_name,
    goals_category,
    strengths,
    help_needed,
    current_streak,
    bio
FROM users 
WHERE id IN (pod_member_ids);
```

---

## 📊 **KPI Tracking Views**

### **Dashboard Queries:**
```sql
-- 1. Pod Attendance
CREATE VIEW pod_attendance_kpi AS
SELECT 
    AVG(attendance_rate) as overall_attendance,
    COUNT(*) as total_meetings_this_week
FROM meetings 
WHERE scheduled_at > NOW() - INTERVAL '7 days';

-- 2. Bot Usage Percentage  
CREATE VIEW bot_usage_kpi AS
SELECT 
    COUNT(DISTINCT CASE WHEN last_activity_at > NOW() - INTERVAL '7 days' THEN id END) * 100.0 / COUNT(*) as weekly_active_percentage
FROM users;

-- 3. Commitment Fulfillment
CREATE VIEW commitment_fulfillment_kpi AS
SELECT 
    SUM(completed_commitments) * 100.0 / SUM(total_commitments) as overall_completion_rate,
    AVG(current_streak) as avg_current_streak
FROM users;

-- 4. New Users
CREATE VIEW new_users_kpi AS
SELECT COUNT(*) as new_users_this_week
FROM users 
WHERE created_at > NOW() - INTERVAL '7 days';
```

---

## 🤖 **Two-Bot System Architecture**

### **Bot 1: Commitment Bot (Existing)**
- Individual commitment tracking
- SMART analysis
- Daily progress
- First-time user detection

### **Bot 2: Pod Management Bot (New)**
- Meeting reminders (Telegram + SMS)
- Attendance tracking
- Pod introductions
- Weekly check-ins
- Member-to-member connections

---

This architecture scales from your current state to 10K+ users while maintaining performance and enabling all the features you've outlined. Should we start implementing the user roles system first, or would you prefer to see the ZEP integration design?