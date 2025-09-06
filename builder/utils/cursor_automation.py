#!/usr/bin/env python3
"""
Cursor Automation

This module provides automation for Cursor chat creation and task execution.
It can send keystrokes and commands to Cursor to automate the chat creation process.
"""

import os
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from .task_orchestrator import Task


class CursorAutomation:
    """Automates Cursor operations for task execution."""
    
    def __init__(self, cursor_executable: str = "cursor"):
        self.cursor_executable = cursor_executable
        self.cache_dir = Path("builder/cache/cursor_automation")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def create_task_chat_automation(self, task: Task) -> Dict[str, Any]:
        """Create automation script for a task chat."""
        try:
            # Create automation script
            script_file = self.cache_dir / f"{task.task_id}_automation.py"
            
            # Create instruction file path
            instruction_file = Path(f"builder/cache/cursor_chats/{task.task_id}_instructions.md")
            
            script_content = f'''#!/usr/bin/env python3
"""
Automation script for task: {task.name}
Task ID: {task.task_id}
"""

import time
import subprocess
import os
from pathlib import Path

def automate_cursor_chat():
    """Automate Cursor chat creation for task."""
    print("🤖 Starting Cursor automation for task: {task.name}")
    
    # Open Cursor
    print("🚀 Opening Cursor...")
    subprocess.Popen(["{self.cursor_executable}", "{task.working_directory}"])
    
    # Wait for Cursor to open
    print("⏳ Waiting for Cursor to open...")
    time.sleep(3)
    
    # Display instructions
    print("📋 Task Instructions:")
    print("=" * 50)
    
    if Path("{instruction_file}").exists():
        with open("{instruction_file}", "r") as f:
            instructions = f.read()
            print(instructions)
    else:
        print("Task instructions not found")
    
    print("=" * 50)
    print("")
    print("💡 Manual Steps Required:")
    print("1. Press Ctrl+T in Cursor to create a new chat")
    print("2. Copy the instructions above and paste them into the chat")
    print("3. Work through the task with the Cursor agent")
    print("4. When complete, run: touch {self.cache_dir}/{task.task_id}_completed")
    print("")
    print("🎯 Task Details:")
    print(f"   Task ID: {task.task_id}")
    print(f"   Name: {task.name}")
    print(f"   Command: {task.command}")
    print(f"   Working Directory: {task.working_directory}")
    print(f"   Agent Type: {task.agent_type}")
    print(f"   Priority: {task.priority}")
    print(f"   Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
    
    return True

if __name__ == "__main__":
    automate_cursor_chat()
'''
            
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            script_file.chmod(0o755)
            
            # Create a simple launcher script
            launcher_file = self.cache_dir / f"{task.task_id}_launcher.sh"
            launcher_content = f'''#!/bin/bash
# Launcher for task: {task.name}
cd "{task.working_directory}"
python3 "{script_file.absolute()}"
'''
            
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            
            launcher_file.chmod(0o755)
            
            return {
                "script_file": str(script_file),
                "launcher_file": str(launcher_file),
                "instruction_file": str(instruction_file),
                "task_id": task.task_id,
                "task_name": task.name
            }
            
        except Exception as e:
            print(f"Error creating automation: {e}")
            return None
    
    def run_task_automation(self, task: Task) -> bool:
        """Run automation for a specific task."""
        try:
            automation_info = self.create_task_chat_automation(task)
            if not automation_info:
                return False
            
            # Run the automation script
            launcher_file = automation_info["launcher_file"]
            subprocess.Popen(['bash', launcher_file])
            
            print(f"✅ Started automation for task: {task.name}")
            print(f"   Launcher: {launcher_file}")
            print(f"   Instructions: {automation_info['instruction_file']}")
            
            return True
            
        except Exception as e:
            print(f"Error running automation: {e}")
            return False
    
    def create_workflow_guide(self, tasks: List[Task]) -> str:
        """Create a workflow guide for multiple tasks."""
        guide_file = self.cache_dir / "workflow_guide.md"
        
        guide_content = f"""# Cursor Task Workflow Guide

## Overview
This guide helps you execute tasks using Cursor agents with proper chat management.

## Tasks to Execute
"""
        
        for i, task in enumerate(tasks, 1):
            guide_content += f"""
### {i}. {task.name}
- **Task ID**: {task.task_id}
- **Agent Type**: {task.agent_type}
- **Command**: `{task.command}`
- **Working Directory**: {task.working_directory}
- **Dependencies**: {', '.join(task.dependencies) if task.dependencies else 'None'}
- **Priority**: {task.priority}

#### Instructions:
1. Open Cursor in the working directory: `cd {task.working_directory} && cursor .`
2. Press **Ctrl+T** to create a new chat
3. Copy the task instructions from: `builder/cache/cursor_chats/{task.task_id}_instructions.md`
4. Paste the instructions into the new chat
5. Work through the task with the Cursor agent
6. When complete, create the completion marker:
   ```bash
   touch builder/cache/cursor_chats/{task.task_id}_completed
   ```

---
"""
        
        guide_content += """
## Workflow Tips

### For Each Task:
1. **Open Cursor**: Always open Cursor in the task's working directory
2. **New Chat**: Use Ctrl+T to create a fresh chat for each task
3. **Copy Instructions**: Use the instruction files as a starting point
4. **Work Collaboratively**: Let the Cursor agent help you execute the task
5. **Mark Complete**: Always create the completion marker when done

### Parallel Execution:
- You can work on multiple tasks simultaneously
- Each task gets its own Cursor window and chat
- Dependencies are automatically managed by the orchestrator

### Monitoring Progress:
```bash
# Check task status
python3 builder/core/cli.py orchestrator:cursor-chat-status

# Check orchestrator status
python3 builder/core/cli.py orchestrator:status
```

## Troubleshooting

### If Cursor doesn't open:
- Check if Cursor is installed: `which cursor`
- Try opening manually: `cursor .`

### If chat creation fails:
- Use Ctrl+T in Cursor to create new chat
- Copy instructions manually from the instruction files

### If completion isn't detected:
- Ensure you create the completion marker file
- Check the file path is correct
- Verify the orchestrator is monitoring the right directory
"""
        
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        return str(guide_file)
