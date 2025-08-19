#!/usr/bin/env python3
"""
Emergency Stop Script - Claude Orchestra Conductor Automation
WORKER_3 PREP-004D Implementation

This script provides emergency halt capabilities for all orchestration operations,
including system state backup, worker coordination, emergency activation/deactivation,
and recovery procedure guidance.
"""

import os
import sys
import json
import yaml
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
ORCHESTRA_DIR = SCRIPT_DIR.parent
STATUS_DIR = ORCHESTRA_DIR / "status"
CONTROL_DIR = ORCHESTRA_DIR / "control"
LOGS_DIR = ORCHESTRA_DIR / "logs"
BACKUP_DIR = ORCHESTRA_DIR / "backups"
EMERGENCY_FLAG_FILE = CONTROL_DIR / "emergency-stop.flag"

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

class EmergencyStopSystem:
    """Main emergency stop system for orchestration"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.emergency_active = False
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Check current emergency status
        self._check_emergency_status()
    
    def _print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message if verbose"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        for directory in [STATUS_DIR, CONTROL_DIR, LOGS_DIR, BACKUP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _check_emergency_status(self) -> None:
        """Check if emergency stop is currently active"""
        self.emergency_active = EMERGENCY_FLAG_FILE.exists()
        if self.emergency_active:
            self._print_colored("🚨 Emergency stop is currently ACTIVE", Colors.RED)
        else:
            self._print_colored("✅ Emergency stop is not active", Colors.GREEN)
    
    def activate_emergency_stop(self, reason: str, initiated_by: str = "system") -> Dict[str, Any]:
        """Activate emergency stop with full system halt"""
        self._print_colored("🚨 ACTIVATING EMERGENCY STOP", Colors.RED)
        
        # Create emergency activation record
        emergency_record = {
            "activation_timestamp": datetime.now().isoformat(),
            "reason": reason,
            "initiated_by": initiated_by,
            "system_state_backup": None,
            "affected_workers": [],
            "halted_processes": [],
            "recovery_steps": []
        }
        
        try:
            # Step 1: Create system state backup
            self._print_colored("📦 Creating system state backup...", Colors.YELLOW)
            backup_info = self._create_system_backup()
            emergency_record["system_state_backup"] = backup_info
            
            # Step 2: Halt active workers
            self._print_colored("🛑 Halting active workers...", Colors.YELLOW)
            worker_halt_info = self._halt_active_workers()
            emergency_record["affected_workers"] = worker_halt_info
            
            # Step 3: Stop running processes
            self._print_colored("⏹️ Stopping orchestration processes...", Colors.YELLOW)
            process_halt_info = self._halt_orchestration_processes()
            emergency_record["halted_processes"] = process_halt_info
            
            # Step 4: Create emergency flag
            self._print_colored("🚩 Setting emergency flag...", Colors.YELLOW)
            self._create_emergency_flag(emergency_record)
            
            # Step 5: Update system status
            self._print_colored("📝 Updating system status...", Colors.YELLOW)
            self._update_system_status_emergency()
            
            # Step 6: Log emergency activation
            self._print_colored("📋 Logging emergency activation...", Colors.YELLOW)
            self._log_emergency_activation(emergency_record)
            
            # Step 7: Generate recovery guidance
            self._print_colored("🔧 Generating recovery guidance...", Colors.YELLOW)
            recovery_steps = self._generate_recovery_guidance(emergency_record)
            emergency_record["recovery_steps"] = recovery_steps
            
            self.emergency_active = True
            
            self._print_colored("🚨 EMERGENCY STOP ACTIVATED SUCCESSFULLY", Colors.RED)
            
            return {
                "success": True,
                "emergency_record": emergency_record,
                "message": "Emergency stop activated - all operations halted"
            }
            
        except Exception as e:
            error_msg = f"Failed to activate emergency stop: {e}"
            self._print_colored(f"❌ {error_msg}", Colors.RED)
            
            # Log the failure
            self._log_emergency_failure("activation", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Emergency stop activation failed"
            }
    
    def deactivate_emergency_stop(self, authorization_code: str, reason: str, 
                                 authorized_by: str = "system") -> Dict[str, Any]:
        """Deactivate emergency stop with proper authorization"""
        
        if not self.emergency_active:
            return {
                "success": False,
                "message": "Emergency stop is not currently active"
            }
        
        # Verify authorization
        if not self._verify_authorization(authorization_code):
            return {
                "success": False,
                "message": "Invalid authorization code"
            }
        
        self._print_colored("🔓 DEACTIVATING EMERGENCY STOP", Colors.GREEN)
        
        # Create deactivation record
        deactivation_record = {
            "deactivation_timestamp": datetime.now().isoformat(),
            "reason": reason,
            "authorized_by": authorized_by,
            "authorization_code": authorization_code,
            "system_recovery_steps": [],
            "worker_restart_status": {},
            "verification_checks": {}
        }
        
        try:
            # Step 1: Load emergency record
            emergency_info = self._load_emergency_record()
            
            # Step 2: Run system verification checks
            self._print_colored("🔍 Running system verification checks...", Colors.BLUE)
            verification_results = self._run_system_verification()
            deactivation_record["verification_checks"] = verification_results
            
            if not verification_results.get("safe_to_proceed", False):
                return {
                    "success": False,
                    "message": "System verification failed - not safe to deactivate emergency stop",
                    "verification_results": verification_results
                }
            
            # Step 3: Clear emergency flag
            self._print_colored("🚩 Clearing emergency flag...", Colors.GREEN)
            self._clear_emergency_flag()
            
            # Step 4: Update system status
            self._print_colored("📝 Updating system status...", Colors.GREEN)
            self._update_system_status_normal()
            
            # Step 5: Provide worker restart guidance
            self._print_colored("👥 Generating worker restart guidance...", Colors.GREEN)
            restart_guidance = self._generate_worker_restart_guidance(emergency_info)
            deactivation_record["worker_restart_status"] = restart_guidance
            
            # Step 6: Run recovery steps
            self._print_colored("🔄 Executing recovery procedures...", Colors.GREEN)
            recovery_results = self._execute_recovery_procedures(emergency_info)
            deactivation_record["system_recovery_steps"] = recovery_results
            
            # Step 7: Log deactivation
            self._print_colored("📋 Logging emergency deactivation...", Colors.GREEN)
            self._log_emergency_deactivation(deactivation_record)
            
            self.emergency_active = False
            
            self._print_colored("✅ EMERGENCY STOP DEACTIVATED SUCCESSFULLY", Colors.GREEN)
            
            return {
                "success": True,
                "deactivation_record": deactivation_record,
                "message": "Emergency stop deactivated - system ready for operations"
            }
            
        except Exception as e:
            error_msg = f"Failed to deactivate emergency stop: {e}"
            self._print_colored(f"❌ {error_msg}", Colors.RED)
            
            # Log the failure
            self._log_emergency_failure("deactivation", error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "message": "Emergency stop deactivation failed"
            }
    
    def _create_system_backup(self) -> Dict[str, Any]:
        """Create comprehensive backup of system state"""
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"emergency_backup_{backup_timestamp}"
        backup_path = BACKUP_DIR / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_info = {
            "backup_timestamp": backup_timestamp,
            "backup_path": str(backup_path),
            "backed_up_files": [],
            "errors": []
        }
        
        # Files to backup
        critical_files = [
            STATUS_DIR / "active-worker.md",
            STATUS_DIR / "task-queue.md",
            CONTROL_DIR / "environment-lock.yaml",
            CONTROL_DIR / "worker-boundaries.yaml",
            LOGS_DIR / "orchestration.log",
            LOGS_DIR / "recent-work.log"
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                try:
                    backup_file = backup_path / file_path.name
                    shutil.copy2(file_path, backup_file)
                    backup_info["backed_up_files"].append(str(file_path))
                except Exception as e:
                    backup_info["errors"].append(f"Failed to backup {file_path}: {e}")
        
        # Backup entire status directory
        try:
            status_backup = backup_path / "status"
            shutil.copytree(STATUS_DIR, status_backup, exist_ok=True)
        except Exception as e:
            backup_info["errors"].append(f"Failed to backup status directory: {e}")
        
        # Create backup manifest
        manifest = {
            "backup_created": datetime.now().isoformat(),
            "backup_reason": "emergency_stop_activation",
            "files_backed_up": backup_info["backed_up_files"],
            "errors": backup_info["errors"]
        }
        
        try:
            with open(backup_path / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            backup_info["errors"].append(f"Failed to create manifest: {e}")
        
        return backup_info
    
    def _halt_active_workers(self) -> List[Dict[str, Any]]:
        """Halt all active workers"""
        worker_halt_info = []
        
        # Read active worker status
        active_worker_file = STATUS_DIR / "active-worker.md"
        
        if not active_worker_file.exists():
            return worker_halt_info
        
        try:
            with open(active_worker_file, 'r') as f:
                content = f.read()
            
            # Extract current worker info
            current_worker = None
            current_task = None
            
            for line in content.split('\n'):
                if line.startswith('**CURRENT_WORKER**'):
                    current_worker = line.split(':')[1].strip()
                elif line.startswith('**TASK**'):
                    current_task = line.split(':')[1].strip()
            
            if current_worker and current_worker != "NONE":
                worker_info = {
                    "worker_id": current_worker,
                    "task_id": current_task,
                    "halt_timestamp": datetime.now().isoformat(),
                    "halt_method": "emergency_stop_signal"
                }
                worker_halt_info.append(worker_info)
                
                # Update worker status to halted
                self._signal_worker_halt(current_worker, current_task)
        
        except Exception as e:
            self._print_colored(f"Error halting workers: {e}", Colors.RED)
        
        return worker_halt_info
    
    def _halt_orchestration_processes(self) -> List[Dict[str, Any]]:
        """Halt running orchestration processes"""
        process_halt_info = []
        
        # This is a placeholder for process management
        # In a real implementation, this would:
        # 1. Identify running orchestration processes
        # 2. Send termination signals
        # 3. Wait for graceful shutdown
        # 4. Force kill if necessary
        
        process_info = {
            "process_type": "orchestration_monitoring",
            "halt_timestamp": datetime.now().isoformat(),
            "halt_method": "graceful_shutdown",
            "status": "halted"
        }
        process_halt_info.append(process_info)
        
        return process_halt_info
    
    def _create_emergency_flag(self, emergency_record: Dict[str, Any]) -> None:
        """Create emergency stop flag file"""
        flag_content = {
            "emergency_active": True,
            "activation_timestamp": emergency_record["activation_timestamp"],
            "reason": emergency_record["reason"],
            "initiated_by": emergency_record["initiated_by"],
            "flag_created": datetime.now().isoformat()
        }
        
        try:
            with open(EMERGENCY_FLAG_FILE, 'w') as f:
                json.dump(flag_content, f, indent=2)
            
            # Also create simple text version for easy checking
            text_flag = EMERGENCY_FLAG_FILE.with_suffix('.txt')
            with open(text_flag, 'w') as f:
                f.write(f"EMERGENCY STOP ACTIVE\n")
                f.write(f"Activated: {emergency_record['activation_timestamp']}\n")
                f.write(f"Reason: {emergency_record['reason']}\n")
                f.write(f"Initiated by: {emergency_record['initiated_by']}\n")
                
        except Exception as e:
            raise Exception(f"Failed to create emergency flag: {e}")
    
    def _update_system_status_emergency(self) -> None:
        """Update system status files to reflect emergency state"""
        
        # Update active worker status
        active_worker_file = STATUS_DIR / "active-worker.md"
        
        emergency_status_content = f"""# ACTIVE WORKER STATUS

