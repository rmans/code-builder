---
id: execute-TASK-2025-09-07-T3.1-context-builder
title: Context Builder – compose existing graph/select/budget
description: Orchestrate PRD→ARCH→INT→IMPL→EXEC→TASK using context_graph/select/budget
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: context
priority: 10
agent_type: backend
dependencies: T2.1, T2.2
tags: [context, docs, tasks, orchestration]
---

# Command: Context Builder – compose existing graph/select/budget

## Description
Orchestrate PRD→ARCH→INT→IMPL→EXEC→TASK using context_graph/select/budget

## Usage
```bash
cb execute-TASK-2025-09-07-T3.1-context-builder
# or
@rules/execute-TASK-2025-09-07-T3.1-context-builder
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
cb execute-TASK-2025-09-07-T3.1-context-builder

# Execute specific phase
cb execute-TASK-2025-09-07-T3.1-context-builder --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T3.1-context-builder --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T3.1-context-builder --interactive
```

## Task Details

---
id: TASK-2025-09-07-T3.1-context-builder
title: Context Builder – compose existing graph/select/budget
description: Orchestrate PRD→ARCH→INT→IMPL→EXEC→TASK using context_graph/select/budget
status: completed
created: 2025-09-07
updated: 2025-01-15
owner: backend-agent
domain: context
priority: 10
agent_type: backend
dependencies: [T2.1, T2.2]
tags: [context, docs, tasks, orchestration]
---

# Task: Context Builder – compose existing graph/select/budget

## Phases
### Phase 1: 🚀 Implementation
- [x] Thin orchestrator that composes `builder/core/context_graph.py`, `context_select.py`, `context_budget.py`
- [x] Flags: `--from discovery,interview`, `--overwrite`, `--sections prd,arch,int,impl,exec,task`
- [x] Outputs:
  - `cb_docs/context/PRD.md`
  - `FE_Architecture.md`, `BE_Architecture.md`
  - `Integration_Plan.md`
  - `Implementation_Roadmap.md`
  - `Execution_Plan.md`
  - `tasks/*.md` + `tasks/index.json`

### Phase 2: 🧪 Testing
- [x] Golden-file tests for headers and key sections
- [x] Verify idempotency + partial regeneration

### Phase 3: 📚 Documentation
- [x] Update "Create Context" section with examples

### Phase 4: 🧹 Cleanup
- [x] Clear warnings for missing inputs; non-fatal

### Phase 5: 💾 Commit
- [x] Commit

## Acceptance Criteria
- [x] Deterministic outputs given same inputs
- [x] All 8 doc types linked (see T7.2)

## Completion Summary

**✅ TASK COMPLETED SUCCESSFULLY!**

### Final Results
- **Context Builder**: Template-based document generation system
- **Master File Integration**: Automatic table generation and cleanup
- **Proper Naming**: Date and title prefixes prevent conflicts
- **Template System**: Uses existing Handlebars templates

### Key Features Implemented
- **Template-Based Generation**: Uses existing Handlebars templates for consistent structure
- **Master File Integration**: Automatically updates master files with document entries
- **Clean Frontmatter**: Master files only contain necessary frontmatter (no documents section)
- **Proper Naming**: Files named as TYPE-YYYY-MM-DD-Title.md
- **CLI Integration**: ctx:build command with full options
- **Table Generation**: Dynamic table generation from document data

### Generated Files
- `cb_docs/prd/PRD-{date}-{title}.md` - Product Requirements Document
- `cb_docs/arch/ARCH-{date}-{title}.md` - Architecture Document
- `cb_docs/integrations/INT-{date}-{title}.md` - Integration Plan
- `cb_docs/impl/IMPL-{date}-{title}.md` - Implementation Roadmap
- `cb_docs/exec/EXEC-{date}-{title}.md` - Execution Plan
- `cb_docs/tasks/TASK-{date}-F{num}.md` - Task files
- `cb_docs/tasks/index.json` - Task index
- Updated master files with proper tables

### Testing Results
- ✅ Template rendering works correctly with discovery and interview data
- ✅ Idempotency verified - same inputs produce same outputs
- ✅ Partial regeneration works correctly
- ✅ Master files are properly updated and synced
- ✅ Frontmatter is clean (no documents section)
- ✅ Tables are generated dynamically from document data
- ✅ All acceptance criteria met

### CLI Commands
- `python -m builder.core.cli ctx:build --overwrite` - Generate all documents
- `python -m builder.core.cli ctx:build --sections prd --sections arch --overwrite` - Generate specific sections
- `python -m builder.core.cli master:sync` - Sync all master files
- `python -m builder.core.cli master:sync --type prd` - Sync specific master file

**The Context Builder is now complete and ready for production use!**

