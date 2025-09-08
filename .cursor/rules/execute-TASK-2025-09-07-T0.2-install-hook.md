---
id: execute-TASK-2025-09-07-T0.2-install-hook
title: Install Hook – setup_commands
description: Add setup_commands() to install.sh to generate and sync commands
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: infrastructure
priority: 6
agent_type: backend
dependencies: T0.1
tags: [install, bootstrap, commands]
---

# Command: Install Hook – setup_commands

## Description
Add setup_commands() to install.sh to generate and sync commands

## Usage
```bash
cb execute-TASK-2025-09-07-T0.2-install-hook
# or
@rules/execute-TASK-2025-09-07-T0.2-install-hook
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
cb execute-TASK-2025-09-07-T0.2-install-hook

# Execute specific phase
cb execute-TASK-2025-09-07-T0.2-install-hook --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T0.2-install-hook --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T0.2-install-hook --interactive
```

## Task Details

---
id: TASK-2025-09-07-T0.2-install-hook
title: Install Hook – setup_commands
description: Add setup_commands() to install.sh to generate and sync commands
status: completed
created: 2025-09-07
updated: 2025-01-15
owner: platform-agent
domain: infrastructure
priority: 6
agent_type: backend
dependencies: [T0.1]
tags: [install, bootstrap, commands]
---

# Task: Install Hook – setup_commands

## Phases
### Phase 1: 🚀 Implementation
- [x] Add `setup_commands()` in `install.sh`:
  - copy templates → generate commands → sync to `.cursor/rules/`
- [x] Echo friendly status (✅ Commands available via @rules/…)

### Phase 2: 🧪 Testing
- [x] `bash install.sh` on clean repo → `@rules/*` available

### Phase 3: 📚 Documentation
- [x] Document install step in `implement.md`

### Phase 4: 🧹 Cleanup
- [x] Idempotent re-runs; safe if directories already exist

### Phase 5: 💾 Commit
- [x] `git add . && git commit -m "chore: install hook to hydrate/sync commands"`

## Acceptance Criteria
- [x] Running install produces runnable `@rules/*` files
- [x] No duplicate files on repeated runs

## Completion Summary
**Completed on:** 2025-01-15  
**Commit:** a170dad - "chore: install hook to hydrate/sync commands"

### What Was Accomplished:
- ✅ Added `setup_commands()` function to `scripts/install.sh`
- ✅ Created command files (`analyze-project.md`, `plan-project.md`) in `.cb/commands/`
- ✅ Implemented rule merger with project rule precedence
- ✅ Generated `@rules/` files for each command
- ✅ Updated documentation in `implement.md`
- ✅ Ensured idempotent re-runs
- ✅ Committed all changes successfully

### Infrastructure Ready For:
- Command system implementation (T0.3)
- Path translation layer (T0.4)
- Cursor integration (T0.5)

