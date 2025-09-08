# Evaluation Guide

## Overview

The Code Builder system includes comprehensive telemetry and metrics collection to track command execution, performance, and usage patterns. This guide covers how to access and interpret these metrics.

## Metrics Collection

### Command Metrics

The system automatically tracks the following metrics for each command execution:

- **Total Commands Run**: Count of all commands executed
- **Successful Commands**: Count of commands that completed successfully (exit code 0)
- **Failed Commands**: Count of commands that failed (non-zero exit code)
- **Average Execution Time**: Mean execution time across all commands
- **Most Used Commands**: Top 10 most frequently used commands with usage counts

### Discovery Metrics

- **Time to First Rules**: Time from session start to first rules command execution
- **Command Discovery Rate**: Commands discovered per minute
- **Execution Success Rate**: Percentage of successful command executions

### Performance Metrics

- **Cache Hit Rate**: Percentage of cache hits vs misses
- **Average Response Time**: Mean response time for operations
- **Memory Usage**: Current memory consumption in MB

### Session Metrics

- **Current Session Start**: Timestamp of current session start
- **Total Sessions**: Number of sessions tracked
- **Average Session Duration**: Mean session length in minutes

## Command History

Each command execution is recorded in the command history with:

- Command ID
- Execution timestamp
- Success/failure status
- Exit code
- Execution time in milliseconds
- Command arguments (with sensitive data redacted)

## Accessing Metrics

### Status Command

Use the `cb status` command to view current metrics:

```bash
# Basic status
cb status

# Detailed status with recent commands
cb status --verbose

# Include performance metrics
cb status --metrics

# JSON output
cb status --format json

# YAML output
cb status --format yaml
```

### Direct File Access

Metrics are stored in `.cb/cache/command_state/`:

- `metrics.json` - All collected metrics
- `state.json` - Command history and project state

## Metrics Schema

### metrics.json Structure

```json
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "command_metrics": {
    "total_commands_run": 0,
    "successful_commands": 0,
    "failed_commands": 0,
    "average_execution_time_ms": 0.0,
    "most_used_commands": []
  },
  "discovery_metrics": {
    "time_to_first_rules": null,
    "command_discovery_rate": 0.0,
    "execution_success_rate": 0.0
  },
  "performance_metrics": {
    "cache_hit_rate": 0.0,
    "average_response_time_ms": 0.0,
    "memory_usage_mb": 0.0
  },
  "session_metrics": {
    "current_session_start": null,
    "total_sessions": 0,
    "average_session_duration_minutes": 0.0
  }
}
```

### state.json Structure

```json
{
  "version": "1.0.0",
  "created": "2025-01-15T00:00:00Z",
  "updated": "2025-01-15T00:00:00Z",
  "project_state": {
    "initialized": false,
    "discovered": false,
    "analyzed": false,
    "planned": false,
    "context_created": false
  },
  "command_history": [
    {
      "command_id": "agent:get-command",
      "timestamp": "2025-01-15T00:00:00Z",
      "success": true,
      "exit_code": 0,
      "execution_time_ms": 7.8,
      "args": ["output=json"]
    }
  ],
  "active_tasks": [],
  "completed_tasks": [],
  "cache_metadata": {
    "last_cleanup": null,
    "size_bytes": 0,
    "file_count": 0
  }
}
```

## Interpreting Metrics

### Success Rate Analysis

- **High Success Rate (>95%)**: System is stable and commands are working well
- **Medium Success Rate (80-95%)**: Some issues may exist, investigate failed commands
- **Low Success Rate (<80%)**: Significant problems, review error logs and command implementations

### Performance Analysis

- **Execution Time**: Monitor for performance regressions
- **Memory Usage**: Track for memory leaks or excessive consumption
- **Cache Hit Rate**: Optimize caching strategy if hit rate is low

### Usage Patterns

- **Most Used Commands**: Focus optimization efforts on frequently used commands
- **Command Discovery Rate**: Measure how quickly users find and use new commands
- **Session Duration**: Understand user engagement patterns

## Data Retention

- Command history is limited to the last 100 entries
- Metrics are accumulated over time (no automatic rotation)
- Consider implementing cleanup policies for long-running systems

## Privacy and Security

- Command arguments are logged but sensitive data should be redacted
- No personal information is collected
- All data is stored locally in the project directory

## Troubleshooting

### Common Issues

1. **Metrics not updating**: Check file permissions on `.cb/cache/command_state/`
2. **Status command fails**: Verify telemetry module is properly installed
3. **Missing command history**: Ensure commands are using the `@track_command` decorator

### Debug Mode

Enable debug logging to troubleshoot telemetry issues:

```bash
export CB_DEBUG=1
cb status --verbose
```

## Integration

### Adding Command Tracking

To track a new command, add the `@track_command` decorator:

```python
from builder.core.cli.base import track_command

@cli.command("my-command")
@track_command("my-command")
def my_command():
    # Command implementation
    pass
```

### Custom Metrics

Extend the metrics collector for custom metrics:

