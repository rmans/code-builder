---
id: task-execution-cleanup
title: Task Execution Cleanup
description: Prevent temporary execute-TASK-*.md files in .cursor/rules/ and ensure proper cleanup
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: orchestration
priority: 9
agent_type: backend
tags: [orchestration, tasks, cleanup, temp-files]
---

# @rules/task-execution-cleanup

Prevent temporary `execute-TASK-*.md` files from being created in `.cursor/rules/` and ensure proper cleanup of task execution artifacts.

## Problem

When executing tasks, the system creates temporary `execute-TASK-*.md` files in `.cursor/rules/` that:
- Clutter the rules directory
- Are not meant to be permanent
- Should be cleaned up automatically
- Can accumulate over time if not managed

## Solution

### 1. **No Temporary Files in .cursor/rules/**
- **NEVER** create `execute-TASK-*.md` files in `.cursor/rules/`
- Use `.cb/cache/task-execution/` for temporary execution files
- Keep `.cursor/rules/` clean and focused on actual rules

### 2. **Proper Temporary File Management**
- Create temporary files in `.cb/cache/task-execution/`
- Use descriptive names: `task-{TASK_ID}-execution-{timestamp}.md`
- Clean up files immediately after task completion
- Use `.gitignore` to exclude temporary execution files

### 3. **Automatic Cleanup**
- Clean up temporary files on successful task completion
- Clean up temporary files on task failure
- Clean up temporary files on system shutdown
- Log cleanup actions for debugging

## Implementation

### Directory Structure
```
.cb/
├── cache/
│   └── task-execution/          # Temporary execution files
│       ├── task-TASK-001-execution-20250908-103000.md
│       └── task-TASK-002-execution-20250908-103500.md
└── rules/                       # Clean rules directory
    ├── execute-tasks.md         # Main rule (permanent)
    └── task-execution-cleanup.md # This rule (permanent)
```

### File Naming Convention
- **Temporary files**: `task-{TASK_ID}-execution-{timestamp}.md`
- **Permanent files**: `{rule-name}.md` (no execute- prefix)

### Cleanup Process
1. **Before task execution**: Create temp file in `.cb/cache/task-execution/`
2. **During execution**: Write progress to temp file
3. **After completion**: Move temp file to results directory or delete
4. **On failure**: Delete temp file and log error

## Rules

### ✅ **DO**
- Create temporary files in `.cb/cache/task-execution/`
- Use descriptive, timestamped filenames
- Clean up files immediately after use
- Log cleanup actions
- Use `.gitignore` for temporary directories

### ❌ **DON'T**
- Create `execute-TASK-*.md` files in `.cursor/rules/`
- Leave temporary files in rules directory
- Use generic or confusing filenames
- Forget to clean up after task completion
- Commit temporary execution files

## Examples

### ✅ **Correct Implementation**
```python
# Create temp file in proper location
temp_file = Path(".cb/cache/task-execution") / f"task-{task_id}-execution-{timestamp}.md"
temp_file.parent.mkdir(parents=True, exist_ok=True)

# Write execution progress
with open(temp_file, 'w') as f:
    f.write(f"Executing {task_id}...")

# Clean up after completion
temp_file.unlink()
```

### ❌ **Incorrect Implementation**
```python
# DON'T: Create in rules directory
temp_file = Path(".cursor/rules") / f"execute-{task_id}.md"

# DON'T: Leave files behind
# (no cleanup code)
```

## Monitoring

### Health Checks
- Monitor `.cursor/rules/` for temporary files
- Alert if `execute-TASK-*.md` files are found
- Check `.cb/cache/task-execution/` for orphaned files
- Verify cleanup is working properly

### Logging
- Log all temporary file creation
- Log all cleanup actions
- Log any cleanup failures
- Track file accumulation over time

## Integration

### Task Execution System
- Integrate with `execute-tasks` command
- Hook into task completion events
- Ensure cleanup on all exit paths
- Handle cleanup in error scenarios

### CI/CD Pipeline
- Add checks for temporary files in rules directory
- Verify cleanup is working in tests
- Monitor for file accumulation
- Alert on cleanup failures

## Notes

- This rule prevents the accumulation of temporary files
- Ensures `.cursor/rules/` stays clean and focused
- Improves system maintainability
- Reduces confusion about file purposes
- Makes debugging easier by keeping temp files organized
