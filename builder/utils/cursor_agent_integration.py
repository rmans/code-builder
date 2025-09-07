#!/usr/bin/env python3
"""
Cursor Agent Integration Module

This module provides a unified interface for Cursor agent orchestration,
combining the task orchestrator with multi-agent cursor management.
"""

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
        return self.multi_agent_manager.launch_agent(task)
    
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
        return self.base_orchestrator.add_task(task)
    
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
