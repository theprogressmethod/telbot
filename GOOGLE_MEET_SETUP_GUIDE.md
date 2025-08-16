# Google Meet REST API Setup Guide

## 🚀 Complete Setup Instructions

This guide will walk you through setting up Google Meet REST API integration for automated attendance tracking in your pod meetings.

## Step 1: Google Cloud Console Setup

### 1.1 Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID** - you'll need this later

### 1.2 Enable Google Meet REST API
1. In the Google Cloud Console, go to **APIs & Services > Library**
2. Search for "**Google Meet REST API**"
3. Click on it and press **"Enable"**
4. Wait for the API to be enabled

### 1.3 Set up Authentication

#### Option A: Service Account (Recommended)

1. **Create Service Account:**
   - Go to **IAM & Admin > Service Accounts**
   - Click **"Create Service Account"**
   - Name: `telbot-meet-integration`
   - Description: `Service account for TelBot Google Meet integration`
   - Click **Create and Continue**

2. **Grant Roles:**
   - For basic functionality, no additional roles needed
   - Click **Continue** then **Done**

3. **Generate Key:**
   - Click on your newly created service account
   - Go to **Keys** tab
   - Click **Add Key > Create New Key**
   - Select **JSON** format
   - Download the file and save it securely as `google-meet-service-account.json`

#### Option B: OAuth 2.0 (Alternative)

1. **Create OAuth Credentials:**
   - Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth 2.0 Client IDs**
   - Configure OAuth consent screen if prompted
   - Application type: **Web application**
   - Add authorized redirect URIs as needed
   - Download the client credentials JSON

## Step 2: Local Environment Setup

### 2.1 Install Dependencies

```bash
pip install -r requirements_google_meet.txt
```

### 2.2 Environment Configuration

Add these variables to your `.env` file:

```bash
# Google Meet API Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_MEET_SERVICE_ACCOUNT_FILE=/absolute/path/to/google-meet-service-account.json

# Optional: OAuth credentials (if using OAuth instead of service account)
# GOOGLE_MEET_CLIENT_ID=your-client-id
# GOOGLE_MEET_CLIENT_SECRET=your-client-secret
```

**Important Security Notes:**
- Store the service account JSON file outside your repository
- Never commit credentials to version control
- Use absolute paths for the service account file

### 2.3 File Placement

Recommended structure:
```
/secure-credentials/
  └── google-meet-service-account.json
/your-project/
  └── telbot/
      ├── .env
      └── ... (your code)
```

Update your `.env`:
```bash
GOOGLE_MEET_SERVICE_ACCOUNT_FILE=/secure-credentials/google-meet-service-account.json
```

## Step 3: Verify Setup

### 3.1 Test API Connection

Run this test to verify your setup:

```bash
python -c "
import asyncio
from google_meet_integration import GoogleMeetIntegration

async def test():
    integration = GoogleMeetIntegration()
    success = await integration.initialize()
    print('✅ Google Meet API connected successfully!' if success else '❌ Connection failed')

asyncio.run(test())
"
```

### 3.2 Check Application Status

Start your application and check the Google Meet status endpoint:

```bash
curl -X GET http://localhost:8000/admin/api/attendance/google-meet/status \
  -H "X-Admin-Key: your-admin-key"
```

Expected response:
```json
{
  "status": "success",
  "google_meet_available": true,
  "integration_initialized": true,
  "service_connected": true,
  "project_id": "your-project-id",
  "required_env_vars": {
    "GOOGLE_CLOUD_PROJECT_ID": true,
    "GOOGLE_MEET_SERVICE_ACCOUNT_FILE": true
  },
  "capabilities": [
    "create_meeting_spaces",
    "track_participants", 
    "automatic_attendance_sync",
    "detailed_session_analytics"
  ]
}
```

## Step 4: Usage Examples

### 4.1 Create Meeting with Google Meet

