#!/usr/bin/env python3
"""
Objective evaluation module for Code Builder ABC iterations.
Parses JSON reports and calculates scores based on config.yaml weights.
"""

import os
import json
import yaml
from typing import Dict, Any

# Import overlay paths for dual-mode support
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
except ImportError:
    # Fallback for standalone mode
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFIG_PATH = os.path.join(ROOT, "docs", "eval", "config.yaml")

def load_config() -> Dict[str, Any]:
    """Load evaluation configuration from docs/eval/config.yaml"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def check_tool_availability() -> Dict[str, bool]:
    """Check which tools are available by looking for their output files"""
    config = load_config()
    reporter_paths = config.get('reporter_paths', {})
    
    availability = {}
    for tool, path in reporter_paths.items():
        full_path = os.path.join(ROOT, path)
        availability[tool] = os.path.exists(full_path)
    
    return availability

def safe_json_parse(path: str) -> Dict[str, Any]:
    """Safely parse JSON file, return empty dict on error"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def parse_vitest_report(path: str) -> Dict[str, float]:
    """Parse vitest.json and extract test metrics"""
    data = safe_json_parse(path)
    
    total_tests = data.get('numTotalTests', 0)
    passed_tests = data.get('numPassedTests', 0)
    
    if total_tests == 0:
        return {"tests": 50.0, "coverage": 50.0}
    
    # Test pass rate (0-100)
    test_score = (passed_tests / total_tests) * 100
    
    # Coverage from coverageMap if available
    coverage_map = data.get('coverageMap', {})
    if coverage_map:
        total_statements = 0
        covered_statements = 0
        
        for file_data in coverage_map.values():
            statements = file_data.get('s', {})
            if statements:
                total_statements += len(statements)
                covered_statements += sum(1 for v in statements.values() if v > 0)
        
        coverage_score = (covered_statements / total_statements * 100) if total_statements > 0 else 50.0
    else:
        coverage_score = 50.0
    
    return {
        "tests": test_score,
        "coverage": coverage_score
    }

def parse_coverage_report(path: str) -> Dict[str, float]:
    """Parse coverage-final.json for detailed coverage metrics"""
    data = safe_json_parse(path)
    
    # Extract line coverage percentage
    total = data.get('total', {})
    lines = total.get('lines', {})
    coverage_pct = lines.get('pct', 50.0)
    
    return {"coverage": coverage_pct}

def parse_eslint_report(path: str) -> Dict[str, float]:
    """Parse eslint.json and calculate inverse error score"""
    data = safe_json_parse(path)
    
    if not isinstance(data, list):
        return {"lint": 50.0}
    
    total_errors = sum(file_data.get('errorCount', 0) for file_data in data)
    total_warnings = sum(file_data.get('warningCount', 0) for file_data in data)
    
    # Convert to score: fewer errors = higher score
    lint_score = max(0, 100 - (total_errors * 2) - (total_warnings * 1))
    
    return {"lint": lint_score}

def parse_markdownlint_report(path: str) -> Dict[str, float]:
    """Parse markdownlint.json and calculate inverse violation score"""
    data = safe_json_parse(path)
    
    if not isinstance(data, list):
        return {"markdown": 50.0}
    
    total_violations = sum(len(file_data.get('violations', [])) for file_data in data)
    
    # Convert to score: fewer violations = higher score
    markdown_score = max(0, 100 - (total_violations * 5))
    
    return {"markdown": markdown_score}

def parse_cspell_report(path: str) -> Dict[str, float]:
    """Parse cspell.json and calculate inverse misspelling score"""
    data = safe_json_parse(path)
    
    # Handle different cspell output formats
    if isinstance(data, dict):
        issues = data.get('issues', [])
        misspellings = len(issues) if issues else 0
    elif isinstance(data, list):
        misspellings = len(data)
    else:
        misspellings = 0
    
    # Convert to score: fewer misspellings = higher score
    spell_score = max(0, 100 - (misspellings * 10))
    
    return {"spell": spell_score}

def check_guardrails() -> Dict[str, float]:
    """Check guardrails compliance - simplified version"""
    try:
        # Simple guardrails check to avoid hanging
        guardrails_path = os.path.join(ROOT, "docs", "rules", "guardrails.json")
        if os.path.exists(guardrails_path):
            data = safe_json_parse(guardrails_path)
            forbidden_patterns = data.get('forbiddenPatterns', [])
            # Simple check - return neutral score for now
            return {"guardrails": 50.0}
        else:
            return {"guardrails": 50.0}
    except Exception:
        return {"guardrails": 50.0}

