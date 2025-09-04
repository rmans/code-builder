# Code Builder 🛠️

Code Builder is a developer productivity scaffold for AI-assisted software projects.  
It combines **ADRs (Architecture Decision Records)**, **iteration loops**, and **rules/guardrails** to make AI outputs repeatable, testable, and compliant with your coding standards.

---

## Why

- Keep architectural decisions explicit (ADRs)
- Generate code via an ABC iteration loop (A base, B hotter, C colder)
- Enforce rules/guardrails (security, style, feature rules)
- Auto-load context (rules + ADRs) per feature/file, so AI assistants (e.g. Cursor) generate code that fits the project

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

---

## Directory Structure

    docs/
      adrs/         # Architecture Decision Records
      templates/    # Jinja2 templates for ADR/spec
      rules/        # Global/project/stack/feature rules + guardrails.json
    builder/
      cli.py        # Python CLI
      rules_loader.py
      cache/        # Generated context.json, iteration history
    src/
      utils/http.ts # Shared HTTP client
      hello.ts      # Example module
    test/
      hello.test.ts # Vitest tests
