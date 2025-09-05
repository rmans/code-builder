"""
Context Graph - Dict-based graph for tracking relationships between documentation and code
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import yaml


class ContextGraph:
    """Dict-based context graph for tracking relationships between docs and code"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {}
        self.node_types = {
            'prd', 'arch', 'integration', 'ux', 'impl', 'exec', 'task', 'adr', 'rules', 'code'
        }
        self.edge_types = {
            'informs', 'implements', 'constrains', 'depends_on', 'tests', 'supersedes'
        }
    
    def add_node(self, node_id: str, node_type: str, **kwargs) -> None:
        """Add a node to the graph"""
        if node_type not in self.node_types:
            raise ValueError(f"Invalid node type: {node_type}")
        
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            **kwargs
        }
    
    def add_edge(self, from_node: str, to_node: str, edge_type: str, **kwargs) -> None:
        """Add an edge to the graph"""
        if edge_type not in self.edge_types:
            raise ValueError(f"Invalid edge type: {edge_type}")
        
        if from_node not in self.edges:
            self.edges[from_node] = []
        
        self.edges[from_node].append({
            'to': to_node,
            'type': edge_type,
            **kwargs
        })
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_edges_from(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all edges from a node"""
        return self.edges.get(node_id, [])
    
    def get_edges_to(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all edges to a node"""
        edges_to = []
        for from_node, edges in self.edges.items():
            for edge in edges:
                if edge['to'] == node_id:
                    edges_to.append({
                        'from': from_node,
                        **edge
                    })
        return edges_to
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_counts = {}
        edge_counts = {}
        
        # Count nodes by type
        for node in self.nodes.values():
            node_type = node['type']
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        # Count edges by type
        for edges in self.edges.values():
            for edge in edges:
                edge_type = edge['type']
                edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': sum(len(edges) for edges in self.edges.values()),
            'node_counts': node_counts,
            'edge_counts': edge_counts
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'stats': self.get_stats()
        }
    
    def save(self, filepath: str) -> None:
        """Save graph to JSON file"""
        def json_serializer(obj):
            """Custom JSON serializer for non-serializable objects"""
            if hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):  # custom objects
                return str(obj)
            else:
                return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False, default=json_serializer)
    
    @classmethod
    def load(cls, filepath: str) -> 'ContextGraph':
        """Load graph from JSON file"""
        graph = cls()
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old format (with stats) and new format
        if 'nodes' in data:
            graph.nodes = data.get('nodes', {})
            graph.edges = data.get('edges', {})
        else:
            # Fallback for old format
            graph.nodes = data
            graph.edges = {}
        
        return graph


