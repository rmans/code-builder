#!/usr/bin/env python3
"""
Evaluation prompt builder for Code Builder ABC iterations.
Generates structured prompts for different evaluation scenarios.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
EVALUATION_RULES_PATH = os.path.join(ROOT, ".cursor", "rules", "evaluation.md")

def load_evaluation_rules() -> str:
    """Load evaluation rules from .cursor/rules/evaluation.md"""
    try:
        with open(EVALUATION_RULES_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Evaluation rules not found."

def load_project_rules(feature: Optional[str] = None, stacks: list = None) -> str:
    """Load project rules using rules_loader"""
    try:
        import sys
        # Add the builder directory to the path
        builder_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sys.path.append(builder_dir)
        from builder.core.rules_loader import load_rules
        
        rules = load_rules(feature, stacks or [])
        return rules.get('rules_markdown', 'No project rules found.')
    except Exception:
        return "Project rules not available."

def read_artifact_content(path: str) -> str:
    """Read artifact content, truncate if too long"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Truncate if too long (keep under 4000 chars for prompt)
        if len(content) > 4000:
            content = content[:4000] + "\n\n... [truncated]"
        
        return content
    except Exception:
        return f"Could not read file: {path}"

def get_rubric_for_type(artifact_type: str) -> str:
    """Get the specific rubric section for artifact type"""
    rubrics = {
        'code': """
### Code Artifacts Rubric
**Weight Distribution:**
- Clarity (20%): Code readability, naming conventions, documentation
- Design (30%): Architecture, patterns, separation of concerns  
- Maintainability (20%): Modularity, complexity, refactoring ease
- Tests (20%): Coverage, quality, test clarity
- Rule Compliance (10%): Adherence to project rules and standards

**Scoring Scale:** 0-100 points per dimension
""",
        'prd': """
### PRD (Product Requirements Document) Rubric
**Weight Distribution:**
- Completeness (30%): All requirements captured, no gaps
- Clarity (25%): Clear, unambiguous language
- Feasibility (25%): Realistic scope and timeline
- Alignment (20%): Matches business objectives
""",
        'adr': """
### ADR (Architecture Decision Record) Rubric
**Weight Distribution:**
- Context (25%): Problem understanding and background
- Decision Rationale (35%): Clear reasoning and justification
- Consequences (20%): Impact analysis and trade-offs
- Alternatives (20%): Considered options and why rejected
""",
        'task': """
### Task Artifacts Rubric
**Weight Distribution:**
- Clarity (30%): Clear, actionable task description
- Acceptance Criteria (40%): Measurable, testable requirements
- Testability (30%): How well the task can be validated
"""
    }
    return rubrics.get(artifact_type, rubrics['task'])

def build_single_eval_prompt(artifact_path: str, artifact_type: Optional[str] = None) -> str:
    """
    Build evaluation prompt for a single artifact.
    
    Args:
        artifact_path: Path to the artifact file
        artifact_type: Type of artifact ('code', 'prd', 'adr', 'task')
    
    Returns:
        Formatted markdown prompt
    """
    # Auto-detect artifact type if not provided
    if not artifact_type:
        try:
            import sys
            builder_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.append(builder_dir)
            from builder.evaluators.artifact_detector import detect_artifact_type
            artifact_type = detect_artifact_type(artifact_path)
        except Exception:
            artifact_type = 'task'
    
    # Load content
    evaluation_rules = load_evaluation_rules()
    project_rules = load_project_rules()
    artifact_content = read_artifact_content(artifact_path)
    
    # Get specific rubric
    rubric = get_rubric_for_type(artifact_type)
    
    prompt = f"""# Artifact Evaluation

## Artifact Details
- **Path:** `{artifact_path}`
- **Type:** `{artifact_type}`
- **Content:**
```
{artifact_content}
```

## Evaluation Rubric
{rubric}

## Project Rules Context
{project_rules[:1000]}{'...' if len(project_rules) > 1000 else ''}

## Evaluation Instructions

1. **Score each dimension** (0-100 points) based on the rubric
2. **Provide specific examples** from the artifact to justify scores
3. **Calculate weighted overall score** using the weight distribution
4. **Return JSON format** as specified below

## Expected Output Format

```json
{{
  "overall_score": 85.2,
  "dimensions": {{
    "clarity": 82,
    "design": 88,
    "maintainability": 79,
    "tests": 91,
    "rule_compliance": 87
  }},
  "reasoning": "Detailed explanation of scoring decisions with specific examples from the artifact.",
  "strengths": ["List of key strengths"],
  "weaknesses": ["List of areas for improvement"]
}}
```

## Evaluation Protocol
{evaluation_rules[:2000]}{'...' if len(evaluation_rules) > 2000 else ''}
"""
    
    return prompt

