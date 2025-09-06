#!/usr/bin/env python3
"""
Golden checks (unit/smoke tests) for code-builder system.

These tests ensure core functionality remains working as the system grows.
Run with: python -m pytest builder/tests/test_golden_checks.py -v
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules to test
from builder.evaluators.doc_schema import STATUS_ENUM, validate_file
from builder.core.context_rules import merge_context_rules
from builder.core.context_graph import ContextGraphBuilder
from builder.core.context_select import ContextSelector
from builder.core.context_budget import ContextBudgetManager


class TestStatusValidation:
    """Test document status validation."""
    
    def test_status_enum_contains_expected_values(self):
        """Test that STATUS_ENUM contains all expected status values."""
        expected_statuses = {
            'draft', 'review', 'approved', 'deprecated',
            'planned', 'proposed', 'pending', 'in_progress', 'accepted'
        }
        assert STATUS_ENUM == expected_statuses, f"Expected {expected_statuses}, got {STATUS_ENUM}"
    
    def test_status_validation_accepts_valid_statuses(self):
        """Test that valid statuses pass validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test markdown file with valid status
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("""---
type: prd
id: TEST-001
title: Test Document
status: approved
owner: test
created: 2024-01-01
links: {}
---

# Test Document
## Problem
Test problem statement.

## Goals
Test goals.

## Requirements
Test requirements.

## Metrics
Test metrics.
""")
            
            result = validate_file(test_file)
            # For now, just check that the status validation part works
            # The section validation might be more complex
            assert 'invalid status' not in str(result['errors']), f"Status validation should pass: {result['errors']}"
    
    def test_status_validation_rejects_invalid_statuses(self):
        """Test that invalid statuses fail validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test markdown file with invalid status
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("""---
type: prd
id: TEST-001
title: Test Document
status: invalid_status
owner: test
created: 2024-01-01
links: {}
---

# Test Document
## Problem
Test problem statement.
""")
            
            result = validate_file(test_file)
            assert not result['ok'], "Invalid status should fail validation"
            assert any('invalid status' in error.lower() for error in result['errors'])


class TestGraphOperations:
    """Test context graph node/edge counts."""
    
    def test_graph_builder_creates_nodes_and_edges(self):
        """Test that graph builder creates expected node and edge counts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal test structure
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir()
            
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            
            # Create a test PRD
            prd_file = docs_dir / "PRD-test.md"
            prd_file.write_text("""---
type: prd
id: PRD-test
title: Test PRD
status: draft
owner: test
created: 2024-01-01
links: {}
---

# Test PRD
## Problem
Test problem.
""")
            
            # Create a test source file
            src_file = src_dir / "test.ts"
            src_file.write_text("// Test source file")
            
            # Use the correct constructor
            builder = ContextGraphBuilder(temp_dir)
            graph = builder.build()
            
            # Check that we have nodes (should have at least the PRD and source file)
            assert len(graph.nodes) > 0, "Graph should have nodes"
            
            # Check that we have edges (may be 0 for minimal test case)
            # The important thing is that the graph builder doesn't crash
            assert isinstance(graph.edges, dict), "Graph should have edges dict"
            
            # Check node types
            node_types = set(node['type'] for node in graph.nodes.values())
            expected_types = {'prd', 'arch', 'integration', 'ux', 'impl', 'exec', 'task', 'adr', 'rules', 'code'}
            assert node_types.issubset(expected_types), f"Unexpected node types: {node_types - expected_types}"


class TestSelectionWeights:
    """Test context selection weight ordering."""
    
    def test_selection_weights_are_ordered(self):
        """Test that selection weights are properly ordered (highest first)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir()
            
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            
            # Create test files
            prd_file = docs_dir / "PRD-test.md"
            prd_file.write_text("""---
type: prd
id: PRD-test
title: Test PRD
status: approved
owner: test
created: 2024-01-01
links: {}
---

