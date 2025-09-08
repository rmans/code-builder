# CLI Architecture Documentation

## Overview

The Code Builder CLI has been refactored from a monolithic 7,612-line file into a clean, modular architecture. This document describes the new structure, how to use it, and how to extend it.

## Architecture

### Modular Structure

The CLI is now organized into focused modules based on command categories:

```
builder/core/cli/
├── __init__.py              # Package initialization and command registration
├── __main__.py              # Entry point for `python -m builder.core.cli`
├── base.py                  # Main CLI group and common utilities
├── document_commands.py     # Document management commands (8 commands)
├── context_commands.py      # Context building commands (12 commands)
├── discovery_commands.py    # Discovery and analysis commands (6 commands)
├── agent_commands.py        # Agent management commands (4 commands)
├── orchestrator_commands.py # Task orchestration commands (13 commands)
├── evaluation_commands.py   # Evaluation and rules commands (5 commands)
├── utility_commands.py      # Utility and maintenance commands (7 commands)
├── iteration_commands.py    # Iteration and planning commands (5 commands)
└── workflow_commands.py     # Workflow validation commands (1 command)
```

### Main Entry Point

The main `builder/core/cli.py` file is now a minimal 14-line entry point:

```python
#!/usr/bin/env python3
"""
Code Builder CLI - Modular Entry Point

This file serves as the main entry point for the Code Builder CLI.
All commands have been extracted to modular files in the cli/ directory.
"""

# Import the main CLI group from the modular structure
from .cli.base import cli

# Make the CLI available as the main entry point
if __name__ == '__main__':
    cli()
```

## Command Categories

### 📝 Document Commands (`document_commands.py`)
- `adr:new` - Create new Architecture Decision Records
- `doc:new` - Create new documents
- `doc:index` - Generate documentation index
- `doc:set-links` - Set front-matter links
- `doc:check` - Validate docs front-matter
- `doc:fix-master` - Fix master files
- `doc:abc` - Manage ABC iteration
- `master:sync` - Synchronize master index files

### 🧠 Context Commands (`context_commands.py`)
- `ctx:build` - Build context package for a target path
- `context:scan` - Scan project and build context graph
- `ctx:build-enhanced` - Enhanced context building
- `ctx:diff` - Compare context packages
- `ctx:explain` - Explain context package
- `ctx:validate` - Validate context package
- `ctx:pack` - Pack context data
- `ctx:trace` - Trace context usage
- `ctx:graph:build` - Build context graph
- `ctx:graph:stats` - Show context graph statistics
- `ctx:select` - Select context for target
- `ctx:budget` - Calculate context budget

### 🔍 Discovery Commands (`discovery_commands.py`)
- `discover:new` - Create a new discovery context
- `discover:analyze` - Analyze codebase using discovery engine
- `discover:validate` - Validate discovery context file
- `discover:refresh` - Refresh discovery context for PRD
- `discover:scan` - Scan project for discovery opportunities
- `discover:regenerate` - Regenerate discovery contexts

### 🤖 Agent Commands (`agent_commands.py`)
- `agent:start` - Start a new agent session
- `agent:stop` - Stop an agent session
- `agent:list` - List agent sessions
- `agent:cleanup` - Clean up old and timed-out agent sessions

### 🎭 Orchestrator Commands (`orchestrator_commands.py`)
- `orchestrator:add-task` - Add a new task to the orchestrator
- `orchestrator:add-agent` - Add a new agent to the orchestrator
- `orchestrator:status` - Show orchestrator status and task information
- `orchestrator:run` - Run the orchestrator to execute tasks
- `orchestrator:execution-order` - Show the optimal execution order for tasks
- `orchestrator:reset` - Reset the orchestrator state
- `orchestrator:load-tasks` - Load tasks from task files
- `orchestrator:execute-tasks` - Execute tasks from task files
- `orchestrator:create-task-template` - Create a task template
- `orchestrator:multi-agent` - Launch multi-agent execution
- `orchestrator:add-task-abc` - Add ABC iteration task
- `orchestrator:run-abc` - Run ABC iteration orchestration
- `orchestrator:abc-status` - Show ABC iteration status

### 📊 Evaluation Commands (`evaluation_commands.py`)
- `rules:show` - Show merged rules and guardrails
- `rules:check` - Check rules compliance using guardrails
- `eval:objective` - Run objective evaluation on an artifact
- `eval:prepare` - Prepare evaluation prompt for Cursor
- `eval:complete` - Complete evaluation by blending objective and subjective scores

