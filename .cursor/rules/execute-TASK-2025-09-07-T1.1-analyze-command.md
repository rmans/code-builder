---
id: execute-TASK-2025-09-07-T1.1-analyze-command
title: Implement Simple Command – Analyze Project
description: Route cb analyze → discover:new and generate @rules/analyze-project
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: commands
priority: 10
agent_type: backend
dependencies: T0.1, T0.2, T0.3, T0.4
tags: [commands, agent-os, discovery, overlay]
---

# Command: Implement Simple Command – Analyze Project

## Description
Route cb analyze → discover:new and generate @rules/analyze-project

## Usage
```bash
cb execute-TASK-2025-09-07-T1.1-analyze-command
# or
@rules/execute-TASK-2025-09-07-T1.1-analyze-command
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
cb execute-TASK-2025-09-07-T1.1-analyze-command

# Execute specific phase
cb execute-TASK-2025-09-07-T1.1-analyze-command --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T1.1-analyze-command --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T1.1-analyze-command --interactive
```

## Task Details

---
id: TASK-2025-09-07-T1.1-analyze-command
title: Implement Simple Command – Analyze Project
description: Route cb analyze → discover:new and generate @rules/analyze-project
status: completed
created: 2025-09-07
updated: 2025-01-15
owner: backend-agent
domain: commands
priority: 10
agent_type: backend
dependencies: [T0.1, T0.2, T0.3, T0.4]
tags: [commands, agent-os, discovery, overlay]
---

# Task: Implement Simple Command – Analyze Project

## Phases
### Phase 1: 🚀 Implementation
- [x] Map in `builder/overlay/simple_router.py`
- [x] Create `.cb/commands/analyze-project.md`
- [x] Create rule `.cursor/rules/analyze-project` (uses OverlayPaths)

### Phase 2: 🧪 Testing
- [x] `cb analyze` and `@rules/analyze-project` in overlay + standalone

### Phase 3: 📚 Documentation
- [x] Update `implement.md` with usage examples

### Phase 4: 🧹 Cleanup
- [x] Validate command doc format; remove hardcoded paths

### Phase 5: 💾 Commit
- [x] Commit + `cb commands:sync`

## Acceptance Criteria
- [x] Works from any repo root; dual-mode support verified

## Completion Summary

**✅ TASK COMPLETED SUCCESSFULLY!**

### Final Results
- **Simple Router**: Created `builder/overlay/simple_router.py` with analyze command
- **Command File**: Copied `analyze-project.md` to `.cb/commands/`
- **Rules Generation**: Created `@rules/analyze-project` using OverlayPaths
- **Dual Mode Support**: Works in both overlay and standalone modes
- **Comprehensive Documentation**: Added Simple Commands section to implement.md

### Key Features Implemented
- **cb analyze command** with --depth, --ignore, --ci options
- **Technology detection** for Python, JavaScript, Markdown, YAML, etc.
- **Project analysis** with file counting and directory structure
- **@rules/ integration** for Cursor agent compatibility
- **OverlayPaths integration** for consistent path resolution
- **Error handling** with graceful fallbacks

### Generated Files
- `cb_docs/discovery/analysis.json` - Detailed project analysis
- `cb_docs/discovery/summary.md` - Human-readable summary
- `.cursor/rules/analyze-project.md` - Agent rules file
- `builder/overlay/simple_router.py` - Simple command router

### Testing Results
- ✅ cb analyze command works in overlay mode
- ✅ @rules/analyze-project functionality verified
- ✅ Dual-mode support confirmed
- ✅ commands:sync integration working
- ✅ All acceptance criteria met

**The simple analyze command is now complete and ready for production use!**

