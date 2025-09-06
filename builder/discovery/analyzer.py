"""
Code Analyzer - Deep analysis phase of discovery.

The CodeAnalyzer performs detailed analysis of code structure, relationships,
and patterns to understand the codebase at a deeper level.
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path


class CodeAnalyzer:
    """Performs deep code analysis for discovery."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.analysis_cache = {}
    
    def analyze(self, target: Path, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep analysis of the target code.
        
        Args:
            target: Path to analyze
            interview_data: Data from interview phase
            
        Returns:
            Analysis results dictionary
        """
        analysis_data = {
            'relationships': self._analyze_relationships(target),
            'complexity_metrics': self._calculate_complexity_metrics(target),
            'code_patterns': self._identify_code_patterns(target),
            'architecture': self._analyze_architecture(target),
            'quality_indicators': self._assess_quality_indicators(target),
            'security_concerns': self._check_security_concerns(target),
            'performance_indicators': self._analyze_performance_indicators(target),
            'maintainability': self._assess_maintainability(target)
        }
        
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
