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


@cli.command("create-context")
@click.option("--sections", multiple=True, type=click.Choice(['prd', 'arch', 'int', 'impl', 'exec', 'task']),
              default=['prd', 'arch', 'int', 'impl', 'exec', 'task'], help="Sections to generate")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
@click.option("--from", "from_sources", multiple=True, type=click.Choice(['discovery', 'interview']),
              default=['discovery', 'interview'], help="Sources to build context from")
def create_context_command(sections, overwrite, from_sources):
    """
    Create comprehensive project context from discovery and interview data.
    
    This command generates PRD, Architecture, Integration Plan, Implementation Roadmap,
    Execution Plan, and Tasks from discovery and interview data.
    """
    try:
        # Import the context builder
        from ..core.context_builder import build_context_cli
        
        # Run context building
        results = build_context_cli(
            from_sources=list(from_sources),
            overwrite=overwrite,
            sections=list(sections)
        )
        
        # Display results
        click.echo(f"✅ Context creation complete!")
        click.echo(f"   Generated sections: {', '.join(sections)}")
        click.echo(f"   Sources: {', '.join(from_sources)}")
        
        # Show generated files
        for section, result in results.items():
            if isinstance(result, dict) and 'file' in result:
                click.echo(f"   📄 {section}: {result['file']}")
            elif isinstance(result, dict) and 'files' in result:
                click.echo(f"   📄 {section}: {len(result['files'])} files")
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error creating context: {e}")
        return 1


def register_simple_commands():
    """Register simple command aliases with the main CLI."""
    # Commands are already registered via the @cli.command decorators
    pass


def get_command_mapping():
    """Get mapping of simple commands to their full implementations."""
    return {
        "analyze": "discover:new",
        "plan": "discover:analyze",
        "create-context": "ctx:build",
        "status": "orchestrator:status",
        "commands": "commands:list",
        "help": "commands:list"
    }


def create_create_context_rule():
    """Create the @rules/create-context rule file."""
    try:
        # Get the rules directory
        rules_dir = Path(overlay_paths.cursor_rules_dir())
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the create-context rule
        rule_file = rules_dir / "create-context.md"
        
        rule_content = """---
id: create-context
title: Create Context
description: Generate comprehensive project context from discovery and interview data
status: active
created: 2025-09-07
updated: 2025-09-07
owner: system
domain: context
priority: 8
agent_type: backend
dependencies: [analyze-project, plan-project]
tags: [context, generation, documentation]
---

# Command: Create Context

## Description
Generates comprehensive project context documents including PRD, Architecture, Integration Plan, Implementation Roadmap, Execution Plan, and Tasks from discovery and interview data.

## Usage
```bash
cb create-context
# or
@rules/create-context
```

## Outputs
- `cb_docs/prd/PRD-{date}-{title}.md` - Product Requirements Document
- `cb_docs/arch/ARCH-{date}-{title}.md` - Architecture Document
- `cb_docs/integrations/INT-{date}-{title}.md` - Integration Plan
- `cb_docs/impl/IMPL-{date}-{title}.md` - Implementation Roadmap
- `cb_docs/exec/EXEC-{date}-{title}.md` - Execution Plan
- `cb_docs/tasks/TASK-{date}-F{num}.md` - Generated Tasks
- `cb_docs/pack_context.json` - Context Pack Metadata

## Flags
- `--sections SECTIONS` - Specific sections to generate (prd,arch,int,impl,exec,task)
- `--overwrite` - Overwrite existing files
- `--from SOURCES` - Input sources (discovery,interview)

## Examples
```bash
# Generate all context documents
cb create-context

# Generate only PRD and Architecture
cb create-context --sections prd,arch

# Overwrite existing files
cb create-context --overwrite

# Use specific input sources
cb create-context --from discovery --from interview
```

## Template Variables
- `{{project_name}}` - Project name from discovery
- `{{product_name}}` - Product name from interview
- `{{persona}}` - Interview persona
- `{{technical_requirements}}` - Technical requirements
- `{{project_type}}` - Project type (web, api, cli, etc.)
- `{{framework}}` - Primary framework
- `{{language}}` - Primary language
"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        return True
        
    except Exception as e:
        print(f"Error creating create-context rule: {e}")
        return False


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