def build_abc_eval_prompt(variants: Dict[str, str], objective_scores: Dict[str, Dict[str, float]]) -> str:
    """
    Build evaluation prompt for ABC iteration comparison.
    
    Args:
        variants: Dict mapping variant names to file paths
        objective_scores: Dict mapping variant names to objective scores
    
    Returns:
        Formatted markdown prompt
    """
    evaluation_rules = load_evaluation_rules()
    project_rules = load_project_rules()
    
    # Build variants section
    variants_section = ""
    for variant_name, path in variants.items():
        content = read_artifact_content(path)
        obj_scores = objective_scores.get(variant_name, {})
        
        variants_section += f"""
### Variant {variant_name}
**Path:** `{path}`
**Objective Scores:** {obj_scores}
**Content:**
```
{content}
```

---
"""
    
    prompt = f"""# ABC Iteration Evaluation

## Variants to Compare
{variants_section}

## Evaluation Rubric
{get_rubric_for_type('code')}

## Project Rules Context
{project_rules[:1000]}{'...' if len(project_rules) > 1000 else ''}

## Evaluation Instructions

1. **Score each variant independently** (0-100 points per dimension)
2. **Consider objective scores** as additional context
3. **Compare variants directly** and identify the winner
4. **Provide detailed reasoning** for the decision
5. **Return JSON format** as specified below

## Expected Output Format

```json
{{
  "variant_scores": {{
    "A": {{
      "overall_score": 85.2,
      "dimensions": {{
        "clarity": 82,
        "design": 88,
        "maintainability": 79,
        "tests": 91,
        "rule_compliance": 87
      }}
    }},
    "B": {{
      "overall_score": 91.7,
      "dimensions": {{
        "clarity": 89,
        "design": 93,
        "maintainability": 88,
        "tests": 95,
        "rule_compliance": 92
      }}
    }},
    "C": {{
      "overall_score": 78.4,
      "dimensions": {{
        "clarity": 75,
        "design": 81,
        "maintainability": 72,
        "tests": 83,
        "rule_compliance": 79
      }}
    }}
  }},
  "winner": "B",
  "confidence": 0.87,
  "reasoning": "Variant B demonstrates superior design patterns with 97.2% test coverage and zero linting errors. The code shows excellent maintainability with clear separation of concerns and comprehensive error handling. The 3.5 point lead over variant A is primarily due to better test quality and rule compliance."
}}
```

## Evaluation Protocol
{evaluation_rules[:2000]}{'...' if len(evaluation_rules) > 2000 else ''}
"""
    
    return prompt

def build_pairwise_prompt(path_a: str, path_b: str, artifact_type: Optional[str] = None) -> str:
    """
    Build evaluation prompt for pairwise comparison.
    
    Args:
        path_a: Path to first artifact
        path_b: Path to second artifact  
        artifact_type: Type of artifacts ('code', 'prd', 'adr', 'task')
    
    Returns:
        Formatted markdown prompt
    """
    # Auto-detect artifact type if not provided
    if not artifact_type:
        try:
            import sys
            builder_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.append(builder_dir)
            from builder.evaluators.artifact_detector import detect_artifact_type
            artifact_type = detect_artifact_type(path_a)
        except Exception:
            artifact_type = 'task'
    
    evaluation_rules = load_evaluation_rules()
    project_rules = load_project_rules()
    
    content_a = read_artifact_content(path_a)
    content_b = read_artifact_content(path_b)
    
    rubric = get_rubric_for_type(artifact_type)
    
    prompt = f"""# Pairwise Artifact Comparison

## Artifact A
**Path:** `{path_a}`
**Content:**
```
{content_a}
```

## Artifact B  
**Path:** `{path_b}`
**Content:**
```
{content_b}
```

## Evaluation Rubric
{rubric}

## Project Rules Context
{project_rules[:1000]}{'...' if len(project_rules) > 1000 else ''}

## Evaluation Instructions

1. **Compare artifacts directly** on each dimension
2. **Identify key differences** and trade-offs
3. **Determine the winner** with clear justification
4. **Provide specific examples** from both artifacts
5. **Return JSON format** as specified below

## Expected Output Format

```json
{{
  "artifact_a": {{
    "overall_score": 85.2,
    "dimensions": {{
      "clarity": 82,
      "design": 88,
      "maintainability": 79,
      "tests": 91,
      "rule_compliance": 87
    }}
  }},
  "artifact_b": {{
    "overall_score": 91.7,
    "dimensions": {{
      "clarity": 89,
      "design": 93,
      "maintainability": 88,
      "tests": 95,
      "rule_compliance": 92
    }}
  }},
  "winner": "artifact_b",
  "confidence": 0.87,
  "reasoning": "Artifact B demonstrates superior design patterns with better test coverage and cleaner code organization. The key differentiator is the comprehensive error handling and more modular architecture.",
  "key_differences": [
    "Artifact B has 95% test coverage vs 91% in A",
    "Artifact B uses dependency injection pattern",
    "Artifact A has more complex conditional logic"
  ]
}}
```

## Evaluation Protocol
{evaluation_rules[:2000]}{'...' if len(evaluation_rules) > 2000 else ''}
"""
    
    return prompt

def test_prompts():
    """Test the prompt builder with sample data"""
    print("=== Evaluation Prompt Builder Test ===")
    
    # Test single evaluation
    print("\n--- Single Evaluation Prompt ---")
    single_prompt = build_single_eval_prompt("src/hello.ts", "code")
    print(f"Single prompt length: {len(single_prompt)} characters")
    print("First 500 chars:")
    print(single_prompt[:500] + "...")
    
    # Test ABC evaluation
    print("\n--- ABC Evaluation Prompt ---")
    variants = {
        "A": "src/hello.ts",
        "B": "src/index.ts", 
        "C": "test/hello.test.ts"
    }
    objective_scores = {
        "A": {"tests": 100, "coverage": 85, "lint": 95},
        "B": {"tests": 100, "coverage": 90, "lint": 98},
        "C": {"tests": 100, "coverage": 95, "lint": 100}
    }
    abc_prompt = build_abc_eval_prompt(variants, objective_scores)
    print(f"ABC prompt length: {len(abc_prompt)} characters")
    print("First 500 chars:")
    print(abc_prompt[:500] + "...")
    
    # Test pairwise evaluation
    print("\n--- Pairwise Evaluation Prompt ---")
    pairwise_prompt = build_pairwise_prompt("src/hello.ts", "src/index.ts", "code")
    print(f"Pairwise prompt length: {len(pairwise_prompt)} characters")
    print("First 500 chars:")
    print(pairwise_prompt[:500] + "...")

if __name__ == "__main__":
    test_prompts()
