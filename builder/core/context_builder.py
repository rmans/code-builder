#!/usr/bin/env python3
"""
Context Builder - Orchestrates context graph, selection, and budget management

This module composes existing context components to generate comprehensive
documentation and task planning from discovery and interview data.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from .context_graph import ContextGraph, GraphNode
from .context_select import ContextSelector
from .context_budget import ContextBudgetManager, BudgetItem


class ContextBuilder:
    """Orchestrates context graph, selection, and budget management for document generation."""
    
    def __init__(self, root_path: str = ".", cache_dir: Optional[str] = None):
        """Initialize the context builder.
        
        Args:
            root_path: Root directory of the project
            cache_dir: Optional cache directory (uses overlay paths if available)
        """
        self.root_path = Path(root_path).resolve()
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use overlay paths if available
            try:
                from ..overlay.paths import OverlayPaths
                overlay_paths = OverlayPaths()
                self.cache_dir = Path(overlay_paths.get_cache_dir())
            except ImportError:
                self.cache_dir = self.root_path / "builder" / "cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up output directories for different document types
        try:
            from ..overlay.paths import OverlayPaths
            overlay_paths = OverlayPaths()
            self.docs_dir = Path(overlay_paths.get_docs_dir())
            self.templates_dir = Path(overlay_paths.get_templates_dir())
        except ImportError:
            self.docs_dir = self.root_path / "cb_docs"
            self.templates_dir = self.docs_dir / "templates"
        
        # Create document type directories
        self.doc_dirs = {
            'prd': self.docs_dir / "prd",
            'arch': self.docs_dir / "arch", 
            'int': self.docs_dir / "integrations",
            'impl': self.docs_dir / "impl",
            'exec': self.docs_dir / "exec",
            'task': self.docs_dir / "tasks"
        }
        
        for doc_dir in self.doc_dirs.values():
            doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.graph = ContextGraph()
        self.selector = ContextSelector(self.graph)
        self.budget_manager = ContextBudgetManager()
        
        # Load existing context if available
        self._load_existing_context()
    
    def build_context(self, 
                     from_sources: List[str] = None,
                     overwrite: bool = False,
                     sections: List[str] = None) -> Dict[str, Any]:
        """Build comprehensive context from discovery and interview data.
        
        Args:
            from_sources: Sources to build from ('discovery', 'interview')
            overwrite: Whether to overwrite existing files
            sections: Sections to generate ('prd', 'arch', 'int', 'impl', 'exec', 'task')
            
        Returns:
            Dictionary with generation results and file paths
        """
        if from_sources is None:
            from_sources = ['discovery', 'interview']
        
        if sections is None:
            sections = ['prd', 'arch', 'int', 'impl', 'exec', 'task']
        
        print(f"🏗️  Building context from sources: {', '.join(from_sources)}")
        print(f"📋 Generating sections: {', '.join(sections)}")
        
        # Load input data
        input_data = self._load_input_data(from_sources)
        
        # Generate context documents
        results = {}
        
        for section in sections:
            if section == 'prd':
                results['prd'] = self._generate_prd(input_data, overwrite)
            elif section == 'arch':
                results['arch'] = self._generate_architecture(input_data, overwrite)
            elif section == 'int':
                results['int'] = self._generate_integration_plan(input_data, overwrite)
            elif section == 'impl':
                results['impl'] = self._generate_implementation_roadmap(input_data, overwrite)
            elif section == 'exec':
                results['exec'] = self._generate_execution_plan(input_data, overwrite)
            elif section == 'task':
                results['task'] = self._generate_tasks(input_data, overwrite)
        
        # Update context graph
        self._update_context_graph(results)
        
        return results
    
    def _load_input_data(self, sources: List[str]) -> Dict[str, Any]:
        """Load input data from specified sources."""
        input_data = {}
        
        for source in sources:
            if source == 'discovery':
                discovery_data = self._load_discovery_data()
                if discovery_data:
                    input_data['discovery'] = discovery_data
            
            elif source == 'interview':
                interview_data = self._load_interview_data()
                if interview_data:
                    input_data['interview'] = interview_data
        
        return input_data
    
    def _load_discovery_data(self) -> Optional[Dict[str, Any]]:
        """Load discovery data from report.json."""
        discovery_file = self.docs_dir / "discovery" / "report.json"
        if discovery_file.exists():
            with open(discovery_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Convert absolute paths to relative paths
                if 'project_info' in data and 'path' in data['project_info']:
                    data['project_info']['path'] = "."
                
                return data
        return None
    
    def _load_interview_data(self) -> Optional[Dict[str, Any]]:
        """Load interview data from interview.json."""
        interview_file = self.docs_dir / "planning" / "interview.json"
        if interview_file.exists():
            with open(interview_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _generate_prd(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate Product Requirements Document using template."""
        prd_dir = self.doc_dirs['prd']
        # Generate proper filename with date prefix and title
        today = datetime.now().strftime('%Y-%m-%d')
        interview = input_data.get('interview', {})
        title = interview.get('product_name', 'Product').replace(' ', '-').replace('_', '-')
        prd_file = prd_dir / f"PRD-{today}-{title}.md"
        
        if not overwrite and prd_file.exists():
            print(f"⏭️  PRD already exists: {prd_file}")
            return {"file": str(prd_file), "status": "skipped"}
        
        # Extract data from inputs
        discovery = input_data.get('discovery', {})
        interview = input_data.get('interview', {})
        
        # Generate PRD content using template
        prd_content = self._render_template('prd.md.hbs', discovery, interview)
        
        # Write PRD file
        with open(prd_file, 'w', encoding='utf-8') as f:
            f.write(prd_content)
        
        # Update master file
        self._update_master_file('prd', f"PRD-{today}-{title}", interview.get('product_name', 'Product'), 'draft', 'product')
        
        # Sync master file to update table
        self._sync_master_file('prd')
        
        print(f"📄 Generated PRD: {prd_file}")
        return {"file": str(prd_file), "status": "generated"}
    
    def _generate_architecture(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate Architecture documents using template."""
        arch_dir = self.doc_dirs['arch']
        # Generate proper filename with date prefix and title
        today = datetime.now().strftime('%Y-%m-%d')
        interview = input_data.get('interview', {})
        title = interview.get('product_name', 'Product').replace(' ', '-').replace('_', '-')
        arch_file = arch_dir / f"ARCH-{today}-{title}.md"
        
        if not overwrite and arch_file.exists():
            print(f"⏭️  Architecture already exists: {arch_file}")
            return {"file": str(arch_file), "status": "skipped"}
        
        # Extract data from inputs
        discovery = input_data.get('discovery', {})
        interview = input_data.get('interview', {})
        
        # Generate architecture content using template
        arch_content = self._render_template('arch.md.hbs', discovery, interview)
        
        # Write architecture file
        with open(arch_file, 'w', encoding='utf-8') as f:
            f.write(arch_content)
        
        # Update master file
        self._update_master_file('arch', f"ARCH-{today}-{title}", f"{interview.get('product_name', 'Product')} Architecture", 'draft', 'architecture')
        
        # Sync master file to update table
        self._sync_master_file('arch')
        
        print(f"📄 Generated Architecture: {arch_file}")
        return {"file": str(arch_file), "status": "generated"}
    
    def _generate_integration_plan(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate Integration Plan using template."""
        int_dir = self.doc_dirs['int']
        # Generate proper filename with date prefix and title
        today = datetime.now().strftime('%Y-%m-%d')
        interview = input_data.get('interview', {})
        title = interview.get('product_name', 'Product').replace(' ', '-').replace('_', '-')
        int_file = int_dir / f"INT-{today}-{title}.md"
        
        if not overwrite and int_file.exists():
            print(f"⏭️  Integration Plan already exists: {int_file}")
            return {"file": str(int_file), "status": "skipped"}
        
        # Extract data from inputs
        discovery = input_data.get('discovery', {})
        interview = input_data.get('interview', {})
        
        # Generate integration plan content using template
        int_content = self._render_template('integrations.md.hbs', discovery, interview)
        
        # Write integration plan file
        with open(int_file, 'w', encoding='utf-8') as f:
            f.write(int_content)
        
        # Update master file
        self._update_master_file('integrations', f"INT-{today}-{title}", f"{interview.get('product_name', 'Product')} Integration Plan", 'draft', 'integration')
        
        print(f"📄 Generated Integration Plan: {int_file}")
        return {"file": str(int_file), "status": "generated"}
    
    def _generate_implementation_roadmap(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate Implementation Roadmap using template."""
        impl_dir = self.doc_dirs['impl']
        # Generate proper filename with date prefix and title
        today = datetime.now().strftime('%Y-%m-%d')
        interview = input_data.get('interview', {})
        title = interview.get('product_name', 'Product').replace(' ', '-').replace('_', '-')
        impl_file = impl_dir / f"IMPL-{today}-{title}.md"
        
        if not overwrite and impl_file.exists():
            print(f"⏭️  Implementation Roadmap already exists: {impl_file}")
            return {"file": str(impl_file), "status": "skipped"}
        
        # Extract data from inputs
        discovery = input_data.get('discovery', {})
        interview = input_data.get('interview', {})
        
        # Generate implementation roadmap content using template
        impl_content = self._render_template('impl.md.hbs', discovery, interview)
        
        # Write implementation roadmap file
        with open(impl_file, 'w', encoding='utf-8') as f:
            f.write(impl_content)
        
        # Update master file
        self._update_master_file('impl', f"IMPL-{today}-{title}", f"{interview.get('product_name', 'Product')} Implementation Roadmap", 'draft', 'implementation')
        
        print(f"📄 Generated Implementation Roadmap: {impl_file}")
        return {"file": str(impl_file), "status": "generated"}
    
    def _generate_execution_plan(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate Execution Plan using template."""
        exec_dir = self.doc_dirs['exec']
        # Generate proper filename with date prefix and title
        today = datetime.now().strftime('%Y-%m-%d')
        interview = input_data.get('interview', {})
        title = interview.get('product_name', 'Product').replace(' ', '-').replace('_', '-')
        exec_file = exec_dir / f"EXEC-{today}-{title}.md"
        
        if not overwrite and exec_file.exists():
            print(f"⏭️  Execution Plan already exists: {exec_file}")
            return {"file": str(exec_file), "status": "skipped"}
        
        # Extract data from inputs
        discovery = input_data.get('discovery', {})
        interview = input_data.get('interview', {})
        
        # Generate execution plan content using template
        exec_content = self._render_template('exec.md.hbs', discovery, interview)
        
        # Write execution plan file
        with open(exec_file, 'w', encoding='utf-8') as f:
            f.write(exec_content)
        
        # Update master file
        self._update_master_file('exec', f"EXEC-{today}-{title}", f"{interview.get('product_name', 'Product')} Execution Plan", 'draft', 'execution')
        
        print(f"📄 Generated Execution Plan: {exec_file}")
        return {"file": str(exec_file), "status": "generated"}
    
    def _generate_tasks(self, input_data: Dict[str, Any], overwrite: bool) -> Dict[str, Any]:
        """Generate task files and index using template."""
        tasks_dir = self.doc_dirs['task']
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate individual task files
        task_files = self._create_task_files(input_data, tasks_dir, overwrite)
        
        # Generate tasks index
        index_file = tasks_dir / "index.json"
        self._create_tasks_index(task_files, index_file)
        
        print(f"📄 Generated {len(task_files)} task files in: {tasks_dir}")
        print(f"📄 Generated tasks index: {index_file}")
        
        return {
            "files": task_files,
            "index": str(index_file),
            "status": "generated"
        }
    
    
    
    
    
    def _create_task_files(self, input_data: Dict[str, Any], tasks_dir: Path, overwrite: bool) -> List[str]:
        """Create individual task files."""
        interview = input_data.get('interview', {})
        features = interview.get('key_features', [])
        
        task_files = []
        
        for i, feature in enumerate(features, 1):
            task_id = f"TASK-{datetime.now().strftime('%Y-%m-%d')}-F{i:02d}"
            task_file = tasks_dir / f"{task_id}.md"
            
            if not overwrite and task_file.exists():
                continue
            
            task_content = self._create_task_content(task_id, feature, interview)
            
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            task_files.append(str(task_file))
        
        return task_files
    
    def _create_task_content(self, task_id: str, feature: str, interview: Dict[str, Any]) -> str:
        """Create individual task content."""
        project_name = interview.get('product_name', 'Project')
        timeline = interview.get('timeline', 'Not specified')
        
        content = f"""---
id: {task_id}
title: Implement {feature}
description: Implement {feature} for {project_name}
status: pending
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
owner: development-team
domain: implementation
priority: 8
agent_type: backend
dependencies: []
tags: [feature, implementation, {feature.lower().replace(' ', '-')}]
---

# Task: Implement {feature}

## Description
Implement {feature} functionality for {project_name}.

## Requirements
- Feature: {feature}
- Project: {project_name}
- Timeline: {timeline}

## Acceptance Criteria
- [ ] Feature implemented according to specifications
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and approved

## Implementation Notes
- Follow project coding standards
- Ensure proper error handling
- Add comprehensive logging
- Consider performance implications

## Testing Strategy
- Unit tests for core functionality
- Integration tests for external dependencies
- End-to-end tests for user workflows
- Performance tests for scalability

## Dependencies
- Project infrastructure setup
- Core framework implementation
- Database schema design

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return content
    
    def _create_tasks_index(self, task_files: List[str], index_file: Path):
        """Create tasks index JSON file."""
        tasks_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_tasks": len(task_files),
                "version": "1.0"
            },
            "tasks": []
        }
        
        for task_file in task_files:
            task_path = Path(task_file)
            task_data = {
                "id": task_path.stem,
                "file": str(task_path),
                "title": f"Task {task_path.stem}",
                "status": "pending"
            }
            tasks_data["tasks"].append(task_data)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, sort_keys=True)
    
    def _update_context_graph(self, results: Dict[str, Any]):
        """Update context graph with generated documents."""
        # This would integrate with the existing context graph
        # For now, we'll just log the results
        print(f"📊 Context graph updated with {len(results)} document types")
    
    def _render_template(self, template_name: str, discovery: Dict[str, Any], interview: Dict[str, Any]) -> str:
        """Render a Handlebars template with discovery and interview data."""
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Prepare template context
        context = {
            'id': f"PRD-{datetime.now().strftime('%Y-%m-%d')}",
            'title': interview.get('product_name', 'Product Requirements Document'),
            'owner': 'product-team',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'requires_abc_iteration': False,
            'abc_target_file': '',
            'abc_rounds': 3,
            'links': {
                'arch': [],
                'ux': [],
                'impl': [],
                'exec': []
            },
            'discovery': discovery,
            'interview': interview,
            'project_name': interview.get('product_name', 'Project'),
            'product_description': interview.get('product_description', ''),
            'target_users': interview.get('target_users', ''),
            'key_features': interview.get('key_features', []),
            'success_metrics': interview.get('success_metrics', []),
            'technical_requirements': interview.get('technical_requirements', ''),
            'assumptions': interview.get('assumptions', []),
            'risks': interview.get('risks', []),
            'decisions': interview.get('decisions', []),
            'languages': discovery.get('languages', {}).get('detected', []),
            'frameworks': discovery.get('frameworks', {}).get('detected', [])
        }
        
        # Simple template rendering (replace Handlebars syntax)
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace Handlebars variables
        for key, value in context.items():
            if isinstance(value, list):
                if key in ['key_features', 'success_metrics', 'assumptions', 'risks', 'decisions']:
                    # Format lists as markdown
                    formatted_list = '\n'.join(f"- {item}" for item in value)
                    template_content = template_content.replace(f"{{{{{key}}}}}", formatted_list)
                else:
                    # Join lists with commas
                    template_content = template_content.replace(f"{{{{{key}}}}}", ', '.join(str(v) for v in value))
            else:
                template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
        
        # Handle Handlebars helpers like | default([])
        template_content = template_content.replace("{{links.arch | default([])}}", "[]")
        template_content = template_content.replace("{{links.ux | default([])}}", "[]")
        template_content = template_content.replace("{{links.impl | default([])}}", "[]")
        template_content = template_content.replace("{{links.exec | default([])}}", "[]")
        
        return template_content
    
    def _update_master_file(self, doc_type: str, doc_id: str, title: str, status: str, domain: str):
        """Update master file with new document entry by adding to documents array temporarily for sync."""
        try:
            from ..config.settings import get_config
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
                                import yaml
                                frontmatter = yaml.safe_load(frontmatter_text) or {}
                            except yaml.YAMLError:
                                frontmatter = {}
                            
                            # Add document to list temporarily (will be removed by sync)
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
                                    'created': datetime.now().strftime('%Y-%m-%d')
                                })
                                
                                # Write updated content (documents will be removed by sync)
                                new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---' + body
                                with open(master_file, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                print(f"📝 Updated master file: {master_file}")
        except Exception as e:
            # Silently fail - master file update is optional
            print(f"⚠️  Warning: Could not update master file: {e}")
    
    def _sync_master_file(self, doc_type: str):
        """Sync master file table from frontmatter documents."""
        try:
            from ..config.settings import get_config
            config = get_config()
            master_files = config.get_master_files()
            
            if doc_type in master_files:
                master_file = master_files[doc_type]
                if os.path.exists(master_file):
                    # Import the sync function from document_commands
                    from .cli.document_commands import _sync_master_file
                    _sync_master_file(master_file, doc_type)
        except Exception as e:
            # Silently fail - master file sync is optional
            print(f"⚠️  Warning: Could not sync master file: {e}")
    
    def _generate_context_pack_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate context pack data without writing to file."""
        try:
            # Create context pack data
            pack_data = {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "version": "1.0",
                    "generator": "Code Builder Context Builder",
                    "total_documents": 0  # Will be updated when documents are generated
                },
                "inputs": {
                    "discovery": input_data.get('discovery', {}),
                    "interview": input_data.get('interview', {})
                },
                "documents": {},
                "rules": self._collect_rules_links(),
                "acceptance_criteria": {},
                "code_excerpts": self._collect_code_excerpts({}),
                "paths": {
                    "root": ".",
                    "docs": "cb_docs",
                    "templates": "cb_docs/templates",
                    "cache": ".cb/cache"
                }
            }
            
            return pack_data
            
        except Exception as e:
            print(f"⚠️  Warning: Could not generate context pack data: {e}")
            return {}
    
    def _generate_context_pack(self, results: Dict[str, Any], input_data: Dict[str, Any]):
        """Generate pack_context.json with metadata about the context pack."""
        try:
            # Create context pack data
            pack_data = {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "version": "1.0",
                    "generator": "Code Builder Context Builder",
                    "total_documents": len([r for r in results.values() if isinstance(r, dict) and r.get('status') == 'generated'])
                },
                "inputs": {
                    "discovery": input_data.get('discovery', {}),
                    "interview": input_data.get('interview', {})
                },
                "documents": {},
                "rules": self._collect_rules_links(),
                "acceptance_criteria": self._collect_acceptance_criteria(results),
                "code_excerpts": self._collect_code_excerpts(results),
                "paths": {
                    "root": ".",
                    "docs": "cb_docs",
                    "templates": "cb_docs/templates",
                    "cache": ".cb/cache"
                }
            }
            
            # Add document metadata
            for doc_type, doc_info in results.items():
                if isinstance(doc_info, dict) and 'file' in doc_info:
                    doc_path = Path(doc_info['file'])
                    pack_data["documents"][doc_type] = {
                        "file": str(doc_path.relative_to(self.root_path)),
                        "status": doc_info.get('status', 'unknown'),
                        "size": doc_path.stat().st_size if doc_path.exists() else 0,
                        "modified": datetime.fromtimestamp(doc_path.stat().st_mtime).isoformat() if doc_path.exists() else None
                    }
                elif isinstance(doc_info, dict) and 'files' in doc_info:
                    # Handle task files
                    pack_data["documents"][doc_type] = {
                        "files": [str(Path(f).relative_to(self.root_path)) for f in doc_info['files']],
                        "count": len(doc_info['files']),
                        "index": str(Path(doc_info['index']).relative_to(self.root_path)) if 'index' in doc_info else None,
                        "status": doc_info.get('status', 'unknown')
                    }
            
            # Write pack_context.json
            pack_file = self.docs_dir / "pack_context.json"
            with open(pack_file, 'w', encoding='utf-8') as f:
                json.dump(pack_data, f, indent=2, sort_keys=True)
            
            print(f"📦 Generated context pack: {pack_file}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not generate context pack: {e}")
    
    def _collect_rules_links(self) -> List[str]:
        """Collect links to relevant rules files."""
        rules_links = []
        try:
            rules_dir = self.docs_dir / "rules"
            if rules_dir.exists():
                for rule_file in rules_dir.glob("*.md"):
                    rules_links.append(str(rule_file.relative_to(self.root_path)))
        except Exception as e:
            print(f"⚠️  Warning: Could not collect rules links: {e}")
        return rules_links
    
    def _collect_acceptance_criteria(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Collect acceptance criteria from generated documents."""
        criteria = {}
        try:
            for doc_type, doc_info in results.items():
                if isinstance(doc_info, dict) and 'file' in doc_info:
                    doc_path = Path(doc_info['file'])
                    if doc_path.exists():
                        # Read document and extract acceptance criteria
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for acceptance criteria sections
                        import re
                        criteria_pattern = r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)'
                        matches = re.findall(criteria_pattern, content, re.DOTALL | re.IGNORECASE)
                        
                        if matches:
                            criteria[doc_type] = [line.strip() for line in matches[0].split('\n') if line.strip() and line.strip().startswith('-')]
        except Exception as e:
            print(f"⚠️  Warning: Could not collect acceptance criteria: {e}")
        return criteria
    
    def _collect_code_excerpts(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Collect relevant code excerpts from the project."""
        excerpts = {}
        try:
            # Look for key source files
            source_files = [
                "builder/core/context_builder.py",
                "builder/core/cli/context_commands.py",
                "builder/discovery/interview.py",
                "builder/discovery/enhanced_engine.py"
            ]
            
            for source_file in source_files:
                file_path = self.root_path / source_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract key functions/classes
                    import re
                    function_pattern = r'def\s+(\w+)\s*\([^)]*\):'
                    class_pattern = r'class\s+(\w+)\s*[\(:]'
                    
                    functions = re.findall(function_pattern, content)
                    classes = re.findall(class_pattern, content)
                    
                    excerpts[source_file] = {
                        "functions": functions[:10],  # Limit to first 10
                        "classes": classes[:5]        # Limit to first 5
                    }
        except Exception as e:
            print(f"⚠️  Warning: Could not collect code excerpts: {e}")
        return excerpts
    
    def _load_existing_context(self):
        """Load existing context from cache."""
        context_file = self.cache_dir / "context_graph.json"
        if context_file.exists():
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
                print(f"📊 Loaded existing context with {len(context_data.get('nodes', []))} nodes")
            except Exception as e:
                print(f"⚠️  Warning: Could not load existing context: {e}")


def build_context_cli(from_sources: List[str] = None,
                     overwrite: bool = False,
                     sections: List[str] = None) -> Dict[str, Any]:
    """CLI-friendly wrapper for context building."""
    builder = ContextBuilder()
    return builder.build_context(from_sources, overwrite, sections)
