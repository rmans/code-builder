---
id: execute-TASK-2025-09-07-QG
title: Quality Gates – Release Criteria
description: Idempotency, parity, determinism, Cursor UX, CI suites green
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: release
priority: 10
agent_type: backend
dependencies: T1.3, T2.4, T3.6, T4.4, T5.3
tags: [quality, release, gates]
---

# Command: Quality Gates – Release Criteria

## Description
Idempotency, parity, determinism, Cursor UX, CI suites green

## Usage
```bash
cb execute-TASK-2025-09-07-QG
# or
@rules/execute-TASK-2025-09-07-QG
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
cb execute-TASK-2025-09-07-QG

# Execute specific phase
cb execute-TASK-2025-09-07-QG --phase implementation

# Dry run
cb execute-TASK-2025-09-07-QG --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-QG --interactive
```

## Task Details

---
id: TASK-2025-09-07-QG
title: Quality Gates – Release Criteria
description: Idempotency, parity, determinism, Cursor UX, CI suites green
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: release-agent
domain: release
priority: 10
agent_type: backend
dependencies: [T1.3, T2.4, T3.6, T4.4, T5.3]
tags: [quality, release, gates]
---

# Task: Quality Gates – Release Criteria

## Phases
### Phase 1: 🚀 Implementation
- [ ] Add CI checks: idempotency, parity (index↔rules), determinism (noninteractive)

### Phase 2: 🧪 Testing
- [ ] Run suites: discovery, interview, context, orchestrator, single-task

### Phase 3: 📚 Documentation
- [ ] Document gate definitions in `evaluate.md`

### Phase 4: 🧹 Cleanup
- [ ] Stabilize any flakey tests

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Clean end-to-end: `@rules/analyze-project → @rules/plan-project → @rules/create-context → @rules/execute-tasks`
- [ ] All suites green

