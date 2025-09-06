"""
Discovery Interview - Initial information gathering phase.

The DiscoveryInterview conducts an initial assessment of the target code,
gathering basic information about structure, dependencies, and context.
"""

import os
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path


class DiscoveryInterview:
    """Conducts initial interview phase of code discovery."""
    
    def __init__(self):
        """Initialize the discovery interview."""
        self.questions = self._load_questions()
        self.patterns = self._load_patterns()
    
    def conduct(self, target: Path, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Conduct interview for the target path.
        
        Args:
            target: Path to analyze
            options: Optional configuration options
            
        Returns:
            Interview data dictionary
        """
        interview_data = {
            'target_type': self._determine_target_type(target),
            'file_info': self._gather_file_info(target),
            'dependencies': self._find_dependencies(target),
            'structure': self._analyze_structure(target),
            'patterns': self._detect_patterns(target),
            'questions': self._answer_questions(target),
            'options': options or {}
        }
        
        return interview_data
    
    def _determine_target_type(self, target: Path) -> str:
        """Determine the type of target (file, directory, etc.)."""
        if target.is_file():
            return 'file'
        elif target.is_dir():
            return 'directory'
        else:
            return 'unknown'
    
    def _gather_file_info(self, target: Path) -> Dict[str, Any]:
        """Gather basic file information."""
        if target.is_file():
            stat = target.stat()
            return {
                'name': target.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': target.suffix,
                'language': self._detect_language(target)
            }
        elif target.is_dir():
            files = list(target.rglob('*'))
            return {
                'name': target.name,
                'file_count': len([f for f in files if f.is_file()]),
                'dir_count': len([f for f in files if f.is_dir()]),
                'total_size': sum(f.stat().st_size for f in files if f.is_file())
            }
        return {}
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext_to_lang = {
            '.py': 'python',
            '.ts': 'typescript',
            '.js': 'javascript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass'
        }
        return ext_to_lang.get(file_path.suffix.lower(), 'unknown')
    
    def _find_dependencies(self, target: Path) -> Dict[str, List[str]]:
        """Find dependencies for the target."""
        dependencies = {
            'imports': [],
            'requires': [],
            'packages': []
        }
        
        if target.is_file() and target.suffix == '.py':
            dependencies['imports'] = self._extract_python_imports(target)
        elif target.is_file() and target.suffix in ['.ts', '.js', '.tsx', '.jsx']:
            dependencies['imports'] = self._extract_js_imports(target)
        
        # Look for package files
        if target.is_dir():
            package_files = ['package.json', 'requirements.txt', 'pyproject.toml', 'setup.py']
            for pkg_file in package_files:
                pkg_path = target / pkg_file
                if pkg_path.exists():
                    dependencies['packages'].append(str(pkg_path))
        
        return dependencies
    
    def _extract_python_imports(self, file_path: Path) -> List[str]:
        """Extract Python import statements."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
        except (SyntaxError, UnicodeDecodeError):
            return []
    
    def _extract_js_imports(self, file_path: Path) -> List[str]:
        """Extract JavaScript/TypeScript import statements."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Simple regex to find import statements
            import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
            imports = re.findall(import_pattern, content)
            
            # Also find require statements
            require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)'
            requires = re.findall(require_pattern, content)
            
            return imports + requires
        except (UnicodeDecodeError, re.error):
            return []
    
    def _analyze_structure(self, target: Path) -> Dict[str, Any]:
        """Analyze the structure of the target."""
        if target.is_file():
            return self._analyze_file_structure(target)
        elif target.is_dir():
            return self._analyze_directory_structure(target)
        return {}
    
    def _analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze structure of a single file."""
        if file_path.suffix == '.py':
            return self._analyze_python_structure(file_path)
        elif file_path.suffix in ['.ts', '.js', '.tsx', '.jsx']:
            return self._analyze_js_structure(file_path)
        return {}
    
    def _analyze_python_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
            
            return {
                'classes': classes,
                'functions': functions,
                'lines': len(content.splitlines())
            }
        except (SyntaxError, UnicodeDecodeError):
            return {}
    
    def _analyze_js_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            
            # Simple pattern matching for JS/TS
            classes = []
            functions = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('class '):
                    classes.append({'name': line.split()[1].split('(')[0], 'line': i})
                elif line.startswith('function ') or 'function(' in line:
                    func_name = line.split('function')[1].split('(')[0].strip()
                    functions.append({'name': func_name, 'line': i})
                elif line.startswith('const ') and '=' in line and '=>' in line:
                    func_name = line.split('const')[1].split('=')[0].strip()
                    functions.append({'name': func_name, 'line': i})
            
            return {
                'classes': classes,
                'functions': functions,
                'lines': len(lines)
            }
        except UnicodeDecodeError:
            return {}
    
    def _analyze_directory_structure(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze directory structure."""
        files = []
        dirs = []
        
        for item in dir_path.iterdir():
            if item.is_file():
                files.append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'extension': item.suffix
                })
            elif item.is_dir():
                dirs.append({'name': item.name})
        
        return {
            'files': files,
            'directories': dirs,
            'total_files': len(files),
            'total_dirs': len(dirs)
        }
    
    def _detect_patterns(self, target: Path) -> List[str]:
        """Detect common patterns in the code."""
        patterns = []
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common patterns
                if 'class ' in content:
                    patterns.append('class-based')
                if 'function ' in content or 'def ' in content:
                    patterns.append('functional')
                if 'import ' in content or 'from ' in content:
                    patterns.append('modular')
                if 'test' in target.name.lower():
                    patterns.append('test-file')
                if 'config' in target.name.lower():
                    patterns.append('configuration')
                
            except UnicodeDecodeError:
                pass
        
        return patterns
    
    def _answer_questions(self, target: Path) -> Dict[str, Any]:
        """Answer discovery questions about the target."""
        answers = {}
        
        for question in self.questions:
            question_id = question.get('id')
            question_text = question.get('question')
            
            if question_id == 'purpose':
                answers[question_id] = self._determine_purpose(target)
            elif question_id == 'complexity':
                answers[question_id] = self._assess_complexity(target)
            elif question_id == 'dependencies':
                answers[question_id] = len(self._find_dependencies(target)['imports'])
            else:
                answers[question_id] = 'unknown'
        
        return answers
    
    def _determine_purpose(self, target: Path) -> str:
        """Determine the purpose of the target."""
        if target.is_file():
            name = target.name.lower()
            if 'test' in name:
                return 'testing'
            elif 'config' in name:
                return 'configuration'
            elif 'main' in name or 'index' in name:
                return 'entry-point'
            elif 'util' in name or 'helper' in name:
                return 'utility'
            else:
                return 'implementation'
        elif target.is_dir():
            return 'module'
        return 'unknown'
    
    def _assess_complexity(self, target: Path) -> str:
        """Assess the complexity of the target."""
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                line_count = len(lines)
                if line_count < 50:
                    return 'simple'
                elif line_count < 200:
                    return 'moderate'
                else:
                    return 'complex'
            except UnicodeDecodeError:
                return 'unknown'
        return 'unknown'
    
    def _load_questions(self) -> List[Dict[str, str]]:
        """Load discovery questions from configuration."""
        # Default questions - in real implementation, load from questions.yml
        return [
            {'id': 'purpose', 'question': 'What is the purpose of this code?'},
            {'id': 'complexity', 'question': 'How complex is this code?'},
            {'id': 'dependencies', 'question': 'How many dependencies does this have?'}
        ]
    
    def _load_patterns(self) -> List[Dict[str, str]]:
        """Load pattern definitions from configuration."""
        # Default patterns - in real implementation, load from patterns.yml
        return [
            {'id': 'class-based', 'pattern': 'class '},
            {'id': 'functional', 'pattern': 'function '},
            {'id': 'modular', 'pattern': 'import '}
        ]
