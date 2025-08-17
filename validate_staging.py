#!/usr/bin/env python3
"""
Staging Validation Script
Quick validation of staging environment and behavioral intelligence system
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load staging environment
load_dotenv('.env.staging')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StagingValidator:
    """Validate staging environment is ready for behavioral intelligence testing"""
    
    def __init__(self):
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "environment": os.getenv('ENVIRONMENT'),
            "tests": {}
        }
        
    def validate_environment(self) -> bool:
        """Validate staging environment configuration"""
        logger.info("🔧 Validating staging environment...")
        
        checks = [
            ('Environment', os.getenv('ENVIRONMENT') == 'staging'),
            ('Safe Mode', os.getenv('SAFE_MODE') == 'true'),
            ('Staging Mode', os.getenv('STAGING_MODE') == 'true'),
            ('Production Comms Blocked', os.getenv('ENABLE_PRODUCTION_COMMUNICATIONS') == 'false')
        ]
        
        all_passed = True
        for check_name, result in checks:
            if result:
                logger.info(f"  ✅ {check_name}")
            else:
                logger.error(f"  ❌ {check_name}")
                all_passed = False
        
        self.results["tests"]["environment"] = all_passed
        return all_passed
    
    def validate_database_connection(self) -> bool:
        """Validate database connection and basic operations"""
        logger.info("🔌 Validating database connection...")
        
        try:
            supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
            
            # Test basic query
            result = supabase.table('users').select('count', count='exact').limit(1).execute()
            user_count = result.count if result.count else 0
            
            logger.info(f"  ✅ Database connected, {user_count} users in system")
            self.results["tests"]["database"] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Database connection failed: {e}")
            self.results["tests"]["database"] = False
            return False
    
    def validate_business_intelligence(self) -> bool:
        """Validate business intelligence dashboard functionality"""
        logger.info("📊 Validating business intelligence...")
        
        try:
            from business_intelligence_dashboard import BusinessIntelligenceDashboard
            
            # Initialize and test
            supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
            
            bi_dashboard = BusinessIntelligenceDashboard(supabase)
            
            # Test metrics calculation (async method)
            import asyncio
            metrics = asyncio.run(bi_dashboard.get_key_business_metrics())
            
            logger.info("  ✅ Business Intelligence Dashboard initialized")
            logger.info(f"  📈 Onboarding Rate: {metrics.get('onboarding_funnel', {}).get('conversion_rate', 'N/A')}%")
            logger.info(f"  📈 System Health: {metrics.get('system_health', {}).get('status', 'N/A')}")
            
            self.results["tests"]["business_intelligence"] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Business Intelligence validation failed: {e}")
            self.results["tests"]["business_intelligence"] = False
            return False
    
    def validate_admin_dashboard(self) -> bool:
        """Validate enhanced admin dashboard"""
        logger.info("🖥️ Validating admin dashboard...")
        
        try:
            from enhanced_admin_dashboard import get_enhanced_admin_dashboard_html
            
            # Generate dashboard HTML
            html = get_enhanced_admin_dashboard_html()
            
            # Check for key elements
            required_elements = [
                'business-intelligence',
                'Business Intelligence Dashboard',
                'onboarding-rate',
                'completion-rate'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html:
                    missing_elements.append(element)
            
            if missing_elements:
                logger.error(f"  ❌ Missing dashboard elements: {missing_elements}")
                self.results["tests"]["admin_dashboard"] = False
                return False
            
            logger.info(f"  ✅ Admin dashboard generated ({len(html)} chars)")
            logger.info("  ✅ All required elements present")
            
            self.results["tests"]["admin_dashboard"] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Admin dashboard validation failed: {e}")
            self.results["tests"]["admin_dashboard"] = False
            return False
    
    def validate_feature_flags(self) -> bool:
        """Validate feature flags configuration"""
        logger.info("🚩 Validating feature flags...")
        
        try:
            from feature_flags import get_feature_flags
            
            flags = get_feature_flags()
            report = flags.get_feature_status_report()
            
            # Check staging-appropriate configuration
            expected_enabled = [
                'business_intelligence_dashboard',
                'behavioral_analytics', 
                'enhanced_admin_dashboard'
            ]
            
            expected_disabled = [
                'superior_onboarding',
                'user_facing_metrics',
                'optimized_nurture_sequences'
            ]
            
            for feature in expected_enabled:
                if flags.is_enabled(feature):
                    logger.info(f"  ✅ {feature}: enabled (correct)")
                else:
                    logger.warning(f"  ⚠️ {feature}: disabled (should be enabled)")
            
            for feature in expected_disabled:
                if not flags.is_enabled(feature):
                    logger.info(f"  ✅ {feature}: disabled (correct)")
                else:
                    logger.warning(f"  ⚠️ {feature}: enabled (should be disabled)")
            
            logger.info(f"  📊 Environment: {report['environment']}")
            logger.info(f"  📊 Features enabled: {report['features_enabled']}/{report['features_total']}")
            
            self.results["tests"]["feature_flags"] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Feature flags validation failed: {e}")
            self.results["tests"]["feature_flags"] = False
            return False
    
    def run_validation(self) -> bool:
        """Run complete staging validation"""
        logger.info("\n" + "="*60)
        logger.info("🧪 STAGING ENVIRONMENT VALIDATION")
        logger.info("="*60)
        
        validations = [
            ("Environment Configuration", self.validate_environment),
            ("Database Connection", self.validate_database_connection),
            ("Business Intelligence", self.validate_business_intelligence),
            ("Admin Dashboard", self.validate_admin_dashboard),
            ("Feature Flags", self.validate_feature_flags)
        ]
        
        passed = 0
        total = len(validations)
        
        for validation_name, validation_func in validations:
            logger.info(f"\n🔄 {validation_name}...")
            try:
                if validation_func():
                    passed += 1
                    logger.info(f"✅ {validation_name}: PASSED")
                else:
                    logger.error(f"❌ {validation_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {validation_name}: CRASHED - {e}")
        
        # Generate summary
        success_rate = (passed / total) * 100
        
        logger.info("\n" + "="*60)
        logger.info("📊 STAGING VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Validations: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {total - passed} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("\n✅ STAGING ENVIRONMENT READY FOR TESTING")
            logger.info("\nYou can now:")
            logger.info("1. Test behavioral intelligence features")
            logger.info("2. Access admin dashboard with business intelligence")
            logger.info("3. Validate metrics and analytics")
            logger.info("4. Proceed with additional dev features testing")
            return True
        else:
            logger.error("\n❌ STAGING NOT READY - ADDRESS ISSUES FIRST")
            return False

def main():
    """Run staging validation"""
    validator = StagingValidator()
    return validator.run_validation()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)