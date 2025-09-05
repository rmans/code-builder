#!/usr/bin/env python3
"""
Unit tests for the context graph system.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from builder.context_graph import ContextGraph, GraphNode, GraphEdge, NODE_TYPES, EDGE_TYPES

class TestContextGraph(unittest.TestCase):
    """Test cases for the context graph system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = ContextGraph()
        
    def test_node_creation(self):
        """Test creating and adding nodes."""
        node = GraphNode(
            id="test-node",
            node_type="prd",
            title="Test Node",
            file_path="/test/path.md",
            metadata={"status": "draft"},
            properties={"feature": "test"}
        )
        
        self.graph.add_node(node)
        
        # Test retrieval
        retrieved = self.graph.get_node("test-node")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test-node")
        self.assertEqual(retrieved.node_type, "prd")
        self.assertEqual(retrieved.title, "Test Node")
        
    def test_edge_creation(self):
        """Test creating and adding edges."""
        # Create two nodes
        node1 = GraphNode("node1", "prd", "Node 1", "/test1.md")
        node2 = GraphNode("node2", "arch", "Node 2", "/test2.md")
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        
        # Create edge
        edge = GraphEdge("node1", "node2", "informs")
        self.graph.add_edge(edge)
        
        # Test edge retrieval
        edges_from = self.graph.get_edges_from("node1")
        edges_to = self.graph.get_edges_to("node2")
        
        self.assertEqual(len(edges_from), 1)
        self.assertEqual(len(edges_to), 1)
        self.assertEqual(edges_from[0].edge_type, "informs")
        
    def test_adjacency(self):
        """Test adjacency relationships."""
        # Create nodes
        node1 = GraphNode("node1", "prd", "Node 1", "/test1.md")
        node2 = GraphNode("node2", "arch", "Node 2", "/test2.md")
        node3 = GraphNode("node3", "ux", "Node 3", "/test3.md")
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)
        
        # Create edges
        self.graph.add_edge(GraphEdge("node1", "node2", "informs"))
        self.graph.add_edge(GraphEdge("node1", "node3", "informs"))
        
        # Test adjacency
        adjacent = self.graph.get_adjacent_nodes("node1")
        self.assertEqual(len(adjacent), 2)
        self.assertIn("node2", adjacent)
        self.assertIn("node3", adjacent)
        
    def test_stats(self):
        """Test graph statistics."""
        # Add some nodes and edges
        node1 = GraphNode("node1", "prd", "Node 1", "/test1.md")
        node2 = GraphNode("node2", "arch", "Node 2", "/test2.md")
        node3 = GraphNode("node3", "code", "Node 3", "/test3.ts")
        
        self.graph.add_node(node1)
        self.graph.add_node(node2)
        self.graph.add_node(node3)
        
        self.graph.add_edge(GraphEdge("node1", "node2", "informs"))
        self.graph.add_edge(GraphEdge("node3", "node1", "implements"))
        
        stats = self.graph.get_stats()
        
        self.assertEqual(stats['total_nodes'], 3)
        self.assertEqual(stats['total_edges'], 2)
        self.assertEqual(stats['node_counts']['prd'], 1)
        self.assertEqual(stats['node_counts']['arch'], 1)
        self.assertEqual(stats['node_counts']['code'], 1)
        self.assertEqual(stats['edge_counts']['informs'], 1)
        self.assertEqual(stats['edge_counts']['implements'], 1)
        
    def test_json_export(self):
        """Test JSON export functionality."""
        # Create test data
        node = GraphNode("test-node", "prd", "Test Node", "/test.md")
        self.graph.add_node(node)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            
        try:
            self.graph.export_json(temp_path)
            
            # Verify file was created and contains valid JSON
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
                
            self.assertIn('nodes', data)
            self.assertIn('edges', data)
            self.assertIn('stats', data)
            self.assertEqual(len(data['nodes']), 1)
            self.assertEqual(data['nodes'][0]['id'], 'test-node')
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_feature_determination(self):
        """Test feature determination from file paths."""
        # Test with feature map
        self.graph.feature_map = {
            "src/auth/**": "auth",
            "src/content/**": "content-engine"
        }
        
        # Test auth feature
        auth_path = Path("/project/src/auth/login.ts")
        feature = self.graph._determine_feature(auth_path)
        self.assertEqual(feature, "auth")
        
        # Test content feature
        content_path = Path("/project/src/content/manager.ts")
        feature = self.graph._determine_feature(content_path)
        self.assertEqual(feature, "content-engine")
        
        # Test unknown feature
        unknown_path = Path("/project/src/unknown/file.ts")
        feature = self.graph._determine_feature(unknown_path)
        self.assertEqual(feature, "unknown")
        
    def test_front_matter_parsing(self):
        """Test front-matter parsing."""
        content = """---
type: prd
id: TEST-001
title: Test Document
status: draft
---

# Test Document
Content here.
"""
        
        front_matter, error = self.graph._parse_front_matter(content)
        
        self.assertIsNotNone(front_matter)
        self.assertIsNone(error)
        self.assertEqual(front_matter['type'], 'prd')
        self.assertEqual(front_matter['id'], 'TEST-001')
        self.assertEqual(front_matter['title'], 'Test Document')
        
    def test_title_extraction(self):
        """Test title extraction from content."""
        content = """# Main Title
Some content here.

## Subtitle
More content.
"""
        
        title = self.graph._extract_title_from_content(content)
        self.assertEqual(title, "Main Title")
        
    def test_export_extraction(self):
        """Test TypeScript export extraction."""
        content = """
export function testFunction() {}
export class TestClass {}
export const testConstant = "value";
export let testVariable = 123;
"""
        
        exports = self.graph._extract_exports(content)
        expected = ["testFunction", "TestClass", "testConstant", "testVariable"]
        
        self.assertEqual(set(exports), set(expected))
        
    def test_pattern_matching(self):
        """Test glob pattern matching."""
        # Test exact match
        self.assertTrue(self.graph._matches_pattern("src/auth/login.ts", "src/auth/**"))
        
        # Test wildcard match
        self.assertTrue(self.graph._matches_pattern("src/auth/components/button.ts", "src/auth/**"))
        
        # Test no match
        self.assertFalse(self.graph._matches_pattern("src/content/manager.ts", "src/auth/**"))

