# Documentation Layer

This repo uses docs to drive codegen, decisions, and evaluation.

---

## Document Index

### 📋 Product Requirements
*Product requirements and specifications*

- ❓ **Master Product Requirements Index** (`0000_MASTER_PRD`)
  - Owner: system | Created: 2025-09-06

### 🏗️ Architecture
*Architectural decisions and designs*

- ❓ **Master Architecture Index** (`0000_MASTER_ARCH`)
  - Owner: system | Created: 2025-09-06

### 🔗 Integrations
*Integration specifications and APIs*

- ❓ **Master Integrations Index** (`0000_MASTER_INTEGRATIONS`)
  - Owner: system | Created: 2025-09-06

### 🎨 User Experience
*UX designs and user research*
*No documents found*

### ⚙️ Implementation
*Implementation details and technical specs*

- ❓ **Master Implementation Index** (`0000_MASTER_IMPL`)
  - Owner: system | Created: 2025-09-06

### 📊 Executive
*Executive summaries and business documents*

- ❓ **Master Execution Index** (`0000_MASTER_EXEC`)
  - Owner: system | Created: 2025-09-06

### ✅ Tasks
*Task definitions and work items*

- ❓ **Master Tasks Index** (`0000_MASTER_TASKS`)
  - Owner: system | Created: 2025-09-06

---

## ADRs (docs/adrs/)
- `0000_MASTER_ADR.md` = index of all decisions
- Sub ADRs like `ADR-0001.md` created by `builder:adr:new`
- Each ADR records context, decision, consequences, alternatives

---

## Templates (docs/templates/)
- Jinja2 templates for ADRs and specs
- Used by CLI to render files

---

## Rules (docs/rules/)
- `00-global.md`, `10-project.md` = global + project-wide rules
- `stack/` (e.g. typescript, react, http-client)
- `feature/` (auth, content-engine, etc.)
- `guardrails.json` = forbidden patterns + hints

---

## Evaluation (docs/eval/)
- `config.yaml` = evaluation weights and configuration
- Defines objective vs subjective weight distribution
- Configures tool paths and scoring weights

---

## Usage Guides
- `USAGE-Cursor-Evaluation.md` = Complete evaluation workflow guide
- `CURSOR-Custom-Commands.md` = Cursor integration setup

---

## Usage
- When editing a file, run `plan:auto <file>` → context.json merges rules + ADRs  
- Cursor/AI gets that context and generates compliant code
- Run `eval:objective <file>` → measure code quality objectively
- Use `--server` flag for interactive Cursor evaluation
- Use `doc:new <type> --title "Title"` → create new documents
- Use `doc:index` → update this index