```bash
curl -X POST http://localhost:8000/admin/api/attendance/google-meet/create-meeting \
  -H "X-Admin-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "pod_id": "11111111-1111-1111-1111-111111111111",
    "pod_name": "Test Pod Alpha",
    "meeting_date": "2025-08-16"
  }'
```

Response:
```json
{
  "status": "success",
  "meeting_id": "meeting-uuid",
  "pod_id": "11111111-1111-1111-1111-111111111111",
  "meeting_date": "2025-08-16",
  "google_meet": {
    "space_id": "spaces/space-id",
    "meeting_uri": "https://meet.google.com/abc-defg-hij",
    "meeting_code": "abc-defg-hij"
  }
}
```

### 4.2 Get Meeting Attendance

After the meeting ends, retrieve attendance data:

```bash
curl -X GET http://localhost:8000/admin/api/attendance/google-meet/attendance/spaces/SPACE_ID \
  -H "X-Admin-Key: your-admin-key"
```

### 4.3 Sync to Attendance System

```bash
curl -X POST http://localhost:8000/admin/api/attendance/google-meet/sync/SPACE_ID/MEETING_ID \
  -H "X-Admin-Key: your-admin-key"
```

## Step 5: Troubleshooting

### Common Issues

#### 1. "Google Meet integration not available"
- **Solution**: Install dependencies: `pip install -r requirements_google_meet.txt`

#### 2. "Service account file not found"
- **Solution**: Check the file path in `GOOGLE_MEET_SERVICE_ACCOUNT_FILE`
- Ensure path is absolute, not relative
- Verify file permissions are readable

#### 3. "Authentication failed"
- **Solution**: 
  - Verify the service account JSON is valid
  - Check that Google Meet REST API is enabled in your project
  - Ensure service account has necessary permissions

#### 4. "Project ID not found"
- **Solution**: Set `GOOGLE_CLOUD_PROJECT_ID` in your `.env` file

#### 5. Permission errors
- **Solution**: The service account needs access to create and read Meet spaces
- For organization accounts, domain admin may need to grant permissions

### Debug Mode

Enable detailed logging by adding to your environment:
```bash
GOOGLE_API_LOG_LEVEL=DEBUG
```

## Step 6: Production Considerations

### Security
- Use Google Cloud Secret Manager for production credentials
- Implement credential rotation policies
- Restrict service account permissions to minimum required

### Monitoring
- Set up alerts for API quota limits
- Monitor authentication failures
- Track meeting creation/sync success rates

### Scaling
- Google Meet API has rate limits - implement backoff strategies
- Consider caching participant data to reduce API calls
- Use batch operations when possible

## Step 7: Workspace Integration (Optional)

For Google Workspace organizations:

### Domain-Wide Delegation
1. In Google Cloud Console, edit your service account
2. Enable "Domain-wide delegation"
3. Note the Client ID
4. In Google Admin Console, go to Security > API Controls > Domain-wide Delegation
5. Add your service account's Client ID with scopes:
   - `https://www.googleapis.com/auth/meetings.space.created`
   - `https://www.googleapis.com/auth/meetings.space.readonly`

### Benefits
- Access meetings created by any user in your domain
- Better participant identification through workspace directory
- Enhanced security through workspace policies

---

## 🎯 Next Steps After Setup

Once Google Meet integration is working:

1. **Test with Real Meetings**: Create test pod meetings and verify attendance tracking
2. **User Matching Logic**: Implement `_match_participant_to_user()` function to connect Google Meet participants to your users
3. **Automated Workflows**: Set up scheduled sync jobs to automatically pull attendance after meetings
4. **Dashboard Integration**: Add Google Meet data to your attendance dashboards
5. **Nurture Sequence Integration**: Connect attendance insights to personalized messaging

The Google Meet integration provides the automated attendance tracking foundation needed for your 10x-100x nurture sequence personalization goals!

---

**Setup completed? Test with the status endpoint and create your first integrated meeting!**