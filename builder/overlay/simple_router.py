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
        import os
        import json
        from pathlib import Path
        
        click.echo("🔍 Analyzing project structure...")
        
        # Create discovery directory if it doesn't exist
        discovery_dir = Path(overlay_paths.get_docs_dir()) / "discovery"
        discovery_dir.mkdir(parents=True, exist_ok=True)
        
        # Basic project analysis
        analysis = {
            "project_name": Path.cwd().name,
            "analysis_depth": depth,
            "ignore_patterns": ignore or [],
            "ci_mode": ci,
            "timestamp": str(Path.cwd().stat().st_mtime),
            "files_analyzed": 0,
            "directories_found": 0,
            "technologies_detected": [],
            "structure": {}
        }
        
        # Simple file analysis
        files_analyzed = 0
        directories_found = 0
        technologies = set()
        
        for root, dirs, files in os.walk("."):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            if root != ".":
                directories_found += 1
            
            for file in files:
                if not file.startswith('.') and not any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.log']):
                    files_analyzed += 1
                    
                    # Detect technologies by file extension
                    if file.endswith('.py'):
                        technologies.add('Python')
                    elif file.endswith(('.js', '.ts')):
                        technologies.add('JavaScript/TypeScript')
                    elif file.endswith('.md'):
                        technologies.add('Markdown')
                    elif file.endswith('.json'):
                        technologies.add('JSON')
                    elif file.endswith('.yaml') or file.endswith('.yml'):
                        technologies.add('YAML')
                    elif file.endswith('.sh'):
                        technologies.add('Shell Script')
                    elif file.endswith('.go'):
                        technologies.add('Go')
                    elif file.endswith('.rs'):
                        technologies.add('Rust')
                    elif file.endswith('.java'):
                        technologies.add('Java')
                    elif file.endswith('.cpp') or file.endswith('.c'):
                        technologies.add('C/C++')
        
        analysis["files_analyzed"] = files_analyzed
        analysis["directories_found"] = directories_found
        analysis["technologies_detected"] = list(technologies)
        
        # Save analysis results
        analysis_file = discovery_dir / "analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        # Create summary
        summary_file = discovery_dir / "summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Project Analysis Summary\n\n")
            f.write(f"**Project:** {analysis['project_name']}\n")
            f.write(f"**Files Analyzed:** {analysis['files_analyzed']}\n")
            f.write(f"**Directories Found:** {analysis['directories_found']}\n")
            f.write(f"**Technologies Detected:** {', '.join(analysis['technologies_detected'])}\n")
            f.write(f"**Analysis Depth:** {analysis['analysis_depth']}\n")
            f.write(f"**CI Mode:** {analysis['ci_mode']}\n")
        
        click.echo(f"✅ Analysis complete!")
        click.echo(f"📄 Results saved to: {analysis_file}")
        click.echo(f"📊 Summary saved to: {summary_file}")
        click.echo(f"🔍 Files analyzed: {files_analyzed}")
        click.echo(f"📁 Directories found: {directories_found}")
        click.echo(f"🛠️  Technologies: {', '.join(technologies) if technologies else 'None detected'}")
        
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
