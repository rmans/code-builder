#!/usr/bin/env python3
"""
Task Orchestration System

This module provides intelligent task orchestration that analyzes dependencies,
schedules agents, and manages concurrent task execution while respecting
dependency constraints.
"""

import os
import json
import time
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import networkx as nx


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class Task:
    """Represents a task to be executed."""
    task_id: str
    name: str
    description: str
    command: str
    working_directory: str
    dependencies: List[str]  # List of task_ids this task depends on
    estimated_duration: int  # Estimated duration in minutes
    priority: int  # Higher number = higher priority
    agent_type: str  # Type of agent needed (e.g., "frontend", "backend", "docs")
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    error_message: Optional[str] = None
    # ABC iteration support
    requires_abc_iteration: bool = False
    abc_target_file: Optional[str] = None  # File to run ABC iteration on
    abc_rounds: int = 3  # Number of ABC rounds
    abc_winner: Optional[str] = None  # Selected winner (A, B, or C)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Agent:
    """Represents an available agent."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    max_concurrent_tasks: int = 1
    last_heartbeat: datetime = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()


class TaskOrchestrator:
    """Orchestrates task execution with dependency management."""
    
    def __init__(self, cache_dir: str = "builder/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.cache_dir / "orchestrator_tasks.json"
        self.agents_file = self.cache_dir / "orchestrator_agents.json"
        self.execution_file = self.cache_dir / "orchestrator_execution.json"
        
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.dependency_graph = nx.DiGraph()
        self.execution_history: List[Dict] = []
        
        self.load_state()
        self._build_dependency_graph()
    
    def load_state(self):
        """Load orchestrator state from cache."""
        # Load tasks
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        # Convert datetime strings back to datetime objects
                        if task_data.get('created_at'):
                            task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                        if task_data.get('started_at'):
                            task_data['started_at'] = datetime.fromisoformat(task_data['started_at'])
                        if task_data.get('completed_at'):
                            task_data['completed_at'] = datetime.fromisoformat(task_data['completed_at'])
                        
                        # Convert status strings to enums
                        task_data['status'] = TaskStatus(task_data['status'])
                        
                        self.tasks[task_id] = Task(**task_data)
            except Exception as e:
                print(f"Warning: Could not load tasks: {e}")
        
        # Load agents
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        # Convert datetime strings back to datetime objects
                        if agent_data.get('last_heartbeat'):
                            agent_data['last_heartbeat'] = datetime.fromisoformat(agent_data['last_heartbeat'])
                        
                        # Convert status strings to enums
                        agent_data['status'] = AgentStatus(agent_data['status'])
                        
                        self.agents[agent_id] = Agent(**agent_data)
            except Exception as e:
                print(f"Warning: Could not load agents: {e}")
        
        # Load execution history
        if self.execution_file.exists():
            try:
                with open(self.execution_file, 'r') as f:
                    self.execution_history = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load execution history: {e}")
    
    def save_state(self):
        """Save orchestrator state to cache."""
        # Save tasks
        try:
            data = {}
            for task_id, task in self.tasks.items():
                task_dict = asdict(task)
                # Convert datetime objects to strings
                if task_dict.get('created_at'):
                    task_dict['created_at'] = task.created_at.isoformat()
                if task_dict.get('started_at'):
                    task_dict['started_at'] = task.started_at.isoformat()
                if task_dict.get('completed_at'):
                    task_dict['completed_at'] = task.completed_at.isoformat()
                
                # Convert enums to strings
                task_dict['status'] = task.status.value
                
                data[task_id] = task_dict
            
            with open(self.tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tasks: {e}")
        
        # Save agents
        try:
            data = {}
            for agent_id, agent in self.agents.items():
                agent_dict = asdict(agent)
                # Convert datetime objects to strings
                if agent_dict.get('last_heartbeat'):
                    agent_dict['last_heartbeat'] = agent.last_heartbeat.isoformat()
                
                # Convert enums to strings
                agent_dict['status'] = agent.status.value
                
                data[agent_id] = agent_dict
            
            with open(self.agents_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save agents: {e}")
        
        # Save execution history
        try:
            with open(self.execution_file, 'w') as f:
                json.dump(self.execution_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save execution history: {e}")
    
    def _build_dependency_graph(self):
        """Build the dependency graph from tasks."""
        self.dependency_graph.clear()
        
        # Add all tasks as nodes
        for task_id, task in self.tasks.items():
            self.dependency_graph.add_node(task_id, task=task)
        
        # Add dependency edges
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    self.dependency_graph.add_edge(dep_id, task_id)
    
    def add_task(self, task: Task) -> str:
        """Add a new task to the orchestrator."""
        self.tasks[task.task_id] = task
        self._build_dependency_graph()
        self.save_state()
        return task.task_id
    
    def add_agent(self, agent: Agent) -> str:
        """Add a new agent to the orchestrator."""
        self.agents[agent.agent_id] = agent
        self.save_state()
        return agent.agent_id
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to run (dependencies satisfied)."""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_satisfied = True
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    dependencies_satisfied = False
                    break
                if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        return ready_tasks
    
    def get_available_agents(self, agent_type: str = None) -> List[Agent]:
        """Get available agents, optionally filtered by type."""
        available = []
        
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE:
                if agent_type is None or agent.agent_type == agent_type:
                    available.append(agent)
        
        return available
    
    def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        if task_id not in self.tasks or agent_id not in self.agents:
            return False
        
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        if task.status != TaskStatus.READY or agent.status != AgentStatus.IDLE:
            return False
        
        # Check if agent can handle this task type
        if task.agent_type != agent.agent_type:
            return False
        
        # Assign the task
        task.status = TaskStatus.RUNNING
        task.assigned_agent = agent_id
        task.started_at = datetime.now()
        
        agent.status = AgentStatus.BUSY
        agent.current_task = task_id
        
        self.save_state()
        return True
    
    def complete_task(self, task_id: str, success: bool = True, error_message: str = None) -> bool:
        """Mark a task as completed or failed."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.RUNNING:
            return False
        
        # Update task status
        if success:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
        else:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
        
        # Free up the agent
        if task.assigned_agent and task.assigned_agent in self.agents:
            agent = self.agents[task.assigned_agent]
            agent.status = AgentStatus.IDLE
            agent.current_task = None
        
        # Record execution
        self.execution_history.append({
            "task_id": task_id,
            "agent_id": task.assigned_agent,
            "status": task.status.value,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": error_message
        })
        
        self.save_state()
        return True
    
    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get all tasks that depend on the given task."""
        if task_id not in self.dependency_graph:
            return []
        
        # Get all nodes reachable from this task
        dependents = list(nx.descendants(self.dependency_graph, task_id))
        return dependents
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in the task graph."""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []
    
    def get_execution_order(self) -> List[List[str]]:
        """Get the optimal execution order for tasks (topological sort)."""
        try:
            # Get topological sort
            execution_order = list(nx.topological_sort(self.dependency_graph))
            
            # Group by dependency level
            levels = []
            remaining = set(execution_order)
            
            while remaining:
                # Find tasks with no dependencies in remaining set
                current_level = []
                for task_id in list(remaining):
                    task = self.tasks[task_id]
                    deps_in_remaining = [dep for dep in task.dependencies if dep in remaining]
                    if not deps_in_remaining:
                        current_level.append(task_id)
                        remaining.remove(task_id)
                
                if current_level:
                    levels.append(current_level)
                else:
                    # Circular dependency detected
                    break
            
            return levels
        except nx.NetworkXError:
            return []
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the orchestrator status."""
        task_counts = {}
        for status in TaskStatus:
            task_counts[status.value] = sum(1 for task in self.tasks.values() if task.status == status)
        
        agent_counts = {}
        for status in AgentStatus:
            agent_counts[status.value] = sum(1 for agent in self.agents.values() if agent.status == status)
        
        return {
            "tasks": {
                "total": len(self.tasks),
                "by_status": task_counts
            },
            "agents": {
                "total": len(self.agents),
                "by_status": agent_counts
            },
            "cycles_detected": len(self.detect_cycles()),
            "ready_tasks": len(self.get_ready_tasks()),
            "available_agents": len(self.get_available_agents())
        }
    
    def execute_task(self, task_id: str) -> bool:
        """Execute a task by running its command and optionally ABC iteration."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        try:
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(task.working_directory)
            
            # Execute the main command
            print(f"🚀 Executing task {task_id}: {task.name}")
            result = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=task.estimated_duration * 60  # Convert to seconds
            )
            
            # Check if main command succeeded
            main_success = result.returncode == 0
            error_message = result.stderr if not main_success else None
            
            if not main_success:
                self.complete_task(task_id, False, f"Main command failed: {error_message}")
                return False
            
            # Run ABC iteration if required
            if task.requires_abc_iteration:
                print(f"🔄 Task {task_id} requires ABC iteration")
                abc_success = self.run_abc_iteration(task_id)
                
                if not abc_success:
                    self.complete_task(task_id, False, "ABC iteration failed")
                    return False
                
                print(f"✅ ABC iteration completed for task {task_id}")
            
            # Mark task as completed
            self.complete_task(task_id, True, None)
            return True
            
        except subprocess.TimeoutExpired:
            self.complete_task(task_id, False, "Task timed out")
            return False
        except Exception as e:
            self.complete_task(task_id, False, str(e))
            return False
        finally:
            # Restore original directory
            os.chdir(original_cwd)
    
    def run_orchestration_cycle(self) -> Dict[str, Any]:
        """Run one orchestration cycle - assign ready tasks to available agents."""
        cycle_info = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "assignments": []
        }
        
        # Get ready tasks
        ready_tasks = self.get_ready_tasks()
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        # Assign tasks to available agents
        for task in ready_tasks:
            available_agents = self.get_available_agents(task.agent_type)
            
            if available_agents:
                # Choose the first available agent
                agent = available_agents[0]
                
                if self.assign_task_to_agent(task.task_id, agent.agent_id):
                    cycle_info["tasks_assigned"] += 1
                    cycle_info["assignments"].append({
                        "task_id": task.task_id,
                        "agent_id": agent.agent_id,
                        "task_name": task.name
                    })
        
        # Execute assigned tasks
        for task in self.tasks.values():
            if task.status == TaskStatus.RUNNING and task.assigned_agent:
                success = self.execute_task(task.task_id)
                if success:
                    cycle_info["tasks_completed"] += 1
                else:
                    cycle_info["tasks_failed"] += 1
        
        return cycle_info
    
    def run_abc_iteration(self, task_id: str) -> bool:
        """Run ABC iteration for a task that requires it."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if not task.requires_abc_iteration or not task.abc_target_file:
            return True  # No ABC iteration needed
        
        try:
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(task.working_directory)
            
            # Run ABC iteration with new iterative system
            print(f"🔄 Running ABC iteration for task {task_id} on {task.abc_target_file}")
            print(f"   Rounds: {task.abc_rounds}")
            
            # Use the new iterative ABC system with auto-selection
            result = subprocess.run([
                "python3", "builder/core/cli.py", "iter:cursor", 
                task.abc_target_file, 
                "--rounds", str(task.abc_rounds),
                "--auto-select"
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout for multiple rounds
            
            if result.returncode == 0:
                print(f"✅ ABC iteration completed for task {task_id}")
                print(f"   Output: {result.stdout}")
                # The new system automatically applies the winner and cleans up
                task.abc_winner = "auto-selected"
                return True
            else:
                print(f"❌ ABC iteration failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ ABC iteration timed out for task {task_id}")
            return False
        except Exception as e:
            print(f"❌ ABC iteration error for task {task_id}: {e}")
            return False
        finally:
            # Restore original directory
            os.chdir(original_cwd)
    
    def _select_abc_winner(self, target_file: str) -> Optional[str]:
        """Select ABC winner based on objective scores (automated selection)."""
        try:
            # Look for variant files in cache
            cache_dir = Path("builder/cache")
            variant_files = {
                "A": cache_dir / "variant_A.ts",
                "B": cache_dir / "variant_B.ts", 
                "C": cache_dir / "variant_C.ts"
            }
            
            # Check which variants exist
            available_variants = {k: v for k, v in variant_files.items() if v.exists()}
            
            if not available_variants:
                return None
            
            # For automated selection, we'll use a simple heuristic:
            # - Prefer variant B (usually the enhanced version)
            # - Fall back to A if B doesn't exist
            # - Fall back to C if neither A nor B exist
            
            if "B" in available_variants:
                return "B"
            elif "A" in available_variants:
                return "A"
            elif "C" in available_variants:
                return "C"
            else:
                return None
                
        except Exception as e:
            print(f"Warning: Error selecting ABC winner: {e}")
            return None
    
    def run_continuous(self, max_cycles: int = None, cycle_delay: float = 5.0):
        """Run continuous orchestration until all tasks are complete or max_cycles reached."""
        cycles = 0
        
        while True:
            if max_cycles and cycles >= max_cycles:
                break
            
            # Check if all tasks are complete
            pending_tasks = [t for t in self.tasks.values() if t.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]]
            if not pending_tasks:
                print("✅ All tasks completed!")
                break
            
            # Run orchestration cycle
            cycle_info = self.run_orchestration_cycle()
            cycles += 1
            
            print(f"🔄 Cycle {cycles}: {cycle_info['tasks_assigned']} assigned, {cycle_info['tasks_completed']} completed, {cycle_info['tasks_failed']} failed")
            
            # Wait before next cycle
            time.sleep(cycle_delay)
        
        return cycles
