#!/usr/bin/env python3
"""
Comprehensive test suite for Render API integration
WORKER_2_NEW Implementation - PREP-003A

Tests all components: client, deployment manager, and monitoring
"""

import unittest
import asyncio
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

# Import modules for testing (adjust imports for standalone execution)
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from render_client import (
    RenderAPIClient, RenderService, Deployment, DeploymentStatus, 
    ServiceType, RenderAPIError, create_render_client
)

# Import with adjusted paths to avoid relative import issues  
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules dynamically
current_dir = os.path.dirname(__file__)
deployment_module = load_module("deployment_manager", os.path.join(current_dir, "deployment_manager.py"))
monitoring_module = load_module("monitoring", os.path.join(current_dir, "monitoring.py"))

# Extract classes from dynamically loaded modules
RenderDeploymentManager = deployment_module.RenderDeploymentManager
DeploymentConfig = deployment_module.DeploymentConfig
DeploymentResult = deployment_module.DeploymentResult
DeploymentStage = deployment_module.DeploymentStage
ValidationResult = deployment_module.ValidationResult

RenderMonitor = monitoring_module.RenderMonitor
HealthStatus = monitoring_module.HealthStatus
HealthCheck = monitoring_module.HealthCheck
Alert = monitoring_module.Alert
AlertSeverity = monitoring_module.AlertSeverity

