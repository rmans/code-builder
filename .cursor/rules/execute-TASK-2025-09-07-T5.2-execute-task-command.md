---
id: execute-TASK-2025-09-07-T5.2-execute-task-command
title: Command & Rules – execute-task + per-task rules
description: Expose cb task run <ID>, @rules/execute-task, and @rules/execute-TASK-###
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: commands
priority: 7
agent_type: backend
dependencies: T5.1, T3.4
tags: [commands, rules, tasks]
---

# Command: Command & Rules – execute-task + per-task rules

## Description
Expose cb task run <ID>, @rules/execute-task, and @rules/execute-TASK-###

## Usage
```bash
cb execute-TASK-2025-09-07-T5.2-execute-task-command
# or
@rules/execute-TASK-2025-09-07-T5.2-execute-task-command
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
cb execute-TASK-2025-09-07-T5.2-execute-task-command

# Execute specific phase
cb execute-TASK-2025-09-07-T5.2-execute-task-command --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T5.2-execute-task-command --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T5.2-execute-task-command --interactive
```

## Task Details

---
id: TASK-2025-09-07-T5.2-execute-task-command
title: Command & Rules – execute-task + per-task rules
description: Expose cb task run <ID>, @rules/execute-task, and @rules/execute-TASK-###
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: backend-agent
domain: commands
priority: 7
agent_type: backend
dependencies: [T5.1, T3.4]
tags: [commands, rules, tasks]
---

# Task: Command & Rules – execute-task + per-task rules

## Phases
### Phase 1: 🚀 Implementation
- [ ] `.cb/commands/execute-task.md`, `.cursor/rules/execute-task`
- [ ] Per-task rules auto-synced from generator

### Phase 2: 🧪 Testing
- [ ] Parity with orchestrator path

### Phase 3: 📚 Documentation
- [ ] Usage + examples

### Phase 4: 🧹 Cleanup
- [ ] Ensure idempotent regeneration

### Phase 5: 💾 Commit
- [ ] Commit + sync

## Acceptance Criteria
- [ ] `@rules/execute-task` and `@rules/execute-TASK-###` share execution path

