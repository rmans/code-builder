---
id: TASK-2025-01-15-refactor-cli
title: Refactor CLI - Break into Modules
description: Refactor builder/core/cli.py into logical modules for better maintainability
status: pending
created: 2025-01-15
updated: 2025-01-15
owner: platform-agent
domain: refactoring
priority: 8
agent_type: backend
dependencies: []
tags: [refactoring, cli, maintainability]
---

# Task: Refactor CLI - Break into Modules

## Problem
The `builder/core/cli.py` file has grown to 7,612 lines with 61 CLI commands, making it difficult to maintain and navigate.

## Proposed Solution
Break the CLI into logical modules based on command categories:

### Module Structure
```
builder/core/cli/
├── __init__.py              # Main CLI entry point
├── base.py                  # Base CLI setup and common utilities
├── document_commands.py     # doc:*, adr:*, master:* (8 commands)
├── context_commands.py      # ctx:*, context:* (12 commands)
├── discovery_commands.py    # discover:* (6 commands)
├── agent_commands.py        # agent:* (4 commands)
├── orchestrator_commands.py # orchestrator:* (12 commands)
├── evaluation_commands.py   # eval:*, rules:* (4 commands)
├── utility_commands.py      # commands:*, cleanup:*, yaml:*, fields:* (8 commands)
├── iteration_commands.py    # iter:*, plan:* (4 commands)
└── workflow_commands.py     # workflows:* (1 command)
```

## Phases

### Phase 1: 🚀 Setup Module Structure
- [x] Create `builder/core/cli/` directory
- [x] Create base module with common utilities
- [x] Set up module imports and CLI group registration

### Phase 2: 📝 Extract Document Commands
- [x] Move `doc:*`, `adr:*`, `master:*` commands to `document_commands.py`
- [x] Extract shared document utilities
- [x] Test document commands functionality

### Phase 3: 🧠 Extract Context Commands  
- [x] Move `ctx:*`, `context:*` commands to `context_commands.py`
- [x] Extract shared context utilities
- [x] Test context commands functionality

### Phase 4: 🔍 Extract Discovery Commands
- [x] Move `discover:*` commands to `discovery_commands.py`
- [x] Extract shared discovery utilities
- [x] Test discovery commands functionality

### Phase 5: 🤖 Extract Agent Commands
- [x] Move `agent:*` commands to `agent_commands.py`
- [x] Extract shared agent utilities
- [x] Test agent commands functionality

### Phase 6: 🎭 Extract Orchestrator Commands
- [x] Move `orchestrator:*` commands to `orchestrator_commands.py`
- [x] Extract shared orchestrator utilities
- [x] Test orchestrator commands functionality

### Phase 7: 📊 Extract Evaluation Commands
- [x] Move `eval:*`, `rules:*` commands to `evaluation_commands.py`
- [x] Extract shared evaluation utilities
- [x] Test evaluation commands functionality

### Phase 8: 🛠️ Extract Utility Commands
- [x] Move `commands:*`, `cleanup:*`, `yaml:*`, `fields:*` commands to `utility_commands.py`
- [x] Extract shared utility functions
- [x] Test utility commands functionality

### Phase 9: 🔄 Extract Iteration Commands
- [x] Move `iter:*`, `plan:*` commands to `iteration_commands.py`
- [x] Extract shared iteration utilities
- [x] Test iteration commands functionality

### Phase 10: ⚙️ Extract Workflow Commands
- [ ] Move `workflows:*` commands to `workflow_commands.py`
- [ ] Extract shared workflow utilities
- [ ] Test workflow commands functionality

### Phase 11: 🧹 Cleanup and Testing
- [ ] Remove original `cli.py` file
- [ ] Update imports throughout codebase
- [ ] Run comprehensive tests
- [ ] Update documentation

### Phase 12: 📚 Documentation
- [ ] Update CLI documentation
- [ ] Create module documentation
- [ ] Update developer guidelines

## Acceptance Criteria
- [ ] All 61 CLI commands work exactly as before
- [ ] Code is organized into logical modules
- [ ] No functionality is lost or changed
- [ ] All tests pass
- [ ] Documentation is updated

## Benefits
- **Maintainability**: Easier to find and modify specific command groups
- **Readability**: Smaller, focused files are easier to understand
- **Collaboration**: Multiple developers can work on different command groups
- **Testing**: Easier to test individual command groups
- **Extensibility**: Easier to add new commands to appropriate modules

## Implementation Notes
- Use Click groups to organize commands by category
- Extract common utilities to base module
- Maintain backward compatibility
- Follow existing code patterns and conventions
