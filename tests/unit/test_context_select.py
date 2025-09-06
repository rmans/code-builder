#!/usr/bin/env python3
"""
Unit tests for the context selection and ranking system.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from builder.core.context_select import ContextSelector, ContextItem
from builder.core.context_graph import ContextGraph, GraphNode, GraphEdge

class TestContextSelector(unittest.TestCase):
    """Test cases for the context selection system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = ContextGraph()
        
        # Create test nodes
        self.prd_node = GraphNode(
            id="PRD-test",
            node_type="prd",
            title="Test PRD",
            file_path="/docs/prd/PRD-test.md",
            metadata={
                "type": "prd",
                "id": "PRD-test",
                "title": "Test PRD",
                "status": "approved",
                "created": "2025-01-01",
                "links": [{"arch": ["ARCH-test"]}]
            },
            properties={"feature": "auth"}
        )
        
        self.arch_node = GraphNode(
            id="ARCH-test",
            node_type="arch",
            title="Test Architecture",
            file_path="/docs/arch/ARCH-test.md",
            metadata={
                "type": "arch",
                "id": "ARCH-test",
                "title": "Test Architecture",
                "status": "approved",
                "created": "2025-01-01",
                "links": [{"prd": ["PRD-test"]}]
            },
            properties={"feature": "auth"}
        )
        
        self.code_node = GraphNode(
            id="code:auth/login.ts",
            node_type="code",
            title="Login Code",
            file_path="/src/auth/login.ts",
            metadata={"exports": ["AuthService"]},
            properties={"feature": "auth", "file_type": "typescript"}
        )
        
        self.test_node = GraphNode(
            id="code:auth/login.test.ts",
            node_type="code",
            title="Login Tests",
            file_path="/src/auth/login.test.ts",
            metadata={"exports": []},
            properties={"feature": "auth", "file_type": "typescript"}
        )
        
        # Add nodes to graph
        self.graph.add_node(self.prd_node)
        self.graph.add_node(self.arch_node)
        self.graph.add_node(self.code_node)
        self.graph.add_node(self.test_node)
        
        # Add edges
        self.graph.add_edge(GraphEdge("PRD-test", "ARCH-test", "informs"))
        self.graph.add_edge(GraphEdge("code:auth/login.ts", "PRD-test", "implements"))
        
        # Create selector
        self.selector = ContextSelector(self.graph)
        
    def test_explicit_link_scoring(self):
        """Test that explicit links get the highest score."""
        items = self.selector.select_context(start_path="/src/auth/login.ts", max_items=5)
        
        # Should find the code node and related items
        self.assertGreater(len(items), 0)
        
        # Check that explicit links get +4 score
        prd_item = next((item for item in items if item.node.id == "PRD-test"), None)
        if prd_item:
            self.assertGreaterEqual(prd_item.score, 4.0)  # At least explicit link bonus
            
    def test_same_feature_scoring(self):
        """Test that same feature items get +3 score."""
        items = self.selector.select_context(start_feature="auth", max_items=5)
        
        # All items should be auth feature
        for item in items:
            self.assertEqual(item.node.properties.get('feature'), 'auth')
            
        # Should get same feature bonus
        for item in items:
            self.assertGreaterEqual(item.score, 3.0)  # At least same feature bonus
            
    def test_same_folder_scoring(self):
        """Test that same folder items get +2 score."""
        items = self.selector.select_context(start_path="/src/auth/login.ts", max_items=5)
        
        # Find items in same folder
        same_folder_items = [item for item in items if Path(item.node.file_path).parent == Path("/src/auth")]
        
        for item in same_folder_items:
            self.assertGreaterEqual(item.score, 2.0)  # At least same folder bonus
            
    def test_approved_status_scoring(self):
        """Test that approved status gets +2 score."""
        items = self.selector.select_context(start_path="/docs/arch/ARCH-test.md", max_items=5)
        
        # Find approved items
        approved_items = [item for item in items if item.node.metadata.get('status') == 'approved']
        
        for item in approved_items:
            self.assertGreaterEqual(item.score, 2.0)  # At least approved bonus
            
    def test_recent_scoring(self):
        """Test that recent items get +1 score."""
        items = self.selector.select_context(start_path="/docs/arch/ARCH-test.md", max_items=5)
        
        # All test items are recent (2025-01-01)
        for item in items:
            if 'recent' in ' '.join(item.reasons):
                self.assertGreaterEqual(item.score, 1.0)  # At least recent bonus
                
    def test_distance_tracking(self):
        """Test that distance is tracked correctly."""
        items = self.selector.select_context(start_path="/src/auth/login.ts", max_items=5)
        
        # Starting node should have distance 0
        start_items = [item for item in items if item.node.id == "code:auth/login.ts"]
        if start_items:
            self.assertEqual(start_items[0].distance, 0)
            
    def test_max_items_limit(self):
        """Test that max_items limit is respected."""
        items = self.selector.select_context(start_feature="auth", max_items=2)
        
        self.assertLessEqual(len(items), 2)
        
    def test_max_distance_limit(self):
        """Test that max_distance limit is respected."""
        items = self.selector.select_context(start_path="/src/auth/login.ts", max_distance=1)
        
        for item in items:
            self.assertLessEqual(item.distance, 1)
            
    def test_context_summary(self):
        """Test context summary generation."""
        items = self.selector.select_context(start_feature="auth", max_items=5)
        summary = self.selector.get_context_summary(items)
        
        self.assertIn('total_items', summary)
        self.assertIn('by_type', summary)
        self.assertIn('by_feature', summary)
        self.assertIn('by_distance', summary)
        self.assertIn('score_range', summary)
        
        self.assertEqual(summary['total_items'], len(items))
        
    def test_empty_results(self):
        """Test behavior with no matching items."""
        # Create empty graph
        empty_graph = ContextGraph()
        empty_selector = ContextSelector(empty_graph)
        
        items = empty_selector.select_context(start_path="/nonexistent/path.ts")
        
        self.assertEqual(len(items), 0)
        
    def test_scoring_weights(self):
        """Test that scoring weights are applied correctly."""
        items = self.selector.select_context(start_path="/src/auth/login.ts", max_items=5)
        
        # Check that reasons contain expected weight values
        for item in items:
            reasons_text = ' '.join(item.reasons)
            
            # Should contain weight values
            if 'explicit link' in reasons_text:
                self.assertIn('+4.0', reasons_text)
            if 'same feature' in reasons_text:
                self.assertIn('+3.0', reasons_text)
            if 'same folder' in reasons_text:
                self.assertIn('+2.0', reasons_text)
            if 'approved status' in reasons_text:
                self.assertIn('+2.0', reasons_text)
            if 'recent' in reasons_text:
                self.assertIn('+1.0', reasons_text)

