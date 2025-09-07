---
description: Enforce first-class error handling in TypeScript
globs: src/**/*.ts,src/**/*.tsx
alwaysApply: true
---
# Use Real Error Types — Never Throw Strings
## Rule
- Never throw string literals
- Always throw Error or subclasses
- Prefer error factory / domain errors
