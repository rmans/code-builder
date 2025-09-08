# Code Builder 🛠️

[![Code Quality](https://github.com/rmans/code-builder/workflows/CI/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Context Packs](https://github.com/rmans/code-builder/workflows/Context%20Packs/badge.svg)](https://github.com/rmans/code-builder/actions)
[![Documentation](https://github.com/rmans/code-builder/workflows/Documentation/badge.svg)](https://github.com/rmans/code-builder/actions)

Code Builder is a comprehensive developer productivity scaffold for AI-assisted software projects.  
It combines **ADRs (Architecture Decision Records)**, **context generation**, **iteration loops**, **rules/guardrails**, **automated evaluation**, **multi-agent orchestration**, and **discovery systems** to make AI outputs repeatable, testable, and compliant with your coding standards.

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/rmans/code-builder.git
cd code-builder
pip install -r requirements.txt && npm install
./scripts/install.sh

# Basic usage
python3 -m builder.core.cli discover:interview --type new-product
python3 -m builder.core.cli ctx:build src/main.ts --purpose implement
python3 -m builder.core.cli quality:gates --verbose
```

## 📚 Documentation

### Core Documentation
- **[System Architecture](builder-docs/readme/README-ARCHITECTURE.md)** - 10 core systems and their interactions
- **[Quickstart Guide](builder-docs/readme/README-QUICKSTART.md)** - Installation and basic usage
- **[Command Reference](builder-docs/readme/README-COMMANDS.md)** - 104+ CLI commands organized by module
- **[Directory Structure](builder-docs/readme/README-DIRECTORY.md)** - Complete project layout and organization

### Specialized Guides
- **[Discovery System](builder-docs/instructions/discover.md)** - Interactive discovery and analysis
- **[Context Management](builder-docs/instructions/context.md)** - Context generation and optimization
- **[Agent Orchestration](builder-docs/instructions/agents.md)** - Multi-agent task execution
- **[Quality Gates](builder-docs/instructions/evaluate.md)** - Release validation and compliance
- **[Telemetry & Metrics](builder-docs/instructions/telemetry.md)** - Command tracking and analytics

## 🏗️ System Overview

Code Builder is built around **10 core systems**:

1. **Context Management** - Graph-based selection and intelligent ranking
2. **Discovery System** - Interactive interviews and code analysis
3. **Multi-Agent Orchestration** - Task management and parallel execution
4. **Evaluation System** - Objective and subjective quality assessment
5. **Document Management** - Master synchronization and template system
6. **Rules & Guardrails** - Hierarchical rules with conflict detection
7. **Cache & Performance** - SHA256-based caching and optimization
8. **PR Ergonomics** - Pull request templates and validation
9. **Telemetry & Metrics** - Command tracking and usage analytics 🆕
10. **Quality Gates** - Release validation and compliance checks 🆕

> **📖 Detailed Architecture**: See [System Architecture](builder-docs/readme/README-ARCHITECTURE.md) for comprehensive details about each system.

## 📊 Key Features

- **104+ CLI Commands** across 15+ specialized modules
- **40+ Python Modules** with comprehensive functionality
- **8 Document Types** with automated master file synchronization
- **5 Quality Test Suites** for comprehensive validation
- **Multi-Agent Support** with session management and orchestration
- **Telemetry System** with command tracking and analytics
- **Quality Gates** with 10 validation checks for release readiness

## 🎯 Why Code Builder?

**For AI-Assisted Development:**
- **Repeatable outputs** through structured context and rules
- **Quality assurance** with automated evaluation and testing
- **Compliance** with coding standards and best practices
- **Scalability** through multi-agent orchestration

**For Team Collaboration:**
- **Consistent documentation** with automated master file sync
- **Clear workflows** with guided discovery and task execution
- **Quality gates** ensuring release readiness
- **Comprehensive tracking** of changes and decisions

## 🔧 Recent Updates

### 🆕 Latest Features
- **Telemetry & Metrics System** - Comprehensive command tracking and analytics
- **Quality Gates System** - 10 validation checks for release readiness
- **Modular CLI Architecture** - 104+ commands organized into specialized modules
- **Enhanced Test Infrastructure** - Quality test suites and comprehensive testing
- **Sensitive Data Protection** - Automatic redaction of credentials and API keys

### 🔄 System Improvements
- **Context graph enhancements** with better ranking algorithms
- **Discovery engine improvements** with interactive validation
- **Document management** with automated synchronization
- **Rules system** with conflict detection and guardrails
- **Cache optimization** with intelligent cleanup and rotation

## 📈 System Statistics

- **CLI Commands**: 104+ commands across 15+ modules
- **Python Modules**: 40+ modules in the builder package
- **Markdown Files**: 200+ documentation files
- **Document Types**: 8 types (PRD, ADR, ARCH, EXEC, IMPL, INTEGRATIONS, TASKS, UX)
- **Test Suites**: 5 comprehensive quality test suites
- **Rules System**: 20+ rule files with hierarchical precedence

> **📊 Detailed Statistics**: See [System Statistics](builder-docs/readme/README-STATISTICS.md) for comprehensive metrics and recent improvements.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub Repository**: [rmans/code-builder](https://github.com/rmans/code-builder)
- **Builder Documentation**: [builder-docs/](builder-docs/)
- **Generated Documentation**: [generated-docs/](generated-docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/rmans/code-builder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rmans/code-builder/discussions)

---

**Quick Navigation**: [Architecture](builder-docs/readme/README-ARCHITECTURE.md) | [Quickstart](builder-docs/readme/README-QUICKSTART.md) | [Commands](builder-docs/readme/README-COMMANDS.md) | [Directory](builder-docs/readme/README-DIRECTORY.md)
