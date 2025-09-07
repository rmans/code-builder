# Documentation Layer

This repo uses docs to drive codegen, decisions, and evaluation. The documentation system is built around **8 document types** with **automated master synchronization** and **cross-reference management**.

---

## 📊 Document System Overview

The documentation system provides:
- **8 Document Types**: PRD, ADR, ARCH, EXEC, IMPL, INTEGRATIONS, TASKS, UX
- **Master Synchronization**: Automated maintenance of `0000_MASTER_*.md` index files
- **Cross-Reference Cleanup**: Automatic removal of broken links when documents are deleted
- **Template System**: Jinja2-based document generation with consistent formatting
- **41 Markdown Files**: Comprehensive documentation across the system

---

## Document Index

### 📋 Product Requirements (PRD)
*Product requirements and specifications*

- ✅ **Master Product Requirements Index** (`0000_MASTER_PRD.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when PRD-*.md files are created/modified/deleted

### 🏗️ Architecture (ARCH)
*Architectural decisions and designs*

- ✅ **Master Architecture Index** (`0000_MASTER_ARCH.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when ARCH-*.md files are created/modified/deleted

### 🔗 Integrations (INTEGRATIONS)
*Integration specifications and APIs*

- ✅ **Master Integrations Index** (`0000_MASTER_INTEGRATIONS.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when INTEGRATIONS-*.md files are created/modified/deleted

### 🎨 User Experience (UX)
*UX designs and user research*

- ✅ **Master UX Index** (`0000_MASTER_UX.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when UX-*.md files are created/modified/deleted

### ⚙️ Implementation (IMPL)
*Implementation details and technical specs*

- ✅ **Master Implementation Index** (`0000_MASTER_IMPL.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when IMPL-*.md files are created/modified/deleted

### 📊 Executive (EXEC)
*Executive summaries and business documents*

- ✅ **Master Execution Index** (`0000_MASTER_EXEC.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when EXEC-*.md files are created/modified/deleted

### ✅ Tasks (TASK)
*Task definitions and work items*

- ✅ **Master Tasks Index** (`0000_MASTER_TASKS.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when TASK-*.md files are created/modified/deleted

### 📋 Architecture Decision Records (ADR)
*Architectural decisions and their rationale*

- ✅ **Master Decision Index** (`0000_MASTER_ADR.md`)
  - Owner: system | Created: 2025-09-06 | Status: Active
  - **Auto-synced**: Updates automatically when ADR-*.md files are created/modified/deleted

---

## 🔄 Master Synchronization System

The documentation system includes **automated master file synchronization** that keeps all `0000_MASTER_*.md` files up to date:

### Automatic Updates
- **Document Creation**: When you create a new document (e.g., `PRD-2025-01-15-example.md`), the master file automatically updates
- **Document Modification**: Changes to document metadata (title, status, domain) are reflected in the master index
- **Document Deletion**: When documents are deleted, they're automatically removed from the master index
- **Cross-Reference Cleanup**: Broken links are automatically cleaned up when referenced documents are deleted

### Manual Synchronization
```bash
# Sync all master files
python3 builder/core/cli.py master:sync

# Sync specific document type
python3 builder/core/cli.py master:sync --type prd

# Clean up cross-references
python3 builder/core/cli.py master:sync --cleanup-refs

# Preview changes without applying
python3 builder/core/cli.py master:sync --dry-run
```

---

## ADRs (docs/adrs/)
- `0000_MASTER_ADR.md` = index of all decisions
- Sub ADRs like `ADR-0001.md` created by `builder:adr:new`
- Each ADR records context, decision, consequences, alternatives
- **Auto-synced**: Master index updates automatically

---

## Templates (docs/templates/)
- Jinja2 templates for ADRs and specs
- Used by CLI to render files
- Consistent formatting across all document types
- Supports variables and conditional rendering

---

## Rules (docs/rules/)
- `00-global.md`, `10-project.md` = global + project-wide rules
- `stack/` (e.g. typescript, react, http-client)
- `feature/` (auth, content-engine, etc.)
- `guardrails.json` = forbidden patterns + hints
- **Hierarchical precedence**: Global → Project → Stack → Feature

---

## Evaluation (docs/eval/)
- `config.yaml` = evaluation weights and configuration
- Defines objective vs subjective weight distribution
- Configures tool paths and scoring weights
- Supports multiple evaluation frameworks

---

## Usage Guides
- `USAGE-Cursor-Evaluation.md` = Complete evaluation workflow guide
- `CURSOR-Custom-Commands.md` = Cursor integration setup
- Comprehensive documentation for all 53 CLI commands

---

## 🚀 Usage Workflows

### Document Creation Workflow
1. **Create document**: `python3 builder/core/cli.py doc:new prd --title "My PRD"`
2. **Auto-sync**: Master file automatically updates
3. **Edit document**: Add content, metadata, and links
4. **Sync references**: `python3 builder/core/cli.py master:sync --cleanup-refs`

### Context Generation Workflow
1. **Generate context**: `python3 builder/core/cli.py plan:auto <file>`
2. **Review context**: Check `builder/cache/pack_context.json`
3. **Use with AI**: Copy context to Cursor or other AI tools
4. **Evaluate results**: `python3 builder/core/cli.py eval:objective <file>`

### Discovery Workflow
1. **Start discovery**: `python3 builder/core/cli.py discover:new --interactive`
2. **Analyze codebase**: `python3 builder/core/cli.py discover:analyze --repo-root`
3. **Generate documents**: Auto-generate PRDs, ADRs, and specifications
4. **Validate results**: `python3 builder/core/cli.py discover:validate <context_file>`
