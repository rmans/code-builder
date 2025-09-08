# Cursor Evaluation Usage Guide

This guide explains how to use the Code Builder evaluation system with Cursor for automated code quality assessment and ABC iteration workflows.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Full ABC Workflow](#full-abc-workflow)
3. [Objective Metrics Guide](#objective-metrics-guide)
4. [Cursor Integration Tips](#cursor-integration-tips)
5. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Setup

First, run the evaluation setup script:

```bash
# Make sure you're in the project root
cd /path/to/code-builder

# Run setup (installs dependencies, creates cache directory)
./builder/setup_evaluation.sh
```

### 2. Try Objective Evaluation

Test the objective evaluation on any TypeScript file:

```bash
# Evaluate a single file
python builder/cli.py eval:objective src/hello.ts

# This will:
# - Detect the artifact type (code/documentation)
# - Run all reports (tests, linting, spelling, etc.)
# - Calculate objective scores
# - Save results to builder/cache/last_objective.json
```

**Example Output:**
```
Detected artifact type: code
Running reports:all...
Objective Scores:
{
  "tests": 100.0,
  "coverage": 85.2,
  "lint": 98.0,
  "spell": 100.0,
  "guardrails": 50.0,
  "overall": 71.7
}
Saved to /path/to/builder/cache/last_objective.json
```

### 3. Try Cursor Integration

Generate a prompt for Cursor evaluation:

```bash
# Prepare evaluation prompt
python builder/cli.py eval:prepare src/hello.ts

# This will:
# - Run objective evaluation
# - Generate a structured prompt
# - Save to builder/cache/cursor_prompt.md
# - Print instructions
```

**Next Steps:**
1. Copy the contents of `builder/cache/cursor_prompt.md`
2. Paste into Cursor Chat or Composer
3. Get Cursor's evaluation response
4. Save the response to a JSON file
5. Complete the evaluation:

```bash
python builder/cli.py eval:complete src/hello.ts --cursor-response cursor_response.json
```

## Full ABC Workflow

The ABC iteration system generates multiple variants of your code and uses Cursor to select the best one.

### Step 1: Generate Variants

```bash
# Start ABC iteration
python builder/cli.py iter:cursor src/hello.ts

# This will:
# - Generate 3 variants (A, B, C) with different approaches
# - Run objective evaluation on each
# - Create comparison prompt
# - Save to builder/cache/abc_prompt.md
```

**Example Output:**
```
Generating A/B/C variants...
Running objective evaluation on variants...
Evaluating variant A...
Evaluating variant B...
Evaluating variant C...
Building ABC comparison prompt...

============================================================
ABC ITERATION READY
============================================================
1. Copy /path/to/builder/cache/abc_prompt.md to Cursor
2. Get Cursor's evaluation (JSON format)
3. Run: python builder/cli.py iter:finish src/hello.ts --winner A|B|C --scores-file <cursor_response.json>

Objective Scores:
  A: 71.7
  B: 71.7
  C: 71.7
============================================================
```

### Step 2: Cursor Evaluation

1. **Copy the prompt** from `builder/cache/abc_prompt.md`
2. **Paste into Cursor** (Chat or Composer)
3. **Use this prompt** in Cursor:

```
Please evaluate these three code variants and select the best one. 
Follow the evaluation rubric provided and return your response in the exact JSON format specified.
```

4. **Get Cursor's response** - it should look like:

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
      }
    }
  },
  "winner": "B",
  "confidence": 0.87,
  "reasoning": "Variant B demonstrates superior design patterns with better test coverage and cleaner code organization."
}
```

5. **Save the response** to a file (e.g., `cursor_response.json`)

### Step 3: Complete the Iteration

```bash
# Finish the ABC iteration
python builder/cli.py iter:finish src/hello.ts --winner B --scores-file cursor_response.json

# This will:
# - Load the winner variant
# - Write it to the target file
# - Save iteration history
# - Print summary
```

**Example Output:**
```
Winner variant B written to src/hello.ts

============================================================
ABC ITERATION COMPLETE
============================================================
Winner: B
Target: src/hello.ts
History: /path/to/builder/cache/iter_history.json

Objective Scores Summary:
  A: 71.7
  B: 71.7 ← WINNER
  C: 71.7

Cursor Evaluation: B
Confidence: 0.87
============================================================
```

## Objective Metrics Guide

### Understanding the Scores

The objective evaluation measures code quality across several dimensions:

#### **Tests (0-100)**
- **What it measures**: Test pass rate and coverage
- **Source**: `builder/cache/vitest.json`
- **Calculation**: `(passed_tests / total_tests) * 100`
- **Good score**: 90+ (all tests passing)

#### **Coverage (0-100)**
- **What it measures**: Code coverage percentage
- **Source**: `builder/cache/coverage-final.json`
- **Calculation**: Line coverage from coverage reports
- **Good score**: 80+ (high coverage)

#### **Lint (0-100)**
- **What it measures**: Code quality and style violations
- **Source**: `builder/cache/eslint.json`
- **Calculation**: `100 - (errors * 2) - (warnings * 1)`
- **Good score**: 95+ (few violations)

#### **Spell (0-100)**
- **What it measures**: Spelling and terminology consistency
- **Source**: `builder/cache/cspell.json`
- **Calculation**: `100 - (misspellings * 10)`
- **Good score**: 95+ (no spelling errors)

#### **Guardrails (0-100)**
- **What it measures**: Adherence to project rules
- **Source**: `builder/cache/guardrails.json`
- **Calculation**: Based on forbidden pattern violations
- **Good score**: 80+ (follows project rules)

### Running Individual Reports

You can run specific reports to understand what's being measured:

```bash
# Run all reports
pnpm run reports:all

