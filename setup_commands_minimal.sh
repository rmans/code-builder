#!/bin/bash
# Minimal setup_commands function for testing

setup_commands() {
    echo "   🔧 Setting up command system..."
    
    # Create command templates directory if it doesn't exist
    mkdir -p .cb/engine/templates/commands
    
    # Create basic command files in .cb/commands/
    echo "   📝 Creating command files..."
    
    # Create analyze-project command
    echo "Creating analyze-project command..."
    cat > .cb/commands/analyze-project.md << 'EOF'
---
id: analyze-project
title: Analyze Project
description: Analyze project structure and generate discovery report
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

# Command: Analyze Project

## Description
Analyzes the current project structure, detects technologies, frameworks, and generates a comprehensive discovery report.

## Usage
```bash
cb analyze
# or
@rules/analyze-project
```

## Outputs
- `cb_docs/discovery/report.json` - Detailed project analysis
- `cb_docs/discovery/summary.md` - Human-readable summary

## Flags
- `--depth N` - Analysis depth (default: 3)
- `--ignore PATTERN` - Ignore files matching pattern
- `--ci` - Non-interactive mode for CI/CD

## Examples
```bash
# Basic analysis
cb analyze

# Deep analysis with custom ignore
cb analyze --depth 5 --ignore "node_modules,dist"

# CI mode
cb analyze --ci
```
EOF

    # Create plan-project command
    echo "Creating plan-project command..."
    cat > .cb/commands/plan-project.md << 'EOF'
---
id: plan-project
title: Plan Project
description: Create project plan through guided interview
status: active
created: 2025-01-15
updated: 2025-01-15
owner: system
domain: planning
priority: 9
agent_type: backend
dependencies: [analyze-project]
tags: [planning, interview, project]
---

# Command: Plan Project

## Description
Creates a comprehensive project plan through guided interview questions and analysis.

## Usage
```bash
cb plan
# or
@rules/plan-project
```

## Outputs
- `cb_docs/planning/interview.json` - Interview responses
- `cb_docs/planning/assumptions.md` - Documented assumptions
- `cb_docs/planning/decisions.md` - Key decisions made

## Flags
- `--persona TYPE` - Interview persona (dev|pm|ai)
- `--noninteractive` - Use defaults instead of prompts

## Examples
```bash
# Interactive planning
cb plan

# Developer persona
cb plan --persona dev

# Non-interactive with defaults
cb plan --noninteractive
```
EOF

    # Create rule merger instead of copying rules
    echo "   🔀 Creating rule merger..."
    cat > .cb/bin/merge-rules << 'EOF'
#!/bin/bash
# Rule Merger - Merges project rules with Code Builder rules

# Detect existing project rules
PROJECT_RULES=""
if [ -d ".cursor/rules" ] && [ "$(ls -A .cursor/rules 2>/dev/null)" ]; then
    PROJECT_RULES=".cursor/rules"
elif [ -d "docs/rules" ] && [ "$(ls -A docs/rules 2>/dev/null)" ]; then
    PROJECT_RULES="docs/rules"
elif [ -f ".cursorrules" ]; then
    PROJECT_RULES=".cursorrules"
fi

# Create merged rules directory
mkdir -p .cb/.cursor/rules

if [ -n "$PROJECT_RULES" ]; then
    echo "   📋 Detected project rules in: $PROJECT_RULES"
    echo "   🔀 Merging with Code Builder rules..."
    
    # Create merged rules file
    echo "# Merged Rules" > .cb/.cursor/rules/merged_rules.md
    echo "" >> .cb/.cursor/rules/merged_rules.md
    echo "## Project Rules (Higher Priority)" >> .cb/.cursor/rules/merged_rules.md
    echo "" >> .cb/.cursor/rules/merged_rules.md
    
    # Add project rules if they exist
    if [ -d "$PROJECT_RULES" ]; then
        find "$PROJECT_RULES" -name "*.md" -exec echo "### {}" \; -exec cat {} \; >> .cb/.cursor/rules/merged_rules.md
    elif [ -f "$PROJECT_RULES" ]; then
        echo "### $PROJECT_RULES" >> .cb/.cursor/rules/merged_rules.md
        cat "$PROJECT_RULES" >> .cb/.cursor/rules/merged_rules.md
    fi
    
    echo "" >> .cb/.cursor/rules/merged_rules.md
    echo "## Code Builder Rules (Lower Priority)" >> .cb/.cursor/rules/merged_rules.md
    echo "" >> .cb/.cursor/rules/merged_rules.md
    
    # Add Code Builder rules
    if [ -d "cb_docs/rules" ]; then
        find cb_docs/rules -name "*.md" -exec echo "### {}" \; -exec cat {} \; >> .cb/.cursor/rules/merged_rules.md
    fi
    
    echo "" >> .cb/.cursor/rules/merged_rules.md
    echo "## Guardrails" >> .cb/.cursor/rules/merged_rules.md
    echo "" >> .cb/.cursor/rules/merged_rules.md
    
    # Add guardrails
    if [ -f "cb_docs/rules/guardrails.json" ]; then
        echo "Guardrails configuration:" >> .cb/.cursor/rules/merged_rules.md
        cat cb_docs/rules/guardrails.json >> .cb/.cursor/rules/merged_rules.md
    fi
    
    echo "   ✅ Rules merged successfully"
else
    echo "   📋 No existing project rules detected"
    echo "   📝 Using Code Builder rules only"
    
    # Copy Code Builder rules directly
    if [ -d "cb_docs/rules" ]; then
        cp -r cb_docs/rules/* .cb/.cursor/rules/ 2>/dev/null || true
    fi
fi

# Create @rules/ files for each command
echo "   🎯 Creating @rules/ files..."
for cmd_file in .cb/commands/*.md; do
    if [ -f "$cmd_file" ]; then
        cmd_name=$(basename "$cmd_file" .md)
        echo "# @rules/$cmd_name" > ".cb/.cursor/rules/$cmd_name"
        echo "" >> ".cb/.cursor/rules/$cmd_name"
        echo "This rule provides access to the $cmd_name command." >> ".cb/.cursor/rules/$cmd_name"
        echo "" >> ".cb/.cursor/rules/$cmd_name"
        echo "## Usage" >> ".cb/.cursor/rules/$cmd_name"
        echo "\`\`\`bash" >> ".cb/.cursor/rules/$cmd_name"
        echo "@rules/$cmd_name" >> ".cb/.cursor/rules/$cmd_name"
        echo "\`\`\`" >> ".cb/.cursor/rules/$cmd_name"
        echo "" >> ".cb/.cursor/rules/$cmd_name"
        echo "## Description" >> ".cb/.cursor/rules/$cmd_name"
        echo "See .cb/commands/$cmd_name.md for full documentation." >> ".cb/.cursor/rules/$cmd_name"
        echo "" >> ".cb/.cursor/rules/$cmd_name"
        echo "## Implementation" >> ".cb/.cursor/rules/$cmd_name"
        echo "This rule is generated by the Code Builder overlay system." >> ".cb/.cursor/rules/$cmd_name"
    fi
done

chmod +x .cb/bin/merge-rules

echo "   ✅ Commands available via @rules/analyze-project, @rules/plan-project, etc."
}
