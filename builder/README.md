# Builder CLI

Python CLI (builder/cli.py) manages ADRs, context generation, planning, iterations, rules, documentation, discovery, and code evaluation. The CLI provides a comprehensive set of commands for AI-assisted development workflows with intelligent discovery, auto ADR linking, and comprehensive metrics tracking.

## Recent Updates

- **Agent Tracking & Orchestration**: Multi-agent session management with intelligent task scheduling
- **Multi-Agent Cursor Integration**: Launch multiple Cursor agents for parallel task execution
- **Task File Parsing**: Execute structured tasks from TASK-*.md files with dependency resolution
- **Agent Ownership Protection**: Prevent cleanup of files created by active agents
- **Discovery System**: Interactive and batch discovery with templates
- **Auto ADR Linking**: Automatic discovery and linking of related ADRs across all document types
- **PII Detection**: Security validation with automatic PII detection and redaction
- **Metrics Tracking**: Comprehensive reporting with historical data and trends
- **CI Integration**: Automated discovery and context pack generation in pull requests

---

## Commands

### ADR Management
- `adr:new`

      python3 builder/cli.py adr:new "Create hello module" --parent ADR-0000 --related src/hello.ts --tags demo

  Creates `docs/adrs/ADR-000X.md` and links it in `0000_MASTER_ADR.md`.

---

### Agent Management
- `agent:start`

      python3 builder/core/cli.py agent:start --type backend --session-id my-agent-1

  Starts a new agent session with specified type and ID.

- `agent:stop`

      python3 builder/core/cli.py agent:stop --session-id my-agent-1

  Stops an active agent session and cleans up resources.

- `agent:list`

      python3 builder/core/cli.py agent:list

  Lists all active agent sessions with their status and created files.

- `agent:cleanup`

      python3 builder/core/cli.py agent:cleanup --session-id my-agent-1

  Cleans up files created by a specific agent session.

---

### Task Orchestration
- `orchestrator:load-tasks`

      python3 builder/core/cli.py orchestrator:load-tasks

  Loads tasks from TASK-*.md files in docs/tasks/ directory.

- `orchestrator:status`

      python3 builder/core/cli.py orchestrator:status

  Shows current orchestrator status with task and agent information.

- `orchestrator:run`

      python3 builder/core/cli.py orchestrator:run --single-cycle

  Runs a single orchestration cycle, assigning and executing tasks.

- `orchestrator:execution-order`

      python3 builder/core/cli.py orchestrator:execution-order

  Shows the optimal execution order for all tasks based on dependencies.

- `orchestrator:multi-agent`

      python3 builder/core/cli.py orchestrator:multi-agent --launch-all

  Launches multiple Cursor agents for parallel task execution.

- `orchestrator:reset`

      python3 builder/core/cli.py orchestrator:reset --confirm

  Resets the orchestrator state, clearing all tasks and agents.

---

### Discovery System
- `discover:new`

      python3 builder/cli.py discover:new --interactive
      python3 builder/cli.py discover:new --batch --template enterprise --product "My Product" --idea "Product idea"
      python3 builder/cli.py discover:new --batch --template startup --auto-generate

  Creates discovery contexts with interactive prompts or batch processing. Supports `default`, `enterprise`, and `startup` templates.

- `discover:analyze`

      python3 builder/cli.py discover:analyze --repo-root

  Analyzes codebase and generates comprehensive discovery reports with metrics.

- `discover:scan`

      python3 builder/cli.py discover:scan --auto-generate

  Scans all documents and auto-generates missing discovery contexts.

- `discover:regenerate`

      python3 builder/cli.py discover:regenerate --all

  Regenerates all discovery outputs and documentation.

- `discover:validate`

      python3 builder/cli.py discover:validate discovery_context.yml

  Validates discovery context files with PII detection and security checks.

- `cleanup:artifacts`

      python3 builder/cli.py cleanup:artifacts --dry-run
      python3 builder/cli.py cleanup:artifacts --clean
      python3 builder/cli.py cleanup:artifacts --check-agents --agent-workspaces

  Scans for and cleans up test/example artifacts outside of designated directories.
  Enhanced with agent-aware cleanup that protects files created by active agents.

---

### Planning & Context
- `plan:auto`

      python3 builder/cli.py plan:auto src/auth/login.ts

  Infers feature from `builder/feature_map.json` and generates intelligent context.

- `ctx:build-enhanced`

      python3 builder/cli.py ctx:build-enhanced src/auth/login.ts --purpose implement --feature auth

  Builds enhanced context with specific parameters and budget management.

- `ctx:explain`

      python3 builder/cli.py ctx:explain

  Shows why specific items were selected for the context.

- `ctx:pack`

      python3 builder/cli.py ctx:pack

  Generates prompt blocks for AI assistants.

Outputs `builder/cache/pack_context.json` and `context.md` with:
- feature and purpose
- merged rules with conflict detection
- acceptance criteria
- ADRs and architecture decisions
- code excerpts and tests
- budget utilization

---

### Documentation Management
- `doc:new`

      python3 builder/cli.py doc:new prd --title "User Authentication" --prd PRD-001

  Creates new documents with proper front-matter and linking.

- `doc:set-links`

      python3 builder/cli.py doc:set-links docs/arch/ARCH-001.md --prd PRD-001 --ux UX-001

  Sets front-matter links without manual YAML editing.

- `doc:check`

      python3 builder/cli.py doc:check

  Validates document front-matter and structure.

