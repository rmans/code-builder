#!/usr/bin/env python3
"""
Example script showing how to use the agent tracking system.

This demonstrates how multiple agents can work concurrently without
interfering with each other's files during cleanup.
"""

import os
import sys
import time
from pathlib import Path

# Add the builder directory to the path
builder_dir = Path(__file__).parent.parent
sys.path.insert(0, str(builder_dir))

from utils.agent_tracker import AgentTracker, track_file_creation, set_current_session_id


def simulate_agent_work(agent_id: str, task: str, duration: int = 5):
    """Simulate an agent working on a task."""
    print(f"🤖 Agent {agent_id} starting work on: {task}")
    
    # Start agent session
    tracker = AgentTracker()
    session_id = tracker.create_session(agent_id, task)
    set_current_session_id(session_id)
    
    print(f"   Session ID: {session_id}")
    
    # Simulate creating files
    work_dir = Path(f"temp_work_{agent_id}")
    work_dir.mkdir(exist_ok=True)
    
    files_created = []
    for i in range(3):
        file_path = work_dir / f"{agent_id}_file_{i}.txt"
        file_path.write_text(f"Content created by {agent_id} for task: {task}")
        files_created.append(str(file_path))
        
        # Track the file creation
        track_file_creation(str(file_path))
        print(f"   Created: {file_path}")
        
        time.sleep(1)  # Simulate work
    
    # Simulate some work time
    print(f"   Working for {duration} seconds...")
    time.sleep(duration)
    
    # Complete the session
    tracker.complete_session(session_id)
    print(f"✅ Agent {agent_id} completed work")
    
    return files_created


def main():
    """Demonstrate concurrent agent work."""
    print("🚀 Starting concurrent agent simulation")
    print()
    
    # Simulate multiple agents working concurrently
    agents = [
        ("agent-1", "Implement user authentication", 3),
        ("agent-2", "Create API documentation", 4),
        ("agent-3", "Add unit tests", 2),
    ]
    
    # Start all agents
    for agent_id, task, duration in agents:
        simulate_agent_work(agent_id, task, duration)
        print()
    
    # Show current sessions
    print("📋 Current agent sessions:")
    tracker = AgentTracker()
    sessions = tracker.list_sessions()
    
    for session in sessions:
        status_emoji = {
            'active': '🟢',
            'completed': '✅',
            'failed': '❌',
            'timeout': '⏰'
        }.get(session.status, '❓')
        
        print(f"{status_emoji} {session.agent_id}: {session.task_description}")
        print(f"   Status: {session.status}")
        print(f"   Files: {len(session.created_files)}")
        print()
    
    # Demonstrate cleanup with agent protection
    print("🧹 Testing cleanup with agent protection:")
    from utils.cleanup_rules import ArtifactCleaner
    
    cleaner = ArtifactCleaner(respect_agent_ownership=True)
    artifacts = cleaner.find_artifacts(dry_run=True)
    
    print("Files that would be cleaned up (respecting agent ownership):")
    for rule_name, files in artifacts.items():
        if files:
            print(f"  {rule_name}: {len(files)} files")
            for file_path in files:
                print(f"    - {file_path}")
    
    print()
    print("💡 Notice: Files created by active agents are protected from cleanup!")


if __name__ == "__main__":
    main()
