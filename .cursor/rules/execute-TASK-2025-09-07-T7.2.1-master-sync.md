---
id: execute-TASK-2025-09-07-T7.2.1-master-sync
title: Master File Synchronization – 0000_MASTER_*.md
description: Hook document generation into master index/update flow
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: docs
priority: 6
agent_type: backend
dependencies: T7.2
tags: [master, sync, docs]
---

# Command: Master File Synchronization – 0000_MASTER_*.md

## Description
Hook document generation into master index/update flow

## Usage
```bash
cb execute-TASK-2025-09-07-T7.2.1-master-sync
# or
@rules/execute-TASK-2025-09-07-T7.2.1-master-sync
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
cb execute-TASK-2025-09-07-T7.2.1-master-sync

# Execute specific phase
cb execute-TASK-2025-09-07-T7.2.1-master-sync --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T7.2.1-master-sync --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T7.2.1-master-sync --interactive
```

## Task Details

---
id: TASK-2025-09-07-T7.2.1-master-sync
title: Master File Synchronization – 0000_MASTER_*.md
description: Hook document generation into master index/update flow
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: docs-agent
domain: docs
priority: 6
agent_type: backend
dependencies: [T7.2]
tags: [master, sync, docs]
---

# Task: Master File Synchronization – 0000_MASTER_*.md

## Phases
### Phase 1: 🚀 Implementation
- [ ] Update 0000_MASTER_* files during doc generation

### Phase 2: 🧪 Testing
- [ ] Ensure masters reflect latest titles/paths

### Phase 3: 📚 Documentation
- [ ] Describe master sync rules

### Phase 4: 🧹 Cleanup
- [ ] Avoid duplicate entries

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Masters always reflect current set with correct ordering

