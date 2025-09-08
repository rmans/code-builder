#!/usr/bin/env python3
"""
Unit tests for OverlayPaths module.

Tests both overlay and standalone mode path resolution.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from builder.overlay.paths import OverlayPaths, overlay_paths


class TestOverlayPaths:
    """Test cases for OverlayPaths class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        os.environ.clear()
        os.environ.update(self.original_env)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_standalone_mode_detection(self):
        """Test standalone mode detection."""
        # Create a project structure without .cb directory
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        
        # Create .git directory to simulate a git repository
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        assert not paths.is_overlay_mode()
        assert paths._mode == 'standalone'
        assert str(paths.cb_root()) == str(project_root)
    
    def test_overlay_mode_detection(self):
        """Test overlay mode detection."""
        # Create a project structure with .cb directory
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        assert paths.is_overlay_mode()
        assert paths._mode == 'overlay'
        assert str(paths.cb_root()) == str(project_root)
    
    def test_overlay_mode_via_env(self):
        """Test overlay mode detection via environment variable."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        os.environ['CB_MODE'] = 'overlay'
        
        paths = OverlayPaths()
        assert paths.is_overlay_mode()
        assert paths._mode == 'overlay'
    
    def test_standalone_paths(self):
        """Test path resolution in standalone mode."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        
        # Test individual path methods
        assert paths.cb_root() == str(project_root)
        assert paths.cursor_rules_dir() == str(project_root / 'cb_docs' / 'rules')
        assert paths.cb_docs_dir() == str(project_root / 'cb_docs')
        assert paths.tasks_index() == str(project_root / 'cb_docs' / 'tasks' / 'index.md')
        assert paths.logs_dir() == str(project_root / 'builder' / 'logs')
        assert paths.cache_dir() == str(project_root / 'builder' / 'cache')
        assert paths.engine_dir() == str(project_root / 'builder')
        assert paths.templates_dir() == str(project_root / 'cb_docs' / 'templates')
        assert paths.adrs_dir() == str(project_root / 'cb_docs' / 'adrs')
        assert paths.tasks_dir() == str(project_root / 'cb_docs' / 'tasks')
    
    def test_overlay_paths(self):
        """Test path resolution in overlay mode."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        
        # Test individual path methods
        assert paths.cb_root() == str(project_root)
        assert paths.cursor_rules_dir() == str(project_root / '.cursor' / 'rules')
        assert paths.cb_docs_dir() == str(project_root / 'cb_docs')
        assert paths.tasks_index() == str(project_root / 'cb_docs' / 'tasks' / 'index.md')
        assert paths.logs_dir() == str(project_root / '.cb' / 'logs')
        assert paths.cache_dir() == str(project_root / '.cb' / 'cache')
        assert paths.engine_dir() == str(project_root / '.cb' / 'engine')
        assert paths.templates_dir() == str(project_root / 'cb_docs' / 'templates')
        assert paths.adrs_dir() == str(project_root / 'cb_docs' / 'adrs')
        assert paths.tasks_dir() == str(project_root / 'cb_docs' / 'tasks')
    
    def test_get_mode_info(self):
        """Test get_mode_info method."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        mode_info = paths.get_mode_info()
        
        assert mode_info['mode'] == 'overlay'
        assert mode_info['is_overlay'] is True
        assert mode_info['cb_root'] == str(project_root)
        assert 'cursor_rules_dir' in mode_info
        assert 'cb_docs_dir' in mode_info
        assert 'tasks_index' in mode_info
        assert 'logs_dir' in mode_info
        assert 'cache_dir' in mode_info
        assert 'engine_dir' in mode_info
        assert 'templates_dir' in mode_info
        assert 'adrs_dir' in mode_info
        assert 'tasks_dir' in mode_info
    
    def test_ensure_directories(self):
        """Test ensure_directories method."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        paths.ensure_directories()
        
        # Check that directories were created
        assert (project_root / '.cursor' / 'rules').exists()
        assert (project_root / 'cb_docs').exists()
        assert (project_root / 'cb_docs' / 'tasks').exists()
        assert (project_root / '.cb' / 'logs').exists()
        assert (project_root / '.cb' / 'cache').exists()
        assert (project_root / 'cb_docs' / 'templates').exists()
        assert (project_root / 'cb_docs' / 'adrs').exists()
    
    def test_validate_success(self):
        """Test validate method with successful validation."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        paths.ensure_directories()
        
        assert paths.validate() is True
    
    def test_validate_failure(self):
        """Test validate method with validation failure."""
        # Create a read-only directory to test validation failure
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        paths = OverlayPaths()
        paths.ensure_directories()
        
        # Make logs directory read-only to cause validation failure
        logs_dir = Path(paths.logs_dir())
        logs_dir.chmod(0o444)
        
        try:
            assert paths.validate() is False
        finally:
            # Restore permissions for cleanup
            logs_dir.chmod(0o755)
    
    def test_global_instance(self):
        """Test global overlay_paths instance."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        # Test global instance
        assert overlay_paths.cb_root() == str(project_root)
        assert overlay_paths.is_overlay_mode() is True


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        os.environ.clear()
        os.environ.update(self.original_env)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        project_root = Path(self.temp_dir) / 'test_project'
        project_root.mkdir()
        (project_root / '.cb').mkdir()
        (project_root / '.git').mkdir()
        
        os.chdir(project_root)
        
        # Import convenience functions
        from .cb.engine.builder.overlay.paths import (
            cb_root, cursor_rules_dir, cb_docs_dir, 
            tasks_index, logs_dir
        )
        
        # Test convenience functions
        assert cb_root() == str(project_root)
        assert cursor_rules_dir() == str(project_root / '.cursor' / 'rules')
        assert cb_docs_dir() == str(project_root / 'cb_docs')
        assert tasks_index() == str(project_root / 'cb_docs' / 'tasks' / 'index.md')
        assert logs_dir() == str(project_root / '.cb' / 'logs')


if __name__ == '__main__':
    pytest.main([__file__])
