#!/usr/bin/env python3
"""
Database Connection Manager
Centralized database connection management with safety checks and monitoring

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
from typing import Dict, List, Optional, Tuple
import yaml
import psycopg2
from urllib.parse import urlparse

class ConnectionManager:
    """Centralized database connection management"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.active_connections = {}
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'database-safety-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load connection manager configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default connection manager configuration"""
        return {
            'connection_pools': {
                'development': {
                    'max_connections': 10,
                    'min_connections': 2,
                    'connection_timeout': 30,
                    'idle_timeout': 300
                },
                'staging': {
                    'max_connections': 20,
                    'min_connections': 5,
                    'connection_timeout': 30,
                    'idle_timeout': 600
                },
                'production': {
                    'max_connections': 50,
                    'min_connections': 10,
                    'connection_timeout': 30,
                    'idle_timeout': 900
                }
            },
            'safety_checks': {
                'validate_before_connect': True,
                'check_ssl_requirements': True,
                'log_connection_attempts': True,
                'monitor_connection_health': True
            },
            'monitoring': {
                'health_check_interval': 60,
                'log_slow_queries': True,
                'slow_query_threshold': 5.0,
                'connection_retry_attempts': 3,
                'retry_delay_seconds': 1
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for connection management"""
        logger = logging.getLogger('connection_manager')
        logger.setLevel(logging.INFO)
        
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'connection-manager.log'
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
    
    def create_connection(self, connection_string: str, environment: str = 'development') -> Tuple[bool, Optional[object], Dict]:
        """Create database connection with safety checks"""
        connection_result = {
            'environment': environment,
            'connection_string': connection_string[:20] + '...' if len(connection_string) > 20 else connection_string,
            'created_at': datetime.now().isoformat(),
            'connection_id': None,
            'validation_passed': False,
            'connection_established': False,
            'safety_checks': []
        }
        
        try:
            self.logger.info(f"Creating connection for {environment}")
            
            # Safety Check 1: Validate connection string
            if self.config['safety_checks'].get('validate_before_connect', True):
                validator = self._get_connection_validator()
                is_valid, validation_result = validator.validate_connection_string(connection_string, environment)
                connection_result['validation_passed'] = is_valid
                connection_result['safety_checks'].append('connection_validation')
                
                if not is_valid:
                    connection_result['error'] = 'Connection string validation failed'
                    connection_result['validation_details'] = validation_result
                    return False, None, connection_result
            
            # Safety Check 2: Check environment locks
            if self._is_environment_locked(environment):
                connection_result['error'] = f'Environment {environment} is locked'
                return False, None, connection_result
            
            # Mock connection for Phase 0 Prep safety
            connection_id = self._create_mock_connection(connection_string, environment)
            connection_result['connection_id'] = connection_id
            connection_result['connection_established'] = True
            connection_result['safety_checks'].append('mock_connection_created')
            
            # Store connection info
            self.active_connections[connection_id] = {
                'environment': environment,
                'created_at': datetime.now(),
                'last_used': datetime.now(),
                'is_active': True
            }
            
            # Log connection attempt
            self._log_connection_attempt(connection_result)
            
            self.logger.info(f"Connection created successfully: {connection_id}")
            return True, connection_id, connection_result
            
        except Exception as e:
            self.logger.error(f"Connection creation failed: {e}")
            connection_result['error'] = str(e)
            return False, None, connection_result
    
    def _get_connection_validator(self):
        """Get connection validator instance"""
        try:
            validator_path = Path(__file__).parent / 'connection-validator.py'
            sys.path.append(str(validator_path.parent))
            from connection_validator import ConnectionValidator
            return ConnectionValidator()
        except ImportError:
            # Fallback to basic validation
            class BasicValidator:
                def validate_connection_string(self, conn_str, env):
                    return len(conn_str) > 10, {'basic_check': True}
            return BasicValidator()
    
    def _create_mock_connection(self, connection_string: str, environment: str) -> str:
        """Create mock connection for Phase 0 Prep"""
        # Generate connection ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        connection_id = f"mock_conn_{environment}_{timestamp}"
        
        self.logger.info(f"Mock connection created: {connection_id}")
        return connection_id
    
    def close_connection(self, connection_id: str) -> Tuple[bool, Dict]:
        """Close database connection"""
        try:
            if connection_id not in self.active_connections:
                return False, {'error': 'Connection not found'}
            
            # Mark connection as inactive
            self.active_connections[connection_id]['is_active'] = False
            self.active_connections[connection_id]['closed_at'] = datetime.now()
            
            self.logger.info(f"Connection closed: {connection_id}")
            return True, {'connection_id': connection_id, 'status': 'closed'}
            
        except Exception as e:
            self.logger.error(f"Error closing connection {connection_id}: {e}")
            return False, {'error': str(e)}
    
    def get_connection_status(self, connection_id: Optional[str] = None) -> Dict:
        """Get status of connections"""
        try:
            if connection_id:
                if connection_id in self.active_connections:
                    return {
                        'connection_id': connection_id,
                        'status': self.active_connections[connection_id]
                    }
                else:
                    return {'error': 'Connection not found'}
            
            # Return all connections status
            return {
                'total_connections': len(self.active_connections),
                'active_connections': sum(1 for c in self.active_connections.values() if c['is_active']),
                'connections': self.active_connections
            }
            
        except Exception as e:
            return {'error': f'Failed to get connection status: {e}'}
    
    def health_check(self, environment: Optional[str] = None) -> Dict:
        """Perform health check on connections"""
        health_result = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'HEALTHY',
            'environments': {},
            'issues': []
        }
        
        try:
            environments_to_check = [environment] if environment else ['development', 'staging', 'production']
            
            for env in environments_to_check:
                env_connections = [
                    conn for conn_id, conn in self.active_connections.items()
                    if conn.get('environment') == env and conn.get('is_active', False)
                ]
                
                env_health = {
                    'environment': env,
                    'active_connections': len(env_connections),
                    'status': 'HEALTHY',
                    'last_check': datetime.now().isoformat()
                }
                
                # Check for stale connections
                stale_count = 0
                for conn in env_connections:
                    if self._is_connection_stale(conn):
                        stale_count += 1
                
                if stale_count > 0:
                    env_health['status'] = 'WARNING'
                    env_health['stale_connections'] = stale_count
                    health_result['issues'].append(f'{env}: {stale_count} stale connections')
                
                health_result['environments'][env] = env_health
            
            # Determine overall health
            if health_result['issues']:
                health_result['overall_health'] = 'WARNING'
            
            return health_result
            
        except Exception as e:
            health_result['overall_health'] = 'ERROR'
            health_result['error'] = str(e)
            return health_result
    
    def _is_connection_stale(self, connection_info: Dict) -> bool:
        """Check if connection is stale"""
        try:
            last_used = connection_info.get('last_used')
            if not last_used:
                return True
            
            if isinstance(last_used, str):
                last_used = datetime.fromisoformat(last_used)
            
            idle_threshold = timedelta(minutes=30)  # 30 minutes
            return datetime.now() - last_used > idle_threshold
            
        except Exception:
            return True
    
    def cleanup_stale_connections(self) -> Dict:
        """Clean up stale connections"""
        cleanup_result = {
            'cleaned_connections': [],
            'total_cleaned': 0
        }
        
        try:
            stale_connections = []
            
            for conn_id, conn_info in self.active_connections.items():
                if conn_info.get('is_active') and self._is_connection_stale(conn_info):
                    stale_connections.append(conn_id)
            
            for conn_id in stale_connections:
                success, result = self.close_connection(conn_id)
                if success:
                    cleanup_result['cleaned_connections'].append(conn_id)
            
            cleanup_result['total_cleaned'] = len(cleanup_result['cleaned_connections'])
            self.logger.info(f"Cleaned up {cleanup_result['total_cleaned']} stale connections")
            
            return cleanup_result
            
        except Exception as e:
            cleanup_result['error'] = str(e)
            return cleanup_result
    
    def _is_environment_locked(self, environment: str) -> bool:
        """Check if environment is locked"""
        try:
            lock_dir = Path(__file__).parent.parent.parent / 'control'
            lock_file = lock_dir / f'{environment}-lock.flag'
            return lock_file.exists()
        except:
            return False
    
    def _log_connection_attempt(self, result: Dict):
        """Log connection attempt to orchestration system"""
        try:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            connection_log = log_dir / 'connection-history.json'
            
            # Load existing history
            history = []
            if connection_log.exists():
                try:
                    with open(connection_log, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new connection result
            history.append(result)
            
            # Keep only recent connections (last 200)
            if len(history) > 200:
                history = history[-200:]
            
            # Save updated history
            with open(connection_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            environment = result['environment']
            status = 'SUCCESS' if result.get('connection_established') else 'FAILED'
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [CONNECTION] [{status}] {environment}: {result.get('connection_id', 'N/A')}"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log connection attempt: {e}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Connection Manager')
    parser.add_argument('action', choices=['connect', 'close', 'status', 'health', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--connection-string', 
                       help='Database connection string (for connect action)')
    parser.add_argument('--connection-id',
                       help='Connection ID (for close action)')
    parser.add_argument('--environment', default='development',
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    
    args = parser.parse_args()
    
    manager = ConnectionManager()
    
    if args.action == 'connect':
        if not args.connection_string:
            print("--connection-string required for connect action")
            sys.exit(1)
        
        success, connection, result = manager.create_connection(args.connection_string, args.environment)
        print(f"Connection {'succeeded' if success else 'failed'}")
        if success:
            print(f"Connection ID: {connection}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(0 if success else 1)
        
    elif args.action == 'close':
        if not args.connection_id:
            print("--connection-id required for close action")
            sys.exit(1)
        
        success, result = manager.close_connection(args.connection_id)
        print(f"Close {'succeeded' if success else 'failed'}")
        if not success:
            print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(0 if success else 1)
        
    elif args.action == 'status':
        status = manager.get_connection_status(args.connection_id)
        print(json.dumps(status, indent=2))
        
    elif args.action == 'health':
        health = manager.health_check(args.environment if args.environment != 'development' else None)
        print(json.dumps(health, indent=2))
        
    elif args.action == 'cleanup':
        result = manager.cleanup_stale_connections()
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()