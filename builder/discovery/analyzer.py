"""
Code Analyzer - Deep analysis phase of discovery.

The CodeAnalyzer performs detailed analysis of code structure, relationships,
and patterns to understand the codebase at a deeper level.
"""

import ast
import re
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path


class CodeAnalyzer:
    """Performs deep code analysis for discovery."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.analysis_cache = {}
        self.metrics_history = []
        self.start_time = None
        self.end_time = None
    
    def analyze(self, target: Path, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep analysis of the target code.
        
        Args:
            target: Path to analyze
            interview_data: Data from interview phase
            
        Returns:
            Analysis results dictionary with metrics
        """
        # Start timing
        self.start_time = time.time()
        
        # Perform analysis with timing for each phase
        analysis_phases = {
            'detected': self._timed_analysis('detect_stack_and_structure', self._detect_stack_and_structure, target),
            'relationships': self._timed_analysis('analyze_relationships', self._analyze_relationships, target),
            'complexity_metrics': self._timed_analysis('calculate_complexity_metrics', self._calculate_complexity_metrics, target),
            'code_patterns': self._timed_analysis('identify_code_patterns', self._identify_code_patterns, target),
            'architecture': self._timed_analysis('analyze_architecture', self._analyze_architecture, target),
            'quality_indicators': self._timed_analysis('assess_quality_indicators', self._assess_quality_indicators, target),
            'security_concerns': self._timed_analysis('check_security_concerns', self._check_security_concerns, target),
            'performance_indicators': self._timed_analysis('analyze_performance_indicators', self._analyze_performance_indicators, target),
            'maintainability': self._timed_analysis('assess_maintainability', self._assess_maintainability, target)
        }
        
        # End timing
        self.end_time = time.time()
        
        # Calculate comprehensive metrics
        metrics = self._calculate_analysis_metrics(analysis_phases, interview_data)
        
        # Add metrics to analysis data
        analysis_data = analysis_phases.copy()
        analysis_data['metrics'] = metrics
        
        # Store metrics in history
        self._store_metrics_history(metrics)
        
        return analysis_data
    
    def _analyze_relationships(self, target: Path) -> Dict[str, Any]:
        """Analyze relationships between code elements."""
        relationships = {
            'imports': [],
            'exports': [],
            'calls': [],
            'inheritance': [],
            'composition': []
        }
        
        if target.is_file():
            if target.suffix == '.py':
                relationships.update(self._analyze_python_relationships(target))
            elif target.suffix in ['.ts', '.js', '.tsx', '.jsx']:
                relationships.update(self._analyze_js_relationships(target))
        
        return relationships
    
    def _analyze_python_relationships(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python-specific relationships."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = []
            exports = []
            calls = []
            inheritance = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ClassDef):
                    # Check for inheritance
                    if node.bases:
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                inheritance.append({
                                    'class': node.name,
                                    'parent': base.id,
                                    'line': node.lineno
                                })
                elif isinstance(node, ast.Call):
                    # Track function calls
                    if isinstance(node.func, ast.Name):
                        calls.append({
                            'function': node.func.id,
                            'line': node.lineno
                        })
            
            return {
                'imports': imports,
                'exports': exports,
                'calls': calls,
                'inheritance': inheritance
            }
        except (SyntaxError, UnicodeDecodeError):
            return {}
    
    def _analyze_js_relationships(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript-specific relationships."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            exports = []
            calls = []
            
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Import statements
                if line.startswith('import '):
                    import_match = re.match(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', line)
                    if import_match:
                        imports.append({
                            'module': import_match.group(1),
                            'line': i
                        })
                
                # Export statements
                elif line.startswith('export '):
                    exports.append({
                        'type': 'named' if 'export const' in line or 'export function' in line else 'default',
                        'line': i
                    })
                
                # Function calls (simple pattern matching)
                call_matches = re.findall(r'(\w+)\s*\(', line)
                for match in call_matches:
                    if match not in ['if', 'for', 'while', 'switch', 'catch']:
                        calls.append({
                            'function': match,
                            'line': i
                        })
            
            return {
                'imports': imports,
                'exports': exports,
                'calls': calls
            }
        except UnicodeDecodeError:
            return {}
    
    def _calculate_complexity_metrics(self, target: Path) -> Dict[str, Any]:
        """Calculate complexity metrics for the target."""
        if not target.is_file():
            return {}
        
        try:
            with open(target, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            
            metrics = {
                'lines_of_code': len(non_empty_lines),
                'total_lines': len(lines),
                'cyclomatic_complexity': self._calculate_cyclomatic_complexity(content),
                'nesting_depth': self._calculate_max_nesting_depth(content),
                'function_count': self._count_functions(content),
                'class_count': self._count_classes(content)
            }
            
            return metrics
        except UnicodeDecodeError:
            return {}
    
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity."""
        # Simple complexity calculation based on control flow statements
        complexity_keywords = [
            'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally',
            'and', 'or', 'case', 'default', '&&', '||', '?', ':', 'switch'
        ]
        
        complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            complexity += content.count(f' {keyword} ')
            complexity += content.count(f' {keyword}(')
            complexity += content.count(f' {keyword}\n')
        
        return complexity
    
    def _calculate_max_nesting_depth(self, content: str) -> int:
        """Calculate maximum nesting depth."""
        lines = content.splitlines()
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Count indentation
            indent = len(line) - len(line.lstrip())
            if indent > current_depth:
                current_depth = indent
                max_depth = max(max_depth, current_depth)
            elif indent < current_depth:
                current_depth = indent
        
        return max_depth // 4  # Assuming 4-space indentation
    
    def _count_functions(self, content: str) -> int:
        """Count function definitions."""
        function_patterns = [
            r'def\s+\w+\s*\(',  # Python
            r'function\s+\w+\s*\(',  # JavaScript
            r'const\s+\w+\s*=\s*\(',  # Arrow functions
            r'export\s+function\s+\w+\s*\('  # Exported functions
        ]
        
        count = 0
        for pattern in function_patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _count_classes(self, content: str) -> int:
        """Count class definitions."""
        class_patterns = [
            r'class\s+\w+',  # Python and JavaScript
            r'export\s+class\s+\w+'  # Exported classes
        ]
        
        count = 0
        for pattern in class_patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _identify_code_patterns(self, target: Path) -> List[Dict[str, Any]]:
        """Identify common code patterns."""
        patterns = []
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Design patterns
                if 'class ' in content and 'def __init__' in content:
                    patterns.append({'type': 'design_pattern', 'name': 'class_based', 'confidence': 0.8})
                
                if 'def ' in content and 'return ' in content:
                    patterns.append({'type': 'design_pattern', 'name': 'functional', 'confidence': 0.7})
                
                if 'import ' in content and 'from ' in content:
                    patterns.append({'type': 'design_pattern', 'name': 'modular', 'confidence': 0.9})
                
                # Anti-patterns
                if content.count('if ') > 10:
                    patterns.append({'type': 'anti_pattern', 'name': 'excessive_conditionals', 'confidence': 0.6})
                
                if 'eval(' in content:
                    patterns.append({'type': 'anti_pattern', 'name': 'eval_usage', 'confidence': 0.9})
                
                # Test patterns
                if 'test' in target.name.lower() or 'assert' in content:
                    patterns.append({'type': 'test_pattern', 'name': 'unit_test', 'confidence': 0.8})
                
            except UnicodeDecodeError:
                pass
        
        return patterns
    
    def _analyze_architecture(self, target: Path) -> Dict[str, Any]:
        """Analyze architectural patterns."""
        architecture = {
            'layers': [],
            'patterns': [],
            'coupling': 'unknown',
            'cohesion': 'unknown'
        }
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detect architectural layers
                if 'controller' in target.name.lower() or 'ctrl' in target.name.lower():
                    architecture['layers'].append('controller')
                
                if 'service' in target.name.lower() or 'business' in target.name.lower():
                    architecture['layers'].append('service')
                
                if 'model' in target.name.lower() or 'entity' in target.name.lower():
                    architecture['layers'].append('model')
                
                if 'view' in target.name.lower() or 'template' in target.name.lower():
                    architecture['layers'].append('view')
                
                # Detect architectural patterns
                if 'class ' in content and 'def __init__' in content:
                    architecture['patterns'].append('object_oriented')
                
                if 'async ' in content or 'await ' in content:
                    architecture['patterns'].append('asynchronous')
                
                if 'decorator' in content or '@' in content:
                    architecture['patterns'].append('decorator')
                
            except UnicodeDecodeError:
                pass
        
        return architecture
    
    def _assess_quality_indicators(self, target: Path) -> Dict[str, Any]:
        """Assess code quality indicators."""
        quality = {
            'readability': 'unknown',
            'documentation': 'unknown',
            'error_handling': 'unknown',
            'testing': 'unknown'
        }
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Documentation assessment
                doc_lines = len([line for line in content.splitlines() if line.strip().startswith('#')])
                total_lines = len([line for line in content.splitlines() if line.strip()])
                doc_ratio = doc_lines / total_lines if total_lines > 0 else 0
                
                if doc_ratio > 0.2:
                    quality['documentation'] = 'good'
                elif doc_ratio > 0.1:
                    quality['documentation'] = 'fair'
                else:
                    quality['documentation'] = 'poor'
                
                # Error handling assessment
                error_patterns = ['try:', 'except:', 'catch', 'throw', 'raise']
                error_count = sum(content.count(pattern) for pattern in error_patterns)
                
                if error_count > 0:
                    quality['error_handling'] = 'present'
                else:
                    quality['error_handling'] = 'missing'
                
                # Testing assessment
                if 'test' in target.name.lower() or 'assert' in content:
                    quality['testing'] = 'present'
                else:
                    quality['testing'] = 'unknown'
                
            except UnicodeDecodeError:
                pass
        
        return quality
    
    def _check_security_concerns(self, target: Path) -> List[Dict[str, Any]]:
        """Check for security concerns."""
        security_issues = []
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Common security issues
                if 'eval(' in content:
                    security_issues.append({
                        'type': 'dangerous_function',
                        'description': 'Use of eval() function',
                        'severity': 'high',
                        'line': content.find('eval(')
                    })
                
                if 'exec(' in content:
                    security_issues.append({
                        'type': 'dangerous_function',
                        'description': 'Use of exec() function',
                        'severity': 'high',
                        'line': content.find('exec(')
                    })
                
                if 'password' in content.lower() and '=' in content:
                    security_issues.append({
                        'type': 'hardcoded_credentials',
                        'description': 'Potential hardcoded password',
                        'severity': 'medium',
                        'line': content.lower().find('password')
                    })
                
            except UnicodeDecodeError:
                pass
        
        return security_issues
    
    def _analyze_performance_indicators(self, target: Path) -> Dict[str, Any]:
        """Analyze performance indicators."""
        performance = {
            'loops': 0,
            'recursion': False,
            'async_operations': False,
            'file_operations': False
        }
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count loops
                loop_patterns = ['for ', 'while ', 'for(', 'while(']
                performance['loops'] = sum(content.count(pattern) for pattern in loop_patterns)
                
                # Check for recursion
                if 'def ' in content and any(func in content for func in ['def ', 'function ']):
                    performance['recursion'] = True
                
                # Check for async operations
                if 'async ' in content or 'await ' in content:
                    performance['async_operations'] = True
                
                # Check for file operations
                file_ops = ['open(', 'read(', 'write(', 'file(']
                performance['file_operations'] = any(op in content for op in file_ops)
                
            except UnicodeDecodeError:
                pass
        
        return performance
    
    def _assess_maintainability(self, target: Path) -> Dict[str, Any]:
        """Assess code maintainability."""
        maintainability = {
            'score': 0,
            'factors': [],
            'recommendations': []
        }
        
        if target.is_file():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                score = 100
                factors = []
                recommendations = []
                
                # Length factor
                lines = len([line for line in content.splitlines() if line.strip()])
                if lines > 500:
                    score -= 20
                    factors.append('file_too_long')
                    recommendations.append('Consider breaking into smaller modules')
                elif lines > 200:
                    score -= 10
                    factors.append('file_long')
                
                # Complexity factor
                complexity = self._calculate_cyclomatic_complexity(content)
                if complexity > 20:
                    score -= 30
                    factors.append('high_complexity')
                    recommendations.append('Reduce cyclomatic complexity')
                elif complexity > 10:
                    score -= 15
                    factors.append('moderate_complexity')
                
                # Documentation factor
                doc_lines = len([line for line in content.splitlines() if line.strip().startswith('#')])
                doc_ratio = doc_lines / lines if lines > 0 else 0
                if doc_ratio < 0.1:
                    score -= 20
                    factors.append('poor_documentation')
                    recommendations.append('Add more documentation')
                
                maintainability['score'] = max(0, score)
                maintainability['factors'] = factors
                maintainability['recommendations'] = recommendations
                
            except UnicodeDecodeError:
                pass
        
        return maintainability
    
    def _detect_stack_and_structure(self, target: Path) -> Dict[str, Any]:
        """Detect programming languages, frameworks, dependencies, and project structure.
        
        Args:
            target: Path to analyze (file or directory)
            
        Returns:
            Dictionary containing detected technologies and structure
        """
        detected = {
            'languages': [],
            'frameworks': [],
            'dependencies': [],
            'project_structure': [],
            'test_runners': [],
            'ci_systems': [],
            'package_managers': [],
            'build_tools': []
        }
        
        if target.is_file():
            # Analyze single file
            detected.update(self._analyze_file_stack(target))
        else:
            # Analyze directory structure
            detected.update(self._analyze_directory_stack(target))
        
        return detected
    
    def _analyze_file_stack(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for technology stack."""
        detected = {
            'languages': [],
            'frameworks': [],
            'dependencies': [],
            'project_structure': [],
            'test_runners': [],
            'ci_systems': [],
            'package_managers': [],
            'build_tools': []
        }
        
        # Detect language by file extension
        if file_path.suffix in ['.js', '.jsx']:
            detected['languages'].append('JavaScript')
        elif file_path.suffix in ['.ts', '.tsx']:
            detected['languages'].append('TypeScript')
        elif file_path.suffix == '.py':
            detected['languages'].append('Python')
        elif file_path.suffix == '.go':
            detected['languages'].append('Go')
        elif file_path.suffix in ['.java', '.jar']:
            detected['languages'].append('Java')
        elif file_path.suffix in ['.rs', '.rlib']:
            detected['languages'].append('Rust')
        
        return detected
    
    def _analyze_directory_stack(self, target: Path) -> Dict[str, Any]:
        """Analyze directory for technology stack and project structure."""
        detected = {
            'languages': [],
            'frameworks': [],
            'dependencies': [],
            'project_structure': [],
            'test_runners': [],
            'ci_systems': [],
            'package_managers': [],
            'build_tools': []
        }
        
        # Detect languages and frameworks from config files
        detected.update(self._detect_from_config_files(target))
        
        # Detect project structure
        detected['project_structure'] = self._detect_project_structure(target)
        
        # Detect test runners
        detected['test_runners'] = self._detect_test_runners(target)
        
        # Detect CI systems
        detected['ci_systems'] = self._detect_ci_systems(target)
        
        # Detect package managers
        detected['package_managers'] = self._detect_package_managers(target)
        
        # Detect build tools
        detected['build_tools'] = self._detect_build_tools(target)
        
        return detected
    
    def _detect_from_config_files(self, target: Path) -> Dict[str, Any]:
        """Detect technologies from configuration files."""
        detected = {
            'languages': [],
            'frameworks': [],
            'dependencies': [],
            'package_managers': []
        }
        
        # Check for package.json (Node.js/JavaScript/TypeScript)
        package_json = target / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                detected['package_managers'].append('npm')
                if 'pnpm' in str(target / 'pnpm-lock.yaml'):
                    detected['package_managers'].append('pnpm')
                if 'yarn' in str(target / 'yarn.lock'):
                    detected['package_managers'].append('yarn')
                
                # Detect languages
                if 'typescript' in data.get('devDependencies', {}):
                    detected['languages'].append('TypeScript')
                else:
                    detected['languages'].append('JavaScript')
                
                # Detect frameworks
                dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'react' in dependencies:
                    detected['frameworks'].append('React')
                if 'vue' in dependencies:
                    detected['frameworks'].append('Vue.js')
                if 'angular' in dependencies:
                    detected['frameworks'].append('Angular')
                if 'express' in dependencies:
                    detected['frameworks'].append('Express.js')
                if 'next' in dependencies:
                    detected['frameworks'].append('Next.js')
                if 'nuxt' in dependencies:
                    detected['frameworks'].append('Nuxt.js')
                if 'svelte' in dependencies:
                    detected['frameworks'].append('Svelte')
                if 'fastapi' in dependencies:
                    detected['frameworks'].append('FastAPI')
                if 'django' in dependencies:
                    detected['frameworks'].append('Django')
                if 'flask' in dependencies:
                    detected['frameworks'].append('Flask')
                
                # Extract dependencies
                for dep, version in dependencies.items():
                    detected['dependencies'].append({
                        'name': dep,
                        'version': version,
                        'type': 'npm'
                    })
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for requirements.txt (Python)
        requirements_txt = target / 'requirements.txt'
        if requirements_txt.exists():
            detected['languages'].append('Python')
            detected['package_managers'].append('pip')
            
            try:
                with open(requirements_txt, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse package name and version
                            if '==' in line:
                                name, version = line.split('==', 1)
                            elif '>=' in line:
                                name, version = line.split('>=', 1)
                            else:
                                name, version = line, 'latest'
                            
                            detected['dependencies'].append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'type': 'pip'
                            })
            except FileNotFoundError:
                pass
        
        # Check for pyproject.toml (Python)
        pyproject_toml = target / 'pyproject.toml'
        if pyproject_toml.exists():
            detected['languages'].append('Python')
            detected['package_managers'].append('pip')
            
            try:
                import toml
                with open(pyproject_toml, 'r') as f:
                    data = toml.load(f)
                
                # Extract dependencies
                if 'project' in data and 'dependencies' in data['project']:
                    for dep in data['project']['dependencies']:
                        detected['dependencies'].append({
                            'name': dep,
                            'version': 'latest',
                            'type': 'pip'
                        })
            except (toml.TomlDecodeError, FileNotFoundError, ImportError):
                pass
        
        # Check for go.mod (Go)
        go_mod = target / 'go.mod'
        if go_mod.exists():
            detected['languages'].append('Go')
            detected['package_managers'].append('go mod')
            
            try:
                with open(go_mod, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('require '):
                            # Parse Go module requirements
                            parts = line.split()
                            if len(parts) >= 3:
                                detected['dependencies'].append({
                                    'name': parts[1],
                                    'version': parts[2],
                                    'type': 'go'
                                })
            except FileNotFoundError:
                pass
        
        # Check for Cargo.toml (Rust)
        cargo_toml = target / 'Cargo.toml'
        if cargo_toml.exists():
            detected['languages'].append('Rust')
            detected['package_managers'].append('cargo')
            
            try:
                import toml
                with open(cargo_toml, 'r') as f:
                    data = toml.load(f)
                
                # Extract dependencies
                if 'dependencies' in data:
                    for dep, version in data['dependencies'].items():
                        if isinstance(version, str):
                            detected['dependencies'].append({
                                'name': dep,
                                'version': version,
                                'type': 'cargo'
                            })
            except (toml.TomlDecodeError, FileNotFoundError, ImportError):
                pass
        
        # Check for pom.xml (Java)
        pom_xml = target / 'pom.xml'
        if pom_xml.exists():
            detected['languages'].append('Java')
            detected['package_managers'].append('maven')
            
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(pom_xml)
                root = tree.getroot()
                
                # Extract dependencies
                for dependency in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency'):
                    group_id = dependency.find('{http://maven.apache.org/POM/4.0.0}groupId')
                    artifact_id = dependency.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                    version = dependency.find('{http://maven.apache.org/POM/4.0.0}version')
                    
                    if group_id is not None and artifact_id is not None:
                        detected['dependencies'].append({
                            'name': f"{group_id.text}:{artifact_id.text}",
                            'version': version.text if version is not None else 'latest',
                            'type': 'maven'
                        })
            except (ET.ParseError, FileNotFoundError):
                pass
        
        return detected
    
    def _detect_project_structure(self, target: Path) -> List[str]:
        """Detect project structure patterns."""
        structure = []
        
        # Common directory patterns
        common_dirs = [
            'src', 'app', 'apps', 'lib', 'libs', 'packages', 'components',
            'pages', 'views', 'templates', 'static', 'public', 'assets',
            'config', 'configs', 'settings', 'utils', 'helpers', 'services',
            'models', 'entities', 'controllers', 'routes', 'middleware',
            'tests', 'test', 'specs', 'docs', 'documentation'
        ]
        
        for item in target.iterdir():
            if item.is_dir() and item.name in common_dirs:
                structure.append(item.name)
        
        # Detect specific patterns
        if (target / 'src').exists():
            structure.append('src_based')
        if (target / 'app').exists():
            structure.append('app_based')
        if (target / 'packages').exists():
            structure.append('monorepo')
        if (target / 'lib').exists():
            structure.append('library')
        
        return structure
    
    def _detect_test_runners(self, target: Path) -> List[str]:
        """Detect test runners and testing frameworks."""
        test_runners = []
        
        # Check package.json for test runners
        package_json = target / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'jest' in dependencies:
                    test_runners.append('Jest')
                if 'vitest' in dependencies:
                    test_runners.append('Vitest')
                if 'mocha' in dependencies:
                    test_runners.append('Mocha')
                if 'jasmine' in dependencies:
                    test_runners.append('Jasmine')
                if 'cypress' in dependencies:
                    test_runners.append('Cypress')
                if 'playwright' in dependencies:
                    test_runners.append('Playwright')
                if 'puppeteer' in dependencies:
                    test_runners.append('Puppeteer')
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for Python test runners
        requirements_txt = target / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    content = f.read()
                
                if 'pytest' in content:
                    test_runners.append('pytest')
                if 'unittest' in content:
                    test_runners.append('unittest')
                if 'nose' in content:
                    test_runners.append('nose')
                if 'tox' in content:
                    test_runners.append('tox')
                    
            except FileNotFoundError:
                pass
        
        # Check for test configuration files
        test_configs = [
            'jest.config.js', 'jest.config.ts', 'vitest.config.js', 'vitest.config.ts',
            'pytest.ini', 'setup.cfg', 'tox.ini', 'cypress.config.js', 'playwright.config.js'
        ]
        
        for config in test_configs:
            if (target / config).exists():
                if 'jest' in config:
                    test_runners.append('Jest')
                elif 'vitest' in config:
                    test_runners.append('Vitest')
                elif 'pytest' in config:
                    test_runners.append('pytest')
                elif 'cypress' in config:
                    test_runners.append('Cypress')
                elif 'playwright' in config:
                    test_runners.append('Playwright')
        
        return list(set(test_runners))  # Remove duplicates
    
    def _detect_ci_systems(self, target: Path) -> List[str]:
        """Detect CI/CD systems."""
        ci_systems = []
        
        # Check for GitHub Actions
        if (target / '.github' / 'workflows').exists():
            ci_systems.append('GitHub Actions')
        
        # Check for GitLab CI
        if (target / '.gitlab-ci.yml').exists():
            ci_systems.append('GitLab CI')
        
        # Check for Jenkins
        if (target / 'Jenkinsfile').exists():
            ci_systems.append('Jenkins')
        
        # Check for CircleCI
        if (target / '.circleci').exists():
            ci_systems.append('CircleCI')
        
        # Check for Travis CI
        if (target / '.travis.yml').exists():
            ci_systems.append('Travis CI')
        
        # Check for Azure DevOps
        if (target / 'azure-pipelines.yml').exists():
            ci_systems.append('Azure DevOps')
        
        return ci_systems
    
    def _detect_package_managers(self, target: Path) -> List[str]:
        """Detect package managers."""
        package_managers = []
        
        # Check for lock files and config files
        if (target / 'package.json').exists():
            package_managers.append('npm')
        if (target / 'pnpm-lock.yaml').exists():
            package_managers.append('pnpm')
        if (target / 'yarn.lock').exists():
            package_managers.append('yarn')
        if (target / 'requirements.txt').exists():
            package_managers.append('pip')
        if (target / 'pyproject.toml').exists():
            package_managers.append('pip')
        if (target / 'go.mod').exists():
            package_managers.append('go mod')
        if (target / 'Cargo.toml').exists():
            package_managers.append('cargo')
        if (target / 'pom.xml').exists():
            package_managers.append('maven')
        if (target / 'gradle').exists() or (target / 'build.gradle').exists():
            package_managers.append('gradle')
        
        return list(set(package_managers))  # Remove duplicates
    
    def _detect_build_tools(self, target: Path) -> List[str]:
        """Detect build tools and bundlers."""
        build_tools = []
        
        # Check package.json for build tools
        package_json = target / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if 'webpack' in dependencies:
                    build_tools.append('Webpack')
                if 'vite' in dependencies:
                    build_tools.append('Vite')
                if 'rollup' in dependencies:
                    build_tools.append('Rollup')
                if 'esbuild' in dependencies:
                    build_tools.append('esbuild')
                if 'parcel' in dependencies:
                    build_tools.append('Parcel')
                if 'babel' in dependencies:
                    build_tools.append('Babel')
                if 'typescript' in dependencies:
                    build_tools.append('TypeScript Compiler')
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for build configuration files
        build_configs = [
            'webpack.config.js', 'webpack.config.ts', 'vite.config.js', 'vite.config.ts',
            'rollup.config.js', 'rollup.config.ts', 'babel.config.js', 'babel.config.json',
            'tsconfig.json', 'tsconfig.build.json', 'build.gradle', 'Makefile'
        ]
        
        for config in build_configs:
            if (target / config).exists():
                if 'webpack' in config:
                    build_tools.append('Webpack')
                elif 'vite' in config:
                    build_tools.append('Vite')
                elif 'rollup' in config:
                    build_tools.append('Rollup')
                elif 'babel' in config:
                    build_tools.append('Babel')
                elif 'tsconfig' in config:
                    build_tools.append('TypeScript Compiler')
                elif 'gradle' in config:
                    build_tools.append('Gradle')
                elif 'Makefile' in config:
                    build_tools.append('Make')
        
        return list(set(build_tools))  # Remove duplicates
    
    def _timed_analysis(self, phase_name: str, analysis_func, *args, **kwargs) -> Dict[str, Any]:
        """Run analysis function with timing.
        
        Args:
            phase_name: Name of the analysis phase
            analysis_func: Analysis function to run
            *args: Arguments for the analysis function
            **kwargs: Keyword arguments for the analysis function
            
        Returns:
            Analysis results with timing information
        """
        start_time = time.time()
        try:
            result = analysis_func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Add timing to result if it's a dictionary
            if isinstance(result, dict):
                result['_timing'] = {
                    'phase': phase_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'elapsed_seconds': elapsed_time
                }
            
            return result
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            return {
                'error': str(e),
                '_timing': {
                    'phase': phase_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'elapsed_seconds': elapsed_time,
                    'error': True
                }
            }
    
    def _calculate_analysis_metrics(self, analysis_phases: Dict[str, Any], interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive analysis metrics.
        
        Args:
            analysis_phases: Results from each analysis phase
            interview_data: Data from interview phase
            
        Returns:
            Comprehensive metrics dictionary
        """
        total_elapsed = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Count features from interview data
        features_count = 0
        if 'synthesis' in interview_data and 'features' in interview_data['synthesis']:
            features_count = len(interview_data['synthesis']['features'])
        elif 'key_features' in interview_data:
            features_count = len(interview_data['key_features'])
        
        # Count gaps from analysis
        gaps_count = 0
        gaps_list = []
        if 'detected' in analysis_phases and 'gaps' in analysis_phases['detected']:
            gaps_count = len(analysis_phases['detected']['gaps'])
            gaps_list = analysis_phases['detected']['gaps']
        
        # Count detection results
        detection_results = {
            'total_detections': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'detection_types': {}
        }
        
        for phase_name, phase_result in analysis_phases.items():
            if isinstance(phase_result, dict):
                if 'error' in phase_result:
                    detection_results['failed_detections'] += 1
                else:
                    detection_results['successful_detections'] += 1
                
                # Count specific detection types
                if 'technologies' in phase_result:
                    detection_results['detection_types']['technologies'] = len(phase_result['technologies'])
                if 'frameworks' in phase_result:
                    detection_results['detection_types']['frameworks'] = len(phase_result['frameworks'])
                if 'libraries' in phase_result:
                    detection_results['detection_types']['libraries'] = len(phase_result['libraries'])
                if 'tools' in phase_result:
                    detection_results['detection_types']['tools'] = len(phase_result['tools'])
        
        detection_results['total_detections'] = detection_results['successful_detections'] + detection_results['failed_detections']
        
        # Calculate phase timings
        phase_timings = {}
        for phase_name, phase_result in analysis_phases.items():
            if isinstance(phase_result, dict) and '_timing' in phase_result:
                timing = phase_result['_timing']
                phase_timings[phase_name] = {
                    'elapsed_seconds': timing['elapsed_seconds'],
                    'start_time': timing['start_time'],
                    'end_time': timing['end_time'],
                    'error': timing.get('error', False)
                }
        
        # Calculate quality metrics
        quality_metrics = {
            'overall_score': 0,
            'maintainability_score': 0,
            'complexity_score': 0,
            'test_coverage': 0,
            'documentation_score': 0
        }
        
        if 'quality_indicators' in analysis_phases:
            quality_data = analysis_phases['quality_indicators']
            quality_metrics.update({
                'overall_score': quality_data.get('overall_score', 0),
                'maintainability_score': quality_data.get('maintainability_score', 0),
                'complexity_score': quality_data.get('complexity_score', 0),
                'test_coverage': quality_data.get('test_coverage', 0),
                'documentation_score': quality_data.get('documentation_score', 0)
            })
        
        # Calculate complexity metrics
        complexity_metrics = {
            'cyclomatic_complexity': 0,
            'lines_of_code': 0,
            'functions_count': 0,
            'classes_count': 0,
            'imports_count': 0
        }
        
        if 'complexity_metrics' in analysis_phases:
            complexity_data = analysis_phases['complexity_metrics']
            complexity_metrics.update({
                'cyclomatic_complexity': complexity_data.get('cyclomatic_complexity', 0),
                'lines_of_code': complexity_data.get('lines_of_code', 0),
                'functions_count': complexity_data.get('functions_count', 0),
                'classes_count': complexity_data.get('classes_count', 0),
                'imports_count': complexity_data.get('imports_count', 0)
            })
        
        # Calculate security metrics
        security_metrics = {
            'security_issues_count': 0,
            'vulnerabilities_count': 0,
            'security_score': 0
        }
        
        if 'security_concerns' in analysis_phases:
            security_data = analysis_phases['security_concerns']
            if isinstance(security_data, dict):
                security_metrics.update({
                    'security_issues_count': len(security_data.get('issues', [])),
                    'vulnerabilities_count': len(security_data.get('vulnerabilities', [])),
                    'security_score': security_data.get('security_score', 0)
                })
            elif isinstance(security_data, list):
                security_metrics.update({
                    'security_issues_count': len(security_data),
                    'vulnerabilities_count': 0,
                    'security_score': 0
                })
        
        # Create comprehensive metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'analysis_id': f"analysis_{int(time.time())}",
            'total_elapsed_seconds': total_elapsed,
            'features': {
                'count': features_count,
                'list': interview_data.get('key_features', []) if 'key_features' in interview_data else []
            },
            'gaps': {
                'count': gaps_count,
                'list': gaps_list
            },
            'detection_results': detection_results,
            'phase_timings': phase_timings,
            'quality_metrics': quality_metrics,
            'complexity_metrics': complexity_metrics,
            'security_metrics': security_metrics,
            'performance_metrics': {
                'analysis_speed': total_elapsed,
                'phases_completed': len([p for p in phase_timings.values() if not p.get('error', False)]),
                'phases_failed': len([p for p in phase_timings.values() if p.get('error', False)]),
                'average_phase_time': sum(p['elapsed_seconds'] for p in phase_timings.values()) / len(phase_timings) if phase_timings else 0
            },
            'summary': {
                'total_phases': len(analysis_phases),
                'successful_phases': detection_results['successful_detections'],
                'failed_phases': detection_results['failed_detections'],
                'success_rate': detection_results['successful_detections'] / detection_results['total_detections'] if detection_results['total_detections'] > 0 else 0,
                'features_discovered': features_count,
                'gaps_identified': gaps_count,
                'overall_quality_score': quality_metrics['overall_score']
            }
        }
        
        return metrics
    
    def _store_metrics_history(self, metrics: Dict[str, Any]) -> None:
        """Store metrics in history for tracking over time.
        
        Args:
            metrics: Metrics dictionary to store
        """
        # Add to in-memory history
        self.metrics_history.append(metrics.copy())
        
        # Keep only last 100 entries to prevent memory issues
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Write to discovery_report.json
        self._write_discovery_report(metrics)
    
    def _write_discovery_report(self, metrics: Dict[str, Any]) -> None:
        """Write discovery report with metrics to JSON file.
        
        Args:
            metrics: Metrics to write
        """
        report_data = {
            'report_metadata': {
                'generated_at': metrics['timestamp'],
                'analysis_id': metrics['analysis_id'],
                'version': '1.0.0',
                'generator': 'CodeAnalyzer'
            },
            'metrics': metrics,
            'historical_metrics': self.metrics_history[-10:],  # Last 10 analyses
            'trends': self._calculate_trends()
        }
        
        # Ensure cache directory exists
        cache_dir = Path('builder/cache')
        cache_dir.mkdir(exist_ok=True)
        
        # Write to discovery_report.json
        report_path = cache_dir / 'discovery_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from historical metrics.
        
        Returns:
            Trends dictionary
        """
        if len(self.metrics_history) < 2:
            return {'insufficient_data': True}
        
        trends = {
            'features_trend': self._calculate_trend('features.count'),
            'gaps_trend': self._calculate_trend('gaps.count'),
            'quality_trend': self._calculate_trend('quality_metrics.overall_score'),
            'complexity_trend': self._calculate_trend('complexity_metrics.cyclomatic_complexity'),
            'performance_trend': self._calculate_trend('total_elapsed_seconds'),
            'success_rate_trend': self._calculate_trend('summary.success_rate')
        }
        
        return trends
    
    def _calculate_trend(self, metric_path: str) -> Dict[str, Any]:
        """Calculate trend for a specific metric.
        
        Args:
            metric_path: Dot-separated path to metric (e.g., 'features.count')
            
        Returns:
            Trend information
        """
        values = []
        for metrics in self.metrics_history:
            try:
                value = metrics
                for key in metric_path.split('.'):
                    value = value[key]
                values.append(float(value))
            except (KeyError, TypeError, ValueError):
                continue
        
        if len(values) < 2:
            return {'trend': 'insufficient_data', 'values': values}
        
        # Calculate simple linear trend
        n = len(values)
        x = list(range(n))
        y = values
        
        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine trend direction
        if slope > 0.1:
            trend_direction = 'increasing'
        elif slope < -0.1:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        return {
            'trend': trend_direction,
            'slope': slope,
            'values': values,
            'first_value': values[0],
            'last_value': values[-1],
            'change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics.
        
        Returns:
            Metrics summary dictionary
        """
        if not self.metrics_history:
            return {'message': 'No metrics available'}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            'latest_analysis': latest_metrics,
            'total_analyses': len(self.metrics_history),
            'trends': self._calculate_trends(),
            'performance_summary': {
                'average_analysis_time': sum(m['total_elapsed_seconds'] for m in self.metrics_history) / len(self.metrics_history),
                'fastest_analysis': min(m['total_elapsed_seconds'] for m in self.metrics_history),
                'slowest_analysis': max(m['total_elapsed_seconds'] for m in self.metrics_history)
            }
        }
