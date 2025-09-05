# Code Builder Evaluation Protocol

## Overview
This document defines the evaluation protocol for Code Builder's ABC iteration system, providing objective metrics parsing and structured rubrics for artifact assessment.

## 1. Objective Metrics Parsing

### JSON Sources in builder/cache/
The evaluation system automatically parses JSON reports from the following locations:

- `builder/cache/vitest.json` - Test results and coverage data
- `builder/cache/eslint.json` - Code quality and linting metrics
- `builder/cache/markdownlint.json` - Documentation quality metrics
- `builder/cache/cspell.json` - Spelling and terminology consistency
- `builder/cache/coverage-final.json` - Detailed coverage analysis

### Metrics Extraction
```javascript
// Example metrics extraction
const metrics = {
  test_coverage: vitest.coverageMap?.total?.statements?.pct || 0,
  test_passed: vitest.numPassedTests || 0,
  test_failed: vitest.numFailedTests || 0,
  lint_errors: eslint.reduce((sum, file) => sum + file.errorCount, 0),
  lint_warnings: eslint.reduce((sum, file) => sum + file.warningCount, 0),
  spell_errors: cspell.issues?.length || 0,
  doc_errors: markdownlint.issues?.length || 0
};
```

## 2. Rubrics by Artifact Type

### Code Artifacts
**Weight Distribution:**
- Clarity (20%): Code readability, naming conventions, documentation
- Design (30%): Architecture, patterns, separation of concerns
- Maintainability (20%): Modularity, complexity, refactoring ease
- Tests (20%): Coverage, quality, test clarity
- Rule Compliance (10%): Adherence to project rules and standards

**Scoring Scale:** 0-100 points per dimension

**Clarity Metrics:**
- Variable/function naming quality (0-25)
- Code organization and structure (0-25)
- Inline documentation and comments (0-25)
- Type annotations and interfaces (0-25)

**Design Metrics:**
- Architectural patterns usage (0-30)
- Separation of concerns (0-30)
- Dependency management (0-20)
- Error handling patterns (0-20)

**Maintainability Metrics:**
- Cyclomatic complexity (0-25)
- Module coupling (0-25)
- Code duplication (0-25)
- Refactoring readiness (0-25)

**Test Metrics:**
- Test coverage percentage (0-40)
- Test quality and clarity (0-30)
- Edge case coverage (0-30)

**Rule Compliance Metrics:**
- Project rule adherence (0-50)
- Style guide compliance (0-50)

### PRD (Product Requirements Document)
**Weight Distribution:**
- Completeness (30%): All requirements captured, no gaps
- Clarity (25%): Clear, unambiguous language
- Feasibility (25%): Realistic scope and timeline
- Alignment (20%): Matches business objectives

**Completeness Metrics:**
- Functional requirements coverage (0-40)
- Non-functional requirements (0-30)
- User stories and acceptance criteria (0-30)

**Clarity Metrics:**
- Language precision (0-35)
- Requirement specificity (0-35)
- Stakeholder understanding (0-30)

**Feasibility Metrics:**
- Technical feasibility (0-40)
- Resource requirements (0-30)
- Timeline realism (0-30)

**Alignment Metrics:**
- Business objective alignment (0-50)
- Stakeholder needs (0-50)

### ADR (Architecture Decision Record)
**Weight Distribution:**
- Context (25%): Problem understanding and background
- Decision Rationale (35%): Clear reasoning and justification
- Consequences (20%): Impact analysis and trade-offs
- Alternatives (20%): Considered options and why rejected

**Context Metrics:**
- Problem statement clarity (0-40)
- Background information (0-30)
- Stakeholder impact (0-30)

**Decision Rationale Metrics:**
- Reasoning quality (0-50)
- Evidence and data (0-30)
- Decision criteria (0-20)

**Consequences Metrics:**
- Impact analysis depth (0-50)
- Risk assessment (0-30)
- Trade-off documentation (0-20)

**Alternatives Metrics:**
- Options considered (0-50)
- Rejection rationale (0-50)

### Task Artifacts
**Weight Distribution:**
- Clarity (30%): Clear, actionable task description
- Acceptance Criteria (40%): Measurable, testable requirements
- Testability (30%): How well the task can be validated

**Clarity Metrics:**
- Task description quality (0-40)
- Scope definition (0-30)
- Dependencies and prerequisites (0-30)

