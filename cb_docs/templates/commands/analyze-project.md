---
id: analyze-project
title: Analyze Project
description: Analyze project structure and generate discovery report
status: active
created: 2025-01-15
updated: 2025-01-15
owner: system
domain: discovery
priority: 8
agent_type: backend
dependencies: []
tags: [discovery, analysis, project]
---

# Command: Analyze Project

## Description
Analyzes the current project structure, detects technologies, frameworks, and generates a comprehensive discovery report.

## Usage
```bash
cb analyze
# or
@rules/analyze-project
```

## Outputs
- `cb_docs/discovery/report.json` - Detailed project analysis
- `cb_docs/discovery/summary.md` - Human-readable summary

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
