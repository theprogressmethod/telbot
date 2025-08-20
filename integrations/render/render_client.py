"""
Render API Client - Core API wrapper for Render.com integration
WORKER_2_NEW Implementation - PREP-003A

Following patterns from main FastAPI application for async HTTP handling
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import os

class DeploymentStatus(Enum):
    """Render deployment status enumeration"""
    CREATED = "created"
    BUILD_IN_PROGRESS = "build_in_progress" 
    LIVE = "live"
    BUILD_FAILED = "build_failed"
    DEPLOY_FAILED = "deploy_failed"
    DEACTIVATED = "deactivated"

class ServiceType(Enum):
    """Render service types"""
    WEB_SERVICE = "web_service"
    BACKGROUND_WORKER = "background_worker"
    STATIC_SITE = "static_site"
    PRIVATE_SERVICE = "private_service"
    CRON_JOB = "cron_job"

@dataclass
class RenderService:
    """Render service data model"""
    id: str
    name: str
    type: str
    repo: str
    branch: str
    status: str
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None
    dashboard_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass 
class Deployment:
    """Render deployment data model"""
    id: str
    service_id: str
    status: str
    commit_sha: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime] = None

class RenderAPIError(Exception):
    """Custom exception for Render API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class RenderAPIClient:
    """
    Async Render API client with authentication and error handling
    Follows async patterns from main FastAPI application
    """
    
    BASE_URL = "https://api.render.com/v1"
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Render API client
        
        Args:
            api_key: Render API key from environment
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.logger = logging.getLogger(__name__)
        
        # Headers for all requests
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: Optional[Dict] = None,
                           params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated async request to Render API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            RenderAPIError: On API errors or network issues
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            ) as session:
                
                self.logger.debug(f"Making {method} request to {url}")
                
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    
                    # Log rate limiting info
                    if 'X-RateLimit-Remaining' in response.headers:
                        remaining = response.headers.get('X-RateLimit-Remaining')
                        reset_time = response.headers.get('X-RateLimit-Reset')
                        self.logger.debug(f"Rate limit - Remaining: {remaining}, Reset: {reset_time}")
                    
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 60))
                        self.logger.warning(f"Rate limited. Waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        # Retry once after rate limit
                        return await self._make_request(method, endpoint, data, params)
                    
                    # Raise for HTTP errors
                    if response.status >= 400:
                        error_text = await response.text()
                        raise RenderAPIError(
                            f"API request failed: {response.status} {error_text}",
                            status_code=response.status
                        )
                    
                    # Return JSON response
                    if response.content_type == 'application/json':
                        return await response.json()
                    else:
                        return {}
                        
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {e}")
            raise RenderAPIError(f"Network error: {e}")
        except asyncio.TimeoutError:
            self.logger.error("Request timed out")
            raise RenderAPIError("Request timed out")
    
    # Service Management Methods
    
    async def get_services(self, service_type: Optional[str] = None, 
                          limit: int = 20) -> List[RenderService]:
        """
        Get all services for the account
        
        Args:
            service_type: Filter by service type
            limit: Maximum number of services to return
            
        Returns:
            List of RenderService objects
        """
        params = {'limit': min(limit, 100)}
        if service_type:
            params['type'] = service_type
        
        self.logger.info(f"Fetching services (limit: {limit}, type: {service_type})")
        
        response = await self._make_request('GET', '/services', params=params)
        
        services = []
        for service_data in response.get('services', []):
            service = RenderService(
                id=service_data['id'],
                name=service_data['name'],
                type=service_data['type'],
                repo=service_data.get('repo', ''),
                branch=service_data.get('branch', 'main'),
                status=service_data.get('serviceDetails', {}).get('status', 'unknown'),
                created_at=datetime.fromisoformat(service_data['createdAt'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(service_data['updatedAt'].replace('Z', '+00:00')),
                url=service_data.get('serviceDetails', {}).get('url'),
                dashboard_url=service_data.get('serviceDetails', {}).get('dashboardUrl')
            )
            services.append(service)
        
        return services
    
    async def get_service(self, service_id: str) -> RenderService:
        """
        Get detailed service information
        
        Args:
            service_id: Render service ID
            
        Returns:
            RenderService object
        """
        self.logger.info(f"Fetching service details for {service_id}")
        
        response = await self._make_request('GET', f'/services/{service_id}')
        
        return RenderService(
            id=response['id'],
            name=response['name'],
            type=response['type'],
            repo=response.get('repo', ''),
            branch=response.get('branch', 'main'),
            status=response.get('serviceDetails', {}).get('status', 'unknown'),
            created_at=datetime.fromisoformat(response['createdAt'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(response['updatedAt'].replace('Z', '+00:00')),
            url=response.get('serviceDetails', {}).get('url'),
            dashboard_url=response.get('serviceDetails', {}).get('dashboardUrl')
        )
    
    async def create_service(self, name: str, repo: str, service_type: ServiceType,
                           branch: str = 'main', auto_deploy: bool = True,
                           env_vars: Optional[Dict[str, str]] = None) -> RenderService:
        """
        Create a new Render service
        
        Args:
            name: Service name
            repo: Git repository URL
            service_type: Type of service to create
            branch: Git branch to deploy
            auto_deploy: Enable auto-deployment on push
            env_vars: Environment variables
            
        Returns:
            Created RenderService object
        """
        payload = {
            'name': name,
            'repo': repo,
            'type': service_type.value,
            'branch': branch,
            'autoDeploy': auto_deploy
        }
        
        if env_vars:
            payload['envVars'] = [{'key': k, 'value': v} for k, v in env_vars.items()]
        
        self.logger.info(f"Creating service: {name} ({service_type.value})")
        
        response = await self._make_request('POST', '/services', data=payload)
        
        # Return the created service
        return await self.get_service(response['id'])
    
    async def update_service(self, service_id: str, name: Optional[str] = None,
                           branch: Optional[str] = None, 
                           auto_deploy: Optional[bool] = None) -> RenderService:
        """
        Update service configuration
        
        Args:
            service_id: Service ID to update
            name: New service name
            branch: New branch to deploy
            auto_deploy: Enable/disable auto-deployment
            
        Returns:
            Updated RenderService object
        """
        payload = {}
        if name is not None:
            payload['name'] = name
        if branch is not None:
            payload['branch'] = branch
        if auto_deploy is not None:
            payload['autoDeploy'] = auto_deploy
        
        if not payload:
            raise ValueError("At least one field must be provided for update")
        
        self.logger.info(f"Updating service {service_id}")
        
        await self._make_request('PATCH', f'/services/{service_id}', data=payload)
        
        return await self.get_service(service_id)
    
    async def delete_service(self, service_id: str) -> bool:
        """
        Delete a service
        
        Args:
            service_id: Service ID to delete
            
        Returns:
            True if successful
        """
        self.logger.warning(f"Deleting service {service_id}")
        
        await self._make_request('DELETE', f'/services/{service_id}')
        return True
    
    # Environment Variables
    
    async def get_env_vars(self, service_id: str) -> Dict[str, str]:
        """
        Get environment variables for a service
        
        Args:
            service_id: Service ID
            
        Returns:
            Dictionary of environment variables
        """
        response = await self._make_request('GET', f'/services/{service_id}/env-vars')
        
        return {item['key']: item['value'] for item in response.get('envVars', [])}
    
    async def set_env_vars(self, service_id: str, env_vars: Dict[str, str]) -> bool:
        """
        Set environment variables for a service
        
        Args:
            service_id: Service ID
            env_vars: Dictionary of environment variables
            
        Returns:
            True if successful
        """
        payload = [{'key': k, 'value': v} for k, v in env_vars.items()]
        
        self.logger.info(f"Setting {len(env_vars)} environment variables for {service_id}")
        
        await self._make_request('PUT', f'/services/{service_id}/env-vars', data=payload)
        return True
    
    async def delete_env_var(self, service_id: str, key: str) -> bool:
        """
        Delete an environment variable
        
        Args:
            service_id: Service ID
            key: Environment variable key to delete
            
        Returns:
            True if successful
        """
        self.logger.info(f"Deleting env var '{key}' from service {service_id}")
        
        await self._make_request('DELETE', f'/services/{service_id}/env-vars/{key}')
        return True
    
    # Deployment Methods
    
    async def get_deployments(self, service_id: str, limit: int = 20) -> List[Deployment]:
        """
        Get deployment history for a service
        
        Args:
            service_id: Service ID
            limit: Number of deployments to return
            
        Returns:
            List of Deployment objects
        """
        params = {'limit': min(limit, 100)}
        
        response = await self._make_request('GET', f'/services/{service_id}/deploys', params=params)
        
        deployments = []
        for deploy_data in response.get('deploys', []):
            deployment = Deployment(
                id=deploy_data['id'],
                service_id=service_id,
                status=deploy_data.get('status', 'unknown'),
                commit_sha=deploy_data.get('commitSha'),
                created_at=datetime.fromisoformat(deploy_data['createdAt'].replace('Z', '+00:00')),
                finished_at=datetime.fromisoformat(deploy_data['finishedAt'].replace('Z', '+00:00')) if deploy_data.get('finishedAt') else None
            )
            deployments.append(deployment)
        
        return deployments
    
    async def get_logs(self, service_id: str, start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve service logs with filtering
        
        Args:
            service_id: Service ID
            start_time: Start time for log filtering
            end_time: End time for log filtering
            limit: Maximum number of log entries
            
        Returns:
            List of log entries
        """
        params = {'limit': min(limit, 1000)}
        
        if start_time:
            params['startTime'] = start_time.isoformat()
        if end_time:
            params['endTime'] = end_time.isoformat()
        
        self.logger.info(f"Fetching logs for service {service_id} (limit: {limit})")
        
        response = await self._make_request('GET', f'/services/{service_id}/logs', params=params)
        
        return response.get('logs', [])
    
    # Health Check
    
    async def validate_connection(self) -> bool:
        """
        Validate API connection and credentials
        
        Returns:
            True if connection is valid
        """
        try:
            await self.get_services(limit=1)
            self.logger.info("API connection validated successfully")
            return True
        except RenderAPIError as e:
            self.logger.error(f"API connection validation failed: {e}")
            return False

# Helper function to create client from environment
def create_render_client() -> RenderAPIClient:
    """
    Create RenderAPIClient from environment variables
    
    Returns:
        Configured RenderAPIClient
        
    Raises:
        ValueError: If RENDER_API_KEY not found
    """
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key:
        raise ValueError("RENDER_API_KEY environment variable required")
    
    return RenderAPIClient(api_key)