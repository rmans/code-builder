#!/usr/bin/env python3
"""
Utility Commands Module

This module contains utility commands like commands:*, cleanup:*, yaml:*, fields:*
"""

import click
import shutil
import subprocess
from pathlib import Path
from .base import cli, safe_yaml_load, safe_json_dumps, common_output_format_option, common_force_option, common_dry_run_option

# Commands family
@cli.command("commands:list")
@common_output_format_option()
@click.option("--status", type=click.Choice(['active', 'inactive', 'all']), default='active')
def commands_list(output_format, status):
    """List available commands from cb_docs/commands/ directory."""
    commands_dir = Path('cb_docs/commands')
    if not commands_dir.exists():
        click.echo("❌ No commands directory found. Run 'cb commands:refresh' first.")
        return 1
    
    commands = []
    for cmd_file in commands_dir.glob('*.md'):
        try:
            with open(cmd_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    cmd_data = safe_yaml_load(frontmatter)
                    if cmd_data:
                        cmd_data['file'] = str(cmd_file)
                        commands.append(cmd_data)
                    else:
                        # Fallback for malformed YAML
                        commands.append({
                            'id': cmd_file.stem,
                            'title': cmd_file.stem.replace('-', ' ').title(),
                            'status': 'unknown',
                            'file': str(cmd_file)
                        })
        except Exception as e:
            click.echo(f"⚠️  Error reading {cmd_file}: {e}")
    
    # Filter by status
    if status != 'all':
        commands = [cmd for cmd in commands if cmd.get('status', 'unknown') == status]
    
    # Sort by priority (higher first) then by title
    commands.sort(key=lambda x: (-x.get('priority', 0), x.get('title', '')))
    
    if output_format == 'json':
        click.echo(safe_json_dumps(commands))
    elif output_format == 'yaml':
        import yaml
        click.echo(yaml.dump(commands, default_flow_style=False))
    else:  # table format
        if not commands:
            click.echo("No commands found.")
            return 0
        
        # Create table
        click.echo(f"📋 Available Commands ({len(commands)} found)")
        click.echo("")
        
        for cmd in commands:
            status_icon = "✅" if cmd.get('status') == 'active' else "⏸️" if cmd.get('status') == 'inactive' else "❓"
            priority = cmd.get('priority', 0)
            title = cmd.get('title', cmd.get('id', 'Unknown'))
            domain = cmd.get('domain', 'general')
            description = cmd.get('description', 'No description')
            
            click.echo(f"{status_icon} {title}")
            click.echo(f"   ID: {cmd.get('id', 'unknown')}")
            click.echo(f"   Domain: {domain}")
            click.echo(f"   Priority: {priority}")
            click.echo(f"   Description: {description}")
            if cmd.get('tags'):
                click.echo(f"   Tags: {', '.join(cmd.get('tags', []))}")
            click.echo("")
    
    return 0

@cli.command("commands:show")
@click.argument("command_name")
@click.option("--format", "output_format", type=click.Choice(['full', 'metadata', 'usage']), default='full')
def commands_show(command_name, output_format):
    """Show detailed information about a specific command."""
    commands_dir = Path('cb_docs/commands')
    if not commands_dir.exists():
        click.echo("❌ No commands directory found. Run 'cb commands:refresh' first.")
        return 1
    
    # Find the command file
    cmd_file = commands_dir / f"{command_name}.md"
    if not cmd_file.exists():
        click.echo(f"❌ Command '{command_name}' not found.")
        click.echo("Available commands:")
        for f in commands_dir.glob('*.md'):
            click.echo(f"  - {f.stem}")
        return 1
    
    try:
        with open(cmd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            click.echo(f"❌ Invalid command file format: {cmd_file}")
            return 1
        
        # Parse frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            click.echo(f"❌ Invalid command file format: {cmd_file}")
            return 1
        
        frontmatter = parts[1]
        markdown_content = parts[2].strip()
        
        cmd_data = safe_yaml_load(frontmatter)
        if not cmd_data:
            return 1
        
        if output_format == 'metadata':
            click.echo(safe_json_dumps(cmd_data))
        elif output_format == 'usage':
            # Extract usage section
            lines = markdown_content.split('\n')
            in_usage = False
            for line in lines:
                if line.strip().startswith('## Usage'):
                    in_usage = True
                    continue
                elif line.strip().startswith('##') and in_usage:
                    break
                elif in_usage:
                    click.echo(line)
        else:  # full format
            click.echo(f"📋 Command: {cmd_data.get('title', command_name)}")
            click.echo(f"ID: {cmd_data.get('id', 'unknown')}")
            click.echo(f"Status: {cmd_data.get('status', 'unknown')}")
            click.echo(f"Domain: {cmd_data.get('domain', 'general')}")
            click.echo(f"Priority: {cmd_data.get('priority', 0)}")
            click.echo(f"Owner: {cmd_data.get('owner', 'unknown')}")
            click.echo(f"Agent Type: {cmd_data.get('agent_type', 'unknown')}")
            if cmd_data.get('dependencies'):
                click.echo(f"Dependencies: {', '.join(cmd_data.get('dependencies', []))}")
            if cmd_data.get('tags'):
                click.echo(f"Tags: {', '.join(cmd_data.get('tags', []))}")
            click.echo("")
            click.echo("Description:")
            click.echo(cmd_data.get('description', 'No description'))
            click.echo("")
            click.echo("Content:")
            click.echo(markdown_content)
    
    except Exception as e:
        click.echo(f"❌ Error reading command file: {e}")
        return 1
    
    return 0

@cli.command("commands:refresh")
@common_force_option()
def commands_refresh(force):
    """Refresh commands from templates and sync to cb_docs/commands/."""
    commands_dir = Path('cb_docs/commands')
    templates_dir = Path('cb_docs/templates/commands')
    
    if not templates_dir.exists():
        click.echo("❌ No templates directory found. Run installer first.")
        return 1
    
    if commands_dir.exists() and not force:
        click.echo("⚠️  Commands directory already exists. Use --force to overwrite.")
        return 1
    
    try:
        # Create commands directory
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy templates to commands
        template_files = list(templates_dir.glob('*.md'))
        if not template_files:
            click.echo("❌ No command templates found.")
            return 1
        
        copied_count = 0
        for template_file in template_files:
            dest_file = commands_dir / template_file.name
            shutil.copy2(template_file, dest_file)
            copied_count += 1
            click.echo(f"✅ Copied {template_file.name}")
        
        click.echo(f"✅ Refreshed {copied_count} commands")
        
        # Run rule merger to sync @rules/ files
        merge_script = Path('.cb/bin/merge-rules')
        if merge_script.exists():
            result = subprocess.run([str(merge_script)], capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("✅ Synced @rules/ files")
            else:
                click.echo(f"⚠️  Warning: Rule merger failed: {result.stderr}")
        
    except Exception as e:
        click.echo(f"❌ Error refreshing commands: {e}")
        return 1
    
    return 0

@cli.command("commands:sync")
@common_dry_run_option()
def commands_sync(dry_run):
    """Sync commands with the rule merger and update @rules/ files."""
    commands_dir = Path('cb_docs/commands')
    if not commands_dir.exists():
        click.echo("❌ No commands directory found. Run 'cb commands:refresh' first.")
        return 1
    
    merge_script = Path('.cb/bin/merge-rules')
    if not merge_script.exists():
        click.echo("❌ Rule merger script not found. Run installer first.")
        return 1
    
    if dry_run:
        click.echo("🔍 Dry run - would sync the following:")
        click.echo(f"  - Commands directory: {commands_dir}")
        click.echo(f"  - Rule merger script: {merge_script}")
        click.echo("  - Would update @rules/ files in .cb/.cursor/rules/")
        return 0
    
    try:
        # Run the rule merger
        result = subprocess.run([str(merge_script)], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("✅ Commands synced successfully")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"❌ Sync failed: {result.stderr}")
            return 1
    
    except Exception as e:
        click.echo(f"❌ Error syncing commands: {e}")
        return 1
    
    return 0

# Placeholder for other utility commands
@cli.command("cleanup:artifacts")
@common_dry_run_option()
def cleanup_artifacts(dry_run):
    """Clean up test/example artifacts from the project."""
    click.echo("🧹 Cleanup artifacts command - to be implemented")
    return 0

@cli.command("yaml:check")
@click.argument("target", default=".")
def yaml_check(target):
    """Check YAML files for syntax errors."""
    click.echo("📋 YAML check command - to be implemented")
    return 0

@cli.command("fields:check")
@click.argument("target", default=".")
def fields_check(target):
    """Check field consistency across documents."""
    click.echo("📋 Fields check command - to be implemented")
    return 0
