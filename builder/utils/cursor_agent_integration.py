#!/usr/bin/env python3
"""
Cursor Agent Integration

This module integrates the task orchestration system with Cursor agents,
allowing tasks to be executed by actual AI agents rather than just shell commands.
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from .task_orchestrator import Task, TaskStatus, Agent, AgentStatus


@dataclass
class CursorAgent:
    """Represents a Cursor agent that can execute tasks."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    cursor_session_id: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    max_concurrent_tasks: int = 1
    last_heartbeat: datetime = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()


class CursorAgentExecutor:
    """Executes tasks using Cursor agents."""
    
    def __init__(self, cursor_executable: str = "cursor"):
        self.cursor_executable = cursor_executable
        self.agent_sessions: Dict[str, str] = {}  # task_id -> session_id
    
    def start_cursor_session(self, task: Task) -> Optional[str]:
        """Start a Cursor session for a task."""
        try:
            # Create a session file with task context
            session_file = Path(f"builder/cache/cursor_sessions/{task.task_id}.json")
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "task_id": task.task_id,
                "task_name": task.name,
                "description": task.description,
                "working_directory": task.working_directory,
                "agent_type": task.agent_type,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            # Start Cursor with the session context
            cmd = [
                self.cursor_executable,
                "--session-file", str(session_file),
                "--working-dir", task.working_directory
            ]
            
            # Start Cursor in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=task.working_directory
            )
            
            # Store session info
            session_id = f"cursor-{task.task_id}-{int(time.time())}"
            self.agent_sessions[task.task_id] = session_id
            
            return session_id
            
        except Exception as e:
            print(f"Error starting Cursor session for {task.task_id}: {e}")
            return None
    
    def send_task_to_cursor(self, task: Task, session_id: str) -> bool:
        """Send task instructions to Cursor agent."""
        try:
            # Create task instruction file
            instruction_file = Path(f"builder/cache/cursor_sessions/{task.task_id}_instructions.md")
            
            instruction_content = f"""# Task: {task.name}

## Description
{task.description}

## Command to Execute
```bash
{task.command}
```

## Working Directory
{task.working_directory}

## Agent Type
{task.agent_type}

## Instructions
Please execute this task using your available tools and capabilities.
Focus on the specific command provided and ensure it completes successfully.

## Expected Output
- Execute the command: `{task.command}`
- Verify the task completes successfully
- Report any issues or errors
- Update the task status when complete

## Context
This task is part of a larger workflow with dependencies:
- Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}
- Priority: {task.priority}
- Estimated Duration: {task.estimated_duration} minutes
"""
            
            with open(instruction_file, 'w') as f:
                f.write(instruction_content)
            
            # Send instruction to Cursor (this would need to be implemented based on Cursor's API)
            # For now, we'll simulate this by creating a marker file
            marker_file = Path(f"builder/cache/cursor_sessions/{task.task_id}_sent")
            marker_file.touch()
            
            return True
            
        except Exception as e:
            print(f"Error sending task to Cursor: {e}")
            return False
    
    def check_task_completion(self, task: Task) -> bool:
        """Check if Cursor agent has completed the task."""
        try:
            # Check for completion marker
            completion_file = Path(f"builder/cache/cursor_sessions/{task.task_id}_completed")
            if completion_file.exists():
                return True
            
            # Check if the command output exists (for simple tasks)
            if task.command.startswith("echo") and ">" in task.command:
                # Extract output file from echo command
                parts = task.command.split(">")
                if len(parts) > 1:
                    output_file = parts[1].strip()
                    if Path(output_file).exists():
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking task completion: {e}")
            return False
    
    def get_task_result(self, task: Task) -> Dict[str, Any]:
        """Get the result of a completed task."""
        try:
            result = {
                "task_id": task.task_id,
                "status": "completed",
                "output": "",
                "error": None,
                "files_created": [],
                "completion_time": datetime.now().isoformat()
            }
            
            # Check for output files
            if task.command.startswith("echo") and ">" in task.command:
                parts = task.command.split(">")
                if len(parts) > 1:
                    output_file = parts[1].strip()
                    if Path(output_file).exists():
                        with open(output_file, 'r') as f:
                            result["output"] = f.read()
                        result["files_created"].append(output_file)
            
            # Check for completion marker
            completion_file = Path(f"builder/cache/cursor_sessions/{task.task_id}_completed")
            if completion_file.exists():
                with open(completion_file, 'r') as f:
                    completion_data = json.load(f)
                    result.update(completion_data)
            
            return result
            
        except Exception as e:
            return {
                "task_id": task.task_id,
                "status": "error",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
    
    def stop_cursor_session(self, task: Task) -> bool:
        """Stop Cursor session for a task."""
        try:
            if task.task_id in self.agent_sessions:
                session_id = self.agent_sessions[task.task_id]
                # In a real implementation, you'd send a stop signal to Cursor
                # For now, we'll just clean up the session
                del self.agent_sessions[task.task_id]
                return True
            return False
        except Exception as e:
            print(f"Error stopping Cursor session: {e}")
            return False


class CursorAgentOrchestrator:
    """Enhanced orchestrator that uses Cursor agents."""
    
    def __init__(self, cache_dir: str = "builder/cache"):
        from .task_orchestrator import TaskOrchestrator
        self.base_orchestrator = TaskOrchestrator(cache_dir)
        self.cursor_executor = CursorAgentExecutor()
        self.active_cursor_sessions: Dict[str, str] = {}
    
    def add_cursor_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> str:
        """Add a Cursor agent to the orchestrator."""
        cursor_agent = CursorAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities
        )
        return self.base_orchestrator.add_agent(cursor_agent)
    
    def execute_task_with_cursor(self, task: Task) -> bool:
        """Execute a task using Cursor agents."""
        try:
            # Start Cursor session
            session_id = self.cursor_executor.start_cursor_session(task)
            if not session_id:
                return False
            
            # Send task to Cursor
            if not self.cursor_executor.send_task_to_cursor(task, session_id):
                return False
            
            # Store active session
            self.active_cursor_sessions[task.task_id] = session_id
            
            # Wait for completion (in a real implementation, this would be async)
            max_wait_time = task.estimated_duration * 60  # Convert to seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                if self.cursor_executor.check_task_completion(task):
                    # Task completed successfully
                    result = self.cursor_executor.get_task_result(task)
                    self.base_orchestrator.complete_task(task.task_id, True)
                    return True
                
                time.sleep(5)  # Check every 5 seconds
            
            # Task timed out
            self.base_orchestrator.complete_task(task.task_id, False, "Task timed out")
            return False
            
        except Exception as e:
            self.base_orchestrator.complete_task(task.task_id, False, str(e))
            return False
    
    def run_cursor_orchestration_cycle(self) -> Dict[str, Any]:
        """Run one orchestration cycle using Cursor agents."""
        cycle_info = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "assignments": []
        }
        
        # Get ready tasks
        ready_tasks = self.base_orchestrator.get_ready_tasks()
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        # Assign tasks to available Cursor agents
        for task in ready_tasks:
            available_agents = self.base_orchestrator.get_available_agents(task.agent_type)
            
            if available_agents:
                agent = available_agents[0]
                
                if self.base_orchestrator.assign_task_to_agent(task.task_id, agent.agent_id):
                    cycle_info["tasks_assigned"] += 1
                    cycle_info["assignments"].append({
                        "task_id": task.task_id,
                        "agent_id": agent.agent_id,
                        "task_name": task.name
                    })
        
        # Execute assigned tasks with Cursor
        for task in self.base_orchestrator.tasks.values():
            if task.status == TaskStatus.RUNNING and task.assigned_agent:
                success = self.execute_task_with_cursor(task)
                if success:
                    cycle_info["tasks_completed"] += 1
                else:
                    cycle_info["tasks_failed"] += 1
        
        return cycle_info
    
    def run_continuous_cursor_orchestration(self, max_cycles: int = None, cycle_delay: float = 5.0):
        """Run continuous orchestration using Cursor agents."""
        cycles = 0
        
        while True:
            if max_cycles and cycles >= max_cycles:
                break
            
            # Check if all tasks are complete
            pending_tasks = [t for t in self.base_orchestrator.tasks.values() 
                           if t.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]]
            if not pending_tasks:
                print("✅ All tasks completed by Cursor agents!")
                break
            
            # Run orchestration cycle
            cycle_info = self.run_cursor_orchestration_cycle()
            cycles += 1
            
            print(f"🔄 Cursor Cycle {cycles}: {cycle_info['tasks_assigned']} assigned, "
                  f"{cycle_info['tasks_completed']} completed, {cycle_info['tasks_failed']} failed")
            
            # Wait before next cycle
            time.sleep(cycle_delay)
        
        return cycles
