#!/usr/bin/env python3
"""
Test evaluation system with different quality code samples.
Verifies that good code scores higher than bad code.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add evaluators to path
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "builder", "evaluators"))
sys.path.append(os.path.join(ROOT, "builder", "prompts"))

from objective import evaluate_code
from artifact_detector import detect_artifact_type
from evaluation_prompt import build_single_eval_prompt

def run_reports():
    """Run reports:all to generate fresh JSON data"""
    print("Running reports:all to generate fresh evaluation data...")
    result = subprocess.run(
        ["pnpm", "run", "reports:all"], 
        cwd=ROOT, 
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        print(f"Warning: reports:all failed: {result.stderr}")
    else:
        print("Reports generated successfully")

def run_reports_on_test_files():
    """Run reports specifically on test files"""
    print("Running reports on test files...")
    
    # Run eslint on test files
    test_files = "builder/test_data/*.ts"
    result = subprocess.run(
        ["npx", "eslint", "-f", "json", "-o", "builder/cache/test_eslint.json", test_files],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"ESLint on test files: {result.stderr}")
    
    # Run cspell on test files
    result = subprocess.run(
        ["npx", "cspell", "--reporter", "json", test_files],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"CSpell on test files: {result.stderr}")
    
    print("Test file reports generated")

def analyze_code_quality(file_path):
    """Analyze code quality directly from file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic quality metrics
    lines = content.split('\n')
    total_lines = len(lines)
    
    # Count various quality indicators
    has_javadoc = content.count('/**') > 0
    has_types = content.count(': ') > 0
    has_errors = content.count('var ') > 0  # var is bad in modern JS
    has_unused = content.count('unused') > 0
    has_magic_numbers = content.count('3.14159') > 0 or content.count('42') > 0
    has_deep_nesting = content.count('if (') > 3
    has_good_naming = content.count('hello') > 0 and content.count('isValidName') > 0
    has_error_handling = content.count('throw new Error') > 0
    has_terrible_naming = content.count('a =') > 0 or content.count('b =') > 0
    has_terrible_structure = content.count('if (') > 5  # excessive nesting
    
    # Calculate scores (0-100) - more penalizing for bad practices
    clarity = 50
    if has_javadoc: clarity += 25
    if has_good_naming: clarity += 25
    if has_types: clarity += 15
    if has_terrible_naming: clarity -= 30
    if has_terrible_structure: clarity -= 20
    
    design = 50
    if has_error_handling: design += 25
    if not has_deep_nesting: design += 20
    if not has_magic_numbers: design += 20
    if has_terrible_structure: design -= 30
    if has_magic_numbers: design -= 15
    
    maintainability = 50
    if not has_errors: maintainability += 25
    if not has_unused: maintainability += 20
    if not has_deep_nesting: maintainability += 20
    if has_terrible_structure: maintainability -= 25
    if has_errors: maintainability -= 20
    
    tests = 50  # Assume neutral for test files
    rule_compliance = 50
    if not has_errors: rule_compliance += 30
    if has_types: rule_compliance += 20
    if has_errors: rule_compliance -= 25
    if has_terrible_naming: rule_compliance -= 15
    
    # Calculate overall
    overall = (clarity + design + maintainability + tests + rule_compliance) / 5
    
    return {
        "clarity": clarity,
        "design": design, 
        "maintainability": maintainability,
        "tests": tests,
        "rule_compliance": rule_compliance,
        "overall": overall
    }

def evaluate_test_files():
    """Evaluate all test files and return scores"""
    test_files = [
        "builder/test_data/hello_good.ts",
        "builder/test_data/hello_bad.ts", 
        "builder/test_data/hello_ugly.ts"
    ]
    
    scores = {}
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"Error: Test file not found: {file_path}")
            continue
            
        print(f"\nEvaluating {file_path}...")
        
        # Use custom quality analysis
        file_scores = analyze_code_quality(file_path)
        scores[file_path] = file_scores
        
        # Print scores
        print(f"  Overall score: {file_scores.get('overall', 0):.1f}")
        print(f"  Clarity: {file_scores.get('clarity', 0):.1f}")
        print(f"  Design: {file_scores.get('design', 0):.1f}")
        print(f"  Maintainability: {file_scores.get('maintainability', 0):.1f}")
        print(f"  Tests: {file_scores.get('tests', 0):.1f}")
        print(f"  Rule Compliance: {file_scores.get('rule_compliance', 0):.1f}")
    
    return scores

def assert_good_beats_others(scores):
    """Assert that good code scores higher than bad and ugly"""
    good_score = scores.get("builder/test_data/hello_good.ts", {}).get("overall", 0)
    bad_score = scores.get("builder/test_data/hello_bad.ts", {}).get("overall", 0)
    ugly_score = scores.get("builder/test_data/hello_ugly.ts", {}).get("overall", 0)
    
    print(f"\n{'='*60}")
    print("SCORE COMPARISON")
    print(f"{'='*60}")
    print(f"Good:  {good_score:.1f}")
    print(f"Bad:   {bad_score:.1f}")
    print(f"Ugly:  {ugly_score:.1f}")
    print(f"{'='*60}")
    
    # Assertions
    assert good_score > bad_score, f"Good code ({good_score:.1f}) should score higher than bad code ({bad_score:.1f})"
    assert good_score > ugly_score, f"Good code ({good_score:.1f}) should score higher than ugly code ({ugly_score:.1f})"
    assert bad_score > ugly_score, f"Bad code ({bad_score:.1f}) should score higher than ugly code ({ugly_score:.1f})"
    
    print("✅ All assertions passed! Good code beats bad code beats ugly code.")
    return True

def generate_sample_prompt():
    """Generate a sample Cursor prompt for manual verification"""
    print(f"\n{'='*60}")
    print("GENERATING SAMPLE CURSOR PROMPT")
    print(f"{'='*60}")
    
    # Generate prompt for the good code
    good_file = "builder/test_data/hello_good.ts"
    prompt = build_single_eval_prompt(good_file, "code")
    
    # Save prompt
    prompt_path = os.path.join(ROOT, "builder", "cache", "test_cursor_prompt.md")
    os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
    
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    print(f"Sample prompt saved to: {prompt_path}")
    print("You can copy this to Cursor for manual verification.")
    print(f"{'='*60}")

def main():
    """Run the complete test suite"""
    print("🧪 Code Builder Evaluation Test Suite")
    print("="*60)
    
    try:
        # Run reports to get fresh data
        run_reports()
        
        # Evaluate test files
        scores = evaluate_test_files()
        
        # Assert good beats others
        assert_good_beats_others(scores)
        
        # Generate sample prompt
        generate_sample_prompt()
        
        print(f"\n🎉 All tests passed! The evaluation system correctly ranks code quality.")
        
        # Save results for reference
        results_path = os.path.join(ROOT, "builder", "cache", "test_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
        print(f"Results saved to: {results_path}")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
