#!/usr/bin/env python3
"""
Context Graph - In-memory representation of project artifacts and relationships.

Builds a graph of nodes (documents, code, rules) and edges (relationships) to understand
how everything feeds into everything else in the project.
"""

import os
import json
import yaml
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import re

# Node types
NODE_TYPES = {
    'PRD': 'prd',
    'ARCH': 'arch', 
    'INTEGRATION': 'integrations',
    'UX': 'ux',
    'IMPL': 'impl',
    'EXEC': 'exec',
    'TASK': 'tasks',
    'ADR': 'adr',
    'RULES': 'rules',
    'CODE': 'code'
}

# Edge types
EDGE_TYPES = {
    'INFORMS': 'informs',
    'IMPLEMENTS': 'implements', 
    'CONSTRAINS': 'constrains',
    'DEPENDS_ON': 'depends_on',
    'TESTS': 'tests',
    'SUPERSEDES': 'supersedes'
}

@dataclass
class GraphNode:
    """Represents a node in the context graph."""
    id: str
    node_type: str
    title: str
    file_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.node_type}:{self.id}"

@dataclass 
class GraphEdge:
    """Represents an edge/relationship in the context graph."""
    source_id: str
    target_id: str
    edge_type: str
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.source_id} --[{self.edge_type}]--> {self.target_id}"

