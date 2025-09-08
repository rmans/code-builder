#!/usr/bin/env python3
"""
Per-Task Command Generator

This module generates individual command files and @rules/ files for each task,
enabling per-task execution through both CLI commands and Cursor @rules/ integration.
"""

import json
import click
from pathlib import Path
from datetime import datetime
from .paths import OverlayPaths
from ..core.cli.base import cli

# Initialize overlay paths
overlay_paths = OverlayPaths()


def generate_task_commands(tasks_data=None):
    """
    Generate command files and @rules/ files for all tasks.
    
    Args:
        tasks_data: Optional tasks data dict. If None, loads from tasks/index.json
    
    Returns:
        dict: Generation results with success/failure counts
    """
    try:
        # Load tasks data if not provided
        if tasks_data is None:
            tasks_data = _load_tasks_data()
        
        if not tasks_data or 'tasks' not in tasks_data:
            print("❌ No tasks data found")
            return {"success": 0, "failed": 0, "errors": ["No tasks data found"]}
        
        tasks = tasks_data['tasks']
        results = {"success": 0, "failed": 0, "errors": []}
        
        print(f"🔄 Generating commands for {len(tasks)} tasks...")
        
        for task in tasks:
            try:
                # Generate command file
                command_success = _generate_command_file(task)
                
                # Generate @rules/ file
                rule_success = _generate_rule_file(task)
                
                if command_success and rule_success:
                    results["success"] += 1
                    print(f"✅ Generated commands for {task['id']}")
                else:
                    results["failed"] += 1
                    error_msg = f"Failed to generate commands for {task['id']}"
                    results["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
                    
            except Exception as e:
                results["failed"] += 1
                error_msg = f"Error generating commands for {task['id']}: {e}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        print(f"✅ Generated {results['success']} task commands")
        if results["failed"] > 0:
            print(f"❌ Failed to generate {results['failed']} task commands")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in generate_task_commands: {e}")
        return {"success": 0, "failed": 0, "errors": [str(e)]}


def _load_tasks_data():
    """Load tasks data from tasks/index.json"""
    try:
        tasks_file = Path("cb_docs/tasks/index.json")
        if not tasks_file.exists():
            print("❌ tasks/index.json not found")
            return None
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading tasks data: {e}")
        return None


def _generate_command_file(task):
    """Generate .cb/commands/execute-TASK-###.md file for a task"""
    try:
        # Get task details
        task_id = task['id']
        task_file = Path(task['file'])
        
        # Read task content
        if not task_file.exists():
            print(f"❌ Task file not found: {task_file}")
            return False
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task_content = f.read()
        
        # Extract task metadata from frontmatter
        task_metadata = _parse_task_metadata(task_content)
        
        # Generate command file content
        command_content = _create_command_content(task_id, task_metadata, task_content)
        
        # Write command file
        commands_dir = Path(overlay_paths.commands_dir())
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        command_file = commands_dir / f"execute-{task_id}.md"
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write(command_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating command file for {task['id']}: {e}")
        return False


def _generate_rule_file(task):
    """Generate .cursor/rules/execute-TASK-###.md file for a task"""
    try:
        # Get task details
        task_id = task['id']
        task_file = Path(task['file'])
        
        # Read task content
        if not task_file.exists():
            print(f"❌ Task file not found: {task_file}")
            return False
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task_content = f.read()
        
        # Extract task metadata from frontmatter
        task_metadata = _parse_task_metadata(task_content)
        
        # Generate rule file content
        rule_content = _create_rule_content(task_id, task_metadata, task_content)
        
        # Write rule file
        rules_dir = Path(overlay_paths.cursor_rules_dir())
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rule_file = rules_dir / f"execute-{task_id}.md"
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating rule file for {task['id']}: {e}")
        return False


def _parse_task_metadata(task_content):
    """Parse task metadata from frontmatter"""
    try:
        import yaml
        import re
        
        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', task_content, re.DOTALL)
        if not frontmatter_match:
            return {}
        
        frontmatter_text = frontmatter_match.group(1)
        return yaml.safe_load(frontmatter_text) or {}
        
    except Exception as e:
        print(f"⚠️  Warning: Could not parse task metadata: {e}")
        return {}


def _create_command_content(task_id, metadata, task_content):
    """Create command file content for a task"""
    title = metadata.get('title', f'Execute {task_id}')
    description = metadata.get('description', f'Execute task {task_id}')
    domain = metadata.get('domain', 'execution')
    priority = metadata.get('priority', 5)
    dependencies = metadata.get('dependencies', [])
    tags = metadata.get('tags', ['task', 'execution'])
    
    # Create command ID
    command_id = f"execute-{task_id}"
    
    # Format dependencies
    deps_str = ', '.join(dependencies) if dependencies else '[]'
    
    # Format tags
    tags_str = ', '.join(tags)
    
    content = f"""---
id: {command_id}
title: {title}
description: {description}
status: active
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
owner: system
domain: {domain}
priority: {priority}
agent_type: backend
dependencies: {deps_str}
tags: [{tags_str}]
---

# Command: {title}

## Description
{description}

## Usage
```bash
cb execute-{task_id}
# or
@rules/execute-{task_id}
```

## Outputs
- Task execution results
- Updated task status
- Generated artifacts (if applicable)

## Flags
- `--phase PHASE` - Execute specific phase only
- `--skip-phases PHASES` - Skip specific phases (comma-separated)
- `--dry-run` - Show execution plan without running
- `--interactive` - Interactive mode with confirmations
- `--force` - Force execution even if dependencies not met

## Examples
```bash
# Execute complete task
cb execute-{task_id}

# Execute specific phase
cb execute-{task_id} --phase implementation

# Dry run
cb execute-{task_id} --dry-run

# Interactive mode
cb execute-{task_id} --interactive
```

## Task Details

{task_content}
"""
    
    return content


def _create_rule_content(task_id, metadata, task_content):
    """Create @rules/ file content for a task"""
    title = metadata.get('title', f'Execute {task_id}')
    description = metadata.get('description', f'Execute task {task_id}')
    domain = metadata.get('domain', 'execution')
    priority = metadata.get('priority', 5)
    dependencies = metadata.get('dependencies', [])
    tags = metadata.get('tags', ['task', 'execution'])
    
    # Create command ID
    command_id = f"execute-{task_id}"
    
    # Format dependencies
    deps_str = ', '.join(dependencies) if dependencies else '[]'
    
    # Format tags
    tags_str = ', '.join(tags)
    
    content = f"""---
id: {command_id}
title: {title}
description: {description}
status: active
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
owner: system
domain: {domain}
priority: {priority}
agent_type: backend
dependencies: {deps_str}
tags: [{tags_str}]
---

# Command: {title}

## Description
{description}

## Usage
```bash
cb execute-{task_id}
# or
@rules/execute-{task_id}
```

## Outputs
- Task execution results
- Updated task status
- Generated artifacts (if applicable)

## Flags
- `--phase PHASE` - Execute specific phase only
- `--skip-phases PHASES` - Skip specific phases (comma-separated)
- `--dry-run` - Show execution plan without running
- `--interactive` - Interactive mode with confirmations
- `--force` - Force execution even if dependencies not met

## Examples
```bash
# Execute complete task
cb execute-{task_id}

# Execute specific phase
cb execute-{task_id} --phase implementation

# Dry run
cb execute-{task_id} --dry-run

# Interactive mode
cb execute-{task_id} --interactive
```

## Task Details

{task_content}
"""
    
    return content


@cli.command("generate-task-commands")
@click.option("--force", is_flag=True, help="Force regeneration of existing commands")
def generate_task_commands_cli(force):
    """Generate command files and @rules/ files for all tasks."""
    try:
        # Check if commands already exist
        if not force:
            commands_dir = Path(overlay_paths.commands_dir())
            if commands_dir.exists() and any(commands_dir.glob("execute-TASK-*.md")):
                click.echo("⚠️  Task commands already exist. Use --force to regenerate.")
                return 1
        
        # Generate task commands
        results = generate_task_commands()
        
        if results["success"] > 0:
            click.echo(f"✅ Successfully generated {results['success']} task commands")
        
        if results["failed"] > 0:
            click.echo(f"❌ Failed to generate {results['failed']} task commands")
            for error in results["errors"]:
                click.echo(f"   {error}")
            return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error generating task commands: {e}")
        return 1


if __name__ == "__main__":
    # Test the command generator
    results = generate_task_commands()
    print(f"Generation results: {results}")
