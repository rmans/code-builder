---
description: Project conventions (naming, exports, tests)
globs: src/**/*,test/**/*.ts
alwaysApply: true
---
# Project Rules
## Rule
1. **Always use** kebab-case for filenames
2. **Always use** camelCase for vars, PascalCase for React components
3. **Always use** named exports (no default exports)
4. **Always create** test files that mirror acceptance criteria

## File Organization
- **Test files go in .testfiles/** - all temporary test files, sample responses, and development artifacts
- **Test results go in .testresults/** - evaluation outputs, test artifacts, and generated reports
- **Never create test files in root** - use .testfiles/ for abc_cursor_response.json, sample_cursor_response.json, etc.
- **Never create test results in root** - use .testresults/ for evaluation reports, test outputs, etc.
- **Keep root directory clean** - only essential project files in root
