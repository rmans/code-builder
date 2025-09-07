---
description: Define how Code Builder rules interact with existing project rules
globs: builder/**/*.py,scripts/**/*.sh,cb_docs/**/*.md
alwaysApply: true
---

# Rule Interaction Strategy

## Overview
When Code Builder is installed on a project that already has its own rules, we need a clear strategy to prevent conflicts and ensure proper rule precedence.

## Current Architecture Issues

### ❌ Problem: Rule Collision
The current system has a fundamental conflict:
- **Code Builder rules**: Loaded from `cb_docs/rules/` (overlay mode)
- **Project rules**: May exist in `docs/rules/`, `.cursor/rules/`, or other locations
- **Cursor rules**: `.cursorrules` file in project root
- **Installer copies**: `.cursor/rules/` from Code Builder to `.cb/.cursor/rules/`

### ❌ Problem: Double Rule Loading
- Code Builder loads from `cb_docs/rules/`
- Installer copies `.cursor/rules/` to `.cb/.cursor/rules/`
- This creates duplicate rule sources

## Proposed Solution: Rule Layering Strategy

### 1. **Rule Source Hierarchy** (Highest to Lowest Priority)

```
1. Project-specific rules (highest priority)
   ├── .cursor/rules/ (if exists in project)
   ├── docs/rules/ (if exists in project)
   └── .cursorrules (project root)

2. Code Builder rules (medium priority)
   ├── cb_docs/rules/feature/*.md
   ├── cb_docs/rules/stack/*.md
   └── cb_docs/rules/*.md

3. Code Builder guardrails (lowest priority)
   └── cb_docs/rules/guardrails.json
```

### 2. **Rule Loading Strategy**

#### **Standalone Mode** (Development)
```python
# Load rules in this order:
1. Project rules from docs/rules/ or .cursor/rules/
2. Code Builder rules from cb_docs/rules/
3. Merge with conflict detection
4. Apply Code Builder guardrails as warnings only
```

#### **Overlay Mode** (Installed)
```python
# Load rules in this order:
1. Host project rules (if accessible)
2. Code Builder rules from cb_docs/rules/
3. Merge with conflict detection
4. Apply Code Builder guardrails as warnings only
```

### 3. **Conflict Resolution**

#### **Rule Conflicts**
- **High severity**: Contradictory patterns (e.g., "use tabs" vs "use spaces")
- **Medium severity**: Overlapping patterns with different messages
- **Low severity**: Duplicate patterns with same message

#### **Resolution Strategy**
1. **Project rules win** for high-severity conflicts
2. **Code Builder rules win** for medium-severity conflicts
3. **Merge** for low-severity conflicts
4. **Log conflicts** for user review

### 4. **Implementation Changes Needed**

#### **A. Update Rule Loader**
```python
def load_rules_with_project_precedence(feature=None, stacks=None):
    """Load rules with project precedence over Code Builder rules."""
    
    # 1. Load project rules first (highest priority)
    project_rules = load_project_rules()
    
    # 2. Load Code Builder rules (medium priority)
    cb_rules = load_code_builder_rules(feature, stacks)
    
    # 3. Detect and resolve conflicts
    conflicts = detect_rule_conflicts(project_rules, cb_rules)
    
    # 4. Merge with project precedence
    merged_rules = merge_rules_with_precedence(project_rules, cb_rules, conflicts)
    
    return merged_rules
```

#### **B. Update Installer**
```bash
# DON'T copy .cursor/rules/ to .cb/.cursor/rules/
# Instead, create a rule merger that respects project rules

# Create rule merger script
cat > .cb/bin/merge-rules << 'EOF'
#!/bin/bash
# Merge project rules with Code Builder rules
python3 -c "
from builder.core.rule_merger import merge_project_and_cb_rules
merged = merge_project_and_cb_rules()
print(merged)
" > .cb/.cursor/rules/merged_rules.md
EOF
```

#### **C. Create Rule Merger**
```python
class ProjectRuleMerger:
    """Merges project rules with Code Builder rules."""
    
    def merge_project_and_cb_rules(self):
        """Merge rules with project precedence."""
        # 1. Detect project rule sources
        project_sources = self.detect_project_rule_sources()
        
        # 2. Load Code Builder rules
        cb_sources = self.load_cb_rules()
        
        # 3. Merge with conflict resolution
        return self.merge_with_conflict_resolution(project_sources, cb_sources)
    
    def detect_project_rule_sources(self):
        """Detect existing project rule sources."""
        sources = []
        
        # Check for .cursor/rules/
        if os.path.exists('.cursor/rules/'):
            sources.extend(self.load_cursor_rules())
        
        # Check for docs/rules/
        if os.path.exists('docs/rules/'):
            sources.extend(self.load_docs_rules())
        
        # Check for .cursorrules
        if os.path.exists('.cursorrules'):
            sources.append(self.load_cursorrules())
        
        return sources
```

### 5. **User Experience**

#### **Rule Discovery**
```bash
# Show rule sources and conflicts
cb rules:status
# Output:
# Project Rules: .cursor/rules/ (3 files)
# Code Builder Rules: cb_docs/rules/ (15 files)
# Conflicts: 2 medium, 1 low
# Active Rules: 18 total
```

#### **Rule Override**
```bash
# Allow users to override Code Builder rules
cb rules:override --project-priority
cb rules:override --cb-priority
cb rules:override --custom-merge
```

### 6. **Migration Strategy**

#### **Phase 1: Detection**
- Detect existing project rules
- Warn about potential conflicts
- Provide migration guidance

#### **Phase 2: Integration**
- Implement rule merger
- Update installer to not copy rules
- Add conflict resolution

#### **Phase 3: User Control**
- Add rule override commands
- Provide rule management UI
- Document best practices

## Benefits

1. **No Rule Conflicts**: Project rules take precedence
2. **Code Builder Value**: Still provides guardrails and best practices
3. **User Control**: Can override precedence if needed
4. **Clean Installation**: No duplicate rule files
5. **Backward Compatibility**: Existing projects continue to work

## Implementation Priority

1. **High**: Update rule loader to detect project rules
2. **High**: Implement conflict detection
3. **Medium**: Create rule merger
4. **Medium**: Update installer
5. **Low**: Add user override commands