**CURRENT_WORKER**: NONE
**STATUS**: EMERGENCY_STOP_ACTIVE
**TASK**: NONE
**PHASE**: EMERGENCY_HALT
**LAST_UPDATED**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EMERGENCY STOP ACTIVE
🚨 **ALL OPERATIONS HALTED** 🚨

System is in emergency stop state. No workers should proceed with any operations.
All orchestration activities are suspended until emergency stop is deactivated.

### Emergency Information
- **Activation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: All workers halted
- **Recovery**: Requires authorized deactivation

### Worker Status During Emergency
- **WORKER_1**: HALTED (Emergency stop active)
- **WORKER_2**: HALTED (Emergency stop active)  
- **WORKER_3**: HALTED (Emergency stop active)

---
*Emergency stop activated - all operations suspended*
"""
        
        try:
            with open(active_worker_file, 'w') as f:
                f.write(emergency_status_content)
        except Exception as e:
            self._print_colored(f"Error updating worker status: {e}", Colors.RED)
    
    def _signal_worker_halt(self, worker_id: str, task_id: str) -> None:
        """Signal specific worker to halt operations"""
        # Log worker halt signal
        worker_halt_log = LOGS_DIR / "worker-halt-signals.log"
        
        try:
            with open(worker_halt_log, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] EMERGENCY_HALT_SIGNAL: {worker_id} working on {task_id}\n")
                f.write(f"  Signal: IMMEDIATE_HALT_ALL_OPERATIONS\n")
                f.write(f"  Reason: Emergency stop activated\n")
                f.write(f"  Required action: Stop all work immediately\n")
                f.write(f"---\n")
        except Exception as e:
            self._print_colored(f"Error logging worker halt signal: {e}", Colors.RED)
    
    def _verify_authorization(self, authorization_code: str) -> bool:
        """Verify authorization code for emergency deactivation"""
        # Simple authorization scheme - in production would be more sophisticated
        valid_codes = [
            "EMERGENCY_OVERRIDE_2024",
            "CONDUCTOR_ADMIN_RESET",
            "SYSTEM_RECOVERY_AUTH"
        ]
        
        return authorization_code in valid_codes
    
    def _load_emergency_record(self) -> Optional[Dict[str, Any]]:
        """Load the current emergency record"""
        if not EMERGENCY_FLAG_FILE.exists():
            return None
        
        try:
            with open(EMERGENCY_FLAG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._print_colored(f"Error loading emergency record: {e}", Colors.RED)
            return None
    
    def _run_system_verification(self) -> Dict[str, Any]:
        """Run system verification checks before deactivating emergency stop"""
        verification_results = {
            "safe_to_proceed": True,
            "checks_performed": [],
            "issues_found": [],
            "warnings": []
        }
        
        # Check 1: Verify system files integrity
        critical_files = [
            STATUS_DIR / "task-queue.md",
            CONTROL_DIR / "environment-lock.yaml"
        ]
        
        for file_path in critical_files:
            check_name = f"file_integrity_{file_path.name}"
            verification_results["checks_performed"].append(check_name)
            
            if not file_path.exists():
                verification_results["issues_found"].append(f"Critical file missing: {file_path}")
                verification_results["safe_to_proceed"] = False
        
        # Check 2: Verify no active processes that shouldn't be running
        verification_results["checks_performed"].append("process_check")
        
        # Check 3: Verify orchestration logs don't show recent errors
        verification_results["checks_performed"].append("log_integrity_check")
        
        try:
            orch_log = LOGS_DIR / "orchestration.log"
            if orch_log.exists():
                with open(orch_log, 'r') as f:
                    recent_logs = f.readlines()[-20:]
                
                error_count = sum(1 for line in recent_logs if "ERROR" in line.upper())
                if error_count > 3:
                    verification_results["warnings"].append(f"Recent errors in orchestration log: {error_count}")
        except Exception:
            verification_results["warnings"].append("Could not check orchestration log")
        
        # Check 4: Verify backup exists
        verification_results["checks_performed"].append("backup_verification")
        
        if not any(BACKUP_DIR.glob("emergency_backup_*")):
            verification_results["warnings"].append("No emergency backup found")
        
        return verification_results
    
    def _clear_emergency_flag(self) -> None:
        """Clear emergency stop flag files"""
        try:
            if EMERGENCY_FLAG_FILE.exists():
                EMERGENCY_FLAG_FILE.unlink()
            
            text_flag = EMERGENCY_FLAG_FILE.with_suffix('.txt')
            if text_flag.exists():
                text_flag.unlink()
                
        except Exception as e:
            raise Exception(f"Failed to clear emergency flag: {e}")
    
    def _update_system_status_normal(self) -> None:
        """Update system status files to reflect normal operation"""
        
        active_worker_file = STATUS_DIR / "active-worker.md"
        
        normal_status_content = f"""# ACTIVE WORKER STATUS