- `doc:index`

      python3 builder/cli.py doc:index

  Generates documentation index with current status.

---

### Context System
- `ctx:graph:build`

      python3 builder/cli.py ctx:graph:build

  Builds context graph from documentation and source code.

- `ctx:graph:stats`

      python3 builder/cli.py ctx:graph:stats

  Shows context graph statistics (nodes and edges by type).

- `ctx:select`

      python3 builder/cli.py ctx:select src/auth/login.ts --feature auth

  Selects and ranks context for a target path.

- `ctx:budget`

      python3 builder/cli.py ctx:budget

  Applies token budget to context selection.

- `ctx:diff`

      python3 builder/cli.py ctx:diff old.json new.json

  Shows differences between two context packs.

---

### Code Evaluation
- `eval:objective <path>`

      python3 builder/cli.py eval:objective src/hello.ts

  Runs objective evaluation using tests, coverage, lint, spell, and guardrails.

- `eval:objective <path> --server`

      python3 builder/cli.py eval:objective src/hello.ts --server

  Starts Cursor Bridge Server for interactive evaluation.

- `eval:prepare <path>`

      python3 builder/cli.py eval:prepare src/hello.ts

  Generates evaluation prompt for Cursor.

- `eval:complete <path> --cursor-response <json>`

      python3 builder/cli.py eval:complete src/hello.ts --cursor-response response.json

  Blends objective and subjective scores.

---

### ABC Iteration
- `iter:cursor <path> [--rounds N]`

      python3 builder/cli.py iter:cursor src/hello.ts

  Generates A/B/C variants and prepares for Cursor evaluation.

- `iter:finish <path> --winner A|B|C`

      python3 builder/cli.py iter:finish src/hello.ts --winner B

  Completes iteration with winner selection.

---

### Rules & Guardrails
- `rules:show`

      python3 builder/cli.py rules:show --feature auth --stacks typescript,react

  Shows merged rules + guardrails with conflict detection.

- `rules:check`

      python3 builder/cli.py rules:check "tests/**/*.ts" --feature auth --stacks typescript,react

  Fails if any forbidden patterns found.

---

## Evaluation System

The builder includes a comprehensive evaluation system:

### Objective Metrics
- **Tests**: Pass rate and coverage analysis
- **Lint**: Code quality and style violations
- **Spell**: Spelling and terminology consistency
- **Guardrails**: Adherence to project rules
- **Coverage**: Line coverage from test reports

### Cursor Integration
- **Bridge Server**: HTTP endpoints for prompt serving and response collection
- **Custom Commands**: Cursor integration for seamless evaluation
- **Auto-completion**: Automatic score blending and result generation

### Workflow
1. **Run objective evaluation** → Get automated metrics
2. **Generate Cursor prompt** → Get human assessment
3. **Blend scores** → Final evaluation with confidence bounds
4. **ABC iteration** → Compare multiple variants

---

## New Features

### Agent Tracking & Orchestration System
- **Multi-agent session management**: Track concurrent agents and prevent interference
- **Intelligent task scheduling**: Dependency-based task execution with NetworkX graphs
- **Agent ownership protection**: Prevent cleanup of files created by active agents
- **Task file parsing**: Execute structured tasks from TASK-*.md files
- **Multi-agent Cursor integration**: Launch multiple Cursor agents for parallel work
- **Dependency resolution**: Automatic task ordering based on dependencies
- **Status tracking**: Monitor task progress and agent activity
- **Workspace isolation**: Each agent gets its own isolated workspace

### Context System
- **Graph-based selection**: Discovers related items through explicit links and proximity
- **Intelligent ranking**: Scores items based on relevance, feature matching, and recency
- **Budget management**: Token-aware packaging with per-purpose allocations
- **Caching**: SHA256-based cache keys for fast, deterministic context generation

### Documentation Management
- **Document creation**: Create new documents with proper front-matter
- **Link management**: Set document links without manual YAML editing
- **Validation**: Comprehensive document structure validation
- **Indexing**: Automatic documentation index generation

### PR Ergonomics
- **Pull request template**: Auto-populated with validation checklist and context preview
- **Context preview**: Shows first 200 lines of generated context
- **Validation commands**: Integrated quality gates for PRs
- **Reviewer guidance**: Clear instructions for context evaluation

### Caching & Performance
- **Intelligent caching**: SHA256-based cache keys with automatic invalidation
- **Force rebuild**: `--force` flag to bypass cache when needed
- **Performance optimization**: Fast context generation and retrieval
- **Deterministic results**: Consistent output for same inputs

---

## Where it fits
- Run **plan:auto** → generate intelligent context
- Use AI editor (Cursor) with context from `pack_context.json` for codegen
- Run **evaluation** → measure code quality objectively and subjectively
- Run **rules:check** + tests before commit
- Record new **ADRs** when design decisions are made
- Create **PRs** with auto-populated templates and context preview
- Use **caching** for fast, consistent context generation

## Orchestrator Workflow
1. **Define tasks** → Create TASK-*.md files in docs/tasks/
2. **Load tasks** → `python3 builder/core/cli.py orchestrator:load-tasks`
3. **Check status** → `python3 builder/core/cli.py orchestrator:status`
4. **Launch agents** → `python3 builder/core/cli.py orchestrator:multi-agent --launch-all`
5. **Execute tasks** → `python3 builder/core/cli.py orchestrator:run`
6. **Monitor progress** → Check agent workspaces and progress logs
7. **Cleanup** → `python3 builder/core/cli.py agent:cleanup` when done
