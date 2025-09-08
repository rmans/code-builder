---
id: project-status
title: Project Status
description: Display current project status and metrics
status: active
created: 2025-09-07
updated: 2025-09-07
owner: system
domain: status
priority: 6
agent_type: backend
dependencies: []
tags: [status, metrics, dashboard]
---

# Command: Project Status

## Description
Displays current project status, metrics, and progress information including task completion, document status, and system health.

## Usage
```bash
cb status
# or
@rules/project-status
```

## Outputs
- Console output with status summary
- `cb_docs/status/status.json` - Detailed status data
- `cb_docs/status/metrics.json` - Performance metrics

## Flags
- `--format FORMAT` - Output format (table,json,yaml)
- `--verbose` - Show detailed information
- `--metrics` - Include performance metrics
- `--tasks` - Show task status
- `--docs` - Show document status

## Examples
```bash
# Basic status
cb status

# Detailed status with metrics
cb status --verbose --metrics

# JSON output
cb status --format json

# Task-focused status
cb status --tasks --verbose
```

## Status Information
- **Project Health**: Overall project status
- **Task Progress**: Completed vs pending tasks
- **Document Status**: Generated documents and their status
- **System Metrics**: Performance and resource usage
- **Recent Activity**: Latest commands and changes
- **Dependencies**: Project dependencies and versions

## Template Variables
- `code-builder` - Project name
- `Node.js` - Project type
- `next` - Primary framework
- `JSON` - Primary language
- `{{total_tasks}}` - Total number of tasks
- `{{completed_tasks}}` - Number of completed tasks
- `{{total_docs}}` - Total number of documents
- `{{last_updated}}` - Last update timestamp
