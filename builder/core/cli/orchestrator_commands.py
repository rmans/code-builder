#!/usr/bin/env python3
"""
Orchestrator Commands Module

This module contains orchestrator-related commands like orchestrator:*
"""

import click
import os
import sys
import time
import uuid
from .base import cli, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    CACHE = ROOT / ".cb" / "cache"

def _get_task_orchestrator():
    """Get TaskOrchestrator instance."""
    try:
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        from utils.task_orchestrator import TaskOrchestrator
        return TaskOrchestrator()
    except ImportError:
        click.echo("❌ TaskOrchestrator not available. Make sure utils/task_orchestrator.py exists.")
        raise SystemExit(1)

# Orchestrator Commands
@cli.command("orchestrator:add-task")
@click.option("--name", required=True, help="Task name")
@click.option("--description", required=True, help="Task description")
@click.option("--command", required=True, help="Command to execute")
@click.option("--working-dir", default=".", help="Working directory")
@click.option("--dependencies", multiple=True, help="Task dependencies (task IDs)")
@click.option("--estimated-duration", default=10, help="Estimated duration in minutes")
@click.option("--priority", default=1, help="Task priority (higher = more important)")
@click.option("--agent-type", required=True, help="Type of agent needed")
def orchestrator_add_task(name, description, command, working_dir, dependencies, estimated_duration, priority, agent_type):
    """Add a new task to the orchestrator."""
    try:
        orchestrator = _get_task_orchestrator()
        
        # Generate unique task ID
        task_id = f"task-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        
        # Create task object (simplified for now)
        task = {
            'task_id': task_id,
            'name': name,
            'description': description,
            'command': command,
            'working_directory': os.path.abspath(working_dir),
            'dependencies': list(dependencies),
            'estimated_duration': estimated_duration,
            'priority': priority,
            'agent_type': agent_type
        }
        
        # Add task to orchestrator
        orchestrator.add_task(task)
        
        click.echo(f"✅ Added task: {task_id}")
        click.echo(f"   Name: {name}")
        click.echo(f"   Agent Type: {agent_type}")
        click.echo(f"   Dependencies: {', '.join(dependencies) if dependencies else 'None'}")
        click.echo(f"   Priority: {priority}")
        
    except Exception as e:
        click.echo(f"❌ Error adding task: {e}")
        raise click.Abort()

@cli.command("orchestrator:add-agent")
@click.option("--agent-id", required=True, help="Agent identifier")
@click.option("--agent-type", required=True, help="Type of agent")
@click.option("--capabilities", multiple=True, help="Agent capabilities")
@click.option("--max-concurrent", default=1, help="Maximum concurrent tasks")
def orchestrator_add_agent(agent_id, agent_type, capabilities, max_concurrent):
    """Add a new agent to the orchestrator."""
    try:
        orchestrator = _get_task_orchestrator()
        
        # Create agent object (simplified for now)
        agent = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'capabilities': list(capabilities),
            'max_concurrent_tasks': max_concurrent
        }
        
        # Add agent to orchestrator
        orchestrator.add_agent(agent)
        
        click.echo(f"✅ Added agent: {agent_id}")
        click.echo(f"   Type: {agent_type}")
        click.echo(f"   Capabilities: {', '.join(capabilities) if capabilities else 'None'}")
        click.echo(f"   Max Concurrent: {max_concurrent}")
        
    except Exception as e:
        click.echo(f"❌ Error adding agent: {e}")
        raise click.Abort()

@cli.command("orchestrator:status")
def orchestrator_status():
    """Show orchestrator status and task information."""
    try:
        orchestrator = _get_task_orchestrator()
        summary = orchestrator.get_status_summary()
        
        click.echo("🎯 Orchestrator Status")
        click.echo("=" * 50)
        click.echo(f"Total Tasks: {summary.get('total_tasks', 0)}")
        click.echo(f"Pending Tasks: {summary.get('pending_tasks', 0)}")
        click.echo(f"Running Tasks: {summary.get('running_tasks', 0)}")
        click.echo(f"Completed Tasks: {summary.get('completed_tasks', 0)}")
        click.echo(f"Failed Tasks: {summary.get('failed_tasks', 0)}")
        click.echo(f"Total Agents: {summary.get('total_agents', 0)}")
        click.echo(f"Available Agents: {summary.get('available_agents', 0)}")
        
        # Show recent tasks
        recent_tasks = summary.get('recent_tasks', [])
        if recent_tasks:
            click.echo(f"\n📋 Recent Tasks:")
            for task in recent_tasks[:5]:  # Show last 5
                status_emoji = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(task.get('status', 'pending'), '❓')
                
                click.echo(f"   {status_emoji} {task.get('name', 'Unknown')} ({task.get('status', 'unknown')})")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}")
        raise click.Abort()