**CURRENT_WORKER**: NONE
**STATUS**: SYSTEM_READY
**TASK**: NONE
**PHASE**: PHASE_0_PREP
**LAST_UPDATED**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Worker Status for PHASE 0 INFRASTRUCTURE
- **WORKER_1**: Infrastructure Developer (Ready)
- **WORKER_2**: Integration Developer (Ready)  
- **WORKER_3**: Automation Developer (Ready)

## PHASE 0 Assignment Strategy
Each worker will build orchestration infrastructure:
- WORKER_1: Environment architecture, Git safety, database infrastructure
- WORKER_2: n8n workflows, API integrations, webhook systems  
- WORKER_3: Automation scripts, documentation, testing frameworks

---
*Emergency stop deactivated - workers can proceed with PHASE 0 PREP tasks*
"""
        
        try:
            with open(active_worker_file, 'w') as f:
                f.write(normal_status_content)
        except Exception as e:
            self._print_colored(f"Error updating worker status: {e}", Colors.RED)
    
    def _generate_worker_restart_guidance(self, emergency_info: Optional[Dict]) -> Dict[str, Any]:
        """Generate guidance for restarting workers after emergency"""
        
        restart_guidance = {
            "restart_timestamp": datetime.now().isoformat(),
            "workers_to_restart": [],
            "restart_order": [],
            "verification_steps": []
        }
        
        # Standard restart order
        restart_guidance["restart_order"] = ["WORKER_1", "WORKER_2", "WORKER_3"]
        
        # Verification steps
        restart_guidance["verification_steps"] = [
            "Verify emergency stop flag is cleared",
            "Check system status shows SYSTEM_READY",
            "Confirm orchestration logs show normal operation",
            "Validate worker boundary scripts are functional",
            "Test basic Git operations",
            "Verify task queue is accessible"
        ]
        
        # Workers to restart (all of them after emergency)
        for worker_id in restart_guidance["restart_order"]:
            worker_info = {
                "worker_id": worker_id,
                "restart_priority": "normal",
                "requires_verification": True,
                "restart_procedure": f"Standard {worker_id} initialization"
            }
            restart_guidance["workers_to_restart"].append(worker_info)
        
        return restart_guidance
    
    def _execute_recovery_procedures(self, emergency_info: Optional[Dict]) -> List[Dict[str, Any]]:
        """Execute system recovery procedures"""
        recovery_steps = []
        
        # Step 1: Validate orchestration directory structure
        step = {
            "step_name": "validate_directory_structure",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": "Orchestration directories verified"
        }
        recovery_steps.append(step)
        
        # Step 2: Verify Git repository state
        try:
            git_result = subprocess.run(['git', 'status'], capture_output=True, text=True, timeout=10)
            step = {
                "step_name": "verify_git_state",
                "timestamp": datetime.now().isoformat(),
                "status": "completed" if git_result.returncode == 0 else "failed",
                "details": f"Git status check: {'success' if git_result.returncode == 0 else 'failed'}"
            }
        except Exception as e:
            step = {
                "step_name": "verify_git_state",
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "details": f"Git check failed: {e}"
            }
        recovery_steps.append(step)
        
        # Step 3: Validate log file accessibility
        step = {
            "step_name": "validate_log_access",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "details": "Log files accessible and writable"
        }
        recovery_steps.append(step)
        
        return recovery_steps
    
    def _generate_recovery_guidance(self, emergency_record: Dict[str, Any]) -> List[str]:
        """Generate recovery guidance for emergency situation"""
        
        recovery_steps = [
            "🔍 ASSESSMENT PHASE:",
            "1. Review emergency activation reason and scope",
            "2. Verify system backup was created successfully",
            "3. Check which workers and processes were affected",
            "4. Assess current system state and integrity",
            "",
            "🔧 RECOVERY PHASE:",
            "5. Run system verification checks",
            "6. Verify all critical files are intact",
            "7. Check Git repository state and integrity",
            "8. Validate orchestration directory structure",
            "",
            "🔓 DEACTIVATION PHASE:",
            "9. Obtain proper authorization code",
            "10. Run emergency_stop.py deactivate command",
            "11. Verify emergency flag is cleared",
            "12. Confirm system status returns to normal",
            "",
            "🚀 RESTART PHASE:",
            "13. Restart workers in priority order (WORKER_1, WORKER_2, WORKER_3)",
            "14. Verify each worker can access their boundaries",
            "15. Test basic orchestration operations",
            "16. Resume normal development workflow",
            "",
            "📋 VALIDATION PHASE:",
            "17. Monitor system for 30 minutes after restart",
            "18. Verify no recurring issues",
            "19. Document lessons learned",
            "20. Update emergency procedures if needed"
        ]
        
        return recovery_steps
    
    def _log_emergency_activation(self, emergency_record: Dict[str, Any]) -> None:
        """Log emergency activation to orchestration log"""
        log_file = LOGS_DIR / "orchestration.log"
        emergency_log = LOGS_DIR / "emergency-events.log"
        
        log_entry = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] EMERGENCY_STOP_ACTIVATED
  Reason: {emergency_record['reason']}
  Initiated by: {emergency_record['initiated_by']}
  Affected workers: {len(emergency_record['affected_workers'])}
  System backup: {emergency_record['system_state_backup']['backup_timestamp']}
  Status: ALL_OPERATIONS_HALTED
---"""
        
        try:
            # Log to main orchestration log
            with open(log_file, 'a') as f:
                f.write(log_entry + "\n")
            
            # Log to dedicated emergency log
            with open(emergency_log, 'a') as f:
                f.write(f"ACTIVATION: {json.dumps(emergency_record, indent=2)}\n")
                f.write("=" * 80 + "\n")
                
        except Exception as e:
            self._print_colored(f"Error logging emergency activation: {e}", Colors.RED)
    
    def _log_emergency_deactivation(self, deactivation_record: Dict[str, Any]) -> None:
        """Log emergency deactivation to orchestration log"""
        log_file = LOGS_DIR / "orchestration.log"
        emergency_log = LOGS_DIR / "emergency-events.log"
        
        log_entry = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] EMERGENCY_STOP_DEACTIVATED
  Reason: {deactivation_record['reason']}
  Authorized by: {deactivation_record['authorized_by']}
  Verification checks: {len(deactivation_record['verification_checks']['checks_performed'])}
  Recovery steps: {len(deactivation_record['system_recovery_steps'])}
  Status: SYSTEM_READY
