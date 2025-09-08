---
id: execute-TASK-2025-09-07-T2.2-interview-runner
title: Interactive Interview – builder/discovery/interview.py
description: Guided Q&A; saves interview.json, assumptions.md, decisions.md
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: discovery
priority: 8
agent_type: backend
dependencies: T2.1
tags: [interview, adr, assumptions]
---

# Command: Interactive Interview – builder/discovery/interview.py

## Description
Guided Q&A; saves interview.json, assumptions.md, decisions.md

## Usage
```bash
cb execute-TASK-2025-09-07-T2.2-interview-runner
# or
@rules/execute-TASK-2025-09-07-T2.2-interview-runner
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
cb execute-TASK-2025-09-07-T2.2-interview-runner

# Execute specific phase
cb execute-TASK-2025-09-07-T2.2-interview-runner --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T2.2-interview-runner --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T2.2-interview-runner --interactive
```

## Task Details

---
id: TASK-2025-09-07-T2.2-interview-runner
title: Interactive Interview – builder/discovery/interview.py
description: Guided Q&A; saves interview.json, assumptions.md, decisions.md
status: completed
created: 2025-09-07
updated: 2025-01-15
owner: backend-agent
domain: discovery
priority: 8
agent_type: backend
dependencies: [T2.1]
tags: [interview, adr, assumptions]
---

# Task: Interactive Interview – builder/discovery/interview.py

## Phases
### Phase 1: 🚀 Implementation
- [x] TTY interactive & `--noninteractive` defaults
- [x] Persona presets: `--persona dev|pm|ai`
- [x] Outputs: `interview.json`, `assumptions.md`, `decisions.md`

### Phase 2: 🧪 Testing
- [x] Snapshot JSON; reruns stable with same flags

### Phase 3: 📚 Documentation
- [x] Add examples/questions catalog

### Phase 4: 🧹 Cleanup
- [x] Validate JSON schema

### Phase 5: 💾 Commit
- [x] Commit

## Acceptance Criteria
- [x] Links back to discovery summary; deterministic defaults

## Completion Summary

**✅ TASK COMPLETED SUCCESSFULLY!**

### Final Results
- **Interactive Interview System**: TTY-based interviews with persona support
- **Persona Defaults**: Developer, Project Manager, and AI Specialist personas
- **Structured Outputs**: JSON, assumptions, and decisions documents
- **JSON Schema Validation**: Proper field types and required fields

### Key Features Implemented
- **TTY Support**: Interactive mode with automatic fallback to non-interactive
- **Persona-Based Planning**: Three distinct personas with appropriate defaults
- **Structured Outputs**: interview.json, assumptions.md, decisions.md
- **CLI Integration**: discover:interview command with full options
- **Schema Validation**: Consistent JSON structure with proper types

### Generated Files
- `cb_docs/planning/interview.json` - Complete interview responses
- `cb_docs/planning/assumptions.md` - Project assumptions document
- `cb_docs/planning/decisions.md` - Key decisions document
- `builder/discovery/interview.py` - Enhanced interview module
- `builder/core/cli/discovery_commands.py` - CLI command integration

### Testing Results
- ✅ TTY interactive mode works correctly
- ✅ Non-interactive mode produces deterministic output
- ✅ All three personas generate appropriate defaults
- ✅ JSON schema validation passes with all required fields
- ✅ File generation is reliable and consistent
- ✅ All acceptance criteria met

**The Interactive Interview System is now complete and ready for production use!**

