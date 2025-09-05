#!/usr/bin/env python3
"""
Unit tests for the context budget management system.
"""

import unittest
import tempfile
import os
from builder.context_budget import (
    ContextBudgetManager, BudgetCategory, BudgetItem, BudgetAllocation
)

class TestContextBudgetManager(unittest.TestCase):
    """Test cases for the context budget management system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.budget_manager = ContextBudgetManager(1000)  # 1000 token limit
        
    def test_budget_allocations(self):
        """Test that budget allocations are correct."""
        # Check that allocations sum to 100%
        total_allocation = sum(self.budget_manager.allocations[cat].allocated_tokens 
                              for cat in BudgetCategory)
        self.assertEqual(total_allocation, 1000)
        
        # Check specific allocations
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.RULES].allocated_tokens, 150)  # 15%
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.ACCEPTANCE].allocated_tokens, 250)  # 25%
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.ADRS].allocated_tokens, 150)  # 15%
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.INTEGRATIONS].allocated_tokens, 150)  # 15%
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.ARCH].allocated_tokens, 100)  # 10%
        self.assertEqual(self.budget_manager.allocations[BudgetCategory.CODE_TEST].allocated_tokens, 200)  # 20%
        
    def test_add_item_within_budget(self):
        """Test adding items within budget."""
        success = self.budget_manager.add_item(
            content="Test content",
            source="test.md",
            category=BudgetCategory.RULES,
            weight=1.0
        )
        
        self.assertTrue(success)
        self.assertEqual(len(self.budget_manager.allocations[BudgetCategory.RULES].items), 1)
        
    def test_add_item_exceeds_budget(self):
        """Test adding items that exceed budget."""
        # Add a large item that exceeds the rules budget
        large_content = "x" * 1000  # 250 tokens
        success = self.budget_manager.add_item(
            content=large_content,
            source="large.md",
            category=BudgetCategory.ARCH,  # 100 token budget
            weight=1.0
        )
        
        # Should fail for non-must-include categories
        self.assertFalse(success)
        
    def test_must_include_categories(self):
        """Test that must-include categories can exceed budget."""
        # Add a large item to a must-include category
        large_content = "x" * 1000  # 250 tokens
        success = self.budget_manager.add_item(
            content=large_content,
            source="large_rules.md",
            category=BudgetCategory.RULES,  # Must include
            weight=1.0
        )
        
        # Should succeed even if exceeds budget
        self.assertTrue(success)
        
    def test_token_counting(self):
        """Test token counting accuracy."""
        item = BudgetItem(
            content="Hello world",  # 11 characters = ~2-3 tokens
            source="test.md",
            weight=1.0,
            category=BudgetCategory.RULES
        )
        
        # Should be approximately 2-3 tokens
        self.assertGreaterEqual(item.token_count, 2)
        self.assertLessEqual(item.token_count, 3)
        
    def test_usage_summary(self):
        """Test usage summary generation."""
        # Add some items
        self.budget_manager.add_item("Test rules", "rules.md", BudgetCategory.RULES, 1.0)
        self.budget_manager.add_item("Test acceptance", "acceptance.md", BudgetCategory.ACCEPTANCE, 1.0)
        
        summary = self.budget_manager.get_usage_summary()
        
        self.assertIn('total_allocated', summary)
        self.assertIn('total_used', summary)
        self.assertIn('total_remaining', summary)
        self.assertIn('is_over_budget', summary)
        self.assertIn('categories', summary)
        
        self.assertEqual(summary['total_allocated'], 1000)
        self.assertGreater(summary['total_used'], 0)
        
    def test_handle_overflow(self):
        """Test overflow handling with weight-based trimming."""
        # Add multiple items to code_test category (200 token budget)
        items = [
            ("Small item 1", 5.0),  # High weight
            ("Small item 2", 3.0),  # Medium weight
            ("Large item 1", 1.0),  # Low weight, but large
            ("Large item 2", 2.0),  # Low weight, large
        ]
        
        for content, weight in items:
            # Create content that will exceed budget when all added
            large_content = content + " " + "x" * 200  # ~50 tokens each
            self.budget_manager.add_item(
                content=large_content,
                source=f"{content}.ts",
                category=BudgetCategory.CODE_TEST,
                weight=weight
            )
            
        # Should be over budget now
        self.assertTrue(self.budget_manager.allocations[BudgetCategory.CODE_TEST].is_over_budget)
        
        # Handle overflow
        overflow_summaries = self.budget_manager.handle_overflow()
        
        # Should have trimmed some items
        self.assertIn('code_test', overflow_summaries)
        self.assertGreater(len(overflow_summaries['code_test']), 0)
        
        # Should keep higher weight items
        remaining_items = self.budget_manager.allocations[BudgetCategory.CODE_TEST].items
        if remaining_items:
            # Should be sorted by weight (highest first)
            weights = [item.weight for item in remaining_items]
            self.assertEqual(weights, sorted(weights, reverse=True))
            
    def test_must_include_preservation(self):
        """Test that must-include categories are never dropped."""
        # Add large items to must-include categories
        large_rules = "x" * 1000  # 250 tokens
        large_acceptance = "x" * 1000  # 250 tokens
        
        self.budget_manager.add_item(large_rules, "rules.md", BudgetCategory.RULES, 1.0)
        self.budget_manager.add_item(large_acceptance, "acceptance.md", BudgetCategory.ACCEPTANCE, 1.0)
        
        # Add items to non-must-include category
        self.budget_manager.add_item("Small arch", "arch.md", BudgetCategory.ARCH, 1.0)
        
        # Handle overflow
        overflow_summaries = self.budget_manager.handle_overflow()
        
        # Must-include categories should still have items
        self.assertGreater(len(self.budget_manager.allocations[BudgetCategory.RULES].items), 0)
        self.assertGreater(len(self.budget_manager.allocations[BudgetCategory.ACCEPTANCE].items), 0)
        
    def test_category_content_retrieval(self):
        """Test retrieving content for categories."""
        # Add items to different categories
        self.budget_manager.add_item("Rules content", "rules.md", BudgetCategory.RULES, 1.0)
        self.budget_manager.add_item("Acceptance content", "acceptance.md", BudgetCategory.ACCEPTANCE, 1.0)
        
        rules_content = self.budget_manager.get_category_content(BudgetCategory.RULES)
        acceptance_content = self.budget_manager.get_category_content(BudgetCategory.ACCEPTANCE)
        
        self.assertIn("Rules content", rules_content)
        self.assertIn("Acceptance content", acceptance_content)
        
    def test_empty_categories(self):
        """Test handling of empty categories."""
        empty_content = self.budget_manager.get_category_content(BudgetCategory.INTEGRATIONS)
        self.assertEqual(empty_content, "")
        
    def test_weight_calculation(self):
        """Test weight calculation for context items."""
        # This would require a ContextItem, so we'll test the method directly
        # Create a mock context item structure
        class MockContextItem:
            def __init__(self, score, reasons, node_metadata, node_type):
                self.score = score
                self.reasons = reasons
                self.node = type('Node', (), {
                    'metadata': node_metadata,
                    'node_type': node_type
                })()
                
        # Test weight calculation
        mock_item = MockContextItem(
            score=5.0,
            reasons=['same feature auth (+3.0)', 'recent (0 days ago, +1.0)'],
            node_metadata={'status': 'approved'},
            node_type='rules'
        )
        
        weight = self.budget_manager._calculate_item_weight(mock_item)
        
        # Should be base score + must-include bonus + approved bonus + recent bonus
        expected_weight = 5.0 + 10.0 + 5.0 + 2.0  # 22.0
        self.assertEqual(weight, expected_weight)
        
    def test_categorization(self):
        """Test item categorization logic."""
        # Test different node types
        test_cases = [
            ('rules', BudgetCategory.RULES),
            ('prd', BudgetCategory.ACCEPTANCE),  # PRD with acceptance in title
            ('adr', BudgetCategory.ADRS),
            ('integrations', BudgetCategory.INTEGRATIONS),
            ('arch', BudgetCategory.ARCH),
            ('code', BudgetCategory.CODE_TEST),
        ]
        
        for node_type, expected_category in test_cases:
            # Create mock context item
            class MockContextItem:
                def __init__(self, node_type, title):
                    self.node = type('Node', (), {
                        'node_type': node_type,
                        'title': title
                    })()
                    
            mock_item = MockContextItem(node_type, f"Test {node_type}")
            category = self.budget_manager._categorize_item(mock_item)
            self.assertEqual(category, expected_category)

class TestBudgetItem(unittest.TestCase):
    """Test cases for BudgetItem class."""
    
    def test_token_counting(self):
        """Test token counting in BudgetItem."""
        # Test with known content
        content = "Hello world" * 10  # 110 characters
        item = BudgetItem(
            content=content,
            source="test.md",
            weight=1.0,
            category=BudgetCategory.RULES
        )
        
        # Should be approximately 110/4 = 27-28 tokens
        self.assertGreaterEqual(item.token_count, 25)
        self.assertLessEqual(item.token_count, 30)
        
    def test_empty_content(self):
        """Test handling of empty content."""
        item = BudgetItem(
            content="",
            source="empty.md",
            weight=1.0,
            category=BudgetCategory.RULES
        )
        
        self.assertEqual(item.token_count, 0)

class TestBudgetAllocation(unittest.TestCase):
    """Test cases for BudgetAllocation class."""
    
    def test_remaining_tokens(self):
        """Test remaining tokens calculation."""
        allocation = BudgetAllocation(
            category=BudgetCategory.RULES,
            allocated_tokens=100,
            used_tokens=30
        )
        
        self.assertEqual(allocation.remaining_tokens, 70)
        
    def test_over_budget_detection(self):
        """Test over budget detection."""
        allocation = BudgetAllocation(
            category=BudgetCategory.RULES,
            allocated_tokens=100,
            used_tokens=150
        )
        
        self.assertTrue(allocation.is_over_budget)
        
    def test_under_budget_detection(self):
        """Test under budget detection."""
        allocation = BudgetAllocation(
            category=BudgetCategory.RULES,
            allocated_tokens=100,
            used_tokens=50
        )
        
        self.assertFalse(allocation.is_over_budget)

if __name__ == '__main__':
    unittest.main()
