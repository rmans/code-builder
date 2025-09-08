#!/usr/bin/env python3
"""
Cursor Agent Integration Module

This module provides a unified interface for Cursor agent orchestration,
combining the task orchestrator with multi-agent cursor management.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .task_orchestrator import TaskOrchestrator, Task, Agent, TaskStatus, AgentStatus
from .multi_agent_cursor import MultiAgentCursorManager

# Import configuration system
from ..config.settings import get_config


class CursorAgent:
    """Represents a Cursor agent with specific capabilities."""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.current_task: Optional[str] = None
        self.max_concurrent_tasks = 1
        self.last_heartbeat = None
    
    def to_agent(self) -> Agent:
        """Convert to the base Agent class."""
        return Agent(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            capabilities=self.capabilities,
            status=self.status,
            current_task=self.current_task,
            max_concurrent_tasks=self.max_concurrent_tasks,
            last_heartbeat=self.last_heartbeat
        )


class CursorAgentOrchestrator:
    """Orchestrates Cursor agents for task execution."""
    
    def __init__(self, cache_dir: str = None):
        # Use configuration system for cache directory
        config = get_config()
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        self.cache_dir = cache_dir
        self.base_orchestrator = TaskOrchestrator(cache_dir)
        self.multi_agent_manager = MultiAgentCursorManager(cache_dir)
        self.cursor_agents: Dict[str, CursorAgent] = {}
        
        # Hook system
        self.hooks_enabled = True
        self.last_update_time = 0
        self.update_debounce_seconds = 2  # Debounce updates
        self.current_md_path = Path(".cb/instructions/current.md")
        self.current_md_path.parent.mkdir(parents=True, exist_ok=True)
    
    def add_cursor_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> str:
        """Add a Cursor agent to the orchestrator."""
        cursor_agent = CursorAgent(agent_id, agent_type, capabilities)
        self.cursor_agents[agent_id] = cursor_agent
        
        # Also add to base orchestrator
        base_agent = cursor_agent.to_agent()
        self.base_orchestrator.add_agent(base_agent)
        
        return agent_id
    
    def get_cursor_agent(self, agent_id: str) -> Optional[CursorAgent]:
        """Get a Cursor agent by ID."""
        return self.cursor_agents.get(agent_id)
    
    def list_cursor_agents(self) -> List[CursorAgent]:
        """List all Cursor agents."""
        return list(self.cursor_agents.values())
    
    def launch_cursor_agent_for_task(self, task_id: str) -> bool:
        """Launch a Cursor agent for a specific task."""
        if task_id not in self.base_orchestrator.tasks:
            return False
        
        task = self.base_orchestrator.tasks[task_id]
        
        # Find an available agent of the right type
        available_agents = self.base_orchestrator.get_available_agents(task.agent_type)
        if not available_agents:
            print(f"No available agents for task type: {task.agent_type}")
            return False
        
        # Use the multi-agent manager to launch the agent
        success = self.multi_agent_manager.launch_agent(task)
        
        if success:
            # Call hook for agent start
            agent_id = available_agents[0].agent_id
            self.on_agent_start(agent_id, task_id)
            
            # Update task status to running
            task.status = TaskStatus.RUNNING
            task.assigned_agent = agent_id
            task.started_at = datetime.now()
        
        return success
    
    def launch_multiple_cursor_agents(self, task_ids: List[str]) -> Dict[str, bool]:
        """Launch multiple Cursor agents for different tasks."""
        results = {}
        
        for task_id in task_ids:
            if task_id in self.base_orchestrator.tasks:
                task = self.base_orchestrator.tasks[task_id]
                results[task_id] = self.multi_agent_manager.launch_agent(task)
            else:
                results[task_id] = False
        
        return results
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the status of a specific agent."""
        if agent_id in self.cursor_agents:
            cursor_agent = self.cursor_agents[agent_id]
            return {
                "agent_id": agent_id,
                "agent_type": cursor_agent.agent_type,
                "status": cursor_agent.status.value,
                "current_task": cursor_agent.current_task,
                "capabilities": cursor_agent.capabilities
            }
        else:
            return {"status": "not_found"}
    
    def get_execution_order(self) -> List[List[str]]:
        """Get the execution order for tasks."""
        return self.base_orchestrator.get_execution_order()
    
    def add_task(self, task: Task) -> str:
        """Add a task to the orchestrator."""
        task_id = self.base_orchestrator.add_task(task)
        
        # Call hook for task creation
        self.on_task_create(task)
        
        return task_id
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to run."""
        return self.base_orchestrator.get_ready_tasks()
    
    def run_orchestration_cycle(self) -> Dict[str, Any]:
        """Run one orchestration cycle."""
        return self.base_orchestrator.run_orchestration_cycle()
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the orchestrator status."""
        summary = self.base_orchestrator.get_status_summary()
        summary["cursor_agents"] = {
            "total": len(self.cursor_agents),
            "by_type": {}
        }
        
        # Count agents by type
        for agent in self.cursor_agents.values():
            agent_type = agent.agent_type
            if agent_type not in summary["cursor_agents"]["by_type"]:
                summary["cursor_agents"]["by_type"][agent_type] = 0
            summary["cursor_agents"]["by_type"][agent_type] += 1
        
        return summary
    
    def on_task_create(self, task: Task) -> None:
        """Hook called when a task is created - regenerate per-task rules."""
        if not self.hooks_enabled:
            return
        
        try:
            # Import here to avoid circular imports
            from ..overlay.command_generator import generate_task_commands
            
            # Generate per-task rules for the new task
            print(f"🔄 Regenerating per-task rules for {task.task_id}")
            generate_task_commands()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not regenerate per-task rules: {e}")
    
    def on_agent_start(self, agent_id: str, task_id: str) -> None:
        """Hook called when an agent starts - update current.md."""
        if not self.hooks_enabled:
            return
        
        # Debounce updates
        current_time = time.time()
        if current_time - self.last_update_time < self.update_debounce_seconds:
            return
        
        self.last_update_time = current_time
        
        try:
            self._update_current_md(task_id, agent_id)
        except Exception as e:
            print(f"⚠️  Warning: Could not update current.md: {e}")
    
    def _update_current_md(self, task_id: str, agent_id: str) -> None:
        """Update the current.md file with active task/agent information."""
        try:
            # Get task information
            task = self.base_orchestrator.tasks.get(task_id)
            # Try to get agent from cursor_agents first, then from base orchestrator
            agent = self.cursor_agents.get(agent_id)
            if not agent:
                # Fallback to base orchestrator agents
                base_agent = self.base_orchestrator.agents.get(agent_id)
                if base_agent:
                    # Convert base agent to cursor agent for consistency
                    agent = CursorAgent(
                        agent_id=base_agent.agent_id,
                        agent_type=base_agent.agent_type,
                        capabilities=base_agent.capabilities
                    )
            
            if not task or not agent:
                return
            
            # Generate current.md content
            content = f"""# Current Task Execution

**Agent**: {agent_id} ({agent.agent_type})
**Task**: {task_id} - {task.name}
**Status**: {task.status.value}
**Started**: {task.started_at.isoformat() if task.started_at else 'Not started'}
**Priority**: {task.priority}

## Task Description
{task.description}

## Agent Capabilities
{', '.join(agent.capabilities)}

## Dependencies
{', '.join(task.dependencies) if task.dependencies else 'None'}

## Acceptance Criteria
{self._get_acceptance_criteria(task)}

## Current Phase
{self._get_current_phase(task)}

---
*Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Write to current.md
            with open(self.current_md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📝 Updated current.md for {agent_id} working on {task_id}")
            
        except Exception as e:
            print(f"❌ Error updating current.md: {e}")
    
    def _get_acceptance_criteria(self, task: Task) -> str:
        """Get acceptance criteria for a task."""
        try:
            # Try to load from task index
            from ..core.task_index import TaskIndexManager
            index_manager = TaskIndexManager()
            index_data = index_manager.load_index()
            
            for task_data in index_data.get('tasks', []):
                if task_data.get('id') == task.task_id:
                    criteria = task_data.get('acceptance_criteria', [])
                    if criteria:
                        return '\n'.join([f"- {criterion}" for criterion in criteria])
            
            return "Not specified"
        except Exception:
            return "Not specified"
    
    def _get_current_phase(self, task: Task) -> str:
        """Get the current phase of task execution."""
        if task.status == TaskStatus.PENDING:
            return "Phase 1: 🚀 Implementation (Pending)"
        elif task.status == TaskStatus.READY:
            return "Phase 1: 🚀 Implementation (Ready)"
        elif task.status == TaskStatus.RUNNING:
            return "Phase 1: 🚀 Implementation (Running)"
        elif task.status == TaskStatus.COMPLETED:
            return "Phase 5: 💾 Commit (Completed)"
        elif task.status == TaskStatus.FAILED:
            return "❌ Failed"
        else:
            return f"Status: {task.status.value}"
    
    def enable_hooks(self) -> None:
        """Enable hook system."""
        self.hooks_enabled = True
        print("✅ Cursor integration hooks enabled")
    
    def disable_hooks(self) -> None:
        """Disable hook system."""
        self.hooks_enabled = False
        print("❌ Cursor integration hooks disabled")
    
    def set_update_debounce(self, seconds: int) -> None:
        """Set the debounce time for updates."""
        self.update_debounce_seconds = seconds
        print(f"⏱️  Update debounce set to {seconds} seconds")
