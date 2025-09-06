"""
Context Selection - Retrieval and ranking system for context-aware code generation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from datetime import datetime, timedelta
import re


class ContextItem:
    """Represents a context item with scoring information"""
    
    def __init__(self, node, score: float = 0.0, distance: int = 0, reasons: List[str] = None):
        self.node = node
        self.score = score
        self.distance = distance
        self.reasons = reasons or []
    
    def __repr__(self):
        return f"ContextItem(node={self.node.id}, score={self.score}, distance={self.distance})"


class ContextSelector:
    """Retrieval and ranking system for context selection"""
    
    def __init__(self, graph_or_root_path, graph_file: str = "builder/cache/context_graph.json"):
        if isinstance(graph_or_root_path, str):
            # Handle string path (original behavior)
            self.root_path = Path(graph_or_root_path)
            self.graph_file = self.root_path / graph_file
            self.graph = None
            self.feature_map = {}
            self._load_graph()
            self._load_feature_map()
        else:
            # Handle ContextGraph object (for tests)
            self.graph = graph_or_root_path
            self.root_path = None
            self.graph_file = None
            self.feature_map = {}
    
    def _load_graph(self) -> None:
        """Load context graph from JSON file"""
        try:
            from context_graph import ContextGraph
            if self.graph_file.exists():
                self.graph = ContextGraph.load(str(self.graph_file))
            else:
                # Build graph if it doesn't exist
                from context_graph import ContextGraphBuilder
                builder = ContextGraphBuilder(str(self.root_path))
                self.graph = builder.build()
        except Exception as e:
            print(f"Warning: Could not load context graph: {e}")
            self.graph = None
    
    def _load_feature_map(self) -> None:
        """Load feature map for feature-based scoring"""
        feature_map_file = self.root_path / "builder" / "feature_map.json"
        if feature_map_file.exists():
            try:
                with open(feature_map_file, 'r', encoding='utf-8') as f:
                    self.feature_map = json.load(f)
            except Exception:
                self.feature_map = {}
    
    def select_context(self, start_path: str = None, start_feature: str = None, 
                      max_items: int = 5, max_distance: int = 3) -> List[ContextItem]:
        """
        Select and rank context items for a target path or feature
        
        Args:
            start_path: Path to the target file (e.g., "src/auth/login.ts")
            start_feature: Feature name for feature-based scoring
            max_items: Maximum number of items to return
            max_distance: Maximum distance to traverse in the graph
            
        Returns:
            List of ContextItem objects with scores and reasons
        """
        if not self.graph:
            return []
        
        items = []
        
        # Find starting nodes
        if start_path:
            # Find nodes by path
            for node_id, node_data in self.graph.nodes.items():
                if node_data.get('file_path') == start_path:
                    start_node = self.graph.get_node(node_id)
                    if start_node:
                        items.append(ContextItem(start_node, score=10.0, distance=0, reasons=["starting node"]))
                        break
        
        if start_feature:
            # Find nodes by feature
            for node_id, node_data in self.graph.nodes.items():
                if node_data.get('properties', {}).get('feature') == start_feature:
                    node = self.graph.get_node(node_id)
                    if node:
                        score = 3.0  # Same feature bonus
                        reasons = ["same feature"]
                        if node_data.get('metadata', {}).get('status') == 'approved':
                            score += 2.0
                            reasons.append("approved status")
                        items.append(ContextItem(node, score=score, distance=0, reasons=reasons))
        
        # Add related nodes
        for item in items[:]:  # Copy to avoid modifying while iterating
            self._add_related_items(item, items, max_distance)
        
        # Sort by score and limit results
        items.sort(key=lambda x: x.score, reverse=True)
        return items[:max_items]
    
    def _add_related_items(self, item: ContextItem, items: List[ContextItem], max_distance: int):
        """Add related items to the context list"""
        if item.distance >= max_distance:
            return
        
        # Get adjacent nodes
        adjacent_ids = self.graph.get_adjacent_nodes(item.node.id)
        
        for adj_id in adjacent_ids:
            # Check if already added
            if any(existing.node.id == adj_id for existing in items):
                continue
            
            adj_node = self.graph.get_node(adj_id)
            if not adj_node:
                continue
            
            # Calculate score based on relationship
            score = 1.0  # Base score
            reasons = [f"related to {item.node.id}"]
            
            # Add feature bonus
            if adj_node.properties.get('feature') == item.node.properties.get('feature'):
                score += 3.0
                reasons.append("same feature +3.0")
            
            # Add status bonus
            if adj_node.metadata.get('status') == 'approved':
                score += 2.0
                reasons.append("approved status +2.0")
            
            # Add folder bonus
            if (item.node.file_path and adj_node.file_path and 
                Path(item.node.file_path).parent == Path(adj_node.file_path).parent):
                score += 2.0
                reasons.append("same folder +2.0")
            
            new_item = ContextItem(adj_node, score=score, distance=item.distance + 1, reasons=reasons)
            items.append(new_item)
    
    def get_context_summary(self, items: List[ContextItem]) -> Dict[str, Any]:
        """Get summary statistics for context items"""
        if not items:
            return {
                'total_items': 0,
                'by_type': {},
                'by_feature': {},
                'by_distance': {},
                'score_range': {'min': 0, 'max': 0}
            }
        
        by_type = {}
        by_feature = {}
        by_distance = {}
        scores = [item.score for item in items]
        
        for item in items:
            # Count by type
            node_type = item.node.node_type
            by_type[node_type] = by_type.get(node_type, 0) + 1
            
            # Count by feature
            feature = item.node.properties.get('feature', 'unknown')
            by_feature[feature] = by_feature.get(feature, 0) + 1
            
            # Count by distance
            distance = item.distance
            by_distance[distance] = by_distance.get(distance, 0) + 1
        
        return {
            'total_items': len(items),
            'by_type': by_type,
            'by_feature': by_feature,
            'by_distance': by_distance,
            'score_range': {'min': min(scores), 'max': max(scores)}
        }
    
    def select_context_old(self, target_path: str, feature: str = "", top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Select and rank context for a target path
        
        Args:
            target_path: Path to the target file (e.g., "src/auth/login.ts")
            feature: Feature name for feature-based scoring
            top_k: Number of top items to return per type
            
        Returns:
            Dictionary with context items grouped by type, each with scores and reasons
        """
        if not self.graph:
            return {}
        
        # Find target node
        target_node = self._find_target_node(target_path)
        if not target_node:
            return {}
        
        # Discover related nodes
        related_nodes = self._discover_related_nodes(target_node, feature)
        
        # Score and rank nodes
        scored_nodes = self._score_and_rank_nodes(related_nodes, target_node, feature)
        
        # Group by type and select top-K
        return self._group_and_select_top_k(scored_nodes, top_k)
    
    def _find_target_node(self, target_path: str) -> Optional[Dict[str, Any]]:
        """Find the target node in the graph"""
        # Look for exact path match
        for node_id, node in self.graph.nodes.items():
            if node.get('file_path') == target_path:
                return node
        
        # Look for partial path match
        target_path_obj = Path(target_path)
        for node_id, node in self.graph.nodes.items():
            if 'file_path' in node:
                node_path = Path(node['file_path'])
                if node_path.name == target_path_obj.name:
                    return node
        
        return None
    
    def _discover_related_nodes(self, target_node: Dict[str, Any], feature: str) -> Set[str]:
        """Discover related nodes through explicit links and one-hop connections"""
        related = set()
        target_id = target_node['id']
        
        # Add target node itself
        related.add(target_id)
        
        # Direct edges from target
        for edge in self.graph.get_edges_from(target_id):
            related.add(edge['to'])
        
        # Direct edges to target
        for edge in self.graph.get_edges_to(target_id):
            related.add(edge['from'])
        
        # One-hop connections (neighbors of neighbors)
        for edge in self.graph.get_edges_from(target_id):
            neighbor_id = edge['to']
            # Add neighbors of neighbors
            for neighbor_edge in self.graph.get_edges_from(neighbor_id):
                related.add(neighbor_edge['to'])
            for neighbor_edge in self.graph.get_edges_to(neighbor_id):
                related.add(neighbor_edge['from'])
        
        # Add nearby code/tests based on path proximity
        related.update(self._find_nearby_code_tests(target_node))
        
        return related
    
    def _find_nearby_code_tests(self, target_node: Dict[str, Any]) -> Set[str]:
        """Find nearby code and test files based on path proximity"""
        nearby = set()
        target_path = target_node.get('file_path', '')
        if not target_path:
            return nearby
        
        target_path_obj = Path(target_path)
        target_dir = target_path_obj.parent
        
        # Look for files in same directory or parent directories
        for node_id, node in self.graph.nodes.items():
            if 'file_path' in node:
                node_path = Path(node['file_path'])
                node_dir = node_path.parent
                
                # Same directory
                if node_dir == target_dir:
                    nearby.add(node_id)
                
                # Parent directory (one level up)
                elif node_dir == target_dir.parent:
                    nearby.add(node_id)
                
                # Same package (src/auth/ -> src/auth/)
                elif (target_path_obj.parts[:2] == node_path.parts[:2] and 
                      len(target_path_obj.parts) >= 2 and len(node_path.parts) >= 2):
                    nearby.add(node_id)
        
        return nearby
    
    def _score_and_rank_nodes(self, node_ids: Set[str], target_node: Dict[str, Any], feature: str) -> List[Dict[str, Any]]:
        """Score and rank nodes based on multiple criteria"""
        scored_nodes = []
        
        for node_id in node_ids:
            if node_id not in self.graph.nodes:
                continue
            
            node = self.graph.nodes[node_id]
            score, reasons = self._calculate_score(node, target_node, feature)
            
            scored_nodes.append({
                'id': node_id,
                'type': node['type'],
                'score': score,
                'reasons': reasons,
                'node': node
            })
        
        # Sort by score (descending)
        scored_nodes.sort(key=lambda x: x['score'], reverse=True)
        return scored_nodes
    
    def _calculate_score(self, node: Dict[str, Any], target_node: Dict[str, Any], feature: str) -> Tuple[float, List[str]]:
        """Calculate score for a node based on multiple criteria"""
        score = 0.0
        reasons = []
        
        # +4 for explicit links
        if self._has_explicit_link(node, target_node):
            score += 4.0
            reasons.append("explicit_link")
        
        # +3 for same feature
        if self._is_same_feature(node, feature):
            score += 3.0
            reasons.append("same_feature")
        
        # +2 for same folder/package
        if self._is_same_folder_package(node, target_node):
            score += 2.0
            reasons.append("same_folder_package")
        
        # +2 for status=approved
        if node.get('status') == 'approved':
            score += 2.0
            reasons.append("status_approved")
        
        # +1 for modified ≤30 days
        if self._is_recently_modified(node):
            score += 1.0
            reasons.append("recently_modified")
        
        # -2 for deprecated
        if node.get('status') == 'deprecated':
            score -= 2.0
            reasons.append("deprecated")
        
        return score, reasons
    
    def _has_explicit_link(self, node: Dict[str, Any], target_node: Dict[str, Any]) -> bool:
        """Check if there's an explicit link between nodes"""
        # Check if target has edges to/from this node
        target_id = target_node['id']
        node_id = node['id']
        
        # Check outgoing edges from target
        for edge in self.graph.get_edges_from(target_id):
            if edge['to'] == node_id:
                return True
        
        # Check incoming edges to target
        for edge in self.graph.get_edges_to(target_id):
            if edge['from'] == node_id:
                return True
        
        return False
    
    def _is_same_feature(self, node: Dict[str, Any], feature: str) -> bool:
        """Check if node belongs to the same feature"""
        if not feature or not self.feature_map:
            return False
        
        # Check if node's file path matches feature patterns
        file_path = node.get('file_path', '')
        if not file_path:
            return False
        
        # Look for feature patterns in file path
        for pattern in self.feature_map.get(feature, {}).get('patterns', []):
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        
        return False
    
    def _is_same_folder_package(self, node: Dict[str, Any], target_node: Dict[str, Any]) -> bool:
        """Check if node is in same folder or package as target"""
        node_path = node.get('file_path', '')
        target_path = target_node.get('file_path', '')
        
        if not node_path or not target_path:
            return False
        
        node_path_obj = Path(node_path)
        target_path_obj = Path(target_path)
        
        # Same directory
        if node_path_obj.parent == target_path_obj.parent:
            return True
        
        # Same package (first two path components)
        if (len(node_path_obj.parts) >= 2 and len(target_path_obj.parts) >= 2 and
            node_path_obj.parts[:2] == target_path_obj.parts[:2]):
            return True
        
        return False
    
    def _is_recently_modified(self, node: Dict[str, Any]) -> bool:
        """Check if node was modified within last 30 days"""
        file_path = node.get('file_path', '')
        if not file_path:
            return False
        
        full_path = self.root_path / file_path
        if not full_path.exists():
            return False
        
        try:
            mtime = full_path.stat().st_mtime
            modified_date = datetime.fromtimestamp(mtime)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            return modified_date > thirty_days_ago
        except Exception:
            return False
    
    def _group_and_select_top_k(self, scored_nodes: List[Dict[str, Any]], top_k: int) -> Dict[str, List[Dict[str, Any]]]:
        """Group nodes by type and select top-K for each type"""
        grouped = {}
        
        for scored_node in scored_nodes:
            node_type = scored_node['type']
            if node_type not in grouped:
                grouped[node_type] = []
            grouped[node_type].append(scored_node)
        
        # Select top-K for each type
        result = {}
        for node_type, nodes in grouped.items():
            result[node_type] = nodes[:top_k]
        
        return result
    