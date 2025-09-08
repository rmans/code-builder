#!/usr/bin/env python3
"""
Task Index Management

This module provides comprehensive task index schema management for the Code Builder system.
It handles task discovery, metadata extraction, and index generation with a canonical schema.
"""

import json
import yaml
import click
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from .cli.base import cli


class TaskIndexManager:
    """Manages task index with canonical schema."""
    
    def __init__(self, tasks_dir: str = "cb_docs/tasks"):
        self.tasks_dir = Path(tasks_dir)
        self.index_file = self.tasks_dir / "index.json"
        self.schema_version = "2.0"
    
    def generate_index(self, force: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive task index with canonical schema.
        
        Args:
            force: Force regeneration even if index exists
            
        Returns:
            dict: Generated index data
        """
        try:
            # Check if index exists and force is not set
            if self.index_file.exists() and not force:
                print("⚠️  Task index already exists. Use --force to regenerate.")
                return self.load_index()
            
            # Discover all task files
            task_files = list(self.tasks_dir.glob("TASK-*.md"))
            if not task_files:
                print("❌ No task files found")
                return {"metadata": {}, "tasks": []}
            
            print(f"🔄 Generating task index for {len(task_files)} tasks...")
            
            # Process each task file
            tasks = []
            for task_file in task_files:
                try:
                    task_data = self._process_task_file(task_file)
                    if task_data:
                        tasks.append(task_data)
                        print(f"✅ Processed {task_data['id']}")
                except Exception as e:
                    print(f"❌ Error processing {task_file.name}: {e}")
            
            # Sort tasks by priority (descending) then by id
            tasks.sort(key=lambda x: (-x.get('priority', 0), x.get('id', '')))
            
            # Create index data
            index_data = {
                "metadata": {
                    "generated": datetime.now().isoformat(),
                    "total_tasks": len(tasks),
                    "version": self.schema_version,
                    "schema": {
                        "version": self.schema_version,
                        "fields": self._get_schema_fields(),
                        "description": "Canonical task index schema for orchestrator and per-task commands"
                    }
                },
                "tasks": tasks
            }
            
            # Write index file
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, sort_keys=True, default=str)
            
            print(f"✅ Generated task index with {len(tasks)} tasks")
            return index_data
            
        except Exception as e:
            print(f"❌ Error generating task index: {e}")
            return {"metadata": {}, "tasks": []}
    
    def load_index(self) -> Dict[str, Any]:
        """Load existing task index."""
        try:
            if not self.index_file.exists():
                return {"metadata": {}, "tasks": []}
            
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading task index: {e}")
            return {"metadata": {}, "tasks": []}
    
    def _process_task_file(self, task_file: Path) -> Optional[Dict[str, Any]]:
        """Process a single task file and extract metadata."""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            import re
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                print(f"⚠️  No frontmatter found in {task_file.name}")
                return None
            
            frontmatter_text = frontmatter_match.group(1)
            metadata = yaml.safe_load(frontmatter_text) or {}
            
            # Extract acceptance criteria from content
            acceptance_criteria = self._extract_acceptance_criteria(content)
            
            # Build task data with canonical schema
            task_data = {
                "id": metadata.get('id', ''),
                "title": metadata.get('title', ''),
                "type": self._determine_task_type(metadata),
                "priority": metadata.get('priority', 5),
                "status": metadata.get('status', 'pending'),
                "deps": metadata.get('dependencies', []),
                "cmd": f"execute-{metadata.get('id', '')}",
                "working_dir": str(task_file.parent),
                "acceptance_criteria": acceptance_criteria,
                "tags": metadata.get('tags', []),
                "file": str(task_file),
                "domain": metadata.get('domain', 'general'),
                "owner": metadata.get('owner', 'system'),
                "agent_type": metadata.get('agent_type', 'backend'),
                "created": metadata.get('created', ''),
                "updated": metadata.get('updated', ''),
                "description": metadata.get('description', '')
            }
            
            return task_data
            
        except Exception as e:
            print(f"❌ Error processing {task_file.name}: {e}")
            return None
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from task content."""
        try:
            import re
            # Look for acceptance criteria sections
            criteria_pattern = r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)'
            matches = re.findall(criteria_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if matches:
                criteria_text = matches[0]
                # Extract bullet points
                criteria_lines = [line.strip() for line in criteria_text.split('\n') if line.strip()]
                criteria = [line for line in criteria_lines if line.startswith('-') or line.startswith('*')]
                return [c[1:].strip() for c in criteria]  # Remove bullet point marker
            
            return []
        except Exception:
            return []
    
    def _determine_task_type(self, metadata: Dict[str, Any]) -> str:
        """Determine task type from metadata."""
        tags = metadata.get('tags', [])
        domain = metadata.get('domain', '')
        
        # Type determination logic
        if 'feature' in tags:
            return 'feature'
        elif 'bug' in tags or 'fix' in tags:
            return 'bugfix'
        elif 'refactor' in tags:
            return 'refactor'
        elif 'documentation' in tags or domain == 'documentation':
            return 'documentation'
        elif 'test' in tags or 'testing' in tags:
            return 'testing'
        elif 'infrastructure' in tags or domain == 'infrastructure':
            return 'infrastructure'
        else:
            return 'general'
    
    def _get_schema_fields(self) -> Dict[str, str]:
        """Get canonical schema field definitions."""
        return {
            "id": "Unique task identifier",
            "title": "Human-readable task title",
            "type": "Task type (feature, bugfix, refactor, documentation, testing, infrastructure, general)",
            "priority": "Task priority (1-10, higher is more important)",
            "status": "Task status (pending, in_progress, completed, cancelled)",
            "deps": "Array of task IDs this task depends on",
            "cmd": "Command to execute this task",
            "working_dir": "Working directory for task execution",
            "acceptance_criteria": "Array of acceptance criteria strings",
            "tags": "Array of categorization tags",
            "file": "Path to task file",
            "domain": "Task domain/category",
            "owner": "Task owner/assignee",
            "agent_type": "Agent type (backend, frontend, ai, etc.)",
            "created": "Creation timestamp",
            "updated": "Last update timestamp",
            "description": "Task description"
        }
    
    def validate_index(self, index_data: Dict[str, Any]) -> bool:
        """Validate task index against schema."""
        try:
            if 'tasks' not in index_data:
                return False
            
            required_fields = ['id', 'title', 'type', 'priority', 'status', 'deps', 'cmd', 'working_dir', 'acceptance_criteria', 'tags']
            
            for task in index_data['tasks']:
                for field in required_fields:
                    if field not in task:
                        print(f"❌ Missing required field '{field}' in task {task.get('id', 'unknown')}")
                        return False
                
                # Validate field types
                if not isinstance(task['deps'], list):
                    print(f"❌ Field 'deps' must be array in task {task['id']}")
                    return False
                
                if not isinstance(task['acceptance_criteria'], list):
                    print(f"❌ Field 'acceptance_criteria' must be array in task {task['id']}")
                    return False
                
                if not isinstance(task['tags'], list):
                    print(f"❌ Field 'tags' must be array in task {task['id']}")
                    return False
                
                if not isinstance(task['priority'], int) or not (1 <= task['priority'] <= 10):
                    print(f"❌ Field 'priority' must be integer 1-10 in task {task['id']}")
                    return False
            
            print("✅ Task index validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Error validating task index: {e}")
            return False


@cli.command("task-index:generate")
@click.option("--force", is_flag=True, help="Force regeneration of existing index")
def generate_task_index(force):
    """Generate comprehensive task index with canonical schema."""
    try:
        manager = TaskIndexManager()
        index_data = manager.generate_index(force=force)
        
        if index_data.get('tasks'):
            click.echo(f"✅ Generated task index with {len(index_data['tasks'])} tasks")
            
            # Validate the generated index
            if manager.validate_index(index_data):
                click.echo("✅ Task index validation passed")
            else:
                click.echo("❌ Task index validation failed")
                return 1
        else:
            click.echo("❌ No tasks found or error generating index")
            return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Error generating task index: {e}")
        return 1


@cli.command("task-index:validate")
def validate_task_index():
    """Validate existing task index against schema."""
    try:
        manager = TaskIndexManager()
        index_data = manager.load_index()
        
        if not index_data.get('tasks'):
            click.echo("❌ No task index found. Run 'task-index:generate' first.")
            return 1
        
        if manager.validate_index(index_data):
            click.echo("✅ Task index is valid")
            return 0
        else:
            click.echo("❌ Task index validation failed")
            return 1
        
    except Exception as e:
        click.echo(f"❌ Error validating task index: {e}")
        return 1


if __name__ == "__main__":
    # Test the task index manager
    manager = TaskIndexManager()
    index_data = manager.generate_index(force=True)
    print(f"Generated index with {len(index_data.get('tasks', []))} tasks")
