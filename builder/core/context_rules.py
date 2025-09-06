#!/usr/bin/env python3
"""
Context Rules - Merge and conflict detection for rule sources.

Merges global + project + feature + stack + guardrails.json → rules_md
with conflict detection and source tracking.
"""

import os
import json
import glob
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# Import overlay paths for dual-mode support
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    RULES_DIR = overlay_paths.get_rules_dir()
except ImportError:
    # Fallback for standalone mode
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    RULES_DIR = os.path.join(ROOT, "docs", "rules")

@dataclass
class RuleSource:
    """Represents a rule source with metadata."""
    path: str
    content: str
    priority: int  # Lower number = higher priority
    source_type: str  # 'global', 'project', 'feature', 'stack', 'guardrails'
    feature: Optional[str] = None
    stack: Optional[str] = None

@dataclass
class RuleConflict:
    """Represents a detected conflict between rules."""
    rule_text: str
    conflicting_sources: List[str]
    conflict_type: str  # 'contradiction', 'overlap', 'pattern_conflict'
    severity: str  # 'high', 'medium', 'low'

class ContextRulesMerger:
    """Merges rule sources and detects conflicts."""
    
    def __init__(self):
        self.sources: List[RuleSource] = []
        self.conflicts: List[RuleConflict] = []
        self.merged_md = ""
        self.guardrails = {}
    
    def load_rules(self, feature: Optional[str] = None, stacks: List[str] = None) -> Dict[str, Any]:
        """
        Load and merge rules by precedence with conflict detection.
        
        Precedence order:
        1) feature/<feature>.md (highest)
        2) stack/*<stack>.md (first match per stack)
        3) 15-implementation.md
        4) 10-project.md
        5) 00-global.md (lowest)
        6) guardrails.json (separate)
        """
        if stacks is None:
            stacks = []
            
        self.sources.clear()
        self.conflicts.clear()
        
        # Load all rule sources
        self._load_feature_rules(feature)
        self._load_stack_rules(stacks)
        self._load_implementation_rules()
        self._load_project_rules()
        self._load_global_rules()
        self._load_guardrails()
        
        # Detect conflicts
        self._detect_conflicts()
        
        # Merge rules by priority
        self._merge_rules()
        
        return {
            "rules_markdown": self.merged_md,
            "guardrails": self.guardrails,
            "conflicts": self._format_conflicts(),
            "sources": self._format_sources()
        }
    
    def _load_feature_rules(self, feature: Optional[str]):
        """Load feature-specific rules."""
        if not feature:
            return
            
        feature_path = os.path.join(RULES_DIR, "feature", f"30-{feature}.md")
        if os.path.exists(feature_path):
            content = self._read_file(feature_path)
            if content.strip():
                self.sources.append(RuleSource(
                    path=feature_path,
                    content=content,
                    priority=1,
                    source_type="feature",
                    feature=feature
                ))
    
    def _load_stack_rules(self, stacks: List[str]):
        """Load stack-specific rules."""
        for stack in stacks:
            if not stack:
                continue
                
            matches = sorted(glob.glob(os.path.join(RULES_DIR, "stack", f"*{stack}.md")))
            if matches:
                content = self._read_file(matches[0])
                if content.strip():
                    self.sources.append(RuleSource(
                        path=matches[0],
                        content=content,
                        priority=2,
                        source_type="stack",
                        stack=stack
                    ))
    
    def _load_implementation_rules(self):
        """Load implementation rules."""
        impl_path = os.path.join(RULES_DIR, "15-implementation.md")
        if os.path.exists(impl_path):
            content = self._read_file(impl_path)
            if content.strip():
                self.sources.append(RuleSource(
                    path=impl_path,
                    content=content,
                    priority=3,
                    source_type="implementation"
                ))
    
    def _load_project_rules(self):
        """Load project rules."""
        project_path = os.path.join(RULES_DIR, "10-project.md")
        if os.path.exists(project_path):
            content = self._read_file(project_path)
            if content.strip():
                self.sources.append(RuleSource(
                    path=project_path,
                    content=content,
                    priority=4,
                    source_type="project"
                ))
    
    def _load_global_rules(self):
        """Load global rules."""
        global_path = os.path.join(RULES_DIR, "00-global.md")
        if os.path.exists(global_path):
            content = self._read_file(global_path)
            if content.strip():
                self.sources.append(RuleSource(
                    path=global_path,
                    content=content,
                    priority=5,
                    source_type="global"
                ))
    
    def _load_guardrails(self):
        """Load guardrails.json."""
        guardrails_path = os.path.join(RULES_DIR, "guardrails.json")
        if os.path.exists(guardrails_path):
            try:
                with open(guardrails_path, "r", encoding="utf-8") as f:
                    self.guardrails = json.load(f)
            except Exception:
                self.guardrails = {}
    
    def _read_file(self, path: str) -> str:
        """Read file content safely."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    
    def _detect_conflicts(self):
        """Detect conflicts between rule sources."""
        # Extract rules from each source
        rule_groups = []
        for source in self.sources:
            rules = self._extract_rules(source.content)
            if rules:
                rule_groups.append({
                    'source': source,
                    'rules': rules
                })
        
        # Check for contradictions
        self._detect_contradictions(rule_groups)
        
        # Check for overlapping patterns in guardrails
        self._detect_guardrail_conflicts()
    
    def _extract_rules(self, content: str) -> List[str]:
        """Extract individual rules from markdown content."""
        rules = []
        
        # Split by lines and look for rule patterns
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip headers and metadata
            if line.startswith('#') or line.startswith('---'):
                continue
            
            # Look for bullet points or numbered items (individual rules)
            if line.startswith('-') or line.startswith('*') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                # Clean up the rule text
                rule_text = line.lstrip('-*123456789. ').strip()
                if rule_text:
                    rules.append(rule_text)
        
        return rules
    
    def _detect_contradictions(self, rule_groups: List[Dict]):
        """Detect contradictions between rule groups."""
        # More specific contradiction detection
        contradiction_patterns = [
            # Storage patterns - more flexible matching (lowercase)
            (r'never.*localstorage', r'always.*localstorage'),
            (r'always.*localstorage', r'never.*localstorage'),
            (r'never.*sessionstorage', r'always.*sessionstorage'),
            (r'always.*sessionstorage', r'never.*sessionstorage'),
            
            # Export patterns
            (r'never\s+use\s+default\s+exports', r'always\s+use\s+default\s+exports'),
            (r'always\s+use\s+default\s+exports', r'never\s+use\s+default\s+exports'),
            (r'always\s+use\s+named\s+exports', r'never\s+use\s+named\s+exports'),
            (r'never\s+use\s+named\s+exports', r'always\s+use\s+named\s+exports'),
            
            # Error handling patterns
            (r'never\s+throw\s+strings', r'always\s+throw\s+strings'),
            (r'always\s+throw\s+strings', r'never\s+throw\s+strings'),
            (r'always\s+throw\s+Error', r'never\s+throw\s+Error'),
            (r'never\s+throw\s+Error', r'always\s+throw\s+Error'),
            
            # Loop patterns
            (r'never\s+use\s+while\s+True', r'always\s+use\s+while\s+True'),
            (r'always\s+use\s+while\s+True', r'never\s+use\s+while\s+True'),
        ]
        
        for i, group1 in enumerate(rule_groups):
            for j, group2 in enumerate(rule_groups[i+1:], i+1):
                for rule1 in group1['rules']:
                    for rule2 in group2['rules']:
                        # Check for specific contradictions
                        for pos_pattern, neg_pattern in contradiction_patterns:
                            if (re.search(pos_pattern, rule1.lower()) and 
                                re.search(neg_pattern, rule2.lower())):
                                
                                self.conflicts.append(RuleConflict(
                                    rule_text=f"'{rule1[:100]}...' vs '{rule2[:100]}...'",
                                    conflicting_sources=[
                                        group1['source'].path,
                                        group2['source'].path
                                    ],
                                    conflict_type="contradiction",
                                    severity="high"
                                ))
                                break  # Only report one conflict per rule pair
    
    def _detect_guardrail_conflicts(self):
        """Detect conflicts in guardrails patterns."""
        if not self.guardrails:
            return
        
        forbidden_patterns = self.guardrails.get('forbiddenPatterns', [])
        hints = self.guardrails.get('hints', [])
        
        # Check for overlapping patterns
        for i, forbidden in enumerate(forbidden_patterns):
            for j, hint in enumerate(hints):
                if i != j:  # Don't compare with self
                    forbidden_pattern = forbidden.get('pattern', '')
                    hint_pattern = hint.get('pattern', '')
                    
                    # Simple overlap detection
                    if (forbidden_pattern and hint_pattern and 
                        forbidden_pattern in hint_pattern or 
                        hint_pattern in forbidden_pattern):
                        
                        self.conflicts.append(RuleConflict(
                            rule_text=f"Forbidden: '{forbidden_pattern}' vs Hint: '{hint_pattern}'",
                            conflicting_sources=["guardrails.json"],
                            conflict_type="pattern_conflict",
                            severity="medium"
                        ))
    
    def _merge_rules(self):
        """Merge rules by priority order."""
        # Sort by priority (lower number = higher priority)
        sorted_sources = sorted(self.sources, key=lambda x: x.priority)
        
        # Merge content
        merged_parts = []
        for source in sorted_sources:
            if source.content.strip():
                merged_parts.append(source.content)
        
        self.merged_md = "\n\n---\n\n".join(merged_parts)
    
    def _format_conflicts(self) -> List[Dict[str, Any]]:
        """Format conflicts for output."""
        return [
            {
                "rule_text": conflict.rule_text,
                "conflicting_sources": conflict.conflicting_sources,
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity
            }
            for conflict in self.conflicts
        ]
    
    def _format_sources(self) -> List[Dict[str, Any]]:
        """Format sources for output."""
        return [
            {
                "path": source.path,
                "priority": source.priority,
                "source_type": source.source_type,
                "feature": source.feature,
                "stack": source.stack,
                "content_length": len(source.content)
            }
            for source in sorted(self.sources, key=lambda x: x.priority)
        ]

def merge_context_rules(feature: Optional[str] = None, stacks: List[str] = None) -> Dict[str, Any]:
    """
    Main function to merge context rules with conflict detection.
    
    Args:
        feature: Feature name for feature-specific rules
        stacks: List of technology stacks for stack-specific rules
    
    Returns:
        Dictionary with merged rules, guardrails, conflicts, and sources
    """
    merger = ContextRulesMerger()
    return merger.load_rules(feature, stacks)

# Backward compatibility with existing rules_loader
def load_rules(feature: str | None, stacks: list[str]) -> dict:
    """
    Backward compatible wrapper for existing rules_loader interface.
    """
    result = merge_context_rules(feature, stacks)
    return {
        "rules_markdown": result["rules_markdown"],
        "guardrails": result["guardrails"]
    }
