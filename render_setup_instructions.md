# 🚀 Render MCP Setup Instructions

## Step 1: Get Your Render API Token
1. Go to: https://dashboard.render.com/account/api-keys
2. Click "Create API Key"
3. Name: "Claude MCP Access"
4. Copy the token (starts with `rnd_`)

## Step 2: Update Claude Configuration
Edit this file:
```
/Users/thomasmulhern/Library/Application Support/Claude/claude_desktop_config.json
```

Replace this line:
```json
"RENDER_API_KEY": "YOUR_RENDER_API_TOKEN_HERE"
```

With your actual token:
```json
"RENDER_API_KEY": "rnd_your_actual_token_here"
```

## Step 3: Restart Claude Desktop
- Quit Claude Desktop completely
- Reopen Claude Desktop
- The Render MCP should now be available

## Step 4: Test the Connection
Once you restart Claude, I'll be able to:
- List your Render services
- Create new services for staging/production
- Manage databases and deployments
- Set up the complete nurture sequence infrastructure

## What Happens Next?
After Render access is working, we'll:
1. Create staging environment for telbot
2. Set up production Postgres database
3. Deploy the nurture sequence system
4. Configure monitoring and alerts
5. Test end-to-end flow
6. Launch to production Monday evening

**Ready for enterprise-level deployment!** 🚀