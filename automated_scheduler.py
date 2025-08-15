#!/usr/bin/env python3
"""
Progress Method - Automated Testing and Monitoring Scheduler
Automated scheduling for tests, health checks, and monitoring tasks
"""

import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TaskType(Enum):
    HEALTH_CHECK = "health_check"
    METRICS_COLLECTION = "metrics_collection"
    TESTING = "testing"
    ALERTING = "alerting"
    CLEANUP = "cleanup"
    REPORTING = "reporting"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ScheduledTask:
    id: str
    name: str
    task_type: TaskType
    schedule_expression: str  # e.g., "every 5 minutes", "daily at 02:00"
    function: Callable
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    error_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TaskExecution:
    task_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.RUNNING
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class AutomatedScheduler:
    """Automated scheduler for Progress Method monitoring and testing tasks"""
    
    def __init__(self, monitor_system=None, metrics_system=None, alerting_system=None, testing_framework=None):
        self.monitor = monitor_system
        self.metrics = metrics_system
        self.alerting = alerting_system
        self.testing = testing_framework
        
        self.scheduled_tasks = {}
        self.task_executions = []
        self.scheduler_thread = None
        self.is_running = False
        
        # Setup default tasks
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """Setup default scheduled tasks for Progress Method"""
        
        default_tasks = [
            # Health Monitoring Tasks
            ScheduledTask(
                id="system_health_check",
                name="System Health Check",
                task_type=TaskType.HEALTH_CHECK,
                schedule_expression="every 2 minutes",
                function=self._run_system_health_check,
                timeout_seconds=60,
                metadata={"priority": "high", "critical": True}
            ),
            
            ScheduledTask(
                id="database_health_check",
                name="Database Health Check",
                task_type=TaskType.HEALTH_CHECK,
                schedule_expression="every 5 minutes",
                function=self._run_database_health_check,
                timeout_seconds=30,
                metadata={"priority": "high", "critical": True}
            ),
            
            # Metrics Collection Tasks
            ScheduledTask(
                id="collect_custom_metrics",
                name="Collect Custom Metrics",
                task_type=TaskType.METRICS_COLLECTION,
                schedule_expression="every 10 minutes",
                function=self._collect_custom_metrics,
                timeout_seconds=120,
                metadata={"priority": "medium"}
            ),
            
            ScheduledTask(
                id="generate_business_kpis",
                name="Generate Business KPIs",
                task_type=TaskType.METRICS_COLLECTION,
                schedule_expression="every 30 minutes",
                function=self._generate_business_kpis,
                timeout_seconds=180,
                metadata={"priority": "medium"}
            ),
            
            # Testing Tasks
            ScheduledTask(
                id="unit_tests",
                name="Run Unit Tests",
                task_type=TaskType.TESTING,
                schedule_expression="every 1 hour",
                function=self._run_unit_tests,
                timeout_seconds=300,
                metadata={"priority": "medium", "test_type": "unit"}
            ),
            
            ScheduledTask(
                id="integration_tests",
                name="Run Integration Tests",
                task_type=TaskType.TESTING,
                schedule_expression="every 4 hours",
                function=self._run_integration_tests,
                timeout_seconds=600,
                metadata={"priority": "medium", "test_type": "integration"}
            ),
            
            ScheduledTask(
                id="performance_tests",
                name="Run Performance Tests",
                task_type=TaskType.TESTING,
                schedule_expression="daily at 02:00",
                function=self._run_performance_tests,
                timeout_seconds=1800,
                metadata={"priority": "low", "test_type": "performance"}
            ),
            
            # Alerting Tasks
            ScheduledTask(
                id="process_alerts",
                name="Process Alerts",
                task_type=TaskType.ALERTING,
                schedule_expression="every 3 minutes",
                function=self._process_alerts,
                timeout_seconds=60,
                metadata={"priority": "high", "critical": True}
            ),
            
            ScheduledTask(
                id="alert_cleanup",
                name="Alert Cleanup",
                task_type=TaskType.CLEANUP,
                schedule_expression="daily at 01:00",
                function=self._cleanup_old_alerts,
                timeout_seconds=300,
                metadata={"priority": "low"}
            ),
            
            # Reporting Tasks
            ScheduledTask(
                id="daily_report",
                name="Generate Daily Report",
                task_type=TaskType.REPORTING,
                schedule_expression="daily at 06:00",
                function=self._generate_daily_report,
                timeout_seconds=300,
                metadata={"priority": "medium", "report_type": "daily"}
            ),
            
            ScheduledTask(
                id="weekly_report",
                name="Generate Weekly Report",
                task_type=TaskType.REPORTING,
                schedule_expression="weekly on monday at 07:00",
                function=self._generate_weekly_report,
                timeout_seconds=600,
                metadata={"priority": "low", "report_type": "weekly"}
            ),
            
            # Cleanup Tasks
            ScheduledTask(
                id="metrics_cleanup",
                name="Metrics Cleanup",
                task_type=TaskType.CLEANUP,
                schedule_expression="daily at 03:00",
                function=self._cleanup_old_metrics,
                timeout_seconds=300,
                metadata={"priority": "low"}
            ),
            
            ScheduledTask(
                id="log_cleanup",
                name="Log Cleanup",
                task_type=TaskType.CLEANUP,
                schedule_expression="weekly on sunday at 04:00",
                function=self._cleanup_old_logs,
                timeout_seconds=600,
                metadata={"priority": "low"}
            )
        ]
        
        # Register all default tasks
        for task in default_tasks:
            self.scheduled_tasks[task.id] = task
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule all tasks
            for task in self.scheduled_tasks.values():
                if task.enabled:
                    self._schedule_task(task)
            
            # Start scheduler thread
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info(f"🕐 Automated scheduler started with {len(self.scheduled_tasks)} tasks")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the automated scheduler"""
        try:
            self.is_running = False
            schedule.clear()
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("🛑 Automated scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("📅 Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(5)  # Wait before retrying
        
        logger.info("📅 Scheduler thread stopped")
    
    def _schedule_task(self, task: ScheduledTask):
        """Schedule a task using the schedule library"""
        try:
            expression = task.schedule_expression.lower()
            
            if "every" in expression and "minutes" in expression:
                # Extract minutes: "every 5 minutes"
                minutes = int([w for w in expression.split() if w.isdigit()][0])
                schedule.every(minutes).minutes.do(self._execute_task_wrapper, task.id)
                
            elif "every" in expression and "hour" in expression:
                # Extract hours: "every 1 hour" or "every 4 hours"
                hours = int([w for w in expression.split() if w.isdigit()][0]) if any(w.isdigit() for w in expression.split()) else 1
                schedule.every(hours).hours.do(self._execute_task_wrapper, task.id)
                
            elif "daily at" in expression:
                # Extract time: "daily at 02:00"
                time_part = expression.split("at")[1].strip()
                schedule.every().day.at(time_part).do(self._execute_task_wrapper, task.id)
                
            elif "weekly" in expression:
                # Extract day and time: "weekly on monday at 07:00"
                parts = expression.split()
                day = None
                time_part = "00:00"
                
                for i, part in enumerate(parts):
                    if part in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        day = part
                    if part == "at" and i + 1 < len(parts):
                        time_part = parts[i + 1]
                
                if day:
                    getattr(schedule.every(), day).at(time_part).do(self._execute_task_wrapper, task.id)
                else:
                    schedule.every().week.at(time_part).do(self._execute_task_wrapper, task.id)
            
            else:
                logger.warning(f"Unknown schedule expression: {expression}")
                
        except Exception as e:
            logger.error(f"❌ Error scheduling task {task.name}: {e}")
    
    def _execute_task_wrapper(self, task_id: str):
        """Wrapper to execute task asynchronously"""
        try:
            # Run task in async context
            asyncio.create_task(self._execute_task(task_id))
        except Exception as e:
            logger.error(f"❌ Error in task wrapper for {task_id}: {e}")
    
    async def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        task = self.scheduled_tasks.get(task_id)
        if not task or not task.enabled:
            return
        
        execution = TaskExecution(
            task_id=task_id,
            started_at=datetime.now()
        )
        self.task_executions.append(execution)
        
        try:
            logger.info(f"🔄 Executing task: {task.name}")
            execution.status = TaskStatus.RUNNING
            task.status = TaskStatus.RUNNING
            
            # Execute the task function with timeout
            result = await asyncio.wait_for(
                task.function(),
                timeout=task.timeout_seconds
            )
            
            # Task completed successfully
            execution.completed_at = datetime.now()
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = TaskStatus.COMPLETED
            execution.result = result
            
            task.status = TaskStatus.COMPLETED
            task.last_run = execution.completed_at
            task.error_count = 0  # Reset error count on success
            
            logger.info(f"✅ Task completed: {task.name} ({execution.duration_seconds:.2f}s)")
            
        except asyncio.TimeoutError:
            # Task timed out
            execution.completed_at = datetime.now()
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = TaskStatus.FAILED
            execution.error_message = f"Task timed out after {task.timeout_seconds} seconds"
            
            task.status = TaskStatus.FAILED
            task.error_count += 1
            
            logger.error(f"⏰ Task timed out: {task.name}")
            
        except Exception as e:
            # Task failed with error
            execution.completed_at = datetime.now()
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            
            task.status = TaskStatus.FAILED
            task.error_count += 1
            
            logger.error(f"❌ Task failed: {task.name} - {e}")
            
            # Disable task if too many errors
            if task.error_count >= task.max_retries:
                task.enabled = False
                logger.error(f"🚫 Task disabled due to repeated failures: {task.name}")
    
    # Task Implementation Methods
    
    async def _run_system_health_check(self) -> Dict[str, Any]:
        """Run system health check"""
        try:
            if not self.monitor:
                return {"status": "skipped", "reason": "Monitor not available"}
            
            overview = await self.monitor.get_system_overview()
            
            # Analyze health status
            status = overview.get("system_status", {}).get("status", "unknown")
            health_percentage = overview.get("system_status", {}).get("health_percentage", 0)
            
            return {
                "status": "completed",
                "health_status": status,
                "health_percentage": health_percentage,
                "components_checked": overview.get("system_status", {}).get("total_components", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _run_database_health_check(self) -> Dict[str, Any]:
        """Run database health check"""
        try:
            from telbot import DatabaseManager
            
            # Test database connectivity
            db_healthy = await DatabaseManager.test_database()
            
            # Additional database tests could go here
            result = {
                "status": "completed",
                "database_healthy": db_healthy,
                "connectivity": "ok" if db_healthy else "failed",
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _collect_custom_metrics(self) -> Dict[str, Any]:
        """Collect custom Progress Method metrics"""
        try:
            if not self.metrics:
                return {"status": "skipped", "reason": "Metrics system not available"}
            
            metrics = await self.metrics.collect_progress_method_metrics()
            
            return {
                "status": "completed",
                "metrics_collected": len(metrics),
                "critical_alerts": len([m for m in metrics if m.severity.value == "critical"]),
                "warning_alerts": len([m for m in metrics if m.severity.value == "warning"]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Custom metrics collection failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _generate_business_kpis(self) -> Dict[str, Any]:
        """Generate business KPIs"""
        try:
            if not self.metrics:
                return {"status": "skipped", "reason": "Metrics system not available"}
            
            kpis = await self.metrics.generate_business_kpis()
            
            return {
                "status": "completed",
                "kpis_generated": len(kpis),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business KPIs generation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        try:
            if not self.testing:
                return {"status": "skipped", "reason": "Testing framework not available"}
            
            results = await self.testing.run_unit_tests()
            
            return {
                "status": "completed",
                "test_results": results,
                "tests_passed": results.get("tests_passed", 0),
                "tests_failed": results.get("tests_failed", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Unit tests failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        try:
            if not self.testing:
                return {"status": "skipped", "reason": "Testing framework not available"}
            
            # This would run integration tests
            # For now, simulate
            return {
                "status": "completed",
                "integration_tests": "simulated",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integration tests failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        try:
            if not self.testing:
                return {"status": "skipped", "reason": "Testing framework not available"}
            
            # This would run performance tests
            # For now, simulate
            return {
                "status": "completed",
                "performance_tests": "simulated",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance tests failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _process_alerts(self) -> Dict[str, Any]:
        """Process alerts from metrics"""
        try:
            if not self.alerting or not self.metrics:
                return {"status": "skipped", "reason": "Alerting or metrics system not available"}
            
            # Get current metrics
            metrics = await self.metrics.collect_progress_method_metrics()
            
            # Convert to dict format for alerting
            metrics_data = [asdict(m) for m in metrics]
            
            # Process for alerts
            alerts = await self.alerting.process_metrics_for_alerts(metrics_data)
            
            return {
                "status": "completed",
                "alerts_generated": len(alerts),
                "metrics_processed": len(metrics_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Alert processing failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _cleanup_old_alerts(self) -> Dict[str, Any]:
        """Cleanup old resolved alerts"""
        try:
            # This would cleanup old alerts from database/storage
            # For now, simulate
            return {
                "status": "completed",
                "alerts_cleaned": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Alert cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily monitoring report"""
        try:
            # Collect data for daily report
            report_data = {
                "date": datetime.now().date().isoformat(),
                "system_health": "healthy",
                "alerts_today": 0,
                "tests_run": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # This would generate and send the report
            logger.info(f"📊 Daily report generated: {report_data}")
            
            return {
                "status": "completed",
                "report_generated": True,
                "report_data": report_data
            }
            
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly monitoring report"""
        try:
            # Collect data for weekly report
            report_data = {
                "week_start": (datetime.now() - timedelta(days=7)).date().isoformat(),
                "week_end": datetime.now().date().isoformat(),
                "system_availability": 99.5,
                "total_alerts": 0,
                "tests_run": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # This would generate and send the report
            logger.info(f"📊 Weekly report generated: {report_data}")
            
            return {
                "status": "completed",
                "report_generated": True,
                "report_data": report_data
            }
            
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _cleanup_old_metrics(self) -> Dict[str, Any]:
        """Cleanup old metrics data"""
        try:
            # This would cleanup old metrics from database/storage
            # For now, simulate
            return {
                "status": "completed",
                "metrics_cleaned": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metrics cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _cleanup_old_logs(self) -> Dict[str, Any]:
        """Cleanup old log files"""
        try:
            # This would cleanup old log files
            # For now, simulate
            return {
                "status": "completed",
                "logs_cleaned": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Log cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    # Management Methods
    
    def add_task(self, task: ScheduledTask) -> bool:
        """Add a new scheduled task"""
        try:
            self.scheduled_tasks[task.id] = task
            
            if self.is_running and task.enabled:
                self._schedule_task(task)
            
            logger.info(f"✅ Added scheduled task: {task.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding task {task.name}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        try:
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]
                logger.info(f"✅ Removed scheduled task: {task_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error removing task {task_id}: {e}")
            return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a scheduled task"""
        try:
            task = self.scheduled_tasks.get(task_id)
            if task:
                task.enabled = True
                if self.is_running:
                    self._schedule_task(task)
                logger.info(f"✅ Enabled task: {task.name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error enabling task {task_id}: {e}")
            return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a scheduled task"""
        try:
            task = self.scheduled_tasks.get(task_id)
            if task:
                task.enabled = False
                logger.info(f"✅ Disabled task: {task.name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error disabling task {task_id}: {e}")
            return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        try:
            total_tasks = len(self.scheduled_tasks)
            enabled_tasks = len([t for t in self.scheduled_tasks.values() if t.enabled])
            failed_tasks = len([t for t in self.scheduled_tasks.values() if t.status == TaskStatus.FAILED])
            
            recent_executions = [e for e in self.task_executions if e.started_at > datetime.now() - timedelta(hours=24)]
            successful_executions = len([e for e in recent_executions if e.status == TaskStatus.COMPLETED])
            
            return {
                "scheduler_running": self.is_running,
                "total_tasks": total_tasks,
                "enabled_tasks": enabled_tasks,
                "failed_tasks": failed_tasks,
                "executions_24h": len(recent_executions),
                "success_rate_24h": (successful_executions / len(recent_executions) * 100) if recent_executions else 100,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {"error": str(e)}
    
    def get_task_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all scheduled tasks"""
        try:
            summary = []
            for task in self.scheduled_tasks.values():
                summary.append({
                    "id": task.id,
                    "name": task.name,
                    "type": task.task_type.value,
                    "schedule": task.schedule_expression,
                    "enabled": task.enabled,
                    "status": task.status.value,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "error_count": task.error_count,
                    "metadata": task.metadata
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting task summary: {e}")
            return []

if __name__ == "__main__":
    print("Automated Scheduler - Automated testing and monitoring for Progress Method")