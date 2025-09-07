#!/usr/bin/env python3
"""
Entry point for running the Code Builder CLI as a module.

Usage:
    python -m builder.core.cli <command> [options]
    python3 -m builder.core.cli <command> [options]
"""

from . import cli

if __name__ == "__main__":
    cli()
