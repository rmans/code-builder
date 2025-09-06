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
    
    def discover(self, target_path: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Run the complete discovery process for a target file or directory.
        
        Args:
            target_path: Path to analyze (file or directory)
            options: Optional configuration options
            
        Returns:
            Dictionary containing discovery results
        """
        target = Path(target_path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")
        
        # Generate cache key
        options = options or {}
        options['question_set'] = self.question_set
        self.cache_key = self._generate_cache_key(target, options)
        
        # Check cache first
        cached_result = self._load_from_cache()
        if cached_result:
            return cached_result
        
        # Run discovery pipeline
        try:
            # Phase 1: Interview - gather initial information
            interview_data = self.interview.conduct(target, options)
            
            # Phase 2: Analysis - deep code analysis
            analysis_data = self.analyzer.analyze(target, interview_data)
            
            # Phase 3: Synthesis - combine and structure findings
            synthesis_data = self.synthesizer.synthesize(analysis_data)
            
            # Phase 4: Generation - create outputs and reports
            generation_data = self.generators.generate(synthesis_data, target)
            
            # Phase 5: Validation - verify results
            validation_data = self.validator.validate(generation_data)
            
            # Combine all results
            self.results = {
                'target': str(target),
                'cache_key': self.cache_key,
                'interview': interview_data,
                'analysis': analysis_data,
                'synthesis': synthesis_data,
                'generation': generation_data,
                'validation': validation_data,
                'timestamp': self._get_timestamp()
            }
            
            # Cache results
            self._save_to_cache()
            
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
        """Generate a cache key based on target and options."""
        import hashlib
        
        # Include target path, modification time, and options
        key_data = {
            'target': str(target),
            'mtime': target.stat().st_mtime if target.exists() else 0,
            'options': options
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
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
