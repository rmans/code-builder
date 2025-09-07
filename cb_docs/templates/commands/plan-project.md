---
id: plan-project
title: Plan Project
description: Create project plan through guided interview
status: active
created: 2025-01-15
updated: 2025-01-15
owner: system
domain: planning
priority: 9
agent_type: backend
dependencies: [analyze-project]
tags: [planning, interview, project]
---

# Command: Plan Project

## Description
Creates a comprehensive project plan through guided interview questions and analysis.

## Usage
```bash
cb plan
# or
@rules/plan-project
```

## Outputs
- `cb_docs/planning/interview.json` - Interview responses
- `cb_docs/planning/assumptions.md` - Documented assumptions
- `cb_docs/planning/decisions.md` - Key decisions made

## Flags
- `--persona TYPE` - Interview persona (dev|pm|ai)
- `--noninteractive` - Use defaults instead of prompts

## Examples
```bash
# Interactive planning
cb plan

# Developer persona
cb plan --persona dev

# Non-interactive with defaults
cb plan --noninteractive
```
