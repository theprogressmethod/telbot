#!/usr/bin/env python3
"""
Worker Preparation Script - Claude Orchestra Conductor Automation
WORKER_3 PREP-004A Implementation

This script generates comprehensive worker contexts for task assignment,
loads task details, sets worker boundaries, and manages worker assignments.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
ORCHESTRA_DIR = SCRIPT_DIR.parent
STATUS_DIR = ORCHESTRA_DIR / "status"
CONTROL_DIR = ORCHESTRA_DIR / "control" 
LOGS_DIR = ORCHESTRA_DIR / "logs"
CONTEXTS_DIR = ORCHESTRA_DIR / "contexts"

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m' # No Color

class WorkerPrep:
    """Main class for worker preparation and context generation"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.task_queue = None
        self.worker_boundaries = None
        self.active_worker_status = None
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Load configuration data
        self._load_configurations()
    
    def _print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message if verbose"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        for directory in [STATUS_DIR, CONTROL_DIR, LOGS_DIR, CONTEXTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_configurations(self) -> None:
        """Load task queue, worker boundaries, and status"""
        self._load_task_queue()
        self._load_worker_boundaries()
        self._load_active_worker_status()
    
    def _load_task_queue(self) -> None:
        """Load task queue from markdown file"""
        task_queue_file = STATUS_DIR / "task-queue.md"
        
        if not task_queue_file.exists():
            self._print_colored("Warning: task-queue.md not found", Colors.YELLOW)
            self.task_queue = {"tasks": [], "completed": [], "blocked": []}
            return
        
        try:
            with open(task_queue_file, 'r') as f:
                content = f.read()
            
            # Parse markdown task queue
            self.task_queue = self._parse_task_queue_markdown(content)
            self._print_colored("✅ Task queue loaded successfully", Colors.GREEN)
            
        except Exception as e:
            self._print_colored(f"Error loading task queue: {e}", Colors.RED)
            self.task_queue = {"tasks": [], "completed": [], "blocked": []}
    
    def _parse_task_queue_markdown(self, content: str) -> Dict[str, List[Dict]]:
        """Parse markdown task queue into structured data"""
        tasks = []
        completed = []
        blocked = []
        
        current_section = None
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Identify sections
            if "HIGH PRIORITY" in line:
                current_section = "active"
            elif "BLOCKED TASKS" in line:
                current_section = "blocked"
            elif "COMPLETED TASKS" in line:
                current_section = "completed"
            
            # Parse task categories
            elif line.startswith("### PREP-"):
                current_category = line.split(":")[0].replace("### ", "")
            
            # Parse individual tasks
            elif line.startswith("- ["):
                task_info = self._parse_task_line(line, current_category)
                if task_info:
                    if current_section == "completed" or "✅" in line:
                        completed.append(task_info)
                    elif current_section == "blocked":
                        blocked.append(task_info)
                    else:
                        tasks.append(task_info)
        
        return {
            "tasks": tasks,
            "completed": completed,
            "blocked": blocked
        }
    
    def _parse_task_line(self, line: str, category: str) -> Optional[Dict[str, Any]]:
        """Parse a single task line from markdown"""
        try:
            # Extract status
            if "[✅]" in line:
                status = "completed"
            elif "[ ]" in line:
                status = "pending"
            else:
                status = "unknown"
            
            # Extract task ID and description
            parts = line.split(":", 1)
            if len(parts) < 2:
                return None
            
            task_id_part = parts[0].replace("- [✅]", "").replace("- [ ]", "").strip()
            task_id = task_id_part.split("**")[1] if "**" in task_id_part else task_id_part
            
            description = parts[1].strip()
            
            # Extract worker assignment if present
            worker_assignment = None
            if "WORKER_" in line:
                worker_parts = line.split("WORKER_")
                if len(worker_parts) > 1:
                    worker_assignment = "WORKER_" + worker_parts[1].split()[0]
            
            return {
                "task_id": task_id,
                "description": description,
                "status": status,
                "category": category,
                "worker_assignment": worker_assignment,
                "raw_line": line
            }
            
        except Exception as e:
            self._print_colored(f"Error parsing task line: {line} - {e}", Colors.YELLOW)
            return None
    
    def _load_worker_boundaries(self) -> None:
        """Load worker boundary definitions"""
        boundaries_file = CONTROL_DIR / "worker-boundaries.yaml"
        
        if not boundaries_file.exists():
            # Create default boundaries
            self.worker_boundaries = self._create_default_boundaries()
            self._save_worker_boundaries()
        else:
            try:
                with open(boundaries_file, 'r') as f:
                    self.worker_boundaries = yaml.safe_load(f)
                self._print_colored("✅ Worker boundaries loaded", Colors.GREEN)
            except Exception as e:
                self._print_colored(f"Error loading boundaries: {e}", Colors.RED)
                self.worker_boundaries = self._create_default_boundaries()
    
    def _create_default_boundaries(self) -> Dict[str, Any]:
        """Create default worker boundary definitions"""
        return {
            "WORKER_1": {
                "specialization": "Infrastructure Developer",
                "allowed_paths": [
                    ".claude-orchestra/control/**",
                    ".claude-orchestra/git-safety/**",
                    "config/**",
                    "database/**",
                    "infrastructure/**"
                ],
                "forbidden_paths": [
                    ".env.production",
                    ".env.staging",
                    "production/secrets/**"
                ],
                "environments": ["development", "testing"],
                "responsibilities": [
                    "Environment architecture",
                    "Git safety systems", 
                    "Database infrastructure",
                    "Security implementations"
                ]
            },
            "WORKER_2": {
                "specialization": "Integration Developer", 
                "allowed_paths": [
                    ".claude-orchestra/workflows/**",
                    "api/**",
                    "integrations/**",
                    "webhooks/**",
                    "n8n/**"
                ],
                "forbidden_paths": [
                    ".claude-orchestra/control/**",
                    ".env.production",
                    ".env.staging"
                ],
                "environments": ["development", "testing"],
                "responsibilities": [
                    "n8n workflow automation",
                    "API integrations",
                    "Webhook systems", 
                    "MCP configurations"
                ]
            },
            "WORKER_3": {
                "specialization": "Automation Developer",
                "allowed_paths": [
                    ".claude-orchestra/scripts/**",
                    ".claude-orchestra/automation/**", 
                    ".claude-orchestra/logs/recent-work.log",
                    ".claude-orchestra/status/active-worker.md",
                    "tests/**",
                    "docs/**"
                ],
                "forbidden_paths": [
                    ".claude-orchestra/control/**",
                    ".claude-orchestra/status/task-queue.md",
                    ".env.production",
                    ".env.staging"
                ],
                "environments": ["development", "testing"],
                "responsibilities": [
                    "Conductor automation scripts",
                    "Testing frameworks",
                    "Documentation systems",
                    "Quality assurance tools"
                ]
            }
        }
    
    def _save_worker_boundaries(self) -> None:
        """Save worker boundaries to file"""
        boundaries_file = CONTROL_DIR / "worker-boundaries.yaml"
        try:
            with open(boundaries_file, 'w') as f:
                yaml.dump(self.worker_boundaries, f, default_flow_style=False, indent=2)
            self._print_colored("✅ Worker boundaries saved", Colors.GREEN)
        except Exception as e:
            self._print_colored(f"Error saving boundaries: {e}", Colors.RED)
    
    def _load_active_worker_status(self) -> None:
        """Load current active worker status"""
        status_file = STATUS_DIR / "active-worker.md"
        
        if not status_file.exists():
            self.active_worker_status = {
                "current_worker": "NONE",
                "status": "READY",
                "task": None,
                "phase": "PHASE_0_PREP"
            }
            return
        
        try:
            with open(status_file, 'r') as f:
                content = f.read()
            
            self.active_worker_status = self._parse_worker_status_markdown(content)
            self._print_colored("✅ Active worker status loaded", Colors.GREEN)
            
        except Exception as e:
            self._print_colored(f"Error loading worker status: {e}", Colors.RED)
            self.active_worker_status = {
                "current_worker": "NONE",
                "status": "ERROR",
                "task": None,
                "phase": "UNKNOWN"
            }
    
    def _parse_worker_status_markdown(self, content: str) -> Dict[str, Any]:
        """Parse worker status markdown into structured data"""
        status = {}
        
        for line in content.split('\n'):
            if line.startswith('**CURRENT_WORKER**'):
                status['current_worker'] = line.split(':')[1].strip()
            elif line.startswith('**STATUS**'):
                status['status'] = line.split(':')[1].strip()
            elif line.startswith('**TASK**'):
                status['task'] = line.split(':')[1].strip()
            elif line.startswith('**PHASE**'):
                status['phase'] = line.split(':')[1].strip()
        
        return status
    
    def generate_worker_context(self, worker_id: str, task_id: str) -> Dict[str, Any]:
        """Generate comprehensive context for a worker assignment"""
        
        # Find the specific task
        task_details = self._find_task_details(task_id)
        if not task_details:
            raise ValueError(f"Task {task_id} not found in task queue")
        
        # Get worker boundary information
        worker_boundaries = self.worker_boundaries.get(worker_id, {})
        
        # Generate context
        context = {
            "worker_id": worker_id,
            "task_assignment": {
                "task_id": task_id,
                "description": task_details.get("description", ""),
                "category": task_details.get("category", ""),
                "status": task_details.get("status", "pending"),
                "assigned_timestamp": datetime.now().isoformat(),
                "deadline": "Current session completion",
                "dependencies": self._get_task_dependencies(task_id)
            },
            "worker_profile": {
                "specialization": worker_boundaries.get("specialization", "General"),
                "responsibilities": worker_boundaries.get("responsibilities", []),
                "environments": worker_boundaries.get("environments", ["development"]),
                "primary_language": worker_boundaries.get("primary_language", "Python")
            },
            "boundaries": {
                "allowed_paths": worker_boundaries.get("allowed_paths", []),
                "forbidden_paths": worker_boundaries.get("forbidden_paths", []),
                "environment_restrictions": worker_boundaries.get("environments", ["development"]),
                "boundary_check_script": ".claude-orchestra/scripts/check_boundaries.py"
            },
            "workspace": {
                "working_directory": str(ORCHESTRA_DIR.parent),
                "scripts_directory": str(SCRIPT_DIR),
                "logs_directory": str(LOGS_DIR),
                "status_directory": str(STATUS_DIR)
            },
            "tools_and_access": {
                "git_operations": ["add", "commit", "pull", "push"],
                "allowed_branches": ["development", f"feature/{task_id.lower()}-*"],
                "forbidden_branches": ["main", "staging", "production"],
                "testing_framework": "Python script validation",
                "apis_available": ["GitHub (limited)", "File system operations"]
            },
            "reporting_requirements": {
                "log_file": ".claude-orchestra/logs/recent-work.log",
                "log_format": "[TIMESTAMP] {worker_id} [ACTION]: Details",
                "update_frequency": "Every work session",
                "required_logs": ["work session start/end", "files modified", "tests run", "blockers encountered"]
            },
            "success_criteria": self._get_success_criteria(task_id),
            "emergency_procedures": {
                "emergency_stop_check": ".claude-orchestra/control/emergency-stop.flag",
                "boundary_violation_action": "STOP immediately and log",
                "unclear_task_action": "Report and wait for guidance",
                "blocker_reporting": "Log to recent-work.log and stop"
            },
            "context_generation": {
                "generated_by": "worker_prep.py",
                "generated_at": datetime.now().isoformat(),
                "conductor_version": "1.0",
                "context_version": "1.0"
            }
        }
        
        return context
    
    def _find_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Find task details by task ID"""
        all_tasks = (self.task_queue.get("tasks", []) + 
                    self.task_queue.get("completed", []) + 
                    self.task_queue.get("blocked", []))
        
        for task in all_tasks:
            if task.get("task_id") == task_id:
                return task
        
        return None
    
    def _get_task_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies for a specific task"""
        # Basic dependency mapping based on task patterns
        dependencies_map = {
            "PREP-001A": [],
            "PREP-001B": ["PREP-001A"],
            "PREP-001C": ["PREP-001A"],
            "PREP-001D": ["PREP-001A", "PREP-001B", "PREP-001C"],
            "PREP-002A": ["PREP-001A"],
            "PREP-002B": ["PREP-002A"],
            "PREP-003A": ["PREP-001A"],
            "PREP-004A": ["PREP-001A", "PREP-001B", "PREP-001C"],
            "PREP-004B": ["PREP-004A"],
            "PREP-004C": ["PREP-004A"],
            "PREP-004D": ["PREP-004A"],
            "PREP-004E": ["PREP-004A"],
            "PREP-005A": ["PREP-004A"],
            "PREP-006A": ["PREP-001A", "PREP-002A", "PREP-003A", "PREP-004A"]
        }
        
        return dependencies_map.get(task_id, [])
    
    def _get_success_criteria(self, task_id: str) -> List[str]:
        """Get success criteria for specific tasks"""
        criteria_map = {
            "PREP-004A": [
                "worker_prep.py script created with full CLI interface",
                "Context generation working for all worker types", 
                "Integration with task queue and boundaries",
                "Logging to orchestration system",
                "Comprehensive error handling"
            ],
            "PREP-004B": [
                "review_work.py script validates task completion",
                "Boundary compliance checking implemented",
                "Code quality analysis working",
                "Review report generation functional",
                "Integration with orchestration logging"
            ],
            "PREP-004C": [
                "deploy_gate.py performs environment validation",
                "Code quality gates implemented",
                "Worker boundary compliance verification",
                "Orchestration state validation",
                "JSON output for automation integration"
            ],
            "PREP-004D": [
                "emergency_stop.py halts all operations",
                "System state backup and capture",
                "Worker coordination during emergencies",
                "Emergency deactivation with authorization",
                "Recovery procedure guidance"
            ],
            "PREP-004E": [
                "progress_report.py generates comprehensive summaries",
                "Worker performance analytics",
                "System health monitoring",
                "Task completion tracking",
                "Multiple output formats (JSON/text)"
            ]
        }
        
        return criteria_map.get(task_id, ["Complete implementation", "Full testing", "Documentation"])
    
    def save_worker_context(self, worker_id: str, task_id: str, context: Dict[str, Any]) -> str:
        """Save worker context to file"""
        context_filename = f"{worker_id}_{task_id}_context.json"
        context_file = CONTEXTS_DIR / context_filename
        
        try:
            with open(context_file, 'w') as f:
                json.dump(context, f, indent=2, default=str)
            
            self._print_colored(f"✅ Context saved: {context_filename}", Colors.GREEN)
            return str(context_file)
            
        except Exception as e:
            self._print_colored(f"Error saving context: {e}", Colors.RED)
            raise
    
    def assign_worker_to_task(self, worker_id: str, task_id: str) -> bool:
        """Assign a worker to a specific task and update status"""
        try:
            # Generate and save context
            context = self.generate_worker_context(worker_id, task_id)
            context_file = self.save_worker_context(worker_id, task_id, context)
            
            # Update active worker status
            self._update_active_worker_status(worker_id, task_id)
            
            # Log the assignment
            self._log_worker_assignment(worker_id, task_id, context_file)
            
            self._print_colored(f"✅ {worker_id} assigned to {task_id}", Colors.GREEN)
            return True
            
        except Exception as e:
            self._print_colored(f"Error assigning worker: {e}", Colors.RED)
            return False
    
    def _update_active_worker_status(self, worker_id: str, task_id: str) -> None:
        """Update the active worker status file"""
        status_file = STATUS_DIR / "active-worker.md"
        
        status_content = f"""# ACTIVE WORKER STATUS

**CURRENT_WORKER**: {worker_id}
**STATUS**: ASSIGNED  
**TASK**: {task_id}
**PHASE**: PHASE_0_PREP
**LAST_UPDATED**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Worker Status for PHASE 0 INFRASTRUCTURE
- **WORKER_1**: Infrastructure Developer (Ready)
- **WORKER_2**: Integration Developer (Ready)  
- **WORKER_3**: Automation Developer (Currently Active - {task_id})

## PHASE 0 Assignment Strategy
Each worker will build orchestration infrastructure:
- WORKER_1: Environment architecture, Git safety, database infrastructure
- WORKER_2: n8n workflows, API integrations, webhook systems  
- WORKER_3: Automation scripts, documentation, testing frameworks

---
*Emergency stop deactivated - workers can proceed with PHASE 0 PREP tasks*
"""
        
        try:
            with open(status_file, 'w') as f:
                f.write(status_content)
            self._print_colored("✅ Active worker status updated", Colors.GREEN)
        except Exception as e:
            self._print_colored(f"Error updating worker status: {e}", Colors.RED)
    
    def _log_worker_assignment(self, worker_id: str, task_id: str, context_file: str) -> None:
        """Log worker assignment to orchestration log"""
        log_file = LOGS_DIR / "orchestration.log"
        
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] WORKER_ASSIGNMENT: {worker_id} assigned to {task_id}\n")
                f.write(f"  Context file: {context_file}\n")
                f.write(f"  Generated by: worker_prep.py\n")
                f.write(f"  Assignment timestamp: {timestamp}\n")
                f.write(f"---\n")
            
            self._print_colored("✅ Assignment logged to orchestration.log", Colors.GREEN)
        except Exception as e:
            self._print_colored(f"Error logging assignment: {e}", Colors.RED)
    
    def list_available_tasks(self) -> List[Dict[str, Any]]:
        """List all available (pending) tasks"""
        return [task for task in self.task_queue.get("tasks", []) 
                if task.get("status") == "pending"]
    
    def list_available_workers(self) -> List[str]:
        """List all defined workers"""
        return list(self.worker_boundaries.keys())
    
    def show_worker_profile(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Show detailed worker profile"""
        return self.worker_boundaries.get(worker_id)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Worker Preparation and Context Generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Assign command
    assign_parser = subparsers.add_parser("assign", help="Assign worker to task")
    assign_parser.add_argument("worker_id", help="Worker ID (e.g., WORKER_1)")
    assign_parser.add_argument("task_id", help="Task ID (e.g., PREP-004A)")
    
    # List commands  
    list_parser = subparsers.add_parser("list", help="List tasks or workers")
    list_parser.add_argument("type", choices=["tasks", "workers"], help="What to list")
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Show worker profile")
    profile_parser.add_argument("worker_id", help="Worker ID")
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Generate context only")
    context_parser.add_argument("worker_id", help="Worker ID")
    context_parser.add_argument("task_id", help="Task ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize worker prep system
    prep = WorkerPrep(verbose=args.verbose)
    
    try:
        if args.command == "assign":
            success = prep.assign_worker_to_task(args.worker_id, args.task_id)
            return 0 if success else 1
            
        elif args.command == "list":
            if args.type == "tasks":
                tasks = prep.list_available_tasks()
                if args.verbose:
                    print(f"{Colors.BLUE}📋 Available Tasks:{Colors.NC}")
                for task in tasks:
                    print(f"  • {task['task_id']}: {task['description']}")
                    if args.verbose:
                        print(f"    Category: {task['category']}")
                        print(f"    Status: {task['status']}")
                        print()
            else:  # workers
                workers = prep.list_available_workers()
                if args.verbose:
                    print(f"{Colors.BLUE}👥 Available Workers:{Colors.NC}")
                for worker_id in workers:
                    profile = prep.show_worker_profile(worker_id)
                    print(f"  • {worker_id}: {profile.get('specialization', 'Unknown')}")
                    if args.verbose:
                        print(f"    Responsibilities: {', '.join(profile.get('responsibilities', []))}")
                        print()
                        
        elif args.command == "profile":
            profile = prep.show_worker_profile(args.worker_id)
            if profile:
                print(f"{Colors.BLUE}👤 Worker Profile: {args.worker_id}{Colors.NC}")
                print(f"Specialization: {profile.get('specialization', 'Unknown')}")
                print(f"Environments: {', '.join(profile.get('environments', []))}")
                print("Responsibilities:")
                for resp in profile.get('responsibilities', []):
                    print(f"  • {resp}")
                print("Allowed paths:")
                for path in profile.get('allowed_paths', []):
                    print(f"  • {path}")
            else:
                print(f"{Colors.RED}❌ Worker {args.worker_id} not found{Colors.NC}")
                return 1
                
        elif args.command == "context":
            context = prep.generate_worker_context(args.worker_id, args.task_id)
            context_file = prep.save_worker_context(args.worker_id, args.task_id, context)
            print(f"{Colors.GREEN}✅ Context generated: {context_file}{Colors.NC}")
            
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())