```python
from builder.telemetry.metrics_collector import MetricsCollector

tracker = MetricsCollector()
# Add custom metric collection logic
```

## Examples

### Basic Status Check

```bash
$ cb status
📊 Code Builder Status
==================================================
Total Commands: 15
Success Rate: 93.3%
Avg Execution Time: 12.4ms
Last Updated: 2025-01-15T10:30:00Z
```

### Detailed Analysis

```bash
$ cb status --verbose --metrics
📊 Code Builder Status
==================================================
Total Commands: 15
Success Rate: 93.3%
Avg Execution Time: 12.4ms
Last Updated: 2025-01-15T10:30:00Z

📋 Recent Commands:
  ✅ agent:get-command (7.8ms)
  ✅ agent:integrate (13.7ms)
  ❌ agent:create-rules (4.1ms)

🔥 Most Used Commands:
  agent:get-command: 5 times
  agent:integrate: 3 times
  status: 2 times
```

This comprehensive telemetry system provides valuable insights into Code Builder usage patterns and performance characteristics, enabling continuous improvement and optimization.

## Quality Gates

The Code Builder system includes comprehensive quality gates to ensure release readiness and system reliability. Quality gates validate critical aspects of the system including idempotency, parity, determinism, and user experience.

### Quality Gates Overview

Quality gates are automated checks that validate:

- **Idempotency**: Operations produce the same result when run multiple times
- **Parity**: Consistency between index and rules files
- **Determinism**: Non-interactive operations produce consistent results
- **Cursor UX**: Rules files meet usability standards
- **End-to-End Flow**: Complete workflow execution
- **Test Suites**: Discovery, context, orchestrator, single-task, and interview suites

### Running Quality Gates

Use the quality gates command to run all validation checks:

```bash
# Run all quality gates
cb quality:gates

# Run with verbose output
cb quality:gates --verbose

# Generate detailed report
cb quality:report --format json

# Run specific gate
cb quality:check --gate idempotency
```

### Quality Gates Results

Quality gates provide comprehensive validation results:

```bash
$ cb quality:gates --verbose
🔍 Running quality gates...

✅ Quality Gates Summary
==================================================
Overall Status: PASSED
Gates Passed: 8/10
Success Rate: 80.0%
Execution Time: 1250.3ms

📋 Gate Details:
  ✅ idempotency: Idempotency checks passed (45.2ms)
  ❌ parity_index_rules: Parity check failed (12.1ms)
  ✅ determinism: Determinism checks passed (89.3ms)
  ❌ cursor_ux: Cursor UX checks failed (23.4ms)
  ✅ end_to_end_flow: End-to-end flow passed (156.7ms)
  ✅ discovery_suite: discovery suite passed (234.1ms)
  ✅ interview_suite: interview suite passed (198.3ms)
  ✅ context_suite: context suite passed (167.2ms)
  ✅ orchestrator_suite: orchestrator suite passed (145.6ms)
  ✅ single_task_suite: single_task suite passed (179.4ms)
```

### Quality Gates Configuration

Quality gates can be configured through the `builder/quality/gates.py` module:

- **Idempotency**: Tests command discovery and rules generation consistency
- **Parity**: Validates index.json ↔ .cursor/rules/ consistency
- **Determinism**: Ensures non-interactive commands produce consistent output
- **Cursor UX**: Validates rules file format and usability
- **End-to-End**: Tests complete workflow execution
- **Test Suites**: Runs comprehensive test suites for all components

### Quality Gates Integration

Quality gates are integrated into the CI/CD pipeline and can be run:

1. **Manually**: `cb quality:gates`
2. **In CI**: Automated validation on pull requests
3. **Pre-release**: Comprehensive validation before releases
4. **Development**: Continuous validation during development

### Quality Gates Metrics

Quality gates track:

- **Execution Time**: Performance of each gate
- **Success Rate**: Overall gate pass rate
- **Gate Details**: Individual gate results and metrics
- **Error Information**: Detailed error messages and debugging info

### Quality Gates Reports

Generate detailed reports in multiple formats:

```bash
# JSON report
cb quality:report --format json --output-file quality_report.json

# YAML report  
cb quality:report --format yaml --output-file quality_report.yaml

# HTML report
cb quality:report --format html --output-file quality_report.html
```

### Quality Gates Troubleshooting

Common issues and solutions:

1. **Parity Check Failures**: Ensure index.json and .cursor/rules/ are synchronized
2. **Cursor UX Issues**: Validate rules file format and required sections
3. **Test Suite Failures**: Check individual test suite implementations
4. **Performance Issues**: Monitor execution times and optimize slow gates

### Quality Gates Best Practices

1. **Run Regularly**: Execute quality gates during development
2. **Fix Issues Promptly**: Address failing gates immediately
3. **Monitor Trends**: Track gate performance over time
4. **Document Changes**: Update gate definitions when system changes
5. **Automate Integration**: Include gates in CI/CD pipelines

This comprehensive quality gates system ensures Code Builder maintains high standards of reliability, consistency, and user experience throughout its development lifecycle.
