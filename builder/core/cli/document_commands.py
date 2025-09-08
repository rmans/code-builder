#!/usr/bin/env python3
"""
Document Commands Module

This module contains document-related commands like doc:*, adr:*, master:*
"""

import click
import os
import re
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
from .base import cli, safe_yaml_load, safe_json_dumps, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    ADRS = overlay_paths.get_adrs_dir()
    TEMPL = overlay_paths.get_templates_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    ADRS = DOCS / "adrs"
    TEMPL = DOCS / "templates"

def _today():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime('%Y-%m-%d')

def _render(template_path, context):
    """Render a Jinja2 template with context."""
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        return template.render(**context)
    except ImportError:
        click.echo("❌ Jinja2 not installed. Install with: pip install jinja2")
        raise SystemExit(1)

def _update_master_file(doc_type, doc_id, title, status, domain):
    """Update master file with new document entry."""
    try:
        from builder.config.settings import get_config
        config = get_config()
        master_files = config.get_master_files()
        
        if doc_type in master_files:
            master_file = master_files[doc_type]
            if os.path.exists(master_file):
                # Read existing content
                with open(master_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter_text = parts[1]
                        body = parts[2]
                        
                        try:
                            frontmatter = yaml.safe_load(frontmatter_text) or {}
                        except yaml.YAMLError:
                            frontmatter = {}
                        
                        # Add document to list
                        if 'documents' not in frontmatter:
                            frontmatter['documents'] = []
                        
                        # Check if document already exists
                        existing_docs = frontmatter.get('documents', [])
                        doc_exists = any(doc.get('id') == doc_id for doc in existing_docs)
                        
                        if not doc_exists:
                            frontmatter['documents'].append({
                                'id': doc_id,
                                'title': title,
                                'status': status,
                                'domain': domain,
                                'created': _today()
                            })
                            
                            # Write updated content
                            new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---' + body
                            with open(master_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
    except Exception as e:
        # Silently fail - master file update is optional
        pass

def _doc_load_front_matter(path):
    """Load front matter from a document file."""
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r'^---\n(.*?)\n---\n', txt, flags=re.S)
    if not m:
        return None, txt, None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, txt, m

def _doc_save_front_matter(path, front, txt, m):
    """Save front matter to a document file."""
    new = '---\n' + yaml.dump(front, sort_keys=False).strip() + '\n---\n' + txt[m.end():]
    Path(path).write_text(new, encoding="utf-8")

def _run_doc_index_hook():
    """Run doc:index hook and return number of docs indexed."""
    try:
        # This would call the doc:index command internally
        # For now, return 0 as a placeholder
        return 0
    except Exception:
        return 0

def _fix_master_file_frontmatter(master_file, doc_type):
    """Fix master file frontmatter for doc:check compliance."""
    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            # Add basic frontmatter
            frontmatter = {
                'id': f'master-{doc_type}',
                'title': f'Master {doc_type.upper()} Index',
                'status': 'active',
                'created': _today(),
                'documents': []
            }
            
            new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---\n' + content
            with open(master_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            click.echo(f"✅ Added frontmatter to {master_file}")
    except Exception as e:
        click.echo(f"⚠️  Error fixing {master_file}: {e}")

# Document Commands
@cli.command("adr:new")
@click.option("--title", required=True)
@click.option("--parent", default="ADR-0000")
@click.option("--related", multiple=True)
@click.option("--tags", default="")
def adr_new(title, parent, related, tags):
    """Create new Architecture Decision Records."""
    os.makedirs(ADRS, exist_ok=True)
    
    # Generate standardized ADR ID: ADR-YYYY-MM-DD-slug
    # Create slug from title
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:20]  # Limit slug length
    
    # Generate date string
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    # Create standardized ADR ID
    next_id = f"ADR-{date_str}-{slug}"
    ctx = {
        "id": next_id, "title": title, "date": _today(), "parent": parent,
        "related_files": list(related), "tags": tags,
        "context": "", "decision": "", "consequences": "", "alternatives": ""
    }
    out = _render(os.path.join(TEMPL, "sub_adr.md.hbs"), ctx)
    out_path = os.path.join(ADRS, f"{next_id}.md")
    with open(out_path, "w", encoding="utf-8") as f: 
        f.write(out)
    
    # Update master ADR file with duplicate prevention
    _update_master_file('adr', next_id, title, "proposed", "")
    
    click.echo(f"Created {out_path}")

# Placeholder for other document commands - will be implemented in next iteration
@cli.command("doc:new")
@click.argument("dtype", type=click.Choice(['prd', 'arch', 'integrations', 'ux', 'impl', 'exec', 'tasks']))
def doc_new(dtype):
    """Create new documents - to be fully implemented."""
    click.echo(f"📝 Creating new {dtype} document - to be implemented")
    return 0

@cli.command("doc:index")
def doc_index():
    """Generate documentation index - to be fully implemented."""
    click.echo("📚 Document index command - to be implemented")
    return 0

@cli.command("doc:set-links")
@click.argument("file")
def doc_set_links(file):
    """Set front-matter links - to be fully implemented."""
    click.echo(f"🔗 Setting links for {file} - to be implemented")
    return 0

@cli.command("doc:check")
def doc_check():
    """Validate docs front-matter - to be fully implemented."""
    click.echo("📋 Document check command - to be implemented")
    return 0

@cli.command("doc:fix-master")
def doc_fix_master():
    """Fix master files - to be fully implemented."""
    click.echo("🔧 Fixing master files - to be implemented")
    return 0

@cli.command("doc:abc")
@click.argument("doc_path")
def doc_abc(doc_path):
    """Manage ABC iteration - to be fully implemented."""
    click.echo(f"🔄 ABC iteration for {doc_path} - to be implemented")
    return 0

@cli.command("master:sync")
@click.option("--type", help="Sync specific document type")
def master_sync(type):
    """Synchronize master index files by regenerating tables from frontmatter documents."""
    try:
        from builder.config.settings import get_config
        config = get_config()
        master_files = config.get_master_files()
        
        if type and type in master_files:
            # Sync specific type
            _sync_master_file(master_files[type], type)
            click.echo(f"✅ Synced master file for {type}")
        else:
            # Sync all types
            for doc_type, master_file in master_files.items():
                if os.path.exists(master_file):
                    _sync_master_file(master_file, doc_type)
                    click.echo(f"✅ Synced master file for {doc_type}")
        
        click.echo("🔄 Master file sync complete!")
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error syncing master files: {e}")
        return 1

def _sync_master_file(master_file, doc_type):
    """Sync a single master file by regenerating the table from frontmatter documents."""
    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return
        
        # Parse frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return
        
        frontmatter_text = parts[1]
        body = parts[2]
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            return
        
        # Get documents from frontmatter
        documents = frontmatter.get('documents', [])
        
        # Remove documents from frontmatter (it should only be in the table)
        if 'documents' in frontmatter:
            del frontmatter['documents']
        
        # Generate table
        if documents:
            table_lines = [
                f"# {frontmatter.get('title', 'Index')}",
                "",
                "| ID | Title | Status | Domain | Link |",
                "|---|---|---|---|---|"
            ]
            
            for doc in documents:
                doc_id = doc.get('id', '')
                title = doc.get('title', '')
                status = doc.get('status', '')
                domain = doc.get('domain', '')
                link = f"[{doc_id}]({doc_id}.md)" if doc_id else ""
                
                table_lines.append(f"| {doc_id} | {title} | {status} | {domain} | {link} |")
        else:
            table_lines = [
                f"# {frontmatter.get('title', 'Index')}",
                "",
                "| ID | Title | Status | Domain | Link |",
                "|---|---|---|---|---|",
                "| *No documents currently defined* |  |  |  |  |"
            ]
        
        # Reconstruct content
        new_body = '\n'.join(table_lines)
        new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---\n\n' + new_body
        
        # Write updated content
        with open(master_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    except Exception as e:
        print(f"⚠️  Warning: Could not sync {master_file}: {e}")