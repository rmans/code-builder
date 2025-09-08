---
id: execute-TASK-2025-09-07-T8.2-current-md
title: Current Instructions – .cb/instructions/current.md
description: Maintain active agent, task, next command, last errors
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: docs
priority: 6
agent_type: backend
dependencies: T4.3
tags: [current, status, docs]
---

# Command: Current Instructions – .cb/instructions/current.md

## Description
Maintain active agent, task, next command, last errors

## Usage
```bash
cb execute-TASK-2025-09-07-T8.2-current-md
# or
@rules/execute-TASK-2025-09-07-T8.2-current-md
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
cb execute-TASK-2025-09-07-T8.2-current-md

# Execute specific phase
cb execute-TASK-2025-09-07-T8.2-current-md --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T8.2-current-md --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T8.2-current-md --interactive
```

## Task Details

---
id: TASK-2025-09-07-T8.2-current-md
title: Current Instructions – .cb/instructions/current.md
description: Maintain active agent, task, next command, last errors
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: tooling-agent
domain: docs
priority: 6
agent_type: backend
dependencies: [T4.3]
tags: [current, status, docs]
---

# Task: Current Instructions – .cb/instructions/current.md

## Phases
### Phase 1: 🚀 Implementation
- [ ] Update on agent start/finish; include suggested `@rules/*`

### Phase 2: 🧪 Testing
- [ ] Orchestration exercise; file reflects state transitions

### Phase 3: 📚 Documentation
- [ ] Explain file semantics

### Phase 4: 🧹 Cleanup
- [ ] Keep concise; rotate error history

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Opening Cursor shows actionable next step

