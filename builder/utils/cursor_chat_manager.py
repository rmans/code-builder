#!/usr/bin/env python3
"""
Cursor Chat Manager

This module manages Cursor chat sessions for task execution.
It provides a more realistic interface to Cursor's chat functionality.
"""

import os
import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from .task_orchestrator import Task, TaskStatus


@dataclass
class CursorChatSession:
    """Represents a Cursor chat session for a task."""
    task_id: str
    chat_id: str
    working_directory: str
    status: str = "active"  # active, completed, failed
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    process: Optional[subprocess.Popen] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class CursorChatManager:
    """Manages Cursor chat sessions for task execution."""
    
    def __init__(self, cache_dir: str = "builder/cache", cursor_executable: str = "cursor"):
        self.cache_dir = Path(cache_dir)
        self.sessions_dir = self.cache_dir / "cursor_chats"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.cursor_executable = cursor_executable
        
        self.active_sessions: Dict[str, CursorChatSession] = {}
        self.session_lock = threading.Lock()
    
    def create_task_chat(self, task: Task) -> Optional[CursorChatSession]:
        """Create a new Cursor chat session for a task."""
        try:
            # Generate unique chat ID
            chat_id = f"chat-{task.task_id}-{int(time.time())}"
            
            # Create session
            session = CursorChatSession(
                task_id=task.task_id,
                chat_id=chat_id,
                working_directory=task.working_directory
            )
            
            # Create task context file
            context_file = self.sessions_dir / f"{task.task_id}_context.json"
            context_data = {
                "task_id": task.task_id,
                "task_name": task.name,
                "description": task.description,
                "command": task.command,
                "working_directory": task.working_directory,
                "agent_type": task.agent_type,
                "dependencies": task.dependencies,
                "priority": task.priority,
                "estimated_duration": task.estimated_duration,
                "chat_id": chat_id,
                "created_at": session.created_at.isoformat()
            }
            
            with open(context_file, 'w') as f:
                json.dump(context_data, f, indent=2)
            
            # Create instruction file for the chat
            instruction_file = self.sessions_dir / f"{task.task_id}_instructions.md"
            self._create_chat_instructions(task, instruction_file)
            
            # Store session
            with self.session_lock:
                self.active_sessions[task.task_id] = session
            
            print(f"💬 Created Cursor chat for task: {task.name}")
            print(f"   Chat ID: {chat_id}")
            print(f"   Working Directory: {task.working_directory}")
            print(f"   Instructions: {instruction_file}")
            print(f"   Context: {context_file}")
            
            return session
            
        except Exception as e:
            print(f"Error creating Cursor chat for {task.task_id}: {e}")
            return None
    
    def _create_chat_instructions(self, task: Task, instruction_file: Path) -> None:
        """Create detailed instructions for the Cursor chat."""
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
You are working in a Cursor chat specifically for this task. Please:

1. **Execute the command**: `{task.command}`
2. **Verify completion**: Ensure the task completes successfully
3. **Report progress**: Keep me updated on your progress
4. **Handle errors**: If there are issues, debug and fix them
5. **Create completion marker**: When done, run:
   ```bash
   touch {self.sessions_dir}/{task.task_id}_completed
   ```

## Context
This task is part of a larger workflow:
- **Dependencies**: {', '.join(task.dependencies) if task.dependencies else 'None'}
- **Priority**: {task.priority}
- **Estimated Duration**: {task.estimated_duration} minutes

## Available Tools
- Use all Cursor tools and capabilities
- Ask questions if you need clarification
- Feel free to explore the codebase
- Use code generation and analysis features

## Notes
- You have full access to the project
- Work in the specified working directory
- Report any issues or blockers
- Be creative in your approach if needed

---

**Ready to start? Please confirm you understand the task and begin execution.**
"""
        
        with open(instruction_file, 'w') as f:
            f.write(instruction_content)
    
    def open_cursor_chat(self, session: CursorChatSession) -> bool:
        """Open Cursor with the task chat session."""
        try:
            # Create a script that opens Cursor and provides instructions for creating a new chat
            script_file = self.sessions_dir / f"{session.task_id}_open_cursor.sh"
            
            script_content = f"""#!/bin/bash
