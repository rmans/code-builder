#!/usr/bin/env python3
"""
Rules System Integration

This module provides integration with the rules system for document generation,
including rule violation checking and front-matter rule references.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..config.settings import get_config


@dataclass
class RuleViolation:
    """Represents a rule violation."""
    pattern: str
    message: str
    line_number: int
    line_content: str
    severity: str  # "error", "warning", "hint"


class RulesChecker:
    """Checks content against rules and generates violation reports."""
    
    def __init__(self, rules_dir: str = None):
        config = get_config()
        if rules_dir is None:
            docs_dir = config.get_effective_docs_dir()
            if isinstance(docs_dir, str):
                rules_dir = Path(docs_dir) / "rules"
            else:
                rules_dir = docs_dir / "rules"
        
        self.rules_dir = Path(rules_dir)
        self.guardrails_file = self.rules_dir / "guardrails.json"
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load rules from guardrails.json and rule files."""
        rules = {
            "forbidden_patterns": [],
            "hints": [],
            "rule_files": []
        }
        
        # Load guardrails.json
        if self.guardrails_file.exists():
            try:
                with open(self.guardrails_file, 'r', encoding='utf-8') as f:
                    guardrails = json.load(f)
                    rules["forbidden_patterns"] = guardrails.get("forbiddenPatterns", [])
                    rules["hints"] = guardrails.get("hints", [])
            except Exception as e:
                print(f"Warning: Could not load guardrails.json: {e}")
        
        # Load rule files
        for rule_file in self.rules_dir.glob("*.md"):
            if rule_file.name != "guardrails.json":
                rules["rule_files"].append(rule_file.name)
        
        return rules
    
    def check_content(self, content: str, file_path: str = None) -> List[RuleViolation]:
        """Check content against all rules and return violations."""
        violations = []
        lines = content.split('\n')
        
        # Check forbidden patterns
        for pattern_info in self.rules["forbidden_patterns"]:
            pattern = pattern_info["pattern"]
            message = pattern_info["message"]
            
            try:
                regex = re.compile(pattern, re.MULTILINE)
                for i, line in enumerate(lines, 1):
                    if regex.search(line):
                        violations.append(RuleViolation(
                            pattern=pattern,
                            message=message,
                            line_number=i,
                            line_content=line.strip(),
                            severity="error"
                        ))
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
        
        # Check hints
        for hint_info in self.rules["hints"]:
            pattern = hint_info["pattern"]
            message = hint_info["message"]
            
            try:
                regex = re.compile(pattern, re.MULTILINE)
                for i, line in enumerate(lines, 1):
                    if regex.search(line):
                        violations.append(RuleViolation(
                            pattern=pattern,
                            message=message,
                            line_number=i,
                            line_content=line.strip(),
                            severity="hint"
                        ))
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
        
        return violations
    
    def check_file(self, file_path: str) -> List[RuleViolation]:
        """Check a file against rules."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.check_content(content, file_path)
        except Exception as e:
            print(f"Warning: Could not check file {file_path}: {e}")
            return []
    
    def get_rule_references(self, doc_type: str) -> List[str]:
        """Get relevant rule file references for a document type."""
        references = []
        
        # Always include global rules
        if (self.rules_dir / "00-global.md").exists():
            references.append("00-global.md")
        
        # Include project rules
        if (self.rules_dir / "10-project.md").exists():
            references.append("10-project.md")
        
        # Include type-specific rules
        if doc_type == "prd":
            if (self.rules_dir / "feature" / "prd.md").exists():
                references.append("feature/prd.md")
        elif doc_type == "arch":
            if (self.rules_dir / "feature" / "arch.md").exists():
                references.append("feature/arch.md")
        elif doc_type == "int":
            if (self.rules_dir / "feature" / "int.md").exists():
                references.append("feature/int.md")
        elif doc_type == "impl":
            if (self.rules_dir / "feature" / "impl.md").exists():
                references.append("feature/impl.md")
        elif doc_type == "exec":
            if (self.rules_dir / "feature" / "exec.md").exists():
                references.append("feature/exec.md")
        
        # Include implementation rules for all types
        if (self.rules_dir / "15-implementation.md").exists():
            references.append("15-implementation.md")
        
        return references
    
    def generate_violation_report(self, violations: List[RuleViolation], file_path: str = None) -> str:
        """Generate a human-readable violation report."""
        if not violations:
            return "✅ No rule violations found"
        
        report = f"❌ Found {len(violations)} rule violations"
        if file_path:
            report += f" in {file_path}"
        report += ":\n\n"
        
        # Group by severity
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]
        hints = [v for v in violations if v.severity == "hint"]
        
        if errors:
            report += "## Errors\n\n"
            for violation in errors:
                report += f"**Line {violation.line_number}**: {violation.message}\n"
                report += f"```\n{violation.line_content}\n```\n\n"
        
        if warnings:
            report += "## Warnings\n\n"
            for violation in warnings:
                report += f"**Line {violation.line_number}**: {violation.message}\n"
                report += f"```\n{violation.line_content}\n```\n\n"
        
        if hints:
            report += "## Hints\n\n"
            for violation in hints:
                report += f"**Line {violation.line_number}**: {violation.message}\n"
                report += f"```\n{violation.line_content}\n```\n\n"
        
        return report


class RulesIntegrator:
    """Integrates rules checking into document generation."""
    
    def __init__(self, rules_dir: str = None):
        self.checker = RulesChecker(rules_dir)
    
    def add_rule_references_to_frontmatter(self, frontmatter: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Add rule references to document front-matter."""
        rule_refs = self.checker.get_rule_references(doc_type)
        
        if rule_refs:
            frontmatter["rules"] = rule_refs
        
        return frontmatter
    
    def check_and_report_violations(self, content: str, file_path: str = None, 
                                   suppress_hints: bool = False) -> Tuple[bool, str]:
        """Check content for violations and return success status and report."""
        violations = self.checker.check_content(content, file_path)
        
        # Filter out hints if requested
        if suppress_hints:
            violations = [v for v in violations if v.severity != "hint"]
        
        # Check if there are any errors or warnings
        has_errors = any(v.severity in ["error", "warning"] for v in violations)
        
        report = self.checker.generate_violation_report(violations, file_path)
        
        return not has_errors, report
    
    def validate_document(self, content: str, doc_type: str, file_path: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a document against rules and return validation results."""
        # Check for violations
        is_valid, report = self.check_and_report_violations(content, file_path)
        
        # Extract front-matter for rule reference addition
        frontmatter = {}
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
        
        # Add rule references
        frontmatter = self.add_rule_references_to_frontmatter(frontmatter, doc_type)
        
        return is_valid, report, frontmatter


def create_rules_integrator(rules_dir: str = None) -> RulesIntegrator:
    """Create a new RulesIntegrator instance."""
    return RulesIntegrator(rules_dir)


# Global integrator instance
integrator = create_rules_integrator()


def check_document_rules(content: str, doc_type: str, file_path: str = None) -> Tuple[bool, str]:
    """Check document content against rules."""
    return integrator.check_and_report_violations(content, file_path)


def add_rule_references(content: str, doc_type: str) -> str:
    """Add rule references to document front-matter."""
    # Extract front-matter
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    try:
        import yaml
        frontmatter = yaml.safe_load(parts[1]) or {}
        
        # Add rule references
        frontmatter = integrator.add_rule_references_to_frontmatter(frontmatter, doc_type)
        
        # Reconstruct content
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        return f"---\n{new_frontmatter}---{parts[2]}"
    
    except Exception as e:
        print(f"Warning: Could not add rule references: {e}")
        return content
