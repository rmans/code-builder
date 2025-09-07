# Implementation Guide

## Installation Scaffolding

### Overview
The Code Builder overlay system requires specific directory structures and state files to function properly. This section covers the scaffolding process that creates the necessary infrastructure.

### Required Directories

#### Core Overlay Directories
- **`.cb/`** - Main overlay directory (created by installer only)
  - **`.cb/commands/`** - Generated command files
  - **`.cb/instructions/`** - Runtime instructions and status
  - **`.cb/engine/`** - Overlay engine components
    - **`.cb/engine/templates/commands/`** - Command templates
  - **`.cb/cache/`** - Runtime cache
    - **`.cb/cache/command_state/`** - Command state and metrics

#### Cursor Integration
- **`.cursor/rules/`** - Cursor rules directory (for rule merging)

### State Files

#### Command State (`state.json`)
```json
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "project_state": {
    "initialized": false,
    "discovered": false,
    "analyzed": false,
    "planned": false,
    "context_created": false
  },
  "command_history": [],
  "active_tasks": [],
  "completed_tasks": [],
  "cache_metadata": {
    "last_cleanup": null,
    "size_bytes": 0,
    "file_count": 0
  }
}
```

#### Metrics (`metrics.json`)
```json
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "command_metrics": {
    "total_commands_run": 0,
    "successful_commands": 0,
    "failed_commands": 0,
    "average_execution_time_ms": 0,
    "most_used_commands": []
  },
  "discovery_metrics": {
    "time_to_first_rules": null,
    "command_discovery_rate": 0.0,
    "execution_success_rate": 0.0
  },
  "performance_metrics": {
    "cache_hit_rate": 0.0,
    "average_response_time_ms": 0,
    "memory_usage_mb": 0
  },
  "session_metrics": {
    "current_session_start": null,
    "total_sessions": 0,
    "average_session_duration_minutes": 0
  }
}
```

### Directory Permissions

All directories should have standard permissions (755):
```bash
drwxr-xr-x  # Owner: read/write/execute, Group: read/execute, Other: read/execute
```

### Git Integration

The `.cb/` directory is automatically ignored by git:
```gitignore
.cb/
.cb/*
```

### Validation

#### Directory Structure Check
```bash
# Verify all required directories exist
find .cb -type d | sort
find .cursor -type d | sort
```

#### State File Validation
```bash
# Verify JSON files are valid
python3 -c "import json; json.load(open('.cb/cache/command_state/state.json'))"
python3 -c "import json; json.load(open('.cb/cache/command_state/metrics.json'))"
```

#### CLI Functionality
```bash
# Test basic CLI functionality
python3 -m builder.core.cli rules:show
```

### Troubleshooting

#### Missing Directories
If directories are missing, recreate them:
```bash
mkdir -p .cb/commands .cb/instructions .cb/engine/templates/commands .cb/cache/command_state .cursor/rules
```

#### Invalid State Files
If state files are corrupted, recreate them with the minimal schema above.

#### Permission Issues
Ensure proper permissions:
```bash
chmod -R 755 .cb/ .cursor/
```

### Path Translation Layer

The Code Builder uses a dual-mode path resolution system that works in both overlay and standalone modes. This ensures consistent behavior regardless of how the system is deployed.

#### OverlayPaths Usage

```python
from .cb.engine.builder.overlay.paths import OverlayPaths, overlay_paths

# Use global instance
paths = overlay_paths

# Or create new instance
paths = OverlayPaths()

# Get mode information
if paths.is_overlay_mode():
    print("Running in overlay mode")
else:
    print("Running in standalone mode")

# Get common paths
root = paths.cb_root()
docs_dir = paths.cb_docs_dir()
rules_dir = paths.cursor_rules_dir()
tasks_index = paths.tasks_index()
logs_dir = paths.logs_dir()
cache_dir = paths.cache_dir()

# Ensure all directories exist
paths.ensure_directories()

# Validate configuration
if paths.validate():
    print("All paths are valid and accessible")
```

#### Convenience Functions

```python
from .cb.engine.builder.overlay.paths import (
    cb_root, cursor_rules_dir, cb_docs_dir, 
    tasks_index, logs_dir
)

# Direct access to common paths
root = cb_root()
docs = cb_docs_dir()
rules = cursor_rules_dir()
```

#### Validation

Test the path resolution system:

```bash
# Validate OverlayPaths configuration
python3 .cb/engine/builder/overlay/paths.py validate
```

### Install Hook - setup_commands()

The installer now includes a `setup_commands()` function that:

1. **Creates Command Files**: Generates `analyze-project.md` and `plan-project.md` in `.cb/commands/`
2. **Rule Merger**: Creates `.cb/bin/merge-rules` script that:
   - Detects existing project rules (`.cursor/rules/`, `docs/rules/`, `.cursorrules`)
   - Merges project rules with Code Builder rules (project rules have higher priority)
   - Creates `merged_rules.md` with proper precedence
3. **@rules/ Files**: Generates individual `@rules/` files for each command
4. **Idempotent**: Safe to run multiple times

**Usage:**
```bash
# The function runs automatically during installation
bash scripts/install.sh

# Or run the rule merger manually
.cb/bin/merge-rules
```

