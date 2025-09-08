---
id: execute-TASK-2025-09-07-T8.1-dynamic-updater
title: DynamicContentUpdater – placeholders & task status
description: Replace placeholders using discovery; update per-task command status; resync rules
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: tooling
priority: 6
agent_type: backend
dependencies: T1.2, T3.4
tags: [updater, sync]
---

# Command: DynamicContentUpdater – placeholders & task status

## Description
Replace placeholders using discovery; update per-task command status; resync rules

## Usage
```bash
cb execute-TASK-2025-09-07-T8.1-dynamic-updater
# or
@rules/execute-TASK-2025-09-07-T8.1-dynamic-updater
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
cb execute-TASK-2025-09-07-T8.1-dynamic-updater

# Execute specific phase
cb execute-TASK-2025-09-07-T8.1-dynamic-updater --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T8.1-dynamic-updater --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T8.1-dynamic-updater --interactive
```

## Task Details

---
id: TASK-2025-09-07-T8.1-dynamic-updater
title: DynamicContentUpdater – placeholders & task status
description: Replace placeholders using discovery; update per-task command status; resync rules
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: tooling-agent
domain: tooling
priority: 6
agent_type: backend
dependencies: [T1.2, T3.4]
tags: [updater, sync]
---

# Task: DynamicContentUpdater – placeholders & task status

## Phases
### Phase 1: 🚀 Implementation
- [ ] Replace `[PROJECT_TYPE]`, Language, Framework
- [ ] Sync `.cursor/rules/` after updates

### Phase 2: 🧪 Testing
- [ ] Run after an orchestration; verify per-task status reflects latest

### Phase 3: 📚 Documentation
- [ ] Add updater section to `implement.md`

### Phase 4: 🧹 Cleanup
- [ ] Debounce to avoid churn

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Command docs always reflect current state

