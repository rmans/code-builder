# Documentation Layer

This repository uses a comprehensive documentation system to drive code generation, architectural decisions, and evaluation. The documentation is automatically indexed and cross-linked to provide intelligent context for AI-assisted development.

## Features

- **Auto-indexing**: Automatic discovery and indexing of all document types
- **Cross-linking**: Intelligent linking between related documents
- **ADR Integration**: Automatic discovery and linking of Architecture Decision Records
- **Template System**: Standardized templates for all document types
- **Validation**: Comprehensive validation of document structure and content
- **CI Integration**: Automated documentation validation in pull requests

---

## Document Index

### 📋 Product Requirements
*Product requirements and specifications*

- ❓ **Master Product Requirements Index** (`0000_MASTER_PRD`)
  - Owner: system | Created: 2025-09-06

- 📝 **Unknown Product** (`PRD-2025-09-06-unknownproduct`)
  - Owner: product_team | Created: 2025-09-06
  - Links: prd:P, R, D, -, 2, 0, 2, 5, -, 0, 9, -, 0, 6, -, u, n, k, n, o, w, n, p, r, o, d, u, c, t

### 🏗️ Architecture
*Architectural decisions and designs*

- ❓ **Master Architecture Index** (`0000_MASTER_ARCH`)
  - Owner: system | Created: 2025-09-06

- 📝 **API Architecture Design** (`ARCH-2025-09-06-api-architecture-des`)
  - Owner: Dev Team | Created: 2025-09-06

- 📝 **Test Architecture with Python and TypeScript** (`ARCH-2025-09-06-test-architecture-wi`)
  - Owner: Dev Team | Created: 2025-09-06

### 🔗 Integrations
*Integration specifications and APIs*

- ❓ **Master Integrations Index** (`0000_MASTER_INTEGRATIONS`)
  - Owner: system | Created: 2025-09-06

### 🎨 User Experience
*UX designs and user research*

- ❓ **Master UX Index** (`0000_MASTER_UX`)
  - Owner: system | Created: 2025-09-06

- 📝 **Test UX with React and TypeScript** (`UX-2025-09-06-test-ux-with-react-a`)
  - Owner: UX Team | Created: 2025-09-06
  - Links: adr:ADR-0002, ADR-2025-09-06-test-standardized-id

### ⚙️ Implementation
*Implementation details and technical specs*

- ❓ **Master Implementation Index** (`0000_MASTER_IMPL`)
  - Owner: system | Created: 2025-09-06

- 📝 **User Authentication Implementation** (`IMPL-2025-09-06-user-authentication-`)
  - Owner: Backend Team | Created: 2025-09-06

### 📊 Executive
*Executive summaries and business documents*

- ❓ **Master Execution Index** (`0000_MASTER_EXEC`)
  - Owner: system | Created: 2025-09-06

- 📝 **Deployment Plan** (`EXEC-2025-09-06-deployment-plan`)
  - Owner: Ops Team | Created: 2025-09-06

### ✅ Tasks
*Task definitions and work items*

- ❓ **Master Tasks Index** (`0000_MASTER_TASKS`)
  - Owner: system | Created: 2025-09-06

### 📋 Architecture Decision Records
*Architectural decisions and their rationale*

- ❓ **Master ADR Index** (`0000_MASTER_ADR`)
  - Owner: system | Created: 2025-09-06

- 📝 **Technology Stack Selection** (`ADR-0001`)
  - Owner: system | Created: 2025-09-06
  - Status: proposed | Tags: technology, stack, payments

- 📝 **Test ADR Duplicate Prevention** (`ADR-0002`)
  - Owner: system | Created: 2025-09-06
  - Status: proposed | Tags: technology, stack, payments

- 📝 **Test Standardized ID Format** (`ADR-2025-09-06-test-standardized-id`)
  - Owner: system | Created: 2025-09-06
  - Status: proposed | Tags: technology, stack, payments

---

## Document Types

### Supported Document Types
- **PRD** (Product Requirements Document): Product specifications and requirements
- **ARCH** (Architecture): Architectural decisions and designs
- **IMPL** (Implementation): Implementation details and technical specs
- **EXEC** (Executive): Executive summaries and business documents
- **UX** (User Experience): UX designs and user research
- **INTEGRATIONS**: Integration specifications and APIs
- **TASKS**: Task definitions and work items
- **ADR** (Architecture Decision Record): Architectural decisions and rationale

### Auto ADR Linking
All document types automatically discover and link related ADRs based on:
- **Content similarity**: Title, tags, and content matching
- **Technology detection**: Automatic extraction of tech stack from titles
- **Weighted scoring**: Title (40%), tags (30%), content (20%), tech (10%)
- **Relevance threshold**: 10% minimum relevance for inclusion

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
