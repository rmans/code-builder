#!/usr/bin/env python3
"""
Agent Tracking System for Concurrent Task Management

This module tracks which agent created which files to prevent cleanup
from interfering with concurrent agent operations.
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Import configuration system
from ..config.settings import get_config


@dataclass
class AgentSession:
    """Represents an active agent session."""
    agent_id: str
    session_id: str
    start_time: datetime
    last_activity: datetime
    created_files: Set[str]
    status: str  # 'active', 'completed', 'failed', 'timeout'
    task_description: str
    working_directory: str


class AgentTracker:
    """Tracks agent sessions and file ownership for safe cleanup."""
    
    def __init__(self, cache_dir: str = None):
        # Use configuration system for cache directory
        config = get_config()
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.cache_dir / "agent_sessions.json"
        self.sessions: Dict[str, AgentSession] = {}
        self.load_sessions()
    
    def load_sessions(self):
        """Load existing sessions from cache."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    for session_id, session_data in data.items():
                        # Convert datetime strings back to datetime objects
                        session_data['start_time'] = datetime.fromisoformat(session_data['start_time'])
                        session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])
                        session_data['created_files'] = set(session_data['created_files'])
                        self.sessions[session_id] = AgentSession(**session_data)
            except Exception as e:
                print(f"Warning: Could not load agent sessions: {e}")
                self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to cache."""
        try:
            data = {}
            for session_id, session in self.sessions.items():
                session_dict = asdict(session)
                # Convert datetime objects to strings for JSON serialization
                session_dict['start_time'] = session.start_time.isoformat()
                session_dict['last_activity'] = session.last_activity.isoformat()
                session_dict['created_files'] = list(session.created_files)
                data[session_id] = session_dict
            
            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save agent sessions: {e}")
    
    def create_session(self, agent_id: str, task_description: str, working_directory: str = ".") -> str:
        """Create a new agent session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = AgentSession(
            agent_id=agent_id,
            session_id=session_id,
            start_time=now,
            last_activity=now,
            created_files=set(),
            status='active',
            task_description=task_description,
            working_directory=os.path.abspath(working_directory)
        )
        
        self.sessions[session_id] = session
        self.save_sessions()
        return session_id
    
    def update_activity(self, session_id: str):
        """Update the last activity time for a session."""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now()
            self.save_sessions()
    
    def add_created_file(self, session_id: str, file_path: str):
        """Add a file to the list of files created by an agent."""
        if session_id in self.sessions:
            self.sessions[session_id].created_files.add(os.path.abspath(file_path))
            self.update_activity(session_id)
    
    def add_created_files(self, session_id: str, file_paths: List[str]):
        """Add multiple files to the list of files created by an agent."""
        if session_id in self.sessions:
            for file_path in file_paths:
                self.sessions[session_id].created_files.add(os.path.abspath(file_path))
            self.update_activity(session_id)
    
    def complete_session(self, session_id: str):
        """Mark a session as completed."""
        if session_id in self.sessions:
            self.sessions[session_id].status = 'completed'
            self.sessions[session_id].last_activity = datetime.now()
            self.save_sessions()
    
    def fail_session(self, session_id: str):
        """Mark a session as failed."""
        if session_id in self.sessions:
            self.sessions[session_id].status = 'failed'
            self.sessions[session_id].last_activity = datetime.now()
            self.save_sessions()
    
    def get_active_sessions(self) -> List[AgentSession]:
        """Get all active sessions."""
        return [session for session in self.sessions.values() if session.status == 'active']
    
    def get_session_files(self, session_id: str) -> Set[str]:
        """Get all files created by a specific session."""
        if session_id in self.sessions:
            return self.sessions[session_id].created_files
        return set()
    
    def get_all_protected_files(self) -> Set[str]:
        """Get all files that should be protected from cleanup."""
        protected = set()
        for session in self.sessions.values():
            if session.status == 'active':
                protected.update(session.created_files)
        return protected
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            self.save_sessions()
            print(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def timeout_inactive_sessions(self, timeout_minutes: int = 60):
        """Mark sessions as timed out if they haven't been active for timeout_minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        timed_out = 0
        
        for session in self.sessions.values():
            if session.status == 'active' and session.last_activity < cutoff_time:
                session.status = 'timeout'
                timed_out += 1
        
        if timed_out:
            self.save_sessions()
            print(f"Marked {timed_out} sessions as timed out")
    
    def get_session_info(self, session_id: str) -> Optional[AgentSession]:
        """Get information about a specific session."""
        return self.sessions.get(session_id)
    
    def list_sessions(self, status_filter: Optional[str] = None) -> List[AgentSession]:
        """List sessions, optionally filtered by status."""
        sessions = list(self.sessions.values())
        if status_filter:
            sessions = [s for s in sessions if s.status == status_filter]
        return sorted(sessions, key=lambda s: s.last_activity, reverse=True)
    
    def get_agent_files(self, agent_id: str) -> Set[str]:
        """Get all files created by a specific agent across all sessions."""
        files = set()
        for session in self.sessions.values():
            if session.agent_id == agent_id and session.status == 'active':
                files.update(session.created_files)
        return files


def get_current_session_id() -> Optional[str]:
    """Get the current session ID from environment variable."""
    return os.environ.get('CODE_BUILDER_SESSION_ID')


def set_current_session_id(session_id: str):
    """Set the current session ID in environment variable."""
    os.environ['CODE_BUILDER_SESSION_ID'] = session_id


def track_file_creation(file_path: str, session_id: Optional[str] = None):
    """Track a file creation for the current or specified session."""
    if session_id is None:
        session_id = get_current_session_id()
    
    if session_id:
        tracker = AgentTracker()
        tracker.add_created_file(session_id, file_path)


def track_files_creation(file_paths: List[str], session_id: Optional[str] = None):
    """Track multiple file creations for the current or specified session."""
    if session_id is None:
        session_id = get_current_session_id()
    
    if session_id:
        tracker = AgentTracker()
        tracker.add_created_files(session_id, file_paths)
