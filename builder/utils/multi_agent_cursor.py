#!/usr/bin/env python3
"""
Multi-Agent Cursor System

This module allows launching multiple Cursor agents to work on different tasks
simultaneously, even without separate chat windows.
"""

import os
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from .task_orchestrator import Task, TaskOrchestrator


class MultiAgentCursorManager:
    """Manages multiple Cursor agents working on different tasks."""
    
    def __init__(self, cache_dir: str = "builder/cache"):
        self.cache_dir = Path(cache_dir)
        self.agents_dir = self.cache_dir / "multi_agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.active_agents = {}
    
    def create_agent_workspace(self, task: Task) -> Dict[str, str]:
        """Create a workspace for a Cursor agent to work on a task."""
        try:
            # Create agent directory
            agent_dir = self.agents_dir / task.task_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Create task context file
            context_file = agent_dir / "task_context.json"
            context_data = {
                "task_id": task.task_id,
                "task_name": task.name,
                "agent_type": task.agent_type,
                "priority": task.priority,
                "working_directory": task.working_directory,
                "command": task.command,
                "dependencies": task.dependencies,
                "estimated_duration": task.estimated_duration,
                "status": "ready",
                "created_at": time.time()
            }
            
            import json
            with open(context_file, 'w') as f:
                json.dump(context_data, f, indent=2)
            
            # Create agent instructions
            instructions_file = agent_dir / "agent_instructions.md"
            self._create_agent_instructions(task, instructions_file)
            
            # Create execution script
            execution_script = agent_dir / "execute_task.sh"
            self._create_execution_script(task, execution_script)
            
            # Create monitoring script
            monitor_script = agent_dir / "monitor_progress.sh"
            self._create_monitor_script(task, monitor_script)
            
            return {
                "agent_dir": str(agent_dir),
                "context_file": str(context_file),
                "instructions_file": str(instructions_file),
                "execution_script": str(execution_script),
                "monitor_script": str(monitor_script)
            }
            
        except Exception as e:
            print(f"Error creating agent workspace: {e}")
            return None
    
    def _create_agent_instructions(self, task: Task, instructions_file: Path) -> None:
        """Create detailed instructions for the Cursor agent."""
        content = f"""# Agent Instructions: {task.name}

## Task Overview
- **Task ID**: {task.task_id}
- **Agent Type**: {task.agent_type}
- **Priority**: {task.priority}
- **Working Directory**: {task.working_directory}

## Your Mission
You are a specialized Cursor agent working on: **{task.name}**

## Primary Command
```bash
{task.command}
```

## Detailed Instructions

### 1. Environment Setup
- Working Directory: `{task.working_directory}`
- Agent Type: {task.agent_type}
- Priority Level: {task.priority}

### 2. Task Execution
1. **Navigate to working directory**: `cd {task.working_directory}`
2. **Execute the command**: `{task.command}`
3. **Verify completion**: Ensure the task completes successfully
4. **Report progress**: Update the progress file
5. **Handle errors**: Debug and fix any issues

### 3. Progress Reporting
- Update progress in: `{self.agents_dir}/{task.task_id}/progress.log`
- Mark completion: `touch {self.agents_dir}/{task.task_id}/completed`
- Report errors: `echo "ERROR: description" > {self.agents_dir}/{task.task_id}/error.log`

### 4. Available Tools
- Use all Cursor tools and capabilities
- Ask questions if you need clarification
- Explore the codebase as needed
- Use code generation and analysis features

### 5. Success Criteria
- Command executes successfully
- No errors in execution
- Progress is documented
- Completion is marked

## Context
This task is part of a larger workflow:
- **Dependencies**: {', '.join(task.dependencies) if task.dependencies else 'None'}
- **Estimated Duration**: {task.estimated_duration} minutes
- **Agent Workspace**: `{self.agents_dir}/{task.task_id}/`

## Notes
- You have full access to the project
- Work independently but report progress
- Be creative in your approach if needed
- Ask for help if you encounter blockers

---

**Ready to start? Begin by executing the primary command and reporting your progress.**
"""
        
        with open(instructions_file, 'w') as f:
            f.write(content)
    
    def _create_execution_script(self, task: Task, execution_script: Path) -> None:
        """Create a script to execute the task."""
        script_content = f"""#!/bin/bash
# Execution Script for Task: {task.name}

echo "🤖 Agent starting task: {task.name}"
echo "=================================="
echo ""

# Set up environment
cd "{task.working_directory}"
echo "📁 Working Directory: $(pwd)"
echo ""

# Create progress log
PROGRESS_LOG="{self.agents_dir}/{task.task_id}/progress.log"
echo "$(date): Agent started task {task.task_id}" > "$PROGRESS_LOG"

# Execute the command
echo "⚡ Executing command: {task.command}"
echo "$(date): Executing command: {task.command}" >> "$PROGRESS_LOG"

if {task.command}; then
    echo "✅ Command executed successfully"
    echo "$(date): Command executed successfully" >> "$PROGRESS_LOG"
    
    # Mark completion
    touch "{self.agents_dir}/{task.task_id}/completed"
    echo "$(date): Task completed successfully" >> "$PROGRESS_LOG"
    echo "🎉 Task {task.task_id} completed!"
else
    echo "❌ Command failed"
    echo "$(date): Command failed" >> "$PROGRESS_LOG"
    echo "ERROR: Command failed" > "{self.agents_dir}/{task.task_id}/error.log"
    exit 1
fi
"""
        
        with open(execution_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        execution_script.chmod(0o755)
    
    def _create_monitor_script(self, task: Task, monitor_script: Path) -> None:
        """Create a script to monitor task progress."""
        script_content = f"""#!/bin/bash
# Monitor Script for Task: {task.task_id}

echo "👀 Monitoring task: {task.name}"
echo "==============================="
echo ""

PROGRESS_LOG="{self.agents_dir}/{task.task_id}/progress.log"
COMPLETED_FILE="{self.agents_dir}/{task.task_id}/completed"
ERROR_FILE="{self.agents_dir}/{task.task_id}/error.log"

while true; do
    echo "📊 Status check at $(date)"
    
    if [ -f "$COMPLETED_FILE" ]; then
        echo "✅ Task completed!"
        break
    elif [ -f "$ERROR_FILE" ]; then
        echo "❌ Task failed!"
        cat "$ERROR_FILE"
        break
    else
        echo "⏳ Task in progress..."
        if [ -f "$PROGRESS_LOG" ]; then
            echo "📝 Latest progress:"
            tail -3 "$PROGRESS_LOG"
        fi
    fi
    
    echo ""
    sleep 5
done
"""
        
        with open(monitor_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        monitor_script.chmod(0o755)
    
    def launch_agent(self, task: Task) -> bool:
        """Launch a Cursor agent for a specific task."""
        try:
            workspace = self.create_agent_workspace(task)
            if not workspace:
                return False
            
            print(f"🤖 Launching Cursor agent for: {task.name}")
            print(f"   Task ID: {task.task_id}")
            print(f"   Agent Type: {task.agent_type}")
            print(f"   Working Directory: {task.working_directory}")
            print(f"   Workspace: {workspace['agent_dir']}")
            print("")
            
            # Store agent info
            self.active_agents[task.task_id] = {
                "task": task,
                "workspace": workspace,
                "started_at": time.time(),
                "status": "running"
            }
            
            print("💡 Agent Instructions:")
            print(f"   1. Open Cursor in: {workspace['agent_dir']}")
            print(f"   2. Read: {workspace['instructions_file']}")
            print(f"   3. Execute: bash {workspace['execution_script']}")
            print(f"   4. Monitor: bash {workspace['monitor_script']}")
            print("")
            print("🎯 The agent can work independently in its workspace!")
            
            return True
            
        except Exception as e:
            print(f"Error launching agent: {e}")
            return False
    
    def launch_multiple_agents(self, tasks: List[Task]) -> Dict[str, bool]:
        """Launch multiple agents for different tasks."""
        results = {}
        
        print(f"🚀 Launching {len(tasks)} Cursor agents...")
        print("=" * 50)
        
        for task in tasks:
            print(f"\n🤖 Agent {len(results) + 1}: {task.name}")
            results[task.task_id] = self.launch_agent(task)
        
        print(f"\n📊 Launch Summary:")
        print(f"   Total agents: {len(tasks)}")
        print(f"   Successful: {sum(results.values())}")
        print(f"   Failed: {len(tasks) - sum(results.values())}")
        
        return results
    
    def get_agent_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a specific agent."""
        if task_id not in self.active_agents:
            return {"status": "not_found"}
        
        agent_info = self.active_agents[task_id]
        workspace = agent_info["workspace"]
        
        # Check completion
        completed_file = Path(workspace["agent_dir"]) / "completed"
        error_file = Path(workspace["agent_dir"]) / "error.log"
        progress_file = Path(workspace["agent_dir"]) / "progress.log"
        
        status = "running"
        if completed_file.exists():
            status = "completed"
        elif error_file.exists():
            status = "failed"
        
        return {
            "task_id": task_id,
            "status": status,
            "workspace": workspace["agent_dir"],
            "started_at": agent_info["started_at"],
            "has_progress": progress_file.exists(),
            "has_error": error_file.exists()
        }
    
    def list_all_agents(self) -> List[Dict[str, Any]]:
        """List all active agents."""
        agents = []
        for task_id in self.active_agents:
            agents.append(self.get_agent_status(task_id))
        return agents
    
    def cleanup_completed_workspaces(self) -> List[str]:
        """Clean up completed agent workspaces."""
        cleaned_workspaces = []
        
        if not self.agents_dir.exists():
            return cleaned_workspaces
        
        for workspace_dir in self.agents_dir.iterdir():
            if not workspace_dir.is_dir():
                continue
            
            # Check if workspace is completed
            completed_file = workspace_dir / "completed"
            error_file = workspace_dir / "error.log"
            
            if completed_file.exists() or error_file.exists():
                try:
                    # Remove the entire workspace directory
                    import shutil
                    shutil.rmtree(workspace_dir)
                    cleaned_workspaces.append(workspace_dir.name)
                except Exception as e:
                    print(f"Warning: Could not clean up workspace {workspace_dir.name}: {e}")
        
        return cleaned_workspaces
