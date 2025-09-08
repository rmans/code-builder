---
id: execute-TASK-2025-09-07-T5.1-task-runner
title: Execute-Task – Single Task Runner
description: Thin facade over task_orchestrator to run/pick one task and report result
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: orchestrator
priority: 8
agent_type: backend
dependencies: T4.1
tags: [single-task, picker, retries]
---

# Command: Execute-Task – Single Task Runner

## Description
Thin facade over task_orchestrator to run/pick one task and report result

## Usage
```bash
cb execute-TASK-2025-09-07-T5.1-task-runner
# or
@rules/execute-TASK-2025-09-07-T5.1-task-runner
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
cb execute-TASK-2025-09-07-T5.1-task-runner

# Execute specific phase
cb execute-TASK-2025-09-07-T5.1-task-runner --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T5.1-task-runner --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T5.1-task-runner --interactive
```

## Task Details

---
id: TASK-2025-09-07-T5.1-task-runner
title: Execute-Task – Single Task Runner
description: Thin facade over task_orchestrator to run/pick one task and report result
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: backend-agent
domain: orchestrator
priority: 8
agent_type: backend
dependencies: [T4.1]
tags: [single-task, picker, retries]
---

# Task: Execute-Task – Single Task Runner

## Phases
### Phase 1: 🚀 Implementation
- [ ] Args: `<TASK_ID>` or `--pick`
- [ ] Flags: `--retries`, `--timeout`, `--resume`
- [ ] Outputs: `results/<TASK_ID>.json`, `logs/<TASK_ID>.log`

### Phase 2: 🧪 Testing
- [ ] Happy path, timeout, retry, resume correctness

### Phase 3: 📚 Documentation
- [ ] Examples for `@rules/execute-task` & `@rules/execute-TASK-###`

### Phase 4: 🧹 Cleanup
- [ ] Exit codes reflect pass/fail

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Picker lists only runnable tasks (deps satisfied)

