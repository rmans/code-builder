# Pull Request

## 🎯 Quick Reference
<!-- Check which sections apply based on files changed in this PR -->
- **Core Validation**: Always complete (all PRs)
- **Document Changes**: Complete if touching `docs/` files
- **Discovery Context**: Complete if touching `docs/prd/` files
- **Document Validation**: Complete relevant subsection based on document type
- **Context Pack**: Complete if generating context for development

## 📋 Pre-submission Checklist

Please ensure the following steps have been completed before submitting this PR:

### 🔧 Core Validation
- [ ] **Documentation Validation**: Run `python3 builder/cli.py doc:check` - all documents pass validation
- [ ] **Documentation Quality**: Run `pnpm run docs:all` - markdown linting and spell checking pass
- [ ] **Tests Pass**: Run `npm run test:all` - both TypeScript and Python tests pass
- [ ] **Code Review**: Self-review of changes for quality and completeness

### 📄 Document-Related Changes (if applicable)
<!-- Check these boxes if this PR touches docs/ files -->

#### PRD Changes (docs/prd/)
- [ ] **Discovery Scan**: Run `python3 builder/cli.py discover:scan --auto-generate` - discovery contexts refreshed
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` - context pack generated successfully
- [ ] **Discovery Validation**: Verify discovery artifacts are uploaded in CI (check Actions tab)

#### ADR Changes (docs/adrs/)
- [ ] **ADR Validation**: Ensure ADR follows standard format with status, context, decision, consequences
- [ ] **Related PRD**: Verify ADR links to relevant PRD if applicable
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for architecture context

#### Architecture Changes (docs/arch/)
- [ ] **Architecture Validation**: Ensure system design is documented with diagrams
- [ ] **Technical Stack**: Verify technology choices are justified and documented
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for implementation context

#### Execution Changes (docs/exec/)
- [ ] **Execution Plan**: Verify deployment strategy and timeline are documented
- [ ] **Dependencies**: Check that all required resources and prerequisites are listed
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for deployment context

#### Implementation Changes (docs/impl/)
- [ ] **Implementation Plan**: Ensure development approach and technical details are documented
- [ ] **Code Examples**: Verify implementation includes relevant code snippets or pseudocode
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for development context

#### Integration Changes (docs/integrations/)
- [ ] **Integration Plan**: Verify external service integrations are documented
- [ ] **API Documentation**: Check that API contracts and data flows are specified
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for integration context

#### Task Changes (docs/tasks/)
- [ ] **Task Breakdown**: Ensure tasks are clearly defined with acceptance criteria
- [ ] **Dependencies**: Verify task dependencies and sequencing are documented
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for task context

#### UX Changes (docs/ux/)
- [ ] **User Research**: Verify user needs and personas are documented
- [ ] **Design System**: Check that UI/UX patterns and components are specified
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` for design context

### 🎯 Context Building
- [ ] **Context Building**: Run `python3 builder/cli.py ctx:build <target_path> --purpose implement` - context builds successfully

## 🎯 Changes Summary

<!-- Provide a brief summary of what this PR changes -->

## 📄 Document-Specific Changes

<!-- Complete relevant sections based on which docs/ files this PR touches -->

### 🔍 Discovery Context (for PRD changes)
- [ ] **Discovery scan completed**: `python3 builder/cli.py discover:scan --auto-generate`
- [ ] **Discovery artifacts uploaded**: Check Actions tab for discovery artifacts
- [ ] **Context pack generated**: `python3 builder/cli.py ctx:pack --stdout`

### 📋 Document Validation

#### PRD Validation (docs/prd/)
- [ ] **PRD structure valid**: All required sections present (Problem, Goals, Requirements, Acceptance Criteria)
- [ ] **Acceptance criteria defined**: Clear, testable criteria with checkboxes
- [ ] **Success metrics specified**: Measurable outcomes defined
- [ ] **Technical stack documented**: Technology choices justified

#### ADR Validation (docs/adrs/)
- [ ] **ADR structure valid**: Status, Context, Decision, Consequences sections present
- [ ] **Decision rationale**: Clear reasoning for architectural decisions
- [ ] **Consequences documented**: Impact and trade-offs clearly stated
- [ ] **Related PRD linked**: ADR references relevant PRD if applicable

#### Architecture Validation (docs/arch/)
- [ ] **System design documented**: High-level architecture and component relationships
- [ ] **Diagrams included**: Architecture diagrams (Mermaid or other) present
- [ ] **Technical stack justified**: Technology choices explained
- [ ] **Scalability considerations**: Performance and scaling approach documented