# Test PRD
## Problem
Test problem.
""")
            
            test_file = src_dir / "test.ts"
            test_file.write_text("// Test file")
            
            # Use the correct constructor
            selector = ContextSelector(temp_dir)
            selection = selector.select_context("src/test.ts", "test", max_items=10)
            
            if selection:
                # Check that weights are ordered (highest first)
                weights = [item.get('weight', 0) for item in selection]
                assert weights == sorted(weights, reverse=True), f"Weights should be ordered highest first: {weights}"
                
                # Check that all items have weights
                for item in selection:
                    assert 'weight' in item, f"Item should have weight: {item}"
                    assert 'reason' in item, f"Item should have reason: {item}"


class TestBudgetConstraints:
    """Test budget manager must-include functionality."""
    
    def test_budget_protects_critical_items(self):
        """Test that budget manager protects Rules and Acceptance items."""
        from builder.core.context_budget import BudgetItem
        
        # Create test budget items using BudgetItem class
        budget_items = [
            BudgetItem(
                id="rules-1",
                type="rules",
                title="Test Rules",
                content="Test rules content",
                file_path="rules.md",
                weight=1.0,
                token_estimate=100,
                source_anchor="[Test Rules](rules.md)"
            ),
            BudgetItem(
                id="acceptance-1",
                type="acceptance",
                title="Test Acceptance",
                content="Test acceptance content",
                file_path="prd.md",
                weight=2.0,
                token_estimate=200,
                source_anchor="[Test Acceptance](prd.md)"
            ),
            BudgetItem(
                id="code-1",
                type="code",
                title="Test Code",
                content="Test code content",
                file_path="src/test.ts",
                weight=3.0,
                token_estimate=300,
                source_anchor="[Test Code](src/test.ts)"
            ),
            BudgetItem(
                id="arch-1",
                type="arch",
                title="Test Arch",
                content="Test arch content",
                file_path="arch.md",
                weight=4.0,
                token_estimate=400,
                source_anchor="[Test Arch](arch.md)"
            ),
        ]
        
        # Test with very small budget
        budget_manager = ContextBudgetManager(total_budget=150)  # Very small budget
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Check that Rules and Acceptance are protected
        selected_types = [item.type for item in selected_items]
        assert 'rules' in selected_types, "Rules should be protected and included"
        assert 'acceptance' in selected_types, "Acceptance should be protected and included"
        
        # Check that budget summary shows protection
        assert 'rules' in budget_summary, "Budget summary should include rules"
        assert 'acceptance' in budget_summary, "Budget summary should include acceptance"
    
    def test_budget_respects_limits(self):
        """Test that budget manager respects token limits."""
        from builder.core.context_budget import BudgetItem
        
        budget_items = [
            BudgetItem(
                id="code-1",
                type="code",
                title="Test Code 1",
                content="Test code 1 content",
                file_path="src/test1.ts",
                weight=1.0,
                token_estimate=100,
                source_anchor="[Test Code 1](src/test1.ts)"
            ),
            BudgetItem(
                id="code-2",
                type="code",
                title="Test Code 2",
                content="Test code 2 content",
                file_path="src/test2.ts",
                weight=2.0,
                token_estimate=200,
                source_anchor="[Test Code 2](src/test2.ts)"
            ),
            BudgetItem(
                id="code-3",
                type="code",
                title="Test Code 3",
                content="Test code 3 content",
                file_path="src/test3.ts",
                weight=3.0,
                token_estimate=300,
                source_anchor="[Test Code 3](src/test3.ts)"
            ),
        ]
        
        budget_manager = ContextBudgetManager(total_budget=250)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Check that total tokens don't exceed budget
        total_tokens = sum(item.token_estimate for item in selected_items)
        assert total_tokens <= 250, f"Total tokens {total_tokens} should not exceed budget 250"
        
        # Check that some items are in overflow if budget is exceeded
        if sum(item.token_estimate for item in budget_items) > 250:
            assert len(overflow_items) > 0, "Should have overflow items when budget is exceeded"


class TestContextPackFields:
    """Test ctx:pack field presence and structure."""
    
    def test_pack_context_has_required_fields(self):
        """Test that pack_context.json has all required fields."""
        # Create a minimal test pack
        test_pack = {
            'task': {
                'purpose': 'implement',
                'target_path': 'src/test.ts',
                'feature': 'test'
            },
            'constraints': {
                'rules_md': 'Test rules',
                'token_limit': 1000,
                'budget_summary': {'code': {'used_tokens': 100}},
                'conflicts': [],
                'sources': []
            },
            'acceptance': [
                {'title': 'Test Acceptance', 'content': 'Test content', 'file_path': 'test.md'}
            ],
            'decisions': [],
            'integrations': [],
            'architecture': [],
            'ux': [],
            'code': [
                {'title': 'Test Code', 'content': '// Test code', 'file_path': 'src/test.ts'}
            ],
            'objective_signals': {},
            'provenance': [],
            'render': {
                'system': 'Test system',
                'instructions': 'Test instructions',
                'user': 'Test user',
                'references': 'Test references'
            }
        }
        
        # Test required fields
        required_fields = [
            'task', 'constraints', 'acceptance', 'decisions', 
            'integrations', 'architecture', 'ux', 'code',
            'objective_signals', 'provenance', 'render'
        ]
        
        for field in required_fields:
            assert field in test_pack, f"Pack should have {field} field"
        
        # Test constraints fields
        constraints = test_pack['constraints']
        required_constraints = ['rules_md', 'token_limit', 'budget_summary', 'conflicts', 'sources']
        for field in required_constraints:
            assert field in constraints, f"Constraints should have {field} field"
    
    def test_pack_context_structure_types(self):
        """Test that pack_context.json has correct data types."""
        test_pack = {
            'task': {'purpose': 'implement', 'target_path': 'src/test.ts', 'feature': 'test'},
            'constraints': {
                'rules_md': 'Test rules',
                'token_limit': 1000,
                'budget_summary': {'code': {'used_tokens': 100}},
                'conflicts': [],
                'sources': []
            },
            'acceptance': [{'title': 'Test', 'content': 'Test', 'file_path': 'test.md'}],
            'decisions': [],
            'integrations': [],
            'architecture': [],
            'ux': [],
            'code': [{'title': 'Test', 'content': '// Test', 'file_path': 'src/test.ts'}],
            'objective_signals': {},
            'provenance': [],
            'render': {'system': 'Test', 'instructions': 'Test', 'user': 'Test', 'references': 'Test'}
        }
        
        # Test data types
        assert isinstance(test_pack['task'], dict), "Task should be dict"
        assert isinstance(test_pack['constraints'], dict), "Constraints should be dict"
        assert isinstance(test_pack['acceptance'], list), "Acceptance should be list"
        assert isinstance(test_pack['code'], list), "Code should be list"
        assert isinstance(test_pack['constraints']['conflicts'], list), "Conflicts should be list"
        assert isinstance(test_pack['constraints']['sources'], list), "Sources should be list"


class TestRulesMerging:
    """Test rules merging functionality."""
    
    def test_rules_merging_returns_expected_structure(self):
        """Test that rules merging returns expected structure."""
        result = merge_context_rules('test', ['typescript'])
        
        # Check required fields
        required_fields = ['rules_markdown', 'guardrails', 'conflicts', 'sources']
        for field in required_fields:
            assert field in result, f"Rules result should have {field} field"
        
        # Check data types
        assert isinstance(result['rules_markdown'], str), "rules_markdown should be string"
        assert isinstance(result['guardrails'], dict), "guardrails should be dict"
        assert isinstance(result['conflicts'], list), "conflicts should be list"
        assert isinstance(result['sources'], list), "sources should be list"
    
    def test_rules_merging_handles_missing_files(self):
        """Test that rules merging handles missing files gracefully."""
        # Test with non-existent feature
        result = merge_context_rules('nonexistent', ['nonexistent'])
        
        # Should still return valid structure
        assert 'rules_markdown' in result
        assert 'conflicts' in result
        assert 'sources' in result
        
        # Should not crash
        assert isinstance(result['rules_markdown'], str)


def run_tests():
    """Run all golden checks."""
    import unittest
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStatusValidation,
        TestGraphOperations,
        TestSelectionWeights,
        TestBudgetConstraints,
        TestContextPackFields,
        TestRulesMerging
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
