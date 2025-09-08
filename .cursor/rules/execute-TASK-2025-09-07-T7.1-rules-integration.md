---
id: execute-TASK-2025-09-07-T7.1-rules-integration
title: Rules System Integration – docs/rules/
description: Honor style/format rules in generated docs and reference in front-matter
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: docs
priority: 6
agent_type: backend
dependencies: T3.1
tags: [rules, docs]
---

# Command: Rules System Integration – docs/rules/

## Description
Honor style/format rules in generated docs and reference in front-matter

## Usage
```bash
cb execute-TASK-2025-09-07-T7.1-rules-integration
# or
@rules/execute-TASK-2025-09-07-T7.1-rules-integration
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
cb execute-TASK-2025-09-07-T7.1-rules-integration

# Execute specific phase
cb execute-TASK-2025-09-07-T7.1-rules-integration --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T7.1-rules-integration --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T7.1-rules-integration --interactive
```

## Task Details

---
id: TASK-2025-09-07-T7.1-rules-integration
title: Rules System Integration – docs/rules/
description: Honor style/format rules in generated docs and reference in front-matter
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: docs-agent
domain: docs
priority: 6
agent_type: backend
dependencies: [T3.1]
tags: [rules, docs]
---

# Task: Rules System Integration – docs/rules/

## Phases
### Phase 1: 🚀 Implementation
- [ ] Incorporate rules checks during generation
- [ ] Include rule refs in doc front-matter

### Phase 2: 🧪 Testing
- [ ] Spot-check rule violations flagged correctly

### Phase 3: 📚 Documentation
- [ ] Describe rules in index

### Phase 4: 🧹 Cleanup
- [ ] Suppress noisy non-actionable warnings

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] PRD/ARCH/INT/IMPL/EXEC include rule refs

