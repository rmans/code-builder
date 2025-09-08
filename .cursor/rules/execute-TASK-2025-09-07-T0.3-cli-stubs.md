---
id: execute-TASK-2025-09-07-T0.3-cli-stubs
title: CLI Stubs – commands:* family
description: Add cb commands:refresh|sync|list|show in .cb/engine/core/cli.py
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: cli
priority: 6
agent_type: backend
dependencies: T0.1, T0.2
tags: [cli, commands, developer-experience]
---

# Command: CLI Stubs – commands:* family

## Description
Add cb commands:refresh|sync|list|show in .cb/engine/core/cli.py

## Usage
```bash
cb execute-TASK-2025-09-07-T0.3-cli-stubs
# or
@rules/execute-TASK-2025-09-07-T0.3-cli-stubs
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
cb execute-TASK-2025-09-07-T0.3-cli-stubs

# Execute specific phase
cb execute-TASK-2025-09-07-T0.3-cli-stubs --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T0.3-cli-stubs --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T0.3-cli-stubs --interactive
```

## Task Details

---
id: TASK-2025-09-07-T0.3-cli-stubs
title: CLI Stubs – commands:* family
description: Add cb commands:refresh|sync|list|show in .cb/engine/core/cli.py
status: completed
created: 2025-09-07
updated: 2025-01-15
owner: platform-agent
domain: cli
priority: 6
agent_type: backend
dependencies: [T0.1, T0.2]
tags: [cli, commands, developer-experience]
---

# Task: CLI Stubs – commands:* family

## Phases
### Phase 1: 🚀 Implementation
- [x] Implement: `commands:refresh`, `commands:sync`, `commands:list`, `commands:show <name>`
- [x] Wire to generator + sync modules

### Phase 2: 🧪 Testing
- [x] `cb commands:list` shows static + generated commands
- [x] `cb commands:show analyze-project` prints doc metadata

### Phase 3: 📚 Documentation
- [x] Add "Command utilities" section in `implement.md`

### Phase 4: 🧹 Cleanup
- [x] Consistent error codes; helpful messages

### Phase 5: 💾 Commit
- [x] `git add . && git commit -m "feat(cli): commands utilities"`

## Acceptance Criteria
- [x] All four subcommands function and are discoverable via `cb --help`

## Completion Summary
**Completed on:** 2025-01-15  
**Commit:** f8b7f74 - "feat(cli): commands utilities"

### What Was Accomplished:
- ✅ Implemented `commands:list` with table/JSON/YAML output formats and status filtering
- ✅ Implemented `commands:show` with full/metadata/usage view options
- ✅ Implemented `commands:refresh` to copy templates to `.cb/commands/`
- ✅ Implemented `commands:sync` to update `@rules/` files via rule merger
- ✅ Fixed JSON serialization for date objects in command metadata
- ✅ Added comprehensive error handling with helpful messages
- ✅ Updated `implement.md` with Command utilities documentation
- ✅ All commands discoverable via `cb --help`

### Infrastructure Ready For:
- Path translation layer (T0.4)
- Cursor integration (T0.5)
- Advanced command management features