class ContextGraph:
    """In-memory graph representation of project context and relationships."""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.feature_map: Dict[str, str] = {}
        
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
        self.adjacency[edge.source_id].add(edge.target_id)
        
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
        
    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        """Get all edges originating from a node."""
        return [edge for edge in self.edges if edge.source_id == node_id]
        
    def get_edges_to(self, node_id: str) -> List[GraphEdge]:
        """Get all edges pointing to a node."""
        return [edge for edge in self.edges if edge.target_id == node_id]
        
    def get_adjacent_nodes(self, node_id: str) -> Set[str]:
        """Get all nodes directly connected to a node."""
        return self.adjacency.get(node_id, set())
        
    def scan_project(self, project_root: str) -> None:
        """Scan the entire project and build the context graph."""
        project_path = Path(project_root)
        
        # Load feature map
        self._load_feature_map(project_path)
        
        # Scan documents
        self._scan_documents(project_path)
        
        # Scan code files
        self._scan_code_files(project_path)
        
        # Scan rules
        self._scan_rules(project_path)
        
        # Build relationships
        self._build_relationships()
        
    def _load_feature_map(self, project_path: Path) -> None:
        """Load the feature map from builder/feature_map.json."""
        feature_map_path = project_path / "builder" / "feature_map.json"
        if feature_map_path.exists():
            try:
                with open(feature_map_path, 'r') as f:
                    self.feature_map = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load feature map: {e}")
                
    def _scan_documents(self, project_path: Path) -> None:
        """Scan all document types and create nodes."""
        docs_path = project_path / "docs"
        if not docs_path.exists():
            return
            
        # Scan each document type directory
        for doc_type, node_type in NODE_TYPES.items():
            if doc_type == 'CODE' or doc_type == 'RULES':
                continue  # Handle these separately
                
            doc_dir = docs_path / node_type
            if doc_dir.exists():
                self._scan_document_directory(doc_dir, node_type)
                
        # Scan ADRs separately (they're in docs/adrs/)
        adr_dir = docs_path / "adrs"
        if adr_dir.exists():
            self._scan_document_directory(adr_dir, 'adr')
            
    def _scan_document_directory(self, doc_dir: Path, node_type: str) -> None:
        """Scan a directory of documents and create nodes."""
        for file_path in doc_dir.glob("*.md"):
            try:
                node = self._create_document_node(file_path, node_type)
                if node:
                    self.add_node(node)
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
                
    def _create_document_node(self, file_path: Path, node_type: str) -> Optional[GraphNode]:
        """Create a node from a document file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse front-matter
            front_matter, _ = self._parse_front_matter(content)
            
            if not front_matter:
                # Create node without front-matter
                node_id = file_path.stem
                title = self._extract_title_from_content(content)
            else:
                node_id = front_matter.get('id', file_path.stem)
                title = front_matter.get('title', self._extract_title_from_content(content))
                
            # Determine feature from file path
            feature = self._determine_feature(file_path)
            
            node = GraphNode(
                id=node_id,
                node_type=node_type,
                title=title,
                file_path=str(file_path),
                metadata=front_matter or {},
                properties={'feature': feature}
            )
            
            return node
            
        except Exception as e:
            print(f"Warning: Could not create node from {file_path}: {e}")
            return None
            
    def _scan_code_files(self, project_path: Path) -> None:
        """Scan code files and create nodes."""
        src_path = project_path / "src"
        if not src_path.exists():
            return
            
        for file_path in src_path.rglob("*.ts"):
            try:
                node = self._create_code_node(file_path)
                if node:
                    self.add_node(node)
            except Exception as e:
                print(f"Warning: Could not process code file {file_path}: {e}")
                
    def _create_code_node(self, file_path: Path) -> Optional[GraphNode]:
        """Create a node from a code file."""
        try:
            # Determine feature from path
            feature = self._determine_feature(file_path)
            
            # Extract class/function names as potential identifiers
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple extraction of exported items
            exports = self._extract_exports(content)
            
            node_id = f"code:{file_path.relative_to(file_path.parents[1])}"
            
            node = GraphNode(
                id=node_id,
                node_type='code',
                title=f"Code: {file_path.name}",
                file_path=str(file_path),
                metadata={'exports': exports},
                properties={'feature': feature, 'file_type': 'typescript'}
            )
            
            return node
            
        except Exception as e:
            print(f"Warning: Could not create code node from {file_path}: {e}")
            return None
            
    def _scan_rules(self, project_path: Path) -> None:
        """Scan rules files and create nodes."""
        rules_path = project_path / "docs" / "rules"
        if not rules_path.exists():
            return
            
        for file_path in rules_path.rglob("*.md"):
            try:
                node = self._create_rule_node(file_path)
                if node:
                    self.add_node(node)
            except Exception as e:
                print(f"Warning: Could not process rule file {file_path}: {e}")
                
    def _create_rule_node(self, file_path: Path) -> Optional[GraphNode]:
        """Create a node from a rule file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse front-matter
            front_matter, _ = self._parse_front_matter(content)
            
            # Determine rule type from path
            rule_type = 'global'
            if 'stack/' in str(file_path):
                rule_type = 'stack'
            elif 'feature/' in str(file_path):
                rule_type = 'feature'
            elif 'project' in file_path.name:
                rule_type = 'project'
                
            node_id = f"rule:{file_path.stem}"
            title = self._extract_title_from_content(content)
            
            node = GraphNode(
                id=node_id,
                node_type='rules',
                title=title,
                file_path=str(file_path),
                metadata=front_matter or {},
                properties={'rule_type': rule_type}
            )
            
            return node
            
        except Exception as e:
            print(f"Warning: Could not create rule node from {file_path}: {e}")
            return None
            
    def _build_relationships(self) -> None:
        """Build relationships between nodes based on links and dependencies."""
        for node in self.nodes.values():
            self._build_node_relationships(node)
            
    def _build_node_relationships(self, node: GraphNode) -> None:
        """Build relationships for a specific node."""
        if node.node_type == 'code':
            self._build_code_relationships(node)
        elif node.metadata:
            self._build_document_relationships(node)
            
    def _build_document_relationships(self, node: GraphNode) -> None:
        """Build relationships from document metadata."""
        links = node.metadata.get('links', [])
        
        if isinstance(links, list):
            for link_group in links:
                if isinstance(link_group, dict):
                    for link_type, link_ids in link_group.items():
                        if isinstance(link_ids, list):
                            for link_id in link_ids:
                                self._create_relationship(node.id, link_id, 'informs')
        elif isinstance(links, dict):
            for link_type, link_ids in links.items():
                if isinstance(link_ids, list):
                    for link_id in link_ids:
                        self._create_relationship(node.id, link_id, 'informs')
                        
    def _build_code_relationships(self, node: GraphNode) -> None:
        """Build relationships for code nodes."""
        # Code implements features
        feature = node.properties.get('feature')
        if feature:
            # Find related documents for this feature
            for other_node in self.nodes.values():
                if other_node.properties.get('feature') == feature:
                    if other_node.node_type in ['prd', 'arch', 'ux']:
                        self._create_relationship(node.id, other_node.id, 'implements')
                        
    def _create_relationship(self, source_id: str, target_id: str, edge_type: str) -> None:
        """Create a relationship between two nodes."""
        # Check if target exists
        if target_id in self.nodes:
            edge = GraphEdge(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type
            )
            self.add_edge(edge)
        else:
            # Try to find by partial match
            matching_nodes = [nid for nid in self.nodes.keys() if target_id in nid or nid in target_id]
            if matching_nodes:
                for match_id in matching_nodes:
                    edge = GraphEdge(
                        source_id=source_id,
                        target_id=match_id,
                        edge_type=edge_type
                    )
                    self.add_edge(edge)
                    
    def _parse_front_matter(self, content: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Parse YAML front-matter from document content."""
        if not content.startswith('---'):
            return None, None
            
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None, None
                
            front_matter_text = parts[1].strip()
            if not front_matter_text:
                return None, None
                
            front_matter = yaml.safe_load(front_matter_text)
            return front_matter, None
            
        except Exception:
            return None, None
            
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"
        
    def _extract_exports(self, content: str) -> List[str]:
        """Extract exported items from TypeScript code."""
        exports = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('export '):
                # Extract function/class names
                match = re.search(r'export\s+(?:function|class|const|let|var)\s+(\w+)', line)
                if match:
                    exports.append(match.group(1))
        return exports
        
    def _determine_feature(self, file_path: Path) -> str:
        """Determine which feature a file belongs to based on path and feature map."""
        path_str = str(file_path)
        
        # Check feature map
        for pattern, feature in self.feature_map.items():
            if self._matches_pattern(path_str, pattern):
                return feature
                
        # Default feature based on path
        if 'auth' in path_str.lower():
            return 'auth'
        elif 'content' in path_str.lower():
            return 'content-engine'
        elif 'utils' in path_str.lower():
            return 'platform'
        else:
            return 'unknown'
            
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a glob pattern."""
        # Simple glob matching
        pattern = pattern.replace('**', '*')
        pattern = pattern.replace('*', '.*')
        pattern = '^' + pattern + '$'
        return bool(re.match(pattern, path))
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        node_counts = defaultdict(int)
        edge_counts = defaultdict(int)
        
        for node in self.nodes.values():
            node_counts[node.node_type] += 1
            
        for edge in self.edges:
            edge_counts[edge.edge_type] += 1
            
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_counts': dict(node_counts),
            'edge_counts': dict(edge_counts),
            'features': list(set(node.properties.get('feature', 'unknown') for node in self.nodes.values()))
        }
        
    def print_stats(self) -> None:
        """Print graph statistics."""
        stats = self.get_stats()
        
        print("📊 Context Graph Statistics")
        print("=" * 40)
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Total Edges: {stats['total_edges']}")
        print()
        
        print("Node Types:")
        for node_type, count in stats['node_counts'].items():
            print(f"  {node_type}: {count}")
        print()
        
        print("Edge Types:")
        for edge_type, count in stats['edge_counts'].items():
            print(f"  {edge_type}: {count}")
        print()
        
        print("Features:")
        for feature in stats['features']:
            print(f"  {feature}")
        print()
        
    def export_json(self, file_path: str) -> None:
        """Export the graph to JSON format."""
        def json_serializer(obj):
            """Custom JSON serializer for non-serializable objects."""
            if hasattr(obj, 'isoformat'):  # datetime/date objects
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        data = {
            'nodes': [
                {
                    'id': node.id,
                    'type': node.node_type,
                    'title': node.title,
                    'file_path': node.file_path,
                    'metadata': node.metadata,
                    'properties': node.properties
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source_id,
                    'target': edge.target_id,
                    'type': edge.edge_type,
                    'weight': edge.weight,
                    'metadata': edge.metadata
                }
                for edge in self.edges
            ],
            'stats': self.get_stats()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=json_serializer)

def main():
    """Main function for testing the context graph."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_graph.py <project_root>")
        sys.exit(1)
        
    project_root = sys.argv[1]
    
    print(f"Building context graph for: {project_root}")
    graph = ContextGraph()
    graph.scan_project(project_root)
    
    # Print statistics
    graph.print_stats()
    
    # Export to JSON
    output_file = os.path.join(project_root, "builder", "cache", "context_graph.json")
    graph.export_json(output_file)
    print(f"Graph exported to: {output_file}")

if __name__ == "__main__":
    main()
