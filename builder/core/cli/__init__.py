#!/usr/bin/env python3
"""
Code Builder CLI - Modular Command Structure

This module provides a modular CLI structure for the Code Builder system.
Commands are organized into logical modules based on functionality.
"""

import click
from .base import cli

# Import all command modules to register them
from . import (
    document_commands,
    context_commands,
    discovery_commands,
    agent_commands,
    agent_integration_commands,
    orchestrator_commands,
    evaluation_commands,
    utility_commands,
    iteration_commands,
    workflow_commands,
)

# Import simple router for command aliases
from ...overlay import simple_router

# Import agent-OS bridge for agent commands
from ...overlay import agent_os_bridge

# Import command generator for task commands
from ...overlay import command_generator

# Import task index management
from .. import task_index

# Import task generator
from ...overlay import task_generator

# Import orchestrator commands
from . import orchestrator_commands
from . import task_runner_commands
from . import simple_router_commands
from . import evaluation_commands
from . import rules_commands
from . import document_types_commands
from . import master_sync_commands
from . import abc_iteration_commands
from . import dynamic_updater_commands
from . import current_instructions_commands

__all__ = ['cli']

if __name__ == "__main__":
    cli()
