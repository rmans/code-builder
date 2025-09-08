#!/usr/bin/env python3
"""
Metrics Collection Module

Collects and manages command metrics including execution times, success rates,
and discovery metrics for the Code Builder system.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class CommandExecution:
    """Represents a single command execution."""
    command_id: str
    start_time: float
    end_time: float
    success: bool
    exit_code: int
    args: List[str]
    timestamp: str


@dataclass
class DiscoveryMetrics:
    """Discovery-related metrics."""
    time_to_first_rules: Optional[float] = None
    command_discovery_rate: float = 0.0
    execution_success_rate: float = 0.0


@dataclass
class CommandMetrics:
    """Command execution metrics."""
    total_commands_run: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_execution_time_ms: float = 0.0
    most_used_commands: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.most_used_commands is None:
            self.most_used_commands = []


@dataclass
class PerformanceMetrics:
    """Performance-related metrics."""
    cache_hit_rate: float = 0.0
    average_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0


@dataclass
class SessionMetrics:
    """Session-related metrics."""
    current_session_start: Optional[str] = None
    total_sessions: int = 0
    average_session_duration_minutes: float = 0.0


class MetricsCollector:
    """Collects and manages metrics for the Code Builder system."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.command_state_dir = cache_dir / "command_state"
        self.metrics_file = self.command_state_dir / "metrics.json"
        self.state_file = self.command_state_dir / "state.json"
        
        # Ensure directories exist
        self.command_state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics if not exists
        self._initialize_metrics()
        self._initialize_state()
    
    def _initialize_metrics(self) -> None:
        """Initialize metrics.json if it doesn't exist."""
        if not self.metrics_file.exists():
            metrics = {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "command_metrics": asdict(CommandMetrics()),
                "discovery_metrics": asdict(DiscoveryMetrics()),
                "performance_metrics": asdict(PerformanceMetrics()),
                "session_metrics": asdict(SessionMetrics())
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
    
    def _initialize_state(self) -> None:
        """Initialize state.json if it doesn't exist."""
        if not self.state_file.exists():
            state = {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "project_state": {
                    "initialized": False,
                    "discovered": False,
                    "analyzed": False,
                    "planned": False,
                    "context_created": False
                },
                "command_history": [],
                "active_tasks": [],
                "completed_tasks": [],
                "cache_metadata": {
                    "last_cleanup": None,
                    "size_bytes": 0,
                    "file_count": 0
                }
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
    
    def record_command_execution(self, command_id: str, start_time: float, 
                               end_time: float, success: bool, exit_code: int, 
                               args: List[str]) -> None:
        """Record a command execution."""
        # Redact sensitive arguments
        redacted_args = self._redact_sensitive_args(args)
        
        execution = CommandExecution(
            command_id=command_id,
            start_time=start_time,
            end_time=end_time,
            success=success,
            exit_code=exit_code,
            args=redacted_args,
            timestamp=datetime.now().isoformat()
        )
        
        # Update metrics
        self._update_command_metrics(execution)
        
        # Update command history in state
        self._update_command_history(execution)
        
        # Update discovery metrics if this is the first rules command
        if command_id.endswith('rules') and self._is_first_rules_command():
            self._update_discovery_metrics(execution)
    
    def _update_command_metrics(self, execution: CommandExecution) -> None:
        """Update command metrics based on execution."""
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        cmd_metrics = metrics["command_metrics"]
        cmd_metrics["total_commands_run"] += 1
        
        if execution.success:
            cmd_metrics["successful_commands"] += 1
        else:
            cmd_metrics["failed_commands"] += 1
        
        # Update average execution time
        execution_time_ms = (execution.end_time - execution.start_time) * 1000
        total_commands = cmd_metrics["total_commands_run"]
        current_avg = cmd_metrics["average_execution_time_ms"]
        cmd_metrics["average_execution_time_ms"] = (
            (current_avg * (total_commands - 1) + execution_time_ms) / float(total_commands)
        )
        
        # Update most used commands
        self._update_most_used_commands(cmd_metrics, execution.command_id)
        
        # Update execution success rate
        metrics["discovery_metrics"]["execution_success_rate"] = (
            float(cmd_metrics["successful_commands"]) / float(cmd_metrics["total_commands_run"])
        )
        
        metrics["updated"] = datetime.now().isoformat()
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def _update_most_used_commands(self, cmd_metrics: Dict[str, Any], command_id: str) -> None:
        """Update the most used commands list."""
        most_used = cmd_metrics["most_used_commands"]
        
        # Find existing entry
        for cmd in most_used:
            if cmd["command_id"] == command_id:
                cmd["count"] += 1
                break
        else:
            # Add new entry
            most_used.append({"command_id": command_id, "count": 1})
        
        # Sort by count (descending) and keep top 10
        most_used.sort(key=lambda x: x["count"], reverse=True)
        cmd_metrics["most_used_commands"] = most_used[:10]
    
    def _update_command_history(self, execution: CommandExecution) -> None:
        """Update command history in state.json."""
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        history_entry = {
            "command_id": execution.command_id,
            "timestamp": execution.timestamp,
            "success": execution.success,
            "exit_code": execution.exit_code,
            "execution_time_ms": (execution.end_time - execution.start_time) * 1000,
            "args": execution.args
        }
        
        state["command_history"].append(history_entry)
        
        # Keep only last 100 entries
        if len(state["command_history"]) > 100:
            state["command_history"] = state["command_history"][-100:]
        
        state["updated"] = datetime.now().isoformat()
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Check for size cap and rotation
        self._check_and_rotate_files()
    
    def _is_first_rules_command(self) -> bool:
        """Check if this is the first rules command execution."""
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        return metrics["discovery_metrics"]["time_to_first_rules"] is None
    
    def _update_discovery_metrics(self, execution: CommandExecution) -> None:
        """Update discovery metrics for first rules command."""
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        # Calculate time to first rules (from session start or project init)
        session_start = metrics["session_metrics"]["current_session_start"]
        if session_start:
            start_time = datetime.fromisoformat(session_start).timestamp()
            metrics["discovery_metrics"]["time_to_first_rules"] = execution.start_time - start_time
        
        # Update command discovery rate (commands discovered per minute)
        total_commands = metrics["command_metrics"]["total_commands_run"]
        if total_commands > 0:
            # This is a simplified calculation - in practice, you'd track actual discovery
            metrics["discovery_metrics"]["command_discovery_rate"] = float(total_commands) / 60.0
        
        metrics["updated"] = datetime.now().isoformat()
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def start_session(self) -> None:
        """Start a new session."""
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        metrics["session_metrics"]["current_session_start"] = datetime.now().isoformat()
        metrics["session_metrics"]["total_sessions"] += 1
        metrics["updated"] = datetime.now().isoformat()
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with open(self.metrics_file, 'r') as f:
            return json.load(f)
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command history."""
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        return state.get("command_history", [])
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a concise status summary for cb status command."""
        metrics = self.get_metrics()
        history = self.get_command_history()
        
        recent_commands = history[-5:] if history else []
        
        return {
            "total_commands": metrics["command_metrics"]["total_commands_run"],
            "success_rate": metrics["discovery_metrics"]["execution_success_rate"],
            "avg_execution_time": metrics["command_metrics"]["average_execution_time_ms"],
            "recent_commands": recent_commands,
            "most_used": metrics["command_metrics"]["most_used_commands"][:3],
            "last_updated": metrics["updated"]
        }
    
    def _check_and_rotate_files(self) -> None:
        """Check file sizes and rotate if necessary."""
        max_size_mb = 10  # 10MB limit
        
        for file_path in [self.metrics_file, self.state_file]:
            if file_path.exists():
                size_mb = float(file_path.stat().st_size) / (1024 * 1024)
                if size_mb > max_size_mb:
                    self._rotate_file(file_path)
    
    def _rotate_file(self, file_path: Path) -> None:
        """Rotate a file by creating a backup and resetting the original."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".{timestamp}.json")
        
        # Create backup
        file_path.rename(backup_path)
        
        # Reset original file
        if file_path.name == "metrics.json":
            self._initialize_metrics()
        elif file_path.name == "state.json":
            self._initialize_state()
        
        # Keep only last 5 backups
        self._cleanup_old_backups(file_path)
    
    def _cleanup_old_backups(self, file_path: Path) -> None:
        """Keep only the last 5 backup files."""
        pattern = f"{file_path.stem}.*.json"
        backups = list(file_path.parent.glob(pattern))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups (keep only 5 most recent)
        for backup in backups[5:]:
            backup.unlink()
    
    def _redact_sensitive_args(self, args: List[str]) -> List[str]:
        """Redact sensitive information from command arguments."""
        sensitive_patterns = [
            'password', 'passwd', 'pwd', 'secret', 'key', 'token', 
            'auth', 'credential', 'api_key', 'access_token'
        ]
        
        redacted = []
        for arg in args:
            # Check if argument contains sensitive information
            is_sensitive = any(pattern in arg.lower() for pattern in sensitive_patterns)
            
            if is_sensitive and '=' in arg:
                # Redact value part of key=value pairs
                key, value = arg.split('=', 1)
                redacted.append(f"{key}=[REDACTED]")
            elif is_sensitive:
                # Redact entire argument
                redacted.append("[REDACTED]")
            else:
                redacted.append(arg)
        
        return redacted