class ContextGraphBuilder:
    """Builder for creating context graphs from repository files"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.docs_path = self.root_path / "docs"
        self.src_path = self.root_path / "src"
        self.builder_path = self.root_path / "builder"
        self.graph = ContextGraph()
    
    def build(self) -> ContextGraph:
        """Build the complete context graph"""
        self._scan_documentation()
        self._scan_source_code()
        self._scan_rules()
        self._add_proximity_edges()
        self._add_test_edges()
        return self.graph
    
    def _scan_documentation(self) -> None:
        """Scan documentation files for nodes and links"""
        doc_type_mapping = {
            'prd': 'prd',
            'arch': 'arch', 
            'integrations': 'integration',
            'ux': 'ux',
            'impl': 'impl',
            'exec': 'exec',
            'tasks': 'task',
            'adrs': 'adr'
        }
        
        for doc_type, node_type in doc_type_mapping.items():
            doc_dir = self.docs_path / doc_type
            if not doc_dir.exists():
                continue
                
            for doc_file in doc_dir.glob("*.md"):
                self._process_doc_file(doc_file, node_type)
    
    def _process_doc_file(self, file_path: Path, node_type: str) -> None:
        """Process a single documentation file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            front_matter, body = self._extract_front_matter(content)
            
            if not front_matter:
                return
            
            doc_id = front_matter.get('id', file_path.stem)
            title = front_matter.get('title', file_path.stem)
            status = front_matter.get('status', 'draft')
            
            # Add document node
            self.graph.add_node(
                doc_id,
                node_type,
                file_path=str(file_path.relative_to(self.root_path)),
                title=title,
                status=status,
                created=front_matter.get('created', ''),
                owner=front_matter.get('owner', '')
            )
            
            # Process links from front-matter
            links = front_matter.get('links', {})
            if isinstance(links, dict):
                for link_type, link_targets in links.items():
                    if isinstance(link_targets, list):
                        for target in link_targets:
                            if target:  # Skip empty targets
                                self._add_doc_link(doc_id, target, link_type)
                    elif isinstance(link_targets, str) and link_targets:
                        self._add_doc_link(doc_id, link_targets, link_type)
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
    
    def _extract_front_matter(self, content: str) -> Tuple[Optional[Dict], str]:
        """Extract YAML front-matter from markdown content"""
        match = re.search(r'^---\n(.*?)\n---\n', content, flags=re.S | re.M)
        if not match:
            return None, content
        
        try:
            front_matter = yaml.safe_load(match.group(1)) or {}
            body = content[match.end():]
            return front_matter, body
        except Exception:
            return None, content
    
    def _add_doc_link(self, from_doc: str, to_doc: str, link_type: str) -> None:
        """Add a link between documents"""
        # Map link types to edge types
        link_mapping = {
            'prd': 'informs',
            'arch': 'informs', 
            'impl': 'implements',
            'exec': 'implements',
            'ux': 'informs',
            'adr': 'constrains'
        }
        
        edge_type = link_mapping.get(link_type, 'informs')
        self.graph.add_edge(from_doc, to_doc, edge_type, link_type=link_type)
    
    def _scan_source_code(self) -> None:
        """Scan source code files for nodes"""
        if not self.src_path.exists():
            return
        
        for code_file in self.src_path.rglob("*.ts"):
            if code_file.is_file():
                self._process_code_file(code_file)
    
    def _process_code_file(self, file_path: Path) -> None:
        """Process a single source code file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = file_path.relative_to(self.root_path)
            
            # Extract class/function names as potential identifiers
            class_matches = re.findall(r'class\s+(\w+)', content)
            function_matches = re.findall(r'function\s+(\w+)', content)
            interface_matches = re.findall(r'interface\s+(\w+)', content)
            
            # Create a code node for the file
            file_id = f"code:{relative_path.as_posix()}"
            self.graph.add_node(
                file_id,
                'code',
                file_path=str(relative_path),
                classes=class_matches,
                functions=function_matches,
                interfaces=interface_matches,
                lines=len(content.splitlines())
            )
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
    
    def _scan_rules(self) -> None:
        """Scan rules files for nodes"""
        rules_dir = self.docs_path / "rules"
        if not rules_dir.exists():
            return
        
        for rule_file in rules_dir.rglob("*.md"):
            if rule_file.is_file():
                self._process_rule_file(rule_file)
    
    def _process_rule_file(self, file_path: Path) -> None:
        """Process a single rules file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = file_path.relative_to(self.root_path)
            
            # Extract rule patterns and descriptions
            rule_patterns = re.findall(r'-\s*\*\*Pattern\*\*:\s*`([^`]+)`', content)
            rule_messages = re.findall(r'-\s*\*\*Message\*\*:\s*([^\n]+)', content)
            
            rule_id = f"rules:{relative_path.as_posix()}"
            self.graph.add_node(
                rule_id,
                'rules',
                file_path=str(relative_path),
                patterns=rule_patterns,
                messages=rule_messages
            )
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
    
    def _add_proximity_edges(self) -> None:
        """Add edges based on file path proximity"""
        # Group nodes by directory
        dir_groups = {}
        for node_id, node in self.graph.nodes.items():
            if 'file_path' in node:
                file_path = Path(node['file_path'])
                parent_dir = str(file_path.parent)
                if parent_dir not in dir_groups:
                    dir_groups[parent_dir] = []
                dir_groups[parent_dir].append(node_id)
        
        # Add proximity edges within same directories
        for dir_path, node_ids in dir_groups.items():
            if len(node_ids) > 1:
                for i, node_id1 in enumerate(node_ids):
                    for node_id2 in node_ids[i+1:]:
                        self.graph.add_edge(
                            node_id1, node_id2, 'depends_on', 
                            reason='path_proximity', directory=dir_path
                        )
    
    def _add_test_edges(self) -> None:
        """Add edges between code and test files"""
        code_nodes = {nid: node for nid, node in self.graph.nodes.items() 
                     if node['type'] == 'code'}
        
        for code_id, code_node in code_nodes.items():
            if 'file_path' in code_node:
                code_path = Path(code_node['file_path'])
                # Look for corresponding test files
                test_patterns = [
                    code_path.with_suffix('.test.ts'),
                    code_path.with_suffix('.spec.ts'),
                    code_path.parent / f"{code_path.stem}.test.ts",
                    code_path.parent / f"{code_path.stem}.spec.ts"
                ]
                
                for test_pattern in test_patterns:
                    test_path = self.root_path / test_pattern
                    if test_path.exists():
                        test_id = f"code:{test_path.relative_to(self.root_path).as_posix()}"
                        if test_id in self.graph.nodes:
                            self.graph.add_edge(
                                test_id, code_id, 'tests',
                                reason='test_mirror'
                            )
                        break