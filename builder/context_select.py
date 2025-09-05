#!/usr/bin/env python3
"""
Context Selection and Ranking System.

Retrieves and ranks relevant pieces of context based on a starting path or feature.
Follows explicit links and uses weighted scoring to find the most relevant items.
"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime, date

from .context_graph import ContextGraph, GraphNode, GraphEdge

@dataclass
class ContextItem:
    """Represents a ranked context item."""
    node: GraphNode
    score: float
    reasons: List[str]
    distance: int  # How many hops from the starting point
    
    def __str__(self) -> str:
        return f"{self.node} (score: {self.score:.1f}, distance: {self.distance})"

class ContextSelector:
    """Selects and ranks relevant context items based on a starting point."""
    
    # Scoring weights as specified
    WEIGHTS = {
        'explicit_link': 4.0,      # +4 explicit link
        'same_feature': 3.0,       # +3 same feature
        'same_folder': 2.0,        # +2 same folder
        'approved_status': 2.0,    # +2 approved
        'recent': 1.0,             # +1 recent
        'deprecated': -2.0,        # -2 deprecated
        'over_budget': -2.0,       # -2 over-budget
    }
    
    def __init__(self, context_graph: ContextGraph):
        self.graph = context_graph
        self.visited_nodes: Set[str] = set()
        
    def select_context(self, 
                      start_path: Optional[str] = None, 
                      start_feature: Optional[str] = None,
                      max_items: int = 10,
                      max_distance: int = 2) -> List[ContextItem]:
        """
        Select and rank context items starting from a path or feature.
        
        Args:
            start_path: Starting file path (e.g., 'src/auth/login.ts')
            start_feature: Starting feature name (e.g., 'auth')
            max_items: Maximum number of items to return
            max_distance: Maximum distance (hops) to follow
            
        Returns:
            List of ranked ContextItem objects
        """
        if not start_path and not start_feature:
            raise ValueError("Either start_path or start_feature must be provided")
            
        # Reset state
        self.visited_nodes.clear()
        
        # Find starting nodes
        start_nodes = self._find_start_nodes(start_path, start_feature)
        if not start_nodes:
            return []
            
        # Collect all relevant nodes
        relevant_nodes = self._collect_relevant_nodes(start_nodes, max_distance)
        
        # Score and rank nodes
        scored_items = self._score_and_rank(relevant_nodes, start_nodes)
        
        # Return top-K items
        return scored_items[:max_items]
        
    def _find_start_nodes(self, start_path: Optional[str], start_feature: Optional[str]) -> List[GraphNode]:
        """Find starting nodes based on path or feature."""
        start_nodes = []
        
        if start_path:
            # Find nodes by file path
            for node in self.graph.nodes.values():
                if start_path in node.file_path or node.file_path.endswith(start_path):
                    start_nodes.append(node)
                    
        if start_feature:
            # Find nodes by feature
            for node in self.graph.nodes.values():
                if node.properties.get('feature') == start_feature:
                    start_nodes.append(node)
                    
        return start_nodes
        
    def _collect_relevant_nodes(self, start_nodes: List[GraphNode], max_distance: int) -> Dict[str, Tuple[GraphNode, int]]:
        """Collect all relevant nodes within max_distance hops."""
        relevant = {}
        to_process = [(node, 0) for node in start_nodes]
        
        while to_process:
            node, distance = to_process.pop(0)
            
            if node.id in self.visited_nodes or distance > max_distance:
                continue
                
            self.visited_nodes.add(node.id)
            relevant[node.id] = (node, distance)
            
            # Follow explicit links (one hop)
            if distance < max_distance:
                linked_nodes = self._get_explicit_links(node)
                for linked_node in linked_nodes:
                    if linked_node.id not in self.visited_nodes:
                        to_process.append((linked_node, distance + 1))
                        
            # Add nearby code/tests
            if distance < max_distance:
                nearby_nodes = self._get_nearby_code_tests(node)
                for nearby_node in nearby_nodes:
                    if nearby_node.id not in self.visited_nodes:
                        to_process.append((nearby_node, distance + 1))
                        
        return relevant
        
    def _get_explicit_links(self, node: GraphNode) -> List[GraphNode]:
        """Get nodes explicitly linked from this node."""
        linked_nodes = []
        
        # Follow outgoing edges
        for edge in self.graph.get_edges_from(node.id):
            if edge.edge_type in ['informs', 'implements', 'depends_on']:
                target_node = self.graph.get_node(edge.target_id)
                if target_node:
                    linked_nodes.append(target_node)
                    
        # Follow document links in metadata
        if node.metadata:
            links = node.metadata.get('links', [])
            if isinstance(links, list):
                for link_group in links:
                    if isinstance(link_group, dict):
                        for link_type, link_ids in link_group.items():
                            if isinstance(link_ids, list):
                                for link_id in link_ids:
                                    linked_node = self._find_node_by_id(link_id)
                                    if linked_node:
                                        linked_nodes.append(linked_node)
            elif isinstance(links, dict):
                for link_type, link_ids in links.items():
                    if isinstance(link_ids, list):
                        for link_id in link_ids:
                            linked_node = self._find_node_by_id(link_id)
                            if linked_node:
                                linked_nodes.append(linked_node)
                                
        return linked_nodes
        
    def _get_nearby_code_tests(self, node: GraphNode) -> List[GraphNode]:
        """Get nearby code and test files."""
        nearby_nodes = []
        
        if node.node_type == 'code':
            # For code files, find related code in same directory
            code_dir = Path(node.file_path).parent
            for other_node in self.graph.nodes.values():
                if (other_node.node_type == 'code' and 
                    other_node.id != node.id and
                    Path(other_node.file_path).parent == code_dir):
                    nearby_nodes.append(other_node)
                    
            # Find test files
            for other_node in self.graph.nodes.values():
                if (other_node.node_type == 'code' and
                    'test' in other_node.file_path.lower() and
                    other_node.properties.get('feature') == node.properties.get('feature')):
                    nearby_nodes.append(other_node)
                    
        else:
            # For documents, find related code in same feature
            feature = node.properties.get('feature')
            if feature:
                for other_node in self.graph.nodes.values():
                    if (other_node.node_type == 'code' and
                        other_node.properties.get('feature') == feature):
                        nearby_nodes.append(other_node)
                        
        return nearby_nodes
        
    def _find_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Find a node by ID with fuzzy matching."""
        # Exact match
        if node_id in self.graph.nodes:
            return self.graph.nodes[node_id]
            
        # Partial match
        for existing_id in self.graph.nodes.keys():
            if node_id in existing_id or existing_id in node_id:
                return self.graph.nodes[existing_id]
                
        return None
        
    def _score_and_rank(self, relevant_nodes: Dict[str, Tuple[GraphNode, int]], 
                       start_nodes: List[GraphNode]) -> List[ContextItem]:
        """Score and rank the relevant nodes."""
        scored_items = []
        start_features = {node.properties.get('feature') for node in start_nodes}
        start_folders = {Path(node.file_path).parent for node in start_nodes}
        
        for node_id, (node, distance) in relevant_nodes.items():
            score = 0.0
            reasons = []
            
            # Check if this is an explicit link
            is_explicit_link = self._is_explicit_link(node, start_nodes)
            if is_explicit_link:
                score += self.WEIGHTS['explicit_link']
                reasons.append(f"explicit link (+{self.WEIGHTS['explicit_link']})")
                
            # Check same feature
            node_feature = node.properties.get('feature')
            if node_feature in start_features:
                score += self.WEIGHTS['same_feature']
                reasons.append(f"same feature '{node_feature}' (+{self.WEIGHTS['same_feature']})")
                
            # Check same folder
            node_folder = Path(node.file_path).parent
            if node_folder in start_folders:
                score += self.WEIGHTS['same_folder']
                reasons.append(f"same folder (+{self.WEIGHTS['same_folder']})")
                
            # Check status bonuses/penalties
            status_score, status_reasons = self._get_status_score(node)
            score += status_score
            reasons.extend(status_reasons)
            
            # Check recency
            recency_score, recency_reason = self._get_recency_score(node)
            score += recency_score
            if recency_reason:
                reasons.append(recency_reason)
                
            # Check for over-budget (placeholder - would need budget info)
            if self._is_over_budget(node):
                score += self.WEIGHTS['over_budget']
                reasons.append(f"over budget ({self.WEIGHTS['over_budget']})")
                
            # Create context item
            item = ContextItem(
                node=node,
                score=score,
                reasons=reasons,
                distance=distance
            )
            scored_items.append(item)
            
        # Sort by score (descending), then by distance (ascending)
        scored_items.sort(key=lambda x: (-x.score, x.distance))
        
        return scored_items
        
    def _is_explicit_link(self, node: GraphNode, start_nodes: List[GraphNode]) -> bool:
        """Check if a node is explicitly linked from start nodes."""
        for start_node in start_nodes:
            # Check outgoing edges
            for edge in self.graph.get_edges_from(start_node.id):
                if edge.target_id == node.id:
                    return True
                    
            # Check document links
            if start_node.metadata:
                links = start_node.metadata.get('links', [])
                if isinstance(links, list):
                    for link_group in links:
                        if isinstance(link_group, dict):
                            for link_ids in link_group.values():
                                if isinstance(link_ids, list) and node.id in link_ids:
                                    return True
                elif isinstance(links, dict):
                    for link_ids in links.values():
                        if isinstance(link_ids, list) and node.id in link_ids:
                            return True
                            
        return False
        
    def _get_status_score(self, node: GraphNode) -> Tuple[float, List[str]]:
        """Get score based on document status."""
        score = 0.0
        reasons = []
        
        if node.metadata:
            status = node.metadata.get('status', '').lower()
            
            if status == 'approved':
                score += self.WEIGHTS['approved_status']
                reasons.append(f"approved status (+{self.WEIGHTS['approved_status']})")
            elif status in ['deprecated', 'superseded']:
                score += self.WEIGHTS['deprecated']
                reasons.append(f"{status} status ({self.WEIGHTS['deprecated']})")
                
        return score, reasons
        
    def _get_recency_score(self, node: GraphNode) -> Tuple[float, Optional[str]]:
        """Get score based on document recency."""
        if not node.metadata or 'created' not in node.metadata:
            return 0.0, None
            
        try:
            created_date = datetime.strptime(node.metadata['created'], '%Y-%m-%d').date()
            days_ago = (date.today() - created_date).days
            
            # Recent if created within last 30 days
            if days_ago <= 30:
                return self.WEIGHTS['recent'], f"recent ({days_ago} days ago, +{self.WEIGHTS['recent']})"
                
        except (ValueError, TypeError):
            pass
            
        return 0.0, None
        
    def _is_over_budget(self, node: GraphNode) -> bool:
        """Check if node is over budget (placeholder implementation)."""
        # This would need actual budget information
        # For now, return False
        return False
        
    def get_context_summary(self, items: List[ContextItem]) -> Dict[str, Any]:
        """Get a summary of the context items."""
        if not items:
            return {'total_items': 0, 'by_type': {}, 'by_feature': {}, 'by_distance': {}}
            
        by_type = defaultdict(int)
        by_feature = defaultdict(int)
        by_distance = defaultdict(int)
        
        for item in items:
            by_type[item.node.node_type] += 1
            by_feature[item.node.properties.get('feature', 'unknown')] += 1
            by_distance[item.distance] += 1
            
        return {
            'total_items': len(items),
            'by_type': dict(by_type),
            'by_feature': dict(by_feature),
            'by_distance': dict(by_distance),
            'score_range': {
                'min': min(item.score for item in items),
                'max': max(item.score for item in items),
                'avg': sum(item.score for item in items) / len(items)
            }
        }

