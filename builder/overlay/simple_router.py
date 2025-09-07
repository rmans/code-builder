#!/usr/bin/env python3
"""
Simple Router for Code Builder Commands

This module provides simple command routing for basic Code Builder commands,
mapping short commands to their full implementations.
"""

import click
from pathlib import Path
from .paths import OverlayPaths
from ..core.cli.base import cli

# Initialize overlay paths
overlay_paths = OverlayPaths()


@cli.command("analyze")
@click.option("--depth", type=int, default=3, help="Analysis depth (default: 3)")
@click.option("--ignore", help="Ignore files matching pattern")
@click.option("--ci", is_flag=True, help="Non-interactive mode for CI/CD")
def analyze_command(depth, ignore, ci):
    """
    Analyze project structure and generate discovery report.
    
    This is a simple implementation that creates basic project analysis.
    """
    try:
        # Import the enhanced discovery engine
        from ..discovery.enhanced_engine import analyze_project_enhanced
        
        # Parse ignore patterns
        ignore_patterns = []
        if ignore:
            ignore_patterns = [pattern.strip() for pattern in ignore.split(',')]
        
        # Run enhanced analysis
        results = analyze_project_enhanced(
            root_path=".",
            depth=depth,
            ignore_patterns=ignore_patterns,
            ci_mode=ci
        )
        
        # Display results
        project_info = results["project_info"]
        languages = results["languages"]
        frameworks = results["frameworks"]
        
        click.echo(f"✅ Analysis complete!")
        click.echo(f"📄 Results saved to: {overlay_paths.get_docs_dir()}/discovery/report.json")
        click.echo(f"📊 Summary saved to: {overlay_paths.get_docs_dir()}/discovery/summary.md")
        click.echo(f"🔍 Files analyzed: {project_info['file_count']:,}")
        click.echo(f"📁 Directories found: {project_info['directory_count']:,}")
        click.echo(f"🛠️  Languages: {', '.join(languages['detected']) if languages['detected'] else 'None detected'}")
        if frameworks["detected"]:
            click.echo(f"🏗️  Frameworks: {', '.join(frameworks['detected'])}")
        
    except Exception as e:
        click.echo(f"❌ Error during analysis: {e}")
        return 1
    
    return 0


@cli.command("plan")
@click.option("--persona", type=click.Choice(['dev', 'pm', 'ai']), default='dev', help="Interview persona")
@click.option("--noninteractive", is_flag=True, help="Use defaults instead of prompts")
def plan_command(persona, noninteractive):
    """
    Create project plan through guided interview.
    
    This command routes to the discover:analyze command with appropriate parameters.
    """
    try:
        # Import the discover analyze command
        from ..core.cli.discovery_commands import discover_analyze
        
        # Call the discover:analyze command with parameters
        discover_analyze(persona=persona, noninteractive=noninteractive)
        
    except ImportError as e:
        click.echo(f"❌ Error: Discovery analyze command not available: {e}")
        click.echo("💡 Try running: cb discover:analyze")
        return 1
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        return 1
    
    return 0


def register_simple_commands():
    """Register simple command aliases with the main CLI."""
    # Commands are already registered via the @cli.command decorators
    pass


def get_command_mapping():
    """Get mapping of simple commands to their full implementations."""
    return {
        "analyze": "discover:new",
        "plan": "discover:analyze",
        "status": "orchestrator:status",
        "commands": "commands:list",
        "help": "commands:list"
    }


def create_analyze_rule():
    """Create the @rules/analyze-project rule file."""
    try:
        # Get the rules directory
        rules_dir = Path(overlay_paths.cursor_rules_dir())
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the analyze-project rule
        rule_file = rules_dir / "analyze-project.md"
        
        docs_dir = overlay_paths.get_docs_dir()
        rule_content = f"""# Analyze Project

## Description
Analyze project structure and generate discovery report.

## Usage
```bash
cb analyze
# or
@rules/analyze-project
```

## Agent Instructions
1. Execute the analyze command using Code Builder CLI
2. Follow any prompts or interactive elements
3. Report results and any issues encountered
4. Check generated discovery files

## Expected Outputs
- `{docs_dir}/discovery/analysis.json` - Detailed project analysis
- `{docs_dir}/discovery/summary.md` - Human-readable summary

## Flags
- `--depth N` - Analysis depth (default: 3)
- `--ignore PATTERN` - Ignore files matching pattern
- `--ci` - Non-interactive mode for CI/CD

## Examples
```bash
# Basic analysis
cb analyze

# Deep analysis with custom ignore
cb analyze --depth 5 --ignore "node_modules,dist"

# CI mode
cb analyze --ci
```

## Context
This command has been selected based on current project state and dependencies.
"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        return str(rule_file)
        
    except Exception as e:
        print(f"Error creating analyze-project rule: {e}")
        return None


if __name__ == "__main__":
    # Test the simple router
    print("Simple Router Commands:")
    mapping = get_command_mapping()
    for simple, full in mapping.items():
        print(f"  {simple} -> {full}")
    
    # Create analyze rule
    rule_file = create_analyze_rule()
    if rule_file:
        print(f"Created analyze-project rule: {rule_file}")
    else:
        print("Failed to create analyze-project rule")
