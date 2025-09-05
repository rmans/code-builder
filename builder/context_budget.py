#!/usr/bin/env python3
"""
Context Budget Manager - Token-aware budget allocation and management.

Manages token budgets for different context categories and handles overflow
by trimming lowest weight items while preserving critical sections.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import re

from .context_select import ContextItem, ContextSelector
from .context_graph import ContextGraph, GraphNode

class BudgetCategory(Enum):
    """Budget categories with their allocation percentages."""
    RULES = "rules"
    ACCEPTANCE = "acceptance" 
    ADRS = "adrs"
    INTEGRATIONS = "integrations"
    ARCH = "arch"
    CODE_TEST = "code_test"

# Budget allocation percentages as specified
BUDGET_ALLOCATIONS = {
    BudgetCategory.RULES: 0.15,        # 15%
    BudgetCategory.ACCEPTANCE: 0.25,   # 25%
    BudgetCategory.ADRS: 0.15,         # 15%
    BudgetCategory.INTEGRATIONS: 0.15, # 15%
    BudgetCategory.ARCH: 0.10,         # 10%
    BudgetCategory.CODE_TEST: 0.20,    # 20%
}

# Categories that must never be dropped
MUST_INCLUDE_CATEGORIES = {
    BudgetCategory.RULES,
    BudgetCategory.ACCEPTANCE
}

@dataclass
class BudgetItem:
    """Represents an item within a budget category."""
    content: str
    source: str  # File path or identifier
    weight: float  # Higher weight = more important
    category: BudgetCategory
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def token_count(self) -> int:
        """Estimate token count (1 token ≈ 4 characters)."""
        return len(self.content) // 4 if self.content else 0

@dataclass
class BudgetAllocation:
    """Represents budget allocation for a category."""
    category: BudgetCategory
    allocated_tokens: int
    used_tokens: int
    items: List[BudgetItem] = field(default_factory=list)
    
    @property
    def remaining_tokens(self) -> int:
        """Tokens remaining in this category."""
        return max(0, self.allocated_tokens - self.used_tokens)
    
    @property
    def is_over_budget(self) -> bool:
        """Whether this category is over budget."""
        return self.used_tokens > self.allocated_tokens

class ContextBudgetManager:
    """Manages token budgets for context categories."""
    
    def __init__(self, total_token_limit: int = 8000):
        self.total_token_limit = total_token_limit
        self.allocations = self._create_allocations()
        self.overflow_summaries = {}
        
    def _create_allocations(self) -> Dict[BudgetCategory, BudgetAllocation]:
        """Create budget allocations based on percentages."""
        allocations = {}
        for category, percentage in BUDGET_ALLOCATIONS.items():
            allocated_tokens = int(self.total_token_limit * percentage)
            allocations[category] = BudgetAllocation(
                category=category,
                allocated_tokens=allocated_tokens,
                used_tokens=0
            )
        return allocations
        
    def add_item(self, content: str, source: str, category: BudgetCategory, 
                 weight: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """
        Add an item to a budget category.
        
        Returns True if added successfully, False if would exceed budget.
        """
        if metadata is None:
            metadata = {}
            
        item = BudgetItem(
            content=content,
            source=source,
            weight=weight,
            category=category,
            metadata=metadata
        )
        
        allocation = self.allocations[category]
        
        # Check if adding this item would exceed budget
        if allocation.used_tokens + item.token_count > allocation.allocated_tokens:
            # If this is a must-include category, force add and handle overflow later
            if category in MUST_INCLUDE_CATEGORIES:
                allocation.items.append(item)
                allocation.used_tokens += item.token_count
                return True
            else:
                return False
        else:
            allocation.items.append(item)
            allocation.used_tokens += item.token_count
            return True
            
    def get_category_content(self, category: BudgetCategory) -> str:
        """Get all content for a category."""
        allocation = self.allocations[category]
        return '\n\n'.join(item.content for item in allocation.items)
        
    def get_total_usage(self) -> int:
        """Get total tokens used across all categories."""
        return sum(allocation.used_tokens for allocation in self.allocations.values())
        
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of budget usage."""
        total_used = self.get_total_usage()
        total_allocated = sum(allocation.allocated_tokens for allocation in self.allocations.values())
        
        summary = {
            'total_allocated': total_allocated,
            'total_used': total_used,
            'total_remaining': total_allocated - total_used,
            'is_over_budget': total_used > total_allocated,
            'categories': {}
        }
        
        for category, allocation in self.allocations.items():
            summary['categories'][category.value] = {
                'allocated': allocation.allocated_tokens,
                'used': allocation.used_tokens,
                'remaining': allocation.remaining_tokens,
                'is_over_budget': allocation.is_over_budget,
                'item_count': len(allocation.items)
            }
            
        return summary
        
    def handle_overflow(self) -> Dict[str, str]:
        """
        Handle budget overflow by trimming lowest weight items.
        Returns summaries of trimmed content.
        """
        summaries = {}
        
        # Sort categories by priority (must-include first, then by allocation percentage)
        category_priority = []
        for category in BudgetCategory:
            if category in MUST_INCLUDE_CATEGORIES:
                category_priority.append((0, category))  # Highest priority
            else:
                category_priority.append((1, category))
                
        category_priority.sort(key=lambda x: (x[0], -BUDGET_ALLOCATIONS[x[1]]))
        
        # Process each category
        for _, category in category_priority:
            allocation = self.allocations[category]
            
            if allocation.is_over_budget:
                # Trim items by weight (lowest first)
                allocation.items.sort(key=lambda x: x.weight, reverse=True)
                
                # Keep items that fit in budget
                kept_items = []
                used_tokens = 0
                trimmed_items = []
                
                for item in allocation.items:
                    if used_tokens + item.token_count <= allocation.allocated_tokens:
                        kept_items.append(item)
                        used_tokens += item.token_count
                    else:
                        trimmed_items.append(item)
                        
                # Update allocation
                allocation.items = kept_items
                allocation.used_tokens = used_tokens
                
                # Create summary of trimmed content
                if trimmed_items:
                    summaries[category.value] = self._create_overflow_summary(trimmed_items)
                    
        return summaries
        
    def _create_overflow_summary(self, trimmed_items: List[BudgetItem]) -> str:
        """Create a summary of trimmed items for overflow reporting."""
        if not trimmed_items:
            return ""
            
        summary_parts = []
        summary_parts.append(f"**{len(trimmed_items)} items trimmed due to budget constraints:**")
        summary_parts.append("")
        
        for item in trimmed_items:
            # Create a brief summary of the content
            content_preview = item.content[:200] + "..." if len(item.content) > 200 else item.content
            summary_parts.append(f"- **{item.source}** (weight: {item.weight:.1f}, tokens: {item.token_count})")
            summary_parts.append(f"  ```\n  {content_preview}\n  ```")
            summary_parts.append("")
            
        return '\n'.join(summary_parts)
        
    def build_context_package(self, context_items: List[ContextItem]) -> str:
        """
        Build a context package from selected items, respecting budget constraints.
        """
        # Clear existing allocations
        for allocation in self.allocations.values():
            allocation.items.clear()
            allocation.used_tokens = 0
            
        # Categorize and add items
        for item in context_items:
            category = self._categorize_item(item)
            weight = self._calculate_item_weight(item)
            
            # Extract content from the item
            content = self._extract_item_content(item)
            
            if content:
                self.add_item(
                    content=content,
                    source=item.node.file_path,
                    category=category,
                    weight=weight,
                    metadata={
                        'node_type': item.node.node_type,
                        'score': item.score,
                        'distance': item.distance
                    }
                )
                
        # Handle overflow
        overflow_summaries = self.handle_overflow()
        
        # Build final context package
        context_parts = []
        context_parts.append("# Context Package")
        context_parts.append("")
        context_parts.append(f"**Total Tokens**: {self.get_total_usage()}/{self.total_token_limit}")
        context_parts.append("")
        
        # Add each category's content
        for category in BudgetCategory:
            content = self.get_category_content(category)
            if content:
                context_parts.append(f"## {category.value.title()}")
                context_parts.append("")
                context_parts.append(content)
                context_parts.append("")
                
        # Add overflow summaries if any
        if overflow_summaries:
            context_parts.append("## Overflow Summaries")
            context_parts.append("")
            context_parts.append("*The following content was trimmed due to budget constraints:*")
            context_parts.append("")
            
            for category, summary in overflow_summaries.items():
                context_parts.append(f"### {category.title()}")
                context_parts.append("")
                context_parts.append(summary)
                context_parts.append("")
                
        return '\n'.join(context_parts)
        
    def _categorize_item(self, item: ContextItem) -> BudgetCategory:
        """Categorize a context item into a budget category."""
        node_type = item.node.node_type
        
        if node_type == 'rules':
            return BudgetCategory.RULES
        elif node_type in ['prd'] and 'acceptance' in item.node.title.lower():
            return BudgetCategory.ACCEPTANCE
        elif node_type == 'adr':
            return BudgetCategory.ADRS
        elif node_type == 'integrations':
            return BudgetCategory.INTEGRATIONS
        elif node_type == 'arch':
            return BudgetCategory.ARCH
        elif node_type == 'code':
            return BudgetCategory.CODE_TEST
        else:
            # Default categorization based on content
            content = self._extract_item_content(item)
            if 'acceptance' in content.lower() or 'criteria' in content.lower():
                return BudgetCategory.ACCEPTANCE
            elif 'rule' in content.lower() or 'guideline' in content.lower():
                return BudgetCategory.RULES
            else:
                return BudgetCategory.CODE_TEST
                
    def _calculate_item_weight(self, item: ContextItem) -> float:
        """Calculate weight for an item based on its properties."""
        weight = item.score  # Start with context selection score
        
        # Boost weight for must-include categories
        category = self._categorize_item(item)
        if category in MUST_INCLUDE_CATEGORIES:
            weight += 10.0
            
        # Boost weight for approved status
        if item.node.metadata and item.node.metadata.get('status') == 'approved':
            weight += 5.0
            
        # Boost weight for recent items
        if 'recent' in ' '.join(item.reasons):
            weight += 2.0
            
        # Reduce weight for deprecated items
        if item.node.metadata and item.node.metadata.get('status') in ['deprecated', 'superseded']:
            weight -= 5.0
            
        return max(0.1, weight)  # Ensure minimum weight
        
    def _extract_item_content(self, item: ContextItem) -> str:
        """Extract content from a context item."""
        # For now, return a simple representation
        # In a real implementation, this would read the actual file content
        content_parts = []
        content_parts.append(f"# {item.node.title}")
        content_parts.append(f"**Source**: {item.node.file_path}")
        content_parts.append(f"**Type**: {item.node.node_type}")
        content_parts.append(f"**Score**: {item.score:.1f}")
        content_parts.append("")
        
        if item.node.metadata:
            content_parts.append("**Metadata**:")
            for key, value in item.node.metadata.items():
                if key not in ['links']:  # Skip complex structures
                    content_parts.append(f"- {key}: {value}")
            content_parts.append("")
            
        # Add a placeholder for actual content
        content_parts.append("*[Content would be loaded from file]*")
        
        return '\n'.join(content_parts)

