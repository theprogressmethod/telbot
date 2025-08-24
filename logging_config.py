"""
Enterprise Logging Configuration
Provides structured logging with Sentry integration, correlation IDs, and proper error tracking
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import contextmanager
import uuid
from functools import wraps
import time

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records for request tracing"""
    
    def __init__(self):
        super().__init__()
        self.correlation_id = None
    
    def set_correlation_id(self, correlation_id: str):
        self.correlation_id = correlation_id
    
    def filter(self, record):
        record.correlation_id = self.correlation_id or str(uuid.uuid4())
        return True


class StructuredLogger:
    """Enterprise-grade structured logging with Sentry integration"""
    
    def __init__(self, name: str = "telbot", environment: str = None):
        self.name = name
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.logger = self._setup_logger()
        self.correlation_filter = CorrelationIdFilter()
        self.logger.addFilter(self.correlation_filter)
        
        # Initialize Sentry if DSN is provided
        self._setup_sentry()
        
        # Metrics for monitoring
        self.metrics = {
            "errors": 0,
            "warnings": 0,
            "requests": 0,
            "deployment_events": []
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configure structured JSON logging"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG if self.environment == "development" else logging.INFO)
        
        # Remove existing handlers
        logger.handlers = []
        
        # JSON formatter for structured logs
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            json_default=str,
            json_encoder=json.JSONEncoder
        )
        
        # Console handler (stdout for normal logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(lambda record: record.levelno < logging.ERROR)
        logger.addHandler(console_handler)
        
        # Error handler (stderr for errors)
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
        
        # File handler for persistent logs
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            f"{log_dir}/app-{self.environment}.log",
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Add error-specific file handler
        error_file_handler = logging.handlers.RotatingFileHandler(
            f"{log_dir}/errors-{self.environment}.log",
            maxBytes=10485760,
            backupCount=10
        )
        error_file_handler.setFormatter(formatter)
        error_file_handler.setLevel(logging.ERROR)
        logger.addHandler(error_file_handler)
        
        return logger
    
    def _setup_sentry(self):
        """Initialize Sentry error tracking"""
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if sentry_dsn:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=self.environment,
                integrations=[
                    sentry_logging,
                    FlaskIntegration(transaction_style='endpoint')
                ],
                traces_sample_rate=0.1 if self.environment == "production" else 1.0,
                attach_stacktrace=True,
                send_default_pii=False,
                before_send=self._before_send_sentry
            )
            
            self.logger.info("Sentry initialized", extra={
                "environment": self.environment,
                "sentry_enabled": True
            })
        else:
            self.logger.warning("Sentry DSN not configured", extra={
                "environment": self.environment,
                "sentry_enabled": False
            })
    
    def _before_send_sentry(self, event, hint):
        """Filter sensitive data before sending to Sentry"""
        # Remove sensitive fields
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'authorization']
        
        if 'extra' in event:
            for field in sensitive_fields:
                if field in event['extra']:
                    event['extra'][field] = '[REDACTED]'
        
        if 'request' in event and 'data' in event['request']:
            for field in sensitive_fields:
                if field in event['request']['data']:
                    event['request']['data'][field] = '[REDACTED]'
        
        return event
    
    @contextmanager
    def correlation_context(self, correlation_id: str = None):
        """Context manager for correlation ID"""
        correlation_id = correlation_id or str(uuid.uuid4())
        self.correlation_filter.set_correlation_id(correlation_id)
        
        try:
            yield correlation_id
        finally:
            self.correlation_filter.set_correlation_id(None)
    
    def log_deployment(self, action: str, details: Dict[str, Any]):
        """Log deployment events with enhanced tracking"""
        deployment_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "environment": self.environment,
            "details": details,
            "correlation_id": self.correlation_filter.correlation_id
        }
        
        self.metrics["deployment_events"].append(deployment_event)
        
        self.logger.info(f"Deployment event: {action}", extra={
            "deployment_action": action,
            "deployment_details": details,
            "event_type": "deployment"
        })
        
        # Send to Sentry as transaction
        with sentry_sdk.start_transaction(op="deployment", name=action):
            sentry_sdk.set_context("deployment", deployment_event)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Enhanced error logging with Sentry integration"""
        self.metrics["errors"] += 1
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "correlation_id": self.correlation_filter.correlation_id
        }
        
        self.logger.error(f"Error occurred: {error}", extra=error_details, exc_info=True)
        
        # Send to Sentry with additional context
        sentry_sdk.capture_exception(error, extra=context)
    
    def log_request(self, method: str, path: str, status: int, duration: float, **kwargs):
        """Log HTTP request with performance metrics"""
        self.metrics["requests"] += 1
        
        request_log = {
            "method": method,
            "path": path,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "correlation_id": self.correlation_filter.correlation_id,
            **kwargs
        }
        
        log_level = logging.INFO if status < 400 else logging.WARNING if status < 500 else logging.ERROR
        
        self.logger.log(log_level, f"{method} {path} - {status}", extra=request_log)
        
        # Track slow requests
        if duration > 1.0:  # More than 1 second
            self.logger.warning(f"Slow request detected: {method} {path}", extra={
                **request_log,
                "performance_alert": True
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for monitoring"""
        return {
            **self.metrics,
            "environment": self.environment,
            "timestamp": datetime.utcnow().isoformat()
        }