# Run individual reports
pnpm run reports:tests    # Test results
pnpm run reports:lint     # Linting results  
pnpm run reports:docs     # Documentation linting
pnpm run reports:spell    # Spell checking
```

### Interpreting Scores

- **90-100**: Excellent - Production ready
- **80-89**: Good - Minor improvements needed
- **70-79**: Fair - Several issues to address
- **60-69**: Poor - Significant refactoring needed
- **Below 60**: Critical - Major quality issues

## Cursor Integration Tips

### Best Models to Use

**Recommended Models:**
- **Claude 3.5 Sonnet** - Best for code evaluation and reasoning
- **GPT-4** - Good alternative with strong analysis capabilities
- **Claude 3 Opus** - Excellent for complex architectural decisions

**Avoid:**
- GPT-3.5 - May not follow JSON format consistently
- Older models - Less reliable for structured output

### Getting Consistent JSON Output

**1. Use the exact prompt format** provided in the generated files
**2. Include this instruction** in your Cursor prompt:

```
IMPORTANT: Return your response in the exact JSON format specified. 
Do not include any markdown formatting or additional text outside the JSON.
```

**3. If Cursor adds markdown**, use the bridge utility to extract JSON:

```python
from builder.cursor_bridge import parse_cursor_response

# This handles both raw JSON and JSON in markdown
response = parse_cursor_response("cursor_response.md")
```

### Referencing Evaluation Rules

**1. The prompts automatically include** relevant evaluation rules
**2. For manual reference**, check these files:
   - `.cursor/rules/evaluation.md` - Complete evaluation protocol
   - `docs/eval/config.yaml` - Scoring weights and configuration
   - `docs/rules/` - Project-specific rules

**3. When asking Cursor**, mention specific criteria:

```
Please evaluate based on:
- Clarity: Code readability and documentation
- Design: Architecture and patterns
- Maintainability: Complexity and modularity
- Tests: Coverage and quality
- Rule Compliance: Adherence to project standards
```

### Advanced Integration

**Using the Cursor Bridge:**

```python
from builder.cursor_bridge import watch_for_cursor, merge_evaluations

# Monitor clipboard for Cursor responses
response = watch_for_cursor(timeout=60)

# Merge objective and subjective scores
merged = merge_evaluations(objective_scores, cursor_response)
```

**Batch Processing:**

```bash
# Evaluate multiple files
for file in src/*.ts; do
  python builder/cli.py eval:prepare "$file"
  echo "Evaluate $file in Cursor, then:"
  echo "python builder/cli.py eval:complete '$file' --cursor-response response.json"
done
```

## Troubleshooting

### Common Issues

**1. "No valid JSON found"**
- **Cause**: Cursor response not in expected format
- **Solution**: Use `parse_cursor_response()` from cursor_bridge.py
- **Prevention**: Include JSON format instructions in prompt

**2. "Reports failed"**
- **Cause**: Missing dependencies or configuration
- **Solution**: Run `./builder/setup_evaluation.sh`
- **Check**: Ensure all tools are installed (`pnpm install`)

**3. "Artifact type not detected"**
- **Cause**: File extension not recognized
- **Solution**: Check file extension (.ts, .tsx, .js, .jsx for code)
- **Manual**: Specify type in CLI commands

**4. "Low confidence scores"**
- **Cause**: Objective and subjective scores disagree
- **Solution**: Review both evaluations for consistency
- **Adjust**: Modify weights in `docs/eval/config.yaml`

### Getting Help

**1. Check the logs** in `builder/cache/` directory
**2. Run with verbose output**:
   ```bash
   python builder/cli.py eval:objective src/hello.ts --verbose
   ```
**3. Test individual components**:
   ```bash
   python builder/test_eval.py  # Test evaluation system
   python builder/cursor_bridge.py  # Test parsing utilities
   ```

**4. Review the evaluation protocol** in `.cursor/rules/evaluation.md`

### Performance Tips

**1. Run reports in parallel** when evaluating multiple files
**2. Use incremental evaluation** for large codebases
**3. Cache results** - the system automatically caches objective scores
**4. Batch Cursor evaluations** to reduce API calls

---

## Next Steps

Once you're comfortable with the basic workflow:

1. **Customize evaluation weights** in `docs/eval/config.yaml`
2. **Add project-specific rules** in `docs/rules/`
3. **Integrate with CI/CD** using the CLI commands
4. **Create custom variant generators** for your specific needs
5. **Extend the evaluation metrics** for domain-specific quality measures

The evaluation system is designed to be flexible and extensible - don't hesitate to modify it for your specific requirements!