def main():
    """Main function for testing budget management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_budget.py <project_root> [token_limit]")
        sys.exit(1)
        
    project_root = sys.argv[1]
    token_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    # Load context graph
    context_graph_path = os.path.join(project_root, "builder", "cache", "context_graph.json")
    if not os.path.exists(context_graph_path):
        print(f"Context graph not found at {context_graph_path}")
        print("Run 'python builder/cli.py context:scan' first")
        sys.exit(1)
        
    # Load graph from JSON
    with open(context_graph_path, 'r') as f:
        graph_data = json.load(f)
        
    # Reconstruct graph
    from .context_graph import ContextGraph, GraphNode, GraphEdge
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
        
    # Create budget manager
    budget_manager = ContextBudgetManager(token_limit)
    
    # Get context items
    selector = ContextSelector(graph)
    items = selector.select_context(start_feature="auth", max_items=20)
    
    print(f"🔍 Building context package with {len(items)} items")
    print(f"📊 Token limit: {token_limit}")
    
    # Build context package
    context_package = budget_manager.build_context_package(items)
    
    # Print summary
    summary = budget_manager.get_usage_summary()
    print(f"\n📈 Budget Usage Summary:")
    print(f"  Total used: {summary['total_used']}/{summary['total_allocated']}")
    print(f"  Over budget: {summary['is_over_budget']}")
    print()
    
    for category, cat_summary in summary['categories'].items():
        status = "⚠️" if cat_summary['is_over_budget'] else "✅"
        print(f"  {status} {category}: {cat_summary['used']}/{cat_summary['allocated']} tokens ({cat_summary['item_count']} items)")
        
    # Save context package
    output_path = os.path.join(project_root, "builder", "cache", "context_package.md")
    with open(output_path, 'w') as f:
        f.write(context_package)
    print(f"\n📁 Context package saved to: {output_path}")

if __name__ == "__main__":
    main()
