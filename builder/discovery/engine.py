"""
Discovery Engine - Core orchestration for code discovery processes.

The DiscoveryEngine coordinates the discovery workflow, managing the interview,
analysis, synthesis, and validation phases.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from .interview import DiscoveryInterview
from .analyzer import CodeAnalyzer
from .synthesizer import DiscoverySynthesizer
from .generators import DiscoveryGenerators
from .validator import DiscoveryValidator


class DiscoveryEngine:
    """Main engine for orchestrating code discovery processes."""
    
    def __init__(self, root_path: str = ".", question_set: str = "comprehensive"):
        """Initialize the discovery engine.
        
        Args:
            root_path: Root directory of the project to analyze
            question_set: Question set to use (new_product, existing_product, comprehensive)
        """
        self.root_path = Path(root_path).resolve()
        self.cache_dir = self.root_path / "builder" / "cache" / "discovery"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.question_set = question_set
        
        # Initialize components
        self.interview = DiscoveryInterview(question_set=question_set)
        self.analyzer = CodeAnalyzer()
        self.synthesizer = DiscoverySynthesizer()
        self.generators = DiscoveryGenerators()
        self.validator = DiscoveryValidator()
        
        # Discovery state
        self.results: Dict[str, Any] = {}
        self.cache_key: Optional[str] = None
    
    def discover(self, target_path: str, options: Optional[Dict] = None, batch_kwargs: Optional[Dict] = None, force: bool = False) -> Dict[str, Any]:
        """Run the complete discovery process for a target file or directory.
        
        Args:
            target_path: Path to analyze (file or directory)
            options: Optional configuration options
            batch_kwargs: Optional batch input data for interview
            force: Force regeneration even if cache is valid
            
        Returns:
            Dictionary containing discovery results
        """
        target = Path(target_path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")
        
        # Generate cache key
        options = options or {}
        options['question_set'] = self.question_set
        if batch_kwargs:
            options['batch_kwargs'] = batch_kwargs
        self.cache_key = self._generate_cache_key(target, options)
        
        # Check cache validity first
        if not force and self._is_cache_valid(target, options, force):
            cached_result = self._load_from_cache()
            if cached_result:
                return cached_result
        
        # If force or cache invalid, clear any existing cache
        if force or not self._is_cache_valid(target, options, force):
            self._clear_cache()
        
        # Run discovery pipeline
        try:
            # Phase 1: Interview - gather initial information
            interview_data = self.interview.conduct(target, options, batch_kwargs)
            
            # Phase 2: Analysis - deep code analysis
            analysis_data = self.analyzer.analyze(target, interview_data)
            
            # Phase 3: Synthesis - combine and structure findings
            synthesis_data = self.synthesizer.synthesize(analysis_data, interview_data)
            
            # Phase 4: Generation - create outputs and reports
            generation_data, generation_warnings, prd_id = self.generators.generate(synthesis_data, target)
            
            # Phase 5: Validation - verify results
            validation_data = self.validator.validate(generation_data, synthesis_data)
            
            # Combine all results
            self.results = {
                'target': str(target),
                'cache_key': self.cache_key,
                'question_set': self.question_set,
                'interview': interview_data,
                'analysis': analysis_data,
                'synthesis': synthesis_data,
                'generation': generation_data,
                'validation': validation_data,
                'prd_id': prd_id,
                'warnings': generation_warnings,
                'timestamp': self._get_timestamp()
            }
            
            # Cache results
            self._save_to_cache()
            
            # Save per-PRD context if PRD was generated
            if prd_id:
                self._save_prd_context(prd_id, synthesis_data)
            
            # Save legacy discovery context
            self._save_legacy_context()
            
            # Try auto ctx:build handoff
            self._try_auto_ctx_build(target)
            
            return self.results
            
        except Exception as e:
            return {
                'error': str(e),
                'target': str(target),
                'cache_key': self.cache_key,
                'timestamp': self._get_timestamp()
            }
    
    def explain(self, target_path: str) -> str:
        """Generate a human-readable explanation of discovery results.
        
        Args:
            target_path: Path that was analyzed
            
        Returns:
            Explanation string
        """
        if not self.results or self.results.get('target') != str(Path(target_path).resolve()):
            # Run discovery if not already done
            self.discover(target_path)
        
        if 'error' in self.results:
            return f"Discovery failed: {self.results['error']}"
        
        return self.synthesizer.explain(self.results)
    
    def clear_cache(self) -> None:
        """Clear the discovery cache."""
        if self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_cache_key(self, target: Path, options: Dict) -> str:
        """Generate a comprehensive cache key based on all relevant inputs."""
        import hashlib
        import yaml
        from datetime import datetime
        
        # Start with basic target and options
        key_data = {
            'target': str(target),
            'target_mtime': target.stat().st_mtime if target.exists() else 0,
            'options': options,
            'question_set': self.question_set
        }
        
        # Add patterns.yml hash
        patterns_file = self.root_path / "builder" / "discovery" / "patterns.yml"
        if patterns_file.exists():
            key_data['patterns_mtime'] = patterns_file.stat().st_mtime
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_content = f.read()
                key_data['patterns_hash'] = hashlib.md5(patterns_content.encode()).hexdigest()
            except Exception:
                key_data['patterns_hash'] = 'error'
        else:
            key_data['patterns_mtime'] = 0
            key_data['patterns_hash'] = 'missing'
        
        # Add questions.yml hash
        questions_file = self.root_path / "builder" / "discovery" / "questions.yml"
        if questions_file.exists():
            key_data['questions_mtime'] = questions_file.stat().st_mtime
            try:
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions_content = f.read()
                key_data['questions_hash'] = hashlib.md5(questions_content.encode()).hexdigest()
            except Exception:
                key_data['questions_hash'] = 'error'
        else:
            key_data['questions_mtime'] = 0
            key_data['questions_hash'] = 'missing'
        
        # Add PRD documents hash (if any exist)
        prd_dir = self.root_path / "docs" / "prd"
        if prd_dir.exists():
            prd_files = list(prd_dir.glob("PRD-*.md"))
            prd_hashes = {}
            for prd_file in prd_files:
                try:
                    with open(prd_file, 'r', encoding='utf-8') as f:
                        prd_content = f.read()
                    prd_hashes[str(prd_file.name)] = {
                        'mtime': prd_file.stat().st_mtime,
                        'hash': hashlib.md5(prd_content.encode()).hexdigest()
                    }
                except Exception:
                    prd_hashes[str(prd_file.name)] = {'mtime': 0, 'hash': 'error'}
            key_data['prd_files'] = prd_hashes
        else:
            key_data['prd_files'] = {}
        
        # Add linked documents hash (ADRs, ARCH, EXEC, IMPL, etc.)
        linked_docs = {}
        for doc_type in ['adrs', 'arch', 'exec', 'impl', 'integrations', 'tasks', 'ux']:
            doc_dir = self.root_path / "docs" / doc_type
            if doc_dir.exists():
                doc_files = list(doc_dir.glob(f"{doc_type.upper()}-*.md"))
                type_hashes = {}
                for doc_file in doc_files:
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            doc_content = f.read()
                        type_hashes[str(doc_file.name)] = {
                            'mtime': doc_file.stat().st_mtime,
                            'hash': hashlib.md5(doc_content.encode()).hexdigest()
                        }
                    except Exception:
                        type_hashes[str(doc_file.name)] = {'mtime': 0, 'hash': 'error'}
                linked_docs[doc_type] = type_hashes
            else:
                linked_docs[doc_type] = {}
        key_data['linked_docs'] = linked_docs
        
        # Add key source file mtimes (important source files)
        key_source_files = self._find_key_source_files(target)
        source_mtimes = {}
        for source_file in key_source_files:
            try:
                source_mtimes[str(source_file)] = source_file.stat().st_mtime
            except Exception:
                source_mtimes[str(source_file)] = 0
        key_data['key_source_files'] = source_mtimes
        
        # Add feature map hash (if exists in results)
        if hasattr(self, 'results') and 'synthesis' in self.results:
            feature_map = self.results.get('synthesis', {}).get('feature_map', {})
            key_data['feature_map_hash'] = hashlib.md5(json.dumps(feature_map, sort_keys=True).encode()).hexdigest()
        else:
            key_data['feature_map_hash'] = 'not_available'
        
        # Generate final hash
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _find_key_source_files(self, target: Path) -> List[Path]:
        """Find key source files that should invalidate cache when changed."""
        key_files = []
        
        # Always include the target file/directory
        if target.exists():
            if target.is_file():
                key_files.append(target)
            else:
                # For directories, include key files
                key_files.extend(self._find_important_files_in_dir(target))
        
        # Add common important files from project root
        important_patterns = [
            "package.json", "package-lock.json", "pnpm-lock.yaml",
            "tsconfig.json", "tsconfig.*.json",
            "requirements.txt", "pyproject.toml", "setup.py",
            "go.mod", "go.sum",
            "Dockerfile", "docker-compose.yml",
            "README.md", "CHANGELOG.md",
            ".github/workflows/*.yml", ".github/workflows/*.yaml"
        ]
        
        for pattern in important_patterns:
            if "*" in pattern:
                # Handle glob patterns
                matches = list(self.root_path.glob(pattern))
                key_files.extend(matches)
            else:
                # Handle single files
                file_path = self.root_path / pattern
                if file_path.exists():
                    key_files.append(file_path)
        
        # Add source files from common directories
        source_dirs = ["src", "lib", "app", "components", "pages", "api"]
        for src_dir in source_dirs:
            src_path = self.root_path / src_dir
            if src_path.exists() and src_path.is_dir():
                key_files.extend(self._find_important_files_in_dir(src_path))
        
        # Remove duplicates and return
        return list(set(key_files))
    
    def _find_important_files_in_dir(self, directory: Path) -> List[Path]:
        """Find important files in a directory (limit to avoid too many files)."""
        important_files = []
        important_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.cs'}
        
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    # Include files with important extensions
                    if file_path.suffix in important_extensions:
                        important_files.append(file_path)
                    # Include configuration files
                    elif file_path.name in ['package.json', 'tsconfig.json', 'requirements.txt', 'go.mod']:
                        important_files.append(file_path)
                    # Limit to prevent too many files
                    if len(important_files) > 50:  # Reasonable limit
                        break
        except Exception:
            pass  # Silently handle permission errors
        
        return important_files
    
    def _load_from_cache(self) -> Optional[Dict]:
        """Load results from cache if available."""
        if not self.cache_key:
            return None
        
        cache_file = self.cache_dir / f"{self.cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def _is_cache_valid(self, target: Path, options: Dict, force: bool = False) -> bool:
        """Check if the current cache is still valid based on comprehensive hash comparison."""
        if force:
            return False
        
        if not self.cache_key:
            return False
        
        # Generate current cache key
        current_cache_key = self._generate_cache_key(target, options)
        
        # Compare with stored cache key
        return current_cache_key == self.cache_key
    
    def _get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        if not self.cache_key:
            return {'status': 'no_cache', 'cache_key': None}
        
        cache_file = self.cache_dir / f"{self.cache_key}.json"
        if not cache_file.exists():
            return {'status': 'missing', 'cache_key': self.cache_key}
        
        try:
            stat = cache_file.stat()
            return {
                'status': 'exists',
                'cache_key': self.cache_key,
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'path': str(cache_file)
            }
        except Exception:
            return {'status': 'error', 'cache_key': self.cache_key}
    
    def _save_to_cache(self) -> None:
        """Save results to cache."""
        if not self.cache_key or not self.results:
            return
        
        cache_file = self.cache_dir / f"{self.cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.results, f, indent=2)
        except IOError:
            pass  # Cache is optional
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _save_prd_context(self, prd_id: str, synthesis_data: Dict[str, Any]) -> None:
        """Save discovery context to per-PRD YAML file."""
        try:
            import yaml
            
            # Create PRD-specific context
            # Try to get product info from multiple sources
            product_name = 'Unknown Product'
            main_idea = ''
            problem_solved = ''
            target_users = ''
            key_features = []
            success_metrics = ''
            tech_stack_preferences = ''
            
            # Try synthesis data first
            if 'questions' in synthesis_data:
                questions = synthesis_data['questions']
                product_name = questions.get('product_name', product_name)
                main_idea = questions.get('main_idea', main_idea)
                problem_solved = questions.get('problem_solved', problem_solved)
                target_users = questions.get('target_users', target_users)
                key_features = questions.get('key_features', key_features)
                success_metrics = questions.get('success_metrics', success_metrics)
                tech_stack_preferences = questions.get('tech_stack_preferences', tech_stack_preferences)
            
            # Fallback to interview data
            if product_name == 'Unknown Product' and 'interview' in self.results:
                interview_questions = self.results['interview'].get('questions', {})
                product_name = interview_questions.get('product_name', product_name)
                main_idea = interview_questions.get('main_idea', main_idea)
                problem_solved = interview_questions.get('problem_solved', problem_solved)
                target_users = interview_questions.get('target_users', target_users)
                key_features = interview_questions.get('key_features', key_features)
                success_metrics = interview_questions.get('success_metrics', success_metrics)
                tech_stack_preferences = interview_questions.get('tech_stack_preferences', tech_stack_preferences)
            
            prd_context = {
                'prd_id': prd_id,
                'product_name': product_name,
                'main_idea': main_idea,
                'problem_solved': problem_solved,
                'target_users': target_users,
                'key_features': key_features,
                'success_metrics': success_metrics,
                'tech_stack_preferences': tech_stack_preferences,
                'detected_tech': synthesis_data.get('detected', {}),
                'created': self._get_timestamp(),
                'status': 'draft',
                'discovery_results': {
                    'interview': self.results.get('interview', {}),
                    'analysis': self.results.get('analysis', {}),
                    'synthesis': self.results.get('synthesis', {}),
                    'generation': self.results.get('generation', {}),
                    'validation': self.results.get('validation', {})
                }
            }
            
            # Save to PRD-specific file
            prd_file = self.cache_dir / f"{prd_id}.yml"
            with open(prd_file, 'w', encoding='utf-8') as f:
                yaml.dump(prd_context, f, default_flow_style=False, sort_keys=False)
                
        except Exception as e:
            # Silently fail for context saving
            pass
    
    def _save_legacy_context(self) -> None:
        """Save discovery context to legacy discovery_context.yml file."""
        try:
            import yaml
            
            # Get product info from interview data (same as per-PRD context)
            interview_questions = self.results.get('interview', {}).get('questions', {})
            product_name = interview_questions.get('product_name', 'Unknown Product')
            main_idea = interview_questions.get('main_idea', '')
            
            # Create legacy context format
            legacy_context = {
                'product': product_name,
                'idea': main_idea,
                'created': self._get_timestamp(),
                'status': 'draft',
                'question_set': self.question_set,
                'auto_generated': True,
                'discovery_phases': {
                    'interview': {'completed': True, 'data': self.results.get('interview', {})},
                    'analysis': {'completed': True, 'data': self.results.get('analysis', {})},
                    'synthesis': {'completed': True, 'data': self.results.get('synthesis', {})},
                    'generation': {'completed': True, 'data': self.results.get('generation', {})},
                    'validation': {'completed': True, 'data': self.results.get('validation', {})}
                },
                'targets': [],
                'insights': self.results.get('synthesis', {}).get('insights', []),
                'recommendations': self.results.get('synthesis', {}).get('recommendations', []),
                'next_steps': [
                    f"Review generated PRD: {self.results.get('prd_id', 'N/A')}",
                    "Refine requirements based on analysis",
                    "Plan implementation phases",
                    "Set up development environment",
                    "Create detailed technical specifications"
                ]
            }
            
            # Add specific fields if available
            if interview_questions.get('problem_solved'):
                legacy_context['problem_solved'] = interview_questions['problem_solved']
            if interview_questions.get('target_users'):
                legacy_context['target_users'] = interview_questions['target_users']
            if interview_questions.get('key_features'):
                legacy_context['key_features'] = interview_questions['key_features']
            if interview_questions.get('success_metrics'):
                legacy_context['success_metrics'] = interview_questions['success_metrics']
            if interview_questions.get('tech_stack_preferences'):
                legacy_context['tech_stack_preferences'] = interview_questions['tech_stack_preferences']
            
            # Save to legacy file
            legacy_file = self.root_path / "builder" / "cache" / "discovery_context.yml"
            legacy_file.parent.mkdir(parents=True, exist_ok=True)
            with open(legacy_file, 'w', encoding='utf-8') as f:
                yaml.dump(legacy_context, f, default_flow_style=False, sort_keys=False)
                
        except Exception as e:
            # Silently fail for legacy context saving
            pass
    
    def _try_auto_ctx_build(self, target: Path) -> None:
        """Try to run ctx:build on sensible paths after discovery generation."""
        try:
            # Find sensible paths to try ctx:build on
            sensible_paths = self._find_sensible_paths(target)
            
            if not sensible_paths:
                print("Next: ctx:build <path> --purpose implement")
                return
            
            # Try each sensible path until one succeeds
            for path in sensible_paths:
                if self._run_ctx_build(path):
                    print(f"✅ Auto ctx:build succeeded for: {path}")
                    return
            
            # If none succeeded, print next steps
            print("Next: ctx:build <path> --purpose implement")
            
        except Exception as e:
            # Silently fail for auto ctx:build
            pass
    
    def _find_sensible_paths(self, target: Path) -> List[str]:
        """Find sensible paths to try ctx:build on."""
        sensible_paths = []
        
        # Priority order for sensible paths
        priority_paths = [
            "src/index.ts",
            "src/main.ts", 
            "src/app.ts",
            "src/auth/login.ts",
            "src/auth/index.ts",
            "index.ts",
            "main.ts",
            "app.ts"
        ]
        
        # Check priority paths first
        for path in priority_paths:
            full_path = self.root_path / path
            if full_path.exists() and full_path.suffix in ['.ts', '.tsx']:
                sensible_paths.append(str(full_path))
        
        # If no priority paths found, find first TypeScript file
        if not sensible_paths:
            for ext in ['*.ts', '*.tsx']:
                for ts_file in self.root_path.rglob(ext):
                    # Skip node_modules but allow test files
                    ts_file_str = str(ts_file)
                    if 'node_modules' not in ts_file_str:
                        sensible_paths.append(ts_file_str)
                        break
                if sensible_paths:
                    break
        
        return sensible_paths
    
    def _run_ctx_build(self, target_path: str) -> bool:
        """Run ctx:build on the target path and return success status."""
        try:
            import subprocess
            import os
            
            # Run ctx:build command
            cmd = [
                'python3', 'builder/cli.py', 'ctx:build', target_path,
                '--purpose', 'implement'
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.root_path,
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            # Check if ctx:build succeeded
            if result.returncode == 0:
                # Check if context files were created
                context_md = self.root_path / "builder" / "cache" / "context.md"
                pack_context = self.root_path / "builder" / "cache" / "pack_context.json"
                
                if context_md.exists() and pack_context.exists():
                    return True
            
            return False
            
        except Exception:
            return False
