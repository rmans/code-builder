#!/usr/bin/env python3
"""
Command Agent Integration Module

This module provides integration between the command system and Cursor agents,
allowing agents to receive appropriate @rules/ commands based on current context.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from .cursor_agent_integration import CursorAgentOrchestrator
from .multi_agent_cursor import MultiAgentCursorManager

# Import configuration system
from ..config.settings import get_config
from ..overlay.paths import OverlayPaths


class CommandAgentIntegration:
    """Integrates command system with Cursor agents."""
    
    def __init__(self, cache_dir: str = None):
        # Use configuration system for paths
        config = get_config()
        overlay_paths = OverlayPaths()
        
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        
        self.cache_dir = Path(cache_dir)
        self.docs_dir = Path(overlay_paths.get_docs_dir())
        self.commands_dir = self.docs_dir / "commands"
        self.rules_dir = Path(".cursor/rules")
        
        # Initialize agent systems
        self.orchestrator = CursorAgentOrchestrator(cache_dir)
        self.multi_agent_manager = MultiAgentCursorManager(cache_dir)
        
        # Ensure rules directory exists
        self.rules_dir.mkdir(parents=True, exist_ok=True)
    
    def get_command_for_agent(self, context: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        Get the most appropriate command for an agent based on current context.
        
        Args:
            context: Current project context (optional)
            
        Returns:
            Tuple of (command_id, @rules/command_name)
        """
        if context is None:
            context = self._get_default_context()
        
        # Load available commands
        commands = self._load_commands()
        
        # Determine the best command based on context
        command_id = self._select_best_command(commands, context)
        
        # Generate @rules/ command
        rules_command = f"@rules/{command_id}"
        
        return command_id, rules_command
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default project context."""
        context = {
            "project_initialized": False,
            "discovered": False,
            "analyzed": False,
            "planned": False,
            "context_created": False,
            "has_tasks": False,
            "has_issues": False,
            "project_type": "unknown"
        }
        
        # Check project state
        try:
            # Check if project is initialized
            if self.docs_dir.exists():
                context["project_initialized"] = True
            
            # Check if discovery has been done
            discovery_dir = self.docs_dir / "discovery"
            if discovery_dir.exists() and any(discovery_dir.iterdir()):
                context["discovered"] = True
            
            # Check if analysis has been done
            analysis_file = self.cache_dir / "discovery_analysis.json"
            if analysis_file.exists():
                context["analyzed"] = True
            
            # Check if planning has been done
            planning_dir = self.docs_dir / "planning"
            if planning_dir.exists() and any(planning_dir.iterdir()):
                context["planned"] = True
            
            # Check if context has been created
            context_file = self.cache_dir / "context.json"
            if context_file.exists():
                context["context_created"] = True
            
            # Check if there are tasks
            tasks_dir = self.docs_dir / "tasks"
            if tasks_dir.exists() and any(tasks_dir.iterdir()):
                context["has_tasks"] = True
            
            # Check for common project files to determine type
            if (Path("package.json").exists() or 
                Path("requirements.txt").exists() or 
                Path("Cargo.toml").exists()):
                context["project_type"] = "code"
            elif Path("README.md").exists():
                context["project_type"] = "documentation"
            
        except Exception as e:
            print(f"Warning: Could not determine project context: {e}")
        
        return context
    
    def _load_commands(self) -> List[Dict[str, Any]]:
        """Load available commands from cb_docs/commands/."""
        commands = []
        
        if not self.commands_dir.exists():
            return commands
        
        for cmd_file in self.commands_dir.glob("*.md"):
            try:
                with open(cmd_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        cmd_data = yaml.safe_load(frontmatter)
                        if cmd_data:
                            cmd_data['file'] = str(cmd_file)
                            commands.append(cmd_data)
            except Exception as e:
                print(f"Warning: Could not load command {cmd_file}: {e}")
        
        return commands
    
    def _select_best_command(self, commands: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Select the best command based on context."""
        if not commands:
            return "analyze-project"  # Default fallback
        
        # Score commands based on context
        scored_commands = []
        
        for cmd in commands:
            score = self._score_command(cmd, context)
            scored_commands.append((cmd['id'], score))
        
        # Sort by score (highest first)
        scored_commands.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best command
        return scored_commands[0][0]
    
    def _score_command(self, cmd: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Score a command based on how well it fits the current context."""
        score = 0
        
        # Base score from priority
        priority = cmd.get('priority', 5)
        score += (10 - priority) * 10  # Higher priority = higher score
        
        # Check dependencies
        dependencies = cmd.get('dependencies', [])
        for dep in dependencies:
            if self._is_dependency_satisfied(dep, context):
                score += 20
            else:
                score -= 10  # Penalty for unmet dependencies
        
        # Context-based scoring
        domain = cmd.get('domain', '')
        agent_type = cmd.get('agent_type', '')
        
        # Discovery commands
        if domain == 'discovery' and not context.get('discovered', False):
            score += 30
        elif domain == 'discovery' and context.get('discovered', False):
            score -= 20
        
        # Planning commands
        if domain == 'planning' and context.get('discovered', False) and not context.get('planned', False):
            score += 25
        elif domain == 'planning' and not context.get('discovered', False):
            score -= 15
        
        # Analysis commands
        if domain == 'analysis' and not context.get('analyzed', False):
            score += 20
        
        # Implementation commands
        if domain == 'implementation' and context.get('planned', False):
            score += 15
        
        # Backend agent type
        if agent_type == 'backend' and context.get('project_type') == 'code':
            score += 10
        
        return score
    
    def _is_dependency_satisfied(self, dependency: str, context: Dict[str, Any]) -> bool:
        """Check if a dependency is satisfied."""
        if dependency == "analyze-project":
            return context.get('analyzed', False)
        elif dependency == "discover":
            return context.get('discovered', False)
        elif dependency == "plan":
            return context.get('planned', False)
        elif dependency == "context":
            return context.get('context_created', False)
        
        return False
    
    def create_rules_command(self, command_id: str) -> str:
        """Create a @rules/ command file for the given command ID."""
        # Load command data
        commands = self._load_commands()
        command_data = next((cmd for cmd in commands if cmd['id'] == command_id), None)
        
        if not command_data:
            raise ValueError(f"Command {command_id} not found")
        
        # Create rules command content
        rules_content = self._generate_rules_content(command_data)
        
        # Write to .cursor/rules/
        rules_file = self.rules_dir / f"execute-{command_id}.md"
        with open(rules_file, 'w', encoding='utf-8') as f:
            f.write(rules_content)
        
        return str(rules_file)
    
    def _generate_rules_content(self, command_data: Dict[str, Any]) -> str:
        """Generate content for a @rules/ command file."""
        title = command_data.get('title', command_data['id'])
        description = command_data.get('description', '')
        
        content = f"""# Execute {title}

## Description
{description}

## Usage
```bash
cb {command_data['id']}
```

## Context
This command has been selected based on current project state and dependencies.

## Agent Instructions
1. Execute the command using the Code Builder CLI
2. Follow any prompts or interactive elements
3. Report results and any issues encountered
4. Update project state as needed

## Expected Outputs
Check the command documentation for expected outputs and file locations.

## Dependencies
{', '.join(command_data.get('dependencies', []))}

## Tags
{', '.join(command_data.get('tags', []))}
"""
        
        return content
    
    def get_project_status_command(self) -> str:
        """Get a project status command for agents."""
        return "@rules/project-status"
    
    def create_project_status_rules(self) -> str:
        """Create a project status @rules/ command."""
        status_content = """# Project Status

## Description
Get current project status and next recommended actions.

## Usage
```bash
cb commands:list
cb orchestrator:status
```

## Agent Instructions
1. Check current project status
2. List available commands
3. Identify next recommended actions
4. Report current state and recommendations

## Status Checks
- Project initialization status
- Discovery completion
- Analysis status
- Planning status
- Available tasks
- Active agents

## Output
Provide a comprehensive status report with recommendations for next steps.
"""
        
        status_file = self.rules_dir / "project-status.md"
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(status_content)
        
        return str(status_file)
    
    def integrate_with_agents(self) -> Dict[str, Any]:
        """Integrate command system with existing agent systems."""
        # Get recommended command
        command_id, rules_command = self.get_command_for_agent()
        
        # Create rules files
        command_file = self.create_rules_command(command_id)
        status_file = self.create_project_status_rules()
        
        return {
            "recommended_command": command_id,
            "rules_command": rules_command,
            "command_file": command_file,
            "status_file": status_file,
            "available_commands": len(self._load_commands())
        }


def get_command_for_agent(context: Dict[str, Any] = None) -> Tuple[str, str]:
    """
    Convenience function to get command for agent.
    
    Args:
        context: Current project context (optional)
        
    Returns:
        Tuple of (command_id, @rules/command_name)
    """
    integration = CommandAgentIntegration()
    return integration.get_command_for_agent(context)


def create_agent_integration() -> CommandAgentIntegration:
    """Create a new CommandAgentIntegration instance."""
    return CommandAgentIntegration()
