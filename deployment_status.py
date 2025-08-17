#!/usr/bin/env python3
"""
Deployment Status Tracker
Track progress through all 6 phases of deployment
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class PhaseStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class DeploymentPhase:
    """Represents a single deployment phase"""
    
    def __init__(self, phase_number: int, name: str, description: str, estimated_duration: str):
        self.phase_number = phase_number
        self.name = name
        self.description = description
        self.estimated_duration = estimated_duration
        self.status = PhaseStatus.NOT_STARTED
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.tasks: List[Dict[str, Any]] = []
        self.notes: List[str] = []
        self.blocking_issues: List[str] = []
    
    def start(self):
        """Mark phase as started"""
        self.status = PhaseStatus.IN_PROGRESS
        self.start_time = datetime.now().isoformat()
    
    def complete(self):
        """Mark phase as completed"""
        self.status = PhaseStatus.COMPLETED
        self.end_time = datetime.now().isoformat()
    
    def fail(self, reason: str):
        """Mark phase as failed"""
        self.status = PhaseStatus.FAILED
        self.end_time = datetime.now().isoformat()
        self.blocking_issues.append(reason)
    
    def block(self, reason: str):
        """Mark phase as blocked"""
        self.status = PhaseStatus.BLOCKED
        self.blocking_issues.append(reason)
    
    def add_task(self, task_name: str, completed: bool = False, notes: str = ""):
        """Add a task to this phase"""
        self.tasks.append({
            "name": task_name,
            "completed": completed,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_note(self, note: str):
        """Add a note to this phase"""
        self.notes.append({
            "note": note,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_progress(self) -> float:
        """Get completion progress as percentage"""
        if not self.tasks:
            return 100.0 if self.status == PhaseStatus.COMPLETED else 0.0
        
        completed_tasks = sum(1 for task in self.tasks if task["completed"])
        return (completed_tasks / len(self.tasks)) * 100

class DeploymentStatusTracker:
    """Track deployment status across all phases"""
    
    def __init__(self):
        self.deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now().isoformat()
        self.phases = self._initialize_phases()
        self.current_phase = 1
        
    def _initialize_phases(self) -> Dict[int, DeploymentPhase]:
        """Initialize all 6 deployment phases"""
        phases = {}
        
        # Phase 1: Complete Dev Testing
        phase1 = DeploymentPhase(
            1, 
            "Complete Dev Testing",
            "Test all behavioral intelligence components in development environment",
            "2-3 days"
        )
        phase1.add_task("Component initialization tests")
        phase1.add_task("Database operations tests")
        phase1.add_task("Superior onboarding flow tests")
        phase1.add_task("Business intelligence metrics tests")
        phase1.add_task("Admin dashboard generation tests")
        phase1.add_task("User metrics generation tests")
        phase1.add_task("Optimized sequences tests")
        phase1.add_task("Complete integration flow tests")
        phases[1] = phase1
        
        # Phase 2: Setup Staging Environment
        phase2 = DeploymentPhase(
            2,
            "Setup Staging Environment", 
            "Configure staging to mirror production exactly",
            "1 day"
        )
        phase2.add_task("Verify environment variables")
        phase2.add_task("Test database connection")
        phase2.add_task("Check database schema")
        phase2.add_task("Run database migrations")
        phase2.add_task("Test component imports")
        phase2.add_task("Setup feature flags")
        phase2.add_task("Test admin dashboard")
        phase2.add_task("Create test data")
        phase2.add_task("Verify API endpoints")
        phases[2] = phase2
        
        # Phase 3: Deploy to Staging & Fix Issues
        phase3 = DeploymentPhase(
            3,
            "Deploy to Staging & Fix Issues",
            "Deploy all components to staging and resolve any issues",
            "2-3 days"
        )
        phase3.add_task("Deploy behavioral intelligence components")
        phase3.add_task("Run staging integration tests")
        phase3.add_task("Fix import/dependency issues")
        phase3.add_task("Fix database issues")
        phase3.add_task("Fix API endpoint issues")
        phase3.add_task("Verify feature flags work")
        phase3.add_task("Test with staging data")
        phase3.add_task("Performance testing")
        phases[3] = phase3
        
        # Phase 4: Migrate to Production
        phase4 = DeploymentPhase(
            4,
            "Migrate to Production",
            "Deploy to production with all features hidden from users",
            "1 day"
        )
        phase4.add_task("Take production backup")
        phase4.add_task("Run production database migrations")
        phase4.add_task("Deploy code with features OFF")
        phase4.add_task("Verify deployment successful")
        phase4.add_task("Test rollback procedure")
        phase4.add_task("Configure monitoring")
        phases[4] = phase4
        
        # Phase 5: Test in Production (Hidden)
        phase5 = DeploymentPhase(
            5,
            "Test in Production (Hidden)",
            "Test all features in production with test users only",
            "2 days"
        )
        phase5.add_task("Add test users to system")
        phase5.add_task("Enable features for test users only")
        phase5.add_task("Test superior onboarding with test users")
        phase5.add_task("Test business intelligence dashboard")
        phase5.add_task("Test user metrics with test users")
        phase5.add_task("Verify regular users see no changes")
        phase5.add_task("Monitor system performance")
        phase5.add_task("Collect test user feedback")
        phases[5] = phase5
        
        # Phase 6: Document Process
        phase6 = DeploymentPhase(
            6,
            "Document Process in Notion",
            "Create comprehensive documentation for team",
            "1 day"
        )
        phase6.add_task("Create system overview documentation")
        phase6.add_task("Document technical architecture")
        phase6.add_task("Create admin operations guide")
        phase6.add_task("Write troubleshooting guide")
        phase6.add_task("Create team training materials")
        phase6.add_task("Document deployment runbooks")
        phase6.add_task("Create go-live procedures")
        phases[6] = phase6
        
        return phases
    
    def get_current_phase(self) -> DeploymentPhase:
        """Get the current active phase"""
        return self.phases[self.current_phase]
    
    def start_phase(self, phase_number: int) -> bool:
        """Start a specific phase"""
        if phase_number in self.phases:
            self.phases[phase_number].start()
            self.current_phase = phase_number
            return True
        return False
    
    def complete_phase(self, phase_number: int) -> bool:
        """Complete a specific phase"""
        if phase_number in self.phases:
            self.phases[phase_number].complete()
            # Auto-advance to next phase if exists
            if phase_number + 1 in self.phases:
                self.current_phase = phase_number + 1
            return True
        return False
    
    def fail_phase(self, phase_number: int, reason: str) -> bool:
        """Mark a phase as failed"""
        if phase_number in self.phases:
            self.phases[phase_number].fail(reason)
            return True
        return False
    
    def block_phase(self, phase_number: int, reason: str) -> bool:
        """Mark a phase as blocked"""
        if phase_number in self.phases:
            self.phases[phase_number].block(reason)
            return True
        return False
    
    def complete_task(self, phase_number: int, task_name: str, notes: str = "") -> bool:
        """Mark a task as completed in a specific phase"""
        if phase_number in self.phases:
            phase = self.phases[phase_number]
            for task in phase.tasks:
                if task_name.lower() in task["name"].lower():
                    task["completed"] = True
                    task["completion_time"] = datetime.now().isoformat()
                    if notes:
                        task["notes"] = notes
                    return True
        return False
    
    def add_note(self, phase_number: int, note: str) -> bool:
        """Add a note to a specific phase"""
        if phase_number in self.phases:
            self.phases[phase_number].add_note(note)
            return True
        return False
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall deployment progress"""
        total_phases = len(self.phases)
        completed_phases = sum(1 for phase in self.phases.values() if phase.status == PhaseStatus.COMPLETED)
        
        # Calculate task progress
        total_tasks = sum(len(phase.tasks) for phase in self.phases.values())
        completed_tasks = sum(
            sum(1 for task in phase.tasks if task["completed"]) 
            for phase in self.phases.values()
        )
        
        return {
            "deployment_id": self.deployment_id,
            "start_time": self.start_time,
            "current_phase": self.current_phase,
            "phases_completed": completed_phases,
            "total_phases": total_phases,
            "phase_progress": f"{completed_phases}/{total_phases}",
            "tasks_completed": completed_tasks,
            "total_tasks": total_tasks,
            "task_progress": f"{completed_tasks}/{total_tasks}",
            "overall_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        progress = self.get_overall_progress()
        current_phase = self.get_current_phase()
        
        report = f"""
🚀 BEHAVIORAL INTELLIGENCE DEPLOYMENT STATUS
{'=' * 60}

Deployment ID: {progress['deployment_id']}
Started: {progress['start_time']}

📊 Overall Progress: {progress['overall_percentage']:.1f}%
   Phases: {progress['phase_progress']} ({progress['phases_completed']} completed)
   Tasks: {progress['task_progress']} ({progress['tasks_completed']} completed)

🎯 Current Phase: {current_phase.phase_number}. {current_phase.name}
   Status: {current_phase.status.value.upper()}
   Progress: {current_phase.get_progress():.1f}%
   Duration: {current_phase.estimated_duration}

📋 Phase Details:
"""
        
        for phase_num, phase in self.phases.items():
            status_icon = {
                PhaseStatus.NOT_STARTED: "⏳",
                PhaseStatus.IN_PROGRESS: "🔄", 
                PhaseStatus.COMPLETED: "✅",
                PhaseStatus.FAILED: "❌",
                PhaseStatus.BLOCKED: "🚫"
            }[phase.status]
            
            completed_tasks = sum(1 for task in phase.tasks if task["completed"])
            
            report += f"""
{status_icon} Phase {phase_num}: {phase.name}
   Status: {phase.status.value.upper()}
   Tasks: {completed_tasks}/{len(phase.tasks)} completed
   Progress: {phase.get_progress():.1f}%
"""
            
            if phase.blocking_issues:
                report += f"   ⚠️ Issues: {'; '.join(phase.blocking_issues)}\n"
        
        return report
    
    def save_status(self, filename: Optional[str] = None) -> str:
        """Save current status to JSON file"""
        if filename is None:
            filename = f"deployment_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Serialize the deployment status
        status_data = {
            "deployment_id": self.deployment_id,
            "start_time": self.start_time,
            "current_phase": self.current_phase,
            "overall_progress": self.get_overall_progress(),
            "phases": {}
        }
        
        for phase_num, phase in self.phases.items():
            status_data["phases"][phase_num] = {
                "name": phase.name,
                "description": phase.description,
                "status": phase.status.value,
                "start_time": phase.start_time,
                "end_time": phase.end_time,
                "estimated_duration": phase.estimated_duration,
                "tasks": phase.tasks,
                "notes": phase.notes,
                "blocking_issues": phase.blocking_issues,
                "progress": phase.get_progress()
            }
        
        with open(filename, "w") as f:
            json.dump(status_data, f, indent=2)
        
        return filename
    
    def load_status(self, filename: str) -> bool:
        """Load status from JSON file"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            self.deployment_id = data["deployment_id"]
            self.start_time = data["start_time"] 
            self.current_phase = data["current_phase"]
            
            # Restore phase states
            for phase_num, phase_data in data["phases"].items():
                phase_num = int(phase_num)
                if phase_num in self.phases:
                    phase = self.phases[phase_num]
                    phase.status = PhaseStatus(phase_data["status"])
                    phase.start_time = phase_data["start_time"]
                    phase.end_time = phase_data["end_time"]
                    phase.tasks = phase_data["tasks"]
                    phase.notes = phase_data["notes"]
                    phase.blocking_issues = phase_data["blocking_issues"]
            
            return True
        except Exception as e:
            print(f"Error loading status: {e}")
            return False

def main():
    """CLI for managing deployment status"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment Status Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show current status")
    status_parser.add_argument("--load", help="Load status from file")
    
    # Start phase command
    start_parser = subparsers.add_parser("start", help="Start a phase")
    start_parser.add_argument("phase", type=int, help="Phase number to start")
    
    # Complete phase command
    complete_parser = subparsers.add_parser("complete", help="Complete a phase")
    complete_parser.add_argument("phase", type=int, help="Phase number to complete")
    
    # Complete task command
    task_parser = subparsers.add_parser("task", help="Complete a task")
    task_parser.add_argument("phase", type=int, help="Phase number")
    task_parser.add_argument("task", help="Task name (partial match)")
    task_parser.add_argument("--notes", help="Optional notes")
    
    # Note command
    note_parser = subparsers.add_parser("note", help="Add a note")
    note_parser.add_argument("phase", type=int, help="Phase number")
    note_parser.add_argument("note", help="Note to add")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save status to file")
    save_parser.add_argument("--filename", help="Output filename")
    
    args = parser.parse_args()
    
    tracker = DeploymentStatusTracker()
    
    if args.command == "status":
        if args.load:
            tracker.load_status(args.load)
        print(tracker.get_status_report())
    
    elif args.command == "start":
        if tracker.start_phase(args.phase):
            print(f"✅ Started Phase {args.phase}")
        else:
            print(f"❌ Failed to start Phase {args.phase}")
    
    elif args.command == "complete":
        if tracker.complete_phase(args.phase):
            print(f"✅ Completed Phase {args.phase}")
        else:
            print(f"❌ Failed to complete Phase {args.phase}")
    
    elif args.command == "task":
        if tracker.complete_task(args.phase, args.task, args.notes or ""):
            print(f"✅ Completed task: {args.task}")
        else:
            print(f"❌ Task not found: {args.task}")
    
    elif args.command == "note":
        if tracker.add_note(args.phase, args.note):
            print(f"✅ Added note to Phase {args.phase}")
        else:
            print(f"❌ Failed to add note to Phase {args.phase}")
    
    elif args.command == "save":
        filename = tracker.save_status(args.filename)
        print(f"✅ Status saved to: {filename}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()