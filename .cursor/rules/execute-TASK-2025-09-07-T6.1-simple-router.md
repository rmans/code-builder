---
id: execute-TASK-2025-09-07-T6.1-simple-router
title: Simple Command Router
description: Map discover/context/eval/task/docs/fix/status to complex commands
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: commands
priority: 7
agent_type: backend
dependencies: T0.3, T0.4
tags: [router, mapping, commands]
---

# Command: Simple Command Router

## Description
Map discover/context/eval/task/docs/fix/status to complex commands

## Usage
```bash
cb execute-TASK-2025-09-07-T6.1-simple-router
# or
@rules/execute-TASK-2025-09-07-T6.1-simple-router
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
cb execute-TASK-2025-09-07-T6.1-simple-router

# Execute specific phase
cb execute-TASK-2025-09-07-T6.1-simple-router --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T6.1-simple-router --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T6.1-simple-router --interactive
```

## Task Details

---
id: TASK-2025-09-07-T6.1-simple-router
title: Simple Command Router
description: Map discover/context/eval/task/docs/fix/status to complex commands
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: backend-agent
domain: commands
priority: 7
agent_type: backend
dependencies: [T0.3, T0.4]
tags: [router, mapping, commands]
---

# Task: Simple Command Router

## Phases
### Phase 1: 🚀 Implementation
- [ ] `builder/overlay/simple_router.py` with mappings:
  - discover→discover:new, context→ctx:build-enhanced, eval→eval:objective
  - task→task:execute, docs→doc:index, fix→[lint:fix,format,cleanup:artifacts], status→orchestrator:status

### Phase 2: 🧪 Testing
- [ ] Unit tests for all mappings and multi-command handling

### Phase 3: 📚 Documentation
- [ ] Cheatsheet in `implement.md`

### Phase 4: 🧹 Cleanup
- [ ] Helpful error output for unknown commands

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] `cb <simple>` works predictably

