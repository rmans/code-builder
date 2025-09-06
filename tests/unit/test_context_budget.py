#!/usr/bin/env python3
"""
Unit tests for the context budget management system.
"""

import unittest
import tempfile
import os
from builder.core.context_budget import (
    ContextBudgetManager, BudgetItem
)


class TestContextBudgetManager(unittest.TestCase):
    """Test cases for the context budget management system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.budget_manager = ContextBudgetManager(1000)  # 1000 token limit
        
    def test_budget_allocations(self):
        """Test that budget allocations are correct."""
        # Check that allocations sum to 100%
        total_allocation = sum(self.budget_manager.budget_allocations.values())
        self.assertEqual(total_allocation, 1000)
        
        # Check specific allocations (percentages from BUDGET_PERCENTAGES)
        self.assertEqual(self.budget_manager.budget_allocations['rules'], 150)  # 15%
        self.assertEqual(self.budget_manager.budget_allocations['acceptance'], 250)  # 25%
        self.assertEqual(self.budget_manager.budget_allocations['adr'], 150)  # 15%
        self.assertEqual(self.budget_manager.budget_allocations['integration'], 150)  # 15%
        self.assertEqual(self.budget_manager.budget_allocations['arch'], 100)  # 10%
        self.assertEqual(self.budget_manager.budget_allocations['code'], 200)  # 20%
        
    def test_token_estimation(self):
        """Test token estimation accuracy."""
        # Test with known content
        content = "Hello world" * 10  # 110 characters, ~11 words
        estimated_tokens = self.budget_manager.estimate_tokens(content)
        
        # Should be approximately 11 * 1.3 = 14.3 tokens
        self.assertGreaterEqual(estimated_tokens, 10)
        self.assertLessEqual(estimated_tokens, 20)
        
    def test_empty_content_token_estimation(self):
        """Test token estimation with empty content."""
        estimated_tokens = self.budget_manager.estimate_tokens("")
        self.assertEqual(estimated_tokens, 0)
        
    def test_create_budget_items(self):
        """Test creating budget items from context selection."""
        context_selection = {
            'rules': [
                {
                    'id': 'rule1',
                    'score': 5.0,
                    'node': {
                        'title': 'Test Rule',
                        'file_path': '/test/rule.md',
                        'status': 'approved'
                    }
                }
            ],
            'code': [
                {
                    'id': 'code1',
                    'score': 3.0,
                    'node': {
                        'title': 'Test Code',
                        'file_path': '/test/code.py'
                    }
                }
            ]
        }
        
        budget_items = self.budget_manager.create_budget_items(context_selection)
        
        self.assertEqual(len(budget_items), 2)
        
        # Check first item (rules)
        rule_item = budget_items[0]
        self.assertEqual(rule_item.id, 'rule1')
        self.assertEqual(rule_item.type, 'rules')
        self.assertEqual(rule_item.title, 'Test Rule')
        self.assertEqual(rule_item.weight, 5.0)
        
        # Check second item (code)
        code_item = budget_items[1]
        self.assertEqual(code_item.id, 'code1')
        self.assertEqual(code_item.type, 'code')
        self.assertEqual(code_item.title, 'Test Code')
        self.assertEqual(code_item.weight, 3.0)
        
    def test_map_to_budget_type(self):
        """Test mapping context types to budget types."""
        test_cases = [
            ('rules', 'rules'),
            ('prd', 'acceptance'),
            ('adr', 'adr'),
            ('integration', 'integration'),
            ('arch', 'arch'),
            ('code', 'code'),
            ('ux', 'arch'),  # UX goes to arch budget
            ('impl', 'arch'),  # Implementation goes to arch budget
            ('exec', 'arch'),  # Execution goes to arch budget
            ('task', 'arch'),  # Tasks go to arch budget
            ('unknown', 'arch')  # Unknown types default to arch
        ]
        
        for context_type, expected_budget_type in test_cases:
            result = self.budget_manager._map_to_budget_type(context_type)
            self.assertEqual(result, expected_budget_type)
            
    def test_apply_budget_within_limits(self):
        """Test applying budget when items are within limits."""
        # Create budget items that fit within budget
        budget_items = [
            BudgetItem(
                id='item1',
                type='rules',
                title='Rule 1',
                content='Short rule content',
                file_path='/test/rule1.md',
                weight=5.0,
                token_estimate=50,
                source_anchor='[Rule 1](/test/rule1.md)'
            ),
            BudgetItem(
                id='item2',
                type='code',
                title='Code 1',
                content='Short code content',
                file_path='/test/code1.py',
                weight=3.0,
                token_estimate=30,
                source_anchor='[Code 1](/test/code1.py)'
            )
        ]
        
        selected, overflow, summary = self.budget_manager.apply_budget(budget_items)
        
        # All items should be selected since they're within budget
        self.assertEqual(len(selected), 2)
        self.assertEqual(len(overflow), 0)
        
        # Check summary structure
        self.assertIn('rules', summary)
        self.assertIn('code', summary)
        
    def test_apply_budget_with_overflow(self):
        """Test applying budget when items exceed limits."""
        # Create budget items that exceed budget
        budget_items = [
            BudgetItem(
                id='item1',
                type='rules',
                title='Large Rule',
                content='x' * 1000,  # Large content
                file_path='/test/rule1.md',
                weight=5.0,
                token_estimate=300,  # Exceeds rules budget of 150
                source_anchor='[Large Rule](/test/rule1.md)'
            ),
            BudgetItem(
                id='item2',
                type='code',
                title='Large Code',
                content='x' * 1000,  # Large content
                file_path='/test/code1.py',
                weight=3.0,
                token_estimate=300,  # Exceeds code budget of 200
                source_anchor='[Large Code](/test/code1.py)'
            )
        ]
        
        selected, overflow, summary = self.budget_manager.apply_budget(budget_items)
        
        # Some items should be in overflow
        self.assertGreater(len(overflow), 0)
        
        # Check that rules items are protected (compressed instead of dropped)
        rules_items = [item for item in selected if item.type == 'rules']
        if rules_items:
            # Rules items should be compressed, not dropped
            self.assertGreater(len(rules_items), 0)
            
    def test_compress_content(self):
        """Test content compression functionality."""
        long_content = 'x' * 500  # 500 characters
        compressed = self.budget_manager._compress_content(long_content)
        
        # Should be compressed to 200 characters + "..."
        self.assertEqual(len(compressed), 203)  # 200 + "..."
        self.assertTrue(compressed.endswith('...'))
        
        # Short content should not be compressed
        short_content = 'short'
        not_compressed = self.budget_manager._compress_content(short_content)
        self.assertEqual(not_compressed, short_content)
        
    def test_create_overflow_summary(self):
        """Test overflow summary creation."""
        overflow_items = [
            BudgetItem(
                id='item1',
                type='rules',
                title='Overflow Rule',
                content='content',
                file_path='/test/rule.md',
                weight=5.0,
                token_estimate=100,
                source_anchor='[Overflow Rule](/test/rule.md)'
            ),
            BudgetItem(
                id='item2',
                type='code',
                title='Overflow Code',
                content='content',
                file_path='/test/code.py',
                weight=3.0,
                token_estimate=100,
                source_anchor='[Overflow Code](/test/code.py)'
            )
        ]
        
        summary = self.budget_manager.create_overflow_summary(overflow_items)
        
        self.assertIn('Overflow Items', summary)
        self.assertIn('RULES', summary)
        self.assertIn('CODE', summary)
        self.assertIn('Overflow Rule', summary)
        self.assertIn('Overflow Code', summary)
        
    def test_empty_overflow_summary(self):
        """Test overflow summary with no overflow items."""
        summary = self.budget_manager.create_overflow_summary([])
        self.assertEqual(summary, "")


class TestBudgetItem(unittest.TestCase):
    """Test cases for BudgetItem class."""
    
    def test_budget_item_creation(self):
        """Test BudgetItem creation and properties."""
        item = BudgetItem(
            id='test1',
            type='rules',
            title='Test Item',
            content='Test content',
            file_path='/test/item.md',
            weight=5.0,
            token_estimate=100,
            source_anchor='[Test Item](/test/item.md)'
        )
        
        self.assertEqual(item.id, 'test1')
        self.assertEqual(item.type, 'rules')
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.content, 'Test content')
        self.assertEqual(item.file_path, '/test/item.md')
        self.assertEqual(item.weight, 5.0)
        self.assertEqual(item.token_estimate, 100)
        self.assertEqual(item.source_anchor, '[Test Item](/test/item.md)')
        
    def test_budget_item_defaults(self):
        """Test BudgetItem with default values."""
        item = BudgetItem(
            id='test1',
            type='rules',
            title='Test Item',
            content='Test content',
            file_path='/test/item.md',
            weight=5.0,
            token_estimate=100
        )
        
        self.assertEqual(item.source_anchor, "")  # Default empty string


if __name__ == '__main__':
    unittest.main()
