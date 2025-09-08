#!/usr/bin/env python3
"""
Orchestrator Commands

This module provides CLI commands for task orchestration, including execution,
filtering, and result management.
"""

import json
import click
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base import cli
from ...utils.task_orchestrator import TaskOrchestrator, Task, TaskStatus
from ...core.task_index import TaskIndexManager


class OrchestratorRunner:
    """CLI runner for task orchestration."""
    
    def __init__(self):
        self.orchestrator = TaskOrchestrator()
        self.task_index_manager = TaskIndexManager()
        self.results_dir = Path("cb_docs/tasks/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_tasks_from_index(self, 
                             filter_tags: List[str] = None,
                             priority_min: int = None,
                             task_ids: List[str] = None) -> List[Task]:
        """Load tasks from task index with filtering."""
        try:
            # Load task index
            index_data = self.task_index_manager.load_index()
            tasks = []
            
            for task_data in index_data.get('tasks', []):
                # Apply filters
                if filter_tags and not any(tag in task_data.get('tags', []) for tag in filter_tags):
                    continue
                
                if priority_min and task_data.get('priority', 0) < priority_min:
                    continue
                
                if task_ids and task_data.get('id') not in task_ids:
                    continue
                
                # Convert to Task object
                task = Task(
                    task_id=task_data.get('id', ''),
                    name=task_data.get('title', ''),
                    description=task_data.get('description', ''),
                    command=f"cb execute-{task_data.get('id', '')}",
                    working_directory=task_data.get('working_dir', '.'),
                    dependencies=task_data.get('deps', []),
                    estimated_duration=30,  # Default 30 minutes
                    priority=task_data.get('priority', 5),
                    agent_type=task_data.get('agent_type', 'general'),
                    requires_abc_iteration=task_data.get('requires_abc_iteration', False),
                    abc_target_file=task_data.get('abc_target_file', ''),
                    abc_rounds=task_data.get('abc_rounds', 3)
                )
                
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            click.echo(f"❌ Error loading tasks from index: {e}")
            return []
    
    def save_task_result(self, task_id: str, result: Dict[str, Any]) -> str:
        """Save individual task result to JSON file."""
        try:
            result_file = self.results_dir / f"{task_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            return str(result_file)
        except Exception as e:
            click.echo(f"❌ Error saving result for {task_id}: {e}")
            return ""
    
    def generate_summary(self, execution_results: List[Dict[str, Any]]) -> str:
        """Generate aggregated summary markdown."""
        try:
            summary_file = self.results_dir / "summary.md"
            
            # Count results by status
            status_counts = {}
            total_tasks = len(execution_results)
            
            for result in execution_results:
                status = result.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Generate summary content
            summary_content = f"""# Task Execution Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Tasks**: {total_tasks}
- **Completed**: {status_counts.get('completed', 0)}
- **Failed**: {status_counts.get('failed', 0)}
- **Pending**: {status_counts.get('pending', 0)}
- **Running**: {status_counts.get('running', 0)}

## Results by Status

"""
            
            for status, count in status_counts.items():
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                summary_content += f"- **{status.title()}**: {count} ({percentage:.1f}%)\n"
            
            summary_content += "\n## Task Details\n\n"
            
            for result in execution_results:
                task_id = result.get('task_id', 'unknown')
                status = result.get('status', 'unknown')
                started_at = result.get('started_at', 'N/A')
                completed_at = result.get('completed_at', 'N/A')
                error_message = result.get('error_message', '')
                
                summary_content += f"### {task_id}\n"
                summary_content += f"- **Status**: {status}\n"
                summary_content += f"- **Started**: {started_at}\n"
                summary_content += f"- **Completed**: {completed_at}\n"
                
                if error_message:
                    summary_content += f"- **Error**: {error_message}\n"
                
                summary_content += "\n"
            
            # Write summary file
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            return str(summary_file)
            
        except Exception as e:
            click.echo(f"❌ Error generating summary: {e}")
            return ""
    
    def detect_deadlocks(self) -> List[List[str]]:
        """Detect potential deadlocks in task dependencies."""
        return self.orchestrator.detect_cycles()
    
    def get_execution_plan(self, tasks: List[Task]) -> List[List[str]]:
        """Get execution plan showing dependency levels."""
        # Add tasks to orchestrator temporarily
        original_tasks = self.orchestrator.tasks.copy()
        self.orchestrator.tasks.clear()
        
        for task in tasks:
            self.orchestrator.tasks[task.task_id] = task
        
        # Build dependency graph
        self.orchestrator._build_dependency_graph()
        
        # Get execution order
        execution_plan = self.orchestrator.get_execution_order()
        
        # Restore original tasks
        self.orchestrator.tasks = original_tasks
        
        return execution_plan
    
    def run_execution(self, 
                     tasks: List[Task],
                     max_parallel: int = 1,
                     dry_run: bool = False) -> List[Dict[str, Any]]:
        """Run task execution with parallelism control."""
        try:
            if dry_run:
                # Generate execution plan
                execution_plan = self.get_execution_plan(tasks)
                
                click.echo("🔍 Dry run - Execution Plan:")
                for level, task_ids in enumerate(execution_plan):
                    click.echo(f"  Level {level + 1}: {', '.join(task_ids)}")
                
                # Check for deadlocks
                deadlocks = self.detect_deadlocks()
                if deadlocks:
                    click.echo(f"⚠️  Deadlocks detected: {deadlocks}")
                else:
                    click.echo("✅ No deadlocks detected")
                
                return []
            
            # Add tasks to orchestrator
            for task in tasks:
                self.orchestrator.add_task(task)
            
            # Run execution
            execution_results = []
            cycles = 0
            max_cycles = 100  # Safety limit
            
            while cycles < max_cycles:
                # Check if all tasks are complete
                pending_tasks = [t for t in self.orchestrator.tasks.values() 
                               if t.status in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]]
                
                if not pending_tasks:
                    break
                
                # Run orchestration cycle
                cycle_info = self.orchestrator.run_orchestration_cycle()
                cycles += 1
                
                click.echo(f"🔄 Cycle {cycles}: {cycle_info['tasks_assigned']} assigned, "
                          f"{cycle_info['tasks_completed']} completed, "
                          f"{cycle_info['tasks_failed']} failed")
                
                # Check for fatal errors
                failed_tasks = [t for t in self.orchestrator.tasks.values() if t.status == TaskStatus.FAILED]
                if failed_tasks:
                    click.echo(f"❌ Fatal error: {len(failed_tasks)} tasks failed")
                    break
            
            # Collect results
            for task in self.orchestrator.tasks.values():
                result = {
                    'task_id': task.task_id,
                    'name': task.name,
                    'status': task.status.value,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'assigned_agent': task.assigned_agent,
                    'error_message': task.error_message
                }
                execution_results.append(result)
                
                # Save individual result
                self.save_task_result(task.task_id, result)
            
            return execution_results
            
        except Exception as e:
            click.echo(f"❌ Error during execution: {e}")
            return []


