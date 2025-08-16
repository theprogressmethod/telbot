# MCP Server Auto-Installer

A robust, one-click solution to install and manage all your MCP servers locally.

## 🚀 Quick Start

```bash
# Install and start all MCP servers
./setup-mcp.sh

# Or run directly with Python
python3 setup_mcp_servers.py
```

## 📋 Supported Servers

Priority servers that will be automatically installed and configured:

- ✅ **Supabase** - Database operations and analytics
- ✅ **Render** - Deployment and hosting management  
- ✅ **Notion** - Knowledge base management
- ✅ **Context7** - Upstash vector database
- ✅ **Telegram** - Bot API integration
- ✅ **Resend** - Email services
- ✅ **GitHub** - Repository management
- ✅ **Docker** - Container operations
- ✅ **n8n** - Workflow automation (local)
- ✅ **Tally** - Form management

## 🛠️ Commands

```bash
# Setup all servers (default)
./setup-mcp.sh

# Stop all running servers
./setup-mcp.sh stop

# Restart all servers
./setup-mcp.sh restart

# Check server status
./setup-mcp.sh status
```

## 🔧 How It Works

1. **Dependency Check** - Verifies Node.js, npm, git, python3
2. **Credential Validation** - Checks environment variables for API keys
3. **Smart Installation** - Installs missing MCP servers via npm
4. **Background Startup** - Starts servers in background with logging
5. **Health Monitoring** - Verifies servers are running correctly
6. **Config Update** - Updates Claude desktop config automatically

## 📁 File Structure

```
~/.mcp_servers/          # Local MCP installation directory
├── logs/                # Server logs
│   ├── supabase.log
│   ├── render.log
│   └── ...
└── server_pids.json     # Running server process IDs

~/Library/Application Support/Claude/
└── claude_desktop_config.json  # Updated automatically
```

## 🔑 Required Environment Variables

The installer reads from your centralized credentials file:

**Primary location:** `~/projects/creds/TheProgressMethod/.env`  
**Fallback location:** `/Users/thomasmulhern/projects/telbot_env/telbot/.env`

```bash
# Supabase
SUPABASE_ACCESS_TOKEN=sbp_...
SUPABASE_PROJECT_REF=your_project_ref

# Render
RENDER_API_TOKEN=rnd_...

# Notion
NOTION_API_KEY=ntn_...

# Telegram
TG_APP_ID=your_app_id
TG_API_HASH=your_api_hash

# Resend
RESEND_API_KEY=re_...

# GitHub
GITHUB_TOKEN=ghp_...

# n8n
N8N_API_URL=https://your-n8n.com
N8N_API_KEY=your_key

# Tally
TALLY_API_KEY=your_key
```

The installer prioritizes the centralized credentials file for better security and organization.

## 🐛 Troubleshooting

### Installation Issues
```bash
# Check dependencies
node --version
npm --version
python3 --version

# Install missing dependencies
brew install node python3
```

### Server Issues
```bash
# Check logs
tail -f ~/.mcp_servers/logs/supabase.log

# Restart problematic server
./setup-mcp.sh restart
```

### Authentication Issues
```bash
# Verify environment variables
./setup-mcp.sh status

# Check your centralized .env file
cat ~/projects/creds/TheProgressMethod/.env
```

## 🔄 Integration with Claude Code

After running the installer:

1. **Restart Claude Code** to pick up the new configuration
2. **Test MCP tools** are available in your conversations
3. **Enjoy seamless integration** without authentication issues

The installer automatically updates your Claude desktop config file, so all servers will be available immediately after restart.

## 🎯 Benefits

- ✅ **One-click setup** - No manual configuration needed
- ✅ **Robust installation** - Multiple fallback methods
- ✅ **Health monitoring** - Automatic startup verification
- ✅ **Process management** - Clean start/stop/restart
- ✅ **Logging** - Full debug information available
- ✅ **Auto-configuration** - Claude config updated automatically

## 🔮 Future Enhancements

- [ ] Auto-update MCP packages
- [ ] Web dashboard for server monitoring
- [ ] Docker container support
- [ ] Service auto-restart on failure
- [ ] Integration with system startup

---

**Problem solved**: No more MCP authentication issues or manual server management!