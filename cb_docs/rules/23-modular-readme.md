# Rule: Modular README Structure

## Purpose
Maintain a modular README structure to improve maintainability, readability, and navigation.

## Rule Statement
The main README.md must remain a concise navigation hub that links to specialized documentation modules rather than containing all content inline.

## Requirements

### 1. Main README Structure
The main README.md must contain:
- **Project title and badges** (lines 1-5)
- **Brief description** (lines 7-8)
- **Quick start section** with essential commands (lines 10-23)
- **Documentation navigation** with links to specialized modules (lines 25-38)
- **System overview** with high-level summary (lines 40-55)
- **Key features** summary (lines 57-65)
- **Why section** with value propositions (lines 67-79)
- **Recent updates** summary (lines 81-95)
- **System statistics** summary (lines 97-105)
- **Contributing, license, and links** (lines 107-121)
- **Quick navigation** footer (lines 123-125)

### 2. Specialized Documentation Modules
Create focused documentation modules in `docs/` directory:
- `README-ARCHITECTURE.md` - Detailed system architecture and interactions
- `README-STATISTICS.md` - Comprehensive statistics and recent improvements
- `README-QUICKSTART.md` - Installation, configuration, and basic usage
- `README-COMMANDS.md` - Complete command reference with examples
- `README-DIRECTORY.md` - Detailed directory structure and organization

### 3. Content Limits
- **Main README**: Maximum 125 lines
- **Each module**: Maximum 200 lines
- **Sections**: Maximum 50 lines per major section
- **Links**: Use descriptive link text with brief descriptions

### 4. Navigation Requirements
- **Cross-references**: Each module must link to related modules
- **Breadcrumbs**: Include "Previous" and "Next" navigation
- **Quick navigation**: Main README footer with links to all modules
- **Consistent formatting**: Use standardized link formats and descriptions

### 5. Content Organization
- **No duplication**: Content must not be duplicated across modules
- **Logical separation**: Each module must have a clear, focused purpose
- **Progressive detail**: Main README provides overview, modules provide details
- **Consistent tone**: Maintain consistent writing style across all modules

## Enforcement

### Validation Checks
1. **Line count**: Main README must not exceed 125 lines
2. **Link validation**: All internal links must be valid and accessible
3. **Content uniqueness**: No content duplication between modules
4. **Navigation completeness**: All modules must have proper navigation links
5. **Structure compliance**: Required sections must be present and properly formatted

### Automated Checks
```bash
# Check README line count
wc -l README.md | grep -q "125" || echo "README too long"

# Validate internal links
grep -o '\[.*\](docs/.*\.md)' README.md | while read link; do
  file=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
  [ -f "$file" ] || echo "Missing file: $file"
done

# Check for content duplication
for file in docs/README-*.md; do
  echo "Checking $file for duplication..."
  # Add specific duplication checks here
done
```

### Manual Review Checklist
- [ ] Main README is concise and focused on navigation
- [ ] All specialized modules exist and are properly linked
- [ ] No content is duplicated between modules
- [ ] Navigation links work correctly
- [ ] Each module has a clear, focused purpose
- [ ] Content is logically organized and easy to find
- [ ] Writing style is consistent across all modules

## Benefits
- **Maintainability**: Easier to update specific sections without affecting others
- **Readability**: Users can focus on relevant information without scrolling through everything
- **Navigation**: Clear structure makes it easy to find specific information
- **Collaboration**: Multiple contributors can work on different modules simultaneously
- **Performance**: Faster loading and rendering of focused content

## Examples

### Good: Modular Structure
```markdown
## 📚 Documentation

### Core Documentation
- **[System Architecture](docs/README-ARCHITECTURE.md)** - 10 core systems and their interactions
- **[Quickstart Guide](docs/README-QUICKSTART.md)** - Installation and basic usage
- **[Command Reference](docs/README-COMMANDS.md)** - 104+ CLI commands organized by module
```

### Bad: Inline Content
```markdown
## System Architecture

Code Builder is built around 10 core systems:

### 1. Context Management System
- Graph-based selection: Discovers related items...
- Intelligent ranking: Scores items based on...
[continues for 500+ lines]
```

## Related Rules
- [22-modular-architecture.md](22-modular-architecture.md) - Modular system architecture
- [21-cli-development.md](21-cli-development.md) - CLI development standards
- [20-shell-scripting.md](20-shell-scripting.md) - Shell scripting guidelines