**Acceptance Criteria Metrics:**
- Measurability (0-50)
- Completeness (0-30)
- Specificity (0-20)

**Testability Metrics:**
- Validation methods (0-50)
- Success criteria (0-30)
- Failure conditions (0-20)

## 3. Output Schema

```json
{
  "variant_scores": {
    "A": {
      "overall_score": 85.2,
      "dimensions": {
        "clarity": 82,
        "design": 88,
        "maintainability": 79,
        "tests": 91,
        "rule_compliance": 87
      },
      "metrics": {
        "test_coverage": 94.5,
        "lint_errors": 0,
        "spell_errors": 2
      }
    },
    "B": {
      "overall_score": 91.7,
      "dimensions": {
        "clarity": 89,
        "design": 93,
        "maintainability": 88,
        "tests": 95,
        "rule_compliance": 92
      },
      "metrics": {
        "test_coverage": 97.2,
        "lint_errors": 0,
        "spell_errors": 0
      }
    },
    "C": {
      "overall_score": 78.4,
      "dimensions": {
        "clarity": 75,
        "design": 81,
        "maintainability": 72,
        "tests": 83,
        "rule_compliance": 79
      },
      "metrics": {
        "test_coverage": 89.1,
        "lint_errors": 3,
        "spell_errors": 5
      }
    }
  },
  "winner": "B",
  "confidence": 0.87,
  "reasoning": "Variant B demonstrates superior design patterns with 97.2% test coverage and zero linting errors. The code shows excellent maintainability with clear separation of concerns and comprehensive error handling. The 3.5 point lead over variant A is primarily due to better test quality and rule compliance."
}
```

## 4. Tiebreak Protocol

When variants have similar scores (within 2 points), use direct pairwise comparison:

1. **Head-to-Head Analysis**: Compare A vs B directly on each dimension
2. **Strengths/Weaknesses**: Identify key differentiators
3. **Contextual Factors**: Consider project priorities and constraints
4. **Decision Matrix**: Weight factors based on current project phase

**Tiebreak Decision Process:**
```javascript
if (Math.abs(scoreA - scoreB) < 2.0) {
  const comparison = {
    clarity: scoreA.clarity - scoreB.clarity,
    design: scoreA.design - scoreB.design,
    maintainability: scoreA.maintainability - scoreB.maintainability,
    tests: scoreA.tests - scoreB.tests,
    rule_compliance: scoreA.rule_compliance - scoreB.rule_compliance
  };
  
  // Weight by project phase priorities
  const weights = getPhaseWeights(currentPhase);
  const weightedScore = Object.keys(comparison)
    .reduce((sum, key) => sum + (comparison[key] * weights[key]), 0);
}
```

## 5. Bias Mitigation

### Independent Scoring
1. **Sequential Evaluation**: Score each variant completely before moving to the next
2. **Blind Assessment**: Evaluate without knowing which is A, B, or C
3. **Dimension Isolation**: Score each dimension independently
4. **Metric Validation**: Cross-check objective metrics with subjective scores

### Bias Prevention Checklist
- [ ] All variants scored independently
- [ ] No comparison during individual scoring
- [ ] Objective metrics parsed from builder/cache/ files
- [ ] Subjective scores justified with specific examples
- [ ] Confidence level reflects uncertainty in close calls
- [ ] Reasoning explains the decision process clearly

### Quality Assurance
- **Double-blind review** for high-stakes decisions
- **Consistency checks** across similar artifact types
- **Calibration sessions** to align scoring standards
- **Retrospective analysis** of evaluation accuracy

## Implementation Notes

### File Structure
```
builder/cache/
├── vitest.json          # Test results and coverage
├── eslint.json          # Linting results
├── markdownlint.json    # Documentation linting
├── cspell.json          # Spell checking results
└── coverage-final.json  # Detailed coverage analysis
```

### Integration Points
- **ABC Iteration**: Called after each variant generation
- **Rule Engine**: Uses project rules for compliance scoring
- **CI/CD**: Integrates with automated testing pipeline
- **Reporting**: Generates evaluation reports for stakeholders

### Error Handling
- Graceful degradation when JSON files are missing
- Default scores for incomplete data
- Clear error messages for parsing failures
- Fallback to manual evaluation when automation fails
