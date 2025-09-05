# Documentation Layer

This repo uses documentation to drive code generation, decisions, evaluation, and context building. The documentation system provides a comprehensive knowledge base that powers AI-assisted development.

---

## Document Index

### 📋 Product Requirements
*Product requirements and specifications*

- 📝 **Auth PRD** (`PRD-auth-prd`)
  - Owner: TBD | Created: 2025-09-05

- ✅ **User Authentication System** (`PRD-user-auth`)
  - Owner: Product Team | Created: 2025-09-05
  - Links: arch:ARCH-auth-architecture | ux:UX-auth-flow | impl:IMPL-auth-service | exec:EXEC-auth-deployment

- 📝 **Test PRD** (`PRD-test-prd`)
  - Owner: TBD | Created: 2025-09-05

### 🏗️ Architecture
*Architectural decisions and designs*

- 📝 **Auth Architecture** (`ARCH-auth-architecture`)
  - Owner: TBD | Created: 2025-09-05
  - Links: prd:P, R, D, -, a, u, t, h, -, p, r, d

- 📝 **API Architecture** (`ARCH-api-architecture`)
  - Owner: John Doe | Created: 2025-09-05
  - Links: prd:PRD-test-prd | ux:UX-001

### 🔗 Integrations
*Integration specifications and APIs*

- ✅ **Authentication Database Integration** (`INT-auth-database`)
  - Owner: Backend Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | impl:IMPL-auth-service | exec:EXEC-auth-deployment

### 🎨 User Experience
*UX designs and user research*

- ✅ **Authentication User Experience Flow** (`UX-auth-flow`)
  - Owner: UX Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | impl:IMPL-auth-service | exec:EXEC-auth-deployment

- 📝 **Placeholder UX** (`UX-001`)
  - Owner: TBD | Created: 2025-09-05

- 📝 **User Dashboard Design** (`UX-user-dashboard-desig`)
  - Owner: Jane Smith | Created: 2025-09-05

- 📝 **UX-001 Design** (`UX-ux-001-design`)
  - Owner: Designer | Created: 2025-09-05

### ⚙️ Implementation
*Implementation details and technical specs*

- 📝 **Auth Implementation Plan** (`IMPL-auth-implementation-plan`)
  - Owner: TBD | Created: 2025-09-05
  - Links: prd:PRD-auth-prd | arch:ARCH-auth-architecture

- ❓ **Authentication Service Implementation** (`IMPL-auth-service`)
  - Owner: Backend Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | integrations:INT-auth-database | ux:UX-auth-flow | exec:EXEC-auth-deployment

- 📝 **Auth Implementation Plan** (`IMPL-auth-implementation-`)
  - Owner: TBD | Created: 2025-09-05

### 📊 Executive
*Executive summaries and business documents*

- 📝 **Auth Execution Plan** (`EXEC-auth-execution-plan`)
  - Owner: TBD | Created: 2025-09-05
  - Links: impl:IMPL-auth-implementation-plan | prd:PRD-auth-prd

- ❓ **Authentication Service Deployment** (`EXEC-auth-deployment`)
  - Owner: DevOps Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | integrations:INT-auth-database | impl:IMPL-auth-service

### ✅ Tasks
*Task definitions and work items*

- ❓ **Deploy Authentication Service to Production** (`TASK-auth-deployment`)
  - Owner: DevOps Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | exec:EXEC-auth-deployment | impl:IMPL-auth-service

- ❓ **Implement Authentication Service Core Features** (`TASK-auth-implementation`)
  - Owner: Backend Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | impl:IMPL-auth-service | integrations:INT-auth-database

- ❓ **Set up Authentication Service Project** (`TASK-auth-setup`)
  - Owner: Backend Team | Created: 2025-09-05
  - Links: prd:PRD-user-auth | arch:ARCH-auth-architecture | impl:IMPL-auth-service | exec:EXEC-auth-deployment

- ❓ **Auth: login form UI** (`TASK-auth-login-form-ui`)
  - Owner: Frontend Team | Created: 2025-09-05
  - Links: prd:PRD-auth-prd | impl:IMPL-auth-implementation-plan

- ❓ **Auth: cookie storage & http client** (`TASK-auth-cookie-storage-http-client`)
  - Owner: Frontend Team | Created: 2025-09-05
  - Links: prd:PRD-auth-prd | impl:IMPL-auth-implementation-plan

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

### Context Generation
- **Generate context**: `python3 builder/cli.py plan:auto <file>` → creates `pack_context.json` and `context.md`
- **Enhanced context**: `python3 builder/cli.py ctx:build-enhanced <file> --purpose implement`
- **Explain selection**: `python3 builder/cli.py ctx:explain` → shows why items were selected
- **Generate prompts**: `python3 builder/cli.py ctx:pack` → creates prompt blocks for AI

### Documentation Management
- **Create documents**: `python3 builder/cli.py doc:new <type> --title "Title"`
- **Set links**: `python3 builder/cli.py doc:set-links <file> --prd PRD-001 --arch ARCH-001`
- **Validate docs**: `python3 builder/cli.py doc:check` → validates front-matter and structure
- **Update index**: `python3 builder/cli.py doc:index` → regenerates this index

### Quality Assurance
- **Documentation quality**: `pnpm run docs:all` → markdown linting and spell checking
- **Code evaluation**: `python3 builder/cli.py eval:objective <file>` → measure code quality
- **Interactive evaluation**: `python3 builder/cli.py eval:objective <file> --server`
- **Rules checking**: `python3 builder/cli.py rules:check "src/**/*.ts" --feature auth`

### Context System
- **Graph statistics**: `python3 builder/cli.py ctx:graph:stats` → shows node/edge counts
- **Context diffing**: `python3 builder/cli.py ctx:diff <old.json> <new.json>` → compare contexts
- **Budget management**: `python3 builder/cli.py ctx:budget` → manage token allocations