class TestContextGraphIntegration(unittest.TestCase):
    """Integration tests for the context graph with real project structure."""
    
    def setUp(self):
        """Set up test project structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create basic project structure
        (self.project_root / "docs" / "prd").mkdir(parents=True)
        (self.project_root / "docs" / "arch").mkdir(parents=True)
        (self.project_root / "docs" / "rules").mkdir(parents=True)
        (self.project_root / "src").mkdir(parents=True)
        (self.project_root / "builder").mkdir(parents=True)
        
        # Create feature map
        feature_map = {
            "src/auth/**": "auth",
            "src/content/**": "content-engine"
        }
        with open(self.project_root / "builder" / "feature_map.json", 'w') as f:
            json.dump(feature_map, f)
            
    def tearDown(self):
        """Clean up test directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_project_scan(self):
        """Test scanning a real project structure."""
        # Create test documents
        prd_content = """---
type: prd
id: TEST-PRD
title: Test PRD
status: draft
owner: Tester
created: 2025-01-01
links:
  - arch: []
  - ux: []
---

# Test PRD
Content here.
"""
        
        with open(self.project_root / "docs" / "prd" / "TEST-PRD.md", 'w') as f:
            f.write(prd_content)
            
        # Create test code file
        code_content = """
export function authFunction() {
    return "authenticated";
}

export class AuthService {
    login() {}
}
"""
        
        (self.project_root / "src" / "auth").mkdir()
        with open(self.project_root / "src" / "auth" / "login.ts", 'w') as f:
            f.write(code_content)
            
        # Create test rule file
        rule_content = """---
description: Test rules
globs: src/**/*
---

# Test Rules
- Rule 1
- Rule 2
"""
        
        with open(self.project_root / "docs" / "rules" / "test-rules.md", 'w') as f:
            f.write(rule_content)
            
        # Scan project
        graph = ContextGraph()
        graph.scan_project(str(self.project_root))
        
        # Verify results
        stats = graph.get_stats()
        self.assertGreater(stats['total_nodes'], 0)
        # Note: edges may be 0 if no relationships are found in test data
        
        # Check specific nodes
        prd_node = graph.get_node("TEST-PRD")
        self.assertIsNotNone(prd_node)
        self.assertEqual(prd_node.node_type, "prd")
        
        # Check code node
        code_nodes = [node for node in graph.nodes.values() if node.node_type == "code"]
        self.assertGreater(len(code_nodes), 0)
        
        # Check feature assignment
        auth_code_nodes = [node for node in code_nodes if node.properties.get('feature') == 'auth']
        self.assertGreater(len(auth_code_nodes), 0)

if __name__ == '__main__':
    unittest.main()
