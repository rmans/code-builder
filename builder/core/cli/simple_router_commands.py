#!/usr/bin/env python3
"""
Simple Router Commands

This module provides CLI commands for the simple command router.
"""

import click
from typing import List

from .base import cli
from ...overlay.simple_router import router, execute_simple_command, list_commands


@cli.command("simple")
@click.argument("command")
@click.argument("args", nargs=-1)
def simple_command(command: str, args: List[str]):
    """Execute a simple command that maps to complex commands."""
    exit_code = execute_simple_command(command, list(args))
    if exit_code != 0:
        click.get_current_context().exit(exit_code)


@cli.command("list-simple-commands")
def list_simple_commands():
    """List all available simple commands and their mappings."""
    commands = list_commands()
    
    click.echo("Available simple commands:")
    click.echo()
    
    for simple_cmd, mapped_cmd in commands.items():
        if isinstance(mapped_cmd, list):
            click.echo(f"  {simple_cmd:12} → {' + '.join(mapped_cmd)}")
        else:
            click.echo(f"  {simple_cmd:12} → {mapped_cmd}")
    
    click.echo()
    click.echo("Usage: cb simple <command> [args...]")
    click.echo("Example: cb simple discover")


@cli.command("map-command")
@click.argument("simple_command")
@click.argument("mapped_command")
def map_command(simple_command: str, mapped_command: str):
    """Add a new simple command mapping."""
    router.add_mapping(simple_command, mapped_command)
    click.echo(f"✅ Mapped '{simple_command}' → '{mapped_command}'")


@cli.command("unmap-command")
@click.argument("simple_command")
def unmap_command(simple_command: str):
    """Remove a simple command mapping."""
    if router.remove_mapping(simple_command):
        click.echo(f"✅ Removed mapping for '{simple_command}'")
    else:
        click.echo(f"❌ No mapping found for '{simple_command}'")
        click.get_current_context().exit(1)
