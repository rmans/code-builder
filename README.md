# Code Builder 🛠️

[![Code Quality](https://github.com/rmans/code-builder/workflows/CI/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Context Packs](https://github.com/rmans/code-builder/workflows/Context%20Packs/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Documentation](https://github.com/rmans/code-builder/workflows/Documentation/badge.svg)](https://github.com/rmans/code-builder/actions)

Code Builder is a comprehensive developer productivity scaffold for AI-assisted software projects.  
It combines **ADRs (Architecture Decision Records)**, **context generation**, **iteration loops**, **rules/guardrails**, **automated evaluation**, **multi-agent orchestration**, and **discovery systems** to make AI outputs repeatable, testable, and compliant with your coding standards.

## 🏗️ System Architecture

Code Builder is built around **8 core systems** working together:

### 1. **Context Management System**
- **Graph-based selection**: Discovers related items through explicit links and code proximity
- **Intelligent ranking**: Scores items based on relevance, feature matching, and recency  
- **Budget management**: Token-aware packaging with per-purpose allocations
- **Caching**: SHA256-based cache keys for fast, deterministic context generation

### 2. **Discovery System** 
- **Interactive interviews**: Guided prompts for new and existing products
- **Code analysis**: Deep analysis of codebase structure, patterns, and dependencies
- **Synthesis engine**: Combines findings into structured insights
- **Document generation**: Auto-generates PRDs, ADRs, and technical specifications
- **Validation**: Ensures generated documents meet quality standards

### 3. **Multi-Agent Orchestration**
- **Task management**: Parse and execute structured tasks from TASK-*.md files
- **Agent tracking**: Session management with ownership protection
- **Dependency resolution**: Intelligent task scheduling based on dependencies
- **Cursor integration**: Launch multiple Cursor agents for parallel execution
- **Progress monitoring**: Real-time tracking of agent activities and file creation

### 4. **Evaluation System**
- **Objective evaluation**: Automated scoring based on test coverage, linting, and metrics
- **Subjective evaluation**: AI-powered quality assessment with structured prompts
- **ABC iteration**: Systematic code improvement through variant generation and comparison
- **Comprehensive reporting**: Historical data, trends, and actionable insights

### 5. **Document Management**
- **Master synchronization**: Automated maintenance of 0000_MASTER_*.md index files
- **Cross-reference cleanup**: Automatic removal of broken links when documents are deleted
- **Template system**: Jinja2-based document generation with consistent formatting
- **8 document types**: PRD, ADR, ARCH, EXEC, IMPL, INTEGRATIONS, TASKS, UX

### 6. **Rules & Guardrails System**
- **Hierarchical rules**: Global → Project → Stack → Feature precedence
- **Conflict detection**: Automatic identification of rule contradictions
- **Guardrails enforcement**: Forbidden patterns and security validation
- **PII detection**: Automatic detection and redaction of sensitive information

### 7. **Cache & Performance System**
- **Intelligent caching**: SHA256-based cache keys with automatic invalidation
- **Agent session cleanup**: Automatic cleanup of old and timed-out sessions
- **Workspace management**: Cleanup of completed agent workspaces
- **Performance optimization**: Fast context generation and retrieval

### 8. **PR Ergonomics System**
- **Auto-populated templates**: GitHub PR templates with validation checklists
- **Context preview**: Shows first 200 lines of generated context
- **Validation commands**: Integrated quality gates for PRs
- **Reviewer guidance**: Clear instructions for context evaluation

---

## Why

- **Keep architectural decisions explicit** (ADRs) - Document design choices and their rationale
- **Generate intelligent context** (rules + ADRs + code) per feature/file - AI assistants get relevant context automatically
- **Enforce rules/guardrails** (security, style, feature rules) - Automated compliance checking with conflict detection
- **Measure code quality** (objective + subjective evaluation) - Quantify and improve code quality
- **Generate code via ABC iteration** (A base, B hotter, C colder) - Systematic code improvement
- **Streamline PR reviews** (templates + context preview) - Faster, more informed code reviews
- **Cache and optimize** (intelligent caching + budget management) - Fast, efficient context generation

---

## 📊 System Statistics

- **53 CLI Commands** across 8 categories
- **34 Python Modules** in the builder system  
- **41 Markdown Files** for comprehensive documentation
- **8 Document Types** with automated master synchronization
- **8 Core Systems** working together seamlessly
- **Multi-language Support** (Python, TypeScript, JavaScript)
- **Comprehensive Testing** (Unit, Integration, E2E)

## Recent Improvements

- **Fixed import issues**: Resolved `rules_loader` and `artifact_detector` import paths in evaluation prompts
- **Enhanced Cursor integration**: Improved chat workflow with proper guidance and session management
- **Multi-agent support**: Better task orchestration and agent management capabilities
- **Cache management**: Added cleanup commands for agent sessions and workspaces
- **Documentation updates**: Improved templates and documentation structure
- **Master file synchronization**: Automated sync of 0000_MASTER_*.md files with cross-reference cleanup

---

## 🚀 Quickstart

Run these commands after cloning:

    git clone <this-repo-url>
    cd code-builder
    pnpm install
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt   # click, pyyaml, jinja2

    # Note: pnpm-lock.yaml is committed to ensure reproducible builds

    pnpm run build      # build TypeScript
    pnpm run test:all   # run all tests (TypeScript + Python)
    pnpm run docs:all   # validate documentation
    pnpm run rules:check "tests/**/*.ts" --feature auth --stacks typescript,react

## 📋 Command Overview

Code Builder provides **53 CLI commands** organized into **8 categories**:

### 🔍 Discovery Commands (6)
- `discover:new` - Interactive discovery with guided prompts
- `discover:analyze` - Deep codebase analysis and insights
- `discover:scan` - Batch discovery with auto-generation
- `discover:validate` - Validate discovery context files
- `discover:refresh` - Refresh specific PRD contexts
- `discover:regenerate` - Regenerate discovery outputs

### 📝 Document Commands (8)
- `doc:new` - Create new documents (PRD, ADR, ARCH, etc.)
- `doc:index` - Update document indexes and cross-references
- `doc:check` - Validate document structure and front-matter
- `doc:set-links` - Set document links and relationships
- `doc:fix-master` - Fix master document indexes
- `doc:abc` - ABC iteration for documents
- `adr:new` - Create new Architecture Decision Records
- `master:sync` - Synchronize master index files

### 🧠 Context Commands (12)
- `ctx:build` - Build context for specific files
- `ctx:build-enhanced` - Enhanced context with parameters
- `ctx:diff` - Compare context packages
- `ctx:explain` - Explain context selection decisions
- `ctx:pack` - Generate context packages
- `ctx:trace` - Trace context generation process
- `ctx:graph:build` - Build context relationship graph
- `ctx:graph:stats` - Show context graph statistics
- `ctx:select` - Select context items
- `ctx:budget` - Manage token budgets
- `context:scan` - Scan for context items
- `plan:auto` - Auto-generate context plans

### 🤖 Agent Commands (4)
- `agent:start` - Start new agent session
- `agent:stop` - Stop agent session
- `agent:list` - List active agents
- `agent:cleanup` - Clean up old sessions

### 🎯 Orchestration Commands (12)
- `orchestrator:add-task` - Add new task
- `orchestrator:add-agent` - Add new agent
- `orchestrator:status` - Show orchestration status
- `orchestrator:run` - Run orchestration cycles
- `orchestrator:execution-order` - Show task execution order
- `orchestrator:reset` - Reset orchestration state
- `orchestrator:load-tasks` - Load tasks from files
- `orchestrator:execute-tasks` - Execute loaded tasks
- `orchestrator:create-task-template` - Create task template
- `orchestrator:multi-agent` - Launch multi-agent workflows
- `orchestrator:add-task-abc` - Add ABC iteration task
- `orchestrator:run-abc` - Run ABC iterations

### 📊 Evaluation Commands (4)
- `eval:objective` - Run objective evaluation
- `eval:prepare` - Prepare evaluation data
- `eval:complete` - Complete evaluation process
- `iter:run` - Run iteration cycles

### 🔄 Iteration Commands (4)
- `iter:cursor` - Cursor-based iteration
- `iter:finish` - Finish iteration process
- `plan:sync` - Sync planning data
- `rules:show` - Show applicable rules

### 🧹 Utility Commands (3)
- `rules:check` - Check rule compliance
- `cleanup:artifacts` - Clean up artifacts
- `master:sync` - Sync master files

## Discovery System

The Discovery system helps you explore, understand, and document your codebase with intelligent analysis and automated context generation:

### Quick Discovery
```bash
# Interactive discovery with guided prompts
python3 builder/cli.py discover:new --interactive

# Batch discovery with templates
python3 builder/cli.py discover:new --batch --template enterprise --product "My Product" --idea "Product idea"

# Auto-generate enhanced content
python3 builder/cli.py discover:new --batch --template startup --auto-generate
```

### Discovery Templates
- **`default`**: Standard product development (3-6 months, 3-5 developers)
- **`enterprise`**: Enterprise-grade (6-12 months, 10+ developers, compliance)
- **`startup`**: Rapid development (1-3 months, 2-4 developers, MVP)

### Discovery Analysis
```bash
# Analyze entire repository
python3 builder/cli.py discover:analyze --repo-root

# Scan and auto-generate missing contexts
python3 builder/cli.py discover:scan --auto-generate

# Regenerate all discovery outputs
python3 builder/cli.py discover:regenerate --all

# Validate discovery context
python3 builder/cli.py discover:validate discovery_context.yml
```

### Auto ADR Linking
All document types now automatically discover and link related ADRs:
- **Content similarity matching**: Based on title, tags, content, and technology
- **Weighted relevance scoring**: Title (40%), tags (30%), content (20%), tech (10%)
- **Smart tech detection**: Automatically extract technologies from document titles
- **Cross-document linking**: Works across PRD, ARCH, IMPL, EXEC, UX documents

---

## Typical Workflow

1. **Generate Context**

       python3 builder/cli.py plan:auto test/example.ts

   Produces `builder/cache/pack_context.json` and `context.md` with intelligent context selection.

2. **Generate/Edit Code** (in Cursor)

   Use the generated context in your AI assistant:
   > "Apply Code Builder Flow for this file: use the context from pack_context.json, propose spec + code + tests, run 3-round ABC, ensure guardrails, and show the winner."

3. **Check & Test**

       pnpm run docs:all          # validate documentation
       pnpm run test:all          # run all tests
       pnpm run rules:check "tests/**/*.ts" --feature auth --stacks typescript,react

4. **Create Pull Request**

   GitHub will auto-populate the PR template with:
   - Validation checklist
   - Context preview (first 200 lines)
   - Testing and documentation sections

5. **Record a Decision**

       python3 builder/cli.py adr:new "Auth login API shape" --parent ADR-0000 --related test/example.ts --tags auth

6. **Evaluate Code Quality**

       # Objective evaluation (automated metrics)
       python3 builder/cli.py eval:objective test/example.ts
       
       # Interactive evaluation with Cursor
       python3 builder/cli.py eval:objective test/example.ts --server
       
       # ABC iteration (compare variants)
       python3 builder/cli.py iter:cursor test/example.ts

---

## Context System

Code Builder includes an intelligent context generation system that automatically selects and packages relevant information for AI assistants:

### Context Generation
- **Graph-based selection**: Discovers related items through explicit links, one-hop connections, and nearby code
- **Intelligent ranking**: Scores items based on relevance, feature matching, and recency
- **Budget management**: Token-aware packaging with per-purpose allocations
- **Caching**: SHA256-based cache keys for fast, deterministic context generation

### Context Commands
```bash
# Generate context for a file
python3 builder/cli.py plan:auto test/example.ts

# Build enhanced context with specific parameters
python3 builder/cli.py ctx:build-enhanced test/example.ts --purpose implement --feature auth

# Explain why specific items were selected
python3 builder/cli.py ctx:explain

# Generate prompt blocks for AI assistants
python3 builder/cli.py ctx:pack

# Show context graph statistics
python3 builder/cli.py ctx:graph:stats
```

### Context Output
- **`pack_context.json`**: Structured context data with rules, acceptance criteria, ADRs, and code
- **`context.md`**: Human-readable context summary
- **Prompt blocks**: Ready-to-use system, instructions, user, and references blocks

---

## Master File Synchronization

Code Builder automatically maintains master index files (`0000_MASTER_*.md`) that provide centralized indexes of all documents in each category. The system automatically syncs these indexes and cleans up cross-references when documents are created, modified, or deleted.

### Master Sync Commands
```bash
# Sync all master files
python3 builder/core/cli.py master:sync

# Sync specific document type
python3 builder/core/cli.py master:sync --type prd

# Clean up cross-references when documents are deleted
python3 builder/core/cli.py master:sync --cleanup-refs

# Dry run to see what would be updated
python3 builder/core/cli.py master:sync --dry-run
```

### Supported Document Types
- **PRD**: Product Requirements Documents (`PRD-*.md`)
- **ADR**: Architecture Decision Records (`ADR-*.md`)
- **ARCH**: Architecture Documents (`ARCH-*.md`)
- **EXEC**: Execution Documents (`EXEC-*.md`)
- **IMPL**: Implementation Documents (`IMPL-*.md`)
- **INTEGRATIONS**: Integration Documents (`INTEGRATIONS-*.md`)
- **TASKS**: Task Documents (`TASK-*.md`)
- **UX**: User Experience Documents (`UX-*.md`)

### Automatic Features
- **Index Updates**: Master files automatically reflect current document status
- **Cross-Reference Cleanup**: When documents are deleted, references are automatically removed
- **Status Tracking**: Document status, domain, and metadata are maintained
- **Link Management**: Relative links to documents are automatically generated

---

## Agent & Orchestration System

Code Builder includes a sophisticated agent tracking and task orchestration system that enables concurrent AI agent workflows with intelligent task scheduling and dependency management.

### Agent Session Management
- **Session tracking**: Each agent gets a unique session ID for tracking
- **File ownership**: Track which files were created by which agents
- **Concurrent protection**: Prevent agents from interfering with each other's work
- **Session timeouts**: Automatic cleanup of stale agent sessions
- **Agent types**: Support for different agent types (backend, frontend, setup, etc.)

### Task Orchestration
- **Dependency resolution**: Uses NetworkX to build task dependency graphs
- **Intelligent scheduling**: Only runs tasks when dependencies are satisfied
- **Parallel execution**: Run independent tasks simultaneously
- **Cycle detection**: Prevents circular dependencies
- **Priority management**: Task priority-based scheduling
- **Status tracking**: Monitor task progress (pending, running, completed, failed)

### Multi-Agent Cursor Integration
- **Isolated workspaces**: Each agent gets its own workspace directory
- **Task instructions**: Detailed instructions for each agent
- **Execution scripts**: Ready-to-run scripts for task execution
- **Progress monitoring**: Track agent progress and completion
- **Manual workflow**: Human agents can follow provided instructions

### Agent-Aware Cleanup System
- **File ownership tracking**: Track which files were created by which agents
- **Active agent protection**: Prevent cleanup of files created by active agents
- **Session-based cleanup**: Clean up files when agent sessions end
- **Workspace cleanup**: Clean up completed agent workspaces automatically
- **Safe concurrent cleanup**: Run cleanup while agents are active without interference

### 5-Phase Agent Workflow
- **Phase 1: 🚀 Implementation**: Build core functionality and business logic
- **Phase 2: 🧪 Testing**: Write and run tests to verify functionality
- **Phase 3: 📚 Documentation**: Add documentation and examples
- **Phase 4: 🧹 Cleanup**: Clean up artifacts and ensure code quality
- **Phase 5: 💾 Commit**: Stage, commit, and push changes to repository

### Agent Commands
```bash
# Start an agent session
python3 builder/core/cli.py agent:start --type backend --session-id my-agent-1

# List active agents
python3 builder/core/cli.py agent:list

# Stop an agent session
python3 builder/core/cli.py agent:stop --session-id my-agent-1

# Cleanup agent files
python3 builder/core/cli.py agent:cleanup --session-id my-agent-1
```

### Orchestrator Commands
```bash
# Create new tasks using Jinja2 template
python3 builder/core/cli.py doc:new tasks --title "Task Name" --owner "owner"

# Load tasks from TASK-*.md files
python3 builder/core/cli.py orchestrator:load-tasks

# Show orchestrator status
python3 builder/core/cli.py orchestrator:status

# Run single orchestration cycle
python3 builder/core/cli.py orchestrator:run --single-cycle

# Show optimal execution order
python3 builder/core/cli.py orchestrator:execution-order

# Launch multiple Cursor agents
python3 builder/core/cli.py orchestrator:multi-agent --launch-all

# Reset orchestrator state
python3 builder/core/cli.py orchestrator:reset --confirm

# Enhanced cleanup with agent awareness
python3 builder/core/cli.py cleanup:artifacts --check-agents --agent-workspaces --clean
```

### Agent Workflow Template
All tasks follow a standardized 5-phase execution workflow:

1. **🚀 Implementation**: Build core functionality
2. **🧪 Testing**: Write and run tests
3. **📚 Documentation**: Add documentation
4. **🧹 Cleanup**: Clean up artifacts
5. **💾 Commit**: Stage and commit changes

All tasks are created using the Jinja2 template system with `doc:new tasks`, which includes the standardized 5-phase agent workflow.

### Task File Format
Tasks are defined in `docs/tasks/TASK-*.md` files with YAML frontmatter:

```yaml
---
id: TASK-2025-01-15-setup-project
title: Setup Project Structure
description: Create basic project structure with directories
agent_type: setup
priority: 10
dependencies: []
tags: [setup, infrastructure]
---

# Task: Setup Project Structure

## Description
Create the basic project structure with necessary directories.

## Command
```bash
mkdir -p src tests docs && echo "Project structure created" > setup.log
```

## Acceptance Criteria
- [ ] `src/` directory created
- [ ] `tests/` directory created  
- [ ] `docs/` directory created
- [ ] `setup.log` file created
```

---

## Directory Structure

    docs/
      adrs/         # Architecture Decision Records
      arch/         # Architecture documents
      integrations/ # Integration specifications
      impl/         # Implementation plans
      exec/         # Execution plans
      ux/           # User experience designs
      tasks/        # Task definitions
      templates/    # Workflow and document templates
      rules/        # Global/project/stack/feature rules + guardrails.json
      eval/         # Evaluation configuration and weights
      CURSOR-Custom-Commands.md    # Cursor integration guide
      USAGE-Cursor-Evaluation.md   # Evaluation usage guide
      README.md     # Documentation index
    builder/
      cli.py        # Python CLI with all commands
      context_graph.py      # Context graph building
      context_select.py     # Context selection and ranking
      context_budget.py     # Token budget management
      context_rules.py      # Rules merging and conflict detection
      evaluators/   # Objective evaluation system
        objective.py        # Core evaluation logic
        artifact_detector.py # File type detection
        doc_schema.py       # Documentation validation
      config/
        prompts/    # Evaluation prompt generation
          evaluation_prompt.py
      scripts/      # Utility scripts
        cursor_server.py    # Flask bridge server
      test_data/    # Sample files for testing
      tests/        # Python unit tests
      cache/        # Generated reports, evaluations, context packs
        packs/      # Cached context packs
        prompt/     # Generated prompt blocks
    tests/          # Consolidated test directory
      data/         # Test files and fixtures
        hello.test.ts # Vitest tests
        hello_bad.ts  # Test fixtures
        hello_good.ts # Test fixtures
        hello_ugly.ts # Test fixtures
        invalid-prd.md # Test data
      results/      # Test output and reports
        budget_report.md
        coverage-final.json
        vitest.json
      integration/  # Integration tests
      scripts/      # Test scripts
      unit/         # Unit tests
    .github/
      workflows/
        ci.yml        # CI with evaluation jobs
        context.yml   # Context pack generation
        docs.yml      # Documentation validation
      pull_request_template.md  # PR template with context preview

---

## PR Ergonomics

Code Builder includes comprehensive PR ergonomics to streamline code reviews:

### Pull Request Template
- **Auto-populated**: GitHub automatically uses the template for new PRs
- **Validation checklist**: Ensures all quality gates are completed
- **Context preview**: Shows first 200 lines of generated context
- **Structured sections**: Testing, documentation, and additional notes

### Validation Commands
```bash
# Documentation validation
python3 builder/cli.py doc:check

# Documentation quality (markdown + spell)
pnpm run docs:all

# Context building
python3 builder/cli.py ctx:build-enhanced test/example.ts --purpose implement

# All tests
pnpm run test:all
```

### PR Template Features
- **Pre-submission checklist**: Validation steps with exact commands
- **Context preview**: Collapsible section with generated context
- **Reviewer guidance**: What to look for in context and code
- **Testing documentation**: How changes were tested
- **Related issues**: Link to discussions and issues

---

## Evaluation System

Code Builder includes a comprehensive evaluation system that measures code quality across multiple dimensions:

### Objective Metrics (Automated)
- **Tests**: Pass rate and coverage analysis from Vitest
- **Lint**: Code quality and style violations from ESLint
- **Spell**: Spelling and terminology consistency from CSpell
- **Guardrails**: Adherence to project rules and standards
- **Coverage**: Line coverage from test reports

### Subjective Metrics (Human + AI)
- **Clarity**: Code readability, naming conventions, documentation
- **Design**: Architecture, patterns, separation of concerns
- **Maintainability**: Modularity, complexity, refactoring ease
- **Tests**: Test quality, coverage, and clarity
- **Rule Compliance**: Adherence to project-specific standards

### Evaluation Workflows

#### Quick Evaluation
```bash
# Objective evaluation only (automated)
python3 builder/cli.py eval:objective test/example.ts

# Interactive evaluation with Cursor Bridge Server
python3 builder/cli.py eval:objective test/example.ts --server
```

#### Manual Evaluation
```bash
# Generate Cursor evaluation prompt
python3 builder/cli.py eval:prepare src/hello.ts

# Complete evaluation with Cursor response
python3 builder/cli.py eval:complete src/hello.ts --cursor-response response.json
```

#### ABC Iteration
```bash
# Generate variants and prepare for Cursor evaluation
python3 builder/cli.py iter:cursor src/hello.ts

# Complete iteration with winner selection
python3 builder/cli.py iter:finish src/hello.ts --winner B --scores-file cursor_response.json
```

### Cursor Integration
- **Bridge Server**: HTTP endpoints for seamless Cursor integration
- **Custom Commands**: One-click evaluation submission
- **Auto-completion**: Automatic score blending and result generation

### CI Integration
- **Automated reports** generated on every PR
- **Context pack generation** for changed files
- **Documentation validation** with markdown linting and spell checking
- **Artifact uploads** with evaluation results and context packs
- **PR comments** with evaluation summaries
- **Non-blocking** - evaluation doesn't fail CI

### Recent Updates

### Agent Tracking & Orchestration System
- **Agent session management**: Track concurrent agents and prevent interference
- **Task orchestration**: Intelligent task scheduling with dependency resolution
- **Multi-agent Cursor integration**: Launch multiple Cursor agents for parallel work
- **Agent ownership protection**: Prevent cleanup of files created by active agents
- **Task file parsing**: Execute tasks from structured TASK-*.md files

### Test Directory Consolidation
- **Consolidated test structure**: All test files now organized under `tests/` directory
- **Test data**: Moved from `.testfiles/` to `tests/data/` for better organization
- **Test results**: Moved from `.testresults/` to `tests/results/` for output files
- **Updated .gitignore**: Reflects new consolidated test directory structure

### Import Path Fixes
- **Fixed evaluation imports**: Corrected import paths for `evaluation_prompt` and `artifact_detector`
- **Updated directory structure**: `builder/config/prompts/` for evaluation prompts
- **Improved reliability**: All CLI commands now work correctly with proper imports

## New Features

#### Agent Tracking & Orchestration
- **Agent session management**: `python3 builder/core/cli.py agent:start --type backend`
- **Task orchestration**: `python3 builder/core/cli.py orchestrator:load-tasks`
- **Multi-agent Cursor**: `python3 builder/core/cli.py orchestrator:multi-agent --launch-all`
- **Agent cleanup**: `python3 builder/core/cli.py agent:cleanup --session-id <id>`
- **Smart cleanup**: `python3 builder/core/cli.py cleanup:artifacts --check-agents --agent-workspaces`
- **Task execution**: `python3 builder/core/cli.py orchestrator:run --single-cycle`
- **Dependency resolution**: Automatic task scheduling based on dependencies
- **Agent ownership**: Protect files created by active agents from cleanup

#### Documentation Management
- **Document creation**: `python3 builder/cli.py doc:new <type> --title "Title"`
- **Document indexing**: `python3 builder/cli.py doc:index`
- **Document validation**: `python3 builder/cli.py doc:check`
- **Link management**: `python3 builder/cli.py doc:set-links`
- **Auto ADR linking**: Automatic discovery and linking of related ADRs across all document types

#### Discovery System
- **Interactive discovery**: `python3 builder/cli.py discover:new --interactive`
- **Batch discovery**: `python3 builder/cli.py discover:new --batch --template <type>`
- **Template support**: `default`, `enterprise`, `startup` templates with tailored fields
- **Auto-generation**: `--auto-generate` flag for enhanced content generation
- **Discovery scanning**: `python3 builder/cli.py discover:scan --auto-generate`
- **Context regeneration**: `python3 builder/cli.py discover:regenerate --all`
- **Artifact cleanup**: `python3 builder/cli.py cleanup:artifacts --clean`

#### Context System
- **Graph building**: `python3 builder/cli.py ctx:graph:build`
- **Context selection**: `python3 builder/cli.py ctx:select`
- **Budget management**: `python3 builder/cli.py ctx:budget`
- **Context diffing**: `python3 builder/cli.py ctx:diff`
- **Context packing**: `python3 builder/cli.py ctx:pack --split --stdout`

#### Security & Compliance
- **PII detection**: Automatic detection of personally identifiable information
- **Redaction policy**: Optional redaction of sensitive data in discovery contexts
- **Security validation**: `python3 builder/cli.py discover:validate <context_file>`

#### Metrics & Reporting
- **Comprehensive metrics**: Feature counts, gap analysis, performance tracking
- **Historical data**: `builder/cache/discovery_report.json` with trends
- **Quality indicators**: Code quality, complexity, security metrics
- **Performance tracking**: Analysis timing and success rates

#### CI/CD Integration
- **Discovery CI**: Automated discovery scanning on PR changes
- **Context Pack CI**: Automated context generation and validation
- **Artifact uploads**: Discovery and context artifacts in PR comments
- **Validation gates**: Rules and acceptance criteria validation

#### Caching & Performance
- **Intelligent caching**: SHA256-based cache keys
- **Cache invalidation**: Automatic on file changes
- **Force rebuild**: `--force` flag to bypass cache
- **Performance optimization**: Fast context generation

See [docs/USAGE-Cursor-Evaluation.md](docs/USAGE-Cursor-Evaluation.md) for detailed usage instructions.
