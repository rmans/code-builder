"""
Context Budget Manager - Token-aware budgeting and overflow handling
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BudgetItem:
    """Represents a budget item with content and metadata"""
    id: str
    type: str
    title: str
    content: str
    file_path: str
    weight: float
    token_estimate: int
    source_anchor: str = ""


class ContextBudgetManager:
    """Token-aware budget manager for context selection"""
    
    def __init__(self, total_budget: int = 8000):
        from ..config.settings import get_config
        self.config = get_config()
        
        # Per-purpose budget percentages
        self.BUDGET_PERCENTAGES = {
            'rules': self.config.budget_rules,      # 15%
            'acceptance': self.config.budget_acceptance, # 25%
            'adr': self.config.budget_adr,        # 15%
            'integration': self.config.budget_integration, # 15%
            'arch': self.config.budget_arch,       # 10%
            'code': self.config.budget_code        # 20% (code + test)
        }
        
        # Token estimation factor
        self.TOKEN_FACTOR = self.config.budget_token_factor
        
        self.total_budget = total_budget
        self.budget_allocations = self._calculate_budget_allocations()
    
    def _calculate_budget_allocations(self) -> Dict[str, int]:
        """Calculate token budget allocations per type"""
        allocations = {}
        for item_type, percentage in self.BUDGET_PERCENTAGES.items():
            allocations[item_type] = int(self.total_budget * percentage)
        return allocations
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using words * 1.3"""
        if not text:
            return 0
        
        # Count words (simple whitespace-based splitting)
        words = len(text.split())
        return int(words * self.TOKEN_FACTOR)
    
    def create_budget_items(self, context_selection: Dict[str, List[Dict[str, Any]]]) -> List[BudgetItem]:
        """Convert context selection to budget items"""
        budget_items = []
        
        for item_type, items in context_selection.items():
            for item in items:
                # Map context types to budget types
                budget_type = self._map_to_budget_type(item_type)
                
                # Extract content from the item
                content = self._extract_content(item)
                
                # Create source anchor
                source_anchor = self._create_source_anchor(item)
                
                # Estimate tokens
                token_estimate = self.estimate_tokens(content)
                
                # Calculate weight (higher score = higher weight)
                weight = item.get('score', 0.0)
                
                budget_item = BudgetItem(
                    id=item['id'],
                    type=budget_type,
                    title=item['node'].get('title', item['id']),
                    content=content,
                    file_path=item['node'].get('file_path', ''),
                    weight=weight,
                    token_estimate=token_estimate,
                    source_anchor=source_anchor
                )
                
                budget_items.append(budget_item)
        
        return budget_items
    
    def _map_to_budget_type(self, context_type: str) -> str:
        """Map context types to budget types"""
        mapping = {
            'prd': 'acceptance',
            'arch': 'arch',
            'adr': 'adr',
            'integration': 'integration',
            'code': 'code',
            'rules': 'rules',
            'ux': 'arch',  # UX goes to arch budget
            'impl': 'arch',  # Implementation goes to arch budget
            'exec': 'arch',  # Execution goes to arch budget
            'task': 'arch'   # Tasks go to arch budget
        }
        return mapping.get(context_type, 'arch')
    
    def _extract_content(self, item: Dict[str, Any]) -> str:
        """Extract content from a context item"""
        node = item['node']
        
        # Try to read the actual file content
        file_path = node.get('file_path', '')
        if file_path:
            try:
                full_path = Path(file_path)
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8')
                    # Extract just the body content (skip front-matter)
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            return parts[2].strip()
                    return content
            except Exception:
                pass
        
        # Fallback to title and metadata
        title = node.get('title', item['id'])
        status = node.get('status', '')
        owner = node.get('owner', '')
        
        content_parts = [title]
        if status:
            content_parts.append(f"Status: {status}")
        if owner:
            content_parts.append(f"Owner: {owner}")
        
        return '\n'.join(content_parts)
    
    def _create_source_anchor(self, item: Dict[str, Any]) -> str:
        """Create a source anchor for referencing the item"""
        node = item['node']
        file_path = node.get('file_path', '')
        title = node.get('title', item['id'])
        
        if file_path:
            return f"[{title}]({file_path})"
        else:
            return f"[{title}]"
    
    def apply_budget(self, budget_items: List[BudgetItem]) -> Tuple[List[BudgetItem], List[BudgetItem], Dict[str, Any]]:
        """Apply budget constraints and return selected items, overflow, and summary"""
        # Group items by budget type
        grouped_items = self._group_by_budget_type(budget_items)
        
        # Apply budget per type
        selected_items = []
        overflow_items = []
        budget_summary = {}
        
        for budget_type, items in grouped_items.items():
            budget_limit = self.budget_allocations[budget_type]
            type_selected, type_overflow, type_summary = self._apply_type_budget(
                items, budget_limit, budget_type
            )
            
            selected_items.extend(type_selected)
            overflow_items.extend(type_overflow)
            budget_summary[budget_type] = type_summary
        
        return selected_items, overflow_items, budget_summary
    
    def _group_by_budget_type(self, budget_items: List[BudgetItem]) -> Dict[str, List[BudgetItem]]:
        """Group budget items by their budget type"""
        grouped = {}
        for item in budget_items:
            budget_type = item.type
            if budget_type not in grouped:
                grouped[budget_type] = []
            grouped[budget_type].append(item)
        
        # Sort each group by weight (descending)
        for items in grouped.values():
            items.sort(key=lambda x: x.weight, reverse=True)
        
        return grouped
    
    def _apply_type_budget(self, items: List[BudgetItem], budget_limit: int, budget_type: str) -> Tuple[List[BudgetItem], List[BudgetItem], Dict[str, Any]]:
        """Apply budget constraints to items of a specific type"""
        selected = []
        overflow = []
        used_tokens = 0
        
        # Special handling for rules and acceptance - they are never dropped
        is_protected = budget_type in ['rules', 'acceptance']
        
        for item in items:
            if used_tokens + item.token_estimate <= budget_limit:
                selected.append(item)
                used_tokens += item.token_estimate
            else:
                if is_protected:
                    # For protected types, compress the last item instead of dropping
                    if selected:
                        last_item = selected[-1]
                        # Compress the last item
                        compressed_content = self._compress_content(last_item.content)
                        compressed_tokens = self.estimate_tokens(compressed_content)
                        
                        # If compression frees up enough space, add the new item
                        if used_tokens - last_item.token_estimate + compressed_tokens + item.token_estimate <= budget_limit:
                            last_item.content = compressed_content
                            last_item.token_estimate = compressed_tokens
                            used_tokens = used_tokens - last_item.token_estimate + compressed_tokens
                            selected.append(item)
                            used_tokens += item.token_estimate
                        else:
                            overflow.append(item)
                    else:
                        # If no items selected yet, compress this item and add it
                        compressed_content = self._compress_content(item.content)
                        compressed_tokens = self.estimate_tokens(compressed_content)
                        item.content = compressed_content
                        item.token_estimate = compressed_tokens
                        selected.append(item)
                        used_tokens += compressed_tokens
                else:
                    overflow.append(item)
        
        summary = {
            'total_items': len(items),
            'selected_items': len(selected),
            'overflow_items': len(overflow),
            'budget_limit': budget_limit,
            'used_tokens': used_tokens,
            'budget_utilization': used_tokens / budget_limit if budget_limit > 0 else 0
        }
        
        return selected, overflow, summary
    
    def _compress_content(self, content: str) -> str:
        """Compress content by summarizing it"""
        if not content:
            return content
        
        # Simple compression: take first 200 characters and add "..."
        if len(content) > 200:
            return content[:200] + "..."
        
        return content
    
    def create_overflow_summary(self, overflow_items: List[BudgetItem]) -> str:
        """Create a summary of overflow items with source anchors"""
        if not overflow_items:
            return ""
        
        # Group overflow by type
        grouped_overflow = {}
        for item in overflow_items:
            if item.type not in grouped_overflow:
                grouped_overflow[item.type] = []
            grouped_overflow[item.type].append(item)
        
        summary_parts = ["## Overflow Items (Excluded due to budget constraints)"]
        
        for overflow_type, items in grouped_overflow.items():
            summary_parts.append(f"\n### {overflow_type.upper()} ({len(items)} items)")
            
            for item in items:
                summary_parts.append(f"- {item.source_anchor} (weight: {item.weight:.1f}, tokens: {item.token_estimate})")
        
        return '\n'.join(summary_parts)
    
    def create_budget_report(self, selected_items: List[BudgetItem], overflow_items: List[BudgetItem], budget_summary: Dict[str, Any]) -> str:
        """Create a comprehensive budget report"""
        report_parts = ["# Context Budget Report"]
        
        # Overall summary
        total_selected = len(selected_items)
        total_overflow = len(overflow_items)
        total_tokens = sum(item.token_estimate for item in selected_items)
        
        report_parts.append(f"\n## Summary")
        report_parts.append(f"- Total selected items: {total_selected}")
        report_parts.append(f"- Total overflow items: {total_overflow}")
        report_parts.append(f"- Total tokens used: {total_tokens}")
        report_parts.append(f"- Budget utilization: {total_tokens / self.total_budget * 100:.1f}%")
        
        # Per-type breakdown
        report_parts.append(f"\n## Budget Allocation by Type")
        for budget_type, summary in budget_summary.items():
            report_parts.append(f"\n### {budget_type.upper()}")
            report_parts.append(f"- Selected: {summary['selected_items']}/{summary['total_items']} items")
            report_parts.append(f"- Tokens: {summary['used_tokens']}/{summary['budget_limit']} ({summary['budget_utilization']*100:.1f}%)")
        
        # Selected items by type
        selected_by_type = {}
        for item in selected_items:
            if item.type not in selected_by_type:
                selected_by_type[item.type] = []
            selected_by_type[item.type].append(item)
        
        report_parts.append(f"\n## Selected Items by Type")
        for item_type, items in selected_by_type.items():
            report_parts.append(f"\n### {item_type.upper()} ({len(items)} items)")
            for item in items:
                report_parts.append(f"- {item.source_anchor} (weight: {item.weight:.1f}, tokens: {item.token_estimate})")
        
        # Overflow summary
        if overflow_items:
            overflow_summary = self.create_overflow_summary(overflow_items)
            report_parts.append(f"\n{overflow_summary}")
        
        return '\n'.join(report_parts)
    
    def save_budget_results(self, selected_items: List[BudgetItem], overflow_items: List[BudgetItem], 
                          budget_summary: Dict[str, Any], output_file: str) -> None:
        """Save budget results to JSON file"""
        results = {
            'selected_items': [
                {
                    'id': item.id,
                    'type': item.type,
                    'title': item.title,
                    'content': item.content,
                    'file_path': item.file_path,
                    'weight': item.weight,
                    'token_estimate': item.token_estimate,
                    'source_anchor': item.source_anchor
                }
                for item in selected_items
            ],
            'overflow_items': [
                {
                    'id': item.id,
                    'type': item.type,
                    'title': item.title,
                    'file_path': item.file_path,
                    'weight': item.weight,
                    'token_estimate': item.token_estimate,
                    'source_anchor': item.source_anchor
                }
                for item in overflow_items
            ],
            'budget_summary': budget_summary,
            'total_budget': self.total_budget,
            'budget_allocations': self.budget_allocations
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)