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

# Utility Commands
@cli.command("cleanup:artifacts")
@click.option("--dry-run", is_flag=True, default=True, help="Show what would be cleaned up without actually deleting")
@click.option("--clean", is_flag=True, help="Actually perform the cleanup")
@click.option("--root", default=".", help="Root directory to scan")
@click.option("--ignore-agents", is_flag=True, help="Ignore agent ownership and clean all artifacts")
@click.option("--check-agents", is_flag=True, help="Check for active agents before cleanup")
@click.option("--agent-workspaces", is_flag=True, help="Also clean up completed agent workspaces")
def cleanup_artifacts(dry_run, clean, root, ignore_agents, check_agents, agent_workspaces):
    """Clean up test/example artifacts outside of designated directories."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        try:
            from utils.cleanup_rules import ArtifactCleaner
            from utils.agent_tracker import AgentTracker
        except ImportError:
            click.echo("❌ Required utility modules not available. Make sure utils/cleanup_rules.py and utils/agent_tracker.py exist.")
            return 1
        
        respect_ownership = not ignore_agents
        cleaner = ArtifactCleaner(root, respect_agent_ownership=respect_ownership)
        
        # Check for active agents if requested
        if check_agents and not ignore_agents:
            try:
                agent_tracker = AgentTracker()
                active_agents = agent_tracker.get_active_sessions()
                if active_agents:
                    click.echo(f"⚠️ Found {len(active_agents)} active agent sessions:")
                    for session in active_agents:
                        click.echo(f"   • {session.session_id}: {session.agent_id} ({len(session.created_files)} files)")
                    click.echo("🛡️ Agent ownership protection enabled - will skip files created by active agents")
                else:
                    click.echo("✅ No active agents found - safe to clean all artifacts")
            except Exception as e:
                click.echo(f"⚠️ Could not check agent status: {e}")
        
        if respect_ownership:
            click.echo("🛡️ Agent ownership protection enabled - will skip files created by active agents")
        else:
            click.echo("⚠️ Agent ownership protection disabled - will clean all artifacts")
        
        # Clean up agent workspaces if requested
        if agent_workspaces:
            click.echo("🧹 Cleaning up completed agent workspaces...")
            try:
                from utils.multi_agent_cursor import MultiAgentCursorManager
                manager = MultiAgentCursorManager()
                cleaned_workspaces = manager.cleanup_completed_workspaces()
                if cleaned_workspaces:
                    click.echo(f"✅ Cleaned up {len(cleaned_workspaces)} completed agent workspaces")
                else:
                    click.echo("ℹ️ No completed agent workspaces found")
            except ImportError:
                click.echo("⚠️ MultiAgentCursorManager not available - skipping workspace cleanup")
            except Exception as e:
                click.echo(f"⚠️ Error cleaning workspaces: {e}")
        
        if clean:
            click.echo("🧹 Performing cleanup...")
            cleaned_files = cleaner.cleanup()
            if cleaned_files:
                click.echo(f"✅ Cleaned up {len(cleaned_files)} files:")
                for file_path in cleaned_files:
                    click.echo(f"   • {file_path}")
            else:
                click.echo("ℹ️ No files needed cleanup")
        else:
            click.echo("🔍 Scanning for artifacts to clean up...")
            artifacts = cleaner.scan()
            if artifacts:
                click.echo(f"Found {len(artifacts)} files that could be cleaned up:")
                for file_path in artifacts:
                    click.echo(f"   • {file_path}")
                click.echo("\nUse --clean to actually perform the cleanup")
            else:
                click.echo("✅ No artifacts found that need cleanup")
        
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")
        return 1
    
    return 0

@cli.command("yaml:check")
@click.argument("target", default=".")
@click.option("--yaml-file", help="Validate specific YAML file")
def yaml_check(target, yaml_file):
    """Check for Python code issues in YAML files."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        try:
            from utils.yaml_python_validator import validate_yaml_python, find_python_in_yaml_files
        except ImportError:
            click.echo("❌ Required utility module not available. Make sure utils/yaml_python_validator.py exists.")
            return 1
        
        if yaml_file:
            # Validate specific YAML file
            is_valid, errors, warnings = validate_yaml_python(yaml_file)
            
            click.echo(f"Validating Python code in YAML: {yaml_file}")
            
            if warnings:
                for warning in warnings:
                    click.echo(f"  ⚠️  {warning}")
            
            if errors:
                for error in errors:
                    click.echo(f"  ❌ {error}")
            
            if is_valid:
                click.echo("  ✅ Python code in YAML is valid")
            else:
                click.echo("  ❌ Python code in YAML has issues")
                return 1
        else:
            # Find Python issues in YAML files
            click.echo(f"Checking for Python code issues in YAML files: {target}")
            issues = find_python_in_yaml_files(target)
            
            if issues:
                click.echo("\nFound Python code issues in YAML files:")
                for file_path, file_issues in issues.items():
                    click.echo(f"\n{file_path}:")
                    for issue in file_issues:
                        click.echo(f"  {issue}")
                return 1
            else:
                click.echo("✅ No Python code issues found in YAML files")
        
    except Exception as e:
        click.echo(f"❌ Error checking YAML files: {e}")
        return 1
    
    return 0

@cli.command("fields:check")
@click.argument("target", default=".")
@click.option("--context-pack", help="Validate specific context pack file")
def fields_check(target, context_pack):
    """Check for field name consistency issues."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        try:
            from utils.field_name_validator import validate_context_pack_fields, find_field_name_issues
        except ImportError:
            click.echo("❌ Required utility module not available. Make sure utils/field_name_validator.py exists.")
            return 1
        
        if context_pack:
            # Validate specific context pack
            is_valid, errors, warnings = validate_context_pack_fields(context_pack)
            
            click.echo(f"Validating context pack: {context_pack}")
            
            if warnings:
                for warning in warnings:
                    click.echo(f"  ⚠️  {warning}")
            
            if errors:
                for error in errors:
                    click.echo(f"  ❌ {error}")
            
            if is_valid:
                click.echo("  ✅ Context pack field names are valid")
            else:
                click.echo("  ❌ Context pack has field name issues")
                return 1
        else:
            # Find field name issues in directory
            click.echo(f"Checking for field name issues in: {target}")
            issues = find_field_name_issues(target)
            
            if issues:
                click.echo("\nFound field name issues:")
                for file_path, file_issues in issues.items():
                    click.echo(f"\n{file_path}:")
                    for issue in file_issues:
                        click.echo(f"  ❌ {issue}")
                return 1
            else:
                click.echo("✅ No field name issues found")
        
    except Exception as e:
        click.echo(f"❌ Error checking field names: {e}")
        return 1
    
    return 0
