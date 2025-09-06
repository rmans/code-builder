#!/usr/bin/env python3
"""
YAML Python Validator - Ensures Python code in YAML files is properly formatted.

This module validates that Python code embedded in YAML files (especially
GitHub Actions workflows) is correctly formatted and won't cause syntax errors.
"""

import re
import yaml
import ast
from typing import Dict, List, Any, Tuple
from pathlib import Path


class YAMLPythonValidator:
    """Validates Python code embedded in YAML files."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_yaml_file(self, yaml_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate Python code in a YAML file.
        
        Args:
            yaml_path: Path to the YAML file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Could not read YAML file: {e}")
            return False, self.errors, self.warnings
        
        # Find all python3 -c commands
        python_commands = self._find_python_commands(content)
        
        for i, (line_num, python_code) in enumerate(python_commands):
            is_valid, cmd_errors, cmd_warnings = self._validate_python_code(python_code, line_num)
            
            if not is_valid:
                self.errors.extend(cmd_errors)
            else:
                self.warnings.extend(cmd_warnings)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _find_python_commands(self, content: str) -> List[Tuple[int, str]]:
        """Find all python3 -c commands in the content."""
        commands = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'python3 -c' in line:
                # Extract the Python code from the command
                python_code = self._extract_python_code(line, lines, i)
                if python_code:
                    commands.append((i, python_code))
        
        return commands
    
    def _extract_python_code(self, start_line: str, all_lines: List[str], start_line_num: int) -> str:
        """Extract Python code from a python3 -c command."""
        # Find the start of the Python code (after the opening quote)
        quote_start = start_line.find('"')
        
        if quote_start == -1:
            # Quote might be on the next line
            line_idx = start_line_num
            while line_idx < len(all_lines):
                line = all_lines[line_idx]
                quote_start = line.find('"')
                if quote_start != -1:
                    python_code = line[quote_start + 1:]
                    line_idx += 1  # Move to next line for multiline handling
                    break
                line_idx += 1
            else:
                return ""
        else:
            python_code = start_line[quote_start + 1:]
            line_idx = start_line_num  # Start from current line for multiline handling
        
        # If the command spans multiple lines, collect them
        while line_idx < len(all_lines):
            line = all_lines[line_idx]
            if line.strip().endswith('"'):
                # Found the end of the command
                python_code = python_code.rstrip('"')
                break
            else:
                # Continue to next line
                line_idx += 1
                if line_idx < len(all_lines):
                    python_code += '\n' + all_lines[line_idx]
        
        return python_code
    
    def _validate_python_code(self, python_code: str, line_num: int) -> Tuple[bool, List[str], List[str]]:
        """Validate a Python code string."""
        errors = []
        warnings = []
        
        # Check for indentation issues
        lines = python_code.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and line.startswith(' '):
                errors.append(f"Line {line_num + i}: Python code is indented - remove leading whitespace")
        
        # Check for common Python syntax issues
        try:
            ast.parse(python_code)
        except SyntaxError as e:
            errors.append(f"Line {line_num}: Python syntax error - {e.msg}")
        except Exception as e:
            errors.append(f"Line {line_num}: Python parsing error - {str(e)}")
        
        # Check for common issues
        if 'import' in python_code and any(line.strip().startswith('import') and line.startswith(' ') for line in lines):
            errors.append(f"Line {line_num}: Import statements should not be indented")
        
        if 'with open' in python_code and any(line.strip().startswith('with open') and line.startswith(' ') for line in lines):
            errors.append(f"Line {line_num}: With statements should not be indented")
        
        if 'print(' in python_code and any(line.strip().startswith('print(') and line.startswith(' ') for line in lines):
            errors.append(f"Line {line_num}: Print statements should not be indented")
        
        # Check for proper multiline string handling
        if python_code.count('"') % 2 != 0:
            warnings.append(f"Line {line_num}: Unmatched quotes in Python code - may cause YAML parsing issues")
        
        return len(errors) == 0, errors, warnings
    
    def find_python_in_yaml_files(self, directory: str) -> Dict[str, List[str]]:
        """
        Find Python code in YAML files and validate them.
        
        Args:
            directory: Directory to search for YAML files
            
        Returns:
            Dictionary mapping file paths to lists of issues
        """
        issues = {}
        
        for file_path in Path(directory).rglob('*.yml'):
            try:
                is_valid, errors, warnings = self.validate_yaml_file(str(file_path))
                
                file_issues = []
                if errors:
                    file_issues.extend([f"❌ {error}" for error in errors])
                if warnings:
                    file_issues.extend([f"⚠️  {warning}" for warning in warnings])
                
                if file_issues:
                    issues[str(file_path)] = file_issues
                    
            except Exception as e:
                issues[str(file_path)] = [f"❌ Error validating file: {e}"]
        
        return issues


def validate_yaml_python(yaml_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate Python code in a YAML file.
    
    Args:
        yaml_path: Path to the YAML file
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = YAMLPythonValidator()
    return validator.validate_yaml_file(yaml_path)


def find_python_in_yaml_files(directory: str) -> Dict[str, List[str]]:
    """
    Convenience function to find Python code issues in YAML files.
    
    Args:
        directory: Directory to search for YAML files
        
    Returns:
        Dictionary mapping file paths to lists of issues
    """
    validator = YAMLPythonValidator()
    return validator.find_python_in_yaml_files(directory)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--find-issues':
            # Find Python issues in YAML files
            directory = sys.argv[2] if len(sys.argv) > 2 else '.'
            issues = find_python_in_yaml_files(directory)
            
            if issues:
                print("Found Python code issues in YAML files:")
                for file_path, file_issues in issues.items():
                    print(f"\n{file_path}:")
                    for issue in file_issues:
                        print(f"  {issue}")
            else:
                print("No Python code issues found in YAML files")
        else:
            # Validate specific file
            file_path = sys.argv[1]
            is_valid, errors, warnings = validate_yaml_python(file_path)
            
            print(f"Validating Python code in YAML: {file_path}")
            
            if warnings:
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
            
            if is_valid:
                print("  ✅ Valid")
            else:
                print("  ❌ Invalid")
                sys.exit(1)
    else:
        print("Usage:")
        print("  python yaml_python_validator.py <yaml_file>")
        print("  python yaml_python_validator.py --find-issues [directory]")
