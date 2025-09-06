#!/usr/bin/env python3
"""
Field Name Validator - Ensures consistent field names across data structures.

This module validates that field names used in validation scripts match
the actual field names in generated data structures.
"""

import json
import re
from typing import Dict, List, Any, Tuple, Set
from pathlib import Path


class FieldNameValidator:
    """Validates field name consistency across data structures and validation code."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.known_field_mappings = {
            'context_pack': {
                'acceptance_criteria': 'acceptance_criteria',  # Correct field name
                'acceptance': 'acceptance_criteria',  # Common mistake
                'rules_markdown': 'rules_markdown',
                'code_excerpts': 'code_excerpts',
                'test_excerpts': 'test_excerpts',
                'target_path': 'target_path',
                'purpose': 'purpose',
                'feature': 'feature',
                'stacks': 'stacks'
            }
        }
    
    def validate_context_pack_fields(self, context_pack_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that a context pack has the expected field names.
        
        Args:
            context_pack_path: Path to the context pack JSON file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(context_pack_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"Could not read context pack file: {e}")
            return False, self.errors, self.warnings
        
        # Check for required fields
        required_fields = [
            'target_path', 'purpose', 'feature', 'stacks',
            'rules', 'prd', 'adrs', 'code_excerpts', 
            'test_excerpts', 'acceptance_criteria'
        ]
        
        for field in required_fields:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
        
        # Check rules structure
        if 'rules' in data:
            rules = data['rules']
            if not isinstance(rules, dict):
                self.errors.append("'rules' field must be a dictionary")
            else:
                if 'rules_markdown' not in rules:
                    self.errors.append("Missing 'rules_markdown' in rules")
                if 'guardrails' not in rules:
                    self.warnings.append("Missing 'guardrails' in rules")
                if 'conflicts' not in rules:
                    self.warnings.append("Missing 'conflicts' in rules")
                if 'sources' not in rules:
                    self.warnings.append("Missing 'sources' in rules")
        
        # Check for common field name mistakes
        if 'acceptance' in data and 'acceptance_criteria' not in data:
            self.errors.append("Found 'acceptance' field but should be 'acceptance_criteria'")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def validate_validation_script(self, script_path: str, data_structure: str = 'context_pack') -> Tuple[bool, List[str], List[str]]:
        """
        Validate that a validation script uses correct field names.
        
        Args:
            script_path: Path to the validation script
            data_structure: Type of data structure being validated
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Could not read script file: {e}")
            return False, self.errors, self.warnings
        
        if data_structure not in self.known_field_mappings:
            self.warnings.append(f"Unknown data structure: {data_structure}")
            return True, self.errors, self.warnings
        
        field_mappings = self.known_field_mappings[data_structure]
        
        # Check for incorrect field names
        for wrong_field, correct_field in field_mappings.items():
            if wrong_field != correct_field:  # Only check for mistakes
                pattern = rf"data\.get\(['\"]{re.escape(wrong_field)}['\"]"
                if re.search(pattern, content):
                    self.errors.append(f"Script uses '{wrong_field}' but should use '{correct_field}'")
        
        # Check for correct field names
        for field in field_mappings.values():
            pattern = rf"data\.get\(['\"]{re.escape(field)}['\"]"
            if re.search(pattern, content):
                self.warnings.append(f"Script correctly uses '{field}' field")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def find_field_name_issues(self, directory: str) -> Dict[str, List[str]]:
        """
        Find potential field name issues in a directory.
        
        Args:
            directory: Directory to search for issues
            
        Returns:
            Dictionary mapping file paths to lists of issues
        """
        issues = {}
        
        # Search for common field name mistakes
        patterns = {
            r"data\.get\(['\"]acceptance['\"]": "Use 'acceptance_criteria' instead of 'acceptance'",
            r"data\['acceptance'\]": "Use 'acceptance_criteria' instead of 'acceptance'",
            r"data\[\"acceptance\"\]": "Use 'acceptance_criteria' instead of 'acceptance'",
        }
        
        for file_path in Path(directory).rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_issues = []
                for pattern, message in patterns.items():
                    if re.search(pattern, content):
                        file_issues.append(message)
                
                if file_issues:
                    issues[str(file_path)] = file_issues
                    
            except Exception:
                continue
        
        # Also check YAML files for similar issues
        for file_path in Path(directory).rglob('*.yml'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_issues = []
                for pattern, message in patterns.items():
                    if re.search(pattern, content):
                        file_issues.append(message)
                
                if file_issues:
                    issues[str(file_path)] = file_issues
                    
            except Exception:
                continue
        
        return issues


def validate_context_pack_fields(context_pack_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate context pack field names.
    
    Args:
        context_pack_path: Path to the context pack JSON file
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = FieldNameValidator()
    return validator.validate_context_pack_fields(context_pack_path)


def validate_validation_script(script_path: str, data_structure: str = 'context_pack') -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate script field names.
    
    Args:
        script_path: Path to the validation script
        data_structure: Type of data structure being validated
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = FieldNameValidator()
    return validator.validate_validation_script(script_path, data_structure)


def find_field_name_issues(directory: str) -> Dict[str, List[str]]:
    """
    Convenience function to find field name issues.
    
    Args:
        directory: Directory to search for issues
        
    Returns:
        Dictionary mapping file paths to lists of issues
    """
    validator = FieldNameValidator()
    return validator.find_field_name_issues(directory)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--find-issues':
            # Find field name issues in directory
            directory = sys.argv[2] if len(sys.argv) > 2 else '.'
            issues = find_field_name_issues(directory)
            
            if issues:
                print("Found field name issues:")
                for file_path, file_issues in issues.items():
                    print(f"\n{file_path}:")
                    for issue in file_issues:
                        print(f"  - {issue}")
            else:
                print("No field name issues found")
        else:
            # Validate specific file
            file_path = sys.argv[1]
            if file_path.endswith('.json'):
                is_valid, errors, warnings = validate_context_pack_fields(file_path)
                print(f"Validating context pack: {file_path}")
            else:
                is_valid, errors, warnings = validate_validation_script(file_path)
                print(f"Validating script: {file_path}")
            
            if warnings:
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
            
            if is_valid:
                print("  ✅ Valid")
            else:
                print("  ❌ Invalid")
                sys.exit(1)
    else:
        print("Usage:")
        print("  python field_name_validator.py <file>")
        print("  python field_name_validator.py --find-issues [directory]")
