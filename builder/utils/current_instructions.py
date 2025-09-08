#!/usr/bin/env python3
"""
Current Instructions System

This module maintains the current.md file with active agent, task, and system status.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..config.settings import get_config
from ..overlay.paths import OverlayPaths


class CurrentInstructionsManager:
    """Manages the current.md file with system status and instructions."""
    
    def __init__(self, cache_dir: str = None):
        config = get_config()
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        
        self.cache_dir = Path(cache_dir)
        self.overlay_paths = OverlayPaths()
        docs_dir = self.overlay_paths.get_docs_dir()
        if isinstance(docs_dir, str):
            self.instructions_dir = Path(docs_dir) / "instructions"
        else:
            self.instructions_dir = docs_dir / "instructions"
        self.current_file = self.instructions_dir / "current.md"
        
        # Ensure instructions directory exists
        self.instructions_dir.mkdir(parents=True, exist_ok=True)
        
        # Error history (keep last 10 errors)
        self.error_history = []
        self.max_error_history = 10
    
    def update_current_status(self, task_id: str = None, agent_id: str = None, 
                            status: str = None, error: str = None) -> None:
        """Update the current.md file with latest status."""
        try:
            # Get current system status
            system_status = self._get_system_status()
            
            # Get active task and agent info
            active_task = self._get_active_task(task_id)
            active_agent = self._get_active_agent(agent_id)
            
            # Add error to history if provided
            if error:
                self._add_error_to_history(error)
            
            # Generate current.md content
            content = self._generate_current_content(
                system_status, active_task, active_agent, status, error
            )
            
            # Write to file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            print(f"Warning: Could not update current.md: {e}")
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "tasks": self._get_task_status(),
            "agents": self._get_agent_status(),
            "commands": self._get_command_status(),
            "rules": self._get_rule_status(),
            "errors": len(self.error_history)
        }
        return status
    
    def _get_task_status(self) -> Dict[str, Any]:
        """Get current task status."""
        try:
            # Load task index
            task_index_file = self.overlay_paths.get_docs_dir() / "tasks" / "index.json"
            if task_index_file.exists():
                with open(task_index_file, 'r', encoding='utf-8') as f:
                    task_index = json.load(f)
                
                tasks = task_index.get("tasks", [])
                active_tasks = [t for t in tasks if t.get("status") in ["pending", "ready", "running"]]
                completed_tasks = [t for t in tasks if t.get("status") == "completed"]
                
                return {
                    "total": len(tasks),
                    "active": len(active_tasks),
                    "completed": len(completed_tasks),
                    "next_ready": self._get_next_ready_task(tasks)
                }
        except Exception:
            pass
        
        return {"total": 0, "active": 0, "completed": 0, "next_ready": None}
    
    def _get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        try:
            # Load orchestrator agents
            agents_file = self.overlay_paths.get_docs_dir() / "orchestrator_agents.json"
            if agents_file.exists():
                with open(agents_file, 'r', encoding='utf-8') as f:
                    agents_data = json.load(f)
                
                agents = agents_data.get("agents", [])
                available_agents = [a for a in agents if a.get("status") == "available"]
                
                return {
                    "total": len(agents),
                    "available": len(available_agents),
                    "types": list(set(a.get("agent_type", "unknown") for a in agents))
                }
        except Exception:
            pass
        
        return {"total": 0, "available": 0, "types": []}
    
    def _get_command_status(self) -> Dict[str, Any]:
        """Get current command status."""
        try:
            commands_dir = self.overlay_paths.get_commands_dir()
            if commands_dir.exists():
                command_files = list(commands_dir.glob("*.md"))
                return {"available": len(command_files)}
        except Exception:
            pass
        
        return {"available": 0}
    
    def _get_rule_status(self) -> Dict[str, Any]:
        """Get current rule status."""
        try:
            rules_dir = self.overlay_paths.get_docs_dir() / "rules"
            if rules_dir.exists():
                rule_files = list(rules_dir.glob("*.md"))
                return {"active": len(rule_files)}
        except Exception:
            pass
        
        return {"active": 0}
    
    def _get_next_ready_task(self, tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get the next ready task."""
        ready_tasks = [t for t in tasks if t.get("status") == "ready"]
        if ready_tasks:
            # Sort by priority (lower number = higher priority)
            ready_tasks.sort(key=lambda x: x.get("priority", 999))
            return ready_tasks[0]
        return None
    
    def _get_active_task(self, task_id: str = None) -> Optional[Dict[str, Any]]:
        """Get active task information."""
        if not task_id:
            return None
        
        try:
            # Load task index
            task_index_file = self.overlay_paths.get_docs_dir() / "tasks" / "index.json"
            if task_index_file.exists():
                with open(task_index_file, 'r', encoding='utf-8') as f:
                    task_index = json.load(f)
                
                tasks = task_index.get("tasks", [])
                for task in tasks:
                    if task.get("id") == task_id:
                        return task
        except Exception:
            pass
        
        return None
    
    def _get_active_agent(self, agent_id: str = None) -> Optional[Dict[str, Any]]:
        """Get active agent information."""
        if not agent_id:
            return None
        
        try:
            # Load orchestrator agents
            agents_file = self.overlay_paths.get_docs_dir() / "orchestrator_agents.json"
            if agents_file.exists():
                with open(agents_file, 'r', encoding='utf-8') as f:
                    agents_data = json.load(f)
                
                agents = agents_data.get("agents", [])
                for agent in agents:
                    if agent.get("agent_id") == agent_id:
                        return agent
        except Exception:
            pass
        
        return None
    
    def _add_error_to_history(self, error: str) -> None:
        """Add error to history."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        self.error_history.insert(0, error_entry)
        
        # Keep only last N errors
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[:self.max_error_history]
    
    def _generate_current_content(self, system_status: Dict[str, Any], 
                                active_task: Optional[Dict[str, Any]], 
                                active_agent: Optional[Dict[str, Any]], 
                                status: str = None, error: str = None) -> str:
        """Generate the current.md content."""
        content = f"""# Current System Status

