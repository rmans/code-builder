#!/usr/bin/env python3
"""
Entry point for running the Code Builder CLI as a module.

Usage:
    python -m builder <command> [options]
    python3 -m builder <command> [options]
"""

from .core.cli import cli

if __name__ == "__main__":
    cli()
