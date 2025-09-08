#!/usr/bin/env python3
"""
Base CLI module for Code Builder

This module contains the main CLI group and common utilities used across all command modules.
"""

import click
import os
import yaml
import json
from datetime import datetime, date
from pathlib import Path

# Import telemetry for command tracking
try:
    from ...telemetry.command_tracker import track_command, get_command_tracker
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False

# Main CLI group
@click.group()
def cli():
    """Code Builder CLI"""
    pass

# Import task generator commands
from ...overlay.task_generator import (
    generate_task_cli,
    list_task_templates_cli,
    validate_task_template_cli
)

# Import quality commands
try:
    from .quality_commands import quality_gates, quality_check, quality_report
    cli.add_command(quality_gates)
    cli.add_command(quality_check)
    cli.add_command(quality_report)
except ImportError:
    pass

# Register task generator commands
cli.add_command(generate_task_cli)
cli.add_command(list_task_templates_cli)
cli.add_command(validate_task_template_cli)

# Common utilities
def safe_yaml_load(content, error_context=""):
    """Safely load YAML content with error handling."""
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        click.echo(f"❌ Error parsing YAML{error_context}: {e}")
        return None

def json_serializer(obj):
    """JSON serializer for common types."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_dumps(data, indent=2):
    """Safely dump data to JSON with proper serialization."""
    return json.dumps(data, indent=indent, default=json_serializer)

def ensure_directory(path):
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_project_root():
    """Get the project root directory."""
    return Path.cwd()

def get_cb_docs_dir():
    """Get the cb_docs directory path."""
    return get_project_root() / "cb_docs"

def get_cache_dir():
    """Get the cache directory path."""
    return get_project_root() / ".cb" / "cache"

def format_command_output(data, output_format='table'):
    """Format command output based on format type."""
    if output_format == 'json':
        click.echo(safe_json_dumps(data))
    elif output_format == 'yaml':
        click.echo(yaml.dump(data, default_flow_style=False))
    else:  # table format
        if isinstance(data, list):
            for item in data:
                click.echo(f"  - {item}")
        elif isinstance(data, dict):
            for key, value in data.items():
                click.echo(f"  {key}: {value}")
        else:
            click.echo(str(data))

# Common click options
def common_output_format_option():
    """Common output format option for commands."""
    return click.option(
        '--format', 'output_format',
        type=click.Choice(['table', 'json', 'yaml']),
        default='table',
        help='Output format'
    )

def common_force_option():
    """Common force option for commands."""
    return click.option(
        '--force', 'force',
        is_flag=True,
        help='Force operation even if target exists'
    )

def common_dry_run_option():
    """Common dry run option for commands."""
    return click.option(
        '--dry-run', 'dry_run',
        is_flag=True,
        help='Show what would be done without making changes'
    )

# Status command
@cli.command("status")
@click.option("--format", "output_format", type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
@click.option("--verbose", is_flag=True, help='Show detailed information')
@click.option("--metrics", is_flag=True, help='Include performance metrics')
def status_command(output_format, verbose, metrics):
    """Display current project status and metrics."""
    try:
        if TELEMETRY_AVAILABLE:
            tracker = get_command_tracker()
            status_data = tracker.get_status_summary()
            
            if output_format == 'json':
                click.echo(safe_json_dumps(status_data))
            elif output_format == 'yaml':
                click.echo(yaml.dump(status_data, default_flow_style=False))
            else:
                # Table format
                click.echo("📊 Code Builder Status")
                click.echo("=" * 50)
                click.echo(f"Total Commands: {status_data['total_commands']}")
                click.echo(f"Success Rate: {status_data['success_rate']:.1%}")
                click.echo(f"Avg Execution Time: {status_data['avg_execution_time']:.1f}ms")
                click.echo(f"Last Updated: {status_data['last_updated']}")
                
                if verbose and status_data['recent_commands']:
                    click.echo("\n📋 Recent Commands:")
                    for cmd in status_data['recent_commands']:
                        status_icon = "✅" if cmd['success'] else "❌"
                        click.echo(f"  {status_icon} {cmd['command_id']} ({cmd['execution_time_ms']:.1f}ms)")
                
                if metrics and status_data['most_used']:
                    click.echo("\n🔥 Most Used Commands:")
                    for cmd in status_data['most_used']:
                        click.echo(f"  {cmd['command_id']}: {cmd['count']} times")
        else:
            click.echo("📊 Code Builder Status")
            click.echo("=" * 50)
            click.echo("Telemetry not available - basic status only")
            click.echo("Project Root: " + str(get_project_root()))
            click.echo("Cache Dir: " + str(get_cache_dir()))
            
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}")
        return 1
    
    return 0