def evaluate_code(path: str) -> Dict[str, float]:
    """
    Evaluate code artifacts using objective metrics.
    Returns scores for tests, coverage, lint, spell, guardrails, and overall.
    """
    config = load_config()
    objective_weights = config.get('objective_weights', {})
    reporter_paths = config.get('reporter_paths', {})
    
    # Initialize scores with neutral values
    scores = {
        "tests": 50.0,
        "coverage": 50.0,
        "lint": 50.0,
        "spell": 50.0,
        "guardrails": 50.0
    }
    
    # Parse vitest report (contains both tests and coverage)
    vitest_path = os.path.join(ROOT, reporter_paths.get('vitest', ''))
    if os.path.exists(vitest_path):
        vitest_scores = parse_vitest_report(vitest_path)
        scores.update(vitest_scores)
    
    # Parse separate coverage report if available
    coverage_path = os.path.join(ROOT, reporter_paths.get('coverage', ''))
    if os.path.exists(coverage_path):
        coverage_scores = parse_coverage_report(coverage_path)
        scores["coverage"] = coverage_scores["coverage"]
    
    # Parse eslint report
    eslint_path = os.path.join(ROOT, reporter_paths.get('eslint', ''))
    if os.path.exists(eslint_path):
        eslint_scores = parse_eslint_report(eslint_path)
        scores.update(eslint_scores)
    
    # Parse cspell report
    cspell_path = os.path.join(ROOT, reporter_paths.get('cspell', ''))
    if os.path.exists(cspell_path):
        cspell_scores = parse_cspell_report(cspell_path)
        scores.update(cspell_scores)
    
    # Check guardrails
    guardrails_scores = check_guardrails()
    scores.update(guardrails_scores)
    
    # Calculate weighted overall score
    overall = sum(scores[key] * objective_weights.get(key, 0) for key in scores.keys())
    scores["overall"] = overall
    
    return scores

def evaluate_doc(path: str, doc_type: str) -> Dict[str, float]:
    """
    Evaluate documentation artifacts using objective metrics.
    Returns scores for spell, markdown, and overall.
    """
    config = load_config()
    objective_weights = config.get('objective_weights', {})
    reporter_paths = config.get('reporter_paths', {})
    
    # Initialize scores with neutral values
    scores = {
        "spell": 50.0,
        "markdown": 50.0
    }
    
    # Parse cspell report
    cspell_path = os.path.join(ROOT, reporter_paths.get('cspell', ''))
    if os.path.exists(cspell_path):
        cspell_scores = parse_cspell_report(cspell_path)
        scores.update(cspell_scores)
    
    # Parse markdownlint report
    markdownlint_path = os.path.join(ROOT, reporter_paths.get('markdownlint', ''))
    if os.path.exists(markdownlint_path):
        markdown_scores = parse_markdownlint_report(markdownlint_path)
        scores.update(markdown_scores)
    
    # Calculate weighted overall score for documentation
    # Use only relevant weights for docs
    doc_weights = {
        "spell": objective_weights.get('spell', 0.5),
        "markdown": objective_weights.get('markdown', 0.5)
    }
    
    # Normalize weights to sum to 1.0
    total_weight = sum(doc_weights.values())
    if total_weight > 0:
        doc_weights = {k: v/total_weight for k, v in doc_weights.items()}
    
    overall = sum(scores[key] * doc_weights.get(key, 0) for key in scores.keys())
    scores["overall"] = overall
    
    return scores

def main():
    """Test the evaluator with current repo files"""
    print("=== Objective Evaluator Test ===")
    
    # Check tool availability
    availability = check_tool_availability()
    print(f"Tool availability: {availability}")
    
    # Test code evaluation
    print("\n--- Code Evaluation ---")
    code_scores = evaluate_code("src/")
    print(f"Code scores: {code_scores}")
    
    # Test doc evaluation
    print("\n--- Documentation Evaluation ---")
    doc_scores = evaluate_doc("docs/", "prd")
    print(f"Doc scores: {doc_scores}")

if __name__ == "__main__":
    main()