"""
Enterprise Health Check System
Provides comprehensive health monitoring for production systems
"""

import os
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Import our logging system
from logging_config import get_logger, performance_monitor

logger = get_logger("health_check")


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class ComponentHealth:
    """Health status for a single component"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    response_time_ms: float
    last_checked: str


class HealthCheckSystem:
    """Comprehensive health monitoring system"""
    
    def __init__(self, app_name: str = "telbot"):
        self.app_name = app_name
        self.start_time = time.time()
        self.checks_performed = 0
        self.last_check_time = None
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "status": self._get_cpu_status(cpu_percent)
            },
            "memory": {
                "percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "status": self._get_memory_status(memory.percent)
            },
            "disk": {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "status": self._get_disk_status(disk.percent)
            },
            "uptime_seconds": int(time.time() - self.start_time)
        }
    
    def _get_cpu_status(self, cpu_percent: float) -> str:
        if cpu_percent < 70:
            return "healthy"
        elif cpu_percent < 85:
            return "warning"
        else:
            return "critical"
    
    def _get_memory_status(self, memory_percent: float) -> str:
        if memory_percent < 80:
            return "healthy"
        elif memory_percent < 90:
            return "warning"
        else:
            return "critical"
    
    def _get_disk_status(self, disk_percent: float) -> str:
        if disk_percent < 80:
            return "healthy"
        elif disk_percent < 90:
            return "warning"
        else:
            return "critical"
    
    @performance_monitor(logger)
    def check_database(self) -> ComponentHealth:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            # Import database connection
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Database URL not configured",
                    details={"error": "Missing DATABASE_URL"},
                    response_time_ms=0,
                    last_checked=datetime.utcnow().isoformat()
                )
            
            # Test connection and simple query
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check connection
            cursor.execute("SELECT 1 as health_check")
            result = cursor.fetchone()
            
            # Check table counts for monitoring
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM users) as user_count,
                    (SELECT COUNT(*) FROM telegram_messages WHERE created_at > NOW() - INTERVAL '1 hour') as recent_messages
            """)
            stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine health based on response time
            if response_time < 100:
                status = HealthStatus.HEALTHY
                message = "Database responding normally"
            elif response_time < 500:
                status = HealthStatus.DEGRADED
                message = "Database response slow"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Database response very slow"
            
            return ComponentHealth(
                name="database",
                status=status,
                message=message,
                details={
                    "connected": True,
                    "user_count": stats.get('user_count', 0) if stats else 0,
                    "recent_messages": stats.get('recent_messages', 0) if stats else 0
                },
                response_time_ms=round(response_time, 2),
                last_checked=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.log_error(e, {"component": "database"})
            return ComponentHealth(
                name="database",
                status=HealthStatus.CRITICAL,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e), "connected": False},
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow().isoformat()
            )
    
    @performance_monitor(logger)
    def check_telegram_bot(self) -> ComponentHealth:
        """Check Telegram bot connectivity"""
        start_time = time.time()
        
        try:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                return ComponentHealth(
                    name="telegram_bot",
                    status=HealthStatus.UNHEALTHY,
                    message="Bot token not configured",
                    details={"error": "Missing TELEGRAM_BOT_TOKEN"},
                    response_time_ms=0,
                    last_checked=datetime.utcnow().isoformat()
                )
            
            # Check bot status via Telegram API
            response = requests.get(
                f"https://api.telegram.org/bot{bot_token}/getMe",
                timeout=5
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    
                    # Check webhook status
                    webhook_response = requests.get(
                        f"https://api.telegram.org/bot{bot_token}/getWebhookInfo",
                        timeout=5
                    )
                    webhook_data = webhook_response.json() if webhook_response.status_code == 200 else {}
                    webhook_info = webhook_data.get('result', {})
                    
                    return ComponentHealth(
                        name="telegram_bot",
                        status=HealthStatus.HEALTHY,
                        message="Bot connected and responding",
                        details={
                            "bot_username": bot_info.get('username'),
                            "bot_id": bot_info.get('id'),
                            "webhook_url": webhook_info.get('url'),
                            "pending_updates": webhook_info.get('pending_update_count', 0),
                            "last_error": webhook_info.get('last_error_message')
                        },
                        response_time_ms=round(response_time, 2),
                        last_checked=datetime.utcnow().isoformat()
                    )
            
            return ComponentHealth(
                name="telegram_bot",
                status=HealthStatus.UNHEALTHY,
                message=f"Bot API returned status {response.status_code}",
                details={"status_code": response.status_code},
                response_time_ms=round(response_time, 2),
                last_checked=datetime.utcnow().isoformat()
            )
            
        except requests.Timeout:
            return ComponentHealth(
                name="telegram_bot",
                status=HealthStatus.CRITICAL,
                message="Bot API timeout",
                details={"error": "Request timeout"},
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.log_error(e, {"component": "telegram_bot"})
            return ComponentHealth(
                name="telegram_bot",
                status=HealthStatus.CRITICAL,
                message=f"Bot check failed: {str(e)}",
                details={"error": str(e)},
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow().isoformat()
            )
    
    @performance_monitor(logger)
    def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity if configured"""
        start_time = time.time()
        
        try:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis not configured (optional)",
                    details={"configured": False},
                    response_time_ms=0,
                    last_checked=datetime.utcnow().isoformat()
                )
            
            import redis
            r = redis.from_url(redis_url)
            
            # Test connection
            r.ping()
            
            # Get some stats
            info = r.info()
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connected and responding",
                details={
                    "connected": True,
                    "used_memory_mb": round(info.get('used_memory', 0) / (1024*1024), 2),
                    "connected_clients": info.get('connected_clients', 0),
                    "uptime_days": round(info.get('uptime_in_seconds', 0) / 86400, 2)
                },
                response_time_ms=round(response_time, 2),
                last_checked=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.DEGRADED,
                message=f"Redis unavailable: {str(e)}",
                details={"error": str(e), "connected": False},
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.utcnow().isoformat()
            )
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get comprehensive health check results"""
        self.checks_performed += 1
        self.last_check_time = datetime.utcnow()
        
        # Run all health checks
        components = [
            self.check_database(),
            self.check_telegram_bot(),
            self.check_redis()
        ]
        
        # Determine overall status
        statuses = [c.status for c in components]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.CRITICAL for s in statuses):
            overall_status = HealthStatus.CRITICAL
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        # Get system metrics
        system_metrics = self.get_system_metrics()
        
        return {
            "status": overall_status.value,
            "timestamp": self.last_check_time.isoformat(),
            "version": os.getenv("APP_VERSION", "unknown"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "checks_performed": self.checks_performed,
            "components": [asdict(c) for c in components],
            "system": system_metrics,
            "deployment": {
                "commit": os.getenv("GIT_COMMIT", "unknown"),
                "deployed_at": os.getenv("DEPLOYED_AT", "unknown"),
                "deployed_by": os.getenv("DEPLOYED_BY", "unknown")
            }
        }
    
    def get_readiness(self) -> Dict[str, Any]:
        """Kubernetes-style readiness probe"""
        health = self.get_overall_health()
        
        return {
            "ready": health["status"] in [HealthStatus.HEALTHY.value, HealthStatus.DEGRADED.value],
            "status": health["status"],
            "timestamp": health["timestamp"]
        }
    
    def get_liveness(self) -> Dict[str, Any]:
        """Kubernetes-style liveness probe"""
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time)
        }


