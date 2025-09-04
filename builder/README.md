# Builder CLI

Python CLI (builder/cli.py) manages ADRs, planning, iterations, and rules.

---

## Commands

### ADR
- `builder:adr:new`

      pnpm run builder:adr:new "Create hello module" --parent ADR-0000 --related src/hello.ts --tags demo

  Creates `docs/adrs/ADR-000X.md` and links it in `0000_MASTER_ADR.md`.

---

### Planning
- `builder:plan:sync`

      pnpm run builder:plan:sync --feature auth --stacks typescript,react

- `builder:plan:auto`

      pnpm run builder:plan:auto src/auth/login.ts

  Infers feature from `builder/feature_map.json`.

Outputs `builder/cache/context.json` with:
- feature
- merged rules
- guardrails
- trace skeleton

---

### Iteration
- `builder:iter:run`

      pnpm run builder:iter src/hello.ts

  Generates 3 ABC rounds, promotes a winner, logs to `builder/cache/iter_history.json`.

---

### Rules
- `builder:rules:show`

      pnpm run rules:show --feature auth --stacks typescript,react

  Shows merged rules + guardrails.

- `builder:rules:check`

      pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react

  Fails if any forbidden patterns found.

---

## Where it fits
- Run **plan** → generate context
- Use AI editor (Cursor) with `.cursorrules` to apply context to codegen
- Run **rules:check** + tests before commit
- Record new **ADRs** when design decisions are made
