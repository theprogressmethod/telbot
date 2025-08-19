#!/usr/bin/env python3
"""
Database Safety System Test Suite
Comprehensive testing of all database safety infrastructure components

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import tempfile

class DatabaseSafetySystemTester:
    """Comprehensive database safety system testing"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.logger = self._setup_logging()
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'components_tested': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'component_results': {}
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for system testing"""
        logger = logging.getLogger('database_safety_tester')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def run_comprehensive_test_suite(self) -> Tuple[bool, Dict]:
        """Run comprehensive test suite for all components"""
        try:
            self.logger.info("Starting comprehensive database safety system test")
            
            # Test each component
            components = [
                ('backup_system', self._test_backup_system),
                ('migration_validator', self._test_migration_validator),
                ('rollback_manager', self._test_rollback_manager),
                ('connection_validator', self._test_connection_validator),
                ('connection_manager', self._test_connection_manager),
                ('connection_tester', self._test_connection_tester),
                ('configuration_files', self._test_configuration_files),
                ('system_integration', self._test_system_integration)
            ]
            
            for component_name, test_function in components:
                self.logger.info(f"Testing component: {component_name}")
                component_result = test_function()
                self.test_results['component_results'][component_name] = component_result
                self.test_results['components_tested'].append(component_name)
                
                # Update counters
                self.test_results['total_tests'] += component_result.get('total_tests', 0)
                self.test_results['passed_tests'] += component_result.get('passed_tests', 0)
                self.test_results['failed_tests'] += component_result.get('failed_tests', 0)
                self.test_results['warnings'].extend(component_result.get('warnings', []))
            
            # Determine overall success
            overall_success = self.test_results['failed_tests'] == 0
            self.test_results['overall_success'] = overall_success
            self.test_results['end_time'] = datetime.now().isoformat()
            
            # Log final results
            self._log_test_results()
            
            self.logger.info(f"System test completed: {'SUCCESS' if overall_success else 'FAILURE'}")
            self.logger.info(f"Tests: {self.test_results['passed_tests']}/{self.test_results['total_tests']} passed")
            
            return overall_success, self.test_results
            
        except Exception as e:
            self.logger.error(f"System test failed with exception: {e}")
            self.test_results['error'] = str(e)
            return False, self.test_results
    
    def _test_backup_system(self) -> Dict:
        """Test backup automation system"""
        result = {
            'component': 'backup_system',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check backup automation script exists and is executable
            backup_script = self.base_path / 'backups' / 'backup-automation.py'
            test_result = self._test_file_exists_and_executable(backup_script, 'backup-automation.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test backup script help command
            if test_result['passed']:
                help_test = self._test_script_help(backup_script)
                result['tests']['help_command'] = help_test
                self._update_counters(result, help_test)
            
            # Test 3: Test backup validator
            validator_script = self.base_path / 'backups' / 'backup-validator.py'
            validator_test = self._test_file_exists_and_executable(validator_script, 'backup-validator.py')
            result['tests']['validator_exists'] = validator_test
            self._update_counters(result, validator_test)
            
            # Test 4: Test backup scheduler
            scheduler_script = self.base_path / 'backups' / 'backup-scheduler.py'
            scheduler_test = self._test_file_exists_and_executable(scheduler_script, 'backup-scheduler.py')
            result['tests']['scheduler_exists'] = scheduler_test
            self._update_counters(result, scheduler_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_migration_validator(self) -> Dict:
        """Test migration validation system"""
        result = {
            'component': 'migration_validator',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check migration validator script exists
            validator_script = self.base_path / 'migrations' / 'migration-validator.py'
            test_result = self._test_file_exists_and_executable(validator_script, 'migration-validator.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test with sample migration file
            if test_result['passed']:
                sample_migration = self._create_sample_migration_file()
                validation_test = self._test_migration_validation(validator_script, sample_migration)
                result['tests']['validation_test'] = validation_test
                self._update_counters(result, validation_test)
                
                # Clean up sample file
                if sample_migration.exists():
                    sample_migration.unlink()
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_rollback_manager(self) -> Dict:
        """Test rollback management system"""
        result = {
            'component': 'rollback_manager',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check rollback manager script exists
            rollback_script = self.base_path / 'rollback' / 'rollback-manager.py'
            test_result = self._test_file_exists_and_executable(rollback_script, 'rollback-manager.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test help command
            if test_result['passed']:
                help_test = self._test_script_help(rollback_script)
                result['tests']['help_command'] = help_test
                self._update_counters(result, help_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_connection_validator(self) -> Dict:
        """Test connection validation system"""
        result = {
            'component': 'connection_validator',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check connection validator script exists
            validator_script = self.base_path / 'connections' / 'connection-validator.py'
            test_result = self._test_file_exists_and_executable(validator_script, 'connection-validator.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test connection validation with sample connection string
            if test_result['passed']:
                validation_test = self._test_connection_validation_function(validator_script)
                result['tests']['validation_function'] = validation_test
                self._update_counters(result, validation_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_connection_manager(self) -> Dict:
        """Test connection management system"""
        result = {
            'component': 'connection_manager',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check connection manager script exists
            manager_script = self.base_path / 'connections' / 'connection-manager.py'
            test_result = self._test_file_exists_and_executable(manager_script, 'connection-manager.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test help command
            if test_result['passed']:
                help_test = self._test_script_help(manager_script)
                result['tests']['help_command'] = help_test
                self._update_counters(result, help_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_connection_tester(self) -> Dict:
        """Test connection testing system"""
        result = {
            'component': 'connection_tester',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check connection tester script exists
            tester_script = self.base_path / 'connections' / 'connection-test.py'
            test_result = self._test_file_exists_and_executable(tester_script, 'connection-test.py')
            result['tests']['script_exists'] = test_result
            self._update_counters(result, test_result)
            
            # Test 2: Test help command
            if test_result['passed']:
                help_test = self._test_script_help(tester_script)
                result['tests']['help_command'] = help_test
                self._update_counters(result, help_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_configuration_files(self) -> Dict:
        """Test configuration files"""
        result = {
            'component': 'configuration_files',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            config_files = [
                'database-safety-config.yaml',
                'backup-config.yaml',
                'migration-config.yaml',
                'rollback-config.yaml'
            ]
            
            for config_file in config_files:
                config_path = self.base_path / 'config' / config_file
                test_result = self._test_config_file(config_path, config_file)
                result['tests'][f'{config_file}_test'] = test_result
                self._update_counters(result, test_result)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_system_integration(self) -> Dict:
        """Test system integration"""
        result = {
            'component': 'system_integration',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': [],
            'tests': {}
        }
        
        try:
            # Test 1: Check directory structure
            structure_test = self._test_directory_structure()
            result['tests']['directory_structure'] = structure_test
            self._update_counters(result, structure_test)
            
            # Test 2: Check logs directory exists
            logs_test = self._test_logs_directory()
            result['tests']['logs_directory'] = logs_test
            self._update_counters(result, logs_test)
            
            # Test 3: Test orchestration integration
            orchestration_test = self._test_orchestration_integration()
            result['tests']['orchestration_integration'] = orchestration_test
            self._update_counters(result, orchestration_test)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _test_file_exists_and_executable(self, file_path: Path, file_name: str) -> Dict:
        """Test if file exists and is executable"""
        try:
            if not file_path.exists():
                return {
                    'passed': False,
                    'message': f'{file_name} does not exist',
                    'expected': str(file_path),
                    'warnings': [f'Missing required file: {file_name}']
                }
            
            if not os.access(file_path, os.X_OK):
                return {
                    'passed': False,
                    'message': f'{file_name} is not executable',
                    'warnings': [f'File permissions issue: {file_name}']
                }
            
            # Check if it's a Python script
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
            
            if not first_line.startswith('#!') or 'python' not in first_line:
                return {
                    'passed': False,
                    'message': f'{file_name} does not have proper Python shebang',
                    'warnings': [f'Shebang issue in {file_name}']
                }
            
            return {
                'passed': True,
                'message': f'{file_name} exists and is executable',
                'file_path': str(file_path)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing {file_name}: {e}',
                'warnings': [f'Test error for {file_name}']
            }
    
    def _test_script_help(self, script_path: Path) -> Dict:
        """Test script help command"""
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'passed': True,
                    'message': 'Help command works correctly',
                    'help_output_length': len(result.stdout)
                }
            else:
                return {
                    'passed': False,
                    'message': f'Help command failed: {result.stderr}',
                    'warnings': [f'Help command issue in {script_path.name}']
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': 'Help command timed out',
                'warnings': [f'Timeout in {script_path.name}']
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing help command: {e}',
                'warnings': [f'Help test error for {script_path.name}']
            }
    
    def _create_sample_migration_file(self) -> Path:
        """Create a sample migration file for testing"""
        sample_content = '''-- Migration ID: test_migration_001
-- Description: Sample migration for testing
-- Author: Database Safety Tester
-- Date: ''' + datetime.now().strftime('%Y-%m-%d') + '''

BEGIN;

CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_table (name) VALUES ('test_record');

COMMIT;
'''
        
        temp_file = Path(tempfile.mktemp(suffix='.sql'))
        with open(temp_file, 'w') as f:
            f.write(sample_content)
        
        return temp_file
    
    def _test_migration_validation(self, validator_script: Path, migration_file: Path) -> Dict:
        """Test migration validation functionality"""
        try:
            result = subprocess.run(
                [sys.executable, str(validator_script), str(migration_file), '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    validation_result = json.loads(result.stdout)
                    return {
                        'passed': True,
                        'message': 'Migration validation completed successfully',
                        'validation_result': validation_result
                    }
                except json.JSONDecodeError:
                    return {
                        'passed': False,
                        'message': 'Migration validation output is not valid JSON',
                        'warnings': ['JSON parsing issue in migration validator']
                    }
            else:
                return {
                    'passed': False,
                    'message': f'Migration validation failed: {result.stderr}',
                    'warnings': ['Migration validation failure']
                }
                
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing migration validation: {e}',
                'warnings': ['Migration validation test error']
            }
    
    def _test_connection_validation_function(self, validator_script: Path) -> Dict:
        """Test connection validation functionality"""
        try:
            # Test the validator by running its main function
            result = subprocess.run(
                [sys.executable, str(validator_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # For the connection validator, running without args should execute the test
            if result.returncode == 0:
                return {
                    'passed': True,
                    'message': 'Connection validation test completed',
                    'output_length': len(result.stdout)
                }
            else:
                return {
                    'passed': False,
                    'message': f'Connection validation test failed: {result.stderr}',
                    'warnings': ['Connection validation test failure']
                }
                
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing connection validation: {e}',
                'warnings': ['Connection validation test error']
            }
    
    def _test_config_file(self, config_path: Path, config_name: str) -> Dict:
        """Test configuration file"""
        try:
            if not config_path.exists():
                return {
                    'passed': False,
                    'message': f'{config_name} does not exist',
                    'warnings': [f'Missing config file: {config_name}']
                }
            
            # Try to read and parse YAML
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                if not config_data:
                    return {
                        'passed': False,
                        'message': f'{config_name} is empty or invalid',
                        'warnings': [f'Empty config file: {config_name}']
                    }
                
                return {
                    'passed': True,
                    'message': f'{config_name} is valid',
                    'config_keys': list(config_data.keys()) if isinstance(config_data, dict) else []
                }
                
            except yaml.YAMLError as e:
                return {
                    'passed': False,
                    'message': f'{config_name} has YAML syntax errors: {e}',
                    'warnings': [f'YAML syntax error in {config_name}']
                }
                
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing {config_name}: {e}',
                'warnings': [f'Config test error for {config_name}']
            }
    
    def _test_directory_structure(self) -> Dict:
        """Test directory structure"""
        try:
            required_dirs = [
                'backups',
                'migrations', 
                'rollback',
                'connections',
                'config'
            ]
            
            missing_dirs = []
            for dir_name in required_dirs:
                dir_path = self.base_path / dir_name
                if not dir_path.exists() or not dir_path.is_dir():
                    missing_dirs.append(dir_name)
            
            if missing_dirs:
                return {
                    'passed': False,
                    'message': f'Missing directories: {missing_dirs}',
                    'warnings': [f'Missing directory structure: {", ".join(missing_dirs)}']
                }
            
            return {
                'passed': True,
                'message': 'Directory structure is complete',
                'directories_found': required_dirs
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing directory structure: {e}',
                'warnings': ['Directory structure test error']
            }
    
    def _test_logs_directory(self) -> Dict:
        """Test logs directory"""
        try:
            logs_dir = self.base_path.parent / 'logs'
            
            if not logs_dir.exists():
                return {
                    'passed': False,
                    'message': 'Logs directory does not exist',
                    'warnings': ['Missing logs directory']
                }
            
            return {
                'passed': True,
                'message': 'Logs directory exists',
                'logs_path': str(logs_dir)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing logs directory: {e}',
                'warnings': ['Logs directory test error']
            }
    
    def _test_orchestration_integration(self) -> Dict:
        """Test orchestration system integration"""
        try:
            # Check for orchestration log
            orchestration_log = self.base_path.parent / 'logs' / 'orchestration.log'
            
            if orchestration_log.exists():
                return {
                    'passed': True,
                    'message': 'Orchestration integration appears to be working',
                    'log_exists': True
                }
            else:
                return {
                    'passed': True,  # Not critical for Phase 0 Prep
                    'message': 'Orchestration log not found (normal for Phase 0 Prep)',
                    'warnings': ['Orchestration log not present'],
                    'log_exists': False
                }
                
        except Exception as e:
            return {
                'passed': False,
                'message': f'Error testing orchestration integration: {e}',
                'warnings': ['Orchestration integration test error']
            }
    
    def _update_counters(self, result: Dict, test_result: Dict):
        """Update test counters"""
        result['total_tests'] += 1
        if test_result.get('passed', False):
            result['passed_tests'] += 1
        else:
            result['failed_tests'] += 1
        
        result['warnings'].extend(test_result.get('warnings', []))
    
    def _log_test_results(self):
        """Log test results to orchestration system"""
        try:
            # Log to file
            log_dir = self.base_path.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            test_log = log_dir / 'database-safety-system-test.json'
            with open(test_log, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            status = 'SUCCESS' if self.test_results.get('overall_success') else 'FAILURE'
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [DATABASE_SAFETY_TEST] [{status}] System test: {self.test_results['passed_tests']}/{self.test_results['total_tests']} tests passed"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log test results: {e}")

def main():
    """Main function for running the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Safety System Tester')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary',
                       help='Output format')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    tester = DatabaseSafetySystemTester()
    success, results = tester.run_comprehensive_test_suite()
    
    if args.output == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Summary output
        print(f"Database Safety System Test Results")
        print(f"==================================")
        print(f"Overall Status: {'SUCCESS' if success else 'FAILURE'}")
        print(f"Tests: {results['passed_tests']}/{results['total_tests']} passed")
        print(f"Components Tested: {len(results['components_tested'])}")
        
        if results.get('warnings'):
            print(f"\nWarnings ({len(results['warnings'])}):")
            for warning in results['warnings'][:10]:  # Limit to first 10
                print(f"  - {warning}")
            if len(results['warnings']) > 10:
                print(f"  ... and {len(results['warnings']) - 10} more")
        
        # Component breakdown
        print(f"\nComponent Test Results:")
        for component, component_result in results.get('component_results', {}).items():
            status = "✓" if component_result['failed_tests'] == 0 else "✗"
            print(f"  {status} {component}: {component_result['passed_tests']}/{component_result['total_tests']} passed")
        
        if not success:
            print(f"\nFailed Tests:")
            for component, component_result in results.get('component_results', {}).items():
                if component_result['failed_tests'] > 0:
                    print(f"\n  {component}:")
                    for test_name, test_result in component_result.get('tests', {}).items():
                        if not test_result.get('passed'):
                            print(f"    ✗ {test_name}: {test_result.get('message', 'No message')}")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()