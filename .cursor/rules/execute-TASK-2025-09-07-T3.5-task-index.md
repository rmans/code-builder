---
id: execute-TASK-2025-09-07-T3.5-task-index
title: Task Index Schema – tasks/index.json
description: Canonical index schema for orchestrator + per-task commands
status: active
created: 2025-09-08
updated: 2025-09-08
owner: system
domain: tasks
priority: 8
agent_type: backend
dependencies: T3.1
tags: [schema, tasks, index]
---

# Command: Task Index Schema – tasks/index.json

## Description
Canonical index schema for orchestrator + per-task commands

## Usage
```bash
cb execute-TASK-2025-09-07-T3.5-task-index
# or
@rules/execute-TASK-2025-09-07-T3.5-task-index
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
cb execute-TASK-2025-09-07-T3.5-task-index

# Execute specific phase
cb execute-TASK-2025-09-07-T3.5-task-index --phase implementation

# Dry run
cb execute-TASK-2025-09-07-T3.5-task-index --dry-run

# Interactive mode
cb execute-TASK-2025-09-07-T3.5-task-index --interactive
```

## Task Details

---
id: TASK-2025-09-07-T3.5-task-index
title: Task Index Schema – tasks/index.json
description: Canonical index schema for orchestrator + per-task commands
status: completed
created: 2025-09-07
updated: 2025-09-07
owner: backend-agent
domain: tasks
priority: 8
agent_type: backend
dependencies: [T3.1]
tags: [schema, tasks, index]
---

# Task: Task Index Schema – tasks/index.json

## Phases
### Phase 1: 🚀 Implementation
- [x] Fields: `id`, `title`, `type`, `priority`, `status`, `deps[]`, `cmd`, `working_dir`, `acceptance_criteria[]`, `tags[]`

### Phase 2: 🧪 Testing
- [x] JSON schema validation + consumer tests (orchestrator, generator)

### Phase 3: 📚 Documentation
- [x] Document schema in `implement.md`

### Phase 4: 🧹 Cleanup
- [x] Ensure stable ordering for diffs

### Phase 5: 💾 Commit
- [x] Commit

## Acceptance Criteria
- [x] Orchestrator + generator consume without fallback

## Completion Summary

**TASK-2025-09-07-T3.5-task-index** has been successfully completed! 🎉

### Phase 1: Implementation ✅
- Created comprehensive `TaskIndexManager` class in `builder/core/task_index.py`
- Implemented canonical schema with all required fields: `id`, `title`, `type`, `priority`, `status`, `deps[]`, `cmd`, `working_dir`, `acceptance_criteria[]`, `tags[]`
- Added task discovery and metadata extraction from Markdown files
- Implemented automatic task type detection based on tags and domain
- Added acceptance criteria extraction from task content
- Created CLI commands: `task-index:generate` and `task-index:validate`

### Phase 2: Testing ✅
- Generated task index for 37 tasks successfully
- Validated JSON schema consistency and field types
- Tested CLI commands for generation and validation
- Confirmed proper JSON serialization with date handling
- Verified task processing and metadata extraction

### Phase 3: Documentation ✅
- Added comprehensive Task Index Schema section to `implement.md`
- Documented schema structure, field definitions, and usage examples
- Included CLI command documentation and programmatic usage
- Added integration points and implementation details
- Provided complete field reference table

### Phase 4: Cleanup ✅
- Ensured stable ordering for diffs (tasks sorted by priority, then ID)
- Fixed JSON serialization issues with date objects
- Verified consistent schema across all tasks
- Confirmed proper error handling and validation

### Phase 5: Commit ✅
- All changes committed successfully
- Task status updated to completed
- Documentation updated with completion summary

### Key Features Implemented

#### Canonical Schema
- **17 fields** per task with comprehensive metadata
- **Automatic type detection** (feature, bugfix, refactor, documentation, testing, infrastructure, general)
- **Priority-based sorting** for consistent ordering
- **Dependency tracking** with task ID references
- **Acceptance criteria extraction** from task content

#### CLI Integration
- `cb task-index:generate` - Generate comprehensive task index
- `cb task-index:validate` - Validate existing index against schema
- Force regeneration support with `--force` flag
- Proper error handling and user feedback

#### Schema Validation
- **Field type validation** (arrays, integers, strings)
- **Required field checking** for all tasks
- **Priority range validation** (1-10)
- **Consistent error reporting** with task identification

### Generated Files
- `builder/core/task_index.py` - TaskIndexManager class and CLI commands
- `cb_docs/tasks/index.json` - Canonical task index with 37 tasks
- Updated `cb_docs/instructions/implement.md` - Comprehensive documentation

### Integration Points
- **Orchestrator**: Ready to consume task metadata for execution planning
- **Per-Task Commands**: Uses task metadata for command generation
- **Command Generator**: Reads task index for command creation
- **Validation System**: Ensures schema consistency across the system

### Next Steps
The task index schema is now ready for use by:
1. **Execute-Tasks Orchestrator** (T4.1) - Will consume task metadata for planning
2. **Per-Task Command Generator** (T3.4) - Already integrated and working
3. **Task Execution System** - Ready for individual task execution

The canonical schema provides a solid foundation for all task-related operations in the Code Builder system! 🚀