@cli.command("execute-tasks")
@click.option("--filter", "filter_tags", multiple=True, help="Filter tasks by tags")
@click.option("--priority", "priority_min", type=int, help="Minimum priority threshold")
@click.option("--max-parallel", type=int, default=1, help="Maximum parallel tasks")
@click.option("--dry-run", is_flag=True, help="Show execution plan without running")
@click.option("--tasks", "task_ids", multiple=True, help="Specific task IDs to execute")
@click.option("--output-dir", default="cb_docs/tasks/results", help="Output directory for results")
def execute_tasks(filter_tags, priority_min, max_parallel, dry_run, task_ids, output_dir):
    """Execute tasks with dependency management and parallelism control."""
    try:
        runner = OrchestratorRunner()
        
        # Load tasks from index
        click.echo("📋 Loading tasks from index...")
        tasks = runner.load_tasks_from_index(
            filter_tags=list(filter_tags) if filter_tags else None,
            priority_min=priority_min,
            task_ids=list(task_ids) if task_ids else None
        )
        
        if not tasks:
            click.echo("❌ No tasks found matching criteria")
            return 1
        
        click.echo(f"✅ Loaded {len(tasks)} tasks")
        
        # Show task summary
        click.echo("\n📊 Task Summary:")
        for task in tasks:
            click.echo(f"  - {task.task_id}: {task.name} (priority: {task.priority})")
        
        # Run execution
        if dry_run:
            click.echo("\n🔍 Dry run mode - generating execution plan...")
            execution_plan = runner.get_execution_plan(tasks)
            
            click.echo("\n📋 Execution Plan:")
            for level, task_ids in enumerate(execution_plan):
                click.echo(f"  Level {level + 1}: {', '.join(task_ids)}")
            
            # Check for deadlocks
            deadlocks = runner.detect_deadlocks()
            if deadlocks:
                click.echo(f"\n⚠️  Deadlocks detected: {deadlocks}")
                return 1
            else:
                click.echo("\n✅ No deadlocks detected")
                return 0
        else:
            click.echo(f"\n🚀 Starting execution with max-parallel={max_parallel}...")
            execution_results = runner.run_execution(tasks, max_parallel, dry_run)
            
            if execution_results:
                # Generate summary
                summary_file = runner.generate_summary(execution_results)
                click.echo(f"\n📊 Summary generated: {summary_file}")
                
                # Show final status
                completed = sum(1 for r in execution_results if r['status'] == 'completed')
                failed = sum(1 for r in execution_results if r['status'] == 'failed')
                click.echo(f"✅ Execution complete: {completed} completed, {failed} failed")
                
                return 0 if failed == 0 else 1
            else:
                click.echo("❌ No execution results")
                return 1
        
    except Exception as e:
        click.echo(f"❌ Error executing tasks: {e}")
        return 1


