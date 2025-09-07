---
id: cli-development
title: CLI Development Best Practices
description: Rules for developing CLI commands and utilities
status: active
created: 2025-01-15
updated: 2025-01-15
owner: platform-agent
domain: development
priority: 7
agent_type: backend
dependencies: []
tags: [cli, development, best-practices]
---

# CLI Development Best Practices

## Directory Structure Rules
- **NEVER create files in `.cb/` directory during development**
- **`.cb/` directory is installer-only** - use `cb_docs/` for development
- **Command files**: `cb_docs/commands/` (development) → `.cb/commands/` (runtime)
- **Template files**: `cb_docs/templates/commands/` (development) → `.cb/engine/templates/commands/` (runtime)
- **Always read from `cb_docs/` in CLI commands**

## Data Serialization Rules
- **Always handle date/datetime objects** in JSON serialization
- **Use custom serializers** for non-standard types
- **Test all output formats** during development
- **Convert dates to ISO strings** before JSON serialization
- **Create reusable serialization utilities** for common types

## Error Handling Rules
- **Create reusable utility functions** for common operations
- **Test error scenarios** for all output formats
- **Use consistent error handling patterns** across similar functions
- **Validate all data types** before serialization
- **Provide helpful error messages** with suggested actions

## Template Management Rules
- **Always ensure template directories exist** before operations
- **Provide fallback mechanisms** when templates are missing
- **Document template directory structure** requirements
- **Test template operations** in clean environments
- **Use installer to copy templates** from `cb_docs/` to `.cb/`

## CLI Command Rules
- **Follow consistent naming patterns**: `category:action`
- **Use Click options** for all parameters
- **Provide helpful help text** and examples
- **Return appropriate exit codes** (0 for success, 1 for error)
- **Test all command variations** and edge cases

## Examples

### ❌ Bad: Creating files in .cb/
```python
# Don't do this during development
commands_dir = Path('.cb/commands')
commands_dir.mkdir(exist_ok=True)
```

### ✅ Good: Reading from cb_docs/
```python
# Do this instead
commands_dir = Path('cb_docs/commands')
if not commands_dir.exists():
    click.echo("❌ No commands directory found. Run installer first.")
    return 1
```

### ❌ Bad: No date serialization
```python
click.echo(json.dumps(data, indent=2))
```

### ✅ Good: Proper date serialization
```python
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

click.echo(json.dumps(data, indent=2, default=json_serializer))
```

### ❌ Bad: Inconsistent error handling
```python
# Different error handling in each function
try:
    data = yaml.safe_load(content)
except yaml.YAMLError:
    click.echo("Error parsing YAML")
```

### ✅ Good: Reusable error handling
```python
def safe_yaml_load(content, error_context=""):
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        click.echo(f"❌ Error parsing YAML{error_context}: {e}")
        return None
```

## Enforcement
- **Lint check**: Verify no files created in `.cb/` during development
- **Test check**: Verify all output formats work correctly
- **Error check**: Verify consistent error handling patterns
- **Template check**: Verify template operations work in clean environments
