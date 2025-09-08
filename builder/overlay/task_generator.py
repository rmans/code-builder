#!/usr/bin/env python3
"""
Task Generator

This module provides template-based task generation for the Code Builder system.
It reads task templates and generates new task files following the 5-phase workflow structure.
"""

import re
import click
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from .paths import OverlayPaths


class TaskGenerator:
    """Generates task files from templates."""
    
    def __init__(self):
        self.overlay_paths = OverlayPaths()
        self.templates_dir = Path("cb_docs/templates")
        self.tasks_dir = Path("cb_docs/tasks")
        self.task_template = self.templates_dir / "tasks.md.hbs"
    
    def generate_task(self, 
                     task_id: str,
                     title: str,
                     description: str = "",
                     owner: str = "system",
                     priority: int = 5,
                     agent_type: str = "general",
                     tags: List[str] = None,
                     dependencies: List[str] = None,
                     acceptance_criteria: List[str] = None,
                     links: Dict[str, List[str]] = None,
                     requires_abc_iteration: bool = False,
                     abc_target_file: str = "",
                     abc_rounds: int = 3,
                     overwrite: bool = False) -> bool:
        """
        Generate a new task file from template.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Task description
            owner: Task owner
            priority: Task priority (1-10)
            agent_type: Agent type (general, backend, frontend, ai, etc.)
            tags: List of tags
            dependencies: List of dependency task IDs
            acceptance_criteria: List of acceptance criteria
            links: Dictionary of links to other documents
            requires_abc_iteration: Whether task requires ABC iteration
            abc_target_file: Target file for ABC iteration
            abc_rounds: Number of ABC iteration rounds
            overwrite: Whether to overwrite existing file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not task_id or not title:
                print("❌ Task ID and title are required")
                return False
            
            # Set defaults
            if tags is None:
                tags = []
            if dependencies is None:
                dependencies = []
            if acceptance_criteria is None:
                acceptance_criteria = []
            if links is None:
                links = {}
            
            # Check if task already exists
            task_file = self.tasks_dir / f"{task_id}.md"
            if task_file.exists() and not overwrite:
                print(f"⚠️  Task {task_id} already exists. Use --overwrite to replace.")
                return False
            
            # Read template
            if not self.task_template.exists():
                print(f"❌ Task template not found: {self.task_template}")
                return False
            
            with open(self.task_template, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Prepare context
            context = {
                'id': task_id,
                'title': title,
                'owner': owner,
                'created': datetime.now().strftime('%Y-%m-%d'),
                'priority': str(priority),  # Convert to string for template
                'agent_type': agent_type,
                'tags': str(tags),  # Convert to string for template
                'requires_abc_iteration': str(requires_abc_iteration).lower(),
                'abc_target_file': abc_target_file,
                'abc_rounds': str(abc_rounds),
                'links': links
            }
            
            # Process template
            processed_content = self._process_template(template_content, context)
            
            # Add acceptance criteria
            if acceptance_criteria:
                criteria_section = "\n".join([f"- [ ] {criterion}" for criterion in acceptance_criteria])
                processed_content = processed_content.replace(
                    "- [ ] Criterion 1\n- [ ] Criterion 2\n- [ ] Criterion 3",
                    criteria_section
                )
            
            # Add dependencies
            if dependencies:
                deps_section = "\n".join([f"- {dep}" for dep in dependencies])
                processed_content = processed_content.replace(
                    "<!-- List any task dependencies -->",
                    deps_section
                )
            
            # Add description
            if description:
                processed_content = processed_content.replace(
                    "<!-- Brief description of what this task accomplishes -->",
                    description
                )
            
            # Write task file
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"✅ Generated task: {task_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating task: {e}")
            return False
    
    def _process_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Process Handlebars template with context variables."""
        try:
            content = template_content
            
            # Replace simple variables
            for key, value in context.items():
                placeholder = f'{{{{{key}}}}}'
                if isinstance(value, list):
                    # Handle list values
                    if key == 'tags':
                        content = content.replace(placeholder, str(value))
                    else:
                        content = content.replace(placeholder, str(value))
                else:
                    content = content.replace(placeholder, str(value))
            
            # Handle default values like {{links.prd | default([])}}
            content = re.sub(r'\{\{([^}]+)\s*\|\s*default\([^)]+\)\}\}', r'[]', content)
            
            return content
            
        except Exception as e:
            print(f"❌ Error processing template: {e}")
            return template_content
    
    def list_available_templates(self) -> List[str]:
        """List available task templates."""
        try:
            templates = []
            for template_file in self.templates_dir.glob("*.md.hbs"):
                templates.append(template_file.stem)
            return templates
        except Exception as e:
            print(f"❌ Error listing templates: {e}")
            return []
    
    def validate_task_template(self) -> bool:
        """Validate that the task template exists and is properly formatted."""
        try:
            if not self.task_template.exists():
                print(f"❌ Task template not found: {self.task_template}")
                return False
            
            with open(self.task_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = [
                "## 5-Phase Agent Workflow",
                "### Phase 1: 🚀 Implementation",
                "### Phase 2: 🧪 Testing",
                "### Phase 3: 📚 Documentation",
                "### Phase 4: 🧹 Cleanup",
                "### Phase 5: 💾 Commit",
                "## Acceptance Criteria"
            ]
            
            for section in required_sections:
                if section not in content:
                    print(f"❌ Missing required section: {section}")
                    return False
            
            print("✅ Task template validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Error validating template: {e}")
            return False


@click.command("generate-task")
@click.option("--id", required=True, help="Task ID (e.g., TASK-2025-09-07-F05)")
@click.option("--title", required=True, help="Task title")
@click.option("--description", default="", help="Task description")
@click.option("--owner", default="system", help="Task owner")
@click.option("--priority", type=int, default=5, help="Task priority (1-10)")
@click.option("--agent-type", default="general", help="Agent type")
@click.option("--tags", multiple=True, help="Task tags")
@click.option("--dependencies", multiple=True, help="Task dependencies")
@click.option("--acceptance-criteria", multiple=True, help="Acceptance criteria")
@click.option("--overwrite", is_flag=True, help="Overwrite existing task")
@click.option("--abc-iteration", is_flag=True, help="Require ABC iteration")
@click.option("--abc-target", default="", help="ABC iteration target file")
@click.option("--abc-rounds", type=int, default=3, help="Number of ABC rounds")
def generate_task_cli(id, title, description, owner, priority, agent_type, tags, 
                     dependencies, acceptance_criteria, overwrite, abc_iteration, 
                     abc_target, abc_rounds):
    """Generate a new task file from template."""
    try:
        generator = TaskGenerator()
        
        # Validate template first
        if not generator.validate_task_template():
            return 1
        
        # Convert CLI options to appropriate types
        tags_list = list(tags) if tags else []
        deps_list = list(dependencies) if dependencies else []
        criteria_list = list(acceptance_criteria) if acceptance_criteria else []
        
        # Generate task
        success = generator.generate_task(
            task_id=id,
            title=title,
            description=description,
            owner=owner,
            priority=priority,
            agent_type=agent_type,
            tags=tags_list,
            dependencies=deps_list,
            acceptance_criteria=criteria_list,
            requires_abc_iteration=abc_iteration,
            abc_target_file=abc_target,
            abc_rounds=abc_rounds,
            overwrite=overwrite
        )
        
        if success:
            print(f"✅ Task {id} generated successfully")
            return 0
        else:
            print(f"❌ Failed to generate task {id}")
            return 1
            
    except Exception as e:
        print(f"❌ Error generating task: {e}")
        return 1


@click.command("list-task-templates")
def list_task_templates_cli():
    """List available task templates."""
    try:
        generator = TaskGenerator()
        templates = generator.list_available_templates()
        
        if templates:
            print("Available task templates:")
            for template in templates:
                print(f"  - {template}")
        else:
            print("No task templates found")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error listing templates: {e}")
        return 1


@click.command("validate-task-template")
def validate_task_template_cli():
    """Validate the task template."""
    try:
        generator = TaskGenerator()
        
        if generator.validate_task_template():
            print("✅ Task template is valid")
            return 0
        else:
            print("❌ Task template validation failed")
            return 1
            
    except Exception as e:
        print(f"❌ Error validating template: {e}")
        return 1


if __name__ == "__main__":
    # Test the task generator
    generator = TaskGenerator()
    
    # Validate template
    if generator.validate_task_template():
        print("✅ Template validation passed")
        
        # Test generation
        success = generator.generate_task(
            task_id="TASK-2025-09-07-TEST",
            title="Test Task Generation",
            description="This is a test task generated from template",
            owner="test-agent",
            priority=7,
            agent_type="backend",
            tags=["test", "generation"],
            acceptance_criteria=["Generate task successfully", "Validate template processing"],
            overwrite=True
        )
        
        if success:
            print("✅ Test task generation successful")
        else:
            print("❌ Test task generation failed")
    else:
        print("❌ Template validation failed")
