---
id: TASK-2025-01-02-base-rule-always
title: Base Repo Rule (Always, Migrated)
description: Migrate existing 00-global.md into concise Always rule (<500 tokens)
status: pending
created: 2025-01-15
updated: 2025-01-15
owner: rules-agent
domain: rules
priority: 25
agent_type: backend
dependencies: [TASK-2025-01-01-rules-migration-setup]
tags: [always, style, safety]
---

# Task: Base Repo Rule (Always)

## Implementation Steps
- Convert docs/rules/00-global.md → .cursor/rules/base.mdc keeping canon guidance.
- Ensure globs: [], alwaysApply: true, sections Do/Don't/Examples.

## Real MDC (sample frame)
---
description: Repo-wide conventions (purity, errors, tests, secrets)
globs: []
alwaysApply: true
---
## Do
- Small/pure functions; composition over inheritance.
- Exhaustive error handling (TS `never` / Py `match`).
- Co-locate tests as `*.spec.*`.
## Don't
- Don't print secrets/stack traces by default.
## Examples
```ts
function assertNever(x: never): never { throw new Error(`Unhandled: ${x}`) }
```

## Commands
python3 builder/core/cli.py rules:validate

## Acceptance Criteria
- Migrated content preserved; <500 tokens; passes validation.

## Testing / Verification
- Golden snapshot for migrated base.

## Rollback
- git mv .cursor/rules/base.mdc .cursor/rules/base.mdc.bak && restore 00-global.md
