#!/bin/bash
# MCP Server Setup Script - Simple wrapper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SCRIPT="$SCRIPT_DIR/setup_mcp_servers.py"

echo "🚀 MCP Server Auto-Installer"
echo "=========================="

# Check if Python requirements are installed
if ! python3 -c "import psutil, requests" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r "$SCRIPT_DIR/requirements-mcp.txt"
fi

# Run the main script
python3 "$MCP_SCRIPT" "$@"