#!/usr/bin/env python3
"""
Tests for context pack validator.
"""

import tempfile
import os
import json
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from builder.utils.context_validator import ContextPackValidator, validate_context_pack, validate_context_pack_file


class TestContextPackValidator:
    """Test cases for context pack validation."""
    
    def test_valid_context_pack(self):
        """Test validation of a valid context pack."""
        # Use a real file that exists
        context_pack = {
            'target_path': 'builder/test_data/hello_good.ts',  # Real file
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': 'Some rules content that is long enough to pass validation',
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [{'path': 'builder/test_data/hello_good.ts', 'excerpt': 'code content', 'line_count': 10}],
            'test_excerpts': [],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2', 'Criteria 3']
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert is_valid
        assert len(errors) == 0
        assert len(warnings) == 0
    
    def test_missing_rules_markdown(self):
        """Test validation catches empty rules_markdown."""
        context_pack = {
            'target_path': 'builder/test_data/hello_good.ts',  # Real file
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': '',  # Empty rules
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [{'path': 'builder/test_data/hello_good.ts', 'excerpt': 'code content', 'line_count': 10}],
            'test_excerpts': [],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2', 'Criteria 3']
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert not is_valid
        assert any('rules_markdown is empty' in error for error in errors)
    
    def test_missing_acceptance_criteria(self):
        """Test validation catches empty acceptance_criteria."""
        context_pack = {
            'target_path': 'builder/test_data/hello_good.ts',  # Real file
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': 'Some rules content that is long enough to pass validation',
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [{'path': 'builder/test_data/hello_good.ts', 'excerpt': 'code content', 'line_count': 10}],
            'test_excerpts': [],
            'acceptance_criteria': []  # Empty acceptance criteria
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert not is_valid
        assert any('acceptance_criteria is empty' in error for error in errors)
    
    def test_missing_code_excerpts(self):
        """Test validation catches empty code_excerpts."""
        context_pack = {
            'target_path': 'builder/test_data/hello_good.ts',  # Real file
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': 'Some rules content that is long enough to pass validation',
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [],  # Empty code excerpts
            'test_excerpts': [],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2', 'Criteria 3']
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert not is_valid
        assert any('code_excerpts is empty' in error for error in errors)
    
    def test_missing_target_file(self):
        """Test validation catches missing target file."""
        context_pack = {
            'target_path': 'nonexistent/file.ts',  # File doesn't exist
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': 'Some rules content that is long enough to pass validation',
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [{'path': 'test/file.ts', 'excerpt': 'code content', 'line_count': 10}],
            'test_excerpts': [],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2', 'Criteria 3']
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert not is_valid
        assert any('target_path does not exist' in error for error in errors)
    
    def test_short_rules_warning(self):
        """Test validation warns about short rules content."""
        context_pack = {
            'target_path': 'builder/test_data/hello_good.ts',  # Real file
            'purpose': 'implement',
            'feature': 'typescript',
            'stacks': ['typescript'],
            'rules': {
                'rules_markdown': 'Short',  # Too short
                'guardrails': {},
                'conflicts': [],
                'sources': []
            },
            'prd': {'content': 'PRD content', 'metadata': {}},
            'adrs': [],
            'code_excerpts': [{'path': 'builder/test_data/hello_good.ts', 'excerpt': 'code content', 'line_count': 10}],
            'test_excerpts': [],
            'acceptance_criteria': ['Criteria 1', 'Criteria 2', 'Criteria 3']
        }
        
        is_valid, errors, warnings = validate_context_pack(context_pack)
        assert is_valid  # Should still be valid
        assert any('rules_markdown seems too short' in warning for warning in warnings)
    
    def test_validate_context_pack_file(self):
        """Test validation from file."""
        # Create a temporary file with invalid context pack
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_context = {
                'target_path': 'test/file.ts',
                'purpose': 'implement',
                'feature': 'typescript',
                'stacks': ['typescript'],
                'rules': {'rules_markdown': ''},  # Invalid
                'prd': {'content': 'PRD content', 'metadata': {}},
                'adrs': [],
                'code_excerpts': [],
                'test_excerpts': [],
                'acceptance_criteria': []
            }
            json.dump(invalid_context, f)
            temp_file = f.name
        
        try:
            is_valid, errors, warnings = validate_context_pack_file(temp_file)
            assert not is_valid
            assert len(errors) > 0
        finally:
            os.unlink(temp_file)
    
    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        is_valid, errors, warnings = validate_context_pack_file('nonexistent.json')
        assert not is_valid
        assert any('not found' in error for error in errors)
    
    def test_validate_invalid_json(self):
        """Test validation of invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            temp_file = f.name
        
        try:
            is_valid, errors, warnings = validate_context_pack_file(temp_file)
            assert not is_valid
            assert any('Invalid JSON' in error for error in errors)
        finally:
            os.unlink(temp_file)


def run_tests():
    """Run all tests."""
    test_class = TestContextPackValidator()
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        method = getattr(test_class, method_name)
        try:
            print(f"Running {method_name}...")
            method()
            print(f"✅ {method_name} passed")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