@cli.command("orchestrator:run")
@click.option("--max-cycles", type=int, help="Maximum number of orchestration cycles")
@click.option("--cycle-delay", default=5.0, help="Delay between cycles in seconds")
@click.option("--single-cycle", is_flag=True, help="Run only one orchestration cycle")
def orchestrator_run(max_cycles, cycle_delay, single_cycle):
    """Run the orchestrator to execute tasks."""
    try:
        orchestrator = _get_task_orchestrator()
        
        # Check for circular dependencies
        cycles = orchestrator.detect_cycles()
        if cycles:
            click.echo(f"❌ Circular dependencies detected: {cycles}")
            raise click.Abort()
        
        if single_cycle:
            click.echo("🔄 Running single orchestration cycle...")
            cycle_info = orchestrator.run_orchestration_cycle()
            click.echo(f"✅ Cycle complete: {cycle_info.get('tasks_assigned', 0)} assigned, {cycle_info.get('tasks_completed', 0)} completed")
        else:
            click.echo("🚀 Starting continuous orchestration...")
            cycles_run = orchestrator.run_continuous(max_cycles, cycle_delay)
            click.echo(f"✅ Orchestration complete after {cycles_run} cycles")
        
    except Exception as e:
        click.echo(f"❌ Error running orchestrator: {e}")
        raise click.Abort()

@cli.command("orchestrator:execution-order")
def orchestrator_execution_order():
    """Show the optimal execution order for tasks."""
    try:
        orchestrator = _get_task_orchestrator()
        
        execution_order = orchestrator.get_execution_order()
        
        if not execution_order:
            click.echo("❌ No valid execution order found (circular dependencies)")
            return
        
        click.echo("📋 Optimal Execution Order:")
        click.echo("=" * 50)
        
        for level, task_ids in enumerate(execution_order, 1):
            click.echo(f"\nLevel {level} (can run in parallel):")
            for task_id in task_ids:
                if task_id in orchestrator.tasks:
                    task = orchestrator.tasks[task_id]
                    click.echo(f"   • {task_id}: {task.get('name', 'Unknown')} ({task.get('agent_type', 'unknown')})")
        
    except Exception as e:
        click.echo(f"❌ Error getting execution order: {e}")
        raise click.Abort()

@cli.command("orchestrator:reset")
@click.option("--confirm", is_flag=True, help="Confirm reset")
def orchestrator_reset(confirm):
    """Reset the orchestrator state."""
    if not confirm:
        click.echo("❌ Use --confirm to reset orchestrator state")
        raise click.Abort()
    
    try:
        orchestrator = _get_task_orchestrator()
        orchestrator.reset()
        click.echo("✅ Orchestrator state reset")
        
    except Exception as e:
        click.echo(f"❌ Error resetting orchestrator: {e}")
        raise click.Abort()

# Placeholder for other orchestrator commands - will be implemented in next iteration
@cli.command("orchestrator:load-tasks")
@click.option("--tasks-dir", default="cb_docs/tasks", help="Directory containing TASK-*.md files")
def orchestrator_load_tasks(tasks_dir):
    """Load tasks from task files - to be implemented."""
    click.echo(f"📋 Loading tasks from {tasks_dir} - to be implemented")
    return 0

@cli.command("orchestrator:execute-tasks")
@click.option("--tasks-dir", default="cb_docs/tasks", help="Directory containing TASK-*.md files")
def orchestrator_execute_tasks(tasks_dir):
    """Execute tasks from task files - to be implemented."""
    click.echo(f"🚀 Executing tasks from {tasks_dir} - to be implemented")
    return 0

@cli.command("orchestrator:create-task-template")
@click.option("--title", required=True, help="Task title")
def orchestrator_create_task_template(title):
    """Create a task template - to be implemented."""
    click.echo(f"📝 Creating task template: {title} - to be implemented")
    return 0

@cli.command("orchestrator:multi-agent")
@click.option("--task-ids", help="Comma-separated list of task IDs to launch agents for")
def orchestrator_multi_agent(task_ids):
    """Launch multi-agent execution - to be implemented."""
    click.echo(f"🤖 Launching multi-agent execution for {task_ids} - to be implemented")
    return 0

@cli.command("orchestrator:add-task-abc")
@click.option("--name", required=True, help="Task name")
def orchestrator_add_task_abc(name):
    """Add ABC iteration task - to be implemented."""
    click.echo(f"🔄 Adding ABC iteration task: {name} - to be implemented")
    return 0

@cli.command("orchestrator:run-abc")
@click.option("--max-cycles", type=int, help="Maximum number of orchestration cycles")
def orchestrator_run_abc(max_cycles):
    """Run ABC iteration orchestration - to be implemented."""
    click.echo(f"🔄 Running ABC iteration orchestration - to be implemented")
    return 0

@cli.command("orchestrator:abc-status")
def orchestrator_abc_status():
    """Show ABC iteration status - to be implemented."""
    click.echo("📊 ABC iteration status - to be implemented")
    return 0
