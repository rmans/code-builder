# Code Builder 🛠️

[![Code Quality](https://github.com/rmans/code-builder/workflows/CI/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Evaluation Status](https://img.shields.io/badge/evaluation-informational-blue)](https://github.com/rmans/code-builder/actions)

Code Builder is a developer productivity scaffold for AI-assisted software projects.  
It combines **ADRs (Architecture Decision Records)**, **iteration loops**, **rules/guardrails**, and **automated evaluation** to make AI outputs repeatable, testable, and compliant with your coding standards.

---

## Why

- **Keep architectural decisions explicit** (ADRs) - Document design choices and their rationale
- **Generate code via ABC iteration** (A base, B hotter, C colder) - Systematic code improvement
- **Enforce rules/guardrails** (security, style, feature rules) - Automated compliance checking
- **Measure code quality** (objective + subjective evaluation) - Quantify and improve code quality
- **Auto-load context** (rules + ADRs) per feature/file, so AI assistants (e.g. Cursor) generate code that fits the project

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
    pnpm run test       # run tests
    pnpm run lint       # run ESLint
    pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react

---

## Typical Workflow

1. **Plan**

       pnpm run builder:plan:auto src/auth/login.ts

   Produces `builder/cache/context.json`.

2. **Generate/Edit Code** (in Cursor)

   Prompt:
   > “Apply Code Builder Flow for this file: load related ADRs, merge rules from context.json, propose spec + code + tests, run 3-round ABC, ensure guardrails, and show the winner.”

3. **Check & Test**

       pnpm run lint
       pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react
       pnpm run test
       pnpm run build

4. **Record a Decision**

       pnpm run builder:adr:new "Auth login API shape" --parent ADR-0000 --related src/auth/login.ts --tags auth

5. **Evaluate Code Quality**

       # Objective evaluation (automated metrics)
       python builder/cli.py eval:objective src/hello.ts
       
       # Interactive evaluation with Cursor
       python builder/cli.py eval:objective src/hello.ts --server
       
       # ABC iteration (compare variants)
       python builder/cli.py iter:cursor src/hello.ts

---

## Directory Structure

    docs/
      adrs/         # Architecture Decision Records
      templates/    # Jinja2 templates for ADR/spec
      rules/        # Global/project/stack/feature rules + guardrails.json
      eval/         # Evaluation configuration and weights
      CURSOR-Custom-Commands.md    # Cursor integration guide
      USAGE-Cursor-Evaluation.md   # Evaluation usage guide
    builder/
      cli.py        # Python CLI with evaluation commands
      evaluators/   # Objective evaluation system
        objective.py        # Core evaluation logic
        artifact_detector.py # File type detection
      prompts/      # Evaluation prompt generation
        evaluation_prompt.py
      scripts/      # Utility scripts
        cursor_server.py    # Flask bridge server
      test_data/    # Sample files for testing
      cache/        # Generated reports, evaluations, context
    src/
      utils/http.ts # Shared HTTP client
      hello.ts      # Example module
    test/
      hello.test.ts # Vitest tests
    .github/workflows/
      ci.yml        # CI with evaluation jobs

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
python builder/cli.py eval:objective src/hello.ts

# Interactive evaluation with Cursor Bridge Server
python builder/cli.py eval:objective src/hello.ts --server
```

#### Manual Evaluation
```bash
# Generate Cursor evaluation prompt
python builder/cli.py eval:prepare src/hello.ts

# Complete evaluation with Cursor response
python builder/cli.py eval:complete src/hello.ts --cursor-response response.json
```

#### ABC Iteration
```bash
# Generate variants and prepare for Cursor evaluation
python builder/cli.py iter:cursor src/hello.ts

# Complete iteration with winner selection
python builder/cli.py iter:finish src/hello.ts --winner B --scores-file cursor_response.json
```

### Cursor Integration
- **Bridge Server**: HTTP endpoints for seamless Cursor integration
- **Custom Commands**: One-click evaluation submission
- **Auto-completion**: Automatic score blending and result generation

### CI Integration
- **Automated reports** generated on every PR
- **Artifact uploads** with evaluation results
- **PR comments** with evaluation summaries
- **Non-blocking** - evaluation doesn't fail CI

See [docs/USAGE-Cursor-Evaluation.md](docs/USAGE-Cursor-Evaluation.md) for detailed usage instructions.