### 🛠️ Utility Commands (`utility_commands.py`)
- `commands:list` - List available commands from cb_docs/commands/
- `commands:show` - Show detailed information about a specific command
- `commands:refresh` - Refresh commands from templates and sync to cb_docs/commands/
- `commands:sync` - Sync commands with the rule merger
- `cleanup:artifacts` - Clean up test/example artifacts outside of designated directories
- `yaml:check` - Check for Python code issues in YAML files
- `fields:check` - Check for field name consistency issues

### 🔄 Iteration Commands (`iteration_commands.py`)
- `plan:sync` - Sync planning data and build context
- `plan:auto` - Infer feature from builder/feature_map.json for PATH and build context
- `iter:run` - Run ABC iteration on target path
- `iter:cursor` - Run iterative ABC evaluation with Cursor
- `iter:finish` - Complete ABC iteration by selecting winner

### ⚙️ Workflow Commands (`workflow_commands.py`)
- `workflows:validate` - Validate GitHub Actions workflow files

## Usage

### Running the CLI

```bash
# Run the main CLI
python -m builder.core.cli --help

# Run specific commands
python -m builder.core.cli commands:list
python -m builder.core.cli ctx:build src/
python -m builder.core.cli eval:objective file.py
```

### Command Help

```bash
# Get help for the main CLI
python -m builder.core.cli --help

# Get help for a specific command
python -m builder.core.cli commands:list --help
python -m builder.core.cli ctx:build --help
```

## Development

### Adding New Commands

1. **Choose the appropriate module** based on command category
2. **Add the command function** with proper Click decorators
3. **Import the command** in the module's `__init__.py` if needed
4. **Test the command** to ensure it works correctly

### Example: Adding a New Document Command

```python
# In builder/core/cli/document_commands.py

@cli.command("doc:new-feature")
@click.argument("name")
@click.option("--template", default="default")
def doc_new_feature(name, template):
    """Create a new feature document."""
    # Implementation here
    click.echo(f"Created feature document: {name}")
```

### Module Structure

Each module follows this pattern:

```python
#!/usr/bin/env python3
"""
Module Name

Brief description of the module's purpose.
"""

import click
from .base import cli, get_project_root

# Helper functions
def _helper_function():
    """Helper function for this module."""
    pass

# Command definitions
@cli.command("command:name")
@click.argument("arg")
@click.option("--option", default="value")
def command_name(arg, option):
    """Command description."""
    # Implementation
    pass
```

## Benefits

### Maintainability
- **Focused Modules**: Each module handles a specific category of commands
- **Smaller Files**: Easier to navigate and understand
- **Clear Separation**: Commands are logically grouped by functionality

### Collaboration
- **Parallel Development**: Multiple developers can work on different command categories
- **Reduced Conflicts**: Changes to one category don't affect others
- **Easier Reviews**: Smaller, focused changes are easier to review

### Testing
- **Isolated Testing**: Each module can be tested independently
- **Focused Test Suites**: Tests are organized by command category
- **Easier Debugging**: Issues are easier to locate and fix

### Extensibility
- **Easy Addition**: New commands can be added to appropriate modules
- **Modular Imports**: Only necessary modules are loaded
- **Clear Dependencies**: Dependencies are explicit and manageable

## Migration Notes

### From Monolithic to Modular

The refactoring maintains 100% backward compatibility:

- **Same Command Names**: All commands work exactly as before
- **Same Options**: All command options and arguments are preserved
- **Same Behavior**: Command behavior is identical to the original
- **Same Entry Point**: `python -m builder.core.cli` works as before

### File Size Reduction

- **Before**: 7,612 lines in single file
- **After**: 14 lines in main file + 2,634 lines across 10 modules
- **Reduction**: 99.8% reduction in main file size
- **Improvement**: Much more maintainable and organized

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are properly imported in `__init__.py`
2. **Command Not Found**: Check that the command is registered in the correct module
3. **Dependency Issues**: Verify that required utility modules exist

### Debugging

```bash
# Test individual modules
python -c "from builder.core.cli.document_commands import *; print('Document commands loaded')"

# Test specific commands
python -m builder.core.cli command:name --help
```

## Future Enhancements

### Planned Improvements
- **Plugin System**: Allow external command modules
- **Command Discovery**: Automatic discovery of new command modules
- **Enhanced Testing**: Comprehensive test suite for all modules
- **Performance Optimization**: Lazy loading of command modules

### Extension Points
- **Custom Modules**: Add new command categories
- **Middleware**: Add command preprocessing/postprocessing
- **Hooks**: Add lifecycle hooks for commands
- **Metrics**: Add command usage tracking

---

This modular architecture provides a solid foundation for the Code Builder CLI, making it more maintainable, extensible, and easier to work with while preserving all existing functionality.
