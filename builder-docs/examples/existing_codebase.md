# Example: Existing Codebase Analysis

This example demonstrates how to analyze and document an existing codebase using the Code Builder system.

## Overview

We'll analyze an existing React application to understand its architecture, identify technical debt, and create improvement recommendations.

## Step 1: Analyze Existing Code

```bash
# First, let's see what files we have
find src/ -name "*.tsx" -o -name "*.ts" -o -name "*.js" | head -10

# Example output:
# src/components/Header.tsx
# src/components/TaskList.tsx
# src/hooks/useTasks.ts
# src/services/api.ts
# src/utils/helpers.ts
```

## Step 2: Create Analysis PRD

```bash
# Create PRD for codebase analysis
python builder/cli.py doc:new prd --title "Codebase Analysis and Improvement"

# This creates: docs/prd/PRD-YYYY-MM-DD-codebase-analysis-and-improvement.md
```

## Step 3: Fill in Analysis PRD

Edit the generated PRD with:

```markdown
---
type: prd
id: PRD-2025-09-06-codebase-analysis
title: Codebase Analysis and Improvement
status: draft
owner: engineering_team
created: 2025-09-06
links:
  prd: PRD-2025-09-06-codebase-analysis
  adr: []
  arch: []
  exec: []
  impl: []
  integrations: []
  tasks: []
  ux: []
---

# Product Requirements Document: Codebase Analysis and Improvement

## Problem

Our existing React application has grown organically and needs analysis to identify:
- Technical debt and code quality issues
- Architecture improvements
- Performance bottlenecks
- Security vulnerabilities
- Testing gaps

## Goals

- Understand current codebase architecture
- Identify technical debt and improvement opportunities
- Create actionable improvement plan
- Establish coding standards and best practices
- Improve maintainability and performance

## Requirements

### Analysis Requirements
- Static code analysis of all TypeScript/JavaScript files
- Architecture pattern identification
- Dependency analysis and security audit
- Performance profiling and optimization opportunities
- Test coverage analysis

### Documentation Requirements
- Current architecture documentation
- Technical debt inventory
- Improvement recommendations with priorities
- Migration strategy for major changes
- Coding standards and guidelines

## Acceptance Criteria

- [ ] Complete inventory of all source files and their purposes
- [ ] Identification of architectural patterns and anti-patterns
- [ ] List of technical debt items with severity ratings
- [ ] Performance analysis with specific bottlenecks identified
- [ ] Security audit results with vulnerability assessment
- [ ] Test coverage report with gaps identified
- [ ] Prioritized improvement roadmap
- [ ] Updated architecture documentation

## Success Metrics

- 100% of source files analyzed and documented
- 90% of technical debt items identified and prioritized
- Performance improvements identified for top 5 bottlenecks
- Security vulnerabilities reduced to zero high/critical issues
- Test coverage increased to 80%+

## Technical Stack

- Analysis Tools: ESLint, TypeScript compiler, dependency scanners
- Documentation: Markdown with Mermaid diagrams
- Testing: Jest, React Testing Library
- Performance: Lighthouse, Web Vitals
- Security: npm audit, Snyk, OWASP ZAP
```

## Step 4: Generate Discovery Context

```bash
# Generate discovery context for analysis
python builder/cli.py discover:regenerate --all

# This analyzes the PRD and creates discovery context
```

## Step 5: Analyze Specific Components

```bash
# Analyze main components
python builder/cli.py ctx:build src/components/TaskList.tsx \
  --purpose analyze \
  --feature task-management \
  --stacks react,typescript \
  --token-limit 6000

# Analyze hooks
python builder/cli.py ctx:build src/hooks/useTasks.ts \
  --purpose analyze \
  --feature state-management \
  --stacks react,typescript \
  --token-limit 4000

# Analyze services
python builder/cli.py ctx:build src/services/api.ts \
  --purpose analyze \
  --feature api-integration \
  --stacks typescript,http \
  --token-limit 5000
```

## Step 6: Create Architecture Analysis

```bash
# Create architecture analysis document
python builder/cli.py doc:new arch --title "Current Architecture Analysis"

# Edit with findings from component analysis
```

## Step 7: Generate Technical Debt Report

```bash
# Create technical debt document
python builder/cli.py doc:new impl --title "Technical Debt Analysis"

# This will reference the architecture analysis
```

## Step 8: Run Comprehensive Analysis

```bash
# Run discovery on all document types
python builder/cli.py discover:regenerate --all

# This generates comprehensive analysis outputs
```

## Step 9: Generate Improvement Plan

```bash
# Create execution plan for improvements
python builder/cli.py doc:new exec --title "Codebase Improvement Plan"

# This creates a prioritized improvement roadmap
```

## Step 10: Validate All Documentation

```bash
# Check all generated documentation
python builder/cli.py doc:check

# This validates all documents are properly formatted
```

## Step 11: Generate Context for Specific Improvements

```bash
# Build context for a specific improvement task
python builder/cli.py ctx:build src/components/Header.tsx \
  --purpose refactor \
  --feature component-optimization \
  --stacks react,typescript \
  --token-limit 6000

# Use context pack for AI-assisted refactoring
python builder/cli.py ctx:pack --stdout
```

## Expected Analysis Outputs

After running all steps, you should have:

1. **Analysis PRD**: `docs/prd/PRD-YYYY-MM-DD-codebase-analysis-and-improvement.md`
2. **Architecture Analysis**: `docs/arch/ARCH-YYYY-MM-DD-current-architecture-analysis.md`
3. **Technical Debt Report**: `docs/impl/IMPL-YYYY-MM-DD-technical-debt-analysis.md`
4. **Improvement Plan**: `docs/exec/EXEC-YYYY-MM-DD-codebase-improvement-plan.md`
5. **Discovery Contexts**: Multiple `.yml` files in `builder/cache/discovery/`
6. **Context Packs**: Multiple `pack_context.json` files for different components
7. **Discovery Outputs**: Analysis reports in `builder/cache/discovery_outputs/`

## Verification Commands

```bash
# Verify all discovery contexts were generated
ls -la builder/cache/discovery/*.yml

# Verify context packs were created
ls -la builder/cache/pack_context.json

# Verify all documentation is valid
python builder/cli.py doc:check

# Verify discovery outputs exist
ls -la builder/cache/discovery_outputs/

# Check specific analysis outputs
find builder/cache/discovery_outputs/ -name "*analysis*" -o -name "*debt*"
```

## Common Analysis Patterns

### Component Analysis
```bash
# Analyze React components
python builder/cli.py ctx:build src/components/ComponentName.tsx \
  --purpose analyze \
  --feature component-architecture \
  --stacks react,typescript \
  --token-limit 5000
```

### Service Analysis
```bash
# Analyze API services
python builder/cli.py ctx:build src/services/ServiceName.ts \
  --purpose analyze \
  --feature api-design \
  --stacks typescript,http \
  --token-limit 4000
```

### Hook Analysis
```bash
# Analyze custom hooks
python builder/cli.py ctx:build src/hooks/useHookName.ts \
  --purpose analyze \
  --feature state-management \
  --stacks react,typescript \
  --token-limit 3000
```

## Troubleshooting

- If analysis fails on specific files, check file syntax and imports
- If discovery context generation fails, verify PRD has proper structure
- If context building fails, ensure target files exist and are readable
- Check `builder/cache/` logs for detailed error information
- Use `--verbose` flag for more detailed output: `python builder/cli.py discover:regenerate --types all --verbose`
