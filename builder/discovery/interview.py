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
    
    def __init__(self, question_set: str = "comprehensive"):
        """Initialize the discovery interview.
        
        Args:
            question_set: Question set to use (new_product, existing_product, comprehensive)
        """
        self.question_set = question_set
        self.questions = self._load_questions(question_set)
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
            question_type = question.get('type', 'text')
            
            if question_id == 'purpose':
                answers[question_id] = self._determine_purpose(target)
            elif question_id == 'complexity':
                answers[question_id] = self._assess_complexity(target)
            elif question_id == 'dependencies':
                answers[question_id] = len(self._find_dependencies(target)['imports'])
            elif question_id == 'product_vision':
                answers[question_id] = self._get_product_vision(target)
            elif question_id == 'target_users':
                answers[question_id] = self._get_target_users(target)
            elif question_id == 'main_idea':
                answers[question_id] = self._get_main_idea(target)
            elif question_id == 'key_features':
                answers[question_id] = self._get_key_features(target)
            elif question_id == 'use_cases':
                answers[question_id] = self._get_use_cases(target)
            elif question_id == 'current_features':
                answers[question_id] = self._get_current_features(target)
            elif question_id == 'hidden_functionality':
                answers[question_id] = self._get_hidden_functionality(target)
            elif question_id == 'external_integrations':
                answers[question_id] = self._get_external_integrations(target)
            elif question_id == 'data_sources':
                answers[question_id] = self._get_data_sources(target)
            elif question_id == 'planned_features':
                answers[question_id] = self._get_planned_features(target)
            elif question_id == 'major_refactoring':
                answers[question_id] = self._get_major_refactoring(target)
            elif question_id == 'refactoring_details':
                answers[question_id] = self._get_refactoring_details(target)
            elif question_id == 'timeline':
                answers[question_id] = self._get_timeline(target)
            elif question_id == 'priorities':
                answers[question_id] = self._get_priorities(target)
            elif question_id == 'coding_standards':
                answers[question_id] = self._get_coding_standards(target)
            elif question_id == 'development_practices':
                answers[question_id] = self._get_development_practices(target)
            elif question_id == 'tech_stack_preferences':
                answers[question_id] = self._get_tech_stack_preferences(target)
            elif question_id == 'team_size':
                answers[question_id] = self._get_team_size(target)
            elif question_id == 'team_experience':
                answers[question_id] = self._get_team_experience(target)
            elif question_id == 'project_initialized':
                answers[question_id] = self._get_project_initialized(target)
            elif question_id == 'project_stage':
                answers[question_id] = self._get_project_stage(target)
            elif question_id == 'deployment_status':
                answers[question_id] = self._get_deployment_status(target)
            else:
                # Default handling for unknown questions
                if question_type == 'categorical':
                    answers[question_id] = 'unknown'
                elif question_type == 'numerical':
                    answers[question_id] = 0
                else:
                    answers[question_id] = 'Not specified'
        
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
    
    # Enhanced question methods
    def _get_product_vision(self, target: Path) -> str:
        """Get product vision from discovery context or infer from code."""
        # This would typically come from discovery context
        return "Product vision not specified - needs manual input"
    
    def _get_target_users(self, target: Path) -> str:
        """Get target users from discovery context or infer from code."""
        return "Target users not specified - needs manual input"
    
    def _get_main_idea(self, target: Path) -> str:
        """Get main product idea from discovery context."""
        return "Main product idea not specified - needs manual input"
    
    def _get_key_features(self, target: Path) -> str:
        """Get key features from discovery context or infer from code."""
        return "Key features not specified - needs manual input"
    
    def _get_use_cases(self, target: Path) -> str:
        """Get use cases from discovery context."""
        return "Use cases not specified - needs manual input"
    
    def _get_current_features(self, target: Path) -> str:
        """Get current features that aren't obvious from code."""
        return "Current features not documented - needs manual input"
    
    def _get_hidden_functionality(self, target: Path) -> str:
        """Get hidden functionality not visible in codebase."""
        return "Hidden functionality not documented - needs manual input"
    
    def _get_external_integrations(self, target: Path) -> str:
        """Get external integrations from dependencies and code analysis."""
        deps = self._find_dependencies(target)
        integrations = []
        
        # Check for common integration patterns
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for API calls, database connections, etc.
                if 'http' in content.lower() or 'api' in content.lower():
                    integrations.append("HTTP/API integrations")
                if 'database' in content.lower() or 'db' in content.lower():
                    integrations.append("Database connections")
                if 'auth' in content.lower() or 'login' in content.lower():
                    integrations.append("Authentication services")
                    
            except UnicodeDecodeError:
                pass
        
        return ", ".join(integrations) if integrations else "No external integrations detected"
    
    def _get_data_sources(self, target: Path) -> str:
        """Get data sources from code analysis."""
        return "Data sources not documented - needs manual input"
    
    def _get_planned_features(self, target: Path) -> str:
        """Get planned features from discovery context."""
        return "Planned features not specified - needs manual input"
    
    def _get_major_refactoring(self, target: Path) -> str:
        """Check if major refactoring is planned."""
        return "unknown"
    
    def _get_refactoring_details(self, target: Path) -> str:
        """Get refactoring details if planned."""
        return "Refactoring details not specified - needs manual input"
    
    def _get_timeline(self, target: Path) -> str:
        """Get project timeline from discovery context."""
        return "unknown"
    
    def _get_priorities(self, target: Path) -> str:
        """Get current development priorities."""
        return "Development priorities not specified - needs manual input"
    
    def _get_coding_standards(self, target: Path) -> str:
        """Get coding standards from project files."""
        # Look for linting configs, style guides, etc.
        standards = []
        
        if target.is_dir():
            # Check for common config files
            config_files = [
                'eslint.config.js', '.eslintrc', 'tsconfig.json',
                'prettier.config.js', '.prettierrc', 'pyproject.toml',
                'setup.cfg', '.flake8', 'pylintrc'
            ]
            
            for config_file in config_files:
                if (target / config_file).exists():
                    standards.append(config_file)
        
        return ", ".join(standards) if standards else "Coding standards not explicitly configured"
    
    def _get_development_practices(self, target: Path) -> str:
        """Get development practices from project files."""
        practices = []
        
        if target.is_dir():
            # Check for CI/CD, testing, etc.
            if (target / '.github').exists():
                practices.append("GitHub Actions CI/CD")
            if (target / 'test').exists() or (target / 'tests').exists():
                practices.append("Unit testing")
            if (target / 'docs').exists():
                practices.append("Documentation")
            if (target / '.git').exists():
                practices.append("Version control")
        
        return ", ".join(practices) if practices else "Development practices not explicitly configured"
    
    def _get_tech_stack_preferences(self, target: Path) -> str:
        """Get tech stack preferences from project files."""
        stack = []
        
        if target.is_dir():
            # Check for package files
            if (target / 'package.json').exists():
                stack.append("Node.js/JavaScript")
            if (target / 'requirements.txt').exists() or (target / 'pyproject.toml').exists():
                stack.append("Python")
            if (target / 'Cargo.toml').exists():
                stack.append("Rust")
            if (target / 'go.mod').exists():
                stack.append("Go")
            if (target / 'pom.xml').exists():
                stack.append("Java")
        
        return ", ".join(stack) if stack else "Tech stack preferences not specified"
    
    def _get_team_size(self, target: Path) -> str:
        """Get team size from discovery context."""
        return "unknown"
    
    def _get_team_experience(self, target: Path) -> str:
        """Get team experience level."""
        return "unknown"
    
    def _get_project_initialized(self, target: Path) -> str:
        """Check if project is initialized."""
        if target.is_dir():
            # Check for common project files
            project_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml']
            if any((target / f).exists() for f in project_files):
                return "yes"
        return "unknown"
    
    def _get_project_stage(self, target: Path) -> str:
        """Get project stage from discovery context."""
        return "unknown"
    
    def _get_deployment_status(self, target: Path) -> str:
        """Get deployment status from discovery context."""
        return "unknown"
    
    def _load_questions(self, question_set: str = "comprehensive") -> List[Dict[str, str]]:
        """Load discovery questions from configuration."""
        try:
            import yaml
            questions_file = Path(__file__).parent / "questions.yml"
            if questions_file.exists():
                with open(questions_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check if specific question set is requested
                if question_set != "comprehensive" and "question_sets" in config:
                    question_sets = config.get("question_sets", {})
                    if question_set in question_sets:
                        set_config = question_sets[question_set]
                        if "file" in set_config:
                            # Load from external file
                            set_file = Path(__file__).parent.parent.parent / set_config["file"]
                            if set_file.exists():
                                with open(set_file, 'r') as f:
                                    set_data = yaml.safe_load(f)
                                return set_data.get('questions', [])
                
                # Return comprehensive questions as default
                return config.get('questions', [])
        except Exception as e:
            print(f"Warning: Could not load questions: {e}")
        
        # Fallback to default questions
        return [
            {'id': 'purpose', 'question': 'What is the purpose of this code?'},
            {'id': 'complexity', 'question': 'How complex is this code?'},
            {'id': 'dependencies', 'question': 'How many dependencies does this have?'},
            {'id': 'product_vision', 'question': 'What problem does this product solve?'},
            {'id': 'target_users', 'question': 'Who are the target users of this product?'},
            {'id': 'main_idea', 'question': 'What is the main idea for this product?'},
            {'id': 'key_features', 'question': 'What are the key features of this product?'},
            {'id': 'use_cases', 'question': 'What are the primary use cases for this product?'}
        ]
    
    def _load_patterns(self) -> List[Dict[str, str]]:
        """Load pattern definitions from configuration."""
        # Default patterns - in real implementation, load from patterns.yml
        return [
            {'id': 'class-based', 'pattern': 'class '},
            {'id': 'functional', 'pattern': 'function '},
            {'id': 'modular', 'pattern': 'import '}
        ]
