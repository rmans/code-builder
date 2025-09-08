#!/usr/bin/env python3
"""
Simple Command Router

This module provides simple command mappings that map short commands
to more complex command sequences for easier usage.
"""

from typing import Dict, List, Optional, Any
import subprocess
import sys
from pathlib import Path

# Import configuration system
from ..config.settings import get_config


class SimpleRouter:
    """Maps simple commands to complex command sequences."""
    
    def __init__(self):
        self.mappings = {
            # Discovery and analysis
            "discover": "discover:new",
            "analyze": "discover:new",
            
            # Context building
            "context": "ctx:build",
            "ctx": "ctx:build",
            
            # Evaluation
            "eval": "eval:objective",
            "evaluate": "eval:objective",
            
            # Task management
            "task": "execute-task --pick",
            "tasks": "execute-tasks",
            "run": "execute-task --pick",
            
            # Documentation
            "docs": "doc:index",
            "doc": "doc:index",
            "documentation": "doc:index",
            
            # Fixing and maintenance
            "fix": ["lint:fix", "format", "cleanup:artifacts"],
            "clean": "cleanup:artifacts",
            "format": "format",
            "lint": "lint:fix",
            
            # Status and monitoring
            "status": "orchestrator:status",
            "state": "orchestrator:status",
            "health": "orchestrator:status",
            
            # Quick actions
            "list": "commands:list",
            "help": "commands:list",
            "refresh": "commands:refresh",
        }
    
    def get_command(self, simple_command: str) -> Optional[str | List[str]]:
        """Get the mapped command(s) for a simple command."""
        return self.mappings.get(simple_command.lower())
    
    def list_available_commands(self) -> Dict[str, str | List[str]]:
        """List all available simple commands and their mappings."""
        return self.mappings.copy()
    
    def execute_simple_command(self, simple_command: str, args: List[str] = None) -> int:
        """Execute a simple command by mapping it to complex commands."""
        if args is None:
            args = []
        
        mapped_command = self.get_command(simple_command)
        
        if not mapped_command:
            print(f"❌ Unknown simple command: {simple_command}")
            print(f"Available commands: {', '.join(self.mappings.keys())}")
            return 1
        
        # Handle single command
        if isinstance(mapped_command, str):
            return self._execute_command(mapped_command, args)
        
        # Handle multiple commands
        elif isinstance(mapped_command, list):
            return self._execute_commands(mapped_command, args)
        
        return 1
    
    def _execute_command(self, command: str, args: List[str]) -> int:
        """Execute a single command."""
        # Build the command as a list for subprocess
        cmd_parts = ["python", "-m", "builder.core.cli"] + command.split()
        if args:
            cmd_parts.extend(args)
        
        print(f"🔄 Executing: {' '.join(cmd_parts)}")
        
        try:
            result = subprocess.run(
                cmd_parts,
                cwd=Path.cwd()
            )
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return 1
    
    def _execute_commands(self, commands: List[str], args: List[str]) -> int:
        """Execute multiple commands in sequence."""
        print(f"🔄 Executing {len(commands)} commands:")
        
        for i, command in enumerate(commands, 1):
            print(f"  {i}. cb {command}")
        
        print()
        
        for i, command in enumerate(commands, 1):
            print(f"🔄 Step {i}/{len(commands)}: {command}")
            
            result = self._execute_command(command, args)
            if result != 0:
                print(f"❌ Command failed: {command}")
                return result
            
            print(f"✅ Step {i} completed")
            print()
        
        print("✅ All commands completed successfully")
        return 0
    
    def add_mapping(self, simple_command: str, mapped_command: str | List[str]) -> None:
        """Add a new command mapping."""
        self.mappings[simple_command.lower()] = mapped_command
    
    def remove_mapping(self, simple_command: str) -> bool:
        """Remove a command mapping."""
        if simple_command.lower() in self.mappings:
            del self.mappings[simple_command.lower()]
            return True
        return False


def create_router() -> SimpleRouter:
    """Create a new SimpleRouter instance."""
    return SimpleRouter()


# Global router instance
router = create_router()


def execute_simple_command(command: str, args: List[str] = None) -> int:
    """Execute a simple command using the global router."""
    return router.execute_simple_command(command, args)


def get_command_mapping(command: str) -> Optional[str | List[str]]:
    """Get the mapping for a simple command."""
    return router.get_command(command)


def list_commands() -> Dict[str, str | List[str]]:
    """List all available simple commands."""
    return router.list_available_commands()