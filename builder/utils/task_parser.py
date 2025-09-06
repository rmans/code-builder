#!/usr/bin/env python3
"""
Task File Parser

This module parses TASK-*.md files and converts them into executable tasks
for the orchestration system.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .task_orchestrator import Task, TaskStatus


@dataclass
class TaskFile:
    """Represents a parsed task file."""
    file_path: str
    task_id: str
    title: str
    status: str
    domain: str
    owner: str
    created: str
    tags: List[str]
    links: Dict[str, List[str]]
    content: str
    frontmatter: Dict[str, Any]


class TaskFileParser:
    """Parses TASK-*.md files and extracts task information."""
    
    def __init__(self, tasks_dir: str = "docs/tasks"):
        self.tasks_dir = Path(tasks_dir)
    
    def find_task_files(self) -> List[Path]:
        """Find all TASK-*.md files in the tasks directory."""
        if not self.tasks_dir.exists():
            return []
        
        task_files = []
        for file_path in self.tasks_dir.glob("TASK-*.md"):
            if file_path.is_file():
                task_files.append(file_path)
        
        return sorted(task_files)
    
    def parse_task_file(self, file_path: Path) -> Optional[TaskFile]:
        """Parse a single task file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Split frontmatter and content
            if not content.startswith('---'):
                return None
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
            
            frontmatter_text = parts[1]
            body_content = parts[2].strip()
            
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_text)
            if not frontmatter:
                return None
            
            # Extract task information
            task_file = TaskFile(
                file_path=str(file_path),
                task_id=frontmatter.get('id', ''),
                title=frontmatter.get('title', ''),
                status=frontmatter.get('status', 'draft'),
                domain=frontmatter.get('domain', ''),
                owner=frontmatter.get('owner', ''),
                created=frontmatter.get('created', ''),
                tags=frontmatter.get('tags', []),
                links=frontmatter.get('links', {}),
                content=body_content,
                frontmatter=frontmatter
            )
            
            return task_file
            
        except Exception as e:
            print(f"Warning: Could not parse task file {file_path}: {e}")
            return None
    
    def parse_all_task_files(self) -> List[TaskFile]:
        """Parse all task files in the tasks directory."""
        task_files = []
        for file_path in self.find_task_files():
            task_file = self.parse_task_file(file_path)
            if task_file:
                task_files.append(task_file)
        
        return task_files
    
    def extract_command_from_content(self, content: str) -> str:
        """Extract command from task content."""
        # Look for code blocks with specific language tags
        code_blocks = re.findall(r'```(?:bash|sh|python|cmd|powershell)\n(.*?)\n```', content, re.DOTALL)
        if code_blocks:
            # Use the first code block as the command
            return code_blocks[0].strip()
        
        # Look for command patterns
        command_patterns = [
            r'```\n(.*?)\n```',  # Generic code blocks
            r'`([^`]+)`',  # Inline code
            r'Command:\s*(.+?)(?:\n|$)',  # "Command:" followed by text
            r'Execute:\s*(.+?)(?:\n|$)',  # "Execute:" followed by text
            r'Run:\s*(.+?)(?:\n|$)',  # "Run:" followed by text
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Default command if nothing found
        return f"echo 'Task: {content[:50]}...'"
    
    def extract_dependencies_from_content(self, content: str, links: Dict[str, List[str]]) -> List[str]:
        """Extract task dependencies from content and links."""
        dependencies = []
        
        # Extract from links
        for link_type, link_list in links.items():
            if link_type == 'tasks' and link_list:
                dependencies.extend(link_list)
        
        # Extract from content (look for task references)
        task_refs = re.findall(r'TASK-\d{4}-\d{2}-\d{2}-[a-zA-Z0-9-]+', content)
        dependencies.extend(task_refs)
        
        # Remove duplicates and return
        return list(set(dependencies))
    
    def extract_estimated_duration(self, content: str) -> int:
        """Extract estimated duration from content (in minutes)."""
        # Look for duration patterns
        duration_patterns = [
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:days?)',
            r'Duration:\s*(\d+)\s*(?:minutes?|mins?|hours?|hrs?|days?)',
            r'Estimated:\s*(\d+)\s*(?:minutes?|mins?|hours?|hrs?|days?)',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                duration = int(matches[0])
                # Convert to minutes
                if 'hour' in pattern.lower() or 'hr' in pattern.lower():
                    duration *= 60
                elif 'day' in pattern.lower():
                    duration *= 24 * 60
                return duration
        
        # Default duration based on content length
        word_count = len(content.split())
        if word_count < 100:
            return 5  # 5 minutes
        elif word_count < 500:
            return 15  # 15 minutes
        else:
            return 30  # 30 minutes
    
    def extract_priority(self, content: str, tags: List[str]) -> int:
        """Extract priority from content and tags."""
        # Check tags for priority indicators
        priority_tags = {
            'critical': 10,
            'high': 8,
            'urgent': 9,
            'medium': 5,
            'low': 2,
            'nice-to-have': 1
        }
        
        for tag in tags:
            if tag.lower() in priority_tags:
                return priority_tags[tag.lower()]
        
        # Check content for priority indicators
        content_lower = content.lower()
        if 'critical' in content_lower or 'urgent' in content_lower:
            return 9
        elif 'high priority' in content_lower or 'important' in content_lower:
            return 8
        elif 'low priority' in content_lower or 'optional' in content_lower:
            return 2
        
        # Default priority
        return 5
    
    def extract_agent_type(self, content: str, tags: List[str], domain: str) -> str:
        """Extract agent type from content, tags, and domain."""
        # Check tags for agent type indicators
        agent_tags = {
            'frontend': 'frontend',
            'backend': 'backend',
            'api': 'backend',
            'database': 'backend',
            'ui': 'frontend',
            'ux': 'frontend',
            'testing': 'testing',
            'test': 'testing',
            'docs': 'docs',
            'documentation': 'docs',
            'deployment': 'deployment',
            'devops': 'deployment',
            'setup': 'setup',
            'configuration': 'setup',
            'security': 'security',
            'performance': 'performance',
            'refactoring': 'refactoring'
        }
        
        for tag in tags:
            if tag.lower() in agent_tags:
                return agent_tags[tag.lower()]
        
        # Check content for agent type indicators
        content_lower = content.lower()
        if any(word in content_lower for word in ['react', 'vue', 'angular', 'component', 'ui', 'frontend']):
            return 'frontend'
        elif any(word in content_lower for word in ['api', 'endpoint', 'server', 'backend', 'database']):
            return 'backend'
        elif any(word in content_lower for word in ['test', 'testing', 'spec', 'unit', 'integration']):
            return 'testing'
        elif any(word in content_lower for word in ['documentation', 'docs', 'readme', 'guide']):
            return 'docs'
        elif any(word in content_lower for word in ['deploy', 'deployment', 'docker', 'kubernetes']):
            return 'deployment'
        elif any(word in content_lower for word in ['setup', 'install', 'configure', 'initial']):
            return 'setup'
        
        # Check domain
        if domain:
            domain_lower = domain.lower()
            if any(word in domain_lower for word in ['frontend', 'ui', 'ux']):
                return 'frontend'
            elif any(word in domain_lower for word in ['backend', 'api', 'server']):
                return 'backend'
            elif any(word in domain_lower for word in ['testing', 'qa']):
                return 'testing'
            elif any(word in domain_lower for word in ['docs', 'documentation']):
                return 'docs'
            elif any(word in domain_lower for word in ['deployment', 'devops']):
                return 'deployment'
        
        # Default agent type
        return 'general'
    
    def convert_to_orchestrator_task(self, task_file: TaskFile) -> Task:
        """Convert a TaskFile to an orchestrator Task."""
        # Extract information from content
        command = self.extract_command_from_content(task_file.content)
        dependencies = self.extract_dependencies_from_content(task_file.content, task_file.links)
        estimated_duration = self.extract_estimated_duration(task_file.content)
        priority = self.extract_priority(task_file.content, task_file.tags)
        agent_type = self.extract_agent_type(task_file.content, task_file.tags, task_file.domain)
        
        # Determine working directory
        working_directory = os.path.dirname(task_file.file_path)
        
        # Create orchestrator task
        orchestrator_task = Task(
            task_id=task_file.task_id,
            name=task_file.title,
            description=task_file.content[:200] + "..." if len(task_file.content) > 200 else task_file.content,
            command=command,
            working_directory=working_directory,
            dependencies=dependencies,
            estimated_duration=estimated_duration,
            priority=priority,
            agent_type=agent_type,
            status=TaskStatus.PENDING
        )
        
        return orchestrator_task
    
    def load_tasks_from_files(self) -> List[Task]:
        """Load all tasks from TASK-*.md files and convert to orchestrator tasks."""
        task_files = self.parse_all_task_files()
        orchestrator_tasks = []
        
        for task_file in task_files:
            try:
                orchestrator_task = self.convert_to_orchestrator_task(task_file)
                orchestrator_tasks.append(orchestrator_task)
            except Exception as e:
                print(f"Warning: Could not convert task {task_file.task_id}: {e}")
        
        return orchestrator_tasks
