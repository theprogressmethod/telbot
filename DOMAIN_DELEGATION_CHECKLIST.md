# 🔐 Domain-Wide Delegation Setup Checklist

## Current Status ✅

Your Google Admin Reports API configuration is **almost complete**! The test confirms:

- ✅ Service account file exists and is readable
- ✅ Environment variables are properly configured  
- ✅ Google Admin Reports API connects successfully
- ✅ Database schema is fully applied
- ⏳ **NEXT STEP:** Configure Domain-Wide Delegation in Google Admin Console

## 🚨 Current Error (Expected)

```
unauthorized_client: Client is unauthorized to retrieve access tokens using this method, or client not authorized for any of the scopes requested.
```

This error means the service account needs **Domain-Wide Delegation** approval from your Google Workspace admin.

## 📋 Complete These Steps

### Step 1: Get Your Service Account Client ID

First, let's find the Client ID from your service account:

```bash
cd /Users/thomasmulhern/projects/telbot_env/telbot
python -c "
import json
with open('google-meet-service-account.json', 'r') as f:
    data = json.load(f)
    print('🔑 CLIENT ID:', data['client_id'])
    print('📧 SERVICE ACCOUNT EMAIL:', data['client_email'])
"
```

**Copy the Client ID** - you'll need it for Step 2.

### Step 2: Configure Domain-Wide Delegation

1. **Open Google Admin Console:**
   ```
   https://admin.google.com
   ```

2. **Navigate to API Controls:**
   - Go to **Security** → **Access and data control** → **API controls**
   - Click **"Manage Domain Wide Delegation"**

3. **Add New API Client:**
   - Click **"Add new"**
   - **Client ID:** [Paste the Client ID from Step 1]
   - **OAuth scopes:** 
     ```
     https://www.googleapis.com/auth/admin.reports.audit.readonly,https://www.googleapis.com/auth/admin.reports.usage.readonly
     ```
   - Click **"Authorize"**

### Step 3: Verify the Setup

After completing Step 2, run the test again:

```bash
python test_google_admin_connection.py
```

**Expected successful result:**
```
🧪 Google Admin Reports API Connection Test
============================================================
✅ PASS   Environment Configuration
✅ PASS   Module Import  
✅ PASS   API Connection
✅ PASS   Database Schema
Overall: 4/4 tests passed

🎉 SUCCESS! All tests passed!
```

## 🔍 Troubleshooting

### If You Still Get "unauthorized_client":

1. **Wait 10-15 minutes** - Changes can take time to propagate
2. **Verify OAuth scopes** - Must be exactly:
   ```
   https://www.googleapis.com/auth/admin.reports.audit.readonly,https://www.googleapis.com/auth/admin.reports.usage.readonly
   ```
3. **Check admin permissions** - You must be a Google Workspace admin
4. **Verify domain** - Make sure `thomas@theprogressmethod.com` is the correct admin email

### If You Get "access_denied":

- The admin user needs "Reports API" access permissions
- Check Google Admin Console → Admin roles → Super Admin access

### If You Get "forbidden":

- Your Google Workspace plan must support Admin Reports API
- Basic plans may not have access to detailed Meet reports

## ✅ Success Indicators

Once Domain-Wide Delegation is working, you'll see:

1. **API Connection Test Passes** - All 4/4 tests successful
2. **Meet Data Retrieved** - Real Meet events appear in test results  
3. **No Authorization Errors** - Clean API responses

## 🎯 What This Enables

Once this final step is complete, the system will be able to:

- **Automatically detect** when people join/leave Google Meet sessions
- **Track exact join times** for punctuality analysis  
- **Match participants** to your internal user database
- **Generate accurate attendance** records without manual entry
- **Provide real insights** into meeting attendance patterns

## 📞 Need Help?

If you encounter issues:

1. **Check Google Admin Console logs:**
   - Security → Investigation tool → Look for API access attempts

2. **Verify service account setup:**
   - Google Cloud Console → IAM & Admin → Service Accounts
   - Ensure Domain-Wide Delegation is enabled

3. **Test with admin user:**
   - Make sure `thomas@theprogressmethod.com` has full admin rights

---

**This is the final configuration step for automatic attendance tracking!** 🚀