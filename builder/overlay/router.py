#!/usr/bin/env python3
"""
Command Router for Code Builder Overlay

This module provides a simple command router that maps natural language
verbs to existing Code Builder CLI commands.
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class CommandRouter:
    """Routes simple commands to the appropriate Code Builder CLI commands."""
    
    def __init__(self):
        self.engine_dir = os.getenv('CB_ENGINE_DIR', '.cb/engine')
        self.cache_dir = os.getenv('CB_CACHE_DIR', '.cb/cache')
        self.sessions_dir = os.path.join(self.cache_dir, 'sessions')
        
        # Ensure sessions directory exists
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Command mapping: simple verb -> (command, args)
        self.command_map = {
            'start': ('menu', []),
            'discover': ('discover:new', []),
            'analyze': ('discover:analyze', []),
            'context': ('ctx:build', ['--purpose', 'implement', '--feature', 'general']),
            'pack': ('ctx:pack', []),
            'eval': ('rules:check', []),
            'test': ('rules:check', []),
            'task': ('doc:new', ['task']),
            'docs': ('doc:index', []),
            'fix': ('autofixes', []),
            'clean': ('cache:clean', []),
            'update': ('engine:update', []),
            'doctor': ('doctor', []),
            'env': ('env', []),
            'version': ('version', []),
        }
        
        # Intent mapping for natural language processing
        self.intent_map = {
            'add auth': ('doc:new', ['task', 'authentication']),
            'add authentication': ('doc:new', ['task', 'authentication']),
            'fix lint': ('fix', []),
            'fix linting': ('fix', []),
            'analyze code': ('discover:analyze', []),
            'analyze project': ('discover:analyze', []),
            'create context': ('context', []),
            'build context': ('context', []),
            'generate docs': ('docs', []),
            'update docs': ('docs', []),
            'run tests': ('eval', []),
            'check rules': ('eval', []),
            'clean cache': ('clean', []),
            'update system': ('update', []),
        }
    
    def route_command(self, args: List[str]) -> int:
        """
        Route a command to the appropriate handler.
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code
        """
        if not args:
            # No arguments - show interactive menu
            return self._show_menu()
        
        verb = args[0].lower()
        remaining_args = args[1:]
        
        # Check for natural language intent
        if verb == 'do' and remaining_args:
            return self._handle_natural_language(' '.join(remaining_args))
        
        # Check for direct command mapping
        if verb in self.command_map:
            command, default_args = self.command_map[verb]
            return self._execute_command(command, default_args + remaining_args)
        
        # Check for backward compatibility pass-through
        return self._pass_through_command(args)
    
    def _show_menu(self) -> int:
        """Show the interactive menu."""
        try:
            from .menu import show_menu
            return show_menu()
        except ImportError:
            # Fallback to simple menu
            print("🔧 Code Builder Overlay")
            print("")
            print("Available commands:")
            for verb, (command, _) in self.command_map.items():
                print(f"  cb {verb:<12} -> {command}")
            print("")
            print("Examples:")
            print("  cb discover     # Start discovery process")
            print("  cb context      # Build context")
            print("  cb docs         # Generate documentation")
            print("  cb eval         # Run evaluation")
            print("")
            print("For help with specific commands:")
            print("  cb <command> --help")
            return 0
    
    def _handle_natural_language(self, intent: str) -> int:
        """Handle natural language commands."""
        intent_lower = intent.lower()
        
        # Find matching intent
        for pattern, (command, args) in self.intent_map.items():
            if pattern in intent_lower:
                print(f"💡 I understand: '{intent}'")
                print(f"   This maps to: cb {command} {' '.join(args)}")
                print("")
                
                # Ask for confirmation unless --yes is provided
                if '--yes' not in sys.argv:
                    try:
                        response = input("Proceed? [Y/n]: ").strip().lower()
                        if response and response not in ['y', 'yes']:
                            print("Cancelled.")
                            return 0
                    except KeyboardInterrupt:
                        print("\nCancelled.")
                        return 0
                
                return self._execute_command(command, args)
        
        # No matching intent found
        print(f"❓ I don't understand: '{intent}'")
        print("")
        print("Available intents:")
        for pattern in self.intent_map.keys():
            print(f"  cb do '{pattern}'")
        print("")
        print("Or use direct commands:")
        for verb in self.command_map.keys():
            print(f"  cb {verb}")
        
        # Log unmapped intent
        self._log_unmapped_intent(intent)
        return 1
    
    def _execute_command(self, command: str, args: List[str]) -> int:
        """Execute a Code Builder CLI command."""
        # Build the full command
        cmd = [
            sys.executable, '-m', 'builder.core.cli',
            command
        ] + args
        
        # Set environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.engine_dir}:{env.get('PYTHONPATH', '')}"
        
        try:
            # Execute the command
            result = subprocess.run(cmd, env=env, cwd=os.getcwd())
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return 1
    
    def _pass_through_command(self, args: List[str]) -> int:
        """Pass through unknown commands to the original CLI."""
        # Build the full command
        cmd = [
            sys.executable, '-m', 'builder.core.cli'
        ] + args
        
        # Set environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.engine_dir}:{env.get('PYTHONPATH', '')}"
        
        try:
            # Execute the command
            result = subprocess.run(cmd, env=env, cwd=os.getcwd())
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return 1
    
    def _log_unmapped_intent(self, intent: str) -> None:
        """Log unmapped intents for future improvement."""
        log_file = os.path.join(self.sessions_dir, 'unmapped_intents.jsonl')
        
        log_entry = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'intent': intent,
            'args': sys.argv[1:]
        }
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass  # Don't fail if logging fails
    
    def get_available_commands(self) -> Dict[str, str]:
        """Get a list of available commands and their descriptions."""
        commands = {}
        
        # Add mapped commands
        for verb, (command, _) in self.command_map.items():
            commands[verb] = f"Maps to: {command}"
        
        # Add natural language commands
        for pattern, (command, _) in self.intent_map.items():
            commands[f"do '{pattern}'"] = f"Maps to: {command}"
        
        return commands


def main():
    """Main entry point for the router."""
    router = CommandRouter()
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    sys.exit(router.route_command(args))


if __name__ == '__main__':
    main()
