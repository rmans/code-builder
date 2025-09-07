# Analyze Project

## Description
Analyze project structure and generate discovery report.

## Usage
```bash
cb analyze
# or
@rules/analyze-project
```

## Agent Instructions
1. Execute the analyze command using Code Builder CLI
2. Follow any prompts or interactive elements
3. Report results and any issues encountered
4. Check generated discovery files

## Expected Outputs
- `/home/rmans/projects/code-builder/cb_docs/discovery/analysis.json` - Detailed project analysis
- `/home/rmans/projects/code-builder/cb_docs/discovery/summary.md` - Human-readable summary

## Flags
- `--depth N` - Analysis depth (default: 3)
- `--ignore PATTERN` - Ignore files matching pattern
- `--ci` - Non-interactive mode for CI/CD

## Examples
```bash
# Basic analysis
cb analyze

# Deep analysis with custom ignore
cb analyze --depth 5 --ignore "node_modules,dist"

# CI mode
cb analyze --ci
```

## Context
This command has been selected based on current project state and dependencies.
