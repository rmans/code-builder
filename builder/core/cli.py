#!/usr/bin/env python3
"""
Code Builder CLI - Modular Entry Point

This file serves as the main entry point for the Code Builder CLI.
All commands have been extracted to modular files in the cli/ directory.
"""

# Import the main CLI group from the modular structure
from .cli.base import cli

# Make the CLI available as the main entry point
if __name__ == '__main__':
    cli()
