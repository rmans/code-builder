#!/usr/bin/env python3
"""
Simple test for the context budget manager.
"""

from builder.context_budget import ContextBudgetManager, BudgetCategory, BudgetItem

def test_overflow_scenario():
    """Test overflow scenario with summaries."""
    print("🧪 Testing Overflow Scenario")
    print("=" * 40)
    
    # Create budget manager with very small limit
    budget_manager = ContextBudgetManager(200)  # 200 tokens total
    
    print("📝 Adding items to cause overflow...")
    
    # Add must-include items (these should never be dropped)
    budget_manager.add_item(
        content="Rules: Keep files under 300 LOC. Tests mirror acceptance criteria 1:1.",
        source="docs/rules/00-global.md",
        category=BudgetCategory.RULES,
        weight=10.0
    )
    
    budget_manager.add_item(
        content="Acceptance Criteria: User can authenticate. System validates tokens.",
        source="docs/prd/PRD-test-prd.md",
        category=BudgetCategory.ACCEPTANCE,
        weight=8.0
    )
    
    # Add multiple code items that will cause overflow
    for i in range(5):
        large_content = f"export class Service{i} {{\n  async method{i}() {{\n    // Large implementation with lots of content\n    const data = '{'x' * 100}';\n    return data;\n  }}\n}}"
        budget_manager.add_item(
            content=large_content,
            source=f"src/service{i}.ts",
            category=BudgetCategory.CODE_TEST,
            weight=float(5 - i)  # Decreasing weights
        )
    
    # Print initial state
    print("\n📊 Initial Budget Usage:")
    summary = budget_manager.get_usage_summary()
    print(f"  Total used: {summary['total_used']}/{summary['total_allocated']}")
    print(f"  Over budget: {summary['is_over_budget']}")
    
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
            print(f"    Preview: {summary[:100]}...")
    else:
        print("  No overflow detected")
    
    # Print final state
    print("\n📈 Final Budget Usage:")
    final_summary = budget_manager.get_usage_summary()
    print(f"  Total used: {final_summary['total_used']}/{final_summary['total_allocated']}")
    print(f"  Over budget: {final_summary['is_over_budget']}")
    
    for category, cat_summary in final_summary['categories'].items():
        status = "⚠️" if cat_summary['is_over_budget'] else "✅"
        print(f"  {status} {category}: {cat_summary['used']}/{cat_summary['allocated']} tokens ({cat_summary['item_count']} items)")
    
    # Verify must-include categories are preserved
    print("\n🔒 Must-include categories preserved:")
    rules_items = len(budget_manager.allocations[BudgetCategory.RULES].items)
    acceptance_items = len(budget_manager.allocations[BudgetCategory.ACCEPTANCE].items)
    print(f"  Rules: {rules_items} items (should be > 0)")
    print(f"  Acceptance: {acceptance_items} items (should be > 0)")
    
    assert rules_items > 0, "Rules should not be dropped"
    assert acceptance_items > 0, "Acceptance should not be dropped"
    
    print("\n✅ Overflow test completed successfully!")

def test_budget_allocations():
    """Test that budget allocations are correct."""
    print("\n🧪 Testing Budget Allocations")
    print("=" * 40)
    
    budget_manager = ContextBudgetManager(1000)
    
    print("💰 Budget Allocations:")
    for category, allocation in budget_manager.allocations.items():
        percentage = (allocation.allocated_tokens / 1000) * 100
        print(f"  {category.value}: {allocation.allocated_tokens} tokens ({percentage:.1f}%)")
    
    # Verify percentages match requirements
    expected_percentages = {
        BudgetCategory.RULES: 15.0,
        BudgetCategory.ACCEPTANCE: 25.0,
        BudgetCategory.ADRS: 15.0,
        BudgetCategory.INTEGRATIONS: 15.0,
        BudgetCategory.ARCH: 10.0,
        BudgetCategory.CODE_TEST: 20.0,
    }
    
    for category, expected_pct in expected_percentages.items():
        actual_pct = (budget_manager.allocations[category].allocated_tokens / 1000) * 100
        assert abs(actual_pct - expected_pct) < 0.1, f"{category.value} should be {expected_pct}%, got {actual_pct}%"
    
    print("✅ Budget allocations are correct!")

if __name__ == "__main__":
    test_budget_allocations()
    test_overflow_scenario()
    print("\n🎉 All tests passed!")
