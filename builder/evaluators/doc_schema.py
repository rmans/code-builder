#!/usr/bin/env python3
"""
Document schema validator for front-matter validation.
Ensures document structure integrity across all document types.
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Schema definitions for each document type
DOCUMENT_SCHEMAS = {
    'prd': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee'],
        'status_enum': ['draft', 'review', 'approved', 'archived'],
        'type_must_be': 'prd'
    },
    'arch': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'decision_date'],
        'status_enum': ['draft', 'review', 'approved', 'superseded', 'archived'],
        'type_must_be': 'arch'
    },
    'integrations': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'endpoint'],
        'status_enum': ['draft', 'review', 'approved', 'deprecated', 'archived'],
        'type_must_be': 'integrations'
    },
    'ux': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'designer'],
        'status_enum': ['draft', 'review', 'approved', 'archived'],
        'type_must_be': 'ux'
    },
    'impl': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'tech_stack'],
        'status_enum': ['draft', 'review', 'approved', 'deprecated', 'archived'],
        'type_must_be': 'impl'
    },
    'exec': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'stakeholders'],
        'status_enum': ['draft', 'review', 'approved', 'archived'],
        'type_must_be': 'exec'
    },
    'tasks': {
        'required_keys': ['type', 'id', 'title', 'status', 'owner', 'created', 'links'],
        'optional_keys': ['tags', 'priority', 'assignee', 'due_date', 'estimated_hours'],
        'status_enum': ['draft', 'in_progress', 'review', 'completed', 'cancelled', 'archived'],
        'type_must_be': 'tasks'
    }
}

def parse_front_matter(content: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Parse YAML front-matter from document content.
    Returns (metadata_dict, error_message) tuple.
    """
    if not content.startswith('---'):
        return None, "Document does not start with front-matter delimiter (---)"
    
    try:
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None, "Invalid front-matter structure - missing closing delimiter"
        
        yaml_content = parts[1].strip()
        if not yaml_content:
            return None, "Empty front-matter section"
        
        metadata = yaml.safe_load(yaml_content)
        if not isinstance(metadata, dict):
            return None, "Front-matter is not a valid YAML object"
        
        return metadata, None
        
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error parsing front-matter: {str(e)}"

def validate_document_metadata(metadata: Dict[str, Any], doc_type: str) -> tuple[bool, List[str]]:
    """
    Validate document metadata against schema.
    Returns (is_valid, error_messages) tuple.
    """
    if doc_type not in DOCUMENT_SCHEMAS:
        return False, [f"Unknown document type: {doc_type}"]
    
    schema = DOCUMENT_SCHEMAS[doc_type]
    errors = []
    
    # Check required keys
    for key in schema['required_keys']:
        if key not in metadata:
            errors.append(f"Missing required key: {key}")
    
    # Check type field
    if 'type' in metadata and metadata['type'] != schema['type_must_be']:
        errors.append(f"Type mismatch: expected '{schema['type_must_be']}', got '{metadata['type']}'")
    
    # Check status enum
    if 'status' in metadata:
        status = metadata['status']
        if status not in schema['status_enum']:
            valid_statuses = ', '.join(schema['status_enum'])
            errors.append(f"Invalid status '{status}'. Valid values: {valid_statuses}")
    
    # Check links structure
    if 'links' in metadata:
        links = metadata['links']
        if not isinstance(links, (dict, list)):
            errors.append("Links must be a dictionary or list")
        elif isinstance(links, list):
            # Validate list of dictionaries structure
            for i, link_item in enumerate(links):
                if not isinstance(link_item, dict):
                    errors.append(f"Link item {i} must be a dictionary")
                else:
                    for link_type, link_ids in link_item.items():
                        if not isinstance(link_ids, list):
                            errors.append(f"Link '{link_type}' must be a list of IDs")
    
    # Check ID format
    if 'id' in metadata:
        doc_id = metadata['id']
        expected_prefix = doc_type.upper()
        if not doc_id.startswith(expected_prefix):
            errors.append(f"ID should start with '{expected_prefix}': {doc_id}")
    
    # Check created date format
    if 'created' in metadata:
        created = metadata['created']
        if hasattr(created, 'isoformat'):
            # Convert date/datetime object to string
            created = created.isoformat()
        elif not isinstance(created, str):
            errors.append("Created date must be a string or date object")
        elif len(created) < 8:  # At least YYYY-MM-DD
            errors.append("Created date must be in YYYY-MM-DD format")
    
    return len(errors) == 0, errors

def validate_document_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a single document file.
    Returns validation result dictionary.
    """
    result = {
        'file_path': file_path,
        'valid': False,
        'errors': [],
        'warnings': [],
        'metadata': None,
        'doc_type': None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['errors'].append(f"Failed to read file: {str(e)}")
        return result
    
    # Parse front-matter
    metadata, parse_error = parse_front_matter(content)
    if parse_error:
        result['errors'].append(parse_error)
        return result
    
    result['metadata'] = metadata
    
    # Determine document type from file path or metadata
    doc_type = None
    if 'type' in metadata:
        doc_type = metadata['type']
    else:
        # Try to infer from file path
        path_parts = file_path.split(os.sep)
        if 'prd' in path_parts:
            doc_type = 'prd'
        elif 'arch' in path_parts:
            doc_type = 'arch'
        elif 'integrations' in path_parts:
            doc_type = 'integrations'
        elif 'ux' in path_parts:
            doc_type = 'ux'
        elif 'impl' in path_parts:
            doc_type = 'impl'
        elif 'exec' in path_parts:
            doc_type = 'exec'
        elif 'tasks' in path_parts:
            doc_type = 'tasks'
    
    if not doc_type:
        result['errors'].append("Could not determine document type")
        return result
    
    result['doc_type'] = doc_type
    
    # Validate metadata
    is_valid, validation_errors = validate_document_metadata(metadata, doc_type)
    result['valid'] = is_valid
    result['errors'].extend(validation_errors)
    
    # Add warnings for optional but recommended fields
    if 'owner' in metadata and metadata['owner'] == 'TBD':
        result['warnings'].append("Owner is set to 'TBD' - consider assigning a real owner")
    
    if 'status' in metadata and metadata['status'] == 'draft':
        result['warnings'].append("Document is in draft status")
    
    return result

def validate_documents_in_directory(directory: str) -> Dict[str, Any]:
    """
    Validate all documents in a directory and subdirectories.
    Returns comprehensive validation report.
    """
    results = []
    total_files = 0
    valid_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                total_files += 1
                
                result = validate_document_file(file_path)
                results.append(result)
                
                if result['valid']:
                    valid_files += 1
    
    return {
        'summary': {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': total_files - valid_files,
            'validation_rate': valid_files / total_files if total_files > 0 else 0
        },
        'results': results,
        'schema_definitions': DOCUMENT_SCHEMAS
    }

def save_schema_report(report: Dict[str, Any], output_path: str) -> None:
    """Save validation report to JSON file."""
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj
    
    serializable_report = make_serializable(report)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Test the validator
    import sys
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        result = validate_document_file(test_file)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python doc_schema.py <file_path>")