def main():
    """Main function for testing context selection."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_select.py <project_root> [start_path] [start_feature]")
        sys.exit(1)
        
    project_root = sys.argv[1]
    start_path = sys.argv[2] if len(sys.argv) > 2 else None
    start_feature = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load context graph
    context_graph_path = os.path.join(project_root, "builder", "cache", "context_graph.json")
    if not os.path.exists(context_graph_path):
        print(f"Context graph not found at {context_graph_path}")
        print("Run 'python builder/cli.py context:scan' first")
        sys.exit(1)
        
    # Load graph from JSON
    with open(context_graph_path, 'r') as f:
        graph_data = json.load(f)
        
    # Reconstruct graph (simplified)
    graph = ContextGraph()
    for node_data in graph_data['nodes']:
        node = GraphNode(
            id=node_data['id'],
            node_type=node_data['type'],
            title=node_data['title'],
            file_path=node_data['file_path'],
            metadata=node_data['metadata'],
            properties=node_data['properties']
        )
        graph.add_node(node)
        
    for edge_data in graph_data['edges']:
        edge = GraphEdge(
            source_id=edge_data['source'],
            target_id=edge_data['target'],
            edge_type=edge_data['type'],
            weight=edge_data.get('weight', 1.0),
            metadata=edge_data.get('metadata', {})
        )
        graph.add_edge(edge)
        
    # Create selector and get context
    selector = ContextSelector(graph)
    
    if start_path:
        print(f"🔍 Selecting context for path: {start_path}")
    if start_feature:
        print(f"🔍 Selecting context for feature: {start_feature}")
        
    items = selector.select_context(start_path, start_feature, max_items=15)
    
    # Print results
    print(f"\n📊 Found {len(items)} relevant items:")
    print("=" * 60)
    
    for i, item in enumerate(items, 1):
        print(f"{i:2d}. {item}")
        if item.reasons:
            print(f"     Reasons: {', '.join(item.reasons)}")
        print()
        
    # Print summary
    summary = selector.get_context_summary(items)
    print("📈 Summary:")
    print(f"  Total items: {summary['total_items']}")
    print(f"  By type: {summary['by_type']}")
    print(f"  By feature: {summary['by_feature']}")
    print(f"  By distance: {summary['by_distance']}")
    if summary['total_items'] > 0:
        print(f"  Score range: {summary['score_range']['min']:.1f} - {summary['score_range']['max']:.1f} (avg: {summary['score_range']['avg']:.1f})")

if __name__ == "__main__":
    main()
