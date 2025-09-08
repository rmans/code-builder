# Cursor Agent Integration

## Overview

The Code Builder system integrates with Cursor agents through a command suggestion system that provides context-aware recommendations for agents to execute. This integration allows agents to receive appropriate `@rules/` commands based on the current project state.

## Architecture

### Command Agent Integration

The integration consists of several key components:

1. **CommandAgentIntegration** - Main integration class
2. **Command Selection Logic** - Context-aware command recommendation
3. **Rules Generation** - Automatic creation of `@rules/` files
4. **Agent CLI Commands** - CLI interface for testing and management

### Integration Flow

```
Project Context → Command Selection → Rules Generation → Agent Execution
```

## Usage

### Basic Integration

```bash
# Get recommended command for current context
cb agent:get-command

# Get command with specific context
cb agent:get-command --context '{"discovered": true, "analyzed": true}'

# Create @rules/ files for agents
cb agent:integrate
```

### Command Selection Logic

The system selects commands based on:

1. **Project State**: Discovery, analysis, planning status
2. **Dependencies**: Whether prerequisite commands have been executed
3. **Priority**: Command priority levels
4. **Context**: Current project type and requirements

### Context Detection

The system automatically detects:

- **Project Initialization**: Whether the project is set up
- **Discovery Status**: Whether project discovery has been completed
- **Analysis Status**: Whether analysis has been performed
- **Planning Status**: Whether planning has been done
- **Task Availability**: Whether there are active tasks
- **Project Type**: Code, documentation, or other project types

## Generated Files

### @rules/ Commands

The system generates two types of `@rules/` files:

1. **Command-specific rules** (e.g., `execute-analyze-project.md`)
2. **Project status rules** (`project-status.md`)

### Example Generated Files

#### execute-analyze-project.md
```markdown
# Execute Analyze Project

## Description
Analyze project structure and generate discovery report

## Usage
```bash
cb analyze-project
```

## Context
This command has been selected based on current project state and dependencies.

## Agent Instructions
1. Execute the command using the Code Builder CLI
2. Follow any prompts or interactive elements
3. Report results and any issues encountered
4. Update project state as needed
```

#### project-status.md
```markdown
# Project Status

## Description
Get current project status and next recommended actions.

## Usage
```bash
cb commands:list
cb orchestrator:status
```

## Agent Instructions
1. Check current project status
2. List available commands
3. Identify next recommended actions
4. Report current state and recommendations
```

## API Reference

### CommandAgentIntegration Class

#### Methods

- `get_command_for_agent(context=None)` - Get recommended command
- `create_rules_command(command_id)` - Create @rules/ file for command
- `create_project_status_rules()` - Create project status @rules/ file
- `integrate_with_agents()` - Full integration setup

#### Example Usage

```python
from builder.utils.command_agent_integration import CommandAgentIntegration

# Create integration instance
integration = CommandAgentIntegration()

# Get recommended command
command_id, rules_command = integration.get_command_for_agent()

# Create rules files
integration.integrate_with_agents()
```

### CLI Commands

#### agent:get-command
Get recommended command for Cursor agent based on current context.

```bash
cb agent:get-command [--context JSON] [--output text|json]
```

**Options:**
- `--context` - JSON context for command selection
- `--output` - Output format (text or json)

#### agent:create-rules
Create @rules/ command files for Cursor agents.

```bash
cb agent:create-rules COMMAND_ID [--status]
```

**Options:**
- `COMMAND_ID` - Command ID to create rules for
- `--status` - Create project status rules instead

#### agent:integrate
Integrate command system with Cursor agents.

```bash
cb agent:integrate [--output text|json]
```

**Options:**
- `--output` - Output format (text or json)

## Command Selection Algorithm

### Scoring System

Commands are scored based on:

1. **Priority** (40%): Higher priority commands get higher scores
2. **Dependencies** (30%): Commands with satisfied dependencies get bonus points
3. **Context Match** (20%): Commands matching current project state
4. **Agent Type** (10%): Commands matching agent capabilities

### Context-Based Scoring

- **Discovery Commands**: +30 if not discovered, -20 if already discovered
- **Planning Commands**: +25 if discovered but not planned, -15 if not discovered
- **Analysis Commands**: +20 if not analyzed
- **Implementation Commands**: +15 if planned

### Dependency Checking

The system checks for:

- `analyze-project` - Analysis completion
- `discover` - Discovery completion
- `plan` - Planning completion
- `context` - Context creation

## Integration with Existing Systems

### CursorAgentOrchestrator

The integration reuses the existing `CursorAgentOrchestrator` for:

- Agent management
- Task orchestration
- Status tracking

### MultiAgentCursorManager

The integration leverages `MultiAgentCursorManager` for:

- Multi-agent coordination
- Workspace management
- Agent lifecycle management

### Command System

The integration connects to the command system through:

- Command loading from `cb_docs/commands/`
- Command metadata parsing
- Command execution tracking

## Error Handling

### Common Issues

1. **Missing Dependencies**: Graceful degradation when utility modules are missing
2. **Invalid Context**: Validation and fallback to default context
3. **Command Not Found**: Fallback to default command (analyze-project)
4. **File Creation Errors**: Proper error reporting and cleanup

### Error Recovery

- **Import Errors**: Clear error messages with suggestions
- **Path Issues**: Automatic path resolution and validation
- **Permission Errors**: Proper error reporting and guidance

## Testing

### Manual Testing

```bash
# Test basic integration
cb agent:integrate

# Test command selection
cb agent:get-command

# Test with different contexts
cb agent:get-command --context '{"discovered": true}'

# Test rules creation
cb agent:create-rules analyze-project
```

### Automated Testing

The integration includes:

- Unit tests for command selection logic
- Integration tests for file generation
- Context detection tests
- Error handling tests

## Future Enhancements

### Planned Features

1. **Dynamic Context Updates**: Real-time context monitoring
2. **Command History**: Track previously executed commands
3. **Agent Preferences**: Learn from agent behavior patterns
4. **Advanced Scoring**: More sophisticated command selection algorithms

### Extension Points

1. **Custom Context Providers**: Add new context detection methods
2. **Custom Scoring**: Implement custom command scoring logic
3. **Custom Rules Templates**: Create custom @rules/ file templates
4. **Integration Hooks**: Add hooks for custom integrations

## Troubleshooting

### Common Problems

1. **No Commands Available**: Check that `cb_docs/commands/` exists and contains valid command files
2. **Context Detection Issues**: Verify project structure and file permissions
3. **Rules Generation Fails**: Check `.cursor/rules/` directory permissions
4. **Import Errors**: Ensure all dependencies are installed

### Debug Mode

Enable debug mode for detailed logging:

```bash
export CB_DEBUG=1
cb agent:integrate
```

## Conclusion

The Cursor Agent Integration provides a seamless way for agents to receive context-aware command recommendations. The system is designed to be extensible, maintainable, and easy to use, while providing powerful capabilities for automated project management and development workflows.
