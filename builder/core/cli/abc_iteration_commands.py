#!/usr/bin/env python3
"""
ABC Iteration Commands

This module provides CLI commands for ABC iteration functionality.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

import click

from .base import cli
from ...utils.abc_iteration import ABCIterationRunner, run_abc_iteration


@cli.command("iterate")
@click.argument("target")
@click.option("--rounds", default=5, help="Number of iteration rounds")
@click.option("--type", "target_type", type=click.Choice(["phase", "task", "general"]), 
              default="phase", help="Target type")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def iterate(target: str, rounds: int, target_type: str, output_format: str):
    """Run ABC iteration for a target."""
    click.echo(f"🔄 Starting ABC iteration for {target} ({rounds} rounds)")
    
    try:
        result = run_abc_iteration(target, rounds, target_type)
        
        if output_format == "json":
            # Convert result to JSON-serializable format
            result_data = {
                "target": result.target,
                "rounds": result.rounds,
                "variants": [
                    {
                        "name": v.name,
                        "score": v.score,
                        "metadata": v.metadata,
                        "artifacts": v.artifacts,
                        "created_at": v.created_at.isoformat()
                    }
                    for v in result.variants
                ],
                "winner": {
                    "name": result.winner.name,
                    "score": result.winner.score,
                    "metadata": result.winner.metadata,
                    "artifacts": result.winner.artifacts,
                    "created_at": result.winner.created_at.isoformat()
                } if result.winner else None,
                "metadata": result.metadata,
                "created_at": result.created_at.isoformat()
            }
            click.echo(json.dumps(result_data, indent=2))
        else:
            # Text output
            click.echo(f"\n📊 ABC Iteration Results for {target}:")
            click.echo(f"Rounds: {result.rounds}")
            click.echo(f"Variants: {len(result.variants)}")
            click.echo()
            
            # Show variants
            click.echo("Variants:")
            for i, variant in enumerate(result.variants, 1):
                click.echo(f"  {i}. {variant.name}: {variant.score:.3f}")
            
            click.echo()
            
            # Show winner
            if result.winner:
                click.echo(f"🏆 Winner: {result.winner.name} (score: {result.winner.score:.3f})")
                click.echo(f"Artifacts: {len(result.winner.artifacts)}")
            else:
                click.echo("❌ No winner selected")
            
            click.echo(f"\n📁 Results saved to: {result.metadata.get('iteration_dir', 'unknown')}")
        
    except Exception as e:
        click.echo(f"❌ ABC iteration failed: {e}")
        click.get_current_context().exit(1)


@cli.command("iterate:list")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def iterate_list(output_format: str):
    """List all previous ABC iterations."""
    runner = ABCIterationRunner()
    iterations = runner.list_iterations()
    
    if output_format == "json":
        click.echo(json.dumps(iterations, indent=2))
    else:
        if not iterations:
            click.echo("No previous iterations found")
            return
        
        click.echo("📋 Previous ABC Iterations:")
        click.echo()
        
        for iteration in iterations:
            click.echo(f"  {iteration['target']:15} | {iteration['rounds']:2d} rounds | "
                      f"{iteration['variants']:2d} variants | Winner: {iteration['winner']:15} | "
                      f"{iteration['created_at'][:19]}")
        
        click.echo()


@cli.command("iterate:show")
@click.argument("iteration_dir")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def iterate_show(iteration_dir: str, output_format: str):
    """Show detailed results for a specific iteration."""
    runner = ABCIterationRunner()
    result = runner.get_iteration_result(iteration_dir)
    
    if not result:
        click.echo(f"❌ Iteration not found: {iteration_dir}")
        click.get_current_context().exit(1)
    
    if output_format == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"📊 ABC Iteration Results: {result['target']}")
        click.echo(f"Rounds: {result['rounds']}")
        click.echo(f"Created: {result['created_at']}")
        click.echo()
        
        # Show variants
        click.echo("Variants:")
        for i, variant in enumerate(result['variants'], 1):
            click.echo(f"  {i}. {variant['name']}: {variant['score']:.3f}")
            click.echo(f"     Artifacts: {len(variant['artifacts'])}")
            click.echo(f"     Metadata: {variant['metadata']}")
            click.echo()
        
        # Show winner
        if result['winner']:
            click.echo(f"🏆 Winner: {result['winner']['name']} (score: {result['winner']['score']:.3f})")
            click.echo(f"Artifacts: {result['winner']['artifacts']}")
        else:
            click.echo("❌ No winner selected")


@cli.command("iterate:cleanup")
@click.option("--older-than", type=int, default=30, help="Remove iterations older than N days")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without actually deleting")
def iterate_cleanup(older_than: int, dry_run: bool):
    """Clean up old iteration results."""
    runner = ABCIterationRunner()
    iterations_dir = runner.iterations_dir
    
    if not iterations_dir.exists():
        click.echo("No iterations directory found")
        return
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=older_than)
    
    removed_count = 0
    total_size = 0
    
    for iteration_dir in iterations_dir.iterdir():
        if iteration_dir.is_dir():
            # Check creation date
            try:
                result_file = iteration_dir / "iteration_result.json"
                if result_file.exists():
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    
                    created_at = datetime.fromisoformat(result_data.get('created_at', ''))
                    
                    if created_at < cutoff_date:
                        # Calculate size
                        size = sum(f.stat().st_size for f in iteration_dir.rglob('*') if f.is_file())
                        total_size += size
                        
                        if dry_run:
                            click.echo(f"Would remove: {iteration_dir} ({size} bytes)")
                        else:
                            import shutil
                            shutil.rmtree(iteration_dir)
                            click.echo(f"Removed: {iteration_dir}")
                        
                        removed_count += 1
                        
            except Exception as e:
                click.echo(f"Warning: Could not process {iteration_dir}: {e}")
    
    if dry_run:
        click.echo(f"\nWould remove {removed_count} iterations ({total_size} bytes)")
    else:
        click.echo(f"\nRemoved {removed_count} iterations ({total_size} bytes)")


@cli.command("iterate:status")
def iterate_status():
    """Show ABC iteration system status."""
    runner = ABCIterationRunner()
    
    click.echo("📊 ABC Iteration System Status:")
    click.echo()
    
    # Check iterations directory
    iterations_dir = runner.iterations_dir
    if iterations_dir.exists():
        iteration_count = len([d for d in iterations_dir.iterdir() if d.is_dir()])
        click.echo(f"  📁 Iterations directory: {iterations_dir}")
        click.echo(f"  📊 Total iterations: {iteration_count}")
    else:
        click.echo(f"  ❌ Iterations directory not found: {iterations_dir}")
    
    # Check recent iterations
    iterations = runner.list_iterations()
    if iterations:
        recent = iterations[:5]  # Show last 5
        click.echo(f"\n  📋 Recent iterations:")
        for iteration in recent:
            click.echo(f"    {iteration['target']:15} | {iteration['created_at'][:19]}")
    else:
        click.echo(f"\n  ℹ️  No iterations found")
    
    click.echo()


@cli.command("iterate:run-phase")
@click.argument("phase", type=click.Choice(["implementation", "testing", "documentation", "cleanup", "commit"]))
@click.option("--rounds", default=5, help="Number of iteration rounds")
def iterate_run_phase(phase: str, rounds: int):
    """Run ABC iteration for a specific phase."""
    click.echo(f"🔄 Running ABC iteration for phase: {phase}")
    
    try:
        result = run_abc_iteration(phase, rounds, "phase")
        
        click.echo(f"\n✅ Phase iteration completed!")
        click.echo(f"Winner: {result.winner.name if result.winner else 'None'}")
        click.echo(f"Score: {result.winner.score:.3f if result.winner else 0}")
        
    except Exception as e:
        click.echo(f"❌ Phase iteration failed: {e}")
        click.get_current_context().exit(1)


@cli.command("iterate:run-task")
@click.argument("task_id")
@click.option("--rounds", default=5, help="Number of iteration rounds")
def iterate_run_task(task_id: str, rounds: int):
    """Run ABC iteration for a specific task."""
    click.echo(f"🔄 Running ABC iteration for task: {task_id}")
    
    try:
        result = run_abc_iteration(task_id, rounds, "task")
        
        click.echo(f"\n✅ Task iteration completed!")
        click.echo(f"Winner: {result.winner.name if result.winner else 'None'}")
        click.echo(f"Score: {result.winner.score:.3f if result.winner else 0}")
        
    except Exception as e:
        click.echo(f"❌ Task iteration failed: {e}")
        click.get_current_context().exit(1)
