# Builder CLI

Python CLI (builder/cli.py) manages ADRs, planning, iterations, rules, and code evaluation.

---

## Commands

### ADR Management
- `builder:adr:new`

      pnpm run builder:adr:new "Create hello module" --parent ADR-0000 --related src/hello.ts --tags demo

  Creates `docs/adrs/ADR-000X.md` and links it in `0000_MASTER_ADR.md`.

---

### Planning & Context
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

### Code Evaluation
- `eval:objective <path>`

      python builder/cli.py eval:objective src/hello.ts

  Runs objective evaluation using tests, coverage, lint, spell, and guardrails.

- `eval:objective <path> --server`

      python builder/cli.py eval:objective src/hello.ts --server

  Starts Cursor Bridge Server for interactive evaluation.

- `eval:prepare <path>`

      python builder/cli.py eval:prepare src/hello.ts

  Generates evaluation prompt for Cursor.

- `eval:complete <path> --cursor-response <json>`

      python builder/cli.py eval:complete src/hello.ts --cursor-response response.json

  Blends objective and subjective scores.

---

### ABC Iteration
- `iter:cursor <path> [--rounds N]`

      python builder/cli.py iter:cursor src/hello.ts

  Generates A/B/C variants and prepares for Cursor evaluation.

- `iter:finish <path> --winner A|B|C`

      python builder/cli.py iter:finish src/hello.ts --winner B

  Completes iteration with winner selection.

---

### Rules & Guardrails
- `builder:rules:show`

      pnpm run rules:show --feature auth --stacks typescript,react

  Shows merged rules + guardrails.

- `builder:rules:check`

      pnpm run rules:check "src/**/*.ts" --feature auth --stacks typescript,react

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

## Where it fits
- Run **plan** → generate context
- Use AI editor (Cursor) with `.cursorrules` to apply context to codegen
- Run **evaluation** → measure code quality objectively and subjectively
- Run **rules:check** + tests before commit
- Record new **ADRs** when design decisions are made
