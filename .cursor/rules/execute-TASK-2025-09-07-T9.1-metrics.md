---
id: execute-TASK-2025-09-07-T9.1-metrics
title: Metrics Collection – command metrics
description: time_to_first_rules, command_discovery_rate, execution_success_rate → metrics.json
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: telemetry
priority: 5
agent_type: backend
dependencies: T0.3, T6.1
tags: [telemetry, metrics]
---

# Command: Metrics Collection – command metrics

## Description
time_to_first_rules, command_discovery_rate, execution_success_rate → metrics.json

## Usage
```bash
cb execute-TASK-2025-09-07-T9.1-metrics
# or
@rules/execute-TASK-2025-09-07-T9.1-metrics
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
cb execute-TASK-2025-09-07-T9.1-metrics

# Execute specific phase
cb execute-TASK-2025-09-07-T9.1-metrics --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T9.1-metrics --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T9.1-metrics --interactive
```

## Task Details

---
id: TASK-2025-09-07-T9.1-metrics
title: Metrics Collection – command metrics
description: time_to_first_rules, command_discovery_rate, execution_success_rate → metrics.json
status: pending
created: 2025-09-07
updated: 2025-09-07
owner: telemetry-agent
domain: telemetry
priority: 5
agent_type: backend
dependencies: [T0.3, T6.1]
tags: [telemetry, metrics]
---

# Task: Metrics Collection – command metrics

## Phases
### Phase 1: 🚀 Implementation
- [ ] Append to `.cb/cache/command_state/metrics.json`

### Phase 2: 🧪 Testing
- [ ] Simulate runs; verify counters + timestamps

### Phase 3: 📚 Documentation
- [ ] Add to `evaluate.md`

### Phase 4: 🧹 Cleanup
- [ ] Size cap + rotation

### Phase 5: 💾 Commit
- [ ] Commit

## Acceptance Criteria
- [ ] Metrics visible via `cb status`

