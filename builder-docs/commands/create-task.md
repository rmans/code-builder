---
id: create-task
title: Create Task
description: Create a new task with structured format
status: active
created: 2025-09-07
updated: 2025-09-07
owner: system
domain: task-management
priority: 7
agent_type: backend
dependencies: []
tags: [task, creation, management, planning]
---

# Command: Create Task

## Description
Creates a new task with structured format, including phases, dependencies, acceptance criteria, and metadata.

## Usage
```bash
cb create-task
# or
@rules/create-task
```

## Outputs
- `cb_docs/tasks/TASK-{{date}}-{{id}}.md` - Generated task file
- `cb_docs/tasks/index.json` - Updated task index
- `cb_docs/tasks/0000_MASTER_TASKS.md` - Updated master tasks file

## Flags
- `--title TITLE` - Task title
- `--description DESC` - Task description
- `--priority PRIORITY` - Task priority (1-10)
- `--owner OWNER` - Task owner
- `--domain DOMAIN` - Task domain
- `--dependencies DEPS` - Comma-separated dependencies
- `--tags TAGS` - Comma-separated tags

## Examples
```bash
# Interactive task creation
cb create-task

# Quick task creation
cb create-task --title "Fix bug" --priority 8

# Task with dependencies
cb create-task --title "Implement feature" --dependencies "TASK-001,TASK-002"

# Task with specific domain
cb create-task --title "Update docs" --domain documentation
```

## Task Structure

### Phases
Each task includes 5 phases:
1. **Implementation** - Core implementation work
2. **Testing** - Testing and validation
3. **Documentation** - Documentation updates
4. **Cleanup** - Code cleanup and optimization
5. **Commit** - Git commit and finalization

### Metadata
- **ID**: Unique task identifier
- **Title**: Descriptive task title
- **Description**: Detailed task description
- **Status**: Current task status
- **Priority**: Task priority (1-10)
- **Owner**: Task owner/assignee
- **Domain**: Task domain/category
- **Dependencies**: Required prerequisite tasks
- **Tags**: Categorization tags

### Acceptance Criteria
- Clear, measurable criteria for task completion
- Specific deliverables and outputs
- Quality standards and requirements

## Template Variables
- `code-builder` - Project name
- `Node.js` - Project type
- `next` - Primary framework
- `JSON` - Primary language
- `{{task_id}}` - Generated task ID
- `{{task_title}}` - Task title
- `{{task_description}}` - Task description
- `{{task_priority}}` - Task priority
- `{{task_owner}}` - Task owner
- `{{task_domain}}` - Task domain