**Output:**
- `.cb/commands/*.md` - Command definitions
- `.cb/.cursor/rules/` - @rules/ files and merged rules
- `.cb/bin/merge-rules` - Rule merger script

### Command Utilities

The CLI now includes a comprehensive `commands:*` family for managing command definitions:

#### Available Commands
- **`cb commands:list`** - List all available commands with filtering and multiple output formats
- **`cb commands:show <name>`** - Show detailed information about a specific command
- **`cb commands:refresh`** - Refresh commands from templates and sync to `.cb/commands/`
- **`cb commands:sync`** - Sync commands with rule merger and update `@rules/` files

#### Features
- **Multiple Output Formats**: Table (default), JSON, YAML for `commands:list`
- **Status Filtering**: Filter by `active`, `inactive`, or `all` commands
- **Detailed Views**: Full, metadata-only, or usage-only views for `commands:show`
- **Template Management**: Copy from `.cb/engine/templates/commands/` to `.cb/commands/`
- **Rule Integration**: Automatically sync with rule merger for `@rules/` files
- **Error Handling**: Consistent error codes and helpful messages

#### Usage Examples
```bash
# List all active commands in table format
cb commands:list

# List commands in JSON format
cb commands:list --format json

# Show detailed information about a command
cb commands:show analyze-project

# Show only usage information
cb commands:show analyze-project --format usage

# Refresh commands from templates
cb commands:refresh --force

# Sync with rule merger
cb commands:sync
```

#### Command File Structure
Commands are defined in `.cb/commands/*.md` files with YAML frontmatter:
```yaml
---
id: command-name
title: Command Title
description: Brief description
status: active
created: 2025-01-15
updated: 2025-01-15
owner: system
domain: discovery
priority: 8
agent_type: backend
dependencies: []
tags: [discovery, analysis, project]
---

# Command: Command Title

## Description
Detailed description...

## Usage
```bash
cb command-name
```

## Examples
```bash
cb command-name --option value
```
```

## Simple Commands

### Overview
Simple commands provide easy-to-use aliases for common Code Builder operations. These commands are implemented in `builder/overlay/simple_router.py` and provide a simplified interface to the full command system.

### Available Simple Commands

#### `cb analyze`
Analyze project structure and generate discovery report.

**Usage:**
```bash
cb analyze [OPTIONS]
```

**Options:**
- `--depth INTEGER` - Analysis depth (default: 3)
- `--ignore TEXT` - Ignore files matching pattern
- `--ci` - Non-interactive mode for CI/CD

**Examples:**
```bash
# Basic analysis
cb analyze

# Deep analysis with custom ignore
cb analyze --depth 5 --ignore "node_modules,dist"

# CI mode
cb analyze --ci
```

**Outputs:**
- `cb_docs/discovery/analysis.json` - Detailed project analysis
- `cb_docs/discovery/summary.md` - Human-readable summary

#### `cb plan`
Create project plan through guided interview.

**Usage:**
```bash
cb plan [OPTIONS]
```

**Options:**
- `--persona [dev|pm|ai]` - Interview persona (default: dev)
- `--noninteractive` - Use defaults instead of prompts

### Implementation Details

#### Simple Router Architecture
The simple router (`builder/overlay/simple_router.py`) provides:

1. **Command Aliases**: Maps short commands to full implementations
2. **Parameter Mapping**: Converts simple parameters to complex command parameters
3. **Error Handling**: Graceful fallback when underlying commands fail
4. **Dual Mode Support**: Works in both overlay and standalone modes

#### Command Registration
Simple commands are registered with the main CLI through the `@cli.command` decorator:

```python
@cli.command("analyze")
@click.option("--depth", type=int, default=3)
@click.option("--ignore", help="Ignore files matching pattern")
@click.option("--ci", is_flag=True)
def analyze_command(depth, ignore, ci):
    # Implementation
```

#### @rules/ Integration
Simple commands automatically generate `@rules/` files for Cursor agent integration:

- **Command-specific rules**: `@rules/analyze-project`
- **Project status rules**: `@rules/project-status`

#### Dual Mode Support
Simple commands work in both modes:

- **Overlay Mode**: When `.cb/` directory exists
- **Standalone Mode**: When running from any directory

### Usage Examples

#### Basic Project Analysis
```bash
# Analyze current project
cb analyze

# Analyze with specific depth
cb analyze --depth 5

# Analyze in CI mode
cb analyze --ci
```

#### Project Planning
```bash
# Interactive planning
cb plan

# Developer persona planning
cb plan --persona dev

# Non-interactive planning
cb plan --noninteractive
```

#### Agent Integration
```bash
# Get recommended command for agents
cb agent:get-command

# Create @rules/ files
cb agent:integrate
```

### Error Handling

Simple commands provide robust error handling:

1. **Import Errors**: Clear messages when underlying commands are unavailable
2. **Parameter Errors**: Validation and helpful error messages
3. **File System Errors**: Graceful handling of permission and path issues
4. **Fallback Suggestions**: Alternative commands when primary commands fail

### Next Steps

After scaffolding is complete:
1. **Command System**: Implement `commands:list`, `commands:refresh`, etc. ✅
2. **Rule Integration**: Set up rule merging with project rules ✅
3. **Template System**: Create command templates ✅
4. **State Management**: Implement state updates and persistence
5. **Path Translation**: Use OverlayPaths for all new features
