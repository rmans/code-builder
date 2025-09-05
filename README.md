# Code Builder 🛠️

[![Code Quality](https://github.com/rmans/code-builder/workflows/CI/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Context Packs](https://github.com/rmans/code-builder/workflows/Context%20Packs/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Documentation](https://github.com/rmans/code-builder/workflows/Documentation/badge.svg)](https://github.com/rmans/code-builder/actions)

Code Builder is a comprehensive developer productivity scaffold for AI-assisted software projects.  
It combines **ADRs (Architecture Decision Records)**, **context generation**, **iteration loops**, **rules/guardrails**, **automated evaluation**, and **PR ergonomics** to make AI outputs repeatable, testable, and compliant with your coding standards.

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

## Quickstart

Run these commands after cloning:

    git clone <this-repo-url>
    cd code-builder
    pnpm install
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt   # click, pyyaml, jinja2

    pnpm run build      # build TypeScript
    pnpm run test:all   # run all tests (TypeScript + Python)
    pnpm run docs:all   # validate documentation
    pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react

---

## Typical Workflow

1. **Generate Context**

       python3 builder/cli.py plan:auto src/auth/login.ts

   Produces `builder/cache/pack_context.json` and `context.md` with intelligent context selection.

2. **Generate/Edit Code** (in Cursor)

   Use the generated context in your AI assistant:
   > "Apply Code Builder Flow for this file: use the context from pack_context.json, propose spec + code + tests, run 3-round ABC, ensure guardrails, and show the winner."

3. **Check & Test**

       pnpm run docs:all          # validate documentation
       pnpm run test:all          # run all tests
       pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react

4. **Create Pull Request**

   GitHub will auto-populate the PR template with:
   - Validation checklist
   - Context preview (first 200 lines)
   - Testing and documentation sections

5. **Record a Decision**

       python3 builder/cli.py adr:new "Auth login API shape" --parent ADR-0000 --related src/auth/login.ts --tags auth

6. **Evaluate Code Quality**

       # Objective evaluation (automated metrics)
       python3 builder/cli.py eval:objective src/hello.ts
       
       # Interactive evaluation with Cursor
       python3 builder/cli.py eval:objective src/hello.ts --server
       
       # ABC iteration (compare variants)
       python3 builder/cli.py iter:cursor src/hello.ts

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
python3 builder/cli.py plan:auto src/auth/login.ts

# Build enhanced context with specific parameters
python3 builder/cli.py ctx:build-enhanced src/auth/login.ts --purpose implement --feature auth

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

## Directory Structure

    docs/
      adrs/         # Architecture Decision Records
      arch/         # Architecture documents
      integrations/ # Integration specifications
      impl/         # Implementation plans
      exec/         # Execution plans
      ux/           # User experience designs
      tasks/        # Task definitions
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
      prompts/      # Evaluation prompt generation
        evaluation_prompt.py
      scripts/      # Utility scripts
        cursor_server.py    # Flask bridge server
      test_data/    # Sample files for testing
      tests/        # Python unit tests
      cache/        # Generated reports, evaluations, context packs
        packs/      # Cached context packs
        prompt/     # Generated prompt blocks
    src/
      auth/         # Authentication module
        login.ts    # Login functionality
      utils/http.ts # Shared HTTP client
      hello.ts      # Example module
    test/
      hello.test.ts # Vitest tests
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
python3 builder/cli.py ctx:build-enhanced src/auth/login.ts --purpose implement

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
python3 builder/cli.py eval:objective src/hello.ts

# Interactive evaluation with Cursor Bridge Server
python3 builder/cli.py eval:objective src/hello.ts --server
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

### New Features

#### Documentation Management
- **Document creation**: `python3 builder/cli.py doc:new <type> --title "Title"`
- **Document indexing**: `python3 builder/cli.py doc:index`
- **Document validation**: `python3 builder/cli.py doc:check`
- **Link management**: `python3 builder/cli.py doc:set-links`

#### Context System
- **Graph building**: `python3 builder/cli.py ctx:graph:build`
- **Context selection**: `python3 builder/cli.py ctx:select`
- **Budget management**: `python3 builder/cli.py ctx:budget`
- **Context diffing**: `python3 builder/cli.py ctx:diff`

#### Caching & Performance
- **Intelligent caching**: SHA256-based cache keys
- **Cache invalidation**: Automatic on file changes
- **Force rebuild**: `--force` flag to bypass cache
- **Performance optimization**: Fast context generation

See [docs/USAGE-Cursor-Evaluation.md](docs/USAGE-Cursor-Evaluation.md) for detailed usage instructions.
