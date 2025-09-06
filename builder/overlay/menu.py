#!/usr/bin/env python3
"""
Interactive Menu for Code Builder Overlay

This module provides a text-based user interface for common Code Builder actions.
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional


class InteractiveMenu:
    """Interactive menu system for Code Builder Overlay."""
    
    def __init__(self):
        self.engine_dir = os.getenv('CB_ENGINE_DIR', '.cb/engine')
        self.cache_dir = os.getenv('CB_CACHE_DIR', '.cb/cache')
        
        # Menu options
        self.options = [
            {
                'key': '1',
                'title': '🔍 Discovery',
                'description': 'Start discovery process for new features',
                'command': ['discover:new', '--interactive']
            },
            {
                'key': '2',
                'title': '📋 Context',
                'description': 'Build context for a file or feature',
                'command': ['ctx:build'],
                'needs_input': True,
                'input_prompt': 'Enter target file path: '
            },
            {
                'key': '3',
                'title': '📚 Documentation',
                'description': 'Generate or update documentation',
                'command': ['doc:index']
            },
            {
                'key': '4',
                'title': '✅ Evaluation',
                'description': 'Run rules check and evaluation',
                'command': ['rules:check']
            },
            {
                'key': '5',
                'title': '📝 New Task',
                'description': 'Create a new task document',
                'command': ['doc:new', 'task'],
                'needs_input': True,
                'input_prompt': 'Enter task title: '
            },
            {
                'key': '6',
                'title': '🔧 Fix Issues',
                'description': 'Run automatic fixes',
                'command': ['autofixes']
            },
            {
                'key': '7',
                'title': '🧹 Clean Cache',
                'description': 'Clean up cache and temporary files',
                'command': ['cache:clean']
            },
            {
                'key': '8',
                'title': '📊 Status',
                'description': 'Show system status and health',
                'command': ['doctor']
            },
            {
                'key': '9',
                'title': '❓ Help',
                'description': 'Show help and available commands',
                'command': ['--help']
            },
            {
                'key': '0',
                'title': '🚪 Exit',
                'description': 'Exit the menu',
                'command': None
            }
        ]
    
    def show_menu(self) -> int:
        """Show the interactive menu."""
        try:
            while True:
                self._clear_screen()
                self._show_header()
                self._show_options()
                
                choice = self._get_choice()
                
                if choice == '0':
                    print("\n👋 Goodbye!")
                    return 0
                
                option = self._find_option(choice)
                if option:
                    result = self._execute_option(option)
                    if result != 0:
                        input("\nPress Enter to continue...")
                else:
                    print(f"\n❌ Invalid choice: {choice}")
                    input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return 0
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1
    
    def _clear_screen(self):
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def _show_header(self):
        """Show the menu header."""
        print("🔧 Code Builder Overlay")
        print("=" * 50)
        print("Choose an action:")
        print("")
    
    def _show_options(self):
        """Show the menu options."""
        for option in self.options:
            print(f"  {option['key']}. {option['title']}")
            print(f"     {option['description']}")
            print("")
    
    def _get_choice(self) -> str:
        """Get user choice."""
        try:
            choice = input("Enter your choice (0-9): ").strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            return '0'
    
    def _find_option(self, choice: str) -> Optional[Dict]:
        """Find option by key."""
        for option in self.options:
            if option['key'] == choice:
                return option
        return None
    
    def _execute_option(self, option: Dict) -> int:
        """Execute the selected option."""
        if not option['command']:
            return 0
        
        command = option['command'].copy()
        
        # Handle options that need input
        if option.get('needs_input', False):
            try:
                user_input = input(option['input_prompt']).strip()
                if not user_input:
                    print("❌ Input required. Cancelled.")
                    return 1
                command.append(user_input)
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Cancelled.")
                return 1
        
        # Execute the command
        print(f"\n🚀 Executing: {' '.join(command)}")
        print("-" * 50)
        
        try:
            # Build the full command
            cmd = [
                sys.executable, '-m', 'builder.core.cli'
            ] + command
            
            # Set environment
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{self.engine_dir}:{env.get('PYTHONPATH', '')}"
            
            # Execute the command
            result = subprocess.run(cmd, env=env, cwd=os.getcwd())
            return result.returncode
            
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return 1


def show_menu() -> int:
    """Show the interactive menu."""
    menu = InteractiveMenu()
    return menu.show_menu()


if __name__ == '__main__':
    sys.exit(show_menu())
