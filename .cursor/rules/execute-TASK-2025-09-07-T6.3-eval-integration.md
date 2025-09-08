---
id: execute-TASK-2025-09-07-T6.3-eval-integration
title: Evaluation Integration – evaluate-code
description: Use builder/evaluators/objective.py; router cb eval → eval:objective; rule @rules/evaluate-code
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: evaluation
priority: 8
agent_type: backend
dependencies: T6.1
tags: [evaluation, commands]
---

# Command: Evaluation Integration – evaluate-code

## Description
Use builder/evaluators/objective.py; router cb eval → eval:objective; rule @rules/evaluate-code

## Usage
```bash
cb execute-TASK-2025-09-07-T6.3-eval-integration
# or
@rules/execute-TASK-2025-09-07-T6.3-eval-integration
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
cb execute-TASK-2025-09-07-T6.3-eval-integration

# Execute specific phase
cb execute-TASK-2025-09-07-T6.3-eval-integration --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T6.3-eval-integration --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T6.3-eval-integration --interactive
```

## Task Details

---
id: TASK-2025-09-07-T6.3-eval-integration
title: Evaluation Integration – evaluate-code
description: Use builder/evaluators/objective.py; router cb eval → eval:objective; rule @rules/evaluate-code
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: qa-agent
domain: evaluation
priority: 8
agent_type: backend
dependencies: [T6.1]
tags: [evaluation, commands]
---

# Task: Evaluation Integration – evaluate-code

## Phases
### Phase 1: 🚀 Implementation
- [ ] CLI flags: `--target <path|task|phase>`
- [ ] Outputs: `cb_docs/eval/*.json|md`; fail → non-zero exit

### Phase 2: 🧪 Testing
- [ ] Evaluate generated docs and task results

### Phase 3: 📚 Documentation
- [ ] Add to `evaluate.md`

### Phase 4: 🧹 Cleanup
- [ ] Stable output schema

### Phase 5: 💾 Commit
- [ ] Commit + sync

## Acceptance Criteria
- [ ] Evaluation works on any artifact; CI-friendly exit codes

