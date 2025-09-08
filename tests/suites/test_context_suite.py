#!/usr/bin/env python3
"""
Context Test Suite

Comprehensive tests for context functionality including:
- Context creation
- Context packing
- Context rules merging
- Context budget management
- Context selection
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from builder.core.context_builder import ContextBuilder
from builder.core.context_rules import merge_context_rules, RuleSource
from builder.core.context_graph import ContextGraphBuilder
from builder.core.context_select import ContextSelector
from builder.core.context_budget import ContextBudgetManager


class TestContextSuite:
    """Test suite for context functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir) / "test_project"
        self.project_root.mkdir()
        
        # Create test project structure
        self._create_test_project()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_project(self):
        """Create a test project structure."""
        # Create docs directory
        docs_dir = self.project_root / "cb_docs"
        docs_dir.mkdir()
        
        # Create tasks directory
        tasks_dir = docs_dir / "tasks"
        tasks_dir.mkdir()
        
        # Create test task files
        (tasks_dir / "TASK-001.md").write_text("""---
id: TASK-001
title: Test Task 1
status: pending
---
# Test Task 1
Description of test task 1.
""")
        
        (tasks_dir / "TASK-002.md").write_text("""---
id: TASK-002
title: Test Task 2
status: completed
---
# Test Task 2
Description of test task 2.
""")
        
        # Create rules directory
        rules_dir = self.project_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        
        (rules_dir / "test-rule.md").write_text("""---
id: test-rule
title: Test Rule
description: A test rule
---
# Test Rule
This is a test rule.
""")
    
    def test_context_builder_creation(self):
        """Test context builder creation."""
        builder = ContextBuilder(str(self.project_root))
        assert builder is not None
        assert builder.project_root == str(self.project_root)
    
    def test_context_rules_merging(self):
        """Test context rules merging."""
        rules_dir = self.project_root / ".cursor" / "rules"
        
        # Test merging rules from directory
        merged_rules = merge_context_rules(str(rules_dir))
        
        assert merged_rules is not None
        assert "rules_markdown" in merged_rules
        assert "rules_count" in merged_rules
        assert merged_rules["rules_count"] > 0
    
    def test_context_graph_building(self):
        """Test context graph building."""
        graph_builder = ContextGraphBuilder(str(self.project_root))
        graph = graph_builder.build_graph()
        
        assert graph is not None
        assert hasattr(graph, 'nodes')
        assert hasattr(graph, 'edges')
    
    def test_context_selection(self):
        """Test context selection."""
        selector = ContextSelector(str(self.project_root))
        
        # Test basic selection
        context = selector.select_context("test")
        
        assert context is not None
        assert "content" in context or "rules" in context
    
    def test_context_budget_management(self):
        """Test context budget management."""
        budget_manager = ContextBudgetManager()
        
        # Test budget allocation
        budget = budget_manager.allocate_budget(1000)
        
        assert budget is not None
        assert budget.total_tokens >= 0
        assert budget.used_tokens >= 0
    
    def test_context_packing(self):
        """Test context packing functionality."""
        builder = ContextBuilder(str(self.project_root))
        
        # Test packing context
        packed_context = builder.pack_context()
        
        assert packed_context is not None
        assert isinstance(packed_context, (str, dict))
    
    def test_context_consistency(self):
        """Test that context operations are consistent."""
        builder = ContextBuilder(str(self.project_root))
        
        # Test multiple context creations
        context1 = builder.create_context("test1")
        context2 = builder.create_context("test2")
        
        # Should be able to create different contexts
        assert context1 is not None
        assert context2 is not None
    
    def test_context_rules_validation(self):
        """Test context rules validation."""
        rules_dir = self.project_root / ".cursor" / "rules"
        
        # Test with valid rules
        merged_rules = merge_context_rules(str(rules_dir))
        assert merged_rules["rules_count"] > 0
        
        # Test with empty directory
        empty_dir = self.project_root / "empty_rules"
        empty_dir.mkdir()
        empty_rules = merge_context_rules(str(empty_dir))
        assert empty_rules["rules_count"] == 0
    
    def test_context_budget_limits(self):
        """Test context budget limits."""
        budget_manager = ContextBudgetManager()
        
        # Test budget allocation with limits
        budget = budget_manager.allocate_budget(1000, max_tokens=500)
        
        assert budget.total_tokens <= 500
        assert budget.used_tokens <= budget.total_tokens
    
    def test_context_error_handling(self):
        """Test context error handling."""
        # Test with non-existent directory
        with pytest.raises((FileNotFoundError, OSError)):
            builder = ContextBuilder("/non/existent/path")
            builder.create_context("test")
    
    def test_context_performance(self):
        """Test context performance."""
        import time
        
        builder = ContextBuilder(str(self.project_root))
        
        start_time = time.time()
        context = builder.create_context("performance_test")
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 5.0  # 5 seconds max
        assert context is not None


class TestContextIntegration:
    """Integration tests for context functionality."""
    
    def test_context_end_to_end(self):
        """Test complete context workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "test_project"
            project_root.mkdir()
            
            # Create basic project structure
            docs_dir = project_root / "cb_docs"
            docs_dir.mkdir()
            
            # Test complete workflow
            builder = ContextBuilder(str(project_root))
            
            # Create context
            context = builder.create_context("integration_test")
            assert context is not None
            
            # Pack context
            packed = builder.pack_context()
            assert packed is not None
    
    def test_context_with_rules(self):
        """Test context with rules integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "test_project"
            project_root.mkdir()
            
            # Create rules
            rules_dir = project_root / ".cursor" / "rules"
            rules_dir.mkdir(parents=True)
            
            (rules_dir / "test.md").write_text("""---
id: test
title: Test
---
# Test Rule
""")
            
            # Test context with rules
            builder = ContextBuilder(str(project_root))
            context = builder.create_context("rules_test")
            
            assert context is not None
    
    def test_context_budget_integration(self):
        """Test context budget integration."""
        budget_manager = ContextBudgetManager()
        builder = ContextBuilder(str(self.project_root))
        
        # Test budget allocation during context creation
        budget = budget_manager.allocate_budget(1000)
        context = builder.create_context("budget_test")
        
        assert context is not None
        assert budget.total_tokens > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
