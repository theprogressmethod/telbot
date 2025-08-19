#!/usr/bin/env python3
"""
Database Connection Validator
Connection string validation and security checking

Part of The Progress Method v1.0 - Phase 0 Prep
WORKER_1 PREP-001D: Database Safety Infrastructure
"""

import re
import json
import logging
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

class ConnectionValidator:
    """Database connection string validation and security checking"""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for connection validation"""
        logger = logging.getLogger('connection_validator')
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def validate_connection_string(self, connection_string: str, environment: str = 'development') -> Tuple[bool, Dict]:
        """Comprehensive connection string validation"""
        result = {
            'connection_string': connection_string[:20] + '...' if len(connection_string) > 20 else connection_string,
            'environment': environment,
            'is_valid': False,
            'security_score': 0,
            'issues': [],
            'recommendations': [],
            'parsed_components': {}
        }
        
        try:
            # Parse connection string
            parsed = self._parse_connection_string(connection_string)
            result['parsed_components'] = parsed
            
            # Security validations
            security_checks = [
                self._check_ssl_requirement(parsed, environment),
                self._check_credential_security(parsed, environment),
                self._check_host_validation(parsed, environment),
                self._check_port_security(parsed, environment)
            ]
            
            passed_checks = sum(1 for check in security_checks if check['passed'])
            result['security_score'] = int((passed_checks / len(security_checks)) * 100)
            
            # Collect issues and recommendations
            for check in security_checks:
                if not check['passed']:
                    result['issues'].extend(check.get('issues', []))
                result['recommendations'].extend(check.get('recommendations', []))
            
            result['is_valid'] = result['security_score'] >= 70
            
            return result['is_valid'], result
            
        except Exception as e:
            result['error'] = str(e)
            return False, result
    
    def _parse_connection_string(self, connection_string: str) -> Dict:
        """Parse database connection string"""
        # Handle different connection string formats
        if connection_string.startswith('postgresql://') or connection_string.startswith('postgres://'):
            return self._parse_postgres_url(connection_string)
        elif '=' in connection_string:
            return self._parse_key_value_format(connection_string)
        else:
            raise ValueError("Unsupported connection string format")
    
    def _parse_postgres_url(self, url: str) -> Dict:
        """Parse PostgreSQL URL format"""
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'username': parsed.username,
            'password': '***' if parsed.password else None,
            'host': parsed.hostname,
            'port': parsed.port,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'ssl_mode': dict(param.split('=') for param in (parsed.query.split('&') if parsed.query else [])).get('sslmode', 'prefer')
        }
    
    def _parse_key_value_format(self, connection_string: str) -> Dict:
        """Parse key=value connection string format"""
        parsed = {}
        pairs = connection_string.split()
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                if key.lower() == 'password':
                    parsed[key] = '***'
                else:
                    parsed[key] = value
        return parsed
    
    def _check_ssl_requirement(self, parsed: Dict, environment: str) -> Dict:
        """Check SSL/TLS requirements"""
        ssl_mode = parsed.get('ssl_mode', parsed.get('sslmode', 'prefer'))
        
        if environment == 'production':
            if ssl_mode not in ['require', 'verify-ca', 'verify-full']:
                return {
                    'passed': False,
                    'issues': ['SSL is not required for production environment'],
                    'recommendations': ['Set sslmode=require or higher for production']
                }
        
        return {'passed': True, 'recommendations': ['SSL configuration looks good']}
    
    def _check_credential_security(self, parsed: Dict, environment: str) -> Dict:
        """Check credential security"""
        issues = []
        recommendations = []
        
        # Check for weak usernames
        username = parsed.get('username', parsed.get('user', ''))
        if username in ['root', 'admin', 'sa', 'postgres']:
            issues.append(f'Using privileged username: {username}')
            recommendations.append('Use dedicated application user instead of admin accounts')
        
        # Check host security
        host = parsed.get('host', parsed.get('hostname', ''))
        if host in ['localhost', '127.0.0.1'] and environment != 'development':
            issues.append('Using localhost in non-development environment')
            recommendations.append('Use proper hostname for non-development environments')
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _check_host_validation(self, parsed: Dict, environment: str) -> Dict:
        """Validate host configuration"""
        host = parsed.get('host', parsed.get('hostname', ''))
        
        if not host:
            return {
                'passed': False,
                'issues': ['No host specified'],
                'recommendations': ['Specify database host']
            }
        
        # Check for localhost in production
        if environment == 'production' and host in ['localhost', '127.0.0.1']:
            return {
                'passed': False,
                'issues': ['Localhost not allowed in production'],
                'recommendations': ['Use production database hostname']
            }
        
        return {'passed': True}
    
    def _check_port_security(self, parsed: Dict, environment: str) -> Dict:
        """Check port configuration"""
        port = parsed.get('port')
        
        if port:
            try:
                port_num = int(port)
                if port_num == 5432 and environment == 'production':
                    return {
                        'passed': True,
                        'recommendations': ['Consider using non-standard port for production']
                    }
            except ValueError:
                return {
                    'passed': False,
                    'issues': ['Invalid port number'],
                    'recommendations': ['Use valid numeric port']
                }
        
        return {'passed': True}

def main():
    """Main function for testing"""
    validator = ConnectionValidator()
    
    # Test connection strings
    test_connections = [
        "postgresql://user:pass@localhost:5432/dbname?sslmode=require",
        "host=localhost port=5432 dbname=test user=postgres password=secret sslmode=prefer"
    ]
    
    for conn_str in test_connections:
        is_valid, result = validator.validate_connection_string(conn_str, 'development')
        print(f"Connection: {result['connection_string']}")
        print(f"Valid: {is_valid}")
        print(f"Security Score: {result['security_score']}")
        if result.get('issues'):
            print(f"Issues: {result['issues']}")
        print("---")

if __name__ == '__main__':
    main()