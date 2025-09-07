#!/usr/bin/env python3
"""
Workflow Commands Module

This module contains workflow-related commands like workflows:*
"""

import click
import os
import sys
from .base import cli, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    CACHE = ROOT / ".cb" / "cache"

def _get_github_actions_validator():
    """Get GitHub Actions validator instance."""
    try:
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        from utils.github_actions_validator import validate_workflow_file, validate_all_workflows
        return validate_workflow_file, validate_all_workflows
    except ImportError:
        click.echo("❌ Required utility module not available. Make sure utils/github_actions_validator.py exists.")
        return None, None

# Workflow Commands
@cli.command("workflows:validate")
@click.argument("workflow_file", required=False)
@click.option("--all", is_flag=True, help="Validate all workflow files in .github/workflows/")
def workflows_validate(workflow_file, all):
    """Validate GitHub Actions workflow files."""
    try:
        validate_workflow_file, validate_all_workflows = _get_github_actions_validator()
        
        if not validate_workflow_file or not validate_all_workflows:
            return 1
        
        if all:
            # Validate all workflows
            results = validate_all_workflows()
            
            total_valid = 0
            total_files = len(results)
            
            for file_path, (is_valid, errors, warnings) in results.items():
                click.echo(f"\nValidating {file_path}...")
                
                if warnings:
                    for warning in warnings:
                        click.echo(f"  ⚠️  {warning}")
                
                if errors:
                    for error in errors:
                        click.echo(f"  ❌ {error}")
                
                if is_valid:
                    total_valid += 1
                    if not warnings:
                        click.echo("  ✅ Valid")
                    else:
                        click.echo("  ✅ Valid with warnings")
                else:
                    click.echo("  ❌ Invalid")
            
            click.echo(f"\nSummary: {total_valid}/{total_files} workflows valid")
            
            if total_valid < total_files:
                return 1
        else:
            # Validate specific file
            if not workflow_file:
                workflow_file = ".github/workflows"
            
            is_valid, errors, warnings = validate_workflow_file(workflow_file)
            
            if warnings:
                click.echo("⚠️  Warnings:")
                for warning in warnings:
                    click.echo(f"  {warning}")
                click.echo()
            
            if errors:
                click.echo("❌ Validation errors:")
                for error in errors:
                    click.echo(f"  {error}")
                click.echo("\n💡 Fix these issues to make the workflow valid.")
                return 1
            else:
                click.echo("✅ Workflow is valid!")
        
    except Exception as e:
        click.echo(f"❌ Error validating workflows: {e}")
        return 1
    
    return 0
