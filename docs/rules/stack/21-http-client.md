---
description: Centralize HTTP behavior with a shared client
globs: src/**/*.ts,src/**/*.tsx
alwaysApply: true
---
# One HTTP Client — Retries, Timeouts, Interceptors
## Rule
- Never use raw fetch or axios.create() in features
- Always use http from src/utils/http.ts
