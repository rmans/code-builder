#!/usr/bin/env python3
import os, json, datetime, glob, re, fnmatch, subprocess
import click
from jinja2 import Template
from pathlib import Path as PPath
from typing import Dict
import requests

ROOT  = os.path.dirname(os.path.dirname(__file__))
DOCS  = os.path.join(ROOT, "docs")
ADRS  = os.path.join(DOCS, "adrs")
TEMPL = os.path.join(DOCS, "templates")
CACHE = os.path.join(ROOT, "builder", "cache")

def _today(): return datetime.date.today().isoformat()

def _render(path, ctx):
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read()).render(**ctx)

def _update_master_file(doc_type, doc_id, title, status="draft", domain=""):
    """Update the master index file for a document type"""
    master_files = {
        'adr': 'docs/adrs/0000_MASTER_ADR.md',
        'prd': 'docs/prd/0000_MASTER_PRD.md',
        'arch': 'docs/arch/0000_MASTER_ARCH.md', 
        'exec': 'docs/exec/0000_MASTER_EXEC.md',
        'impl': 'docs/impl/0000_MASTER_IMPL.md',
        'integrations': 'docs/integrations/0000_MASTER_INTEGRATIONS.md',
        'tasks': 'docs/tasks/0000_MASTER_TASKS.md',
        'ux': 'docs/ux/0000_MASTER_UX.md'
    }
    
    master_file = master_files.get(doc_type)
    if not master_file or not os.path.exists(master_file):
        return
    
    # Check if entry already exists
    try:
        with open(master_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if doc_id already exists in the file
        if f"| {doc_id} |" in content:
            click.echo(f"Entry {doc_id} already exists in {master_file}")
            return
        
        # Create the new row
        row = f"| {doc_id} | {title} | {status} | {domain} | ./{doc_id}.md |\n"
        
        # Append to master file
        with open(master_file, "a", encoding="utf-8") as f:
            f.write(row)
        click.echo(f"Updated {master_file}")
    except Exception as e:
        click.echo(f"Warning: Could not update {master_file}: {e}")

def _extract_target_from_prd(prd_file) -> str:
    """Extract target path from PRD content"""
    try:
        with open(prd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for target information in PRD content
        # This could be in a "Target Path" or "Source" section
        import re
        
        # Try to find target path patterns
        target_patterns = [
            r'Target Path[:\s]+(.+)',
            r'Source[:\s]+(.+)',
            r'Repository[:\s]+(.+)',
            r'Codebase[:\s]+(.+)'
        ]
        
        for pattern in target_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                if target and target != '.':
                    return target
        
        # Default to repo root
        return "."
        
    except Exception:
        return "."

def _extract_batch_kwargs_from_prd(prd_file) -> dict:
    """Extract batch kwargs from PRD content for auto-generation"""
    try:
        with open(prd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information from PRD content
        import re
        
        batch_kwargs = {}
        
        # Extract product name
        product_match = re.search(r'Product Requirements Document[:\s]+(.+)', content)
        if product_match:
            batch_kwargs['product'] = product_match.group(1).strip()
        
        # Extract main idea from Executive Summary
        summary_match = re.search(r'## Executive Summary\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if summary_match:
            batch_kwargs['idea'] = summary_match.group(1).strip()
        
        # Extract problem from Problem Statement
        problem_match = re.search(r'## Problem Statement\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if problem_match:
            batch_kwargs['problem'] = problem_match.group(1).strip()
        
        # Extract target users
        users_match = re.search(r'## Target Users\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if users_match:
            batch_kwargs['users'] = users_match.group(1).strip()
        
        # Extract key features
        features_match = re.search(r'## Key Features\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if features_match:
            features_text = features_match.group(1).strip()
            # Convert numbered list to comma-separated
            features = re.findall(r'\d+\.\s*(.+)', features_text)
            if features:
                batch_kwargs['features'] = ', '.join(features)
        
        # Extract success metrics
        metrics_match = re.search(r'## Success Metrics\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if metrics_match:
            batch_kwargs['metrics'] = metrics_match.group(1).strip()
        
        return batch_kwargs
        
    except Exception:
        return {}

def _is_prd_stale(prd_file, cache_file) -> bool:
    """Check if PRD cache is stale by comparing content hashes"""
    try:
        import hashlib
        
        # Get PRD file modification time
        prd_mtime = prd_file.stat().st_mtime
        
        # Get cache file modification time
        cache_mtime = cache_file.stat().st_mtime
        
        # If PRD is newer than cache, it's stale
        if prd_mtime > cache_mtime:
            return True
        
        # Load cache file to check for content hash
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = yaml.safe_load(f)
        
        # Check if cache has content hash
        cached_hash = cache_data.get('content_hash')
        if not cached_hash:
            return True  # No hash means stale
        
        # Compute current PRD content hash
        with open(prd_file, 'r', encoding='utf-8') as f:
            prd_content = f.read()
        
        current_hash = hashlib.md5(prd_content.encode()).hexdigest()
        
        # Compare hashes
        return cached_hash != current_hash
        
    except Exception:
        return True  # Error means stale

def _refresh_prd_context(prd_id: str, question_set: str, pack: bool) -> None:
    """Refresh a single PRD context using existing refresh logic"""
    from discovery.engine import DiscoveryEngine
    from discovery.analyzer import CodeAnalyzer
    from discovery.synthesizer import DiscoverySynthesizer
    from discovery.validator import DiscoveryValidator
    from discovery.generators import DiscoveryGenerators
    import yaml
    from pathlib import Path
    
    # Load the PRD cache file
    prd_cache_file = Path("builder/cache/discovery") / f"{prd_id}.yml"
    if not prd_cache_file.exists():
        raise FileNotFoundError(f"PRD cache file not found: {prd_cache_file}")
    
    # Load PRD data
    with open(prd_cache_file, 'r', encoding='utf-8') as f:
        prd_data = yaml.safe_load(f)
    
    # Extract original discovery results
    discovery_results = prd_data.get('discovery_results', {})
    interview_data = discovery_results.get('interview', {})
    original_target = interview_data.get('target', '.')
    
    # Initialize discovery engine
    engine = DiscoveryEngine(question_set=question_set)
    
    # Re-run analysis
    analysis_data = engine.analyzer.analyze(Path(original_target), interview_data)
    
    # Re-run synthesis
    synthesis_data = engine.synthesizer.synthesize(analysis_data, interview_data)
    
    # Re-run validation
    validation_data = engine.validator.validate(analysis_data, synthesis_data)
    
    # Update PRD cache with refreshed data
    prd_data['discovery_results']['analysis'] = analysis_data
    prd_data['discovery_results']['synthesis'] = synthesis_data
    prd_data['discovery_results']['validation'] = validation_data
    prd_data['last_refreshed'] = engine._get_timestamp()
    
    # Update content hash
    prd_file = Path("docs/prd") / f"{prd_id}.md"
    if prd_file.exists():
        with open(prd_file, 'r', encoding='utf-8') as f:
            prd_content = f.read()
        import hashlib
        prd_data['content_hash'] = hashlib.md5(prd_content.encode()).hexdigest()
    
    # Save updated PRD cache
    with open(prd_cache_file, 'w', encoding='utf-8') as f:
        yaml.dump(prd_data, f, default_flow_style=False, sort_keys=False)
    
    # Optional: Generate context pack
    if pack:
        try:
            engine._try_auto_ctx_build(Path(original_target))
        except Exception:
            pass  # Silently fail for pack generation

def _adapt_results_for_prd(results, target_prd_id, prd_file):
    """Adapt discovery results to match a specific PRD ID"""
    import yaml
    import hashlib
    from pathlib import Path
    
    try:
        # Extract information from the PRD file
        batch_kwargs = _extract_batch_kwargs_from_prd(prd_file)
        
        # Create adapted context data
        adapted_context = {
            'prd_id': target_prd_id,
            'product_name': batch_kwargs.get('product', 'Unknown Product'),
            'main_idea': batch_kwargs.get('idea', ''),
            'problem_solved': batch_kwargs.get('problem', ''),
            'target_users': batch_kwargs.get('users', ''),
            'key_features': batch_kwargs.get('features', ''),
            'success_metrics': batch_kwargs.get('metrics', ''),
            'tech_stack_preferences': 'Node.js/JavaScript, Python',  # Default
            'detected_tech': results.get('analysis', {}).get('detected', {}),
            'created': results.get('interview', {}).get('timestamp', ''),
            'status': 'draft',
            'discovery_results': {
                'interview': results.get('interview', {}),
                'analysis': results.get('analysis', {}),
                'synthesis': results.get('synthesis', {}),
                'generation': results.get('generation', {}),
                'validation': results.get('validation', {})
            }
        }
        
        # Add content hash
        with open(prd_file, 'r', encoding='utf-8') as f:
            prd_content = f.read()
        adapted_context['content_hash'] = hashlib.md5(prd_content.encode()).hexdigest()
        
        # Save adapted context
        cache_file = Path("builder/cache/discovery") / f"{target_prd_id}.yml"
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(adapted_context, f, default_flow_style=False, sort_keys=False)
            
    except Exception as e:
        raise Exception(f"Failed to adapt results for {target_prd_id}: {e}")

def _get_doc_type_from_file(doc_file):
    """Determine document type from file path"""
    doc_name = doc_file.stem
    if doc_name.startswith("PRD-"):
        return "prd"
    elif doc_name.startswith("ADR-"):
        return "adr"
    elif doc_name.startswith("ARCH-"):
        return "arch"
    elif doc_name.startswith("EXEC-"):
        return "exec"
    elif doc_name.startswith("IMPL-"):
        return "impl"
    elif doc_name.startswith("INTEGRATIONS-"):
        return "integrations"
    elif doc_name.startswith("TASKS-"):
        return "tasks"
    elif doc_name.startswith("UX-"):
        return "ux"
    else:
        return "unknown"

def _extract_target_from_doc(doc_file):
    """Extract target path from document content (generalized for all types)"""
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for target information in document content
        import re
        
        # Try to find target path patterns
        target_patterns = [
            r'Target Path[:\s]+(.+)',
            r'Source[:\s]+(.+)',
            r'Repository[:\s]+(.+)',
            r'Codebase[:\s]+(.+)',
            r'Implementation Path[:\s]+(.+)',
            r'Code Path[:\s]+(.+)'
        ]
        
        for pattern in target_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                if target and target != '.':
                    return target
        
        # Default to repo root
        return "."
        
    except Exception:
        return "."

def _extract_batch_kwargs_from_doc(doc_file):
    """Extract batch kwargs from document content (generalized for all types)"""
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information from document content
        import re
        
        batch_kwargs = {}
        
        # Extract title/name
        title_patterns = [
            r'# (.+?)(?:\n|$)',
            r'Title[:\s]+(.+)',
            r'Name[:\s]+(.+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                batch_kwargs['product'] = match.group(1).strip()
                break
        
        # Extract description/summary
        desc_patterns = [
            r'## Summary\s*\n\s*(.+?)(?=\n##|\Z)',
            r'## Description\s*\n\s*(.+?)(?=\n##|\Z)',
            r'## Overview\s*\n\s*(.+?)(?=\n##|\Z)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                batch_kwargs['idea'] = match.group(1).strip()
                break
        
        # Extract problem/context
        problem_patterns = [
            r'## Problem\s*\n\s*(.+?)(?=\n##|\Z)',
            r'## Context\s*\n\s*(.+?)(?=\n##|\Z)',
            r'## Background\s*\n\s*(.+?)(?=\n##|\Z)'
        ]
        
        for pattern in problem_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                batch_kwargs['problem'] = match.group(1).strip()
                break
        
        return batch_kwargs
        
    except Exception:
        return {}

def _is_doc_stale(doc_file, cache_file):
    """Check if document cache is stale by comparing content hashes (generalized)"""
    try:
        import hashlib
        
        # Get document file modification time
        doc_mtime = doc_file.stat().st_mtime
        
        # Get cache file modification time
        cache_mtime = cache_file.stat().st_mtime
        
        # If document is newer than cache, it's stale
        if doc_mtime > cache_mtime:
            return True
        
        # Load cache file to check for content hash
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = yaml.safe_load(f)
        
        # Check if cache has content hash
        cached_hash = cache_data.get('content_hash')
        if not cached_hash:
            return True  # No hash means stale
        
        # Compute current document content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        
        current_hash = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Compare hashes
        return cached_hash != current_hash
        
    except Exception:
        return True  # Error means stale

def _update_doc_content_hash(doc_id, doc_file):
    """Update content hash for non-PRD documents"""
    import yaml
    import hashlib
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Load existing cache file
        cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
        if not cache_file.exists():
            return
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = yaml.safe_load(f)
        
        # Update content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        cache_data['content_hash'] = hashlib.md5(doc_content.encode()).hexdigest()
        cache_data['last_updated'] = datetime.now().isoformat()
        
        # Save updated cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(cache_data, f, default_flow_style=False, sort_keys=False)
            
    except Exception:
        pass  # Silently fail for content hash updates

def _get_discovery_tier(doc_type):
    """Determine discovery tier for document type"""
    discovery_tiers = {
        "prd": "full",           # Tier 1: Full discovery context
        "arch": "targeted",      # Tier 2: Targeted discovery context
        "impl": "targeted",      # Tier 2: Targeted discovery context
        "adr": "lightweight",    # Tier 3: Lightweight discovery context
        "exec": "lightweight",   # Tier 3: Lightweight discovery context
        "ux": "lightweight",     # Tier 3: Lightweight discovery context
        "tasks": "hash_only",    # Tier 4: Content hash only
        "integrations": "hash_only"  # Tier 4: Content hash only
    }
    return discovery_tiers.get(doc_type, "hash_only")

def _generate_targeted_discovery_context(doc_id, doc_file, doc_type):
    """Generate targeted discovery context for ARCH and IMPL documents"""
    import yaml
    import hashlib
    from pathlib import Path
    from discovery.engine import DiscoveryEngine
    from datetime import datetime
    
    try:
        # Extract target and basic info from document
        target = _extract_target_from_doc(doc_file) or "."
        batch_kwargs = _extract_batch_kwargs_from_doc(doc_file)
        
        # Initialize discovery engine
        engine = DiscoveryEngine(question_set="comprehensive")
        
        # Run targeted analysis based on document type
        if doc_type == "arch":
            # Architecture-focused analysis
            analysis_data = _analyze_architecture_context(target, doc_file)
        elif doc_type == "impl":
            # Implementation-focused analysis
            analysis_data = _analyze_implementation_context(target, doc_file)
        else:
            # Fallback to basic analysis
            analysis_data = engine.analyzer.analyze(Path(target), {})
        
        # Create targeted context
        targeted_context = {
            'doc_id': doc_id,
            'doc_type': doc_type,
            'title': batch_kwargs.get('product', 'Unknown'),
            'description': batch_kwargs.get('idea', ''),
            'target_path': target,
            'analysis_data': analysis_data,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'discovery_tier': 'targeted'
        }
        
        # Add content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        targeted_context['content_hash'] = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Save targeted context
        cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(targeted_context, f, default_flow_style=False, sort_keys=False)
            
    except Exception as e:
        raise Exception(f"Failed to generate targeted context for {doc_id}: {e}")

def _generate_lightweight_discovery_context(doc_id, doc_file, doc_type):
    """Generate lightweight discovery context for ADR, EXEC, and UX documents"""
    import yaml
    import hashlib
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Extract basic info from document
        batch_kwargs = _extract_batch_kwargs_from_doc(doc_file)
        
        # Create lightweight context based on document type
        if doc_type == "adr":
            # ADR-focused lightweight analysis
            analysis_data = _analyze_adr_context(doc_file)
        elif doc_type == "exec":
            # Execution-focused lightweight analysis
            analysis_data = _analyze_execution_context(doc_file)
        elif doc_type == "ux":
            # UX-focused lightweight analysis
            analysis_data = _analyze_ux_context(doc_file)
        else:
            # Fallback to basic analysis
            analysis_data = {}
        
        # Create lightweight context
        lightweight_context = {
            'doc_id': doc_id,
            'doc_type': doc_type,
            'title': batch_kwargs.get('product', 'Unknown'),
            'description': batch_kwargs.get('idea', ''),
            'analysis_data': analysis_data,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'discovery_tier': 'lightweight'
        }
        
        # Add content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        lightweight_context['content_hash'] = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Save lightweight context
        cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(lightweight_context, f, default_flow_style=False, sort_keys=False)
            
    except Exception as e:
        raise Exception(f"Failed to generate lightweight context for {doc_id}: {e}")

def _analyze_architecture_context(target, doc_file):
    """Analyze architecture-specific context"""
    try:
        from discovery.engine import DiscoveryEngine
        engine = DiscoveryEngine(question_set="comprehensive")
        
        # Run architecture-focused analysis
        analysis_data = engine.analyzer.analyze(Path(target), {})
        
        # Focus on architectural patterns and system structure
        arch_analysis = {
            'system_structure': analysis_data.get('detected', {}),
            'architectural_patterns': _detect_architectural_patterns(target),
            'component_analysis': _analyze_components(target),
            'dependencies': analysis_data.get('dependencies', {}),
            'tech_stack': analysis_data.get('detected', {}).get('languages', [])
        }
        
        return arch_analysis
        
    except Exception:
        return {'error': 'Failed to analyze architecture context'}

def _analyze_implementation_context(target, doc_file):
    """Analyze implementation-specific context"""
    try:
        from discovery.engine import DiscoveryEngine
        engine = DiscoveryEngine(question_set="comprehensive")
        
        # Run implementation-focused analysis
        analysis_data = engine.analyzer.analyze(Path(target), {})
        
        # Focus on implementation details and code quality
        impl_analysis = {
            'code_structure': analysis_data.get('detected', {}),
            'implementation_patterns': _detect_implementation_patterns(target),
            'code_quality': _analyze_code_quality(target),
            'dependencies': analysis_data.get('dependencies', {}),
            'tech_stack': analysis_data.get('detected', {}).get('languages', [])
        }
        
        return impl_analysis
        
    except Exception:
        return {'error': 'Failed to analyze implementation context'}

def _analyze_adr_context(doc_file):
    """Analyze ADR-specific context"""
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract ADR-specific information
        import re
        
        adr_analysis = {
            'decision_rationale': _extract_section(content, '## Decision'),
            'alternatives': _extract_section(content, '## Alternatives'),
            'consequences': _extract_section(content, '## Consequences'),
            'status': _extract_status(content),
            'related_decisions': _extract_related_decisions(content)
        }
        
        return adr_analysis
        
    except Exception:
        return {'error': 'Failed to analyze ADR context'}

def _analyze_execution_context(doc_file):
    """Analyze execution-specific context"""
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract execution-specific information
        exec_analysis = {
            'milestones': _extract_section(content, '## Milestones'),
            'timeline': _extract_section(content, '## Timeline'),
            'resources': _extract_section(content, '## Resources'),
            'risks': _extract_section(content, '## Risks'),
            'dependencies': _extract_section(content, '## Dependencies')
        }
        
        return exec_analysis
        
    except Exception:
        return {'error': 'Failed to analyze execution context'}

def _analyze_ux_context(doc_file):
    """Analyze UX-specific context"""
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract UX-specific information
        ux_analysis = {
            'user_personas': _extract_section(content, '## User Personas'),
            'user_flows': _extract_section(content, '## User Flows'),
            'wireframes': _extract_section(content, '## Wireframes'),
            'accessibility': _extract_section(content, '## Accessibility'),
            'usability_goals': _extract_section(content, '## Usability Goals')
        }
        
        return ux_analysis
        
    except Exception:
        return {'error': 'Failed to analyze UX context'}

def _extract_section(content, section_header):
    """Extract content from a specific section"""
    import re
    pattern = f"{re.escape(section_header)}\\s*\\n\\s*(.+?)(?=\\n##|\\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def _extract_status(content):
    """Extract status from document content"""
    import re
    status_match = re.search(r'status[:\s]+(.+)', content, re.IGNORECASE)
    return status_match.group(1).strip() if status_match else "draft"

def _extract_related_decisions(content):
    """Extract related decisions from ADR content"""
    import re
    related_match = re.search(r'related[:\s]+(.+)', content, re.IGNORECASE)
    if related_match:
        return [d.strip() for d in related_match.group(1).split(',')]
    return []

def _detect_architectural_patterns(target):
    """Detect architectural patterns in the codebase"""
    # Placeholder for architectural pattern detection
    return {
        'patterns': ['MVC', 'Microservices'],
        'layers': ['Presentation', 'Business', 'Data'],
        'communication': ['REST', 'GraphQL']
    }

def _analyze_components(target):
    """Analyze system components"""
    # Placeholder for component analysis
    return {
        'components': ['API', 'Database', 'Frontend'],
        'interfaces': ['REST API', 'Database Schema'],
        'dependencies': ['External APIs', 'Third-party Libraries']
    }

def _detect_implementation_patterns(target):
    """Detect implementation patterns in the codebase"""
    # Placeholder for implementation pattern detection
    return {
        'patterns': ['Repository', 'Factory', 'Observer'],
        'design_principles': ['SOLID', 'DRY', 'KISS'],
        'code_organization': ['Modular', 'Layered']
    }

def _analyze_code_quality(target):
    """Analyze code quality metrics"""
    # Placeholder for code quality analysis
    return {
        'complexity': 'Medium',
        'test_coverage': '80%',
        'documentation': 'Good',
        'maintainability': 'High'
    }

def _refresh_targeted_context(doc_id, doc_file, doc_type, pack):
    """Refresh targeted discovery context for ARCH and IMPL documents"""
    import yaml
    import hashlib
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Load existing cache file
        cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
        if not cache_file.exists():
            return
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = yaml.safe_load(f)
        
        # Refresh analysis data based on document type
        if doc_type == "arch":
            analysis_data = _analyze_architecture_context(cache_data.get('target_path', '.'), doc_file)
        elif doc_type == "impl":
            analysis_data = _analyze_implementation_context(cache_data.get('target_path', '.'), doc_file)
        else:
            analysis_data = cache_data.get('analysis_data', {})
        
        # Update cache data
        cache_data['analysis_data'] = analysis_data
        cache_data['last_refreshed'] = datetime.now().isoformat()
        
        # Update content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        cache_data['content_hash'] = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Save updated cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(cache_data, f, default_flow_style=False, sort_keys=False)
        
        # Optional: Generate context pack
        if pack:
            try:
                from discovery.engine import DiscoveryEngine
                engine = DiscoveryEngine(question_set="comprehensive")
                engine._try_auto_ctx_build(Path(cache_data.get('target_path', '.')))
            except Exception:
                pass  # Silently fail for pack generation
                
    except Exception as e:
        raise Exception(f"Failed to refresh targeted context for {doc_id}: {e}")

def _refresh_lightweight_context(doc_id, doc_file, doc_type):
    """Refresh lightweight discovery context for ADR, EXEC, and UX documents"""
    import yaml
    import hashlib
    from pathlib import Path
    from datetime import datetime
    
    try:
        # Load existing cache file
        cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
        if not cache_file.exists():
            return
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = yaml.safe_load(f)
        
        # Refresh analysis data based on document type
        if doc_type == "adr":
            analysis_data = _analyze_adr_context(doc_file)
        elif doc_type == "exec":
            analysis_data = _analyze_execution_context(doc_file)
        elif doc_type == "ux":
            analysis_data = _analyze_ux_context(doc_file)
        else:
            analysis_data = cache_data.get('analysis_data', {})
        
        # Update cache data
        cache_data['analysis_data'] = analysis_data
        cache_data['last_refreshed'] = datetime.now().isoformat()
        
        # Update content hash
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        cache_data['content_hash'] = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Save updated cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(cache_data, f, default_flow_style=False, sort_keys=False)
                
    except Exception as e:
        raise Exception(f"Failed to refresh lightweight context for {doc_id}: {e}")

@click.group()
def cli():
    """Code Builder CLI"""

# -------------------- ADR --------------------
@cli.command("adr:new")
@click.option("--title", required=True)
@click.option("--parent", default="ADR-0000")
@click.option("--related", multiple=True)
@click.option("--tags", default="")
def adr_new(title, parent, related, tags):
    os.makedirs(ADRS, exist_ok=True)
    
    # Generate standardized ADR ID: ADR-YYYY-MM-DD-slug
    from datetime import datetime
    
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
    with open(out_path, "w", encoding="utf-8") as f: f.write(out)
    
    # Update master ADR file with duplicate prevention
    _update_master_file('adr', next_id, title, "proposed", "")
    
    click.echo(f"Created {out_path}")

# -------------------- RULES LOADER --------------------
def _load_rules(feature, stacks):
    from context_rules import merge_context_rules
    return merge_context_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])

# -------------------- DOCUMENT HELPERS --------------------
import re, yaml
from pathlib import Path

def _doc_load_front_matter(path):
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
    new = '---\n' + yaml.safe_dump(front, sort_keys=False).strip() + '\n---\n' + txt[m.end():]
    Path(path).write_text(new, encoding="utf-8")

# -------------------- PLAN --------------------
@cli.command("plan:sync")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def plan_sync(feature, stacks):
    os.makedirs(CACHE, exist_ok=True)
    rules = _load_rules(feature, stacks)
    ctx = {
        "trace": {"prd":"PRD#TBD","arch":"ARCH#TBD","ux":"UX#TBD","integration":"INT#TBD","adrs":[]},
        "acceptance": ["compiles","tests pass"],
        "goal": "Scaffolded by plan:sync",
        "name": "Scaffold",
        "feature": feature,
        "rules": rules
    }
    with open(os.path.join(CACHE,"context.json"),"w",encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)
    click.echo("Wrote builder/cache/context.json")

@cli.command("plan:auto")
@click.argument("path", default="src")
@click.option("--stacks", default="typescript,react")
def plan_auto(path, stacks):
    """Infer feature from builder/feature_map.json for PATH and build context."""
    fmap = {}
    try:
        fmap = json.loads(PPath("builder/feature_map.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    feature = ""
    for pattern, val in (fmap or {}).items():
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatchcase(path, pattern):
            feature = val
            break
    
    click.echo(f"🔍 Detected feature: '{feature or 'none'}' for path: {path}")
    
    # Call ctx:build-enhanced after feature detection
    try:
        click.echo("🔧 Building enhanced context package...")
        
        # Import the enhanced context building modules
        from context_graph import ContextGraphBuilder
        from context_select import ContextSelector
        from context_budget import ContextBudgetManager
        
        # 1. Build context graph
        graph_builder = ContextGraphBuilder(ROOT)
        graph = graph_builder.build()
        
        # 2. Select context using graph
        selector = ContextSelector(ROOT)
        context_selection = selector.select_context(path, feature, top_k=10)
        
        if not context_selection:
            click.echo("❌ No context found for target path")
            return
        
        # 3. Apply budget constraints
        budget_manager = ContextBudgetManager(total_budget=8000)
        budget_items = budget_manager.create_budget_items(context_selection)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # 4. Load rules
        rules = _load_rules(feature, stacks)
        
        # 5. Build enhanced context package
        context_package = _build_enhanced_context_package(
            path, 'implement', feature, stacks, 8000,
            selected_items, overflow_items, budget_summary, rules
        )
        
        # 6. Write pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        with open(pack_context_path, "w", encoding="utf-8") as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Created {pack_context_path}")
        
        # 7. Generate enhanced context.md
        context_md = _generate_enhanced_context_md(context_package)
        context_md_path = os.path.join(CACHE, "context.md")
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)
        click.echo(f"✅ Created {context_md_path}")
        
        # 8. Generate 1-line summary with counts per type and budget
        _show_plan_auto_summary(context_package, budget_summary, 8000)
        
    except Exception as e:
        click.echo(f"❌ Error building enhanced context: {e}")
        # Fallback to basic context.json for backward compatibility
        os.makedirs(CACHE, exist_ok=True)
        rules = _load_rules(feature, stacks)
        ctx = {
            "trace": {"prd":"PRD#TBD","arch":"ARCH#TBD","ux":"UX#TBD","integration":"INT#TBD","adrs":[]},
            "acceptance": ["compiles","tests pass"],
            "goal": "Scaffolded by plan:auto",
            "name": "Scaffold",
            "feature": feature,
            "rules": rules
        }
        with open(os.path.join(CACHE,"context.json"),"w",encoding="utf-8") as f:
            json.dump(ctx, f, indent=2)
        click.echo(f"⚠️  Fallback: wrote builder/cache/context.json only")

# -------------------- ABC ITERATION --------------------
def _abc_params(base_t=0.6, base_p=0.9, round_idx=0, variant="A"):
    adj = 0.0 if variant=="A" else (0.1 if variant=="B" else -0.1)
    scale = max(0.05, 0.1 - round_idx*0.015)
    return round(base_t*(1+adj*scale/0.1),2), round(base_p*(1+adj*scale/0.1),2)

@cli.command("iter:run")
@click.argument("target_path")
@click.option("--rounds", default=3)
def iter_run(target_path, rounds):
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    history = []
    base_t, base_p = 0.6, 0.9
    best = {"score": -1, "content": "", "params": (base_t, base_p)}
    for r in range(rounds):
        variants = {}
        for v in ["A","B","C"]:
            t,p = _abc_params(base_t, base_p, r, v)
            content = f"// gen variant {v} @T={t} P={p}\nexport const hello = ()=>'hi';\n"
            score = len(content) - (1 if v!='A' else 0)
            variants[v] = {"content": content, "score": score, "params": (t,p)}
        winner = max(variants.values(), key=lambda x: x["score"])
        base_t, base_p = winner["params"]
        best = winner
        history.append({"round": r+1, "winner": {"T":base_t,"P":base_p}, "score": winner["score"]})
    with open(target_path, "w", encoding="utf-8") as f: f.write(best["content"])
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, "iter_history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    click.echo(f"Finalized {target_path} with ABC loop ({rounds} rounds)")

# -------------------- RULES --------------------
@cli.command("rules:show")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def rules_show(feature, stacks):
    rules = _load_rules(feature, stacks)
    click.echo("===== MERGED RULES =====\n")
    click.echo(rules.get("rules_markdown") or "(none)")
    click.echo("\n===== GUARDRAILS =====\n")
    click.echo(json.dumps(rules.get("guardrails", {}), indent=2))

@cli.command("rules:check")
@click.argument("path")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def rules_check(path, feature, stacks):
    rules = _load_rules(feature, stacks)
    guardrails = rules.get("guardrails", {})
    patterns = guardrails.get("forbiddenPatterns", [])
    paths = glob.glob(path, recursive=True)
    failed = False
    for p in paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            for pr in patterns:
                pat = pr.get("pattern")
                msg = pr.get("message", "Forbidden pattern")
                if pat and re.search(pat, txt):
                    click.echo(f"FAIL {p}: {msg} ({pat})")
                    failed = True
    if failed:
        raise SystemExit(2)
    click.echo("Guardrails OK")

# -------------------- EVALUATION --------------------
@cli.command("eval:objective")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_objective(path, server):
    """Run objective evaluation on an artifact"""
    if server:
        # Start server mode
        import sys
        import importlib.util
        
        # Add scripts directory to path
        scripts_path = os.path.join(ROOT, "builder", "scripts")
        if scripts_path not in sys.path:
            sys.path.append(scripts_path)
        
        # Import cursor_server module
        cursor_server_path = os.path.join(scripts_path, "cursor_server.py")
        spec = importlib.util.spec_from_file_location("cursor_server", cursor_server_path)
        cursor_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cursor_server)
        
        create_evaluation = cursor_server.create_evaluation
        start_server = cursor_server.start_server
        
        click.echo("🚀 Starting Cursor Bridge Server...")
        click.echo("📝 Creating evaluation...")
        
        eval_id = create_evaluation(path, "single")
        
        click.echo(f"✅ Evaluation created: {eval_id}")
        click.echo(f"🔗 Prompt URL: http://127.0.0.1:5000/prompt/{eval_id}")
        click.echo(f"📋 Copy this URL to Cursor Chat or Composer")
        click.echo(f"⏳ Waiting for Cursor response...")
        
        # Start server in background thread
        import threading
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for completion with timeout
        import time
        max_wait_time = 300  # 5 minutes timeout
        start_time = time.time()
        
        click.echo(f"⏳ Waiting for Cursor response (timeout: {max_wait_time}s)...")
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check server status with timeout
                response = requests.get(f"http://127.0.0.1:5000/", timeout=5)
                if response.status_code == 200:
                    # Check if our evaluation is complete by looking for the eval_id in completed evaluations
                    if f'completed_at' in response.text and eval_id in response.text:
                        click.echo("✅ Evaluation completed!")
                        return
                
                # Check if evaluation file exists and has completion timestamp
                eval_file = os.path.join(ROOT, "builder", "cache", "evaluations", f"{eval_id}.json")
                if os.path.exists(eval_file):
                    with open(eval_file, 'r') as f:
                        eval_data = json.load(f)
                        if eval_data.get('completed_at'):
                            click.echo("✅ Evaluation completed!")
                            return
                            
            except requests.exceptions.RequestException as e:
                click.echo(f"⚠️  Server check failed: {e}")
            except Exception as e:
                click.echo(f"⚠️  Error checking completion: {e}")
            
            time.sleep(2)  # Check every 2 seconds
        
        click.echo(f"⏰ Timeout reached ({max_wait_time}s). Evaluation may still be in progress.")
        click.echo(f"🔗 You can check status at: http://127.0.0.1:5000/")
        click.echo(f"📝 Evaluation ID: {eval_id}")
        return
    
    # Regular mode (existing logic)
    try:
        # Import evaluators
        import sys
        sys.path.append(os.path.join(ROOT, "builder"))
        from evaluators.objective import evaluate_code, evaluate_doc
        from evaluators.artifact_detector import detect_artifact_type
        
        # Detect artifact type
        artifact_type = detect_artifact_type(path)
        click.echo(f"Detected artifact type: {artifact_type}")
        
        # Run reports:all to generate JSON reports
        click.echo("Running reports:all...")
        result = subprocess.run(
            ["pnpm", "run", "reports:all"], 
            cwd=ROOT, 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Warning: reports:all failed: {result.stderr}")
        
        # Run objective evaluation
        if artifact_type == 'code':
            scores = evaluate_code(path)
        else:
            scores = evaluate_doc(path, artifact_type)
        
        # Print scores
        click.echo("Objective Scores:")
        click.echo(json.dumps(scores, indent=2))
        
        # Save to cache
        os.makedirs(CACHE, exist_ok=True)
        output_path = os.path.join(CACHE, "last_objective.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "artifact_path": path,
                "artifact_type": artifact_type,
                "scores": scores,
                "timestamp": datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        click.echo(f"Saved to {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("eval:prepare")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_prepare(path, server):
    """Prepare evaluation prompt for Cursor"""
    if server:
        # Use server mode (same as eval:objective --server)
        eval_objective(path, True)
        return
    
    # Regular mode (existing logic)
    try:
        # Run objective evaluation first
        click.echo("Running objective evaluation...")
        result = subprocess.run(
            ["python", os.path.join(ROOT, "builder", "cli.py"), "eval:objective", path],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Warning: objective evaluation failed: {result.stderr}")
        
        # Import prompt builder
        import sys
        sys.path.append(os.path.join(ROOT, "builder"))
        from prompts.evaluation_prompt import build_single_eval_prompt
        from evaluators.artifact_detector import detect_artifact_type
        
        # Generate prompt
        artifact_type = detect_artifact_type(path)
        prompt = build_single_eval_prompt(path, artifact_type)
        
        # Save prompt
        os.makedirs(CACHE, exist_ok=True)
        prompt_path = os.path.join(CACHE, "cursor_prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        click.echo("Copy builder/cache/cursor_prompt.md to Cursor")
        click.echo(f"Prompt saved to {prompt_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("eval:complete")
@click.argument("path")
@click.option("--cursor-response", required=True, help="Path to Cursor's JSON response")
def eval_complete(path, cursor_response):
    """Complete evaluation by blending objective and subjective scores"""
    try:
        # Load objective scores
        objective_path = os.path.join(CACHE, "last_objective.json")
        if not os.path.exists(objective_path):
            click.echo("Error: No objective scores found. Run eval:objective first.")
            raise SystemExit(1)
        
        with open(objective_path, "r", encoding="utf-8") as f:
            objective_data = json.load(f)
        
        # Load Cursor response
        if not os.path.exists(cursor_response):
            click.echo(f"Error: Cursor response file not found: {cursor_response}")
            raise SystemExit(1)
        
        with open(cursor_response, "r", encoding="utf-8") as f:
            cursor_data = json.load(f)
        
        # Load config for weights
        config_path = os.path.join(ROOT, "docs", "eval", "config.yaml")
        import yaml
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception:
            config = {}
        
        artifact_type = objective_data.get("artifact_type", "code")
        artifact_weights = config.get("artifact_weights", {}).get(artifact_type, {"objective": 0.7, "subjective": 0.3})
        
        # Blend scores
        objective_scores = objective_data.get("scores", {})
        subjective_scores = cursor_data.get("dimensions", {})
        
        # Calculate blended scores
        blended_scores = {}
        for dimension in subjective_scores.keys():
            if dimension in objective_scores:
                obj_score = objective_scores[dimension]
                subj_score = subjective_scores[dimension]
                blended = (obj_score * artifact_weights["objective"] + 
                          subj_score * artifact_weights["subjective"])
                blended_scores[dimension] = blended
            else:
                blended_scores[dimension] = subjective_scores[dimension]
        
        # Calculate overall blended score
        overall_blended = (objective_scores.get("overall", 50) * artifact_weights["objective"] + 
                          cursor_data.get("overall_score", 50) * artifact_weights["subjective"])
        
        # Create final evaluation
        final_eval = {
            "artifact_path": path,
            "artifact_type": artifact_type,
            "objective_scores": objective_scores,
            "subjective_scores": subjective_scores,
            "blended_scores": blended_scores,
            "overall_score": overall_blended,
            "weights": artifact_weights,
            "cursor_reasoning": cursor_data.get("reasoning", ""),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save final evaluation
        os.makedirs(CACHE, exist_ok=True)
        final_path = os.path.join(CACHE, "final_eval.json")
        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(final_eval, f, indent=2)
        
        # Print results
        click.echo("Final Evaluation Results:")
        click.echo(f"Overall Score: {overall_blended:.1f}")
        click.echo(f"Objective: {objective_scores.get('overall', 0):.1f} (weight: {artifact_weights['objective']})")
        click.echo(f"Subjective: {cursor_data.get('overall_score', 0):.1f} (weight: {artifact_weights['subjective']})")
        click.echo(f"Saved to {final_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

# -------------------- ABC ITERATION --------------------
def generate_variants(target_path: str) -> Dict[str, str]:
    """Generate A/B/C variants of a file (simple generator)"""
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Simple variant generation - add comments/annotations
        variants = {
            "A": original_content,  # Original
            "B": f"// Variant B: Enhanced version\n{original_content}",
            "C": f"// Variant C: Alternative approach\n{original_content.replace('export const', 'export function')}"
        }
        
        # Save variants to cache
        os.makedirs(CACHE, exist_ok=True)
        variant_paths = {}
        for name, content in variants.items():
            variant_path = os.path.join(CACHE, f"variant_{name}.ts")
            with open(variant_path, 'w', encoding='utf-8') as f:
                f.write(content)
            variant_paths[name] = variant_path
        
        return variant_paths
    except Exception as e:
        click.echo(f"Error generating variants: {e}")
        raise SystemExit(1)

@cli.command("iter:cursor")
@click.argument("target_path")
@click.option("--rounds", default=1, help="Number of ABC rounds")
def iter_cursor(target_path, rounds):
    """Run ABC iteration with Cursor evaluation"""
    try:
        # Generate variants
        click.echo("Generating A/B/C variants...")
        variant_paths = generate_variants(target_path)
        
        # Run objective evaluation on each variant
        click.echo("Running objective evaluation on variants...")
        import sys
        sys.path.append(os.path.join(ROOT, "builder"))
        from evaluators.objective import evaluate_code, evaluate_doc
        from evaluators.artifact_detector import detect_artifact_type
        
        artifact_type = detect_artifact_type(target_path)
        objective_scores = {}
        
        for name, path in variant_paths.items():
            click.echo(f"Evaluating variant {name}...")
            if artifact_type == 'code':
                scores = evaluate_code(path)
            else:
                scores = evaluate_doc(path, artifact_type)
            objective_scores[name] = scores
        
        # Build ABC comparison prompt
        click.echo("Building ABC comparison prompt...")
        from prompts.evaluation_prompt import build_abc_eval_prompt
        
        prompt = build_abc_eval_prompt(variant_paths, objective_scores)
        
        # Save prompt
        prompt_path = os.path.join(CACHE, "abc_prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        # Print instructions
        click.echo("\n" + "="*60)
        click.echo("ABC ITERATION READY")
        click.echo("="*60)
        click.echo(f"1. Copy {prompt_path} to Cursor")
        click.echo("2. Get Cursor's evaluation (JSON format)")
        click.echo("3. Run: python builder/cli.py iter:finish {target_path} --winner A|B|C --scores-file <cursor_response.json>")
        click.echo("\nObjective Scores:")
        for name, scores in objective_scores.items():
            click.echo(f"  {name}: {scores.get('overall', 0):.1f}")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("iter:finish")
@click.argument("target_path")
@click.option("--winner", required=True, type=click.Choice(['A', 'B', 'C']), help="Winner variant")
@click.option("--scores-file", help="Path to Cursor evaluation JSON")
def iter_finish(target_path, winner, scores_file):
    """Complete ABC iteration by selecting winner"""
    try:
        # Load winner variant
        winner_path = os.path.join(CACHE, f"variant_{winner}.ts")
        if not os.path.exists(winner_path):
            click.echo(f"Error: Winner variant {winner} not found. Run iter:cursor first.")
            raise SystemExit(1)
        
        with open(winner_path, 'r', encoding='utf-8') as f:
            winner_content = f.read()
        
        # Write winner to target path
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(winner_content)
        
        click.echo(f"Winner variant {winner} written to {target_path}")
        
        # Load objective scores for all variants
        objective_scores = {}
        for variant in ['A', 'B', 'C']:
            variant_path = os.path.join(CACHE, f"variant_{variant}.ts")
            if os.path.exists(variant_path):
                # Re-run evaluation to get fresh scores
                import sys
                sys.path.append(os.path.join(ROOT, "builder"))
                from evaluators.objective import evaluate_code, evaluate_doc
                from evaluators.artifact_detector import detect_artifact_type
                
                artifact_type = detect_artifact_type(target_path)
                if artifact_type == 'code':
                    scores = evaluate_code(variant_path)
                else:
                    scores = evaluate_doc(variant_path, artifact_type)
                objective_scores[variant] = scores
        
        # Load Cursor evaluation if provided
        cursor_evaluation = None
        if scores_file and os.path.exists(scores_file):
            with open(scores_file, 'r', encoding='utf-8') as f:
                cursor_evaluation = json.load(f)
        
        # Create iteration record
        iteration_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "target_path": target_path,
            "winner": winner,
            "objective_scores": objective_scores,
            "cursor_evaluation": cursor_evaluation,
            "round": 1  # Could be enhanced to track multiple rounds
        }
        
        # Append to iteration history
        history_path = os.path.join(CACHE, "iter_history.json")
        history = []
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append(iteration_record)
        
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        
        # Print summary
        click.echo("\n" + "="*60)
        click.echo("ABC ITERATION COMPLETE")
        click.echo("="*60)
        click.echo(f"Winner: {winner}")
        click.echo(f"Target: {target_path}")
        click.echo(f"History: {history_path}")
        
        click.echo("\nObjective Scores Summary:")
        for variant, scores in objective_scores.items():
            marker = " ← WINNER" if variant == winner else ""
            click.echo(f"  {variant}: {scores.get('overall', 0):.1f}{marker}")
        
        if cursor_evaluation:
            click.echo(f"\nCursor Evaluation: {cursor_evaluation.get('winner', 'N/A')}")
            click.echo(f"Confidence: {cursor_evaluation.get('confidence', 'N/A')}")
        
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

# -------------------- DOC FACTORY --------------------
@cli.command("doc:new")
@click.argument("dtype", type=click.Choice(['prd', 'arch', 'integrations', 'ux', 'impl', 'exec', 'tasks']))
@click.option("--title", required=True, help="Document title")
@click.option("--owner", default="", help="Document owner")
@click.option("--links", multiple=True, help="Links to other documents (format: type:id)")
@click.option("--prd", default="", help="Link to PRD document")
@click.option("--arch", default="", help="Link to Architecture document")
@click.option("--adr", default="", help="Link to ADR document")
@click.option("--impl", default="", help="Link to Implementation document")
@click.option("--exec", "exec_", default="", help="Link to Execution document")
@click.option("--ux", default="", help="Link to UX document")
def doc_new(dtype, title, owner, links, prd, arch, adr, impl, exec_, ux):
    """Create a new document from template"""
    # Validate required title
    if not title or not title.strip():
        click.echo("Error: --title is required and cannot be empty")
        raise SystemExit(1)
    
    # Generate slug and ID using standardized format: TYPE-YYYY-MM-DD-slug
    from datetime import datetime
    
    # Create slug from title
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:20]  # Limit slug length
    
    # Generate date string
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    # Create standardized ID
    doc_id = f"{dtype.upper()}-{date_str}-{slug}"
    
    # Set default owner if not provided
    if not owner:
        owner = "TBD"
    
    # Parse links from --links option
    parsed_links = {}
    for link in links:
        if ':' in link:
            link_type, link_id = link.split(':', 1)
            if link_type not in parsed_links:
                parsed_links[link_type] = []
            parsed_links[link_type].append(link_id)
    
    # Add individual link flags
    individual_links = {
        'prd': prd,
        'arch': arch,
        'adr': adr,
        'impl': impl,
        'exec': exec_,
        'ux': ux
    }
    
    for link_type, link_id in individual_links.items():
        if link_id and link_id.strip():
            # For individual flags, we want to set the link directly, not as an array
            parsed_links[link_type] = link_id.strip()
    
    # Create context for template rendering
    ctx = {
        "id": doc_id,
        "title": title,
        "owner": owner,
        "created": _today(),
        "links": parsed_links
    }
    
    # Determine output directory and file path
    doc_dir = os.path.join(DOCS, dtype)
    os.makedirs(doc_dir, exist_ok=True)
    
    # Load and render template
    template_path = os.path.join(TEMPL, f"{dtype}.md.hbs")
    if not os.path.exists(template_path):
        click.echo(f"Error: Template {template_path} not found")
        raise SystemExit(1)
    
    try:
        content = _render(template_path, ctx)
    except Exception as e:
        click.echo(f"Error rendering template: {e}")
        raise SystemExit(1)
    
    # Write the document
    output_path = os.path.join(doc_dir, f"{doc_id}.md")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"Created {output_path}")
        
        # Update master file
        _update_master_file(dtype, doc_id, title, "draft", "")
        
    except Exception as e:
        click.echo(f"Error writing file: {e}")
        raise SystemExit(1)

@cli.command("doc:index")
@click.option("--no-warn", is_flag=True, help="Disable warnings about missing link targets")
def doc_index(no_warn):
    """Generate documentation index in docs/README.md"""
    import yaml
    from collections import defaultdict
    
    # Document type configurations
    doc_types = {
        'prd': {'name': 'Product Requirements', 'icon': '📋', 'description': 'Product requirements and specifications'},
        'arch': {'name': 'Architecture', 'icon': '🏗️', 'description': 'Architectural decisions and designs'},
        'integrations': {'name': 'Integrations', 'icon': '🔗', 'description': 'Integration specifications and APIs'},
        'ux': {'name': 'User Experience', 'icon': '🎨', 'description': 'UX designs and user research'},
        'impl': {'name': 'Implementation', 'icon': '⚙️', 'description': 'Implementation details and technical specs'},
        'exec': {'name': 'Executive', 'icon': '📊', 'description': 'Executive summaries and business documents'},
        'tasks': {'name': 'Tasks', 'icon': '✅', 'description': 'Task definitions and work items'}
    }
    
    # Scan for documents
    documents = defaultdict(list)
    all_doc_ids = set()
    warnings = []
    
    for doc_type in doc_types.keys():
        doc_dir = os.path.join(DOCS, doc_type)
        if os.path.exists(doc_dir):
            for filename in os.listdir(doc_dir):
                if filename.endswith('.md') and not filename.startswith('.'):
                    filepath = os.path.join(doc_dir, filename)
                    doc_id = filename.replace('.md', '')
                    all_doc_ids.add(doc_id)
                    
                    # Try to parse front-matter for metadata
                    metadata = {}
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith('---'):
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    yaml_content = parts[1].strip()
                                    metadata = yaml.safe_load(yaml_content) or {}
                    except Exception as e:
                        if not no_warn:
                            warnings.append(f"⚠️  Could not parse front-matter for {filepath}: {e}")
                    
                    # Ensure links is always a dict
                    links = metadata.get('links', {})
                    if isinstance(links, list):
                        # Convert list of dicts to single dict
                        parsed_links = {}
                        for link_item in links:
                            if isinstance(link_item, dict):
                                parsed_links.update(link_item)
                        links = parsed_links
                    
                    documents[doc_type].append({
                        'id': doc_id,
                        'filename': filename,
                        'path': filepath,
                        'title': metadata.get('title', doc_id),
                        'status': metadata.get('status', 'unknown'),
                        'owner': metadata.get('owner', 'TBD'),
                        'created': metadata.get('created', 'unknown'),
                        'links': links
                    })
    
    # Check for missing link targets
    if not no_warn:
        for doc_type, docs in documents.items():
            for doc in docs:
                links = doc['links']
                if isinstance(links, dict):
                    for link_type, link_ids in links.items():
                        if isinstance(link_ids, list):
                            for link_id in link_ids:
                                if link_id not in all_doc_ids:
                                    warnings.append(f"⚠️  {doc['id']} links to missing {link_type}:{link_id}")
    
    # Generate README content
    readme_content = """# Documentation Layer

This repo uses docs to drive codegen, decisions, and evaluation.

---

## Document Index

"""
    
    # Add document sections
    for doc_type, config in doc_types.items():
        docs = documents[doc_type]
        if docs:
            readme_content += f"### {config['icon']} {config['name']}\n"
            readme_content += f"*{config['description']}*\n\n"
            
            for doc in sorted(docs, key=lambda x: x['created'], reverse=True):
                status_emoji = {
                    'draft': '📝',
                    'review': '👀', 
                    'approved': '✅',
                    'archived': '📦',
                    'unknown': '❓'
                }.get(doc['status'], '❓')
                
                readme_content += f"- {status_emoji} **{doc['title']}** (`{doc['id']}`)\n"
                readme_content += f"  - Owner: {doc['owner']} | Created: {doc['created']}\n"
                
                # Show links if any
                has_links = any(links for links in doc['links'].values() if links)
                if has_links:
                    readme_content += "  - Links: "
                    link_parts = []
                    for link_type, link_ids in doc['links'].items():
                        if link_ids:
                            link_parts.append(f"{link_type}:{', '.join(link_ids)}")
                    readme_content += " | ".join(link_parts) + "\n"
                
                readme_content += "\n"
        else:
            readme_content += f"### {config['icon']} {config['name']}\n"
            readme_content += f"*{config['description']}*\n"
            readme_content += f"*No documents found*\n\n"
    
    # Add existing sections
    readme_content += """---

## ADRs (docs/adrs/)
- `0000_MASTER_ADR.md` = index of all decisions
- Sub ADRs like `ADR-0001.md` created by `builder:adr:new`
- Each ADR records context, decision, consequences, alternatives

---

## Templates (docs/templates/)
- Jinja2 templates for ADRs and specs
- Used by CLI to render files

---

## Rules (docs/rules/)
- `00-global.md`, `10-project.md` = global + project-wide rules
- `stack/` (e.g. typescript, react, http-client)
- `feature/` (auth, content-engine, etc.)
- `guardrails.json` = forbidden patterns + hints

---

## Evaluation (docs/eval/)
- `config.yaml` = evaluation weights and configuration
- Defines objective vs subjective weight distribution
- Configures tool paths and scoring weights

---

## Usage Guides
- `USAGE-Cursor-Evaluation.md` = Complete evaluation workflow guide
- `CURSOR-Custom-Commands.md` = Cursor integration setup

---

## Usage
- When editing a file, run `plan:auto <file>` → context.json merges rules + ADRs  
- Cursor/AI gets that context and generates compliant code
- Run `eval:objective <file>` → measure code quality objectively
- Use `--server` flag for interactive Cursor evaluation
- Use `doc:new <type> --title "Title"` → create new documents
- Use `doc:index` → update this index
"""
    
    # Write the README
    readme_path = os.path.join(DOCS, "README.md")
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        click.echo(f"✅ Updated {readme_path}")
    except Exception as e:
        click.echo(f"Error writing README: {e}")
        raise SystemExit(1)
    
    # Show warnings if any
    if warnings:
        click.echo("\n⚠️  Warnings:")
        for warning in warnings:
            click.echo(f"  {warning}")
        click.echo(f"\nTotal warnings: {len(warnings)}")
    else:
        click.echo("✅ No warnings found")

# -------------------- CONTEXT BUILDER --------------------
@cli.command("ctx:build")
@click.argument("target_path")
@click.option("--purpose", required=True, help="Purpose: implement, review, test, etc.")
@click.option("--feature", default="", help="Feature name for rules")
@click.option("--stacks", default="typescript,react", help="Comma-separated stack names")
@click.option("--token-limit", default=8000, help="Token budget limit")
def ctx_build(target_path, purpose, feature, stacks, token_limit):
    """Build context package for a target path"""
    import yaml
    import re
    from pathlib import Path
    
    # Ensure cache directory exists
    os.makedirs(CACHE, exist_ok=True)
    
    # Load rules
    rules = _load_rules(feature, stacks)
    
    # Find nearest PRD
    prd_content = ""
    prd_metadata = {}
    adr_contents = []
    
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
                                    yaml_content = parts[1].strip()
                                    metadata = yaml.safe_load(yaml_content) or {}
                                    if metadata.get('type') == 'prd':
                                        prd_content = content
                                        prd_metadata = metadata
                                        prd_found = True
                                        break
                    except Exception:
                        continue
        if prd_found:
            break
    
    # Extract ADR references from PRD
    if prd_content:
        # Look for ADR references in PRD content
        adr_refs = re.findall(r'ADR-\d+', prd_content)
        for adr_ref in adr_refs:
            adr_path = os.path.join(DOCS, "adrs", f"{adr_ref}.md")
            if os.path.exists(adr_path):
                try:
                    with open(adr_path, 'r', encoding='utf-8') as f:
                        adr_contents.append(f.read())
                except Exception:
                    continue
    
    # Extract code excerpts
    code_excerpts = []
    if os.path.exists(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract first 50 lines as excerpt
                lines = content.split('\n')
                excerpt = '\n'.join(lines[:50])
                if len(lines) > 50:
                    excerpt += '\n... (truncated)'
                code_excerpts.append({
                    'path': target_path,
                    'excerpt': excerpt,
                    'line_count': len(lines)
                })
        except Exception:
            pass
    
    # Look for test files
    test_excerpts = []
    test_path = target_path.replace('.ts', '.test.ts').replace('.js', '.test.js')
    if os.path.exists(test_path):
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                excerpt = '\n'.join(lines[:30])
                if len(lines) > 30:
                    excerpt += '\n... (truncated)'
                test_excerpts.append({
                    'path': test_path,
                    'excerpt': excerpt,
                    'line_count': len(lines)
                })
        except Exception:
            pass
    
    # Extract acceptance criteria from PRD
    acceptance_criteria = []
    if prd_content:
        # Look for acceptance criteria section
        lines = prd_content.split('\n')
        in_acceptance = False
        for line in lines:
            if 'acceptance criteria' in line.lower() or 'acceptance' in line.lower():
                in_acceptance = True
                continue
            if in_acceptance and line.strip().startswith('#'):
                break
            if in_acceptance and line.strip().startswith('-'):
                acceptance_criteria.append(line.strip())
    
    # Build context package
    context_package = {
        'target_path': target_path,
        'purpose': purpose,
        'feature': feature,
        'stacks': stacks.split(',') if stacks else [],
        'rules': rules,
        'prd': {
            'content': prd_content,
            'metadata': prd_metadata
        },
        'adrs': adr_contents,
        'code_excerpts': code_excerpts,
        'test_excerpts': test_excerpts,
        'acceptance_criteria': acceptance_criteria,
        'generated_at': _today()
    }
    
    # Ensure all values are JSON serializable
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj
    
    context_package = make_serializable(context_package)
    
    # Write pack_context.json
    pack_context_path = os.path.join(CACHE, "pack_context.json")
    try:
        with open(pack_context_path, "w", encoding="utf-8") as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Created {pack_context_path}")
    except Exception as e:
        click.echo(f"Error writing pack_context.json: {e}")
        raise SystemExit(1)
    
    # Generate context.md
    context_md = f"""# Context Package

**Target**: `{target_path}`  
**Purpose**: {purpose}  
**Feature**: {feature or 'None'}  
**Stacks**: {', '.join(context_package['stacks'])}  
**Generated**: {_today()}

---

## Rules

{rules.get('rules_markdown', 'No rules found')}

---

## PRD

{prd_content if prd_content else 'No PRD found'}

---

## ADRs

{chr(10).join([f"### {i+1}\n\n{adr}" for i, adr in enumerate(adr_contents)]) if adr_contents else 'No ADRs found'}

---

## Code Excerpts

{chr(10).join([f"### {excerpt['path']}\n\n```\n{excerpt['excerpt']}\n```\n" for excerpt in code_excerpts]) if code_excerpts else 'No code excerpts found'}

---

## Test Excerpts

{chr(10).join([f"### {excerpt['path']}\n\n```\n{excerpt['excerpt']}\n```\n" for excerpt in test_excerpts]) if test_excerpts else 'No test excerpts found'}

---

## Acceptance Criteria

{chr(10).join([f"- {criteria}" for criteria in acceptance_criteria]) if acceptance_criteria else 'No acceptance criteria found'}
"""
    
    # Write context.md
    context_md_path = os.path.join(CACHE, "context.md")
    try:
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)
        click.echo(f"✅ Created {context_md_path}")
    except Exception as e:
        click.echo(f"Error writing context.md: {e}")
        raise SystemExit(1)
    
    # Calculate token usage (rough estimate: 1 token ≈ 4 characters)
    def estimate_tokens(text):
        return len(text) // 4 if text else 0
    
    total_tokens = (
        estimate_tokens(rules.get('rules_markdown', '')) +
        estimate_tokens(prd_content) +
        sum(estimate_tokens(adr) for adr in adr_contents) +
        sum(estimate_tokens(excerpt['excerpt']) for excerpt in code_excerpts) +
        sum(estimate_tokens(excerpt['excerpt']) for excerpt in test_excerpts) +
        estimate_tokens('\n'.join(acceptance_criteria))
    )
    
    # Show summary
    click.echo(f"\n📦 Context Package Summary:")
    click.echo(f"  Rules: {len(rules.get('rules_markdown', '').split())} words")
    click.echo(f"  PRD: {'Found' if prd_content else 'Not found'}")
    click.echo(f"  ADRs: {len(adr_contents)}")
    click.echo(f"  Code excerpts: {len(code_excerpts)}")
    click.echo(f"  Test excerpts: {len(test_excerpts)}")
    click.echo(f"  Acceptance criteria: {len(acceptance_criteria)}")
    click.echo(f"  Estimated tokens: {total_tokens}/{token_limit}")
    
    if total_tokens > token_limit:
        click.echo(f"⚠️  Token budget exceeded! Consider reducing content or increasing --token-limit")
    elif total_tokens > token_limit * 0.8:
        click.echo(f"⚠️  Approaching token limit ({total_tokens}/{token_limit})")
    else:
        click.echo(f"✅ Token usage within budget")

# -------------------- CONTEXT BUILD HELPERS --------------------
def _build_enhanced_context_package(target_path, purpose, feature, stacks, token_limit, 
                                   selected_items, overflow_items, budget_summary, rules):
    """Build enhanced context package with all required fields"""
    
    # Group selected items by type
    items_by_type = {}
    for item in selected_items:
        item_type = item.type
        if item_type not in items_by_type:
            items_by_type[item_type] = []
        items_by_type[item_type].append(item)
    
    # Extract acceptance criteria from PRD items
    acceptance = []
    for item in items_by_type.get('acceptance', []):
        acceptance.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract decisions from ADR items
    decisions = []
    for item in items_by_type.get('adr', []):
        decisions.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract integrations
    integrations = []
    for item in items_by_type.get('integration', []):
        integrations.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract architecture items
    architecture = []
    for item in items_by_type.get('arch', []):
        architecture.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract UX items
    ux = []
    for item in items_by_type.get('ux', []):
        ux.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract code items
    code = []
    for item in items_by_type.get('code', []):
        code.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Build objective signals from existing reports
    objective_signals = _build_objective_signals()
    
    # Build provenance information
    provenance = _build_provenance(selected_items, overflow_items, budget_summary)
    
    # Build render information
    render = _build_render_info(target_path, purpose, feature, selected_items)
    
    return {
        'task': {
            'purpose': purpose,
            'target_path': target_path,
            'feature': feature
        },
        'constraints': {
            'rules_md': rules.get('rules_markdown', ''),
            'token_limit': token_limit,
            'budget_summary': budget_summary,
            'conflicts': rules.get('conflicts', []),
            'sources': rules.get('sources', [])
        },
        'acceptance': acceptance,
        'decisions': decisions,
        'integrations': integrations,
        'architecture': architecture,
        'ux': ux,
        'code': code,
        'objective_signals': objective_signals,
        'provenance': provenance,
        'render': render,
        'generated_at': _today()
    }

def _build_objective_signals():
    """Build objective signals from existing reports"""
    signals = {}
    
    # Check for existing reports
    reports = [
        'builder/cache/schema.json',
        'builder/cache/markdownlint.json',
        'builder/cache/cspell.json'
    ]
    
    for report_path in reports:
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    report_name = os.path.basename(report_path).replace('.json', '')
                    signals[report_name] = data
            except Exception:
                continue
    
    return signals

def _build_provenance(selected_items, overflow_items, budget_summary):
    """Build provenance information"""
    return {
        'selected_count': len(selected_items),
        'overflow_count': len(overflow_items),
        'budget_utilization': sum(item.token_estimate for item in selected_items),
        'budget_summary': budget_summary,
        'selection_method': 'graph_based',
        'budget_method': 'token_aware'
    }

def _build_render_info(target_path, purpose, feature, selected_items):
    """Build render information for context generation"""
    return {
        'system': f"Context builder for {target_path}",
        'instructions': f"Generate {purpose} for {target_path}",
        'user': f"Feature: {feature or 'general'}",
        'references': [item.source_anchor for item in selected_items]
    }

def _generate_enhanced_context_md(context_package):
    """Generate enhanced context.md with pretty formatting"""
    
    task = context_package['task']
    constraints = context_package['constraints']
    
    md_parts = [
        "# Context Package",
        "",
        f"**Target**: `{task['target_path']}`",
        f"**Purpose**: {task['purpose']}",
        f"**Feature**: {task['feature'] or 'None'}",
        f"**Generated**: {context_package['generated_at']}",
        "",
        "---",
        "",
        "## Task",
        "",
        f"- **Purpose**: {task['purpose']}",
        f"- **Target Path**: `{task['target_path']}`",
        f"- **Feature**: {task['feature'] or 'None'}",
        "",
        "---",
        "",
        "## Constraints",
        "",
        "### Rules",
        "",
        constraints['rules_md'] or "No rules found",
        "",
        f"**Token Budget**: {constraints['token_limit']} tokens",
        ""
    ]
    
    # Add acceptance criteria
    if context_package['acceptance']:
        md_parts.extend([
            "---",
            "",
            "## Acceptance Criteria",
            ""
        ])
        for item in context_package['acceptance']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add decisions (ADRs)
    if context_package['decisions']:
        md_parts.extend([
            "---",
            "",
            "## Decisions (ADRs)",
            ""
        ])
        for item in context_package['decisions']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add integrations
    if context_package['integrations']:
        md_parts.extend([
            "---",
            "",
            "## Integrations",
            ""
        ])
        for item in context_package['integrations']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add architecture
    if context_package['architecture']:
        md_parts.extend([
            "---",
            "",
            "## Architecture",
            ""
        ])
        for item in context_package['architecture']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add UX
    if context_package['ux']:
        md_parts.extend([
            "---",
            "",
            "## UX",
            ""
        ])
        for item in context_package['ux']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add code
    if context_package['code']:
        md_parts.extend([
            "---",
            "",
            "## Code",
            ""
        ])
        for item in context_package['code']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                "```typescript",
                item['content'],
                "```",
                ""
            ])
    
    # Add objective signals
    if context_package['objective_signals']:
        md_parts.extend([
            "---",
            "",
            "## Objective Signals",
            ""
        ])
        for signal_name, signal_data in context_package['objective_signals'].items():
            md_parts.extend([
                f"### {signal_name.title()}",
                "",
                f"```json",
                json.dumps(signal_data, indent=2),
                "```",
                ""
            ])
    
    # Add provenance
    provenance = context_package['provenance']
    md_parts.extend([
        "---",
        "",
        "## Provenance",
        "",
        f"- **Selected Items**: {provenance['selected_count']}",
        f"- **Overflow Items**: {provenance['overflow_count']}",
        f"- **Budget Utilization**: {provenance['budget_utilization']} tokens",
        f"- **Selection Method**: {provenance['selection_method']}",
        f"- **Budget Method**: {provenance['budget_method']}",
        ""
    ])
    
    return '\n'.join(md_parts)

def _show_context_summary(context_package, budget_summary, token_limit):
    """Show enhanced context summary"""
    task = context_package['task']
    provenance = context_package['provenance']
    
    click.echo(f"\n📦 Enhanced Context Package Summary:")
    click.echo(f"  Target: {task['target_path']}")
    click.echo(f"  Purpose: {task['purpose']}")
    click.echo(f"  Feature: {task['feature'] or 'None'}")
    click.echo(f"  Selected items: {provenance['selected_count']}")
    click.echo(f"  Overflow items: {provenance['overflow_count']}")
    click.echo(f"  Token usage: {provenance['budget_utilization']}/{token_limit}")
    
    # Show per-type breakdown
    click.echo(f"\n📊 Content by Type:")
    for content_type in ['acceptance', 'decisions', 'integrations', 'architecture', 'ux', 'code']:
        count = len(context_package.get(content_type, []))
        if count > 0:
            click.echo(f"  {content_type.title()}: {count} items")
    
    # Show budget utilization
    total_budget = sum(summary['budget_limit'] for summary in budget_summary.values())
    used_budget = sum(summary['used_tokens'] for summary in budget_summary.values())
    utilization = (used_budget / total_budget * 100) if total_budget > 0 else 0
    
    click.echo(f"\n💰 Budget Utilization: {utilization:.1f}%")
    
    if utilization > 100:
        click.echo(f"⚠️  Budget exceeded!")
    elif utilization > 80:
        click.echo(f"⚠️  Approaching budget limit")
    else:
        click.echo(f"✅ Budget usage within limits")

# -------------------- DOCUMENT LINKS --------------------
@cli.command("doc:set-links")
@click.argument("file")
@click.option("--prd", default=None)
@click.option("--arch", default=None)
@click.option("--adr", default=None)
@click.option("--impl", default=None)
@click.option("--exec", "exec_", default=None)
@click.option("--ux", default=None)
def doc_set_links(file, prd, arch, adr, impl, exec_, ux):
    """Set front-matter links on a doc without manual editing."""
    fm, txt, m = _doc_load_front_matter(file)
    if m is None:
        raise click.ClickException(f"No YAML front-matter found in {file}")
    links = fm.get("links") or {}
    if prd: links["prd"] = prd
    if arch: links["arch"] = arch
    if adr: links["adr"] = adr
    if impl: links["impl"] = impl
    if exec_: links["exec"] = exec_
    if ux: links["ux"] = ux
    fm["links"] = links
    _doc_save_front_matter(file, fm, txt, m)
    click.echo(f"Updated links in {file}: " + ", ".join([f"{k}={v}" for k,v in links.items()]))

# -------------------- DOCUMENT VALIDATOR --------------------
@cli.command("doc:check")
@click.option("--output", default="builder/cache/schema.json", help="Output JSON report path")
@click.option("--fail-fast", is_flag=True, help="Stop on first validation error")
def doc_check(output, fail_fast):
    """Validate docs front-matter and required sections; write builder/cache/schema.json."""
    import subprocess, sys, os
    ROOT = os.path.dirname(os.path.dirname(__file__))
    rc = subprocess.call([sys.executable, os.path.join(ROOT,"builder","evaluators","doc_schema.py")])
    sys.exit(rc)

# -------------------- CONTEXT GRAPH --------------------
@cli.command("context:scan")
@click.option("--output", default="builder/cache/context_graph.json", help="Output JSON file path")
@click.option("--stats-only", is_flag=True, help="Only print statistics, don't export JSON")
def context_scan(output, stats_only):
    """Scan project and build context graph of nodes and relationships"""
    try:
        from context_graph import ContextGraph
        
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

# -------------------- CONTEXT SELECTION --------------------

# -------------------- ENHANCED CONTEXT BUILD --------------------
@cli.command("ctx:build-enhanced")
@click.argument("target_path")
@click.option("--purpose", required=True, help="Purpose: implement, review, test, etc.")
@click.option("--feature", default="", help="Feature name for rules")
@click.option("--stacks", default="typescript,react", help="Comma-separated stack names")
@click.option("--token-limit", default=8000, help="Token budget limit")
@click.option("--force", is_flag=True, help="Force rebuild, bypass cache")
def ctx_build_enhanced(target_path, purpose, feature, stacks, token_limit, force):
    """Build enhanced context package using graph + selection + budget"""
    try:
        from context_graph import ContextGraphBuilder
        from context_select import ContextSelector
        from context_budget import ContextBudgetManager
        
        # Ensure cache directory exists
        os.makedirs(CACHE, exist_ok=True)
        
        click.echo(f"🔍 Building enhanced context for: {target_path}")
        click.echo(f"📋 Purpose: {purpose}, Feature: {feature or 'None'}")
        click.echo(f"💰 Token budget: {token_limit}")
        
        # Generate cache key
        cache_key, cache_key_string = _generate_cache_key(target_path, purpose, feature, stacks, token_limit)
        cache_path = _get_cache_path(cache_key)
        
        # Check cache first (unless force is specified)
        if not force and os.path.exists(cache_path):
            click.echo("💾 Loading from cache...")
            context_package = _load_from_cache(cache_path)
            if context_package:
                click.echo(f"✅ Cache hit: {cache_key[:8]}...")
                
                # Write to standard output locations
                pack_context_path = os.path.join(CACHE, "pack_context.json")
                with open(pack_context_path, "w", encoding="utf-8") as f:
                    json.dump(context_package, f, indent=2, ensure_ascii=False)
                click.echo(f"✅ Created {pack_context_path}")
                
                # Generate context.md from cached data
                context_md = _generate_enhanced_context_md(context_package)
                context_md_path = os.path.join(CACHE, "context.md")
                with open(context_md_path, "w", encoding="utf-8") as f:
                    f.write(context_md)
                click.echo(f"✅ Created {context_md_path}")
                
                # Show summary
                budget_summary = context_package.get('constraints', {}).get('budget_summary', {})
                _show_context_summary(context_package, budget_summary, token_limit)
                return
        
        if force:
            click.echo("🔄 Force rebuild: bypassing cache")
        else:
            click.echo("💾 Cache miss: building fresh context")
        
        # Step 1: Build context graph
        click.echo("📊 Building context graph...")
        graph_builder = ContextGraphBuilder(ROOT)
        graph = graph_builder.build()
        
        # Step 2: Select context using graph
        click.echo("🎯 Selecting relevant context...")
        selector = ContextSelector(ROOT)
        context_selection = selector.select_context(target_path, feature, top_k=10)
        
        if not context_selection:
            click.echo("❌ No context found for target path")
            return
        
        # Step 3: Apply budget constraints
        click.echo("💰 Applying token budget...")
        budget_manager = ContextBudgetManager(total_budget=token_limit)
        budget_items = budget_manager.create_budget_items(context_selection)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Step 4: Load rules
        rules = _load_rules(feature, stacks)
        
        # Step 5: Build enhanced context package
        context_package = _build_enhanced_context_package(
            target_path, purpose, feature, stacks, token_limit,
            selected_items, overflow_items, budget_summary, rules
        )
        
        # Step 6: Save to cache
        if _save_to_cache(cache_path, context_package):
            click.echo(f"💾 Cached: {cache_key[:8]}...")
        else:
            click.echo("⚠️  Warning: Failed to save to cache")
        
        # Step 7: Write pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        with open(pack_context_path, "w", encoding="utf-8") as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Created {pack_context_path}")
        
        # Step 8: Generate enhanced context.md
        context_md = _generate_enhanced_context_md(context_package)
        context_md_path = os.path.join(CACHE, "context.md")
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)
        click.echo(f"✅ Created {context_md_path}")
        
        # Step 9: Show summary
        _show_context_summary(context_package, budget_summary, token_limit)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT DIFF --------------------
@cli.command("ctx:diff")
@click.argument("old_pack")
@click.argument("new_pack")
@click.option("--output", default="", help="Output file path (prints to stdout if not specified)")
def ctx_diff(old_pack, new_pack, output):
    """Show differences between two context packs (added/removed items, weight changes, budget changes)"""
    try:
        import json
        from collections import defaultdict
        
        # Load both packs
        with open(old_pack, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        with open(new_pack, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        # Generate diff report
        diff_report = _generate_context_diff(old_data, new_data)
        
        # Output diff
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(diff_report)
            click.echo(f"✅ Diff report written to {output}")
        else:
            click.echo(diff_report)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT EXPLAIN --------------------
@cli.command("ctx:explain")
@click.option("--input", default="builder/cache/pack_context.json", help="Input pack_context.json file")
@click.option("--selection", default="builder/cache/context_selection.json", help="Context selection file with scores")
def ctx_explain(input, selection):
    """Explain why specific context items were selected with ranked table"""
    try:
        import json
        from pathlib import Path
        from datetime import datetime
        
        # Check if files exist
        if not os.path.exists(input):
            click.echo(f"❌ Input file not found: {input}")
            click.echo("Run 'ctx:build-enhanced' first to generate pack_context.json")
            return
        
        if not os.path.exists(selection):
            click.echo(f"❌ Selection file not found: {selection}")
            click.echo("Run 'ctx:build-enhanced' first to generate context_selection.json")
            return
        
        # Load pack_context.json
        with open(input, 'r', encoding='utf-8') as f:
            pack_context = json.load(f)
        
        # Load context_selection.json
        with open(selection, 'r', encoding='utf-8') as f:
            selection_data = json.load(f)
        
        # Extract task information
        task = pack_context.get('task', {})
        click.echo(f"🔍 Context Explanation for: {task.get('target_path', 'Unknown')}")
        click.echo(f"📋 Purpose: {task.get('purpose', 'Unknown')}")
        click.echo(f"🏷️  Feature: {task.get('feature', 'None')}")
        click.echo()
        
        # Collect all selected items with their scores
        all_items = []
        
        # Process each type in selection data
        for item_type, items in selection_data.items():
            for item in items:
                node = item.get('node', {})
                all_items.append({
                    'id': item.get('id', 'unknown'),
                    'type': item.get('type', item_type),
                    'title': node.get('title', 'Untitled'),
                    'file_path': node.get('file_path', ''),
                    'score': item.get('score', 0.0),
                    'reasons': item.get('reasons', []),
                    'status': node.get('status', 'unknown'),
                    'created': node.get('created', ''),
                    'last_modified': _get_last_modified(node.get('file_path', ''))
                })
        
        # Sort by score (highest first)
        all_items.sort(key=lambda x: x['score'], reverse=True)
        
        # Display ranked table
        click.echo("📊 Ranked Context Items (by selection score):")
        click.echo("=" * 120)
        
        # Table header
        header = f"{'Rank':<4} {'Score':<6} {'Type':<12} {'Status':<10} {'ID/Path':<30} {'Reasons':<20} {'Modified':<12}"
        click.echo(header)
        click.echo("-" * 120)
        
        # Table rows
        for i, item in enumerate(all_items, 1):
            # Truncate long paths
            display_path = item['file_path']
            if len(display_path) > 28:
                display_path = "..." + display_path[-25:]
            
            # Format reasons
            reasons_str = ", ".join(item['reasons'][:2])  # Show first 2 reasons
            if len(item['reasons']) > 2:
                reasons_str += f" (+{len(item['reasons'])-2})"
            
            # Format last modified
            modified_str = item['last_modified'] or "Unknown"
            
            row = f"{i:<4} {item['score']:<6.1f} {item['type']:<12} {item['status']:<10} {display_path:<30} {reasons_str:<20} {modified_str:<12}"
            click.echo(row)
        
        click.echo("-" * 120)
        
        # Summary statistics
        total_items = len(all_items)
        avg_score = sum(item['score'] for item in all_items) / total_items if total_items > 0 else 0
        
        # Count by type
        type_counts = {}
        for item in all_items:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # Count by reason
        reason_counts = {}
        for item in all_items:
            for reason in item['reasons']:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        click.echo(f"\n📈 Summary Statistics:")
        click.echo(f"  Total items: {total_items}")
        click.echo(f"  Average score: {avg_score:.2f}")
        click.echo(f"  Score range: {min(item['score'] for item in all_items):.1f} - {max(item['score'] for item in all_items):.1f}")
        
        click.echo(f"\n📊 Items by Type:")
        for item_type, count in sorted(type_counts.items()):
            click.echo(f"  {item_type}: {count}")
        
        click.echo(f"\n🎯 Selection Reasons:")
        for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {reason}: {count} items")
        
        # Show budget utilization if available
        constraints = pack_context.get('constraints', {})
        budget_summary = constraints.get('budget_summary', {})
        if budget_summary:
            click.echo(f"\n💰 Budget Utilization:")
            total_budget = sum(summary.get('budget_limit', 0) for summary in budget_summary.values())
            used_budget = sum(summary.get('used_tokens', 0) for summary in budget_summary.values())
            utilization = (used_budget / total_budget * 100) if total_budget > 0 else 0
            click.echo(f"  Used: {used_budget}/{total_budget} tokens ({utilization:.1f}%)")
            
            for budget_type, summary in budget_summary.items():
                items_selected = summary.get('selected_items', 0)
                items_total = summary.get('total_items', 0)
                budget_used = summary.get('used_tokens', 0)
                budget_limit = summary.get('budget_limit', 0)
                click.echo(f"  {budget_type}: {items_selected}/{items_total} items ({budget_used}/{budget_limit} tokens)")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

def _get_last_modified(file_path):
    """Get last modified date for a file"""
    try:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except Exception:
        pass
    return "Unknown"

def _show_plan_auto_summary(context_package, budget_summary, token_limit):
    """Show 1-line summary with counts per type and budget used"""
    # Check for rules presence
    rules_present = bool(context_package.get('constraints', {}).get('rules_md', '').strip())
    rules_status = "✓" if rules_present else "✗"
    
    # Check for acceptance criteria presence
    acceptance_present = bool(context_package.get('acceptance', []))
    acceptance_status = "✓" if acceptance_present else "✗"
    
    # Count items by type with specific abbreviations
    type_counts = {}
    type_abbrevs = {
        'decisions': 'adr',
        'integrations': 'integ', 
        'architecture': 'arch',
        'code': 'code'
    }
    
    for section, abbrev in type_abbrevs.items():
        items = context_package.get(section, [])
        count = len(items)
        if count > 0:
            type_counts[abbrev] = count
    
    # Calculate budget percentage
    total_used = sum(summary.get('used_tokens', 0) for summary in budget_summary.values())
    budget_pct = int(total_used / token_limit * 100) if token_limit > 0 else 0
    
    # Build summary line in the required format
    summary_parts = [
        f"rules {rules_status}",
        f"acceptance {acceptance_status}"
    ]
    
    # Add type counts
    for abbrev, count in type_counts.items():
        summary_parts.append(f"{abbrev} {count}")
    
    # Add budget percentage
    summary_parts.append(f"budget {budget_pct}%")
    
    summary_line = f"Context: {', '.join(summary_parts)}"
    click.echo(summary_line)

def _generate_cache_key(target_path, purpose, feature, stacks, token_limit):
    """Generate cache key based on inputs and file hashes"""
    import hashlib
    import os
    from pathlib import Path
    
    # Pack schema version (increment when structure changes)
    PACK_SCHEMA_VERSION = "1.0"
    
    # Get file hashes for docs and src directories
    def get_directory_hash(directory):
        """Get combined hash of all files in directory"""
        if not os.path.exists(directory):
            return "no_dir"
        
        hashes = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.md', '.ts', '.tsx', '.js', '.jsx', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
                            hashes.append(f"{file}:{file_hash}")
                    except Exception:
                        continue
        return hashlib.sha256('|'.join(sorted(hashes)).encode()).hexdigest()[:16]
    
    # Get rules hash
    def get_rules_hash():
        """Get hash of all rules files"""
        rules_files = [
            "docs/rules/00-global.md",
            "docs/rules/10-project.md", 
            "docs/rules/guardrails.json"
        ]
        
        # Add feature-specific rules
        if feature:
            feature_rules = f"docs/rules/feature/30-{feature}.md"
            if os.path.exists(feature_rules):
                rules_files.append(feature_rules)
        
        # Add stack-specific rules
        for stack in stacks.split(','):
            stack_rules = f"docs/rules/stack/20-{stack.strip()}.md"
            if os.path.exists(stack_rules):
                rules_files.append(stack_rules)
        
        hashes = []
        for rules_file in rules_files:
            if os.path.exists(rules_file):
                try:
                    with open(rules_file, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
                        hashes.append(f"{os.path.basename(rules_file)}:{file_hash}")
                except Exception:
                    continue
        
        return hashlib.sha256('|'.join(sorted(hashes)).encode()).hexdigest()[:16]
    
    # Build cache key components
    docs_hash = get_directory_hash("docs")
    src_hash = get_directory_hash("src")
    rules_hash = get_rules_hash()
    
    # Create cache key string
    cache_key_parts = [
        f"feature:{feature or 'none'}",
        f"purpose:{purpose}",
        f"target:{target_path}",
        f"docs:{docs_hash}",
        f"src:{src_hash}",
        f"rules:{rules_hash}",
        f"stacks:{stacks}",
        f"tokens:{token_limit}",
        f"schema:{PACK_SCHEMA_VERSION}"
    ]
    
    cache_key_string = '|'.join(cache_key_parts)
    cache_key = hashlib.sha256(cache_key_string.encode()).hexdigest()[:32]
    
    return cache_key, cache_key_string

def _get_cache_path(cache_key):
    """Get cache file path for given cache key"""
    cache_dir = os.path.join(CACHE, "packs")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{cache_key}.json")

def _load_from_cache(cache_path):
    """Load context package from cache"""
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def _save_to_cache(cache_path, context_package):
    """Save context package to cache"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def _generate_context_diff(old_data, new_data):
    """Generate a comprehensive diff report between two context packs"""
    from collections import defaultdict
    
    diff_lines = []
    diff_lines.append("# Context Pack Diff Report")
    diff_lines.append("")
    from datetime import datetime
    diff_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    diff_lines.append("")
    
    # Task comparison
    old_task = old_data.get('task', {})
    new_task = new_data.get('task', {})
    diff_lines.append("## Task Changes")
    diff_lines.append("")
    
    task_changes = []
    for key in ['purpose', 'target_path', 'feature']:
        old_val = old_task.get(key, '')
        new_val = new_task.get(key, '')
        if old_val != new_val:
            task_changes.append(f"- **{key}**: `{old_val}` → `{new_val}`")
    
    if task_changes:
        diff_lines.extend(task_changes)
    else:
        diff_lines.append("No task changes")
    diff_lines.append("")
    
    # Budget comparison
    old_budget = old_data.get('constraints', {}).get('budget_summary', {})
    new_budget = new_data.get('constraints', {}).get('budget_summary', {})
    
    diff_lines.append("## Budget Changes")
    diff_lines.append("")
    
    # Calculate total tokens
    old_total = sum(cat.get('used_tokens', 0) for cat in old_budget.values())
    new_total = sum(cat.get('used_tokens', 0) for cat in new_budget.values())
    old_limit = old_data.get('constraints', {}).get('token_limit', 0)
    new_limit = new_data.get('constraints', {}).get('token_limit', 0)
    
    diff_lines.append(f"**Total Tokens**: {old_total} → {new_total} ({new_total - old_total:+d})")
    diff_lines.append(f"**Token Limit**: {old_limit} → {new_limit} ({new_limit - old_limit:+d})")
    diff_lines.append(f"**Utilization**: {old_total/old_limit*100:.1f}% → {new_total/new_limit*100:.1f}%")
    diff_lines.append("")
    
    # Category-level budget changes
    all_categories = set(old_budget.keys()) | set(new_budget.keys())
    for category in sorted(all_categories):
        old_cat = old_budget.get(category, {})
        new_cat = new_budget.get(category, {})
        
        old_tokens = old_cat.get('used_tokens', 0)
        new_tokens = new_cat.get('used_tokens', 0)
        old_items = old_cat.get('selected_items', 0)
        new_items = new_cat.get('selected_items', 0)
        
        if old_tokens != new_tokens or old_items != new_items:
            diff_lines.append(f"### {category.title()}")
            diff_lines.append(f"- **Items**: {old_items} → {new_items} ({new_items - old_items:+d})")
            diff_lines.append(f"- **Tokens**: {old_tokens} → {new_tokens} ({new_tokens - old_tokens:+d})")
            diff_lines.append("")
    
    # Content section comparisons
    content_sections = ['acceptance', 'decisions', 'integrations', 'architecture', 'ux', 'code']
    
    for section in content_sections:
        old_items = old_data.get(section, [])
        new_items = new_data.get(section, [])
        
        # Create item maps for comparison
        old_map = {_get_item_key(item): item for item in old_items}
        new_map = {_get_item_key(item): item for item in new_items}
        
        added_items = []
        removed_items = []
        changed_items = []
        
        # Find added items
        for key, item in new_map.items():
            if key not in old_map:
                added_items.append(item)
        
        # Find removed items
        for key, item in old_map.items():
            if key not in new_map:
                removed_items.append(item)
        
        # Find changed items (same key, different content)
        for key in old_map.keys() & new_map.keys():
            old_item = old_map[key]
            new_item = new_map[key]
            if _items_different(old_item, new_item):
                changed_items.append((old_item, new_item))
        
        # Generate section diff
        if added_items or removed_items or changed_items:
            diff_lines.append(f"## {section.title()} Changes")
            diff_lines.append("")
            
            if added_items:
                diff_lines.append(f"### Added ({len(added_items)} items)")
                for item in added_items[:5]:  # Limit to first 5
                    title = item.get('title', 'Untitled')[:60]
                    file_path = item.get('file_path', 'Unknown')
                    diff_lines.append(f"- **{title}**")
                    diff_lines.append(f"  - Source: `{file_path}`")
                if len(added_items) > 5:
                    diff_lines.append(f"- ... and {len(added_items) - 5} more")
                diff_lines.append("")
            
            if removed_items:
                diff_lines.append(f"### Removed ({len(removed_items)} items)")
                for item in removed_items[:5]:  # Limit to first 5
                    title = item.get('title', 'Untitled')[:60]
                    file_path = item.get('file_path', 'Unknown')
                    diff_lines.append(f"- **{title}**")
                    diff_lines.append(f"  - Source: `{file_path}`")
                if len(removed_items) > 5:
                    diff_lines.append(f"- ... and {len(removed_items) - 5} more")
                diff_lines.append("")
            
            if changed_items:
                diff_lines.append(f"### Changed ({len(changed_items)} items)")
                for old_item, new_item in changed_items[:3]:  # Limit to first 3
                    title = old_item.get('title', 'Untitled')[:60]
                    diff_lines.append(f"- **{title}**")
                    # Show what changed
                    changes = _get_item_changes(old_item, new_item)
                    for change in changes:
                        diff_lines.append(f"  - {change}")
                if len(changed_items) > 3:
                    diff_lines.append(f"- ... and {len(changed_items) - 3} more")
                diff_lines.append("")
    
    # Summary
    total_added = sum(len([item for item in new_data.get(section, []) 
                          if _get_item_key(item) not in {_get_item_key(item) for item in old_data.get(section, [])}])
                     for section in content_sections)
    total_removed = sum(len([item for item in old_data.get(section, []) 
                            if _get_item_key(item) not in {_get_item_key(item) for item in new_data.get(section, [])}])
                       for section in content_sections)
    
    diff_lines.append("## Summary")
    diff_lines.append("")
    diff_lines.append(f"- **Items Added**: {total_added}")
    diff_lines.append(f"- **Items Removed**: {total_removed}")
    diff_lines.append(f"- **Token Change**: {new_total - old_total:+d}")
    diff_lines.append(f"- **Utilization Change**: {new_total/new_limit*100 - old_total/old_limit*100:+.1f}%")
    
    return "\n".join(diff_lines)

def _get_item_key(item):
    """Get a unique key for an item based on title and file_path"""
    title = item.get('title', '')
    file_path = item.get('file_path', '')
    return f"{title}|{file_path}"

def _items_different(old_item, new_item):
    """Check if two items are different (ignoring metadata)"""
    # Compare key fields that matter for content
    key_fields = ['title', 'content', 'file_path']
    for field in key_fields:
        if old_item.get(field) != new_item.get(field):
            return True
    return False

def _get_item_changes(old_item, new_item):
    """Get a list of changes between two items"""
    changes = []
    
    if old_item.get('title') != new_item.get('title'):
        changes.append(f"Title: '{old_item.get('title', '')}' → '{new_item.get('title', '')}'")
    
    if old_item.get('file_path') != new_item.get('file_path'):
        changes.append(f"Source: '{old_item.get('file_path', '')}' → '{new_item.get('file_path', '')}'")
    
    old_content = old_item.get('content', '')
    new_content = new_item.get('content', '')
    if old_content != new_content:
        old_len = len(old_content)
        new_len = len(new_content)
        changes.append(f"Content: {old_len} → {new_len} chars ({new_len - old_len:+d})")
    
    return changes

# -------------------- CONTEXT BUDGET --------------------

# -------------------- CONTEXT EXPLAIN --------------------

@cli.command("ctx:pack")
@click.option("--output", default="", help="Output file path (prints to stdout if not specified)")
@click.option("--split", is_flag=True, help="Emit four separate files: system.txt, instructions.txt, user.txt, references.md")
@click.option("--stdout", is_flag=True, help="Print in sequence with clear separators for copy/paste")
def ctx_pack(output, split, stdout):
    """Emit four blocks from pack_context.json: system, instructions, user, references"""
    try:
        import json
        
        # Load pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        if not os.path.exists(pack_context_path):
            click.echo("❌ No pack_context.json found. Run 'ctx:build-enhanced' first.")
            raise SystemExit(1)
            
        with open(pack_context_path, 'r', encoding='utf-8') as f:
            context_package = json.load(f)
        
        # Build the 4 blocks
        blocks = []
        
        # Block 1: SYSTEM - merged rules_md + "obey acceptance criteria" line
        system_block = []
        system_block.append("## SYSTEM")
        system_block.append("")
        
        # Add rules_md (highest priority)
        rules_md = context_package.get('constraints', {}).get('rules_md', '')
        if rules_md:
            system_block.append(rules_md)
            system_block.append("")
        
        # Add acceptance criteria directive
        system_block.append("**OBEY ACCEPTANCE CRITERIA** - All implementation must satisfy the acceptance criteria listed in the instructions block.")
        system_block.append("")
        
        blocks.append("\n".join(system_block))
        
        # Block 2: INSTRUCTIONS - goal, acceptance bullets, constraints (budgets/limits)
        instructions_block = []
        instructions_block.append("## INSTRUCTIONS")
        instructions_block.append("")
        
        # Task information
        task = context_package.get('task', {})
        purpose = task.get('purpose', 'unknown')
        target_path = task.get('target_path', '')
        feature = task.get('feature', '')
        
        # Goal
        instructions_block.append(f"**Goal**: {purpose} {target_path}")
        if feature:
            instructions_block.append(f"**Feature**: {feature}")
        instructions_block.append("")
        
        # Acceptance criteria (bulleted list)
        acceptance_items = context_package.get('acceptance', [])
        if acceptance_items:
            instructions_block.append("**Acceptance Criteria**:")
            instructions_block.append("")
            for item in acceptance_items:
                # Extract acceptance criteria from content
                content = item.get('content', '')
                if 'Acceptance Criteria' in content:
                    # Find the acceptance criteria section
                    lines = content.split('\n')
                    in_criteria = False
                    for line in lines:
                        if 'Acceptance Criteria' in line:
                            in_criteria = True
                            continue
                        elif in_criteria and line.strip() and not line.startswith('#'):
                            if line.strip().startswith('-'):
                                instructions_block.append(f"  {line.strip()}")
                            elif line.strip():
                                instructions_block.append(f"  - {line.strip()}")
                        elif in_criteria and line.startswith('#'):
                            break
            instructions_block.append("")
        
        # Constraints (budgets/limits)
        constraints = context_package.get('constraints', {})
        budget_summary = constraints.get('budget_summary', {})
        if budget_summary:
            instructions_block.append("**Constraints**:")
            instructions_block.append("")
            total_budget = sum(summary.get('budget_limit', 0) for summary in budget_summary.values())
            used_budget = sum(summary.get('used_tokens', 0) for summary in budget_summary.values())
            instructions_block.append(f"- Token budget: {used_budget}/{total_budget} tokens")
            for budget_type, summary in budget_summary.items():
                items_selected = summary.get('selected_items', 0)
                items_total = summary.get('total_items', 0)
                instructions_block.append(f"- {budget_type.title()}: {items_selected}/{items_total} items")
            instructions_block.append("")
        
        blocks.append("\n".join(instructions_block))
        
        # Block 3: USER - succinct restatement (derived from target path + feature)
        user_block = []
        user_block.append("## USER")
        user_block.append("")
        
        # Succinct restatement
        if target_path and feature:
            user_block.append(f"Implement {feature} functionality in {target_path}")
        elif target_path:
            user_block.append(f"Implement functionality in {target_path}")
        else:
            user_block.append("Implement the requested functionality")
        user_block.append("")
        
        # Add relevant code excerpts if available
        code_items = context_package.get('code', [])
        if code_items:
            user_block.append("**Current Code**:")
            user_block.append("")
            for item in code_items[:3]:  # Limit to 3 code items
                title = item.get('title', 'Unknown')
                content = item.get('content', '')
                file_path = item.get('file_path', '')
                if file_path:
                    user_block.append(f"```typescript")
                    user_block.append(f"// {file_path}")
                    # Show first 20 lines of content
                    lines = content.split('\n')[:20]
                    user_block.append('\n'.join(lines))
                    if len(content.split('\n')) > 20:
                        user_block.append("// ... (truncated)")
                    user_block.append("```")
                    user_block.append("")
        
        blocks.append("\n".join(user_block))
        
        # Block 4: REFERENCES - bulleted list of included sources with anchors
        references_block = []
        references_block.append("## REFERENCES")
        references_block.append("")
        
        # Acceptance items
        if acceptance_items:
            references_block.append("**Acceptance Sources**:")
            for item in acceptance_items:
                title = item.get('title', 'Unknown')
                source_anchor = item.get('source_anchor', '')
                if source_anchor:
                    references_block.append(f"- {source_anchor}")
                else:
                    file_path = item.get('file_path', '')
                    if file_path:
                        references_block.append(f"- [{title}]({file_path})")
            references_block.append("")
        
        # Architecture items
        arch_items = context_package.get('architecture', [])
        if arch_items:
            references_block.append("**Architecture Sources**:")
            for item in arch_items:
                title = item.get('title', 'Unknown')
                source_anchor = item.get('source_anchor', '')
                if source_anchor:
                    references_block.append(f"- {source_anchor}")
                else:
                    file_path = item.get('file_path', '')
                    if file_path:
                        references_block.append(f"- [{title}]({file_path})")
            references_block.append("")
        
        # Code items
        if code_items:
            references_block.append("**Code Sources**:")
            for item in code_items:
                title = item.get('title', 'Unknown')
                source_anchor = item.get('source_anchor', '')
                if source_anchor:
                    references_block.append(f"- {source_anchor}")
                else:
                    file_path = item.get('file_path', '')
                    if file_path:
                        references_block.append(f"- [{title}]({file_path})")
            references_block.append("")
        
        # Other sources
        other_sections = ['decisions', 'integrations', 'ux']
        for section in other_sections:
            items = context_package.get(section, [])
            if items:
                references_block.append(f"**{section.title()} Sources**:")
                for item in items:
                    title = item.get('title', 'Unknown')
                    source_anchor = item.get('source_anchor', '')
                    if source_anchor:
                        references_block.append(f"- {source_anchor}")
                    else:
                        file_path = item.get('file_path', '')
                        if file_path:
                            references_block.append(f"- [{title}]({file_path})")
                references_block.append("")
        
        blocks.append("\n".join(references_block))
        
        # Handle different output modes
        if split:
            # Create prompt directory
            prompt_dir = os.path.join(CACHE, "prompt")
            os.makedirs(prompt_dir, exist_ok=True)
            
            # Write four separate files
            files_written = []
            
            # System block
            system_file = os.path.join(prompt_dir, "system.txt")
            with open(system_file, 'w', encoding='utf-8') as f:
                f.write(blocks[0])
            files_written.append("system.txt")
            
            # Instructions block
            instructions_file = os.path.join(prompt_dir, "instructions.txt")
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(blocks[1])
            files_written.append("instructions.txt")
            
            # User block
            user_file = os.path.join(prompt_dir, "user.txt")
            with open(user_file, 'w', encoding='utf-8') as f:
                f.write(blocks[2])
            files_written.append("user.txt")
            
            # References block
            references_file = os.path.join(prompt_dir, "references.md")
            with open(references_file, 'w', encoding='utf-8') as f:
                f.write(blocks[3])
            files_written.append("references.md")
            
            click.echo(f"✅ Split context pack written to {prompt_dir}/")
            for filename in files_written:
                click.echo(f"  - {filename}")
                
        elif stdout:
            # Print with clear separators for copy/paste
            click.echo("=" * 80)
            click.echo("SYSTEM BLOCK")
            click.echo("=" * 80)
            click.echo(blocks[0])
            click.echo()
            click.echo("=" * 80)
            click.echo("INSTRUCTIONS BLOCK")
            click.echo("=" * 80)
            click.echo(blocks[1])
            click.echo()
            click.echo("=" * 80)
            click.echo("USER BLOCK")
            click.echo("=" * 80)
            click.echo(blocks[2])
            click.echo()
            click.echo("=" * 80)
            click.echo("REFERENCES BLOCK")
            click.echo("=" * 80)
            click.echo(blocks[3])
            click.echo()
            click.echo("=" * 80)
            
        else:
            # Original behavior: combine all blocks
            full_output = "\n\n".join(blocks)
            
            # Output to file or stdout
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(full_output)
                click.echo(f"✅ Context pack saved to: {output}")
            else:
                click.echo(full_output)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:trace")
@click.option("--output", default="builder/cache/trace.csv", help="Output CSV file path")
@click.option("--format", type=click.Choice(['csv', 'md']), default='csv', help="Output format (csv or md)")
def ctx_trace(output, format):
    """Generate traceability matrix mapping PRD → Arch → Impl → Tasks → Code/Tests → ADRs."""
    try:
        import json
        import csv
        from collections import defaultdict
        
        # Load context graph
        context_graph_path = os.path.join(CACHE, "context_graph.json")
        if not os.path.exists(context_graph_path):
            click.echo("❌ No context graph found. Run 'context:scan' first.")
            raise SystemExit(1)
            
        with open(context_graph_path, 'r') as f:
            graph_data = json.load(f)
        
        # Build node lookup by ID
        nodes_by_id = {}
        for node in graph_data['nodes']:
            nodes_by_id[node['id']] = node
        
        # Build relationships from links metadata
        relationships = defaultdict(list)
        
        for node in graph_data['nodes']:
            node_id = node['id']
            node_type = node['type']
            metadata = node.get('metadata', {})
            links = metadata.get('links', [])
            
            # Extract relationships from links
            for link_group in links:
                for link_type, target_ids in link_group.items():
                    if target_ids:  # Only process non-empty lists
                        for target_id in target_ids:
                            if target_id in nodes_by_id:
                                relationships[node_id].append({
                                    'target': target_id,
                                    'type': link_type,
                                    'source_type': node_type,
                                    'target_type': nodes_by_id[target_id]['type']
                                })
        
        # Build traceability matrix
        trace_matrix = []
        
        # Process each PRD and trace through the hierarchy
        prd_nodes = [node for node in graph_data['nodes'] if node['type'] == 'prd']
        
        if not prd_nodes:
            click.echo("❌ No PRD documents found in context graph.")
            return
        
        for prd in prd_nodes:
            prd_id = prd['id']
            prd_title = prd['title']
            
            # Find architecture documents linked to this PRD
            arch_docs = []
            for rel in relationships.get(prd_id, []):
                if rel['type'] == 'arch' and rel['target_type'] == 'arch':
                    arch_docs.append(rel['target'])
            
            # If no direct arch links, find any arch documents
            if not arch_docs:
                arch_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'arch']
            
            for arch_id in arch_docs:
                arch_title = nodes_by_id[arch_id]['title']
                
                # Find implementation documents linked to this arch
                impl_docs = []
                for rel in relationships.get(arch_id, []):
                    if rel['type'] == 'impl' and rel['target_type'] == 'impl':
                        impl_docs.append(rel['target'])
                
                # If no direct impl links, find any impl documents
                if not impl_docs:
                    impl_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'impl']
                
                # If no impl docs, use ux docs as implementation guidance
                if not impl_docs:
                    impl_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'ux']
                
                for impl_id in impl_docs:
                    impl_title = nodes_by_id[impl_id]['title']
                    
                    # Find task/execution documents
                    task_docs = []
                    for rel in relationships.get(impl_id, []):
                        if rel['type'] == 'exec' and rel['target_type'] == 'exec':
                            task_docs.append(rel['target'])
                    
                    # If no task docs, find any exec documents
                    if not task_docs:
                        task_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'exec']
                    
                    # If no exec docs, create a placeholder
                    if not task_docs:
                        task_docs = ['TASK-PLACEHOLDER']
                    
                    for task_id in task_docs:
                        task_title = "Task Placeholder" if task_id == 'TASK-PLACEHOLDER' else nodes_by_id[task_id]['title']
                        
                        # Find code files related to this task/impl
                        code_files = []
                        test_files = []
                        
                        # Look for code files that might be related
                        for node in graph_data['nodes']:
                            if node['type'] == 'code':
                                file_path = node['file_path']
                                if file_path:
                                    if file_path.endswith('.test.ts') or file_path.endswith('.test.js'):
                                        test_files.append(node['id'])
                                    else:
                                        code_files.append(node['id'])
                        
                        # Find ADRs related to this implementation
                        adr_docs = []
                        for node in graph_data['nodes']:
                            if node['type'] == 'adr' and node['id'] != 'ADR-0000':  # Skip master ADR
                                # Check if ADR is related to any of our code files
                                metadata = node.get('metadata', {})
                                related_files = metadata.get('related_files', [])
                                if any(code_file in related_files for code_file in code_files):
                                    adr_docs.append(node['id'])
                        
                        # If no specific ADR links, include all ADRs
                        if not adr_docs:
                            adr_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'adr' and node['id'] != 'ADR-0000']
                        
                        # Create traceability entries
                        for code_id in code_files:
                            code_title = nodes_by_id[code_id]['title']
                            code_path = nodes_by_id[code_id]['file_path']
                            
                            for adr_id in adr_docs:
                                adr_title = nodes_by_id[adr_id]['title']
                                
                                trace_matrix.append({
                                    'PRD': prd_title,
                                    'Architecture': arch_title,
                                    'Implementation': impl_title,
                                    'Tasks': task_title,
                                    'Code': code_title,
                                    'Code_Path': code_path,
                                    'Tests': ', '.join([nodes_by_id[tid]['title'] for tid in test_files if tid in nodes_by_id]),
                                    'ADRs': adr_title,
                                    'Status': 'Active'
                                })
        
        if not trace_matrix:
            click.echo("❌ No traceability relationships found.")
            return
        
        # Output the matrix
        if format == 'csv':
            # Ensure output directory exists
            output_dir = os.path.dirname(output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['PRD', 'Architecture', 'Implementation', 'Tasks', 'Code', 'Code_Path', 'Tests', 'ADRs', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(trace_matrix)
            
            click.echo(f"✅ Traceability matrix saved to: {output}")
            click.echo(f"📊 Generated {len(trace_matrix)} traceability entries")
            
        elif format == 'md':
            # Generate markdown table
            md_content = []
            md_content.append("# Traceability Matrix")
            md_content.append("")
            md_content.append("| PRD | Architecture | Implementation | Tasks | Code | Tests | ADRs | Status |")
            md_content.append("|-----|-------------|---------------|-------|------|-------|------|--------|")
            
            for entry in trace_matrix:
                md_content.append(f"| {entry['PRD']} | {entry['Architecture']} | {entry['Implementation']} | {entry['Tasks']} | {entry['Code']} | {entry['Tests']} | {entry['ADRs']} | {entry['Status']} |")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            
            click.echo(f"✅ Traceability matrix saved to: {output}")
            click.echo(f"📊 Generated {len(trace_matrix)} traceability entries")
        
        # Show summary
        click.echo(f"\n📈 Summary:")
        click.echo(f"  PRDs: {len(set(entry['PRD'] for entry in trace_matrix))}")
        click.echo(f"  Architecture docs: {len(set(entry['Architecture'] for entry in trace_matrix))}")
        click.echo(f"  Implementation docs: {len(set(entry['Implementation'] for entry in trace_matrix))}")
        click.echo(f"  Code files: {len(set(entry['Code'] for entry in trace_matrix))}")
        click.echo(f"  ADRs: {len(set(entry['ADRs'] for entry in trace_matrix))}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT GRAPH --------------------
@cli.command("ctx:graph:build")
@click.option("--output", default="builder/cache/context_graph.json", help="Output JSON file path")
def ctx_graph_build(output):
    """Build context graph from docs and source code"""
    try:
        from context_graph import ContextGraphBuilder
        
        click.echo("🔍 Building context graph...")
        builder = ContextGraphBuilder(ROOT)
        graph = builder.build()
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save graph
        graph.save(output)
        
        # Show stats
        stats = graph.get_stats()
        click.echo(f"✅ Context graph saved to: {output}")
        click.echo(f"📊 Graph Statistics:")
        click.echo(f"  Total nodes: {stats['total_nodes']}")
        click.echo(f"  Total edges: {stats['total_edges']}")
        click.echo(f"  Node types: {stats['node_counts']}")
        click.echo(f"  Edge types: {stats['edge_counts']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:graph:stats")
def ctx_graph_stats():
    """Show context graph statistics"""
    try:
        from context_graph import ContextGraphBuilder
        
        # Build or load graph
        graph_file = os.path.join(ROOT, "builder", "cache", "context_graph.json")
        if os.path.exists(graph_file):
            from context_graph import ContextGraph
            graph = ContextGraph.load(graph_file)
            click.echo("📊 Context Graph Statistics (from cache):")
        else:
            click.echo("🔍 Building context graph...")
            builder = ContextGraphBuilder(ROOT)
            graph = builder.build()
            click.echo("📊 Context Graph Statistics (fresh build):")
        
        stats = graph.get_stats()
        
        # Display stats
        click.echo(f"  Total nodes: {stats['total_nodes']}")
        click.echo(f"  Total edges: {stats['total_edges']}")
        click.echo("")
        
        click.echo("  Node counts by type:")
        for node_type, count in sorted(stats['node_counts'].items()):
            click.echo(f"    {node_type}: {count}")
        
        click.echo("")
        click.echo("  Edge counts by type:")
        for edge_type, count in sorted(stats['edge_counts'].items()):
            click.echo(f"    {edge_type}: {count}")
        
        # Show some sample relationships
        if stats['total_edges'] > 0:
            click.echo("")
            click.echo("  Sample relationships:")
            sample_count = 0
            for from_node, edges in graph.edges.items():
                if sample_count >= 5:
                    break
                for edge in edges[:2]:  # Show first 2 edges from each node
                    if sample_count >= 5:
                        break
                    from_info = graph.get_node(from_node)
                    to_info = graph.get_node(edge['to'])
                    if from_info and to_info:
                        click.echo(f"    {from_info['type']}:{from_node} --{edge['type']}--> {to_info['type']}:{edge['to']}")
                        sample_count += 1
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT SELECTION --------------------
@cli.command("ctx:select")
@click.argument("target_path")
@click.option("--feature", default="", help="Feature name for feature-based scoring")
@click.option("--top-k", default=5, help="Number of top items to return per type")
@click.option("--output", default="builder/cache/context_selection.json", help="Output JSON file path")
def ctx_select(target_path, feature, top_k, output):
    """Select and rank context for a target path"""
    try:
        from context_select import ContextSelector
        
        click.echo(f"🔍 Selecting context for: {target_path}")
        if feature:
            click.echo(f"📋 Feature: {feature}")
        
        selector = ContextSelector(ROOT)
        context = selector.select_context(target_path, feature, top_k)
        
        if not context:
            click.echo("❌ No context found for target path")
            return
        
        # Save context selection
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False, default=str)
        
        # Show summary
        summary = selector.get_context_summary(context)
        click.echo(f"✅ Context selection saved to: {output}")
        click.echo(summary)
        
        # Show statistics
        total_items = sum(len(items) for items in context.values())
        click.echo(f"\n📊 Selected {total_items} context items across {len(context)} types")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT BUDGET --------------------
@cli.command("ctx:budget")
@click.argument("target_path")
@click.option("--feature", default="", help="Feature name for feature-based scoring")
@click.option("--budget", default=8000, help="Total token budget")
@click.option("--output", default="builder/cache/context_budget.json", help="Output JSON file path")
@click.option("--report", default="builder/cache/budget_report.md", help="Budget report markdown file path")
def ctx_budget(target_path, feature, budget, output, report):
    """Apply token budget to context selection"""
    try:
        from context_select import ContextSelector
        from context_budget import ContextBudgetManager
        
        click.echo(f"💰 Applying token budget to: {target_path}")
        click.echo(f"📊 Total budget: {budget} tokens")
        if feature:
            click.echo(f"📋 Feature: {feature}")
        
        # Get context selection
        selector = ContextSelector(ROOT)
        context = selector.select_context(target_path, feature, top_k=10)  # Get more items for budgeting
        
        if not context:
            click.echo("❌ No context found for target path")
            return
        
        # Apply budget
        budget_manager = ContextBudgetManager(total_budget=budget)
        budget_items = budget_manager.create_budget_items(context)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Save results
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        budget_manager.save_budget_results(selected_items, overflow_items, budget_summary, output)
        
        # Generate and save report
        report_content = budget_manager.create_budget_report(selected_items, overflow_items, budget_summary)
        with open(report, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Show summary
        total_tokens = sum(item.token_estimate for item in selected_items)
        click.echo(f"✅ Budget applied successfully!")
        click.echo(f"📄 Selected: {len(selected_items)} items ({total_tokens} tokens)")
        click.echo(f"📄 Overflow: {len(overflow_items)} items")
        click.echo(f"📊 Budget utilization: {total_tokens / budget * 100:.1f}%")
        click.echo(f"💾 Results saved to: {output}")
        click.echo(f"📋 Report saved to: {report}")
        
        # Show per-type breakdown
        click.echo(f"\n📊 Budget Allocation:")
        for budget_type, summary in budget_summary.items():
            click.echo(f"  {budget_type.upper()}: {summary['selected_items']}/{summary['total_items']} items ({summary['used_tokens']}/{summary['budget_limit']} tokens)")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


# Discovery Commands
@cli.command("discover:new")
@click.option("--product", required=True, help="Product name for discovery context")
@click.option("--idea", required=True, help="Short idea description")
@click.option("--problem", help="Problem this product solves")
@click.option("--users", help="Target users")
@click.option("--features", help="Key features (comma-separated)")
@click.option("--metrics", help="Success metrics")
@click.option("--tech", help="Technology stack preferences")
@click.option("--timeline", help="Project timeline")
@click.option("--team-size", help="Development team size")
@click.option("--question-set", default="new_product", help="Question set to use (new_product, existing_product, comprehensive)")
@click.option("--auto-generate", is_flag=True, help="Auto-generate discovery context")
@click.option("--output", default="builder/cache/discovery_context.yml", help="Output context file path")
def discover_new(product, idea, problem, users, features, metrics, tech, timeline, team_size, question_set, auto_generate, output):
    """Create a new discovery context for product development"""
    try:
        from discovery.engine import DiscoveryEngine
        import yaml
        from datetime import datetime
        
        click.echo(f"🔍 Creating discovery context for: {product}")
        click.echo(f"💡 Idea: {idea}")
        click.echo(f"📋 Question Set: {question_set}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create discovery context with batch inputs
        discovery_context = {
            'product': product,
            'idea': idea,
            'created': datetime.now().isoformat(),
            'status': 'draft',
            'question_set': question_set,
            'auto_generated': auto_generate,
            'discovery_phases': {
                'interview': {'completed': False, 'data': {}},
                'analysis': {'completed': False, 'data': {}},
                'synthesis': {'completed': False, 'data': {}},
                'generation': {'completed': False, 'data': {}},
                'validation': {'completed': False, 'data': {}}
            },
            'targets': [],
            'insights': [],
            'recommendations': [],
            'next_steps': []
        }
        
        # Add batch inputs if provided
        if problem:
            discovery_context['problem_solved'] = problem
        if users:
            discovery_context['target_users'] = users
        if features:
            # Split comma-separated features
            feature_list = [f.strip() for f in features.split(",") if f.strip()]
            discovery_context['key_features'] = feature_list
        if metrics:
            discovery_context['success_metrics'] = metrics
        if tech:
            discovery_context['tech_stack_preferences'] = tech
        if timeline:
            discovery_context['timeline'] = timeline
        if team_size:
            discovery_context['team_size'] = team_size
        
        # Auto-generate if requested
        if auto_generate:
            click.echo("🤖 Auto-generating discovery context...")
            
            # Prepare batch kwargs for discovery engine
            batch_kwargs = {
                'product': product,
                'idea': idea,
                'problem': problem,
                'users': users,
                'features': features,
                'metrics': metrics,
                'tech': tech,
                'timeline': timeline,
                'team_size': team_size
            }
            
            # Initialize discovery engine
            engine = DiscoveryEngine(question_set=question_set)
            
            # Run discovery with batch kwargs to generate user stories
            try:
                discovery_results = engine.discover(".", batch_kwargs=batch_kwargs)
                
                # Extract user stories from discovery results
                if 'interview' in discovery_results and 'questions' in discovery_results['interview']:
                    questions = discovery_results['interview']['questions']
                    if 'features_with_stories' in questions:
                        discovery_context['features_with_stories'] = questions['features_with_stories']
                        click.echo("📝 Generated user stories for features")
            except Exception as e:
                click.echo(f"⚠️  Warning: Could not generate user stories: {e}")
            
            # Fill in missing required fields for new products
            if 'problem_solved' not in discovery_context:
                discovery_context['problem_solved'] = f"Problem to be defined for {product}"
            if 'target_users' not in discovery_context:
                discovery_context['target_users'] = "Target users to be defined"
            if 'key_features' not in discovery_context:
                discovery_context['key_features'] = ["Feature 1", "Feature 2", "Feature 3"]
            if 'success_metrics' not in discovery_context:
                discovery_context['success_metrics'] = "Success metrics to be defined"
            if 'tech_stack_preferences' not in discovery_context:
                discovery_context['tech_stack_preferences'] = "Technology stack to be defined"
            if 'timeline' not in discovery_context:
                discovery_context['timeline'] = "Timeline to be defined"
            
            # Add some basic next steps
            discovery_context['next_steps'] = [
                f"Define requirements for {product}",
                f"Create architecture for {idea}",
                f"Identify key stakeholders for {product}",
                f"Plan development phases for {idea}",
                f"Set up testing strategy for {product}"
            ]
            
            # Add some initial insights
            discovery_context['insights'] = [
                f"Product '{product}' focuses on: {idea}",
                "Initial discovery phase completed",
                "Ready for detailed analysis phase"
            ]
            
            discovery_context['discovery_phases']['interview']['completed'] = True
            discovery_context['discovery_phases']['interview']['data'] = {
                'product_scope': idea,
                'complexity_estimate': 'medium',
                'stakeholders': ['product_owner', 'development_team', 'end_users']
            }
        
        # Save discovery context
        with open(output, 'w', encoding='utf-8') as f:
            yaml.dump(discovery_context, f, default_flow_style=False, sort_keys=False)
        
        click.echo(f"✅ Discovery context created successfully!")
        click.echo(f"📄 Saved to: {output}")
        click.echo(f"📊 Status: {discovery_context['status']}")
        
        # Show what was filled in
        filled_fields = [k for k, v in discovery_context.items() if k not in ["created", "status", "question_set", "auto_generated", "discovery_phases", "targets", "insights", "recommendations", "next_steps"] and v not in ["To be defined", "Target users to be defined", "Success metrics to be defined", "Technology stack to be defined", "Timeline to be defined"]]
        if filled_fields:
            click.echo(f"📝 Filled fields: {', '.join(filled_fields)}")
        
        if auto_generate:
            click.echo(f"🤖 Auto-generated with {len(discovery_context['next_steps'])} next steps")
            click.echo(f"💡 Generated {len(discovery_context['insights'])} initial insights")
        
        # Show next steps
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Run: python builder/cli.py discover:analyze --repo-root")
        click.echo(f"2. Run: python builder/cli.py discover:validate {output}")
        click.echo(f"3. Review generated context and refine as needed")
        click.echo(f"4. Run: python builder/cli.py discover:regenerate --batch")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


@cli.command("discover:analyze")
@click.option("--repo-root", is_flag=True, help="Analyze entire repository root")
@click.option("--target", help="Specific target path to analyze")
@click.option("--feature", default="", help="Feature name for analysis")
@click.option("--question-set", default="comprehensive", help="Question set to use (new_product, existing_product, comprehensive)")
@click.option("--output", default="builder/cache/discovery_analysis.json", help="Output analysis file path")
@click.option("--batch", is_flag=True, help="Run in batch mode (non-interactive)")
def discover_analyze(repo_root, target, feature, question_set, output, batch):
    """Analyze codebase using discovery engine"""
    try:
        from discovery.engine import DiscoveryEngine
        import json
        
        if not repo_root and not target:
            click.echo("❌ Error: Must specify either --repo-root or --target")
            raise SystemExit(1)
        
        # Initialize discovery engine with question set
        engine = DiscoveryEngine(question_set=question_set)
        
        if repo_root:
            click.echo("🔍 Analyzing entire repository...")
            analysis_target = "."
        else:
            click.echo(f"🔍 Analyzing target: {target}")
            analysis_target = target
        
        # Run discovery analysis
        results = engine.discover(analysis_target, {
            'feature': feature,
            'batch_mode': batch,
            'include_patterns': True,
            'include_security': True,
            'include_performance': True
        })
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save analysis results
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        if 'error' in results:
            click.echo(f"❌ Discovery failed: {results['error']}")
            raise SystemExit(1)
        
        # Show summary
        click.echo(f"✅ Discovery analysis completed!")
        click.echo(f"📄 Results saved to: {output}")
        click.echo(f"🎯 Target: {results.get('target', 'unknown')}")
        
        # Show key insights
        synthesis = results.get('synthesis', {})
        insights = synthesis.get('insights', [])
        if insights:
            click.echo(f"\n💡 Key Insights ({len(insights)}):")
            for i, insight in enumerate(insights[:3], 1):  # Show top 3
                click.echo(f"  {i}. {insight}")
            if len(insights) > 3:
                click.echo(f"  ... and {len(insights) - 3} more insights")
        
        # Show recommendations
        recommendations = synthesis.get('recommendations', [])
        if recommendations:
            click.echo(f"\n📋 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                click.echo(f"  {i}. {rec}")
            if len(recommendations) > 3:
                click.echo(f"  ... and {len(recommendations) - 3} more recommendations")
        
        # Show next steps
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Review analysis results in: {output}")
        click.echo(f"2. Run: python builder/cli.py discover:validate {output}")
        click.echo(f"3. Generate reports: python builder/cli.py discover:regenerate --reports")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


@cli.command("discover:validate")
@click.argument("context_file")
@click.option("--strict", is_flag=True, help="Use strict validation mode")
@click.option("--output", default="builder/cache/validation_report.json", help="Output validation report path")
def discover_validate(context_file, strict, output):
    """Validate discovery context or analysis results"""
    try:
        from discovery.validator import DiscoveryValidator
        import json
        import yaml
        from pathlib import Path
        
        click.echo(f"🔍 Validating: {context_file}")
        
        # Check if file exists
        if not Path(context_file).exists():
            click.echo(f"❌ Error: File not found: {context_file}")
            raise SystemExit(1)
        
        # Load file based on extension
        file_ext = Path(context_file).suffix.lower()
        if file_ext == '.json':
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_ext in ['.yml', '.yaml']:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            click.echo(f"❌ Error: Unsupported file format: {file_ext}")
            raise SystemExit(1)
        
        # Initialize validator
        validator = DiscoveryValidator()
        
        # Determine validation type based on data structure
        if 'discovery_phases' in data:
            # This is a discovery context file
            click.echo("📋 Validating discovery context...")
            validation_results = {
                'type': 'discovery_context',
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'checks': []
            }
            
            # Check required fields
            required_fields = ['product', 'idea', 'created', 'status', 'discovery_phases']
            for field in required_fields:
                if field not in data:
                    validation_results['errors'].append(f"Missing required field: {field}")
                    validation_results['is_valid'] = False
                else:
                    validation_results['checks'].append(f"Field '{field}' present")
            
            # Check discovery phases
            phases = data.get('discovery_phases', {})
            expected_phases = ['interview', 'analysis', 'synthesis', 'generation', 'validation']
            for phase in expected_phases:
                if phase not in phases:
                    validation_results['warnings'].append(f"Missing phase: {phase}")
                else:
                    validation_results['checks'].append(f"Phase '{phase}' present")
            
        elif 'synthesis' in data and 'analysis' in data:
            # This is a discovery analysis result
            click.echo("📊 Validating discovery analysis results...")
            generation_data = data.get('generation', {})
            synthesis_data = data.get('synthesis', {})
            validation_results = validator.validate(generation_data, synthesis_data)
        else:
            click.echo("❌ Error: Unknown file format - not a discovery context or analysis result")
            raise SystemExit(1)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save validation report
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2)
        
        # Show validation results
        if validation_results.get('is_valid', False):
            click.echo(f"✅ Validation passed!")
        else:
            click.echo(f"❌ Validation failed!")
        
        # Show errors
        errors = validation_results.get('errors', [])
        if errors:
            click.echo(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                click.echo(f"  - {error}")
        
        # Show warnings
        warnings = validation_results.get('warnings', [])
        if warnings:
            click.echo(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                click.echo(f"  - {warning}")
        
        # Show checks performed
        checks = validation_results.get('checks', [])
        if checks:
            click.echo(f"\n✅ Checks performed ({len(checks)}):")
            for check in checks[:5]:  # Show first 5
                click.echo(f"  - {check}")
            if len(checks) > 5:
                click.echo(f"  ... and {len(checks) - 5} more checks")
        
        click.echo(f"\n📄 Validation report saved to: {output}")
        
        # Show next steps
        if validation_results.get('is_valid', False):
            click.echo(f"\n🚀 Next Steps:")
            click.echo(f"1. Run: python builder/cli.py discover:regenerate --reports")
            click.echo(f"2. Review generated documentation")
            click.echo(f"3. Update discovery context as needed")
        else:
            click.echo(f"\n🔧 Fix Issues:")
            click.echo(f"1. Address validation errors above")
            click.echo(f"2. Re-run validation: python builder/cli.py discover:validate {context_file}")
            click.echo(f"3. Check file format and required fields")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


@cli.command("discover:refresh")
@click.option("--prd", required=True, help="PRD ID to refresh (e.g., PRD-2025-09-06-example)")
@click.option("--regenerate-docs", is_flag=True, help="Regenerate documentation after refresh")
@click.option("--regenerate-pack", is_flag=True, help="Regenerate context pack after refresh")
@click.option("--question-set", default="comprehensive", help="Question set to use for refresh")
def discover_refresh(prd, regenerate_docs, regenerate_pack, question_set):
    """Refresh a single PRD by re-running analysis and synthesis"""
    import yaml
    from pathlib import Path
    from discovery.engine import DiscoveryEngine
    from discovery.analyzer import CodeAnalyzer
    from discovery.synthesizer import DiscoverySynthesizer
    from discovery.validator import DiscoveryValidator
    from discovery.generators import DiscoveryGenerators
    
    try:
        # Load the PRD cache file
        prd_cache_file = Path("builder/cache/discovery") / f"{prd}.yml"
        if not prd_cache_file.exists():
            click.echo(f"❌ PRD cache file not found: {prd_cache_file}")
            click.echo("Available PRDs:")
            for prd_file in Path("builder/cache/discovery").glob("PRD-*.yml"):
                click.echo(f"  - {prd_file.stem}")
            raise SystemExit(1)
        
        # Load PRD data
        with open(prd_cache_file, 'r', encoding='utf-8') as f:
            prd_data = yaml.safe_load(f)
        
        click.echo(f"🔄 Refreshing PRD: {prd}")
        click.echo(f"📋 Product: {prd_data.get('product_name', 'Unknown')}")
        
        # Extract original discovery results
        discovery_results = prd_data.get('discovery_results', {})
        interview_data = discovery_results.get('interview', {})
        original_target = interview_data.get('target', '.')
        
        # Initialize discovery engine
        engine = DiscoveryEngine(question_set=question_set)
        
        # Re-run analysis
        click.echo("🔍 Re-running analysis...")
        analysis_data = engine.analyzer.analyze(Path(original_target), interview_data)
        
        # Re-run synthesis
        click.echo("🔄 Re-running synthesis...")
        synthesis_data = engine.synthesizer.synthesize(analysis_data, interview_data)
        
        # Re-run validation
        click.echo("✅ Re-running validation...")
        validation_data = engine.validator.validate(analysis_data, synthesis_data)
        
        # Update PRD cache with refreshed data
        prd_data['discovery_results']['analysis'] = analysis_data
        prd_data['discovery_results']['synthesis'] = synthesis_data
        prd_data['discovery_results']['validation'] = validation_data
        prd_data['last_refreshed'] = engine._get_timestamp()
        
        # Save updated PRD cache
        with open(prd_cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(prd_data, f, default_flow_style=False, sort_keys=False)
        
        click.echo(f"✅ PRD refreshed: {prd}")
        
        # Optional: Regenerate documentation
        if regenerate_docs:
            click.echo("📝 Regenerating documentation...")
            generators = DiscoveryGenerators()
            try:
                artifacts, warnings, new_prd_id = generators.generate(synthesis_data, Path(original_target))
                if warnings:
                    for warning in warnings:
                        click.echo(f"⚠️  {warning}")
                click.echo(f"✅ Documentation regenerated")
            except Exception as e:
                click.echo(f"⚠️  Documentation regeneration failed: {e}")
        
        # Optional: Regenerate context pack
        if regenerate_pack:
            click.echo("📦 Regenerating context pack...")
            try:
                # Try to run ctx:build on sensible paths
                engine._try_auto_ctx_build(Path(original_target))
                click.echo("✅ Context pack regenerated")
            except Exception as e:
                click.echo(f"⚠️  Context pack regeneration failed: {e}")
        
        click.echo(f"🎉 PRD refresh complete: {prd}")
        
    except Exception as e:
        click.echo(f"❌ Error refreshing PRD: {e}")
        raise SystemExit(1)

@cli.command("discover:scan")
@click.option("--auto-generate", is_flag=True, help="Auto-generate missing contexts")
@click.option("--pack", is_flag=True, help="Generate context packs for refreshed documents")
@click.option("--question-set", default="comprehensive", help="Question set to use for refresh")
@click.option("--type", default="all", help="Document type to scan (prd, adr, arch, exec, impl, integrations, tasks, ux, all)")
def discover_scan(auto_generate, pack, question_set, type):
    """Scan all documents and refresh stale or missing contexts"""
    import yaml
    import hashlib
    from pathlib import Path
    from discovery.engine import DiscoveryEngine
    
    try:
        # Determine document types to scan
        if type == "all":
            doc_types = ["prd", "adr", "arch", "exec", "impl", "integrations", "tasks", "ux"]
        else:
            doc_types = [type]
        
        click.echo(f"🔍 Scanning {', '.join(doc_types)} documents for freshness...")
        
        # Find all document files
        all_files = []
        for doc_type in doc_types:
            doc_dir = Path(f"docs/{doc_type}")
            if doc_type == "adr":
                # ADRs use different pattern
                pattern = "ADR-*.md"
            elif doc_type == "integrations":
                # Integrations use different pattern
                pattern = "INTEGRATIONS-*.md"
            else:
                # Other types use TYPE-*.md pattern
                pattern = f"{doc_type.upper()}-*.md"
            
            files = list(doc_dir.glob(pattern))
            all_files.extend(files)
            click.echo(f"📋 Found {len(files)} {doc_type.upper()} files")
        
        if not all_files:
            click.echo("❌ No document files found")
            return
        
        click.echo(f"📋 Total: {len(all_files)} documents")
        
        # Initialize discovery engine
        engine = DiscoveryEngine(question_set=question_set)
        
        refreshed_count = 0
        up_to_date_count = 0
        missing_count = 0
        
        for doc_file in all_files:
            doc_id = doc_file.stem  # e.g., "PRD-2025-09-06-payments", "ADR-2025-09-06-test"
            doc_type = _get_doc_type_from_file(doc_file)
            click.echo(f"\n🔍 Checking {doc_id} ({doc_type.upper()})...")
            
            # Check if document cache exists
            cache_file = Path("builder/cache/discovery") / f"{doc_id}.yml"
            
            if not cache_file.exists():
                click.echo(f"  ❌ Missing cache file: {cache_file}")
                if auto_generate:
                    # Determine discovery tier for this document type
                    discovery_tier = _get_discovery_tier(doc_type)
                    
                    if discovery_tier == "full":
                        # Tier 1: Full discovery context (PRD)
                        click.echo(f"  🔄 Auto-generating full discovery context for {doc_id}...")
                        try:
                            target = _extract_target_from_doc(doc_file) or "."
                            batch_kwargs = _extract_batch_kwargs_from_doc(doc_file)
                            results = engine.discover(target, batch_kwargs=batch_kwargs)
                            
                            generated_prd_id = results.get('prd_id')
                            if generated_prd_id == doc_id:
                                click.echo(f"  ✅ Generated full context for {doc_id}")
                                refreshed_count += 1
                            else:
                                click.echo(f"  🔄 Generated {generated_prd_id}, adapting for {doc_id}...")
                                _adapt_results_for_prd(results, doc_id, doc_file)
                                click.echo(f"  ✅ Generated full context for {doc_id}")
                                refreshed_count += 1
                        except Exception as e:
                            click.echo(f"  ❌ Error generating full context: {e}")
                            missing_count += 1
                    
                    elif discovery_tier == "targeted":
                        # Tier 2: Targeted discovery context (ARCH, IMPL)
                        click.echo(f"  🔄 Auto-generating targeted discovery context for {doc_id}...")
                        try:
                            _generate_targeted_discovery_context(doc_id, doc_file, doc_type)
                            click.echo(f"  ✅ Generated targeted context for {doc_id}")
                            refreshed_count += 1
                        except Exception as e:
                            click.echo(f"  ❌ Error generating targeted context: {e}")
                            missing_count += 1
                    
                    elif discovery_tier == "lightweight":
                        # Tier 3: Lightweight discovery context (ADR, EXEC, UX)
                        click.echo(f"  🔄 Auto-generating lightweight discovery context for {doc_id}...")
                        try:
                            _generate_lightweight_discovery_context(doc_id, doc_file, doc_type)
                            click.echo(f"  ✅ Generated lightweight context for {doc_id}")
                            refreshed_count += 1
                        except Exception as e:
                            click.echo(f"  ❌ Error generating lightweight context: {e}")
                            missing_count += 1
                    
                    else:
                        # Tier 4: Content hash only (TASKS, INTEGRATIONS)
                        click.echo(f"  ℹ️  {doc_type.upper()} documents use content hash tracking only")
                        missing_count += 1
                else:
                    missing_count += 1
                continue
            
            # Check freshness by comparing content hashes
            if _is_doc_stale(doc_file, cache_file):
                click.echo(f"  🔄 Stale cache detected, refreshing {doc_id}...")
                try:
                    # Use appropriate refresh logic based on discovery tier
                    discovery_tier = _get_discovery_tier(doc_type)
                    
                    if discovery_tier == "full":
                        # Tier 1: Full discovery refresh (PRD)
                        _refresh_prd_context(doc_id, question_set, pack)
                    elif discovery_tier == "targeted":
                        # Tier 2: Targeted discovery refresh (ARCH, IMPL)
                        _refresh_targeted_context(doc_id, doc_file, doc_type, pack)
                    elif discovery_tier == "lightweight":
                        # Tier 3: Lightweight discovery refresh (ADR, EXEC, UX)
                        _refresh_lightweight_context(doc_id, doc_file, doc_type)
                    else:
                        # Tier 4: Content hash only (TASKS, INTEGRATIONS)
                        _update_doc_content_hash(doc_id, doc_file)
                    
                    click.echo(f"  ✅ Refreshed {doc_id}")
                    refreshed_count += 1
                except Exception as e:
                    click.echo(f"  ❌ Error refreshing {doc_id}: {e}")
                    missing_count += 1
            else:
                click.echo(f"  ✅ Up-to-date: {doc_id}")
                up_to_date_count += 1
        
        # Print summary
        click.echo(f"\n📊 Scan Summary:")
        click.echo(f"  🔄 Refreshed: {refreshed_count}")
        click.echo(f"  ✅ Up-to-date: {up_to_date_count}")
        click.echo(f"  ❌ Missing/Failed: {missing_count}")
        click.echo(f"  📋 Total: {len(all_files)}")
        
    except Exception as e:
        click.echo(f"❌ Error during scan: {e}")
        raise SystemExit(1)

@cli.command("discover:regenerate")
@click.option("--batch", is_flag=True, help="Run in batch mode (non-interactive)")
@click.option("--reports", is_flag=True, help="Generate reports only")
@click.option("--docs", is_flag=True, help="Generate documentation only")
@click.option("--diagrams", is_flag=True, help="Generate diagrams only")
@click.option("--all", is_flag=True, help="Generate all outputs")
@click.option("--input", default="builder/cache/discovery_analysis.json", help="Input analysis file path")
@click.option("--output-dir", default="builder/cache/discovery_outputs", help="Output directory for generated files")
def discover_regenerate(batch, reports, docs, diagrams, all, input, output_dir):
    """Regenerate discovery outputs from analysis results"""
    try:
        from discovery.generators import DiscoveryGenerators
        import json
        from pathlib import Path
        
        # Determine what to generate
        if all:
            generate_reports = True
            generate_docs = True
            generate_diagrams = True
        else:
            generate_reports = reports
            generate_docs = docs
            generate_diagrams = diagrams
            
            # If nothing specified, generate reports by default
            if not any([reports, docs, diagrams]):
                generate_reports = True
        
        click.echo(f"🔄 Regenerating discovery outputs...")
        click.echo(f"📁 Input: {input}")
        click.echo(f"📁 Output: {output_dir}")
        
        # Check if input file exists
        if not Path(input).exists():
            click.echo(f"❌ Error: Input file not found: {input}")
            raise SystemExit(1)
        
        # Load analysis results
        with open(input, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        if 'error' in analysis_data:
            click.echo(f"❌ Error: Analysis file contains error: {analysis_data['error']}")
            raise SystemExit(1)
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize generators
        generators = DiscoveryGenerators()
        
        # Get synthesis data
        synthesis_data = analysis_data.get('synthesis', {})
        if not synthesis_data:
            click.echo(f"❌ Error: No synthesis data found in analysis file")
            raise SystemExit(1)
        
        # Generate outputs
        target_path = Path(analysis_data.get('target', 'unknown'))
        generation_data = generators.generate(synthesis_data, target_path)
        
        # Save generated outputs
        generated_files = []
        
        if generate_reports:
            click.echo("📄 Generating reports...")
            reports = generation_data.get('reports', {})
            for format_name, content in reports.items():
                report_file = Path(output_dir) / f"discovery_report.{format_name}"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(str(report_file))
                click.echo(f"  ✅ {format_name.upper()} report: {report_file}")
        
        if generate_docs:
            click.echo("📚 Generating documentation...")
            documentation = generation_data.get('documentation', {})
            for doc_name, content in documentation.items():
                doc_file = Path(output_dir) / f"{doc_name.lower()}.md"
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(str(doc_file))
                click.echo(f"  ✅ {doc_name} documentation: {doc_file}")
        
        if generate_diagrams:
            click.echo("📊 Generating diagrams...")
            diagrams = generation_data.get('diagrams', {})
            for diagram_name, content in diagrams.items():
                diagram_file = Path(output_dir) / diagram_name
                with open(diagram_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(str(diagram_file))
                click.echo(f"  ✅ {diagram_name} diagram: {diagram_file}")
        
        # Generate recommendations
        recommendations = generation_data.get('recommendations', {})
        if recommendations:
            click.echo("📋 Generating recommendations...")
            for rec_name, content in recommendations.items():
                rec_file = Path(output_dir) / rec_name
                with open(rec_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                generated_files.append(str(rec_file))
                click.echo(f"  ✅ {rec_name} recommendations: {rec_file}")
        
        # Save generation metadata
        metadata = generation_data.get('metadata', {})
        metadata_file = Path(output_dir) / "generation_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        generated_files.append(str(metadata_file))
        
        click.echo(f"\n✅ Discovery outputs regenerated successfully!")
        click.echo(f"📁 Generated {len(generated_files)} files in: {output_dir}")
        
        # Show generated files
        click.echo(f"\n📄 Generated Files:")
        for file_path in generated_files:
            click.echo(f"  - {file_path}")
        
        # Show next steps
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Review generated outputs in: {output_dir}")
        click.echo(f"2. Share reports with stakeholders")
        click.echo(f"3. Update discovery context based on findings")
        click.echo(f"4. Run: python builder/cli.py discover:analyze --repo-root (to re-analyze)")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
