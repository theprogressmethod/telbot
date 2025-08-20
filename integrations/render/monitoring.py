"""
Render Monitor - Service health monitoring and alerting
WORKER_2_NEW Implementation - PREP-003A

Continuous monitoring of Render services with health checks and alerting
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

try:
    from .render_client import RenderAPIClient, RenderService, RenderAPIError
except ImportError:
    from render_client import RenderAPIClient, RenderService, RenderAPIError

class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    """Health check result"""
    service_id: str
    service_name: str
    status: HealthStatus
    timestamp: datetime
    uptime_percentage: float
    error_count: int
    response_time_ms: Optional[float] = None
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class Alert:
    """Service alert"""
    id: str
    service_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class RenderMonitor:
    """
    Continuous service health monitoring with alerting capabilities
    Integrates with Progress Method accountability patterns
    """
    
    def __init__(self, client: RenderAPIClient, check_interval_seconds: int = 300):
        """
        Initialize monitor
        
        Args:
            client: Configured RenderAPIClient
            check_interval_seconds: Health check interval (default 5 minutes)
        """
        self.client = client
        self.check_interval = check_interval_seconds
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self._monitoring_active = False
        self._monitored_services: Set[str] = set()
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Health data
        self._health_history: Dict[str, List[HealthCheck]] = {}
        self._current_health: Dict[str, HealthCheck] = {}
        
        # Alerting
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Performance tracking
        self._performance_history: Dict[str, List[Dict[str, Any]]] = {}
    
    # Monitoring control
    
    def add_service(self, service_id: str):
        """Add service to monitoring"""
        self._monitored_services.add(service_id)
        if service_id not in self._health_history:
            self._health_history[service_id] = []
        self.logger.info(f"Added service {service_id} to monitoring")
    
    def remove_service(self, service_id: str):
        """Remove service from monitoring"""
        self._monitored_services.discard(service_id)
        self.logger.info(f"Removed service {service_id} from monitoring")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback function for alert notifications"""
        self._alert_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info(f"Started monitoring {len(self._monitored_services)} services")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        self.logger.info("Stopped monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all monitored services"""
        if not self._monitored_services:
            return
        
        self.logger.debug(f"Performing health checks on {len(self._monitored_services)} services")
        
        # Run health checks concurrently
        tasks = [
            self._check_service_health(service_id) 
            for service_id in self._monitored_services
        ]
        
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for service_id, result in zip(self._monitored_services, health_results):
            if isinstance(result, Exception):
                self.logger.error(f"Health check failed for {service_id}: {result}")
                continue
            
            if result:
                # Store health check
                self._current_health[service_id] = result
                self._health_history[service_id].append(result)
                
                # Keep only last 100 checks per service
                if len(self._health_history[service_id]) > 100:
                    self._health_history[service_id].pop(0)
                
                # Check for alerts
                await self._evaluate_alerts(result)
    
    async def _check_service_health(self, service_id: str) -> Optional[HealthCheck]:
        """
        Perform comprehensive health check for a single service
        
        Args:
            service_id: Service ID to check
            
        Returns:
            HealthCheck result or None if failed
        """
        try:
            # Get service details
            service = await self.client.get_service(service_id)
            
            # Calculate health metrics
            health_status = self._calculate_health_status(service)
            uptime_percentage = await self._calculate_uptime(service_id)
            error_count = await self._count_recent_errors(service_id)
            
            # Analyze issues and recommendations
            issues, recommendations = self._analyze_service_issues(service, uptime_percentage, error_count)
            
            return HealthCheck(
                service_id=service_id,
                service_name=service.name,
                status=health_status,
                timestamp=datetime.now(),
                uptime_percentage=uptime_percentage,
                error_count=error_count,
                issues=issues,
                recommendations=recommendations
            )
            
        except RenderAPIError as e:
            self.logger.error(f"Health check API error for {service_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Health check failed for {service_id}: {e}")
            return None
    
    def _calculate_health_status(self, service: RenderService) -> HealthStatus:
        """Calculate overall health status based on service data"""
        if service.status == 'live':
            return HealthStatus.HEALTHY
        elif service.status in ['build_in_progress', 'deploy_in_progress']:
            return HealthStatus.WARNING
        elif service.status in ['build_failed', 'deploy_failed', 'deactivated']:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.UNKNOWN
    
    async def _calculate_uptime(self, service_id: str) -> float:
        """Calculate service uptime percentage over last 24 hours"""
        try:
            # Get recent deployments to assess uptime
            deployments = await self.client.get_deployments(service_id, limit=10)
            
            # Simple uptime calculation based on successful vs failed deployments
            if not deployments:
                return 100.0
            
            successful = len([d for d in deployments if d.status == 'live'])
            total = len(deployments)
            
            return (successful / total) * 100 if total > 0 else 100.0
            
        except Exception as e:
            self.logger.error(f"Uptime calculation failed for {service_id}: {e}")
            return 0.0
    
    async def _count_recent_errors(self, service_id: str) -> int:
        """Count errors in recent logs"""
        try:
            # Get recent logs
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            logs = await self.client.get_logs(service_id, start_time, end_time, limit=500)
            
            # Count error-level log entries
            error_count = 0
            for log_entry in logs:
                message = log_entry.get('message', '').lower()
                if any(keyword in message for keyword in ['error', 'exception', 'failed', 'crash']):
                    error_count += 1
            
            return error_count
            
        except Exception as e:
            self.logger.error(f"Error counting failed for {service_id}: {e}")
            return 0
    
    def _analyze_service_issues(self, service: RenderService, 
                               uptime_percentage: float, error_count: int) -> tuple:
        """Analyze service for issues and generate recommendations"""
        issues = []
        recommendations = []
        
        # Check uptime
        if uptime_percentage < 95:
            issues.append(f"Low uptime: {uptime_percentage:.1f}%")
            recommendations.append("Review recent deployment failures and fix build issues")
        
        # Check error count
        if error_count > 50:
            issues.append(f"High error count: {error_count} errors in last hour")
            recommendations.append("Review application logs for error patterns")
        elif error_count > 10:
            issues.append(f"Moderate error count: {error_count} errors in last hour")
            recommendations.append("Monitor error trends and investigate if increasing")
        
        # Check service status
        if service.status in ['build_failed', 'deploy_failed']:
            issues.append(f"Service deployment failed: {service.status}")
            recommendations.append("Check build logs and fix deployment issues")
        elif service.status == 'deactivated':
            issues.append("Service is deactivated")
            recommendations.append("Reactivate service if needed")
        
        # Check for stale deployments
        service_age_hours = (datetime.now() - service.updated_at).total_seconds() / 3600
        if service_age_hours > 24 * 7:  # 1 week
            issues.append(f"No updates in {service_age_hours/24:.0f} days")
            recommendations.append("Consider updating service with latest code")
        
        return issues, recommendations
    
    # Alert management
    
    async def _evaluate_alerts(self, health_check: HealthCheck):
        """Evaluate health check for alert conditions"""
        service_id = health_check.service_id
        
        # Critical health status
        if health_check.status == HealthStatus.CRITICAL:
            await self._trigger_alert(
                service_id,
                AlertSeverity.CRITICAL,
                f"Service {health_check.service_name} is in critical state"
            )
        
        # Low uptime
        if health_check.uptime_percentage < 90:
            await self._trigger_alert(
                service_id,
                AlertSeverity.WARNING,
                f"Service {health_check.service_name} has low uptime: {health_check.uptime_percentage:.1f}%"
            )
        
        # High error count
        if health_check.error_count > 100:
            await self._trigger_alert(
                service_id,
                AlertSeverity.CRITICAL,
                f"Service {health_check.service_name} has high error count: {health_check.error_count}"
            )
        elif health_check.error_count > 50:
            await self._trigger_alert(
                service_id,
                AlertSeverity.WARNING,
                f"Service {health_check.service_name} has elevated error count: {health_check.error_count}"
            )
        
        # Resolve alerts if service is healthy
        if health_check.status == HealthStatus.HEALTHY and health_check.error_count < 10:
            await self._resolve_alerts(service_id)
    
    async def _trigger_alert(self, service_id: str, severity: AlertSeverity, message: str):
        """Trigger an alert for a service"""
        alert_id = f"{service_id}_{severity.value}_{datetime.now().timestamp()}"
        
        # Check if similar alert is already active
        existing_alerts = [
            a for a in self._active_alerts.values()
            if a.service_id == service_id and a.severity == severity and not a.resolved
        ]
        
        if existing_alerts:
            return  # Don't duplicate similar active alerts
        
        alert = Alert(
            id=alert_id,
            service_id=service_id,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        
        self._active_alerts[alert_id] = alert
        
        self.logger.warning(f"Alert triggered: {message}")
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    async def _resolve_alerts(self, service_id: str):
        """Resolve all active alerts for a service"""
        resolved_count = 0
        
        for alert in self._active_alerts.values():
            if alert.service_id == service_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                resolved_count += 1
        
        if resolved_count > 0:
            self.logger.info(f"Resolved {resolved_count} alerts for service {service_id}")
    
    # Data access methods
    
    def get_current_health(self, service_id: Optional[str] = None) -> Dict[str, HealthCheck]:
        """Get current health status for services"""
        if service_id:
            return {service_id: self._current_health.get(service_id)} if service_id in self._current_health else {}
        return self._current_health.copy()
    
    def get_health_history(self, service_id: str, hours: int = 24) -> List[HealthCheck]:
        """Get health history for a service"""
        if service_id not in self._health_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            check for check in self._health_history[service_id]
            if check.timestamp >= cutoff_time
        ]
    
    def get_active_alerts(self, service_id: Optional[str] = None) -> List[Alert]:
        """Get active alerts"""
        alerts = [alert for alert in self._active_alerts.values() if not alert.resolved]
        
        if service_id:
            alerts = [alert for alert in alerts if alert.service_id == service_id]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary statistics"""
        total_services = len(self._monitored_services)
        active_alerts = len(self.get_active_alerts())
        
        # Count by health status
        health_counts = {}
        for health in self._current_health.values():
            status = health.status.value
            health_counts[status] = health_counts.get(status, 0) + 1
        
        # Calculate average uptime
        uptimes = [health.uptime_percentage for health in self._current_health.values()]
        avg_uptime = sum(uptimes) / len(uptimes) if uptimes else 0
        
        return {
            'total_monitored_services': total_services,
            'active_alerts': active_alerts,
            'health_distribution': health_counts,
            'average_uptime_percentage': round(avg_uptime, 2),
            'monitoring_active': self._monitoring_active,
            'check_interval_seconds': self.check_interval
        }
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        summary = self.get_monitoring_summary()
        
        # Service details
        service_details = []
        for service_id in self._monitored_services:
            health = self._current_health.get(service_id)
            alerts = self.get_active_alerts(service_id)
            
            if health:
                service_details.append({
                    'service_id': service_id,
                    'service_name': health.service_name,
                    'status': health.status.value,
                    'uptime_percentage': health.uptime_percentage,
                    'error_count': health.error_count,
                    'issues_count': len(health.issues),
                    'active_alerts': len(alerts),
                    'last_check': health.timestamp.isoformat()
                })
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'summary': summary,
            'services': service_details,
            'active_alerts': [
                {
                    'id': alert.id,
                    'service_id': alert.service_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.get_active_alerts()
            ]
        }
    
    async def cleanup(self):
        """Clean up monitor resources"""
        await self.stop_monitoring()
        self._monitored_services.clear()
        self._health_history.clear()
        self._current_health.clear()
        self._active_alerts.clear()
        
        self.logger.info("RenderMonitor cleanup completed")