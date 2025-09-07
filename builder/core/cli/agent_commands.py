#!/usr/bin/env python3
"""
Agent Commands Module

This module contains agent-related commands like agent:*
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
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    CACHE = ROOT / ".cb" / "cache"

def _get_agent_tracker():
    """Get AgentTracker instance."""
    try:
        # Add the builder directory to the path to import from utils
        builder_dir = os.path.join(os.path.dirname(__file__), '..')
        sys.path.insert(0, os.path.abspath(builder_dir))
        from utils.agent_tracker import AgentTracker
        return AgentTracker()
    except ImportError:
        click.echo("❌ AgentTracker not available. Make sure utils/agent_tracker.py exists.")
        raise SystemExit(1)

# Agent Commands
@cli.command("agent:start")
@click.option("--agent-id", required=True, help="Unique identifier for this agent")
@click.option("--task", required=True, help="Description of the task being performed")
@click.option("--working-dir", default=".", help="Working directory for this agent")
def agent_start(agent_id, task, working_dir):
    """Start a new agent session for tracking file creation."""
    try:
        tracker = _get_agent_tracker()
        session_id = tracker.create_session(agent_id, task, working_dir)
        
        # Set environment variable for this session
        os.environ['CODE_BUILDER_SESSION_ID'] = session_id
        
        click.echo(f"🤖 Started agent session: {session_id}")
        click.echo(f"   Agent ID: {agent_id}")
        click.echo(f"   Task: {task}")
        click.echo(f"   Working Directory: {os.path.abspath(working_dir)}")
        click.echo(f"   Session ID: {session_id}")
        click.echo("💡 Files created by this agent will be protected from cleanup")
        
    except Exception as e:
        click.echo(f"❌ Error starting agent session: {e}")
        raise click.Abort()

@cli.command("agent:stop")
@click.option("--session-id", help="Session ID to stop (defaults to current session)")
@click.option("--status", type=click.Choice(['completed', 'failed']), default='completed', help="Session completion status")
def agent_stop(session_id, status):
    """Stop an agent session."""
    try:
        tracker = _get_agent_tracker()
        
        if not session_id:
            session_id = os.environ.get('CODE_BUILDER_SESSION_ID')
            if not session_id:
                click.echo("❌ No session ID provided and no current session found")
                raise click.Abort()
        
        session = tracker.get_session_info(session_id)
        if not session:
            click.echo(f"❌ Session not found: {session_id}")
            raise click.Abort()
        
        if status == 'completed':
            tracker.complete_session(session_id)
            click.echo(f"✅ Completed agent session: {session_id}")
        else:
            tracker.fail_session(session_id)
            click.echo(f"❌ Failed agent session: {session_id}")
        
        # Clear environment variable
        if os.environ.get('CODE_BUILDER_SESSION_ID') == session_id:
            del os.environ['CODE_BUILDER_SESSION_ID']
        
        click.echo(f"   Agent ID: {session.agent_id}")
        click.echo(f"   Task: {session.task_description}")
        click.echo(f"   Files created: {len(session.created_files)}")
        
    except Exception as e:
        click.echo(f"❌ Error stopping agent session: {e}")
        raise click.Abort()

@cli.command("agent:list")
@click.option("--status", help="Filter by session status (active, completed, failed, timeout)")
@click.option("--agent-id", help="Filter by agent ID")
def agent_list(status, agent_id):
    """List agent sessions."""
    try:
        tracker = _get_agent_tracker()
        sessions = tracker.list_sessions(status_filter=status)
        
        if agent_id:
            sessions = [s for s in sessions if s.agent_id == agent_id]
        
        if not sessions:
            click.echo("📭 No sessions found")
            return
        
        click.echo(f"🤖 Found {len(sessions)} agent sessions:")
        click.echo()
        
        for session in sessions:
            status_emoji = {
                'active': '🟢',
                'completed': '✅',
                'failed': '❌',
                'timeout': '⏰'
            }.get(session.status, '❓')
            
            click.echo(f"{status_emoji} {session.session_id}")
            click.echo(f"   Agent: {session.agent_id}")
            click.echo(f"   Task: {session.task_description}")
            click.echo(f"   Status: {session.status}")
            click.echo(f"   Started: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"   Last Activity: {session.last_activity.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"   Files Created: {len(session.created_files)}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error listing sessions: {e}")
        raise click.Abort()

@cli.command("agent:cleanup")
@click.option("--max-age-hours", default=24, help="Remove sessions older than this many hours")
@click.option("--timeout-minutes", default=60, help="Mark sessions as timed out after this many minutes of inactivity")
def agent_cleanup(max_age_hours, timeout_minutes):
    """Clean up old and timed-out agent sessions."""
    try:
        tracker = _get_agent_tracker()
        
        # Clean up old sessions
        tracker.cleanup_old_sessions(max_age_hours)
        
        # Timeout inactive sessions
        tracker.timeout_inactive_sessions(timeout_minutes)
        
        click.echo("🧹 Agent session cleanup completed")
        
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")
        raise click.Abort()
