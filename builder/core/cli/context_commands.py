#!/usr/bin/env python3
"""
Context Commands Module

This module contains context-related commands like ctx:*, context:*
"""

import click
import os
import yaml
from pathlib import Path
from .base import cli, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    CACHE = ROOT / ".cb" / "cache"

def _load_rules(feature, stacks):
    """Load rules for context building."""
    try:
        from ..context_rules import merge_context_rules
        return merge_context_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])
    except ImportError:
        return {}

def _find_prd_discovery_file(prd_id):
    """Find PRD discovery file for given PRD ID."""
    try:
        discovery_dir = DOCS / "discovery"
        if discovery_dir.exists():
            for file_path in discovery_dir.glob(f"*{prd_id}*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    return data, str(file_path)
    except Exception:
        pass
    return None, None

# Context Commands
@cli.command("ctx:build")
@click.argument("target_path")
@click.option("--purpose", required=True, help="Purpose: implement, review, test, etc.")
@click.option("--feature", default="", help="Feature name for rules")
@click.option("--stacks", default="typescript,react", help="Comma-separated stack names")
@click.option("--token-limit", default=8000, help="Token budget limit")
@click.option("--prd", default="", help="PRD document ID for discovery context")
def ctx_build(target_path, purpose, feature, stacks, token_limit, prd):
    """Build context package for a target path."""
    # Ensure cache directory exists
    os.makedirs(CACHE, exist_ok=True)
    
    # Load rules
    rules = _load_rules(feature, stacks)
    
    # Find PRD content and metadata
    prd_content = ""
    prd_metadata = {}
    adr_contents = []
    discovery_data = None
    discovery_file_path = None
    
    if prd:
        # Use specific PRD discovery file when --prd flag is provided
        click.echo(f"🔍 Looking for PRD discovery file: {prd}")
        discovery_data, discovery_file_path = _find_prd_discovery_file(prd)
        
        if discovery_data:
            click.echo(f"✅ Found discovery file: {discovery_file_path}")
            # Extract PRD content from discovery data
            prd_content = discovery_data.get('prd_content', '')
            prd_metadata = discovery_data.get('prd_metadata', {})
        else:
            click.echo(f"⚠️  Warning: No discovery file found for PRD {prd}")
    
    # If no PRD specified or discovery file not found, look for nearest PRD
    if not prd_content:
        # Look for PRD in same directory or parent directories
        target_dir = os.path.dirname(target_path)
        prd_found = False
        
        # Search for PRD files
        for root, dirs, files in os.walk(DOCS):
            if root.startswith(os.path.join(DOCS, "prd")):
                for file in files:
                    if file.endswith('.md'):
                        prd_path = os.path.join(root, file)
                        try:
                            with open(prd_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content.startswith('---'):
                                    parts = content.split('---', 2)
                                    if len(parts) >= 3:
                                        frontmatter = yaml.safe_load(parts[1]) or {}
                                        if frontmatter.get('id') == prd:
                                            prd_content = parts[2]
                                            prd_metadata = frontmatter
                                            prd_found = True
                                            break
                        except Exception:
                            continue
                if prd_found:
                    break
    
    # Build context package
    context_package = {
        "target_path": target_path,
        "purpose": purpose,
        "feature": feature,
        "stacks": stacks.split(","),
        "token_limit": token_limit,
        "rules": rules,
        "prd_content": prd_content,
        "prd_metadata": prd_metadata,
        "adr_contents": adr_contents,
        "discovery_data": discovery_data,
        "discovery_file_path": discovery_file_path
    }
    
    # Save context package
    context_file = os.path.join(CACHE, "pack_context.json")
    with open(context_file, "w", encoding="utf-8") as f:
        yaml.dump(context_package, f, default_flow_style=False)
    
    click.echo(f"✅ Context package built for {target_path}")
    click.echo(f"📁 Saved to: {context_file}")

@cli.command("context:scan")
@click.option("--output", default="builder/cache/context_graph.json", help="Output JSON file path")
@click.option("--stats-only", is_flag=True, help="Only print statistics, don't export JSON")
def context_scan(output, stats_only):
    """Scan project and build context graph of nodes and relationships."""
    try:
        from ..context_graph import ContextGraph
        
        click.echo("🔍 Scanning project for context graph...")
        
        # Build context graph
        graph = ContextGraph()
        graph.scan_project(ROOT)
        
        # Print statistics
        graph.print_stats()
        
        # Export to JSON unless stats-only
        if not stats_only:
            os.makedirs(os.path.dirname(output), exist_ok=True)
            graph.export_json(output)
            click.echo(f"📁 Context graph exported to: {output}")
        
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("Make sure context_graph.py exists in the builder directory")
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# Placeholder for other context commands - will be implemented in next iteration
@cli.command("ctx:build-enhanced")
@click.argument("target_path")
def ctx_build_enhanced(target_path):
    """Enhanced context building - to be implemented."""
    click.echo(f"🧠 Enhanced context building for {target_path} - to be implemented")
    return 0

@cli.command("ctx:diff")
@click.argument("old_pack")
def ctx_diff(old_pack):
    """Compare context packages - to be implemented."""
    click.echo(f"🔍 Comparing context packages with {old_pack} - to be implemented")
    return 0

@cli.command("ctx:explain")
@click.option("--input", default="builder/cache/pack_context.json")
def ctx_explain(input):
    """Explain context package - to be implemented."""
    click.echo(f"📋 Explaining context from {input} - to be implemented")
    return 0

@cli.command("ctx:validate")
@click.argument("context_file", default="builder/cache/pack_context.json")
def ctx_validate(context_file):
    """Validate context package - to be implemented."""
    click.echo(f"✅ Validating context file {context_file} - to be implemented")
    return 0

@cli.command("ctx:pack")
@click.option("--output", default="", help="Output file path")
def ctx_pack(output):
    """Pack context data - to be implemented."""
    click.echo(f"📦 Packing context data to {output or 'stdout'} - to be implemented")
    return 0

@cli.command("ctx:trace")
@click.option("--output", default="builder/cache/trace.csv")
def ctx_trace(output):
    """Trace context usage - to be implemented."""
    click.echo(f"🔍 Tracing context usage to {output} - to be implemented")
    return 0

@cli.command("ctx:graph:build")
@click.option("--output", default="builder/cache/context_graph.json")
def ctx_graph_build(output):
    """Build context graph - to be implemented."""
    click.echo(f"📊 Building context graph to {output} - to be implemented")
    return 0

@cli.command("ctx:graph:stats")
def ctx_graph_stats():
    """Show context graph statistics - to be implemented."""
    click.echo("📊 Context graph statistics - to be implemented")
    return 0

@cli.command("ctx:select")
@click.argument("target_path")
def ctx_select(target_path):
    """Select context for target - to be implemented."""
    click.echo(f"🎯 Selecting context for {target_path} - to be implemented")
    return 0

@cli.command("ctx:budget")
@click.argument("target_path")
def ctx_budget(target_path):
    """Calculate context budget - to be implemented."""
    click.echo(f"💰 Calculating context budget for {target_path} - to be implemented")
    return 0


@cli.command("ctx:build")
@click.option("--from", "from_sources", multiple=True, type=click.Choice(['discovery', 'interview']), 
              default=['discovery', 'interview'], help="Sources to build context from")
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
@click.option("--sections", multiple=True, type=click.Choice(['prd', 'arch', 'int', 'impl', 'exec', 'task']),
              default=['prd', 'arch', 'int', 'impl', 'exec', 'task'], help="Sections to generate")
def ctx_build(from_sources, overwrite, sections):
    """Build comprehensive context from discovery and interview data."""
    try:
        from ..context_builder import build_context_cli
        
        click.echo("🏗️  Building context from discovery and interview data...")
        
        # Convert tuple to list
        from_sources_list = list(from_sources)
        sections_list = list(sections)
        
        # Build context
        results = build_context_cli(
            from_sources=from_sources_list,
            overwrite=overwrite,
            sections=sections_list
        )
        
        # Display results
        click.echo("\n✅ Context building complete!")
        click.echo(f"📊 Generated {len(results)} document types:")
        
        for doc_type, doc_info in results.items():
            if isinstance(doc_info, dict) and 'file' in doc_info:
                status = doc_info.get('status', 'unknown')
                click.echo(f"  📄 {doc_type.upper()}: {doc_info['file']} ({status})")
            elif isinstance(doc_info, dict) and 'files' in doc_info:
                click.echo(f"  📄 {doc_type.upper()}: {len(doc_info['files'])} files generated")
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error building context: {e}")
        return 1