#### Execution Validation (docs/exec/)
- [ ] **Deployment strategy**: Clear deployment approach and timeline
- [ ] **Dependencies listed**: All required resources and prerequisites
- [ ] **Risk assessment**: Potential issues and mitigation strategies
- [ ] **Rollback plan**: Recovery procedures documented

#### Implementation Validation (docs/impl/)
- [ ] **Development approach**: Clear implementation strategy
- [ ] **Code examples**: Relevant code snippets or pseudocode included
- [ ] **Testing strategy**: Unit, integration, and E2E testing approach
- [ ] **Performance considerations**: Optimization and monitoring approach

#### Integration Validation (docs/integrations/)
- [ ] **API contracts**: External service interfaces documented
- [ ] **Data flows**: Information flow between systems specified
- [ ] **Authentication**: Security and access control documented
- [ ] **Error handling**: Failure scenarios and recovery documented

#### Task Validation (docs/tasks/)
- [ ] **Task breakdown**: Clear, actionable tasks with acceptance criteria
- [ ] **Dependencies**: Task sequencing and prerequisites documented
- [ ] **Timeline**: Realistic estimates and milestones
- [ ] **Resources**: Required team members and skills

#### UX Validation (docs/ux/)
- [ ] **User research**: User needs, personas, and use cases documented
- [ ] **Design system**: UI/UX patterns and component specifications
- [ ] **User flows**: Complete user journey and interaction patterns
- [ ] **Accessibility**: WCAG compliance and inclusive design considerations

### 🔗 Cross-Document Validation
<!-- Check that related documents are updated when making changes -->
- [ ] **PRD changes**: Related ADR, ARCH, IMPL, UX documents updated
- [ ] **ADR changes**: Related PRD, ARCH, IMPL documents updated
- [ ] **ARCH changes**: Related PRD, ADR, IMPL, EXEC documents updated
- [ ] **IMPL changes**: Related PRD, ARCH, TASKS documents updated
- [ ] **EXEC changes**: Related PRD, ARCH, IMPL documents updated
- [ ] **UX changes**: Related PRD, IMPL documents updated

## 🔍 Context Pack Preview

<!-- This section shows the context pack for reviewers to understand what was built -->

<details>
<summary>📄 Context Pack Output (Click to expand)</summary>

### 🚀 Quick Context Generation
```bash
# Generate context pack for this PR
python3 builder/cli.py ctx:pack --stdout

# Or build context for specific file
python3 builder/cli.py ctx:build <target_path> --purpose implement --feature <feature> --stacks <stacks> --token-limit 8000
```

### 📋 Context Pack Content
<!-- 
Paste the output of `python3 builder/cli.py ctx:pack --stdout` below:
1. Run the command above
2. Copy the entire output
3. Paste it in the code block below
4. This helps reviewers understand the context without running commands locally
-->

```markdown
# Paste ctx:pack --stdout output here

# Example:
# ===========================================
# Context Pack: Task Manager Implementation
# ===========================================
# 
# ## Rules
# - Use TypeScript for all new code
# - Follow React best practices
# - Implement proper error handling
# 
# ## Acceptance Criteria
# - [ ] Users can create tasks
# - [ ] Users can mark tasks complete
# - [ ] Real-time updates work
# 
# ## Architecture
# - Component-based React architecture
# - RESTful API design
# - WebSocket for real-time updates
# 
# ## Code Excerpts
# [Relevant code snippets will appear here]
```

### 🔧 Alternative: Context Markdown
<!-- If ctx:pack --stdout is not available, use context.md instead -->
```markdown
<!-- 
Alternative: Copy first 200 lines of builder/cache/context.md here
This provides the same context information in markdown format
-->
```

</details>

## 🧪 Testing

<!-- Describe how you tested these changes -->

- [ ] Local testing completed
- [ ] Context building verified
- [ ] Documentation validation passed
- [ ] No breaking changes introduced

## 📚 Documentation

<!-- List any documentation changes or additions -->

- [ ] Documentation updated (if applicable)
- [ ] README updated (if applicable)
- [ ] Comments added to code (if applicable)

## 🔗 Related Issues

<!-- Link to any related issues or discussions -->

Closes #<!-- issue number -->

## 📝 Additional Notes

<!-- Any additional information for reviewers -->

---

**For Reviewers:**
- Check the context preview above to understand what was built
- Verify all checklist items are completed
- Test the changes locally if needed
- Ensure the context pack is relevant and complete
