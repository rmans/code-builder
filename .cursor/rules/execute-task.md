# Execute Single Task

Execute individual tasks with retry logic, timeout handling, and comprehensive result reporting.

## Usage

```bash
cb execute-task <TASK_ID>
cb execute-task --pick [--agent-type TYPE]
```

## Key Features

- **Single Task Execution**: Run one task at a time with full control
- **Automatic Task Picking**: Use `--pick` to automatically select the highest priority runnable task
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **Timeout Handling**: Prevent tasks from running indefinitely
- **Resume Support**: Resume running tasks that were interrupted
- **Comprehensive Results**: Detailed JSON results with timing and output

## Examples

### Execute Specific Task
```bash
# Basic execution
cb execute-task TASK-001

# With custom retry and timeout
cb execute-task TASK-001 --retries 5 --timeout 600

# Resume a running task
cb execute-task TASK-001 --resume
```

### Pick and Execute
```bash
# Pick highest priority task
cb execute-task --pick

# Pick task by agent type
cb execute-task --pick --agent-type backend
cb execute-task --pick --agent-type frontend

# Pick with custom settings
cb execute-task --pick --agent-type backend --retries 2 --timeout 120
```

## Task Selection

The `--pick` option selects tasks based on:

1. **Dependencies Satisfied**: Only tasks with all dependencies completed
2. **Status**: Only PENDING or READY tasks
3. **Priority**: Highest priority task is selected
4. **Agent Type**: Filtered by `--agent-type` if specified

## Result Files

### JSON Result (`cb_docs/tasks/results/<TASK_ID>.json`)
```json
{
  "success": true,
  "task_id": "TASK-001",
  "task_name": "Task Name",
  "attempt": 1,
  "return_code": 0,
  "stdout": "Command output",
  "stderr": "Error output",
  "duration": 1.23,
  "timestamp": "2025-09-08T08:18:31.768914"
}
```

### Log File (`cb_docs/tasks/logs/<TASK_ID>.log`)
Contains detailed execution logs and error information.

## Error Handling

- **Dependency Failures**: Clear error when dependencies not satisfied
- **Timeout Handling**: Graceful timeout with retry logic
- **Retry Logic**: Exponential backoff between retries
- **Exit Codes**: Proper exit codes for script integration

## Best Practices

1. **Always check dependencies** before executing tasks
2. **Use appropriate timeouts** based on task complexity
3. **Set reasonable retry counts** to avoid infinite loops
4. **Monitor result files** for detailed execution information
5. **Use `--pick` for automation** when task selection is flexible

## Integration

- **CI/CD Pipelines**: Use exit codes for build success/failure
- **Monitoring**: Parse JSON results for metrics and alerts
- **Automation**: Combine with `--pick` for unattended execution
- **Debugging**: Use logs and detailed results for troubleshooting

## Related Commands

- `cb list-runnable-tasks` - See available tasks
- `cb pick-task` - Preview task selection
- `cb execute-tasks` - Multi-task orchestration
