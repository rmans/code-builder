# Rule: Modular Architecture Enforcement

## Description
This rule enforces modular code architecture to prevent monolithic files and maintain clean, maintainable code organization. It applies to all code files, especially CLI commands, utility functions, and feature modules.

## Guidelines

### 1. File Size Limits
- **Maximum File Size**: No single Python file should exceed 500 lines
- **Recommended Size**: Keep files under 300 lines for optimal maintainability
- **Exception**: Configuration files, data files, and generated code may exceed limits with justification

### 2. Single Responsibility Principle
- **One Purpose Per File**: Each file should have a single, well-defined responsibility
- **Clear Naming**: File names should clearly indicate their purpose
- **Focused Scope**: Avoid mixing unrelated functionality in the same file

### 3. CLI Command Organization
- **Command Categories**: Group related commands into focused modules
- **Maximum Commands Per Module**: No more than 15 commands per module
- **Logical Grouping**: Commands should be grouped by functionality, not alphabetically
- **Shared Utilities**: Extract common functionality to base utilities

### 4. Module Structure
- **Clear Hierarchy**: Use clear directory structure with logical groupings
- **Import Organization**: Group imports logically (standard library, third-party, local)
- **Documentation**: Each module must have clear docstrings and purpose statements

### 5. Function and Class Limits
- **Function Length**: No function should exceed 50 lines
- **Class Length**: No class should exceed 200 lines
- **Method Count**: No class should have more than 20 methods
- **Parameter Count**: Functions should not have more than 5 parameters

### 6. Dependency Management
- **Minimal Dependencies**: Keep module dependencies minimal and explicit
- **Circular Dependencies**: Avoid circular imports between modules
- **Lazy Loading**: Use lazy loading for heavy dependencies when possible

## Enforcement Patterns

### Forbidden Patterns
- **Monolithic Files**: Files with more than 500 lines
- **Mixed Responsibilities**: Files that handle multiple unrelated concerns
- **Deep Nesting**: Functions with more than 4 levels of nesting
- **Long Parameter Lists**: Functions with more than 5 parameters
- **God Classes**: Classes that handle multiple unrelated responsibilities

### Required Patterns
- **Modular Structure**: Use focused modules for related functionality
- **Clear Interfaces**: Define clear interfaces between modules
- **Documentation**: Comprehensive documentation for all modules
- **Testing**: Unit tests for each module
- **Error Handling**: Proper error handling in each module

## Implementation Guidelines

### CLI Commands
```python
# ✅ Good: Focused command module
# builder/core/cli/document_commands.py
@cli.command("doc:new")
def doc_new():
    """Create new document - single responsibility"""
    pass

# ❌ Bad: Mixed responsibilities
# builder/core/cli/mixed_commands.py
@cli.command("doc:new")
def doc_new():
    """Create document"""
    pass

@cli.command("agent:start")
def agent_start():
    """Start agent - different responsibility"""
    pass
```

### Utility Functions
```python
# ✅ Good: Focused utility module
# builder/utils/document_helpers.py
def parse_frontmatter(content):
    """Parse document frontmatter - single purpose"""
    pass

# ❌ Bad: Mixed utilities
# builder/utils/helpers.py
def parse_frontmatter(content):
    """Parse frontmatter"""
    pass

def validate_yaml(content):
    """Validate YAML - different purpose"""
    pass

def send_email(recipient, subject):
    """Send email - completely different purpose"""
    pass
```

### Module Organization
```python
# ✅ Good: Clear module structure
builder/
├── core/
│   ├── cli/
│   │   ├── base.py              # CLI base and utilities
│   │   ├── document_commands.py # Document commands
│   │   └── context_commands.py  # Context commands
│   └── utils/
│       ├── document_helpers.py  # Document utilities
│       └── context_helpers.py   # Context utilities

# ❌ Bad: Monolithic structure
builder/
├── core/
│   ├── cli.py                   # 5000+ lines
│   └── utils.py                 # 2000+ lines
```

## Monitoring and Enforcement

### Automated Checks
- **File Size Monitoring**: Automated checks for file size limits
- **Import Analysis**: Check for circular dependencies
- **Complexity Metrics**: Monitor cyclomatic complexity
- **Documentation Coverage**: Ensure all modules are documented

### Code Review Guidelines
- **Size Review**: Check file sizes during code review
- **Responsibility Review**: Verify single responsibility principle
- **Dependency Review**: Check for unnecessary dependencies
- **Documentation Review**: Ensure proper documentation

### Refactoring Triggers
- **File Size**: Refactor when files exceed 400 lines
- **Complexity**: Refactor when functions exceed 30 lines
- **Dependencies**: Refactor when modules have too many dependencies
- **Maintenance**: Refactor when modules become hard to maintain

## Benefits

### Maintainability
- **Easier Navigation**: Smaller files are easier to find and understand
- **Focused Changes**: Changes are isolated to specific modules
- **Reduced Risk**: Smaller changes have lower risk of breaking other functionality

### Collaboration
- **Parallel Development**: Multiple developers can work on different modules
- **Reduced Conflicts**: Smaller files reduce merge conflicts
- **Clear Ownership**: Clear module boundaries for code ownership

### Testing
- **Isolated Testing**: Each module can be tested independently
- **Focused Test Suites**: Tests are organized by module
- **Easier Debugging**: Issues are easier to locate and fix

### Performance
- **Lazy Loading**: Only load necessary modules
- **Reduced Memory**: Smaller modules use less memory
- **Faster Startup**: Faster application startup times

## Examples

### Good Modular Structure
```python
# builder/core/cli/document_commands.py (200 lines)
"""
Document Commands Module

Handles all document-related CLI commands including creation,
indexing, validation, and synchronization.
"""

import click
from .base import cli
from ..utils.document_helpers import parse_frontmatter, validate_document

@cli.command("doc:new")
def doc_new():
    """Create new document."""
    pass

@cli.command("doc:index")
def doc_index():
    """Generate document index."""
    pass
```

### Bad Monolithic Structure
```python
# builder/core/cli.py (5000+ lines)
"""
Everything in one file - DON'T DO THIS
"""

import click
# ... 100+ imports

# ... 50+ command functions
# ... 100+ helper functions
# ... Mixed responsibilities
```

## Migration Strategy

### When to Refactor
- **File Size**: When files exceed 400 lines
- **Complexity**: When functions exceed 30 lines
- **Maintenance**: When files become hard to maintain
- **Collaboration**: When multiple developers work on same file

### How to Refactor
1. **Identify Boundaries**: Find logical separation points
2. **Extract Modules**: Create focused modules for related functionality
3. **Update Imports**: Update all import statements
4. **Test Thoroughly**: Ensure all functionality still works
5. **Update Documentation**: Update all documentation

### Gradual Migration
- **Phase 1**: Extract largest modules first
- **Phase 2**: Extract remaining large functions
- **Phase 3**: Optimize and clean up
- **Phase 4**: Add monitoring and enforcement

## Conclusion

Modular architecture is essential for maintainable, scalable code. This rule ensures that the codebase remains clean, organized, and easy to work with as it grows. By following these guidelines, we can prevent the accumulation of technical debt and maintain high code quality.

Remember: **Small, focused modules are better than large, monolithic files.**