def performance_monitor(logger: StructuredLogger):
    """Decorator for monitoring function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = str(uuid.uuid4())
            
            with logger.correlation_context(correlation_id):
                logger.logger.debug(f"Starting {func.__name__}", extra={
                    "function": func.__name__,
                    "args": str(args)[:100],  # Truncate for safety
                    "kwargs": str(kwargs)[:100]
                })
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    logger.logger.debug(f"Completed {func.__name__}", extra={
                        "function": func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "success": True
                    })
                    
                    # Alert on slow operations
                    if duration > 5.0:
                        logger.logger.warning(f"Slow operation: {func.__name__}", extra={
                            "function": func.__name__,
                            "duration_ms": round(duration * 1000, 2),
                            "performance_alert": True
                        })
                    
                    return result
                
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_error(e, {
                        "function": func.__name__,
                        "duration_ms": round(duration * 1000, 2),
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    })
                    raise
        
        return wrapper
    return decorator


class DeploymentLogger:
    """Specialized logger for deployment operations"""
    
    def __init__(self, base_logger: StructuredLogger):
        self.logger = base_logger
        self.deployment_id = None
        self.start_time = None
    
    def start_deployment(self, deployment_id: str, environment: str, version: str):
        """Log deployment start"""
        self.deployment_id = deployment_id
        self.start_time = time.time()
        
        self.logger.log_deployment("deployment_started", {
            "deployment_id": deployment_id,
            "environment": environment,
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Set Sentry context
        sentry_sdk.set_tag("deployment_id", deployment_id)
        sentry_sdk.set_context("deployment", {
            "id": deployment_id,
            "environment": environment,
            "version": version
        })
    
    def log_step(self, step: str, status: str, details: Dict[str, Any] = None):
        """Log deployment step"""
        self.logger.logger.info(f"Deployment step: {step}", extra={
            "deployment_id": self.deployment_id,
            "step": step,
            "status": status,
            "details": details or {},
            "event_type": "deployment_step"
        })
    
    def end_deployment(self, success: bool, error: Exception = None):
        """Log deployment completion"""
        duration = time.time() - self.start_time if self.start_time else 0
        
        if success:
            self.logger.log_deployment("deployment_completed", {
                "deployment_id": self.deployment_id,
                "duration_seconds": round(duration, 2),
                "success": True
            })
        else:
            self.logger.log_deployment("deployment_failed", {
                "deployment_id": self.deployment_id,
                "duration_seconds": round(duration, 2),
                "success": False,
                "error": str(error) if error else "Unknown error"
            })
            
            if error:
                self.logger.log_error(error, {
                    "deployment_id": self.deployment_id,
                    "deployment_failure": True
                })


# Create global logger instance
logger = StructuredLogger()

# Convenience functions
def get_logger(name: str = None) -> StructuredLogger:
    """Get a logger instance"""
    if name:
        custom_logger = StructuredLogger(name)
        return custom_logger
    return logger

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Global error logging function"""
    logger.log_error(error, context)

def log_deployment(action: str, details: Dict[str, Any]):
    """Global deployment logging function"""
    logger.log_deployment(action, details)

def log_request(method: str, path: str, status: int, duration: float, **kwargs):
    """Global request logging function"""
    logger.log_request(method, path, status, duration, **kwargs)

# Export for Flask integration
def init_flask_logging(app):
    """Initialize Flask application logging"""
    import flask
    from flask import g, request
    
    @app.before_request
    def before_request():
        g.correlation_id = str(uuid.uuid4())
        g.start_time = time.time()
        logger.correlation_filter.set_correlation_id(g.correlation_id)
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            log_request(
                method=request.method,
                path=request.path,
                status=response.status_code,
                duration=duration,
                remote_addr=request.remote_addr,
                user_agent=request.user_agent.string
            )
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        log_error(error, {
            "path": request.path,
            "method": request.method,
            "remote_addr": request.remote_addr
        })
        
        if isinstance(error, flask.HTTPException):
            return error
        
        return flask.jsonify({
            "error": "Internal server error",
            "correlation_id": g.get('correlation_id')
        }), 500
    
    return app
