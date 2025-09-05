---
description: Global defaults that apply everywhere
globs: src/**/*,test/**/*
alwaysApply: true
---
# Global Rules
- Keep files under 300 LOC.
- Tests mirror acceptance criteria 1:1.
- Public APIs must include JSDoc/docstrings.

## Task Execution
- **Never get hung up on verification tasks** - if core functionality works, declare success
- **Avoid repeated terminal commands** that don't add value
- **Stop after 2-3 attempts** on the same task - don't loop endlessly
- **Focus on delivering working solutions** rather than perfect verification
- **Never re-run successful commands** unless explicitly requested - if it worked once, it's done
- **One verification run maximum** unless user asks for more - additional runs are waste
- **Always commit after successful completion** - commit changes when task is done successfully

## Rule Creation Guidelines
- **Global rules** (`00-global.md`) - Universal coding principles, task execution, rule system guidelines
- **Project rules** (`10-project.md`) - Project-specific conventions, naming, file organization, workflows
- **Stack rules** (`stack/*.md`) - Technology-specific standards (TypeScript, React, etc.)
- **Feature rules** (`feature/*.md`) - Feature-specific requirements and constraints
- **Implementation rules** (`15-implementation.md`) - Code quality, reliability, performance standards
- **When in doubt** - Ask: "Is this universal or project-specific?" Universal → global, specific → project

