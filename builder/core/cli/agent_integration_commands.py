#!/usr/bin/env python3
"""
Agent Integration Commands Module

This module contains commands for integrating with Cursor agents.
"""

import click
import json
from .base import cli, get_project_root, track_command

# Import required modules and functions
try:
    from ...overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    CACHE = ROOT / ".cb" / "cache"

@cli.command("agent:get-command")
@click.option("--context", help="JSON context for command selection")
@click.option("--output", type=click.Choice(['text', 'json']), default='text')
@track_command("agent:get-command")
def agent_get_command(context, output):
    """Get recommended command for Cursor agent based on current context."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        from builder.utils.command_agent_integration import get_command_for_agent
        
        # Parse context if provided
        context_data = None
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                click.echo("❌ Error: Invalid JSON context provided")
                return 1
        
        # Get recommended command
        command_id, rules_command = get_command_for_agent(context_data)
        
        if output == 'json':
            result = {
                "command_id": command_id,
                "rules_command": rules_command,
                "context": context_data
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"🎯 Recommended Command: {command_id}")
            click.echo(f"📋 Rules Command: {rules_command}")
            if context_data:
                click.echo(f"📊 Context: {json.dumps(context_data, indent=2)}")
        
    except ImportError as e:
        click.echo(f"❌ Error: Required module not available: {e}")
        return 1
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        return 1
    
    return 0

@cli.command("agent:create-rules")
@click.argument("command_id")
@click.option("--status", is_flag=True, help="Create project status rules instead")
@track_command("agent:create-rules")
def agent_create_rules(command_id, status):
    """Create @rules/ command files for Cursor agents."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        from builder.utils.command_agent_integration import CommandAgentIntegration
        
        integration = CommandAgentIntegration()
        
        if status:
            # Create project status rules
            rules_file = integration.create_project_status_rules()
            click.echo(f"✅ Created project status rules: {rules_file}")
        else:
            # Create command-specific rules
            rules_file = integration.create_rules_command(command_id)
            click.echo(f"✅ Created rules for {command_id}: {rules_file}")
        
    except ImportError as e:
        click.echo(f"❌ Error: Required module not available: {e}")
        return 1
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        return 1
    
    return 0

@cli.command("agent:integrate")
@click.option("--output", type=click.Choice(['text', 'json']), default='text')
@track_command("agent:integrate")
def agent_integrate(output):
    """Integrate command system with Cursor agents."""
    try:
        import sys
        import os
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        
        from builder.utils.command_agent_integration import CommandAgentIntegration
        
        integration = CommandAgentIntegration()
        result = integration.integrate_with_agents()
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("🤖 Agent Integration Complete!")
            click.echo(f"🎯 Recommended Command: {result['recommended_command']}")
            click.echo(f"📋 Rules Command: {result['rules_command']}")
            click.echo(f"📄 Command File: {result['command_file']}")
            click.echo(f"📊 Status File: {result['status_file']}")
            click.echo(f"📚 Available Commands: {result['available_commands']}")
        
    except ImportError as e:
        click.echo(f"❌ Error: Required module not available: {e}")
        return 1
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        return 1
    
    return 0
