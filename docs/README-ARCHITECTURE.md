# System Architecture 🏗️

Code Builder is built around **10 core systems** working together:

## 1. **Context Management System**
- **Graph-based selection**: Discovers related items through explicit links and code proximity
- **Intelligent ranking**: Scores items based on relevance, feature matching, and recency  
- **Budget management**: Token-aware packaging with per-purpose allocations
- **Caching**: SHA256-based cache keys for fast, deterministic context generation

## 2. **Discovery System** 
- **Interactive interviews**: Guided prompts for new and existing products
- **Code analysis**: Deep analysis of codebase structure, patterns, and dependencies
- **Synthesis engine**: Combines findings into structured insights
- **Document generation**: Auto-generates PRDs, ADRs, and technical specifications
- **Validation**: Ensures generated documents meet quality standards

## 3. **Multi-Agent Orchestration**
- **Task management**: Parse and execute structured tasks from TASK-*.md files
- **Agent tracking**: Session management with ownership protection
- **Dependency resolution**: Intelligent task scheduling based on dependencies
- **Cursor integration**: Launch multiple Cursor agents for parallel execution
- **Progress monitoring**: Real-time tracking of agent activities and file creation

## 4. **Evaluation System**
- **Objective evaluation**: Automated scoring based on test coverage, linting, and metrics
- **Subjective evaluation**: AI-powered quality assessment with structured prompts
- **ABC iteration**: Systematic code improvement through variant generation and comparison
- **Comprehensive reporting**: Historical data, trends, and actionable insights

## 5. **Document Management**
- **Master synchronization**: Automated maintenance of 0000_MASTER_*.md index files
- **Cross-reference cleanup**: Automatic removal of broken links when documents are deleted
- **Template system**: Jinja2-based document generation with consistent formatting
- **8 document types**: PRD, ADR, ARCH, EXEC, IMPL, INTEGRATIONS, TASKS, UX

## 6. **Rules & Guardrails System**
- **Hierarchical rules**: Global → Project → Stack → Feature precedence
- **Conflict detection**: Automatic identification of rule contradictions
- **Guardrails enforcement**: Forbidden patterns and security validation
- **PII detection**: Automatic detection and redaction of sensitive information

## 7. **Cache & Performance System**
- **Intelligent caching**: SHA256-based cache keys for deterministic context generation
- **Performance optimization**: Fast context retrieval and document processing
- **Memory management**: Efficient handling of large codebases and context packs
- **Cleanup automation**: Automatic removal of stale cache entries

## 8. **PR Ergonomics System**
- **Pull request templates**: Auto-populated with context and validation checklists
- **Documentation validation**: Automated checks for completeness and quality
- **Context preview**: First 200 lines of generated context in PR descriptions
- **Reviewer guidance**: Clear instructions for code review and validation

## 9. **Telemetry & Metrics System** 🆕
- **Command tracking**: Comprehensive logging of all CLI command executions
- **Performance analytics**: Timing, success rates, and usage patterns
- **Usage statistics**: Command frequency, user behavior, and system utilization
- **Data persistence**: JSON-based storage with file rotation and cleanup
- **Sensitive data protection**: Automatic redaction of passwords and API keys

## 10. **Quality Gates System** 🆕
- **Release validation**: 10 comprehensive checks for release readiness
- **Idempotency testing**: Ensures operations can be safely repeated
- **Parity validation**: Verifies consistency across different environments
- **Determinism checks**: Confirms reproducible builds and outputs
- **UX validation**: Tests Cursor integration and user experience
- **Test suite integration**: Automated quality testing with detailed reporting

---

**Next**: [System Statistics & Features](README-STATISTICS.md) | [Quickstart Guide](README-QUICKSTART.md) | [Command Reference](README-COMMANDS.md)