**Last Updated**: {system_status['timestamp']}

## 🎯 Current Focus

"""
        
        if active_task and active_agent:
            content += f"""**Active Task**: {active_task.get('id', 'unknown')} - {active_task.get('name', 'unknown')}
**Assigned Agent**: {active_agent.get('agent_id', 'unknown')} ({active_agent.get('agent_type', 'unknown')})
**Status**: {status or active_task.get('status', 'unknown')}

### Task Details
- **Description**: {active_task.get('description', 'No description')}
- **Priority**: {active_task.get('priority', 'unknown')}
- **Domain**: {active_task.get('domain', 'unknown')}
- **Dependencies**: {', '.join(active_task.get('dependencies', [])) or 'None'}

### Agent Capabilities
{', '.join(active_agent.get('capabilities', [])) or 'No capabilities listed'}

"""
        else:
            content += """**Status**: No active task or agent

"""
        
        # System overview
        content += f"""## 📊 System Overview

### Tasks
- **Total**: {system_status['tasks']['total']}
- **Active**: {system_status['tasks']['active']}
- **Completed**: {system_status['tasks']['completed']}

### Agents
- **Total**: {system_status['agents']['total']}
- **Available**: {system_status['agents']['available']}
- **Types**: {', '.join(system_status['agents']['types']) or 'None'}

### Commands
- **Available**: {system_status['commands']['available']}

### Rules
- **Active**: {system_status['rules']['active']}

"""
        
        # Next steps
        next_task = system_status['tasks'].get('next_ready')
        if next_task:
            content += f"""## 🚀 Next Steps

**Next Ready Task**: {next_task.get('id', 'unknown')} - {next_task.get('name', 'unknown')}
- **Priority**: {next_task.get('priority', 'unknown')}
- **Domain**: {next_task.get('domain', 'unknown')}

**Suggested Commands**:
- `cb execute-task {next_task.get('id', 'unknown')}` - Execute the next task
- `cb execute-tasks` - Execute all ready tasks
- `cb task:status` - Check task status

"""
        else:
            content += """## 🚀 Next Steps

**No ready tasks available**

**Suggested Commands**:
- `cb task:status` - Check task status
- `cb generate-task "New Task"` - Create a new task
- `cb ctx:build` - Build context documents

"""
        
        # Recent errors
        if self.error_history:
            content += f"""## ⚠️ Recent Errors

"""
            for i, error_entry in enumerate(self.error_history[:5]):  # Show last 5
                content += f"{i+1}. **{error_entry['timestamp']}**: {error_entry['error']}\n"
            
            content += "\n"
        
        # Current error
        if error:
            content += f"""## 🚨 Current Error

**{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**: {error}

"""
        
        # Suggested rules
        content += """## 📋 Suggested Rules

Based on current context, consider these rules:
- `@rules/execute-task` - For task execution
- `@rules/context-builder` - For document generation
- `@rules/evaluation` - For quality assessment

"""
        
        # Quick reference
        content += """## 🔧 Quick Reference

### Common Commands
- `cb execute-task <task_id>` - Execute specific task
- `cb execute-tasks` - Execute all ready tasks
- `cb task:status` - Show task status
- `cb ctx:build` - Build context documents
- `cb eval:objective` - Run objective evaluation
- `cb rules:check <file>` - Check file against rules

### Status Commands
- `cb update:status` - Show system status
- `cb master:status` - Show master file status
- `cb doc-types:status` - Show document types status

"""
        
        return content
    
    def clear_current_status(self) -> None:
        """Clear the current.md file."""
        try:
            if self.current_file.exists():
                self.current_file.unlink()
        except Exception as e:
            print(f"Warning: Could not clear current.md: {e}")
    
    def get_current_status(self) -> Optional[Dict[str, Any]]:
        """Get current status from file."""
        try:
            if not self.current_file.exists():
                return None
            
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse basic info from content
            lines = content.split('\n')
            status = {
                "file_exists": True,
                "last_updated": None,
                "active_task": None,
                "active_agent": None,
                "error_count": 0
            }
            
            for line in lines:
                if line.startswith("**Last Updated**: "):
                    status["last_updated"] = line.replace("**Last Updated**: ", "")
                elif line.startswith("**Active Task**: "):
                    status["active_task"] = line.replace("**Active Task**: ", "")
                elif line.startswith("**Assigned Agent**: "):
                    status["active_agent"] = line.replace("**Assigned Agent**: ", "")
                elif line.startswith("- **Errors**: "):
                    status["error_count"] = int(line.replace("- **Errors**: ", ""))
            
            return status
            
        except Exception as e:
            print(f"Warning: Could not read current.md: {e}")
            return None


def create_current_instructions_manager(cache_dir: str = None) -> CurrentInstructionsManager:
    """Create a new CurrentInstructionsManager instance."""
    return CurrentInstructionsManager(cache_dir)


# Global manager instance
current_manager = create_current_instructions_manager()


def update_current_status(task_id: str = None, agent_id: str = None, 
                         status: str = None, error: str = None) -> None:
    """Update current status using the global manager."""
    current_manager.update_current_status(task_id, agent_id, status, error)


def clear_current_status() -> None:
    """Clear current status using the global manager."""
    current_manager.clear_current_status()


def get_current_status() -> Optional[Dict[str, Any]]:
    """Get current status using the global manager."""
    return current_manager.get_current_status()
