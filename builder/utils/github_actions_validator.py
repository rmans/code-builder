#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator - Ensures workflows follow best practices.

This module validates GitHub Actions workflows to prevent common issues like
missing permissions, unhandled API calls, and other workflow problems.
"""

import os
import yaml
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path


class GitHubActionsValidator:
    """Validates GitHub Actions workflows for best practices."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_workflow(self, workflow_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a GitHub Actions workflow file.
        
        Args:
            workflow_path: Path to the workflow YAML file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Could not parse YAML file: {e}")
            return False, self.errors, self.warnings
        
        # Validate workflow structure
        self._validate_workflow_structure(workflow)
        
        # Validate jobs
        if 'jobs' in workflow:
            for job_name, job_config in workflow['jobs'].items():
                self._validate_job(job_name, job_config)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_workflow_structure(self, workflow: Dict[str, Any]) -> None:
        """Validate basic workflow structure."""
        required_fields = ['name', 'jobs']
        for field in required_fields:
            if field not in workflow:
                self.errors.append(f"Missing required field: {field}")
        
        # Check for 'on' field - YAML parser might interpret it as boolean True key
        has_on_field = 'on' in workflow or True in workflow
        if not has_on_field:
            self.errors.append("Missing required field: 'on'")
        elif True in workflow and isinstance(workflow[True], dict):
            # Valid case where 'on:' is parsed as True key with dict value
            pass  # Valid
        elif 'on' in workflow and isinstance(workflow['on'], dict):
            # Standard case where 'on' is a string key
            pass  # Valid
        elif 'on' in workflow and workflow['on'] is True:
            # This is a valid YAML pattern where 'on:' is followed by indented content
            pass  # Valid
        else:
            self.errors.append("'on' field must be a dictionary")
    
    def _validate_job(self, job_name: str, job_config: Dict[str, Any]) -> None:
        """Validate a job configuration."""
        if not isinstance(job_config, dict):
            return
        
        # Check for github-script usage
        uses_github_script = False
        has_permissions = 'permissions' in job_config
        
        if 'steps' in job_config:
            for step in job_config['steps']:
                if isinstance(step, dict) and 'uses' in step:
                    if 'actions/github-script' in step['uses']:
                        uses_github_script = True
                        self._validate_github_script_step(step)
        
        # Check permissions if using github-script
        if uses_github_script and not has_permissions:
            self.errors.append(f"Job '{job_name}' uses github-script but has no permissions block")
        elif uses_github_script and has_permissions:
            self._validate_permissions(job_name, job_config['permissions'])
    
    def _validate_github_script_step(self, step: Dict[str, Any]) -> None:
        """Validate a github-script step."""
        if 'with' not in step or 'script' not in step['with']:
            return
        
        script = step['with']['script']
        
        # Check for proper error handling
        if 'github.rest.issues.createComment' in script or 'github.rest.issues.updateComment' in script:
            if 'try' not in script or 'catch' not in script:
                self.warnings.append("GitHub API calls should be wrapped in try-catch blocks")
        
        # Check for continue-on-error
        if 'continue-on-error' not in step:
            self.warnings.append("github-script steps should have continue-on-error: true")
    
    def _validate_permissions(self, job_name: str, permissions: Dict[str, str]) -> None:
        """Validate job permissions."""
        required_permissions = {
            'contents': 'read',
            'pull-requests': 'write',
            'issues': 'write'
        }
        
        for perm, level in required_permissions.items():
            if perm not in permissions:
                self.errors.append(f"Job '{job_name}' missing required permission: {perm}: {level}")
            elif permissions[perm] != level:
                self.warnings.append(f"Job '{job_name}' permission '{perm}' should be '{level}', got '{permissions[perm]}'")


def validate_workflow_file(workflow_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a workflow file.
    
    Args:
        workflow_path: Path to the workflow YAML file
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = GitHubActionsValidator()
    return validator.validate_workflow(workflow_path)


def validate_all_workflows(workflows_dir: str = '.github/workflows') -> Dict[str, Tuple[bool, List[str], List[str]]]:
    """
    Validate all workflow files in a directory.
    
    Args:
        workflows_dir: Directory containing workflow files
        
    Returns:
        Dictionary mapping file paths to validation results
    """
    results = {}
    
    if not os.path.exists(workflows_dir):
        return results
    
    for file_path in Path(workflows_dir).glob('*.yml'):
        results[str(file_path)] = validate_workflow_file(str(file_path))
    
    for file_path in Path(workflows_dir).glob('*.yaml'):
        results[str(file_path)] = validate_workflow_file(str(file_path))
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Validate specific file
        workflow_path = sys.argv[1]
        is_valid, errors, warnings = validate_workflow_file(workflow_path)
        
        print(f"Validating {workflow_path}...")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  ⚠️  {warning}")
        
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  ❌ {error}")
        
        if is_valid and not warnings:
            print("✅ Workflow is valid!")
        elif is_valid:
            print("✅ Workflow is valid with warnings")
        else:
            print("❌ Workflow has errors")
            sys.exit(1)
    else:
        # Validate all workflows
        results = validate_all_workflows()
        
        total_valid = 0
        total_files = len(results)
        
        for file_path, (is_valid, errors, warnings) in results.items():
            print(f"\nValidating {file_path}...")
            
            if warnings:
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
            
            if is_valid:
                total_valid += 1
                if not warnings:
                    print("  ✅ Valid")
                else:
                    print("  ✅ Valid with warnings")
            else:
                print("  ❌ Invalid")
        
        print(f"\nSummary: {total_valid}/{total_files} workflows valid")
        
        if total_valid < total_files:
            sys.exit(1)
