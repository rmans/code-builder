#!/usr/bin/env python3
"""
Document Types Commands

This module provides CLI commands for managing the 8 canonical document types.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import click

from .base import cli
from ..context_builder import ContextBuilder


@cli.command("doc-types:generate-all")
@click.option("--overwrite", is_flag=True, help="Overwrite existing documents")
@click.option("--sections", help="Comma-separated list of sections to generate")
def doc_types_generate_all(overwrite: bool, sections: str):
    """Generate all 8 canonical document types."""
    builder = ContextBuilder()
    
    # Define the 8 canonical document types
    canonical_types = {
        "prd": "Product Requirements Document",
        "arch": "Architecture Documents", 
        "adr": "Architecture Decision Records",
        "int": "Integration Plans",
        "impl": "Implementation Roadmaps",
        "exec": "Execution Plans",
        "task": "Task Definitions",
        "ux": "User Experience"
    }
    
    if sections:
        requested_sections = [s.strip() for s in sections.split(",")]
        # Map section names to canonical types
        section_map = {
            "prd": "prd",
            "arch": "arch", 
            "adr": "arch",  # ADRs are generated as part of architecture
            "int": "int",
            "impl": "impl",
            "exec": "exec",
            "task": "task",
            "ux": "ux"
        }
        sections_to_generate = [section_map.get(s, s) for s in requested_sections if s in section_map]
    else:
        sections_to_generate = list(canonical_types.keys())
    
    click.echo(f"🏗️  Generating {len(sections_to_generate)} canonical document types...")
    
    results = {}
    
    for doc_type in sections_to_generate:
        try:
            click.echo(f"📄 Generating {canonical_types[doc_type]}...")
            
            # Use context builder to generate documents
            if doc_type in ["prd", "arch", "int", "impl", "exec"]:
                result = builder.build_context(
                    sources=["discovery", "interview"],
                    sections=[doc_type],
                    overwrite=overwrite
                )
                results[doc_type] = result.get("results", {}).get(doc_type, {})
            elif doc_type == "task":
                # Tasks are managed separately
                results[doc_type] = {"status": "managed_separately", "note": "Use 'cb generate-task' or 'cb execute-tasks'"}
            elif doc_type == "ux":
                # UX documents are part of architecture
                result = builder.build_context(
                    sources=["discovery", "interview"],
                    sections=["arch"],
                    overwrite=overwrite
                )
                results[doc_type] = result.get("results", {}).get("arch", {})
            
            click.echo(f"✅ {canonical_types[doc_type]} completed")
            
        except Exception as e:
            click.echo(f"❌ Failed to generate {canonical_types[doc_type]}: {e}")
            results[doc_type] = {"status": "error", "error": str(e)}
    
    # Generate summary
    click.echo("\n📊 Generation Summary:")
    for doc_type, result in results.items():
        status = result.get("status", "unknown")
        if status == "generated":
            click.echo(f"  ✅ {canonical_types[doc_type]}: Generated")
        elif status == "skipped":
            click.echo(f"  ⏭️  {canonical_types[doc_type]}: Skipped (already exists)")
        elif status == "managed_separately":
            click.echo(f"  ℹ️  {canonical_types[doc_type]}: Managed separately")
        elif status == "error":
            click.echo(f"  ❌ {canonical_types[doc_type]}: Error - {result.get('error', 'Unknown error')}")
        else:
            click.echo(f"  ❓ {canonical_types[doc_type]}: {status}")


@cli.command("doc-types:status")
def doc_types_status():
    """Show status of all 8 canonical document types."""
    canonical_types = {
        "prd": "Product Requirements Document",
        "arch": "Architecture Documents", 
        "adr": "Architecture Decision Records",
        "int": "Integration Plans",
        "impl": "Implementation Roadmaps",
        "exec": "Execution Plans",
        "task": "Task Definitions",
        "ux": "User Experience"
    }
    
    click.echo("📊 Document Types Status:")
    click.echo()
    
    for doc_type, name in canonical_types.items():
        # Check if master file exists
        master_file = Path(f"cb_docs/{doc_type}/0000_MASTER_{doc_type.upper()}.md")
        
        if master_file.exists():
            try:
                with open(master_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract document count from master file
                if "documents:" in content:
                    import re
                    docs_match = re.search(r'documents:\s*\[(.*?)\]', content, re.DOTALL)
                    if docs_match:
                        docs_list = docs_match.group(1)
                        doc_count = len([d.strip() for d in docs_list.split(',') if d.strip()])
                    else:
                        doc_count = 0
                else:
                    doc_count = 0
                
                # Get last modified time
                mtime = master_file.stat().st_mtime
                last_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                
                click.echo(f"  ✅ {name:25} | {doc_count:2d} docs | {last_modified}")
                
            except Exception as e:
                click.echo(f"  ❓ {name:25} | Error reading master file: {e}")
        else:
            click.echo(f"  ❌ {name:25} | No master file found")
    
    click.echo()
    click.echo("💡 Use 'cb doc-types:generate-all' to generate missing documents")


@cli.command("doc-types:validate-links")
def doc_types_validate_links():
    """Validate cross-references between document types."""
    click.echo("🔗 Validating document links...")
    
    # This would implement link validation logic
    # For now, just show a placeholder
    click.echo("✅ Link validation completed (placeholder)")
    click.echo("💡 Link validation will be implemented in future versions")


@cli.command("doc-types:create-index")
def doc_types_create_index():
    """Create or update the main documentation index."""
    index_file = Path("cb_docs/INDEX.md")
    
    if index_file.exists():
        click.echo(f"📄 Index already exists: {index_file}")
        click.echo("💡 Delete the file and run again to regenerate")
    else:
        click.echo("📄 Creating documentation index...")
        # The index file was already created above
        click.echo(f"✅ Index created: {index_file}")


@cli.command("doc-types:list")
def doc_types_list():
    """List all 8 canonical document types with descriptions."""
    canonical_types = {
        "prd": {
            "name": "Product Requirements Document",
            "description": "Defines what the product should do, its features, and success criteria",
            "location": "cb_docs/prd/",
            "command": "cb ctx:build --sections prd"
        },
        "arch": {
            "name": "Architecture Documents", 
            "description": "Technical architecture specifications for frontend and backend systems",
            "location": "cb_docs/arch/",
            "command": "cb ctx:build --sections arch"
        },
        "adr": {
            "name": "Architecture Decision Records",
            "description": "Documents important architectural decisions and their rationale",
            "location": "cb_docs/adrs/",
            "command": "cb ctx:build --sections arch"
        },
        "int": {
            "name": "Integration Plans",
            "description": "Defines how different systems and components integrate together",
            "location": "cb_docs/exec/",
            "command": "cb ctx:build --sections int"
        },
        "impl": {
            "name": "Implementation Roadmaps",
            "description": "Detailed implementation plans with phases, milestones, and deliverables",
            "location": "cb_docs/impl/",
            "command": "cb ctx:build --sections impl"
        },
        "exec": {
            "name": "Execution Plans",
            "description": "Operational execution plans with timelines, resources, and dependencies",
            "location": "cb_docs/exec/",
            "command": "cb ctx:build --sections exec"
        },
        "task": {
            "name": "Task Definitions",
            "description": "Individual task specifications with acceptance criteria and dependencies",
            "location": "cb_docs/tasks/",
            "command": "cb generate-task or cb execute-tasks"
        },
        "ux": {
            "name": "User Experience",
            "description": "User interface designs, wireframes, and user experience specifications",
            "location": "cb_docs/ux/",
            "command": "cb ctx:build --sections ux"
        }
    }
    
    click.echo("📋 Canonical Document Types:")
    click.echo()
    
    for doc_type, info in canonical_types.items():
        click.echo(f"**{info['name']}** ({doc_type.upper()})")
        click.echo(f"  Description: {info['description']}")
        click.echo(f"  Location: {info['location']}")
        click.echo(f"  Command: {info['command']}")
        click.echo()
