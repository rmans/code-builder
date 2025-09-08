# Quickstart Guide 🚀

## Installation

```bash
# Clone the repository
git clone https://github.com/rmans/code-builder.git
cd code-builder

# Install dependencies
pip install -r requirements.txt
npm install

# Run the installation script
./scripts/install.sh
```

## Basic Usage

### 1. Discovery & Analysis
```bash
# Interactive discovery for new products
python3 -m builder.core.cli discover:interview --type new-product

# Analyze existing codebase
python3 -m builder.core.cli discover:analyze --path src/

# Generate discovery report
python3 -m builder.core.cli discover:report --output discovery-report.md
```

### 2. Context Generation
```bash
# Generate context for a specific file
python3 -m builder.core.cli ctx:build src/hello.ts --purpose implement

# Build enhanced context with specific focus
python3 -m builder.core.cli ctx:build-enhanced test/example.ts --purpose test

# Generate context pack for multiple files
python3 -m builder.core.cli ctx:pack src/ --purpose review
```

### 3. Task Management
```bash
# Create a new task
python3 -m builder.core.cli task:create "Implement user authentication"

# Execute a single task
python3 -m builder.core.cli task:execute TASK-2025-09-07-AUTH

# Execute multiple tasks with orchestration
python3 -m builder.core.cli tasks:execute --parallel 3
```

### 4. Quality & Evaluation
```bash
# Run quality gates
python3 -m builder.core.cli quality:gates --verbose

# Evaluate code quality
python3 -m builder.core.cli eval:objective src/hello.ts

# Generate evaluation report
python3 -m builder.core.cli eval:report --output quality-report.md
```

### 5. Telemetry & Status
```bash
# Check system status
python3 -m builder.core.cli status

# View command history
python3 -m builder.core.cli history --limit 10

# Get usage statistics
python3 -m builder.core.cli metrics --summary
```

## Typical Workflow

### 1. **Project Discovery**
```bash
# Start with discovery for new projects
python3 -m builder.core.cli discover:interview --type new-product
python3 -m builder.core.cli discover:analyze --path src/
python3 -m builder.core.cli discover:report
```

### 2. **Context Building**
```bash
# Generate context for development
python3 -m builder.core.cli ctx:build src/main.ts --purpose implement
python3 -m builder.core.cli ctx:build-enhanced tests/ --purpose test
```

### 3. **Task Execution**
```bash
# Create and execute tasks
python3 -m builder.core.cli task:create "Add error handling"
python3 -m builder.core.cli task:execute TASK-2025-09-07-ERROR-HANDLING
```

### 4. **Quality Validation**
```bash
# Run quality checks
python3 -m builder.core.cli quality:gates
python3 -m builder.core.cli eval:objective src/main.ts
```

### 5. **Documentation & Review**
```bash
# Sync master files
python3 -m builder.core.cli master:sync-all

# Generate PR context
python3 -m builder.core.cli ctx:build-enhanced . --purpose review
```

## Configuration

### Environment Setup
```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
npm install

# Configure Cursor integration
python3 -m builder.core.cli agent:setup
```

### Project Configuration
```bash
# Initialize project rules
python3 -m builder.core.cli rules:init

# Set up quality gates
python3 -m builder.core.cli quality:setup

# Configure telemetry
python3 -m builder.core.cli telemetry:setup
```

## Advanced Features

### Multi-Agent Orchestration
```bash
# Launch multiple agents for parallel work
python3 -m builder.core.cli agents:launch --count 3 --tasks TASK-2025-09-07-*

# Monitor agent progress
python3 -m builder.core.cli agents:status

# Clean up agent sessions
python3 -m builder.core.cli agents:cleanup
```

### ABC Iteration
```bash
# Generate code variants
python3 -m builder.core.cli iter:cursor src/hello.ts

# Complete iteration with winner selection
python3 -m builder.core.cli iter:finish src/hello.ts --winner B
```

### Document Management
```bash
# Create new documents
python3 -m builder.core.cli doc:create --type prd "User Authentication System"
python3 -m builder.core.cli doc:create --type adr "Authentication Architecture"

# Sync all master files
python3 -m builder.core.cli master:sync-all
```

---

**Previous**: [System Statistics](README-STATISTICS.md) | **Next**: [Command Reference](README-COMMANDS.md) | [Directory Structure](README-DIRECTORY.md)
