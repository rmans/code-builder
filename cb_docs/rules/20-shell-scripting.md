---
id: shell-scripting
title: Shell Scripting Best Practices
description: Rules for writing robust shell scripts
status: active
created: 2025-01-15
updated: 2025-01-15
owner: platform-agent
domain: development
priority: 7
agent_type: backend
dependencies: []
tags: [shell, scripting, best-practices]
---

# Shell Scripting Best Practices

## Heredoc Rules
- **Never use nested heredocs** inside functions
- **Always verify heredoc closure** with `bash -n` before proceeding
- **Use unique EOF markers** for nested heredocs (e.g., `EOF`, `MERGED_EOF`)
- **Count opening and closing markers** to ensure they match
- **For complex content**, use external files or echo commands instead

## File Operations Rules
- **Always create directories** before writing files: `mkdir -p dir/`
- **Verify directory exists** before file operations
- **Use absolute paths** when possible to avoid path issues
- **Check file permissions** after creation

## Debugging Rules
- **Maximum 3 attempts** to fix syntax errors before asking for help
- **Clean up temporary files** immediately after debugging
- **Use `bash -n`** for syntax checking before creating new files
- **Test incrementally** - fix one issue at a time
- **Document the root cause** when issues are resolved

## Function Design Rules
- **Keep functions simple** - avoid complex logic inside functions
- **Use external scripts** for complex operations
- **Make functions idempotent** - safe to run multiple times
- **Echo progress messages** for long-running operations

## Error Handling Rules
- **Use `set -e`** to exit on errors
- **Redirect stderr** to `/dev/null` for non-critical operations
- **Provide fallback mechanisms** for critical operations
- **Test error conditions** during development

## Examples

### ❌ Bad: Nested Heredocs
```bash
setup_commands() {
    cat > file.md << 'EOF'
    content with heredoc
    cat > nested.md << 'NESTED_EOF'
    nested content
    NESTED_EOF
EOF
}
```

### ✅ Good: Simple Heredocs
```bash
setup_commands() {
    cat > file.md << 'EOF'
    simple content
EOF
}
```

### ✅ Good: External Files
```bash
setup_commands() {
    # Create content in external file
    create_command_file "analyze-project.md"
}
```

### ❌ Bad: Missing Directory
```bash
setup_commands() {
    cat > .cb/commands/file.md << 'EOF'
    content
EOF
}
```

### ✅ Good: Create Directory First
```bash
setup_commands() {
    mkdir -p .cb/commands
    cat > .cb/commands/file.md << 'EOF'
    content
EOF
}
```

## Enforcement
- **Lint check**: Verify no nested heredocs in shell scripts
- **Syntax check**: Run `bash -n` on all shell scripts
- **Directory check**: Verify directories exist before file operations
- **Cleanup check**: Ensure no temporary files remain after operations
