#!/usr/bin/env python3
"""
Cleanup Rules for Test/Example Artifacts

This module defines rules for automatically detecting and cleaning up
test and example artifacts that are created outside of designated
test/example directories.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class CleanupRule:
    """A rule for detecting and cleaning up artifacts."""
    name: str
    pattern: str
    description: str
    directories_to_ignore: List[str]
    file_extensions: List[str] = None
    is_regex: bool = True


class ArtifactCleaner:
    """Cleans up test and example artifacts based on defined rules."""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.rules = self._load_cleanup_rules()
        self.designated_dirs = {
            "test": ["test/", "tests/", "spec/", "specs/"],
            "example": ["examples/", "docs/examples/", "sample/", "samples/"],
            "cache": ["builder/cache/", ".cache/", "node_modules/", ".git/"],
            "venv": [".venv/", "venv/", "env/", ".env/"]
        }
    
    def _load_cleanup_rules(self) -> List[CleanupRule]:
        """Load cleanup rules for different types of artifacts."""
        return [
            # Test documents
            CleanupRule(
                name="test_documents",
                pattern=r"^(PRD|ARCH|IMPL|EXEC|UX|INTEGRATIONS|TASKS|ADR)-\d{4}-\d{2}-\d{2}-test-",
                description="Test documents with test- prefix",
                directories_to_ignore=["test/", "tests/", "docs/examples/"],
                file_extensions=[".md"]
            ),
            
            # Example documents
            CleanupRule(
                name="example_documents",
                pattern=r"^(PRD|ARCH|IMPL|EXEC|UX|INTEGRATIONS|TASKS|ADR)-\d{4}-\d{2}-\d{2}-example-",
                description="Example documents with example- prefix",
                directories_to_ignore=["examples/", "docs/examples/", "sample/"],
                file_extensions=[".md"]
            ),
            
            # Temporary files
            CleanupRule(
                name="temp_files",
                pattern=r"^temp_|^tmp_|\.tmp$|\.temp$",
                description="Temporary files",
                directories_to_ignore=["test/", "tests/", "temp/", "tmp/"],
                file_extensions=[".py", ".md", ".txt", ".json", ".yml", ".yaml"]
            ),
            
            # Backup files
            CleanupRule(
                name="backup_files",
                pattern=r"\.save$|\.bak$|\.backup$|~$",
                description="Backup files",
                directories_to_ignore=["test/", "tests/", "backup/", "backups/"],
                file_extensions=[".md", ".py", ".txt", ".json", ".yml", ".yaml"]
            ),
            
            # Test data files
            CleanupRule(
                name="test_data",
                pattern=r"test_.*\.(json|yml|yaml|md|py)$",
                description="Test data files",
                directories_to_ignore=["test/", "tests/", "fixtures/", "data/"],
                file_extensions=[".json", ".yml", ".yaml", ".md", ".py"]
            ),
            
            # Empty template documents
            CleanupRule(
                name="empty_templates",
                pattern=r"^(PRD|ARCH|IMPL|EXEC|UX|INTEGRATIONS|TASKS|ADR)-\d{4}-\d{2}-\d{2}-.*\.md$",
                description="Empty template documents",
                directories_to_ignore=["templates/", "docs/templates/"],
                file_extensions=[".md"]
            )
        ]
    
    def is_in_designated_directory(self, file_path: Path) -> bool:
        """Check if a file is in a designated test/example directory."""
        file_str = str(file_path)
        for dir_type, dirs in self.designated_dirs.items():
            for dir_pattern in dirs:
                if file_str.startswith(dir_pattern) or f"/{dir_pattern}" in file_str:
                    return True
        return False
    
    def is_empty_template(self, file_path: Path) -> bool:
        """Check if a document is an empty template."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Check for YAML front matter
            if not content.startswith("---"):
                return False
            
            # Extract front matter
            front_matter_match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not front_matter_match:
                return False
            
            front_matter = front_matter_match.group(1)
            body = content[front_matter_match.end():].strip()
            
            # Check if body is empty or only contains empty sections
            if body and not re.match(r'^#+\s*\n*$', body):
                return False
            
            # Check for empty sections in body
            sections = re.findall(r'^##+\s+.*$', body, re.MULTILINE)
            if sections:
                # Check if all sections are empty
                for section in sections:
                    section_content = re.search(
                        rf'^{re.escape(section)}\s*\n(.*?)(?=^##|\Z)',
                        body,
                        re.DOTALL | re.MULTILINE
                    )
                    if section_content and section_content.group(1).strip():
                        return False
            
            return True
        except Exception:
            return False
    
    def find_artifacts(self, dry_run: bool = True) -> Dict[str, List[Path]]:
        """Find artifacts that should be cleaned up."""
        artifacts = {}
        
        for rule in self.rules:
            artifacts[rule.name] = []
            
            # Search for files matching the pattern
            for file_path in self.root_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Skip if in designated directory
                if self.is_in_designated_directory(file_path):
                    continue
                
                # Check file extension
                if rule.file_extensions and file_path.suffix not in rule.file_extensions:
                    continue
                
                # Check pattern match
                if rule.is_regex:
                    if re.search(rule.pattern, file_path.name):
                        artifacts[rule.name].append(file_path)
                else:
                    if rule.pattern in file_path.name:
                        artifacts[rule.name].append(file_path)
            
            # Special handling for empty templates
            if rule.name == "empty_templates":
                empty_templates = []
                for file_path in artifacts[rule.name]:
                    if self.is_empty_template(file_path):
                        empty_templates.append(file_path)
                artifacts[rule.name] = empty_templates
        
        return artifacts
    
    def cleanup_artifacts(self, dry_run: bool = True) -> Dict[str, List[Path]]:
        """Clean up found artifacts."""
        artifacts = self.find_artifacts(dry_run)
        cleaned = {}
        
        for rule_name, files in artifacts.items():
            cleaned[rule_name] = []
            
            for file_path in files:
                if dry_run:
                    cleaned[rule_name].append(file_path)
                else:
                    try:
                        file_path.unlink()
                        cleaned[rule_name].append(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        return cleaned
    
    def print_cleanup_report(self, artifacts: Dict[str, List[Path]]) -> None:
        """Print a report of found artifacts."""
        total_files = sum(len(files) for files in artifacts.values())
        
        if total_files == 0:
            print("✅ No artifacts found for cleanup")
            return
        
        print(f"🔍 Found {total_files} artifacts for cleanup:")
        print()
        
        for rule_name, files in artifacts.items():
            if not files:
                continue
            
            rule = next(r for r in self.rules if r.name == rule_name)
            print(f"📋 {rule.description} ({len(files)} files):")
            
            for file_path in files:
                relative_path = file_path.relative_to(self.root_dir)
                print(f"  - {relative_path}")
            print()


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up test/example artifacts")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Show what would be cleaned up without actually deleting")
    parser.add_argument("--clean", action="store_true",
                       help="Actually perform the cleanup")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    
    args = parser.parse_args()
    
    cleaner = ArtifactCleaner(args.root)
    
    if args.clean:
        print("🧹 Cleaning up artifacts...")
        cleaned = cleaner.cleanup_artifacts(dry_run=False)
        cleaner.print_cleanup_report(cleaned)
    else:
        print("🔍 Scanning for artifacts (dry run)...")
        artifacts = cleaner.find_artifacts(dry_run=True)
        cleaner.print_cleanup_report(artifacts)
        print("💡 Use --clean to actually perform the cleanup")


if __name__ == "__main__":
    main()