class TestContextSelectorIntegration(unittest.TestCase):
    """Integration tests for context selection with real project structure."""
    
    def setUp(self):
        """Set up test project structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create project structure
        (self.project_root / "docs" / "prd").mkdir(parents=True)
        (self.project_root / "src" / "auth").mkdir(parents=True)
        (self.project_root / "builder").mkdir(parents=True)
        
        # Create feature map
        feature_map = {"src/auth/**": "auth"}
        with open(self.project_root / "builder" / "feature_map.json", 'w') as f:
            json.dump(feature_map, f)
            
    def tearDown(self):
        """Clean up test directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_real_project_context_selection(self):
        """Test context selection with real project files."""
        # Create test files
        prd_content = """---
type: prd
id: PRD-auth
title: Authentication PRD
status: approved
owner: Tester
created: 2025-01-01
links:
  - arch: []
  - ux: []
---

# Authentication PRD
Content here.
"""
        
        with open(self.project_root / "docs" / "prd" / "PRD-auth.md", 'w') as f:
            f.write(prd_content)
            
        code_content = """
export class AuthService {
    login() {}
}
"""
        
        with open(self.project_root / "src" / "auth" / "login.ts", 'w') as f:
            f.write(code_content)
            
        # Build context graph
        from builder.core.context_graph import ContextGraph
        graph = ContextGraph()
        graph.scan_project(str(self.project_root))
        
        # Test context selection
        selector = ContextSelector(graph)
        items = selector.select_context(start_path="src/auth/login.ts")
        
        # Should find relevant items
        self.assertGreater(len(items), 0)
        
        # Should include the code file
        code_items = [item for item in items if item.node.node_type == 'code']
        self.assertGreater(len(code_items), 0)

if __name__ == '__main__':
    unittest.main()
