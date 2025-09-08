---
id: TASK-2025-01-03-typescript-react-rule
title: TypeScript/React Rule (Auto-Attached, Migrated)
description: Migrate stack/react.md into frontend-react.mdc scoped to apps/web and packages/ui
status: pending
created: 2025-01-15
updated: 2025-01-15
owner: fe-agent
domain: rules
priority: 40
agent_type: backend
dependencies: [TASK-2025-01-01-rules-migration-setup]
tags: [react, next, typescript]
---

# Task: TypeScript/React Rule

## Implementation Steps
- Map docs/rules/stack/react.md → .cursor/rules/frontend-react.mdc.
- Ensure array globs and concrete examples.

## MDC (frame)
---
description: React/Next patterns for apps/web & packages/ui
globs:
  - "apps/web/**/*.{ts,tsx,css}"
  - "packages/ui/src/**/*.{ts,tsx}"
alwaysApply: false
---
## Do
- Server components by default; "use client" only if needed.
- Server actions/loaders for data access; Tailwind for layout.
## Don't
- Don't fetch in client comps; avoid mixed styling.
## Examples
```ts
// apps/web/app/profile/actions.ts
export async function loadProfile(id: string) { /* ... */ }
```

## Commands
python3 builder/core/cli.py rules:validate

## Acceptance Criteria
- Valid FM, scoped globs, examples compile contextually.

## Testing / Verification
- Validator + path existence tests.

## Rollback
- Keep original under docs/rules/stack/react.md.bak
