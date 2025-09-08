#!/usr/bin/env python3
"""
Single Task Runner Commands

This module provides CLI commands for running individual tasks with retry logic,
timeout handling, and result reporting.
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

import click

from .base import cli
from ...utils.task_orchestrator import TaskOrchestrator, Task, TaskStatus
from ...utils.cursor_agent_integration import CursorAgentOrchestrator


class SingleTaskRunner:
    """Runs individual tasks with retry logic and result reporting."""
    
    def __init__(self, cache_dir: str = None):
        self.orchestrator = CursorAgentOrchestrator(cache_dir)
        self.results_dir = Path("cb_docs/tasks/results")
        self.logs_dir = Path("cb_docs/tasks/logs")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def list_runnable_tasks(self) -> List[Task]:
        """Get list of tasks that are ready to run (dependencies satisfied)."""
        return self.orchestrator.get_ready_tasks()
    
    def pick_task(self, agent_type: str = None) -> Optional[Task]:
        """Pick a runnable task, optionally filtered by agent type."""
        runnable_tasks = self.list_runnable_tasks()
        
        if agent_type:
            runnable_tasks = [t for t in runnable_tasks if t.agent_type == agent_type]
        
        if not runnable_tasks:
            return None
        
        # Return the highest priority task
        return max(runnable_tasks, key=lambda t: t.priority)
    
    def run_task(self, task_id: str, retries: int = 3, timeout: int = 300, 
                 resume: bool = False) -> Dict[str, Any]:
        """Run a specific task with retry logic and timeout handling."""
        if task_id not in self.orchestrator.base_orchestrator.tasks:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            }
        
        task = self.orchestrator.base_orchestrator.tasks[task_id]
        
        # Check if task is runnable
        if task.status not in [TaskStatus.PENDING, TaskStatus.READY]:
            if resume and task.status == TaskStatus.RUNNING:
                click.echo(f"Resuming running task: {task_id}")
            else:
                return {
                    "success": False,
                    "error": f"Task {task_id} is not runnable (status: {task.status.value})",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Check dependencies
        ready_tasks = self.list_runnable_tasks()
        if task not in ready_tasks:
            return {
                "success": False,
                "error": f"Task {task_id} dependencies not satisfied",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Run the task
        result = self._execute_task(task, retries, timeout)
        
        # Save result
        self._save_result(task_id, result)
        
        return result
    
    def _execute_task(self, task: Task, retries: int, timeout: int) -> Dict[str, Any]:
        """Execute a task with retry logic."""
        start_time = time.time()
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                click.echo(f"Executing task {task.task_id} (attempt {attempt + 1}/{retries + 1})")
                
                # Update task status
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                
                # Execute the command
                result = subprocess.run(
                    task.command,
                    shell=True,
                    cwd=task.working_directory,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                # Check if successful
                if result.returncode == 0:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    
                    return {
                        "success": True,
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "attempt": attempt + 1,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "duration": time.time() - start_time,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    last_error = f"Command failed with return code {result.returncode}"
                    if result.stderr:
                        last_error += f": {result.stderr}"
                    
                    if attempt < retries:
                        click.echo(f"Attempt {attempt + 1} failed, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        task.status = TaskStatus.FAILED
                        task.error_message = last_error
                        
                        return {
                            "success": False,
                            "task_id": task.task_id,
                            "task_name": task.name,
                            "attempt": attempt + 1,
                            "return_code": result.returncode,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "error": last_error,
                            "duration": time.time() - start_time,
                            "timestamp": datetime.now().isoformat()
                        }
                        
            except subprocess.TimeoutExpired:
                last_error = f"Task timed out after {timeout} seconds"
                if attempt < retries:
                    click.echo(f"Task timed out, retrying...")
                    time.sleep(2 ** attempt)
                else:
                    task.status = TaskStatus.FAILED
                    task.error_message = last_error
                    
                    return {
                        "success": False,
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "attempt": attempt + 1,
                        "error": last_error,
                        "duration": time.time() - start_time,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                if attempt < retries:
                    click.echo(f"Unexpected error, retrying...")
                    time.sleep(2 ** attempt)
                else:
                    task.status = TaskStatus.FAILED
                    task.error_message = last_error
                    
                    return {
                        "success": False,
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "attempt": attempt + 1,
                        "error": last_error,
                        "duration": time.time() - start_time,
                        "timestamp": datetime.now().isoformat()
                    }
        
        # This should never be reached, but just in case
        return {
            "success": False,
            "task_id": task.task_id,
            "task_name": task.name,
            "error": "Maximum retries exceeded",
            "timestamp": datetime.now().isoformat()
        }
    
    def _save_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """Save task result to JSON file."""
        result_file = self.results_dir / f"{task_id}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        click.echo(f"Result saved to: {result_file}")
    
    def _save_log(self, task_id: str, log_content: str) -> None:
        """Save task log to file."""
        log_file = self.logs_dir / f"{task_id}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        click.echo(f"Log saved to: {log_file}")


@cli.command("execute-task")
@click.argument("task_id", required=False)
@click.option("--pick", is_flag=True, help="Pick a runnable task automatically")
@click.option("--agent-type", help="Filter tasks by agent type (when using --pick)")
@click.option("--retries", default=3, help="Number of retry attempts")
@click.option("--timeout", default=300, help="Timeout in seconds")
@click.option("--resume", is_flag=True, help="Resume running tasks")
def execute_task(task_id: str, pick: bool, agent_type: str, retries: int, 
                 timeout: int, resume: bool):
    """Execute a single task with retry logic and timeout handling."""
    runner = SingleTaskRunner()
    
    if pick:
        # Pick a runnable task
        task = runner.pick_task(agent_type)
        if not task:
            click.echo("No runnable tasks found")
            sys.exit(1)
        
        task_id = task.task_id
        click.echo(f"Picked task: {task_id} - {task.name}")
    
    elif not task_id:
        click.echo("Error: Must specify either TASK_ID or --pick")
        sys.exit(1)
    
    # Run the task
    result = runner.run_task(task_id, retries, timeout, resume)
    
    # Print result summary
    if result["success"]:
        click.echo(f"✅ Task {task_id} completed successfully")
        click.echo(f"Duration: {result.get('duration', 0):.2f} seconds")
        if result.get("stdout"):
            click.echo(f"Output: {result['stdout']}")
    else:
        click.echo(f"❌ Task {task_id} failed")
        click.echo(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


@cli.command("list-runnable-tasks")
@click.option("--agent-type", help="Filter by agent type")
def list_runnable_tasks(agent_type: str):
    """List all tasks that are ready to run (dependencies satisfied)."""
    runner = SingleTaskRunner()
    tasks = runner.list_runnable_tasks()
    
    if agent_type:
        tasks = [t for t in tasks if t.agent_type == agent_type]
    
    if not tasks:
        click.echo("No runnable tasks found")
        return
    
    click.echo(f"Found {len(tasks)} runnable tasks:")
    click.echo()
    
    for task in sorted(tasks, key=lambda t: t.priority, reverse=True):
        click.echo(f"  {task.task_id} - {task.name}")
        click.echo(f"    Type: {task.agent_type}")
        click.echo(f"    Priority: {task.priority}")
        click.echo(f"    Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
        click.echo()


@cli.command("pick-task")
@click.option("--agent-type", help="Filter by agent type")
def pick_task(agent_type: str):
    """Pick the highest priority runnable task."""
    runner = SingleTaskRunner()
    task = runner.pick_task(agent_type)
    
    if not task:
        click.echo("No runnable tasks found")
        sys.exit(1)
    
    click.echo(f"Picked task: {task.task_id} - {task.name}")
    click.echo(f"Type: {task.agent_type}")
    click.echo(f"Priority: {task.priority}")
    click.echo(f"Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
