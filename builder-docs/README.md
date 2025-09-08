# Code Builder Documentation 📚

This directory contains all documentation and configuration files for the Code Builder system itself.

## Directory Structure

### 📁 `readme/` - README Documentation Modules
- **README-ARCHITECTURE.md** - Detailed system architecture and interactions
- **README-STATISTICS.md** - Comprehensive statistics and recent improvements
- **README-QUICKSTART.md** - Installation, configuration, and basic usage
- **README-COMMANDS.md** - Complete command reference with examples
- **README-DIRECTORY.md** - Detailed project structure and organization

### 📁 `instructions/` - Implementation Guides
- **cli-architecture.md** - CLI system architecture and design
- **current.md** - Current implementation status
- **cursor-agent-integration.md** - Cursor agent integration guide
- **evaluate.md** - Evaluation system documentation
- **implement.md** - Implementation guidelines

### 📁 `commands/` - Command Documentation
- **analyze-project.md** - Project analysis command
- **create-context.md** - Context creation command
- **create-task.md** - Task creation command
- **evaluate-code.md** - Code evaluation command
- **execute-task.md** - Task execution command
- **execute-tasks.md** - Multi-task execution command
- **fix-issues.md** - Issue fixing command
- **plan-project.md** - Project planning command
- **project-status.md** - Project status command

### 📁 `rules/` - Rules and Guardrails
- **00-global.md** - Global rules and standards
- **10-project.md** - Project-specific rules
- **15-implementation.md** - Implementation guidelines
- **17-no-cb-directory-creation.md** - Directory creation rules
- **18-rule-interaction-strategy.md** - Rule interaction guidelines
- **19-no-rule-copying.md** - Rule copying restrictions
- **20-shell-scripting.md** - Shell scripting guidelines
- **21-cli-development.md** - CLI development standards
- **22-modular-architecture.md** - Modular architecture guidelines
- **23-modular-readme.md** - README modularization rules
- **guardrails.json** - Forbidden patterns and security rules

### 📁 `templates/` - Document Templates
- **commands/** - Command documentation templates
- **discovery/** - Discovery system templates
- **Various document templates** - PRD, ADR, ARCH, etc.

### 📁 `eval/` - Evaluation Configuration
- **config.yaml** - Evaluation weights and configuration

### 📁 `examples/` - Usage Examples
- **discovery_context.yml** - Discovery context examples
- **existing_codebase.md** - Existing codebase examples
- **new_product.md** - New product examples

### 📄 Root Files
- **CURSOR-Custom-Commands.md** - Cursor integration guide
- **USAGE-Cursor-Evaluation.md** - Evaluation usage guide
- **SECURITY.md** - Security guidelines

## Purpose

This directory contains all the documentation, configuration, and templates that define how Code Builder works and how to use it. It's separate from the generated documentation outputs to maintain clear separation between:

- **Builder Documentation** (this directory) - How to use and configure Code Builder
- **Generated Documentation** (`../generated-docs/`) - Outputs created by Code Builder

## Maintenance

- **Documentation updates** should be made in this directory
- **Template changes** should be reflected in the templates directory
- **Rule updates** should be made in the rules directory
- **Configuration changes** should be made in the eval directory

---

**Related**: [Generated Documentation](../generated-docs/) | [Main README](../README.md)
