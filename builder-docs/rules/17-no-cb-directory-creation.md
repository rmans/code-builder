---
description: Prevent creation of files in .cb/ directory during development
globs: builder/**/*.py,src/**/*.ts,tests/**/*.ts,scripts/**/*.sh
alwaysApply: true
---

# No .cb/ Directory Creation Rule

## Overview
The `.cb/` directory is **only** created by the installer script and should **never** be created or modified during development.

## Rule
- **NEVER create files or directories in `.cb/`** during development
- **NEVER write to `.cb/`** in any Python, TypeScript, or shell scripts
- **NEVER reference `.cb/`** as a target directory in code
- **ONLY the installer** (`scripts/install.sh`) should create `.cb/`

## What .cb/ Is For
- **Overlay environment**: Contains a copy of essential project files
- **Installation artifact**: Created when users run `bash install.sh`
- **Runtime environment**: Used by the overlay system, not development

## Correct Patterns
```python
# ✅ CORRECT: Use configuration for paths
from builder.config.settings import get_config
config = get_config()
docs_dir = config.get_effective_docs_dir()  # Points to cb_docs/ in overlay mode

# ✅ CORRECT: Use OverlayPaths for dual-mode operation
from builder.overlay.paths import OverlayPaths
paths = OverlayPaths()
rules_dir = paths.cursor_rules_dir()

# ❌ WRONG: Hardcoded .cb/ paths
output_path = ".cb/commands/new_command.md"  # DON'T DO THIS
```

## What Should Be Created Instead
- **Documentation**: `cb_docs/` (source of truth)
- **Templates**: `cb_docs/templates/`
- **Rules**: `cb_docs/rules/`
- **Cache**: Use `config.get_effective_cache_dir()`
- **Commands**: Use `config.get_effective_commands_dir()`

## Enforcement
- **Guardrails**: Detect `.cb/` in file paths
- **Code Review**: Reject PRs that create `.cb/` files
- **Testing**: Verify no `.cb/` creation in unit tests

## Exception
- **Installer only**: `scripts/install.sh` is the only script allowed to create `.cb/`
- **Overlay mode**: When running in overlay mode, use configuration paths, not hardcoded `.cb/`

## Why This Matters
- **Separation of concerns**: Development vs. installation
- **Clean builds**: No leftover `.cb/` files in development
- **Proper architecture**: Overlay system should be self-contained
- **User experience**: Users get clean installation without development artifacts
