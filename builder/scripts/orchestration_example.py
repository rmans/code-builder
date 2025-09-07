#!/usr/bin/env python3
"""
Orchestration System Example

This script demonstrates how to use the task orchestration system
to manage complex workflows with dependencies.
"""

import os
import sys
import time
from pathlib import Path

# Add the builder directory to the path
builder_dir = Path(__file__).parent.parent
sys.path.insert(0, str(builder_dir))

from utils.task_orchestrator import TaskOrchestrator, Task, Agent, TaskStatus, AgentStatus


def create_example_tasks():
    """Create a set of example tasks with dependencies."""
    orchestrator = TaskOrchestrator()
    
    # Clear any existing tasks
    orchestrator.tasks.clear()
    orchestrator.agents.clear()
    orchestrator.save_state()
    
    # Create tasks with dependencies
    tasks = [
        Task(
            task_id="setup-project",
            name="Setup Project Structure",
            description="Create basic project directories and files",
            command="mkdir -p src tests docs && echo 'Project setup complete' > setup.log",
            working_directory=".",
            dependencies=[],
            estimated_duration=2,
            priority=10,
            agent_type="setup"
        ),
        Task(
            task_id="install-deps",
            name="Install Dependencies",
            description="Install project dependencies",
            command="npm install && pip install -r requirements.txt",
            working_directory=".",
            dependencies=["setup-project"],
            estimated_duration=5,
            priority=9,
            agent_type="setup"
        ),
        Task(
            task_id="create-api",
            name="Create API Endpoints",
            description="Implement REST API endpoints",
            command="echo 'API created' > src/api.py",
            working_directory=".",
            dependencies=["install-deps"],
            estimated_duration=15,
            priority=8,
            agent_type="backend"
        ),
        Task(
            task_id="create-frontend",
            name="Create Frontend Components",
            description="Build React components",
            command="echo 'Frontend created' > src/components.jsx",
            working_directory=".",
            dependencies=["install-deps"],
            estimated_duration=20,
            priority=7,
            agent_type="frontend"
        ),
        Task(
            task_id="write-tests",
            name="Write Unit Tests",
            description="Create comprehensive test suite",
            command="echo 'Tests written' > tests/test_suite.py",
            working_directory=".",
            dependencies=["create-api", "create-frontend"],
            estimated_duration=10,
            priority=6,
            agent_type="testing"
        ),
        Task(
            task_id="create-docs",
            name="Create Documentation",
            description="Generate API and user documentation",
            command="echo 'Docs created' > cb_docs/README.md",
            working_directory=".",
            dependencies=["create-api"],
            estimated_duration=8,
            priority=5,
            agent_type="docs"
        ),
        Task(
            task_id="deploy",
            name="Deploy Application",
            description="Deploy to production environment",
            command="echo 'Deployed' > deploy.log",
            working_directory=".",
            dependencies=["write-tests", "create-docs"],
            estimated_duration=5,
            priority=4,
            agent_type="deployment"
        )
    ]
    
    # Add tasks to orchestrator
    for task in tasks:
        orchestrator.add_task(task)
    
    return orchestrator


def create_example_agents():
    """Create example agents for different task types."""
    orchestrator = TaskOrchestrator()
    
    agents = [
        Agent(
            agent_id="setup-agent-1",
            agent_type="setup",
            capabilities=["project-setup", "dependency-management"],
            max_concurrent_tasks=2
        ),
        Agent(
            agent_id="backend-agent-1",
            agent_type="backend",
            capabilities=["api-development", "database-design"],
            max_concurrent_tasks=1
        ),
        Agent(
            agent_id="frontend-agent-1",
            agent_type="frontend",
            capabilities=["react", "ui-design", "responsive-layout"],
            max_concurrent_tasks=1
        ),
        Agent(
            agent_id="testing-agent-1",
            agent_type="testing",
            capabilities=["unit-testing", "integration-testing", "e2e-testing"],
            max_concurrent_tasks=2
        ),
        Agent(
            agent_id="docs-agent-1",
            agent_type="docs",
            capabilities=["technical-writing", "api-documentation"],
            max_concurrent_tasks=1
        ),
        Agent(
            agent_id="deployment-agent-1",
            agent_type="deployment",
            capabilities=["docker", "kubernetes", "ci-cd"],
            max_concurrent_tasks=1
        )
    ]
    
    # Add agents to orchestrator
    for agent in agents:
        orchestrator.add_agent(agent)
    
    return orchestrator


