---
id: execute-TASK-2025-09-07-T7.2-doc-types
title: Document Types Alignment – 8 canonical types
description: Ensure PRD, ADR, ARCH(FE/BE), INT, IMPL, EXEC, TASK are produced and linked
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: docs
priority: 7
agent_type: backend
dependencies: T3.1
tags: [docs, index, linkage]
---

# Command: Document Types Alignment – 8 canonical types

## Description
Ensure PRD, ADR, ARCH(FE/BE), INT, IMPL, EXEC, TASK are produced and linked

## Usage
```bash
cb execute-TASK-2025-09-07-T7.2-doc-types
# or
@rules/execute-TASK-2025-09-07-T7.2-doc-types
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
cb execute-TASK-2025-09-07-T7.2-doc-types

# Execute specific phase
cb execute-TASK-2025-09-07-T7.2-doc-types --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T7.2-doc-types --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T7.2-doc-types --interactive
```

## Task Details

---
id: TASK-2025-09-07-T7.2-doc-types
title: Document Types Alignment – 8 canonical types
description: Ensure PRD, ADR, ARCH(FE/BE), INT, IMPL, EXEC, TASK are produced and linked
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: docs-agent
domain: docs
priority: 7
agent_type: backend
dependencies: [T3.1]
tags: [docs, index, linkage]
---

# Task: Document Types Alignment – 8 canonical types

## Phases
### Phase 1: 🚀 Implementation
- [ ] Generate/ensure all 8 doc types
- [ ] Create index page linking them

### Phase 2: 🧪 Testing
- [ ] Link integrity test

### Phase 3: 📚 Documentation
- [ ] Explain each type's purpose

### Phase 4: 🧹 Cleanup
- [ ] Consistent naming

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Single index navigates to all 8 types

