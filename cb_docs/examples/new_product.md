# Example: New Product Development

This example demonstrates the complete end-to-end workflow for developing a new product using the Code Builder system.

## Overview

We'll create a simple "Task Manager" web application with user authentication, task CRUD operations, and real-time updates.

## Step 1: Create PRD

```bash
# Create a new PRD for the task manager
python builder/cli.py doc:new prd --title "Task Manager Web Application"

# This creates: docs/prd/PRD-YYYY-MM-DD-task-manager-web-application.md
```

## Step 2: Fill in PRD Content

Edit the generated PRD file with the following content:

```markdown
---
type: prd
id: PRD-2025-09-06-task-manager
title: Task Manager Web Application
status: draft
owner: product_team
created: 2025-09-06
links:
  prd: PRD-2025-09-06-task-manager
  adr: []
  arch: []
  exec: []
  impl: []
  integrations: []
  tasks: []
  ux: []
---

# Product Requirements Document: Task Manager Web Application

## Problem

Teams need a simple, intuitive way to manage tasks and track progress without complex project management overhead.

## Goals

- Create a lightweight task management system
- Enable real-time collaboration
- Provide mobile-friendly interface
- Ensure data security and user privacy

## Requirements

### Functional Requirements
- User authentication and authorization
- Create, read, update, delete tasks
- Task categorization and filtering
- Real-time updates via WebSocket
- Mobile-responsive design

### Non-Functional Requirements
- Page load time < 2 seconds
- Support 100+ concurrent users
- 99.9% uptime
- Data encryption in transit and at rest

## Acceptance Criteria

- [ ] Users can register and login securely
- [ ] Users can create tasks with title, description, and due date
- [ ] Users can mark tasks as complete/incomplete
- [ ] Users can filter tasks by status and category
- [ ] Real-time updates work across multiple browser tabs
- [ ] Application works on mobile devices
- [ ] All user data is encrypted

## Success Metrics

- User registration rate: 50+ users in first month
- Task completion rate: 80% of created tasks completed
- User satisfaction: 4.5+ stars average rating
- Performance: 95% of page loads under 2 seconds

## Technical Stack

- Frontend: React with TypeScript
- Backend: Node.js with Express
- Database: PostgreSQL
- Real-time: Socket.io
- Authentication: JWT tokens
- Deployment: Docker containers
```

## Step 3: Generate Discovery Context

```bash
# Generate discovery context for the PRD
python builder/cli.py discover:regenerate --all

# This creates discovery context files in builder/cache/discovery/
```

## Step 4: Create Architecture Document

```bash
# Create architecture document
python builder/cli.py doc:new arch --title "Task Manager Architecture"

# Edit the generated file with system design
```

## Step 5: Generate Implementation Plan

```bash
# Create implementation document
python builder/cli.py doc:new impl --title "Task Manager Implementation"

# This will reference the PRD and architecture
```

## Step 6: Build Context for Development

```bash
# Build context for a specific file (e.g., main component)
python builder/cli.py ctx:build src/components/TaskList.tsx \
  --purpose implement \
  --feature task-management \
  --stacks react,typescript \
  --token-limit 8000

# This creates pack_context.json and context.md
```

## Step 7: Generate Code with Context

```bash
# Use the context pack to generate code
python builder/cli.py ctx:pack --stdout

# This outputs the context in a format ready for AI code generation
```

## Step 8: Validate Documentation

```bash
# Check all documentation is valid
python builder/cli.py doc:check

# This validates PRD, architecture, and implementation docs
```

## Step 9: Generate Full Discovery Report

```bash
# Generate comprehensive discovery report
python builder/cli.py discover:regenerate --all

# This creates discovery outputs for all document types
```

## Expected Outputs

After running all steps, you should have:

1. **PRD Document**: `docs/prd/PRD-YYYY-MM-DD-task-manager-web-application.md`
2. **Architecture Document**: `docs/arch/ARCH-YYYY-MM-DD-task-manager-architecture.md`
3. **Implementation Document**: `docs/impl/IMPL-YYYY-MM-DD-task-manager-implementation.md`
4. **Discovery Context**: `builder/cache/discovery/PRD-YYYY-MM-DD-task-manager-web-application.yml`
5. **Context Pack**: `builder/cache/pack_context.json` and `builder/cache/context.md`
6. **Discovery Outputs**: Various generated files in `builder/cache/discovery_outputs/`

## Verification Commands

```bash
# Verify discovery context was generated
ls -la builder/cache/discovery/PRD-*.yml

# Verify context pack was created
ls -la builder/cache/pack_context.json builder/cache/context.md

# Verify documentation is valid
python builder/cli.py doc:check

# Verify discovery outputs
ls -la builder/cache/discovery_outputs/
```

## Troubleshooting

- If `discover:regenerate` fails, check that PRD has proper YAML front-matter
- If `ctx:build` fails, ensure target file exists or use a valid path
- If `doc:check` fails, verify all required fields are present in documents
- Check logs in `builder/cache/` for detailed error information
