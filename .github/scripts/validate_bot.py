#!/usr/bin/env python3
"""
Validate Telegram Bot Token
Ensures the bot token is valid and the bot is accessible
"""

import os
import sys
import json
import urllib.request
import urllib.error

def validate_bot_token():
    """Validate the bot token by calling Telegram API"""
    bot_token = os.environ.get('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN environment variable not set")
        return False
    
    # Check token format
    if not bot_token or ':' not in bot_token:
        print("❌ Invalid bot token format")
        return False
    
    # Call Telegram API to validate
    api_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot validated: @{bot_info.get('username', 'unknown')}")
                print(f"   Bot ID: {bot_info.get('id', 'unknown')}")
                print(f"   Name: {bot_info.get('first_name', 'unknown')}")
                return True
            else:
                print(f"❌ Bot validation failed: {data.get('description', 'Unknown error')}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error validating bot: {e.code}")
        return False
    except Exception as e:
        print(f"❌ Error validating bot: {str(e)}")
        return False

if __name__ == "__main__":
    success = validate_bot_token()
    sys.exit(0 if success else 1)
