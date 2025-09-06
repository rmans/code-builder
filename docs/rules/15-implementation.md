---
description: Implementation quality and reliability standards
globs: builder/**/*.py,src/**/*.ts,tests/**/*.ts
alwaysApply: true
---
# Implementation Rules

## Code Quality
- **Never create code that can hang** - avoid infinite loops, blocking operations, complex imports
- **Always add timeouts** for external operations and file parsing
- **Use safe error handling** - graceful degradation instead of crashes
- **Keep functions simple** - avoid complex nested operations that can fail

## Loop and Control Flow
- **Never use `while True:`** - always have clear exit conditions and timeouts
- **Always add timeouts** to polling loops and waiting operations
- **Use time-based conditions** instead of infinite loops (e.g., `while time.time() - start < timeout`)
- **Provide clear exit conditions** - make loop termination obvious and reliable
- **Add progress indicators** for long-running operations
- **Handle timeout scenarios** gracefully with helpful messages

## Performance
- **Fast execution** - code should complete quickly or have clear progress indicators
- **Minimal dependencies** - avoid heavy imports that can cause delays
- **Efficient algorithms** - use appropriate data structures and avoid O(n²) operations

## Reliability
- **Fail gracefully** - return neutral values instead of crashing
- **Handle missing files** - check existence before processing
- **Validate inputs** - ensure data is in expected format before use

## Context Pack Validation
- **Always generate fallback content** - if PRD/discovery data is missing, create default acceptance criteria
- **Validate RULES_DIR path** - ensure rules directory path calculation is correct (use 3 dirname() calls)
- **Check required fields** - context packs must have non-empty rules_markdown, acceptance_criteria, and code_excerpts
- **Test file existence** - verify target files exist before attempting to extract code excerpts
- **Provide meaningful defaults** - generate file-type-specific acceptance criteria when none are found
- **Never return empty arrays** - always populate required fields with fallback content

## Terminal Usage
- **Always open new terminal** - when executing commands, start fresh terminal session
- **Avoid terminal reuse** - don't rely on previous terminal state or environment
- **Fresh shell for each command** - ensures clean environment and avoids hanging issues

