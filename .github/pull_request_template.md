# Pull Request

## 📋 Pre-submission Checklist

Please ensure the following steps have been completed before submitting this PR:

- [ ] **Documentation Validation**: Run `python3 builder/cli.py doc:check` - all documents pass validation
- [ ] **Documentation Quality**: Run `pnpm run docs:all` - markdown linting and spell checking pass
- [ ] **Context Building**: Run `python3 builder/cli.py ctx:build-enhanced <target_path> --purpose implement` - context builds successfully
- [ ] **Tests Pass**: Run `npm run test:all` - both TypeScript and Python tests pass
- [ ] **Code Review**: Self-review of changes for quality and completeness

## 🎯 Changes Summary

<!-- Provide a brief summary of what this PR changes -->

## 🔍 Context Preview

<!-- This section will be automatically populated with context.md content for reviewers -->

<details>
<summary>📄 Context Pack Preview (Click to expand)</summary>

```markdown
<!-- 
To populate this section, run:
python3 builder/cli.py ctx:build-enhanced <target_path> --purpose implement
Then copy the first 200 lines of builder/cache/context.md here
-->

# Context Pack Preview

## System Rules
<!-- Rules and constraints will appear here -->

## Acceptance Criteria  
<!-- Acceptance criteria will appear here -->

## Architecture Decisions
<!-- ADRs and architectural decisions will appear here -->

## Code Excerpts
<!-- Relevant code snippets will appear here -->

<!-- 
Instructions for reviewers:
1. Copy the first 200 lines of builder/cache/context.md into this section
2. This helps reviewers understand the context without running commands locally
3. Update this section if the target path or context changes
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
