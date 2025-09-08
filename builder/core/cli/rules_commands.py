#!/usr/bin/env python3
"""
Rules Commands

This module provides CLI commands for rules checking and validation.
"""

import sys
from pathlib import Path
from typing import List

import click

from .base import cli
from ...utils.rules_integration import RulesChecker, RulesIntegrator, check_document_rules


@cli.command("rules:check")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--suppress-hints", is_flag=True, help="Suppress hint-level violations")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def rules_check(file_path: str, suppress_hints: bool, output_format: str):
    """Check a file against rules and report violations."""
    checker = RulesChecker()
    violations = checker.check_file(file_path)
    
    if suppress_hints:
        violations = [v for v in violations if v.severity != "hint"]
    
    if output_format == "json":
        import json
        result = {
            "file": file_path,
            "violations": [
                {
                    "pattern": v.pattern,
                    "message": v.message,
                    "line_number": v.line_number,
                    "line_content": v.line_content,
                    "severity": v.severity
                }
                for v in violations
            ],
            "total_violations": len(violations),
            "has_errors": any(v.severity in ["error", "warning"] for v in violations)
        }
        click.echo(json.dumps(result, indent=2))
    else:
        report = checker.generate_violation_report(violations, file_path)
        click.echo(report)
    
    # Exit with error code if there are violations
    has_errors = any(v.severity in ["error", "warning"] for v in violations)
    if has_errors:
        sys.exit(1)


@cli.command("rules:check-content")
@click.argument("content", required=False)
@click.option("--file", "file_path", type=click.Path(exists=True), help="Read content from file")
@click.option("--doc-type", default="general", help="Document type for rule selection")
@click.option("--suppress-hints", is_flag=True, help="Suppress hint-level violations")
def rules_check_content(content: str, file_path: str, doc_type: str, suppress_hints: bool):
    """Check content against rules."""
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    elif not content:
        click.echo("Error: Must provide either content or --file")
        sys.exit(1)
    
    is_valid, report = check_document_rules(content, doc_type)
    
    click.echo(report)
    
    if not is_valid:
        sys.exit(1)


@cli.command("rules:validate-doc")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("doc_type")
@click.option("--suppress-hints", is_flag=True, help="Suppress hint-level violations")
def rules_validate_doc(file_path: str, doc_type: str, suppress_hints: bool):
    """Validate a document against rules and show rule references."""
    integrator = RulesIntegrator()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    is_valid, report, frontmatter = integrator.validate_document(content, doc_type, file_path)
    
    click.echo(report)
    
    if frontmatter.get("rules"):
        click.echo(f"\n📋 Rule references: {', '.join(frontmatter['rules'])}")
    
    if not is_valid:
        sys.exit(1)


@cli.command("rules:list")
def rules_list():
    """List all available rules."""
    checker = RulesChecker()
    
    click.echo("Available Rules:")
    click.echo()
    
    # Forbidden patterns
    click.echo(f"🚫 Forbidden Patterns: {len(checker.rules['forbidden_patterns'])}")
    for pattern in checker.rules["forbidden_patterns"][:5]:  # Show first 5
        click.echo(f"  - {pattern['message']}")
    if len(checker.rules["forbidden_patterns"]) > 5:
        click.echo(f"  ... and {len(checker.rules['forbidden_patterns']) - 5} more")
    
    click.echo()
    
    # Hints
    click.echo(f"💡 Hints: {len(checker.rules['hints'])}")
    for hint in checker.rules["hints"][:5]:  # Show first 5
        click.echo(f"  - {hint['message']}")
    if len(checker.rules["hints"]) > 5:
        click.echo(f"  ... and {len(checker.rules['hints']) - 5} more")
    
    click.echo()
    
    # Rule files
    click.echo(f"📄 Rule Files: {len(checker.rules['rule_files'])}")
    for rule_file in checker.rules["rule_files"]:
        click.echo(f"  - {rule_file}")


@cli.command("rules:add-refs")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("doc_type")
def rules_add_refs(file_path: str, doc_type: str):
    """Add rule references to document front-matter."""
    from ...utils.rules_integration import add_rule_references
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_content = add_rule_references(content, doc_type)
    
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        click.echo(f"✅ Added rule references to {file_path}")
    else:
        click.echo(f"ℹ️  No changes needed for {file_path}")
