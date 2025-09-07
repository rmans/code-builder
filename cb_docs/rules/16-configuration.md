---
description: Avoid hardcoding paths and configuration values
globs: builder/**/*.py,src/**/*.ts,tests/**/*.ts
alwaysApply: true
---
# Configuration Best Practices

## Centralized Configuration
- **Always use `builder.config.settings.get_config()`** to retrieve configuration values.
- **Never hardcode file paths** (e.g., `docs/`, `cb_docs/`, `builder/cache`) directly in code.
- **Never hardcode configuration values** (e.g., `0.7`, `50.0`, `"127.0.0.1"`) directly in code.
- **Always use `config.get_effective_docs_dir()`, `config.get_effective_cache_dir()`, etc.** for dynamic paths.
- **Always use configuration functions** (e.g., `get_ai_default_temp()`, `get_eval_default_score()`) for values.
- **Define all configurable paths and values** in `builder/config/settings.py`.
- **Ensure environment variables override defaults** for overlay mode.
- **Test path resolution** in both standalone and overlay modes.

## Configuration Categories
- **AI/ML Parameters**: Temperature, top-p, weights, thresholds
- **Evaluation Settings**: Default scores, confidence thresholds, weights
- **Scoring Weights**: Title, tags, content, technology weights
- **Relevance Thresholds**: Low, medium relevance thresholds
- **Context Budget**: Percentage allocations, token factors
- **Network Settings**: Hosts, ports, timeouts, poll intervals
- **Version Information**: Schema versions, app versions

## Path Management
- **Use `OverlayPaths` class** for path resolution in overlay mode.
- **Use `get_config()` methods** for all path construction.
- **Never construct paths manually** with string concatenation.
- **Always test both modes** - standalone and overlay path resolution.

## Environment Variables
- **CB_DOCS_DIR** - Override docs directory path
- **CB_CACHE_DIR** - Override cache directory path  
- **CB_ENGINE_DIR** - Override engine directory path
- **CB_MODE** - Set to "overlay" or "standalone"

## Examples

### ❌ Bad - Hardcoded paths
```python
docs_dir = "cb_docs"
cache_dir = "builder/cache"
file_path = os.path.join("cb_docs", "rules", "guardrails.json")
```

### ✅ Good - Using configuration
```python
from builder.config.settings import get_config

config = get_config()
docs_dir = config.get_effective_docs_dir()
cache_dir = config.get_effective_cache_dir()
file_path = os.path.join(config.get_effective_docs_dir(), "rules", "guardrails.json")
```

### ✅ Good - Using OverlayPaths
```python
from builder.overlay.paths import OverlayPaths

paths = OverlayPaths()
docs_dir = paths.get_docs_dir()
cache_dir = paths.get_cache_dir()
rules_dir = paths.get_rules_dir()
```