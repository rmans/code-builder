# Pull Request

## 📋 Pre-submission Checklist

Please ensure the following steps have been completed before submitting this PR:

### 🔧 Core Validation
- [ ] **Documentation Validation**: Run `python3 builder/cli.py doc:check` - all documents pass validation
- [ ] **Documentation Quality**: Run `pnpm run docs:all` - markdown linting and spell checking pass
- [ ] **Tests Pass**: Run `npm run test:all` - both TypeScript and Python tests pass
- [ ] **Code Review**: Self-review of changes for quality and completeness

### 📄 PRD-Related Changes (if applicable)
<!-- Check these boxes if this PR touches docs/prd/ files -->
- [ ] **Discovery Scan**: Run `python3 builder/cli.py discover:scan --auto-generate` - discovery contexts refreshed
- [ ] **Context Pack**: Run `python3 builder/cli.py ctx:pack --stdout` - context pack generated successfully
- [ ] **Discovery Validation**: Verify discovery artifacts are uploaded in CI (check Actions tab)

### 🎯 Context Building
- [ ] **Context Building**: Run `python3 builder/cli.py ctx:build <target_path> --purpose implement` - context builds successfully

## 🎯 Changes Summary

<!-- Provide a brief summary of what this PR changes -->

## 📄 PRD-Related Changes

<!-- Complete this section if this PR touches docs/prd/ files -->

### 🔍 Discovery Context
- [ ] **Discovery scan completed**: `python3 builder/cli.py discover:scan --auto-generate`
- [ ] **Discovery artifacts uploaded**: Check Actions tab for discovery artifacts
- [ ] **Context pack generated**: `python3 builder/cli.py ctx:pack --stdout`

### 📋 PRD Validation
- [ ] **PRD structure valid**: All required sections present
- [ ] **Acceptance criteria defined**: Clear, testable criteria
- [ ] **Success metrics specified**: Measurable outcomes defined
- [ ] **Technical stack documented**: Technology choices justified

### 🔗 Related Documents
<!-- List any related documents that should be updated -->
- [ ] Architecture document updated (if applicable)
- [ ] Implementation plan updated (if applicable)
- [ ] UX document updated (if applicable)
- [ ] Execution plan updated (if applicable)

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
