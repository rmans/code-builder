---
description: Prevent copying rules during installation to avoid conflicts with project rules
globs: scripts/**/*.sh,builder/**/*.py
alwaysApply: true
---

# No Rule Copying During Installation

## Overview
The installer should **NOT** copy Code Builder rules to the target project, as this creates conflicts with existing project rules.

## Current Problem
```bash
# ❌ WRONG: Current installer copies rules
cp -r .cursor .cb/  # This copies .cursor/rules/ to .cb/.cursor/rules/
```

This creates:
- **Duplicate rules**: Project has rules + Code Builder rules
- **Rule conflicts**: Conflicting patterns and messages
- **User confusion**: Which rules are active?
- **Maintenance issues**: Rules get out of sync

## Correct Approach

### **1. Rule Detection Strategy**
```python
# ✅ CORRECT: Detect existing project rules
def detect_project_rules():
    """Detect existing project rule sources."""
    sources = []
    
    # Check for .cursor/rules/
    if os.path.exists('.cursor/rules/'):
        sources.append('.cursor/rules/')
    
    # Check for docs/rules/
    if os.path.exists('docs/rules/'):
        sources.append('docs/rules/')
    
    # Check for .cursorrules
    if os.path.exists('.cursorrules'):
        sources.append('.cursorrules')
    
    return sources
```

### **2. Rule Merger Instead of Copying**
```python
# ✅ CORRECT: Merge rules instead of copying
def create_rule_merger():
    """Create a rule merger that respects project precedence."""
    merger_script = """
    #!/bin/bash
    # Merge project rules with Code Builder rules
    python3 -c "
    from builder.core.rule_merger import merge_project_and_cb_rules
    merged = merge_project_and_cb_rules()
    print(merged)
    " > .cb/.cursor/rules/merged_rules.md
    """
    return merger_script
```

### **3. Updated Installer Logic**
```bash
# ✅ CORRECT: Installer should NOT copy rules
# DON'T DO THIS:
# cp -r .cursor .cb/

# ✅ DO THIS INSTEAD:
# 1. Detect existing project rules
if [ -d ".cursor/rules" ] || [ -d "docs/rules" ] || [ -f ".cursorrules" ]; then
    echo "   Detected existing project rules - will merge with Code Builder rules"
    # Create rule merger instead of copying
    create_rule_merger
else
    echo "   No existing project rules - using Code Builder rules only"
    # Safe to copy rules if no conflicts
    cp -r .cursor .cb/
fi
```

## Rule Precedence

### **Project Rules (Highest Priority)**
1. `.cursor/rules/` (if exists)
2. `docs/rules/` (if exists)
3. `.cursorrules` (if exists)

### **Code Builder Rules (Medium Priority)**
1. `cb_docs/rules/feature/*.md`
2. `cb_docs/rules/stack/*.md`
3. `cb_docs/rules/*.md`

### **Code Builder Guardrails (Lowest Priority)**
1. `cb_docs/rules/guardrails.json` (warnings only)

## Implementation Requirements

### **1. Update Installer**
- Remove `cp -r .cursor .cb/` line
- Add rule detection logic
- Create rule merger instead of copying
- Add user notification about rule merging

### **2. Create Rule Merger**
- Detect existing project rules
- Load Code Builder rules
- Merge with conflict resolution
- Generate merged rules file

### **3. Add Rule Management Commands**
```bash
# Show rule sources and conflicts
cb rules:status

# Override rule precedence
cb rules:override --project-priority
cb rules:override --cb-priority

# Show conflicts
cb rules:conflicts
```

## Benefits

1. **No Rule Conflicts**: Project rules take precedence
2. **Clean Installation**: No duplicate rule files
3. **User Control**: Can override precedence if needed
4. **Maintainability**: Rules stay in sync
5. **Backward Compatibility**: Existing projects continue to work

## Enforcement

- **Guardrails**: Detect rule copying in installer
- **Code Review**: Reject PRs that copy rules
- **Testing**: Verify no rule conflicts after installation
- **Documentation**: Clear guidance on rule management

## Migration

### **Existing Installations**
- Detect existing `.cb/.cursor/rules/`
- Warn about potential conflicts
- Provide migration command: `cb rules:migrate`

### **New Installations**
- Use rule merger by default
- No rule copying
- Clear user notification about rule precedence
