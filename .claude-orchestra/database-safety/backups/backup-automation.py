#!/usr/bin/env python3
"""
Database Backup Automation System
Core backup orchestration with scheduling, validation, and rotation

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import json
import logging
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

# Add orchestration path for logging
sys.path.append(str(Path(__file__).parent.parent.parent))

class DatabaseBackupAutomation:
    """Automated database backup system with validation and rotation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.backup_dir = Path(self.config.get('backup_directory', '/tmp/db_backups'))
        self.logger = self._setup_logging()
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'backup-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load backup configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default backup configuration"""
        return {
            'backup_directory': '/tmp/db_backups',
            'retention_days': 30,
            'compression': True,
            'validation_required': True,
            'environments': {
                'development': {
                    'enabled': True,
                    'schedule': 'daily',
                    'retention_days': 7
                },
                'staging': {
                    'enabled': False,
                    'schedule': 'weekly',
                    'retention_days': 14
                },
                'production': {
                    'enabled': False,
                    'schedule': 'daily',
                    'retention_days': 30
                }
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for backup operations"""
        logger = logging.getLogger('backup_automation')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / 'database-backups.log'
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
    
    def create_backup(self, environment: str = 'development') -> Tuple[bool, str]:
        """Create a database backup for specified environment"""
        try:
            self.logger.info(f"Starting backup for environment: {environment}")
            
            # Check if environment backup is enabled
            env_config = self.config.get('environments', {}).get(environment, {})
            if not env_config.get('enabled', False):
                self.logger.warning(f"Backup disabled for environment: {environment}")
                return False, f"Backup disabled for {environment}"
            
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{environment}_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Mock backup creation (safe for Phase 0 Prep)
            backup_content = self._generate_mock_backup(environment)
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            # Compress if configured
            if self.config.get('compression', True):
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    backup_path.unlink()  # Remove uncompressed version
                    backup_path = compressed_path
            
            # Validate backup
            if self.config.get('validation_required', True):
                is_valid, validation_msg = self._validate_backup(backup_path)
                if not is_valid:
                    self.logger.error(f"Backup validation failed: {validation_msg}")
                    return False, f"Validation failed: {validation_msg}"
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Log backup creation
            backup_info = {
                'environment': environment,
                'backup_path': str(backup_path),
                'checksum': checksum,
                'size_bytes': backup_path.stat().st_size,
                'created_at': datetime.now().isoformat()
            }
            
            self._log_backup_info(backup_info)
            self.logger.info(f"Backup created successfully: {backup_path}")
            
            return True, str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False, f"Backup failed: {e}"
    
    def _generate_mock_backup(self, environment: str) -> str:
        """Generate mock backup content for safety (Phase 0 Prep)"""
        return f"""-- Database Backup Mock for {environment}
-- Created: {datetime.now().isoformat()}
-- Environment: {environment}
-- Safety: This is a mock backup for Phase 0 Prep testing

-- Mock schema
CREATE TABLE IF NOT EXISTS mock_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mock data
INSERT INTO mock_users (username) VALUES 
    ('test_user_1'),
    ('test_user_2'),
    ('test_user_3');

-- Backup completed successfully
-- Checksum will be calculated separately
"""
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress backup file using gzip"""
        try:
            import gzip
            import shutil
            
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            self.logger.info(f"Backup compressed: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return None
    
    def _validate_backup(self, backup_path: Path) -> Tuple[bool, str]:
        """Validate backup file integrity"""
        try:
            if not backup_path.exists():
                return False, "Backup file does not exist"
            
            # Check file size
            size = backup_path.stat().st_size
            if size == 0:
                return False, "Backup file is empty"
            
            # Check if compressed file can be read
            if backup_path.suffix == '.gz':
                import gzip
                try:
                    with gzip.open(backup_path, 'rt') as f:
                        f.readline()  # Try to read first line
                except Exception:
                    return False, "Compressed backup file is corrupted"
            else:
                # Check if regular file can be read
                try:
                    with open(backup_path, 'r') as f:
                        f.readline()  # Try to read first line
                except Exception:
                    return False, "Backup file is corrupted or unreadable"
            
            return True, "Backup validation successful"
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of backup file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def _log_backup_info(self, backup_info: Dict):
        """Log backup information to orchestration system"""
        try:
            # Log to backup-specific log
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            backup_log = log_dir / 'backup-history.json'
            
            # Load existing history or create new
            history = []
            if backup_log.exists():
                try:
                    with open(backup_log, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new backup info
            history.append(backup_info)
            
            # Keep only recent backups in history
            cutoff_date = datetime.now() - timedelta(days=90)
            history = [
                b for b in history 
                if datetime.fromisoformat(b['created_at']) > cutoff_date
            ]
            
            # Save updated history
            with open(backup_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [BACKUP] [SUCCESS] {backup_info['environment']} backup created: {backup_info['backup_path']}"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log backup info: {e}")
    
    def cleanup_old_backups(self, environment: str = 'development') -> int:
        """Clean up old backup files based on retention policy"""
        try:
            env_config = self.config.get('environments', {}).get(environment, {})
            retention_days = env_config.get('retention_days', 7)
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            cleaned_count = 0
            for backup_file in self.backup_dir.glob(f"backup_{environment}_*"):
                try:
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        backup_file.unlink()
                        cleaned_count += 1
                        self.logger.info(f"Cleaned up old backup: {backup_file}")
                except Exception as e:
                    self.logger.error(f"Failed to clean backup {backup_file}: {e}")
            
            self.logger.info(f"Cleaned up {cleaned_count} old backups for {environment}")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0
    
    def get_backup_status(self, environment: str = 'development') -> Dict:
        """Get backup status for environment"""
        try:
            backups = list(self.backup_dir.glob(f"backup_{environment}_*"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            status = {
                'environment': environment,
                'total_backups': len(backups),
                'latest_backup': None,
                'total_size_mb': 0,
                'last_backup_age_hours': None
            }
            
            if backups:
                latest = backups[0]
                status['latest_backup'] = str(latest)
                status['last_backup_age_hours'] = (
                    datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)
                ).total_seconds() / 3600
                
                # Calculate total size
                total_size = sum(b.stat().st_size for b in backups)
                status['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get backup status: {e}")
            return {'error': str(e)}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Automation')
    parser.add_argument('action', choices=['create', 'cleanup', 'status'], 
                       help='Action to perform')
    parser.add_argument('--environment', default='development',
                       choices=['development', 'staging', 'production'],
                       help='Environment to backup')
    
    args = parser.parse_args()
    
    automation = DatabaseBackupAutomation()
    
    if args.action == 'create':
        success, message = automation.create_backup(args.environment)
        print(f"Backup result: {message}")
        sys.exit(0 if success else 1)
        
    elif args.action == 'cleanup':
        count = automation.cleanup_old_backups(args.environment)
        print(f"Cleaned up {count} old backups")
        
    elif args.action == 'status':
        status = automation.get_backup_status(args.environment)
        print(json.dumps(status, indent=2))

if __name__ == '__main__':
    main()