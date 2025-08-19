#!/usr/bin/env python3
"""
Database Rollback Manager
Automated and manual rollback orchestration with safety validation

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

class RollbackManager:
    """Comprehensive rollback management and orchestration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'rollback-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load rollback configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default rollback configuration"""
        return {
            'safety_checks': {
                'verify_backup_before_rollback': True,
                'require_confirmation': True,
                'validate_rollback_script': True,
                'create_rollback_backup': True
            },
            'timeouts': {
                'rollback_timeout_minutes': 30,
                'validation_timeout_minutes': 5,
                'backup_timeout_minutes': 15
            },
            'environments': {
                'development': {
                    'auto_rollback_enabled': True,
                    'require_approval': False
                },
                'staging': {
                    'auto_rollback_enabled': True,
                    'require_approval': True
                },
                'production': {
                    'auto_rollback_enabled': False,
                    'require_approval': True
                }
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for rollback operations"""
        logger = logging.getLogger('rollback_manager')
        logger.setLevel(logging.INFO)
        
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'rollback-operations.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def execute_rollback(self, rollback_script: str, environment: str = 'development', reason: str = 'manual') -> Tuple[bool, Dict]:
        """Execute rollback with comprehensive safety checks"""
        rollback_result = {
            'rollback_script': rollback_script,
            'environment': environment,
            'reason': reason,
            'start_time': datetime.now().isoformat(),
            'safety_checks': [],
            'rollback_status': 'STARTED',
            'backup_created': False,
            'rollback_executed': False,
            'validation_passed': False
        }
        
        try:
            self.logger.info(f"Starting rollback: {rollback_script} for {environment}")
            
            # Safety Check 1: Verify rollback script exists
            if not self._verify_rollback_script(rollback_script):
                rollback_result['rollback_status'] = 'FAILED'
                rollback_result['error'] = 'Rollback script not found or invalid'
                return False, rollback_result
            
            rollback_result['safety_checks'].append('script_verification')
            
            # Safety Check 2: Create backup before rollback
            if self.config['safety_checks'].get('create_rollback_backup', True):
                backup_success = self._create_pre_rollback_backup(environment)
                rollback_result['backup_created'] = backup_success
                rollback_result['safety_checks'].append('pre_rollback_backup')
                
                if not backup_success:
                    rollback_result['rollback_status'] = 'FAILED'
                    rollback_result['error'] = 'Pre-rollback backup failed'
                    return False, rollback_result
            
            # Execute rollback (mock for Phase 0 Prep)
            rollback_success = self._execute_rollback_script(rollback_script, environment)
            rollback_result['rollback_executed'] = rollback_success
            
            if rollback_success:
                # Post-rollback validation
                validation_success = self._validate_rollback_success(environment)
                rollback_result['validation_passed'] = validation_success
                rollback_result['safety_checks'].append('post_rollback_validation')
                
                if validation_success:
                    rollback_result['rollback_status'] = 'SUCCESS'
                    rollback_result['end_time'] = datetime.now().isoformat()
                    self.logger.info(f"Rollback completed successfully: {rollback_script}")
                else:
                    rollback_result['rollback_status'] = 'VALIDATION_FAILED'
                    self.logger.error(f"Rollback validation failed: {rollback_script}")
            else:
                rollback_result['rollback_status'] = 'EXECUTION_FAILED'
                self.logger.error(f"Rollback execution failed: {rollback_script}")
            
            # Log rollback operation
            self._log_rollback_operation(rollback_result)
            
            return rollback_result['rollback_status'] == 'SUCCESS', rollback_result
            
        except Exception as e:
            self.logger.error(f"Rollback failed with exception: {e}")
            rollback_result['rollback_status'] = 'ERROR'
            rollback_result['error'] = str(e)
            return False, rollback_result
    
    def _verify_rollback_script(self, rollback_script: str) -> bool:
        """Verify rollback script exists and is valid"""
        try:
            script_path = Path(rollback_script)
            if not script_path.exists():
                self.logger.error(f"Rollback script not found: {rollback_script}")
                return False
            
            # Basic content validation
            with open(script_path, 'r') as f:
                content = f.read()
            
            if len(content.strip()) < 10:
                self.logger.error("Rollback script appears empty")
                return False
            
            # Check for SQL content
            if not any(keyword in content.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']):
                self.logger.warning("Rollback script may not contain valid SQL")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying rollback script: {e}")
            return False
    
    def _create_pre_rollback_backup(self, environment: str) -> bool:
        """Create backup before executing rollback"""
        try:
            backup_script = Path(__file__).parent.parent / 'backups' / 'backup-automation.py'
            cmd = [sys.executable, str(backup_script), 'create', '--environment', environment]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)  # 15 min timeout
            
            if result.returncode == 0:
                self.logger.info(f"Pre-rollback backup created for {environment}")
                return True
            else:
                self.logger.error(f"Pre-rollback backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating pre-rollback backup: {e}")
            return False
    
    def _execute_rollback_script(self, rollback_script: str, environment: str) -> bool:
        """Execute the rollback script (mock for Phase 0 Prep)"""
        try:
            self.logger.info(f"Executing rollback script: {rollback_script}")
            
            # Mock execution for Phase 0 Prep safety
            with open(rollback_script, 'r') as f:
                script_content = f.read()
            
            # Simulate rollback execution
            lines = [line.strip() for line in script_content.split('\n') if line.strip() and not line.strip().startswith('--')]
            
            self.logger.info(f"Mock rollback execution: {len(lines)} statements")
            
            # In real implementation, this would execute against the database
            # For Phase 0 Prep, we simulate success
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing rollback script: {e}")
            return False
    
    def _validate_rollback_success(self, environment: str) -> bool:
        """Validate that rollback was successful"""
        try:
            # Mock validation for Phase 0 Prep
            self.logger.info(f"Validating rollback success for {environment}")
            
            # In real implementation, this would verify database state
            # For Phase 0 Prep, we simulate success
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating rollback: {e}")
            return False
    
    def _log_rollback_operation(self, result: Dict):
        """Log rollback operation to orchestration system"""
        try:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            rollback_log = log_dir / 'rollback-history.json'
            
            # Load existing history
            history = []
            if rollback_log.exists():
                try:
                    with open(rollback_log, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new rollback result
            history.append(result)
            
            # Keep only recent rollbacks (last 50)
            if len(history) > 50:
                history = history[-50:]
            
            # Save updated history
            with open(rollback_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            status = result['rollback_status']
            environment = result['environment']
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [ROLLBACK] [{status}] {environment}: {result['rollback_script']}"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log rollback operation: {e}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Rollback Manager')
    parser.add_argument('rollback_script', help='Path to rollback script')
    parser.add_argument('--environment', default='development',
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--reason', default='manual',
                       help='Reason for rollback')
    parser.add_argument('--force', action='store_true',
                       help='Force rollback without confirmation')
    
    args = parser.parse_args()
    
    if not args.force:
        print(f"About to rollback: {args.rollback_script} in {args.environment}")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Rollback cancelled")
            sys.exit(1)
    
    manager = RollbackManager()
    success, result = manager.execute_rollback(args.rollback_script, args.environment, args.reason)
    
    print(f"Rollback status: {result.get('rollback_status', 'UNKNOWN')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()