@cli.command("orchestrator:status")
def orchestrator_status():
    """Show orchestrator status and task summary."""
    try:
        runner = OrchestratorRunner()
        summary = runner.orchestrator.get_status_summary()
        
        click.echo("📊 Orchestrator Status:")
        click.echo(f"  Tasks: {summary['tasks']['total']}")
        for status, count in summary['tasks']['by_status'].items():
            click.echo(f"    {status}: {count}")
        
        click.echo(f"  Agents: {summary['agents']['total']}")
        for status, count in summary['agents']['by_status'].items():
            click.echo(f"    {status}: {count}")
        
        click.echo(f"  Ready tasks: {summary['ready_tasks']}")
        click.echo(f"  Available agents: {summary['available_agents']}")
        click.echo(f"  Cycles detected: {summary['cycles_detected']}")
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}")
        return 1


@cli.command("orchestrator:validate")
def orchestrator_validate():
    """Validate task dependencies and detect issues."""
    try:
        runner = OrchestratorRunner()
        
        # Load tasks from index
        tasks = runner.load_tasks_from_index()
        
        if not tasks:
            click.echo("❌ No tasks found")
            return 1
        
        # Add tasks to orchestrator
        for task in tasks:
            runner.orchestrator.add_task(task)
        
        # Check for deadlocks
        deadlocks = runner.detect_deadlocks()
        if deadlocks:
            click.echo(f"❌ Deadlocks detected: {deadlocks}")
            return 1
        
        # Check execution plan
        execution_plan = runner.get_execution_plan(tasks)
        if not execution_plan:
            click.echo("❌ No valid execution plan found")
            return 1
        
        click.echo("✅ Task dependencies are valid")
        click.echo(f"📋 Execution plan has {len(execution_plan)} levels")
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error validating: {e}")
        return 1


if __name__ == "__main__":
    # Test the orchestrator runner
    runner = OrchestratorRunner()
    tasks = runner.load_tasks_from_index()
    print(f"Loaded {len(tasks)} tasks")
    
    if tasks:
        execution_plan = runner.get_execution_plan(tasks)
        print(f"Execution plan: {execution_plan}")