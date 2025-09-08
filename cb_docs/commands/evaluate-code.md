---
id: evaluate-code
title: Evaluate Code
description: Evaluate code quality, performance, and compliance
status: active
created: 2025-09-07
updated: 2025-09-07
owner: system
domain: evaluation
priority: 7
agent_type: backend
dependencies: [analyze-project]
tags: [evaluation, quality, performance, compliance]
---

# Command: Evaluate Code

## Description
Evaluates code quality, performance, security, and compliance against project standards and best practices.

## Usage
```bash
cb evaluate
# or
@rules/evaluate-code
```

## Outputs
- `cb_docs/eval/evaluation-report.json` - Detailed evaluation results
- `cb_docs/eval/quality-metrics.json` - Quality metrics and scores
- `cb_docs/eval/compliance-report.md` - Human-readable compliance report
- `cb_docs/eval/performance-analysis.json` - Performance analysis

## Flags
- `--type TYPE` - Evaluation type (quality,performance,security,compliance,all)
- `--files PATTERN` - Specific files to evaluate
- `--standards STANDARDS` - Standards to check against
- `--threshold THRESHOLD` - Quality threshold (0-100)
- `--output FORMAT` - Output format (json,md,html)

## Examples
```bash
# Full evaluation
cb evaluate

# Quality evaluation only
cb evaluate --type quality

# Specific files
cb evaluate --files "src/**/*.py"

# Custom threshold
cb evaluate --threshold 80

# Security evaluation
cb evaluate --type security
```

## Evaluation Types

### Quality Evaluation
- **Code Style**: Linting, formatting, naming conventions
- **Complexity**: Cyclomatic complexity, maintainability index
- **Documentation**: Code comments, docstrings, README coverage
- **Test Coverage**: Unit test coverage, integration test coverage

### Performance Evaluation
- **Runtime Performance**: Execution time, memory usage
- **Build Performance**: Compilation time, bundle size
- **Database Performance**: Query optimization, indexing

### Security Evaluation
- **Vulnerability Scanning**: Known security issues
- **Dependency Audit**: Outdated or vulnerable dependencies
- **Code Security**: Security anti-patterns, best practices

### Compliance Evaluation
- **Standards Compliance**: Industry standards, coding standards
- **License Compliance**: License compatibility, attribution
- **Regulatory Compliance**: GDPR, HIPAA, SOX requirements

## Template Variables
- `code-builder` - Project name
- `Node.js` - Project type
- `next` - Primary framework
- `JSON` - Primary language
- `{{quality_score}}` - Overall quality score
- `{{performance_score}}` - Performance score
- `{{security_score}}` - Security score
- `{{compliance_score}}` - Compliance score
