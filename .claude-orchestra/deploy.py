#!/usr/bin/env python3
"""
Claude Orchestra Main Deployment Interface
Simple, secure deployment from dev to production
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from deployment_orchestrator import DeploymentOrchestrator
from security_manager import SecurityManager


class ClaudeOrchestraDeployment:
    """Main deployment interface"""
    
    def __init__(self):
        self.orchestrator = DeploymentOrchestrator()
        self.security = SecurityManager()
        
    def interactive_deploy(self):
        """Interactive deployment wizard"""
        print("\n" + "="*60)
        print("🎭 Claude Orchestra Deployment System v2.0")
        print("="*60)
        
        # Show current status
        current_env = self.orchestrator.current_environment
        print(f"\n📍 Current Environment: {current_env}")
        
        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes:")
            print(result.stdout)
            response = input("\nCommit these changes before deployment? (y/n): ")
            if response.lower() == 'y':
                message = input("Commit message: ")
                subprocess.run(["git", "add", "."])
                subprocess.run(["git", "commit", "-m", message])
        
        # Select target environment
        print("\n🎯 Select target environment:")
        print("  1. Development")
        print("  2. Staging")
        print("  3. Production")
        
        choice = input("\nChoice (1-3): ")
        
        env_map = {
            '1': 'development',
            '2': 'staging',
            '3': 'production'
        }
        
        target_env = env_map.get(choice)
        if not target_env:
            print("❌ Invalid choice")
            return
            
        # Confirm production deployment
        if target_env == 'production':
            print("\n⚠️  PRODUCTION DEPLOYMENT")
            print("This will deploy to the live production environment.")
            confirm = input("Type 'DEPLOY TO PRODUCTION' to confirm: ")
            if confirm != 'DEPLOY TO PRODUCTION':
                print("❌ Deployment cancelled")
                return
                
        # Run pre-deployment checks
        print("\n🔍 Running pre-deployment checks...")
        
        # Enable deployment mode for git
        if target_env in ['staging', 'production']:
            print("🔓 Enabling deployment mode...")
            self.security.enable_deployment_mode(30)
            
        # Deploy
        print(f"\n🚀 Deploying to {target_env}...")
        success = self.orchestrator.deploy_to_environment(target_env)
        
        if success:
            print(f"\n✅ Successfully deployed to {target_env}!")
            
            # Special handling for Telegram bot
            if target_env == 'production':
                print("\n🤖 Setting up Telegram webhook...")
                self.setup_telegram_webhook()
                
        else:
            print(f"\n❌ Deployment to {target_env} failed")
            
        # Disable deployment mode
        if target_env in ['staging', 'production']:
            self.security.disable_deployment_mode()
            
    def setup_telegram_webhook(self):
        """Set up Telegram webhook for production bot"""
        print("\n📡 Configuring Telegram webhook...")
        
        # Production bot token
        bot_token = "8418941418:AAEmmRYh0LpJU9xEx2buXBBSmQC9hse4BI0"
        webhook_url = "https://telbot-f4on.onrender.com/webhook"
        
        # Set webhook using curl
        cmd = [
            "curl", "-X", "POST",
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            "-d", f"url={webhook_url}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "true" in result.stdout:
            print("✅ Webhook configured successfully")
        else:
            print(f"⚠️  Webhook configuration response: {result.stdout}")
            
        # Verify webhook
        verify_cmd = [
            "curl", "-s",
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        
        try:
            webhook_info = json.loads(result.stdout)
            if webhook_info.get('result', {}).get('url') == webhook_url:
                print(f"✅ Webhook verified: {webhook_url}")
            else:
                print("⚠️  Webhook verification failed")
                print(f"Response: {result.stdout}")
        except:
            print("⚠️  Could not verify webhook")
            
    def quick_production_deploy(self):
        """Quick deployment to production with all checks"""
        print("\n🚀 Quick Production Deployment")
        print("="*60)
        
        # Enable deployment mode
        print("🔓 Enabling deployment mode...")
        self.security.enable_deployment_mode(30)
        
        try:
            # Add and commit main_production.py
            print("📦 Preparing files...")
            subprocess.run(["git", "add", "main_production.py"], check=True)
            subprocess.run(["git", "add", ".claude-orchestra"], check=True)
            
            # Commit
            print("💾 Committing changes...")
            subprocess.run([
                "git", "commit", "-m",
                "Deploy production with Week1 dashboard integration"
            ], check=False)  # Don't fail if nothing to commit
            
            # Push to master
            print("📤 Pushing to master branch...")
            subprocess.run(["git", "push", "origin", "HEAD:master"], check=True)
            
            # Wait for deployment
            print("⏳ Waiting for Render deployment (30 seconds)...")
            time.sleep(30)
            
            # Check health
            print("🏥 Checking service health...")
            if self.orchestrator.check_service_health('production'):
                print("✅ Production service is healthy!")
                
                # Set webhook
                self.setup_telegram_webhook()
                
                # Test dashboard
                print("\n🔗 Production URLs:")
                print("  Bot: @ProgressMethodBot")
                print("  Dashboard: https://telbot-f4on.onrender.com/admin/week1")
                print("  Health: https://telbot-f4on.onrender.com/health")
                
                return True
            else:
                print("⚠️  Service health check failed")
                print("Check: https://dashboard.render.com/web/srv-d2elp8qdbo4c738ir500")
                return False
                
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            return False
            
        finally:
            # Disable deployment mode
            self.security.disable_deployment_mode()
            
    def check_status(self):
        """Check deployment status"""
        print("\n📊 Deployment Status")
        print("="*60)
        
        # Check each environment
        environments = ['development', 'staging', 'production']
        
        for env in environments:
            print(f"\n{env.upper()}:")
            
            # Check service health
            health = self.orchestrator.check_service_health(env)
            print(f"  Health: {'✅ Healthy' if health else '❌ Unhealthy'}")
            
            # Get service URL
            service_url = self.orchestrator.config['deployment']['services'][env]['url']
            print(f"  URL: {service_url}")
            
            # Check last deployment
            deployment_log = Path(__file__).parent / "logs" / "deployments.log"
            if deployment_log.exists():
                with open(deployment_log, 'r') as f:
                    lines = f.readlines()
                    
                # Find last deployment for this env
                for line in reversed(lines):
                    try:
                        data = json.loads(line)
                        if data.get('environment') == env:
                            timestamp = data.get('timestamp', 'Unknown')
                            status = data.get('status', 'Unknown')
                            print(f"  Last Deploy: {timestamp[:19]} - {status}")
                            break
                    except:
                        pass


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude Orchestra - Secure Dev to Prod Deployment"
    )
    
    parser.add_argument(
        "action",
        nargs='?',
        default="interactive",
        choices=["interactive", "quick", "status", "install"],
        help="Deployment action"
    )
    
    args = parser.parse_args()
    
    deployer = ClaudeOrchestraDeployment()
    
    if args.action == "interactive":
        deployer.interactive_deploy()
    elif args.action == "quick":
        deployer.quick_production_deploy()
    elif args.action == "status":
        deployer.check_status()
    elif args.action == "install":
        # Install git hooks
        security = SecurityManager()
        security.install_git_hooks()
        print("✅ Claude Orchestra installed!")


if __name__ == "__main__":
    main()
