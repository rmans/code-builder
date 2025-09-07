#!/usr/bin/env python3
"""
Cursor Agent Integration Example

This script demonstrates how to use Cursor agents for task execution
instead of simple shell commands.
"""

import os
import sys
from pathlib import Path

# Add the builder directory to the path
builder_dir = Path(__file__).parent.parent
sys.path.insert(0, str(builder_dir))

from utils.cursor_agent_integration import CursorAgentOrchestrator, CursorAgent
from utils.task_parser import TaskFileParser


def demonstrate_cursor_agents():
    """Demonstrate Cursor agent orchestration."""
    print("🤖 Cursor Agent Integration Demo")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = CursorAgentOrchestrator()
    
    # Add Cursor agents
    print("\n🔧 Setting up Cursor agents...")
    orchestrator.add_cursor_agent("cursor-setup-agent", "setup", ["project-setup", "configuration"])
    orchestrator.add_cursor_agent("cursor-backend-agent", "backend", ["api-development", "database-design"])
    orchestrator.add_cursor_agent("cursor-frontend-agent", "frontend", ["react", "ui-design", "responsive-layout"])
    orchestrator.add_cursor_agent("cursor-testing-agent", "testing", ["unit-testing", "integration-testing"])
    orchestrator.add_cursor_agent("cursor-docs-agent", "docs", ["technical-writing", "api-documentation"])
    
    print("✅ Cursor agents configured")
    
    # Load tasks from files
    print("\n📋 Loading tasks from TASK-*.md files...")
    parser = TaskFileParser("cb_docs/tasks")
    orchestrator_tasks = parser.load_tasks_from_files()
    
    for task in orchestrator_tasks:
        orchestrator.base_orchestrator.add_task(task)
    
    print(f"✅ Loaded {len(orchestrator_tasks)} tasks")
    
    # Show execution order
    execution_order = orchestrator.base_orchestrator.get_execution_order()
    if execution_order:
        print("\n📋 Execution Order (using Cursor agents):")
        for level, task_ids in enumerate(execution_order, 1):
            print(f"\nLevel {level} (can run in parallel):")
            for task_id in task_ids:
                if task_id in orchestrator.base_orchestrator.tasks:
                    task = orchestrator.base_orchestrator.tasks[task_id]
                    print(f"   • {task.name} ({task.agent_type}) → Cursor agent")
    
    # Show how Cursor agents would receive tasks
    print("\n💡 How Cursor agents receive tasks:")
    for task in orchestrator_tasks:
        print(f"\n📄 Task: {task.name}")
        print(f"   Agent Type: {task.agent_type}")
        print(f"   Command: {task.command}")
        print(f"   Working Dir: {task.working_directory}")
        print(f"   Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
        
        # Show what instruction file would be created
        instruction_file = f"builder/cache/cursor_sessions/{task.task_id}_instructions.md"
        print(f"   Instruction File: {instruction_file}")
        print(f"   → Cursor agent would receive detailed instructions")
        print(f"   → Agent would execute the task intelligently")
        print(f"   → Agent would report completion status")
    
    print("\n🚀 To run with actual Cursor agents:")
    print("python3 builder/core/cli.py orchestrator:cursor-execute --auto-load")
    print("\n💡 Note: This requires Cursor to be installed and accessible")


def show_cursor_agent_benefits():
    """Show the benefits of using Cursor agents."""
    print("\n🎯 Benefits of Cursor Agent Integration:")
    print("=" * 50)
    
    benefits = [
        "🧠 Intelligent Execution: Cursor agents can understand context and make decisions",
        "🔧 Tool Usage: Agents can use Cursor's built-in tools and functions",
        "📝 Code Generation: Agents can write and modify code as needed",
        "🔍 Analysis: Agents can analyze files and understand project structure",
        "🔄 Iterative Improvement: Agents can refine solutions based on feedback",
        "📊 Progress Tracking: Agents can provide detailed progress reports",
        "🛠️ Error Handling: Agents can debug and fix issues intelligently",
        "📚 Learning: Agents can learn from previous tasks and improve",
        "🎨 Creative Solutions: Agents can come up with creative approaches",
        "🔗 Integration: Agents can integrate with other tools and services"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n🆚 Comparison:")
    print("   Shell Commands: Execute fixed commands, limited flexibility")
    print("   Cursor Agents: Intelligent execution, adaptive, creative")


if __name__ == "__main__":
    demonstrate_cursor_agents()
    show_cursor_agent_benefits()
