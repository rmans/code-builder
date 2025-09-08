#!/usr/bin/env python3
"""
Dynamic Content Updater Commands

This module provides CLI commands for dynamic content updating.
"""

import json
from pathlib import Path
from typing import Dict, Any

import click

from .base import cli
from ...utils.dynamic_content_updater import (
    DynamicContentUpdater, update_content, update_file, sync_rules
)


@cli.command("update:content")
@click.argument("content")
@click.option("--type", "content_type", type=click.Choice(["general", "task", "command", "rule"]), 
              default="general", help="Content type")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def update_content_cmd(content: str, content_type: str, output_format: str):
    """Update content with current project context."""
    try:
        updated_content = update_content(content, content_type)
        
        if output_format == "json":
            result = {
                "original": content,
                "updated": updated_content,
                "content_type": content_type,
                "changed": content != updated_content
            }
            click.echo(json.dumps(result, indent=2))
        else:
            if content != updated_content:
                click.echo("✅ Content updated:")
                click.echo(updated_content)
            else:
                click.echo("ℹ️  No placeholders found to update")
        
    except Exception as e:
        click.echo(f"❌ Content update failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:file")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--type", "content_type", type=click.Choice(["general", "task", "command", "rule"]), 
              default="general", help="Content type")
@click.option("--backup", is_flag=True, help="Create backup before updating")
def update_file_cmd(file_path: str, content_type: str, backup: bool):
    """Update a file with current project context."""
    try:
        file_path = Path(file_path)
        
        if backup:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            import shutil
            shutil.copy2(file_path, backup_path)
            click.echo(f"📄 Backup created: {backup_path}")
        
        updater = DynamicContentUpdater()
        updated = updater.update_file(str(file_path), content_type)
        
        if updated:
            click.echo(f"✅ File updated: {file_path}")
        else:
            click.echo(f"ℹ️  No updates needed: {file_path}")
        
    except Exception as e:
        click.echo(f"❌ File update failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:directory")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--type", "content_type", type=click.Choice(["general", "task", "command", "rule"]), 
              default="general", help="Content type")
@click.option("--pattern", default="*.md", help="File pattern to match")
@click.option("--recursive", is_flag=True, help="Search recursively")
def update_directory_cmd(directory: str, content_type: str, pattern: str, recursive: bool):
    """Update all files in a directory."""
    try:
        updater = DynamicContentUpdater()
        
        if recursive:
            result = updater.update_directory(directory, content_type, pattern)
        else:
            directory_path = Path(directory)
            result = {"updated": 0, "errors": 0, "files": []}
            
            for file_path in directory_path.glob(pattern):
                if updater.update_file(str(file_path), content_type):
                    result["updated"] += 1
                    result["files"].append(str(file_path))
        
        click.echo(f"📊 Directory update results:")
        click.echo(f"  Updated: {result['updated']} files")
        click.echo(f"  Errors: {result['errors']} files")
        
        if result["files"]:
            click.echo(f"  Files updated:")
            for file_path in result["files"]:
                click.echo(f"    - {file_path}")
        
    except Exception as e:
        click.echo(f"❌ Directory update failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:rules")
def update_rules_cmd():
    """Sync rules after content updates."""
    try:
        updated = sync_rules()
        
        if updated:
            click.echo("✅ Rules synchronized")
        else:
            click.echo("ℹ️  No rule updates needed")
        
    except Exception as e:
        click.echo(f"❌ Rules sync failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:project-context")
def update_project_context_cmd():
    """Refresh project context from discovery data."""
    try:
        updater = DynamicContentUpdater()
        updater.refresh_project_context()
        
        click.echo("✅ Project context refreshed")
        click.echo(f"  Project Type: {updater.project_context.get('project_type', 'unknown')}")
        click.echo(f"  Language: {updater.project_context.get('language', 'unknown')}")
        click.echo(f"  Framework: {updater.project_context.get('framework', 'unknown')}")
        click.echo(f"  Name: {updater.project_context.get('name', 'unknown')}")
        
    except Exception as e:
        click.echo(f"❌ Project context refresh failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:status")
def update_status_cmd():
    """Show current update status and context."""
    try:
        updater = DynamicContentUpdater()
        
        click.echo("📊 Dynamic Content Updater Status:")
        click.echo()
        
        # Project context
        click.echo("Project Context:")
        for key, value in updater.project_context.items():
            click.echo(f"  {key}: {value}")
        
        click.echo()
        
        # Task status
        task_status = updater._get_current_task_status()
        click.echo("Task Status:")
        click.echo(f"  Status: {task_status['status']}")
        click.echo(f"  Active: {task_status['active_count']}")
        click.echo(f"  Completed: {task_status['completed_count']}")
        click.echo(f"  Total: {task_status['total_count']}")
        
        click.echo()
        
        # Command status
        command_status = updater._get_current_command_status()
        click.echo("Command Status:")
        click.echo(f"  Status: {command_status['status']}")
        click.echo(f"  Available: {command_status['available_count']}")
        click.echo(f"  Categories: {', '.join(command_status['categories'])}")
        
        click.echo()
        
        # Rule status
        rule_status = updater._get_current_rule_status()
        click.echo("Rule Status:")
        click.echo(f"  Status: {rule_status['status']}")
        click.echo(f"  Active: {rule_status['active_count']}")
        click.echo(f"  Categories: {', '.join(rule_status['categories'])}")
        
    except Exception as e:
        click.echo(f"❌ Status check failed: {e}")
        click.get_current_context().exit(1)


@cli.command("update:all")
@click.option("--backup", is_flag=True, help="Create backups before updating")
def update_all_cmd(backup: bool):
    """Update all dynamic content in the project."""
    try:
        updater = DynamicContentUpdater()
        
        click.echo("🔄 Updating all dynamic content...")
        
        # Update commands
        click.echo("  Updating commands...")
        commands_dir = updater.overlay_paths.get_commands_dir()
        if commands_dir.exists():
            cmd_result = updater.update_directory(str(commands_dir), "command")
            click.echo(f"    Updated {cmd_result['updated']} command files")
        
        # Update rules
        click.echo("  Updating rules...")
        rules_dir = updater.overlay_paths.get_docs_dir() / "rules"
        if rules_dir.exists():
            rule_result = updater.update_directory(str(rules_dir), "rule")
            click.echo(f"    Updated {rule_result['updated']} rule files")
        
        # Update tasks
        click.echo("  Updating tasks...")
        tasks_dir = updater.overlay_paths.get_docs_dir() / "tasks"
        if tasks_dir.exists():
            task_result = updater.update_directory(str(tasks_dir), "task")
            click.echo(f"    Updated {task_result['updated']} task files")
        
        # Sync rules
        click.echo("  Syncing rules...")
        sync_rules()
        
        click.echo("✅ All dynamic content updated")
        
    except Exception as e:
        click.echo(f"❌ Update all failed: {e}")
        click.get_current_context().exit(1)