# Create health check instance
health_checker = HealthCheckSystem()


def create_health_endpoints(app: Flask):
    """Add health check endpoints to Flask app"""
    
    @app.route('/health', methods=['GET'])
    def health():
        """Comprehensive health check endpoint"""
        try:
            health_data = health_checker.get_overall_health()
            status_code = 200 if health_data["status"] == HealthStatus.HEALTHY.value else 503
            return jsonify(health_data), status_code
        except Exception as e:
            logger.log_error(e, {"endpoint": "/health"})
            return jsonify({
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/health/ready', methods=['GET'])
    def readiness():
        """Readiness probe for Kubernetes/load balancers"""
        try:
            readiness_data = health_checker.get_readiness()
            status_code = 200 if readiness_data["ready"] else 503
            return jsonify(readiness_data), status_code
        except Exception as e:
            logger.log_error(e, {"endpoint": "/health/ready"})
            return jsonify({"ready": False, "error": str(e)}), 503
    
    @app.route('/health/live', methods=['GET'])
    def liveness():
        """Liveness probe for Kubernetes/monitoring"""
        try:
            liveness_data = health_checker.get_liveness()
            return jsonify(liveness_data), 200
        except Exception as e:
            logger.log_error(e, {"endpoint": "/health/live"})
            return jsonify({"alive": False, "error": str(e)}), 503
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Prometheus-compatible metrics endpoint"""
        try:
            health_data = health_checker.get_overall_health()
            
            # Format as Prometheus metrics
            metrics_text = []
            
            # System metrics
            system = health_data.get('system', {})
            metrics_text.append(f"# HELP cpu_usage_percent CPU usage percentage")
            metrics_text.append(f"# TYPE cpu_usage_percent gauge")
            metrics_text.append(f"cpu_usage_percent {system.get('cpu', {}).get('percent', 0)}")
            
            metrics_text.append(f"# HELP memory_usage_percent Memory usage percentage")
            metrics_text.append(f"# TYPE memory_usage_percent gauge")
            metrics_text.append(f"memory_usage_percent {system.get('memory', {}).get('percent', 0)}")
            
            metrics_text.append(f"# HELP disk_usage_percent Disk usage percentage")
            metrics_text.append(f"# TYPE disk_usage_percent gauge")
            metrics_text.append(f"disk_usage_percent {system.get('disk', {}).get('percent', 0)}")
            
            metrics_text.append(f"# HELP uptime_seconds Application uptime in seconds")
            metrics_text.append(f"# TYPE uptime_seconds counter")
            metrics_text.append(f"uptime_seconds {system.get('uptime_seconds', 0)}")
            
            # Component health
            for component in health_data.get('components', []):
                name = component['name'].replace('-', '_')
                status_value = 1 if component['status'] == 'healthy' else 0
                
                metrics_text.append(f"# HELP component_{name}_healthy Component health status")
                metrics_text.append(f"# TYPE component_{name}_healthy gauge")
                metrics_text.append(f'component_{name}_healthy {status_value}')
                
                metrics_text.append(f"# HELP component_{name}_response_time_ms Component response time")
                metrics_text.append(f"# TYPE component_{name}_response_time_ms gauge")
                metrics_text.append(f"component_{name}_response_time_ms {component['response_time_ms']}")
            
            return '\n'.join(metrics_text), 200, {'Content-Type': 'text/plain'}
            
        except Exception as e:
            logger.log_error(e, {"endpoint": "/metrics"})
            return str(e), 500
    
    return app


# Uptime monitoring integration
class UptimeMonitor:
    """Integration with Uptime Robot and other monitoring services"""
    
    def __init__(self):
        self.uptime_robot_api_key = os.getenv("UPTIME_ROBOT_API_KEY")
        self.monitors = []
    
    def create_monitor(self, name: str, url: str, alert_contacts: List[str] = None) -> Dict[str, Any]:
        """Create an Uptime Robot monitor"""
        if not self.uptime_robot_api_key:
            return {"error": "Uptime Robot API key not configured"}
        
        try:
            response = requests.post(
                "https://api.uptimerobot.com/v2/newMonitor",
                data={
                    "api_key": self.uptime_robot_api_key,
                    "friendly_name": name,
                    "url": url,
                    "type": 1,  # HTTP(S)
                    "interval": 300,  # 5 minutes
                    "alert_contacts": "_".join(alert_contacts) if alert_contacts else ""
                },
                timeout=10
            )
            
            return response.json()
            
        except Exception as e:
            logger.log_error(e, {"service": "uptime_robot", "action": "create_monitor"})
            return {"error": str(e)}
    
    def get_monitor_status(self, monitor_id: str) -> Dict[str, Any]:
        """Get status of a specific monitor"""
        if not self.uptime_robot_api_key:
            return {"error": "Uptime Robot API key not configured"}
        
        try:
            response = requests.post(
                "https://api.uptimerobot.com/v2/getMonitors",
                data={
                    "api_key": self.uptime_robot_api_key,
                    "monitors": monitor_id,
                    "response_times": 1,
                    "logs": 1
                },
                timeout=10
            )
            
            return response.json()
            
        except Exception as e:
            logger.log_error(e, {"service": "uptime_robot", "action": "get_monitor_status"})
            return {"error": str(e)}


if __name__ == "__main__":
    # Test health checks
    health = health_checker.get_overall_health()
    print(json.dumps(health, indent=2))
