---
id: execute-tasks
title: Execute Tasks
description: Execute tasks with dependency management and parallelism control
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: orchestration
priority: 8
agent_type: backend
tags: [orchestration, tasks, execution, dependencies]
---

# @rules/execute-tasks

Execute tasks with intelligent dependency management, parallelism control, and comprehensive result tracking.

## Overview

The `execute-tasks` command provides a powerful orchestration system for running multiple tasks with:

- **Dependency Management**: Automatic task ordering based on dependencies
- **Parallelism Control**: Configurable parallel execution limits
- **Filtering**: Task selection by tags, priority, or specific IDs
- **Dry Run**: Execution planning without actual execution
- **Result Tracking**: Individual task results and aggregated summaries
- **Deadlock Detection**: Automatic detection of circular dependencies

## Usage

### Basic Execution
```bash
# Execute all tasks
cb execute-tasks

# Dry run to see execution plan
cb execute-tasks --dry-run
```

### Filtered Execution
```bash
# High priority tasks only
cb execute-tasks --priority 8

# Backend tasks only
cb execute-tasks --filter backend

# Specific tasks
cb execute-tasks --tasks TASK-2025-09-07-F01 TASK-2025-09-07-F02
```

### Parallel Execution
```bash
# Run up to 3 tasks in parallel
cb execute-tasks --max-parallel 3

# Dry run with parallelism
cb execute-tasks --dry-run --max-parallel 3
```

## Flags

| Flag | Type | Description | Example |
|------|------|-------------|---------|
| `--filter` | multiple | Filter tasks by tags | `--filter backend --filter api` |
| `--priority` | integer | Minimum priority threshold | `--priority 8` |
| `--max-parallel` | integer | Maximum parallel tasks | `--max-parallel 3` |
| `--dry-run` | flag | Show execution plan without running | `--dry-run` |
| `--tasks` | multiple | Specific task IDs to execute | `--tasks TASK-2025-09-07-F01` |
| `--output-dir` | string | Output directory for results | `--output-dir results/` |

## Outputs

### Individual Task Results
Each task generates a JSON result file in `cb_docs/tasks/results/`:

```json
{
  "task_id": "TASK-2025-09-07-F01",
  "name": "Implement Planning tools",
  "status": "completed",
  "started_at": "2025-09-08T10:30:00",
  "completed_at": "2025-09-08T10:45:00",
  "assigned_agent": "agent-1",
  "error_message": null
}
```

### Summary Report
Generated `cb_docs/tasks/results/summary.md`:

```markdown
# Task Execution Summary

Generated: 2025-09-08 10:45:00

## Overview
- **Total Tasks**: 5
- **Completed**: 4
- **Failed**: 1
- **Pending**: 0
- **Running**: 0

## Results by Status
- **Completed**: 4 (80.0%)
- **Failed**: 1 (20.0%)

## Task Details
...
```

## Examples

### Execute High Priority Tasks
```bash
cb execute-tasks --priority 8 --max-parallel 2
```

### Execute Backend Tasks Only
```bash
cb execute-tasks --filter backend --dry-run
```

### Execute Specific Tasks
```bash
cb execute-tasks --tasks TASK-2025-09-07-F01 TASK-2025-09-07-F02 --output-dir specific-results/
```

### Plan Execution Without Running
```bash
cb execute-tasks --dry-run --priority 7
```

## Error Handling

### Deadlock Detection
- Automatically detects circular dependencies
- Reports deadlocks in dry-run mode
- Prevents execution if deadlocks detected

### Fatal Error Handling
- Stops execution on task failures
- Reports failed tasks clearly
- Provides error messages and context

### Exit Codes
- `0`: Success (all tasks completed)
- `1`: Failure (tasks failed or errors detected)

## Integration

### Task Index
- Reads tasks from `cb_docs/tasks/index.json`
- Uses canonical task schema for consistency
- Supports all task metadata and dependencies

### Command Generator
- Works with per-task command generation
- Integrates with individual task execution
- Supports command chaining and workflows

### Result Management
- Saves results to structured output directory
- Generates comprehensive summaries
- Provides detailed execution tracking

## Agent Instructions

When using this command:

1. **Always start with dry-run** to understand the execution plan
2. **Use appropriate filters** to focus on relevant tasks
3. **Set reasonable parallelism** based on system resources
4. **Monitor execution progress** and handle failures gracefully
5. **Review results** in both individual JSON files and summary report
6. **Use exit codes** to determine success/failure in scripts

## Notes

- Tasks are executed in dependency order
- Parallel execution respects dependency constraints
- Results are saved even if execution fails
- Dry-run mode is safe and shows exact execution plan
- All flags can be combined for complex filtering
