#!/usr/bin/env python3
"""
Dynamic Content Updater

This module provides dynamic content updating capabilities for replacing
placeholders and keeping task status synchronized.
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta

from ..config.settings import get_config
from ..overlay.paths import OverlayPaths


class DynamicContentUpdater:
    """Updates dynamic content with current project state."""
    
    def __init__(self, cache_dir: str = None):
        config = get_config()
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        
        self.cache_dir = Path(cache_dir)
        self.overlay_paths = OverlayPaths()
        self.last_update_time = 0
        self.update_debounce_seconds = 5  # Debounce updates
        
        # Load project context
        self.project_context = self._load_project_context()
    
    def _load_project_context(self) -> Dict[str, Any]:
        """Load current project context from discovery data."""
        try:
            # Try to load from discovery data
            discovery_file = self.overlay_paths.get_docs_dir() / "discovery" / "discovery_data.json"
            if discovery_file.exists():
                import json
                with open(discovery_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Fallback to basic project detection
        return self._detect_project_context()
    
    def _detect_project_context(self) -> Dict[str, Any]:
        """Detect project context from file system."""
        context = {
            "project_type": "unknown",
            "language": "unknown",
            "framework": "unknown",
            "name": "unknown",
            "description": "unknown"
        }
        
        # Detect language and framework
        if (Path(".") / "package.json").exists():
            context["language"] = "javascript"
            context["framework"] = "node"
            context["project_type"] = "web"
        elif (Path(".") / "requirements.txt").exists():
            context["language"] = "python"
            context["framework"] = "python"
            context["project_type"] = "backend"
        elif (Path(".") / "Cargo.toml").exists():
            context["language"] = "rust"
            context["framework"] = "rust"
            context["project_type"] = "system"
        elif (Path(".") / "go.mod").exists():
            context["language"] = "go"
            context["framework"] = "go"
            context["project_type"] = "backend"
        elif (Path(".") / "pom.xml").exists():
            context["language"] = "java"
            context["framework"] = "maven"
            context["project_type"] = "enterprise"
        
        # Detect project name
        if (Path(".") / "package.json").exists():
            try:
                import json
                with open("package.json", 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    context["name"] = package_data.get("name", "unknown")
                    context["description"] = package_data.get("description", "unknown")
            except Exception:
                pass
        
        return context
    
    def update_content(self, content: str, content_type: str = "general") -> str:
        """Update content with current project context."""
        updated_content = content
        
        # Replace common placeholders
        placeholders = {
            "[PROJECT_TYPE]": self.project_context.get("project_type", "unknown"),
            "[LANGUAGE]": self.project_context.get("language", "unknown"),
            "[FRAMEWORK]": self.project_context.get("framework", "unknown"),
            "[PROJECT_NAME]": self.project_context.get("name", "unknown"),
            "[PROJECT_DESCRIPTION]": self.project_context.get("description", "unknown"),
            "[CURRENT_DATE]": datetime.now().strftime("%Y-%m-%d"),
            "[CURRENT_TIME]": datetime.now().strftime("%H:%M:%S"),
            "[CURRENT_DATETIME]": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for placeholder, value in placeholders.items():
            updated_content = updated_content.replace(placeholder, str(value))
        
        # Update content type specific placeholders
        if content_type == "task":
            updated_content = self._update_task_content(updated_content)
        elif content_type == "command":
            updated_content = self._update_command_content(updated_content)
        elif content_type == "rule":
            updated_content = self._update_rule_content(updated_content)
        
        return updated_content
    
    def _update_task_content(self, content: str) -> str:
        """Update task-specific content."""
        # Update task status placeholders
        task_status = self._get_current_task_status()
        
        placeholders = {
            "[TASK_STATUS]": task_status.get("status", "unknown"),
            "[ACTIVE_TASKS]": str(task_status.get("active_count", 0)),
            "[COMPLETED_TASKS]": str(task_status.get("completed_count", 0)),
            "[TOTAL_TASKS]": str(task_status.get("total_count", 0))
        }
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _update_command_content(self, content: str) -> str:
        """Update command-specific content."""
        # Update command status placeholders
        command_status = self._get_current_command_status()
        
        placeholders = {
            "[COMMAND_STATUS]": command_status.get("status", "unknown"),
            "[AVAILABLE_COMMANDS]": str(command_status.get("available_count", 0)),
            "[COMMAND_CATEGORIES]": ", ".join(command_status.get("categories", []))
        }
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _update_rule_content(self, content: str) -> str:
        """Update rule-specific content."""
        # Update rule status placeholders
        rule_status = self._get_current_rule_status()
        
        placeholders = {
            "[RULE_STATUS]": rule_status.get("status", "unknown"),
            "[ACTIVE_RULES]": str(rule_status.get("active_count", 0)),
            "[RULE_CATEGORIES]": ", ".join(rule_status.get("categories", []))
        }
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _get_current_task_status(self) -> Dict[str, Any]:
        """Get current task status."""
        try:
            # Load task index
            task_index_file = self.overlay_paths.get_docs_dir() / "tasks" / "index.json"
            if task_index_file.exists():
                import json
                with open(task_index_file, 'r', encoding='utf-8') as f:
                    task_index = json.load(f)
                
                tasks = task_index.get("tasks", [])
                active_count = len([t for t in tasks if t.get("status") in ["pending", "ready", "running"]])
                completed_count = len([t for t in tasks if t.get("status") == "completed"])
                
                return {
                    "status": "active" if active_count > 0 else "idle",
                    "active_count": active_count,
                    "completed_count": completed_count,
                    "total_count": len(tasks)
                }
        except Exception:
            pass
        
        return {
            "status": "unknown",
            "active_count": 0,
            "completed_count": 0,
            "total_count": 0
        }
    
    def _get_current_command_status(self) -> Dict[str, Any]:
        """Get current command status."""
        try:
            # Count available commands
            commands_dir = self.overlay_paths.get_commands_dir()
            if commands_dir.exists():
                command_files = list(commands_dir.glob("*.md"))
                categories = set()
                
                for cmd_file in command_files:
                    try:
                        with open(cmd_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith("---"):
                                parts = content.split("---", 2)
                                if len(parts) >= 3:
                                    import yaml
                                    frontmatter = yaml.safe_load(parts[1]) or {}
                                    domain = frontmatter.get("domain", "general")
                                    categories.add(domain)
                    except Exception:
                        pass
                
                return {
                    "status": "active",
                    "available_count": len(command_files),
                    "categories": list(categories)
                }
        except Exception:
            pass
        
        return {
            "status": "unknown",
            "available_count": 0,
            "categories": []
        }
    
    def _get_current_rule_status(self) -> Dict[str, Any]:
        """Get current rule status."""
        try:
            # Count active rules
            rules_dir = self.overlay_paths.get_docs_dir() / "rules"
            if rules_dir.exists():
                rule_files = list(rules_dir.glob("*.md"))
                categories = set()
                
                for rule_file in rule_files:
                    try:
                        with open(rule_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith("---"):
                                parts = content.split("---", 2)
                                if len(parts) >= 3:
                                    import yaml
                                    frontmatter = yaml.safe_load(parts[1]) or {}
                                    category = frontmatter.get("category", "general")
                                    categories.add(category)
                    except Exception:
                        pass
                
                return {
                    "status": "active",
                    "active_count": len(rule_files),
                    "categories": list(categories)
                }
        except Exception:
            pass
        
        return {
            "status": "unknown",
            "active_count": 0,
            "categories": []
        }
    
    def update_file(self, file_path: str, content_type: str = "general") -> bool:
        """Update a file with current project context."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update content
            updated_content = self.update_content(content, content_type)
            
            # Only write if content changed
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating file {file_path}: {e}")
            return False
    
    def update_directory(self, directory: str, content_type: str = "general", 
                        file_pattern: str = "*.md") -> Dict[str, Any]:
        """Update all files in a directory."""
        directory = Path(directory)
        if not directory.exists():
            return {"updated": 0, "errors": 0, "files": []}
        
        updated_files = []
        error_count = 0
        
        for file_path in directory.rglob(file_pattern):
            try:
                if self.update_file(str(file_path), content_type):
                    updated_files.append(str(file_path))
            except Exception as e:
                print(f"Error updating {file_path}: {e}")
                error_count += 1
        
        return {
            "updated": len(updated_files),
            "errors": error_count,
            "files": updated_files
        }
    
    def sync_rules(self) -> bool:
        """Sync rules after content updates."""
        try:
            # Update .cursor/rules/ directory
            cursor_rules_dir = Path(".cursor/rules")
            if cursor_rules_dir.exists():
                result = self.update_directory(str(cursor_rules_dir), "rule")
                return result["updated"] > 0
        except Exception as e:
            print(f"Error syncing rules: {e}")
            return False
    
    def update_with_debounce(self, file_path: str, content_type: str = "general") -> bool:
        """Update file with debouncing to avoid churn."""
        current_time = time.time()
        
        # Check if enough time has passed since last update
        if current_time - self.last_update_time < self.update_debounce_seconds:
            return False
        
        # Update the file
        updated = self.update_file(file_path, content_type)
        
        if updated:
            self.last_update_time = current_time
        
        return updated
    
    def refresh_project_context(self) -> None:
        """Refresh project context from discovery data."""
        self.project_context = self._load_project_context()


def create_content_updater(cache_dir: str = None) -> DynamicContentUpdater:
    """Create a new DynamicContentUpdater instance."""
    return DynamicContentUpdater(cache_dir)


# Global updater instance
content_updater = create_content_updater()


def update_content(content: str, content_type: str = "general") -> str:
    """Update content using the global updater."""
    return content_updater.update_content(content, content_type)


def update_file(file_path: str, content_type: str = "general") -> bool:
    """Update file using the global updater."""
    return content_updater.update_file(file_path, content_type)


def sync_rules() -> bool:
    """Sync rules using the global updater."""
    return content_updater.sync_rules()
