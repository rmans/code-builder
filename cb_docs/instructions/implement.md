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

### Next Steps

After scaffolding is complete:
1. **Command System**: Implement `commands:list`, `commands:refresh`, etc.
2. **Rule Integration**: Set up rule merging with project rules
3. **Template System**: Create command templates
4. **State Management**: Implement state updates and persistence
5. **Path Translation**: Use OverlayPaths for all new features
