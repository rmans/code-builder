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

## GitHub Actions Best Practices
- **Always add explicit permissions** - workflows using github-script must have permissions block with pull-requests: write and issues: write
- **Wrap API calls in try-catch** - all github.rest API calls must be wrapped in try-catch blocks to handle permission errors
- **Use continue-on-error for comments** - comment creation should not fail the entire workflow
- **Log fallback content** - when comment creation fails, log the content that would have been posted
- **Test permission requirements** - verify workflows work with minimal required permissions
- **Handle 403 errors gracefully** - provide clear error messages and fallback behavior

## Data Structure Consistency
- **Use correct field names** - always use the actual field names from generated data structures
- **Validate field names match** - ensure validation scripts use the same field names as the data they're validating
- **Check context pack structure** - verify field names in context packs match what validation expects
- **Test validation locally** - run validation scripts locally before committing to catch field name mismatches
- **Document field mappings** - clearly document which fields contain which data in generated structures
- **Never assume field names** - always check the actual generated data structure before writing validation code

## Terminal Usage
- **Always open new terminal** - when executing commands, start fresh terminal session
- **Avoid terminal reuse** - don't rely on previous terminal state or environment
- **Fresh shell for each command** - ensures clean environment and avoids hanging issues

