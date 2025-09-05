---
description: Implementation quality and reliability standards
globs: builder/**/*.py,src/**/*.ts,test/**/*.ts
alwaysApply: true
---
# Implementation Rules

## Code Quality
- **Never create code that can hang** - avoid infinite loops, blocking operations, complex imports
- **Always add timeouts** for external operations and file parsing
- **Use safe error handling** - graceful degradation instead of crashes
- **Keep functions simple** - avoid complex nested operations that can fail

## Performance
- **Fast execution** - code should complete quickly or have clear progress indicators
- **Minimal dependencies** - avoid heavy imports that can cause delays
- **Efficient algorithms** - use appropriate data structures and avoid O(n²) operations

## Reliability
- **Fail gracefully** - return neutral values instead of crashing
- **Handle missing files** - check existence before processing
- **Validate inputs** - ensure data is in expected format before use

## Terminal Usage
- **Always open new terminal** - when executing commands, start fresh terminal session
- **Avoid terminal reuse** - don't rely on previous terminal state or environment
- **Fresh shell for each command** - ensures clean environment and avoids hanging issues

