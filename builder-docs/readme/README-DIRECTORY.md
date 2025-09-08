# Directory Structure 📁

```
code-builder/
├── 📁 cb_docs/                    # Documentation system (8 document types)
│   ├── 📁 adrs/               # Architecture Decision Records
│   │   └── 0000_MASTER_ADR.md # Master ADR index (auto-synced)
│   ├── 📁 arch/               # Architecture documents  
│   │   ├── 0000_MASTER_ARCH.md # Master architecture index
│   │   └── ARCH-2025-09-07-Project-Management-System.md
│   ├── 📁 prd/                # Product Requirements Documents
│   │   └── 0000_MASTER_PRD.md # Master PRD index
│   ├── 📁 exec/               # Execution plans
│   │   └── 0000_MASTER_EXEC.md # Master execution index
│   ├── 📁 impl/               # Implementation plans
│   │   └── 0000_MASTER_IMPL.md # Master implementation index
│   ├── 📁 integrations/       # Integration specifications
│   │   ├── 0000_MASTER_INTEGRATIONS.md # Master integrations index
│   │   └── INT-2025-09-07-Project-Management-System.md
│   ├── 📁 tasks/              # Task definitions
│   │   ├── 0000_MASTER_TASKS.md # Master tasks index
│   │   └── index.json         # Task index data
│   ├── 📁 ux/                 # User experience designs
│   │   └── 0000_MASTER_UX.md # Master UX index
│   ├── 📁 commands/           # Command documentation 🆕
│   │   ├── analyze-project.md
│   │   ├── create-context.md
│   │   ├── create-task.md
│   │   ├── evaluate-code.md
│   │   ├── execute-task.md
│   │   ├── execute-tasks.md
│   │   ├── fix-issues.md
│   │   ├── plan-project.md
│   │   └── project-status.md
│   ├── 📁 instructions/       # Implementation guides 🆕
│   │   ├── cli-architecture.md
│   │   ├── current.md
│   │   ├── cursor-agent-integration.md
│   │   ├── evaluate.md
│   │   └── implement.md
│   ├── 📁 discovery/          # Discovery outputs 🆕
│   │   ├── analysis.json
│   │   ├── report.json
│   │   └── summary.md
│   ├── 📁 planning/           # Planning documents 🆕
│   │   ├── assumptions.md
│   │   ├── decisions.md
│   │   └── interview.json
│   ├── 📁 templates/          # Jinja2 document templates
│   │   ├── 📁 commands/       # Command templates 🆕
│   │   └── [other templates]  # Document templates
│   ├── 📁 rules/              # Rules & guardrails system
│   │   ├── 00-global.md       # Global rules
│   │   ├── 10-project.md      # Project rules
│   │   ├── 15-implementation.md # Implementation rules
│   │   ├── 17-no-cb-directory-creation.md
│   │   ├── 18-rule-interaction-strategy.md
│   │   ├── 19-no-rule-copying.md
│   │   ├── 20-shell-scripting.md
│   │   ├── 21-cli-development.md
│   │   ├── 22-modular-architecture.md
│   │   ├── stack/             # Stack-specific rules
│   │   ├── feature/           # Feature-specific rules
│   │   └── guardrails.json    # Forbidden patterns
│   ├── 📁 eval/               # Evaluation configuration
│   │   └── config.yaml        # Evaluation weights & config
│   ├── 📁 examples/           # Usage examples
│   ├── CURSOR-Custom-Commands.md    # Cursor integration guide
│   ├── USAGE-Cursor-Evaluation.md   # Evaluation usage guide
│   ├── SECURITY.md            # Security guidelines
│   ├── INDEX.md               # Documentation index 🆕
│   ├── pack_context.json      # Context pack data 🆕
│   └── README.md              # Documentation index
│
├── 📁 builder/                # Core Python system (40+ modules)
│   ├── 📁 core/               # Core functionality
│   │   ├── 📁 cli/            # Modular CLI system (104+ commands)
│   │   │   ├── base.py        # Main CLI group and utilities
│   │   │   ├── context_commands.py      # Context building (12 commands)
│   │   │   ├── discovery_commands.py    # Discovery & analysis (6 commands)
│   │   │   ├── document_commands.py     # Document management (8 commands)
│   │   │   ├── agent_commands.py        # Agent management (4 commands)
│   │   │   ├── orchestrator_commands.py # Task orchestration (12 commands)
│   │   │   ├── evaluation_commands.py   # Evaluation & rules (5 commands)
│   │   │   ├── quality_commands.py      # Quality gates (3 commands)
│   │   │   ├── utility_commands.py      # Utilities (7 commands)
│   │   │   └── [other modules]         # Additional command modules
│   │   ├── context_graph.py   # Context graph building
│   │   ├── context_select.py  # Context selection & ranking
│   │   ├── context_budget.py  # Token budget management
│   │   ├── context_rules.py   # Rules merging & conflict detection
│   │   ├── context_builder.py # Context building orchestration
│   │   └── task_index.py      # Task indexing system
│   ├── 📁 discovery/          # Discovery system (6 commands)
│   │   ├── engine.py          # Discovery orchestration
│   │   ├── enhanced_engine.py # Enhanced discovery engine
│   │   ├── analyzer.py        # Code analysis
│   │   ├── synthesizer.py     # Findings synthesis
│   │   ├── generators.py      # Document generation
│   │   ├── validator.py       # Validation system
│   │   └── interview.py       # Interactive discovery
│   ├── 📁 telemetry/          # Telemetry & metrics system 🆕
│   │   ├── metrics_collector.py    # Command tracking & analytics
│   │   └── command_tracker.py      # Command execution decorator
│   ├── 📁 quality/            # Quality gates system 🆕
│   │   └── gates.py           # 10 validation checks
│   ├── 📁 overlay/            # Overlay system 🆕
│   │   ├── paths.py           # Path resolution
│   │   ├── router.py          # Command routing
│   │   ├── menu.py            # Interactive menu
│   │   └── [other modules]    # Overlay functionality
│   ├── 📁 evaluators/         # Evaluation system (4 commands)
│   │   ├── objective.py       # Objective evaluation
│   │   ├── artifact_detector.py # File type detection
│   │   └── doc_schema.py      # Documentation validation
│   ├── 📁 utils/              # Utility modules
│   │   ├── agent_tracker.py   # Agent session management
│   │   ├── task_orchestrator.py # Task orchestration
│   │   ├── multi_agent_cursor.py # Multi-agent Cursor integration
│   │   ├── cleanup_rules.py   # Artifact cleanup
│   │   ├── cursor_agent_integration.py # Cursor integration
│   │   ├── cursor_bridge.py   # Cursor bridge utilities
│   │   ├── master_file_sync.py # Master file synchronization 🆕
│   │   ├── abc_iteration.py   # ABC iteration system 🆕
│   │   ├── command_agent_integration.py # Command integration 🆕
│   │   ├── current_instructions.py # Current instructions 🆕
│   │   ├── dynamic_content_updater.py # Content updates 🆕
│   │   └── rules_integration.py # Rules integration 🆕
│   ├── 📁 config/             # Configuration
│   │   ├── prompts/           # Evaluation prompt generation
│   │   │   └── evaluation_prompt.py
│   │   └── settings.py        # System settings 🆕
│   ├── 📁 scripts/            # Utility scripts
│   │   └── cursor_server.py   # Flask bridge server
│   ├── 📁 cache/              # Generated data & reports
│   │   ├── packs/             # Cached context packs
│   │   ├── discovery/         # Discovery outputs
│   │   ├── multi_agents/      # Agent workspaces
│   │   ├── evaluations/       # Evaluation results
│   │   ├── command_state/     # Command telemetry data 🆕
│   │   └── metrics/           # Metrics and analytics 🆕
│   └── README.md              # Builder documentation
│
├── 📁 tests/                  # Consolidated test system
│   ├── 📁 unit/               # Unit tests
│   │   ├── test_context_budget.py
│   │   ├── test_context_graph.py
│   │   ├── test_context_select.py
│   │   ├── test_context_validator.py
│   │   ├── test_overlay_paths.py
│   │   └── test_server.py
│   ├── 📁 integration/        # Integration tests
│   │   └── test_golden_checks.py
│   ├── 📁 suites/             # Quality test suites 🆕
│   │   ├── test_context_suite.py
│   │   ├── test_discovery_suite.py
│   │   ├── test_interview_suite.py
│   │   ├── test_orchestrator_suite.py
│   │   └── test_single_task_suite.py
│   ├── 📁 data/               # Test fixtures & data
│   │   └── discovery_test_answers.json
│   ├── 📁 fixtures/           # Test project fixtures
│   │   ├── 📁 js-project/     # JavaScript test project
│   │   └── 📁 py-project/     # Python test project
│   ├── 📁 results/            # Test output & reports
│   │   ├── budget_report.md
│   │   ├── coverage-final.json
│   │   └── vitest.json
│   ├── 📁 scripts/            # Test scripts
│   │   ├── test_discovery_with_answers.py
│   │   └── test_context_workflow.sh
│   └── run_quality_suites.py  # Quality test runner 🆕
│
├── 📁 src/                    # Source code (TypeScript/JavaScript)
├── 📁 scripts/                # Project scripts
│   └── install.sh             # Installation script 🆕
├── 📁 .github/                # GitHub workflows & templates
│   └── workflows/             # CI/CD pipelines
├── 📁 .cursor/                # Cursor configuration
│   └── rules/                 # Cursor rules
├── package.json               # Node.js dependencies & scripts
├── pnpm-lock.yaml            # Package lock file
├── requirements.txt           # Python dependencies
├── tsconfig.json              # TypeScript configuration
├── vitest.config.ts           # Test configuration
├── eslint.config.js           # Linting configuration
├── cspell.json               # Spell checking configuration
└── README.md                  # Main documentation
```

## Key Directories

### 📁 `cb_docs/` - Documentation System
- **8 document types** with master index files
- **Command documentation** for all CLI commands
- **Implementation guides** for system usage
- **Rules & guardrails** with hierarchical precedence
- **Templates** for document generation

### 📁 `builder/` - Core Python System
- **40+ modules** organized by functionality
- **104+ CLI commands** across specialized modules
- **Telemetry system** for command tracking and analytics
- **Quality gates** for release validation
- **Overlay system** for enhanced user experience

### 📁 `tests/` - Test Infrastructure
- **Unit tests** for individual components
- **Integration tests** for end-to-end workflows
- **Quality test suites** for comprehensive validation
- **Test fixtures** with realistic project examples
- **Quality test runner** for automated testing

---

**Previous**: [Command Reference](README-COMMANDS.md) | **Next**: [System Architecture](README-ARCHITECTURE.md) | [Quickstart Guide](README-QUICKSTART.md)
