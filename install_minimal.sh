#!/bin/bash

# Code Builder Overlay Installer - Minimal Version
# Simple approach: .cb/ = project copy, cb_cb_docs/ = cb_docs/ copy

set -e

echo "🔧 Code Builder Overlay Installer"
echo "================================="

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "📋 Detected OS: $OS"

# Function to setup commands and rules
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

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run from project root."
    exit 1
fi

# Check if already installed
if [ -d ".cb" ]; then
    echo "⚠️  Overlay already exists. Reinstalling..."
    rm -rf .cb
fi

# Ensure cb_docs exists and is complete (source of truth for documentation)
if [ ! -d "cb_docs" ]; then
    echo "⚠️  cb_docs/ not found. Creating from git history..."
    if git checkout 2bc80cc -- docs 2>/dev/null; then
        cp -r docs cb_docs && rm -rf docs
        echo "   ✅ cb_docs/ created from git history"
    else
        echo "   ❌ Failed to restore from git history. Creating minimal cb_docs/..."
        mkdir -p cb_docs/rules cb_docs/templates cb_docs/adrs
        echo "   ⚠️  Please manually populate cb_docs/ with documentation"
    fi
else
    echo "   Checking cb_docs/ for missing files..."
    # Check if key directories exist, restore if missing
    if [ ! -d "cb_docs/rules" ]; then
        echo "   Restoring missing cb_docs/rules/..."
        if git checkout 2bc80cc -- docs/rules 2>/dev/null; then
            cp -r docs/rules cb_docs/ && rm -rf docs/rules
            echo "   ✅ cb_docs/rules/ restored"
        else
            echo "   ❌ Failed to restore rules/, creating empty directory"
            mkdir -p cb_docs/rules
        fi
    fi
    # Check for templates
    if [ ! -d "cb_docs/templates" ]; then
        echo "   Restoring missing cb_docs/templates/..."
        if git checkout 2bc80cc -- docs/templates 2>/dev/null; then
            cp -r docs/templates cb_docs/ && rm -rf docs/templates
            echo "   ✅ cb_docs/templates/ restored"
        else
            echo "   ❌ Failed to restore templates/, creating empty directory"
            mkdir -p cb_docs/templates
        fi
    fi
    # Check for adrs
    if [ ! -d "cb_docs/adrs" ]; then
        echo "   Restoring missing cb_docs/adrs/..."
        if git checkout 2bc80cc -- docs/adrs 2>/dev/null; then
            cp -r docs/adrs cb_docs/ && rm -rf docs/adrs
            echo "   ✅ cb_docs/adrs/ restored"
        else
            echo "   ❌ Failed to restore adrs/, creating empty directory"
            mkdir -p cb_docs/adrs
        fi
    fi
    # Check for guardrails.json
    if [ ! -f "cb_docs/rules/guardrails.json" ]; then
        echo "   Restoring missing cb_docs/rules/guardrails.json..."
        if git checkout 2bc80cc -- docs/rules/guardrails.json 2>/dev/null; then
            cp docs/rules/guardrails.json cb_docs/rules/ && rm -rf docs/rules/guardrails.json
            echo "   ✅ cb_docs/rules/guardrails.json restored"
        else
            echo "   ❌ Failed to restore guardrails.json, creating minimal version"
            mkdir -p cb_docs/rules
            echo '{"forbiddenPatterns": []}' > cb_docs/rules/guardrails.json
        fi
    fi
fi

echo "   ✅ cb_docs/ is complete"

# Create .cb directory structure
echo "   Creating .cb directory structure..."
mkdir -p .cb/commands
mkdir -p .cb/instructions
mkdir -p .cb/engine/templates/commands
mkdir -p .cb/cache/command_state
mkdir -p .cursor/rules

# Create state files
echo "   Creating state files..."
cat > .cb/cache/command_state/state.json << 'EOF'
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "project_state": {
    "overlay_mode": true,
    "cb_docs_dir": "cb_docs",
    "cache_dir": ".cb/cache",
    "engine_dir": ".cb"
  },
  "command_history": [],
  "active_tasks": [],
  "completed_tasks": [],
  "cache_metadata": {
    "last_cleanup": "2025-01-15T00:00:00Z",
    "size_bytes": 0
  }
}
EOF

cat > .cb/cache/command_state/metrics.json << 'EOF'
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "command_metrics": {
    "total_commands": 0,
    "successful_commands": 0,
    "failed_commands": 0,
    "average_execution_time_ms": 0
  },
  "discovery_metrics": {
    "total_discoveries": 0,
    "successful_discoveries": 0,
    "failed_discoveries": 0,
    "average_discovery_time_ms": 0
  },
  "performance_metrics": {
    "total_execution_time_ms": 0,
    "peak_memory_usage_mb": 0,
    "cache_hit_rate": 0.0
  },
  "session_metrics": {
    "current_session_start": "2025-01-15T00:00:00Z",
    "total_sessions": 1,
    "average_session_duration_minutes": 0
  }
}
EOF

# Create .cb/bin directory and cb executable
echo "   Creating .cb/bin directory and cb executable..."
mkdir -p .cb/bin

# .cb/bin/cb - main CLI executable
cat > .cb/bin/cb << 'EOF'
#!/bin/bash
# Code Builder Overlay CLI

# Set overlay environment
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb"
export CB_MODE=overlay

# Add .cb/bin to PATH
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment
if [ -f "$(pwd)/.venv/bin/activate" ]; then
    source "$(pwd)/.venv/bin/activate"
fi

# Set PYTHONPATH to include .cb
export PYTHONPATH="$(pwd)/.cb:$PYTHONPATH"

# Run the CLI from .cb/
exec "$(pwd)/.venv/bin/python" -m builder.core.cli "$@"
EOF

chmod +x .cb/bin/cb

# .cb/activate - environment activation
cat > .cb/activate << 'EOF'
#!/bin/bash
# Code Builder Overlay Environment Activation

# Set overlay environment
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb"
export CB_MODE=overlay

# Add .cb/bin to PATH
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment
if [ -f "$(pwd)/.venv/bin/activate" ]; then
    source "$(pwd)/.venv/bin/activate"
fi

echo "🔧 Code Builder Overlay activated!"
echo "   CB_MODE: $CB_MODE"
echo "   CB_DOCS_DIR: $CB_DOCS_DIR"
echo "   CB_CACHE_DIR: $CB_CACHE_DIR"
echo "   CB_ENGINE_DIR: $CB_ENGINE_DIR"
echo ""
echo "💡 Add 'source .cb/activate' to your shell rc file for automatic activation"
echo "   Commands: cb help, cb discover, cb context, cb docs, etc."
EOF

chmod +x .cb/activate

# Setup commands and rules
echo "   Setting up commands and rules..."
setup_commands

# Update .gitignore
echo "   Updating .gitignore..."
if ! grep -q "^\.cb/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Code Builder Overlay" >> .gitignore
    echo ".cb/" >> .gitignore
    echo "cb_cb_docs/" >> .gitignore
fi

echo ""
echo "✅ Code Builder Overlay installed successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate: source .cb/activate"
echo "   2. Test: cb help"
echo "   3. Add to shell: echo 'source .cb/activate' >> ~/.bashrc"
echo ""
echo "📁 Structure:"
echo "   .cb/     - Essential overlay files (builder/, bin/, cache/)"
echo "   .venv/   - Virtual environment (created during installation)"
echo "   cb_docs/ - Documentation directory (source of truth for docs)"
echo ""
echo "💡 The overlay system is now ready to use!"