def demonstrate_orchestration():
    """Demonstrate the orchestration system."""
    print("🎯 Task Orchestration System Demo")
    print("=" * 50)
    
    # Create tasks and agents
    orchestrator = create_example_tasks()
    orchestrator = create_example_agents()
    
    # Show initial status
    print("\n📋 Initial Status:")
    summary = orchestrator.get_status_summary()
    print(f"Tasks: {summary['tasks']['total']}")
    print(f"Agents: {summary['agents']['total']}")
    print(f"Ready Tasks: {summary['ready_tasks']}")
    print(f"Available Agents: {summary['available_agents']}")
    
    # Show execution order
    print("\n📋 Execution Order:")
    execution_order = orchestrator.get_execution_order()
    for level, task_ids in enumerate(execution_order, 1):
        print(f"\nLevel {level} (can run in parallel):")
        for task_id in task_ids:
            if task_id in orchestrator.tasks:
                task = orchestrator.tasks[task_id]
                print(f"   • {task.name} ({task.agent_type})")
    
    # Check for circular dependencies
    cycles = orchestrator.detect_cycles()
    if cycles:
        print(f"\n❌ Circular dependencies detected: {cycles}")
        return
    else:
        print("\n✅ No circular dependencies detected")
    
    # Run orchestration cycles
    print("\n🚀 Running Orchestration Cycles:")
    print("-" * 30)
    
    max_cycles = 10
    for cycle in range(1, max_cycles + 1):
        cycle_info = orchestrator.run_orchestration_cycle()
        
        print(f"Cycle {cycle}: {cycle_info['tasks_assigned']} assigned, "
              f"{cycle_info['tasks_completed']} completed, "
              f"{cycle_info['tasks_failed']} failed")
        
        # Show assignments
        if cycle_info['assignments']:
            for assignment in cycle_info['assignments']:
                print(f"   → {assignment['task_name']} → {assignment['agent_id']}")
        
        # Check if all tasks are complete
        pending_tasks = [t for t in orchestrator.tasks.values() 
                        if t.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]]
        if not pending_tasks:
            print("\n✅ All tasks completed!")
            break
        
        # Small delay between cycles
        time.sleep(1)
    
    # Show final status
    print("\n📊 Final Status:")
    summary = orchestrator.get_status_summary()
    for status, count in summary['tasks']['by_status'].items():
        if count > 0:
            print(f"   {status.title()}: {count}")
    
    # Show execution history
    print("\n📋 Execution History:")
    for entry in orchestrator.execution_history:
        status_emoji = "✅" if entry['status'] == 'completed' else "❌"
        print(f"   {status_emoji} {entry['task_id']} by {entry['agent_id']}")


def demonstrate_dependency_management():
    """Demonstrate dependency management features."""
    print("\n🔗 Dependency Management Demo")
    print("=" * 50)
    
    orchestrator = create_example_tasks()
    
    # Show task dependencies
    print("\n📋 Task Dependencies:")
    for task_id, task in orchestrator.tasks.items():
        if task.dependencies:
            print(f"{task.name}:")
            for dep_id in task.dependencies:
                dep_task = orchestrator.tasks[dep_id]
                print(f"   → depends on: {dep_task.name}")
        else:
            print(f"{task.name}: (no dependencies)")
    
    # Show what depends on each task
    print("\n📋 What Depends On Each Task:")
    for task_id, task in orchestrator.tasks.items():
        dependents = orchestrator.get_task_dependencies(task_id)
        if dependents:
            print(f"{task.name}:")
            for dep_id in dependents:
                dep_task = orchestrator.tasks[dep_id]
                print(f"   ← {dep_task.name}")
        else:
            print(f"{task.name}: (nothing depends on this)")


if __name__ == "__main__":
    demonstrate_orchestration()
    demonstrate_dependency_management()
