# 🔐 Google Admin Reports API Setup Guide

## Overview

To enable automatic Google Meet attendance tracking, we need to configure access to the Google Admin Reports API. This API provides detailed information about Meet sessions, including participant join/leave times.

## 📋 Prerequisites

1. **Google Workspace Admin Access** - You need admin privileges in your Google Workspace
2. **Organization Domain** - Your meetings must be on a Google Workspace domain (not personal Gmail)
3. **Meet Usage** - Participants must join via Google Meet (not phone dial-in only)

## 🚀 Step-by-Step Setup

### Step 1: Create Service Account

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com
   ```

2. **Select or Create Project:**
   - Use existing project or create new one
   - Note the Project ID for later

3. **Enable Required APIs:**
   - Go to "APIs & Services" → "Library"
   - Search and enable:
     - "Admin SDK API"
     - "Google Calendar API" (if not already enabled)

4. **Create Service Account:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: `telbot-meet-tracker`
   - Description: `Service account for automatic Meet attendance tracking`
   - Click "Create and Continue"

5. **Download Service Account Key:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create New Key"
   - Choose "JSON" format
   - Download the file (keep it secure!)

### Step 2: Configure Domain-Wide Delegation

1. **Enable Domain-Wide Delegation:**
   - In the service account details page
   - Check "Enable Domain-Wide Delegation"
   - Add "Product name for consent screen": `TelBot Meet Tracker`
   - Save the changes

2. **Note the Client ID:**
   - Copy the "Client ID" from the service account details
   - You'll need this for the next step

### Step 3: Authorize in Google Workspace Admin

1. **Go to Google Admin Console:**
   ```
   https://admin.google.com
   ```

2. **Navigate to API Controls:**
   - Security → Access and data control → API controls
   - Click "Manage Domain Wide Delegation"

3. **Add API Client:**
   - Click "Add new"
   - **Client ID:** [Paste the Client ID from Step 2]
   - **OAuth Scopes:** 
     ```
     https://www.googleapis.com/auth/admin.reports.audit.readonly,https://www.googleapis.com/auth/admin.reports.usage.readonly
     ```
   - Click "Authorize"

### Step 4: Configure Environment Variables

1. **Place Service Account File:**
   ```bash
   # Copy the downloaded JSON file to your project
   cp ~/Downloads/telbot-meet-tracker-*.json /Users/thomasmulhern/projects/telbot_env/telbot/google_service_account.json
   ```

2. **Update Environment Variables:**
   Add these to your `.env` file or environment:
   ```bash
   # Google Admin Reports API Configuration
   GOOGLE_MEET_SERVICE_ACCOUNT_FILE=/Users/thomasmulhern/projects/telbot_env/telbot/google_service_account.json
   GOOGLE_CALENDAR_USER_EMAIL=your-admin-email@yourdomain.com
   ORGANIZATION_DOMAIN=yourdomain.com
   
   # Optional: Enable debug logging
   GOOGLE_API_DEBUG=true
   ```

   **Replace with your actual values:**
   - `your-admin-email@yourdomain.com` - Your Google Workspace admin email
   - `yourdomain.com` - Your organization's domain

## 🧪 Testing the Setup

### Option 1: Quick Test Script

Run the test script to verify your configuration:

```bash
cd /Users/thomasmulhern/projects/telbot_env/telbot
python test_google_admin_connection.py
```

### Option 2: Manual Test

1. **Create a Test Meeting:**
   - Use the dashboard at http://localhost:8080/test
   - Create a meeting for today with Google Calendar enabled
   - Join the meeting briefly to generate data

2. **Wait 10-15 minutes** (Google data has a delay)

3. **Run Manual Sync:**
   ```bash
   python automatic_attendance_engine.py --sync-date today
   ```

## 🔍 Troubleshooting

### Common Issues

1. **"Access Denied" Error:**
   - Check that Domain-Wide Delegation is enabled
   - Verify the OAuth scopes are correct
   - Ensure you're using an admin email address

2. **"Service Account Not Found":**
   - Check the file path in `GOOGLE_MEET_SERVICE_ACCOUNT_FILE`
   - Verify the JSON file is valid and readable

3. **"No Data Returned":**
   - Meet data has 10-15 minute delay from Google
   - Ensure meetings are on your Google Workspace domain
   - Check that participants actually joined via Meet (not just phone)

4. **"Insufficient Permissions":**
   - Verify admin console delegation was set up correctly
   - Check that the admin email has the required permissions

### Debug Commands

```bash
# Test basic API connection
python -c "from google_admin_reports import GoogleAdminReports; g = GoogleAdminReports(); print('✅ Connection successful')"

# Check for recent Meet data
python -c "
from google_admin_reports import GoogleAdminReports
from datetime import datetime, timedelta
g = GoogleAdminReports()
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
events = g.get_meet_activities(yesterday)
print(f'Found {len(events)} Meet events for {yesterday}')
"
```

## 🔒 Security Notes

1. **Service Account Security:**
   - Keep the JSON file secure and never commit to git
   - Only grant minimum required permissions
   - Regularly rotate service account keys

2. **Data Privacy:**
   - The system only accesses Meet metadata (join/leave times)
   - No meeting content or recordings are accessed
   - All data stays within your own database

3. **Access Logging:**
   - All API access is logged in Google Admin Console
   - Monitor "Security" → "Investigation tool" for API usage

## ✅ Success Indicators

You'll know the setup is working when:

1. ✅ API connection test passes without errors
2. ✅ Manual sync finds and processes Meet data  
3. ✅ Participant join/leave times appear in database
4. ✅ Dashboard shows "Last Sync" timestamps updating

## 🎯 Next Steps

Once API access is working:

1. **Enable Meet Links in Meetings** - Ensure calendar events include Meet links
2. **Test Real Meeting Detection** - Create and join a test meeting
3. **Set Up Daily Sync** - Schedule automatic daily processing
4. **Monitor Accuracy** - Compare detected vs actual attendance

---

**Need Help?**
- Check Google Admin Console logs for API access errors
- Verify all environment variables are set correctly  
- Ensure service account JSON file has proper permissions
- Test with a simple meeting before complex scenarios