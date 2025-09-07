#!/usr/bin/env python3
"""
Enhanced Discovery Engine - T1.2 Implementation

This module provides enhanced discovery capabilities with language/framework detection,
depth control, ignore patterns, and structured outputs for report.json and summary.md.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

# Import overlay paths for consistent path resolution
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
except ImportError:
    overlay_paths = None


class EnhancedDiscoveryEngine:
    """Enhanced discovery engine with comprehensive project analysis."""
    
    def __init__(self, root_path: str = ".", cache_dir: Optional[str] = None):
        """Initialize the enhanced discovery engine.
        
        Args:
            root_path: Root directory of the project to analyze
            cache_dir: Optional cache directory (uses overlay paths if available)
        """
        self.root_path = Path(root_path).resolve()
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif overlay_paths:
            self.cache_dir = Path(overlay_paths.get_cache_dir()) / "discovery"
        else:
            self.cache_dir = self.root_path / "builder" / "cache" / "discovery"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up output directory
        if overlay_paths:
            self.output_dir = Path(overlay_paths.get_docs_dir()) / "discovery"
        else:
            self.output_dir = self.root_path / "cb_docs" / "discovery"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis results
        self.analysis_results = {}
        self.start_time = None
        self.end_time = None
    
    def analyze_project(self, 
                       depth: int = 3, 
                       ignore_patterns: Optional[List[str]] = None, 
                       ci_mode: bool = False) -> Dict[str, Any]:
        """Analyze project structure and generate discovery report.
        
        Args:
            depth: Analysis depth (1-5, where 5 is deepest)
            ignore_patterns: List of patterns to ignore
            ci_mode: Non-interactive mode for CI/CD
            
        Returns:
            Dictionary containing analysis results
        """
        self.start_time = time.time()
        ignore_patterns = ignore_patterns or []
        
        print(f"🔍 Analyzing project structure (depth: {depth})...")
        
        # Initialize analysis results
        self.analysis_results = {
            "project_info": self._analyze_project_info(),
            "languages": self._detect_languages(depth, ignore_patterns),
            "frameworks": self._detect_frameworks(depth, ignore_patterns),
            "package_managers": self._detect_package_managers(depth, ignore_patterns),
            "test_runners": self._detect_test_runners(depth, ignore_patterns),
            "lint_formatters": self._detect_lint_formatters(depth, ignore_patterns),
            "monorepo_hints": self._detect_monorepo_hints(depth, ignore_patterns),
            "structure": self._analyze_structure(depth, ignore_patterns),
            "dependencies": self._analyze_dependencies(depth, ignore_patterns),
            "configuration": self._analyze_configuration(depth, ignore_patterns),
            "metadata": {
                "analysis_depth": depth,
                "ignore_patterns": ignore_patterns,
                "ci_mode": ci_mode,
                "timestamp": datetime.now().isoformat(),
                "analysis_duration": 0
            }
        }
        
        # Calculate analysis duration
        self.end_time = time.time()
        self.analysis_results["metadata"]["analysis_duration"] = self.end_time - self.start_time
        
        # Generate outputs
        self._generate_report_json()
        self._generate_summary_md()
        
        # Update project state
        self._update_project_state()
        
        return self.analysis_results
    
    def _analyze_project_info(self) -> Dict[str, Any]:
        """Analyze basic project information."""
        return {
            "name": self.root_path.name,
            "path": str(self.root_path),
            "type": self._determine_project_type(),
            "size_bytes": self._calculate_project_size(),
            "file_count": self._count_files(),
            "directory_count": self._count_directories()
        }
    
    def _detect_languages(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect programming languages used in the project."""
        languages = {}
        file_extensions = {}
        
        for file_path in self._walk_files(depth, ignore_patterns):
            ext = file_path.suffix.lower()
            if ext:
                file_extensions[ext] = file_extensions.get(ext, 0) + 1
                
                # Map extensions to languages
                lang = self._extension_to_language(ext)
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "detected": list(languages.keys()),
            "file_counts": languages,
            "extensions": file_extensions,
            "primary": max(languages.items(), key=lambda x: x[1])[0] if languages else None
        }
    
    def _detect_frameworks(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect frameworks and libraries used."""
        frameworks = set()
        framework_files = {}
        
        # Check for framework-specific files
        framework_indicators = {
            "react": ["package.json", "src/App.js", "src/App.jsx", "src/App.tsx"],
            "vue": ["package.json", "src/App.vue", "vue.config.js"],
            "angular": ["package.json", "angular.json", "src/app/app.module.ts"],
            "django": ["manage.py", "settings.py", "requirements.txt"],
            "flask": ["app.py", "requirements.txt", "flask_app.py"],
            "express": ["package.json", "app.js", "server.js", "index.js"],
            "next": ["package.json", "next.config.js", "pages/"],
            "nuxt": ["package.json", "nuxt.config.js", "pages/"],
            "svelte": ["package.json", "svelte.config.js", "src/App.svelte"],
            "fastapi": ["main.py", "requirements.txt", "app/main.py"],
            "rails": ["Gemfile", "config/application.rb", "app/controllers/"],
            "spring": ["pom.xml", "build.gradle", "src/main/java/"],
            "laravel": ["composer.json", "artisan", "app/Http/Controllers/"],
            "symfony": ["composer.json", "bin/console", "src/Controller/"]
        }
        
        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                if (self.root_path / indicator).exists():
                    frameworks.add(framework)
                    framework_files[framework] = indicator
                    break
        
        # Check package.json for framework dependencies
        package_json = self.root_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    for dep in deps.keys():
                        if "react" in dep.lower():
                            frameworks.add("react")
                        elif "vue" in dep.lower():
                            frameworks.add("vue")
                        elif "angular" in dep.lower():
                            frameworks.add("angular")
                        elif "express" in dep.lower():
                            frameworks.add("express")
                        elif "next" in dep.lower():
                            frameworks.add("next")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "detected": list(frameworks),
            "indicators": framework_files,
            "confidence": self._calculate_framework_confidence(frameworks)
        }
    
    def _detect_package_managers(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect package managers used."""
        package_managers = set()
        manager_files = {}
        
        # Check for package manager files
        manager_indicators = {
            "npm": ["package.json", "package-lock.json"],
            "yarn": ["package.json", "yarn.lock"],
            "pnpm": ["package.json", "pnpm-lock.yaml"],
            "pip": ["requirements.txt", "setup.py", "pyproject.toml"],
            "poetry": ["pyproject.toml", "poetry.lock"],
            "pipenv": ["Pipfile", "Pipfile.lock"],
            "cargo": ["Cargo.toml", "Cargo.lock"],
            "composer": ["composer.json", "composer.lock"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "gem": ["Gemfile", "Gemfile.lock"],
            "go": ["go.mod", "go.sum"],
            "nuget": ["packages.config", "*.csproj"],
            "conan": ["conanfile.txt", "conanfile.py"]
        }
        
        for manager, indicators in manager_indicators.items():
            for indicator in indicators:
                if (self.root_path / indicator).exists():
                    package_managers.add(manager)
                    manager_files[manager] = indicator
                    break
        
        return {
            "detected": list(package_managers),
            "files": manager_files,
            "primary": self._determine_primary_package_manager(package_managers)
        }
    
    def _detect_test_runners(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect test runners and testing frameworks."""
        test_runners = set()
        test_files = {}
        
        # Check for test configuration files
        test_configs = {
            "jest": ["jest.config.js", "jest.config.ts", "jest.config.json"],
            "vitest": ["vitest.config.js", "vitest.config.ts"],
            "mocha": ["mocha.opts", ".mocharc.js", ".mocharc.json"],
            "jasmine": ["jasmine.json", "spec/support/jasmine.json"],
            "karma": ["karma.conf.js", "karma.conf.ts"],
            "cypress": ["cypress.json", "cypress.config.js"],
            "playwright": ["playwright.config.js", "playwright.config.ts"],
            "pytest": ["pytest.ini", "pyproject.toml", "tox.ini"],
            "unittest": ["test_*.py", "*_test.py"],
            "nose": ["nosetests.cfg", "setup.cfg"],
            "rspec": ["spec/", "Rakefile"],
            "minitest": ["test/", "test_helper.rb"],
            "junit": ["pom.xml", "build.gradle"],
            "testng": ["testng.xml", "pom.xml"],
            "cargo-test": ["Cargo.toml"],
            "go-test": ["*_test.go", "go.mod"]
        }
        
        for runner, configs in test_configs.items():
            for config in configs:
                if (self.root_path / config).exists():
                    test_runners.add(runner)
                    test_files[runner] = config
                    break
        
        # Count test files
        test_file_count = 0
        for file_path in self._walk_files(depth, ignore_patterns):
            if any(pattern in file_path.name.lower() for pattern in ["test", "spec", "_test", "_spec"]):
                test_file_count += 1
        
        return {
            "detected": list(test_runners),
            "config_files": test_files,
            "test_file_count": test_file_count,
            "coverage_indicators": self._detect_coverage_tools()
        }
    
    def _detect_lint_formatters(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect linting and formatting tools."""
        tools = set()
        config_files = {}
        
        # Check for linting/formatting config files
        tool_configs = {
            "eslint": [".eslintrc.js", ".eslintrc.json", ".eslintrc.yml", "eslint.config.js"],
            "prettier": [".prettierrc", ".prettierrc.js", ".prettierrc.json", "prettier.config.js"],
            "stylelint": [".stylelintrc", ".stylelintrc.js", ".stylelintrc.json"],
            "tslint": ["tslint.json"],
            "jshint": [".jshintrc", ".jshintrc.json"],
            "pylint": [".pylintrc", "pylint.ini", "setup.cfg"],
            "flake8": [".flake8", "setup.cfg", "tox.ini"],
            "black": ["pyproject.toml", "setup.cfg"],
            "isort": [".isort.cfg", "pyproject.toml", "setup.cfg"],
            "mypy": ["mypy.ini", "pyproject.toml"],
            "rubocop": [".rubocop.yml", ".rubocop.yaml"],
            "rustfmt": ["rustfmt.toml"],
            "gofmt": ["go.mod"],
            "clang-format": [".clang-format"],
            "prettier": [".prettierrc", ".prettierrc.js", ".prettierrc.json"]
        }
        
        for tool, configs in tool_configs.items():
            for config in configs:
                if (self.root_path / config).exists():
                    tools.add(tool)
                    config_files[tool] = config
                    break
        
        return {
            "detected": list(tools),
            "config_files": config_files,
            "categories": self._categorize_lint_tools(tools)
        }
    
    def _detect_monorepo_hints(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Detect monorepo patterns and tools."""
        hints = set()
        indicators = {}
        
        # Check for monorepo tools
        monorepo_tools = {
            "lerna": ["lerna.json", "package.json"],
            "nx": ["nx.json", "workspace.json"],
            "rush": ["rush.json"],
            "yarn-workspaces": ["package.json"],
            "pnpm-workspaces": ["pnpm-workspace.yaml"],
            "bazel": ["WORKSPACE", "BUILD"],
            "buck": [".buckconfig", "BUCK"],
            "gradle-multiproject": ["settings.gradle", "settings.gradle.kts"]
        }
        
        for tool, configs in monorepo_tools.items():
            for config in configs:
                if (self.root_path / config).exists():
                    hints.add(tool)
                    indicators[tool] = config
                    break
        
        # Check for multiple package.json files (workspace indicator)
        package_json_count = len(list(self.root_path.rglob("package.json")))
        if package_json_count > 1:
            hints.add("multiple-package-json")
            indicators["multiple-package-json"] = package_json_count
        
        return {
            "detected": list(hints),
            "indicators": indicators,
            "workspace_count": package_json_count,
            "is_monorepo": len(hints) > 0 or package_json_count > 1
        }
    
    def _analyze_structure(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Analyze project structure and organization."""
        structure = {
            "directories": {},
            "files": {},
            "depth": depth,
            "organization_pattern": self._detect_organization_pattern()
        }
        
        # Analyze directory structure
        for root, dirs, files in os.walk(self.root_path):
            if depth > 0 and root.count(os.sep) - self.root_path.as_posix().count(os.sep) >= depth:
                continue
            
            rel_path = Path(root).relative_to(self.root_path)
            if rel_path == Path("."):
                continue
            
            # Skip ignored directories
            if any(pattern in str(rel_path) for pattern in ignore_patterns):
                continue
            
            structure["directories"][str(rel_path)] = {
                "file_count": len(files),
                "subdir_count": len(dirs),
                "size_bytes": sum((Path(root) / f).stat().st_size for f in files if (Path(root) / f).exists())
            }
        
        return structure
    
    def _analyze_dependencies(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            "external": {},
            "internal": {},
            "dev_dependencies": {},
            "total_count": 0
        }
        
        # Analyze package.json if it exists
        package_json = self.root_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    
                    dependencies["external"] = deps
                    dependencies["dev_dependencies"] = dev_deps
                    dependencies["total_count"] = len(deps) + len(dev_deps)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Analyze requirements.txt if it exists
        requirements_txt = self.root_path / "requirements.txt"
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r') as f:
                    lines = f.readlines()
                    deps = [line.strip().split('==')[0] for line in lines if line.strip() and not line.startswith('#')]
                    dependencies["external"]["python"] = deps
                    dependencies["total_count"] += len(deps)
            except FileNotFoundError:
                pass
        
        return dependencies
    
    def _analyze_configuration(self, depth: int, ignore_patterns: List[str]) -> Dict[str, Any]:
        """Analyze configuration files and settings."""
        config_files = {}
        
        # Common configuration files
        config_patterns = {
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"],
            "ci_cd": [".github/workflows/", ".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile"],
            "environment": [".env", ".env.local", ".env.production", ".env.development"],
            "database": ["database.yml", "db.json", "migrations/"],
            "deployment": ["deploy.sh", "deploy.yml", "k8s/", "kubernetes/"],
            "monitoring": ["prometheus.yml", "grafana/", "monitoring/"],
            "documentation": ["README.md", "docs/", "CHANGELOG.md", "LICENSE"]
        }
        
        for category, patterns in config_patterns.items():
            found_files = []
            for pattern in patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    dir_path = self.root_path / pattern.rstrip("/")
                    if dir_path.exists():
                        found_files.append(pattern)
                else:
                    # File pattern
                    if (self.root_path / pattern).exists():
                        found_files.append(pattern)
            
            if found_files:
                config_files[category] = found_files
        
        return {
            "files": config_files,
            "total_config_files": sum(len(files) for files in config_files.values()),
            "categories": list(config_files.keys())
        }
    
    def _walk_files(self, depth: int, ignore_patterns: List[str]) -> List[Path]:
        """Walk through files respecting depth and ignore patterns."""
        files = []
        
        for root, dirs, filenames in os.walk(self.root_path):
            # Skip ignored directories
            if any(pattern in root for pattern in ignore_patterns):
                continue
            
            # Respect depth limit
            if depth > 0 and root.count(os.sep) - self.root_path.as_posix().count(os.sep) >= depth:
                continue
            
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.root_path)
                
                # Skip ignored files
                if any(pattern in str(rel_path) for pattern in ignore_patterns):
                    continue
                
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                
                files.append(file_path)
        
        return files
    
    def _extension_to_language(self, ext: str) -> Optional[str]:
        """Map file extension to programming language."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.h': 'C/C++',
            '.hpp': 'C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.ml': 'OCaml',
            '.fs': 'F#',
            '.erl': 'Erlang',
            '.ex': 'Elixir',
            '.dart': 'Dart',
            '.r': 'R',
            '.m': 'Objective-C',
            '.mm': 'Objective-C++',
            '.pl': 'Perl',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.fish': 'Fish',
            '.ps1': 'PowerShell',
            '.bat': 'Batch',
            '.cmd': 'Batch',
            '.lua': 'Lua',
            '.vim': 'Vim Script',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.cfg': 'Config',
            '.conf': 'Config',
            '.md': 'Markdown',
            '.rst': 'reStructuredText',
            '.tex': 'LaTeX',
            '.dockerfile': 'Dockerfile'
        }
        
        return language_map.get(ext)
    
    def _determine_project_type(self) -> str:
        """Determine the primary project type."""
        if (self.root_path / "package.json").exists():
            return "Node.js"
        elif (self.root_path / "requirements.txt").exists() or (self.root_path / "setup.py").exists():
            return "Python"
        elif (self.root_path / "Cargo.toml").exists():
            return "Rust"
        elif (self.root_path / "go.mod").exists():
            return "Go"
        elif (self.root_path / "pom.xml").exists():
            return "Java"
        elif (self.root_path / "Gemfile").exists():
            return "Ruby"
        elif (self.root_path / "composer.json").exists():
            return "PHP"
        else:
            return "Mixed/Unknown"
    
    def _calculate_project_size(self) -> int:
        """Calculate total project size in bytes."""
        total_size = 0
        for file_path in self._walk_files(5, []):
            try:
                total_size += file_path.stat().st_size
            except (OSError, FileNotFoundError):
                pass
        return total_size
    
    def _count_files(self) -> int:
        """Count total number of files."""
        return len(self._walk_files(5, []))
    
    def _count_directories(self) -> int:
        """Count total number of directories."""
        dir_count = 0
        for root, dirs, files in os.walk(self.root_path):
            dir_count += len(dirs)
        return dir_count
    
    def _calculate_framework_confidence(self, frameworks: Set[str]) -> Dict[str, float]:
        """Calculate confidence scores for detected frameworks."""
        confidence = {}
        for framework in frameworks:
            # Simple confidence based on number of indicators
            confidence[framework] = 0.8  # Base confidence
        return confidence
    
    def _determine_primary_package_manager(self, managers: Set[str]) -> Optional[str]:
        """Determine the primary package manager."""
        if not managers:
            return None
        
        # Priority order
        priority = ["pnpm", "yarn", "npm", "poetry", "pipenv", "pip", "cargo", "maven", "gradle"]
        
        for manager in priority:
            if manager in managers:
                return manager
        
        return list(managers)[0]
    
    def _detect_coverage_tools(self) -> List[str]:
        """Detect code coverage tools."""
        coverage_tools = []
        
        coverage_files = [
            "coverage.xml", "coverage.json", "lcov.info", ".nyc_output/",
            "coverage/", "htmlcov/", "coverage-report/"
        ]
        
        for file_path in coverage_files:
            if (self.root_path / file_path).exists():
                coverage_tools.append(file_path)
        
        return coverage_tools
    
    def _categorize_lint_tools(self, tools: Set[str]) -> Dict[str, List[str]]:
        """Categorize linting tools by type."""
        categories = {
            "javascript": [],
            "python": [],
            "css": [],
            "general": []
        }
        
        js_tools = ["eslint", "prettier", "stylelint", "tslint", "jshint"]
        py_tools = ["pylint", "flake8", "black", "isort", "mypy"]
        css_tools = ["stylelint"]
        
        for tool in tools:
            if tool in js_tools:
                categories["javascript"].append(tool)
            elif tool in py_tools:
                categories["python"].append(tool)
            elif tool in css_tools:
                categories["css"].append(tool)
            else:
                categories["general"].append(tool)
        
        return {k: v for k, v in categories.items() if v}
    
    def _detect_organization_pattern(self) -> str:
        """Detect project organization pattern."""
        if (self.root_path / "src").exists():
            return "src-based"
        elif (self.root_path / "lib").exists():
            return "lib-based"
        elif (self.root_path / "app").exists():
            return "app-based"
        else:
            return "flat"
    
    def _generate_report_json(self) -> None:
        """Generate detailed report.json file."""
        report_file = self.output_dir / "report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, default=str, sort_keys=True)
        
        print(f"📄 Detailed report saved to: {report_file}")
    
    def _generate_summary_md(self) -> None:
        """Generate human-readable summary.md file."""
        summary_file = self.output_dir / "summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Project Discovery Summary\n\n")
            
            # Project info
            project_info = self.analysis_results["project_info"]
            f.write(f"**Project:** {project_info['name']}\n")
            f.write(f"**Type:** {project_info['type']}\n")
            f.write(f"**Files:** {project_info['file_count']:,}\n")
            f.write(f"**Size:** {project_info['size_bytes']:,} bytes\n\n")
            
            # Languages
            languages = self.analysis_results["languages"]
            f.write("## Languages\n")
            if languages["detected"]:
                f.write(f"**Primary:** {languages['primary']}\n")
                f.write(f"**Detected:** {', '.join(languages['detected'])}\n")
            else:
                f.write("No programming languages detected.\n")
            f.write("\n")
            
            # Frameworks
            frameworks = self.analysis_results["frameworks"]
            f.write("## Frameworks\n")
            if frameworks["detected"]:
                f.write(f"**Detected:** {', '.join(frameworks['detected'])}\n")
            else:
                f.write("No frameworks detected.\n")
            f.write("\n")
            
            # Package Managers
            package_managers = self.analysis_results["package_managers"]
            f.write("## Package Managers\n")
            if package_managers["detected"]:
                f.write(f"**Primary:** {package_managers['primary']}\n")
                f.write(f"**Detected:** {', '.join(package_managers['detected'])}\n")
            else:
                f.write("No package managers detected.\n")
            f.write("\n")
            
            # Test Runners
            test_runners = self.analysis_results["test_runners"]
            f.write("## Testing\n")
            if test_runners["detected"]:
                f.write(f"**Runners:** {', '.join(test_runners['detected'])}\n")
                f.write(f"**Test Files:** {test_runners['test_file_count']}\n")
            else:
                f.write("No test runners detected.\n")
            f.write("\n")
            
            # Linting/Formatting
            lint_tools = self.analysis_results["lint_formatters"]
            f.write("## Code Quality\n")
            if lint_tools["detected"]:
                f.write(f"**Tools:** {', '.join(lint_tools['detected'])}\n")
            else:
                f.write("No linting/formatting tools detected.\n")
            f.write("\n")
            
            # Monorepo
            monorepo = self.analysis_results["monorepo_hints"]
            f.write("## Monorepo\n")
            f.write(f"**Is Monorepo:** {monorepo['is_monorepo']}\n")
            if monorepo["detected"]:
                f.write(f"**Tools:** {', '.join(monorepo['detected'])}\n")
            f.write("\n")
            
            # Dependencies
            deps = self.analysis_results["dependencies"]
            f.write("## Dependencies\n")
            f.write(f"**Total:** {deps['total_count']}\n")
            f.write(f"**External:** {len(deps['external'])}\n")
            f.write(f"**Dev Dependencies:** {len(deps['dev_dependencies'])}\n\n")
            
            # Configuration
            config = self.analysis_results["configuration"]
            f.write("## Configuration\n")
            f.write(f"**Config Files:** {config['total_config_files']}\n")
            f.write(f"**Categories:** {', '.join(config['categories'])}\n\n")
            
            # Analysis metadata
            metadata = self.analysis_results["metadata"]
            f.write("## Analysis Metadata\n")
            f.write(f"**Depth:** {metadata['analysis_depth']}\n")
            f.write(f"**Duration:** {metadata['analysis_duration']:.2f}s\n")
            f.write(f"**Timestamp:** {metadata['timestamp']}\n")
        
        print(f"📊 Summary saved to: {summary_file}")
    
    def _update_project_state(self) -> None:
        """Update project state to mark discovery as completed."""
        try:
            # Try to update state.json
            state_file = self.cache_dir / "state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {"project_state": {}}
            
            state["project_state"]["discovered"] = True
            state["project_state"]["discovery_timestamp"] = datetime.now().isoformat()
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, sort_keys=True)
                
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            # If we can't update state, that's okay
            pass


def analyze_project_enhanced(root_path: str = ".", 
                           depth: int = 3, 
                           ignore_patterns: Optional[List[str]] = None, 
                           ci_mode: bool = False) -> Dict[str, Any]:
    """Convenience function to run enhanced project analysis.
    
    Args:
        root_path: Root directory to analyze
        depth: Analysis depth (1-5)
        ignore_patterns: List of patterns to ignore
        ci_mode: Non-interactive mode
        
    Returns:
        Analysis results dictionary
    """
    engine = EnhancedDiscoveryEngine(root_path)
    return engine.analyze_project(depth, ignore_patterns, ci_mode)


if __name__ == "__main__":
    # Test the enhanced discovery engine
    import sys
    
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"🔍 Running enhanced discovery on: {root}")
    results = analyze_project_enhanced(root, depth)
    print(f"✅ Analysis complete! Check cb_docs/discovery/ for outputs.")
