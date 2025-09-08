#!/usr/bin/env python3
"""
Evaluation Commands

This module provides CLI commands for code evaluation and quality assessment.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

import click

from .base import cli
from ...evaluators.objective import evaluate_code, load_config, check_tool_availability


@cli.command("eval:objective")
@click.argument("target", required=False)
@click.option("--output-format", type=click.Choice(["json", "md"]), default="json", help="Output format")
def eval_objective(target: str, output_format: str):
    """Evaluate code quality, performance, and compliance using objective metrics."""
    if not target:
        target = "."
    
    click.echo(f"🔍 Evaluating: {target}")
    
    try:
        # Run evaluation
        result = evaluate_code(target)
        
        # Save results
        eval_dir = Path("cb_docs/eval")
        eval_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == "json":
            output_file = eval_dir / f"evaluation_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            click.echo(f"📄 Results saved to: {output_file}")
        else:
            output_file = eval_dir / f"evaluation_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Evaluation Report\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Results\n\n")
                f.write("```json\n")
                f.write(json.dumps(result, indent=2, default=str))
                f.write("\n```\n")
            click.echo(f"📄 Results saved to: {output_file}")
        
        click.echo("✅ Evaluation completed successfully")
        sys.exit(0)
        
    except Exception as e:
        click.echo(f"❌ Evaluation error: {e}")
        sys.exit(1)