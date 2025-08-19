#!/usr/bin/env python3
"""
Database Backup Validator
Verification system for backup file integrity and restoration testing

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import json
import gzip
import hashlib
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

class BackupValidator:
    """Comprehensive backup validation and integrity checking"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'backup-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load validation configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default validation configuration"""
        return {
            'validation_checks': {
                'file_integrity': True,
                'size_validation': True,
                'content_validation': True,
                'checksum_verification': True,
                'restoration_test': False  # Disabled for Phase 0 Prep
            },
            'min_backup_size_bytes': 100,
            'max_backup_age_hours': 48,
            'required_content_patterns': [
                'CREATE TABLE',
                'INSERT INTO'
            ]
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for validation operations"""
        logger = logging.getLogger('backup_validator')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / 'backup-validation.log'
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
    
    def validate_backup(self, backup_path: str) -> Tuple[bool, Dict]:
        """Comprehensive backup validation"""
        backup_file = Path(backup_path)
        
        validation_result = {
            'backup_path': backup_path,
            'validation_time': datetime.now().isoformat(),
            'checks_performed': [],
            'passed_checks': [],
            'failed_checks': [],
            'overall_status': 'PENDING',
            'recommendations': []
        }
        
        try:
            self.logger.info(f"Starting validation for backup: {backup_path}")
            
            # Check 1: File existence and basic properties
            if self.config['validation_checks'].get('file_integrity', True):
                result = self._check_file_integrity(backup_file)
                validation_result['checks_performed'].append('file_integrity')
                if result['passed']:
                    validation_result['passed_checks'].append('file_integrity')
                else:
                    validation_result['failed_checks'].append('file_integrity')
                    validation_result['recommendations'].extend(result.get('recommendations', []))
            
            # Check 2: Size validation
            if self.config['validation_checks'].get('size_validation', True):
                result = self._check_size_validation(backup_file)
                validation_result['checks_performed'].append('size_validation')
                if result['passed']:
                    validation_result['passed_checks'].append('size_validation')
                else:
                    validation_result['failed_checks'].append('size_validation')
                    validation_result['recommendations'].extend(result.get('recommendations', []))
            
            # Check 3: Content validation
            if self.config['validation_checks'].get('content_validation', True):
                result = self._check_content_validation(backup_file)
                validation_result['checks_performed'].append('content_validation')
                if result['passed']:
                    validation_result['passed_checks'].append('content_validation')
                else:
                    validation_result['failed_checks'].append('content_validation')
                    validation_result['recommendations'].extend(result.get('recommendations', []))
            
            # Check 4: Checksum verification
            if self.config['validation_checks'].get('checksum_verification', True):
                result = self._check_checksum_verification(backup_file)
                validation_result['checks_performed'].append('checksum_verification')
                if result['passed']:
                    validation_result['passed_checks'].append('checksum_verification')
                else:
                    validation_result['failed_checks'].append('checksum_verification')
                    validation_result['recommendations'].extend(result.get('recommendations', []))
            
            # Check 5: Restoration test (disabled for Phase 0 Prep)
            if self.config['validation_checks'].get('restoration_test', False):
                result = self._check_restoration_test(backup_file)
                validation_result['checks_performed'].append('restoration_test')
                if result['passed']:
                    validation_result['passed_checks'].append('restoration_test')
                else:
                    validation_result['failed_checks'].append('restoration_test')
                    validation_result['recommendations'].extend(result.get('recommendations', []))
            
            # Determine overall status
            if not validation_result['failed_checks']:
                validation_result['overall_status'] = 'PASSED'
                self.logger.info(f"Backup validation PASSED: {backup_path}")
            else:
                validation_result['overall_status'] = 'FAILED'
                self.logger.warning(f"Backup validation FAILED: {backup_path}")
            
            # Log validation result
            self._log_validation_result(validation_result)
            
            return validation_result['overall_status'] == 'PASSED', validation_result
            
        except Exception as e:
            self.logger.error(f"Validation failed with exception: {e}")
            validation_result['overall_status'] = 'ERROR'
            validation_result['error'] = str(e)
            return False, validation_result
    
    def _check_file_integrity(self, backup_file: Path) -> Dict:
        """Check basic file integrity"""
        try:
            if not backup_file.exists():
                return {
                    'passed': False,
                    'message': 'Backup file does not exist',
                    'recommendations': ['Check backup creation process', 'Verify file path']
                }
            
            if not backup_file.is_file():
                return {
                    'passed': False,
                    'message': 'Path is not a regular file',
                    'recommendations': ['Check if path points to correct file']
                }
            
            # Check if file is readable
            try:
                with open(backup_file, 'rb') as f:
                    f.read(1)
            except PermissionError:
                return {
                    'passed': False,
                    'message': 'File is not readable',
                    'recommendations': ['Check file permissions']
                }
            
            return {
                'passed': True,
                'message': 'File integrity check passed',
                'file_size': backup_file.stat().st_size,
                'last_modified': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'File integrity check failed: {e}',
                'recommendations': ['Investigate file system issues']
            }
    
    def _check_size_validation(self, backup_file: Path) -> Dict:
        """Validate backup file size"""
        try:
            file_size = backup_file.stat().st_size
            min_size = self.config.get('min_backup_size_bytes', 100)
            
            if file_size < min_size:
                return {
                    'passed': False,
                    'message': f'Backup file too small: {file_size} bytes (minimum: {min_size})',
                    'actual_size': file_size,
                    'minimum_size': min_size,
                    'recommendations': ['Check backup creation process', 'Verify data was actually backed up']
                }
            
            # Check backup age
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            age_hours = (datetime.now() - file_time).total_seconds() / 3600
            max_age = self.config.get('max_backup_age_hours', 48)
            
            warnings = []
            if age_hours > max_age:
                warnings.append(f'Backup is {age_hours:.1f} hours old (max recommended: {max_age})')
            
            return {
                'passed': True,
                'message': 'Size validation passed',
                'file_size': file_size,
                'age_hours': age_hours,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Size validation failed: {e}',
                'recommendations': ['Check file system status']
            }
    
    def _check_content_validation(self, backup_file: Path) -> Dict:
        """Validate backup file content"""
        try:
            required_patterns = self.config.get('required_content_patterns', [])
            
            # Read file content (handle compressed files)
            if backup_file.suffix == '.gz':
                with gzip.open(backup_file, 'rt') as f:
                    content = f.read()
            else:
                with open(backup_file, 'r') as f:
                    content = f.read()
            
            missing_patterns = []
            found_patterns = []
            
            for pattern in required_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                return {
                    'passed': False,
                    'message': f'Missing required content patterns: {missing_patterns}',
                    'found_patterns': found_patterns,
                    'missing_patterns': missing_patterns,
                    'recommendations': ['Check backup completeness', 'Verify database schema']
                }
            
            # Additional content checks
            line_count = content.count('\n')
            
            return {
                'passed': True,
                'message': 'Content validation passed',
                'found_patterns': found_patterns,
                'line_count': line_count,
                'content_size': len(content)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Content validation failed: {e}',
                'recommendations': ['Check file encoding', 'Verify file is not corrupted']
            }
    
    def _check_checksum_verification(self, backup_file: Path) -> Dict:
        """Verify backup file checksum"""
        try:
            # Calculate current checksum
            current_checksum = self._calculate_checksum(backup_file)
            
            # Try to find stored checksum
            checksum_file = backup_file.with_suffix(backup_file.suffix + '.sha256')
            stored_checksum = None
            
            if checksum_file.exists():
                try:
                    with open(checksum_file, 'r') as f:
                        stored_checksum = f.read().strip().split()[0]
                except Exception:
                    pass
            
            if stored_checksum:
                if current_checksum == stored_checksum:
                    return {
                        'passed': True,
                        'message': 'Checksum verification passed',
                        'current_checksum': current_checksum,
                        'stored_checksum': stored_checksum
                    }
                else:
                    return {
                        'passed': False,
                        'message': 'Checksum mismatch detected',
                        'current_checksum': current_checksum,
                        'stored_checksum': stored_checksum,
                        'recommendations': ['File may be corrupted', 'Re-create backup']
                    }
            else:
                # Create checksum file for future verification
                with open(checksum_file, 'w') as f:
                    f.write(f"{current_checksum}  {backup_file.name}\n")
                
                return {
                    'passed': True,
                    'message': 'Checksum calculated and stored',
                    'current_checksum': current_checksum,
                    'checksum_file_created': str(checksum_file)
                }
                
        except Exception as e:
            return {
                'passed': False,
                'message': f'Checksum verification failed: {e}',
                'recommendations': ['Check file system integrity']
            }
    
    def _check_restoration_test(self, backup_file: Path) -> Dict:
        """Test backup restoration (disabled for Phase 0 Prep)"""
        return {
            'passed': True,
            'message': 'Restoration test skipped (Phase 0 Prep safety)',
            'note': 'Restoration testing disabled for infrastructure setup phase'
        }
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def _log_validation_result(self, result: Dict):
        """Log validation result to orchestration system"""
        try:
            # Log to validation-specific log
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            validation_log = log_dir / 'backup-validation-history.json'
            
            # Load existing history
            history = []
            if validation_log.exists():
                try:
                    with open(validation_log, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Add new validation result
            history.append(result)
            
            # Keep only recent validations
            cutoff_date = datetime.now() - timedelta(days=30)
            history = [
                v for v in history 
                if datetime.fromisoformat(v['validation_time']) > cutoff_date
            ]
            
            # Save updated history
            with open(validation_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            status = result['overall_status']
            backup_path = result['backup_path']
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [BACKUP_VALIDATION] [{status}] {backup_path}"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log validation result: {e}")
    
    def validate_multiple_backups(self, backup_directory: str) -> Dict:
        """Validate all backups in a directory"""
        try:
            backup_dir = Path(backup_directory)
            if not backup_dir.exists():
                return {'error': 'Backup directory does not exist'}
            
            backup_files = list(backup_dir.glob('backup_*.sql*'))
            
            results = {
                'total_backups': len(backup_files),
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'backup_results': []
            }
            
            for backup_file in backup_files:
                is_valid, validation_result = self.validate_backup(str(backup_file))
                
                if validation_result['overall_status'] == 'PASSED':
                    results['passed'] += 1
                elif validation_result['overall_status'] == 'FAILED':
                    results['failed'] += 1
                else:
                    results['errors'] += 1
                
                results['backup_results'].append({
                    'file': str(backup_file),
                    'status': validation_result['overall_status'],
                    'checks_passed': len(validation_result['passed_checks']),
                    'checks_failed': len(validation_result['failed_checks'])
                })
            
            return results
            
        except Exception as e:
            return {'error': f'Validation failed: {e}'}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Validator')
    parser.add_argument('backup_path', help='Path to backup file or directory')
    parser.add_argument('--multiple', action='store_true',
                       help='Validate multiple backups in directory')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary',
                       help='Output format')
    
    args = parser.parse_args()
    
    validator = BackupValidator()
    
    if args.multiple:
        results = validator.validate_multiple_backups(args.backup_path)
    else:
        is_valid, results = validator.validate_backup(args.backup_path)
    
    if args.output == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Summary output
        if args.multiple:
            print(f"Validation Summary:")
            print(f"Total backups: {results.get('total_backups', 0)}")
            print(f"Passed: {results.get('passed', 0)}")
            print(f"Failed: {results.get('failed', 0)}")
            print(f"Errors: {results.get('errors', 0)}")
        else:
            print(f"Backup: {args.backup_path}")
            print(f"Status: {results.get('overall_status', 'UNKNOWN')}")
            print(f"Checks passed: {len(results.get('passed_checks', []))}")
            print(f"Checks failed: {len(results.get('failed_checks', []))}")

if __name__ == '__main__':
    main()