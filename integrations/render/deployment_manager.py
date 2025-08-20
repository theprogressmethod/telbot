"""
Render Deployment Manager - Service deployment automation with safety checks
WORKER_2_NEW Implementation - PREP-003A

Handles deployment workflows, rollbacks, and safety validations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

try:
    from .render_client import RenderAPIClient, RenderService, Deployment, RenderAPIError
except ImportError:
    from render_client import RenderAPIClient, RenderService, Deployment, RenderAPIError

class DeploymentStage(Enum):
    """Deployment pipeline stages"""
    VALIDATING = "validating"
    DEPLOYING = "deploying" 
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class ValidationResult(Enum):
    """Pre-deployment validation results"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    service_id: str
    commit_sha: Optional[str] = None
    clear_cache: bool = False
    env_vars: Optional[Dict[str, str]] = None
    validation_checks: bool = True
    auto_rollback: bool = True
    monitor_duration_minutes: int = 10

@dataclass
class DeploymentResult:
    """Deployment execution result"""
    deployment_id: str
    service_id: str
    stage: DeploymentStage
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    validation_results: Dict[str, ValidationResult] = field(default_factory=dict)
    rollback_deployment_id: Optional[str] = None
    logs: List[str] = field(default_factory=list)

class RenderDeploymentManager:
    """
    Advanced deployment manager with safety checks, validation, and rollback capabilities
    Integrates with Progress Method accountability system patterns
    """
    
    def __init__(self, client: RenderAPIClient, max_concurrent_deployments: int = 3):
        """
        Initialize deployment manager
        
        Args:
            client: Configured RenderAPIClient
            max_concurrent_deployments: Maximum concurrent deployments
        """
        self.client = client
        self.max_concurrent_deployments = max_concurrent_deployments
        self.logger = logging.getLogger(__name__)
        
        # Track active deployments
        self._active_deployments: Dict[str, DeploymentResult] = {}
        self._deployment_history: List[DeploymentResult] = []
        
        # Monitoring tasks
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    # Pre-deployment validation
    
    async def _validate_service_health(self, service_id: str) -> ValidationResult:
        """Check if service is in healthy state for deployment"""
        try:
            service = await self.client.get_service(service_id)
            
            if service.status in ['live', 'created']:
                return ValidationResult.PASSED
            elif service.status in ['build_in_progress', 'deploy_in_progress']:
                return ValidationResult.WARNING
            else:
                return ValidationResult.FAILED
                
        except Exception as e:
            self.logger.error(f"Health validation failed for {service_id}: {e}")
            return ValidationResult.FAILED
    
    async def _validate_recent_deployments(self, service_id: str) -> ValidationResult:
        """Check for recent deployment failures"""
        try:
            deployments = await self.client.get_deployments(service_id, limit=5)
            
            # Check if recent deployments had failures
            failed_count = 0
            for deploy in deployments[:3]:  # Check last 3 deployments
                if deploy.status in ['build_failed', 'deploy_failed']:
                    failed_count += 1
            
            if failed_count == 0:
                return ValidationResult.PASSED
            elif failed_count <= 1:
                return ValidationResult.WARNING
            else:
                return ValidationResult.FAILED
                
        except Exception as e:
            self.logger.error(f"Recent deployments validation failed for {service_id}: {e}")
            return ValidationResult.FAILED
    
    async def _validate_environment(self, service_id: str) -> ValidationResult:
        """Validate service environment and configuration"""
        try:
            service = await self.client.get_service(service_id)
            env_vars = await self.client.get_env_vars(service_id)
            
            # Basic validations
            if not service.repo:
                return ValidationResult.FAILED
            
            # Check for required environment variables based on service type
            if service.type == 'web_service':
                if 'PORT' not in env_vars and 'DATABASE_URL' not in env_vars:
                    return ValidationResult.WARNING
            
            return ValidationResult.PASSED
            
        except Exception as e:
            self.logger.error(f"Environment validation failed for {service_id}: {e}")
            return ValidationResult.FAILED
    
    async def _run_pre_deployment_validations(self, config: DeploymentConfig) -> Dict[str, ValidationResult]:
        """
        Run all pre-deployment validation checks
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dictionary of validation results
        """
        if not config.validation_checks:
            return {}
        
        self.logger.info(f"Running pre-deployment validations for {config.service_id}")
        
        # Run validations concurrently
        validations = await asyncio.gather(
            self._validate_service_health(config.service_id),
            self._validate_recent_deployments(config.service_id),
            self._validate_environment(config.service_id),
            return_exceptions=True
        )
        
        results = {
            'service_health': validations[0] if not isinstance(validations[0], Exception) else ValidationResult.FAILED,
            'recent_deployments': validations[1] if not isinstance(validations[1], Exception) else ValidationResult.FAILED,
            'environment': validations[2] if not isinstance(validations[2], Exception) else ValidationResult.FAILED
        }
        
        return results
    
    # Deployment execution
    
    async def deploy_service(self, config: DeploymentConfig) -> DeploymentResult:
        """
        Deploy service with comprehensive safety checks and monitoring
        
        Args:
            config: Deployment configuration
            
        Returns:
            DeploymentResult with execution details
        """
        # Check concurrent deployment limit
        if len(self._active_deployments) >= self.max_concurrent_deployments:
            raise RenderAPIError("Maximum concurrent deployments reached")
        
        result = DeploymentResult(
            deployment_id="",  # Will be set after deployment starts
            service_id=config.service_id,
            stage=DeploymentStage.VALIDATING,
            success=False,
            start_time=datetime.now()
        )
        
        try:
            self.logger.info(f"Starting deployment for service {config.service_id}")
            
            # Stage 1: Pre-deployment validation
            if config.validation_checks:
                result.validation_results = await self._run_pre_deployment_validations(config)
                
                # Check for validation failures
                failures = [k for k, v in result.validation_results.items() if v == ValidationResult.FAILED]
                if failures:
                    result.error_message = f"Pre-deployment validation failed: {', '.join(failures)}"
                    result.stage = DeploymentStage.FAILED
                    result.end_time = datetime.now()
                    return result
            
            # Stage 2: Update environment variables if provided
            if config.env_vars:
                await self.client.set_env_vars(config.service_id, config.env_vars)
                result.logs.append(f"Updated {len(config.env_vars)} environment variables")
            
            # Stage 3: Trigger deployment
            result.stage = DeploymentStage.DEPLOYING
            deployment_id = await self._trigger_deployment(config)
            result.deployment_id = deployment_id
            
            # Track active deployment
            self._active_deployments[deployment_id] = result
            
            # Stage 4: Monitor deployment
            result.stage = DeploymentStage.MONITORING
            success = await self._monitor_deployment(config, result)
            
            if success:
                result.stage = DeploymentStage.COMPLETED
                result.success = True
                self.logger.info(f"Deployment {deployment_id} completed successfully")
                
                # Start post-deployment monitoring if configured
                if config.monitor_duration_minutes > 0:
                    await self._start_post_deployment_monitoring(config, result)
            else:
                result.stage = DeploymentStage.FAILED
                
                # Auto-rollback if enabled and deployment failed
                if config.auto_rollback:
                    await self._perform_rollback(config, result)
            
            result.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Deployment failed for service {config.service_id}: {e}")
            result.error_message = str(e)
            result.stage = DeploymentStage.FAILED
            result.end_time = datetime.now()
            
            # Auto-rollback on exception if enabled
            if config.auto_rollback:
                try:
                    await self._perform_rollback(config, result)
                except Exception as rollback_error:
                    self.logger.error(f"Rollback also failed: {rollback_error}")
        
        finally:
            # Clean up active deployment tracking
            if result.deployment_id in self._active_deployments:
                del self._active_deployments[result.deployment_id]
            
            # Store in history
            self._deployment_history.append(result)
            
            # Keep only last 50 deployments in memory
            if len(self._deployment_history) > 50:
                self._deployment_history.pop(0)
        
        return result
    
    async def _trigger_deployment(self, config: DeploymentConfig) -> str:
        """
        Trigger the actual deployment via Render API
        
        Args:
            config: Deployment configuration
            
        Returns:
            Deployment ID
        """
        payload = {}
        
        if config.commit_sha:
            payload['commitSha'] = config.commit_sha
        
        if config.clear_cache:
            payload['clearCache'] = True
        
        self.logger.info(f"Triggering deployment for service {config.service_id}")
        
        response = await self.client._make_request(
            'POST', 
            f'/services/{config.service_id}/deploys',
            data=payload
        )
        
        return response['id']
    
    async def _monitor_deployment(self, config: DeploymentConfig, result: DeploymentResult) -> bool:
        """
        Monitor deployment progress until completion or failure
        
        Args:
            config: Deployment configuration
            result: Deployment result to update
            
        Returns:
            True if deployment succeeded
        """
        max_wait_time = 600  # 10 minutes max
        check_interval = 15  # Check every 15 seconds
        elapsed_time = 0
        
        self.logger.info(f"Monitoring deployment {result.deployment_id}")
        
        while elapsed_time < max_wait_time:
            try:
                deployment_status = await self.client._make_request(
                    'GET',
                    f'/services/{config.service_id}/deploys/{result.deployment_id}'
                )
                
                status = deployment_status.get('status')
                result.logs.append(f"[{datetime.now()}] Deployment status: {status}")
                
                if status == 'live':
                    return True
                elif status in ['build_failed', 'deploy_failed']:
                    result.error_message = f"Deployment failed with status: {status}"
                    return False
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
                
            except Exception as e:
                self.logger.error(f"Error monitoring deployment: {e}")
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
        
        result.error_message = f"Deployment monitoring timed out after {max_wait_time} seconds"
        return False
    
    async def _perform_rollback(self, config: DeploymentConfig, result: DeploymentResult):
        """
        Perform rollback to previous successful deployment
        
        Args:
            config: Deployment configuration
            result: Current deployment result
        """
        try:
            self.logger.warning(f"Performing rollback for service {config.service_id}")
            
            # Get recent successful deployments
            deployments = await self.client.get_deployments(config.service_id, limit=10)
            
            # Find last successful deployment (excluding current failed one)
            rollback_target = None
            for deploy in deployments:
                if (deploy.status == 'live' and 
                    deploy.id != result.deployment_id):
                    rollback_target = deploy
                    break
            
            if not rollback_target:
                result.logs.append("No suitable rollback target found")
                return
            
            # Create rollback deployment
            rollback_config = DeploymentConfig(
                service_id=config.service_id,
                commit_sha=rollback_target.commit_sha,
                clear_cache=True,
                validation_checks=False,  # Skip validations for rollback
                auto_rollback=False  # Prevent infinite rollback loops
            )
            
            rollback_id = await self._trigger_deployment(rollback_config)
            result.rollback_deployment_id = rollback_id
            result.stage = DeploymentStage.ROLLED_BACK
            
            result.logs.append(f"Rollback deployment initiated: {rollback_id}")
            self.logger.info(f"Rollback completed: {rollback_id}")
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            result.logs.append(f"Rollback failed: {e}")
    
    async def _start_post_deployment_monitoring(self, config: DeploymentConfig, result: DeploymentResult):
        """
        Start background monitoring of deployment health
        
        Args:
            config: Deployment configuration
            result: Deployment result
        """
        async def monitor():
            """Background monitoring task"""
            monitor_duration = config.monitor_duration_minutes * 60
            check_interval = 30
            elapsed = 0
            
            while elapsed < monitor_duration:
                try:
                    service = await self.client.get_service(config.service_id)
                    
                    if service.status != 'live':
                        self.logger.warning(f"Service {config.service_id} unhealthy during monitoring: {service.status}")
                        
                        # Trigger rollback if service becomes unhealthy
                        if config.auto_rollback:
                            await self._perform_rollback(config, result)
                        break
                    
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
                    
                except Exception as e:
                    self.logger.error(f"Error during post-deployment monitoring: {e}")
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval
            
            # Clean up monitoring task
            if result.deployment_id in self._monitoring_tasks:
                del self._monitoring_tasks[result.deployment_id]
        
        # Start monitoring task
        if result.deployment_id not in self._monitoring_tasks:
            task = asyncio.create_task(monitor())
            self._monitoring_tasks[result.deployment_id] = task
    
    # Batch operations
    
    async def batch_deploy(self, configs: List[DeploymentConfig]) -> List[DeploymentResult]:
        """
        Deploy multiple services with controlled concurrency
        
        Args:
            configs: List of deployment configurations
            
        Returns:
            List of deployment results
        """
        self.logger.info(f"Starting batch deployment of {len(configs)} services")
        
        # Deploy with concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent_deployments)
        
        async def deploy_with_semaphore(config):
            async with semaphore:
                return await self.deploy_service(config)
        
        results = await asyncio.gather(
            *[deploy_with_semaphore(config) for config in configs],
            return_exceptions=True
        )
        
        # Handle exceptions in results
        deployment_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed result for exception
                failed_result = DeploymentResult(
                    deployment_id="",
                    service_id=configs[i].service_id,
                    stage=DeploymentStage.FAILED,
                    success=False,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(result)
                )
                deployment_results.append(failed_result)
            else:
                deployment_results.append(result)
        
        successful = len([r for r in deployment_results if r.success])
        self.logger.info(f"Batch deployment completed: {successful}/{len(deployment_results)} successful")
        
        return deployment_results
    
    # Status and monitoring
    
    def get_active_deployments(self) -> Dict[str, DeploymentResult]:
        """Get currently active deployments"""
        return self._active_deployments.copy()
    
    def get_deployment_history(self, service_id: Optional[str] = None, limit: int = 20) -> List[DeploymentResult]:
        """
        Get deployment history
        
        Args:
            service_id: Filter by service ID
            limit: Maximum number of results
            
        Returns:
            List of deployment results
        """
        history = self._deployment_history
        
        if service_id:
            history = [r for r in history if r.service_id == service_id]
        
        # Sort by start time, most recent first
        history.sort(key=lambda x: x.start_time, reverse=True)
        
        return history[:limit]
    
    def get_deployment_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get deployment statistics for specified time period
        
        Args:
            hours: Time period in hours
            
        Returns:
            Deployment statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_deployments = [
            r for r in self._deployment_history
            if r.start_time >= cutoff_time
        ]
        
        total = len(recent_deployments)
        successful = len([r for r in recent_deployments if r.success])
        failed = total - successful
        rollbacks = len([r for r in recent_deployments if r.rollback_deployment_id])
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            'period_hours': hours,
            'total_deployments': total,
            'successful_deployments': successful,
            'failed_deployments': failed,
            'rollbacks': rollbacks,
            'success_rate_percent': round(success_rate, 2)
        }
    
    async def cleanup(self):
        """Clean up manager resources"""
        # Cancel all monitoring tasks
        for task in self._monitoring_tasks.values():
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks.values(), return_exceptions=True)
        
        self._monitoring_tasks.clear()
        self._active_deployments.clear()
        
        self.logger.info("RenderDeploymentManager cleanup completed")