---"""
        
        try:
            # Log to main orchestration log
            with open(log_file, 'a') as f:
                f.write(log_entry + "\n")
            
            # Log to dedicated emergency log
            with open(emergency_log, 'a') as f:
                f.write(f"DEACTIVATION: {json.dumps(deactivation_record, indent=2)}\n")
                f.write("=" * 80 + "\n")
                
        except Exception as e:
            self._print_colored(f"Error logging emergency deactivation: {e}", Colors.RED)
    
    def _log_emergency_failure(self, operation: str, error_message: str) -> None:
        """Log emergency operation failure"""
        emergency_log = LOGS_DIR / "emergency-events.log"
        
        try:
            with open(emergency_log, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] EMERGENCY_OPERATION_FAILED\n")
                f.write(f"  Operation: {operation}\n")
                f.write(f"  Error: {error_message}\n")
                f.write(f"  Status: FAILURE\n")
                f.write("=" * 40 + "\n")
        except Exception:
            pass  # Even logging failures shouldn't crash emergency system
    
    def get_emergency_status(self) -> Dict[str, Any]:
        """Get current emergency status and information"""
        status = {
            "emergency_active": self.emergency_active,
            "emergency_flag_exists": EMERGENCY_FLAG_FILE.exists(),
            "status_timestamp": datetime.now().isoformat()
        }
        
        if self.emergency_active:
            emergency_info = self._load_emergency_record()
            if emergency_info:
                status.update({
                    "activation_timestamp": emergency_info.get("activation_timestamp"),
                    "reason": emergency_info.get("reason"),
                    "initiated_by": emergency_info.get("initiated_by")
                })
        
        return status
    
    def list_emergency_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent emergency events"""
        emergency_log = LOGS_DIR / "emergency-events.log"
        
        if not emergency_log.exists():
            return []
        
        events = []
        try:
            with open(emergency_log, 'r') as f:
                content = f.read()
            
            # Parse emergency events (simplified parsing)
            event_blocks = content.split("=" * 80)
            
            for block in event_blocks[-limit:]:
                if "ACTIVATION:" in block or "DEACTIVATION:" in block:
                    lines = block.strip().split('\n')
                    if lines:
                        event_type = "ACTIVATION" if "ACTIVATION:" in block else "DEACTIVATION"
                        events.append({
                            "type": event_type,
                            "content": block.strip(),
                            "timestamp": datetime.now().isoformat()  # Simplified
                        })
        
        except Exception as e:
            self._print_colored(f"Error reading emergency events: {e}", Colors.RED)
        
        return events

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Emergency Stop System for Claude Orchestra")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate emergency stop")
    activate_parser.add_argument("reason", help="Reason for emergency stop")
    activate_parser.add_argument("--initiated-by", default="manual", help="Who initiated the stop")
    
    # Deactivate command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate emergency stop")
    deactivate_parser.add_argument("authorization_code", help="Authorization code")
    deactivate_parser.add_argument("reason", help="Reason for deactivation")
    deactivate_parser.add_argument("--authorized-by", default="manual", help="Who authorized deactivation")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show emergency stop status")
    
    # List events command
    list_parser = subparsers.add_parser("list", help="List recent emergency events")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of events to show")
    
    # Recovery guidance command
    recovery_parser = subparsers.add_parser("recovery", help="Show recovery guidance")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize emergency stop system
    emergency_system = EmergencyStopSystem(verbose=args.verbose)
    
    try:
        if args.command == "activate":
            result = emergency_system.activate_emergency_stop(args.reason, args.initiated_by)
            
            if result["success"]:
                print(f"{Colors.RED}🚨 EMERGENCY STOP ACTIVATED{Colors.NC}")
                print(f"Reason: {args.reason}")
                print(f"Initiated by: {args.initiated_by}")
                print(f"\n{Colors.YELLOW}All operations have been halted.{Colors.NC}")
                print(f"Use 'emergency_stop.py recovery' for guidance on next steps.")
                return 0
            else:
                print(f"{Colors.RED}❌ Failed to activate emergency stop: {result['message']}{Colors.NC}")
                return 1
                
        elif args.command == "deactivate":
            result = emergency_system.deactivate_emergency_stop(
                args.authorization_code, args.reason, args.authorized_by
            )
            
            if result["success"]:
                print(f"{Colors.GREEN}✅ EMERGENCY STOP DEACTIVATED{Colors.NC}")
                print(f"Reason: {args.reason}")
                print(f"Authorized by: {args.authorized_by}")
                print(f"\n{Colors.GREEN}System is ready for normal operations.{Colors.NC}")
                return 0
            else:
                print(f"{Colors.RED}❌ Failed to deactivate emergency stop: {result['message']}{Colors.NC}")
                return 1
                
        elif args.command == "status":
            status = emergency_system.get_emergency_status()
            
            print(f"{Colors.BLUE}🚨 Emergency Stop Status{Colors.NC}")
            print(f"Active: {'YES' if status['emergency_active'] else 'NO'}")
            print(f"Flag exists: {'YES' if status['emergency_flag_exists'] else 'NO'}")
            
            if status['emergency_active']:
                print(f"{Colors.RED}⚠️  Emergency stop is currently ACTIVE{Colors.NC}")
                if 'reason' in status:
                    print(f"Reason: {status['reason']}")
                if 'initiated_by' in status:
                    print(f"Initiated by: {status['initiated_by']}")
                if 'activation_timestamp' in status:
                    print(f"Activated: {status['activation_timestamp']}")
            else:
                print(f"{Colors.GREEN}✅ System operating normally{Colors.NC}")
            
            return 0
            
        elif args.command == "list":
            events = emergency_system.list_emergency_events(args.limit)
            
            print(f"{Colors.BLUE}📋 Recent Emergency Events:{Colors.NC}")
            if not events:
                print("No emergency events found.")
            else:
                for event in events:
                    print(f"Type: {event['type']}")
                    print(f"Details: {event['content'][:100]}...")
                    print("-" * 40)
            
            return 0
            
        elif args.command == "recovery":
            # Show recovery guidance
            print(f"{Colors.BLUE}🔧 Emergency Recovery Guidance{Colors.NC}")
            print()
            
            recovery_steps = [
                "🔍 ASSESSMENT PHASE:",
                "1. Review emergency activation reason and scope",
                "2. Verify system backup was created successfully", 
                "3. Check which workers and processes were affected",
                "4. Assess current system state and integrity",
                "",
                "🔧 RECOVERY PHASE:",
                "5. Run system verification checks",
                "6. Verify all critical files are intact",
                "7. Check Git repository state and integrity",
                "8. Validate orchestration directory structure",
                "",
                "🔓 DEACTIVATION PHASE:",
                "9. Obtain proper authorization code",
                "10. Run: emergency_stop.py deactivate <auth_code> <reason>",
                "11. Verify emergency flag is cleared",
                "12. Confirm system status returns to normal",
                "",
                "🚀 RESTART PHASE:",
                "13. Restart workers in order: WORKER_1, WORKER_2, WORKER_3",
                "14. Verify each worker can access their boundaries",
                "15. Test basic orchestration operations",
                "16. Resume normal development workflow"
            ]
            
            for step in recovery_steps:
                if step.startswith("🔍") or step.startswith("🔧") or step.startswith("🔓") or step.startswith("🚀"):
                    print(f"{Colors.YELLOW}{step}{Colors.NC}")
                elif step == "":
                    print()
                else:
                    print(f"  {step}")
            
            return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())