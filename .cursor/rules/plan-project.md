# Plan Project

## Description
Create project plan through guided interview questions and analysis.

## Usage
```bash
cb plan
# or
@rules/plan-project
```

## Agent Instructions
1. Execute the plan command using Code Builder CLI
2. Follow the guided interview process
3. Answer questions based on project requirements
4. Review generated planning documents

## Expected Outputs
- `/home/rmans/projects/code-builder/cb_docs/planning/interview.json` - Interview responses
- `/home/rmans/projects/code-builder/cb_docs/planning/assumptions.md` - Documented assumptions
- `/home/rmans/projects/code-builder/cb_docs/planning/decisions.md` - Key decisions made

## Flags
- `--persona [dev|pm|ai]` - Interview persona (default: dev)
- `--noninteractive` - Use defaults instead of prompts
- `--auto-analyze` - Automatically run analysis if not done

## Examples
```bash
# Interactive planning
cb plan

# Developer persona
cb plan --persona dev

# Non-interactive with defaults
cb plan --noninteractive

# Auto-analyze then plan
cb plan --auto-analyze
```

## Context
This command has been selected based on current project state and dependencies.
