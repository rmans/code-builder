#!/usr/bin/env python3
"""
Test script for the context budget manager.
"""

from builder.context_budget import ContextBudgetManager, BudgetCategory, BudgetItem

def test_budget_manager():
    """Test the budget manager functionality."""
    print("🧪 Testing Context Budget Manager")
    print("=" * 40)
    
    # Create budget manager with small limit for testing
    budget_manager = ContextBudgetManager(1000)  # 1000 tokens
    
    # Test adding items
    print("📝 Adding test items...")
    
    # Add rules item (must include)
    success = budget_manager.add_item(
        content="Rule 1: Keep files under 300 LOC\nRule 2: Tests mirror acceptance criteria 1:1",
        source="docs/rules/00-global.md",
        category=BudgetCategory.RULES,
        weight=10.0
    )
    print(f"  Rules item added: {success}")
    
    # Add acceptance criteria (must include)
    success = budget_manager.add_item(
        content="Acceptance Criteria:\n- User can authenticate with valid credentials\n- System validates tokens according to ADR-0001",
        source="docs/prd/PRD-test-prd.md",
        category=BudgetCategory.ACCEPTANCE,
        weight=8.0
    )
    print(f"  Acceptance item added: {success}")
    
    # Add ADR item
    success = budget_manager.add_item(
        content="ADR-0001: Create hello module\nContext: We need a hello module for testing\nDecision: Create a simple hello.ts module",
        source="docs/adrs/ADR-0001.md",
        category=BudgetCategory.ADRS,
        weight=5.0
    )
    print(f"  ADR item added: {success}")
    
    # Add code item
    success = budget_manager.add_item(
        content="export class AuthService {\n  async login(credentials) {\n    // Implementation here\n  }\n}",
        source="src/auth/login.ts",
        category=BudgetCategory.CODE_TEST,
        weight=3.0
    )
    print(f"  Code item added: {success}")
    
    # Add another code item (should cause overflow)
    success = budget_manager.add_item(
        content="export class TestService {\n  async testMethod() {\n    // Very long implementation that exceeds budget\n    const longString = 'x' * 1000;\n    return longString;\n  }\n}",
        source="src/test/service.ts",
        category=BudgetCategory.CODE_TEST,
        weight=2.0
    )
    print(f"  Large code item added: {success}")
    
    # Print usage summary
    print("\n📊 Budget Usage Summary:")
    summary = budget_manager.get_usage_summary()
    print(f"  Total used: {summary['total_used']}/{summary['total_allocated']}")
    print(f"  Over budget: {summary['is_over_budget']}")
    print()
    
    for category, cat_summary in summary['categories'].items():
        status = "⚠️" if cat_summary['is_over_budget'] else "✅"
        print(f"  {status} {category}: {cat_summary['used']}/{cat_summary['allocated']} tokens ({cat_summary['item_count']} items)")
    
    # Handle overflow
    print("\n🔧 Handling overflow...")
    overflow_summaries = budget_manager.handle_overflow()
    
    if overflow_summaries:
        print("  Overflow summaries created:")
        for category, summary in overflow_summaries.items():
            print(f"    {category}: {len(summary)} characters")
    else:
        print("  No overflow detected")
    
    # Print final summary
    print("\n📈 Final Budget Usage:")
    final_summary = budget_manager.get_usage_summary()
    print(f"  Total used: {final_summary['total_used']}/{final_summary['total_allocated']}")
    print(f"  Over budget: {final_summary['is_over_budget']}")
    
    # Test budget allocations
    print("\n💰 Budget Allocations:")
    for category, allocation in budget_manager.allocations.items():
        print(f"  {category.value}: {allocation.allocated_tokens} tokens ({allocation.allocated_tokens/1000*100:.1f}%)")
    
    print("\n✅ Budget manager test completed!")

if __name__ == "__main__":
    test_budget_manager()
