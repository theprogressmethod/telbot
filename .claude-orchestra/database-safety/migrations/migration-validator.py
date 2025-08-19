#!/usr/bin/env python3
"""
Database Migration Validator
Pre-migration safety checks, syntax validation, and impact analysis

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import os
import sys
import re
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import yaml

class MigrationValidator:
    """Comprehensive migration validation and safety checking"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_config_path()
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
    def _get_config_path(self) -> str:
        """Get configuration file path"""
        base_path = Path(__file__).parent.parent
        return str(base_path / 'config' / 'migration-config.yaml')
    
    def _load_config(self) -> Dict:
        """Load migration validation configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default migration validation configuration"""
        return {
            'validation_rules': {
                'require_rollback_script': True,
                'require_impact_assessment': True,
                'check_syntax': True,
                'validate_dependencies': True,
                'check_destructive_operations': True,
                'require_backup_before_migration': True
            },
            'destructive_operations': [
                'DROP TABLE',
                'DROP COLUMN',
                'DROP INDEX',
                'TRUNCATE',
                'DELETE FROM',
                'ALTER TABLE.*DROP'
            ],
            'required_patterns': {
                'begin_transaction': r'BEGIN\s*;|START\s+TRANSACTION\s*;',
                'commit_transaction': r'COMMIT\s*;',
                'rollback_available': r'ROLLBACK\s*;'
            },
            'environments': {
                'development': {
                    'strict_validation': False,
                    'allow_destructive': True,
                    'require_approval': False
                },
                'staging': {
                    'strict_validation': True,
                    'allow_destructive': True,
                    'require_approval': True
                },
                'production': {
                    'strict_validation': True,
                    'allow_destructive': False,
                    'require_approval': True
                }
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for migration validation"""
        logger = logging.getLogger('migration_validator')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / 'migration-validation.log'
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
    
    def validate_migration(self, migration_file: str, environment: str = 'development') -> Tuple[bool, Dict]:
        """Comprehensive migration validation"""
        migration_path = Path(migration_file)
        
        validation_result = {
            'migration_file': migration_file,
            'environment': environment,
            'validation_time': datetime.now().isoformat(),
            'checks_performed': [],
            'passed_checks': [],
            'failed_checks': [],
            'warnings': [],
            'overall_status': 'PENDING',
            'risk_level': 'UNKNOWN',
            'recommendations': []
        }
        
        try:
            self.logger.info(f"Starting migration validation: {migration_file} for {environment}")
            
            # Check 1: File existence and readability
            file_check = self._check_file_existence(migration_path)
            validation_result['checks_performed'].append('file_existence')
            if file_check['passed']:
                validation_result['passed_checks'].append('file_existence')
            else:
                validation_result['failed_checks'].append('file_existence')
                validation_result['recommendations'].extend(file_check.get('recommendations', []))
            
            if not file_check['passed']:
                validation_result['overall_status'] = 'FAILED'
                return False, validation_result
            
            # Read migration content
            migration_content = self._read_migration_file(migration_path)
            
            # Check 2: Syntax validation
            if self.config['validation_rules'].get('check_syntax', True):
                syntax_check = self._check_sql_syntax(migration_content)
                validation_result['checks_performed'].append('syntax_validation')
                if syntax_check['passed']:
                    validation_result['passed_checks'].append('syntax_validation')
                else:
                    validation_result['failed_checks'].append('syntax_validation')
                    validation_result['recommendations'].extend(syntax_check.get('recommendations', []))
            
            # Check 3: Destructive operations
            if self.config['validation_rules'].get('check_destructive_operations', True):
                destructive_check = self._check_destructive_operations(migration_content, environment)
                validation_result['checks_performed'].append('destructive_operations')
                if destructive_check['passed']:
                    validation_result['passed_checks'].append('destructive_operations')
                else:
                    validation_result['failed_checks'].append('destructive_operations')
                validation_result['warnings'].extend(destructive_check.get('warnings', []))
                validation_result['recommendations'].extend(destructive_check.get('recommendations', []))
            
            # Check 4: Transaction handling
            transaction_check = self._check_transaction_handling(migration_content)
            validation_result['checks_performed'].append('transaction_handling')
            if transaction_check['passed']:
                validation_result['passed_checks'].append('transaction_handling')
            else:
                validation_result['failed_checks'].append('transaction_handling')
                validation_result['recommendations'].extend(transaction_check.get('recommendations', []))
            
            # Check 5: Rollback script availability
            if self.config['validation_rules'].get('require_rollback_script', True):
                rollback_check = self._check_rollback_script(migration_path)
                validation_result['checks_performed'].append('rollback_script')
                if rollback_check['passed']:
                    validation_result['passed_checks'].append('rollback_script')
                else:
                    validation_result['failed_checks'].append('rollback_script')
                    validation_result['recommendations'].extend(rollback_check.get('recommendations', []))
            
            # Check 6: Environment-specific validation
            env_check = self._check_environment_requirements(migration_content, environment)
            validation_result['checks_performed'].append('environment_requirements')
            if env_check['passed']:
                validation_result['passed_checks'].append('environment_requirements')
            else:
                validation_result['failed_checks'].append('environment_requirements')
                validation_result['recommendations'].extend(env_check.get('recommendations', []))
            
            # Check 7: Impact assessment
            if self.config['validation_rules'].get('require_impact_assessment', True):
                impact_assessment = self._assess_migration_impact(migration_content)
                validation_result['impact_assessment'] = impact_assessment
                validation_result['risk_level'] = impact_assessment.get('risk_level', 'MEDIUM')
            
            # Determine overall status
            env_config = self.config['environments'].get(environment, {})
            strict_validation = env_config.get('strict_validation', False)
            
            if strict_validation and validation_result['failed_checks']:
                validation_result['overall_status'] = 'FAILED'
            elif validation_result['failed_checks']:
                validation_result['overall_status'] = 'WARNING'
            else:
                validation_result['overall_status'] = 'PASSED'
            
            # Log validation result
            self._log_validation_result(validation_result)
            
            return validation_result['overall_status'] in ['PASSED', 'WARNING'], validation_result
            
        except Exception as e:
            self.logger.error(f"Migration validation failed with exception: {e}")
            validation_result['overall_status'] = 'ERROR'
            validation_result['error'] = str(e)
            return False, validation_result
    
    def _check_file_existence(self, migration_path: Path) -> Dict:
        """Check if migration file exists and is readable"""
        try:
            if not migration_path.exists():
                return {
                    'passed': False,
                    'message': 'Migration file does not exist',
                    'recommendations': ['Check file path', 'Ensure file was created correctly']
                }
            
            if not migration_path.is_file():
                return {
                    'passed': False,
                    'message': 'Path is not a regular file',
                    'recommendations': ['Check if path points to correct file']
                }
            
            # Check if file is readable
            try:
                with open(migration_path, 'r') as f:
                    f.read(1)
            except PermissionError:
                return {
                    'passed': False,
                    'message': 'File is not readable',
                    'recommendations': ['Check file permissions']
                }
            
            return {
                'passed': True,
                'message': 'File exists and is readable',
                'file_size': migration_path.stat().st_size
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'File check failed: {e}',
                'recommendations': ['Investigate file system issues']
            }
    
    def _read_migration_file(self, migration_path: Path) -> str:
        """Read migration file content"""
        try:
            with open(migration_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(migration_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _check_sql_syntax(self, migration_content: str) -> Dict:
        """Basic SQL syntax validation"""
        try:
            issues = []
            
            # Check for balanced parentheses
            paren_count = migration_content.count('(') - migration_content.count(')')
            if paren_count != 0:
                issues.append(f"Unbalanced parentheses: {paren_count} extra {'(' if paren_count > 0 else ')'}")
            
            # Check for balanced quotes
            single_quotes = migration_content.count("'")
            if single_quotes % 2 != 0:
                issues.append("Unbalanced single quotes")
            
            double_quotes = migration_content.count('"')
            if double_quotes % 2 != 0:
                issues.append("Unbalanced double quotes")
            
            # Check for common SQL keywords
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
            has_sql = any(keyword in migration_content.upper() for keyword in sql_keywords)
            
            if not has_sql:
                issues.append("No recognizable SQL statements found")
            
            # Check for proper statement termination
            statements = [s.strip() for s in migration_content.split(';') if s.strip()]
            for i, statement in enumerate(statements[:-1]):  # Skip last (empty after final ;)
                if not statement.strip():
                    continue
                # Each statement should end with semicolon (except the last one which we split on)
                if not any(keyword in statement.upper() for keyword in sql_keywords):
                    issues.append(f"Statement {i+1} may not be valid SQL")
            
            if issues:
                return {
                    'passed': False,
                    'message': 'Syntax issues found',
                    'issues': issues,
                    'recommendations': ['Review SQL syntax', 'Test in development environment']
                }
            
            return {
                'passed': True,
                'message': 'Basic syntax validation passed',
                'statement_count': len(statements)
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Syntax check failed: {e}',
                'recommendations': ['Check file encoding and content']
            }
    
    def _check_destructive_operations(self, migration_content: str, environment: str) -> Dict:
        """Check for potentially destructive operations"""
        try:
            destructive_patterns = self.config.get('destructive_operations', [])
            env_config = self.config['environments'].get(environment, {})
            allow_destructive = env_config.get('allow_destructive', True)
            
            found_operations = []
            warnings = []
            
            content_upper = migration_content.upper()
            
            for pattern in destructive_patterns:
                matches = re.findall(pattern, content_upper, re.IGNORECASE)
                if matches:
                    found_operations.extend(matches)
            
            if found_operations:
                if not allow_destructive:
                    return {
                        'passed': False,
                        'message': f'Destructive operations not allowed in {environment}',
                        'found_operations': found_operations,
                        'recommendations': [
                            f'Remove destructive operations for {environment}',
                            'Consider alternative approaches',
                            'Test in development first'
                        ]
                    }
                else:
                    warnings.append(f'Destructive operations found: {len(found_operations)}')
                    return {
                        'passed': True,
                        'message': 'Destructive operations allowed but flagged',
                        'found_operations': found_operations,
                        'warnings': warnings,
                        'recommendations': [
                            'Ensure backup exists before running',
                            'Test rollback procedures',
                            'Consider maintenance window'
                        ]
                    }
            
            return {
                'passed': True,
                'message': 'No destructive operations found'
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Destructive operations check failed: {e}',
                'recommendations': ['Review migration content manually']
            }
    
    def _check_transaction_handling(self, migration_content: str) -> Dict:
        """Check for proper transaction handling"""
        try:
            required_patterns = self.config.get('required_patterns', {})
            content_upper = migration_content.upper()
            
            issues = []
            recommendations = []
            
            # Check for transaction begin
            begin_pattern = required_patterns.get('begin_transaction', r'BEGIN\s*;')
            if not re.search(begin_pattern, content_upper):
                issues.append('No transaction BEGIN found')
                recommendations.append('Add BEGIN; at start of migration')
            
            # Check for commit
            commit_pattern = required_patterns.get('commit_transaction', r'COMMIT\s*;')
            if not re.search(commit_pattern, content_upper):
                issues.append('No COMMIT statement found')
                recommendations.append('Add COMMIT; at end of migration')
            
            # Check statement order
            begin_pos = content_upper.find('BEGIN')
            commit_pos = content_upper.find('COMMIT')
            
            if begin_pos >= 0 and commit_pos >= 0 and begin_pos > commit_pos:
                issues.append('COMMIT appears before BEGIN')
                recommendations.append('Ensure proper transaction order: BEGIN...COMMIT')
            
            if issues:
                return {
                    'passed': False,
                    'message': 'Transaction handling issues found',
                    'issues': issues,
                    'recommendations': recommendations
                }
            
            return {
                'passed': True,
                'message': 'Transaction handling appears correct'
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Transaction check failed: {e}',
                'recommendations': ['Review transaction structure manually']
            }
    
    def _check_rollback_script(self, migration_path: Path) -> Dict:
        """Check for corresponding rollback script"""
        try:
            # Look for rollback script in same directory
            migration_dir = migration_path.parent
            migration_name = migration_path.stem
            
            # Common rollback naming patterns
            rollback_patterns = [
                f"{migration_name}_rollback.sql",
                f"{migration_name}.rollback.sql",
                f"rollback_{migration_name}.sql",
                f"{migration_name}_down.sql"
            ]
            
            rollback_files = []
            for pattern in rollback_patterns:
                rollback_path = migration_dir / pattern
                if rollback_path.exists():
                    rollback_files.append(str(rollback_path))
            
            if not rollback_files:
                return {
                    'passed': False,
                    'message': 'No rollback script found',
                    'expected_names': rollback_patterns,
                    'recommendations': [
                        'Create corresponding rollback script',
                        'Use naming convention: {migration}_rollback.sql',
                        'Test rollback procedure'
                    ]
                }
            
            # Validate rollback script content
            rollback_path = Path(rollback_files[0])
            try:
                with open(rollback_path, 'r') as f:
                    rollback_content = f.read()
                
                if len(rollback_content.strip()) < 10:
                    return {
                        'passed': False,
                        'message': 'Rollback script appears empty or too short',
                        'rollback_files': rollback_files,
                        'recommendations': [
                            'Add proper rollback statements',
                            'Ensure rollback undoes migration changes'
                        ]
                    }
                
            except Exception as e:
                return {
                    'passed': False,
                    'message': f'Cannot read rollback script: {e}',
                    'rollback_files': rollback_files,
                    'recommendations': ['Check rollback file permissions and content']
                }
            
            return {
                'passed': True,
                'message': 'Rollback script found and appears valid',
                'rollback_files': rollback_files
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Rollback check failed: {e}',
                'recommendations': ['Manually verify rollback script exists']
            }
    
    def _check_environment_requirements(self, migration_content: str, environment: str) -> Dict:
        """Check environment-specific requirements"""
        try:
            env_config = self.config['environments'].get(environment, {})
            issues = []
            recommendations = []
            
            # Check if approval is required
            if env_config.get('require_approval', False):
                # Look for approval marker in migration
                if '-- APPROVED' not in migration_content.upper():
                    issues.append(f'Migration requires approval for {environment}')
                    recommendations.append('Add approval marker: -- APPROVED by [name] on [date]')
            
            # Environment-specific checks can be added here
            if environment == 'production':
                # Extra strict checks for production
                if 'TRUNCATE' in migration_content.upper():
                    issues.append('TRUNCATE operations discouraged in production')
                    recommendations.append('Consider DELETE with WHERE clause instead')
            
            if issues:
                return {
                    'passed': False,
                    'message': f'Environment requirements not met for {environment}',
                    'issues': issues,
                    'recommendations': recommendations
                }
            
            return {
                'passed': True,
                'message': f'Environment requirements satisfied for {environment}'
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Environment check failed: {e}',
                'recommendations': ['Review environment configuration']
            }
    
    def _assess_migration_impact(self, migration_content: str) -> Dict:
        """Assess potential impact of migration"""
        try:
            impact_assessment = {
                'risk_level': 'LOW',
                'estimated_downtime': 'MINIMAL',
                'affected_tables': [],
                'affected_columns': [],
                'data_changes': False,
                'schema_changes': False,
                'index_changes': False
            }
            
            content_upper = migration_content.upper()
            
            # Detect table operations
            table_matches = re.findall(r'(?:CREATE|ALTER|DROP)\s+TABLE\s+(\w+)', content_upper)
            impact_assessment['affected_tables'] = list(set(table_matches))
            
            # Detect column operations
            column_matches = re.findall(r'(?:ADD|DROP|ALTER)\s+COLUMN\s+(\w+)', content_upper)
            impact_assessment['affected_columns'] = list(set(column_matches))
            
            # Check for schema changes
            schema_operations = ['CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'CREATE INDEX', 'DROP INDEX']
            if any(op in content_upper for op in schema_operations):
                impact_assessment['schema_changes'] = True
            
            # Check for data changes
            data_operations = ['INSERT', 'UPDATE', 'DELETE', 'TRUNCATE']
            if any(op in content_upper for op in data_operations):
                impact_assessment['data_changes'] = True
            
            # Check for index changes
            index_operations = ['CREATE INDEX', 'DROP INDEX', 'REINDEX']
            if any(op in content_upper for op in index_operations):
                impact_assessment['index_changes'] = True
            
            # Assess risk level
            risk_factors = 0
            
            if 'DROP TABLE' in content_upper:
                risk_factors += 3
            if 'DROP COLUMN' in content_upper:
                risk_factors += 2
            if 'TRUNCATE' in content_upper or 'DELETE FROM' in content_upper:
                risk_factors += 2
            if len(impact_assessment['affected_tables']) > 5:
                risk_factors += 1
            if impact_assessment['data_changes']:
                risk_factors += 1
            
            if risk_factors >= 4:
                impact_assessment['risk_level'] = 'HIGH'
                impact_assessment['estimated_downtime'] = 'SIGNIFICANT'
            elif risk_factors >= 2:
                impact_assessment['risk_level'] = 'MEDIUM'
                impact_assessment['estimated_downtime'] = 'MODERATE'
            else:
                impact_assessment['risk_level'] = 'LOW'
                impact_assessment['estimated_downtime'] = 'MINIMAL'
            
            return impact_assessment
            
        except Exception as e:
            return {
                'risk_level': 'UNKNOWN',
                'error': f'Impact assessment failed: {e}'
            }
    
    def _log_validation_result(self, result: Dict):
        """Log validation result to orchestration system"""
        try:
            # Log to validation-specific log
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            validation_log = log_dir / 'migration-validation-history.json'
            
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
            
            # Keep only recent validations (last 100)
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            with open(validation_log, 'w') as f:
                json.dump(history, f, indent=2)
                
            # Log to orchestration log
            orchestration_log = log_dir / 'orchestration.log'
            status = result['overall_status']
            migration_file = result['migration_file']
            environment = result['environment']
            with open(orchestration_log, 'a') as f:
                log_entry = f"[{datetime.now().isoformat()}] [MIGRATION_VALIDATION] [{status}] {environment}: {migration_file}"
                f.write(log_entry + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log validation result: {e}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Validator')
    parser.add_argument('migration_file', help='Path to migration file')
    parser.add_argument('--environment', default='development',
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary',
                       help='Output format')
    
    args = parser.parse_args()
    
    validator = MigrationValidator()
    is_valid, results = validator.validate_migration(args.migration_file, args.environment)
    
    if args.output == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Summary output
        print(f"Migration: {args.migration_file}")
        print(f"Environment: {args.environment}")
        print(f"Status: {results.get('overall_status', 'UNKNOWN')}")
        print(f"Risk Level: {results.get('risk_level', 'UNKNOWN')}")
        print(f"Checks passed: {len(results.get('passed_checks', []))}")
        print(f"Checks failed: {len(results.get('failed_checks', []))}")
        
        if results.get('warnings'):
            print(f"\nWarnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        if results.get('recommendations'):
            print(f"\nRecommendations:")
            for rec in results['recommendations']:
                print(f"  - {rec}")
    
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()