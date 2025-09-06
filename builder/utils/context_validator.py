#!/usr/bin/env python3
"""
Context Pack Validator - Ensures context packs meet quality standards.

This module provides validation functions to prevent context pack generation
errors and ensure all required fields are populated with meaningful content.
"""

from typing import Dict, List, Any, Tuple
import os


class ContextPackValidator:
    """Validates context packs to ensure they meet quality standards."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, context_pack: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a context pack and return validation results.
        
        Args:
            context_pack: The context pack dictionary to validate
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate required structure
        self._validate_structure(context_pack)
        
        # Validate rules content
        self._validate_rules(context_pack)
        
        # Validate acceptance criteria
        self._validate_acceptance_criteria(context_pack)
        
        # Validate code excerpts
        self._validate_code_excerpts(context_pack)
        
        # Validate target file
        self._validate_target_file(context_pack)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_structure(self, context_pack: Dict[str, Any]) -> None:
        """Validate basic structure of context pack."""
        required_fields = [
            'target_path', 'purpose', 'feature', 'stacks',
            'rules', 'prd', 'adrs', 'code_excerpts', 
            'test_excerpts', 'acceptance_criteria'
        ]
        
        for field in required_fields:
            if field not in context_pack:
                self.errors.append(f"Missing required field: {field}")
    
    def _validate_rules(self, context_pack: Dict[str, Any]) -> None:
        """Validate rules content."""
        rules = context_pack.get('rules', {})
        rules_markdown = rules.get('rules_markdown', '')
        
        if not rules_markdown or rules_markdown.strip() == '':
            self.errors.append("rules_markdown is empty - check RULES_DIR path and rules loading")
        elif len(rules_markdown.strip()) < 50:
            self.warnings.append("rules_markdown seems too short (less than 50 characters)")
    
    def _validate_acceptance_criteria(self, context_pack: Dict[str, Any]) -> None:
        """Validate acceptance criteria content."""
        acceptance_criteria = context_pack.get('acceptance_criteria', [])
        
        if not acceptance_criteria or len(acceptance_criteria) == 0:
            self.errors.append("acceptance_criteria is empty - implement fallback generation")
        elif len(acceptance_criteria) < 3:
            self.warnings.append(f"acceptance_criteria has only {len(acceptance_criteria)} items - consider adding more")
        
        # Check content quality
        if acceptance_criteria:
            total_text = ' '.join([str(item) for item in acceptance_criteria])
            if len(total_text.strip()) < 20:
                self.warnings.append("acceptance_criteria content seems too short")
    
    def _validate_code_excerpts(self, context_pack: Dict[str, Any]) -> None:
        """Validate code excerpts content."""
        code_excerpts = context_pack.get('code_excerpts', [])
        
        if not code_excerpts or len(code_excerpts) == 0:
            self.errors.append("code_excerpts is empty - check target file exists and is readable")
        elif len(code_excerpts) < 1:
            self.warnings.append("code_excerpts has no excerpts - target file may be empty")
    
    def _validate_target_file(self, context_pack: Dict[str, Any]) -> None:
        """Validate target file exists and is accessible."""
        target_path = context_pack.get('target_path', '')
        
        if not target_path:
            self.errors.append("target_path is empty")
            return
        
        if not os.path.exists(target_path):
            self.errors.append(f"target_path does not exist: {target_path}")
        elif not os.path.isfile(target_path):
            self.errors.append(f"target_path is not a file: {target_path}")
        elif os.path.getsize(target_path) == 0:
            self.warnings.append(f"target_path is empty: {target_path}")


def validate_context_pack(context_pack: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a context pack.
    
    Args:
        context_pack: The context pack dictionary to validate
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = ContextPackValidator()
    return validator.validate(context_pack)


def validate_context_pack_file(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a context pack from a JSON file.
    
    Args:
        file_path: Path to the context pack JSON file
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    import json
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            context_pack = json.load(f)
        return validate_context_pack(context_pack)
    except FileNotFoundError:
        return False, [f"Context pack file not found: {file_path}"], []
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in context pack file: {e}"], []
    except Exception as e:
        return False, [f"Error reading context pack file: {e}"], []
