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

# Main CLI group
@click.group()
def cli():
    """Code Builder CLI"""
    pass

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