class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases"""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
    
    def run_async(self, coro):
        """Helper to run async functions in tests"""
        return self.loop.run_until_complete(coro)

class TestRenderAPIClient(AsyncTestCase):
    """Test cases for RenderAPIClient"""
    
    def setUp(self):
        super().setUp()
        self.client = RenderAPIClient("test_api_key_12345")
    
    @patch('aiohttp.ClientSession')
    def test_initialization(self, mock_session_class):
        """Test RenderAPIClient initialization"""
        client = RenderAPIClient("test_key", timeout=60)
        
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.timeout.total, 60)
        
        expected_headers = {
            'Authorization': 'Bearer test_key',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.assertEqual(client.headers, expected_headers)
    
    async def _mock_successful_response(self, data: Dict[str, Any]):
        """Helper to create mock successful HTTP response"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.headers = {}
        mock_response.json.return_value = data
        return mock_response
    
    @patch('aiohttp.ClientSession')
    def test_make_request_success(self, mock_session_class):
        """Test successful API request"""
        async def test():
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            mock_response = await self._mock_successful_response({
                "id": "service123", 
                "name": "test-service"
            })
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            result = await self.client._make_request('GET', '/services/123')
            
            self.assertEqual(result, {"id": "service123", "name": "test-service"})
            
            mock_session.request.assert_called_once_with(
                method='GET',
                url=f"{self.client.BASE_URL}/services/123",
                json=None,
                params=None
            )
        
        self.run_async(test())
    
    @patch('aiohttp.ClientSession')
    def test_make_request_rate_limit_handling(self, mock_session_class):
        """Test rate limit handling with retry"""
        async def test():
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            # First response: rate limited
            mock_response_429 = AsyncMock()
            mock_response_429.status = 429
            mock_response_429.headers = {'Retry-After': '1'}
            
            # Second response: success
            mock_response_success = await self._mock_successful_response({"success": True})
            
            mock_session.request.return_value.__aenter__.side_effect = [
                mock_response_429, mock_response_success
            ]
            
            with patch('asyncio.sleep') as mock_sleep:
                result = await self.client._make_request('GET', '/test')
                
                self.assertEqual(result, {"success": True})
                mock_sleep.assert_called_with(1)
        
        self.run_async(test())
    
    @patch('aiohttp.ClientSession')
    def test_make_request_http_error(self, mock_session_class):
        """Test HTTP error handling"""
        async def test():
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.text.return_value = "Not Found"
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            with self.assertRaises(RenderAPIError) as context:
                await self.client._make_request('GET', '/nonexistent')
            
            self.assertEqual(context.exception.status_code, 404)
        
        self.run_async(test())
    
    def test_get_services(self):
        """Test get_services method"""
        async def test():
            with patch.object(self.client, '_make_request') as mock_request:
                mock_request.return_value = {
                    "services": [
                        {
                            "id": "srv1",
                            "name": "service1", 
                            "type": "web_service",
                            "repo": "https://github.com/user/repo1",
                            "branch": "main",
                            "serviceDetails": {"status": "live"},
                            "createdAt": "2025-08-20T00:00:00Z",
                            "updatedAt": "2025-08-20T12:00:00Z"
                        }
                    ]
                }
                
                services = await self.client.get_services(service_type="web_service", limit=10)
                
                mock_request.assert_called_once_with('GET', '/services', params={
                    'limit': 10,
                    'type': 'web_service'
                })
                
                self.assertEqual(len(services), 1)
                self.assertIsInstance(services[0], RenderService)
                self.assertEqual(services[0].name, "service1")
        
        self.run_async(test())
    
    def test_create_service(self):
        """Test create_service method"""
        async def test():
            with patch.object(self.client, '_make_request') as mock_request, \
                 patch.object(self.client, 'get_service') as mock_get_service:
                
                mock_request.return_value = {"id": "new_service_123"}
                mock_get_service.return_value = RenderService(
                    id="new_service_123",
                    name="test-service",
                    type="web_service",
                    repo="https://github.com/user/repo",
                    branch="main",
                    status="created",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                service = await self.client.create_service(
                    name="test-service",
                    repo="https://github.com/user/repo",
                    service_type=ServiceType.WEB_SERVICE,
                    env_vars={"NODE_ENV": "production"}
                )
                
                self.assertEqual(service.id, "new_service_123")
                self.assertEqual(service.name, "test-service")
                
                # Verify create request payload
                mock_request.assert_called_once()
                args, kwargs = mock_request.call_args
                payload = kwargs['data']
                self.assertEqual(payload['name'], "test-service")
                self.assertEqual(payload['type'], 'web_service')
                self.assertIn('envVars', payload)
        
        self.run_async(test())
    
    def test_validate_connection(self):
        """Test API connection validation"""
        async def test():
            # Test successful validation
            with patch.object(self.client, 'get_services') as mock_get_services:
                mock_get_services.return_value = []
                
                result = await self.client.validate_connection()
                self.assertTrue(result)
                
                # Test failed validation
                mock_get_services.side_effect = RenderAPIError("Auth failed")
                result = await self.client.validate_connection()
                self.assertFalse(result)
        
        self.run_async(test())
    
    @patch.dict('os.environ', {'RENDER_API_KEY': 'env_test_key'})
    def test_create_render_client(self):
        """Test create_render_client helper function"""
        client = create_render_client()
        self.assertIsInstance(client, RenderAPIClient)
        self.assertEqual(client.api_key, 'env_test_key')
    
    def test_create_render_client_missing_key(self):
        """Test create_render_client with missing API key"""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                create_render_client()
            
            self.assertIn("RENDER_API_KEY", str(context.exception))

class TestRenderDeploymentManager(AsyncTestCase):
    """Test cases for RenderDeploymentManager"""
    
    def setUp(self):
        super().setUp()
        self.mock_client = AsyncMock(spec=RenderAPIClient)
        self.manager = RenderDeploymentManager(self.mock_client, max_concurrent_deployments=2)
    
    def test_initialization(self):
        """Test RenderDeploymentManager initialization"""
        self.assertEqual(self.manager.client, self.mock_client)
        self.assertEqual(self.manager.max_concurrent_deployments, 2)
        self.assertEqual(len(self.manager._active_deployments), 0)
        self.assertEqual(len(self.manager._deployment_history), 0)
    
    def test_validation_methods(self):
        """Test pre-deployment validation methods"""
        async def test():
            # Test service health validation
            mock_service = RenderService(
                id="srv123",
                name="test-service",
                type="web_service",
                repo="https://github.com/user/repo",
                branch="main",
                status="live",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.mock_client.get_service.return_value = mock_service
            
            result = await self.manager._validate_service_health("srv123")
            self.assertEqual(result, ValidationResult.PASSED)
            
            # Test unhealthy service
            mock_service.status = "build_failed"
            result = await self.manager._validate_service_health("srv123")
            self.assertEqual(result, ValidationResult.FAILED)
        
        self.run_async(test())
    
    def test_deploy_service_success(self):
        """Test successful service deployment"""
        async def test():
            # Mock successful deployment flow
            self.mock_client.get_service.return_value = RenderService(
                id="srv123",
                name="test-service",
                type="web_service", 
                repo="https://github.com/user/repo",
                branch="main",
                status="live",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.mock_client.set_env_vars.return_value = True
            self.mock_client.get_deployments.return_value = []
            self.mock_client.get_env_vars.return_value = {}
            
            # Mock deployment trigger and monitoring
            with patch.object(self.manager, '_trigger_deployment') as mock_trigger, \
                 patch.object(self.manager, '_monitor_deployment') as mock_monitor:
                
                mock_trigger.return_value = "deploy123"
                mock_monitor.return_value = True
                
                config = DeploymentConfig(
                    service_id="srv123",
                    env_vars={"NODE_ENV": "production"}
                )
                
                result = await self.manager.deploy_service(config)
                
                self.assertTrue(result.success)
                self.assertEqual(result.stage, DeploymentStage.COMPLETED)
                self.assertEqual(result.deployment_id, "deploy123")
                
                # Verify env vars were set
                self.mock_client.set_env_vars.assert_called_once_with(
                    "srv123", {"NODE_ENV": "production"}
                )
        
        self.run_async(test())
    
    def test_deploy_service_validation_failure(self):
        """Test deployment failure due to validation"""
        async def test():
            # Mock unhealthy service
            self.mock_client.get_service.return_value = RenderService(
                id="srv123",
                name="test-service",
                type="web_service",
                repo="https://github.com/user/repo", 
                branch="main",
                status="build_failed",  # Unhealthy status
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.mock_client.get_deployments.return_value = []
            self.mock_client.get_env_vars.return_value = {}
            
            config = DeploymentConfig(service_id="srv123")
            result = await self.manager.deploy_service(config)
            
            self.assertFalse(result.success)
            self.assertEqual(result.stage, DeploymentStage.FAILED)
            self.assertIn("validation failed", result.error_message.lower())
        
        self.run_async(test())
    
    def test_batch_deploy(self):
        """Test batch deployment functionality"""
        async def test():
            # Create multiple deployment configs
            configs = [
                DeploymentConfig(service_id="srv1"),
                DeploymentConfig(service_id="srv2"),
                DeploymentConfig(service_id="srv3")
            ]
            
            # Mock successful deployments
            with patch.object(self.manager, 'deploy_service') as mock_deploy:
                mock_results = [
                    DeploymentResult(
                        deployment_id=f"deploy{i}",
                        service_id=f"srv{i}",
                        stage=DeploymentStage.COMPLETED,
                        success=True,
                        start_time=datetime.now(),
                        end_time=datetime.now()
                    )
                    for i in range(1, 4)
                ]
                
                mock_deploy.side_effect = mock_results
                
                results = await self.manager.batch_deploy(configs)
                
                self.assertEqual(len(results), 3)
                self.assertEqual(mock_deploy.call_count, 3)
                
                # All should be successful
                successful = [r for r in results if r.success]
                self.assertEqual(len(successful), 3)
        
        self.run_async(test())
    
    def test_deployment_stats(self):
        """Test deployment statistics calculation"""
        # Add mock deployment history
        now = datetime.now()
        
        self.manager._deployment_history = [
            DeploymentResult(
                deployment_id="deploy1",
                service_id="srv1",
                stage=DeploymentStage.COMPLETED,
                success=True,
                start_time=now - timedelta(hours=1),
                end_time=now - timedelta(hours=1) + timedelta(minutes=5)
            ),
            DeploymentResult(
                deployment_id="deploy2", 
                service_id="srv2",
                stage=DeploymentStage.FAILED,
                success=False,
                start_time=now - timedelta(hours=2),
                end_time=now - timedelta(hours=2) + timedelta(minutes=3),
                rollback_deployment_id="rollback1"
            )
        ]
        
        stats = self.manager.get_deployment_stats(hours=24)
        
        self.assertEqual(stats['total_deployments'], 2)
        self.assertEqual(stats['successful_deployments'], 1) 
        self.assertEqual(stats['failed_deployments'], 1)
        self.assertEqual(stats['rollbacks'], 1)
        self.assertEqual(stats['success_rate_percent'], 50.0)
    
    def test_concurrent_deployment_limit(self):
        """Test concurrent deployment limit enforcement"""
        async def test():
            # Fill up active deployments to max capacity
            self.manager._active_deployments = {
                "deploy1": Mock(),
                "deploy2": Mock()
            }
            
            config = DeploymentConfig(service_id="srv3")
            
            with self.assertRaises(RenderAPIError) as context:
                await self.manager.deploy_service(config)
            
            self.assertIn("Maximum concurrent deployments", str(context.exception))
        
        self.run_async(test())

class TestRenderMonitor(AsyncTestCase):
    """Test cases for RenderMonitor"""
    
    def setUp(self):
        super().setUp()
        self.mock_client = AsyncMock(spec=RenderAPIClient)
        self.monitor = RenderMonitor(self.mock_client, check_interval_seconds=1)
    
    def test_initialization(self):
        """Test RenderMonitor initialization"""
        self.assertEqual(self.monitor.client, self.mock_client)
        self.assertEqual(self.monitor.check_interval, 1)
        self.assertFalse(self.monitor._monitoring_active)
        self.assertEqual(len(self.monitor._monitored_services), 0)
    
    def test_service_management(self):
        """Test adding and removing services from monitoring"""
        self.monitor.add_service("srv123")
        self.assertIn("srv123", self.monitor._monitored_services)
        self.assertIn("srv123", self.monitor._health_history)
        
        self.monitor.remove_service("srv123")
        self.assertNotIn("srv123", self.monitor._monitored_services)
    
    def test_health_status_calculation(self):
        """Test health status calculation logic"""
        # Test healthy service
        service = RenderService(
            id="srv123",
            name="test-service",
            type="web_service",
            repo="https://github.com/user/repo",
            branch="main", 
            status="live",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        status = self.monitor._calculate_health_status(service)
        self.assertEqual(status, HealthStatus.HEALTHY)
        
        # Test critical service
        service.status = "build_failed"
        status = self.monitor._calculate_health_status(service)
        self.assertEqual(status, HealthStatus.CRITICAL)
        
        # Test warning service
        service.status = "build_in_progress"
        status = self.monitor._calculate_health_status(service)
        self.assertEqual(status, HealthStatus.WARNING)
    
    def test_service_health_check(self):
        """Test individual service health check"""
        async def test():
            self.mock_client.get_service.return_value = RenderService(
                id="srv123",
                name="test-service",
                type="web_service",
                repo="https://github.com/user/repo",
                branch="main",
                status="live",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.mock_client.get_deployments.return_value = [
                Mock(status="live"),
                Mock(status="live")
            ]
            
            self.mock_client.get_logs.return_value = [
                {"message": "Info: Application started"},
                {"message": "Error: Database connection failed"}
            ]
            
            health_check = await self.monitor._check_service_health("srv123")
            
            self.assertIsNotNone(health_check)
            self.assertEqual(health_check.service_id, "srv123")
            self.assertEqual(health_check.status, HealthStatus.HEALTHY)
            self.assertGreater(health_check.uptime_percentage, 0)
            self.assertGreaterEqual(health_check.error_count, 1)  # Should find "Error" in logs
        
        self.run_async(test())
    
    def test_alert_system(self):
        """Test alert triggering and resolution"""
        async def test():
            # Test alert triggering
            await self.monitor._trigger_alert(
                "srv123",
                AlertSeverity.CRITICAL,
                "Service is down"
            )
            
            active_alerts = self.monitor.get_active_alerts()
            self.assertEqual(len(active_alerts), 1)
            self.assertEqual(active_alerts[0].severity, AlertSeverity.CRITICAL)
            
            # Test alert resolution
            await self.monitor._resolve_alerts("srv123")
            
            resolved_alerts = [a for a in self.monitor._active_alerts.values() if a.resolved]
            self.assertEqual(len(resolved_alerts), 1)
            
            active_alerts = self.monitor.get_active_alerts()
            self.assertEqual(len(active_alerts), 0)
        
        self.run_async(test())
    
    def test_monitoring_summary(self):
        """Test monitoring summary generation"""
        # Add services and health data
        self.monitor.add_service("srv1")
        self.monitor.add_service("srv2")
        
        self.monitor._current_health = {
            "srv1": HealthCheck(
                service_id="srv1",
                service_name="service1",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                uptime_percentage=99.5,
                error_count=2
            ),
            "srv2": HealthCheck(
                service_id="srv2", 
                service_name="service2",
                status=HealthStatus.WARNING,
                timestamp=datetime.now(),
                uptime_percentage=95.0,
                error_count=15
            )
        }
        
        summary = self.monitor.get_monitoring_summary()
        
        self.assertEqual(summary['total_monitored_services'], 2)
        self.assertEqual(summary['health_distribution']['healthy'], 1)
        self.assertEqual(summary['health_distribution']['warning'], 1) 
        self.assertEqual(summary['average_uptime_percentage'], 97.25)
    
    def test_health_report_generation(self):
        """Test comprehensive health report generation"""
        async def test():
            # Setup test data
            self.monitor.add_service("srv123")
            
            health_check = HealthCheck(
                service_id="srv123",
                service_name="test-service",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                uptime_percentage=99.8,
                error_count=5,
                issues=["Minor performance degradation"],
                recommendations=["Consider scaling up"]
            )
            
            self.monitor._current_health["srv123"] = health_check
            
            # Add an active alert
            await self.monitor._trigger_alert("srv123", AlertSeverity.WARNING, "High error rate")
            
            report = await self.monitor.generate_health_report()
            
            self.assertIn('report_timestamp', report)
            self.assertIn('summary', report)
            self.assertIn('services', report)
            self.assertIn('active_alerts', report)
            
            self.assertEqual(len(report['services']), 1)
            self.assertEqual(report['services'][0]['service_id'], 'srv123')
            self.assertEqual(len(report['active_alerts']), 1)
        
        self.run_async(test())

class TestIntegration(AsyncTestCase):
    """Integration tests for complete Render API integration"""
    
    def setUp(self):
        super().setUp()
        self.client = RenderAPIClient("integration_test_key")
        self.deployment_manager = RenderDeploymentManager(self.client)
        self.monitor = RenderMonitor(self.client, check_interval_seconds=1)
    
    def test_full_workflow_integration(self):
        """Test complete workflow: client -> deployment -> monitoring"""
        async def test():
            # Mock all API responses
            with patch.object(self.client, '_make_request') as mock_request:
                # Setup mock responses for different endpoints
                def mock_response(*args, **kwargs):
                    method, endpoint = args[0], args[1]
                    
                    if endpoint == '/services' and method == 'GET':
                        return {
                            'services': [{
                                'id': 'srv123',
                                'name': 'integration-test',
                                'type': 'web_service',
                                'repo': 'https://github.com/user/repo',
                                'branch': 'main',
                                'serviceDetails': {'status': 'live'},
                                'createdAt': '2025-08-20T00:00:00Z',
                                'updatedAt': '2025-08-20T12:00:00Z'
                            }]
                        }
                    elif 'deploys' in endpoint and method == 'POST':
                        return {'id': 'deploy123'}
                    elif 'deploys/deploy123' in endpoint:
                        return {'status': 'live'}
                    elif 'logs' in endpoint:
                        return {'logs': [{'message': 'Application started'}]}
                    else:
                        return {}
                
                mock_request.side_effect = mock_response
                
                # Test 1: Get services via client
                services = await self.client.get_services()
                self.assertEqual(len(services), 1)
                self.assertEqual(services[0].name, 'integration-test')
                
                # Test 2: Deploy service via deployment manager
                config = DeploymentConfig(service_id='srv123')
                
                with patch.object(self.deployment_manager, '_monitor_deployment', return_value=True):
                    result = await self.deployment_manager.deploy_service(config)
                    
                    self.assertTrue(result.success)
                    self.assertEqual(result.deployment_id, 'deploy123')
                
                # Test 3: Monitor service health
                self.monitor.add_service('srv123')
                health_check = await self.monitor._check_service_health('srv123')
                
                self.assertIsNotNone(health_check)
                self.assertEqual(health_check.service_id, 'srv123')
                self.assertEqual(health_check.status, HealthStatus.HEALTHY)
        
        self.run_async(test())

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    test_classes = [
        TestRenderAPIClient,
        TestRenderDeploymentManager,
        TestRenderMonitor,
        TestIntegration
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"RENDER API INTEGRATION TEST RESULTS")
    print(f"WORKER_2_NEW Implementation - PREP-003A")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.splitlines()[-1] if traceback.splitlines() else 'Unknown failure'}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.splitlines()[-1] if traceback.splitlines() else 'Unknown error'}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)