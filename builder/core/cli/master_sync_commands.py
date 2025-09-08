#!/usr/bin/env python3
"""
Master File Synchronization Commands

This module provides CLI commands for master file synchronization.
"""

import json
from pathlib import Path
from typing import Dict, Any

import click

from .base import cli
from ...utils.master_file_sync import (
    MasterFileSync, sync_all_master_files, sync_master_file, 
    add_document_to_master, validate_master_files
)


@cli.command("master:sync-all")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def master_sync_all(output_format: str):
    """Synchronize all master files."""
    click.echo("🔄 Synchronizing all master files...")
    
    results = sync_all_master_files()
    
    if output_format == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        click.echo("\n📊 Master File Sync Results:")
        click.echo()
        
        for doc_type, result in results.items():
            status = result.get("status", "unknown")
            if status == "success":
                count = result.get("documents_count", 0)
                click.echo(f"  ✅ {doc_type.upper():4} | {count:2d} documents | {result.get('file', '')}")
            elif status == "skipped":
                reason = result.get("reason", "Unknown reason")
                click.echo(f"  ⏭️  {doc_type.upper():4} | Skipped: {reason}")
            elif status == "error":
                error = result.get("error", "Unknown error")
                click.echo(f"  ❌ {doc_type.upper():4} | Error: {error}")
            else:
                click.echo(f"  ❓ {doc_type.upper():4} | {status}")
        
        click.echo()


@cli.command("master:sync")
@click.argument("doc_type")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def master_sync(doc_type: str, output_format: str):
    """Synchronize a specific master file."""
    click.echo(f"🔄 Synchronizing {doc_type} master file...")
    
    result = sync_master_file(doc_type)
    
    if output_format == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        status = result.get("status", "unknown")
        if status == "success":
            count = result.get("documents_count", 0)
            file_path = result.get("file", "")
            click.echo(f"✅ Synchronized {doc_type} master file: {count} documents")
            click.echo(f"📄 File: {file_path}")
        elif status == "skipped":
            reason = result.get("reason", "Unknown reason")
            click.echo(f"⏭️  Skipped: {reason}")
        elif status == "error":
            error = result.get("error", "Unknown error")
            click.echo(f"❌ Error: {error}")
        else:
            click.echo(f"❓ Status: {status}")


@cli.command("master:validate")
@click.option("--output-format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def master_validate(output_format: str):
    """Validate all master files for consistency."""
    click.echo("🔍 Validating master files...")
    
    results = validate_master_files()
    
    if output_format == "json":
        click.echo(json.dumps(results, indent=2))
    else:
        click.echo("\n📊 Master File Validation Results:")
        click.echo()
        
        for doc_type, result in results.items():
            status = result.get("status", "unknown")
            if status == "valid":
                count = result.get("documents_count", 0)
                duplicates = result.get("duplicate_ids", [])
                missing = result.get("missing_files", [])
                
                click.echo(f"  ✅ {doc_type.upper():4} | {count:2d} documents | Valid")
                
                if duplicates:
                    click.echo(f"      ⚠️  Duplicate IDs: {', '.join(duplicates)}")
                
                if missing:
                    click.echo(f"      ⚠️  Missing files: {', '.join(missing)}")
                    
            elif status == "missing":
                file_path = result.get("file", "")
                click.echo(f"  ❌ {doc_type.upper():4} | Missing: {file_path}")
            elif status == "invalid":
                reason = result.get("reason", "Unknown reason")
                click.echo(f"  ❌ {doc_type.upper():4} | Invalid: {reason}")
            elif status == "error":
                error = result.get("error", "Unknown error")
                click.echo(f"  ❌ {doc_type.upper():4} | Error: {error}")
            else:
                click.echo(f"  ❓ {doc_type.upper():4} | {status}")
        
        click.echo()


@cli.command("master:add-document")
@click.argument("doc_type")
@click.argument("doc_id")
@click.argument("title")
@click.option("--status", default="draft", help="Document status")
@click.option("--domain", default="", help="Document domain")
@click.option("--owner", default="", help="Document owner")
def master_add_document(doc_type: str, doc_id: str, title: str, status: str, domain: str, owner: str):
    """Add a document to its master file."""
    doc_info = {
        "id": doc_id,
        "title": title,
        "status": status,
        "domain": domain,
        "owner": owner
    }
    
    success = add_document_to_master(doc_type, doc_info)
    
    if success:
        click.echo(f"✅ Added document {doc_id} to {doc_type} master file")
    else:
        click.echo(f"❌ Failed to add document {doc_id} to {doc_type} master file")
        click.get_current_context().exit(1)


@cli.command("master:list")
def master_list():
    """List all master files and their status."""
    sync = MasterFileSync()
    
    click.echo("📋 Master Files:")
    click.echo()
    
    for doc_type, master_file in sync.master_files.items():
        if master_file.exists():
            try:
                with open(master_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        documents = frontmatter.get('documents', [])
                        title = frontmatter.get('title', 'Index')
                        
                        click.echo(f"  ✅ {doc_type.upper():4} | {len(documents):2d} docs | {title}")
                    else:
                        click.echo(f"  ❓ {doc_type.upper():4} | Invalid format")
                else:
                    click.echo(f"  ❓ {doc_type.upper():4} | No frontmatter")
            except Exception as e:
                click.echo(f"  ❌ {doc_type.upper():4} | Error: {e}")
        else:
            click.echo(f"  ❌ {doc_type.upper():4} | Missing: {master_file}")


@cli.command("master:create-missing")
def master_create_missing():
    """Create missing master files."""
    sync = MasterFileSync()
    
    click.echo("🔄 Creating missing master files...")
    
    for doc_type, master_file in sync.master_files.items():
        if not master_file.exists():
            try:
                # Create directory if it doesn't exist
                master_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create basic master file
                title = f"{doc_type.upper()} Index"
                content = f"""---
type: {doc_type}
title: {title}
status: active
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
documents: []
---

# {title}

| ID | Title | Status | Domain | Link |
|---|---|---|---|---|
| *No documents currently defined* |  |  |  |  |
"""
                
                with open(master_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                click.echo(f"  ✅ Created {doc_type.upper()} master file: {master_file}")
                
            except Exception as e:
                click.echo(f"  ❌ Failed to create {doc_type.upper()} master file: {e}")
        else:
            click.echo(f"  ⏭️  {doc_type.upper()} master file already exists")
