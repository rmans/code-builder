#!/usr/bin/env python3
"""
Current Instructions Commands

This module provides CLI commands for managing current instructions.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

import click

from .base import cli
from ...utils.current_instructions import (
    CurrentInstructionsManager, update_current_status, clear_current_status, get_current_status
)


@cli.command("current:update")
@click.option("--task-id", help="Active task ID")
@click.option("--agent-id", help="Active agent ID")
@click.option("--status", help="Current status")
@click.option("--error", help="Current error message")
def current_update(task_id: str, agent_id: str, status: str, error: str):
    """Update current instructions with latest status."""
    try:
        update_current_status(task_id, agent_id, status, error)
        click.echo("✅ Current instructions updated")
    except Exception as e:
        click.echo(f"❌ Failed to update current instructions: {e}")
        click.get_current_context().exit(1)


@cli.command("current:show")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def current_show(output_format: str):
    """Show current instructions content."""
    try:
        manager = CurrentInstructionsManager()
        
        if not manager.current_file.exists():
            click.echo("No current instructions file found")
            return
        
        with open(manager.current_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if output_format == "json":
            # Parse content into structured format
            lines = content.split('\n')
            parsed = {
                "file_exists": True,
                "content": content,
                "last_updated": None,
                "active_task": None,
                "active_agent": None,
                "system_status": {}
            }
            
            for line in lines:
                if line.startswith("**Last Updated**: "):
                    parsed["last_updated"] = line.replace("**Last Updated**: ", "")
                elif line.startswith("**Active Task**: "):
                    parsed["active_task"] = line.replace("**Active Task**: ", "")
                elif line.startswith("**Assigned Agent**: "):
                    parsed["active_agent"] = line.replace("**Assigned Agent**: ", "")
            
            click.echo(json.dumps(parsed, indent=2))
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Failed to show current instructions: {e}")
        click.get_current_context().exit(1)


@cli.command("current:status")
def current_status():
    """Show current instructions status."""
    try:
        status = get_current_status()
        
        if not status:
            click.echo("No current instructions file found")
            return
        
        click.echo("📊 Current Instructions Status:")
        click.echo()
        
        if status.get("file_exists"):
            click.echo(f"  📄 File exists: {manager.current_file}")
            click.echo(f"  🕒 Last updated: {status.get('last_updated', 'Unknown')}")
            click.echo(f"  🎯 Active task: {status.get('active_task', 'None')}")
            click.echo(f"  🤖 Active agent: {status.get('active_agent', 'None')}")
            click.echo(f"  ⚠️  Error count: {status.get('error_count', 0)}")
        else:
            click.echo("  ❌ File does not exist")
        
    except Exception as e:
        click.echo(f"❌ Failed to get current status: {e}")
        click.get_current_context().exit(1)


@cli.command("current:clear")
def current_clear():
    """Clear current instructions file."""
    try:
        clear_current_status()
        click.echo("✅ Current instructions cleared")
    except Exception as e:
        click.echo(f"❌ Failed to clear current instructions: {e}")
        click.get_current_context().exit(1)


@cli.command("current:refresh")
def current_refresh():
    """Refresh current instructions with latest system status."""
    try:
        manager = CurrentInstructionsManager()
        manager.update_current_status()
        click.echo("✅ Current instructions refreshed")
    except Exception as e:
        click.echo(f"❌ Failed to refresh current instructions: {e}")
        click.get_current_context().exit(1)


@cli.command("current:init")
def current_init():
    """Initialize current instructions file."""
    try:
        manager = CurrentInstructionsManager()
        manager.update_current_status()
        click.echo("✅ Current instructions initialized")
        click.echo(f"📄 File created: {manager.current_file}")
    except Exception as e:
        click.echo(f"❌ Failed to initialize current instructions: {e}")
        click.get_current_context().exit(1)


@cli.command("current:errors")
@click.option("--limit", default=10, help="Number of errors to show")
def current_errors(limit: int):
    """Show recent errors from current instructions."""
    try:
        manager = CurrentInstructionsManager()
        
        if not manager.current_file.exists():
            click.echo("No current instructions file found")
            return
        
        with open(manager.current_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract errors from content
        lines = content.split('\n')
        in_errors_section = False
        error_count = 0
        
        click.echo("⚠️  Recent Errors:")
        click.echo()
        
        for line in lines:
            if "## ⚠️ Recent Errors" in line:
                in_errors_section = True
                continue
            elif in_errors_section and line.startswith("## "):
                break
            elif in_errors_section and line.strip() and error_count < limit:
                click.echo(f"  {line}")
                error_count += 1
        
        if error_count == 0:
            click.echo("  No recent errors found")
        
    except Exception as e:
        click.echo(f"❌ Failed to show errors: {e}")
        click.get_current_context().exit(1)


@cli.command("current:next-steps")
def current_next_steps():
    """Show next steps from current instructions."""
    try:
        manager = CurrentInstructionsManager()
        
        if not manager.current_file.exists():
            click.echo("No current instructions file found")
            return
        
        with open(manager.current_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract next steps from content
        lines = content.split('\n')
        in_next_steps_section = False
        
        click.echo("🚀 Next Steps:")
        click.echo()
        
        for line in lines:
            if "## 🚀 Next Steps" in line:
                in_next_steps_section = True
                continue
            elif in_next_steps_section and line.startswith("## "):
                break
            elif in_next_steps_section and line.strip():
                click.echo(f"  {line}")
        
    except Exception as e:
        click.echo(f"❌ Failed to show next steps: {e}")
        click.get_current_context().exit(1)


@cli.command("current:watch")
@click.option("--interval", default=5, help="Update interval in seconds")
def current_watch(interval: int):
    """Watch current instructions for changes."""
    try:
        import time
        
        click.echo(f"👀 Watching current instructions (interval: {interval}s)")
        click.echo("Press Ctrl+C to stop")
        
        last_modified = 0
        
        while True:
            try:
                manager = CurrentInstructionsManager()
                
                if manager.current_file.exists():
                    current_modified = manager.current_file.stat().st_mtime
                    
                    if current_modified > last_modified:
                        click.echo(f"\n🔄 Updated at {datetime.now().strftime('%H:%M:%S')}")
                        click.echo("=" * 50)
                        
                        with open(manager.current_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        click.echo(content)
                        
                        last_modified = current_modified
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                click.echo("\n👋 Stopped watching")
                break
            except Exception as e:
                click.echo(f"⚠️  Watch error: {e}")
                time.sleep(interval)
        
    except Exception as e:
        click.echo(f"❌ Failed to watch current instructions: {e}")
        click.get_current_context().exit(1)