# Open Cursor with task context
cd "{session.working_directory}"

# Display task information
echo "🤖 Opening Cursor for task: {session.task_id}"
echo "📁 Working Directory: {session.working_directory}"
echo "💬 Chat ID: {session.chat_id}"
echo ""
echo "📋 Task Instructions:"
echo "===================="
cat "{self.sessions_dir}/{session.task_id}_instructions.md"
echo ""
echo "🚀 Starting Cursor..."
echo ""
echo "💡 INSTRUCTIONS:"
echo "1. Cursor will open in a new window"
echo "2. Press Ctrl+T to create a new chat"
echo "3. Copy and paste the task instructions above into the chat"
echo "4. Work through the task with the Cursor agent"
echo "5. When complete, run: touch {self.sessions_dir}/{session.task_id}_completed"
echo ""

# Open Cursor
cursor .
"""
            
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            script_file.chmod(0o755)
            
            # Open Cursor directly
            try:
                subprocess.Popen([self.cursor_executable, session.working_directory])
                print(f"🚀 Opened Cursor for task: {session.task_id}")
                print(f"   Working Directory: {session.working_directory}")
                print(f"   Instructions: {self.sessions_dir}/{session.task_id}_instructions.md")
                print("")
                print("💡 Next steps:")
                print("1. Press Ctrl+T in Cursor to create a new chat")
                print("2. Copy the task instructions from the terminal output above")
                print("3. Paste them into the new chat")
                print("4. Work through the task with the Cursor agent")
                print(f"5. When complete, run: touch {self.sessions_dir}/{session.task_id}_completed")
                return True
            except Exception as e:
                print(f"Error opening Cursor directly: {e}")
                return False
            
        except Exception as e:
            print(f"Error opening Cursor chat: {e}")
            return False
    
    def check_task_completion(self, task_id: str) -> bool:
        """Check if a task has been completed by checking for completion marker."""
        completion_file = self.sessions_dir / f"{task_id}_completed"
        return completion_file.exists()
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task."""
        try:
            completion_file = self.sessions_dir / f"{task_id}_completed"
            if not completion_file.exists():
                return None
            
            # Read completion data
            result = {
                "task_id": task_id,
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "completion_file": str(completion_file)
            }
            
            # Try to read additional result data
            result_file = self.sessions_dir / f"{task_id}_result.json"
            if result_file.exists():
                with open(result_file, 'r') as f:
                    additional_data = json.load(f)
                    result.update(additional_data)
            
            return result
            
        except Exception as e:
            print(f"Error getting task result: {e}")
            return None
    
    def close_chat_session(self, task_id: str) -> bool:
        """Close a Cursor chat session."""
        try:
            with self.session_lock:
                if task_id in self.active_sessions:
                    session = self.active_sessions[task_id]
                    session.status = "completed"
                    session.completed_at = datetime.now()
                    del self.active_sessions[task_id]
                    return True
            return False
        except Exception as e:
            print(f"Error closing chat session: {e}")
            return False
    
    def list_active_sessions(self) -> List[CursorChatSession]:
        """List all active Cursor chat sessions."""
        with self.session_lock:
            return list(self.active_sessions.values())
    
    def get_session_info(self, task_id: str) -> Optional[CursorChatSession]:
        """Get information about a specific chat session."""
        with self.session_lock:
            return self.active_sessions.get(task_id)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old chat sessions."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in self.sessions_dir.glob("*_context.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        created_at = datetime.fromisoformat(data['created_at'])
                        
                        if created_at < cutoff_time:
                            task_id = data['task_id']
                            
                            # Remove related files
                            for pattern in [f"{task_id}_*"]:
                                for old_file in self.sessions_dir.glob(pattern):
                                    old_file.unlink()
                            
                            cleaned_count += 1
                            
                except Exception:
                    continue
            
            if cleaned_count > 0:
                print(f"🧹 Cleaned up {cleaned_count} old chat sessions")
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0
