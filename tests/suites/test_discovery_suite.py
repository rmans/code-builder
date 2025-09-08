#!/usr/bin/env python3
"""
Discovery Test Suite

Comprehensive tests for discovery functionality including:
- Project analysis
- File scanning
- Context generation
- Discovery engine validation
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from builder.discovery.enhanced_engine import EnhancedDiscoveryEngine, analyze_project_enhanced
from builder.overlay.paths import OverlayPaths


class TestDiscoverySuite:
    """Test suite for discovery functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir) / "test_project"
        self.project_root.mkdir()
        
        # Create a basic project structure
        self._create_test_project()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_project(self):
        """Create a test project structure."""
        # Create basic files
        (self.project_root / "README.md").write_text("# Test Project\nA test project for discovery.")
        (self.project_root / "package.json").write_text('{"name": "test-project", "version": "1.0.0"}')
        (self.project_root / "requirements.txt").write_text("click==8.0.0\npytest==6.0.0")
        
        # Create source directory
        src_dir = self.project_root / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('Hello, World!')")
        (src_dir / "utils.py").write_text("def helper(): pass")
        
        # Create tests directory
        tests_dir = self.project_root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): assert True")
    
    def test_project_analysis(self):
        """Test basic project analysis."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        result = engine.analyze_project()
        
        assert result is not None
        assert "project_type" in result
        assert "languages" in result
        assert "frameworks" in result
        assert "files_analyzed" in result
    
    def test_file_scanning(self):
        """Test file scanning functionality."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        files = engine._scan_files()
        
        assert len(files) > 0
        assert any(f.endswith('.py') for f in files)
        assert any(f.endswith('.md') for f in files)
        assert any(f.endswith('.json') for f in files)
    
    def test_language_detection(self):
        """Test language detection."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        languages = engine._detect_languages()
        
        assert "Python" in languages
        assert "JavaScript" in languages
        assert "Markdown" in languages
    
    def test_framework_detection(self):
        """Test framework detection."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        frameworks = engine._detect_frameworks()
        
        # Should detect pytest for Python
        assert "pytest" in frameworks or "Python" in frameworks
    
    def test_project_type_detection(self):
        """Test project type detection."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        project_type = engine._detect_project_type()
        
        assert project_type in ["Python", "Node.js", "Mixed", "Unknown"]
    
    def test_analysis_metadata(self):
        """Test analysis metadata generation."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        result = engine.analyze_project()
        
        assert "analysis_duration" in result
        assert "timestamp" in result
        assert "file_count" in result
        assert result["file_count"] > 0
    
    def test_discovery_consistency(self):
        """Test that discovery results are consistent across runs."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        
        result1 = engine.analyze_project()
        result2 = engine.analyze_project()
        
        # Key fields should be consistent
        assert result1["project_type"] == result2["project_type"]
        assert result1["languages"] == result2["languages"]
        assert result1["file_count"] == result2["file_count"]
    
    def test_enhanced_analysis_function(self):
        """Test the enhanced analysis function."""
        result = analyze_project_enhanced(str(self.project_root))
        
        assert result is not None
        assert "project_analysis" in result
        assert "file_analysis" in result
        assert "summary" in result
    
    def test_discovery_with_ignore_patterns(self):
        """Test discovery with ignore patterns."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        ignore_patterns = ["*.pyc", "__pycache__"]
        
        result = engine.analyze_project(ignore_patterns=ignore_patterns)
        
        assert result is not None
        # Should not include Python cache files
        files = result.get("files_analyzed", [])
        assert not any("__pycache__" in f for f in files)
    
    def test_discovery_ci_mode(self):
        """Test discovery in CI mode."""
        engine = EnhancedDiscoveryEngine(str(self.project_root))
        result = engine.analyze_project(ci_mode=True)
        
        assert result is not None
        # CI mode should be more conservative
        assert "ci_mode" in result or result.get("analysis_duration", 0) > 0


class TestDiscoveryIntegration:
    """Integration tests for discovery functionality."""
    
    def test_discovery_with_overlay_paths(self):
        """Test discovery with overlay paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "test_project"
            project_root.mkdir()
            
            # Create basic project
            (project_root / "README.md").write_text("# Test Project")
            (project_root / "package.json").write_text('{"name": "test-project"}')
            
            # Test with overlay paths
            overlay_paths = OverlayPaths()
            engine = EnhancedDiscoveryEngine(str(project_root))
            result = engine.analyze_project()
            
            assert result is not None
            assert "project_type" in result
    
    def test_discovery_error_handling(self):
        """Test discovery error handling."""
        # Test with non-existent directory
        with pytest.raises((FileNotFoundError, OSError)):
            engine = EnhancedDiscoveryEngine("/non/existent/path")
            engine.analyze_project()
    
    def test_discovery_empty_project(self):
        """Test discovery with empty project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "empty_project"
            project_root.mkdir()
            
            engine = EnhancedDiscoveryEngine(str(project_root))
            result = engine.analyze_project()
            
            assert result is not None
            assert result.get("file_count", 0) == 0
            assert result.get("project_type") == "Unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
