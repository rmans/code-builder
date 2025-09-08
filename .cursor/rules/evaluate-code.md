# Evaluate Code

Evaluate code quality, performance, and compliance using objective metrics and automated tools.

## Usage

```bash
cb eval:objective [TARGET]
cb simple eval [TARGET]
```

## Key Features

- **Objective Metrics**: Automated evaluation using multiple tools
- **Multiple Targets**: Evaluate paths, tasks, or phases
- **Flexible Output**: JSON or Markdown reports
- **CI-Friendly**: Proper exit codes for automation
- **Comprehensive Scoring**: Tests, coverage, linting, spelling, and guardrails

## Examples

### Basic Evaluation
```bash
# Evaluate current directory
cb eval:objective
cb simple eval

# Evaluate specific path
cb eval:objective src/
cb eval:objective tests/
```

### Output Formats
```bash
# JSON output (default)
cb eval:objective --output-format json

# Markdown report
cb eval:objective --output-format md
```

### Target Types
```bash
# Evaluate specific file/directory
cb eval:objective src/components/

# Evaluate task result
cb eval:objective TASK-001

# Evaluate phase
cb eval:objective implementation
```

## Evaluation Metrics

The system evaluates code across multiple dimensions:

### Test Quality (0-100)
- Test coverage percentage
- Test execution success rate
- Test quality metrics

### Code Coverage (0-100)
- Line coverage percentage
- Branch coverage percentage
- Function coverage percentage

### Linting (0-100)
- ESLint compliance
- Code style adherence
- Best practice violations

### Documentation (0-100)
- Spelling accuracy
- Documentation completeness
- Markdown linting

### Security & Compliance (0-100)
- Guardrail violations
- Security best practices
- Compliance rules

### Overall Score (0-100)
Weighted average of all metrics based on project configuration.

## Output Files

### JSON Results (`cb_docs/eval/evaluation_YYYYMMDD_HHMMSS.json`)
```json
{
  "tests": 100.0,
  "coverage": 85.5,
  "lint": 98.0,
  "spell": 90.0,
  "guardrails": 75.0,
  "overall": 89.7
}
```

### Markdown Report (`cb_docs/eval/evaluation_YYYYMMDD_HHMMSS.md`)
Comprehensive report with:
- Executive summary
- Detailed metrics breakdown
- Recommendations for improvement
- Visual score indicators

## Integration

### CI/CD Pipelines
```bash
# In CI script
cb eval:objective
if [ $? -eq 0 ]; then
    echo "✅ Code quality check passed"
else
    echo "❌ Code quality check failed"
    exit 1
fi
```

### Quality Gates
```bash
# Set quality threshold
cb eval:objective --output-format json > eval.json
score=$(jq -r '.overall' eval.json)
if (( $(echo "$score >= 80" | bc -l) )); then
    echo "✅ Quality gate passed: $score"
else
    echo "❌ Quality gate failed: $score"
    exit 1
fi
```

### Monitoring
```bash
# Track quality trends
cb eval:objective --output-format json > "eval_$(date +%Y%m%d).json"
```

## Best Practices

1. **Regular Evaluation**: Run evaluations frequently during development
2. **Quality Gates**: Set minimum thresholds for CI/CD pipelines
3. **Trend Analysis**: Track scores over time to identify improvements
4. **Targeted Evaluation**: Focus on specific areas when needed
5. **Documentation**: Use markdown reports for human-readable summaries

## Troubleshooting

### Common Issues
- **No tools available**: Ensure evaluation tools are installed and configured
- **Missing reports**: Check that tool output files exist in expected locations
- **Low scores**: Review specific metric details to identify improvement areas

### Configuration
Evaluation behavior can be configured in `cb_docs/eval/config.yaml`:
- Tool paths and availability
- Scoring weights and thresholds
- Default values for missing data

## Related Commands

- `cb simple eval` - Use simple router for evaluation
- `cb eval:task TASK_ID` - Evaluate specific task result
- `cb eval:phase PHASE` - Evaluate specific phase
- `cb simple status` - Check overall project status
