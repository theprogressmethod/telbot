#!/usr/bin/env python3
"""
Database Backup Scheduler
Cron-compatible backup scheduling with environment-aware timing and conflict prevention

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import threading
import time

class BackupScheduler:
    """Automated backup scheduling system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.running = False
        self.scheduler_thread = None
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'backup-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load scheduler configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default scheduler configuration"""
        return {
            'schedules': {
                'development': {
                    'enabled': True,
                    'frequency': 'daily',
                    'time': '02:00',
                    'timezone': 'UTC',
                    'max_concurrent': 1
                },
                'staging': {
                    'enabled': False,
                    'frequency': 'weekly',
                    'time': '01:00',
                    'day_of_week': 'sunday',
                    'timezone': 'UTC',
                    'max_concurrent': 1
                },
                'production': {
                    'enabled': False,
                    'frequency': 'daily',
                    'time': '00:30',
                    'timezone': 'UTC',
                    'max_concurrent': 2
                }
            },
            'conflict_prevention': {
                'check_running_backups': True,
                'max_wait_minutes': 30,
                'retry_delay_minutes': 5
            },
            'emergency_triggers': {
                'enabled': True,
                'pre_migration': True,
                'pre_deployment': True,
                'on_critical_update': True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for scheduler operations"""
        logger = logging.getLogger('backup_scheduler')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / 'backup-scheduler.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return False
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Backup scheduler started")
        return True
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return False
            
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        self.logger.info("Backup scheduler stopped")
        return True
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Check each environment schedule
                for env_name, schedule_config in self.config.get('schedules', {}).items():
                    if schedule_config.get('enabled', False):
                        if self._should_run_backup(env_name, schedule_config):
                            self._schedule_backup(env_name)
                
                # Sleep for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)  # Continue after error
    
    def _should_run_backup(self, environment: str, schedule_config: Dict) -> bool:
        """Determine if backup should run for environment"""
        try:
            now = datetime.now()
            frequency = schedule_config.get('frequency', 'daily')
            scheduled_time = schedule_config.get('time', '02:00')
            
            # Parse scheduled time
            hour, minute = map(int, scheduled_time.split(':'))
            
            # Check if we're in the right time window (within 1 minute)
            if not (now.hour == hour and now.minute == minute):
                return False
            
            # Check frequency-specific conditions
            if frequency == 'daily':
                return self._should_run_daily(environment, now)
            elif frequency == 'weekly':
                day_of_week = schedule_config.get('day_of_week', 'sunday').lower()
                return self._should_run_weekly(environment, now, day_of_week)
            elif frequency == 'hourly':
                return self._should_run_hourly(environment, now)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking schedule for {environment}: {e}")
            return False
    
    def _should_run_daily(self, environment: str, now: datetime) -> bool:
        """Check if daily backup should run"""
        # Check if backup already ran today
        last_backup = self._get_last_backup_time(environment)
        if last_backup and last_backup.date() == now.date():
            return False
        
        return True
    
    def _should_run_weekly(self, environment: str, now: datetime, day_of_week: str) -> bool:
        """Check if weekly backup should run"""
        # Map day names to weekday numbers
        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_weekday = days.get(day_of_week, 6)  # Default to Sunday
        
        if now.weekday() != target_weekday:
            return False
        
        # Check if backup already ran this week
        last_backup = self._get_last_backup_time(environment)
        if last_backup:
            days_since_backup = (now - last_backup).days
            if days_since_backup < 7:
                return False
        
        return True
    
    def _should_run_hourly(self, environment: str, now: datetime) -> bool:
        """Check if hourly backup should run"""
        # Check if backup already ran this hour
        last_backup = self._get_last_backup_time(environment)
        if last_backup:
            time_diff = now - last_backup
            if time_diff.total_seconds() < 3600:  # Less than 1 hour
                return False
        
        return True
    
    def _get_last_backup_time(self, environment: str) -> Optional[datetime]:
        """Get timestamp of last backup for environment"""
        try:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            backup_log = log_dir / 'backup-history.json'
            
            if not backup_log.exists():
                return None
            
            with open(backup_log, 'r') as f:
                history = json.load(f)
            
            # Find most recent backup for this environment
            env_backups = [
                b for b in history 
                if b.get('environment') == environment
            ]
            
            if not env_backups:
                return None
            
            # Sort by creation time and get most recent
            env_backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            last_backup_time = env_backups[0].get('created_at')
            
            if last_backup_time:
                return datetime.fromisoformat(last_backup_time)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last backup time: {e}")
            return None
    
    def _schedule_backup(self, environment: str):
        """Schedule a backup for the specified environment"""
        try:
            self.logger.info(f"Scheduling backup for environment: {environment}")
            
            # Check for running backups (conflict prevention)
            if self._is_backup_running(environment):
                self.logger.warning(f"Backup already running for {environment}, skipping")
                return False
            
            # Check for system locks
            if self._is_environment_locked(environment):
                self.logger.warning(f"Environment {environment} is locked, skipping backup")
                return False
            
            # Create backup task
            backup_script = Path(__file__).parent / 'backup-automation.py'
            
            # Run backup in background
            cmd = [sys.executable, str(backup_script), 'create', '--environment', environment]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Backup completed successfully for {environment}")
                    self._log_scheduled_backup(environment, 'SUCCESS', result.stdout)
                else:
                    self.logger.error(f"Backup failed for {environment}: {result.stderr}")
                    self._log_scheduled_backup(environment, 'FAILED', result.stderr)
                
            except subprocess.TimeoutExpired:
                self.logger.error(f"Backup timeout for {environment}")
                self._log_scheduled_backup(environment, 'TIMEOUT', 'Backup process timed out')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling backup for {environment}: {e}")
            self._log_scheduled_backup(environment, 'ERROR', str(e))
            return False
    
    def _is_backup_running(self, environment: str) -> bool:
        """Check if backup is currently running for environment"""
        try:
            # Check for running backup processes
            result = subprocess.run(
                ['pgrep', '-f', f'backup-automation.py.*{environment}'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            # If pgrep fails, assume no backup is running
            return False
    
    def _is_environment_locked(self, environment: str) -> bool:
        """Check if environment is locked (e.g., during maintenance)"""
        try:
            lock_dir = Path(__file__).parent.parent.parent / 'control'
            lock_file = lock_dir / f'{environment}-lock.flag'
            return lock_file.exists()
        except:
            return False
    
    def _log_scheduled_backup(self, environment: str, status: str, message: str):
        """Log scheduled backup result"""
        try:
            log_entry = {
                'environment': environment,
                'status': status,
                'message': message,
                'scheduled_at': datetime.now().isoformat(),
                'scheduler': 'backup-scheduler'
            }
            
            # Log to scheduler-specific log
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            scheduler_log = log_dir / 'scheduled-backups.json'
            
            # Load existing history
            history = []
            if scheduler_log.exists():
                try:
                    with open(scheduler_log, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new entry
            history.append(log_entry)
            
            # Keep only recent entries (last 100)
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            with open(scheduler_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            with open(orchestration_log, 'a') as f:
                log_entry_text = f"[{datetime.now().isoformat()}] [SCHEDULED_BACKUP] [{status}] {environment}: {message}"
                f.write(log_entry_text + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log scheduled backup: {e}")
    
    def trigger_emergency_backup(self, environment: str, reason: str = 'emergency') -> bool:
        """Trigger emergency backup immediately"""
        try:
            if not self.config.get('emergency_triggers', {}).get('enabled', True):
                self.logger.warning("Emergency backups are disabled")
                return False
            
            self.logger.info(f"Triggering emergency backup for {environment}: {reason}")
            
            # Skip normal scheduling checks for emergency backups
            backup_script = Path(__file__).parent / 'backup-automation.py'
            cmd = [sys.executable, str(backup_script), 'create', '--environment', environment]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            
            if result.returncode == 0:
                self.logger.info(f"Emergency backup completed for {environment}")
                self._log_scheduled_backup(environment, 'EMERGENCY_SUCCESS', f"Reason: {reason}")
                return True
            else:
                self.logger.error(f"Emergency backup failed for {environment}: {result.stderr}")
                self._log_scheduled_backup(environment, 'EMERGENCY_FAILED', f"Reason: {reason}, Error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Emergency backup error: {e}")
            self._log_scheduled_backup(environment, 'EMERGENCY_ERROR', f"Reason: {reason}, Error: {e}")
            return False
    
    def get_schedule_status(self) -> Dict:
        """Get current scheduler status"""
        try:
            status = {
                'running': self.running,
                'environments': {},
                'next_scheduled': {}
            }
            
            for env_name, schedule_config in self.config.get('schedules', {}).items():
                env_status = {
                    'enabled': schedule_config.get('enabled', False),
                    'frequency': schedule_config.get('frequency', 'daily'),
                    'time': schedule_config.get('time', '02:00'),
                    'last_backup': None,
                    'next_backup': None
                }
                
                # Get last backup time
                last_backup = self._get_last_backup_time(env_name)
                if last_backup:
                    env_status['last_backup'] = last_backup.isoformat()
                
                # Calculate next backup time
                next_backup = self._calculate_next_backup_time(env_name, schedule_config)
                if next_backup:
                    env_status['next_backup'] = next_backup.isoformat()
                
                status['environments'][env_name] = env_status
            
            return status
            
        except Exception as e:
            return {'error': f'Failed to get status: {e}'}
    
    def _calculate_next_backup_time(self, environment: str, schedule_config: Dict) -> Optional[datetime]:
        """Calculate next scheduled backup time"""
        try:
            now = datetime.now()
            frequency = schedule_config.get('frequency', 'daily')
            scheduled_time = schedule_config.get('time', '02:00')
            
            hour, minute = map(int, scheduled_time.split(':'))
            
            if frequency == 'daily':
                next_backup = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_backup <= now:
                    next_backup += timedelta(days=1)
                return next_backup
                
            elif frequency == 'weekly':
                day_of_week = schedule_config.get('day_of_week', 'sunday').lower()
                days = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                target_weekday = days.get(day_of_week, 6)
                
                days_ahead = target_weekday - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                
                next_backup = now + timedelta(days=days_ahead)
                next_backup = next_backup.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return next_backup
                
            elif frequency == 'hourly':
                next_backup = now.replace(minute=minute, second=0, microsecond=0)
                if next_backup <= now:
                    next_backup += timedelta(hours=1)
                return next_backup
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating next backup time: {e}")
            return None

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Scheduler')
    parser.add_argument('action', choices=['start', 'stop', 'status', 'emergency'], 
                       help='Scheduler action')
    parser.add_argument('--environment', 
                       choices=['development', 'staging', 'production'],
                       help='Environment for emergency backup')
    parser.add_argument('--reason', default='manual',
                       help='Reason for emergency backup')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (for start action)')
    
    args = parser.parse_args()
    
    scheduler = BackupScheduler()
    
    if args.action == 'start':
        if args.daemon:
            scheduler.start_scheduler()
            try:
                # Keep main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop_scheduler()
        else:
            success = scheduler.start_scheduler()
            print(f"Scheduler started: {success}")
            
    elif args.action == 'stop':
        success = scheduler.stop_scheduler()
        print(f"Scheduler stopped: {success}")
        
    elif args.action == 'status':
        status = scheduler.get_schedule_status()
        print(json.dumps(status, indent=2))
        
    elif args.action == 'emergency':
        if not args.environment:
            print("--environment required for emergency backup")
            sys.exit(1)
        
        success = scheduler.trigger_emergency_backup(args.environment, args.reason)
        print(f"Emergency backup {'succeeded' if success else 'failed'}")
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()