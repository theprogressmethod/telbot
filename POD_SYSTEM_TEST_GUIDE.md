# 🧪 Pod System Testing Guide

## Quick Setup & Test

### 1. **Check Your Telegram User ID**
In Telegram, message @TPMdevtestbot:
```
/start
```
The bot logs will show your user ID.

### 2. **Grant Yourself Admin Access**
Go to Supabase Dashboard → SQL Editor and run:
```sql
-- Find your user ID
SELECT id, telegram_user_id, telegram_username, first_name 
FROM users 
WHERE telegram_username = 'yourusername';

-- Grant admin role (replace with your values)
INSERT INTO user_roles (user_id, telegram_user_id, role, granted_at)
VALUES (
    'your-uuid-here',  -- From above query
    123456789,         -- Your Telegram user ID
    'admin',
    NOW()
);
```

### 3. **Test Admin Commands in Telegram**

#### Create a Pod:
```
/createpod "Test Squad" Monday 19:00
```

#### List All Pods:
```
/listpods
```

#### Add Yourself to Pod:
```
/addtopod @yourusername "Test Squad"
```

### 4. **Test User Commands**

#### View Your Pod:
```
/mypod
```
Shows:
- Pod name and meeting time
- All members with their weekly stats
- Meeting link

#### Check Leaderboard:
```
/podleaderboard
```
Shows weekly rankings based on completed commitments

#### View Pod Week:
```
/podweek
```
Shows current pod week progress

### 5. **Test with Multiple Users**

1. Have a friend message the bot: `/start`
2. Add them to your pod: `/addtopod @friend "Test Squad"`
3. Both make commitments: `/commit I will read for 30 minutes today`
4. Mark some complete: `/done`
5. Check leaderboard: `/podleaderboard`

## What the Pod System Does

✅ **For Users:**
- Groups 4-6 people for weekly accountability
- Shows pod members and their progress
- Weekly leaderboard for friendly competition
- Meeting reminders and links

✅ **For Admins:**
- Create and manage pods
- Assign users to pods
- Monitor pod health
- Send pod announcements

## Database Tables Used

- **pods**: Stores pod information
- **pod_memberships**: Links users to pods
- **pod_announcements**: Stores pod messages
- **pod_weeks**: Tracks weekly cycles

## Common Issues

**"You're not in a pod yet!"**
- Ask an admin to add you using `/addtopod`

**"Admin access required"**
- You need admin role in user_roles table

**"Pod not found"**
- Check exact pod name with `/listpods`
- Pod names are case-sensitive

## Testing Checklist

- [ ] Admin can create pod
- [ ] Admin can list all pods  
- [ ] Admin can add users to pod
- [ ] User can view their pod
- [ ] User can see pod leaderboard
- [ ] Leaderboard updates with commitments
- [ ] Pod shows correct member count
- [ ] Meeting time displays correctly

## Monitor Bot Logs

Watch for errors:
```bash
# In terminal where bot is running
# Look for lines with "pod" or "Pod"
```

## Success Metrics

A working pod system should:
1. Allow admins to create/manage pods
2. Show users their pod information
3. Track weekly progress per pod
4. Display accurate leaderboards
5. Handle 4-6 members per pod