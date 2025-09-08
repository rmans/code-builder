---
id: execute-TASK-2025-09-07-T4.3-cursor-hooks
title: Cursor Integration Hooks
description: Use/extend builder/utils/cursor_agent_integration.py to update current.md and per-task rules
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: cursor
priority: 8
agent_type: backend
dependencies: T0.5, T3.4
tags: [cursor, hooks, current-md]
---

# Command: Cursor Integration Hooks

## Description
Use/extend builder/utils/cursor_agent_integration.py to update current.md and per-task rules

## Usage
```bash
cb execute-TASK-2025-09-07-T4.3-cursor-hooks
# or
@rules/execute-TASK-2025-09-07-T4.3-cursor-hooks
```

## Outputs
- Task execution results
- Updated task status
- Generated artifacts (if applicable)

## Flags
- `--phase PHASE` - Execute specific phase only
- `--skip-phases PHASES` - Skip specific phases (comma-separated)
- `--dry-run` - Show execution plan without running
- `--interactive` - Interactive mode with confirmations
- `--force` - Force execution even if dependencies not met

## Examples
```bash
# Execute complete task
cb execute-TASK-2025-09-07-T4.3-cursor-hooks

# Execute specific phase
cb execute-TASK-2025-09-07-T4.3-cursor-hooks --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T4.3-cursor-hooks --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T4.3-cursor-hooks --interactive
```

## Task Details

---
id: TASK-2025-09-07-T4.3-cursor-hooks
title: Cursor Integration Hooks
description: Use/extend builder/utils/cursor_agent_integration.py to update current.md and per-task rules
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: backend-agent
domain: cursor
priority: 8
agent_type: backend
dependencies: [T0.5, T3.4]
tags: [cursor, hooks, current-md]
---

# Task: Cursor Integration Hooks

## Phases
### Phase 1: 🚀 Implementation
- [ ] `on_task_create()` → regenerate per-task rules
- [ ] `on_agent_start()` → update `.cb/instructions/current.md`

### Phase 2: 🧪 Testing
- [ ] Hooks fire during orchestrations; file content correct

### Phase 3: 📚 Documentation
- [ ] Describe hook timing and side effects

### Phase 4: 🧹 Cleanup
- [ ] Avoid tight loops; debounce updates

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] current.md always reflects active task/agent

