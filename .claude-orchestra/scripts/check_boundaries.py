#!/usr/bin/env python3
"""
Boundary Enforcement Script for Claude Orchestra
Validates if a worker can access a specific file path
"""
import yaml
import sys
import os
from pathlib import Path
import fnmatch
import argparse
from datetime import datetime

def load_boundaries():
    """Load worker boundaries from YAML file"""
    boundaries_file = Path('.claude-orchestra/control/boundaries.yaml')
    if not boundaries_file.exists():
        return None
    
    with open(boundaries_file, 'r') as f:
        return yaml.safe_load(f)

def check_emergency_stop():
    """Check if emergency stop is active"""
    emergency_file = Path('.claude-orchestra/control/emergency-stop.flag')
    return emergency_file.exists()

def normalize_path(filepath):
    """Normalize file path for comparison"""
    return str(Path(filepath).resolve())

def path_matches_pattern(filepath, pattern):
    """Check if file path matches a pattern (supports wildcards)"""
    # Convert to relative path for pattern matching
    try:
        rel_path = str(Path(filepath).relative_to(Path.cwd()))
    except ValueError:
        rel_path = str(Path(filepath))
    
    # Normalize paths - remove trailing slashes
    rel_path = rel_path.rstrip('/')
    pattern = pattern.rstrip('/')
    
    # Handle ** patterns
    if '**' in pattern:
        # For tests/** pattern, allow tests/ and anything under tests/
        base_pattern = pattern.replace('**', '').rstrip('/')
        return rel_path == base_pattern or rel_path.startswith(base_pattern + '/')
    else:
        return fnmatch.fnmatch(rel_path, pattern) or rel_path == pattern

def check_worker_access(worker_id, filepath, boundaries):
    """Check if worker can access the specified file"""
    
    # Check emergency stop first
    if check_emergency_stop():
        return False, "EMERGENCY_STOP_ACTIVE"
    
    # Get worker configuration
    if worker_id not in boundaries:
        return False, f"UNKNOWN_WORKER: {worker_id}"
    
    worker_config = boundaries[worker_id]
    
    # Check global restrictions first
    global_restrictions = boundaries.get('GLOBAL_RESTRICTIONS', {})
    never_touch = global_restrictions.get('never_touch', [])
    
    for forbidden_pattern in never_touch:
        if path_matches_pattern(filepath, forbidden_pattern):
            return False, f"GLOBAL_FORBIDDEN: {forbidden_pattern}"
    
    # Check worker-specific forbidden paths
    forbidden_paths = worker_config.get('forbidden_paths', [])
    for forbidden_pattern in forbidden_paths:
        if path_matches_pattern(filepath, forbidden_pattern):
            return False, f"WORKER_FORBIDDEN: {forbidden_pattern}"
    
    # Check worker-specific allowed paths
    allowed_paths = worker_config.get('allowed_paths', [])
    for allowed_pattern in allowed_paths:
        if path_matches_pattern(filepath, allowed_pattern):
            return True, "ALLOWED"
    
    # If not in allowed paths, deny access
    return False, "NOT_IN_ALLOWED_PATHS"

def log_access_attempt(worker_id, filepath, result, reason):
    """Log access attempt to errors.log if denied"""
    if not result:
        log_dir = Path('.claude-orchestra/logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'errors.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] [BOUNDARY_CHECK] {worker_id} DENIED access to {filepath} - {reason}\n")

def main():
    parser = argparse.ArgumentParser(description='Check worker file access boundaries')
    parser.add_argument('--worker', required=True, help='Worker ID (e.g., WORKER_1)')
    parser.add_argument('filepath', help='File path to check access for')
    
    args = parser.parse_args()
    
    # Load boundaries configuration
    boundaries = load_boundaries()
    if boundaries is None:
        print("ERROR: Could not load boundaries configuration")
        sys.exit(1)
    
    # Check access
    allowed, reason = check_worker_access(args.worker, args.filepath, boundaries)
    
    # Log if denied
    log_access_attempt(args.worker, args.filepath, allowed, reason)
    
    # Output result
    if allowed:
        print("ALLOWED")
        sys.exit(0)
    else:
        print("DENIED")
        print(f"Reason: {reason}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()