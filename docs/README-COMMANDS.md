# Command Reference 📋

## Command Overview

Code Builder provides **104+ commands** organized into specialized modules:

### 🔍 Discovery Commands (6)
- `discover:interview` - Interactive discovery interviews
- `discover:analyze` - Analyze codebase structure and patterns
- `discover:report` - Generate discovery reports and summaries
- `discover:validate` - Validate discovery findings and outputs
- `discover:template` - Generate discovery templates
- `discover:questions` - Manage discovery question sets

### 📝 Document Commands (8)
- `doc:create` - Create new documents (PRD, ADR, etc.)
- `doc:update` - Update existing documents
- `doc:validate` - Validate document structure and content
- `doc:template` - Generate document templates
- `doc:sync` - Synchronize document cross-references
- `doc:cleanup` - Clean up orphaned documents
- `doc:export` - Export documents in various formats
- `doc:import` - Import documents from external sources

### 🧠 Context Commands (12)
- `ctx:build` - Build context for specific files
- `ctx:build-enhanced` - Enhanced context building with advanced features
- `ctx:pack` - Create context packs for multiple files
- `ctx:validate` - Validate context quality and completeness
- `ctx:cache` - Manage context cache
- `ctx:cleanup` - Clean up stale context data
- `ctx:export` - Export context in various formats
- `ctx:import` - Import context from external sources
- `ctx:analyze` - Analyze context usage and patterns
- `ctx:optimize` - Optimize context for specific purposes
- `ctx:merge` - Merge multiple context sources
- `ctx:split` - Split large context into manageable chunks

### 🤖 Agent Commands (4)
- `agent:launch` - Launch new agent sessions
- `agent:status` - Check agent status and progress
- `agent:cleanup` - Clean up agent sessions
- `agent:setup` - Set up agent configuration

### 📊 Telemetry & Status Commands (3) 🆕
- `status` - System status and health check
- `history` - Command execution history
- `metrics` - Usage statistics and analytics

### 🎯 Orchestration Commands (12)
- `tasks:execute` - Execute multiple tasks with orchestration
- `tasks:schedule` - Schedule task execution
- `tasks:monitor` - Monitor task progress
- `tasks:cleanup` - Clean up completed tasks
- `tasks:validate` - Validate task definitions
- `tasks:optimize` - Optimize task execution order
- `tasks:retry` - Retry failed tasks
- `tasks:cancel` - Cancel running tasks
- `tasks:status` - Check task status
- `tasks:list` - List available tasks
- `tasks:create` - Create new tasks
- `tasks:update` - Update existing tasks

### 📊 Evaluation Commands (4)
- `eval:objective` - Run objective evaluation
- `eval:subjective` - Run subjective evaluation
- `eval:report` - Generate evaluation reports
- `eval:compare` - Compare evaluation results

### 🔄 Iteration Commands (4)
- `iter:cursor` - Generate code variants for Cursor evaluation
- `iter:finish` - Complete iteration with winner selection
- `iter:compare` - Compare iteration variants
- `iter:history` - View iteration history

### 🧹 Utility Commands (3)
- `util:cleanup` - Clean up temporary files and cache
- `util:validate` - Validate system configuration
- `util:backup` - Backup system data and configuration

### 🎯 Quality Gates Commands (3) 🆕
- `quality:gates` - Run all quality gates
- `quality:check` - Run specific quality checks
- `quality:report` - Generate quality gate reports

### 📚 Master Sync Commands (4)
- `master:sync` - Synchronize specific master files
- `master:sync-all` - Synchronize all master files
- `master:validate` - Validate master file integrity
- `master:backup` - Backup master files

## Command Usage Examples

### Discovery Workflow
```bash
# Start discovery process
python3 -m builder.core.cli discover:interview --type new-product

# Analyze existing codebase
python3 -m builder.core.cli discover:analyze --path src/ --output analysis.json

# Generate comprehensive report
python3 -m builder.core.cli discover:report --input analysis.json --output report.md
```

### Context Building
```bash
# Basic context generation
python3 -m builder.core.cli ctx:build src/main.ts --purpose implement

# Enhanced context with specific focus
python3 -m builder.core.cli ctx:build-enhanced tests/ --purpose test --focus unit

# Create context pack for review
python3 -m builder.core.cli ctx:pack src/ --purpose review --output review-pack.json
```

### Task Management
```bash
# Create new task
python3 -m builder.core.cli task:create "Implement user authentication" --priority high

# Execute single task
python3 -m builder.core.cli task:execute TASK-2025-09-07-AUTH --agent-count 2

# Execute multiple tasks
python3 -m builder.core.cli tasks:execute --parallel 3 --filter "priority:high"
```

### Quality & Evaluation
```bash
# Run quality gates
python3 -m builder.core.cli quality:gates --verbose --output quality-report.json

# Objective evaluation
python3 -m builder.core.cli eval:objective src/main.ts --output eval-results.json

# Generate evaluation report
python3 -m builder.core.cli eval:report --input eval-results.json --output report.md
```

### Telemetry & Monitoring
```bash
# Check system status
python3 -m builder.core.cli status --verbose

# View command history
python3 -m builder.core.cli history --limit 20 --format json

# Get usage metrics
python3 -m builder.core.cli metrics --period 7d --output metrics.json
```

## Command Options

### Common Options
- `--verbose` - Enable verbose output
- `--output` - Specify output file
- `--format` - Choose output format (json, yaml, markdown)
- `--dry-run` - Preview changes without executing
- `--help` - Show command help

### Context Options
- `--purpose` - Context purpose (implement, test, review, debug)
- `--focus` - Specific focus area
- `--budget` - Token budget limit
- `--cache` - Enable/disable caching

### Task Options
- `--parallel` - Number of parallel agents
- `--filter` - Filter tasks by criteria
- `--priority` - Task priority level
- `--agent-count` - Number of agents to use

### Quality Options
- `--checks` - Specific quality checks to run
- `--threshold` - Quality threshold for passing
- `--report` - Generate detailed reports

---

**Previous**: [Quickstart Guide](README-QUICKSTART.md) | **Next**: [Directory Structure](README-DIRECTORY.md) | [System Architecture](README-ARCHITECTURE.md)
