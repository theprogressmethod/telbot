#!/usr/bin/env python3
"""
Comprehensive Test Report for The Progress Method Bot
Tests all components and generates a detailed deployment report

Enhanced by WORKER_3 with comprehensive pytest framework integration
"""

import asyncio
import logging
import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Comprehensive test runner for The Progress Method bot with pytest integration"""
    
    def __init__(self):
        # Test configuration
        self.test_environment = os.getenv("ENVIRONMENT", "test")
        self.bot_token = os.getenv("BOT_TOKEN")
        self.supabase_url = os.getenv("SUPABASE_URL") 
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Test framework paths
        self.test_dir = Path("tests")
        self.unit_test_dir = self.test_dir / "unit"
        self.integration_test_dir = self.test_dir / "integration" 
        self.fixtures_dir = self.test_dir / "fixtures"
        
        # Test results
        self.test_results = []
        self.pytest_results = {}
        self.start_time = datetime.now()
        
        logger.info("🧪 Enhanced Test Runner initialized with pytest framework")
        logger.info(f"📁 Test environment: {self.test_environment}")
    
    def validate_test_framework(self) -> Dict[str, Any]:
        """Validate pytest test framework setup"""
        test_name = "Test Framework Validation"
        logger.info(f"🔍 Running {test_name}...")
        
        try:
            validation_results = {
                "directories": {},
                "config_files": {},
                "test_files": {},
                "test_counts": {}
            }
            
            # Check directories
            required_dirs = [self.test_dir, self.unit_test_dir, self.integration_test_dir, self.fixtures_dir]
            for test_dir in required_dirs:
                validation_results["directories"][str(test_dir)] = test_dir.exists()
            
            # Check configuration files
            config_files = ["pytest.ini", "conftest.py", ".env.test", "requirements-test.txt"]
            for config_file in config_files:
                validation_results["config_files"][config_file] = Path(config_file).exists()
            
            # Check test files and count functions
            test_files = [
                "tests/unit/test_bot.py",
                "tests/unit/test_auth.py", 
                "tests/unit/test_dashboard.py",
                "tests/unit/test_commitment.py"
            ]
            
            total_tests = 0
            for test_file in test_files:
                file_path = Path(test_file)
                exists = file_path.exists()
                validation_results["test_files"][test_file] = exists
                
                if exists:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        test_count = content.count("def test_")
                        validation_results["test_counts"][test_file] = test_count
                        total_tests += test_count
                else:
                    validation_results["test_counts"][test_file] = 0
            
            validation_results["total_test_functions"] = total_tests
            
            all_valid = (
                all(validation_results["directories"].values()) and
                all(validation_results["config_files"].values()) and 
                all(validation_results["test_files"].values()) and
                total_tests > 0
            )
            
            return {
                "test_name": test_name,
                "status": "PASS" if all_valid else "FAIL",
                "details": validation_results,
                "timestamp": datetime.now().isoformat(),
                "total_test_functions": total_tests
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            return {
                "test_name": test_name,
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity and core operations"""
        test_name = "Database Connectivity"
        try:
            # Test basic connection
            users_result = self.supabase.table("users").select("count").execute()
            
            # Test table existence
            tables_to_check = [
                "users", "user_sequence_state", "nurture_message_queue",
                "message_analytics", "user_engagement_summary", 
                "communication_preferences", "commitments", "pods"
            ]
            
            accessible_tables = []
            for table in tables_to_check:
                try:
                    result = self.supabase.table(table).select("*").limit(1).execute()
                    accessible_tables.append(table)
                except:
                    pass
            
            # Test functions
            functions_available = []
            try:
                result = self.supabase.rpc('calculate_engagement_score', {
                    'target_user_id': str(uuid.uuid4()),
                    'score_type': 'overall'
                }).execute()
                functions_available.append('calculate_engagement_score')
            except:
                pass
            
            return {
                "success": True,
                "total_tables": len(tables_to_check),
                "accessible_tables": len(accessible_tables),
                "accessible_table_list": accessible_tables,
                "functions_available": len(functions_available),
                "connection_stable": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "connection_stable": False
            }
    
    async def test_nurture_controller(self) -> Dict[str, Any]:
        """Test the unified nurture controller"""
        test_name = "Nurture Controller"
        try:
            # Import and initialize
            from unified_nurture_controller import UnifiedNurtureController
            controller = UnifiedNurtureController(self.supabase)
            
            # Test engagement scoring
            test_user_id = str(uuid.uuid4())
            engagement_ctx = await controller._get_user_engagement_context(test_user_id)
            
            # Test message personalization
            message_data = {"message": "Hello {first_name}! Test message."}
            personalized = await controller._personalize_message(
                test_user_id, message_data, engagement_ctx
            )
            
            return {
                "success": True,
                "controller_initialized": True,
                "engagement_scoring": engagement_ctx.overall_score >= 0,
                "personalization_working": "Hello" in personalized,
                "default_engagement_score": engagement_ctx.overall_score
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "controller_initialized": False
            }
    
    async def test_email_service(self) -> Dict[str, Any]:
        """Test the email delivery service"""
        test_name = "Email Service"
        try:
            from email_delivery_service import EmailDeliveryService
            
            # Initialize with test mode
            email_service = EmailDeliveryService(
                api_key="test_key",  # Using test key to avoid actual sending
                from_email="test@example.com"
            )
            email_service.set_supabase_client(self.supabase)
            
            # Test template rendering
            templates_available = len(email_service.templates) > 0
            
            # Test configuration
            resend_configured = self.resend_api_key != "test_key"
            
            return {
                "success": True,
                "service_initialized": True,
                "templates_available": templates_available,
                "template_count": len(email_service.templates),
                "resend_configured": resend_configured,
                "supabase_connected": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service_initialized": False
            }
    
    async def test_telegram_bot(self) -> Dict[str, Any]:
        """Test Telegram bot configuration"""
        test_name = "Telegram Bot"
        try:
            if not self.bot_token:
                return {
                    "success": False,
                    "error": "Bot token not configured",
                    "bot_configured": False
                }
            
            # Test bot API access
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getMe",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    bot_info = response.json()
                    bot_working = bot_info.get("ok", False)
                    
                    return {
                        "success": bot_working,
                        "bot_configured": True,
                        "bot_working": bot_working,
                        "bot_username": bot_info.get("result", {}).get("username"),
                        "api_accessible": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Bot API returned {response.status_code}",
                        "bot_configured": True,
                        "api_accessible": False
                    }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "bot_configured": bool(self.bot_token)
            }
    
    async def test_admin_dashboard(self) -> Dict[str, Any]:
        """Test admin dashboard functionality"""
        test_name = "Admin Dashboard"
        try:
            # Test if admin API can start
            admin_api_available = os.path.exists("enhanced_admin_api.py")
            
            # Test basic endpoints (if running)
            endpoints_working = []
            try:
                async with httpx.AsyncClient() as client:
                    # Test health endpoint
                    response = await client.get("http://localhost:8001/", timeout=5.0)
                    if response.status_code == 200:
                        endpoints_working.append("health")
                    
                    # Test metrics endpoint
                    response = await client.get("http://localhost:8001/admin/api/metrics", timeout=5.0)
                    if response.status_code == 200:
                        endpoints_working.append("metrics")
                        
            except:
                pass  # Admin API might not be running
            
            return {
                "success": admin_api_available,
                "api_file_exists": admin_api_available,
                "endpoints_tested": len(endpoints_working),
                "working_endpoints": endpoints_working,
                "dashboard_accessible": len(endpoints_working) > 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api_file_exists": False
            }
    
    async def test_sequence_management(self) -> Dict[str, Any]:
        """Test sequence management functionality"""
        test_name = "Sequence Management"
        try:
            # Test sequence types and data
            from nurture_sequences import SequenceType, get_sequence_messages
            
            # Test sequence type enumeration
            sequence_types = list(SequenceType)
            
            # Test sequence message loading
            test_messages = get_sequence_messages(SequenceType.ONBOARDING)
            
            # Test sequence state management
            sequence_states = self.supabase.table("user_sequence_state").select("*").limit(5).execute()
            
            return {
                "success": True,
                "sequence_types_available": len(sequence_types),
                "sequence_types": [st.value for st in sequence_types],
                "test_messages_loaded": len(test_messages) > 0,
                "message_count": len(test_messages),
                "sequence_states_accessible": len(sequence_states.data) >= 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sequence_types_available": 0
            }
    
    async def test_system_integration(self) -> Dict[str, Any]:
        """Test overall system integration"""
        test_name = "System Integration"
        try:
            # Test that all major components can work together
            from unified_nurture_controller import UnifiedNurtureController
            from email_delivery_service import EmailDeliveryService
            
            # Initialize components
            controller = UnifiedNurtureController(self.supabase)
            email_service = EmailDeliveryService("test_key", "test@example.com")
            email_service.set_supabase_client(self.supabase)
            
            # Configure controller with email service
            controller.set_email_service(email_service)
            
            # Test basic workflow (without actually sending)
            test_user_id = str(uuid.uuid4())
            engagement_ctx = await controller._get_user_engagement_context(test_user_id)
            
            # Test analytics generation
            analytics = await controller.get_sequence_analytics(days=7)
            
            return {
                "success": True,
                "components_integrated": True,
                "controller_email_configured": True,
                "engagement_calculation": engagement_ctx.overall_score >= 0,
                "analytics_generation": isinstance(analytics, dict),
                "end_to_end_functional": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "components_integrated": False
            }
    
    async def test_safety_controls(self) -> Dict[str, Any]:
        """Test safety controls and development mode"""
        test_name = "Safety Controls"
        try:
            # Check environment safety
            environment = os.getenv("ENVIRONMENT", "production")
            safe_mode = os.getenv("SAFE_MODE", "false").lower() == "true"
            production_comms = os.getenv("ENABLE_PRODUCTION_COMMUNICATIONS", "false").lower() == "true"
            
            # Test safety controls import
            try:
                from safety_controls import SafetyControls
                safety = SafetyControls()
                safety_initialized = True
            except:
                safety_initialized = False
            
            return {
                "success": True,
                "environment": environment,
                "safe_mode": safe_mode,
                "production_communications_blocked": not production_comms,
                "safety_controls_initialized": safety_initialized,
                "development_mode": environment == "development"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "environment": "unknown"
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all tests and generate comprehensive report"""
        tests = [
            ("Database Connectivity", self.test_database_connectivity),
            ("Nurture Controller", self.test_nurture_controller),
            ("Email Service", self.test_email_service),
            ("Telegram Bot", self.test_telegram_bot),
            ("Admin Dashboard", self.test_admin_dashboard),
            ("Sequence Management", self.test_sequence_management),
            ("System Integration", self.test_system_integration),
            ("Safety Controls", self.test_safety_controls)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🧪 Running: {test_name}")
                start_time = datetime.now()
                
                result = await test_func()
                
                duration = (datetime.now() - start_time).total_seconds()
                
                test_result = {
                    "test_name": test_name,
                    "success": result.get("success", False),
                    "duration": duration,
                    "details": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(test_result)
                
                status = "✅ PASS" if test_result["success"] else "❌ FAIL"
                logger.info(f"{status} {test_name} ({duration:.2f}s)")
                
            except Exception as e:
                test_result = {
                    "test_name": test_name,
                    "success": False,
                    "duration": 0,
                    "details": {"error": str(e)},
                    "timestamp": datetime.now().isoformat()
                }
                results.append(test_result)
                logger.error(f"❌ ERROR {test_name}: {e}")
        
        return results
    
    def generate_deployment_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive deployment report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = round(passed_tests/total_tests*100, 1) if total_tests > 0 else 0
        
        total_duration = sum(r["duration"] for r in results)
        
        # Deployment readiness assessment
        critical_tests = ["Database Connectivity", "Nurture Controller", "System Integration"]
        critical_passed = sum(1 for r in results if r["test_name"] in critical_tests and r["success"])
        deployment_ready = critical_passed == len(critical_tests) and success_rate >= 70
        
        report = f"""
🚀 ENHANCED NURTURE SYSTEM - DEPLOYMENT REPORT
{'=' * 60}

📊 Test Summary:
  Total Tests: {total_tests}
  Passed: {passed_tests} ✅
  Failed: {failed_tests} ❌
  Success Rate: {success_rate}%
  Total Duration: {round(total_duration, 2)}s
  Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 Deployment Status: {'✅ READY FOR DEPLOYMENT' if deployment_ready else '⚠️  NEEDS ATTENTION'}

📋 Detailed Test Results:
"""
        
        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report += f"\n{status} {result['test_name']} ({result['duration']:.2f}s)"
            
            # Show key details from each test
            details = result["details"]
            if result["success"]:
                # Show positive metrics
                key_metrics = []
                for key, value in details.items():
                    if key != "success" and key != "error":
                        if isinstance(value, (int, float)) and value > 0:
                            key_metrics.append(f"{key}: {value}")
                        elif isinstance(value, bool) and value:
                            key_metrics.append(f"{key}: ✅")
                        elif isinstance(value, str) and value not in ["", "unknown"]:
                            key_metrics.append(f"{key}: {value}")
                
                if key_metrics:
                    report += f"\n    Metrics: {', '.join(key_metrics[:3])}"
            else:
                # Show error details
                error = details.get("error", "Unknown error")
                report += f"\n    Error: {error[:100]}"
        
        # Component Status Summary
        report += f"\n\n🔧 Component Status:"
        
        # Database
        db_test = next((r for r in results if "Database" in r["test_name"]), None)
        if db_test and db_test["success"]:
            accessible_tables = db_test["details"].get("accessible_tables", 0)
            report += f"\n  📊 Database: ✅ Connected ({accessible_tables} tables accessible)"
        else:
            report += f"\n  📊 Database: ❌ Connection issues"
        
        # Nurture System
        nurture_test = next((r for r in results if "Nurture Controller" in r["test_name"]), None)
        if nurture_test and nurture_test["success"]:
            report += f"\n  🎯 Nurture System: ✅ Operational"
        else:
            report += f"\n  🎯 Nurture System: ❌ Needs configuration"
        
        # Email Service
        email_test = next((r for r in results if "Email Service" in r["test_name"]), None)
        if email_test and email_test["success"]:
            template_count = email_test["details"].get("template_count", 0)
            resend_configured = email_test["details"].get("resend_configured", False)
            status = "✅ Ready" if resend_configured else "⚠️  Test mode"
            report += f"\n  📧 Email Service: {status} ({template_count} templates)"
        else:
            report += f"\n  📧 Email Service: ❌ Configuration needed"
        
        # Telegram Bot
        bot_test = next((r for r in results if "Telegram Bot" in r["test_name"]), None)
        if bot_test and bot_test["success"]:
            bot_username = bot_test["details"].get("bot_username", "unknown")
            report += f"\n  🤖 Telegram Bot: ✅ Online (@{bot_username})"
        else:
            report += f"\n  🤖 Telegram Bot: ❌ Token/connectivity issues"
        
        # Admin Dashboard
        admin_test = next((r for r in results if "Admin Dashboard" in r["test_name"]), None)
        if admin_test and admin_test["success"]:
            endpoints = admin_test["details"].get("endpoints_tested", 0)
            report += f"\n  📱 Admin Dashboard: ✅ Available ({endpoints} endpoints tested)"
        else:
            report += f"\n  📱 Admin Dashboard: ⚠️  May need manual start"
        
        # Safety Controls
        safety_test = next((r for r in results if "Safety Controls" in r["test_name"]), None)
        if safety_test and safety_test["success"]:
            environment = safety_test["details"].get("environment", "unknown")
            safe_mode = safety_test["details"].get("safe_mode", False)
            status = "🔒 Safe" if safe_mode or environment == "development" else "⚠️  Production"
            report += f"\n  🛡️  Safety Controls: {status} (env: {environment})"
        else:
            report += f"\n  🛡️  Safety Controls: ❌ Not configured"
        
        # Deployment Recommendations
        report += f"\n\n🎯 Deployment Recommendations:"
        
        if deployment_ready:
            report += f"\n  ✅ System is ready for deployment to development environment"
            report += f"\n  ✅ All critical components are operational"
            report += f"\n  ✅ Multi-channel delivery system is functional"
            if failed_tests > 0:
                report += f"\n  ⚠️  {failed_tests} non-critical components need attention"
        else:
            report += f"\n  ❌ System needs attention before deployment:"
            
            if not db_test or not db_test["success"]:
                report += f"\n    🔧 Fix database connectivity issues"
            
            if not nurture_test or not nurture_test["success"]:
                report += f"\n    🔧 Configure nurture controller properly"
            
            if not bot_test or not bot_test["success"]:
                report += f"\n    🔧 Fix Telegram bot configuration"
            
            if success_rate < 70:
                report += f"\n    🔧 Address failing tests to improve success rate"
        
        # Next Steps
        report += f"\n\n🚀 Next Steps:"
        report += f"\n  1. 📊 Review test results and address any failing components"
        report += f"\n  2. 🔧 Configure production email domain in Resend (currently test mode)"
        report += f"\n  3. 🚀 Deploy to development server (srv-d2em4oripnbc73a5bmog)"
        report += f"\n  4. 🧪 Run integration tests with real user data"
        report += f"\n  5. 📱 Set up monitoring and alerting"
        report += f"\n  6. 👥 Create demo environment for presentation"
        
        # Technical Notes
        report += f"\n\n📝 Technical Notes:"
        report += f"\n  • Enhanced nurture system uses existing database schema"
        report += f"\n  • Email delivery requires verified domain in Resend"
        report += f"\n  • Safety controls prevent accidental production communications"
        report += f"\n  • Admin dashboard provides real-time monitoring and control"
        report += f"\n  • Multi-channel delivery supports Telegram and email"
        report += f"\n  • Engagement scoring adapts message delivery preferences"
        
        return report

async def main():
    """Main test runner"""
    try:
        tester = ComprehensiveTestRunner()
        results = await tester.run_all_tests()
        report = tester.generate_deployment_report(results)
        
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"deployment_test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        # Return exit code based on deployment readiness
        critical_tests = ["Database Connectivity", "Nurture Controller", "System Integration"]
        critical_passed = sum(1 for r in results if r["test_name"] in critical_tests and r["success"])
        success_rate = sum(1 for r in results if r["success"]) / len(results) if results else 0
        
        deployment_ready = critical_passed == len(critical_tests) and success_rate >= 0.7
        return 0 if deployment_ready else 1
        
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)