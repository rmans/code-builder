#!/usr/bin/env python3
"""
Artifact detector for Code Builder ABC iterations.
Identifies file types based on extensions, content patterns, and front-matter.
"""

import os
import re
import yaml
from typing import Dict, Any, Literal

def extract_front_matter(path: str) -> Dict[str, Any]:
    """
    Parse YAML front-matter between --- markers.
    Returns empty dict if none found.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML front-matter
        if not content.startswith('---\n'):
            return {}
        
        # Find the end of front-matter
        end_marker = content.find('\n---\n', 4)
        if end_marker == -1:
            return {}
        
        # Extract YAML content
        yaml_content = content[4:end_marker]
        
        # Parse YAML
        return yaml.safe_load(yaml_content) or {}
    
    except Exception:
        return {}

def detect_artifact_type(path: str) -> Literal['code', 'prd', 'adr', 'task']:
    """
    Detect artifact type based on file path, content, and front-matter.
    
    Rules:
    - .ts/.tsx/.js/.jsx -> 'code'
    - Contains 'ADR-' -> 'adr'  
    - Contains 'SPEC_' or 'PRD' -> 'prd'
    - Has YAML front-matter with 'type: task' -> 'task'
    - Default -> 'task'
    """
    # Check file extension for code files
    _, ext = os.path.splitext(path.lower())
    if ext in ['.ts', '.tsx', '.js', '.jsx']:
        return 'code'
    
    # Check filename patterns
    filename = os.path.basename(path)
    
    # ADR pattern
    if 'ADR-' in filename:
        return 'adr'
    
    # PRD/SPEC pattern
    if 'SPEC_' in filename or 'PRD' in filename:
        return 'prd'
    
    # Check front-matter for explicit type
    front_matter = extract_front_matter(path)
    if front_matter and 'type' in front_matter:
        artifact_type = front_matter['type']
        if artifact_type in ['code', 'prd', 'adr', 'task']:
            return artifact_type
    
    # Default to task
    return 'task'

def test_detector():
    """Test the artifact detector with current repo files"""
    print("=== Artifact Detector Test ===")
    
    # Test files from the repo
    test_files = [
        "src/hello.ts",
        "src/index.ts", 
        "src/utils/http.ts",
        "test/hello.test.ts",
        "vitest.config.ts",
        "docs/SPEC_hello.md",
        "docs/adrs/ADR-0001.md",
        "docs/adrs/ADR-0002.md",
        "docs/rules/00-global.md",
        "docs/rules/10-project.md",
        "docs/eval/config.yaml",
        "package.json",
        "README.md"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            artifact_type = detect_artifact_type(file_path)
            front_matter = extract_front_matter(file_path)
            print(f"{file_path:<30} -> {artifact_type:<6} (front-matter: {bool(front_matter)})")
        else:
            print(f"{file_path:<30} -> NOT FOUND")

if __name__ == "__main__":
    test_detector()
