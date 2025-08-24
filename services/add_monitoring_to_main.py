#!/usr/bin/env python3
"""
Add monitoring routes to main.py for production deployment
"""

import os

def add_monitoring_to_main():
    """Add webhook monitoring to main.py"""
    
    # Read current main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if monitoring is already added
    if 'webhook_monitoring' in content:
        print("✅ Monitoring already added to main.py")
        return
    
    # Find the import section and add monitoring import
    if 'from webhook_monitoring import' not in content:
        # Add import after other imports
        import_line = 'from webhook_monitoring import add_webhook_monitoring_routes, track_webhook_request\n'
        
        # Find a good place to add the import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from supabase import'):
                lines.insert(i + 1, import_line.strip())
                break
        
        content = '\n'.join(lines)
    
    # Add monitoring routes setup
    if 'add_webhook_monitoring_routes(app)' not in content:
        # Find where routes are added and add monitoring
        setup_line = '\n# Add webhook monitoring routes\nadd_webhook_monitoring_routes(app)\n'
        
        # Find the webhook handler section
        webhook_pos = content.find('@app.post("/webhook")')
        if webhook_pos > 0:
            # Insert before webhook handler
            content = content[:webhook_pos] + setup_line + content[webhook_pos:]
    
    # Add request tracking to webhook handler
    if 'track_webhook_request(' not in content:
        # Find the webhook return statements and add tracking
        content = content.replace(
            'return {"ok": True}',
            'track_webhook_request(True)\n        return {"ok": True}'
        )
        content = content.replace(
            'return {"ok": False, "error": "Invalid data format"}',
            'track_webhook_request(False)\n            return {"ok": False, "error": "Invalid data format"}'
        )
        content = content.replace(
            'return {"ok": False, "error": "Bot import failed"}',
            'track_webhook_request(False)\n            return {"ok": False, "error": "Bot import failed"}'
        )
        content = content.replace(
            'return {"ok": False, "error": f"Validation failed: {str(ve)}"}',
            'track_webhook_request(False)\n            return {"ok": False, "error": f"Validation failed: {str(ve)}"}'
        )
    
    # Write updated main.py
    with open('main.py', 'w') as f:
        f.write(content)
    
    print("✅ Added monitoring routes to main.py")
    print("📊 New endpoints available:")
    print("  - /webhook/health - Webhook health check")
    print("  - /webhook/stats - Request statistics")
    print("  - /webhook/recover - Emergency recovery")
    print("  - /bot/dashboard - Monitoring dashboard")

if __name__ == "__main__":
    add_monitoring_to_main()
    print("\n🚀 Ready to deploy with monitoring!")
    print("Next steps:")
    print("1. git add . && git commit -m 'Add bot monitoring system'")
    print("2. git push (deploys to Render)")
    print("3. Visit https://telbot-f4on.onrender.com/bot/dashboard")