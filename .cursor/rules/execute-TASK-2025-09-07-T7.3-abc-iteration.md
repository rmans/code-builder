---
id: execute-TASK-2025-09-07-T7.3-abc-iteration
title: ABC Iteration Integration
description: Expose cb iterate run --target <phase|task> --rounds 5 and store iteration metadata
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: iteration
priority: 7
agent_type: backend
dependencies: T3.1, T6.3
tags: [iteration, abc, evaluation]
---

# Command: ABC Iteration Integration

## Description
Expose cb iterate run --target <phase|task> --rounds 5 and store iteration metadata

## Usage
```bash
cb execute-TASK-2025-09-07-T7.3-abc-iteration
# or
@rules/execute-TASK-2025-09-07-T7.3-abc-iteration
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
cb execute-TASK-2025-09-07-T7.3-abc-iteration

# Execute specific phase
cb execute-TASK-2025-09-07-T7.3-abc-iteration --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T7.3-abc-iteration --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T7.3-abc-iteration --interactive
```

## Task Details

---
id: TASK-2025-09-07-T7.3-abc-iteration
title: ABC Iteration Integration
description: Expose cb iterate run --target <phase|task> --rounds 5 and store iteration metadata
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: research-agent
domain: iteration
priority: 7
agent_type: backend
dependencies: [T3.1, T6.3]
tags: [iteration, abc, evaluation]
---

# Task: ABC Iteration Integration

## Phases
### Phase 1: 🚀 Implementation
- [ ] Runner to spawn A/B/C variants and evaluate via objective evaluator
- [ ] Persist variant scores + winner

### Phase 2: 🧪 Testing
- [ ] 5-round loop; winner selection deterministic given seed

### Phase 3: 📚 Documentation
- [ ] Add usage to `evaluate.md`

### Phase 4: 🧹 Cleanup
- [ ] Cap resource use; deterministic seeding

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Selector chooses winner; artifacts stored with references

